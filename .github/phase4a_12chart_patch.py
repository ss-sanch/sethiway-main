from pathlib import Path

html_path = Path('sethistock.html')
js_path = Path('sethistock-financial-history.js')
html = html_path.read_text()
js = js_path.read_text()

# --- Wider 4x3 financial dashboard without changing the rest of SethiStock width. ---
html = html.replace(
    '<div id="key-metrics" class="scroll-mt-24">',
    '<div id="key-metrics" class="scroll-mt-24 w-[calc(100vw-2rem)] max-w-[1800px] relative left-1/2 -translate-x-1/2">',
    1,
)
html = html.replace(
    '<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6" id="individual-charts-container"></div>',
    '<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-5" id="individual-charts-container"></div>',
    1,
)

# --- Share the existing research request between Research Labs and Financial Metrics. ---
research_anchor = '''    const RESEARCH_API = "https://sethistock-api.onrender.com";
    let researchRequestId = 0;
'''
research_insert = '''    const RESEARCH_API = "https://sethistock-api.onrender.com";
    let researchRequestId = 0;
    const sharedResearchPromises = window.SethiStockResearchPromises || new Map();
    window.SethiStockResearchPromises = sharedResearchPromises;
    window.getSethiStockResearch = window.getSethiStockResearch || (ticker => {
        const symbol = String(ticker || '').trim().toUpperCase();
        if (!symbol) return Promise.reject(new Error('Ticker is required'));
        if (sharedResearchPromises.has(symbol)) return sharedResearchPromises.get(symbol);
        const promise = fetch(`${RESEARCH_API}/api/research/${encodeURIComponent(symbol)}`)
            .then(res => {
                if (!res.ok) throw new Error(`Research API returned ${res.status}`);
                return res.json();
            });
        sharedResearchPromises.set(symbol, promise);
        promise.catch(() => sharedResearchPromises.delete(symbol));
        return promise;
    });
'''
if research_anchor not in html:
    raise SystemExit('research bootstrap anchor not found')
html = html.replace(research_anchor, research_insert, 1)

old_fetch = '''            const res = await fetch(`${RESEARCH_API}/api/research/${encodeURIComponent(ticker)}`);
            if (!res.ok) throw new Error(`Research API returned ${res.status}`);
            const data = await res.json();
'''
new_fetch = '''            const data = await window.getSethiStockResearch(ticker);
'''
if old_fetch not in html:
    raise SystemExit('research fetch anchor not found')
html = html.replace(old_fetch, new_fetch, 1)

# --- SEC metric registry: request EBITDA when supported, with a live-API fallback below. ---
js = js.replace(
    "        'revenue', 'net_income', 'gross_margin', 'operating_margin', 'net_margin',\n        'operating_cash_flow', 'free_cash_flow', 'capex', 'cash', 'debt', 'shares'\n    ];",
    "        'revenue', 'net_income', 'ebitda', 'gross_margin', 'operating_margin', 'net_margin',\n        'operating_cash_flow', 'free_cash_flow', 'capex', 'cash', 'debt', 'shares'\n    ];\n    const BASE_SEC_METRICS = SEC_METRICS.filter(metric => metric !== 'ebitda');",
    1,
)
js = js.replace(
    "        net_income: 'net',\n        gross_margin: 'gross_margin',",
    "        net_income: 'net',\n        ebitda: 'ebitda',\n        gross_margin: 'gross_margin',",
    1,
)
js = js.replace(
    "            net: Array.isArray(fin?.net) ? fin.net.slice() : [],\n            gross_margin:",
    "            net: Array.isArray(fin?.net) ? fin.net.slice() : [],\n            ebitda: Array.isArray(fin?.ebitda) ? fin.ebitda.slice() : [],\n            gross_margin:",
    1,
)

state_anchor = '''    const financialMemoryCache = new Map();
'''
state_insert = '''    const financialMemoryCache = new Map();
    let researchData = null;
    let researchTicker = '';
'''
if state_anchor not in js:
    raise SystemExit('state anchor not found')
js = js.replace(state_anchor, state_insert, 1)

# --- Margin point-change helpers and research-card helpers. ---
helper_anchor = '''    function syncWindowControls(windowValue) {
'''
helpers = '''    function deltaBetween(past, latest) {
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

''' + helper_anchor
if helper_anchor not in js:
    raise SystemExit('helper insertion anchor not found')
js = js.replace(helper_anchor, helpers, 1)

