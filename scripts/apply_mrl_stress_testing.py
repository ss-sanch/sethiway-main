from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')

# 1. Keep stress chart aligned with existing wide-screen MRL chart heights.
old = '''            #market-risk-lab #corr-chart,
            #market-risk-lab #risk-contribution-chart,
            #market-risk-lab #derivatives-chart { height: 393px !important; }'''
new = '''            #market-risk-lab #corr-chart,
            #market-risk-lab #risk-contribution-chart,
            #market-risk-lab #derivatives-chart,
            #market-risk-lab #stress-chart { height: 393px !important; }'''
if old not in s:
    raise SystemExit('Wide-screen chart CSS marker not found')
s = s.replace(old, new, 1)

# 2. Replace the full-width options button with compact Options + Stress controls.
old = '''                        <button type="button" onclick="openOptionsOverlay()" class="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-violet-200 bg-violet-50/60 hover:bg-violet-50 transition text-xs font-black text-violet-700">
                            <span>Options Overlay</span><span id="option-count-badge" class="bg-white border border-violet-200 rounded-full px-2 py-0.5 text-[10px]">0 positions</span>
                        </button>'''
new = '''                        <div class="grid grid-cols-2 gap-2">
                            <button type="button" onclick="openOptionsOverlay()" class="flex items-center justify-between gap-2 px-3 py-2 rounded-lg border border-violet-200 bg-violet-50/60 hover:bg-violet-50 transition text-[11px] font-black text-violet-700">
                                <span>Options</span><span id="option-count-badge" class="bg-white border border-violet-200 rounded-full px-2 py-0.5 text-[9px]">0 positions</span>
                            </button>
                            <button type="button" onclick="openStressTest()" class="flex items-center justify-between gap-2 px-3 py-2 rounded-lg border border-amber-200 bg-amber-50/60 hover:bg-amber-50 transition text-[11px] font-black text-amber-700">
                                <span>Stress Test</span><span id="stress-count-badge" class="bg-white border border-amber-200 rounded-full px-2 py-0.5 text-[9px]">4 presets</span>
                            </button>
                        </div>'''
if old not in s:
    raise SystemExit('Options control marker not found')
s = s.replace(old, new, 1)

# 3. Add Stress tab and view to the third analytics card.
old = '''                                    <button id="risk-tab-attribution" type="button" onclick="showRiskDetail('attribution')" class="px-2 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Contribution</button>
                                    <button id="risk-tab-greeks" type="button" onclick="showRiskDetail('greeks')" class="px-2 py-1.5 rounded-md text-gray-500">Greeks</button>
                                    <button id="risk-tab-correlation" type="button" onclick="showRiskDetail('correlation')" class="px-2 py-1.5 rounded-md text-gray-500">Correlation</button>'''
new = '''                                    <button id="risk-tab-attribution" type="button" onclick="showRiskDetail('attribution')" class="px-2 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Contrib</button>
                                    <button id="risk-tab-greeks" type="button" onclick="showRiskDetail('greeks')" class="px-2 py-1.5 rounded-md text-gray-500">Greeks</button>
                                    <button id="risk-tab-stress" type="button" onclick="showRiskDetail('stress')" class="px-2 py-1.5 rounded-md text-gray-500">Stress</button>
                                    <button id="risk-tab-correlation" type="button" onclick="showRiskDetail('correlation')" class="px-2 py-1.5 rounded-md text-gray-500">Corr</button>'''
if old not in s:
    raise SystemExit('Risk tabs marker not found')
s = s.replace(old, new, 1)

old = '''                            <div id="derivatives-view" class="hidden"><div id="derivatives-chart" style="height:255px"></div></div>
                            <div id="correlation-view" class="hidden"><div id="corr-chart" style="height:255px"></div></div>'''
new = '''                            <div id="derivatives-view" class="hidden"><div id="derivatives-chart" style="height:255px"></div></div>
                            <div id="stress-view" class="hidden"><div id="stress-chart" style="height:255px"></div></div>
                            <div id="correlation-view" class="hidden"><div id="corr-chart" style="height:255px"></div></div>'''
if old not in s:
    raise SystemExit('Risk views marker not found')
s = s.replace(old, new, 1)

