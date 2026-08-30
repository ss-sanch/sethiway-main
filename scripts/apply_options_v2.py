from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')

# 1. Add educational insights panel beneath the existing four-column options engine.
marker = '''            </div>\n        </section>\n\n        <!-- MARKOWITZ OPTIMISER (INSTITUTIONAL 4-COLUMN LAYOUT) -->'''
section = '''            </div>\n\n            <div id="options-insights" class="hidden max-w-[1600px] w-full mx-auto px-4 -mt-10 mb-16">\n                <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 md:p-6">\n                    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 mb-5">\n                        <div>\n                            <p class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Position Interpretation</p>\n                            <h3 class="text-xl font-black text-gray-900">What does this option actually mean?</h3>\n                            <p id="op-insight-summary" class="text-sm text-gray-500 mt-1 max-w-4xl">Run a calculation to translate the option price into break-even, payoff and risk intuition.</p>\n                        </div>\n                        <button type="button" onclick="toggleModal('modal-options-payoff')" class="shrink-0 px-4 py-2 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 text-xs font-black hover:bg-blue-100 transition">How to read this</button>\n                    </div>\n\n                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Break-even at expiry</p><p id="op-break-even" class="text-xl font-black text-gray-900 mt-1">--</p><p class="text-[10px] text-gray-400 mt-1">Underlying price needed to recover premium.</p></div>\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Intrinsic value</p><p id="op-intrinsic" class="text-xl font-black text-gray-900 mt-1">--</p><p class="text-[10px] text-gray-400 mt-1">Value from exercising immediately.</p></div>\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Time value</p><p id="op-time-value" class="text-xl font-black text-gray-900 mt-1">--</p><p class="text-[10px] text-gray-400 mt-1">Premium paid for remaining uncertainty.</p></div>\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Moneyness</p><p id="op-moneyness" class="text-xl font-black text-gray-900 mt-1">--</p><p id="op-moneyness-note" class="text-[10px] text-gray-400 mt-1">Relationship between spot and strike.</p></div>\n                    </div>\n\n                    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,2fr)_minmax(300px,1fr)] gap-4">\n                        <div class="rounded-xl border border-gray-200 p-3 min-w-0">\n                            <div class="flex items-center justify-between px-2 pt-1"><div><h4 class="font-black text-sm text-gray-900">Expiry Payoff &amp; Profit/Loss</h4><p class="text-xs text-gray-500">Profit after subtracting the theoretical premium paid today.</p></div><span id="op-payoff-type" class="text-[10px] font-black uppercase tracking-wider bg-gray-100 text-gray-500 rounded-full px-3 py-1">--</span></div>\n                            <div id="op-payoff-chart" style="height:320px"></div>\n                        </div>\n                        <div class="rounded-xl border border-blue-100 bg-blue-50/40 p-5">\n                            <p class="text-[10px] font-black uppercase tracking-widest text-blue-700 mb-2">What to take away</p>\n                            <div id="op-learning-points" class="space-y-3 text-sm text-gray-700 leading-relaxed">\n                                <p>Run an option calculation to generate a plain-English interpretation.</p>\n                            </div>\n                            <div id="op-greek-translation" class="hidden mt-5 pt-4 border-t border-blue-100">\n                                <p class="text-[10px] font-black uppercase tracking-widest text-indigo-700 mb-2">Greek translation</p>\n                                <div class="space-y-2 text-xs text-gray-600">\n                                    <p id="op-delta-translation"></p>\n                                    <p id="op-vega-translation"></p>\n                                    <p id="op-theta-translation"></p>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n            </div>\n        </section>\n\n        <!-- MARKOWITZ OPTIMISER (INSTITUTIONAL 4-COLUMN LAYOUT) -->'''
if marker not in s:
    raise SystemExit('Options section end marker not found')
s = s.replace(marker, section, 1)

