from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #attribution, #benchmark, #holdings, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin'
    ),
    (
        '                <a href="#benchmark" class="hover:text-blue-600">Benchmark</a>\n                <a href="#holdings" class="hover:text-blue-600">Holdings</a>',
        '                <a href="#benchmark" class="hover:text-blue-600">Benchmark</a>\n                <a href="#drawdown" class="hover:text-blue-600">Drawdown</a>\n                <a href="#holdings" class="hover:text-blue-600">Holdings</a>',
        'navigation'
    ),
    (
        "    let currentBenchmark = 'sp500';\n    const activeSeries = {portfolio:true, sp500:true, nasdaq:true, vwrl:true};",
        "    let currentBenchmark = 'sp500';\n    let currentRollingWindow = 63;\n    let currentRollingMetric = 'return';\n    const activeSeries = {portfolio:true, sp500:true, nasdaq:true, vwrl:true};",
        'rolling state'
    ),
    (
        '        renderPerformance();\n        renderAttribution();\n        renderBenchmarkAnalytics();\n    }',
        '        renderPerformance();\n        renderAttribution();\n        renderBenchmarkAnalytics();\n        renderDrawdownRolling();\n    }',
        'range synchronisation'
    ),
    (
        "    function setBenchmark(key) {\n        if (!['sp500','nasdaq','vwrl'].includes(key)) return;\n        currentBenchmark = key;\n        renderBenchmarkAnalytics();\n    }",
        "    function setBenchmark(key) {\n        if (!['sp500','nasdaq','vwrl'].includes(key)) return;\n        currentBenchmark = key;\n        ['benchmark-select','drawdown-benchmark-select'].forEach(id => {\n            const select = document.getElementById(id);\n            if (select && select.value !== key) select.value = key;\n        });\n        renderBenchmarkAnalytics();\n        renderDrawdownRolling();\n    }",
        'benchmark synchronisation'
    ),
    (
        '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderHoldings(snapshot); renderAnalytics(performance);',
        '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics(performance);',
        'initial render'
    ),
    (
        "            document.getElementById('benchmark-regression-chart').innerHTML = '<div class=\"h-full flex items-center justify-center text-sm text-gray-400\">Unable to load benchmark regression.</div>';\n            document.getElementById('holdings-table').innerHTML",
        "            document.getElementById('benchmark-regression-chart').innerHTML = '<div class=\"h-full flex items-center justify-center text-sm text-gray-400\">Unable to load benchmark regression.</div>';\n            document.getElementById('drawdown-chart').innerHTML = '<div class=\"h-full flex items-center justify-center text-sm text-gray-400\">Unable to load drawdown history.</div>';\n            document.getElementById('rolling-chart').innerHTML = '<div class=\"h-full flex items-center justify-center text-sm text-gray-400\">Unable to load rolling analytics.</div>';\n            document.getElementById('holdings-table').innerHTML",
        'error state'
    ),
]

for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    text = text.replace(old, new, 1)

