from pathlib import Path

path = Path('sethiportfolio-admin.html')
text = path.read_text()

section = r'''
            <section class="card mt-6 overflow-hidden">
                <div class="p-5 md:p-6 border-b border-gray-100 flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-[0.14em] text-fuchsia-700">Investment intelligence</p>
                        <h2 class="text-xl font-black mt-1">Thesis Tracking</h2>
                        <p class="text-xs text-gray-500 mt-1 max-w-3xl">Maintain the structured investment case separately from the journal. Core thesis fields can be edited; conviction and status changes over time should be appended as dated reviews.</p>
                    </div>
                    <span class="text-[9px] font-black uppercase tracking-wider rounded-full bg-fuchsia-50 text-fuchsia-700 border border-fuchsia-100 px-2 py-1 self-start">Phase 3 · append-only reviews</span>
                </div>

                <div class="grid xl:grid-cols-2 gap-0 xl:divide-x divide-gray-100">
                    <form id="thesis-form" class="p-5 md:p-6 space-y-4">
                        <div class="flex items-start justify-between gap-3"><div><p class="text-[10px] font-black uppercase tracking-wider text-fuchsia-700">Thesis record</p><h3 class="text-lg font-black mt-1">Create or Edit Investment Thesis</h3></div><button id="thesis-cancel-edit" type="button" class="hidden text-[11px] font-black text-gray-500 hover:text-gray-900">Cancel edit</button></div>
                        <div class="grid sm:grid-cols-2 gap-4"><div><label class="label" for="thesis-symbol">Holding</label><select id="thesis-symbol" class="field" required><option value="">Select live holding</option></select></div><div><label class="label" for="thesis-opened-date">Opened date</label><input id="thesis-opened-date" type="date" class="field" required></div></div>
                        <div><label class="label" for="thesis-title">Thesis title</label><input id="thesis-title" class="field" placeholder="Short statement of the investment case" required></div>
                        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3"><div><label class="label" for="thesis-status-field">Opening status</label><select id="thesis-status-field" class="field"><option value="ACTIVE">Active</option><option value="WATCH">Watch</option><option value="UNDER_REVIEW">Under Review</option><option value="INVALIDATED">Invalidated</option><option value="CLOSED">Closed</option></select></div><div><label class="label" for="thesis-conviction">Opening conviction</label><select id="thesis-conviction" class="field"><option value="1">1 / 5</option><option value="2">2 / 5</option><option value="3" selected>3 / 5</option><option value="4">4 / 5</option><option value="5">5 / 5</option></select></div><div><label class="label" for="thesis-target-price">Target price</label><input id="thesis-target-price" type="number" min="0" step="0.0001" class="field" placeholder="Optional"></div><div><label class="label" for="thesis-target-currency">Target currency</label><select id="thesis-target-currency" class="field"><option>GBP</option><option>USD</option><option>EUR</option></select></div></div>
                        <div><label class="label" for="thesis-core">Core thesis</label><textarea id="thesis-core" rows="5" class="field resize-y" placeholder="Why should this investment create value from the price paid?" required></textarea></div>
                        <div class="grid md:grid-cols-2 gap-4"><div><label class="label" for="thesis-catalysts">Catalysts</label><textarea id="thesis-catalysts" rows="4" class="field resize-y" placeholder="Events or developments that could unlock value"></textarea></div><div><label class="label" for="thesis-risks">Key risks</label><textarea id="thesis-risks" rows="4" class="field resize-y" placeholder="The main ways the investment case could disappoint"></textarea></div></div>
                        <div><label class="label" for="thesis-invalidation">Invalidation condition</label><textarea id="thesis-invalidation" rows="4" class="field resize-y" placeholder="What observable evidence would make the original thesis no longer defensible?" required></textarea></div>
                        <div class="grid sm:grid-cols-2 gap-4 items-end"><div><label class="label" for="thesis-next-review">Next review date</label><input id="thesis-next-review" type="date" class="field"></div><label class="flex items-center gap-3 rounded-xl bg-gray-50 border border-gray-200 px-4 py-3 cursor-pointer"><input id="thesis-published" type="checkbox" checked class="w-4 h-4"><span><span class="block text-xs font-black">Publish thesis</span><span class="block text-[10px] text-gray-500 mt-0.5">Untick to keep it private.</span></span></label></div>
                        <div class="rounded-xl bg-fuchsia-50 border border-fuchsia-100 p-3 text-[11px] text-fuchsia-900 leading-relaxed">When editing an existing thesis, opening status and opening conviction remain the historical starting point. Use the review form to record how your current view changed.</div>
                        <button id="thesis-submit" type="submit" class="w-full rounded-xl bg-fuchsia-700 text-white px-4 py-3 text-sm font-black hover:bg-fuchsia-800 transition">Save thesis</button>
                    </form>

                    <form id="thesis-review-form" class="p-5 md:p-6 space-y-4 bg-gray-50/35">
                        <div><p class="text-[10px] font-black uppercase tracking-wider text-blue-700">Dated review</p><h3 class="text-lg font-black mt-1">Update Conviction Without Rewriting History</h3><p class="text-xs text-gray-500 mt-1">Every submission becomes a permanent review entry beneath the original thesis.</p></div>
                        <div><label class="label" for="thesis-review-id">Thesis</label><select id="thesis-review-id" class="field"><option value="">Select thesis to review</option></select></div>
                        <div class="grid sm:grid-cols-2 gap-4"><div><label class="label" for="thesis-review-date">Review date</label><input id="thesis-review-date" type="date" class="field" required></div><div><label class="label" for="thesis-review-next">Next review date</label><input id="thesis-review-next" type="date" class="field"></div></div>
                        <div class="grid sm:grid-cols-2 gap-4"><div><label class="label" for="thesis-review-status">Current status</label><select id="thesis-review-status" class="field"><option value="ACTIVE">Active</option><option value="WATCH">Watch</option><option value="UNDER_REVIEW">Under Review</option><option value="INVALIDATED">Invalidated</option><option value="CLOSED">Closed</option></select></div><div><label class="label" for="thesis-review-conviction">Current conviction</label><select id="thesis-review-conviction" class="field"><option value="1">1 / 5</option><option value="2">2 / 5</option><option value="3">3 / 5</option><option value="4">4 / 5</option><option value="5">5 / 5</option></select></div></div>
                        <div><label class="label" for="thesis-review-summary">What changed?</label><textarea id="thesis-review-summary" rows="4" class="field resize-y" placeholder="Concise judgement: what changed in the case, and why does conviction/status move or stay unchanged?" required></textarea></div>
                        <div><label class="label" for="thesis-review-evidence">Evidence / observations</label><textarea id="thesis-review-evidence" rows="5" class="field resize-y" placeholder="Results, valuation change, competitive evidence, management execution, industry data or other observations"></textarea></div>
                        <label class="flex items-center gap-3 rounded-xl bg-white border border-gray-200 px-4 py-3 cursor-pointer"><input id="thesis-review-published" type="checkbox" checked class="w-4 h-4"><span><span class="block text-xs font-black">Publish review</span><span class="block text-[10px] text-gray-500 mt-0.5">A private review still remains in the admin history.</span></span></label>
                        <button id="thesis-review-submit" type="submit" class="w-full rounded-xl bg-blue-700 text-white px-4 py-3 text-sm font-black hover:bg-blue-800 transition">Append thesis review</button>
                    </form>
                </div>

                <div class="border-t border-gray-100">
                    <div class="p-5 border-b border-gray-100 flex items-center justify-between gap-4"><div><p class="text-[10px] font-black uppercase tracking-[0.14em] text-gray-400">Thesis book</p><h3 class="text-lg font-black mt-1">Manage Structured Theses</h3><p class="text-xs text-gray-500 mt-1">Closing or invalidating a thesis should normally be done through a dated review rather than deletion.</p></div><span id="thesis-count" class="text-[10px] font-black uppercase tracking-wider text-gray-400">0 theses</span></div>
                    <div id="thesis-manager" class="divide-y divide-gray-100"><div class="p-6 text-sm text-gray-400">Loading theses…</div></div>
                </div>
            </section>

'''

