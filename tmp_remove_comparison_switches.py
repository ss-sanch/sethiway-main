from pathlib import Path
import re

# --- HTML: remove comparison switches and leave a simple Annual badge ---
html_path = Path('sethistock.html')
html = html_path.read_text()

html = html.replace(
    '.tf-btn.active, .type-btn.active, .financial-period-btn.active, .financial-window-btn.active, .comparison-period-btn.active, .comparison-window-btn.active, .comparison-mode-btn.active { background-color: #2563eb; color: white; border-color: #2563eb; }',
    '.tf-btn.active, .type-btn.active, .financial-period-btn.active, .financial-window-btn.active { background-color: #2563eb; color: white; border-color: #2563eb; }',
    1
)

header_pattern = re.compile(
    r'(<div id="comparisons" class="scroll-mt-24">\s*)'
    r'<div class="mt-10 mb-3 border-b border-gray-200 pb-4 flex flex-col xl:flex-row xl:items-end justify-between gap-4">.*?'
    r'(<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">)',
    re.S,
)
replacement = r'''\1<div class="mt-10 mb-3 border-b border-gray-200 pb-4 flex items-end justify-between gap-4">
                <div>
                    <h3 class="text-2xl font-black">Financial Comparisons</h3>
                    <p class="text-sm text-gray-500 mt-1">Compare profitability, cash conversion and balance-sheet strength across the full annual history already loaded above.</p>
                </div>
                <span class="px-2.5 py-1 rounded-md bg-gray-100 border border-gray-200 text-[10px] font-black text-gray-500 uppercase tracking-widest">Annual</span>
            </div>
            \2'''
html, count = header_pattern.subn(replacement, html, count=1)
if count != 1:
    raise SystemExit(f'Expected to replace one Financial Comparisons control header, replaced {count}')

# No comparison-specific controls/status should remain in the visible UI.
for token in ('comparison-period-btn', 'comparison-window-btn', 'comparison-mode-btn', 'comparison-status'):
    if token in html:
        raise SystemExit(f'Comparison control token still present in HTML: {token}')

html_path.write_text(html)

# --- JS: lock comparisons to Annual / MAX / Absolute and remove fetch-capable control code ---
js_path = Path('sethistock-financial-history.js')
js = js_path.read_text()

state_old = """    let comparisonPeriod = 'annual';\n    let comparisonWindow = 'max';\n    let comparisonMode = 'absolute';\n    let comparisonView = null;\n    let comparisonRequestToken = 0;\n"""
if state_old not in js:
    raise SystemExit('Comparison state block not found')
js = js.replace(state_old, "    let comparisonView = null;\n", 1)