section = r'''
            <!-- DRAWDOWN + ROLLING PERFORMANCE -->
            <div id="drawdown" class="section-intro"><h2>Drawdown &amp;<br>Rolling Performance</h2><div class="section-overview"><strong>How difficult was the path?</strong>Track losses from prior peaks, the time needed to recover, and how return and volatility evolved through rolling windows. Drawdown metrics use the selected period; rolling statistics retain the required lookback history.</div></div>
            <section class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-rose-600 mb-1">Path Risk</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">What happened between the starting point and the return?</h3>
                        <p id="drawdown-context" class="text-sm text-gray-500 mt-1">Drawdown and rolling behaviour versus S&amp;P 500 Total Return.</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2 xl:justify-end">
                        <select id="drawdown-benchmark-select" onchange="setBenchmark(this.value)" aria-label="Select benchmark for drawdown comparison" class="bg-white border border-gray-200 text-gray-800 text-xs font-black rounded-lg px-3 py-2 outline-none focus:border-rose-400">
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
                    <div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Current Drawdown</p><p id="drawdown-current" class="text-2xl font-black mt-1">—</p><p id="drawdown-current-note" class="text-[9px] text-gray-400 mt-1">From the latest high-water mark</p></div>
                    <div class="rounded-xl bg-red-50/50 border border-red-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-red-700">Maximum Drawdown</p><p id="drawdown-max" class="text-2xl font-black mt-1 text-red-600">—</p><p id="drawdown-max-note" class="text-[9px] text-red-700/70 mt-1">Worst peak-to-trough loss</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Longest Drawdown</p><p id="drawdown-longest" class="text-2xl font-black mt-1">—</p><p id="drawdown-longest-note" class="text-[9px] text-gray-400 mt-1">Peak until recovery or period end</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Max DD Recovery</p><p id="drawdown-recovery" class="text-2xl font-black mt-1">—</p><p id="drawdown-recovery-note" class="text-[9px] text-gray-400 mt-1">Trough back to previous peak</p></div>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-2 gap-5">
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Underwater Drawdown</h4><p class="text-xs text-gray-500 mt-0.5">Percentage loss from each series' previous high-water mark within the selected period.</p></div>
                        <div id="drawdown-chart" style="height:350px"></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1 flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3">
                            <div><h4 id="rolling-chart-title" class="font-black text-sm text-gray-900">3M Rolling Return</h4><p id="rolling-chart-note" class="text-xs text-gray-500 mt-0.5">Trailing return for the portfolio and selected benchmark.</p></div>
                            <div class="flex flex-wrap items-center gap-2 shrink-0">
                                <div class="flex rounded-lg bg-gray-100 p-1 text-[10px] font-black">
                                    <button type="button" data-rolling-metric="return" onclick="setRollingMetric('return')" class="rolling-metric-btn px-2.5 py-1.5 rounded-md bg-white text-rose-700 shadow-sm">Return</button>
                                    <button type="button" data-rolling-metric="volatility" onclick="setRollingMetric('volatility')" class="rolling-metric-btn px-2.5 py-1.5 rounded-md text-gray-500">Volatility</button>
                                </div>
                                <div class="flex rounded-lg bg-gray-100 p-1 text-[10px] font-black">
                                    <button type="button" data-rolling-window="21" onclick="setRollingWindow(21)" class="rolling-window-btn px-2.5 py-1.5 rounded-md text-gray-500">1M</button>
                                    <button type="button" data-rolling-window="63" onclick="setRollingWindow(63)" class="rolling-window-btn px-2.5 py-1.5 rounded-md bg-white text-rose-700 shadow-sm">3M</button>
                                    <button type="button" data-rolling-window="126" onclick="setRollingWindow(126)" class="rolling-window-btn px-2.5 py-1.5 rounded-md text-gray-500">6M</button>
                                </div>
                            </div>
                        </div>
                        <div id="rolling-chart" style="height:350px"></div>
                    </div>
                </div>
                <div class="mt-4 rounded-lg bg-rose-50/60 border border-rose-100 px-4 py-3 text-[11px] leading-relaxed text-rose-900"><strong>Method:</strong> drawdown is the percentage change from the running high-water mark. Drawdown duration is measured in calendar days from the prior peak to recovery, or to the latest observation if unrecovered. Rolling returns use 21, 63 or 126 trading-day lookbacks; rolling volatility is the sample standard deviation of daily returns annualised by √252.</div>
            </section>

'''

anchor = '            <!-- COMPOSITION + HOLDINGS -->'
if anchor not in text:
    raise SystemExit('Missing holdings anchor')
text = text.replace(anchor, section + anchor, 1)

