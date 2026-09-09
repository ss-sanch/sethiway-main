from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #exposure, #risk, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #exposure, #fx, #risk, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin'
    ),
    (
        '                <a href="#exposure" class="hover:text-blue-600">Exposure</a>\n                <a href="#risk" class="hover:text-blue-600">Risk</a>',
        '                <a href="#exposure" class="hover:text-blue-600">Exposure</a>\n                <a href="#fx" class="hover:text-blue-600">FX</a>\n                <a href="#risk" class="hover:text-blue-600">Risk</a>',
        'navigation'
    ),
    (
        '    let exposureData = null;\n    let riskAnalyticsData = null;',
        '    let exposureData = null;\n    let fxAnalyticsData = null;\n    let riskAnalyticsData = null;',
        'state'
    ),
    (
        '        renderDrawdownRolling();\n        renderAnalytics();',
        '        renderDrawdownRolling();\n        renderAnalytics();\n        renderFxHistory();',
        'range render'
    ),
    (
        '    loadPortfolio();\n    loadExposureMap();\n    loadRiskAnalytics();',
        '    loadPortfolio();\n    loadExposureMap();\n    loadFxAnalytics();\n    loadRiskAnalytics();',
        'load call'
    ),
]
for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing FX UI anchor: {label}')
    text = text.replace(old, new, 1)

section = r'''

            <!-- FX ANALYTICS -->
            <div id="fx" class="section-intro"><h2>FX Analytics</h2><div class="section-overview"><strong>What did currency do to GBP returns?</strong>Separate the current open book's local-price effect from FX translation, then stress the foreign-quoted holdings against sterling.</div></div>
            <section id="fx-analytics-card" class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-fuchsia-700 mb-1">FX Translation</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">Did the security move, or did sterling move?</h3>
                        <p id="fx-status" class="text-sm text-gray-500 mt-1">Calculating open-book FX translation and sterling sensitivity…</p>
                    </div>
                    <span class="self-start text-[10px] font-black uppercase tracking-wider rounded-full bg-fuchsia-50 text-fuchsia-700 border border-fuchsia-100 px-3 py-1.5">GBP base currency</span>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-5">
                    <div class="rounded-xl bg-gray-900 text-white p-4 col-span-2 md:col-span-1"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Foreign-Quoted Book</p><p id="fx-foreign-weight" class="text-2xl font-black mt-1">—</p><p id="fx-foreign-value" class="text-[9px] text-gray-400 mt-1">Share of total NAV</p></div>
                    <div class="rounded-xl bg-fuchsia-50/60 border border-fuchsia-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-fuchsia-700">Open-Book FX Effect</p><p id="fx-effect" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-fuchsia-700/70 mt-1">Translation since weighted entry FX</p></div>
                    <div class="rounded-xl bg-sky-50/60 border border-sky-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-sky-700">Local Price Effect</p><p id="fx-local-effect" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-sky-700/70 mt-1">Security-price component at entry FX</p></div>
                    <div class="rounded-xl bg-amber-50/60 border border-amber-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-amber-700">Largest FX Effect</p><p id="fx-largest-name" class="text-xl font-black mt-1">—</p><p id="fx-largest-value" class="text-[9px] text-amber-700/70 mt-1">Largest absolute holding-level translation</p></div>
                    <div class="rounded-xl bg-rose-50/60 border border-rose-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-rose-700">GBP +1% Shock</p><p id="fx-gbp-plus-one" class="text-2xl font-black mt-1">—</p><p id="fx-gbp-plus-one-note" class="text-[9px] text-rose-700/70 mt-1">Estimated NAV impact</p></div>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,.8fr)] gap-5 items-start">
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Open-Book P&amp;L Decomposition</h4><p class="text-xs text-gray-500 mt-0.5">Current unrealised P&amp;L split into local-price and FX translation effects. GBP-quoted holdings have no separate FX bar.</p></div>
                        <div id="fx-decomposition-chart" style="height:390px"></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Sterling Shock Sensitivity</h4><p class="text-xs text-gray-500 mt-0.5">All non-GBP quote currencies shocked simultaneously; local security prices held constant.</p></div>
                        <div id="fx-scenario-chart" style="height:390px"></div>
                    </div>
                </div>

                <div class="rounded-xl border border-gray-200 p-3 min-w-0 mt-5">
                    <div class="px-2 pt-1 flex flex-col md:flex-row md:items-start md:justify-between gap-2">
                        <div><h4 class="font-black text-sm text-gray-900">Foreign Currencies vs GBP</h4><p id="fx-history-note" class="text-xs text-gray-500 mt-0.5">Rebased FX paths for the foreign quote currencies currently in the portfolio.</p></div>
                        <span id="fx-history-period" class="text-[10px] font-black uppercase tracking-wider text-fuchsia-700 bg-fuchsia-50 border border-fuchsia-100 rounded-full px-2.5 py-1">Since Inception</span>
                    </div>
                    <div id="fx-history-chart" style="height:310px"></div>
                </div>

                <div id="fx-method" class="mt-4 rounded-lg bg-fuchsia-50/50 border border-fuchsia-100 px-4 py-3 text-[11px] leading-relaxed text-fuchsia-900"><strong>Method:</strong> waiting for the live FX decomposition. This analyses quote-currency translation, not issuer revenue or underlying ETF economic-currency exposure.</div>
            </section>
'''

