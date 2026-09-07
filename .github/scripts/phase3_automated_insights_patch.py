from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #risk, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #risk, #analytics, #insights, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin'
    ),
    (
        '                <a href="#analytics" class="hover:text-blue-600">Analytics</a>\n                <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>',
        '                <a href="#analytics" class="hover:text-blue-600">Analytics</a>\n                <a href="#insights" class="hover:text-blue-600">Insights</a>\n                <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>',
        'navigation'
    ),
    (
        '    let riskAnalyticsData = null;\n    let journalEntries = [];',
        '    let riskAnalyticsData = null;\n    let latestSnapshot = null;\n    let latestTransactions = [];\n    let journalEntries = [];',
        'state'
    ),
    (
        '            attributionData = attributionPayload || { periods: {} };\n            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;',
        '            attributionData = attributionPayload || { periods: {} };\n            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;\n            latestSnapshot = snapshot;',
        'snapshot state'
    ),
    (
        '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics();\n            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions);',
        '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics();\n            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions); renderAutomatedInsights();',
        'load render'
    ),
    (
        '    function renderTransactions(transactions) {\n        const list = (transactions || []).slice().reverse();',
        '    function renderTransactions(transactions) {\n        latestTransactions = transactions || [];\n        const list = latestTransactions.slice().reverse();',
        'transaction state'
    ),
    (
        '        document.getElementById(\'risk-method\').innerHTML = `<strong>Method:</strong> ${data.methodology || \'Variance-covariance Euler VaR attribution.\'} Parameters: ${(Number(params.confidence || 0.99) * 100).toFixed(0)}% confidence, ${params.horizon_days || 10}-day horizon, ${params.lookback || \'2y\'} lookback.`;\n    }',
        '        document.getElementById(\'risk-method\').innerHTML = `<strong>Method:</strong> ${data.methodology || \'Variance-covariance Euler VaR attribution.\'} Parameters: ${(Number(params.confidence || 0.99) * 100).toFixed(0)}% confidence, ${params.horizon_days || 10}-day horizon, ${params.lookback || \'2y\'} lookback.`;\n        renderAutomatedInsights();\n    }',
        'risk rerender'
    ),
]

for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing automated insights anchor: {label}')
    text = text.replace(old, new, 1)

