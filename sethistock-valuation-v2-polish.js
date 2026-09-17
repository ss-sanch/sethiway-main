(() => {
    'use strict';

    if (window.__sethiStockValuationV2PolishInstalled) return;
    window.__sethiStockValuationV2PolishInstalled = true;

    const VERSION = '4d3';
    const VIEW_KEY = 'sethistockValuationView';
    let timer = null;
    let view = 'standard';

    const numberFromText = value => {
        const match = String(value || '').replace(/,/g, '').match(/-?[\d.]+/);
        return match ? Number(match[0]) : null;
    };
    const isReverseMode = () => document.querySelector('[data-valuation-mode="reverse"]')?.classList.contains('bg-blue-600') === true;
    const root = () => document.getElementById('valuation');

    function rememberView(next) {
        view = next === 'advanced' ? 'advanced' : 'standard';
        try { localStorage.setItem(VIEW_KEY, view); } catch (_) {}
    }

    function removeLegacyValuationUI() {
        const legacyMatrixTitle = [...document.querySelectorAll('h3')].find(node => node.textContent.trim() === 'Live DCF Sensitivity Matrix');
        const legacyMatrix = legacyMatrixTitle?.closest('.bg-gray-50');
        if (legacyMatrix && !legacyMatrix.closest('#valuation')) legacyMatrix.remove();

        const legacyLboTitle = [...document.querySelectorAll('h3')].find(node => node.textContent.trim() === 'Mini-LBO (Leveraged Buyout) Model');
        const legacyLbo = legacyLboTitle?.closest('.bg-gray-50');
        if (legacyLbo && !legacyLbo.closest('#valuation')) legacyLbo.remove();

        const valuation = root();
        let sibling = valuation?.nextElementSibling;
        for (let i = 0; sibling && i < 4; i += 1) {
            const next = sibling.nextElementSibling;
            const blank = !sibling.textContent.trim() && !sibling.querySelector('input,button,select,textarea,table,canvas,svg,img');
            const looksLikeShell = sibling.className.includes('border') && sibling.className.includes('rounded');
            if (blank && looksLikeShell) sibling.remove();
            sibling = next;
        }
    }

    function ensureViewToggle() {
        const valuation = root();
        if (!valuation?.dataset.valuationV2) return;

        const badge = [...valuation.querySelectorAll('span')].find(node => node.textContent.trim() === 'Model v2');
        if (badge) badge.textContent = 'DCF Model';

        if (document.getElementById('valuation-view-toggle')) return;
        const header = valuation.firstElementChild;
        const right = header?.lastElementChild;
        if (!right) return;

        const wrap = document.createElement('div');
        wrap.className = 'flex flex-col items-end gap-2';
        wrap.innerHTML = `
            <div id="valuation-view-toggle" class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1">
                <button type="button" data-valuation-view="standard" class="px-3 py-1.5 rounded-md text-[10px] font-black transition">Standard</button>
                <button type="button" data-valuation-view="advanced" class="px-3 py-1.5 rounded-md text-[10px] font-black transition">Advanced</button>
            </div>
            <div id="valuation-data-note" class="text-[10px] font-black text-emerald-700 uppercase tracking-widest">Uses loaded data · zero extra requests</div>`;
        right.replaceWith(wrap);
    }

    function ensureStandardDiscountInput() {
        const valuation = root();
        if (!valuation || document.getElementById('val-standard-rate-wrap')) return;
        const assumptions = [...valuation.querySelectorAll('p')].find(node => node.textContent.trim().toLowerCase() === 'core assumptions')?.nextElementSibling;
        if (!assumptions) return;
        const wrap = document.createElement('label');
        wrap.id = 'val-standard-rate-wrap';
        wrap.className = 'block';
        wrap.innerHTML = `<span class="block text-[9px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Discount Rate</span><div class="relative"><input id="val-standard-rate" type="number" min="3" max="30" step="0.1" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 pr-10 text-sm font-black text-gray-900 outline-none focus:border-blue-300 focus:ring-2 focus:ring-blue-100"><span class="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-black text-gray-400">%</span></div>`;
        const exitInput = document.getElementById('val-exit-multiple')?.closest('label');
        assumptions.insertBefore(wrap, exitInput || null);

        wrap.querySelector('input')?.addEventListener('input', event => {
            const desired = Number(event.target.value);
            const real = Number(document.getElementById('val-real-yield')?.value);
            const inflation = Number(document.getElementById('val-inflation')?.value);
            const beta = Number(document.getElementById('val-beta')?.value);
            const erp = document.getElementById('val-erp');
            if (!Number.isFinite(desired) || !Number.isFinite(real) || !Number.isFinite(inflation) || !Number.isFinite(beta) || beta <= 0 || !erp) return;
            erp.value = ((desired - real - inflation) / beta).toFixed(2);
            window.calculateDCF?.();
            schedulePolish(0);
        });
    }

    function terminalMethodWrap() {
        const label = [...root()?.querySelectorAll('p') || []].find(node => node.textContent.trim().toLowerCase() === 'terminal method');
        return label?.parentElement || null;
    }

    function setDisplay(node, show, display = '') {
        if (!node) return;
        node.style.display = show ? display : 'none';
    }

    function setSnapshotLayout(standard) {
        const valuation = root();
        const price = document.getElementById('val-snap-price')?.parentElement;
        const implied = document.getElementById('val-snap-implied')?.parentElement;
        const base = document.getElementById('val-snap-base')?.parentElement;
        const upside = document.getElementById('val-snap-upside')?.parentElement;
        const rate = document.getElementById('val-snap-rate')?.parentElement;
        const grid = price?.parentElement;
        setDisplay(implied, !standard);
        setDisplay(rate, !standard);
        [price, base, upside].forEach(node => setDisplay(node, true));
        if (grid) grid.style.gridTemplateColumns = standard ? 'repeat(3,minmax(0,1fr))' : '';
        const baseLabel = base?.querySelector('p');
        if (baseLabel) baseLabel.textContent = standard ? 'Fair Value' : (isReverseMode() ? 'Implied Value Check' : 'Base Fair Value');
    }

    function setStandardView() {
        const valuation = root();
        if (!valuation) return;

        const forward = valuation.querySelector('[data-valuation-mode="forward"]');
        const exit = valuation.querySelector('[data-terminal="exit"]');
        const coe = valuation.querySelector('[data-rate-basis="coe"]');
        if (isReverseMode()) forward?.click();
        if (!exit?.classList.contains('bg-blue-600')) exit?.click();
        if (!coe?.classList.contains('bg-blue-600')) coe?.click();

        const sections = [...valuation.querySelectorAll('section')];
        const workbench = sections.find(section => section.querySelector('h4')?.textContent.trim().match(/DCF Workbench|DCF Calculator/));
        const scenarios = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Scenario Valuation');
        const sensitivity = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Sensitivity Analysis');
        const fairRange = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Fair Value Range');
        const lbo = document.getElementById('valuation-lbo-details');
        const discountEngine = [...workbench?.querySelectorAll('p') || []].find(node => node.textContent.trim().toLowerCase() === 'discount-rate engine')?.closest('.rounded-xl');
        const innerGrid = discountEngine?.parentElement;
        const modeToggle = valuation.querySelector('[data-valuation-mode]')?.parentElement;

        setDisplay(scenarios, false);
        setDisplay(sensitivity, false);
        setDisplay(fairRange, false);
        setDisplay(lbo, false);
        setDisplay(discountEngine, false);
        setDisplay(modeToggle, false);
        setDisplay(terminalMethodWrap(), false);
        setDisplay(document.getElementById('val-standard-rate-wrap'), true);
        if (innerGrid) innerGrid.style.gridTemplateColumns = '1fr';
        if (workbench) {
            workbench.classList.remove('xl:col-span-3');
            workbench.classList.add('xl:col-span-5');
            const title = workbench.querySelector('h4');
            if (title) title.textContent = 'DCF Calculator';
        }
        setTextSafe('valuation-mode-copy', 'Set a few core assumptions and see what the business could be worth.');
        const topCopy = valuation.firstElementChild?.querySelector('p.text-sm');
        if (topCopy) topCopy.textContent = 'A simple DCF by default, with deeper valuation tools one click away.';
        setSnapshotLayout(true);
    }

    function setAdvancedView() {
        const valuation = root();
        if (!valuation) return;
        const sections = [...valuation.querySelectorAll('section')];
        const workbench = sections.find(section => section.querySelector('h4')?.textContent.trim().match(/DCF Workbench|DCF Calculator/));
        const scenarios = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Scenario Valuation');
        const sensitivity = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Sensitivity Analysis');
        const fairRange = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Fair Value Range');
        const lbo = document.getElementById('valuation-lbo-details');
        const discountEngine = [...workbench?.querySelectorAll('p') || []].find(node => node.textContent.trim().toLowerCase() === 'discount-rate engine')?.closest('.rounded-xl');
        const innerGrid = discountEngine?.parentElement;
        const modeToggle = valuation.querySelector('[data-valuation-mode]')?.parentElement;

        [scenarios, sensitivity, fairRange, lbo, discountEngine, modeToggle, terminalMethodWrap()].forEach(node => setDisplay(node, true));
        setDisplay(document.getElementById('val-standard-rate-wrap'), false);
        if (innerGrid) innerGrid.style.gridTemplateColumns = '';
        if (workbench) {
            workbench.classList.remove('xl:col-span-5');
            workbench.classList.add('xl:col-span-3');
            const title = workbench.querySelector('h4');
            if (title) title.textContent = 'DCF Workbench';
        }
        setTextSafe('valuation-mode-copy', isReverseMode() ? `Solve the FCF growth rate today's share price requires.` : 'Project your own FCF growth assumption into an implied fair value.');
        const topCopy = valuation.firstElementChild?.querySelector('p.text-sm');
        if (topCopy) topCopy.textContent = 'What is priced in, what could the business be worth, and which assumptions matter?';
        setSnapshotLayout(false);
    }

    function setTextSafe(id, value) {
        const node = document.getElementById(id);
        if (node) node.textContent = value;
    }

    function syncViewButtons() {
        document.querySelectorAll('[data-valuation-view]').forEach(button => {
            const active = button.dataset.valuationView === view;
            button.className = `px-3 py-1.5 rounded-md text-[10px] font-black transition ${active ? 'bg-blue-600 text-white' : 'bg-white text-gray-500'}`;
        });
    }

    function polishCopyAndLayout() {
        const valuation = root();
        if (!valuation?.dataset.valuationV2) return;
        const sections = [...valuation.querySelectorAll('section')];
        const workbench = sections.find(section => section.querySelector('h4')?.textContent.trim().match(/DCF Workbench|DCF Calculator/));
        const scenarios = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Scenario Valuation');
        const topGrid = workbench?.parentElement;
        if (topGrid) topGrid.classList.add('items-start');
        if (scenarios) scenarios.classList.add('self-start');
    }

    function polishRealYield() {
        const input = document.getElementById('val-real-yield');
        const value = Number(input?.value);
        if (input && Number.isFinite(value)) input.value = value.toFixed(1);
    }

    function polishGrowthField() {
        const field = document.getElementById('val-growth-field');
        const input = document.getElementById('val-growth');
        const label = field?.querySelector('label > span');
        if (!field || !input || !label) return;
        if (isReverseMode()) {
            label.textContent = 'Solved FCF Growth';
            const implied = numberFromText(document.getElementById('val-implied-growth')?.textContent);
            if (Number.isFinite(implied)) input.value = implied.toFixed(1);
        } else {
            label.textContent = 'FCF Growth';
        }
    }

    function syncStandardRate() {
        const input = document.getElementById('val-standard-rate');
        if (!input || document.activeElement === input) return;
        const coe = numberFromText(document.getElementById('val-coe')?.textContent);
        if (Number.isFinite(coe)) input.value = coe.toFixed(1);
    }

    function suppressDuplicateBaseMarker() {
        if (!isReverseMode() || typeof Plotly === 'undefined') return;
        const field = document.getElementById('football-field');
        if (!field?._fullLayout?.shapes || field._fullLayout.shapes.length < 2) return;
        const current = numberFromText(document.getElementById('val-snap-price')?.textContent);
        const base = numberFromText(document.getElementById('val-snap-base')?.textContent);
        if (!Number.isFinite(current) || !Number.isFinite(base)) return;
        const tolerance = Math.max(0.01, Math.abs(current) * 0.0001);
        if (Math.abs(current - base) <= tolerance) Plotly.relayout(field, { 'shapes[1].visible': false });
    }

    function applyView() {
        view === 'advanced' ? setAdvancedView() : setStandardView();
        syncViewButtons();
    }

    function applyPolish() {
        removeLegacyValuationUI();
        ensureViewToggle();
        ensureStandardDiscountInput();
        polishCopyAndLayout();
        polishRealYield();
        polishGrowthField();
        syncStandardRate();
        applyView();
        suppressDuplicateBaseMarker();
    }

    function schedulePolish(delay = 0) {
        clearTimeout(timer);
        timer = setTimeout(applyPolish, delay);
    }

    document.addEventListener('click', event => {
        const viewButton = event.target.closest?.('[data-valuation-view]');
        if (viewButton) {
            rememberView(viewButton.dataset.valuationView);
            applyView();
            schedulePolish(20);
            return;
        }

        const button = event.target.closest?.('[data-valuation-mode]');
        if (button) {
            const input = document.getElementById('val-growth');
            if (input) {
                if (button.dataset.valuationMode === 'reverse') {
                    if (!input.dataset.forwardGrowth) input.dataset.forwardGrowth = input.value;
                } else if (button.dataset.valuationMode === 'forward' && input.dataset.forwardGrowth) {
                    input.value = input.dataset.forwardGrowth;
                    delete input.dataset.forwardGrowth;
                }
            }
        }
        if (event.target.closest?.('#valuation')) schedulePolish(0);
    }, true);

    document.addEventListener('input', event => {
        if (event.target.id === 'val-growth' && !isReverseMode()) delete event.target.dataset.forwardGrowth;
        if (event.target.closest?.('#valuation')) schedulePolish(0);
    });

    window.addEventListener('sethistock:analysis-ready', () => schedulePolish(120));
    window.addEventListener('sethistock:financial-history-ready', () => schedulePolish(80));
    window.addEventListener('resize', () => schedulePolish(80));

    try { view = localStorage.getItem(VIEW_KEY) === 'advanced' ? 'advanced' : 'standard'; } catch (_) {}
    schedulePolish(0);
    setTimeout(applyPolish, 150);

    window.SethiStockValuationV2Polish = { apply: applyPolish, version: VERSION, getView: () => view };
})();
