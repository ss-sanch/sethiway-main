from pathlib import Path
import re

html = Path('sethistock.html')
text = html.read_text()

# Active control styling: add comparison controls.
old_active = '.tf-btn.active, .type-btn.active, .financial-period-btn.active, .financial-window-btn.active { background-color: #2563eb; color: white; border-color: #2563eb; }'
new_active = '.tf-btn.active, .type-btn.active, .financial-period-btn.active, .financial-window-btn.active, .comparison-period-btn.active, .comparison-window-btn.active, .comparison-mode-btn.active { background-color: #2563eb; color: white; border-color: #2563eb; }'
if old_active not in text:
    raise SystemExit('Active control CSS marker not found')
text = text.replace(old_active, new_active, 1)
text = text.replace('#dashboard, #key-metrics, #comparisons, #research-labs, #valuation, #extra', '#dashboard, #key-metrics, #comparisons, #valuation, #extra', 1)

# Retire the old Research nav destination in desktop and mobile navs.
research_nav = '<a href="#research-labs" class="hover:text-blue-600 transition">Research</a>'
nav_count = text.count(research_nav)
if nav_count < 2:
    raise SystemExit(f'Expected two Research nav links, found {nav_count}')
text = text.replace(research_nav, '')

comparison_html = '''        <div id="comparisons" class="scroll-mt-24">
            <div class="mt-10 mb-3 border-b border-gray-200 pb-4 flex flex-col xl:flex-row xl:items-end justify-between gap-4">
                <div>
                    <h3 class="text-2xl font-black">Financial Comparisons</h3>
                    <p class="text-sm text-gray-500 mt-1">Compare growth, cash conversion and balance-sheet strength using the financial history already loaded above.</p>
                </div>
                <div class="flex flex-col items-start xl:items-end gap-2">
                    <div class="flex flex-wrap items-center gap-2">
                        <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200" aria-label="Comparison reporting period">
                            <button type="button" class="comparison-period-btn active px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-period="annual">Annual</button>
                            <button type="button" class="comparison-period-btn px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-period="quarterly">Quarterly</button>
                        </div>
                        <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200" aria-label="Comparison history window">
                            <button type="button" class="comparison-window-btn px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-window="3">3Y</button>
                            <button type="button" class="comparison-window-btn px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-window="5">5Y</button>
                            <button type="button" class="comparison-window-btn px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-window="10">10Y</button>
                            <button type="button" class="comparison-window-btn active px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-window="max">MAX</button>
                        </div>
                        <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200" aria-label="Comparison chart mode">
                            <button type="button" class="comparison-mode-btn active px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-mode="absolute">Absolute</button>
                            <button type="button" class="comparison-mode-btn px-3 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-comparison-mode="indexed">Indexed</button>
                        </div>
                    </div>
                    <p id="comparison-status" class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Annual · Absolute · Loaded history</p>
                </div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <article data-financial-card="comp-rev-net" class="bg-white p-5 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between gap-3 mb-2">
                        <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">Revenue vs Net Income</h4>
                        <button type="button" class="financial-expand-btn inline-flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-400 hover:text-blue-600 hover:border-blue-300 hover:bg-blue-50 transition" data-chart-id="comp-rev-net" aria-label="Expand Revenue vs Net Income chart" title="Expand chart"><svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg></button>
                    </div>
                    <div id="comp-rev-net" class="h-56 w-full"></div>
                    <div id="comp-rev-net-footer" class="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-gray-100 pt-3 mt-2"></div>
                </article>
                <article data-financial-card="comp-cash-debt" class="bg-white p-5 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between gap-3 mb-2">
                        <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">Cash vs Total Debt</h4>
                        <button type="button" class="financial-expand-btn inline-flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-400 hover:text-blue-600 hover:border-blue-300 hover:bg-blue-50 transition" data-chart-id="comp-cash-debt" aria-label="Expand Cash vs Total Debt chart" title="Expand chart"><svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg></button>
                    </div>
                    <div id="comp-cash-debt" class="h-56 w-full"></div>
                    <div id="comp-cash-debt-footer" class="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-gray-100 pt-3 mt-2"></div>
                </article>
                <article data-financial-card="comp-fcf-ocf" class="bg-white p-5 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between gap-3 mb-2">
                        <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">Operating CF vs Free Cash Flow</h4>
                        <button type="button" class="financial-expand-btn inline-flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-400 hover:text-blue-600 hover:border-blue-300 hover:bg-blue-50 transition" data-chart-id="comp-fcf-ocf" aria-label="Expand Operating CF vs Free Cash Flow chart" title="Expand chart"><svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg></button>
                    </div>
                    <div id="comp-fcf-ocf" class="h-56 w-full"></div>
                    <div id="comp-fcf-ocf-footer" class="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-gray-100 pt-3 mt-2"></div>
                </article>
                <article data-financial-card="comp-ocf-capex" class="bg-white p-5 rounded-2xl shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between gap-3 mb-2">
                        <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">Operating CF vs CapEx</h4>
                        <button type="button" class="financial-expand-btn inline-flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-400 hover:text-blue-600 hover:border-blue-300 hover:bg-blue-50 transition" data-chart-id="comp-ocf-capex" aria-label="Expand Operating CF vs CapEx chart" title="Expand chart"><svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg></button>
                    </div>
                    <div id="comp-ocf-capex" class="h-56 w-full"></div>
                    <div id="comp-ocf-capex-footer" class="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-gray-100 pt-3 mt-2"></div>
                </article>
            </div>
        </div>
'''

