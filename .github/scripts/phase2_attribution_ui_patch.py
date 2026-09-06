from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #holdings, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #holdings, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin',
    ),
    (
        '<a href="#performance" class="hover:text-blue-600">Performance</a>\n                <a href="#holdings" class="hover:text-blue-600">Holdings</a>',
        '<a href="#performance" class="hover:text-blue-600">Performance</a>\n                <a href="#attribution" class="hover:text-blue-600">Attribution</a>\n                <a href="#holdings" class="hover:text-blue-600">Holdings</a>',
        'navigation attribution link',
    ),
    (
        '<button onclick="setRange(\'1M\', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">1M</button>',
        '<button data-range="1M" onclick="setRange(\'1M\', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">1M</button>',
        'performance 1M range',
    ),
    (
        '<button onclick="setRange(\'3M\', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">3M</button>',
        '<button data-range="3M" onclick="setRange(\'3M\', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">3M</button>',
        'performance 3M range',
    ),
    (
        '<button onclick="setRange(\'YTD\', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">YTD</button>',
        '<button data-range="YTD" onclick="setRange(\'YTD\', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">YTD</button>',
        'performance YTD range',
    ),
    (
        '<button onclick="setRange(\'SI\', this)" class="range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Since Inception</button>',
        '<button data-range="SI" onclick="setRange(\'SI\', this)" class="range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Since Inception</button>',
        'performance SI range',
    ),
    (
        'let portfolioData = { dates: [], portfolio: [], sp500: [], nasdaq: [], vwrl: [] };\n    let journalEntries = [];',
        'let portfolioData = { dates: [], portfolio: [], sp500: [], nasdaq: [], vwrl: [] };\n    let attributionData = { periods: {} };\n    let journalEntries = [];',
        'attribution state',
    ),
]

for old, new, label in replacements:
    if new in text and old not in text:
        continue
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    text = text.replace(old, new, 1)

section_anchor = '''            </section>

            <!-- COMPOSITION + HOLDINGS -->'''
section_html = '''            </section>

            <!-- PERFORMANCE ATTRIBUTION -->
            <div id="attribution" class="section-intro"><h2>Performance Attribution</h2><div class="section-overview"><strong>What actually drove the return</strong>Decompose portfolio performance into the contribution from each investment. The calculation uses dated transactions and changing position sizes rather than applying today's weights retrospectively.</div></div>
            <section class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Return Drivers</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">Where portfolio performance came from</h3>
                        <p class="text-sm text-gray-500 mt-1 max-w-3xl">Instrument P&amp;L is reconciled from opening and closing market values plus every purchase and sale during the period.</p>
                    </div>
                    <div class="flex rounded-lg bg-gray-100 p-1 text-xs font-black shrink-0">
                        <button data-range="1M" onclick="setRange('1M', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">1M</button>
                        <button data-range="3M" onclick="setRange('3M', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">3M</button>
                        <button data-range="YTD" onclick="setRange('YTD', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">YTD</button>
                        <button data-range="SI" onclick="setRange('SI', this)" class="range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Since Inception</button>
                    </div>
                </div>

                <div class="grid grid-cols-2 xl:grid-cols-4 gap-3 mb-5">
                    <div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Period Return</p><p id="attribution-return" class="text-2xl font-black mt-1">—</p><p id="attribution-period" class="text-[10px] text-gray-400 mt-1">—</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Portfolio P&amp;L</p><p id="attribution-pnl" class="text-2xl font-black mt-1">—</p><p class="text-[10px] text-gray-400 mt-1">Change in NAV over the period</p></div>
                    <div class="rounded-xl bg-emerald-50/60 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">Biggest Contributor</p><p id="attribution-top-name" class="text-lg font-black mt-1 text-gray-900">—</p><p id="attribution-top-value" class="text-sm font-black mt-1 text-emerald-700">—</p></div>
                    <div class="rounded-xl bg-red-50/50 border border-red-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-red-700">Biggest Detractor</p><p id="attribution-bottom-name" class="text-lg font-black mt-1 text-gray-900">—</p><p id="attribution-bottom-value" class="text-sm font-black mt-1 text-red-600">—</p></div>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.35fr)] gap-5 items-start">
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Contribution to Portfolio Return</h4><p class="text-xs text-gray-500 mt-0.5">Percentage-point impact by investment; the largest positive and negative drivers are shown.</p></div>
                        <div id="attribution-chart" style="height:340px"></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 overflow-hidden min-w-0">
                        <div class="px-4 py-3 border-b border-gray-100 bg-gray-50"><h4 class="font-black text-sm text-gray-900">Attribution Detail</h4><p class="text-xs text-gray-500 mt-0.5">Average weight reflects the capital actually deployed through the selected period.</p></div>
                        <div class="overflow-x-auto max-h-[390px] overflow-y-auto">
                            <table class="w-full text-sm">
                                <thead class="sticky top-0 bg-white text-gray-400 uppercase tracking-wider text-[10px] border-b border-gray-100">
                                    <tr><th class="text-left px-4 py-3">Holding</th><th class="text-right px-3 py-3">Avg Weight</th><th class="text-right px-3 py-3">P&amp;L</th><th class="text-right px-4 py-3">Contribution</th></tr>
                                </thead>
                                <tbody id="attribution-table"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div id="attribution-reconciliation" class="mt-4 rounded-lg bg-blue-50/50 border border-blue-100 px-4 py-3 text-[11px] font-bold text-blue-800">Loading transaction-aware attribution…</div>
            </section>

            <!-- COMPOSITION + HOLDINGS -->'''