comparison_logic = r'''    function comparisonAnnualPoints(view, key) {
        const points = validMetricPoints(view, key);
        return collapseAnnualPlotPoints(points);
    }

    function comparisonRows(view, firstKey, secondKey) {
        if (!view || view.period !== 'annual') return [];
        const first = comparisonAnnualPoints(view, firstKey);
        const second = comparisonAnnualPoints(view, secondKey);
        const secondByYear = new Map(second.map(point => [String(point.annualCategory || annualCategoryLabel(point)), point]));
        return first.map(point => {
            const year = String(point.annualCategory || annualCategoryLabel(point));
            const match = secondByYear.get(year);
            if (!match) return null;
            const firstValue = finiteNumber(point.value);
            const secondValue = finiteNumber(match.value);
            if (firstValue === null || secondValue === null) return null;
            return { year, first: firstValue, second: secondValue };
        }).filter(Boolean);
    }

    function comparisonCagr(rows, field, years = 5) {
        if (!Array.isArray(rows) || rows.length < years + 1) return null;
        const latest = rows[rows.length - 1];
        const start = rows[rows.length - 1 - years];
        const latestValue = finiteNumber(latest?.[field]);
        const startValue = finiteNumber(start?.[field]);
        const latestYear = Number(latest?.year);
        const startYear = Number(start?.year);
        const periods = Number.isFinite(latestYear) && Number.isFinite(startYear) && latestYear > startYear
            ? latestYear - startYear
            : years;
        if (latestValue === null || startValue === null || latestValue <= 0 || startValue <= 0 || periods <= 0) return null;
        return (Math.pow(latestValue / startValue, 1 / periods) - 1) * 100;
    }

    function comparisonPct(value, digits = 1) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number.toFixed(digits)}%`;
    }

    function comparisonSignedPct(value, digits = 1) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number >= 0 ? '+' : ''}${number.toFixed(digits)}%`;
    }

    function comparisonMoney(value) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        return `${number < 0 ? '-' : ''}$${compactNumber(Math.abs(number))}`;
    }

    function comparisonMultiple(value) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number.toFixed(2)}x`;
    }

    function comparisonFooterItem(label, value, tone = 'text-gray-900') {
        return `<div><p class="text-[9px] font-black uppercase tracking-wider text-gray-400">${label}</p><p class="mt-1 text-sm font-black ${tone}">${value}</p></div>`;
    }

    function renderComparisonFooter(view, id) {
        const footer = document.getElementById(`${id}-footer`);
        if (!footer) return;
        const config = {
            'comp-rev-net': ['revenue', 'net'],
            'comp-cash-debt': ['cash', 'debt'],
            'comp-fcf-ocf': ['ocf', 'fcf'],
            'comp-ocf-capex': ['ocf', 'capex']
        }[id];
        if (!config) return;
        const rows = comparisonRows(view, config[0], config[1]);
        if (!rows.length) {
            footer.innerHTML = comparisonFooterItem('Insight', 'N/A');
            return;
        }
        const latest = rows[rows.length - 1];
        const lastFive = rows.slice(-5);
        let items = [];

        if (id === 'comp-rev-net') {
            const margin = latest.first ? latest.second / latest.first * 100 : null;
            const older = rows.length >= 6 ? rows[rows.length - 6] : null;
            const oldMargin = older?.first ? older.second / older.first * 100 : null;
            const delta = margin !== null && oldMargin !== null ? margin - oldMargin : null;
            items = [
                ['Net Margin', comparisonPct(margin)],
                ['5Y Δ Margin', delta === null ? 'N/A' : `${delta >= 0 ? '+' : ''}${delta.toFixed(1)}pp`],
                ['Revenue 5Y CAGR', comparisonSignedPct(comparisonCagr(rows, 'first'))],
                ['Net Income 5Y CAGR', comparisonSignedPct(comparisonCagr(rows, 'second'))]
            ];
        } else if (id === 'comp-cash-debt') {
            const netDebt = latest.second - latest.first;
            const debtCash = latest.first ? latest.second / latest.first : null;
            items = [
                ['Net Debt', comparisonMoney(netDebt)],
                ['Debt / Cash', comparisonMultiple(debtCash)],
                ['Cash 5Y CAGR', comparisonSignedPct(comparisonCagr(rows, 'first'))],
                ['Debt 5Y CAGR', comparisonSignedPct(comparisonCagr(rows, 'second'))]
            ];
        } else if (id === 'comp-fcf-ocf') {
            const conversion = latest.first ? latest.second / latest.first * 100 : null;
            const conversions = lastFive.filter(row => row.first).map(row => row.second / row.first * 100);
            const avg = conversions.length ? conversions.reduce((sum, value) => sum + value, 0) / conversions.length : null;
            items = [
                ['FCF Conversion', comparisonPct(conversion)],
                ['5Y Avg Conversion', comparisonPct(avg)],
                ['FCF 5Y CAGR', comparisonSignedPct(comparisonCagr(rows, 'second'))],
                ['OCF 5Y CAGR', comparisonSignedPct(comparisonCagr(rows, 'first'))]
            ];
        } else {
            const ratio = latest.first ? latest.second / latest.first * 100 : null;
            const retained = latest.first - latest.second;
            const ratios = lastFive.filter(row => row.first).map(row => row.second / row.first * 100);
            const avg = ratios.length ? ratios.reduce((sum, value) => sum + value, 0) / ratios.length : null;
            items = [
                ['CapEx / OCF', comparisonPct(ratio)],
                ['Retained Cash', comparisonMoney(retained)],
                ['5Y Avg CapEx / OCF', comparisonPct(avg)],
                ['OCF 5Y CAGR', comparisonSignedPct(comparisonCagr(rows, 'first'))]
            ];
        }
        footer.innerHTML = items.map(([label, value]) => comparisonFooterItem(label, value)).join('');
    }

    function drawComparison(view, id, first, second) {
        const rows = comparisonRows(view, first.key, second.key);
        if (!rows.length) {
            emptyChart(id, 'Annual comparison history unavailable');
            renderComparisonFooter(view, id);
            return;
        }
        if (!preparePlotContainer(id)) return;
        const custom = rows.map(row => [
            metricDisplayValue(first.key, row.first),
            metricDisplayValue(second.key, row.second),
            row.first !== 0 ? `${(row.second / row.first * 100).toFixed(1)}%` : 'N/A'
        ]);
        const hover = `%{x}<br>${first.name}: %{customdata[0]}<br>${second.name}: %{customdata[1]}<br>${second.name} / ${first.name}: %{customdata[2]}<extra></extra>`;
        const traces = [
            { x: rows.map(row => row.year), y: rows.map(row => row.first), type: 'bar', name: first.name, marker: { color: first.colour, line: { width: 0 } }, customdata: custom, hovertemplate: hover },
            { x: rows.map(row => row.year), y: rows.map(row => row.second), type: 'bar', name: second.name, marker: { color: second.colour, line: { width: 0 } }, customdata: custom, hovertemplate: hover }
        ];
        const layout = chartLayout({ period: 'annual' }, true);
        layout.barmode = 'group';
        layout.xaxis.type = 'category';
        Plotly.react(id, traces, layout, { displayModeBar: false, responsive: true });
        renderComparisonFooter(view, id);
    }

    function renderFinancialComparisons(view) {
        if (!view || view.period !== 'annual') return;
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
        bindExpandButtons();
    }

'''

