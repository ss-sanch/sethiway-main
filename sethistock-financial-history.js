// SethiStock Phase 2E — SEC-backed Annual / Quarterly / TTM financial history.
// Loaded after sethistock.html's legacy renderer so the existing stock endpoint remains
// an immediate fallback while the richer SEC history hydrates independently.

(() => {
    const PERIOD_LABELS = { annual: 'Annual', quarterly: 'Quarterly', ttm: 'TTM' };
    const SEC_METRICS = [
        'revenue', 'net_income', 'ebitda', 'gross_margin', 'operating_margin', 'net_margin',
        'operating_cash_flow', 'free_cash_flow', 'capex', 'cash', 'debt', 'shares'
    ];
    const BASE_SEC_METRICS = SEC_METRICS.filter(metric => metric !== 'ebitda');
    const FRONTEND_METRICS = {
        revenue: 'revenue',
        net_income: 'net',
        ebitda: 'ebitda',
        gross_margin: 'gross_margin',
        operating_margin: 'op_margin',
        net_margin: 'net_margin',
        operating_cash_flow: 'ocf',
        free_cash_flow: 'fcf',
        capex: 'capex',
        cash: 'cash',
        debt: 'debt',
        shares: 'shares'
    };
    const RATIO_KEYS = new Set(['gross_margin', 'op_margin', 'net_margin']);
    const FINANCIAL_CACHE_TTL_MS = 30 * 60 * 1000;
    const FINANCIAL_CACHE_MAX = 30;

    let financialTicker = '';
    let fallbackView = null;
    let displayedView = null;
    let desiredPeriod = 'annual';
    let desiredWindow = 'max';
    let expandedChartId = null;
    let prefetchGeneration = 0;
    let requestId = 0;
    let requestController = null;
    const financialMemoryCache = new Map();
    let researchData = null;
    let researchTicker = '';

    function finiteNumber(value) {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function humanPeriod(period) {
        return PERIOD_LABELS[period] || 'Annual';
    }

    function compactNumber(value) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        return new Intl.NumberFormat('en-GB', {
            notation: 'compact',
            maximumFractionDigits: Math.abs(number) >= 1e9 ? 2 : 1
        }).format(number);
    }

    function metricDisplayValue(key, value) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        if (RATIO_KEYS.has(key)) return `${number.toFixed(1)}%`;
        if (key === 'shares') return `${compactNumber(number)} shares`;
        return `$${compactNumber(number)}`;
    }

    function normaliseLegacyDate(year) {
        const match = String(year ?? '').match(/(19|20)\d{2}/);
        return match ? `${match[0]}-12-31` : String(year ?? '');
    }

    function metricPointsFromAligned(view, key) {
        const values = Array.isArray(view?.[key]) ? view[key] : [];
        const dates = Array.isArray(view?.dates) ? view.dates : [];
        const labels = Array.isArray(view?.labels) ? view.labels : [];
        const points = [];
        for (let index = 0; index < values.length; index++) {
            const value = finiteNumber(values[index]);
            if (value === null) continue;
            points.push({
                value,
                end: dates[index] || null,
                label: labels[index] || dates[index] || ''
            });
        }
        return points;
    }

    function buildLegacyView(fin) {
        const years = Array.isArray(fin?.years) ? fin.years.slice() : [];
        const dates = years.map(normaliseLegacyDate);
        const labels = years.map(year => String(year));
        const view = {
            period: 'annual',
            source: 'Legacy annual data',
            sourceType: 'legacy',
            dates,
            labels,
            years: labels,
            qualityWarnings: 0,
            periodCount: years.length,
            revenue: Array.isArray(fin?.revenue) ? fin.revenue.slice() : [],
            net: Array.isArray(fin?.net) ? fin.net.slice() : [],
            ebitda: Array.isArray(fin?.ebitda) ? fin.ebitda.slice() : [],
            gross_margin: Array.isArray(fin?.gross_margin) ? fin.gross_margin.slice() : [],
            op_margin: Array.isArray(fin?.op_margin) ? fin.op_margin.slice() : [],
            net_margin: Array.isArray(fin?.net_margin) ? fin.net_margin.slice() : [],
            fcf: Array.isArray(fin?.fcf) ? fin.fcf.slice() : [],
            ocf: Array.isArray(fin?.ocf) ? fin.ocf.slice() : [],
            capex: Array.isArray(fin?.capex) ? fin.capex.slice() : [],
            cash: Array.isArray(fin?.cash) ? fin.cash.slice() : [],
            debt: Array.isArray(fin?.debt) ? fin.debt.slice() : [],
            shares: Array.isArray(fin?.shares) ? fin.shares.slice() : [],
            metricPoints: {}
        };
        Object.keys(FRONTEND_METRICS).forEach(secMetric => {
            const key = FRONTEND_METRICS[secMetric];
            view.metricPoints[key] = metricPointsFromAligned(view, key);
        });
        return view;
    }

    function transformSecPayload(payload) {
        if (!payload || payload.period_engine_version !== '2d-v1' || !payload.metrics) {
            throw new Error('Historical fundamentals payload is unavailable.');
        }

        const dateSet = new Set();
        const labelByDate = new Map();
        const metricPoints = {};
        let qualityWarnings = 0;

        for (const [secMetric, frontendKey] of Object.entries(FRONTEND_METRICS)) {
            const metric = payload.metrics?.[secMetric] || {};
            const rawSeries = Array.isArray(metric.series) ? metric.series : [];
            const points = [];

            rawSeries.forEach(point => {
                const end = point?.end;
                let value = finiteNumber(point?.value);
                if (!end || value === null) return;
                if (RATIO_KEYS.has(frontendKey)) value *= 100;
                const label = point.label || end;
                points.push({ ...point, value, end, label });
                dateSet.add(end);
                if (!labelByDate.has(end) || secMetric === 'revenue') labelByDate.set(end, label);
            });
            points.sort((a, b) => String(a.end).localeCompare(String(b.end)));
            metricPoints[frontendKey] = points;

            const reconciliation = metric?.quality?.reconciliation_points || {};
            qualityWarnings += Number(reconciliation.basis_mismatch || 0);
        }

        const dates = Array.from(dateSet).sort();
        const labels = dates.map(date => labelByDate.get(date) || date);
        const view = {
            period: payload.period,
            source: payload.source || 'SEC EDGAR Company Facts',
            sourceType: 'sec',
            dates,
            labels,
            years: labels,
            fiscalCalendar: payload.fiscal_calendar || {},
            storage: payload.storage || null,
            metricPoints,
            qualityWarnings,
            periodCount: metricPoints.revenue?.length || 0
        };

        for (const key of Object.values(FRONTEND_METRICS)) {
            const byEnd = new Map((metricPoints[key] || []).map(point => [point.end, point.value]));
            view[key] = dates.map(date => byEnd.has(date) ? byEnd.get(date) : null);
        }
        return view;
    }

    function rememberFinancialView(key, view) {
        financialMemoryCache.delete(key);
        financialMemoryCache.set(key, { view, savedAt: Date.now() });
        while (financialMemoryCache.size > FINANCIAL_CACHE_MAX) {
            financialMemoryCache.delete(financialMemoryCache.keys().next().value);
        }
    }

    function setStatus(message, tone = 'neutral') {
        const element = document.getElementById('financial-history-status');
        if (!element) return;
        element.textContent = message;
        const toneClass = tone === 'error'
            ? 'text-red-600'
            : tone === 'success'
                ? 'text-emerald-700'
                : tone === 'loading'
                    ? 'text-blue-600'
                    : 'text-gray-400';
        element.className = `text-[11px] font-bold uppercase tracking-widest mt-2 text-right ${toneClass}`;
    }

    function setQualityAlert(view) {
        const alert = document.getElementById('financial-history-alert');
        if (!alert) return;
        if (view?.qualityWarnings > 0) {
            alert.textContent = 'Some reported quarters use a different accounting basis from later-restated annual figures. SethiStock preserves the reported periods and excludes incompatible windows from TTM calculations.';
            alert.classList.remove('hidden');
        } else {
            alert.classList.add('hidden');
            alert.textContent = '';
        }
    }

    function syncPeriodControls(period) {
        document.querySelectorAll('.financial-period-btn').forEach(button => {
            button.classList.toggle('active', button.dataset.financialPeriod === period);
        });
        const comparisonLabel = document.getElementById('comparison-period-label');
        if (comparisonLabel) comparisonLabel.textContent = humanPeriod(period);
    }

    function historyDescriptor(view) {
        if (!view) return 'Historical fundamentals unavailable';
        if (view.sourceType !== 'sec') return 'Legacy annual fallback';
        const points = view.metricPoints?.revenue || [];
        if (!points.length) return `SEC EDGAR · ${humanPeriod(view.period)}`;
        const first = points[0]?.label || points[0]?.end;
        const last = points[points.length - 1]?.label || points[points.length - 1]?.end;
        return `SEC EDGAR · ${first}–${last} · ${points.length} ${humanPeriod(view.period).toLowerCase()} periods`;
    }

    function validMetricPoints(view, key) {
        const stored = view?.metricPoints?.[key];
        if (Array.isArray(stored) && stored.length) {
            return stored.filter(point => finiteNumber(point.value) !== null);
        }
        return metricPointsFromAligned(view, key);
    }

    function cagrBetween(past, latest) {
        const pastValue = finiteNumber(past?.value);
        const latestValue = finiteNumber(latest?.value);
        if (pastValue === null || latestValue === null || pastValue <= 0 || latestValue <= 0) return 'N/A';
        const pastDate = new Date(past.end);
        const latestDate = new Date(latest.end);
        const elapsedYears = (latestDate - pastDate) / (365.25 * 24 * 60 * 60 * 1000);
        if (!Number.isFinite(elapsedYears) || elapsedYears <= 0.45) return 'N/A';
        const cagr = (Math.pow(latestValue / pastValue, 1 / elapsedYears) - 1) * 100;
        if (!Number.isFinite(cagr)) return 'N/A';
        return `${cagr > 0 ? '+' : ''}${cagr.toFixed(2)}%`;
    }

    function nearestHistoricalPoint(points, latest, yearsBack) {
        const target = new Date(latest.end);
        if (Number.isNaN(target.getTime())) return null;
        target.setUTCFullYear(target.getUTCFullYear() - yearsBack);
        let best = null;
        let bestDistance = Infinity;
        points.forEach(point => {
            if (point === latest) return;
            const date = new Date(point.end);
            if (Number.isNaN(date.getTime()) || date >= new Date(latest.end)) return;
            const distance = Math.abs(date - target);
            if (distance < bestDistance) {
                best = point;
                bestDistance = distance;
            }
        });
        // A quarterly period can move by several weeks across fiscal calendars; beyond
        // roughly half a year we no longer call it a comparable N-year observation.
        return bestDistance <= 190 * 24 * 60 * 60 * 1000 ? best : null;
    }

    function getGrowthStats(view, key) {
        const points = validMetricPoints(view, key);
        if (points.length < 2) return { '1Y': '-', '3Y': '-', '5Y': '-', 'MAX': '-' };
        const latest = points[points.length - 1];
        const result = {};
        [1, 3, 5].forEach(years => {
            const past = nearestHistoricalPoint(points, latest, years);
            result[`${years}Y`] = past ? cagrBetween(past, latest) : '-';
        });
        result.MAX = cagrBetween(points[0], latest);
        return result;
    }

    function growthColour(value) {
        if (!value || value === 'N/A' || value === '-') return 'text-gray-400';
        return value.startsWith('-') ? 'text-red-500' : 'text-green-500';
    }


    function deltaBetween(past, latest) {
        const pastValue = finiteNumber(past?.value);
        const latestValue = finiteNumber(latest?.value);
        if (pastValue === null || latestValue === null) return '-';
        const delta = latestValue - pastValue;
        return `${delta > 0 ? '+' : ''}${delta.toFixed(2)}pp`;
    }

    function getMarginDeltaStats(view) {
        const points = validMetricPoints(view, 'net_margin');
        if (points.length < 2) return { '1Y': '-', '3Y': '-', '5Y': '-', 'MAX': '-' };
        const latest = points[points.length - 1];
        const result = {};
        [1, 3, 5].forEach(years => {
            const past = nearestHistoricalPoint(points, latest, years);
            result[`${years}Y`] = past ? deltaBetween(past, latest) : '-';
        });
        result.MAX = deltaBetween(points[0], latest);
        return result;
    }

    function researchPct(value, digits = 1) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number.toFixed(digits)}%`;
    }

    function researchMult(value, digits = 1) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number.toFixed(digits)}x`;
    }

    function filterDatedItems(items, dateKey, windowValue = desiredWindow) {
        if (!Array.isArray(items) || !items.length || windowValue === 'max') return items || [];
        const years = Number(windowValue);
        if (!Number.isFinite(years) || years <= 0) return items;
        const valid = items.filter(item => !Number.isNaN(new Date(item?.[dateKey]).getTime()));
        if (!valid.length) return items;
        const latest = new Date(valid[valid.length - 1][dateKey]);
        const cutoff = new Date(latest);
        cutoff.setUTCFullYear(cutoff.getUTCFullYear() - years);
        return valid.filter(item => new Date(item[dateKey]) >= cutoff);
    }

    function statsForCard(card, view) {
        if (card.mode === 'margin') {
            const values = getMarginDeltaStats(view);
            return {
                labels: ['1Y Δ', '3Y Δ', '5Y Δ', 'MAX Δ'],
                values: ['1Y', '3Y', '5Y', 'MAX'].map(key => values[key]),
                classes: ['1Y', '3Y', '5Y', 'MAX'].map(key => growthColour(values[key]))
            };
        }
        if (card.mode === 'valuation') {
            const study = researchData?.valuation_bands;
            const bands = study?.bands || {};
            return {
                labels: ['Current', 'Median', 'Percentile', 'P25–P75'],
                values: [
                    researchMult(study?.current_pe),
                    researchMult(bands.median),
                    study?.current_percentile == null ? 'N/A' : researchPct(study.current_percentile, 0),
                    bands.p25 == null || bands.p75 == null ? 'N/A' : `${Number(bands.p25).toFixed(1)}–${Number(bands.p75).toFixed(1)}x`
                ],
                classes: ['text-blue-600', 'text-slate-700', 'text-blue-600', 'text-slate-500']
            };
        }
        if (card.mode === 'earnings') {
            const summary = researchData?.earnings_reaction?.summary || {};
            const avg5 = finiteNumber(summary.average_5d_move_pct);
            return {
                labels: ['Beat Rate', 'Avg |1D|', 'Avg 5D', 'Quarters'],
                values: [
                    researchPct(summary.eps_beat_rate_pct, 0),
                    researchPct(summary.average_abs_1d_move_pct),
                    researchPct(avg5),
                    summary.quarters == null ? 'N/A' : String(summary.quarters)
                ],
                classes: [
                    finiteNumber(summary.eps_beat_rate_pct) !== null && Number(summary.eps_beat_rate_pct) >= 50 ? 'text-green-600' : 'text-slate-700',
                    'text-slate-700',
                    avg5 === null ? 'text-gray-400' : (avg5 < 0 ? 'text-red-500' : 'text-green-600'),
                    'text-slate-500'
                ]
            };
        }
        const growth = getGrowthStats(view, card.key);
        return {
            labels: ['1Y CAGR', '3Y CAGR', '5Y CAGR', 'MAX'],
            values: ['1Y', '3Y', '5Y', 'MAX'].map(key => growth[key]),
            classes: ['1Y', '3Y', '5Y', 'MAX'].map(key => growthColour(growth[key]))
        };
    }

    function renderEarningsDetail() {
        const detail = document.getElementById('financial-detail-ind-earnings');
        if (!detail) return;
        const study = researchData?.earnings_reaction;
        if (!study?.available || !study.events?.length) {
            detail.innerHTML = '<div class="py-6 text-center text-sm font-semibold text-gray-400">Detailed earnings history is unavailable for this security.</div>';
            return;
        }
        const rows = study.events.map(event => {
            const surprise = finiteNumber(event.surprise_pct);
            const move1 = finiteNumber(event.move_1d_pct);
            const move5 = finiteNumber(event.move_5d_pct);
            const colour = value => value === null ? 'text-gray-400' : (value < 0 ? 'text-red-600' : 'text-green-600');
            return `<tr class="border-t border-gray-100">
                <td class="py-2.5 pr-3 font-bold text-gray-700 whitespace-nowrap">${event.earnings_date || '—'}</td>
                <td class="py-2.5 px-3 text-gray-600">${event.eps_estimate == null ? 'N/A' : Number(event.eps_estimate).toFixed(2)}</td>
                <td class="py-2.5 px-3 text-gray-600">${event.reported_eps == null ? 'N/A' : Number(event.reported_eps).toFixed(2)}</td>
                <td class="py-2.5 px-3 font-black ${colour(surprise)}">${surprise === null ? 'N/A' : researchPct(surprise)}</td>
                <td class="py-2.5 px-3 font-black ${colour(move1)}">${move1 === null ? 'N/A' : researchPct(move1)}</td>
                <td class="py-2.5 pl-3 font-black ${colour(move5)}">${move5 === null ? 'N/A' : researchPct(move5)}</td>
            </tr>`;
        }).join('');
        detail.innerHTML = `<div class="border-t border-gray-100 pt-3 mt-1">
            <div class="flex items-center justify-between gap-3 mb-2">
                <div><p class="text-[10px] font-black text-purple-600 uppercase tracking-widest">Event Detail</p><p class="text-xs text-gray-500">EPS result and subsequent share-price reaction.</p></div>
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Yahoo Finance · ${study.events.length} events</span>
            </div>
            <div class="overflow-x-auto max-h-[30vh] overflow-y-auto">
                <table class="w-full text-left text-xs">
                    <thead class="sticky top-0 bg-white text-gray-400 uppercase tracking-wider">
                        <tr><th class="py-2 pr-3">Earnings</th><th class="py-2 px-3">EPS Est.</th><th class="py-2 px-3">EPS Actual</th><th class="py-2 px-3">Surprise</th><th class="py-2 px-3">1D</th><th class="py-2 pl-3">5D</th></tr>
                    </thead><tbody>${rows}</tbody>
                </table>
            </div>
        </div>`;
    }

    async function loadFinancialResearch(ticker, generation = prefetchGeneration) {
        const symbol = String(ticker || '').trim().toUpperCase();
        if (!symbol) return null;
        try {
            const loader = typeof window.getSethiStockResearch === 'function'
                ? window.getSethiStockResearch(symbol)
                : fetch(`https://sethistock-api.onrender.com/api/research/${encodeURIComponent(symbol)}`).then(response => {
                    if (!response.ok) throw new Error(`Research API returned ${response.status}`);
                    return response.json();
                });
            const data = await loader;
            if (generation !== prefetchGeneration || symbol !== String(state.ticker || '').trim().toUpperCase()) return null;
            researchData = data;
            researchTicker = symbol;
            if (displayedView) {
                renderFinancialCards(displayedView);
                renderFinancialCharts(displayedView);
                if (expandedChartId === 'ind-earnings') renderEarningsDetail();
            }
            return data;
        } catch (error) {
            console.debug(`Phase 4A research cards unavailable for ${symbol}:`, error);
            return null;
        }
    }

    function syncWindowControls(windowValue) {
        document.querySelectorAll('.financial-window-btn').forEach(button => {
            button.classList.toggle('active', String(button.dataset.financialWindow) === String(windowValue));
        });
    }

    function filterPointsToWindow(points, windowValue = desiredWindow) {
        if (!Array.isArray(points) || !points.length || windowValue === 'max') return points || [];
        const years = Number(windowValue);
        if (!Number.isFinite(years) || years <= 0) return points;
        const latestDate = new Date(points[points.length - 1]?.end);
        if (Number.isNaN(latestDate.getTime())) return points;
        const cutoff = new Date(latestDate);
        cutoff.setUTCFullYear(cutoff.getUTCFullYear() - years);
        return points.filter(point => {
            const date = new Date(point?.end);
            return !Number.isNaN(date.getTime()) && date >= cutoff;
        });
    }

    function clearExpandedCardStyles(card) {
        if (!card) return;
        card.style.position = '';
        card.style.left = '';
        card.style.right = '';
        card.style.top = '';
        card.style.bottom = '';
        card.style.width = '';
        card.style.maxWidth = '';
        card.style.height = '';
        card.style.margin = '';
        card.style.transform = '';
        card.style.zIndex = '';
        card.style.boxShadow = '';
        card.style.overflow = '';
        const chartNode = card.querySelector('[id^="ind-"]');
        if (chartNode) chartNode.style.height = '';
        const detail = card.querySelector('[id^="financial-detail-"]');
        if (detail) detail.classList.add('hidden');
    }

    function toggleExpandedChart(chartId) {
        const card = document.querySelector(`[data-financial-card="${chartId}"]`);
        if (!card) return;
        const currentlyExpanded = expandedChartId === chartId;

        document.querySelectorAll('.financial-card').forEach(clearExpandedCardStyles);
        const existingBackdrop = document.getElementById('financial-chart-backdrop');
        if (existingBackdrop && existingBackdrop.parentNode) existingBackdrop.parentNode.removeChild(existingBackdrop);

        expandedChartId = currentlyExpanded ? null : chartId;
        document.body.classList.toggle('modal-active', Boolean(expandedChartId));
        if (!expandedChartId) {
            renderFinancialCharts(displayedView);
            requestAnimationFrame(() => Plotly.Plots.resize(chartId));
            return;
        }

        const backdrop = document.createElement('button');
        backdrop.id = 'financial-chart-backdrop';
        backdrop.type = 'button';
        backdrop.className = 'fixed inset-0 z-[150] bg-gray-900/55';
        backdrop.setAttribute('aria-label', 'Close expanded chart');
        backdrop.addEventListener('click', () => toggleExpandedChart(chartId));
        document.body.appendChild(backdrop);

        // Avoid transforms on the enlarged Plotly container. Transformed SVGs can
        // land on fractional pixels and render soft; fixed edges + auto margins stay crisp.
        card.style.position = 'fixed';
        card.style.left = '0';
        card.style.right = '0';
        card.style.top = '6vh';
        card.style.bottom = '6vh';
        card.style.width = 'calc(100vw - 48px)';
        card.style.maxWidth = '1280px';
        card.style.height = '88vh';
        card.style.margin = '0 auto';
        card.style.transform = 'none';
        card.style.zIndex = '160';
        card.style.boxShadow = '0 30px 70px rgba(15, 23, 42, 0.28)';
        card.style.overflow = chartId === 'ind-earnings' ? 'auto' : 'hidden';

        const chart = document.getElementById(chartId);
        const detail = document.getElementById(`financial-detail-${chartId}`);
        if (chartId === 'ind-earnings') {
            if (chart) chart.style.height = '38vh';
            if (detail) detail.classList.remove('hidden');
            renderEarningsDetail();
        } else if (chart) {
            chart.style.height = 'calc(88vh - 118px)';
        }
        // Wait for the fixed card to settle before Plotly measures its enlarged box.
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                renderFinancialCharts(displayedView);
                const expandedPlot = document.getElementById(chartId);
                if (expandedPlot) Plotly.Plots.resize(expandedPlot);
                setTimeout(() => {
                    if (expandedPlot?.isConnected) Plotly.Plots.resize(expandedPlot);
                }, 80);
            });
        });
    }

    function bindExpandButtons() {
        document.querySelectorAll('.financial-expand-btn').forEach(button => {
            button.addEventListener('click', () => toggleExpandedChart(button.dataset.chartId));
        });
    }

    function renderFinancialCards(view) {
        const cards = [
            { id: 'ind-rev', key: 'revenue', title: 'Revenue' },
            { id: 'ind-ebitda', key: 'ebitda', title: 'EBITDA' },
            { id: 'ind-net', key: 'net', title: 'Net Income' },
            { id: 'ind-margins', key: 'net_margin', title: 'Margin Profile', mode: 'margin' },
            { id: 'ind-ocf', key: 'ocf', title: 'Operating Cash Flow' },
            { id: 'ind-fcf', key: 'fcf', title: 'Free Cash Flow' },
            { id: 'ind-capex', key: 'capex', title: 'Capital Expenditure' },
            { id: 'ind-cash', key: 'cash', title: 'Cash Equivalents' },
            { id: 'ind-debt', key: 'debt', title: 'Total Debt' },
            { id: 'ind-shares', key: 'shares', title: 'Shares Outstanding' },
            { id: 'ind-pe', title: 'P/E (TTM) History', mode: 'valuation' },
            { id: 'ind-earnings', title: 'Earnings Surprise', mode: 'earnings' }
        ];
        const container = document.getElementById('individual-charts-container');
        if (!container) return;
        const periodLabel = humanPeriod(view?.period || 'annual');

        if (container.dataset?.phase4DashboardReady !== '1') {
            let html = '';
            cards.forEach(card => {
                const initialBadge = card.mode === 'valuation' ? 'TTM' : card.mode === 'earnings' ? 'Events' : periodLabel;
                html += `
                    <div class="financial-card bg-white px-4 pt-4 pb-3 rounded-2xl shadow-sm border border-gray-200 flex flex-col h-[330px] relative" data-financial-card="${card.id}">
                        <div class="flex items-center justify-between gap-3 mb-1">
                            <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">${card.title}</h4>
                            <div class="flex items-center gap-2">
                                <span id="fin-period-${card.id}" class="px-2 py-1 rounded-md bg-gray-50 border border-gray-100 text-[9px] font-black text-gray-400 uppercase tracking-widest">${initialBadge}</span>
                                <button type="button" class="financial-expand-btn inline-flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-400 hover:text-blue-600 hover:border-blue-300 hover:bg-blue-50 transition" data-chart-id="${card.id}" aria-label="Expand ${card.title} chart" title="Expand chart">
                                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
                                </button>
                            </div>
                        </div>
                        <div id="${card.id}" class="w-full flex-1 min-h-0 mt-0"></div>
                        <div id="financial-detail-${card.id}" class="hidden"></div>
                        <div class="grid grid-cols-4 gap-2 mt-1 pt-2.5 border-t border-gray-100">
                            ${[0,1,2,3].map(index => `<div class="text-center min-w-0"><p id="fin-label-${card.id}-${index}" class="text-[9px] text-gray-400 font-bold uppercase truncate">—</p><p id="fin-stat-${card.id}-${index}" class="font-semibold text-xs text-gray-400 truncate">-</p></div>`).join('')}
                        </div>
                    </div>`;
            });
            container.innerHTML = html;
            if (container.dataset) container.dataset.phase4DashboardReady = '1';
            bindExpandButtons();
        }

        cards.forEach(card => {
            const badge = document.getElementById(`fin-period-${card.id}`);
            if (badge) {
                if (card.mode === 'valuation') badge.textContent = 'TTM';
                else if (card.mode === 'earnings') badge.textContent = 'Events';
                else badge.textContent = view?.period === 'ttm' && ['cash', 'debt', 'shares'].includes(card.key)
                    ? 'Point-in-time'
                    : periodLabel;
            }
            const stats = statsForCard(card, view);
            for (let index = 0; index < 4; index += 1) {
                const label = document.getElementById(`fin-label-${card.id}-${index}`);
                const value = document.getElementById(`fin-stat-${card.id}-${index}`);
                if (label) label.textContent = stats.labels[index] || '—';
                if (value) {
                    value.textContent = stats.values[index] ?? '-';
                    value.className = `font-semibold text-xs ${stats.classes[index] || 'text-gray-400'} truncate`;
                }
            }
        });
    }

    function emptyChart(id, message = 'Data Unavailable') {
        const element = document.getElementById(id);
        if (element) element.innerHTML = `<div class="flex h-full items-center justify-center text-gray-400 font-bold text-sm text-center px-5">${message}</div>`;
    }

    function chartLayout(view, showLegend = false) {
        return {
            margin: { t: 6, b: showLegend ? 40 : 28, l: 44, r: 6 },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            showlegend: showLegend,
            autosize: true,
            hovermode: 'x unified',
            hoverlabel: {
                bgcolor: '#ffffff',
                bordercolor: '#cbd5e1',
                font: { color: '#0f172a', size: 12 },
                align: 'left',
                namelength: -1
            },
            xaxis: {
                type: 'date',
                showgrid: false,
                nticks: view.period === 'annual' ? 10 : 8,
                tickformat: view.period === 'annual' ? '%Y' : '%b %Y',
                tickfont: { color: '#64748b', size: 10 },
                automargin: true
            },
            yaxis: {
                showgrid: true,
                gridcolor: '#f1f5f9',
                zerolinecolor: '#e2e8f0',
                tickformat: '~s',
                tickfont: { color: '#64748b', size: 10 },
                automargin: true
            },
            legend: showLegend ? { orientation: 'h', xanchor: 'center', x: 0.5, y: -0.18, font: { size: 10 } } : undefined
        };
    }

    function traceForMetric(view, key, name, colour, options = {}) {
        const points = filterPointsToWindow(validMetricPoints(view, key));
        if (!points.length) return null;
        const annualBars = view.period === 'annual' && options.forceLine !== true;
        const trace = {
            x: points.map(point => point.end),
            y: points.map(point => point.value),
            name,
            customdata: points.map(point => point.label),
            text: points.map(point => metricDisplayValue(key, point.value)),
            hovertemplate: '%{customdata}<br>%{text}<extra></extra>'
        };
        if (annualBars) {
            trace.type = 'bar';
            trace.marker = { color: colour, line: { width: 0 } };
            trace.textposition = 'outside';
            trace.textfont = { color: '#334155', size: 10 };
            trace.cliponaxis = false;
        } else {
            trace.type = 'scatter';
            trace.mode = view.period === 'quarterly' ? 'lines+markers' : 'lines';
            trace.line = { color: colour, width: 2.4 };
            trace.marker = { color: colour, size: 5 };
            trace.connectgaps = false;
        }
        return trace;
    }

    function drawSingleMetric(view, id, key, colour, options = {}) {
        const trace = traceForMetric(view, key, options.name || key, colour, options);
        if (!trace) return emptyChart(id);
        const layout = chartLayout(view, false);
        if (RATIO_KEYS.has(key)) layout.yaxis.tickformat = '.1f';
        Plotly.react(id, [trace], layout, { displayModeBar: false, responsive: true });
    }

    function drawMargins(view) {
        const specs = [
            ['gross_margin', 'Gross (%)', '#8b5cf6'],
            ['op_margin', 'Operating (%)', '#22c55e'],
            ['net_margin', 'Net (%)', '#3b82f6']
        ];
        const traces = specs
            .map(([key, name, colour]) => traceForMetric(view, key, name, colour, { forceLine: true }))
            .filter(Boolean);
        if (!traces.length) return emptyChart('ind-margins');
        const layout = chartLayout(view, true);
        layout.yaxis.tickformat = '.1f';
        layout.yaxis.ticksuffix = '%';
        Plotly.react('ind-margins', traces, layout, { displayModeBar: false, responsive: true });
    }

    function drawHistoricalPE() {
        const study = researchData?.valuation_bands;
        if (!study?.available || !study.observations?.length) return emptyChart('ind-pe', researchData ? 'Historical P/E unavailable' : 'Loading valuation history…');
        const observations = filterDatedItems([...study.observations].sort((a, b) => String(a.date).localeCompare(String(b.date))), 'date');
        if (!observations.length) return emptyChart('ind-pe', 'No P/E observations in this window');
        const trace = {
            x: observations.map(item => item.date),
            y: observations.map(item => item.pe),
            type: 'scatter', mode: 'lines+markers',
            line: { color: '#2563eb', width: 2.4 },
            marker: { size: 5, color: '#ffffff', line: { color: '#2563eb', width: 1.5 } },
            customdata: observations.map(item => [item.price, item.ttm_eps]),
            hovertemplate: '%{x}<br>P/E: %{y:.1f}x<br>Price: $%{customdata[0]:.2f}<br>TTM EPS: %{customdata[1]:.3f}<extra></extra>'
        };
        const layout = chartLayout({ period: 'quarterly' }, false);
        layout.yaxis.tickformat = '.1f';
        layout.yaxis.ticksuffix = 'x';
        layout.shapes = [];
        const median = finiteNumber(study?.bands?.median);
        const current = finiteNumber(study?.current_pe);
        if (median !== null) layout.shapes.push({ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: median, y1: median, line: { color: '#94a3b8', width: 1.5, dash: 'dash' } });
        if (current !== null) layout.shapes.push({ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: current, y1: current, line: { color: '#111827', width: 1.5, dash: 'dot' } });
        Plotly.react('ind-pe', [trace], layout, { displayModeBar: false, responsive: true });
    }

    function drawEarningsSurprise() {
        const study = researchData?.earnings_reaction;
        if (!study?.available || !study.events?.length) return emptyChart('ind-earnings', researchData ? 'Earnings surprise history unavailable' : 'Loading earnings history…');
        const events = filterDatedItems([...study.events].sort((a, b) => String(a.earnings_date).localeCompare(String(b.earnings_date))), 'earnings_date')
            .filter(event => finiteNumber(event.surprise_pct) !== null);
        if (!events.length) return emptyChart('ind-earnings', 'No EPS surprise observations in this window');
        const y = events.map(event => Number(event.surprise_pct));
        const trace = {
            x: events.map(event => event.earnings_date),
            y,
            type: 'bar',
            marker: { color: y.map(value => value >= 0 ? '#16a34a' : '#dc2626') },
            customdata: events.map(event => [event.eps_estimate, event.reported_eps, event.move_1d_pct, event.move_5d_pct]),
            hovertemplate: '%{x}<br>EPS surprise: %{y:.1f}%<br>Estimate: %{customdata[0]}<br>Actual: %{customdata[1]}<br>1D: %{customdata[2]:.1f}%<br>5D: %{customdata[3]:.1f}%<extra></extra>'
        };
        const layout = chartLayout({ period: 'quarterly' }, false);
        layout.yaxis.tickformat = '.1f';
        layout.yaxis.ticksuffix = '%';
        layout.bargap = 0.28;
        Plotly.react('ind-earnings', [trace], layout, { displayModeBar: false, responsive: true });
    }

    function drawComparison(view, id, first, second) {
        const nonAnnual = view.period !== 'annual';
        const trace1 = traceForMetric(view, first.key, first.name, first.colour, { forceLine: nonAnnual });
        const trace2 = traceForMetric(view, second.key, second.name, second.colour, { forceLine: nonAnnual });
        const traces = [trace1, trace2].filter(Boolean);
        if (traces.length < 2) return emptyChart(id);
        const layout = chartLayout(view, true);
        if (view.period === 'annual') layout.barmode = 'group';
        Plotly.react(id, traces, layout, { displayModeBar: false, responsive: true });
    }

    function renderFinancialCharts(view) {
        if (!view) return;
        drawSingleMetric(view, 'ind-rev', 'revenue', '#3b82f6', { name: 'Revenue' });
        drawSingleMetric(view, 'ind-ebitda', 'ebitda', '#0f766e', { name: 'EBITDA' });
        drawSingleMetric(view, 'ind-net', 'net', '#a855f7', { name: 'Net Income' });
        drawMargins(view);
        drawSingleMetric(view, 'ind-ocf', 'ocf', '#10b981', { name: 'Operating Cash Flow' });
        drawSingleMetric(view, 'ind-fcf', 'fcf', '#059669', { name: 'Free Cash Flow' });
        drawSingleMetric(view, 'ind-capex', 'capex', '#ef4444', { name: 'Capital Expenditure' });
        drawSingleMetric(view, 'ind-cash', 'cash', '#0ea5e9', { name: 'Cash' });
        drawSingleMetric(view, 'ind-debt', 'debt', '#f97316', { name: 'Debt' });
        drawSingleMetric(view, 'ind-shares', 'shares', '#64748b', { name: 'Shares' });
        drawHistoricalPE();
        drawEarningsSurprise();

        drawComparison(view, 'comp-rev-net',
            { key: 'revenue', name: 'Revenue', colour: '#94a3b8' },
            { key: 'net', name: 'Net Income', colour: '#3b82f6' });
        drawComparison(view, 'comp-cash-debt',
            { key: 'cash', name: 'Cash', colour: '#0ea5e9' },
            { key: 'debt', name: 'Debt', colour: '#f97316' });
        drawComparison(view, 'comp-fcf-ocf',
            { key: 'ocf', name: 'Operating CF', colour: '#10b981' },
            { key: 'fcf', name: 'Free Cash Flow', colour: '#059669' });
        drawComparison(view, 'comp-ocf-capex',
            { key: 'ocf', name: 'Operating CF', colour: '#10b981' },
            { key: 'capex', name: 'CapEx', colour: '#ef4444' });
    }

    function renderView(view, statusTone = 'success', statusOverride = null) {
        displayedView = view;
        desiredPeriod = view.period || 'annual';
        state.financialPeriod = desiredPeriod;
        syncPeriodControls(desiredPeriod);
        renderFinancialCards(view);
        syncWindowControls(desiredWindow);
        renderFinancialCharts(view);
        setQualityAlert(view);
        setStatus(statusOverride || historyDescriptor(view), statusTone);
    }

    async function fetchSecHistoryPayload(ticker, period, signal = null) {
        const request = async metrics => {
            const query = new URLSearchParams({ period, metrics: metrics.join(','), limit: '200' });
            return fetchJsonWithRetry(
                `${API_URL}/api/sec/${encodeURIComponent(ticker)}/fundamentals/series?${query.toString()}`,
                signal ? { signal } : {},
                1
            );
        };
        try {
            return await request(SEC_METRICS);
        } catch (error) {
            if (signal?.aborted || error?.name === 'AbortError') throw error;
            console.debug(`EBITDA SEC series not yet available for ${ticker}; using baseline fundamentals.`);
            return request(BASE_SEC_METRICS);
        }
    }

    async function fetchFinancialHistoryIntoCache(ticker, period, generation = prefetchGeneration) {
        const key = `${ticker}|${period}`;
        const cached = financialMemoryCache.get(key);
        if (cached && Date.now() - cached.savedAt < FINANCIAL_CACHE_TTL_MS) return cached.view;
        try {
            const payload = await fetchSecHistoryPayload(ticker, period);
            if (generation !== prefetchGeneration || ticker !== String(state.ticker || '').trim().toUpperCase()) return null;
            const view = transformSecPayload(payload);
            if (!view.metricPoints.revenue?.length) return null;
            rememberFinancialView(key, view);
            return view;
        } catch (error) {
            console.debug(`Phase 4A ${period} prefetch skipped for ${ticker}:`, error);
            return null;
        }
    }

    function prefetchOtherPeriods(ticker, loadedPeriod) {
        const generation = prefetchGeneration;
        const periods = ['annual', 'quarterly', 'ttm'].filter(period => period !== loadedPeriod);
        const run = () => periods.reduce((promise, period) => promise.then(() => fetchFinancialHistoryIntoCache(ticker, period, generation)), Promise.resolve());
        if ('requestIdleCallback' in window) requestIdleCallback(run, { timeout: 1200 });
        else setTimeout(run, 250);
    }

    async function loadFinancialHistory(period = desiredPeriod) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!ticker) return null;
        desiredPeriod = period;
        state.financialPeriod = period;
        syncPeriodControls(period);

        const key = `${ticker}|${period}`;
        const cached = financialMemoryCache.get(key);
        if (cached && Date.now() - cached.savedAt < FINANCIAL_CACHE_TTL_MS) {
            if (ticker === String(state.ticker || '').trim().toUpperCase() && desiredPeriod === period) {
                renderView(cached.view);
            }
            return cached.view;
        }

        const thisRequest = ++requestId;
        if (requestController) requestController.abort();
        requestController = new AbortController();
        setStatus(`Loading ${humanPeriod(period)} SEC history…`, 'loading');

        try {
            const payload = await fetchSecHistoryPayload(ticker, period, requestController.signal);
            if (thisRequest !== requestId) return null;
            const view = transformSecPayload(payload);
            if (!view.metricPoints.revenue?.length) throw new Error('Revenue history unavailable.');
            rememberFinancialView(key, view);
            prefetchOtherPeriods(ticker, period);
            if (ticker === String(state.ticker || '').trim().toUpperCase() && desiredPeriod === period) {
                renderView(view);
            }
            return view;
        } catch (error) {
            if (error?.name === 'AbortError') return null;
            console.warn(`Phase 2E ${period} fundamentals failed for ${ticker}:`, error);
            if (period === 'annual' && fallbackView && financialTicker === ticker) {
                renderView(fallbackView, 'error', 'SEC history unavailable · showing legacy annual data');
            } else {
                const keepPeriod = displayedView?.period || 'annual';
                desiredPeriod = keepPeriod;
                state.financialPeriod = keepPeriod;
                syncPeriodControls(keepPeriod);
                setStatus(`${humanPeriod(period)} SEC history unavailable · keeping ${humanPeriod(keepPeriod)}`, 'error');
            }
            return null;
        } finally {
            if (thisRequest === requestId) requestController = null;
        }
    }

    function resetForTicker(ticker, fin) {
        if (requestController) requestController.abort();
        requestController = null;
        requestId += 1;
        prefetchGeneration += 1;
        desiredWindow = 'max';
        expandedChartId = null;
        document.body.classList.remove('modal-active');
        document.querySelectorAll('.financial-card').forEach(clearExpandedCardStyles);
        const existingBackdrop = document.getElementById('financial-chart-backdrop');
        if (existingBackdrop && existingBackdrop.parentNode) existingBackdrop.parentNode.removeChild(existingBackdrop);
        financialTicker = ticker;
        researchData = null;
        researchTicker = '';
        fallbackView = buildLegacyView(fin);
        displayedView = fallbackView;
        desiredPeriod = 'annual';
        state.financialPeriod = 'annual';
        syncPeriodControls('annual');
        setQualityAlert(fallbackView);
        setStatus('Loading long-run SEC history…', 'loading');
    }

    // Override only the two legacy chart-rendering functions. The main stock request,
    // DCF, peers, research labs and Phase 1 price/quote loading remain untouched.
    injectFinancialHTML = function(fin) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);
        else fallbackView = buildLegacyView(fin);
        renderFinancialCards(fallbackView);
    };

    drawFinancials = function(fin) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);
        else fallbackView = buildLegacyView(fin);

        // Keep the existing short history visible instantly, then hydrate the SEC view.
        renderFinancialCharts(fallbackView);
        displayedView = fallbackView;
        setStatus('Loading long-run SEC history…', 'loading');
        loadFinancialHistory('annual').catch(() => null);
        loadFinancialResearch(ticker, prefetchGeneration).catch(() => null);
    };

    document.querySelectorAll('.financial-period-btn').forEach(button => {
        button.addEventListener('click', () => {
            const period = button.dataset.financialPeriod;
            if (!period || period === desiredPeriod && displayedView?.period === period) return;
            loadFinancialHistory(period).catch(() => null);
        });
    });

    document.querySelectorAll('.financial-window-btn').forEach(button => {
        button.addEventListener('click', () => {
            const nextWindow = button.dataset.financialWindow || 'max';
            if (String(nextWindow) === String(desiredWindow)) return;
            desiredWindow = nextWindow;
            syncWindowControls(desiredWindow);
            if (displayedView) renderFinancialCharts(displayedView);
        });
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && expandedChartId) toggleExpandedChart(expandedChartId);
    });

    // Expose a tiny debugging surface for production smoke tests without coupling the
    // rest of SethiStock to the implementation details of this module.
    window.SethiStockFinancialHistory = {
        get period() { return desiredPeriod; },
        get source() { return displayedView?.sourceType || null; },
        get periodCount() { return displayedView?.periodCount || 0; },
        load: loadFinancialHistory
    };
})();
