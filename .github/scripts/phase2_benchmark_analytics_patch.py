from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #attribution, #holdings, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #benchmark, #holdings, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin'
    ),
    (
        '                <a href="#attribution" class="hover:text-blue-600">Attribution</a>\n                <a href="#holdings" class="hover:text-blue-600">Holdings</a>',
        '                <a href="#attribution" class="hover:text-blue-600">Attribution</a>\n                <a href="#benchmark" class="hover:text-blue-600">Benchmark</a>\n                <a href="#holdings" class="hover:text-blue-600">Holdings</a>',
        'navigation'
    ),
    (
        "    let currentRange = 'SI';\n    const activeSeries = {portfolio:true, sp500:true, nasdaq:true, vwrl:true};",
        "    let currentRange = 'SI';\n    let currentBenchmark = 'sp500';\n    const activeSeries = {portfolio:true, sp500:true, nasdaq:true, vwrl:true};",
        'benchmark state'
    ),
    (
        '        renderPerformance();\n        renderAttribution();\n    }',
        '        renderPerformance();\n        renderAttribution();\n        renderBenchmarkAnalytics();\n    }',
        'range synchronisation'
    ),
    (
        '            renderPerformance(); renderAttribution(); renderHoldings(snapshot); renderAnalytics(performance);',
        '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderHoldings(snapshot); renderAnalytics(performance);',
        'initial render'
    ),
]

for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    text = text.replace(old, new, 1)

section = r'''
            <!-- BENCHMARK ANALYTICS -->
            <div id="benchmark" class="section-intro"><h2>Benchmark Analytics</h2><div class="section-overview"><strong>Was active risk rewarded?</strong>Measure the portfolio against a chosen benchmark using excess return, regression sensitivity, tracking error and market capture. Period controls stay aligned with Performance and Attribution.</div></div>
            <section class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-violet-600 mb-1">Relative Performance</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">Did active decisions beat the alternative?</h3>
                        <p id="benchmark-context" class="text-sm text-gray-500 mt-1">Comparing the portfolio with S&amp;P 500 Total Return.</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2 xl:justify-end">
                        <select id="benchmark-select" onchange="setBenchmark(this.value)" aria-label="Select benchmark for relative analytics" class="bg-white border border-gray-200 text-gray-800 text-xs font-black rounded-lg px-3 py-2 outline-none focus:border-violet-400">
                            <option value="sp500">S&amp;P 500 Total Return</option>
                            <option value="nasdaq">Nasdaq-100 (QQQ)</option>
                            <option value="vwrl">VWRL</option>
                        </select>
                        <div class="flex rounded-lg bg-gray-100 p-1 text-xs font-black">
                            <button data-range="1M" onclick="setRange('1M', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">1M</button>
                            <button data-range="3M" onclick="setRange('3M', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">3M</button>
                            <button data-range="YTD" onclick="setRange('YTD', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">YTD</button>
                            <button data-range="SI" onclick="setRange('SI', this)" class="range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm">Since Inception</button>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
                    <div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Excess Return</p><p id="benchmark-excess" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Portfolio minus benchmark</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Beta</p><p id="benchmark-beta" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Daily return sensitivity</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Regression Alpha</p><p id="benchmark-alpha" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Annualised intercept</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Tracking Error</p><p id="benchmark-tracking" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Annualised active volatility</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Information Ratio</p><p id="benchmark-ir" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Active return per unit risk</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Correlation</p><p id="benchmark-correlation" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Daily return correlation</p></div>
                    <div class="rounded-xl bg-emerald-50/50 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">Upside Capture</p><p id="benchmark-up-capture" class="text-2xl font-black mt-1 text-gray-900">—</p><p class="text-[9px] text-emerald-700/70 mt-1">Benchmark-positive days</p></div>
                    <div class="rounded-xl bg-red-50/50 border border-red-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-red-700">Downside Capture</p><p id="benchmark-down-capture" class="text-2xl font-black mt-1 text-gray-900">—</p><p class="text-[9px] text-red-700/70 mt-1">Benchmark-negative days</p></div>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-2 gap-5">
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Cumulative Excess Return</h4><p class="text-xs text-gray-500 mt-0.5">The percentage-point gap between portfolio and benchmark performance through the selected period.</p></div>
                        <div id="benchmark-active-chart" style="height:330px"></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Daily Return Sensitivity</h4><p id="benchmark-regression-note" class="text-xs text-gray-500 mt-0.5">Regression of portfolio returns on benchmark returns.</p></div>
                        <div id="benchmark-regression-chart" style="height:330px"></div>
                    </div>
                </div>
                <div class="mt-4 rounded-lg bg-violet-50/60 border border-violet-100 px-4 py-3 text-[11px] leading-relaxed text-violet-900"><strong>Method:</strong> beta and alpha use an OLS regression of aligned daily portfolio returns on benchmark returns. Alpha is the annualised regression intercept; tracking error and information ratio use daily active returns annualised over 252 trading days. Capture ratios compare average portfolio returns with average benchmark returns on benchmark-up and benchmark-down days.</div>
            </section>

'''