anchor = '            <div id="allocation-correction-modal"'
if anchor not in text:
    raise SystemExit('Thesis admin section anchor not found')
text = text.replace(anchor, section + anchor, 1)

replacements = [
    (
        '    let liveJournal = [];\n    let editingJournalId = null;',
        '    let liveJournal = [];\n    let liveTheses = [];\n    let liveSnapshot = null;\n    let editingJournalId = null;\n    let editingThesisId = null;',
        'admin state'
    ),
    (
        '        liveJournal = [];\n        editingJournalId = null;',
        '        liveJournal = [];\n        liveTheses = [];\n        liveSnapshot = null;\n        editingJournalId = null;\n        editingThesisId = null;',
        'logout state'
    ),
    (
        '            const [portfolioResponse, txnData, journalData] = await Promise.all([\n                fetch(`${API}/${PORTFOLIO}`),\n                apiFetch(`/admin/${PORTFOLIO}/ledger`),\n                apiFetch(`/admin/${PORTFOLIO}/journal`)\n            ]);',
        '            const [portfolioResponse, txnData, journalData, thesisData] = await Promise.all([\n                fetch(`${API}/${PORTFOLIO}`),\n                apiFetch(`/admin/${PORTFOLIO}/ledger`),\n                apiFetch(`/admin/${PORTFOLIO}/journal`),\n                apiFetch(`/admin/${PORTFOLIO}/theses`)\n            ]);',
        'refresh requests'
    ),
    (
        '            const snapshot = portfolio.snapshot || portfolio;\n            liveTransactions = txnData.transactions || [];\n            effectiveTransactions = txnData.effective_transactions || [];\n            liveJournal = journalData.journal || [];',
        '            const snapshot = portfolio.snapshot || portfolio;\n            liveSnapshot = snapshot;\n            liveTransactions = txnData.transactions || [];\n            effectiveTransactions = txnData.effective_transactions || [];\n            liveJournal = journalData.journal || [];\n            liveTheses = thesisData.theses || [];',
        'refresh state'
    ),
    (
        '            renderTransactionOptions();\n            renderRecentTransactions();\n            renderJournalManager();',
        '            renderTransactionOptions();\n            renderRecentTransactions();\n            renderJournalManager();\n            renderThesisSymbolOptions();\n            renderThesisReviewOptions();\n            renderThesisManager();',
        'refresh rendering'
    ),
]

