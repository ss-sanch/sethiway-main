from pathlib import Path

p = Path('sethiportfolio-admin.html')
s = p.read_text(encoding='utf-8')

# 1) Add paired allocation-correction modal before the existing single-trade correction modal.
modal_marker = '''            <div id="correction-modal" class="hidden fixed inset-0 z-[80] bg-gray-950/45 backdrop-blur-sm p-4 items-center justify-center">\n'''
if modal_marker not in s:
    raise SystemExit('single correction modal marker missing')
allocation_modal = '''            <div id="allocation-correction-modal" class="hidden fixed inset-0 z-[90] bg-gray-950/45 backdrop-blur-sm p-4 items-center justify-center overflow-y-auto">\n                <div class="w-full max-w-4xl rounded-2xl bg-white border border-gray-200 shadow-2xl overflow-hidden my-auto">\n                    <div class="p-5 border-b border-gray-100 flex items-start justify-between gap-4">\n                        <div><p class="text-[10px] font-black uppercase tracking-[0.14em] text-amber-700">Paired allocation correction</p><h2 id="allocation-correction-title" class="text-xl font-black mt-1">Correct Allocation</h2><p id="allocation-correction-original" class="text-xs text-gray-500 mt-1">Original allocation details.</p></div>\n                        <button type="button" onclick="closeAllocationCorrectionModal()" class="text-xl leading-none text-gray-400 hover:text-gray-900">×</button>\n                    </div>\n                    <form id="allocation-correction-form" class="p-5 space-y-5">\n                        <div class="grid md:grid-cols-[.65fr_1fr_1fr] gap-4">\n                            <div><label class="label" for="allocation-correction-date">Correct trade date</label><input id="allocation-correction-date" type="date" class="field" required><p class="text-[10px] text-gray-400 mt-1.5">Changing the date refreshes both reference prices and FX.</p></div>\n                            <div class="rounded-xl border border-red-100 bg-red-50/40 p-4 space-y-3">\n                                <div><p class="text-[9px] font-black uppercase tracking-wider text-red-700">Funding leg · SELL</p><p id="allocation-correction-funding-symbol" class="text-sm font-black mt-1">—</p><p id="allocation-correction-funding-status" class="text-[10px] font-bold text-gray-400 mt-1">Waiting for market data.</p></div>\n                                <div class="grid grid-cols-3 gap-2"><div><label class="label" for="allocation-correction-funding-qty">Quantity</label><input id="allocation-correction-funding-qty" type="number" min="0" step="0.000001" class="field" required></div><div><label class="label" for="allocation-correction-funding-price">Price</label><input id="allocation-correction-funding-price" type="number" min="0" step="0.0001" class="field" required></div><div><label class="label" for="allocation-correction-funding-fees">Fees</label><input id="allocation-correction-funding-fees" type="number" min="0" step="0.01" class="field" required></div></div>\n                            </div>\n                            <div class="rounded-xl border border-emerald-100 bg-emerald-50/40 p-4 space-y-3">\n                                <div><p class="text-[9px] font-black uppercase tracking-wider text-emerald-700">Target leg · BUY</p><p id="allocation-correction-target-symbol" class="text-sm font-black mt-1">—</p><p id="allocation-correction-target-status" class="text-[10px] font-bold text-gray-400 mt-1">Waiting for market data.</p></div>\n                                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2"><div><label class="label" for="allocation-correction-target-qty">Quantity</label><input id="allocation-correction-target-qty" type="number" min="0" step="0.000001" class="field" required></div><div><label class="label" for="allocation-correction-target-price">Price</label><input id="allocation-correction-target-price" type="number" min="0" step="0.0001" class="field" required></div><div><label class="label" for="allocation-correction-target-fx">FX to GBP</label><input id="allocation-correction-target-fx" type="number" min="0" step="0.000001" class="field" required></div><div><label class="label" for="allocation-correction-target-fees">Fees</label><input id="allocation-correction-target-fees" type="number" min="0" step="0.01" class="field" required></div></div>\n                                <button id="allocation-correction-match" type="button" class="text-[10px] font-black text-emerald-700 hover:text-emerald-900">Match BUY size to funding proceeds →</button>\n                            </div>\n                        </div>\n                        <div><label class="label" for="allocation-correction-reason">Private correction reason</label><textarea id="allocation-correction-reason" rows="3" class="field resize-y" placeholder="Explain why the original allocation date or data was incorrect" required></textarea><p class="text-[10px] text-gray-400 mt-1.5">This reason remains in the private audit ledger. The public corrected rows retain the original investment rationale.</p></div>\n                        <div id="allocation-correction-preview" class="rounded-xl border border-gray-200 bg-gray-50 p-4 text-xs text-gray-600 leading-relaxed">Preview the correction before anything is written.</div>\n                        <div class="rounded-xl bg-amber-50 border border-amber-200 p-3 text-[11px] leading-relaxed text-amber-800">The original rows are never deleted. The private ledger receives two reversals on the original date and a corrected SELL/BUY pair on the new date. The public portfolio shows only the corrected economic allocation.</div>\n                        <div class="flex flex-col sm:flex-row gap-3 sm:justify-end"><button type="button" onclick="closeAllocationCorrectionModal()" class="rounded-xl border border-gray-200 px-4 py-3 text-sm font-black hover:bg-gray-50">Cancel</button><button id="allocation-correction-preview-btn" type="submit" class="rounded-xl bg-gray-900 text-white px-5 py-3 text-sm font-black hover:bg-black">Preview correction</button><button id="allocation-correction-confirm" type="button" class="hidden rounded-xl bg-amber-600 text-white px-5 py-3 text-sm font-black hover:bg-amber-700">Confirm & record correction</button></div>\n                    </form>\n                </div>\n            </div>\n\n''' + modal_marker
s = s.replace(modal_marker, allocation_modal, 1)

