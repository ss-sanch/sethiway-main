from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #risk, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #exposure, #risk, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin'
    ),
    (
        '                <a href="#holdings" class="hover:text-blue-600">Holdings</a>\n                <a href="#risk" class="hover:text-blue-600">Risk</a>',
        '                <a href="#holdings" class="hover:text-blue-600">Holdings</a>\n                <a href="#exposure" class="hover:text-blue-600">Exposure</a>\n                <a href="#risk" class="hover:text-blue-600">Risk</a>',
        'navigation'
    ),
    (
        '    let attributionData = { periods: {} };\n    let riskAnalyticsData = null;\n    let journalEntries = [];',
        '    let attributionData = { periods: {} };\n    let exposureData = null;\n    let riskAnalyticsData = null;\n    let journalEntries = [];',
        'state'
    ),
    (
        '    loadPortfolio();\n    loadRiskAnalytics();',
        '    loadPortfolio();\n    loadExposureMap();\n    loadRiskAnalytics();',
        'load call'
    ),
]

for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing exposure UI anchor: {label}')
    text = text.replace(old, new, 1)

section = r'''

            <!-- PORTFOLIO EXPOSURE MAP -->
            <div id="exposure" class="section-intro"><h2>Exposure Map</h2><div class="section-overview"><strong>What are you actually exposed to?</strong>Look beyond ticker weights to see sector, quote-currency and issuer-geography concentration across the current portfolio. ETF sector look-through is used where the underlying fund data supports it.</div></div>
            <section id="exposure-map-card" class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-sky-700 mb-1">Exposure Map</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">What sits underneath the portfolio weights?</h3>
                        <p id="exposure-status" class="text-sm text-gray-500 mt-1">Classifying live holdings and fund look-through…</p>
                    </div>
                    <span class="self-start text-[10px] font-black uppercase tracking-wider rounded-full bg-sky-50 text-sky-700 border border-sky-100 px-3 py-1.5">Current portfolio</span>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-5">
                    <div class="rounded-xl bg-gray-900 text-white p-4 col-span-2 md:col-span-1"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Largest Sector</p><p id="exposure-largest-sector" class="text-xl font-black mt-1">—</p><p id="exposure-largest-sector-note" class="text-[9px] text-gray-400 mt-1">Share of invested capital</p></div>
                    <div class="rounded-xl bg-violet-50/60 border border-violet-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-violet-700">Largest Quote Currency</p><p id="exposure-largest-currency" class="text-2xl font-black mt-1">—</p><p id="exposure-largest-currency-note" class="text-[9px] text-violet-700/70 mt-1">Share of total NAV incl. cash</p></div>
                    <div class="rounded-xl bg-amber-50/60 border border-amber-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-amber-700">ETF / Fund Share</p><p id="exposure-fund-share" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-amber-700/70 mt-1">Share of total portfolio NAV</p></div>
                    <div class="rounded-xl bg-emerald-50/60 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">Sector Coverage</p><p id="exposure-sector-coverage" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-emerald-700/70 mt-1">Direct + fund sector look-through</p></div>
                    <div class="rounded-xl bg-blue-50/60 border border-blue-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-blue-700">Geography Coverage</p><p id="exposure-geography-coverage" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-blue-700/70 mt-1">Issuer-country look-through</p></div>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,.8fr)_minmax(0,.95fr)] gap-4 items-start">
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Sector Exposure</h4><p class="text-xs text-gray-500 mt-0.5">Share of invested capital. ETF sector weights are looked through when fund data is available.</p></div>
                        <div id="exposure-sector-chart" style="height:350px"></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Quote-Currency Exposure</h4><p class="text-xs text-gray-500 mt-0.5">Share of total NAV, including cash in the portfolio base currency.</p></div>
                        <div id="exposure-currency-chart" style="height:300px"></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 p-3 min-w-0">
                        <div class="px-2 pt-1"><h4 class="font-black text-sm text-gray-900">Issuer Geography</h4><p class="text-xs text-gray-500 mt-0.5">Direct holdings use issuer country; ETF geography is left unresolved without underlying-country data.</p></div>
                        <div id="exposure-geography-chart" style="height:300px"></div>
                    </div>
                </div>

                <div id="exposure-method" class="mt-4 rounded-lg bg-sky-50/50 border border-sky-100 px-4 py-3 text-[11px] leading-relaxed text-sky-900"><strong>Method:</strong> waiting for the live exposure classification. Quote-currency exposure is not the same as economic or revenue currency exposure.</div>
            </section>
'''

anchor = '\n\n            <!-- PORTFOLIO RISK ANALYTICS -->'
if anchor not in text:
    raise SystemExit('Exposure section insertion anchor missing')
text = text.replace(anchor, section + anchor, 1)

