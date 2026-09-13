// SethiStock Phase 3E — dynamic company-specific operating-driver UI.
// Builds on the verified Phase 3C histories and Phase 3D persistent cache without
// blocking the rest of SethiStock. Missing periods are never interpolated.

(() => {
    'use strict';

    const DRIVER_API = typeof API_URL === 'string' ? API_URL : 'https://sethistock-api.onrender.com';
    const PERIODS = ['quarterly', 'annual', 'reported'];
    const MEMORY_TTL_MS = 30 * 60 * 1000;
    const MEMORY_MAX = 120;
    const MAX_PARALLEL = 3;
    const PREFETCH_PARALLEL = 2;

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
        return period === 'annual' ? 'Annual' : period === 'reported' ? 'Reported' : 'Quarterly';
    }

    function humanCategory(category) {
        return String(category || 'operating driver')
            .replaceAll('_', ' ')
            .replace(/\b\w/g, char => char.toUpperCase());
    }

    function sourceLabel(sourceMode, observation) {
        const mode = String(sourceMode || observation?.extraction_method || '').toLowerCase();
        if (mode.includes('table')) return 'SEC filing table';
        if (mode.includes('derived')) return 'Derived SEC ratio';
        if (mode.includes('inline') || mode.includes('xbrl')) return 'Inline XBRL';
        return 'SEC filing';
    }

    function formatDate(value) {
        if (!value) return '';
        const date = new Date(`${String(value).slice(0, 10)}T00:00:00Z`);
        if (Number.isNaN(date.getTime())) return String(value);
        return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(date);
    }

    function compactNumber(value, maximumFractionDigits = 2) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        return new Intl.NumberFormat('en-GB', {
            notation: 'compact',
            maximumFractionDigits
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

        if (metric?.display_format === 'percentage') {
            return { value: current - previous, label: 'YoY Δ', suffix: 'pp' };
        }
        if (previous === 0) return null;
        return { value: ((current - previous) / Math.abs(previous)) * 100, label: 'YoY', suffix: '%' };
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
            #company-drivers { scroll-margin-top: 8rem; }
            .driver-period-btn.active { background-color:#2563eb; color:#fff; border-color:#2563eb; }
            .driver-card .modebar { display:none !important; }
            @media (prefers-reduced-motion: reduce) { .driver-loading-pulse { animation:none !important; } }
        `;
        document.head.appendChild(style);
    }

    function ensureNavigation() {
        qsa('nav').forEach(nav => {
            if (qs('a[href="#company-drivers"]', nav)) return;
            const financialLink = qs('a[href="#key-metrics"]', nav);
            if (!financialLink) return;
            financialLink.insertAdjacentHTML('afterend', '<a href="#company-drivers" class="hover:text-blue-600 transition">Drivers</a>');
        });
    }

    function ensureUI() {
        ensureStyles();
        ensureNavigation();
        if (qs('#company-drivers')) return;
        const comparisons = qs('#comparisons');
        const financials = qs('#key-metrics');
        if (!comparisons || !financials) return;

        const section = document.createElement('section');
        section.id = 'company-drivers';
        section.className = 'mt-10 scroll-mt-24';
        section.innerHTML = `
            <div class="mb-5 border-b border-gray-200 pb-4 flex flex-col lg:flex-row lg:items-end justify-between gap-4">
                <div class="max-w-4xl">
                    <div class="flex items-center gap-3 flex-wrap">
                        <h3 class="text-2xl font-black text-gray-900">Company Drivers</h3>
                        <span class="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-100 text-[10px] font-black text-blue-700 uppercase tracking-widest">Filing-derived</span>
                    </div>
                    <p id="driver-theme" class="text-sm text-gray-500 mt-1">Company-specific operating KPIs from verified SEC filing histories.</p>
                </div>
                <div class="flex flex-col items-start lg:items-end gap-2">
                    <div id="driver-period-controls" class="flex space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200" aria-label="Company driver period">
                        <button type="button" class="driver-period-btn active px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-bold rounded-md text-gray-600 transition" data-driver-period="quarterly">Quarterly</button>
                        <button type="button" class="driver-period-btn px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-bold rounded-md text-gray-600 transition" data-driver-period="annual">Annual</button>
                        <button type="button" class="driver-period-btn px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-bold rounded-md text-gray-600 transition" data-driver-period="reported">Reported</button>
                    </div>
                    <p id="driver-status" class="text-[11px] font-bold uppercase tracking-widest text-gray-400">Search a supported stock to load operating drivers</p>
                </div>
            </div>

            <div id="driver-summary" class="hidden mb-5 rounded-xl border border-blue-100 bg-blue-50/60 px-4 py-3 text-xs text-blue-900"></div>
            <div id="driver-empty" class="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-10 text-center">
                <p class="text-sm font-bold text-gray-600">Company Drivers will appear here for supported flagship companies.</p>
                <p class="text-xs text-gray-400 mt-1">Only verified filing histories are charted; missing periods are never estimated.</p>
            </div>
            <div id="driver-chart-grid" class="hidden grid grid-cols-1 xl:grid-cols-2 gap-6"></div>
            <div id="driver-unavailable" class="hidden mt-5 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3"></div>
        `;
        comparisons.parentNode.insertBefore(section, comparisons);

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
        element.className = `text-[11px] font-bold uppercase tracking-widest ${colour}`;
    }

    function setTheme(registry) {
        const theme = qs('#driver-theme');
        if (!theme) return;
        if (registry?.theme) {
            theme.textContent = `${registry.company || registry.ticker}: ${registry.theme}.`;
        } else {
            theme.textContent = 'Company-specific operating KPIs from verified SEC filing histories.';
        }
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

    function renderLoadingCards(metrics) {
        const empty = qs('#driver-empty');
        const grid = qs('#driver-chart-grid');
        if (!grid) return;
        empty?.classList.add('hidden');
        grid.classList.remove('hidden');
        grid.innerHTML = metrics.map(metric => `
            <article id="driver-card-${escapeHtml(metric.key)}" class="driver-card bg-white p-6 rounded-2xl shadow-sm border border-gray-200 min-h-[390px]">
                <div class="flex items-start justify-between gap-4 mb-5">
                    <div class="min-w-0">
                        <p class="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">${escapeHtml(humanCategory(metric.category))}</p>
                        <h4 class="text-lg font-black text-gray-900 leading-tight">${escapeHtml(metric.label)}</h4>
                    </div>
                    <span class="driver-loading-pulse animate-pulse h-6 w-20 rounded-full bg-gray-100 shrink-0"></span>
                </div>
                <div class="grid grid-cols-2 gap-3 mb-4">
                    <div class="h-16 rounded-xl bg-gray-100 animate-pulse"></div>
                    <div class="h-16 rounded-xl bg-gray-100 animate-pulse"></div>
                </div>
                <div class="h-[220px] rounded-xl bg-gray-50 animate-pulse"></div>
                <div class="mt-4 h-8 rounded-lg bg-gray-50 animate-pulse"></div>
            </article>
        `).join('');
    }

    function renderUnavailableMetrics(registry, coverage) {
        const target = qs('#driver-unavailable');
        if (!target) return;
        const rows = (coverage?.metrics || []).filter(row => !row?.verified);
        if (!rows.length) {
            target.classList.add('hidden');
            target.innerHTML = '';
            return;
        }
        const registryMap = new Map((registry?.metrics || []).map(metric => [metric.key, metric]));
        target.classList.remove('hidden');
        target.innerHTML = `
            <div class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4">
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest shrink-0">Tracked separately</p>
                <div class="flex flex-wrap gap-2">
                    ${rows.map(row => {
                        const metric = registryMap.get(row.key);
                        const reason = row.reason || metric?.notes || 'A verified continuous filing history is not available.';
                        return `<span class="px-2.5 py-1 rounded-full bg-white border border-gray-200 text-[10px] font-bold text-gray-500" title="${escapeHtml(reason)}">${escapeHtml(row.label || metric?.label || row.key)}</span>`;
                    }).join('')}
                </div>
            </div>
            <p class="text-[11px] text-gray-400 mt-2">These KPIs remain in the registry but are not charted until an official, comparable history is verified.</p>
        `;
    }

    function latestSource(observations) {
        for (let i = observations.length - 1; i >= 0; i -= 1) {
            if (observations[i]?.source_url || observations[i]?.accession || observations[i]?.filing_date) return observations[i];
        }
        return observations[observations.length - 1] || null;
    }

    function renderSummary(histories) {
        const target = qs('#driver-summary');
        if (!target) return;
        const good = histories.filter(item => item?.payload?.observations?.length);
        if (!good.length) {
            target.classList.add('hidden');
            return;
        }
        const dates = good.flatMap(item => item.payload.observations.map(periodDate).filter(Boolean));
        const fresh = good.filter(item => item.payload.cache_persistent && item.payload.cache_fresh).length;
        const persistent = good.filter(item => item.payload.cache_persistent).length;
        const earliest = dates.length ? dates.slice().sort()[0] : null;
        const latest = dates.length ? dates.slice().sort().at(-1) : null;
        target.classList.remove('hidden');
        target.innerHTML = `
            <div class="flex flex-wrap items-center gap-x-5 gap-y-1">
                <span><strong>${good.length}</strong> verified driver ${good.length === 1 ? 'series' : 'series'}</span>
                ${earliest && latest ? `<span><strong>${escapeHtml(formatDate(earliest))}</strong> → <strong>${escapeHtml(formatDate(latest))}</strong></span>` : ''}
                <span><strong>${persistent}/${good.length}</strong> persisted in SethiStock</span>
                ${persistent ? `<span><strong>${fresh}/${persistent}</strong> cache snapshots fresh</span>` : ''}
                <span class="text-blue-700 font-semibold">Every plotted observation retains filing provenance.</span>
            </div>
        `;
    }

    function sourceFooter(metric, payload, observations) {
        const source = latestSource(observations);
        if (!source) return '<span class="text-gray-400">Source provenance unavailable</span>';
        const label = sourceLabel(payload?.source_mode, source);
        const filed = source.filing_date ? `Filed ${formatDate(source.filing_date)}` : '';
        const accession = source.accession ? ` · ${source.accession}` : '';
        const link = /^https:\/\//i.test(String(source.source_url || ''))
            ? `<a href="${escapeHtml(source.source_url)}" target="_blank" rel="noopener noreferrer" class="font-black text-blue-600 hover:text-blue-800 transition">Open filing ↗</a>`
            : '';
        return `
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[10px]">
                <span class="text-gray-400"><strong class="text-gray-600">${escapeHtml(label)}</strong>${filed ? ` · ${escapeHtml(filed)}` : ''}${accession ? escapeHtml(accession) : ''}</span>
                ${link}
            </div>
        `;
    }

    function renderMetricCard(metric, payload) {
        const card = qs(`#driver-card-${CSS.escape(metric.key)}`);
        if (!card) return;
        const observations = Array.isArray(payload?.observations)
            ? payload.observations.filter(row => finiteNumber(row?.value) !== null && periodDate(row)).sort((a, b) => String(periodDate(a)).localeCompare(String(periodDate(b))))
            : [];

        if (!payload?.verified || !observations.length) {
            card.innerHTML = `
                <div class="flex items-start justify-between gap-4 mb-4">
                    <div><p class="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">${escapeHtml(humanCategory(metric.category))}</p><h4 class="text-lg font-black text-gray-900">${escapeHtml(metric.label)}</h4></div>
                    <span class="px-2.5 py-1 rounded-full bg-gray-50 border border-gray-200 text-[9px] font-black text-gray-400 uppercase tracking-widest">Unavailable</span>
                </div>
                <div class="flex min-h-[260px] items-center justify-center text-center px-8"><div><p class="text-sm font-bold text-gray-500">No verified ${escapeHtml(humanPeriod(activePeriod).toLowerCase())} observations.</p><p class="text-xs text-gray-400 mt-1">SethiStock will not infer missing operating KPIs.</p></div></div>
            `;
            return;
        }

        const latest = observations.at(-1);
        const change = yoyChange(metric, observations);
        const coverage = payload.coverage || {};
        const coverageText = coverage.start && coverage.end ? `${formatDate(coverage.start)} – ${formatDate(coverage.end)}` : `${observations.length} observations`;
        const cacheBadge = payload.cache_persistent
            ? `<span class="px-2.5 py-1 rounded-full ${payload.cache_fresh ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-amber-50 border-amber-100 text-amber-700'} border text-[9px] font-black uppercase tracking-widest">${payload.cache_fresh ? 'Cached' : 'Refreshing'}</span>`
            : `<span class="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-[9px] font-black uppercase tracking-widest">Live SEC</span>`;

        card.innerHTML = `
            <div class="flex items-start justify-between gap-4 mb-4">
                <div class="min-w-0">
                    <p class="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">${escapeHtml(humanCategory(metric.category))}</p>
                    <h4 class="text-lg font-black text-gray-900 leading-tight">${escapeHtml(metric.label)}</h4>
                    <p class="text-[11px] text-gray-400 mt-1 line-clamp-2">${escapeHtml(metric.description || '')}</p>
                </div>
                ${cacheBadge}
            </div>
            <div class="grid grid-cols-2 gap-3 mb-2">
                <div class="rounded-xl border border-gray-100 bg-gray-50 p-3">
                    <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Latest</p>
                    <p class="text-2xl font-black text-gray-900 mt-1">${escapeHtml(displayValue(metric, latest.value))}</p>
                    <p class="text-[10px] font-semibold text-gray-400 mt-0.5">${escapeHtml(observationLabel(latest))}</p>
                </div>
                <div class="rounded-xl border border-gray-100 bg-gray-50 p-3">
                    <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest">${escapeHtml(change?.label || 'YoY')}</p>
                    <p class="text-2xl font-black mt-1 ${changeClass(change)}">${escapeHtml(changeText(change))}</p>
                    <p class="text-[10px] font-semibold text-gray-400 mt-0.5">${escapeHtml(coverageText)}</p>
                </div>
            </div>
            <div id="driver-chart-${escapeHtml(metric.key)}" class="w-full h-[225px]"></div>
            <div class="border-t border-gray-100 pt-3 mt-2">${sourceFooter(metric, payload, observations)}</div>
        `;

        drawMetricChart(metric, payload, observations);
    }

    function drawMetricChart(metric, payload, observations) {
        const target = qs(`#driver-chart-${CSS.escape(metric.key)}`);
        if (!target || typeof Plotly === 'undefined') return;
        const dates = observations.map(periodDate);
        const values = observations.map(row => Number(row.value));
        const customdata = observations.map(row => [
            observationLabel(row),
            row.filing_date ? formatDate(row.filing_date) : 'N/A',
            sourceLabel(payload?.source_mode, row),
            row.accession || 'N/A',
            row.derived ? 'Derived from matching filed observations' : 'Reported observation'
        ]);
        const isLine = ['percentage', 'multiple'].includes(metric?.display_format) || ['ratio', 'growth', 'balance'].includes(metric?.value_kind);
        const trace = isLine ? {
            x: dates,
            y: values,
            type: 'scatter',
            mode: 'lines+markers',
            connectgaps: false,
            line: { color: '#2563eb', width: 2.25 },
            marker: { size: 6, color: '#ffffff', line: { color: '#2563eb', width: 2 } },
            customdata,
            hovertemplate: `<b>${escapeHtml(metric.label)}</b><br>%{customdata[0]}<br>Value: %{y:,.2f}${escapeHtml(axisSuffix(metric))}<br>Filed: %{customdata[1]}<br>Source: %{customdata[2]}<br>Accession: %{customdata[3]}<br>%{customdata[4]}<extra></extra>`
        } : {
            x: dates,
            y: values,
            type: 'bar',
            marker: { color: '#2563eb' },
            customdata,
            hovertemplate: `<b>${escapeHtml(metric.label)}</b><br>%{customdata[0]}<br>Value: ${escapeHtml(axisPrefix(metric))}%{y:,.3s}${escapeHtml(axisSuffix(metric))}<br>Filed: %{customdata[1]}<br>Source: %{customdata[2]}<br>Accession: %{customdata[3]}<br>%{customdata[4]}<extra></extra>`
        };

        Plotly.react(target, [trace], {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { t: 12, r: 12, b: 42, l: 52 },
            font: { color: '#6b7280', size: 10 },
            showlegend: false,
            hovermode: 'closest',
            xaxis: { gridcolor: '#f3f4f6', tickformat: '%b %y', fixedrange: true },
            yaxis: {
                gridcolor: '#e5e7eb',
                fixedrange: true,
                tickprefix: axisPrefix(metric),
                ticksuffix: axisSuffix(metric),
                exponentformat: 'SI',
                separatethousands: true
            }
        }, { displayModeBar: false, responsive: true });
    }

    function renderCardError(metric, error) {
        const card = qs(`#driver-card-${CSS.escape(metric.key)}`);
        if (!card) return;
        card.innerHTML = `
            <div class="flex items-start justify-between gap-4 mb-4">
                <div><p class="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">${escapeHtml(humanCategory(metric.category))}</p><h4 class="text-lg font-black text-gray-900">${escapeHtml(metric.label)}</h4></div>
                <span class="px-2.5 py-1 rounded-full bg-red-50 border border-red-100 text-[9px] font-black text-red-600 uppercase tracking-widest">Unavailable</span>
            </div>
            <div class="flex min-h-[260px] items-center justify-center text-center px-8"><div><p class="text-sm font-bold text-gray-500">Driver history could not be loaded.</p><p class="text-xs text-gray-400 mt-1">${escapeHtml(error?.message || 'Temporary data error')}</p></div></div>
        `;
    }

    async function mapConcurrent(items, limit, worker) {
        const results = new Array(items.length);
        let cursor = 0;
        async function run() {
            while (cursor < items.length) {
                const index = cursor++;
                try {
                    results[index] = await worker(items[index], index);
                } catch (error) {
                    results[index] = { error, item: items[index] };
                }
            }
        }
        await Promise.all(Array.from({ length: Math.min(limit, items.length) }, run));
        return results;
    }

    async function getMetadata(ticker, signal) {
        const cacheKey = ticker;
        const cached = recall(metaCache, cacheKey);
        if (cached) return cached;
        const [registry, coverage] = await Promise.all([
            json(`${DRIVER_API}/api/drivers/${encodeURIComponent(ticker)}`, signal),
            json(`${DRIVER_API}/api/drivers/${encodeURIComponent(ticker)}/coverage`, signal)
        ]);
        const value = { registry, coverage };
        remember(metaCache, cacheKey, value);
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

    async function prefetchPeriod(ticker, registry, coverage, period, generation) {
        const coverageMap = new Map((coverage?.metrics || []).map(row => [row.key, row]));
        const verifiedMetrics = (registry?.metrics || []).filter(metric => coverageMap.get(metric.key)?.verified === true);
        if (!verifiedMetrics.length) return;

        await mapConcurrent(verifiedMetrics, PREFETCH_PARALLEL, async metric => {
            if (generation !== prefetchGeneration || activeTicker !== ticker) return null;
            try {
                return await getHistory(ticker, metric.key, period);
            } catch (_) {
                // Background hydration must never interrupt the visible Quarterly UI.
                return null;
            }
        });
    }

    function scheduleAdjacentPeriodPrefetch(ticker, registry, coverage, generation) {
        const run = async () => {
            if (generation !== prefetchGeneration || activeTicker !== ticker) return;
            await prefetchPeriod(ticker, registry, coverage, 'annual', generation);
            if (generation !== prefetchGeneration || activeTicker !== ticker) return;
            await prefetchPeriod(ticker, registry, coverage, 'reported', generation);
        };
        if (typeof requestIdleCallback === 'function') requestIdleCallback(() => run().catch(() => null), { timeout: 1200 });
        else setTimeout(() => run().catch(() => null), 300);
    }

    async function renderDrivers(ticker, registry, coverage, period = activePeriod) {
        const thisRequest = ++requestId;
        if (controller) controller.abort();
        controller = new AbortController();
        const signal = controller.signal;
        activePeriod = period;
        syncPeriodButtons();
        setTheme(registry);

        const coverageMap = new Map((coverage?.metrics || []).map(row => [row.key, row]));
        const verifiedMetrics = (registry?.metrics || []).filter(metric => coverageMap.get(metric.key)?.verified === true);
        renderUnavailableMetrics(registry, coverage);

        if (!verifiedMetrics.length) {
            showEmpty(`${registry?.company || ticker} has no verified filing-driver history yet.`, 'The registry is preserved, but SethiStock only charts operating KPIs after a comparable official history is verified.');
            setStatus(`${ticker} driver history not yet chart-ready`, 'neutral');
            return;
        }

        renderLoadingCards(verifiedMetrics);
        setStatus(`Loading ${humanPeriod(period).toLowerCase()} ${ticker} drivers…`, 'live');
        const histories = await mapConcurrent(verifiedMetrics, MAX_PARALLEL, async metric => {
            const payload = await getHistory(ticker, metric.key, period, signal);
            if (thisRequest !== requestId) return { metric, stale: true };
            renderMetricCard(metric, payload);
            return { metric, payload };
        });

        if (thisRequest !== requestId) return;
        const successes = histories.filter(item => item?.payload?.observations?.length);
        const errors = histories.filter(item => item?.error);
        errors.forEach(item => {
            if (item.item) renderCardError(item.item, item.error);
        });
        renderSummary(histories);

        if (successes.length) {
            setStatus(`${ticker} · ${successes.length}/${verifiedMetrics.length} ${humanPeriod(period).toLowerCase()} driver series loaded`, errors.length ? 'neutral' : 'success');
        } else {
            setStatus(`${ticker} ${humanPeriod(period).toLowerCase()} driver history unavailable`, 'error');
        }
        controller = null;
    }

    async function loadCompanyDrivers(ticker) {
        ensureUI();
        const requestedSymbol = String(ticker || '').trim().toUpperCase();
        if (!requestedSymbol) return;
        const symbol = requestedSymbol === 'GOOG' ? 'GOOGL' : requestedSymbol;
        activeTicker = symbol;
        const thisPrefetchGeneration = ++prefetchGeneration;
        latestRegistry = null;
        latestCoverage = null;
        setTheme(null);
        setStatus(`Checking ${symbol} driver coverage…`, 'live');
        showEmpty(`Checking ${symbol} Company Drivers…`, 'Loading the verified KPI registry and filing coverage.');

        const metadataController = new AbortController();
        const localRequest = ++requestId;
        try {
            const { registry, coverage } = await getMetadata(symbol, metadataController.signal);
            if (localRequest !== requestId || activeTicker !== symbol) return;
            latestRegistry = registry;
            latestCoverage = coverage;
            setTheme(registry);
            await renderDrivers(symbol, registry, coverage, activePeriod);
            // Quarterly is the visible default. Hydrate Annual (then Reported) quietly
            // once the first render is complete so tab switches reuse memory/Supabase.
            if (activePeriod === 'quarterly') {
                scheduleAdjacentPeriodPrefetch(symbol, registry, coverage, thisPrefetchGeneration);
            }
        } catch (error) {
            if (error?.name === 'AbortError' || localRequest !== requestId) return;
            if (error?.status === 404) {
                showEmpty(`Company Drivers are not yet available for ${symbol}.`, 'The rest of SethiStock remains fully available. Driver coverage currently focuses on the flagship Phase 3 universe.');
                setStatus(`${symbol} outside current driver coverage`, 'neutral');
            } else {
                showEmpty('Company Drivers are temporarily unavailable.', error?.message || 'The driver service could not be reached.', 'error');
                setStatus('Driver service temporarily unavailable', 'error');
            }
        }
    }

    function resolvedTicker() {
        const fromState = typeof state === 'object' ? String(state?.ticker || '').trim().toUpperCase() : '';
        const fromDisplay = qs('#display-ticker')?.textContent?.trim().toUpperCase() || '';
        return fromState || fromDisplay;
    }

    function waitForMainAnalysis(requestedValue) {
        ensureUI();
        const requested = String(requestedValue || '').trim().toUpperCase();
        setStatus(`Waiting for ${requested || 'stock'} analysis…`, 'live');
        let attempts = 0;
        const timer = setInterval(() => {
            attempts += 1;
            const dashboard = qs('#dashboard');
            const button = qs('#search-btn');
            const ticker = resolvedTicker();
            if (dashboard?.classList.contains('opacity-100') && !button?.disabled && ticker) {
                clearInterval(timer);
                if (ticker !== activeTicker || !latestRegistry) loadCompanyDrivers(ticker).catch(() => null);
            } else if (attempts >= 100) {
                clearInterval(timer);
                setStatus('Waiting for a successful stock analysis', 'neutral');
            }
        }, 250);
    }

    function boot() {
        ensureUI();
        const form = qs('#search-form');
        const input = qs('#ticker-input');
        if (form && form.dataset.companyDriversBound !== '1') {
            form.dataset.companyDriversBound = '1';
            form.addEventListener('submit', () => {
                waitForMainAnalysis(input?.value || 'stock');
            });
        }

        const existing = resolvedTicker();
        const dashboard = qs('#dashboard');
        if (existing && dashboard && !dashboard.classList.contains('hidden')) {
            waitForMainAnalysis(existing);
        }
    }

    window.SethiStockCompanyDrivers = {
        get ticker() { return activeTicker; },
        get period() { return activePeriod; },
        get verifiedCount() { return latestCoverage?.verified_count || 0; },
        load: loadCompanyDrivers,
        setPeriod(period) {
            if (!PERIODS.includes(period)) return Promise.resolve(null);
            activePeriod = period;
            syncPeriodButtons();
            if (!activeTicker || !latestRegistry || !latestCoverage) return Promise.resolve(null);
            return renderDrivers(activeTicker, latestRegistry, latestCoverage, period);
        }
    };

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
    else boot();
})();