if section_html not in text:
    count = text.count(section_anchor)
    if count != 1:
        raise SystemExit(f'attribution section anchor: expected 1 match, found {count}')
    text = text.replace(section_anchor, section_html, 1)

setrange_old = '''    function setRange(range, btn) {
        currentRange = range;
        document.querySelectorAll('.range-btn').forEach(b => b.className='range-btn px-3 py-1.5 rounded-md text-gray-500');
        btn.className='range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm';
        renderPerformance();
    }'''

setrange_new = '''    function setRange(range, btn) {
        currentRange = range;
        document.querySelectorAll('.range-btn').forEach(b => {
            b.className = b.dataset.range === range
                ? 'range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm'
                : 'range-btn px-3 py-1.5 rounded-md text-gray-500';
        });
        renderPerformance();
        renderAttribution();
    }'''

if setrange_new not in text:
    count = text.count(setrange_old)
    if count != 1:
        raise SystemExit(f'setRange anchor: expected 1 match, found {count}')
    text = text.replace(setrange_old, setrange_new, 1)

function_anchor = '''    function setRange(range, btn) {
        currentRange = range;
        document.querySelectorAll('.range-btn').forEach(b => {
            b.className = b.dataset.range === range
                ? 'range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm'
                : 'range-btn px-3 py-1.5 rounded-md text-gray-500';
        });
        renderPerformance();
        renderAttribution();
    }
'''

