(() => {
    'use strict';

    if (window.__sethiStockValuationV2PolishInstalled) return;
    window.__sethiStockValuationV2PolishInstalled = true;

    const VERSION = '4d18';
    const VIEW_KEY = 'sethistockValuationView';
    let timer = null;
    let view = 'standard';

    const root = () => document.getElementById('valuation');
    const numberFromText = value => {
        const match = String(value || '').replace(/,/g, '').match(/-?[\d.]+/);
        return match ? Number(match[0]) : null;
    };
    const isReverseMode = () => root()?.querySelector('[data-valuation-mode="reverse"]')?.classList.contains('bg-blue-600') === true;
    const setTextSafe = (id, value) => {
        const node = document.getElementById(id);
        if (node) node.textContent = value;
    };
    const setDisplay = (node, show, display = '') => {
        if (node) node.style.display = show ? display : 'none';
    };

    function rememberView(next) {
        view = next === 'advanced' ? 'advanced' : 'standard';
        try { localStorage.setItem(VIEW_KEY, view); } catch (_) {}
    }

    function findSection(titlePattern) {
        return [...root()?.querySelectorAll('section') || []].find(section => titlePattern.test(section.querySelector('h4')?.textContent.trim() || '')) || null;
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
        for (let i = 0; sibling && i < 5; i += 1) {
            const next = sibling.nextElementSibling;
            const blank = !sibling.textContent.trim() && !sibling.querySelector('input,button,select,textarea,table,canvas,svg,img');
            const looksLikeShell = String(sibling.className).includes('border') && String(sibling.className).includes('rounded');
            if (blank && looksLikeShell) sibling.remove();
            sibling = next;
        }
    }

    function ensureViewToggle() {
        const valuation = root();
        if (!valuation?.dataset.valuationV2) return;

        const heading = [...valuation.querySelectorAll('h3')].find(node => /Advanced Valuation|^Valuation$/.test(node.textContent.trim()));
        if (!heading) return;
        heading.textContent = 'Valuation';

        const badge = [...valuation.querySelectorAll('span')].find(node => /Model v2|DCF Model/i.test(node.textContent.trim()));
        if (badge) badge.textContent = 'DCF Model';

        const header = heading.parentElement?.parentElement?.parentElement;
        if (!header) return;

        document.querySelectorAll('#valuation-view-toggle').forEach(toggle => {
            if (!valuation.contains(toggle)) toggle.closest('[data-valuation-header-controls]')?.remove();
        });

        let controls = valuation.querySelector('[data-valuation-header-controls]');
        if (!controls) {
            controls = document.createElement('div');
            controls.dataset.valuationHeaderControls = '1';
            controls.className = 'flex flex-col items-start lg:items-end gap-2 shrink-0';
            controls.innerHTML = `
                <div id="valuation-view-toggle" class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1 shadow-sm" aria-label="Valuation view">
                    <button type="button" data-valuation-view="standard" class="px-4 py-2 rounded-md text-xs font-black transition">Standard</button>
                    <button type="button" data-valuation-view="advanced" class="px-4 py-2 rounded-md text-xs font-black transition">Advanced</button>
                </div>
                <div id="valuation-data-note" class="text-[9px] font-black text-emerald-700 uppercase tracking-widest">Uses loaded data · zero extra requests</div>`;
        }

        [...header.children].forEach(child => {
            if (child === controls || child.contains(heading)) return;
            const text = child.textContent.trim();
            if (/Client-side|Uses loaded data/i.test(text)) child.remove();
        });
        if (controls.parentElement !== header) header.appendChild(controls);
    }

    function ensureStandardDiscountInput() {
        const valuation = root();
        const workbench = findSection(/DCF Workbench|DCF Calculator/);
        if (!valuation || !workbench) return;

        const coreLabel = [...workbench.querySelectorAll('p')].find(node => node.textContent.trim().toLowerCase() === 'core assumptions');
        const assumptions = coreLabel?.nextElementSibling;
        if (!assumptions) return;

        document.querySelectorAll('#val-standard-rate-wrap').forEach(node => {
            if (!valuation.contains(node) || node.parentElement !== assumptions) node.remove();
        });

        let wrap = valuation.querySelector('#val-standard-rate-wrap');
        if (wrap) return;

        wrap = document.createElement('label');
        wrap.id = 'val-standard-rate-wrap';
        wrap.className = 'block';
        wrap.innerHTML = `<span class="block text-[9px] font-black uppercase tracking-widest text-gray-400 mb-1.5">Discount Rate</span><div class="relative"><input id="val-standard-rate" type="number" min="3" max="30" step="0.1" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 pr-10 text-sm font-black text-gray-900 outline-none focus:border-blue-300 focus:ring-2 focus:ring-blue-100"><span class="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-black text-gray-400">%</span></div>`;

        const growthWrap = valuation.querySelector('#val-growth-field');
        if (growthWrap?.parentElement === assumptions) growthWrap.insertAdjacentElement('afterend', wrap);
        else assumptions.appendChild(wrap);

        wrap.querySelector('input')?.addEventListener('input', event => {
            const desired = Number(event.target.value);
            const real = Number(document.getElementById('val-real-yield')?.value);
            const inflation = Number(document.getElementById('val-inflation')?.value);
            const beta = Number(document.getElementById('val-beta')?.value);
            const erp = document.getElementById('val-erp');
            if (!Number.isFinite(desired) || !Number.isFinite(real) || !Number.isFinite(inflation) || !Number.isFinite(beta) || beta <= 0 || !erp) return;
            erp.value = Math.max(0, Math.min(20, (desired - real - inflation) / beta)).toFixed(2);
            window.calculateDCF?.();
            schedulePolish(0);
        });
    }

    function terminalMethodWrap() {
        const label = [...root()?.querySelectorAll('p') || []].find(node => node.textContent.trim().toLowerCase() === 'terminal method');
        return label?.parentElement || null;
    }

    function setSnapshotLayout(standard) {
        const price = document.getElementById('val-snap-price')?.parentElement;
        const implied = document.getElementById('val-snap-implied')?.parentElement;
        const base = document.getElementById('val-snap-base')?.parentElement;
        const upside = document.getElementById('val-snap-upside')?.parentElement;
        const rate = document.getElementById('val-snap-rate')?.parentElement;
        const grid = price?.parentElement;

        [price, implied, base, upside, rate].forEach(node => setDisplay(node, true));
        if (grid) grid.style.gridTemplateColumns = '';

        const baseLabel = base?.querySelector('p');
        if (baseLabel) baseLabel.textContent = standard ? 'Fair Value' : (isReverseMode() ? 'Implied Value Check' : 'Base Fair Value');
    }

    function setStandardView() {
        const valuation = root();
        if (!valuation) return;

        const forward = valuation.querySelector('[data-valuation-mode="forward"]');
        const exit = valuation.querySelector('[data-terminal="exit"]');
        const coe = valuation.querySelector('[data-rate-basis="coe"]');
        const exitSensitivity = valuation.querySelector('[data-sensitivity="exit"]');
        if (isReverseMode()) forward?.click();
        if (!exit?.classList.contains('bg-blue-600')) exit?.click();
        if (!coe?.classList.contains('bg-blue-600')) coe?.click();
        if (!exitSensitivity?.classList.contains('bg-blue-600')) exitSensitivity?.click();

        const workbench = findSection(/DCF Workbench|DCF Calculator/);
        const scenarios = findSection(/^Scenario Valuation$/);
        const sensitivity = findSection(/^Sensitivity Analysis$/);
        const fairRange = findSection(/^Fair Value Range$/);
        const discountEngine = [...workbench?.querySelectorAll('p') || []].find(node => node.textContent.trim().toLowerCase() === 'discount-rate engine')?.closest('.rounded-xl');
        const innerGrid = discountEngine?.parentElement;
        const modeToggle = valuation.querySelector('[data-valuation-mode]')?.parentElement;
        const sensitivityToggle = sensitivity?.querySelector('[data-sensitivity]')?.parentElement;

        setDisplay(scenarios, true);
        setDisplay(sensitivity, true);
        setDisplay(fairRange, true);
        setDisplay(discountEngine, false);
        setDisplay(modeToggle, false);
        setDisplay(sensitivityToggle, false);
        setDisplay(terminalMethodWrap(), false);
        setDisplay(valuation.querySelector('#val-standard-rate-wrap'), true);

        if (innerGrid) innerGrid.style.gridTemplateColumns = '1fr';
        if (workbench) {
            workbench.classList.remove('xl:col-span-5');
            workbench.classList.add('xl:col-span-3');
            const title = workbench.querySelector('h4');
            if (title) title.textContent = 'DCF Calculator';
        }
        if (scenarios) {
            if (scenarios.closest('[data-lbo-right-stack]')) scenarios.classList.remove('xl:col-span-2');
            else scenarios.classList.add('xl:col-span-2');
            const copy = scenarios.querySelector('p.text-xs');
            if (copy) copy.textContent = 'A quick Bear, Base and Bull range around the assumptions you have set.';
        }
        setTextSafe('valuation-mode-copy', 'Set the core assumptions; the scenario panel shows how the result moves under a simple bear/base/bull range.');
        const topCopy = valuation.firstElementChild?.querySelector('p.text-sm');
        if (topCopy) topCopy.textContent = 'A clear DCF view by default, with the full valuation workbench one click away.';
        setSnapshotLayout(true);
    }

    function setAdvancedView() {
        const valuation = root();
        if (!valuation) return;

        const workbench = findSection(/DCF Workbench|DCF Calculator/);
        const scenarios = findSection(/^Scenario Valuation$/);
        const sensitivity = findSection(/^Sensitivity Analysis$/);
        const fairRange = findSection(/^Fair Value Range$/);
        const discountEngine = [...workbench?.querySelectorAll('p') || []].find(node => node.textContent.trim().toLowerCase() === 'discount-rate engine')?.closest('.rounded-xl');
        const innerGrid = discountEngine?.parentElement;
        const modeToggle = valuation.querySelector('[data-valuation-mode]')?.parentElement;
        const sensitivityToggle = sensitivity?.querySelector('[data-sensitivity]')?.parentElement;

        [scenarios, sensitivity, fairRange, discountEngine, modeToggle, sensitivityToggle, terminalMethodWrap()].forEach(node => setDisplay(node, true));
        setDisplay(valuation.querySelector('#val-standard-rate-wrap'), false);

        if (innerGrid) innerGrid.style.gridTemplateColumns = '';
        if (workbench) {
            workbench.classList.remove('xl:col-span-5');
            workbench.classList.add('xl:col-span-3');
            const title = workbench.querySelector('h4');
            if (title) title.textContent = 'DCF Workbench';
        }
        if (scenarios) {
            if (scenarios.closest('[data-lbo-right-stack]')) scenarios.classList.remove('xl:col-span-2');
            const copy = scenarios.querySelector('p.text-xs');
            if (copy) copy.textContent = 'Bear, Base and Bull flex growth, discount rate and terminal assumptions coherently.';
        }
        setTextSafe('valuation-mode-copy', isReverseMode() ? `Solve the FCF growth rate today's share price requires.` : 'Project your own FCF growth assumption into an implied fair value.');
        const topCopy = valuation.firstElementChild?.querySelector('p.text-sm');
        if (topCopy) topCopy.textContent = 'What is priced in, what could the business be worth, and which assumptions matter?';
        setSnapshotLayout(false);
    }

    function syncViewButtons() {
        root()?.querySelectorAll('[data-valuation-view]').forEach(button => {
            const active = button.dataset.valuationView === view;
            button.className = `px-4 py-2 rounded-md text-xs font-black transition ${active ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-gray-500 hover:text-blue-700'}`;
        });
    }

    function polishCopyAndLayout() {
        const valuation = root();
        if (!valuation?.dataset.valuationV2) return;
        const workbench = findSection(/DCF Workbench|DCF Calculator/);
        const scenarios = findSection(/^Scenario Valuation$/);
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
        const input = root()?.querySelector('#val-standard-rate');
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

        const modeButton = event.target.closest?.('[data-valuation-mode]');
        if (modeButton) {
            const input = document.getElementById('val-growth');
            if (input) {
                if (modeButton.dataset.valuationMode === 'reverse') {
                    if (!input.dataset.forwardGrowth) input.dataset.forwardGrowth = input.value;
                } else if (modeButton.dataset.valuationMode === 'forward' && input.dataset.forwardGrowth) {
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