# 2. Add payoff interpretation modal before the existing options architecture modal.
marker = '''    <!-- MODAL: UNIFIED OPTIONS ENGINE MASTER -->'''
modal = '''    <!-- MODAL: OPTIONS PAYOFF GUIDE -->\n    <div id="modal-options-payoff" class="hidden fixed inset-0 z-[205] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">\n        <div class="bg-white rounded-2xl shadow-2xl p-6 md:p-8 max-w-2xl w-full relative max-h-[90vh] overflow-y-auto">\n            <button type="button" onclick="toggleModal('modal-options-payoff')" class="absolute top-4 right-4 text-gray-400 hover:text-red-500 text-xl font-bold">×</button>\n            <p class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Student Guide</p>\n            <h3 class="text-2xl font-black text-gray-900">From option price to economic meaning</h3>\n            <div class="space-y-4 mt-5 text-sm text-gray-600 leading-relaxed">\n                <div class="border-l-4 border-blue-500 pl-4"><h4 class="font-black text-gray-900">1. The premium is your starting cost</h4><p>The theoretical option value is treated as the premium paid today for one share of option exposure. The expiry P&amp;L chart subtracts this premium from the option's payoff at expiry.</p></div>\n                <div class="border-l-4 border-emerald-500 pl-4"><h4 class="font-black text-gray-900">2. Break-even is not the strike</h4><p>A call must finish above strike plus premium to break even. A put must finish below strike minus premium. Crossing the strike only creates intrinsic value; it does not automatically create a profit.</p></div>\n                <div class="border-l-4 border-indigo-500 pl-4"><h4 class="font-black text-gray-900">3. Intrinsic value versus time value</h4><p>Intrinsic value is what immediate exercise would produce. Any premium above intrinsic value is time value: the price of having remaining time for the underlying to move favourably.</p></div>\n                <div class="border-l-4 border-amber-500 pl-4"><h4 class="font-black text-gray-900">4. Moneyness describes where spot sits relative to strike</h4><p>In-the-money means the option already has intrinsic value; at-the-money means spot is close to strike; out-of-the-money means exercise would currently produce no value.</p></div>\n                <div class="border-l-4 border-slate-400 pl-4"><h4 class="font-black text-gray-900">5. Greeks describe today's sensitivity, not expiry payoff</h4><p>Delta, Gamma, Vega and Theta are local sensitivities of the option's current theoretical value. The payoff chart is different: it shows the contractual outcome at expiry after the premium is paid.</p></div>\n            </div>\n        </div>\n    </div>\n\n    <!-- MODAL: UNIFIED OPTIONS ENGINE MASTER -->'''
if marker not in s:
    raise SystemExit('Options master modal marker not found')
s = s.replace(marker, modal, 1)

