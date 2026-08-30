from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')

# Phase 3.1: educational UX and interpretation layer.
# Trigger marker: v2
# 1. Add info buttons to Model Comparison and MC P&L Distribution.
s = s.replace(
'''<div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm min-w-0"><div class="flex items-center justify-between border-b border-gray-100 pb-2 mb-2"><div><h3 class="font-black text-lg text-gray-900">Model Comparison</h3><p class="text-xs text-gray-500">Same portfolio, different risk assumptions.</p></div><span id="model-gap" class="text-xs font-bold bg-gray-100 rounded-full px-3 py-1 text-gray-600">--</span></div><div id="model-chart" style="height:255px"></div></div>''',
'''<div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm min-w-0"><div class="flex items-center justify-between border-b border-gray-100 pb-2 mb-2"><div><h3 class="font-black text-lg text-gray-900">Model Comparison</h3><p class="text-xs text-gray-500">Same portfolio, different risk assumptions.</p></div><div class="flex items-center gap-2"><span id="model-gap" class="text-xs font-bold bg-gray-100 rounded-full px-3 py-1 text-gray-600">--</span><button type="button" onclick="toggleModal('modal-risk-lab-guide')" class="text-gray-400 hover:text-blue-600 transition" title="How to interpret this chart">ⓘ</button></div></div><div id="model-chart" style="height:255px"></div></div>''',
1)

s = s.replace(
'''<div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm min-w-0"><div class="border-b border-gray-100 pb-2 mb-2"><h3 class="font-black text-lg text-gray-900">MC P&amp;L Distribution</h3><p class="text-xs text-gray-500">Losses beyond the VaR threshold form the tail.</p></div><div id="pnl-chart" style="height:255px"></div></div>''',
'''<div class="bg-white border border-gray-200 rounded-xl p-4 shadow-sm min-w-0"><div class="flex items-start justify-between gap-3 border-b border-gray-100 pb-2 mb-2"><div><h3 class="font-black text-lg text-gray-900">MC P&amp;L Distribution</h3><p class="text-xs text-gray-500">Losses beyond the VaR threshold form the tail.</p></div><button type="button" onclick="toggleModal('modal-risk-lab-guide')" class="text-gray-400 hover:text-blue-600 transition mt-1" title="How to interpret this chart">ⓘ</button></div><div id="pnl-chart" style="height:255px"></div></div>''',
1)

# 2. Rework right analytics header so the subtitle gets its own full-width row and add info button.
old = '''                            <div class="flex items-center justify-between gap-3 border-b border-gray-100 pb-2 mb-2">
                                <div class="min-w-0">
                                    <h3 id="risk-detail-title" class="font-black text-lg text-gray-900">Risk Contribution</h3>
                                    <p id="risk-detail-subtitle" class="text-xs text-gray-500 truncate">Run an analysis to decompose portfolio VaR.</p>
                                </div>
                                <div class="flex shrink-0 rounded-lg bg-gray-100 p-1 text-[10px] font-black uppercase tracking-wide">
                                    <button id="risk-tab-attribution" type="button" onclick="showRiskDetail('attribution')" class="px-2 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Contrib</button>
                                    <button id="risk-tab-greeks" type="button" onclick="showRiskDetail('greeks')" class="px-2 py-1.5 rounded-md text-gray-500">Greeks</button>
                                    <button id="risk-tab-stress" type="button" onclick="showRiskDetail('stress')" class="px-2 py-1.5 rounded-md text-gray-500">Stress</button>
                                    <button id="risk-tab-correlation" type="button" onclick="showRiskDetail('correlation')" class="px-2 py-1.5 rounded-md text-gray-500">Corr</button>
                                </div>
                            </div>'''