region = re.compile(r'    function syncComparisonControls\(\) \{.*?(?=    function renderFinancialCharts\()', re.S)
js, count = region.subn(comparison_logic, js, count=1)
if count != 1:
    raise SystemExit(f'Expected to replace comparison control/renderer region once, replaced {count}')

js = js.replace(
    "        if (!comparisonView || comparisonPeriod === (view.period || 'annual')) comparisonView = view;",
    "        if (view.period === 'annual') comparisonView = view;",
    1
)

reset_old = """        comparisonPeriod = 'annual';\n        comparisonWindow = 'max';\n        comparisonMode = 'absolute';\n        comparisonView = null;\n        comparisonRequestToken += 1;\n"""
if reset_old not in js:
    raise SystemExit('Comparison reset block not found')
js = js.replace(reset_old, "        comparisonView = null;\n", 1)

# Retain annual comparisons even if Key Financial Metrics switches to Quarterly/TTM.
# Any existing call now renders the saved annual comparisonView rather than requesting another period.
js = js.replace('    bindComparisonControls();', '    bindExpandButtons();', 1)

# Any recursive/legacy comparison render call from the first implementation must be gone.
if 'loadComparisonPeriod(' in js or 'comparisonRequestToken' in js or 'comparisonPeriod' in js or 'comparisonWindow' in js or 'comparisonMode' in js:
    raise SystemExit('Legacy comparison switch logic still present after simplification')
if 'comparison-period-btn' in js or 'comparison-window-btn' in js or 'comparison-mode-btn' in js:
    raise SystemExit('Legacy comparison button bindings still present after simplification')

# Ensure renderView sends the stable annual comparison view to the comparison renderer.
# The first implementation already calls renderFinancialComparisons; normalise any call to the saved annual view.
js = js.replace('renderFinancialComparisons(view);', 'renderFinancialComparisons(comparisonView || (view.period === \'annual\' ? view : null));')

js_path.write_text(js)
print('PHASE4C_SWITCH_REMOVAL_PATCHED')
