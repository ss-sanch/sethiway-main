from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')

# 1. Keep the new attribution chart aligned with the Phase 1 wide-screen sizing.
old_css = '''            #market-risk-lab #model-chart,
            #market-risk-lab #pnl-chart,
            #market-risk-lab #corr-chart { height: 393px !important; }'''
new_css = '''            #market-risk-lab #model-chart,
            #market-risk-lab #pnl-chart,
            #market-risk-lab #corr-chart,
            #market-risk-lab #risk-contribution-chart { height: 393px !important; }'''
if old_css not in s:
    raise SystemExit('MRL chart-height CSS marker not found')
s = s.replace(old_css, new_css, 1)

# 2. Replace the correlation-only third analytics card with a zero-extra-scroll toggle card.
old_card = '''                        <div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm min-w-0 lg:col-span-2 2xl:col-span-1"><div class="flex items-center justify-between border-b border-gray-100 pb-2 mb-2"><div><h3 class="font-black text-lg text-gray-900">Asset Correlation Matrix</h3><p class="text-xs text-gray-500">Dependence structure for the Monte Carlo engine.</p></div><span id="obs-badge" class="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">--</span></div><div id="corr-chart" style="height:255px"></div></div>'''
new_card = '''                        <div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm min-w-0 lg:col-span-2 2xl:col-span-1">
                            <div class="flex items-center justify-between gap-3 border-b border-gray-100 pb-2 mb-2">
                                <div class="min-w-0">
                                    <h3 id="risk-detail-title" class="font-black text-lg text-gray-900">Risk Contribution</h3>
                                    <p id="risk-detail-subtitle" class="text-xs text-gray-500 truncate">Run an analysis to decompose portfolio VaR.</p>
                                </div>
                                <div class="flex shrink-0 rounded-lg bg-gray-100 p-1 text-[10px] font-black uppercase tracking-wide">
                                    <button id="risk-tab-attribution" type="button" onclick="showRiskDetail('attribution')" class="px-2.5 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Contribution</button>
                                    <button id="risk-tab-correlation" type="button" onclick="showRiskDetail('correlation')" class="px-2.5 py-1.5 rounded-md text-gray-500">Correlation</button>
                                </div>
                            </div>
                            <div id="risk-attribution-view"><div id="risk-contribution-chart" style="height:255px"></div></div>
                            <div id="correlation-view" class="hidden"><div id="corr-chart" style="height:255px"></div></div>
                        </div>'''
if old_card not in s:
    raise SystemExit('Correlation card marker not found')
s = s.replace(old_card, new_card, 1)

# 3. Add state + toggle/render helpers before the Market Risk Lab engine.
engine_marker = '''        // ==========================================\n        // MARKET RISK LAB V2 ENGINE\n        // ==========================================\n        let activePositions = [ ["AAPL", 30], ["NVDA", 25], ["JPM", 25], ["GLD", 20] ];'''
engine_replacement = '''        // ==========================================\n        // MARKET RISK LAB V2 ENGINE\n        // ==========================================\n        let latestRiskData = null;\n\n        function renderCorrelationDetail(data) {\n            if (!data || !data.diagnostics || !data.diagnostics.correlation_matrix) return;\n            const matrix = data.diagnostics.correlation_matrix;\n            const tickers = Object.keys(matrix);\n            const z = tickers.map(r => tickers.map(c => matrix[r][c]));\n            Plotly.newPlot('corr-chart', [{\n                z, x: tickers, y: tickers, type: 'heatmap', colorscale: 'RdBu', zmin: -1, zmax: 1,\n                hovertemplate: '%{y} / %{x}: %{z:.3f}<extra></extra>'\n            }], {\n                margin: { t: 10, r: 20, l: 55, b: 45 },\n                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)'\n            }, { displayModeBar: false, responsive: true });\n        }\n\n        function showRiskDetail(view) {\n            const attributionView = document.getElementById('risk-attribution-view');\n            const correlationView = document.getElementById('correlation-view');\n            const attributionTab = document.getElementById('risk-tab-attribution');\n            const correlationTab = document.getElementById('risk-tab-correlation');\n            const title = document.getElementById('risk-detail-title');\n            const subtitle = document.getElementById('risk-detail-subtitle');\n\n            const activeClasses = ['bg-white', 'text-blue-700', 'shadow-sm'];\n            const inactiveClasses = ['text-gray-500'];\n\n            if (view === 'correlation') {\n                attributionView.classList.add('hidden');\n                correlationView.classList.remove('hidden');\n                activeClasses.forEach(c => correlationTab.classList.add(c));\n                inactiveClasses.forEach(c => correlationTab.classList.remove(c));\n                activeClasses.forEach(c => attributionTab.classList.remove(c));\n                inactiveClasses.forEach(c => attributionTab.classList.add(c));\n                title.innerText = 'Asset Correlation Matrix';\n                const obs = latestRiskData?.diagnostics?.historical_observations;\n                subtitle.innerText = obs ? `${obs} observations · dependence structure for the Monte Carlo engine.` : 'Dependence structure for the Monte Carlo engine.';\n                renderCorrelationDetail(latestRiskData);\n            } else {\n                correlationView.classList.add('hidden');\n                attributionView.classList.remove('hidden');\n                activeClasses.forEach(c => attributionTab.classList.add(c));\n                inactiveClasses.forEach(c => attributionTab.classList.remove(c));\n                activeClasses.forEach(c => correlationTab.classList.remove(c));\n                inactiveClasses.forEach(c => correlationTab.classList.add(c));\n                title.innerText = 'Risk Contribution';\n                const a = latestRiskData?.attribution;\n                subtitle.innerText = a\n                    ? `Parametric VaR ${formatMoney(a.portfolio_var)} · diversification ${a.diversification_pct.toFixed(1)}%`\n                    : 'Run an analysis to decompose portfolio VaR.';\n                if (document.getElementById('risk-contribution-chart').data) Plotly.Plots.resize('risk-contribution-chart');\n            }\n        }\n\n        let activePositions = [ ["AAPL", 30], ["NVDA", 25], ["JPM", 25], ["GLD", 20] ];'''
if engine_marker not in s:
    raise SystemExit('MRL engine marker not found')
