from pathlib import Path

p = Path('sethiportfolio.html')
s = p.read_text(encoding='utf-8')

replacements = {
'''<span class="text-[9px] font-black uppercase tracking-widest text-gray-500 bg-gray-50 border border-gray-200 rounded-full px-2.5 py-1">Illustrative V1 Data</span>''':
'''<span class="text-[9px] font-black uppercase tracking-widest text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-full px-2.5 py-1">Live Portfolio Data</span>''',
'''<h2 class="text-2xl font-black tracking-tight text-gray-900">Fundamental Portfolio</h2>''':
'''<h2 id="portfolio-name" class="text-2xl font-black tracking-tight text-gray-900">Fundamental Portfolio</h2>''',
'''<p class="text-sm text-gray-500 mt-1.5 leading-relaxed">\n                        Bottom-up equities focused on durable quality, valuation discipline and long-term capital allocation. Every material change links to a dated investment note.\n                    </p>''':
'''<p id="portfolio-description" class="text-sm text-gray-500 mt-1.5 leading-relaxed">Loading portfolio strategy…</p>''',
'''<div class="rounded-xl bg-gray-900 text-white px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Portfolio Value</p><p class="text-xl font-black mt-0.5">£100,000</p></div>''':
'''<div class="rounded-xl bg-gray-900 text-white px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Portfolio Value</p><p id="portfolio-value" class="text-xl font-black mt-0.5">Loading…</p></div>''',
'''<div class="rounded-xl bg-emerald-50 border border-emerald-100 px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-emerald-700">Total Return</p><p class="text-xl font-black mt-0.5 text-emerald-700">+12.8%</p></div>''':
'''<div class="rounded-xl bg-emerald-50 border border-emerald-100 px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-emerald-700">Total Return</p><p id="total-return" class="text-xl font-black mt-0.5 text-emerald-700">Loading…</p></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Vs S&amp;P 500</p><p class="text-xl font-black mt-0.5 text-gray-900">+3.6pp</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Vs S&amp;P 500</p><p id="vs-sp500" class="text-xl font-black mt-0.5 text-gray-900">Loading…</p></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Since</p><p class="text-xl font-black mt-0.5 text-gray-900">Jun 2026</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 px-3.5 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Since</p><p id="since-date" class="text-xl font-black mt-0.5 text-gray-900">Loading…</p></div>''',
'''<div class="mt-auto pt-3"><span class="text-[9px] text-gray-400 bg-gray-50 border border-gray-100 rounded-full px-2.5 py-1">Illustrative only · not a live track record</span></div>''':
'''<div class="mt-auto pt-3"><span id="data-status" class="text-[9px] text-gray-400 bg-gray-50 border border-gray-100 rounded-full px-2.5 py-1">Transaction-backed portfolio · market prices via API</span></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-3"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Largest Position</p><p class="font-black mt-1">Company A · 24%</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-3"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Largest Position</p><p id="largest-position" class="font-black mt-1">Loading…</p></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-3"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Holdings</p><p class="font-black mt-1">6 positions</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-3"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Holdings</p><p id="holdings-count" class="font-black mt-1">Loading…</p></div>''',
'''<span class="text-xs text-gray-400">Illustrative holdings</span>''':
'''<span id="holdings-status" class="text-xs text-gray-400">Live market snapshot</span>''',
'''<tr><th class="text-left px-5 py-3">Holding</th><th class="text-right px-4 py-3">Weight</th><th class="text-right px-4 py-3">Entry</th><th class="text-right px-4 py-3">Current</th><th class="text-right px-4 py-3">Return</th><th class="text-right px-5 py-3">Contribution</th></tr>''':
'''<tr><th class="text-left px-5 py-3">Holding</th><th class="text-right px-4 py-3">Weight</th><th class="text-right px-4 py-3">Avg Cost</th><th class="text-right px-4 py-3">Current</th><th class="text-right px-4 py-3">Return</th><th class="text-right px-5 py-3">Unrealised P&amp;L</th></tr>''',
'''<div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Total Return</p><p class="text-2xl font-black mt-1">+12.8%</p></div>''':
'''<div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Total Return</p><p id="analytics-total-return" class="text-2xl font-black mt-1">—</p></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Annualised</p><p class="text-2xl font-black mt-1">+18.4%</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Annualised</p><p id="analytics-annualised" class="text-2xl font-black mt-1">—</p></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Volatility</p><p class="text-2xl font-black mt-1">14.2%</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Volatility</p><p id="analytics-volatility" class="text-2xl font-black mt-1">—</p></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Max Drawdown</p><p class="text-2xl font-black mt-1 text-red-600">-7.6%</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Max Drawdown</p><p id="analytics-drawdown" class="text-2xl font-black mt-1 text-red-600">—</p></div>''',
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4 col-span-2 md:col-span-1"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Sharpe</p><p class="text-2xl font-black mt-1">1.18</p></div>''':
'''<div class="rounded-xl bg-gray-50 border border-gray-100 p-4 col-span-2 md:col-span-1"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Sharpe*</p><p id="analytics-sharpe" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">0% risk-free rate</p></div>''',
'''<span class="text-[10px] uppercase tracking-wider font-black text-gray-400 bg-gray-50 border border-gray-100 rounded-full px-3 py-1">3 demo notes</span>''':
'''<span id="journal-count" class="text-[10px] uppercase tracking-wider font-black text-gray-400 bg-gray-50 border border-gray-100 rounded-full px-3 py-1">Loading notes…</span>'''
}

