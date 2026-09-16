// SethiStock Phase 4B — focused Revenue Drivers / By Segment view.
// Reuses the verified Phase 3C histories and Phase 3D persistent cache, but keeps
// the normal stock page compact by loading this UI only when the user asks for it.

(() => {
    'use strict';

    const DRIVER_API = typeof API_URL === 'string' ? API_URL : 'https://sethistock-api.onrender.com';
    const PERIODS = ['quarterly', 'annual'];
    const MEMORY_TTL_MS = 30 * 60 * 1000;
    const MEMORY_MAX = 120;
    const MAX_PARALLEL = 3;
    const PREFETCH_PARALLEL = 2;
    const SUPPORTED = new Set(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'JPM', 'V']);

    // Phase 4B deliberately narrows the old Company Drivers surface to metrics that
    // explain revenue mix or the operating volume directly behind revenue. Generic
    // profitability/capital metrics now belong in Key Financial Metrics instead.
    const REVENUE_DRIVER_KEYS = {
        AAPL: ['iphone_revenue', 'services_revenue', 'wearables_home_accessories_revenue'],
        MSFT: ['intelligent_cloud_revenue', 'microsoft_cloud_revenue', 'gaming_revenue', 'azure_growth'],
        GOOGL: ['google_search_revenue', 'youtube_ads_revenue', 'google_cloud_revenue'],
        AMZN: ['aws_revenue', 'advertising_services_revenue', 'international_revenue'],
        META: ['family_of_apps_revenue', 'reality_labs_revenue', 'ad_impressions_growth', 'average_price_per_ad_growth'],
        NVDA: ['data_center_revenue', 'gaming_revenue', 'automotive_revenue'],
        TSLA: ['automotive_revenue', 'vehicle_deliveries', 'energy_storage_deployments'],
        NFLX: ['paid_memberships', 'average_revenue_per_membership', 'ad_tier_scale'],
        JPM: ['net_interest_income', 'deposits', 'loans'],
        V: ['payments_volume', 'processed_transactions', 'cross_border_volume_growth', 'payments_credentials']
    };

    let activeTicker = '';
    let activePeriod = 'quarterly';
    let requestId = 0;
    let controller = null;
    let latestRegistry = null;
    let latestCoverage = null;
    let prefetchGeneration = 0;
    const historyCache = new Map();
    const metaCache = new Map();

    const qs = (selector, root = document) => root.querySelector(selector);
    const qsa = (selector, root = document) => Array.from(root.querySelectorAll(selector));

    function canonicalTicker(value) {
        const symbol = String(value || '').trim().toUpperCase();
        return symbol === 'GOOG' ? 'GOOGL' : symbol;
    }

    function supportsTicker(value) {
        return SUPPORTED.has(canonicalTicker(value));
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function finiteNumber(value) {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function humanPeriod(period) {
        return period === 'annual' ? 'Annual' : 'Quarterly';
    }

    function humanCategory(category) {
        return String(category || 'revenue driver')
            .replaceAll('_', ' ')
            .replace(/\b\w/g, char => char.toUpperCase());
    }

    function sourceLabel(sourceMode, observation) {
        const mode = String(sourceMode || observation?.extraction_method || '').toLowerCase();
        if (mode.includes('table')) return 'SEC filing table';
        if (mode.includes('derived')) return 'Derived SEC series';
        if (mode.includes('inline') || mode.includes('xbrl')) return 'Inline XBRL';
        return 'SEC filing';
    }

    function formatDate(value) {
        if (!value) return '';
        const date = new Date(`${String(value).slice(0, 10)}T00:00:00Z`);
        if (Number.isNaN(date.getTime())) return String(value);
        return new Intl.DateTimeFormat('en-GB', {
            day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC'
        }).format(date);
    }

    function compactNumber(value, maximumFractionDigits = 2) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        return new Intl.NumberFormat('en-GB', {
            notation: 'compact', maximumFractionDigits
        }).format(number);
    }

    function displayValue(metric, value) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        const format = metric?.display_format;
        const unit = String(metric?.unit || '').toLowerCase();
        if (format === 'percentage' || unit === 'percent') return `${number.toFixed(Math.abs(number) < 10 ? 1 : 0)}%`;
        if (format === 'currency' || unit === 'usd') {
            const sign = number < 0 ? '-' : '';
            return `${sign}$${compactNumber(Math.abs(number))}`;
        }
        if (format === 'multiple') return `${number.toFixed(1)}x`;
        const suffix = metric?.unit && !['count', 'usd'].includes(unit) ? ` ${metric.unit}` : '';
        return `${compactNumber(number)}${suffix}`;
    }

    function axisPrefix(metric) {
        return metric?.display_format === 'currency' ? '$' : '';
    }

    function axisSuffix(metric) {
        if (metric?.display_format === 'percentage') return '%';
        const unit = String(metric?.unit || '');
        if (metric?.display_format === 'count' && unit && !['count', 'devices', 'vehicles', 'memberships', 'hours'].includes(unit.toLowerCase())) return ` ${unit}`;
        return '';
    }

    function periodDate(row) {
        return row?.end || row?.instant || row?.report_date || null;
    }

    function observationLabel(row) {
        const date = periodDate(row);
        const type = String(row?.period_type || '').toLowerCase();
        if (type === 'quarter' && date) {
            const d = new Date(`${date}T00:00:00Z`);
            if (!Number.isNaN(d.getTime())) return `Q${Math.floor(d.getUTCMonth() / 3) + 1} ${d.getUTCFullYear()}`;
        }
        if (type === 'annual' && date) return `FY ${String(date).slice(0, 4)}`;
        return date ? formatDate(date) : 'Reported period';
    }

    function comparablePrior(observations, latest) {
        const latestDate = new Date(`${periodDate(latest)}T00:00:00Z`);
        if (Number.isNaN(latestDate.getTime())) return null;
        const target = latestDate.getTime() - 365.25 * 24 * 60 * 60 * 1000;
        let best = null;
        let bestDistance = Infinity;
        for (const row of observations) {
            if (row === latest) continue;
            const dateValue = periodDate(row);
            if (!dateValue) continue;
            const date = new Date(`${dateValue}T00:00:00Z`).getTime();
            if (!Number.isFinite(date) || date >= latestDate.getTime()) continue;
            const distance = Math.abs(date - target);
            if (distance < bestDistance) {
                bestDistance = distance;
                best = row;
            }
        }
        return bestDistance <= 190 * 24 * 60 * 60 * 1000 ? best : null;
    }

    function yoyChange(metric, observations) {
        if (!Array.isArray(observations) || observations.length < 2) return null;
        const latest = observations[observations.length - 1];
        const prior = comparablePrior(observations, latest);
        const current = finiteNumber(latest?.value);
        const previous = finiteNumber(prior?.value);
        if (current === null || previous === null) return null;
        if (metric?.display_format === 'percentage') return { value: current - previous, suffix: 'pp' };
        if (previous === 0) return null;
        return { value: ((current - previous) / Math.abs(previous)) * 100, suffix: '%' };
    }

    function changeText(change) {
        if (!change) return '—';
        const sign = change.value > 0 ? '+' : '';
        return `${sign}${change.value.toFixed(1)}${change.suffix}`;
    }

    function changeClass(change) {
        if (!change) return 'text-gray-400';
        if (change.value > 0) return 'text-emerald-600';
        if (change.value < 0) return 'text-red-600';
        return 'text-gray-500';
    }

    function remember(map, key, value) {
        map.delete(key);
        map.set(key, { value, savedAt: Date.now() });
        while (map.size > MEMORY_MAX) map.delete(map.keys().next().value);
    }

    function recall(map, key) {
        const cached = map.get(key);
        if (!cached || Date.now() - cached.savedAt > MEMORY_TTL_MS) return null;
        return cached.value;
    }

    async function json(url, signal) {
        if (typeof fetchJsonWithRetry === 'function') return fetchJsonWithRetry(url, { signal }, 1);
        const response = await fetch(url, { signal });
        let payload = null;
        try { payload = await response.json(); } catch (_) {}
        if (!response.ok) {
            const error = new Error(payload?.detail || `Request failed (${response.status})`);
            error.status = response.status;
            throw error;
        }
        return payload;
    }

    function ensureStyles() {
        if (qs('#sethistock-driver-styles')) return;
        const style = document.createElement('style');
        style.id = 'sethistock-driver-styles';
        style.textContent = `
            #company-drivers { overscroll-behavior:contain; }
            .driver-period-btn.active { background:#2563eb; color:#fff; border-color:#2563eb; }
            .driver-card .modebar { display:none !important; }
            .driver-card { min-width:0; }
            @media (prefers-reduced-motion: reduce) { .driver-loading-pulse { animation:none !important; } }
        `;
        document.head.appendChild(style);
    }

    function closeDrivers(returnToRevenue = false) {
        if (controller) controller.abort();
        controller = null;
        const section = qs('#company-drivers');
        if (section) section.classList.add('hidden');
        document.body.classList.remove('modal-active');
        if (returnToRevenue) {
            const revenueCard = qs('[data-financial-card="ind-rev"]');
            if (revenueCard) requestAnimationFrame(() => revenueCard.scrollIntoView({ behavior: 'smooth', block: 'center' }));
        }
    }

    function ensureUI() {
        ensureStyles();
        if (qs('#company-drivers')) return;

        const section = document.createElement('section');
        section.id = 'company-drivers';
        section.className = 'hidden fixed inset-0 z-[210] bg-gray-50 overflow-y-auto';
        section.setAttribute('role', 'dialog');
        section.setAttribute('aria-modal', 'true');
        section.setAttribute('aria-label', 'Revenue drivers');
        section.innerHTML = `
            <div class="sticky top-0 z-20 bg-white/95 backdrop-blur-md border-b border-gray-200">
                <div class="max-w-[1800px] mx-auto px-5 md:px-8 py-3 flex items-center justify-between gap-4">
                    <button id="driver-back-button" type="button" class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm font-bold text-gray-700 hover:text-blue-700 hover:border-blue-300 hover:bg-blue-50 transition">
                        <span aria-hidden="true">←</span><span>Back to Financials</span>
                    </button>
                    <div class="flex items-center gap-2">
                        <span class="hidden sm:inline px-2.5 py-1 rounded-full bg-blue-50 border border-blue-100 text-[9px] font-black text-blue-700 uppercase tracking-widest">Filing-derived</span>
                        <button id="driver-close-button" type="button" aria-label="Close revenue drivers" class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-500 hover:text-gray-900 hover:border-gray-300 transition text-xl">×</button>
                    </div>
                </div>
            </div>

            <div class="max-w-[1800px] mx-auto px-5 md:px-8 py-7 md:py-9">
                <div class="mb-5 border-b border-gray-200 pb-5 flex flex-col xl:flex-row xl:items-end justify-between gap-4">
                    <div class="max-w-4xl">
                        <p class="text-[10px] font-black text-blue-600 uppercase tracking-[0.18em] mb-1">Company Drivers · Revenue Engine</p>
                        <h2 id="driver-view-title" class="text-3xl md:text-4xl font-black tracking-tight text-gray-900">Revenue Drivers</h2>
                        <p id="driver-theme" class="text-sm text-gray-500 mt-1.5">Revenue segments and direct operating drivers from verified company filings.</p>
                    </div>
                    <div class="flex flex-col items-start xl:items-end gap-2">
                        <div id="driver-period-controls" class="flex space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200" aria-label="Revenue driver period">
                            <button type="button" class="driver-period-btn active px-4 py-1.5 text-sm font-bold rounded-md text-gray-600 transition" data-driver-period="quarterly">Quarterly</button>
                            <button type="button" class="driver-period-btn px-4 py-1.5 text-sm font-bold rounded-md text-gray-600 transition" data-driver-period="annual">Annual</button>
                        </div>
                        <p id="driver-status" class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Open a supported stock to load revenue drivers</p>
                    </div>
                </div>

                <div id="driver-summary" class="hidden mb-4 rounded-xl border border-blue-100 bg-blue-50/60 px-4 py-2.5 text-[11px] text-blue-900"></div>
                <div id="driver-empty" class="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-14 text-center">
                    <p class="text-sm font-bold text-gray-600">Revenue-driver histories will appear here.</p>
                    <p class="text-xs text-gray-400 mt-1">Only verified filing histories are charted; missing periods are never estimated.</p>
                </div>
                <div id="driver-chart-grid" class="hidden grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-4"></div>
                <div id="driver-unavailable" class="hidden mt-4 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3"></div>
            </div>`;
        document.body.appendChild(section);

        qs('#driver-back-button', section)?.addEventListener('click', () => closeDrivers(true));
        qs('#driver-close-button', section)?.addEventListener('click', () => closeDrivers(false));
        qsa('.driver-period-btn', section).forEach(button => {
            button.addEventListener('click', () => {
                const next = button.dataset.driverPeriod;
                if (!PERIODS.includes(next) || next === activePeriod) return;
                activePeriod = next;
                syncPeriodButtons();
                if (activeTicker && latestRegistry && latestCoverage) {
                    renderDrivers(activeTicker, latestRegistry, latestCoverage, next).catch(() => null);
                }
            });
        });
    }

    function syncPeriodButtons() {
        qsa('.driver-period-btn').forEach(button => {
            button.classList.toggle('active', button.dataset.driverPeriod === activePeriod);
        });
    }

    function setStatus(text, tone = 'neutral') {
        const element = qs('#driver-status');
        if (!element) return;
        element.textContent = text;
        const colour = tone === 'error' ? 'text-red-600' : tone === 'live' ? 'text-blue-600' : tone === 'success' ? 'text-emerald-700' : 'text-gray-400';
        element.className = `text-[10px] font-bold uppercase tracking-widest ${colour}`;
    }

    function setTheme(registry) {
        const theme = qs('#driver-theme');
        const title = qs('#driver-view-title');
        if (title) title.textContent = `${registry?.company || activeTicker || ''} Revenue Drivers`.trim();
        if (!theme) return;
        const suffix = registry?.theme ? ` ${registry.theme}.` : '';
        theme.textContent = `Revenue segments and direct demand/volume drivers from verified company filings.${suffix}`;
    }

    function showEmpty(title, detail, tone = 'neutral') {
        const empty = qs('#driver-empty');
        const grid = qs('#driver-chart-grid');
        const summary = qs('#driver-summary');
        const unavailable = qs('#driver-unavailable');
        if (!empty || !grid) return;
        grid.classList.add('hidden');
        grid.innerHTML = '';
        summary?.classList.add('hidden');
        unavailable?.classList.add('hidden');
        empty.classList.remove('hidden');
        const titleClass = tone === 'error' ? 'text-red-600' : 'text-gray-700';
        empty.innerHTML = `<p class="text-sm font-bold ${titleClass}">${escapeHtml(title)}</p><p class="text-xs text-gray-400 mt-1">${escapeHtml(detail)}</p>`;
    }

    function selectedMetrics(registry, coverage, requireVerified = true) {
        const ticker = canonicalTicker(registry?.ticker || activeTicker);
        const allowed = new Set(REVENUE_DRIVER_KEYS[ticker] || []);
        const coverageMap = new Map((coverage?.metrics || []).map(row => [row.key, row]));
        return (registry?.metrics || []).filter(metric => {
            if (!allowed.has(metric.key)) return false;
            return !requireVerified || coverageMap.get(metric.key)?.verified === true;
        });
    }

    function renderLoadingCards(metrics) {
        const empty = qs('#driver-empty');
        const grid = qs('#driver-chart-grid');
        if (!grid) return;
        empty?.classList.add('hidden');
        grid.classList.remove('hidden');
        grid.innerHTML = metrics.map(metric => `
            <article id="driver-card-${escapeHtml(metric.key)}" class="driver-card bg-white p-4 rounded-2xl shadow-sm border border-gray-200 min-h-[300px]">
                <div class="flex items-start justify-between gap-3 mb-3">
                    <div class="min-w-0">
                        <p class="text-[9px] font-black text-blue-600 uppercase tracking-widest mb-1">${escapeHtml(humanCategory(metric.category))}</p>
                        <h4 class="text-sm font-black text-gray-900 leading-tight">${escapeHtml(metric.label)}</h4>
                    </div>
                    <span class="driver-loading-pulse animate-pulse h-5 w-16 rounded-full bg-gray-100 shrink-0"></span>
                </div>
                <div class="grid grid-cols-2 gap-2 mb-3"><div class="h-12 rounded-lg bg-gray-100 animate-pulse"></div><div class="h-12 rounded-lg bg-gray-100 animate-pulse"></div></div>
                <div class="h-[180px] rounded-xl bg-gray-50 animate-pulse"></div>
            </article>`).join('');
    }

    function renderUnavailableMetrics(registry, coverage) {
        const target = qs('#driver-unavailable');
        if (!target) return;
        const allowed = new Set((REVENUE_DRIVER_KEYS[canonicalTicker(registry?.ticker)] || []));
        const registryMap = new Map((registry?.metrics || []).map(metric => [metric.key, metric]));
        const rows = (coverage?.metrics || []).filter(row => allowed.has(row.key) && !row?.verified);
        if (!rows.length) {
            target.classList.add('hidden');
            target.innerHTML = '';
            return;
        }
        target.classList.remove('hidden');
        target.innerHTML = `<div class="flex flex-wrap items-center gap-2"><span class="text-[9px] font-black text-gray-400 uppercase tracking-widest mr-1">Not yet chartable</span>${rows.map(row => {
            const metric = registryMap.get(row.key);
            const reason = row.reason || metric?.notes || 'A verified comparable filing history is not available.';
            return `<span class="px-2 py-1 rounded-full bg-white border border-gray-200 text-[9px] font-bold text-gray-500" title="${escapeHtml(reason)}">${escapeHtml(row.label || metric?.label || row.key)}</span>`;
        }).join('')}</div>`;
    }

    function latestSource(observations) {
        for (let i = observations.length - 1; i >= 0; i -= 1) {
            if (observations[i]?.source_url || observations[i]?.accession || observations[i]?.filing_date) return observations[i];
        }
        return observations[observations.length - 1] || null;
    }

    function sourceFooter(metric, payload, observations) {
        const source = latestSource(observations);
        if (!source) return '<span class="text-gray-400">Source provenance unavailable</span>';
        const label = sourceLabel(payload?.source_mode, source);
        const filed = source.filing_date ? ` · ${formatDate(source.filing_date)}` : '';
        const link = /^https:\/\//i.test(String(source.source_url || ''))
            ? `<a href="${escapeHtml(source.source_url)}" target="_blank" rel="noopener noreferrer" class="font-black text-blue-600 hover:text-blue-800 transition">Filing ↗</a>`
            : '';
        return `<div class="flex items-center justify-between gap-2 text-[9px]"><span class="text-gray-400 truncate"><strong class="text-gray-600">${escapeHtml(label)}</strong>${escapeHtml(filed)}</span>${link}</div>`;
    }

    function renderSummary(histories) {
        const target = qs('#driver-summary');
        if (!target) return;
        const good = histories.filter(item => item?.payload?.observations?.length);
        if (!good.length) {
            target.classList.add('hidden');
            return;
        }
        const persisted = good.filter(item => item.payload.cache_persistent).length;
        target.classList.remove('hidden');
        target.innerHTML = `<div class="flex flex-wrap items-center gap-x-4 gap-y-1"><span><strong>${good.length}</strong> verified revenue-driver series</span><span><strong>${persisted}/${good.length}</strong> persisted in SethiStock</span><span class="text-blue-700 font-semibold">Every plotted point retains filing provenance.</span></div>`;
    }

    function annualObservationSet(observations) {
        if (activePeriod !== 'annual') return observations;
        const byYear = new Map();
        observations.forEach(row => {
            const date = String(periodDate(row) || '');
            const year = date.slice(0, 4);
            if (!year) return;
            const previous = byYear.get(year);
            if (!previous || String(periodDate(row)) >= String(periodDate(previous))) byYear.set(year, row);
        });
        return Array.from(byYear.values()).sort((a, b) => String(periodDate(a)).localeCompare(String(periodDate(b))));
    }

    function renderMetricCard(metric, payload) {
        const card = qs(`#driver-card-${CSS.escape(metric.key)}`);
        if (!card) return;
        let observations = Array.isArray(payload?.observations)
            ? payload.observations.filter(row => finiteNumber(row?.value) !== null && periodDate(row)).sort((a, b) => String(periodDate(a)).localeCompare(String(periodDate(b))))
            : [];
        observations = annualObservationSet(observations);

        if (!payload?.verified || !observations.length) {
            card.innerHTML = `<div class="flex min-h-[250px] items-center justify-center text-center px-5"><div><h4 class="text-sm font-black text-gray-800">${escapeHtml(metric.label)}</h4><p class="text-xs text-gray-400 mt-2">No verified ${escapeHtml(humanPeriod(activePeriod).toLowerCase())} observations.</p></div></div>`;
            return;
        }

        const latest = observations.at(-1);
        const change = yoyChange(metric, observations);
        const cacheBadge = payload.cache_persistent
            ? `<span class="px-2 py-1 rounded-full ${payload.cache_fresh ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-amber-50 border-amber-100 text-amber-700'} border text-[8px] font-black uppercase tracking-widest">${payload.cache_fresh ? 'Cached' : 'Refreshing'}</span>`
            : `<span class="px-2 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-[8px] font-black uppercase tracking-widest">Live SEC</span>`;

        card.innerHTML = `
            <div class="flex items-start justify-between gap-3 mb-2.5">
                <div class="min-w-0">
                    <p class="text-[9px] font-black text-blue-600 uppercase tracking-widest mb-0.5">${escapeHtml(humanCategory(metric.category))}</p>
                    <h4 class="text-sm font-black text-gray-900 leading-tight">${escapeHtml(metric.label)}</h4>
                </div>${cacheBadge}
            </div>
            <div class="grid grid-cols-2 gap-2 mb-1.5">
                <div class="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2">
                    <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Latest</p>
                    <p class="text-lg font-black text-gray-900 mt-0.5">${escapeHtml(displayValue(metric, latest.value))}</p>
                    <p class="text-[9px] font-semibold text-gray-400">${escapeHtml(observationLabel(latest))}</p>
                </div>
                <div class="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2">
                    <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest">YoY</p>
                    <p class="text-lg font-black mt-0.5 ${changeClass(change)}">${escapeHtml(changeText(change))}</p>
                    <p class="text-[9px] font-semibold text-gray-400">${observations.length} observations</p>
                </div>
            </div>
            <div id="driver-chart-${escapeHtml(metric.key)}" class="w-full h-[180px]"></div>
            <div class="border-t border-gray-100 pt-2 mt-1">${sourceFooter(metric, payload, observations)}</div>`;
        drawMetricChart(metric, payload, observations);
    }

    function drawMetricChart(metric, payload, observations) {
        const target = qs(`#driver-chart-${CSS.escape(metric.key)}`);
        if (!target || typeof Plotly === 'undefined') return;
        const dates = activePeriod === 'annual'
            ? observations.map(row => String(periodDate(row)).slice(0, 4))
            : observations.map(periodDate);
        const values = observations.map(row => Number(row.value));
        const customdata = observations.map(row => [
            observationLabel(row),
            row.filing_date ? formatDate(row.filing_date) : 'N/A',
            sourceLabel(payload?.source_mode, row),
            row.accession || 'N/A'
        ]);
        const isLine = ['percentage', 'multiple'].includes(metric?.display_format) || ['ratio', 'growth'].includes(metric?.value_kind);
        const trace = isLine ? {
            x: dates, y: values, type: 'scatter', mode: 'lines+markers', connectgaps: false,
            line: { color: '#2563eb', width: 2 },
            marker: { size: 5, color: '#ffffff', line: { color: '#2563eb', width: 1.5 } },
            customdata,
            hovertemplate: `<b>${escapeHtml(metric.label)}</b><br>%{customdata[0]}<br>Value: %{y:,.2f}${escapeHtml(axisSuffix(metric))}<br>Filed: %{customdata[1]}<br>Source: %{customdata[2]}<extra></extra>`
        } : {
            x: dates, y: values, type: 'bar', marker: { color: '#2563eb' }, customdata,
            hovertemplate: `<b>${escapeHtml(metric.label)}</b><br>%{customdata[0]}<br>Value: ${escapeHtml(axisPrefix(metric))}%{y:,.3s}${escapeHtml(axisSuffix(metric))}<br>Filed: %{customdata[1]}<br>Source: %{customdata[2]}<extra></extra>`
        };

        Plotly.react(target, [trace], {
            paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { t: 6, r: 6, b: 30, l: 44 },
            font: { color: '#64748b', size: 9 }, showlegend: false, hovermode: 'closest',
            hoverlabel: { bgcolor: '#ffffff', bordercolor: '#cbd5e1', font: { color: '#0f172a', size: 11 }, namelength: -1 },
            xaxis: {
                type: activePeriod === 'annual' ? 'category' : 'date',
                gridcolor: '#f8fafc', tickformat: activePeriod === 'annual' ? undefined : '%b %y',
                nticks: activePeriod === 'annual' ? 10 : 7, fixedrange: true, automargin: true
            },
            yaxis: { gridcolor: '#eef2f7', zerolinecolor: '#cbd5e1', tickprefix: axisPrefix(metric), ticksuffix: axisSuffix(metric), tickformat: metric?.display_format === 'percentage' ? '.1f' : '~s', fixedrange: true, automargin: true },
            bargap: 0.25
        }, { displayModeBar: false, responsive: true });
    }

    async function getMetadata(ticker, signal) {
        const cached = recall(metaCache, ticker);
        if (cached) return cached;
        const [registry, coverage] = await Promise.all([
            json(`${DRIVER_API}/api/drivers/${encodeURIComponent(ticker)}`, signal),
            json(`${DRIVER_API}/api/drivers/${encodeURIComponent(ticker)}/coverage`, signal)
        ]);
        const value = { registry, coverage };
        remember(metaCache, ticker, value);
        return value;
    }

    async function getHistory(ticker, metricKey, period, signal) {
        const cacheKey = `${ticker}|${metricKey}|${period}`;
        const cached = recall(historyCache, cacheKey);
        if (cached) return cached;
        const query = new URLSearchParams({ filings: '16', period, limit: '40' });
        const payload = await json(`${DRIVER_API}/api/drivers/${encodeURIComponent(ticker)}/history/${encodeURIComponent(metricKey)}?${query.toString()}`, signal);
        remember(historyCache, cacheKey, payload);
        return payload;
    }

    async function mapConcurrent(items, limit, worker) {
        const results = new Array(items.length);
        let index = 0;
        async function runner() {
            while (index < items.length) {
                const current = index++;
                try { results[current] = await worker(items[current], current); }
                catch (error) { results[current] = { error }; }
            }
        }
        await Promise.all(Array.from({ length: Math.min(limit, items.length) }, () => runner()));
        return results;
    }

    async function prefetchPeriod(ticker, registry, coverage, period, generation) {
        const metrics = selectedMetrics(registry, coverage, true);
        if (!metrics.length) return;
        await mapConcurrent(metrics, PREFETCH_PARALLEL, async metric => {
            if (generation !== prefetchGeneration || activeTicker !== ticker) return null;
            try { return await getHistory(ticker, metric.key, period); } catch (_) { return null; }
        });
    }

    function scheduleAdjacentPeriodPrefetch(ticker, registry, coverage, generation) {
        const run = () => prefetchPeriod(ticker, registry, coverage, 'annual', generation);
        if (typeof requestIdleCallback === 'function') requestIdleCallback(() => run().catch(() => null), { timeout: 1400 });
        else setTimeout(() => run().catch(() => null), 500);
    }

    async function renderDrivers(ticker, registry, coverage, period = activePeriod) {
        const thisRequest = ++requestId;
        if (controller) controller.abort();
        controller = new AbortController();
        const signal = controller.signal;
        activePeriod = period;
        syncPeriodButtons();
        setTheme(registry);

        const metrics = selectedMetrics(registry, coverage, true);
        renderUnavailableMetrics(registry, coverage);
        if (!metrics.length) {
            showEmpty(`${registry?.company || ticker} has no verified revenue-driver history yet.`, 'The filing registry is preserved, but only comparable revenue segments and direct demand drivers are shown here.');
            setStatus(`${ticker} revenue-driver history not yet chart-ready`, 'neutral');
            return;
        }

        renderLoadingCards(metrics);
        setStatus(`Loading ${humanPeriod(period).toLowerCase()} ${ticker} revenue drivers…`, 'live');
        const histories = await mapConcurrent(metrics, MAX_PARALLEL, async metric => {
            const payload = await getHistory(ticker, metric.key, period, signal);
            if (thisRequest !== requestId) return { metric, stale: true };
            renderMetricCard(metric, payload);
            return { metric, payload };
        });
        if (thisRequest !== requestId) return;

        const successes = histories.filter(item => item?.payload?.observations?.length);
        const errors = histories.filter(item => item?.error);
        renderSummary(histories);
        setStatus(successes.length
            ? `${ticker} · ${successes.length}/${metrics.length} ${humanPeriod(period).toLowerCase()} revenue-driver series loaded`
            : `${ticker} ${humanPeriod(period).toLowerCase()} revenue-driver history unavailable`,
            successes.length && !errors.length ? 'success' : successes.length ? 'neutral' : 'error');
        controller = null;
    }

    async function loadCompanyDrivers(ticker) {
        ensureUI();
        const symbol = canonicalTicker(ticker);
        if (!symbol || !supportsTicker(symbol)) {
            showEmpty(`Revenue Drivers are not yet available for ${symbol || 'this security'}.`, 'Current coverage is limited to the Phase 3 flagship universe.');
            setStatus('Outside current revenue-driver coverage', 'neutral');
            return;
        }

        activeTicker = symbol;
        const section = qs('#company-drivers');
        if (section?.dataset) section.dataset.expectedTicker = symbol;
        const generation = ++prefetchGeneration;
        latestRegistry = null;
        latestCoverage = null;
        setTheme(null);
        setStatus(`Checking ${symbol} revenue-driver coverage…`, 'live');
        showEmpty(`Loading ${symbol} Revenue Drivers…`, 'Checking the verified filing registry and persistent driver cache.');

        const localRequest = ++requestId;
        const metadataController = new AbortController();
        try {
            const { registry, coverage } = await getMetadata(symbol, metadataController.signal);
            if (localRequest !== requestId || activeTicker !== symbol) return;
            latestRegistry = registry;
            latestCoverage = coverage;
            setTheme(registry);
            await renderDrivers(symbol, registry, coverage, activePeriod);
            if (activePeriod === 'quarterly') scheduleAdjacentPeriodPrefetch(symbol, registry, coverage, generation);
        } catch (error) {
            if (error?.name === 'AbortError' || localRequest !== requestId) return;
            if (error?.status === 404) {
                showEmpty(`Revenue Drivers are not yet available for ${symbol}.`, 'The rest of SethiStock remains fully available.');
                setStatus(`${symbol} outside current coverage`, 'neutral');
            } else {
                showEmpty('Revenue Drivers are temporarily unavailable.', error?.message || 'The driver service could not be reached.', 'error');
                setStatus('Revenue-driver service temporarily unavailable', 'error');
            }
        }
    }

    async function openDrivers(ticker) {
        ensureUI();
        const symbol = canonicalTicker(ticker || (typeof state === 'object' ? state?.ticker : '') || qs('#display-ticker')?.textContent);
        if (!supportsTicker(symbol)) return false;
        const section = qs('#company-drivers');
        section?.classList.remove('hidden');
        document.body.classList.add('modal-active');
        activePeriod = 'quarterly';
        syncPeriodButtons();
        await loadCompanyDrivers(symbol);
        return true;
    }

    function boot() {
        ensureUI();
        document.addEventListener('keydown', event => {
            if (event.key === 'Escape' && !qs('#company-drivers')?.classList.contains('hidden')) closeDrivers(false);
        });
    }

    window.SethiStockCompanyDrivers = {
        get ticker() { return activeTicker; },
        get period() { return activePeriod; },
        get verifiedCount() { return latestCoverage?.verified_count || 0; },
        supports: supportsTicker,
        open: openDrivers,
        close: closeDrivers,
        load: loadCompanyDrivers,
        setPeriod(period) {
            if (!PERIODS.includes(period)) return Promise.resolve(null);
            activePeriod = period;
            syncPeriodButtons();
            if (!activeTicker || !latestRegistry || !latestCoverage) return Promise.resolve(null);
            return renderDrivers(activeTicker, latestRegistry, latestCoverage, period);
        }
    };

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
    else boot();
})();
