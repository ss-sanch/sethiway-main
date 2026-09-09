from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

if 'id="rebalance"' in text or 'rebalance-simulator' in text:
    raise SystemExit('Rebalance simulator UI already present')

text = text.replace(
    '#performance, #attribution, #benchmark, #drawdown, #holdings, #exposure, #fx, #risk, #analytics, #decisions, #journal, #changes',
    '#performance, #attribution, #benchmark, #drawdown, #holdings, #exposure, #fx, #risk, #rebalance, #analytics, #decisions, #journal, #changes',
    1,
)
text = text.replace(
    '<a href="#risk" class="hover:text-blue-600">Risk</a>\n                <a href="#analytics" class="hover:text-blue-600">Analytics</a>',
    '<a href="#risk" class="hover:text-blue-600">Risk</a>\n                <a href="#rebalance" class="hover:text-blue-600">What-if</a>\n                <a href="#analytics" class="hover:text-blue-600">Analytics</a>',
    1,
)

section = r'''

            <!-- REBALANCE WHAT-IF SIMULATOR -->
            <div id="rebalance" class="section-intro"><h2>What-If</h2><div class="section-overview"><strong>Test a rebalance before making it</strong>Change hypothetical holding and cash weights, then recompute concentration and Euler VaR without altering the live portfolio or creating transactions.</div></div>
            <section id="rebalance-card" class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-teal-700 mb-1">Rebalance Simulator</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">What happens to risk if the weights change?</h3>
                        <p id="rebalance-status" class="text-sm text-gray-500 mt-1">Edit the target allocation, make sure it totals 100%, then analyse the hypothetical portfolio.</p>
                    </div>
                    <span class="self-start text-[10px] font-black uppercase tracking-wider rounded-full bg-teal-50 text-teal-700 border border-teal-100 px-3 py-1.5">Simulation only · no trades</span>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-[420px_minmax(0,1fr)] gap-5 items-start">
                    <div class="rounded-xl border border-gray-200 overflow-hidden">
                        <div class="px-4 py-3 bg-gray-50 border-b border-gray-100">
                            <div class="grid grid-cols-[minmax(0,1fr)_72px_92px] gap-2 text-[9px] font-black uppercase tracking-wider text-gray-400">
                                <span>Holding</span><span class="text-right">Current</span><span class="text-right">Target</span>
                            </div>
                        </div>
                        <div id="rebalance-weight-list" class="divide-y divide-gray-100 max-h-[410px] overflow-y-auto">
                            <div class="px-4 py-8 text-sm text-gray-400 text-center">Loading current weights…</div>
                        </div>
                        <div class="px-4 py-3 border-t border-gray-100 bg-violet-50/35">
                            <div class="grid grid-cols-[minmax(0,1fr)_72px_92px] gap-2 items-center">
                                <div><span class="font-black text-sm text-gray-900">Cash</span><p class="text-[9px] text-gray-400 mt-0.5">Zero price risk in this simulator</p></div>
                                <span id="rebalance-current-cash" class="text-right text-xs font-black text-gray-500">—</span>
                                <div class="flex items-center justify-end gap-1"><input id="rebalance-cash-input" type="number" min="0" max="100" step="0.1" class="w-20 rounded-lg border border-gray-200 bg-white px-2 py-1.5 text-right text-sm font-black outline-none focus:border-teal-400" oninput="updateRebalanceTotal()"><span class="text-xs font-bold text-gray-400">%</span></div>
                            </div>
                        </div>
                        <div class="px-4 py-3 border-t border-gray-100 flex items-center justify-between gap-3">
                            <div><p class="text-[9px] uppercase tracking-wider font-black text-gray-400">Target Total</p><p id="rebalance-total" class="text-xl font-black text-gray-900">—</p></div>
                            <p id="rebalance-total-note" class="text-[10px] font-bold text-gray-400 text-right">Must equal 100%</p>
                        </div>
                        <div class="p-4 pt-1 grid grid-cols-2 gap-2">
                            <button type="button" onclick="resetRebalance()" class="rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-black text-gray-700 hover:bg-gray-50">Reset to Current</button>
                            <button type="button" onclick="equalWeightRebalance()" class="rounded-lg border border-teal-100 bg-teal-50 px-3 py-2 text-xs font-black text-teal-800 hover:bg-teal-100">Equal Weight</button>
                            <button id="rebalance-run-btn" type="button" onclick="runRebalanceSimulation()" class="col-span-2 rounded-lg bg-gray-900 px-4 py-3 text-sm font-black text-white hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed" disabled>Analyse Rebalance →</button>
                        </div>
                    </div>

                    <div class="min-w-0">
                        <div class="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
                            <div class="rounded-xl bg-gray-900 text-white p-4 col-span-2 lg:col-span-1"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">10D 99% VaR</p><p id="rebalance-var" class="text-xl font-black mt-1">—</p><p id="rebalance-var-note" class="text-[9px] text-gray-400 mt-1">Current → proposed · % of NAV</p></div>
                            <div class="rounded-xl bg-emerald-50/60 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">Effective Holdings</p><p id="rebalance-effective" class="text-xl font-black mt-1">—</p><p id="rebalance-effective-note" class="text-[9px] text-emerald-700/70 mt-1">Inverse-HHI</p></div>
                            <div class="rounded-xl bg-amber-50/60 border border-amber-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-amber-700">Top 5</p><p id="rebalance-top5" class="text-xl font-black mt-1">—</p><p id="rebalance-top5-note" class="text-[9px] text-amber-700/70 mt-1">Invested-book concentration</p></div>
                            <div class="rounded-xl bg-violet-50/60 border border-violet-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-violet-700">Diversification</p><p id="rebalance-diversification" class="text-xl font-black mt-1">—</p><p id="rebalance-diversification-note" class="text-[9px] text-violet-700/70 mt-1">VaR benefit</p></div>
                            <div class="rounded-xl bg-blue-50/60 border border-blue-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-blue-700">Turnover</p><p id="rebalance-turnover" class="text-xl font-black mt-1">—</p><p id="rebalance-turnover-note" class="text-[9px] text-blue-700/70 mt-1">Approx. share of NAV traded</p></div>
                        </div>

                        <div class="grid grid-cols-1 2xl:grid-cols-2 gap-4">
                            <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                                <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Risk Contribution: Current vs Proposed</h4><p class="text-xs text-gray-500 mt-0.5">How each holding's share of Euler VaR changes under the target allocation.</p></div>
                                <div id="rebalance-risk-chart" style="height:360px"><div class="h-full flex items-center justify-center text-sm text-gray-400">Run a scenario to compare risk contribution.</div></div>
                            </div>
                            <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                                <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Estimated Rebalance Trades</h4><p class="text-xs text-gray-500 mt-0.5">Approximate GBP buys and sells required at the current NAV; transaction costs are excluded.</p></div>
                                <div id="rebalance-trade-chart" style="height:360px"><div class="h-full flex items-center justify-center text-sm text-gray-400">No hypothetical trades analysed yet.</div></div>
                            </div>
                        </div>

                        <div id="rebalance-summary" class="mt-4 rounded-xl bg-teal-50/50 border border-teal-100 px-4 py-3 text-xs font-bold leading-relaxed text-teal-900">Build a target allocation on the left. The simulator will compare concentration and price risk against the live portfolio.</div>
                    </div>
                </div>

                <div id="rebalance-method" class="mt-4 rounded-lg bg-gray-50 border border-gray-100 px-4 py-3 text-[11px] leading-relaxed text-gray-500"><strong class="text-gray-700">Method:</strong> hypothetical only. Current holdings and cash can be reweighted; no transaction is written to SethiPortfolio.</div>
            </section>
'''