pattern = re.compile(r'        <div id="comparisons" class="scroll-mt-24">.*?        </div>\n\n\n        <section id="research-labs"', re.S)
match = pattern.search(text)
if not match:
    raise SystemExit('Comparison/Research boundary not found')
text = pattern.sub(comparison_html + '\n\n        <section id="research-labs"', text, count=1)

# Remove the now-redundant visible Research Labs section.
research_section = re.compile(r'\n\s*<section id="research-labs" class="mt-12 scroll-mt-24">.*?</section>\s*', re.S)
text, removed = research_section.subn('\n', text, count=1)
if removed != 1:
    raise SystemExit(f'Expected one Research Labs section, removed {removed}')

# Prevent the legacy inline research renderer from recreating the retired UI or launching
# its old post-analysis routine. The shared getSethiStockResearch() helper remains intact.
marker = '    function ensureResearchUI() {\n        if (document.getElementById("research-labs")) return;'
if marker not in text:
    raise SystemExit('ensureResearchUI marker not found')
text = text.replace(marker, '    function ensureResearchUI() {\n        return; // Retired: research charts now live in Key Financial Metrics.\n        if (document.getElementById("research-labs")) return;', 1)

load_marker = '    async function loadStockResearch(ticker) {\n        ensureResearchUI();'
if load_marker not in text:
    raise SystemExit('loadStockResearch marker not found')
text = text.replace(load_marker, '    async function loadStockResearch(ticker) {\n        return null; // Retired legacy UI; shared research data is consumed by Financial History.\n        ensureResearchUI();', 1)
html.write_text(text)

js = Path('sethistock-financial-history.js')
code = js.read_text()

state_marker = "    let desiredPeriod = 'annual';\n    let desiredWindow = 'max';\n    let expandedChartId = null;"
if state_marker not in code:
    raise SystemExit('Financial state marker not found')
code = code.replace(state_marker, "    let desiredPeriod = 'annual';\n    let desiredWindow = 'max';\n    let comparisonPeriod = 'annual';\n    let comparisonWindow = 'max';\n    let comparisonMode = 'absolute';\n    let comparisonView = null;\n    let comparisonRequestToken = 0;\n    let expandedChartId = null;", 1)

trace_marker = "        const rawPoints = filterPointsToWindow(validMetricPoints(view, key));"
if trace_marker not in code:
    raise SystemExit('traceForMetric window marker not found')
code = code.replace(trace_marker, "        const rawPoints = filterPointsToWindow(validMetricPoints(view, key), options.windowValue ?? desiredWindow);", 1)

bind_old = '''    function bindExpandButtons() {
        document.querySelectorAll('.financial-expand-btn').forEach(button => {
            button.addEventListener('click', () => toggleExpandedChart(button.dataset.chartId));
        });
    }'''
