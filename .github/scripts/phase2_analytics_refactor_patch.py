from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

old_section = r'''            <!-- PORTFOLIO ANALYTICS -->
            <div id="analytics" class="section-intro"><h2>Analytics</h2><div class="section-overview"><strong>Return and risk together</strong>View returns alongside volatility, maximum drawdown and the Sharpe ratio to understand the path taken to achieve them.</div></div>
            <section class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-3 mb-4">
                    <div><p class="text-[10px] font-black uppercase tracking-widest text-indigo-600 mb-1">Analytics</p><h3 class="text-xl font-black">Performance in context</h3><p class="text-sm text-gray-500 mt-1">A restrained set of metrics — deeper optimisation and risk analytics belong in SethiQuant.</p></div>
                    <a href="sethiquant.html?portfolio=fundamental&source=sethiportfolio#section-var" class="text-xs font-black text-indigo-700 bg-indigo-50 border border-indigo-100 rounded-lg px-4 py-2 hover:bg-indigo-100 hover:border-indigo-200 transition" title="Load the live portfolio into SethiQuant's Market Risk Lab">Analyse Portfolio in SethiQuant →</a>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
                    <div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Total Return</p><p id="analytics-total-return" class="text-2xl font-black mt-1">—</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Annualised</p><p id="analytics-annualised" class="text-2xl font-black mt-1">—</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Volatility</p><p id="analytics-volatility" class="text-2xl font-black mt-1">—</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Max Drawdown</p><p id="analytics-drawdown" class="text-2xl font-black mt-1 text-red-600">—</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4 col-span-2 md:col-span-1"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Sharpe*</p><p id="analytics-sharpe" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">0% risk-free rate</p></div>
                </div>
            </section>
'''

new_section = r'''            <!-- RETURN EFFICIENCY ANALYTICS -->
            <div id="analytics" class="section-intro"><h2>Analytics</h2><div class="section-overview"><strong>Was the return efficient?</strong>Assess the quality of the daily return distribution rather than repeating headline performance, drawdown or concentration metrics already covered elsewhere.</div></div>
            <section class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-indigo-600 mb-1">Return Efficiency</p>
                        <h3 class="text-xl md:text-2xl font-black">How consistently was return earned?</h3>
                        <p id="analytics-context" class="text-sm text-gray-500 mt-1">Risk-adjusted and downside-aware statistics over Since Inception.</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2">
                        <div class="flex rounded-lg bg-gray-100 p-1 text-xs font-black">
                            <button data-range="1M" onclick="setRange('1M', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">1M</button>
                            <button data-range="3M" onclick="setRange('3M', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">3M</button>
                            <button data-range="YTD" onclick="setRange('YTD', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">YTD</button>
                            <button data-range="SI" onclick="setRange('SI', this)" class="range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Since Inception</button>
                        </div>
                        <a href="sethiquant.html?portfolio=fundamental&source=sethiportfolio-analytics#section-var" class="text-xs font-black text-indigo-700 bg-indigo-50 border border-indigo-100 rounded-lg px-4 py-2 hover:bg-indigo-100 hover:border-indigo-200 transition" title="Load the live portfolio into SethiQuant's Market Risk Lab">Open SethiQuant →</a>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
                    <div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Sharpe Ratio</p><p id="analytics-sharpe" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Return per unit total volatility</p></div>
                    <div class="rounded-xl bg-emerald-50/60 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">Sortino Ratio</p><p id="analytics-sortino" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-emerald-700/70 mt-1">Return per unit downside risk</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Downside Deviation</p><p id="analytics-downside" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Annualised downside variability</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Positive Days</p><p id="analytics-positive-days" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Share of daily observations &gt; 0</p></div>
                    <div class="rounded-xl bg-blue-50/60 border border-blue-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-blue-700">Gain / Loss Ratio</p><p id="analytics-gain-loss" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-blue-700/70 mt-1">Average gain ÷ average loss</p></div>
                    <div class="rounded-xl bg-violet-50/60 border border-violet-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-violet-700">Tail Ratio</p><p id="analytics-tail" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-violet-700/70 mt-1">95th percentile ÷ |5th percentile|</p></div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.35fr)] gap-3 mt-4">
                    <div class="rounded-xl bg-indigo-50/50 border border-indigo-100 px-4 py-3"><p class="text-[10px] uppercase tracking-widest font-black text-indigo-700 mb-1">Distribution Readout</p><p id="analytics-distribution" class="text-xs font-bold text-gray-700 leading-relaxed">Calculating daily return asymmetry…</p></div>
                    <div id="analytics-method" class="rounded-xl bg-gray-50 border border-gray-100 px-4 py-3 text-[11px] leading-relaxed text-gray-500"><strong class="text-gray-700">Method:</strong> Sharpe assumes a 0% risk-free rate; Sortino uses a 0% daily target. Downside deviation is annualised from negative daily deviations.</div>
                </div>
            </section>
'''