functions = r'''

    function exposurePercent(value, digits=1) {
        const number = Number(value);
        return Number.isFinite(number) ? `${number.toFixed(digits)}%` : '—';
    }

    function exposureDisplayLabel(label) {
        return String(label || 'Unclassified')
            .replace('ETF / Fund — geographic look-through unavailable', 'ETF / Fund — no look-through');
    }

    function renderExposureBars(elementId, rows, color, basisLabel) {
        const chart = document.getElementById(elementId);
        const data = Array.isArray(rows) ? rows.filter(row => Number(row.weight_pct) > 0.005) : [];
        if (!data.length) {
            chart.innerHTML = '<div class="h-full flex items-center justify-center text-center px-5 text-sm text-gray-400">Exposure classification is unavailable.</div>';
            return;
        }
        const shown = data.slice(0, 12);
        const labels = shown.map(row => exposureDisplayLabel(row.label));
        const values = shown.map(row => Number(row.weight_pct || 0));
        const dynamicHeight = Math.max(250, Math.min(390, 115 + shown.length * 27));
        chart.style.height = `${dynamicHeight}px`;
        Plotly.react(elementId, [{
            x:values,
            y:labels,
            type:'bar',
            orientation:'h',
            marker:{color},
            text:values.map(value => `${value.toFixed(1)}%`),
            textposition:'auto',
            cliponaxis:false,
            customdata:shown.map(row => row.label),
            hovertemplate:`<b>%{customdata}</b><br>${basisLabel}: %{x:.2f}%<extra></extra>`
        }], {
            margin:{t:12,r:24,l:115,b:42},
            paper_bgcolor:'rgba(0,0,0,0)',
            plot_bgcolor:'rgba(0,0,0,0)',
            showlegend:false,
            xaxis:{title:'Share (%)',gridcolor:'#f3f4f6',rangemode:'tozero'},
            yaxis:{automargin:true,autorange:'reversed',tickfont:{size:10}},
        }, {displayModeBar:false,responsive:true});
    }

    function renderExposureMap(data) {
        exposureData = data;
        const portfolio = data?.portfolio || {};
        const coverage = data?.coverage || {};
        const exposures = data?.exposures || {};
        const largest = data?.largest || {};
        const failures = Array.isArray(coverage.metadata_failures) ? coverage.metadata_failures : [];

        document.getElementById('exposure-status').textContent = `${portfolio.holding_count || 0} invested holdings · ${exposurePercent(coverage.sector_lookthrough_pct)} sector coverage · ${exposurePercent(coverage.geography_lookthrough_pct)} geography coverage${failures.length ? ` · metadata fallback: ${failures.join(', ')}` : ''}`;

        const sector = largest.sector;
        document.getElementById('exposure-largest-sector').textContent = sector?.label || '—';
        document.getElementById('exposure-largest-sector-note').textContent = sector ? `${exposurePercent(sector.weight_pct)} of invested capital` : 'Share of invested capital';

        const currency = largest.currency;
        document.getElementById('exposure-largest-currency').textContent = currency?.label || '—';
        document.getElementById('exposure-largest-currency-note').textContent = currency ? `${exposurePercent(currency.weight_pct)} of total NAV incl. cash` : 'Share of total NAV incl. cash';

        const securityRows = Array.isArray(exposures.security_type) ? exposures.security_type : [];
        const fundRow = securityRows.find(row => String(row.label) === 'ETF / Fund');
        document.getElementById('exposure-fund-share').textContent = fundRow ? exposurePercent(fundRow.weight_pct) : '0.0%';
        document.getElementById('exposure-sector-coverage').textContent = exposurePercent(coverage.sector_lookthrough_pct);
        document.getElementById('exposure-geography-coverage').textContent = exposurePercent(coverage.geography_lookthrough_pct);

        renderExposureBars('exposure-sector-chart', exposures.sector, '#0ea5e9', 'Invested capital');
        renderExposureBars('exposure-currency-chart', exposures.currency, '#7c3aed', 'Total NAV');
        renderExposureBars('exposure-geography-chart', exposures.geography, '#f59e0b', 'Invested capital');

        document.getElementById('exposure-method').innerHTML = `<strong>Method:</strong> ${data.methodology || 'Live security classification with fund sector look-through where available.'} Sector coverage: ${exposurePercent(coverage.sector_lookthrough_pct)}; geography coverage: ${exposurePercent(coverage.geography_lookthrough_pct)}.${failures.length ? ` Metadata fallback used for ${failures.join(', ')}.` : ''}`;
    }

    async function loadExposureMap() {
        try {
            const response = await fetch(`${API_BASE}/${PORTFOLIO_SLUG}/exposures`);
            if (!response.ok) {
                let detail = `Exposure request failed (${response.status})`;
                try { const body = await response.json(); detail = body.detail || detail; } catch (_) {}
                throw new Error(detail);
            }
            renderExposureMap(await response.json());
        } catch (error) {
            console.error('SethiPortfolio exposure map failed:', error);
            document.getElementById('exposure-status').textContent = 'Live exposure classification is temporarily unavailable; the rest of SethiPortfolio is unaffected.';
            ['exposure-sector-chart','exposure-currency-chart','exposure-geography-chart'].forEach(id => {
                document.getElementById(id).innerHTML = '<div class="h-full flex items-center justify-center text-center px-5 text-sm text-gray-400">Unable to load the live exposure map.</div>';
            });
            document.getElementById('exposure-method').innerHTML = `<strong>Exposure API:</strong> ${error.message || 'temporarily unavailable'}`;
        }
    }
'''

function_anchor = '\n\n    function riskPercent(value, digits=1) {'
if function_anchor not in text:
    raise SystemExit('Exposure functions insertion anchor missing')
text = text.replace(function_anchor, functions + function_anchor, 1)

path.write_text(text)