# 4. Insert compact custom stress modal before the options modal.
marker = '''    <!-- MODAL: MARKET RISK LAB OPTIONS OVERLAY -->'''
modal = '''    <!-- MODAL: MARKET RISK LAB STRESS TEST -->
    <div id="modal-risk-stress" class="hidden fixed inset-0 z-[225] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl p-6 max-w-lg w-full relative">
            <button type="button" onclick="closeStressTest()" class="absolute top-4 right-4 text-gray-400 hover:text-red-500 text-xl font-bold">×</button>
            <div class="pr-10 mb-5">
                <h3 class="text-2xl font-black text-gray-900">Custom Stress Scenario</h3>
                <p class="text-sm text-gray-500 mt-1">Add one instantaneous market shock alongside the four preset scenarios. Options are fully repriced under the shocked spot and volatility state.</p>
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div><label class="block text-[10px] font-black uppercase tracking-widest text-gray-500 mb-1">Equity Shock (%)</label><input id="stress-equity-shock" type="number" min="-80" max="80" step="1" value="-15" class="w-full border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 font-bold"></div>
                <div><label class="block text-[10px] font-black uppercase tracking-widest text-gray-500 mb-1">Vol Shock (pts)</label><input id="stress-vol-shock" type="number" min="-100" max="200" step="1" value="12" class="w-full border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 font-bold"></div>
            </div>
            <div class="flex items-center justify-between gap-3 mt-5 pt-4 border-t border-gray-100">
                <button type="button" onclick="clearCustomStress()" class="px-4 py-2 rounded-lg bg-gray-50 text-gray-500 font-bold text-sm border border-gray-200">Use Presets Only</button>
                <button type="button" onclick="applyCustomStress()" class="px-5 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-black text-sm shadow-sm">Apply Custom Scenario</button>
            </div>
        </div>
    </div>

''' + marker
if marker not in s:
    raise SystemExit('Options modal marker not found')
s = s.replace(marker, modal, 1)

# 5. Add stress state/helpers alongside options state.
old = '''        let latestRiskData = null;
        let activeRiskOptions = [];'''
new = '''        let latestRiskData = null;
        let activeRiskOptions = [];
        let customRiskStress = null;

        function updateStressBadge() {
            const badge = document.getElementById('stress-count-badge');
            if (badge) badge.innerText = customRiskStress ? '+ custom' : '4 presets';
        }

        function openStressTest() {
            document.getElementById('stress-equity-shock').value = customRiskStress?.equity_shock_pct ?? -15;
            document.getElementById('stress-vol-shock').value = customRiskStress?.vol_shock_points ?? 12;
            toggleModal('modal-risk-stress');
        }

        function closeStressTest() { toggleModal('modal-risk-stress'); }

        function applyCustomStress() {
            const equityShock = parseFloat(document.getElementById('stress-equity-shock').value);
            const volShock = parseFloat(document.getElementById('stress-vol-shock').value);
            if (!Number.isFinite(equityShock) || equityShock < -80 || equityShock > 80 || !Number.isFinite(volShock) || volShock < -100 || volShock > 200) {
                alert('Enter an equity shock between -80% and +80% and a volatility shock between -100 and +200 points.');
                return;
            }
            customRiskStress = { equity_shock_pct: equityShock, vol_shock_points: volShock };
            updateStressBadge();
            toggleModal('modal-risk-stress');
        }

        function clearCustomStress() {
            customRiskStress = null;
            updateStressBadge();
            toggleModal('modal-risk-stress');
        }'''
if old not in s:
    raise SystemExit('Risk state marker not found')
s = s.replace(old, new, 1)

# 6. Extend showRiskDetail to include stress.
old = '''            const views = { attribution: document.getElementById('risk-attribution-view'), greeks: document.getElementById('derivatives-view'), correlation: document.getElementById('correlation-view') };
            const tabs = { attribution: document.getElementById('risk-tab-attribution'), greeks: document.getElementById('risk-tab-greeks'), correlation: document.getElementById('risk-tab-correlation') };'''
new = '''            const views = { attribution: document.getElementById('risk-attribution-view'), greeks: document.getElementById('derivatives-view'), stress: document.getElementById('stress-view'), correlation: document.getElementById('correlation-view') };
            const tabs = { attribution: document.getElementById('risk-tab-attribution'), greeks: document.getElementById('risk-tab-greeks'), stress: document.getElementById('risk-tab-stress'), correlation: document.getElementById('risk-tab-correlation') };'''
if old not in s:
    raise SystemExit('showRiskDetail views marker not found')
s = s.replace(old, new, 1)

old = '''            } else if (view === 'greeks') {
                title.innerText = 'Derivatives Risk';
                const d = latestRiskData?.derivatives;
                subtitle.innerText = d?.active ? `Δ £${Math.round(d.aggregate_dollar_delta).toLocaleString()} · Γ(1%) ${formatMoney(d.aggregate_gamma_pnl_1pct)} · Vega ${formatMoney(d.aggregate_vega_pnl_1vol)}/vol pt` : 'No options overlay is active.';
                if (document.getElementById('derivatives-chart').data) Plotly.Plots.resize('derivatives-chart');
            } else {'''