if old_section not in text:
    raise SystemExit('Old Analytics section not found')
text = text.replace(old_section, new_section, 1)

old_functions = r'''    function calculateAnalytics(values, dates) {
        if (!values.length) return null;
        const total = values.at(-1) - 100;
        const start = new Date(`${dates[0]}T00:00:00`), end = new Date(`${dates.at(-1)}T00:00:00`);
        const years = Math.max((end-start)/(365.25*24*3600*1000), 1/365.25);
        const annualised = (Math.pow(values.at(-1)/100, 1/years)-1)*100;
        const returns = values.slice(1).map((v,i) => v/values[i]-1).filter(Number.isFinite);
        const mean = returns.reduce((a,b)=>a+b,0)/(returns.length || 1);
        const variance = returns.length > 1 ? returns.reduce((sum,r)=>sum+(r-mean)**2,0)/(returns.length-1) : 0;
        const vol = Math.sqrt(variance)*Math.sqrt(252)*100;
        const sharpe = vol ? (mean*252)/(vol/100) : 0;
        let peak = values[0], maxDD = 0;
        values.forEach(v => { peak=Math.max(peak,v); maxDD=Math.min(maxDD,(v/peak-1)*100); });
        return {total, annualised, vol, sharpe, maxDD};
    }

    function renderAnalytics(performance) {
        const a = calculateAnalytics(performance.portfolio || [], performance.dates || []);
        if (!a) return;
        document.getElementById('analytics-total-return').textContent = fmtPct(a.total);
        document.getElementById('analytics-annualised').textContent = fmtPct(a.annualised);
        document.getElementById('analytics-volatility').textContent = `${a.vol.toFixed(2)}%`;
        document.getElementById('analytics-drawdown').textContent = `${a.maxDD.toFixed(2)}%`;
        document.getElementById('analytics-sharpe').textContent = a.sharpe.toFixed(2);
    }
'''