# 2) Add effective transaction state and allocation correction state.
vars_old = '''    let liveTransactions = [];\n    let liveJournal = [];\n    let editingJournalId = null;\n    let correctingTransactionId = null;\n'''
vars_new = '''    let liveTransactions = [];\n    let effectiveTransactions = [];\n    let liveJournal = [];\n    let editingJournalId = null;\n    let correctingTransactionId = null;\n    let correctingAllocationId = null;\n    let allocationCorrectionPreviewPayload = '';\n'''
if vars_old not in s:
    raise SystemExit('state marker missing')
s = s.replace(vars_old, vars_new, 1)

logout_old = '''        liveTransactions = [];\n        liveJournal = [];\n        editingJournalId = null;\n        correctingTransactionId = null;\n'''
logout_new = '''        liveTransactions = [];\n        effectiveTransactions = [];\n        liveJournal = [];\n        editingJournalId = null;\n        correctingTransactionId = null;\n        correctingAllocationId = null;\n        allocationCorrectionPreviewPayload = '';\n'''
if logout_old not in s:
    raise SystemExit('logout state marker missing')
s = s.replace(logout_old, logout_new, 1)

# 3) Admin refresh uses authenticated raw + effective ledgers.
refresh_old = '''            const [portfolioResponse, txnResponse, journalData] = await Promise.all([\n                fetch(`${API}/${PORTFOLIO}`),\n                fetch(`${API}/${PORTFOLIO}/transactions`),\n                apiFetch(`/admin/${PORTFOLIO}/journal`)\n            ]);\n            if (!portfolioResponse.ok || !txnResponse.ok) throw new Error('Unable to load current portfolio state.');\n            const portfolio = await portfolioResponse.json();\n            const txns = await txnResponse.json();\n            const snapshot = portfolio.snapshot || portfolio;\n            liveTransactions = txns.transactions || [];\n            liveJournal = journalData.journal || [];\n'''
refresh_new = '''            const [portfolioResponse, txnData, journalData] = await Promise.all([\n                fetch(`${API}/${PORTFOLIO}`),\n                apiFetch(`/admin/${PORTFOLIO}/transactions`),\n                apiFetch(`/admin/${PORTFOLIO}/journal`)\n            ]);\n            if (!portfolioResponse.ok) throw new Error('Unable to load current portfolio state.');\n            const portfolio = await portfolioResponse.json();\n            const snapshot = portfolio.snapshot || portfolio;\n            liveTransactions = txnData.transactions || [];\n            effectiveTransactions = txnData.effective_transactions || [];\n            liveJournal = journalData.journal || [];\n'''
if refresh_old not in s:
    raise SystemExit('refresh transaction marker missing')