anchor = '            <!-- COMPOSITION + HOLDINGS -->'
if anchor not in text:
    raise SystemExit('Missing holdings anchor')
text = text.replace(anchor, section + anchor, 1)

functions = r'''
    function setBenchmark(key) {
        if (!['sp500','nasdaq','vwrl'].includes(key)) return;
        currentBenchmark = key;
        renderBenchmarkAnalytics();
    }

    function benchmarkWindow(key = currentBenchmark) {
        const portfolio = portfolioData.portfolio || [];
        const benchmark = portfolioData[key] || [];
        const dates = portfolioData.dates || [];
        const start = rangeStartIndex(currentRange);
        const limit = Math.min(portfolio.length, benchmark.length, dates.length);
        let first = -1, last = -1;
        for (let i = start; i < limit; i++) {
            const p = Number(portfolio[i]), b = Number(benchmark[i]);
            if (Number.isFinite(p) && p > 0 && Number.isFinite(b) && b > 0) {
                if (first < 0) first = i;
                last = i;
            }
        }
        if (first < 0 || last <= first) return null;

        const daily = [];
        for (let i = first + 1; i <= last; i++) {
            const p0 = Number(portfolio[i - 1]), p1 = Number(portfolio[i]);
            const b0 = Number(benchmark[i - 1]), b1 = Number(benchmark[i]);
            if (![p0,p1,b0,b1].every(v => Number.isFinite(v) && v > 0)) continue;
            daily.push({date:dates[i], portfolio:p1/p0 - 1, benchmark:b1/b0 - 1});
        }
        return {portfolio, benchmark, dates, first, last, daily};
    }

    function benchmarkStats(key = currentBenchmark) {
        const window = benchmarkWindow(key);
        if (!window || window.daily.length < 2) return null;
        const {portfolio, benchmark, first, last, daily} = window;
        const pReturn = portfolio[last] / portfolio[first] - 1;
        const bReturn = benchmark[last] / benchmark[first] - 1;
        const p = daily.map(row => row.portfolio);
        const b = daily.map(row => row.benchmark);
        const mean = values => values.reduce((sum, value) => sum + value, 0) / values.length;
        const meanP = mean(p), meanB = mean(b);
        const sampleCov = p.reduce((sum, value, i) => sum + (value - meanP) * (b[i] - meanB), 0) / (p.length - 1);
        const varB = b.reduce((sum, value) => sum + (value - meanB) ** 2, 0) / (b.length - 1);
        const varP = p.reduce((sum, value) => sum + (value - meanP) ** 2, 0) / (p.length - 1);
        const beta = varB > 0 ? sampleCov / varB : 0;
        const alphaDaily = meanP - beta * meanB;
        const alphaAnnual = alphaDaily * 252 * 100;
        const active = daily.map(row => row.portfolio - row.benchmark);
        const meanActive = mean(active);
        const activeVariance = active.reduce((sum, value) => sum + (value - meanActive) ** 2, 0) / (active.length - 1);
        const trackingError = Math.sqrt(Math.max(0, activeVariance)) * Math.sqrt(252) * 100;
        const informationRatio = trackingError > 0 ? (meanActive * 252) / (trackingError / 100) : 0;
        const correlation = varP > 0 && varB > 0 ? sampleCov / Math.sqrt(varP * varB) : 0;
        const up = daily.filter(row => row.benchmark > 0);
        const down = daily.filter(row => row.benchmark < 0);
        const capture = rows => {
            if (!rows.length) return null;
            const avgP = rows.reduce((sum, row) => sum + row.portfolio, 0) / rows.length;
            const avgB = rows.reduce((sum, row) => sum + row.benchmark, 0) / rows.length;
            return Math.abs(avgB) > 1e-12 ? avgP / avgB * 100 : null;
        };
        return {
            window, pReturn, bReturn, excess:(pReturn - bReturn) * 100,
            beta, alphaDaily, alphaAnnual, trackingError, informationRatio,
            correlation, upCapture:capture(up), downCapture:capture(down)
        };
    }

    function renderBenchmarkAnalytics() {
        const stats = benchmarkStats(currentBenchmark);
        const meta = seriesMeta[currentBenchmark] || {name:'Benchmark', color:'#7c3aed'};
        const context = document.getElementById('benchmark-context');
        if (context) context.textContent = `Comparing the portfolio with ${meta.name} over ${currentRange === 'SI' ? 'Since Inception' : currentRange}.`;

        const metricIds = ['benchmark-excess','benchmark-beta','benchmark-alpha','benchmark-tracking','benchmark-ir','benchmark-correlation','benchmark-up-capture','benchmark-down-capture'];
        if (!stats) {
            metricIds.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = '—'; });
            document.getElementById('benchmark-active-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Insufficient aligned benchmark history for this period.</div>';
            document.getElementById('benchmark-regression-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">At least two aligned return observations are required.</div>';
            document.getElementById('benchmark-regression-note').textContent = 'Regression unavailable for the selected period.';
            return;
        }

        const signClass = value => Number(value) >= 0 ? 'text-emerald-600' : 'text-red-600';
        const excessEl = document.getElementById('benchmark-excess');
        excessEl.textContent = fmtPp(stats.excess);
        excessEl.className = `text-2xl font-black mt-1 ${stats.excess >= 0 ? 'text-emerald-400' : 'text-red-400'}`;
        document.getElementById('benchmark-beta').textContent = stats.beta.toFixed(2);
        const alphaEl = document.getElementById('benchmark-alpha');
        alphaEl.textContent = fmtPct(stats.alphaAnnual);
        alphaEl.className = `text-2xl font-black mt-1 ${signClass(stats.alphaAnnual)}`;
        document.getElementById('benchmark-tracking').textContent = `${stats.trackingError.toFixed(2)}%`;
        const irEl = document.getElementById('benchmark-ir');
        irEl.textContent = stats.informationRatio.toFixed(2);
        irEl.className = `text-2xl font-black mt-1 ${signClass(stats.informationRatio)}`;
        document.getElementById('benchmark-correlation').textContent = stats.correlation.toFixed(2);
        document.getElementById('benchmark-up-capture').textContent = stats.upCapture == null ? '—' : `${stats.upCapture.toFixed(0)}%`;
        document.getElementById('benchmark-down-capture').textContent = stats.downCapture == null ? '—' : `${stats.downCapture.toFixed(0)}%`;

        const {window} = stats;
        const activeDates = [], activeSpread = [];
        const baseP = Number(window.portfolio[window.first]);
        const baseB = Number(window.benchmark[window.first]);
        for (let i = window.first; i <= window.last; i++) {
            const p = Number(window.portfolio[i]), b = Number(window.benchmark[i]);
            if (![p,b].every(v => Number.isFinite(v) && v > 0)) continue;
            activeDates.push(window.dates[i]);
            activeSpread.push(((p / baseP - 1) - (b / baseB - 1)) * 100);
        }
        Plotly.react('benchmark-active-chart', [{
            x:activeDates, y:activeSpread, type:'scatter', mode:'lines', fill:'tozeroy',
            line:{color:'#7c3aed', width:2.5}, fillcolor:'rgba(124,58,237,.08)',
            hovertemplate:'%{x}<br>Excess return: %{y:.2f}pp<extra></extra>'
        }], {
            margin:{t:12,r:18,l:52,b:42}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', showlegend:false,
            xaxis:{showgrid:false}, yaxis:{title:'Excess return (pp)', gridcolor:'#f3f4f6', zeroline:true, zerolinecolor:'#9ca3af'}, hovermode:'x'
        }, {displayModeBar:false, responsive:true});

        const x = window.daily.map(row => row.benchmark * 100);
        const y = window.daily.map(row => row.portfolio * 100);
        const minX = Math.min(...x), maxX = Math.max(...x);
        const lineX = minX === maxX ? [minX - .1, maxX + .1] : [minX, maxX];
        const lineY = lineX.map(value => (stats.alphaDaily + stats.beta * (value / 100)) * 100);
        Plotly.react('benchmark-regression-chart', [
            {
                x, y, text:window.daily.map(row => row.date), type:'scatter', mode:'markers', name:'Daily returns',
                marker:{color:meta.color, size:6, opacity:.55},
                hovertemplate:'%{text}<br>Benchmark: %{x:.2f}%<br>Portfolio: %{y:.2f}%<extra></extra>'
            },
            {
                x:lineX, y:lineY, type:'scatter', mode:'lines', name:'OLS fit',
                line:{color:'#111827', width:2}, hoverinfo:'skip'
            }
        ], {
            margin:{t:12,r:18,l:52,b:48}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', showlegend:false,
            xaxis:{title:'Benchmark daily return (%)', gridcolor:'#f3f4f6', zeroline:true, zerolinecolor:'#d1d5db'},
            yaxis:{title:'Portfolio daily return (%)', gridcolor:'#f3f4f6', zeroline:true, zerolinecolor:'#d1d5db'}
        }, {displayModeBar:false, responsive:true});
        document.getElementById('benchmark-regression-note').textContent = `${window.daily.length} aligned daily observations · R² ${(stats.correlation ** 2).toFixed(2)} · beta ${stats.beta.toFixed(2)}.`;
    }

'''

func_anchor = '    const collapsedLists = {'
if func_anchor not in text:
    raise SystemExit('Missing function insertion anchor')
text = text.replace(func_anchor, functions + func_anchor, 1)

catch_anchor = "            document.getElementById('attribution-table').innerHTML = '<tr><td colspan=\"4\" class=\"px-4 py-8 text-center text-gray-400\">Unable to load attribution.</td></tr>';"
if catch_anchor not in text:
    raise SystemExit('Missing error-state anchor')
text = text.replace(catch_anchor, catch_anchor + "\n            document.getElementById('benchmark-active-chart').innerHTML = '<div class=\"h-full flex items-center justify-center text-sm text-gray-400\">Unable to load benchmark analytics.</div>';\n            document.getElementById('benchmark-regression-chart').innerHTML = '<div class=\"h-full flex items-center justify-center text-sm text-gray-400\">Unable to load benchmark regression.</div>';", 1)

path.write_text(text)