bind_new = '''    function bindExpandButtons() {
        document.querySelectorAll('.financial-expand-btn').forEach(button => {
            if (button.dataset.financialExpandBound === '1') return;
            button.dataset.financialExpandBound = '1';
            button.addEventListener('click', () => toggleExpandedChart(button.dataset.chartId));
        });
    }'''
if bind_old not in code:
    raise SystemExit('bindExpandButtons block not found')
code = code.replace(bind_old, bind_new, 1)

comparison_logic = r'''    function syncComparisonControls() {
        document.querySelectorAll('.comparison-period-btn').forEach(button => {
            button.classList.toggle('active', button.dataset.comparisonPeriod === comparisonPeriod);
        });
        document.querySelectorAll('.comparison-window-btn').forEach(button => {
            button.classList.toggle('active', String(button.dataset.comparisonWindow) === String(comparisonWindow));
        });
        document.querySelectorAll('.comparison-mode-btn').forEach(button => {
            button.classList.toggle('active', button.dataset.comparisonMode === comparisonMode);
        });
    }

    function setComparisonStatus(message, tone = 'neutral') {
        const element = document.getElementById('comparison-status');
        if (!element) return;
        element.textContent = message;
        element.className = `text-[10px] font-bold uppercase tracking-widest ${tone === 'loading' ? 'text-blue-600' : tone === 'error' ? 'text-red-500' : 'text-gray-400'}`;
    }

    function comparisonPeriodLabel(view) {
        return humanPeriod(view?.period || comparisonPeriod);
    }

    function comparisonMetricPoints(view, key) {
        const filtered = filterPointsToWindow(validMetricPoints(view, key), comparisonWindow);
        return view?.period === 'annual' ? collapseAnnualPlotPoints(filtered) : filtered;
    }

    function comparisonDateKey(point, annual) {
        return annual ? (point?.annualCategory || annualCategoryLabel(point)) : String(point?.end || '');
    }

    function pairedComparisonRows(view, firstKey, secondKey, windowValue = 'max') {
        const annual = view?.period === 'annual';
        const firstRaw = filterPointsToWindow(validMetricPoints(view, firstKey), windowValue);
        const secondRaw = filterPointsToWindow(validMetricPoints(view, secondKey), windowValue);
        const first = annual ? collapseAnnualPlotPoints(firstRaw) : firstRaw;
        const second = annual ? collapseAnnualPlotPoints(secondRaw) : secondRaw;
        const secondMap = new Map(second.map(point => [comparisonDateKey(point, annual), point]));
        return first.map(point => {
            const key = comparisonDateKey(point, annual);
            const match = secondMap.get(key);
            if (!match) return null;
            return {
                key,
                end: point?.end || match?.end || null,
                first: finiteNumber(point?.value),
                second: finiteNumber(match?.value)
            };
        }).filter(row => row && row.first !== null && row.second !== null);
    }

    function comparisonPriorRow(rows, years = 5) {
        if (!Array.isArray(rows) || rows.length < 2) return null;
        const latest = rows[rows.length - 1];
        const latestDate = new Date(`${latest.end || latest.key}T00:00:00Z`);
        if (Number.isNaN(latestDate.getTime())) {
            const latestYear = Number(String(latest.key).slice(0, 4));
            return rows.find(row => Number(String(row.key).slice(0, 4)) === latestYear - years) || null;
        }
        const target = new Date(latestDate.getTime());
        target.setUTCFullYear(target.getUTCFullYear() - years);
        let best = null;
        let distance = Infinity;
        rows.slice(0, -1).forEach(row => {
            const date = new Date(`${row.end || row.key}T00:00:00Z`);
            if (Number.isNaN(date.getTime())) return;
            const delta = Math.abs(date.getTime() - target.getTime());
            if (delta < distance) { distance = delta; best = row; }
        });
        return distance <= 220 * 24 * 60 * 60 * 1000 ? best : null;
    }

    function ratioPercent(numerator, denominator) {
        const top = finiteNumber(numerator);
        const bottom = finiteNumber(denominator);
        if (top === null || bottom === null || bottom === 0) return null;
        return (top / bottom) * 100;
    }

    function formatComparisonPercent(value, digits = 1, suffix = '%') {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        const sign = suffix === 'pp' && number > 0 ? '+' : '';
        return `${sign}${number.toFixed(digits)}${suffix}`;
    }

    function formatComparisonMoney(value) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : metricDisplayValue('revenue', number);
    }

    function formatComparisonRatio(value) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number.toFixed(2)}x`;
    }

    function averageRecentRatio(view, numeratorKey, denominatorKey, years = 5) {
        const rows = pairedComparisonRows(view, numeratorKey, denominatorKey, String(years));
        const ratios = rows.map(row => ratioPercent(row.first, row.second)).filter(value => value !== null);
        if (!ratios.length) return null;
        return ratios.reduce((sum, value) => sum + value, 0) / ratios.length;
    }

    function comparisonFooterStats(view, id) {
        const growth = key => getGrowthStats(view, key)?.['5Y'] || '-';
        if (id === 'comp-rev-net') {
            const rows = pairedComparisonRows(view, 'revenue', 'net');
            const latest = rows[rows.length - 1];
            const prior = comparisonPriorRow(rows, 5);
            const latestMargin = latest ? ratioPercent(latest.second, latest.first) : null;
            const priorMargin = prior ? ratioPercent(prior.second, prior.first) : null;
            const delta = latestMargin !== null && priorMargin !== null ? latestMargin - priorMargin : null;
            return [
                ['Net Margin', formatComparisonPercent(latestMargin)],
                ['5Y Δ Margin', formatComparisonPercent(delta, 1, 'pp')],
                ['Revenue 5Y CAGR', growth('revenue')],
                ['Net Income 5Y CAGR', growth('net')]
            ];
        }
        if (id === 'comp-cash-debt') {
            const rows = pairedComparisonRows(view, 'cash', 'debt');
            const latest = rows[rows.length - 1];
            const netDebt = latest ? latest.second - latest.first : null;
            const debtCash = latest && latest.first !== 0 ? latest.second / latest.first : null;
            return [
                ['Net Debt', formatComparisonMoney(netDebt)],
                ['Debt / Cash', formatComparisonRatio(debtCash)],
                ['Cash 5Y CAGR', growth('cash')],
                ['Debt 5Y CAGR', growth('debt')]
            ];
        }
        if (id === 'comp-fcf-ocf') {
            const rows = pairedComparisonRows(view, 'fcf', 'ocf');
            const latest = rows[rows.length - 1];
            const conversion = latest ? ratioPercent(latest.first, latest.second) : null;
            return [
                ['FCF Conversion', formatComparisonPercent(conversion)],
                ['5Y Avg Conversion', formatComparisonPercent(averageRecentRatio(view, 'fcf', 'ocf', 5))],
                ['FCF 5Y CAGR', growth('fcf')],
                ['OCF 5Y CAGR', growth('ocf')]
            ];
        }
        if (id === 'comp-ocf-capex') {
            const rows = pairedComparisonRows(view, 'ocf', 'capex');
            const latest = rows[rows.length - 1];
            const intensity = latest ? ratioPercent(latest.second, latest.first) : null;
            const retained = latest ? latest.first - latest.second : null;
            return [
                ['CapEx / OCF', formatComparisonPercent(intensity)],
                ['Retained Cash', formatComparisonMoney(retained)],
                ['5Y Avg CapEx / OCF', formatComparisonPercent(averageRecentRatio(view, 'capex', 'ocf', 5))],
                ['OCF 5Y CAGR', growth('ocf')]
            ];
        }
        return [];
    }

    function renderComparisonFooter(view, id) {
        const footer = document.getElementById(`${id}-footer`);
        if (!footer) return;
        const stats = comparisonFooterStats(view, id);
        footer.innerHTML = stats.map(([label, value]) => `
            <div class="min-w-0">
                <p class="text-[9px] font-black text-gray-400 uppercase tracking-wider leading-tight">${label}</p>
                <p class="text-sm font-black text-gray-900 mt-1 truncate">${value}</p>
            </div>`).join('');
    }

    function indexedTrace(trace, key) {
        if (!trace || !Array.isArray(trace.y)) return trace;
        const original = trace.y.map(value => finiteNumber(value));
        const baseIndex = original.findIndex(value => value !== null && value !== 0);
        if (baseIndex < 0) return trace;
        const base = original[baseIndex];
        const labels = Array.isArray(trace.customdata) ? trace.customdata.slice() : trace.x.slice();
        const displayValues = original.map(value => value === null ? 'N/A' : metricDisplayValue(key, value));
        trace.y = original.map(value => value === null ? null : (value / base) * 100);
        trace.customdata = labels.map((label, index) => [label, displayValues[index]]);
        trace.text = undefined;
        trace.hovertemplate = '%{customdata[0]}<br>%{fullData.name}: %{customdata[1]}<br>Indexed: %{y:.1f}<extra></extra>';
        return trace;
    }

    function drawComparison(view, id, first, second) {
        const nonAnnual = view.period !== 'annual';
        const trace1 = traceForMetric(view, first.key, first.name, first.colour, { forceLine: nonAnnual, windowValue: comparisonWindow });
        const trace2 = traceForMetric(view, second.key, second.name, second.colour, { forceLine: nonAnnual, windowValue: comparisonWindow });
        const traces = [trace1, trace2].filter(Boolean);
        if (traces.length < 2) {
            emptyChart(id, 'Comparison history unavailable');
            renderComparisonFooter(view, id);
            return;
        }
        if (comparisonMode === 'indexed') {
            indexedTrace(trace1, first.key);
            indexedTrace(trace2, second.key);
        }
        if (!preparePlotContainer(id)) return;
        const layout = chartLayout(view, true);
        layout.hovermode = 'x unified';
        layout.hoverlabel = { bgcolor: '#ffffff', bordercolor: '#cbd5e1', font: { color: '#0f172a', size: 11 } };
        if (view.period === 'annual') layout.barmode = 'group';
        if (comparisonMode === 'indexed') {
            layout.yaxis.tickprefix = '';
            layout.yaxis.ticksuffix = '';
            layout.yaxis.tickformat = '.0f';
            layout.yaxis.title = { text: 'Index (first visible = 100)', font: { size: 10, color: '#64748b' } };
            layout.shapes = [{ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 100, y1: 100, line: { color: '#cbd5e1', width: 1, dash: 'dot' } }];
        }
        Plotly.react(id, traces, layout, { displayModeBar: false, responsive: true });
        renderComparisonFooter(view, id);
    }

    function renderFinancialComparisons(view) {
        if (!view) return;
        syncComparisonControls();
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
        const sourceLabel = view.sourceType === 'sec' ? 'SEC history' : 'loaded history';
        setComparisonStatus(`${comparisonPeriodLabel(view)} · ${comparisonMode === 'indexed' ? 'Indexed' : 'Absolute'} · ${sourceLabel}`);
        bindExpandButtons();
    }

    async function loadComparisonPeriod(period) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!ticker || !['annual', 'quarterly'].includes(period)) return;
        comparisonPeriod = period;
        syncComparisonControls();
        const token = ++comparisonRequestToken;

        let view = null;
        if (displayedView?.period === period) view = displayedView;
        if (!view) {
            const cached = financialMemoryCache.get(`${ticker}|${period}`);
            if (cached && Date.now() - cached.savedAt < FINANCIAL_CACHE_TTL_MS) view = cached.view;
        }
        if (!view && period === 'annual' && fallbackView) view = fallbackView;

        if (view) {
            if (token !== comparisonRequestToken) return;
            comparisonView = view;
            renderFinancialComparisons(view);
            return;
        }

        setComparisonStatus(`Loading ${humanPeriod(period)} comparison history…`, 'loading');
        view = await fetchFinancialHistoryIntoCache(ticker, period, prefetchGeneration);
        if (token !== comparisonRequestToken || ticker !== String(state.ticker || '').trim().toUpperCase()) return;
        if (!view) {
            setComparisonStatus(`${humanPeriod(period)} comparison history unavailable`, 'error');
            return;
        }
        comparisonView = view;
        renderFinancialComparisons(view);
    }

    function bindComparisonControls() {
        document.querySelectorAll('.comparison-period-btn').forEach(button => {
            if (button.dataset.comparisonBound === '1') return;
            button.dataset.comparisonBound = '1';
            button.addEventListener('click', () => {
                const next = button.dataset.comparisonPeriod || 'annual';
                if (next === comparisonPeriod && comparisonView) return;
                loadComparisonPeriod(next).catch(error => {
                    console.debug('Comparison period load skipped:', error);
                    setComparisonStatus('Comparison history temporarily unavailable', 'error');
                });
            });
        });
        document.querySelectorAll('.comparison-window-btn').forEach(button => {
            if (button.dataset.comparisonBound === '1') return;
            button.dataset.comparisonBound = '1';
            button.addEventListener('click', () => {
                comparisonWindow = button.dataset.comparisonWindow || 'max';
                syncComparisonControls();
                if (comparisonView) renderFinancialComparisons(comparisonView);
            });
        });
        document.querySelectorAll('.comparison-mode-btn').forEach(button => {
            if (button.dataset.comparisonBound === '1') return;
            button.dataset.comparisonBound = '1';
            button.addEventListener('click', () => {
                comparisonMode = button.dataset.comparisonMode === 'indexed' ? 'indexed' : 'absolute';
                syncComparisonControls();
                if (comparisonView) renderFinancialComparisons(comparisonView);
            });
        });
        syncComparisonControls();
        bindExpandButtons();
    }

    function renderFinancialCharts(view) {'''