s = s.replace(engine_marker, engine_replacement, 1)

# 4. Remove the old observations-badge write, which no longer exists.
s = s.replace("                document.getElementById('obs-badge').innerText = `${data.diagnostics.historical_observations} observations`;\n", '', 1)

# 5. Replace correlation-only rendering with the attribution renderer and default view selection.
old_render = '''                const matrix = data.diagnostics.correlation_matrix;\n                const tickers = Object.keys(matrix);\n                const z = tickers.map(r => tickers.map(c => matrix[r][c]));\n                Plotly.newPlot('corr-chart', [{ z, x: tickers, y: tickers, type: 'heatmap', colorscale: 'RdBu', zmin: -1, zmax: 1 }], { margin: { t: 10, r: 20, l: 55, b: 45 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)' }, { displayModeBar: false, responsive: true });'''
new_render = '''                latestRiskData = data;\n                const attribution = data.attribution;\n                if (!attribution || !Array.isArray(attribution.components)) {\n                    throw new Error('Risk attribution data was not returned by the engine.');\n                }\n\n                const components = attribution.components;\n                const contributionColors = components.map(c => c.component_var < 0 ? '#10b981' : '#2563eb');\n                Plotly.newPlot('risk-contribution-chart', [{\n                    x: components.map(c => c.component_var),\n                    y: components.map(c => c.ticker),\n                    type: 'bar',\n                    orientation: 'h',\n                    marker: { color: contributionColors },\n                    text: components.map(c => `${c.contribution_pct.toFixed(1)}%`),\n                    textposition: 'auto',\n                    customdata: components.map(c => [c.standalone_var, c.marginal_var_per_1000, c.weight_pct]),\n                    hovertemplate: '<b>%{y}</b><br>Component VaR: £%{x:,.0f}<br>Contribution: %{text}<br>Standalone VaR: £%{customdata[0]:,.0f}<br>Marginal VaR / £1k: £%{customdata[1]:,.2f}<br>Portfolio weight: %{customdata[2]:.1f}%<extra></extra>'\n                }], {\n                    margin: { t: 10, r: 20, l: 55, b: 45 },\n                    xaxis: { title: 'Component VaR (£)', gridcolor: '#f3f4f6', zeroline: true, zerolinecolor: '#d1d5db' },\n                    yaxis: { autorange: 'reversed' },\n                    paper_bgcolor: 'rgba(0,0,0,0)',\n                    plot_bgcolor: 'rgba(0,0,0,0)',\n                    showlegend: false\n                }, { displayModeBar: false, responsive: true });\n\n                showRiskDetail('attribution');'''
if old_render not in s:
    raise SystemExit('Old correlation render block not found')
s = s.replace(old_render, new_render, 1)

p.write_text(s, encoding='utf-8')

required = [
    'id="risk-contribution-chart"',
    "function showRiskDetail(view)",
    'Marginal VaR / £1k',
    'data.attribution',
    '#market-risk-lab #risk-contribution-chart { height: 393px !important; }',
]
missing = [m for m in required if m not in s]
if missing:
    raise SystemExit(f'Missing Phase 2A markers: {missing}')

print('Phase 2A risk-attribution frontend applied.')