new = '''                            <div class="border-b border-gray-100 pb-2 mb-2">
                                <div class="flex items-center justify-between gap-3">
                                    <div class="flex items-center gap-2 min-w-0">
                                        <h3 id="risk-detail-title" class="font-black text-lg text-gray-900">Risk Contribution</h3>
                                        <button type="button" onclick="toggleModal('modal-risk-lab-guide')" class="text-gray-400 hover:text-blue-600 transition shrink-0" title="Learn how to interpret Market Risk Lab">ⓘ</button>
                                    </div>
                                    <div class="flex shrink-0 rounded-lg bg-gray-100 p-1 text-[10px] font-black uppercase tracking-wide">
                                        <button id="risk-tab-attribution" type="button" onclick="showRiskDetail('attribution')" class="px-2 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Contrib</button>
                                        <button id="risk-tab-greeks" type="button" onclick="showRiskDetail('greeks')" class="px-2 py-1.5 rounded-md text-gray-500">Greeks</button>
                                        <button id="risk-tab-stress" type="button" onclick="showRiskDetail('stress')" class="px-2 py-1.5 rounded-md text-gray-500">Stress</button>
                                        <button id="risk-tab-correlation" type="button" onclick="showRiskDetail('correlation')" class="px-2 py-1.5 rounded-md text-gray-500">Corr</button>
                                    </div>
                                </div>
                                <p id="risk-detail-subtitle" class="text-xs text-gray-500 mt-1.5 leading-relaxed whitespace-normal">Run an analysis to decompose portfolio VaR.</p>
                            </div>'''
if old not in s:
    raise SystemExit('risk detail header marker not found')
s = s.replace(old, new, 1)

# 3. Add an educational interpretation section below the main dashboard, before closing the MRL section.
marker = '''            </div>
        </section>

        <!-- QUANTITATIVE LEGAL DISCLAIMER -->'''
guide = '''            </div>

            <div class="max-w-[1800px] mx-auto mt-4 bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Interpretation Guide</p>
                        <h3 class="text-xl font-black text-gray-900">How to read the Market Risk Lab</h3>
                        <p class="text-sm text-gray-500 mt-1 max-w-3xl">The models answer different questions. Read them together rather than treating any single number as a complete measure of risk.</p>
                    </div>
                    <button type="button" onclick="toggleModal('modal-risk-lab-guide')" class="shrink-0 px-4 py-2 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 text-xs font-black hover:bg-blue-100 transition">Open step-by-step guide</button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><h4 class="font-black text-sm text-gray-900 mb-1">1. VaR &amp; Expected Shortfall</h4><p class="text-xs text-gray-600 leading-relaxed">VaR is the loss threshold at the chosen confidence level. Expected Shortfall asks how severe losses are on average once that threshold is breached.</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><h4 class="font-black text-sm text-gray-900 mb-1">2. Risk Contribution</h4><p class="text-xs text-gray-600 leading-relaxed">Component VaR shows which holdings are driving portfolio risk after correlations are considered. A large weight does not always mean a large risk contribution.</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><h4 class="font-black text-sm text-gray-900 mb-1">3. Greeks</h4><p class="text-xs text-gray-600 leading-relaxed">Delta measures directional option exposure, Gamma measures curvature and Vega measures sensitivity to volatility. These explain how derivatives reshape the portfolio's P&amp;L.</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><h4 class="font-black text-sm text-gray-900 mb-1">4. Stress Testing</h4><p class="text-xs text-gray-600 leading-relaxed">Stress tests ask “what if markets move sharply?” They are scenario analyses, not forecasts. Compare the equity, options and total P&amp;L to see where protection or extra downside comes from.</p></div>
                </div>
            </div>
        </section>

        <!-- QUANTITATIVE LEGAL DISCLAIMER -->'''
if marker not in s:
    raise SystemExit('MRL section close marker not found')
s = s.replace(marker, guide, 1)