# 3. Add a renderer before the unified options form submit handler.
marker = '''        document.getElementById('op-form').addEventListener('submit', async (e) => {'''
helper = r'''        function renderOptionInsights({ optionType, style, spot, strike, premium, greeks }) {
            const insights = document.getElementById('options-insights');
            insights.classList.remove('hidden');

            const intrinsic = optionType === 'call' ? Math.max(spot - strike, 0) : Math.max(strike - spot, 0);
            const timeValue = Math.max(premium - intrinsic, 0);
            const breakEven = optionType === 'call' ? strike + premium : Math.max(0, strike - premium);
            const distancePct = strike ? ((spot - strike) / strike) * 100 : 0;
            const nearATM = Math.abs(distancePct) <= 1.5;
            let moneyness;
            if (nearATM) moneyness = 'At the money';
            else if (optionType === 'call') moneyness = spot > strike ? 'In the money' : 'Out of the money';
            else moneyness = spot < strike ? 'In the money' : 'Out of the money';

            document.getElementById('op-break-even').innerText = `$${breakEven.toFixed(2)}`;
            document.getElementById('op-intrinsic').innerText = `$${intrinsic.toFixed(2)}`;
            document.getElementById('op-time-value').innerText = `$${timeValue.toFixed(2)}`;
            document.getElementById('op-moneyness').innerText = moneyness;
            document.getElementById('op-moneyness-note').innerText = `Spot is ${Math.abs(distancePct).toFixed(1)}% ${distancePct >= 0 ? 'above' : 'below'} strike.`;
            document.getElementById('op-payoff-type').innerText = `${style === 'american' ? 'American' : 'European'} ${optionType}`;

            const lower = Math.max(0.01, Math.min(spot, strike, breakEven) * 0.55);
            const upper = Math.max(spot, strike, breakEven) * 1.45;
            const xs = [];
            const payoff = [];
            const pnl = [];
            const points = 121;
            for (let i = 0; i < points; i++) {
                const terminal = lower + (upper - lower) * i / (points - 1);
                const value = optionType === 'call' ? Math.max(terminal - strike, 0) : Math.max(strike - terminal, 0);
                xs.push(terminal);
                payoff.push(value);
                pnl.push(value - premium);
            }

            Plotly.newPlot('op-payoff-chart', [
                { x: xs, y: payoff, name: 'Option payoff', type: 'scatter', mode: 'lines', line: { color: '#9ca3af', width: 2, dash: 'dot' }, hovertemplate: 'Expiry spot: $%{x:.2f}<br>Payoff: $%{y:.2f}<extra></extra>' },
                { x: xs, y: pnl, name: 'Profit / Loss', type: 'scatter', mode: 'lines', line: { color: '#2563eb', width: 3 }, fill: 'tozeroy', fillcolor: 'rgba(37,99,235,0.08)', hovertemplate: 'Expiry spot: $%{x:.2f}<br>P&L: $%{y:.2f}<extra></extra>' }
            ], {
                margin: { t: 20, r: 20, l: 55, b: 45 },
                xaxis: { title: 'Underlying price at expiry ($)', gridcolor: '#f3f4f6' },
                yaxis: { title: 'Value / P&L per share ($)', gridcolor: '#f3f4f6', zeroline: true, zerolinecolor: '#9ca3af' },
                shapes: [
                    { type: 'line', x0: strike, x1: strike, y0: 0, y1: 1, yref: 'paper', line: { color: '#ef4444', dash: 'dash', width: 1.5 } },
                    { type: 'line', x0: breakEven, x1: breakEven, y0: 0, y1: 1, yref: 'paper', line: { color: '#10b981', dash: 'dot', width: 1.5 } }
                ],
                annotations: [
                    { x: strike, y: 1, yref: 'paper', text: 'Strike', showarrow: false, yshift: 10, font: { size: 10, color: '#ef4444' } },
                    { x: breakEven, y: 1, yref: 'paper', text: 'Break-even', showarrow: false, yshift: -4, font: { size: 10, color: '#059669' } }
                ],
                legend: { orientation: 'h', y: 1.12, font: { size: 10 } },
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)'
            }, { displayModeBar: false, responsive: true });

            const direction = optionType === 'call' ? 'rise' : 'fall';
            const beyond = optionType === 'call' ? 'above' : 'below';
            const profitMove = optionType === 'call' ? ((breakEven / spot) - 1) * 100 : (1 - breakEven / spot) * 100;
            document.getElementById('op-insight-summary').innerText = `At today's theoretical premium of $${premium.toFixed(2)}, this ${optionType} breaks even at $${breakEven.toFixed(2)} at expiry.`;
            document.getElementById('op-learning-points').innerHTML = `
                <p><strong>Profit condition:</strong> the underlying needs to finish ${beyond} <strong>$${breakEven.toFixed(2)}</strong>. From today's spot, that is roughly a ${Math.abs(profitMove).toFixed(1)}% ${direction}.</p>
                <p><strong>Premium composition:</strong> $${intrinsic.toFixed(2)} is intrinsic value and $${timeValue.toFixed(2)} is time value. ${timeValue > intrinsic ? 'Most of the premium currently reflects remaining uncertainty rather than immediate exercise value.' : 'A meaningful share of the premium is already backed by intrinsic value.'}</p>
                <p><strong>Expiry shape:</strong> the maximum loss for a long option is the premium paid ($${premium.toFixed(2)} per share). ${optionType === 'call' ? 'Upside profit is theoretically uncapped.' : `Profit increases as the underlying falls, with the contractual floor at a $0 stock price.`}</p>`;

            const greekBox = document.getElementById('op-greek-translation');
            if (greeks) {
                greekBox.classList.remove('hidden');
                const onePctDelta = greeks.delta * spot * 0.01;
                document.getElementById('op-delta-translation').innerHTML = `<strong>Delta:</strong> a +1% move in the underlying implies roughly ${onePctDelta >= 0 ? '+' : ''}$${onePctDelta.toFixed(2)} of first-order option value change per share, before Gamma.`;
                document.getElementById('op-vega-translation').innerHTML = `<strong>Vega:</strong> a +1 volatility-point move changes theoretical value by roughly ${greeks.vega >= 0 ? '+' : ''}$${greeks.vega.toFixed(2)} per share.`;
                document.getElementById('op-theta-translation').innerHTML = `<strong>Theta:</strong> holding other inputs constant, one calendar day changes theoretical value by roughly ${greeks.theta >= 0 ? '+' : ''}$${greeks.theta.toFixed(2)} per share.`;
            } else {
                greekBox.classList.add('hidden');
            }

            setTimeout(() => Plotly.Plots.resize('op-payoff-chart'), 0);
        }

        document.getElementById('op-form').addEventListener('submit', async (e) => {'''