section = r'''
            <!-- AUTOMATED PORTFOLIO INSIGHTS -->
            <div id="insights" class="section-intro"><h2>Portfolio Insights</h2><div class="section-overview"><strong>One read across the portfolio</strong>Convert the performance, attribution, drawdown, risk and decision data already on SethiPortfolio into a concise current-state diagnosis. No additional inputs are required.</div></div>
            <section class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-sky-700 mb-1">Automated Read</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">What matters now?</h3>
                        <p id="insights-status" class="text-sm text-gray-500 mt-1">Combining 1M performance, live risk and the latest portfolio decision…</p>
                    </div>
                    <span class="self-start text-[10px] font-black uppercase tracking-wider rounded-full bg-sky-50 text-sky-700 border border-sky-100 px-3 py-1.5">No extra data entry</span>
                </div>

                <div class="rounded-xl bg-gray-900 text-white px-5 py-4 mb-4">
                    <div class="flex items-center gap-2 mb-2"><span class="w-2 h-2 rounded-full bg-sky-400"></span><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Current Portfolio Read</p></div>
                    <p id="insights-summary" class="text-sm md:text-[15px] leading-7 font-semibold text-gray-100">Waiting for live portfolio data…</p>
                </div>

                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                    <div class="rounded-xl bg-blue-50/60 border border-blue-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-blue-700">1M vs S&amp;P 500</p><p id="insights-relative" class="text-2xl font-black mt-1">—</p><p id="insights-relative-note" class="text-[9px] text-blue-700/70 mt-1">Recent active return</p></div>
                    <div class="rounded-xl bg-emerald-50/60 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">1M Top Driver</p><p id="insights-driver" class="text-xl font-black mt-1">—</p><p id="insights-driver-note" class="text-[9px] text-emerald-700/70 mt-1">Largest contribution</p></div>
                    <div class="rounded-xl bg-rose-50/60 border border-rose-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-rose-700">Current Drawdown</p><p id="insights-drawdown" class="text-2xl font-black mt-1">—</p><p id="insights-drawdown-note" class="text-[9px] text-rose-700/70 mt-1">From latest high-water mark</p></div>
                    <div class="rounded-xl bg-amber-50/60 border border-amber-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-amber-700">Top Risk Contributor</p><p id="insights-risk" class="text-xl font-black mt-1">—</p><p id="insights-risk-note" class="text-[9px] text-amber-700/70 mt-1">Waiting for live risk map</p></div>
                </div>

                <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,.65fr)] gap-4">
                    <div class="rounded-xl border border-gray-200 overflow-hidden">
                        <div class="px-4 py-3 border-b border-gray-100"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Priority Readout</p><h4 class="text-sm font-black mt-0.5">What deserves attention?</h4></div>
                        <div id="insights-priority" class="divide-y divide-gray-100"><div class="p-4 text-sm text-gray-400">Generating portfolio observations…</div></div>
                    </div>
                    <div class="rounded-xl border border-gray-200 bg-gray-50/40 p-4">
                        <p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Latest Decision</p>
                        <div id="insights-decision" class="mt-2 text-sm text-gray-500 leading-relaxed">Loading the latest effective portfolio change…</div>
                    </div>
                </div>

                <div class="mt-4 rounded-lg bg-sky-50/50 border border-sky-100 px-4 py-3 text-[11px] leading-relaxed text-sky-900"><strong>How to read this:</strong> observations are deterministic summaries of existing SethiPortfolio data. Concentration, correlation, drawdown and relative-performance thresholds are prompts for review, not investment recommendations.</div>
            </section>

'''

anchor = '            <!-- JOURNAL + CHANGE LOG -->'
if anchor not in text:
    raise SystemExit('Automated insights section anchor missing')
text = text.replace(anchor, section + anchor, 1)