attribution_function = function_anchor + '''
    function renderAttribution() {
        const period = attributionData?.periods?.[currentRange];
        const table = document.getElementById('attribution-table');
        const reconciliation = document.getElementById('attribution-reconciliation');
        if (!period) {
            if (table) table.innerHTML = '<tr><td colspan="4" class="px-4 py-8 text-center text-gray-400">Attribution is unavailable for this period.</td></tr>';
            if (reconciliation) reconciliation.textContent = 'Transaction-aware attribution is temporarily unavailable.';
            return;
        }

        const components = Array.isArray(period.components) ? [...period.components] : [];
        const positives = components.filter(c => Number(c.contribution_pp) > 0).sort((a,b) => b.contribution_pp - a.contribution_pp);
        const negatives = components.filter(c => Number(c.contribution_pp) < 0).sort((a,b) => a.contribution_pp - b.contribution_pp);
        const top = positives[0];
        const bottom = negatives[0];

        const returnEl = document.getElementById('attribution-return');
        returnEl.textContent = fmtPct(period.portfolio_return_pct);
        returnEl.className = `text-2xl font-black mt-1 ${Number(period.portfolio_return_pct) >= 0 ? 'text-emerald-400' : 'text-red-400'}`;
        document.getElementById('attribution-pnl').textContent = fmtGBP(period.total_pnl);
        document.getElementById('attribution-pnl').className = `text-2xl font-black mt-1 ${Number(period.total_pnl) >= 0 ? 'text-emerald-700' : 'text-red-600'}`;
        document.getElementById('attribution-period').textContent = `${prettyDate(period.start_date)} → ${prettyDate(period.end_date)}`;
        document.getElementById('attribution-top-name').textContent = top ? top.symbol : 'None';
        document.getElementById('attribution-top-value').textContent = top ? `${fmtPp(top.contribution_pp)} · ${fmtGBP(top.pnl)}` : 'No positive contribution';
        document.getElementById('attribution-bottom-name').textContent = bottom ? bottom.symbol : 'None';
        document.getElementById('attribution-bottom-value').textContent = bottom ? `${fmtPp(bottom.contribution_pp)} · ${fmtGBP(bottom.pnl)}` : 'No negative contribution';

        if (!components.length) {
            table.innerHTML = '<tr><td colspan="4" class="px-4 py-8 text-center text-gray-400">No attributable positions in this period.</td></tr>';
            document.getElementById('attribution-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">No contribution data for this period.</div>';
        } else {
            table.innerHTML = components.map(c => {
                const positive = Number(c.contribution_pp) >= 0;
                return `<tr class="border-b border-gray-50 last:border-0">
                    <td class="px-4 py-3"><a href="sethistock.html?ticker=${encodeURIComponent(c.symbol)}&source=portfolio-attribution" class="font-black text-gray-900 hover:text-blue-700">${c.symbol}</a><div class="text-[10px] text-gray-400 mt-0.5 max-w-[220px] truncate">${c.name || c.symbol}</div></td>
                    <td class="px-3 py-3 text-right font-bold text-gray-600">${Number(c.average_weight_pct || 0).toFixed(2)}%</td>
                    <td class="px-3 py-3 text-right font-black ${Number(c.pnl) >= 0 ? 'text-emerald-600' : 'text-red-600'}">${fmtGBP(c.pnl)}</td>
                    <td class="px-4 py-3 text-right font-black ${positive ? 'text-emerald-600' : 'text-red-600'}">${fmtPp(c.contribution_pp)}</td>
                </tr>`;
            }).join('');

            let shown;
            if (components.length <= 10) {
                shown = [...components];
            } else {
                const chosen = [...positives.slice(0, 5), ...negatives.slice(0, 5)];
                const keys = new Set(chosen.map(c => c.symbol));
                const otherContribution = components.filter(c => !keys.has(c.symbol)).reduce((sum, c) => sum + Number(c.contribution_pp || 0), 0);
                shown = [...chosen];
                if (Math.abs(otherContribution) >= 0.005) shown.push({symbol:'Other', contribution_pp:otherContribution, pnl:0});
            }
            shown.sort((a,b) => Number(a.contribution_pp) - Number(b.contribution_pp));
            Plotly.newPlot('attribution-chart', [{
                x: shown.map(c => Number(c.contribution_pp)),
                y: shown.map(c => c.symbol),
                type:'bar', orientation:'h',
                marker:{color:shown.map(c => Number(c.contribution_pp) >= 0 ? '#10b981' : '#ef4444')},
                text:shown.map(c => fmtPp(c.contribution_pp)), textposition:'auto',
                hovertemplate:'<b>%{y}</b><br>Contribution: %{x:.2f}pp<extra></extra>'
            }], {
                margin:{t:12,r:20,l:65,b:42},
                xaxis:{title:'Contribution (percentage points)', gridcolor:'#f3f4f6', zeroline:true, zerolinecolor:'#9ca3af'},
                yaxis:{automargin:true},
                paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', showlegend:false
            }, {displayModeBar:false, responsive:true});
        }

        const error = Math.abs(Number(period.reconciliation_error || 0));
        const componentTotal = Number(period.component_contribution_pp || 0);
        reconciliation.innerHTML = `<strong>Reconciled attribution:</strong> components sum to ${fmtPp(componentTotal)} versus a ${fmtPct(period.portfolio_return_pct)} portfolio return. ${error < 0.05 ? 'Transaction and fee effects reconcile to NAV.' : `Residual reconciliation difference: ${fmtGBP(error)}.`}`;
        reconciliation.className = error < 0.05
            ? 'mt-4 rounded-lg bg-blue-50/50 border border-blue-100 px-4 py-3 text-[11px] font-bold text-blue-800'
            : 'mt-4 rounded-lg bg-amber-50 border border-amber-100 px-4 py-3 text-[11px] font-bold text-amber-800';
    }
'''