# --- Expanded card behaviour: landscape modal + earnings event detail. ---
start = js.index('    function clearExpandedCardStyles(card) {')
end = js.index('\n    function bindExpandButtons()', start)
expanded_block = '''    function clearExpandedCardStyles(card) {
        if (!card) return;
        card.style.position = '';
        card.style.left = '';
        card.style.top = '';
        card.style.width = '';
        card.style.maxWidth = '';
        card.style.height = '';
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
        backdrop.className = 'fixed inset-0 z-[150] bg-gray-900/55 backdrop-blur-sm';
        backdrop.setAttribute('aria-label', 'Close expanded chart');
        backdrop.addEventListener('click', () => toggleExpandedChart(chartId));
        document.body.appendChild(backdrop);

        card.style.position = 'fixed';
        card.style.left = '50%';
        card.style.top = '7vh';
        card.style.width = '92vw';
        card.style.maxWidth = '1280px';
        card.style.height = '86vh';
        card.style.transform = 'translateX(-50%)';
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
            chart.style.height = 'calc(86vh - 118px)';
        }
        requestAnimationFrame(() => {
            renderFinancialCharts(displayedView);
            Plotly.Plots.resize(chartId);
        });
    }
'''
js = js[:start] + expanded_block + js[end:]

# --- Rebuild the card shell as the ordered 12-card dashboard. ---
start = js.index('    function renderFinancialCards(view) {')
end = js.index('\n    function emptyChart', start)
render_cards = '''    function renderFinancialCards(view) {
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
'''
js = js[:start] + render_cards + js[end:]

# --- Research charts. ---
draw_anchor = '''    function drawComparison(view, id, first, second) {
'''
research_draw = '''    function drawHistoricalPE() {
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

''' + draw_anchor
if draw_anchor not in js:
    raise SystemExit('draw comparison anchor not found')
js = js.replace(draw_anchor, research_draw, 1)

# --- Render all 12 cards in logical order. ---
start = js.index('    function renderFinancialCharts(view) {')
end = js.index('\n    function renderView', start)
render_charts = '''    function renderFinancialCharts(view) {
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
'''
js = js[:start] + render_charts + js[end:]

# --- SEC request helper: try EBITDA-capable schema, then fall back cleanly against live v1 API. ---
fetch_anchor = '''    async function fetchFinancialHistoryIntoCache(ticker, period, generation = prefetchGeneration) {
'''
fetch_helper = '''    async function fetchSecHistoryPayload(ticker, period, signal = null) {
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

''' + fetch_anchor
if fetch_anchor not in js:
    raise SystemExit('fetch cache anchor not found')
js = js.replace(fetch_anchor, fetch_helper, 1)

old_prefetch = '''            const query = new URLSearchParams({ period, metrics: SEC_METRICS.join(','), limit: '200' });
            const payload = await fetchJsonWithRetry(`${API_URL}/api/sec/${encodeURIComponent(ticker)}/fundamentals/series?${query.toString()}`, {}, 1);
'''
if old_prefetch not in js:
    raise SystemExit('prefetch request anchor not found')
js = js.replace(old_prefetch, '''            const payload = await fetchSecHistoryPayload(ticker, period);\n''', 1)

old_load = '''            const query = new URLSearchParams({
                period,
                metrics: SEC_METRICS.join(','),
                limit: '200'
            });
            const payload = await fetchJsonWithRetry(
                `${API_URL}/api/sec/${encodeURIComponent(ticker)}/fundamentals/series?${query.toString()}`,
                { signal: requestController.signal },
                1
            );
'''
if old_load not in js:
    raise SystemExit('load request anchor not found')
js = js.replace(old_load, '''            const payload = await fetchSecHistoryPayload(ticker, period, requestController.signal);\n''', 1)

# --- Reset/load shared research with each ticker. ---
reset_anchor = '''        financialTicker = ticker;
        fallbackView = buildLegacyView(fin);
'''
reset_replacement = '''        financialTicker = ticker;
        researchData = null;
        researchTicker = '';
        fallbackView = buildLegacyView(fin);
'''
if reset_anchor not in js:
    raise SystemExit('reset research anchor not found')
js = js.replace(reset_anchor, reset_replacement, 1)

draw_load_anchor = '''        loadFinancialHistory('annual').catch(() => null);
    };
'''
draw_load_replacement = '''        loadFinancialHistory('annual').catch(() => null);
        loadFinancialResearch(ticker, prefetchGeneration).catch(() => null);
    };
'''
if draw_load_anchor not in js:
    raise SystemExit('draw research load anchor not found')
js = js.replace(draw_load_anchor, draw_load_replacement, 1)

# Improve window switches for research cards too (renderFinancialCharts already covers both).

html_path.write_text(html)
js_path.write_text(js)
