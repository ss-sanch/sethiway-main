from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

replacements = [
    (
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #risk, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        '#performance, #attribution, #benchmark, #drawdown, #holdings, #risk, #analytics, #theses, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
        'scroll margin'
    ),
    (
        '                <a href="#analytics" class="hover:text-blue-600">Analytics</a>\n                <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>',
        '                <a href="#analytics" class="hover:text-blue-600">Analytics</a>\n                <a href="#theses" class="hover:text-blue-600">Theses</a>\n                <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>',
        'navigation'
    ),
    (
        '    let riskAnalyticsData = null;\n    let journalEntries = [];',
        '    let riskAnalyticsData = null;\n    let thesisData = [];\n    let latestSnapshot = null;\n    let journalEntries = [];',
        'state'
    ),
    (
        '            attributionData = attributionPayload || { periods: {} };\n            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;',
        '            attributionData = attributionPayload || { periods: {} };\n            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;\n            latestSnapshot = snapshot;',
        'snapshot state'
    ),
    (
        '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics();\n            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions);',
        '            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); renderAnalytics();\n            if (thesisData.length) renderTheses(thesisData);\n            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions);',
        'rerender theses'
    ),
    (
        '    loadPortfolio();\n    loadRiskAnalytics();',
        '    loadPortfolio();\n    loadRiskAnalytics();\n    loadTheses();',
        'load theses'
    ),
]

for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing public thesis anchor: {label}')
    text = text.replace(old, new, 1)

section = r'''
            <!-- THESIS MONITOR -->
            <div id="theses" class="section-intro"><h2>Thesis Monitor</h2><div class="section-overview"><strong>Is the investment case still intact?</strong>Track the original case, conviction, catalysts, risks and explicit invalidation conditions for each investment. Dated reviews preserve how the thesis changed after capital was committed.</div></div>
            <section id="thesis-monitor-card" class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4 mb-5">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-fuchsia-700 mb-1">Investment Intelligence</p>
                        <h3 class="text-xl md:text-2xl font-black text-gray-900">What would make us change our mind?</h3>
                        <p id="thesis-status" class="text-sm text-gray-500 mt-1">Loading published investment theses…</p>
                    </div>
                    <a href="sethiportfolio-admin.html" class="text-xs font-black text-fuchsia-800 bg-fuchsia-50 border border-fuchsia-100 rounded-lg px-4 py-2.5 hover:bg-fuchsia-100 hover:border-fuchsia-200 transition shrink-0">Manage theses →</a>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
                    <div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Live Theses</p><p id="thesis-live-count" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-gray-400 mt-1">Active, watch or under review</p></div>
                    <div class="rounded-xl bg-fuchsia-50/60 border border-fuchsia-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-fuchsia-700">Avg Conviction</p><p id="thesis-average-conviction" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-fuchsia-700/70 mt-1">Across live theses · /5</p></div>
                    <div class="rounded-xl bg-amber-50/60 border border-amber-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-amber-700">Reviews Due</p><p id="thesis-reviews-due" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-amber-700/70 mt-1">Review date reached or passed</p></div>
                    <div class="rounded-xl bg-blue-50/60 border border-blue-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-blue-700">Under Review</p><p id="thesis-under-review" class="text-2xl font-black mt-1">—</p><p class="text-[9px] text-blue-700/70 mt-1">Cases requiring fresh judgement</p></div>
                </div>

                <div id="thesis-list" class="grid grid-cols-1 xl:grid-cols-2 gap-4">
                    <div class="xl:col-span-2 rounded-xl border border-dashed border-gray-200 p-8 text-center text-sm text-gray-400">Loading thesis monitor…</div>
                </div>

                <div class="mt-4 rounded-lg bg-fuchsia-50/50 border border-fuchsia-100 px-4 py-3 text-[11px] leading-relaxed text-fuchsia-900"><strong>Discipline:</strong> conviction and status changes are stored as dated reviews. The original thesis remains visible so later outcomes can be assessed against what was actually believed at the time.</div>
            </section>

'''

anchor = '            <!-- JOURNAL + CHANGE LOG -->'
if anchor not in text:
    raise SystemExit('Thesis section insertion anchor not found')
text = text.replace(anchor, section + anchor, 1)