s = s.replace(refresh_old, refresh_new, 1)

# Journal links must use only economic/effective rows.
s = s.replace('''        [...liveTransactions].reverse().forEach(txn => {\n''', '''        [...effectiveTransactions].reverse().forEach(txn => {\n''', 1)

# 4) Replace recent-transaction renderer with allocation-aware controls.
render_start = s.index('    function renderRecentTransactions() {')
render_end = s.index('    function renderJournalManager() {', render_start)
render_new = r'''    function allocationMeta(txn) {
        const match=/^ALLOCATION ([a-f0-9]{12}) (FUNDING|TARGET):\s*(.*)$/i.exec(String(txn?.note||''));
        return match ? {decisionId:match[1].toLowerCase(),leg:match[2].toUpperCase(),reason:match[3]} : null;
    }
    function allocationReversalMeta(txn) {
        const match=/^ALLOCATION-REVERSAL ([a-f0-9]{12}) ORIGINAL ([a-f0-9]{12}) (FUNDING|TARGET):/i.exec(String(txn?.note||''));
        return match ? {correctionId:match[1].toLowerCase(),originalDecisionId:match[2].toLowerCase(),leg:match[3].toUpperCase()} : null;
    }
    function supersededAllocationIds() {
        return new Set(liveTransactions.map(allocationReversalMeta).filter(Boolean).map(x=>x.originalDecisionId));
    }

    function renderRecentTransactions() {
        const container = el('recent-transactions');
        container.replaceChildren();
        if (!liveTransactions.length) {
            const empty = document.createElement('div'); empty.className='p-6 text-sm text-gray-400'; empty.textContent='No transactions recorded.'; container.appendChild(empty); return;
        }
        const superseded=supersededAllocationIds();
        [...liveTransactions].reverse().slice(0,18).forEach(txn => {
            const instrument = txn.instruments || {};
            const isTradeCorrection = /^(REVERSAL|CORRECTION) of /.test(txn.note || '');
            const allocation = allocationMeta(txn);
            const allocationReversal = allocationReversalMeta(txn);
            const isAudit = isTradeCorrection || !!allocationReversal;
            const isSuperseded = allocation && superseded.has(allocation.decisionId);
            const isCorrectedAllocation = allocation && /^\[CORRECTS [a-f0-9]{12}\]/i.test(allocation.reason||'');
            const row = document.createElement('div'); row.className='p-4 md:px-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3';
            const left = document.createElement('div'); left.className='min-w-0';
            const top = document.createElement('div'); top.className='flex items-center gap-2 flex-wrap';
            const symbol = document.createElement('span'); symbol.className='text-sm font-black'; symbol.textContent=instrument.symbol || '—';
            const side = document.createElement('span'); side.className=`text-[9px] font-black uppercase tracking-wider rounded-full px-2 py-0.5 ${String(txn.side).toUpperCase()==='BUY'?'bg-emerald-50 text-emerald-700':'bg-red-50 text-red-700'}`; side.textContent=txn.side;
            top.append(symbol, side);
            if (isTradeCorrection) { const badge=document.createElement('span'); badge.className='text-[9px] font-black uppercase tracking-wider rounded-full px-2 py-0.5 bg-amber-50 text-amber-700'; badge.textContent=(txn.note||'').startsWith('REVERSAL')?'Reversal':'Corrected'; top.appendChild(badge); }
            if (allocationReversal) { const badge=document.createElement('span'); badge.className='text-[9px] font-black uppercase tracking-wider rounded-full px-2 py-0.5 bg-amber-50 text-amber-700'; badge.textContent='Allocation reversal'; top.appendChild(badge); }
            if (allocation) { const badge=document.createElement('span'); badge.className=`text-[9px] font-black uppercase tracking-wider rounded-full px-2 py-0.5 ${isSuperseded?'bg-gray-100 text-gray-500':isCorrectedAllocation?'bg-amber-50 text-amber-700':'bg-blue-50 text-blue-700'}`; badge.textContent=isSuperseded?'Superseded':isCorrectedAllocation?'Corrected allocation':'Allocation'; top.appendChild(badge); }
            const detail = document.createElement('p'); detail.className='text-xs text-gray-500 mt-1 truncate'; detail.textContent=`${Number(txn.quantity || 0).toLocaleString('en-GB')} units @ ${money(txn.price, txn.currency || instrument.currency || 'GBP')}${txn.note ? ' · ' + txn.note : ''}`;
            left.append(top, detail);
            const actions=document.createElement('div'); actions.className='flex items-center gap-3 shrink-0';
            const date = document.createElement('span'); date.className='text-xs font-bold text-gray-400'; date.textContent=prettyDate(txn.trade_date); actions.appendChild(date);
            if (allocation && !isSuperseded && allocation.leg==='TARGET') { const btn=document.createElement('button'); btn.type='button'; btn.className='text-[11px] font-black text-amber-700 hover:text-amber-900'; btn.textContent='Correct allocation'; btn.onclick=()=>openAllocationCorrectionModal(allocation.decisionId); actions.appendChild(btn); }
            else if (!isAudit && !allocation) { const btn=document.createElement('button'); btn.type='button'; btn.className='text-[11px] font-black text-red-700 hover:text-red-900'; btn.textContent='Correct trade'; btn.onclick=()=>openCorrectionModal(txn.id); actions.appendChild(btn); }
            row.append(left,actions); container.appendChild(row);
        });
    }

'''
s = s[:render_start] + render_new + s[render_end:]