if marker not in s:
    raise SystemExit('Options submit marker not found')
s = s.replace(marker, helper, 1)

# 4. Capture premium/greeks after routing result and render insights before chart fetch.
marker = '''                // Map UI Outputs\n                if (style === 'american') {'''
replacement = '''                // Map UI Outputs\n                let calculatedPremium = 0;\n                let calculatedGreeks = null;\n                if (style === 'american') {'''
if marker not in s:
    raise SystemExit('Options output marker not found')
s = s.replace(marker, replacement, 1)

marker = '''                    document.getElementById('out-price').innerText = `$${data.results.american_price.toFixed(2)}`;'''
replacement = '''                    calculatedPremium = data.results.american_price;\n                    document.getElementById('out-price').innerText = `$${data.results.american_price.toFixed(2)}`;'''
s = s.replace(marker, replacement, 1)

marker = '''                    document.getElementById('out-price').innerText = `$${data.results.theoretical_price.toFixed(2)}`;'''
replacement = '''                    calculatedPremium = data.results.theoretical_price;\n                    calculatedGreeks = data.results.greeks;\n                    document.getElementById('out-price').innerText = `$${data.results.theoretical_price.toFixed(2)}`;'''
s = s.replace(marker, replacement, 1)

marker = '''                // 2. Execute Visualisation Engine (If Ticker Provided)'''
replacement = '''                renderOptionInsights({\n                    optionType: payload.option_type,\n                    style,\n                    spot: spotPrice,\n                    strike: strikePrice,\n                    premium: calculatedPremium,\n                    greeks: calculatedGreeks\n                });\n\n                // 2. Execute Visualisation Engine (If Ticker Provided)'''
if marker not in s:
    raise SystemExit('Options visualisation marker not found')
s = s.replace(marker, replacement, 1)

p.write_text(s, encoding='utf-8')

required = ['id="options-insights"', 'id="op-payoff-chart"', 'function renderOptionInsights', 'modal-options-payoff', 'renderOptionInsights({']
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit(f'Missing Options V2 markers: {missing}')
print('Options Valuation 2.0 frontend applied.')