functions = r'''
    function insightWindowReturn(series, range='1M') {
        const dates = portfolioData.dates || [];
        const values = series || [];
        const limit = Math.min(dates.length, values.length);
        if (limit < 2) return null;
        const lastDate = new Date(`${dates[limit - 1]}T00:00:00`);
        let cutoff = new Date(lastDate);
        if (range === '1M') cutoff.setMonth(cutoff.getMonth() - 1);
        else if (range === '3M') cutoff.setMonth(cutoff.getMonth() - 3);
        else if (range === 'YTD') cutoff = new Date(lastDate.getFullYear(), 0, 1);
        let first = -1;
        for (let i = 0; i < limit; i++) {
            const value = Number(values[i]);
            if (new Date(`${dates[i]}T00:00:00`) >= cutoff && Number.isFinite(value) && value > 0) { first = i; break; }
        }
        let last = -1;
        for (let i = limit - 1; i >= 0; i--) {
            const value = Number(values[i]);
            if (Number.isFinite(value) && value > 0) { last = i; break; }
        }
        if (first < 0 || last <= first) return null;
        return (Number(values[last]) / Number(values[first]) - 1) * 100;
    }

    function insightTone(type) {
        const map = {
            warning:{dot:'bg-amber-500', badge:'bg-amber-50 text-amber-700 border-amber-100', label:'Watch'},
            risk:{dot:'bg-red-500', badge:'bg-red-50 text-red-700 border-red-100', label:'Risk'},
            positive:{dot:'bg-emerald-500', badge:'bg-emerald-50 text-emerald-700 border-emerald-100', label:'Positive'},
            neutral:{dot:'bg-blue-500', badge:'bg-blue-50 text-blue-700 border-blue-100', label:'Monitor'}
        };
        return map[type] || map.neutral;
    }

    function latestPortfolioDecision() {
        const txns = [...(latestTransactions || [])];
        if (!txns.length) return null;
        txns.sort((a,b) => String(b.trade_date || '').localeCompare(String(a.trade_date || '')));
        const allocationTarget = txns.find(txn => /^ALLOCATION ([a-f0-9]{12}) TARGET:/i.test(String(txn.note || '')));
        const latestDate = String(txns[0]?.trade_date || '');
        let chosen = allocationTarget && String(allocationTarget.trade_date || '') === latestDate ? allocationTarget : txns[0];
        const targetMatch = /^ALLOCATION ([a-f0-9]{12}) TARGET:\s*(.*)$/i.exec(String(chosen.note || ''));
        if (targetMatch) {
            const decisionId = targetMatch[1].toLowerCase();
            const funding = txns.find(txn => new RegExp(`^ALLOCATION ${decisionId} FUNDING:`, 'i').test(String(txn.note || '')));
            const targetSymbol = chosen.instruments?.symbol || '—';
            const fundingSymbol = funding?.instruments?.symbol || 'portfolio funding';
            const rationale = journalEntries.find(j => j.related_transaction_id === chosen.id);
            return {
                date: chosen.trade_date,
                title: `${fundingSymbol} → ${targetSymbol}`,
                text: targetMatch[2] || chosen.note || 'Active allocation recorded.',
                rationale,
            };
        }
        const symbol = chosen.instruments?.symbol || '—';
        const side = String(chosen.side || '').toUpperCase();
        const rationale = journalEntries.find(j => j.related_transaction_id === chosen.id);
        return {date:chosen.trade_date, title:`${side} ${symbol}`, text:chosen.note || `${side} transaction recorded.`, rationale};
    }

    function renderAutomatedInsights() {
        const summary = document.getElementById('insights-summary');
        if (!summary) return;
        const p1m = insightWindowReturn(portfolioData.portfolio, '1M');
        const s1m = insightWindowReturn(portfolioData.sp500, '1M');
        const excess = p1m != null && s1m != null ? p1m - s1m : null;
        const oneMonth = attributionData?.periods?.['1M'];
        const components = Array.isArray(oneMonth?.components) ? oneMonth.components : [];
        const contributor = [...components].filter(row => Number(row.contribution_pp) > 0).sort((a,b)=>Number(b.contribution_pp)-Number(a.contribution_pp))[0] || null;
        const detractor = [...components].filter(row => Number(row.contribution_pp) < 0).sort((a,b)=>Number(a.contribution_pp)-Number(b.contribution_pp))[0] || null;
        const dd = drawdownAnalysis(portfolioData.portfolio || [], portfolioData.dates || [], 0);
        const currentDD = dd?.currentDrawdown ?? null;
        const concentration = riskAnalyticsData?.concentration || {};
        const riskAttribution = riskAnalyticsData?.attribution || {};
        const riskPortfolio = riskAnalyticsData?.portfolio || {};
        const topRisk = concentration.top_risk_contributor || riskAttribution.components?.[0] || null;

        const relativeEl = document.getElementById('insights-relative');
        relativeEl.textContent = excess == null ? '—' : fmtPp(excess);
        relativeEl.className = `text-2xl font-black mt-1 ${excess == null ? 'text-gray-900' : excess >= 0 ? 'text-emerald-600' : 'text-red-600'}`;
        document.getElementById('insights-relative-note').textContent = p1m == null || s1m == null ? 'Insufficient 1M history' : `Portfolio ${fmtPct(p1m)} · S&P ${fmtPct(s1m)}`;

        document.getElementById('insights-driver').textContent = contributor?.symbol || detractor?.symbol || '—';
        const driver = contributor || detractor;
        document.getElementById('insights-driver-note').textContent = driver ? `${fmtPp(driver.contribution_pp)} contribution · 1M` : 'No attributable 1M driver';

        const drawdownEl = document.getElementById('insights-drawdown');
        drawdownEl.textContent = currentDD == null ? '—' : `${Number(currentDD).toFixed(2)}%`;
        drawdownEl.className = `text-2xl font-black mt-1 ${currentDD == null ? 'text-gray-900' : currentDD < -5 ? 'text-red-600' : currentDD < -2 ? 'text-amber-600' : 'text-gray-900'}`;
        document.getElementById('insights-drawdown-note').textContent = dd?.currentEpisode?.start?.date ? `Peak from ${prettyDate(dd.currentEpisode.start.date)}` : 'At or near high-water mark';

        document.getElementById('insights-risk').textContent = topRisk?.ticker || '—';
        document.getElementById('insights-risk-note').textContent = topRisk ? `${Number(topRisk.contribution_pct || 0).toFixed(1)}% of Euler VaR · ${Number(topRisk.invested_weight_pct || 0).toFixed(1)}% weight` : 'Live risk map still loading';

        const sentenceParts = [];
        if (p1m != null && excess != null) sentenceParts.push(`Over the last month, the portfolio returned ${fmtPct(p1m)} and ${excess >= 0 ? 'outperformed' : 'underperformed'} the S&P 500 by ${Math.abs(excess).toFixed(2)}pp.`);
        if (contributor) sentenceParts.push(`${contributor.symbol} was the largest positive contributor at ${fmtPp(contributor.contribution_pp)}${detractor ? `, while ${detractor.symbol} detracted ${fmtPp(detractor.contribution_pp)}` : ''}.`);
        if (currentDD != null) sentenceParts.push(Math.abs(currentDD) < 0.05 ? 'The portfolio is currently at its high-water mark.' : `It is currently ${Math.abs(currentDD).toFixed(2)}% below its latest high-water mark.`);
        if (topRisk) sentenceParts.push(`Risk is led by ${topRisk.ticker}; the largest five holdings represent ${Number(concentration.top_5_invested_weight_pct || 0).toFixed(1)}% of invested capital.`);
        summary.textContent = sentenceParts.length ? sentenceParts.join(' ') : 'Live portfolio data is still loading.';
        document.getElementById('insights-status').textContent = riskAnalyticsData ? 'Current read · trailing 1M performance + live invested-book risk.' : 'Current read · trailing 1M performance loaded; live risk map is still calculating.';

        const observations = [];
        if (excess != null) {
            if (excess <= -2) observations.push({type:'warning', title:'Relative performance', text:`The portfolio trails the S&P 500 by ${Math.abs(excess).toFixed(2)}pp over the last month. Check whether the shortfall is concentrated in one holding or broad-based.`});
            else if (excess >= 2) observations.push({type:'positive', title:'Relative performance', text:`The portfolio leads the S&P 500 by ${excess.toFixed(2)}pp over the last month. Attribution shows ${contributor?.symbol || 'the leading positions'} as the main recent driver.`});
            else observations.push({type:'neutral', title:'Relative performance', text:`One-month active return is ${excess >= 0 ? '+' : ''}${excess.toFixed(2)}pp versus the S&P 500 — close enough that stock-level attribution matters more than the headline spread.`});
        }
        if (currentDD != null) {
            if (currentDD <= -5) observations.push({type:'risk', title:'Drawdown state', text:`The portfolio is ${Math.abs(currentDD).toFixed(2)}% below its latest peak. This is large enough to review whether the drawdown is consistent with the intended risk budget.`});
            else if (currentDD <= -2) observations.push({type:'warning', title:'Drawdown state', text:`Current drawdown is ${Math.abs(currentDD).toFixed(2)}%. The portfolio remains below its recent high but well inside the maximum historical drawdown shown above.`});
            else observations.push({type:'positive', title:'Drawdown state', text:`Current drawdown is only ${Math.abs(currentDD).toFixed(2)}%, leaving the portfolio close to its recent high-water mark.`});
        }
        if (riskAnalyticsData) {
            const top5 = Number(concentration.top_5_invested_weight_pct || 0);
            const effective = Number(concentration.effective_holdings || 0);
            const actual = Number(riskPortfolio.holding_count || 0);
            const ratio = actual > 0 ? effective / actual : 1;
            if (top5 >= 75 || ratio <= .65) observations.push({type:'warning', title:'Capital concentration', text:`The top five holdings are ${top5.toFixed(1)}% of invested capital and ${actual} holdings behave like roughly ${effective.toFixed(1)} equally weighted positions. Capital is meaningfully concentrated.`});
            else observations.push({type:'positive', title:'Capital concentration', text:`Top-five concentration is ${top5.toFixed(1)}% and effective holdings are ${effective.toFixed(1)} versus ${actual} actual positions, indicating a reasonably distributed invested book.`});

            const gap = concentration.largest_risk_weight_gap;
            if (gap) {
                const mismatch = Number(gap.risk_minus_weight_pp || 0);
                observations.push({type:Math.abs(mismatch) >= 5 ? 'warning' : 'neutral', title:'Risk vs capital', text:`${gap.ticker} has the largest risk/weight gap: ${Number(gap.contribution_pct || 0).toFixed(1)}% of Euler VaR versus ${Number(gap.invested_weight_pct || 0).toFixed(1)}% of invested capital (${mismatch >= 0 ? '+' : ''}${mismatch.toFixed(1)}pp).`});
            }
            const avgCorr = Number(concentration.weighted_average_correlation || 0);
            observations.push({type:avgCorr >= .6 ? 'warning' : avgCorr <= .3 ? 'positive' : 'neutral', title:'Diversification structure', text:`Capital-weighted average pairwise correlation is ${avgCorr.toFixed(2)} and the model estimates a ${Number(riskAttribution.diversification_pct || 0).toFixed(1)}% VaR diversification benefit.`});
        }

        const priority = {risk:0, warning:1, neutral:2, positive:3};
        observations.sort((a,b)=>(priority[a.type] ?? 9)-(priority[b.type] ?? 9));
        const shown = observations.slice(0,3);
        document.getElementById('insights-priority').innerHTML = shown.length ? shown.map(item => { const tone=insightTone(item.type); return `<div class="p-4 flex gap-3"><span class="mt-1.5 w-2 h-2 rounded-full shrink-0 ${tone.dot}"></span><div class="min-w-0"><div class="flex items-center gap-2 flex-wrap"><p class="text-xs font-black text-gray-900">${item.title}</p><span class="text-[9px] font-black uppercase tracking-wider rounded-full border px-2 py-0.5 ${tone.badge}">${tone.label}</span></div><p class="text-xs text-gray-500 leading-relaxed mt-1">${item.text}</p></div></div>`; }).join('') : '<div class="p-4 text-sm text-gray-400">Waiting for enough data to generate observations.</div>';

        const decision = latestPortfolioDecision();
        const decisionEl = document.getElementById('insights-decision');
        if (!decision) {
            decisionEl.innerHTML = '<p>No effective portfolio transactions are available yet.</p>';
        } else {
            decisionEl.innerHTML = `<div class="flex items-center justify-between gap-3"><p class="font-black text-gray-900">${decision.title}</p><span class="text-[10px] font-black text-gray-400">${prettyDate(decision.date)}</span></div><p class="text-xs text-gray-500 leading-relaxed mt-2">${decision.text}</p>${decision.rationale ? `<button type="button" onclick="openJournalModal('${decision.rationale.id}')" class="mt-3 text-xs font-black text-blue-700 hover:text-blue-900">Open linked rationale →</button>` : '<p class="text-[10px] text-gray-400 mt-3">No published journal rationale linked to this transaction.</p>'}`;
        }
    }

'''

anchor = '    function openJournalModal(entryId) {'
if anchor not in text:
    raise SystemExit('Automated insights function anchor missing')
text = text.replace(anchor, functions + anchor, 1)

path.write_text(text)