for old, new, label in replacements:
    if old not in text:
        raise SystemExit(f'Missing thesis admin anchor: {label}')
    text = text.replace(old, new, 1)

functions = r'''
    function thesisAdminStatusLabel(status) {
        return String(status || 'ACTIVE').replaceAll('_',' ').toLowerCase().replace(/\b\w/g, c=>c.toUpperCase());
    }

    function resetThesisForm() {
        editingThesisId = null;
        el('thesis-form').reset();
        el('thesis-conviction').value = '3';
        el('thesis-status-field').value = 'ACTIVE';
        el('thesis-published').checked = true;
        el('thesis-opened-date').value = new Date().toISOString().slice(0,10);
        el('thesis-submit').textContent = 'Save thesis';
        el('thesis-cancel-edit').classList.add('hidden');
        renderThesisSymbolOptions();
    }

    function renderThesisSymbolOptions() {
        const select = el('thesis-symbol');
        const current = select.value;
        select.replaceChildren(new Option('Select live holding', ''));
        (liveSnapshot?.holdings || []).forEach(holding => {
            const option = new Option(`${holding.symbol} · ${holding.name}`, holding.symbol);
            option.dataset.currency = holding.currency || 'GBP';
            select.appendChild(option);
        });
        if ([...select.options].some(option => option.value === current)) select.value = current;
        if (select.value) {
            const holding=(liveSnapshot?.holdings||[]).find(row=>row.symbol===select.value);
            if(holding?.currency && [...el('thesis-target-currency').options].some(o=>o.value===holding.currency)) el('thesis-target-currency').value=holding.currency;
        }
    }

    function thesisPayload() {
        const targetRaw = el('thesis-target-price').value.trim();
        return {
            symbol:el('thesis-symbol').value,
            title:el('thesis-title').value.trim(),
            core_thesis:el('thesis-core').value.trim(),
            catalysts:el('thesis-catalysts').value.trim(),
            key_risks:el('thesis-risks').value.trim(),
            invalidation_condition:el('thesis-invalidation').value.trim(),
            status:el('thesis-status-field').value,
            conviction:Number(el('thesis-conviction').value),
            target_price:targetRaw === '' ? null : Number(targetRaw),
            target_currency:el('thesis-target-currency').value,
            opened_date:el('thesis-opened-date').value,
            next_review_date:el('thesis-next-review').value || null,
            is_published:el('thesis-published').checked
        };
    }

    function editThesis(id) {
        const thesis=liveTheses.find(row=>row.id===id); if(!thesis) return;
        editingThesisId=id;
        const instrument=thesis.instruments||{};
        renderThesisSymbolOptions();
        el('thesis-symbol').value=instrument.symbol||'';
        el('thesis-title').value=thesis.title||'';
        el('thesis-core').value=thesis.core_thesis||'';
        el('thesis-catalysts').value=thesis.catalysts||'';
        el('thesis-risks').value=thesis.key_risks||'';
        el('thesis-invalidation').value=thesis.invalidation_condition||'';
        el('thesis-status-field').value=thesis.status||'ACTIVE';
        el('thesis-conviction').value=String(thesis.conviction||3);
        el('thesis-target-price').value=thesis.target_price==null?'':thesis.target_price;
        el('thesis-target-currency').value=thesis.target_currency||instrument.currency||'GBP';
        el('thesis-opened-date').value=thesis.opened_date||'';
        el('thesis-next-review').value=thesis.next_review_date||'';
        el('thesis-published').checked=!!thesis.is_published;
        el('thesis-submit').textContent='Update thesis';
        el('thesis-cancel-edit').classList.remove('hidden');
        el('thesis-title').scrollIntoView({behavior:'smooth',block:'center'});
    }

    function renderThesisReviewOptions() {
        const select=el('thesis-review-id');
        const current=select.value;
        select.replaceChildren(new Option('Select thesis to review',''));
        liveTheses.forEach(thesis=>{
            const instrument=thesis.instruments||{};
            const label=`${instrument.symbol||'—'} · ${thesis.title} · ${thesisAdminStatusLabel(thesis.effective_status||thesis.status)} · ${thesis.effective_conviction||thesis.conviction}/5`;
            select.appendChild(new Option(label,thesis.id));
        });
        if ([...select.options].some(option=>option.value===current)) select.value=current;
        if(select.value) primeThesisReview();
    }

    function primeThesisReview() {
        const thesis=liveTheses.find(row=>row.id===el('thesis-review-id').value);
        if(!thesis) return;
        el('thesis-review-status').value=thesis.effective_status||thesis.status||'ACTIVE';
        el('thesis-review-conviction').value=String(thesis.effective_conviction||thesis.conviction||3);
        el('thesis-review-next').value=thesis.effective_next_review_date||thesis.next_review_date||'';
    }

    function resetThesisReviewForm() {
        el('thesis-review-form').reset();
        el('thesis-review-date').value=new Date().toISOString().slice(0,10);
        el('thesis-review-published').checked=true;
        renderThesisReviewOptions();
    }

    function renderThesisManager() {
        const container=el('thesis-manager');
        container.replaceChildren();
        el('thesis-count').textContent=`${liveTheses.length} ${liveTheses.length===1?'thesis':'theses'}`;
        if(!liveTheses.length){const empty=document.createElement('div');empty.className='p-6 text-sm text-gray-400';empty.textContent='No structured theses recorded yet.';container.appendChild(empty);return;}
        liveTheses.forEach(thesis=>{
            const instrument=thesis.instruments||{};
            const row=document.createElement('div');row.className='p-4 md:px-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3';
            const left=document.createElement('div');left.className='min-w-0';
            const top=document.createElement('div');top.className='flex items-center gap-2 flex-wrap';
            const symbol=document.createElement('span');symbol.className='text-sm font-black';symbol.textContent=instrument.symbol||'—';
            const title=document.createElement('span');title.className='text-sm font-bold text-gray-700';title.textContent=thesis.title;
            const status=document.createElement('span');status.className='text-[9px] font-black uppercase tracking-wider rounded-full px-2 py-0.5 bg-fuchsia-50 text-fuchsia-700';status.textContent=thesisAdminStatusLabel(thesis.effective_status||thesis.status);
            top.append(symbol,title,status);
            const next=thesis.effective_next_review_date||thesis.next_review_date;
            const detail=document.createElement('p');detail.className='text-xs text-gray-500 mt-1';detail.textContent=`Conviction ${thesis.effective_conviction||thesis.conviction}/5 · ${thesis.is_published?'Published':'Private'} · Opened ${prettyDate(thesis.opened_date)}${next?' · Next review '+prettyDate(next):''} · ${(thesis.updates||[]).length} reviews`;
            left.append(top,detail);
            const actions=document.createElement('div');actions.className='flex gap-3 shrink-0';
            const review=document.createElement('button');review.type='button';review.className='text-[11px] font-black text-blue-700 hover:text-blue-900';review.textContent='Review';review.onclick=()=>{el('thesis-review-id').value=thesis.id;primeThesisReview();el('thesis-review-summary').scrollIntoView({behavior:'smooth',block:'center'});};
            const edit=document.createElement('button');edit.type='button';edit.className='text-[11px] font-black text-fuchsia-700 hover:text-fuchsia-900';edit.textContent='Edit core';edit.onclick=()=>editThesis(thesis.id);
            actions.append(review,edit);row.append(left,actions);container.appendChild(row);
        });
    }

    el('thesis-symbol').addEventListener('change',()=>{
        const holding=(liveSnapshot?.holdings||[]).find(row=>row.symbol===el('thesis-symbol').value);
        if(holding?.currency && [...el('thesis-target-currency').options].some(option=>option.value===holding.currency)) el('thesis-target-currency').value=holding.currency;
    });
    el('thesis-cancel-edit').addEventListener('click',resetThesisForm);
    el('thesis-review-id').addEventListener('change',primeThesisReview);

    el('thesis-form').addEventListener('submit',async event=>{
        event.preventDefault();
        const payload=thesisPayload();
        const verb=editingThesisId?'Update':'Create';
        if(!confirm(`${verb} the structured thesis for ${payload.symbol}?\n\nCurrent-view changes after opening should be recorded through dated reviews.`)) return;
        const btn=el('thesis-submit');btn.disabled=true;btn.textContent=editingThesisId?'Updating thesis…':'Saving thesis…';
        try{
            const path=editingThesisId?`/admin/${PORTFOLIO}/theses/${editingThesisId}`:`/admin/${PORTFOLIO}/theses`;
            await apiFetch(path,{method:editingThesisId?'PATCH':'POST',body:JSON.stringify(payload)});
            setMessage('global-message',`${payload.symbol} thesis ${editingThesisId?'updated':'created'} successfully.`,'success');
            resetThesisForm();
            await refreshAdminData();
        }catch(error){setMessage('global-message',error.message,'error');}
        finally{btn.disabled=false;btn.textContent=editingThesisId?'Update thesis':'Save thesis';}
    });

    el('thesis-review-form').addEventListener('submit',async event=>{
        event.preventDefault();
        const thesisId=el('thesis-review-id').value;
        const thesis=liveTheses.find(row=>row.id===thesisId);
        if(!thesis){setMessage('global-message','Select a thesis to review.','error');return;}
        const payload={
            effective_date:el('thesis-review-date').value,
            status:el('thesis-review-status').value,
            conviction:Number(el('thesis-review-conviction').value),
            summary:el('thesis-review-summary').value.trim(),
            evidence:el('thesis-review-evidence').value.trim(),
            next_review_date:el('thesis-review-next').value||null,
            is_published:el('thesis-review-published').checked
        };
        const symbol=(thesis.instruments||{}).symbol||'thesis';
        if(!confirm(`Append a permanent ${symbol} thesis review dated ${prettyDate(payload.effective_date)}?\n\nStatus: ${thesisAdminStatusLabel(payload.status)} · Conviction: ${payload.conviction}/5`)) return;
        const btn=el('thesis-review-submit');btn.disabled=true;btn.textContent='Appending review…';
        try{
            await apiFetch(`/admin/${PORTFOLIO}/theses/${thesisId}/updates`,{method:'POST',body:JSON.stringify(payload)});
            setMessage('global-message',`${symbol} thesis review appended. The previous view remains in history.`,'success');
            resetThesisReviewForm();
            await refreshAdminData();
        }catch(error){setMessage('global-message',error.message,'error');}
        finally{btn.disabled=false;btn.textContent='Append thesis review';}
    });

    resetThesisForm();
    resetThesisReviewForm();

'''

anchor = '    function allocationLegs(decisionId) {'
if anchor not in text:
    raise SystemExit('Thesis admin function insertion anchor not found')
text = text.replace(anchor, functions + anchor, 1)

path.write_text(text)