if attribution_function not in text:
    count = text.count(function_anchor)
    if count != 1:
        raise SystemExit(f'attribution function anchor: expected 1 match, found {count}')
    text = text.replace(function_anchor, attribution_function, 1)

load_old = '''            const [portfolioRes, performanceRes, journalRes, transactionsRes] = await Promise.all([
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/performance`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/journal?limit=100`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/transactions`)
            ]);
            if (![portfolioRes,performanceRes,journalRes,transactionsRes].every(r=>r.ok)) throw new Error('One or more portfolio API requests failed.');
            const [portfolioPayload, performance, journalPayload, transactionPayload] = await Promise.all([
                portfolioRes.json(), performanceRes.json(), journalRes.json(), transactionsRes.json()
            ]);'''

load_new = '''            const [portfolioRes, performanceRes, attributionRes, journalRes, transactionsRes] = await Promise.all([
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/performance`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/attribution`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/journal?limit=100`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/transactions`)
            ]);
            if (![portfolioRes,performanceRes,attributionRes,journalRes,transactionsRes].every(r=>r.ok)) throw new Error('One or more portfolio API requests failed.');
            const [portfolioPayload, performance, attributionPayload, journalPayload, transactionPayload] = await Promise.all([
                portfolioRes.json(), performanceRes.json(), attributionRes.json(), journalRes.json(), transactionsRes.json()
            ]);
            attributionData = attributionPayload || { periods: {} };'''

if load_new not in text:
    count = text.count(load_old)
    if count != 1:
        raise SystemExit(f'load attribution anchor: expected 1 match, found {count}')
    text = text.replace(load_old, load_new, 1)

render_old = '            renderPerformance(); renderHoldings(snapshot); renderAnalytics(performance);\n            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions);'
render_new = '            renderPerformance(); renderAttribution(); renderHoldings(snapshot); renderAnalytics(performance);\n            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions);'
if render_new not in text:
    count = text.count(render_old)
    if count != 1:
        raise SystemExit(f'render attribution anchor: expected 1 match, found {count}')
    text = text.replace(render_old, render_new, 1)

error_old = '''            document.getElementById('performance-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load live portfolio data.</div>';
            document.getElementById('holdings-table').innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">Unable to load holdings.</td></tr>';'''
error_new = '''            document.getElementById('performance-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load live portfolio data.</div>';
            document.getElementById('attribution-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load performance attribution.</div>';
            document.getElementById('attribution-table').innerHTML = '<tr><td colspan="4" class="px-4 py-8 text-center text-gray-400">Unable to load attribution.</td></tr>';
            document.getElementById('holdings-table').innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">Unable to load holdings.</td></tr>';'''
if error_new not in text:
    count = text.count(error_old)
    if count != 1:
        raise SystemExit(f'attribution error-state anchor: expected 1 match, found {count}')
    text = text.replace(error_old, error_new, 1)

path.write_text(text)
