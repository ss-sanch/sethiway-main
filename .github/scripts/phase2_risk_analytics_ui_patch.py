from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #risk, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin'
    ),
    (
        '                <a href="#holdings" class="hover:text-blue-600">Holdings</a>\n                <a href="#analytics" class="hover:text-blue-600">Analytics</a>',
        '                <a href="#holdings" class="hover:text-blue-600">Holdings</a>\n                <a href="#risk" class="hover:text-blue-600">Risk</a>\n                <a href="#analytics" class="hover:text-blue-600">Analytics</a>',
        'navigation'
    ),
    (
        "    let attributionData = { periods: {} };\n    let journalEntries = [];",
        "    let attributionData = { periods: {} };\n    let riskAnalyticsData = null;\n    let journalEntries = [];",
        'risk state'
    ),
    (
        '    loadPortfolio();\n</script>',
        '    loadPortfolio();\n    loadRiskAnalytics();\n</script>',
        'risk async load'
    ),
]

for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    text = text.replace(old, new, 1)

section = r'''
            <!-- PORTFOLIO RISK ANALYTICS -->
            <div id="risk" class="section-intro"><h2>Portfolio Risk</h2><div class="section-overview"><strong>Where the risk actually sits</strong>Separate capital allocation from risk allocation. Compare each holding's invested weight with its Euler VaR contribution, measure concentration and diversification, and inspect how positions move together.</div></div>
            <section id="risk-analytics-card" class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-cyan-700 mb-1">Risk Map</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">Is capital concentration the same as risk concentration?</h3>
                        <p id="risk-status" class="text-sm text-gray-500 mt-1">Calculating the live invested-book risk map…</p>
                    </div>
                    <a href="sethiquant.html?portfolio=fundamental&source=sethiportfolio-risk#section-var" class="text-xs font-black text-cyan-800 bg-cyan-50 border border-cyan-100 rounded-lg px-4 py-2.5 hover:bg-cyan-100 hover:border-cyan-200 transition shrink-0" title="Open the live portfolio in SethiQuant's Market Risk Lab">Open full Market Risk Lab →</a>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-5">
                    <div class="rounded-xl bg-gray-900 text-white p-4 col-span-2 md:col-span-1"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Top Risk Contributor</p><p id="risk-top-name" class="text-xl font-black mt-1">—</p><p id="risk-top-value" class="text-[10px] text-gray-400 mt-1">Euler VaR share vs invested weight</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Top 5 Concentration</p><p id="risk-top5" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Share of invested capital</p></div>
                    <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Effective Holdings</p><p id="risk-effective" class="text-2xl font-black mt-1">—</p><p id="risk-effective-note" class="text-[9px] text-gray-400 mt-1">Inverse-HHI concentration</p></div>
                    <div class="rounded-xl bg-emerald-50/60 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">Diversification Benefit</p><p id="risk-diversification" class="text-2xl font-black mt-1 text-gray-900">—</p><p class="text-[9px] text-emerald-700/70 mt-1">VaR reduction vs standalone sum</p></div>
                    <div class="rounded-xl bg-violet-50/60 border border-violet-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-violet-700">Avg Correlation</p><p id="risk-avg-correlation" class="text-2xl font-black mt-1 text-gray-900">—</p><p class="text-[9px] text-violet-700/70 mt-1">Capital-weighted pairwise</p></div>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.2fr)] gap-5 items-start">
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Risk Contribution vs Capital Weight</h4><p id="risk-contribution-note" class="text-xs text-gray-500 mt-0.5">Euler VaR contribution compared with each holding's share of invested capital.</p></div>
                        <div id="risk-contribution-chart" style="height:390px"></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0 overflow-hidden">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Correlation Matrix</h4><p id="risk-correlation-note" class="text-xs text-gray-500 mt-0.5">Aligned daily local-price return correlations across the invested book.</p></div>
                        <div id="risk-correlation-chart" style="height:390px"></div>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-3 mt-5">
                    <div class="rounded-xl bg-amber-50/60 border border-amber-100 px-4 py-3"><p class="text-[10px] uppercase tracking-widest font-black text-amber-700 mb-1">Concentration</p><p id="risk-concentration-insight" class="text-xs font-bold text-gray-700 leading-relaxed">Calculating capital concentration…</p></div>
                    <div class="rounded-xl bg-blue-50/60 border border-blue-100 px-4 py-3"><p class="text-[10px] uppercase tracking-widest font-black text-blue-700 mb-1">Risk vs Weight</p><p id="risk-gap-insight" class="text-xs font-bold text-gray-700 leading-relaxed">Comparing risk allocation with capital allocation…</p></div>
                    <div class="rounded-xl bg-violet-50/60 border border-violet-100 px-4 py-3"><p class="text-[10px] uppercase tracking-widest font-black text-violet-700 mb-1">Co-movement</p><p id="risk-correlation-insight" class="text-xs font-bold text-gray-700 leading-relaxed">Calculating pairwise correlation structure…</p></div>
                </div>

                <div id="risk-method" class="mt-4 rounded-lg bg-cyan-50/50 border border-cyan-100 px-4 py-3 text-[11px] leading-relaxed text-cyan-900"><strong>Method:</strong> waiting for the live risk summary. Cash is excluded from invested-book risk calculations.</div>
            </section>

'''