# 4. Add detailed modal before the existing risk metrics modal.
marker = '''    <!-- MODAL: RISK METRICS -->'''
modal = '''    <!-- MODAL: MARKET RISK LAB EDUCATION GUIDE -->
    <div id="modal-risk-lab-guide" class="hidden fixed inset-0 z-[230] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl p-6 md:p-8 max-w-3xl w-full relative max-h-[90vh] overflow-y-auto">
            <button type="button" onclick="toggleModal('modal-risk-lab-guide')" class="absolute top-4 right-4 text-gray-400 hover:text-red-500 text-xl font-bold">×</button>
            <div class="pr-10 mb-6">
                <p class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Student Guide</p>
                <h3 class="text-2xl font-black text-gray-900">Understanding the Market Risk Lab</h3>
                <p class="text-sm text-gray-500 mt-2 leading-relaxed">This lab combines several risk models because each one answers a different question. The aim is not to find one “correct” risk number, but to understand how assumptions, correlations and nonlinear positions change the loss profile.</p>
            </div>
            <div class="space-y-5 text-sm text-gray-600 leading-relaxed">
                <div class="border-l-4 border-blue-500 pl-4"><h4 class="font-black text-gray-900 mb-1">Step 1 — Start with VaR and Expected Shortfall</h4><p><strong>Historical VaR</strong> replays realised market moves from the selected lookback. <strong>Monte Carlo VaR</strong> creates new correlated scenarios from estimated return behaviour. At 99% confidence, VaR marks the loss level exceeded by roughly the worst 1% of scenarios. Expected Shortfall then averages those tail losses.</p><p class="mt-2 text-xs text-gray-500"><strong>Takeaway:</strong> compare the two models. A meaningful gap tells you the estimated tail risk is sensitive to modelling assumptions.</p></div>
                <div class="border-l-4 border-indigo-500 pl-4"><h4 class="font-black text-gray-900 mb-1">Step 2 — Ask what is causing the risk</h4><p>The <strong>Contribution</strong> view uses a parametric Euler decomposition. Component VaR allocates total equity-book VaR across holdings after accounting for covariance. Marginal VaR estimates how much portfolio VaR changes for an additional unit of exposure.</p><p class="mt-2 text-xs text-gray-500"><strong>Takeaway:</strong> focus on concentration of risk, not just concentration of capital. Correlation can make a smaller holding a larger risk contributor.</p></div>
                <div class="border-l-4 border-violet-500 pl-4"><h4 class="font-black text-gray-900 mb-1">Step 3 — If options are present, inspect the Greeks</h4><p><strong>Delta</strong> captures first-order exposure to the underlying price. <strong>Gamma</strong> captures curvature, meaning Delta itself changes as the underlying moves. <strong>Vega</strong> measures sensitivity to a one volatility-point change. The chart expresses each sensitivity as an approximate £ P&amp;L impact.</p><p class="mt-2 text-xs text-gray-500"><strong>Takeaway:</strong> options can hedge directional risk while adding convexity or volatility exposure, so their risk cannot be understood from Delta alone.</p></div>
                <div class="border-l-4 border-amber-500 pl-4"><h4 class="font-black text-gray-900 mb-1">Step 4 — Use stress tests for large moves</h4><p>Stress testing deliberately asks what happens outside normal model conditions. Equity positions are marked directly to the scenario shock, while European options are <strong>fully repriced with Black–Scholes</strong> at the stressed spot and volatility rather than extrapolating local Greeks across a large move.</p><p class="mt-2 text-xs text-gray-500"><strong>Takeaway:</strong> the worst scenario is not a forecast. It is a vulnerability check: where would the portfolio lose money, and do the options cushion or amplify that loss?</p></div>
                <div class="border-l-4 border-slate-400 pl-4"><h4 class="font-black text-gray-900 mb-1">Step 5 — Check correlation</h4><p>The correlation matrix shows how the assets have historically moved together. High positive correlation reduces diversification; low or negative correlation can offset risk. Correlations are estimates and can change sharply during stressed markets.</p><p class="mt-2 text-xs text-gray-500"><strong>Takeaway:</strong> diversification is a property of relationships between positions, not simply the number of positions held.</p></div>
            </div>
        </div>
    </div>

    <!-- MODAL: RISK METRICS -->'''
if marker not in s:
    raise SystemExit('risk metrics modal marker not found')
s = s.replace(marker, modal, 1)

p.write_text(s, encoding='utf-8')

required = [
    "modal-risk-lab-guide",
    "How to read the Market Risk Lab",
    "Open step-by-step guide",
    "whitespace-normal",
    "Step 4 — Use stress tests for large moves",
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit(f'Missing education UX markers: {missing}')
print('MRL education UX applied.')