new_functions = r'''    function analyticsQuantile(values, q) {
        if (!values.length) return null;
        const sorted = [...values].sort((a,b) => a-b);
        const position = (sorted.length - 1) * q;
        const lower = Math.floor(position), upper = Math.ceil(position);
        if (lower === upper) return sorted[lower];
        const weight = position - lower;
        return sorted[lower] * (1 - weight) + sorted[upper] * weight;
    }

    function calculateAnalytics(values) {
        if (!Array.isArray(values) || values.length < 3) return null;
        const returns = [];
        for (let i = 1; i < values.length; i++) {
            const previous = Number(values[i - 1]);
            const current = Number(values[i]);
            if (Number.isFinite(previous) && previous > 0 && Number.isFinite(current) && current > 0) {
                returns.push(current / previous - 1);
            }
        }
        if (returns.length < 2) return null;

        const mean = returns.reduce((sum, value) => sum + value, 0) / returns.length;
        const variance = returns.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (returns.length - 1);
        const annualVol = Math.sqrt(Math.max(0, variance)) * Math.sqrt(252);
        const annualReturnArithmetic = mean * 252;
        const sharpe = annualVol > 1e-12 ? annualReturnArithmetic / annualVol : null;

        const downsideSquares = returns.map(value => Math.min(value, 0) ** 2);
        const downsideDeviation = Math.sqrt(downsideSquares.reduce((sum, value) => sum + value, 0) / downsideSquares.length) * Math.sqrt(252);
        const sortino = downsideDeviation > 1e-12 ? annualReturnArithmetic / downsideDeviation : null;

        const positive = returns.filter(value => value > 0);
        const negative = returns.filter(value => value < 0);
        const positiveDays = positive.length / returns.length * 100;
        const avgGain = positive.length ? positive.reduce((sum, value) => sum + value, 0) / positive.length : null;
        const avgLoss = negative.length ? negative.reduce((sum, value) => sum + value, 0) / negative.length : null;
        const gainLoss = avgGain != null && avgLoss != null && Math.abs(avgLoss) > 1e-12 ? avgGain / Math.abs(avgLoss) : null;
        const q95 = analyticsQuantile(returns, 0.95);
        const q05 = analyticsQuantile(returns, 0.05);
        const tailRatio = q95 != null && q05 != null && Math.abs(q05) > 1e-12 ? q95 / Math.abs(q05) : null;

        return {returns, mean, annualVol, sharpe, downsideDeviation, sortino, positiveDays, avgGain, avgLoss, gainLoss, q95, q05, tailRatio};
    }

    function renderAnalytics() {
        const start = rangeStartIndex(currentRange);
        const values = (portfolioData.portfolio || []).slice(start);
        const dates = (portfolioData.dates || []).slice(start);
        const a = calculateAnalytics(values);
        const ids = ['analytics-sharpe','analytics-sortino','analytics-downside','analytics-positive-days','analytics-gain-loss','analytics-tail'];
        if (!a) {
            ids.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = '—'; });
            document.getElementById('analytics-context').textContent = 'Insufficient daily observations for the selected period.';
            document.getElementById('analytics-distribution').textContent = 'Return-distribution diagnostics are unavailable for this period.';
            return;
        }

        const periodLabel = currentRange === 'SI' ? 'Since Inception' : currentRange;
        document.getElementById('analytics-context').textContent = `${a.returns.length} daily observations · risk-adjusted and downside-aware statistics over ${periodLabel}.`;

        const ratioClass = value => value == null ? 'text-gray-900' : value >= 1 ? 'text-emerald-600' : value < 0 ? 'text-red-600' : 'text-gray-900';
        const sharpeEl = document.getElementById('analytics-sharpe');
        sharpeEl.textContent = a.sharpe == null ? '—' : a.sharpe.toFixed(2);
        sharpeEl.className = `text-2xl font-black mt-1 ${a.sharpe == null ? 'text-white' : a.sharpe >= 1 ? 'text-emerald-400' : a.sharpe < 0 ? 'text-red-400' : 'text-white'}`;

        const sortinoEl = document.getElementById('analytics-sortino');
        sortinoEl.textContent = a.sortino == null ? '—' : a.sortino.toFixed(2);
        sortinoEl.className = `text-2xl font-black mt-1 ${ratioClass(a.sortino)}`;
        document.getElementById('analytics-downside').textContent = `${(a.downsideDeviation * 100).toFixed(2)}%`;

        const positiveEl = document.getElementById('analytics-positive-days');
        positiveEl.textContent = `${a.positiveDays.toFixed(1)}%`;
        positiveEl.className = `text-2xl font-black mt-1 ${a.positiveDays >= 50 ? 'text-emerald-600' : 'text-red-600'}`;

        const gainLossEl = document.getElementById('analytics-gain-loss');
        gainLossEl.textContent = a.gainLoss == null ? '—' : `${a.gainLoss.toFixed(2)}x`;
        gainLossEl.className = `text-2xl font-black mt-1 ${ratioClass(a.gainLoss)}`;

        const tailEl = document.getElementById('analytics-tail');
        tailEl.textContent = a.tailRatio == null ? '—' : `${a.tailRatio.toFixed(2)}x`;
        tailEl.className = `text-2xl font-black mt-1 ${ratioClass(a.tailRatio)}`;

        const avgGain = a.avgGain == null ? '—' : `+${(a.avgGain * 100).toFixed(2)}%`;
        const avgLoss = a.avgLoss == null ? '—' : `${(a.avgLoss * 100).toFixed(2)}%`;
        const upperTail = a.q95 == null ? '—' : `+${(a.q95 * 100).toFixed(2)}%`;
        const lowerTail = a.q05 == null ? '—' : `${(a.q05 * 100).toFixed(2)}%`;
        document.getElementById('analytics-distribution').textContent = `Average up day ${avgGain} versus average down day ${avgLoss}. The 95th / 5th percentile daily returns are ${upperTail} / ${lowerTail}.`;
        document.getElementById('analytics-method').innerHTML = `<strong class="text-gray-700">Method:</strong> Sharpe assumes a 0% risk-free rate; Sortino uses a 0% daily target. Downside deviation annualises negative daily deviations by √252. Gain/loss ratio compares average positive and negative days; tail ratio compares the 95th percentile with the absolute 5th percentile. Window: ${dates.length ? `${prettyDate(dates[0])} → ${prettyDate(dates.at(-1))}` : periodLabel}.`;
    }
'''

if old_functions not in text:
    raise SystemExit('Old Analytics functions not found')
text = text.replace(old_functions, new_functions, 1)

old_range = "        renderBenchmarkAnalytics();\n        renderDrawdownRolling();\n    }"
new_range = "        renderBenchmarkAnalytics();\n        renderDrawdownRolling();\n        renderAnalytics();\n    }"
if old_range not in text:
    raise SystemExit('setRange anchor not found')
text = text.replace(old_range, new_range, 1)

old_load = "            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics(performance);"
new_load = "            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics();"
if old_load not in text:
    raise SystemExit('loadPortfolio Analytics call not found')
text = text.replace(old_load, new_load, 1)

path.write_text(text)