anchor = '            <!-- PORTFOLIO ANALYTICS -->'
if anchor not in text:
    raise SystemExit('Portfolio analytics section anchor not found')
text = text.replace(anchor, section + anchor, 1)

functions = r'''
    function riskPercent(value, digits=1) {
        const number = Number(value);
        return Number.isFinite(number) ? `${number.toFixed(digits)}%` : '—';
    }

    function renderRiskAnalytics(data) {
        riskAnalyticsData = data;
        const concentration = data?.concentration || {};
        const attribution = data?.attribution || {};
        const components = Array.isArray(attribution.components) ? [...attribution.components] : [];
        const params = data?.parameters || {};
        const portfolio = data?.portfolio || {};
        const topRisk = concentration.top_risk_contributor || components[0];

        document.getElementById('risk-status').textContent = `${portfolio.holding_count || components.length} invested holdings · ${params.observations || '—'} aligned daily observations · ${(Number(params.confidence || 0.99) * 100).toFixed(0)}% / ${params.horizon_days || 10}-day Euler VaR`;
        document.getElementById('risk-top-name').textContent = topRisk?.ticker || '—';
        document.getElementById('risk-top-value').textContent = topRisk
            ? `${riskPercent(topRisk.contribution_pct)} of risk · ${riskPercent(topRisk.invested_weight_pct)} invested weight`
            : 'Euler VaR share vs invested weight';
        document.getElementById('risk-top5').textContent = riskPercent(concentration.top_5_invested_weight_pct);
        document.getElementById('risk-effective').textContent = Number(concentration.effective_holdings || 0).toFixed(1);
        document.getElementById('risk-effective-note').textContent = `${portfolio.holding_count || components.length} actual invested holdings`;
        document.getElementById('risk-diversification').textContent = riskPercent(attribution.diversification_pct);
        document.getElementById('risk-avg-correlation').textContent = Number(concentration.weighted_average_correlation || 0).toFixed(2);

        const contributionChart = document.getElementById('risk-contribution-chart');
        if (!components.length) {
            contributionChart.innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Risk contribution is unavailable.</div>';
        } else {
            let shown = [...components].sort((a,b) => Math.abs(Number(b.contribution_pct || 0)) - Math.abs(Number(a.contribution_pct || 0)));
            const truncated = shown.length > 15;
            shown = shown.slice(0, 15);
            document.getElementById('risk-contribution-note').textContent = truncated
                ? `Largest 15 risk contributors shown from ${components.length} holdings; all holdings remain included in the risk calculation.`
                : 'Euler VaR contribution compared with each holding\'s share of invested capital.';
            Plotly.react('risk-contribution-chart', [
                {
                    x:shown.map(row => Number(row.contribution_pct || 0)),
                    y:shown.map(row => row.ticker),
                    name:'Risk contribution', type:'bar', orientation:'h',
                    marker:{color:'#f59e0b'},
                    hovertemplate:'<b>%{y}</b><br>Euler VaR contribution: %{x:.2f}%<extra></extra>'
                },
                {
                    x:shown.map(row => Number(row.invested_weight_pct || 0)),
                    y:shown.map(row => row.ticker),
                    name:'Invested weight', type:'bar', orientation:'h',
                    marker:{color:'#2563eb'},
                    hovertemplate:'<b>%{y}</b><br>Invested weight: %{x:.2f}%<extra></extra>'
                }
            ], {
                barmode:'group', margin:{t:28,r:20,l:72,b:45},
                paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
                legend:{orientation:'h',x:0,y:1.12,font:{size:10}},
                xaxis:{title:'Share (%)',gridcolor:'#f3f4f6',zeroline:true,zerolinecolor:'#9ca3af'},
                yaxis:{automargin:true,autorange:'reversed'},
            }, {displayModeBar:false,responsive:true});
        }

        const allTickers = Array.isArray(data?.correlation?.tickers) ? data.correlation.tickers : [];
        const matrix = data?.correlation?.matrix || {};
        const weightByTicker = new Map(components.map(row => [row.ticker, Number(row.invested_weight_pct || 0)]));
        let matrixTickers = [...allTickers];
        if (matrixTickers.length > 18) {
            matrixTickers.sort((a,b) => (weightByTicker.get(b) || 0) - (weightByTicker.get(a) || 0));
            matrixTickers = matrixTickers.slice(0, 18);
            document.getElementById('risk-correlation-note').textContent = `Largest 18 of ${allTickers.length} holdings shown by invested weight; correlation diagnostics still use the full book.`;
        } else {
            document.getElementById('risk-correlation-note').textContent = `Aligned daily local-price return correlations across all ${matrixTickers.length} invested holdings.`;
        }

        if (matrixTickers.length < 2) {
            document.getElementById('risk-correlation-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Correlation data is unavailable.</div>';
        } else {
            const z = matrixTickers.map(row => matrixTickers.map(col => Number(matrix?.[row]?.[col] ?? 0)));
            const showValues = matrixTickers.length <= 12;
            Plotly.react('risk-correlation-chart', [{
                z, x:matrixTickers, y:matrixTickers, type:'heatmap', zmin:-1, zmax:1, zmid:0,
                colorscale:[[0,'#2563eb'],[0.5,'#f8fafc'],[1,'#ef4444']],
                colorbar:{title:'Corr',thickness:12,len:.8},
                text:showValues ? z.map(row => row.map(value => value.toFixed(2))) : undefined,
                texttemplate:showValues ? '%{text}' : undefined,
                textfont:{size:9},
                hovertemplate:'%{y} / %{x}<br>Correlation: %{z:.2f}<extra></extra>'
            }], {
                margin:{t:18,r:35,l:72,b:70}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
                xaxis:{tickangle:-45,side:'bottom',tickfont:{size:9}}, yaxis:{autorange:'reversed',tickfont:{size:9}},
            }, {displayModeBar:false,responsive:true});
        }

        const effective = Number(concentration.effective_holdings || 0);
        const actual = Number(portfolio.holding_count || components.length || 0);
        document.getElementById('risk-concentration-insight').textContent = `The largest five positions represent ${riskPercent(concentration.top_5_invested_weight_pct)} of invested capital. Inverse-HHI concentration is equivalent to about ${effective.toFixed(1)} equally weighted holdings versus ${actual} actual holdings.`;

        const gap = concentration.largest_risk_weight_gap;
        if (gap) {
            const gapValue = Number(gap.risk_minus_weight_pp || 0);
            document.getElementById('risk-gap-insight').textContent = `${gap.ticker} has the largest risk/weight mismatch: ${riskPercent(gap.contribution_pct)} of Euler VaR against ${riskPercent(gap.invested_weight_pct)} of invested capital (${gapValue >= 0 ? '+' : ''}${gapValue.toFixed(1)}pp).`;
        } else {
            document.getElementById('risk-gap-insight').textContent = 'Risk and capital weights are not available for comparison.';
        }

        const high = concentration.highest_correlation_pair;
        const low = concentration.lowest_correlation_pair;
        const pairText = high ? `Highest pair: ${high.left}/${high.right} ${Number(high.correlation).toFixed(2)}.` : '';
        const lowText = low ? ` Lowest pair: ${low.left}/${low.right} ${Number(low.correlation).toFixed(2)}.` : '';
        document.getElementById('risk-correlation-insight').textContent = `Capital-weighted average pairwise correlation is ${Number(concentration.weighted_average_correlation || 0).toFixed(2)}. ${pairText}${lowText}`.trim();

        document.getElementById('risk-method').innerHTML = `<strong>Method:</strong> ${data.methodology || 'Variance-covariance Euler VaR attribution.'} Parameters: ${(Number(params.confidence || 0.99) * 100).toFixed(0)}% confidence, ${params.horizon_days || 10}-day horizon, ${params.lookback || '2y'} lookback.`;
    }

    async function loadRiskAnalytics() {
        try {
            const response = await fetch(`${API_BASE}/${PORTFOLIO_SLUG}/risk-analytics`);
            if (!response.ok) {
                let detail = `Risk analytics request failed (${response.status})`;
                try { const body = await response.json(); detail = body.detail || detail; } catch (_) {}
                throw new Error(detail);
            }
            const data = await response.json();
            renderRiskAnalytics(data);
        } catch (error) {
            console.error('SethiPortfolio risk analytics failed:', error);
            document.getElementById('risk-status').textContent = 'Live risk analytics are temporarily unavailable; the rest of SethiPortfolio is unaffected.';
            document.getElementById('risk-contribution-chart').innerHTML = '<div class="h-full flex items-center justify-center text-center px-6 text-sm text-gray-400">Unable to calculate the live risk-contribution map.</div>';
            document.getElementById('risk-correlation-chart').innerHTML = '<div class="h-full flex items-center justify-center text-center px-6 text-sm text-gray-400">Unable to calculate the live correlation matrix.</div>';
            document.getElementById('risk-method').innerHTML = `<strong>Risk API:</strong> ${error.message || 'temporarily unavailable'}`;
        }
    }

'''

function_anchor = '    function calculateAnalytics(values, dates) {'
if function_anchor not in text:
    raise SystemExit('Analytics function anchor not found')
text = text.replace(function_anchor, functions + function_anchor, 1)

path.write_text(text)