# 5) Insert allocation-correction JS before single-trade correction functions.
js_marker = '''    function openCorrectionModal(id) {\n'''
if js_marker not in s:
    raise SystemExit('single correction JS marker missing')
allocation_js = r'''    function allocationLegs(decisionId) {
        const rows=liveTransactions.filter(txn=>allocationMeta(txn)?.decisionId===decisionId);
        return {
            funding:rows.find(txn=>allocationMeta(txn)?.leg==='FUNDING')||null,
            target:rows.find(txn=>allocationMeta(txn)?.leg==='TARGET')||null
        };
    }
    function invalidateAllocationCorrectionPreview(message='Values changed · preview again before recording.') {
        allocationCorrectionPreviewPayload='';
        el('allocation-correction-confirm').classList.add('hidden');
        const box=el('allocation-correction-preview');
        if(box){ box.textContent=message; box.className='rounded-xl border border-gray-200 bg-gray-50 p-4 text-xs text-gray-600 leading-relaxed'; }
    }
    function allocationCorrectionPayload() {
        return {
            corrected_trade_date:el('allocation-correction-date').value,
            funding_quantity:Number(el('allocation-correction-funding-qty').value),
            funding_price:Number(el('allocation-correction-funding-price').value),
            funding_fees:Number(el('allocation-correction-funding-fees').value||0),
            target_quantity:Number(el('allocation-correction-target-qty').value),
            target_price:Number(el('allocation-correction-target-price').value),
            target_fees:Number(el('allocation-correction-target-fees').value||0),
            target_fx_rate_to_base:Number(el('allocation-correction-target-fx').value||1),
            reason:el('allocation-correction-reason').value.trim()
        };
    }
    function matchCorrectedTargetToFunding() {
        const proceeds=Number(el('allocation-correction-funding-qty').value||0)*Number(el('allocation-correction-funding-price').value||0)-Number(el('allocation-correction-funding-fees').value||0);
        const price=Number(el('allocation-correction-target-price').value||0), fx=Number(el('allocation-correction-target-fx').value||1), fees=Number(el('allocation-correction-target-fees').value||0);
        if(proceeds<=0 || price<=0 || fx<=0) return;
        const qty=Math.max(0,(proceeds/fx-fees)/price);
        el('allocation-correction-target-qty').value=qty.toFixed(6);
        invalidateAllocationCorrectionPreview();
    }
    async function refreshAllocationCorrectionMarketData() {
        if(!correctingAllocationId) return;
        const {funding,target}=allocationLegs(correctingAllocationId);
        const tradeDate=el('allocation-correction-date').value;
        if(!funding || !target || !tradeDate) return;
        const fundingSymbol=(funding.instruments||{}).symbol, targetSymbol=(target.instruments||{}).symbol;
        el('allocation-correction-funding-status').textContent='Checking reference close…'; el('allocation-correction-funding-status').className='text-[10px] font-bold text-blue-600 mt-1';
        el('allocation-correction-target-status').textContent='Checking reference close + FX…'; el('allocation-correction-target-status').className='text-[10px] font-bold text-blue-600 mt-1';
        invalidateAllocationCorrectionPreview('Refreshing market references…');
        try {
            const [fundingData,targetData]=await Promise.all([
                apiFetch(`/admin/${PORTFOLIO}/instrument-lookup?symbol=${encodeURIComponent(fundingSymbol)}&trade_date=${encodeURIComponent(tradeDate)}`),
                apiFetch(`/admin/${PORTFOLIO}/instrument-lookup?symbol=${encodeURIComponent(targetSymbol)}&trade_date=${encodeURIComponent(tradeDate)}`)
            ]);
            el('allocation-correction-funding-price').value=Number(fundingData.reference_close).toFixed(4);
            el('allocation-correction-target-price').value=Number(targetData.reference_close).toFixed(4);
            el('allocation-correction-target-fx').value=Number(targetData.fx_rate_to_base||1).toFixed(6);
            const fundingSession=fundingData.used_previous_session?`previous session ${prettyDate(fundingData.price_date)}`:`close ${prettyDate(fundingData.price_date)}`;
            const targetSession=targetData.used_previous_session?`previous session ${prettyDate(targetData.price_date)}`:`close ${prettyDate(targetData.price_date)}`;
            const fxSession=targetData.currency==='GBP'?'FX 1.000000':`FX ${Number(targetData.fx_rate_to_base).toFixed(6)} ${targetData.currency}/GBP · ${prettyDate(targetData.fx_price_date)}`;
            el('allocation-correction-funding-status').textContent=`✓ ${fundingSession}`; el('allocation-correction-funding-status').className='text-[10px] font-black text-emerald-700 mt-1';
            el('allocation-correction-target-status').textContent=`✓ ${targetSession} · ${fxSession}`; el('allocation-correction-target-status').className='text-[10px] font-black text-emerald-700 mt-1';
            matchCorrectedTargetToFunding();
        } catch(error) {
            el('allocation-correction-funding-status').textContent=`✕ ${error.message}`; el('allocation-correction-funding-status').className='text-[10px] font-bold text-red-600 mt-1';
            el('allocation-correction-target-status').textContent='Unable to complete market-data refresh.'; el('allocation-correction-target-status').className='text-[10px] font-bold text-red-600 mt-1';
            invalidateAllocationCorrectionPreview('Market-data refresh failed. Fix the inputs before previewing.');
        }
    }
    async function openAllocationCorrectionModal(decisionId) {
        const {funding,target}=allocationLegs(decisionId); if(!funding || !target) return;
        correctingAllocationId=decisionId; allocationCorrectionPreviewPayload='';
        const fundingSymbol=(funding.instruments||{}).symbol||'—', targetSymbol=(target.instruments||{}).symbol||'—';
        el('allocation-correction-title').textContent=`Correct allocation: ${fundingSymbol} → ${targetSymbol}`;
        el('allocation-correction-original').textContent=`Original effective date ${prettyDate(funding.trade_date)} · both original rows remain in the private audit ledger.`;
        el('allocation-correction-funding-symbol').textContent=fundingSymbol;
        el('allocation-correction-target-symbol').textContent=`${targetSymbol} · ${target.currency||(target.instruments||{}).currency||'GBP'}`;
        el('allocation-correction-funding-qty').value=funding.quantity;
        el('allocation-correction-funding-price').value=funding.price;
        el('allocation-correction-funding-fees').value=funding.fees||0;
        el('allocation-correction-target-qty').value=target.quantity;
        el('allocation-correction-target-price').value=target.price;
        el('allocation-correction-target-fx').value=target.fx_rate_to_base||1;
        el('allocation-correction-target-fees').value=target.fees||0;
        el('allocation-correction-reason').value='';
        const next=new Date(`${funding.trade_date}T12:00:00`); next.setDate(next.getDate()+1); el('allocation-correction-date').value=next.toISOString().slice(0,10);
        invalidateAllocationCorrectionPreview('Loading corrected-date market references…');
        const modal=el('allocation-correction-modal'); modal.classList.remove('hidden'); modal.classList.add('flex'); document.body.style.overflow='hidden';
        await refreshAllocationCorrectionMarketData();
    }
    function closeAllocationCorrectionModal() {
        correctingAllocationId=null; allocationCorrectionPreviewPayload='';
        const modal=el('allocation-correction-modal'); modal.classList.add('hidden'); modal.classList.remove('flex'); document.body.style.overflow='';
    }
    el('allocation-correction-date').addEventListener('change',refreshAllocationCorrectionMarketData);
    el('allocation-correction-match').addEventListener('click',matchCorrectedTargetToFunding);
    ['allocation-correction-funding-qty','allocation-correction-funding-price','allocation-correction-funding-fees','allocation-correction-target-qty','allocation-correction-target-price','allocation-correction-target-fx','allocation-correction-target-fees','allocation-correction-reason'].forEach(id=>el(id).addEventListener('input',()=>invalidateAllocationCorrectionPreview()));

    el('allocation-correction-form').addEventListener('submit',async event=>{
        event.preventDefault(); if(!correctingAllocationId) return;
        const payload=allocationCorrectionPayload();
        const btn=el('allocation-correction-preview-btn'); btn.disabled=true; btn.textContent='Validating preview…';
        try {
            const preview=await apiFetch(`/admin/${PORTFOLIO}/allocation/${correctingAllocationId}/correct/preview`,{method:'POST',body:JSON.stringify(payload)});
            allocationCorrectionPreviewPayload=JSON.stringify(payload);
            const box=el('allocation-correction-preview');
            box.className='rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-xs text-emerald-800 leading-relaxed';
            box.textContent=`✓ Preview passed · ${prettyDate(preview.original_trade_date)} → ${prettyDate(preview.corrected_trade_date)} · Funding proceeds ${money(preview.funding_proceeds_base,'GBP')} · Target cost ${money(preview.target_cost_base,'GBP')} · Net cash impact ${money(preview.net_cash_impact,'GBP')} · Minimum historical cash ${money(preview.validation?.minimum_cash,'GBP')}. No rows have been written.`;
            el('allocation-correction-confirm').classList.remove('hidden');
        } catch(error) { invalidateAllocationCorrectionPreview(`✕ Preview rejected: ${error.message}`); el('allocation-correction-preview').className='rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-700 leading-relaxed'; }
        finally { btn.disabled=false; btn.textContent='Preview correction'; }
    });

    el('allocation-correction-confirm').addEventListener('click',async()=>{
        if(!correctingAllocationId) return;
        const payload=allocationCorrectionPayload();
        if(JSON.stringify(payload)!==allocationCorrectionPreviewPayload){ invalidateAllocationCorrectionPreview(); return; }
        if(!confirm(`Permanently record this paired allocation correction to ${prettyDate(payload.corrected_trade_date)}?\n\nThe private ledger will keep the original rows plus reversals. The public portfolio will show only the corrected allocation.`)) return;
        const btn=el('allocation-correction-confirm'); btn.disabled=true; btn.textContent='Recording correction…';
        try {
            const result=await apiFetch(`/admin/${PORTFOLIO}/allocation/${correctingAllocationId}/correct`,{method:'POST',body:JSON.stringify(payload)});
            closeAllocationCorrectionModal();
            setMessage('global-message',`Allocation corrected to ${prettyDate(payload.corrected_trade_date)}. Public history now uses the corrected economic rows; the original remains private audit history.`,'success');
            await refreshAdminData();
            if(result.target_transaction?.id){ el('journal-transaction').value=result.target_transaction.id; el('journal-date').value=payload.corrected_trade_date; el('journal-category').value='Investment Note'; el('journal-title').scrollIntoView({behavior:'smooth',block:'center'}); }
        } catch(error) { setMessage('global-message',error.message,'error'); }
        finally { btn.disabled=false; btn.textContent='Confirm & record correction'; }
    });
    el('allocation-correction-modal').addEventListener('click',event=>{ if(event.target===el('allocation-correction-modal')) closeAllocationCorrectionModal(); });
    document.addEventListener('keydown',event=>{ if(event.key==='Escape'&&!el('allocation-correction-modal').classList.contains('hidden')) closeAllocationCorrectionModal(); });

''' + js_marker
s = s.replace(js_marker, allocation_js, 1)

p.write_text(s, encoding='utf-8')
print('allocation correction admin UI patched')