anchor = '\n\n            <!-- PORTFOLIO RISK ANALYTICS -->'
if anchor not in text:
    raise SystemExit('FX section insertion anchor missing')
text = text.replace(anchor, section + anchor, 1)

functions = r'''

    function fxMoney(value) {
        const number = Number(value);
        if (!Number.isFinite(number)) return '—';
        return `${number >= 0 ? '+' : '-'}${fmtGBP(Math.abs(number))}`;
    }

    function fxSignedPct(value, digits=2) {
        const number = Number(value);
        if (!Number.isFinite(number)) return '—';
        return `${number >= 0 ? '+' : ''}${number.toFixed(digits)}%`;
    }

    function fxClass(value, positive='text-emerald-600', negative='text-red-600') {
        return Number(value) >= 0 ? positive : negative;
    }

    function renderFxHistory() {
        if (!fxAnalyticsData) return;
        const history = fxAnalyticsData.history || {};
        const traces = [];
        const periodLabel = currentRange === 'SI' ? 'Since Inception' : currentRange;
        const currencyMeta = new Map((fxAnalyticsData.currencies || []).map(row => [row.currency, row]));
        Object.entries(history).forEach(([currency, payload]) => {
            const dates = Array.isArray(payload.dates) ? payload.dates : [];
            const rates = Array.isArray(payload.rates) ? payload.rates : [];
            if (!dates.length || dates.length !== rates.length) return;
            const period = currencyMeta.get(currency)?.periods?.[currentRange];
            const startDate = period?.start_date || dates[0];
            let start = dates.findIndex(date => date >= startDate);
            if (start < 0) start = 0;
            const shownDates = dates.slice(start);
            const shownRates = rates.slice(start).map(Number);
            if (shownRates.length < 2 || !Number.isFinite(shownRates[0]) || shownRates[0] === 0) return;
            const base = shownRates[0];
            traces.push({
                x:shownDates,
                y:shownRates.map(value => value / base * 100),
                type:'scatter', mode:'lines', name:`${currency}/GBP`,
                line:{width:2.5},
                hovertemplate:`%{x}<br>${currency}/GBP rebased: %{y:.2f}<extra></extra>`
            });
        });
        document.getElementById('fx-history-period').textContent = periodLabel;
        if (!traces.length) {
            document.getElementById('fx-history-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">No foreign-currency history is available for this period.</div>';
            return;
        }
        Plotly.react('fx-history-chart', traces, {
            margin:{t:18,r:20,l:52,b:42}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
            legend:{orientation:'h',x:0,y:1.12,font:{size:10}}, xaxis:{showgrid:false},
            yaxis:{title:'Rebased FX rate',gridcolor:'#f3f4f6'}, hovermode:'x unified'
        }, {displayModeBar:false,responsive:true});
        const moves = (fxAnalyticsData.currencies || []).map(row => {
            const p = row.periods?.[currentRange];
            return p ? `${row.currency}/GBP ${fxSignedPct(p.change_pct)}` : null;
        }).filter(Boolean);
        document.getElementById('fx-history-note').textContent = moves.length
            ? `${periodLabel} move: ${moves.join(' · ')}. A positive move means the foreign currency strengthened against GBP.`
            : 'Rebased FX paths for the foreign quote currencies currently in the portfolio.';
    }

    function renderFxAnalytics(data) {
        fxAnalyticsData = data;
        const portfolio = data?.portfolio || {};
        const decomposition = data?.decomposition || {};
        const holdings = Array.isArray(data?.holdings) ? [...data.holdings] : [];
        const scenarios = Array.isArray(data?.scenarios) ? [...data.scenarios] : [];
        const currencies = Array.isArray(data?.currencies) ? data.currencies : [];

        document.getElementById('fx-status').textContent = `${portfolio.foreign_currency_count || currencies.length} foreign quote currenc${(portfolio.foreign_currency_count || currencies.length) === 1 ? 'y' : 'ies'} · ${Number(portfolio.foreign_quote_weight_pct || 0).toFixed(1)}% of NAV foreign-quoted · decomposition reconciles to current open-book unrealised P&L`;
        document.getElementById('fx-foreign-weight').textContent = `${Number(portfolio.foreign_quote_weight_pct || 0).toFixed(1)}%`;
        document.getElementById('fx-foreign-value').textContent = `${fmtGBP(portfolio.foreign_quote_value)} of total NAV`;

        const fxEffect = Number(decomposition.fx_effect || 0);
        const fxEl = document.getElementById('fx-effect');
        fxEl.textContent = fxMoney(fxEffect);
        fxEl.className = `text-2xl font-black mt-1 ${fxClass(fxEffect)}`;

        const localEffect = Number(decomposition.local_price_effect || 0);
        const localEl = document.getElementById('fx-local-effect');
        localEl.textContent = fxMoney(localEffect);
        localEl.className = `text-2xl font-black mt-1 ${fxClass(localEffect)}`;

        const largest = decomposition.largest_fx_effect;
        document.getElementById('fx-largest-name').textContent = largest?.symbol || '—';
        document.getElementById('fx-largest-value').textContent = largest ? `${fxMoney(largest.fx_effect)} · ${largest.currency}/GBP ${fxSignedPct(largest.fx_rate_change_since_entry_pct)}` : 'No foreign-currency holding';

        const plusOne = scenarios.find(row => Number(row.gbp_move_pct) === 1);
        const plusOneEl = document.getElementById('fx-gbp-plus-one');
        plusOneEl.textContent = plusOne ? fxSignedPct(plusOne.nav_impact_pct) : '—';
        plusOneEl.className = `text-2xl font-black mt-1 ${plusOne ? fxClass(plusOne.nav_impact_pct) : 'text-gray-900'}`;
        document.getElementById('fx-gbp-plus-one-note').textContent = plusOne ? `${fxMoney(plusOne.pnl_impact)} if GBP strengthens 1%` : 'Estimated NAV impact';

        const shown = holdings.filter(row => Math.abs(Number(row.local_price_effect || 0)) > .01 || Math.abs(Number(row.fx_effect || 0)) > .01).slice(0, 15).reverse();
        if (!shown.length) {
            document.getElementById('fx-decomposition-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">No open-book P&amp;L decomposition is available.</div>';
        } else {
            Plotly.react('fx-decomposition-chart', [
                {x:shown.map(r => Number(r.local_price_effect || 0)), y:shown.map(r => r.symbol), name:'Local price', type:'bar', orientation:'h', marker:{color:'#0ea5e9'}, hovertemplate:'<b>%{y}</b><br>Local price effect: £%{x:,.0f}<extra></extra>'},
                {x:shown.map(r => Number(r.fx_effect || 0)), y:shown.map(r => r.symbol), name:'FX translation', type:'bar', orientation:'h', marker:{color:'#c026d3'}, hovertemplate:'<b>%{y}</b><br>FX effect: £%{x:,.0f}<extra></extra>'}
            ], {
                barmode:'relative', margin:{t:28,r:18,l:72,b:45}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
                legend:{orientation:'h',x:0,y:1.12,font:{size:10}}, xaxis:{title:'P&L effect (£)',gridcolor:'#f3f4f6',zeroline:true,zerolinecolor:'#9ca3af'}, yaxis:{automargin:true}
            }, {displayModeBar:false,responsive:true});
        }

        if (!scenarios.length) {
            document.getElementById('fx-scenario-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Sterling sensitivity is unavailable.</div>';
        } else {
            const labels = scenarios.map(row => `${Number(row.gbp_move_pct) > 0 ? '+' : ''}${Number(row.gbp_move_pct).toFixed(0)}%`);
            const impacts = scenarios.map(row => Number(row.nav_impact_pct || 0));
            Plotly.react('fx-scenario-chart', [{
                x:labels, y:impacts, type:'bar',
                marker:{color:impacts.map(value => value >= 0 ? '#10b981' : '#ef4444')},
                text:impacts.map(value => `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`), textposition:'auto',
                hovertemplate:'GBP move: %{x}<br>NAV impact: %{y:.2f}%<extra></extra>'
            }], {
                margin:{t:18,r:18,l:52,b:48}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', showlegend:false,
                xaxis:{title:'GBP move vs foreign quote currencies'}, yaxis:{title:'NAV impact (%)',gridcolor:'#f3f4f6',zeroline:true,zerolinecolor:'#9ca3af'}
            }, {displayModeBar:false,responsive:true});
        }

        renderFxHistory();
        document.getElementById('fx-method').innerHTML = `<strong>Method:</strong> ${data.methodology || 'Weighted-average entry-FX decomposition of the current open book.'} Reconciliation residual: ${fmtGBP(Math.abs(Number(decomposition.reconciliation_error || 0)))}.`;
    }

    async function loadFxAnalytics() {
        try {
            const response = await fetch(`${API_BASE}/${PORTFOLIO_SLUG}/fx-analytics`);
            if (!response.ok) {
                let detail = `FX analytics request failed (${response.status})`;
                try { const body = await response.json(); detail = body.detail || detail; } catch (_) {}
                throw new Error(detail);
            }
            renderFxAnalytics(await response.json());
        } catch (error) {
            console.error('SethiPortfolio FX analytics failed:', error);
            document.getElementById('fx-status').textContent = 'Live FX analytics are temporarily unavailable; the rest of SethiPortfolio is unaffected.';
            ['fx-decomposition-chart','fx-scenario-chart','fx-history-chart'].forEach(id => {
                document.getElementById(id).innerHTML = '<div class="h-full flex items-center justify-center text-center px-5 text-sm text-gray-400">Unable to load live FX analytics.</div>';
            });
            document.getElementById('fx-method').innerHTML = `<strong>FX API:</strong> ${error.message || 'temporarily unavailable'}`;
        }
    }
'''

function_anchor = '\n\n    function riskPercent(value, digits=1) {'
if function_anchor not in text:
    raise SystemExit('FX functions insertion anchor missing')
text = text.replace(function_anchor, functions + function_anchor, 1)

path.write_text(text)