functions = r'''
    function thesisEscape(value) {
        return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
    }

    function thesisStatusMeta(status) {
        const key = String(status || 'ACTIVE').toUpperCase();
        const map = {
            ACTIVE:{label:'Active', cls:'bg-emerald-50 text-emerald-700 border-emerald-100'},
            WATCH:{label:'Watch', cls:'bg-amber-50 text-amber-700 border-amber-100'},
            UNDER_REVIEW:{label:'Under Review', cls:'bg-blue-50 text-blue-700 border-blue-100'},
            INVALIDATED:{label:'Invalidated', cls:'bg-red-50 text-red-700 border-red-100'},
            CLOSED:{label:'Closed', cls:'bg-gray-100 text-gray-600 border-gray-200'}
        };
        return map[key] || map.ACTIVE;
    }

    function thesisDate(value) {
        return value ? prettyDate(value) : 'Not scheduled';
    }

    function renderTheses(theses) {
        thesisData = Array.isArray(theses) ? theses : [];
        const list = document.getElementById('thesis-list');
        const liveStatuses = new Set(['ACTIVE','WATCH','UNDER_REVIEW']);
        const live = thesisData.filter(row => liveStatuses.has(String(row.effective_status || row.status || '').toUpperCase()));
        const avg = live.length ? live.reduce((sum,row)=>sum + Number(row.effective_conviction || row.conviction || 0),0) / live.length : 0;
        const today = new Date(); today.setHours(0,0,0,0);
        const due = live.filter(row => {
            const value = row.effective_next_review_date || row.next_review_date;
            if (!value) return false;
            const d = new Date(`${value}T00:00:00`);
            return Number.isFinite(d.getTime()) && d <= today;
        });
        const reviewing = live.filter(row => String(row.effective_status || '').toUpperCase() === 'UNDER_REVIEW');

        document.getElementById('thesis-live-count').textContent = String(live.length);
        document.getElementById('thesis-average-conviction').textContent = live.length ? avg.toFixed(1) : '—';
        document.getElementById('thesis-reviews-due').textContent = String(due.length);
        document.getElementById('thesis-under-review').textContent = String(reviewing.length);
        document.getElementById('thesis-status').textContent = thesisData.length
            ? `${thesisData.length} published ${thesisData.length === 1 ? 'thesis' : 'theses'} · ${live.length} currently live · review history is append-only.`
            : 'No published structured theses yet. Existing journal entries remain unchanged.';

        if (!thesisData.length) {
            list.innerHTML = '<div class="xl:col-span-2 rounded-xl border border-dashed border-gray-200 p-8 text-center"><p class="font-black text-gray-700">No structured theses published yet</p><p class="text-sm text-gray-400 mt-1">Use Portfolio Admin to create the first holding-level thesis. The Investment Journal continues to work independently.</p></div>';
            return;
        }

        const holdingMap = new Map((latestSnapshot?.holdings || []).map(row => [String(row.symbol || '').toUpperCase(), row]));
        const rank = {UNDER_REVIEW:0, WATCH:1, ACTIVE:2, INVALIDATED:3, CLOSED:4};
        const sorted = [...thesisData].sort((a,b) => (rank[String(a.effective_status || a.status)] ?? 9) - (rank[String(b.effective_status || b.status)] ?? 9));
        list.innerHTML = sorted.map(row => {
            const instrument = row.instruments || {};
            const symbol = String(instrument.symbol || '—').toUpperCase();
            const name = thesisEscape(instrument.name || symbol);
            const statusKey = String(row.effective_status || row.status || 'ACTIVE').toUpperCase();
            const status = thesisStatusMeta(statusKey);
            const conviction = Math.max(1, Math.min(5, Number(row.effective_conviction || row.conviction || 3)));
            const convictionMove = Number(row.conviction_change || 0);
            const convictionText = `${'●'.repeat(conviction)}${'○'.repeat(5-conviction)}`;
            const holding = holdingMap.get(symbol);
            const target = row.target_price == null ? null : Number(row.target_price);
            const currency = String(row.target_currency || instrument.currency || holding?.currency || 'GBP').toUpperCase();
            const current = holding && String(holding.currency || '').toUpperCase() === currency ? Number(holding.current_price) : null;
            const upside = target != null && Number.isFinite(current) && current > 0 ? (target/current - 1) * 100 : null;
            const nextReview = row.effective_next_review_date || row.next_review_date;
            const dueReview = nextReview && new Date(`${nextReview}T00:00:00`) <= today && liveStatuses.has(statusKey);
            const updates = Array.isArray(row.updates) ? row.updates : [];
            const latest = row.latest_update || updates[0];
            const moveLabel = convictionMove === 0 ? 'unchanged' : `${convictionMove > 0 ? '+' : ''}${convictionMove} since opening`;
            const targetLine = target == null ? 'No explicit target' : `${thesisEscape(fmtMoney(target, currency))}${upside == null ? '' : ` · ${upside >= 0 ? '+' : ''}${upside.toFixed(1)}% vs current`}`;
            const history = updates.length ? `<details class="mt-4 border-t border-gray-100 pt-3"><summary class="cursor-pointer text-xs font-black text-fuchsia-700">Review history · ${updates.length} ${updates.length === 1 ? 'entry' : 'entries'}</summary><div class="mt-3 space-y-2">${updates.map(update => { const meta=thesisStatusMeta(update.status); return `<div class="rounded-lg bg-gray-50 border border-gray-100 px-3 py-2"><div class="flex flex-wrap items-center gap-2"><span class="text-[10px] font-black text-gray-400">${thesisEscape(thesisDate(update.effective_date))}</span><span class="text-[9px] font-black uppercase rounded-full border px-2 py-0.5 ${meta.cls}">${meta.label}</span><span class="text-[10px] font-black text-gray-600">Conviction ${Number(update.conviction)}/5</span></div><p class="text-xs text-gray-700 mt-1.5 leading-relaxed">${thesisEscape(update.summary)}</p>${update.evidence ? `<p class="text-[11px] text-gray-500 mt-1 leading-relaxed">${thesisEscape(update.evidence)}</p>` : ''}</div>`;}).join('')}</div></details>` : '';
            return `<article class="rounded-xl border ${statusKey === 'UNDER_REVIEW' ? 'border-blue-200' : statusKey === 'INVALIDATED' ? 'border-red-200' : 'border-gray-200'} p-5 hover:shadow-sm transition min-w-0">
                <div class="flex items-start justify-between gap-4">
                    <div class="min-w-0"><div class="flex flex-wrap items-center gap-2"><a href="sethistock.html?ticker=${encodeURIComponent(symbol)}&source=portfolio-thesis" class="font-black text-lg text-gray-900 hover:text-blue-700">${thesisEscape(symbol)} ↗</a><span class="text-[9px] font-black uppercase rounded-full border px-2 py-0.5 ${status.cls}">${status.label}</span></div><p class="text-[10px] text-gray-400 mt-0.5 truncate">${name}</p><h4 class="text-base font-black mt-2">${thesisEscape(row.title)}</h4></div>
                    <div class="text-right shrink-0"><p class="text-[9px] uppercase tracking-wider font-black text-gray-400">Conviction</p><p class="font-black text-fuchsia-700 tracking-wider mt-1" title="${conviction}/5">${convictionText}</p><p class="text-[9px] text-gray-400 mt-0.5">${moveLabel}</p></div>
                </div>
                <div class="mt-4 rounded-lg bg-gray-50 border border-gray-100 px-4 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Core Thesis</p><p class="text-sm text-gray-700 leading-relaxed mt-1">${thesisEscape(row.core_thesis)}</p></div>
                <div class="grid sm:grid-cols-3 gap-2 mt-3">
                    <div class="rounded-lg bg-emerald-50/60 border border-emerald-100 px-3 py-2"><p class="text-[9px] uppercase tracking-wider font-black text-emerald-700">Catalysts</p><p class="text-[11px] text-gray-700 leading-relaxed mt-1">${thesisEscape(row.catalysts || 'No explicit catalyst recorded.')}</p></div>
                    <div class="rounded-lg bg-amber-50/60 border border-amber-100 px-3 py-2"><p class="text-[9px] uppercase tracking-wider font-black text-amber-700">Key Risks</p><p class="text-[11px] text-gray-700 leading-relaxed mt-1">${thesisEscape(row.key_risks || 'No additional risk note recorded.')}</p></div>
                    <div class="rounded-lg bg-red-50/60 border border-red-100 px-3 py-2"><p class="text-[9px] uppercase tracking-wider font-black text-red-700">Invalidation</p><p class="text-[11px] text-gray-700 leading-relaxed mt-1">${thesisEscape(row.invalidation_condition)}</p></div>
                </div>
                <div class="grid sm:grid-cols-3 gap-2 mt-3 text-[11px]"><div><span class="font-black text-gray-400 uppercase tracking-wider text-[9px]">Target</span><p class="font-bold text-gray-700 mt-0.5">${targetLine}</p></div><div><span class="font-black text-gray-400 uppercase tracking-wider text-[9px]">Next Review</span><p class="font-bold mt-0.5 ${dueReview ? 'text-red-600' : 'text-gray-700'}">${thesisEscape(thesisDate(nextReview))}${dueReview ? ' · due' : ''}</p></div><div><span class="font-black text-gray-400 uppercase tracking-wider text-[9px]">Last Review</span><p class="font-bold text-gray-700 mt-0.5">${thesisEscape(thesisDate(row.last_review_date))}</p></div></div>
                ${latest ? `<div class="mt-3 rounded-lg bg-fuchsia-50/50 border border-fuchsia-100 px-3 py-2"><p class="text-[9px] uppercase tracking-wider font-black text-fuchsia-700">Latest Review</p><p class="text-xs text-gray-700 mt-1 leading-relaxed">${thesisEscape(latest.summary)}</p></div>` : ''}
                ${history}
            </article>`;
        }).join('');
    }

    async function loadTheses() {
        try {
            const response = await fetch(`${API_BASE}/${PORTFOLIO_SLUG}/theses`);
            if (!response.ok) {
                let detail = `Thesis request failed (${response.status})`;
                try { const body = await response.json(); detail = body.detail || detail; } catch (_) {}
                throw new Error(detail);
            }
            const data = await response.json();
            renderTheses(data.theses || []);
        } catch (error) {
            console.error('SethiPortfolio thesis tracking failed:', error);
            document.getElementById('thesis-status').textContent = 'Structured thesis tracking is temporarily unavailable; the rest of SethiPortfolio is unaffected.';
            document.getElementById('thesis-list').innerHTML = `<div class="xl:col-span-2 rounded-xl border border-dashed border-gray-200 p-8 text-center text-sm text-gray-400">Unable to load thesis tracking. ${thesisEscape(error.message || '')}</div>`;
        }
    }

'''

anchor = '    function openJournalModal(entryId) {'
if anchor not in text:
    raise SystemExit('Thesis function insertion anchor not found')
text = text.replace(anchor, functions + anchor, 1)

path.write_text(text)