anchor = '            <!-- RETURN EFFICIENCY ANALYTICS -->'
if anchor not in text:
    raise SystemExit('Return analytics anchor not found')
text = text.replace(anchor, section + '\n\n' + anchor, 1)

text = text.replace(
    '    let riskAnalyticsData = null;\n    let journalEntries = [];',
    '    let riskAnalyticsData = null;\n    let rebalanceSimulationData = null;\n    let portfolioSnapshot = null;\n    let journalEntries = [];',
    1,
)

js = r'''

    function rebalanceSigned(value, suffix='') {
        const number = Number(value);
        if (!Number.isFinite(number)) return '—';
        return `${number >= 0 ? '+' : ''}${number.toFixed(2)}${suffix}`;
    }

    function initRebalanceEditor(snapshot) {
        portfolioSnapshot = snapshot;
        const holdings = Array.isArray(snapshot?.holdings) ? snapshot.holdings : [];
        const list = document.getElementById('rebalance-weight-list');
        if (!holdings.length) {
            list.innerHTML = '<div class="px-4 py-8 text-sm text-gray-400 text-center">No current holdings are available for simulation.</div>';
            return;
        }
        list.innerHTML = holdings.map(row => {
            const weight = Number(row.weight_pct || 0);
            const symbol = String(row.symbol || '—');
            return `<div class="px-4 py-3 grid grid-cols-[minmax(0,1fr)_72px_92px] gap-2 items-center" data-rebalance-row data-symbol="${symbol}">
                <div class="min-w-0"><span class="font-black text-sm text-gray-900">${symbol}</span><p class="text-[9px] text-gray-400 truncate mt-0.5">${row.name || symbol}</p></div>
                <span class="text-right text-xs font-black text-gray-500">${weight.toFixed(2)}%</span>
                <div class="flex items-center justify-end gap-1"><input type="number" min="0" max="100" step="0.1" value="${weight.toFixed(2)}" data-rebalance-target data-current="${weight.toFixed(4)}" class="w-20 rounded-lg border border-gray-200 bg-white px-2 py-1.5 text-right text-sm font-black outline-none focus:border-teal-400" oninput="updateRebalanceTotal()"><span class="text-xs font-bold text-gray-400">%</span></div>
            </div>`;
        }).join('');
        const cash = Number(snapshot.cash_weight_pct || 0);
        const cashInput = document.getElementById('rebalance-cash-input');
        cashInput.value = cash.toFixed(2);
        cashInput.dataset.current = cash.toFixed(4);
        document.getElementById('rebalance-current-cash').textContent = `${cash.toFixed(2)}%`;
        updateRebalanceTotal(false);
    }

    function rebalanceAllocation() {
        const weights = [];
        document.querySelectorAll('[data-rebalance-row]').forEach(row => {
            const input = row.querySelector('[data-rebalance-target]');
            weights.push({symbol:row.dataset.symbol, weight_pct:Number(input?.value || 0)});
        });
        return {weights, cash_weight_pct:Number(document.getElementById('rebalance-cash-input')?.value || 0)};
    }

    function updateRebalanceTotal(markDirty=true) {
        const allocation = rebalanceAllocation();
        const total = allocation.weights.reduce((sum, row) => sum + Number(row.weight_pct || 0), 0) + Number(allocation.cash_weight_pct || 0);
        const active = allocation.weights.filter(row => Number(row.weight_pct) > .0001).length;
        const valid = Math.abs(total - 100) <= .05 && active >= 2;
        const totalEl = document.getElementById('rebalance-total');
        totalEl.textContent = `${total.toFixed(2)}%`;
        totalEl.className = `text-xl font-black ${valid ? 'text-emerald-600' : 'text-red-600'}`;
        document.getElementById('rebalance-total-note').textContent = active < 2 ? 'Keep at least 2 holdings' : valid ? 'Ready to analyse' : `${rebalanceSigned(100-total, '%')} remaining`;
        const run = document.getElementById('rebalance-run-btn');
        run.disabled = !valid;
        if (markDirty && rebalanceSimulationData) {
            document.getElementById('rebalance-status').textContent = 'Target weights changed since the last analysis — run the simulator again to refresh the comparison.';
        }
    }

    function resetRebalance() {
        document.querySelectorAll('[data-rebalance-target]').forEach(input => { input.value = Number(input.dataset.current || 0).toFixed(2); });
        const cash = document.getElementById('rebalance-cash-input');
        cash.value = Number(cash.dataset.current || 0).toFixed(2);
        updateRebalanceTotal();
    }

    function equalWeightRebalance() {
        const inputs = [...document.querySelectorAll('[data-rebalance-target]')];
        if (!inputs.length) return;
        const cash = Math.max(0, Math.min(100, Number(document.getElementById('rebalance-cash-input').value || 0)));
        const invested = 100 - cash;
        const base = Math.floor((invested / inputs.length) * 100) / 100;
        let assigned = 0;
        inputs.forEach((input, index) => {
            const value = index === inputs.length - 1 ? invested - assigned : base;
            input.value = value.toFixed(2);
            assigned += value;
        });
        updateRebalanceTotal();
    }

    function rebalancePairText(current, proposed, digits=2, suffix='') {
        return `${Number(current || 0).toFixed(digits)}${suffix} → ${Number(proposed || 0).toFixed(digits)}${suffix}`;
    }

    function renderRebalanceSimulation(data) {
        rebalanceSimulationData = data;
        const current = data?.current?.risk || {};
        const proposed = data?.proposed?.risk || {};
        const changes = data?.changes || {};

        document.getElementById('rebalance-status').textContent = `${Number(data?.parameters?.observations || 0)} aligned daily observations · 99% / 10-day Euler VaR · target allocation analysed without changing the live portfolio`;

        const varEl = document.getElementById('rebalance-var');
        varEl.textContent = rebalancePairText(current.portfolio_var_nav_pct, proposed.portfolio_var_nav_pct, 2, '%');
        const varDelta = Number(changes.portfolio_var_nav_change_pp || 0);
        varEl.className = `text-xl font-black mt-1 ${varDelta <= 0 ? 'text-emerald-400' : 'text-red-400'}`;
        document.getElementById('rebalance-var-note').textContent = `${rebalanceSigned(varDelta, 'pp')} · ${fmtGBP(changes.portfolio_var_change)} VaR change`;

        const effectiveDelta = Number(changes.effective_holdings_change || 0);
        document.getElementById('rebalance-effective').textContent = rebalancePairText(current.effective_holdings, proposed.effective_holdings, 1);
        document.getElementById('rebalance-effective-note').textContent = `${rebalanceSigned(effectiveDelta)} effective holdings`;

        const top5Delta = Number(changes.top_5_change_pp || 0);
        document.getElementById('rebalance-top5').textContent = rebalancePairText(current.top_5_invested_weight_pct, proposed.top_5_invested_weight_pct, 1, '%');
        document.getElementById('rebalance-top5-note').textContent = `${rebalanceSigned(top5Delta, 'pp')} concentration`;

        const divDelta = Number(changes.diversification_change_pp || 0);
        document.getElementById('rebalance-diversification').textContent = rebalancePairText(current.diversification_pct, proposed.diversification_pct, 1, '%');
        document.getElementById('rebalance-diversification-note').textContent = `${rebalanceSigned(divDelta, 'pp')} diversification benefit`;

        document.getElementById('rebalance-turnover').textContent = `${Number(changes.turnover_pct || 0).toFixed(1)}%`;
        document.getElementById('rebalance-turnover-note').textContent = `${Number(changes.trade_count || 0)} material holding change${Number(changes.trade_count || 0) === 1 ? '' : 's'}`;

        const currentRisk = new Map((current.components || []).map(row => [row.ticker, Number(row.contribution_pct || 0)]));
        const proposedRisk = new Map((proposed.components || []).map(row => [row.ticker, Number(row.contribution_pct || 0)]));
        const symbols = [...new Set([...currentRisk.keys(), ...proposedRisk.keys()])]
            .sort((a,b) => Math.abs((proposedRisk.get(a)||0)) - Math.abs((proposedRisk.get(b)||0)));
        Plotly.react('rebalance-risk-chart', [
            {x:symbols.map(symbol => currentRisk.get(symbol) || 0), y:symbols, type:'bar', orientation:'h', name:'Current', marker:{color:'#94a3b8'}, hovertemplate:'<b>%{y}</b><br>Current risk: %{x:.2f}%<extra></extra>'},
            {x:symbols.map(symbol => proposedRisk.get(symbol) || 0), y:symbols, type:'bar', orientation:'h', name:'Proposed', marker:{color:'#0f766e'}, hovertemplate:'<b>%{y}</b><br>Proposed risk: %{x:.2f}%<extra></extra>'}
        ], {
            barmode:'group', margin:{t:35,r:18,l:72,b:45}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
            legend:{orientation:'h',x:0,y:1.13,font:{size:10}}, xaxis:{title:'Euler VaR contribution (%)',gridcolor:'#f3f4f6',zeroline:true,zerolinecolor:'#9ca3af'}, yaxis:{automargin:true}
        }, {displayModeBar:false,responsive:true});

        const trades = Array.isArray(changes.trades) ? [...changes.trades].reverse() : [];
        if (!trades.length) {
            document.getElementById('rebalance-trade-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Target allocation matches the current portfolio.</div>';
        } else {
            const values = trades.map(row => Number(row.estimated_value_change || 0));
            Plotly.react('rebalance-trade-chart', [{
                x:values, y:trades.map(row => row.symbol), type:'bar', orientation:'h',
                marker:{color:values.map(value => value >= 0 ? '#10b981' : '#ef4444')},
                text:values.map(value => `${value >= 0 ? 'BUY ' : 'SELL '}${fmtGBP(Math.abs(value))}`), textposition:'auto',
                hovertemplate:'<b>%{y}</b><br>Estimated change: £%{x:,.0f}<extra></extra>'
            }], {
                margin:{t:20,r:18,l:72,b:45}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', showlegend:false,
                xaxis:{title:'Estimated value change (£)',gridcolor:'#f3f4f6',zeroline:true,zerolinecolor:'#9ca3af'}, yaxis:{automargin:true}
            }, {displayModeBar:false,responsive:true});
        }

        const largest = changes.largest_trade;
        const riskWord = varDelta < -0.005 ? 'reduces' : varDelta > .005 ? 'increases' : 'leaves broadly unchanged';
        const concentrationWord = top5Delta < -0.05 ? 'reduces' : top5Delta > .05 ? 'increases' : 'leaves broadly unchanged';
        document.getElementById('rebalance-summary').innerHTML = `<strong>Scenario read:</strong> this allocation ${riskWord} 10-day 99% price VaR (${rebalanceSigned(varDelta, 'pp')} of NAV) and ${concentrationWord} Top-5 concentration (${rebalanceSigned(top5Delta, 'pp')}). Estimated one-way turnover is ${Number(changes.turnover_pct || 0).toFixed(1)}%.${largest ? ` Largest shift: <strong>${largest.symbol}</strong> ${rebalanceSigned(largest.change_pp, 'pp')} (${largest.estimated_value_change >= 0 ? 'buy' : 'sell'} ${fmtGBP(Math.abs(largest.estimated_value_change))}).` : ''}`;
        document.getElementById('rebalance-method').innerHTML = `<strong class="text-gray-700">Method:</strong> ${data.methodology || 'Static target-weight simulation using the same Euler VaR framework as Portfolio Risk.'}`;
    }

    async function runRebalanceSimulation() {
        const button = document.getElementById('rebalance-run-btn');
        if (button.disabled) return;
        const original = button.textContent;
        button.disabled = true;
        button.textContent = 'Analysing…';
        document.getElementById('rebalance-status').textContent = 'Recomputing concentration and risk for the hypothetical allocation…';
        try {
            const response = await fetch(`${API_BASE}/${PORTFOLIO_SLUG}/rebalance-simulator`, {
                method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(rebalanceAllocation())
            });
            if (!response.ok) {
                let detail = `Rebalance simulation failed (${response.status})`;
                try { const body = await response.json(); detail = body.detail || detail; } catch (_) {}
                throw new Error(detail);
            }
            renderRebalanceSimulation(await response.json());
        } catch (error) {
            console.error('SethiPortfolio rebalance simulator failed:', error);
            document.getElementById('rebalance-status').textContent = `Unable to analyse this target allocation: ${error.message}`;
        } finally {
            button.textContent = original;
            updateRebalanceTotal(false);
        }
    }
'''

js_anchor = '    function openJournalModal(entryId) {'
if js_anchor not in text:
    raise SystemExit('JS insertion anchor not found')
text = text.replace(js_anchor, js + '\n\n' + js_anchor, 1)

text = text.replace(
    '            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;',
    '            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;\n            portfolioSnapshot = snapshot;',
    1,
)
text = text.replace(
    '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics();',
    '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); initRebalanceEditor(snapshot); renderAnalytics();',
    1,
)

path.write_text(text)