for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f'markup target not found: {old[:80]}')
    s = s.replace(old, new, 1)

script_start = s.rfind('<script>')
script_end = s.rfind('</script>')
if script_start == -1 or script_end == -1 or script_end < script_start:
    raise SystemExit('script block not found')

new_script = r'''<script>
    const API_BASE = 'https://sethistock-api.onrender.com/api/portfolio';
    const PORTFOLIO_SLUG = 'fundamental';
    let portfolioData = { dates: [], portfolio: [], sp500: [], nasdaq: [], vwrl: [] };
    let currentRange = 'SI';
    const activeSeries = {portfolio:true, sp500:true, nasdaq:true, vwrl:true};
    const seriesMeta = {
        portfolio:{name:'Sethi Fundamental', dash:'solid', width:3},
        sp500:{name:'S&P 500 Total Return', dash:'dot', width:2},
        nasdaq:{name:'Nasdaq-100 (QQQ)', dash:'dash', width:2},
        vwrl:{name:'VWRL', dash:'dashdot', width:2}
    };

    const fmtGBP = value => new Intl.NumberFormat('en-GB', {style:'currency', currency:'GBP', maximumFractionDigits:0}).format(value || 0);
    const fmtMoney = (value, currency='GBP') => new Intl.NumberFormat('en-GB', {style:'currency', currency, minimumFractionDigits:2, maximumFractionDigits:2}).format(value || 0);
    const fmtPct = value => `${value >= 0 ? '+' : ''}${Number(value || 0).toFixed(2)}%`;
    const fmtPp = value => `${value >= 0 ? '+' : ''}${Number(value || 0).toFixed(2)}pp`;
    const prettyDate = value => new Date(`${value}T00:00:00`).toLocaleDateString('en-GB', {day:'2-digit', month:'short', year:'numeric'});

    function rangeStartIndex(range) {
        if (!portfolioData.dates.length || range === 'SI') return 0;
        const last = new Date(`${portfolioData.dates.at(-1)}T00:00:00`);
        let cutoff = new Date(last);
        if (range === '1M') cutoff.setMonth(cutoff.getMonth() - 1);
        else if (range === '3M') cutoff.setMonth(cutoff.getMonth() - 3);
        else if (range === 'YTD') cutoff = new Date(last.getFullYear(), 0, 1);
        else if (range === '1Y') cutoff.setFullYear(cutoff.getFullYear() - 1);
        const idx = portfolioData.dates.findIndex(d => new Date(`${d}T00:00:00`) >= cutoff);
        return idx < 0 ? 0 : idx;
    }

    function renderPerformance() {
        const start = rangeStartIndex(currentRange);
        const dates = portfolioData.dates.slice(start);
        const traces = Object.keys(activeSeries).filter(k => activeSeries[k]).map(k => ({
            x: dates,
            y: portfolioData[k].slice(start),
            name: seriesMeta[k].name,
            type:'scatter', mode:'lines', connectgaps:false,
            line:{width:seriesMeta[k].width, dash:seriesMeta[k].dash},
            hovertemplate:'%{x}<br>%{y:.2f}<extra>'+seriesMeta[k].name+'</extra>'
        }));
        Plotly.react('performance-chart', traces, {
            margin:{t:15,r:25,l:50,b:45}, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
            legend:{orientation:'h',y:1.08,x:0}, xaxis:{showgrid:false}, yaxis:{title:'Rebased value',gridcolor:'#f3f4f6'},
            hovermode:'x unified'
        }, {displayModeBar:false,responsive:true});
    }

    function toggleSeriesMenu() { document.getElementById('series-menu').classList.toggle('hidden'); }
    function updateSeriesCount() {
        const activeCount = 1 + ['sp500','nasdaq','vwrl'].filter(k => activeSeries[k]).length;
        document.getElementById('series-count').textContent = `${activeCount}/4`;
    }
    document.querySelectorAll('[data-series-check]').forEach(input => input.addEventListener('change', () => {
        activeSeries[input.dataset.seriesCheck] = input.checked;
        updateSeriesCount(); renderPerformance();
    }));
    document.addEventListener('click', event => {
        const menu = document.getElementById('series-menu');
        const button = document.getElementById('series-menu-btn');
        if (!menu.contains(event.target) && !button.contains(event.target)) menu.classList.add('hidden');
    });
    function setRange(range, btn) {
        currentRange = range;
        document.querySelectorAll('.range-btn').forEach(b => b.className='range-btn px-3 py-1.5 rounded-md text-gray-500');
        btn.className='range-btn px-3 py-1.5 rounded-md bg-white text-blue-700 shadow-sm';
        renderPerformance();
    }

    function renderHoldings(snapshot) {
        const holdings = snapshot.holdings || [];
        const chartLabels = holdings.map(h => h.symbol);
        const chartValues = holdings.map(h => h.weight_pct);
        if ((snapshot.cash_weight_pct || 0) > 0.01) { chartLabels.push('Cash'); chartValues.push(snapshot.cash_weight_pct); }
        Plotly.react('weights-chart', [{labels:chartLabels,values:chartValues,type:'pie',hole:.62,textinfo:'label+percent',hovertemplate:'%{label}: %{value:.2f}%<extra></extra>'}], {
            margin:{t:10,r:10,l:10,b:10}, paper_bgcolor:'rgba(0,0,0,0)', showlegend:false
        }, {displayModeBar:false,responsive:true});

        const largest = holdings[0];
        document.getElementById('largest-position').textContent = largest ? `${largest.symbol} · ${largest.weight_pct.toFixed(2)}%` : 'Cash';
        document.getElementById('holdings-count').textContent = `${holdings.length} position${holdings.length === 1 ? '' : 's'}`;
        document.getElementById('holdings-table').innerHTML = holdings.length ? holdings.map(h => `
            <tr class="border-t border-gray-100 hover:bg-gray-50/60 transition">
                <td class="px-5 py-4"><div class="font-black text-gray-900">${h.name}</div><div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">${h.symbol} · ${h.quantity.toLocaleString('en-GB')} units</div></td>
                <td class="px-4 py-4 text-right font-black">${h.weight_pct.toFixed(2)}%</td>
                <td class="px-4 py-4 text-right text-gray-500">${fmtMoney(h.average_cost, h.currency)}</td>
                <td class="px-4 py-4 text-right text-gray-500">${fmtMoney(h.current_price, h.currency)}</td>
                <td class="px-4 py-4 text-right font-black ${h.unrealised_return_pct>=0?'text-emerald-600':'text-red-600'}">${fmtPct(h.unrealised_return_pct)}</td>
                <td class="px-5 py-4 text-right font-black ${h.unrealised_pnl>=0?'text-emerald-600':'text-red-600'}">${fmtMoney(h.unrealised_pnl, snapshot.base_currency)}</td>
            </tr>`).join('') : '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">No open holdings.</td></tr>';
    }

    function calculateAnalytics(values, dates) {
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

    function renderJournal(entries) {
        const list = entries || [];
        document.getElementById('journal-count').textContent = `${list.length} published note${list.length === 1 ? '' : 's'}`;
        document.getElementById('journal-list').innerHTML = list.length ? list.map(j => `
            <article class="rounded-xl border border-gray-200 p-4 md:p-5 hover:border-amber-300 transition">
                <div class="flex flex-wrap items-center gap-2 text-[10px] font-black uppercase tracking-wider"><span class="text-gray-400">${prettyDate(j.effective_date)}</span><span class="text-amber-700 bg-amber-50 border border-amber-100 rounded-full px-2 py-0.5">${j.category || 'Journal'}</span></div>
                <h4 class="text-lg font-black mt-2">${j.title}</h4><p class="text-sm text-gray-500 mt-1 leading-relaxed">${j.summary || ''}</p>
                ${j.body ? `<details class="mt-3"><summary class="text-xs font-black text-blue-700 cursor-pointer">Read analysis</summary><p class="text-sm text-gray-600 mt-2 whitespace-pre-line">${j.body}</p></details>` : ''}
            </article>`).join('') : '<div class="rounded-xl border border-dashed border-gray-200 p-7 text-sm text-gray-400 text-center">No published investment notes yet. Future portfolio decisions will appear here with their dated rationale.</div>';
    }

    function renderTransactions(transactions) {
        const list = (transactions || []).slice().reverse();
        document.getElementById('change-log').innerHTML = list.length ? list.map(t => {
            const instrument = t.instruments || {};
            const side = String(t.side || '').toUpperCase();
            return `<div class="p-5 hover:bg-gray-50/60 transition"><div class="flex items-center justify-between gap-3"><div><div class="flex items-center gap-2"><span class="font-black">${instrument.symbol || '—'}</span><span class="text-[10px] uppercase tracking-wider font-black ${side==='BUY'?'text-emerald-700 bg-emerald-50':'text-red-700 bg-red-50'} rounded-full px-2 py-0.5">${side}</span></div><p class="text-xs text-gray-500 mt-1">${Number(t.quantity).toLocaleString('en-GB')} units @ ${fmtMoney(Number(t.price), t.currency || instrument.currency || 'GBP')}</p></div><span class="text-xs font-bold text-gray-400">${prettyDate(t.trade_date)}</span></div>${t.note ? `<p class="text-[11px] text-gray-500 mt-3">${t.note}</p>` : ''}</div>`;
        }).join('') : '<div class="p-6 text-sm text-gray-400 text-center">No portfolio transactions recorded.</div>';
    }

    async function loadPortfolio() {
        try {
            const [portfolioRes, performanceRes, journalRes, transactionsRes] = await Promise.all([
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/performance`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/journal`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/transactions`)
            ]);
            if (![portfolioRes,performanceRes,journalRes,transactionsRes].every(r=>r.ok)) throw new Error('One or more portfolio API requests failed.');
            const [portfolioPayload, performance, journalPayload, transactionPayload] = await Promise.all([
                portfolioRes.json(), performanceRes.json(), journalRes.json(), transactionsRes.json()
            ]);
            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;
            const sp500 = performance.benchmarks['^SP500TR']?.values || [];
            const nasdaq = performance.benchmarks['QQQ']?.values || [];
            const vwrl = performance.benchmarks['VWRL.L']?.values || [];
            portfolioData = {dates:performance.dates || [], portfolio:performance.portfolio || [], sp500, nasdaq, vwrl};

            document.getElementById('portfolio-name').textContent = info.name;
            document.getElementById('portfolio-description').textContent = info.description || '';
            document.getElementById('portfolio-value').textContent = fmtGBP(snapshot.portfolio_value);
            const totalReturn = (snapshot.portfolio_value / info.initial_capital - 1) * 100;
            document.getElementById('total-return').textContent = fmtPct(totalReturn);
            document.getElementById('since-date').textContent = new Date(`${info.inception_date}T00:00:00`).toLocaleDateString('en-GB',{month:'short',year:'numeric'});
            const spReturn = sp500.length ? sp500.at(-1)-100 : 0;
            document.getElementById('vs-sp500').textContent = fmtPp(totalReturn-spReturn);
            document.getElementById('holdings-status').textContent = `Priced ${new Date(snapshot.pricing_timestamp).toLocaleString('en-GB')}`;

            renderPerformance(); renderHoldings(snapshot); renderAnalytics(performance);
            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions);
        } catch (error) {
            console.error('SethiPortfolio load failed:', error);
            document.getElementById('data-status').textContent = 'Live data temporarily unavailable · please retry shortly';
            document.getElementById('performance-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load live portfolio data.</div>';
            document.getElementById('holdings-table').innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">Unable to load holdings.</td></tr>';
        }
    }

    loadPortfolio();
</script>'''

s = s[:script_start] + new_script + s[script_end + len('</script>'):]
p.write_text(s, encoding='utf-8')