pattern = re.compile(r"    function drawComparison\(view, id, first, second\) \{.*?\n    \}\n\n    function renderFinancialCharts\(view\) \{", re.S)
code, count = pattern.subn(comparison_logic, code, count=1)
if count != 1:
    raise SystemExit(f'Expected one drawComparison replacement, got {count}')

old_calls = '''        drawComparison(view, 'comp-rev-net',
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
            { key: 'capex', name: 'CapEx', colour: '#ef4444' });'''
if old_calls not in code:
    raise SystemExit('Original comparison draw block not found')
code = code.replace(old_calls, "        renderFinancialComparisons(comparisonView || view);", 1)

render_view_marker = '''    function renderView(view, statusTone = 'success', statusOverride = null) {
        displayedView = view;'''
if render_view_marker not in code:
    raise SystemExit('renderView marker not found')
code = code.replace(render_view_marker, '''    function renderView(view, statusTone = 'success', statusOverride = null) {
        displayedView = view;
        if (!comparisonView || comparisonPeriod === (view.period || 'annual')) comparisonView = view;''', 1)

reset_marker = '''        prefetchGeneration += 1;
        desiredWindow = 'max';
        closeExpandedChart();'''
if reset_marker not in code:
    raise SystemExit('reset comparison marker not found')
code = code.replace(reset_marker, '''        prefetchGeneration += 1;
        desiredWindow = 'max';
        comparisonPeriod = 'annual';
        comparisonWindow = 'max';
        comparisonMode = 'absolute';
        comparisonView = null;
        comparisonRequestToken += 1;
        closeExpandedChart();''', 1)

fallback_marker = '''        fallbackView = buildLegacyView(fin);
        applyFastEbitdaFallback(ticker, fallbackView);
        displayedView = fallbackView;'''
if fallback_marker not in code:
    raise SystemExit('fallback comparison marker not found')
code = code.replace(fallback_marker, '''        fallbackView = buildLegacyView(fin);
        applyFastEbitdaFallback(ticker, fallbackView);
        displayedView = fallbackView;
        comparisonView = fallbackView;''', 1)

# Bind the independent comparison controls once; their only network action is the user's
# explicit Annual/Quarterly click path above.
keydown_marker = "    document.addEventListener('keydown', event => {"
if keydown_marker not in code:
    raise SystemExit('keydown marker not found')
code = code.replace(keydown_marker, "    bindComparisonControls();\n\n    document.addEventListener('keydown', event => {", 1)

js.write_text(code)
print('PHASE4C_PATCH_APPLIED')