new = '''            } else if (view === 'greeks') {
                title.innerText = 'Derivatives Risk';
                const d = latestRiskData?.derivatives;
                subtitle.innerText = d?.active ? `Δ £${Math.round(d.aggregate_dollar_delta).toLocaleString()} · Γ(1%) ${formatMoney(d.aggregate_gamma_pnl_1pct)} · Vega ${formatMoney(d.aggregate_vega_pnl_1vol)}/vol pt` : 'No options overlay is active.';
                if (document.getElementById('derivatives-chart').data) Plotly.Plots.resize('derivatives-chart');
            } else if (view === 'stress') {
                title.innerText = 'Stress Testing';
                const st = latestRiskData?.stress_testing;
                subtitle.innerText = st?.worst_scenario ? `Worst: ${st.worst_scenario} ${formatMoney(st.worst_pnl)} · full revaluation` : 'Preset and custom market shock scenarios.';
                if (document.getElementById('stress-chart').data) Plotly.Plots.resize('stress-chart');
            } else {'''
if old not in s:
    raise SystemExit('showRiskDetail greeks marker not found')
s = s.replace(old, new, 1)

# 7. Send custom stress to backend.
old = '''                options: activeRiskOptions.map(o => ({ underlying: o.underlying, option_type: o.option_type, strike: o.strike, days_to_expiry: o.days_to_expiry, implied_vol: o.implied_vol_pct / 100, contracts: o.contracts, multiplier: 100 })),
                portfolio_value:'''
new = '''                options: activeRiskOptions.map(o => ({ underlying: o.underlying, option_type: o.option_type, strike: o.strike, days_to_expiry: o.days_to_expiry, implied_vol: o.implied_vol_pct / 100, contracts: o.contracts, multiplier: 100 })),
                custom_stress: customRiskStress,
                portfolio_value:'''
if old not in s:
    raise SystemExit('Payload marker not found')
s = s.replace(old, new, 1)

# 8. Render stress scenario chart before deciding the default detail view.
old = '''                const derivatives = data.derivatives;
                const derivativesChart = document.getElementById('derivatives-chart');'''
new = '''                const stress = data.stress_testing;
                if (stress?.scenarios?.length) {
                    const scenarios = stress.scenarios;
                    Plotly.newPlot('stress-chart', [
                        { x: scenarios.map(r => r.name), y: scenarios.map(r => r.equity_pnl), name: 'Equity P&L', type: 'bar', marker: { color: '#9ca3af' } },
                        { x: scenarios.map(r => r.name), y: scenarios.map(r => r.options_pnl), name: 'Options P&L', type: 'bar', marker: { color: '#7c3aed' } },
                        { x: scenarios.map(r => r.name), y: scenarios.map(r => r.total_pnl), name: 'Total P&L', type: 'scatter', mode: 'lines+markers', line: { color: '#ef4444', width: 3 }, marker: { size: 7 } }
                    ], {
                        barmode: 'relative', margin: { t: 10, r: 10, l: 55, b: 60 },
                        yaxis: { title: 'Scenario P&L (£)', gridcolor: '#f3f4f6', zeroline: true, zerolinecolor: '#d1d5db' },
                        xaxis: { tickangle: -15 },
                        legend: { orientation: 'h', y: 1.12, font: { size: 9 } },
                        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)'
                    }, { displayModeBar: false, responsive: true });
                }

                const derivatives = data.derivatives;
                const derivativesChart = document.getElementById('derivatives-chart');'''
if old not in s:
    raise SystemExit('Derivatives render marker not found')
s = s.replace(old, new, 1)

old = '''                    showRiskDetail('greeks');
                } else {
                    derivativesChart.innerHTML = `<div class="h-full flex items-center justify-center text-sm text-gray-400 italic text-center px-8">Add an option through Options Overlay to activate Delta, Gamma and Vega risk.</div>`;
                    showRiskDetail('attribution');
                }'''
new = '''                    showRiskDetail(customRiskStress ? 'stress' : 'greeks');
                } else {
                    derivativesChart.innerHTML = `<div class="h-full flex items-center justify-center text-sm text-gray-400 italic text-center px-8">Add an option through Options Overlay to activate Delta, Gamma and Vega risk.</div>`;
                    showRiskDetail(customRiskStress ? 'stress' : 'attribution');
                }'''
if old not in s:
    raise SystemExit('Default risk detail marker not found')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')

required = [
    'id="risk-tab-stress"',
    'id="stress-chart"',
    'id="modal-risk-stress"',
    'custom_stress: customRiskStress',
    'data.stress_testing',
    'full revaluation',
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit(f'Missing Phase 3 frontend markers: {missing}')

print('Phase 3 frontend stress testing applied.')