functions = r'''
    function daysBetween(startDate, endDate) {
        const start = new Date(`${startDate}T00:00:00`);
        const end = new Date(`${endDate}T00:00:00`);
        return Math.max(0, Math.round((end - start) / 86400000));
    }

    function drawdownAnalysis(values, dates, startIndex = 0) {
        const points = [];
        const limit = Math.min(values.length, dates.length);
        for (let i = Math.max(0, startIndex); i < limit; i++) {
            const value = Number(values[i]);
            if (Number.isFinite(value) && value > 0) points.push({index:i, value, date:dates[i]});
        }
        if (!points.length) return null;

        let peakValue = points[0].value;
        let peakPoint = points[0];
        let activeEpisode = null;
        const episodes = [];
        const seriesDates = [];
        const drawdowns = [];
        let maxDrawdown = 0;
        let maxEpisode = null;

        points.forEach((point, pointIndex) => {
            if (point.value >= peakValue - 1e-12) {
                if (activeEpisode) {
                    activeEpisode.recovery = point;
                    activeEpisode.durationDays = daysBetween(activeEpisode.start.date, point.date);
                    activeEpisode.recoveryDays = daysBetween(activeEpisode.trough.date, point.date);
                    episodes.push(activeEpisode);
                    activeEpisode = null;
                }
                peakValue = point.value;
                peakPoint = point;
            }

            const drawdown = (point.value / peakValue - 1) * 100;
            seriesDates.push(point.date);
            drawdowns.push(drawdown);

            if (drawdown < -1e-9) {
                if (!activeEpisode) {
                    activeEpisode = {
                        start: peakPoint,
                        trough: point,
                        maxDrawdown: drawdown,
                        recovery: null,
                        durationDays: 0,
                        recoveryDays: null,
                    };
                }
                if (drawdown < activeEpisode.maxDrawdown) {
                    activeEpisode.maxDrawdown = drawdown;
                    activeEpisode.trough = point;
                }
                if (drawdown < maxDrawdown) maxDrawdown = drawdown;
            }

            if (pointIndex === points.length - 1 && activeEpisode) {
                activeEpisode.durationDays = daysBetween(activeEpisode.start.date, point.date);
                activeEpisode.recoveryDays = null;
                episodes.push(activeEpisode);
                activeEpisode = null;
            }
        });

        if (episodes.length) {
            maxEpisode = episodes.reduce((worst, episode) => !worst || episode.maxDrawdown < worst.maxDrawdown ? episode : worst, null);
        }
        const longestEpisode = episodes.reduce((longest, episode) => !longest || episode.durationDays > longest.durationDays ? episode : longest, null);
        const currentDrawdown = drawdowns.at(-1) || 0;
        const currentEpisode = currentDrawdown < -1e-9 ? episodes.at(-1) : null;
        return {
            dates: seriesDates,
            drawdowns,
            currentDrawdown,
            maxDrawdown,
            maxEpisode,
            longestEpisode,
            currentEpisode,
            latestDate: points.at(-1).date,
        };
    }

    function setRollingWindow(window) {
        const parsed = Number(window);
        if (![21,63,126].includes(parsed)) return;
        currentRollingWindow = parsed;
        document.querySelectorAll('.rolling-window-btn').forEach(button => {
            button.className = Number(button.dataset.rollingWindow) === parsed
                ? 'rolling-window-btn px-2.5 py-1.5 rounded-md bg-white text-rose-700 shadow-sm'
                : 'rolling-window-btn px-2.5 py-1.5 rounded-md text-gray-500';
        });
        renderRollingChart();
    }

    function setRollingMetric(metric) {
        if (!['return','volatility'].includes(metric)) return;
        currentRollingMetric = metric;
        document.querySelectorAll('.rolling-metric-btn').forEach(button => {
            button.className = button.dataset.rollingMetric === metric
                ? 'rolling-metric-btn px-2.5 py-1.5 rounded-md bg-white text-rose-700 shadow-sm'
                : 'rolling-metric-btn px-2.5 py-1.5 rounded-md text-gray-500';
        });
        renderRollingChart();
    }

    function rollingMetricSeries(values, window, metric) {
        const output = new Array(values.length).fill(null);
        if (metric === 'return') {
            for (let i = window; i < values.length; i++) {
                const start = Number(values[i - window]);
                const end = Number(values[i]);
                if (Number.isFinite(start) && start > 0 && Number.isFinite(end) && end > 0) {
                    output[i] = (end / start - 1) * 100;
                }
            }
            return output;
        }

        const dailyReturns = new Array(values.length).fill(null);
        for (let i = 1; i < values.length; i++) {
            const previous = Number(values[i - 1]);
            const current = Number(values[i]);
            if (Number.isFinite(previous) && previous > 0 && Number.isFinite(current) && current > 0) {
                dailyReturns[i] = current / previous - 1;
            }
        }
        for (let i = window; i < values.length; i++) {
            const sample = dailyReturns.slice(i - window + 1, i + 1).filter(Number.isFinite);
            if (sample.length < window) continue;
            const mean = sample.reduce((sum, value) => sum + value, 0) / sample.length;
            const variance = sample.length > 1
                ? sample.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (sample.length - 1)
                : 0;
            output[i] = Math.sqrt(Math.max(0, variance)) * Math.sqrt(252) * 100;
        }
        return output;
    }

    function renderRollingChart() {
        const chart = document.getElementById('rolling-chart');
        if (!chart) return;
        const dates = portfolioData.dates || [];
        const portfolio = portfolioData.portfolio || [];
        const benchmark = portfolioData[currentBenchmark] || [];
        const displayStart = rangeStartIndex(currentRange);
        const portfolioRolling = rollingMetricSeries(portfolio, currentRollingWindow, currentRollingMetric);
        const benchmarkRolling = rollingMetricSeries(benchmark, currentRollingWindow, currentRollingMetric);
        const labels = {21:'1M',63:'3M',126:'6M'};
        const windowLabel = labels[currentRollingWindow] || `${currentRollingWindow}D`;
        const metricLabel = currentRollingMetric === 'return' ? 'Rolling Return' : 'Rolling Volatility';
        document.getElementById('rolling-chart-title').textContent = `${windowLabel} ${metricLabel}`;
        document.getElementById('rolling-chart-note').textContent = currentRollingMetric === 'return'
            ? `Trailing ${windowLabel} return for the portfolio and selected benchmark.`
            : `Annualised volatility of daily returns over a trailing ${windowLabel} window.`;

        const traces = [
            {key:'portfolio', values:portfolioRolling, meta:seriesMeta.portfolio},
            {key:'benchmark', values:benchmarkRolling, meta:seriesMeta[currentBenchmark]},
        ].map(item => ({
            x: dates.slice(displayStart),
            y: item.values.slice(displayStart),
            name: item.meta.name,
            type:'scatter', mode:'lines', connectgaps:false,
            line:{color:item.meta.color, width:item.key === 'portfolio' ? 3 : 2, dash:item.key === 'portfolio' ? 'solid' : item.meta.dash},
            hovertemplate:`%{x}<br>${metricLabel}: %{y:.2f}%<extra>${item.meta.name}</extra>`
        }));
        const hasData = traces.some(trace => trace.y.some(Number.isFinite));
        if (!hasData) {
            chart.innerHTML = `<div class="h-full flex items-center justify-center text-center px-6 text-sm text-gray-400">Not enough history for a ${windowLabel} ${metricLabel.toLowerCase()} in the selected period.</div>`;
            return;
        }
        Plotly.react('rolling-chart', traces, {
            margin:{t:16,r:20,l:55,b:42}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
            showlegend:true, legend:{orientation:'h',x:0,y:1.12,font:{size:10}},
            xaxis:{showgrid:false}, yaxis:{title:currentRollingMetric === 'return' ? 'Rolling return (%)' : 'Annualised volatility (%)', gridcolor:'#f3f4f6', zeroline:currentRollingMetric === 'return', zerolinecolor:'#d1d5db'},
            hovermode:'x unified'
        }, {displayModeBar:false, responsive:true});
    }

    function renderDrawdownRolling() {
        const chart = document.getElementById('drawdown-chart');
        if (!chart) return;
        const start = rangeStartIndex(currentRange);
        const portfolioAnalysis = drawdownAnalysis(portfolioData.portfolio || [], portfolioData.dates || [], start);
        const benchmarkAnalysis = drawdownAnalysis(portfolioData[currentBenchmark] || [], portfolioData.dates || [], start);
        const meta = seriesMeta[currentBenchmark] || {name:'Benchmark', color:'#7c3aed', dash:'dash'};
        const context = document.getElementById('drawdown-context');
        if (context) context.textContent = `Drawdown and rolling behaviour versus ${meta.name} over ${currentRange === 'SI' ? 'Since Inception' : currentRange}.`;

        if (!portfolioAnalysis) {
            ['drawdown-current','drawdown-max','drawdown-longest','drawdown-recovery'].forEach(id => {
                const el = document.getElementById(id); if (el) el.textContent = '—';
            });
            chart.innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Drawdown history is unavailable for this period.</div>';
            renderRollingChart();
            return;
        }

        const fmtDD = value => `${Number(value || 0).toFixed(2)}%`;
        const currentEl = document.getElementById('drawdown-current');
        currentEl.textContent = fmtDD(portfolioAnalysis.currentDrawdown);
        currentEl.className = `text-2xl font-black mt-1 ${portfolioAnalysis.currentDrawdown < -0.005 ? 'text-red-400' : 'text-emerald-400'}`;
        document.getElementById('drawdown-current-note').textContent = portfolioAnalysis.currentEpisode
            ? `Below peak from ${prettyDate(portfolioAnalysis.currentEpisode.start.date)}`
            : 'At the selected-period high-water mark';

        document.getElementById('drawdown-max').textContent = fmtDD(portfolioAnalysis.maxDrawdown);
        document.getElementById('drawdown-max-note').textContent = portfolioAnalysis.maxEpisode
            ? `${prettyDate(portfolioAnalysis.maxEpisode.start.date)} → ${prettyDate(portfolioAnalysis.maxEpisode.trough.date)}`
            : 'No drawdown in the selected period';

        const longest = portfolioAnalysis.longestEpisode;
        document.getElementById('drawdown-longest').textContent = longest ? `${longest.durationDays} days` : '0 days';
        document.getElementById('drawdown-longest-note').textContent = longest
            ? (longest.recovery ? `Recovered ${prettyDate(longest.recovery.date)}` : `Still underwater at ${prettyDate(portfolioAnalysis.latestDate)}`)
            : 'No underwater episode';

        const maxEpisode = portfolioAnalysis.maxEpisode;
        if (!maxEpisode) {
            document.getElementById('drawdown-recovery').textContent = '0 days';
            document.getElementById('drawdown-recovery-note').textContent = 'No recovery required';
        } else if (maxEpisode.recovery) {
            document.getElementById('drawdown-recovery').textContent = `${maxEpisode.recoveryDays} days`;
            document.getElementById('drawdown-recovery-note').textContent = `${prettyDate(maxEpisode.trough.date)} → ${prettyDate(maxEpisode.recovery.date)}`;
        } else {
            const sinceTrough = daysBetween(maxEpisode.trough.date, portfolioAnalysis.latestDate);
            document.getElementById('drawdown-recovery').textContent = 'Unrecovered';
            document.getElementById('drawdown-recovery-note').textContent = `${sinceTrough} days since trough`;
        }

        const traces = [{
            x:portfolioAnalysis.dates,
            y:portfolioAnalysis.drawdowns,
            name:'Sethi Fundamental', type:'scatter', mode:'lines', fill:'tozeroy',
            line:{color:'#ef4444', width:2.5}, fillcolor:'rgba(239,68,68,.10)',
            hovertemplate:'%{x}<br>Drawdown: %{y:.2f}%<extra>Sethi Fundamental</extra>'
        }];
        if (benchmarkAnalysis) {
            traces.push({
                x:benchmarkAnalysis.dates,
                y:benchmarkAnalysis.drawdowns,
                name:meta.name, type:'scatter', mode:'lines',
                line:{color:meta.color, width:2, dash:meta.dash || 'dash'},
                hovertemplate:`%{x}<br>Drawdown: %{y:.2f}%<extra>${meta.name}</extra>`
            });
        }
        Plotly.react('drawdown-chart', traces, {
            margin:{t:16,r:20,l:55,b:42}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
            showlegend:true, legend:{orientation:'h',x:0,y:1.12,font:{size:10}},
            xaxis:{showgrid:false}, yaxis:{title:'Drawdown (%)', gridcolor:'#f3f4f6', zeroline:true, zerolinecolor:'#9ca3af'},
            hovermode:'x unified'
        }, {displayModeBar:false, responsive:true});

        renderRollingChart();
    }

'''

anchor = '    const collapsedLists = {'
if anchor not in text:
    raise SystemExit('Missing JavaScript insertion anchor')
text = text.replace(anchor, functions + anchor, 1)

path.write_text(text)
