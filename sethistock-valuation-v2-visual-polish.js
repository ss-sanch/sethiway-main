(() => {
    'use strict';

    if (window.__sethiStockValuationV2VisualPolishInstalled) return;
    window.__sethiStockValuationV2VisualPolishInstalled = true;

    const VERSION = '4d13';
    let timer = null;

    const root = () => document.getElementById('valuation');

    function findSection(titlePattern) {
        return [...root()?.querySelectorAll('section') || []].find(section =>
            titlePattern.test(section.querySelector('h4')?.textContent.trim() || '')
        ) || null;
    }

    function standardViewActive() {
        return root()?.querySelector('[data-valuation-view="standard"]')?.classList.contains('bg-blue-600') === true;
    }

    function balanceTopCards() {
        const valuation = root();
        if (!valuation) return;

        const workbench = findSection(/DCF Workbench|DCF Calculator/);
        const scenarios = findSection(/^Scenario Valuation$/);
        const grid = workbench?.parentElement;
        if (!workbench || !scenarios || !grid) return;

        // Keep the top valuation cards content-sized in both views. The LBO launcher
        // now sits under Scenario Valuation, so stretching either card creates dead space
        // and can push the launcher below the visible row.
        grid.classList.add('items-start');
        grid.style.alignItems = 'start';
        workbench.style.alignSelf = 'start';
        scenarios.style.alignSelf = 'start';
        workbench.classList.remove('h-full');
        scenarios.classList.remove('h-full');

        const rightStack = scenarios.closest('[data-lbo-right-stack]');
        if (rightStack) {
            rightStack.style.alignSelf = 'start';
            rightStack.style.height = 'auto';
        }
    }

    function liftSmallTypography() {
        const valuation = root();
        if (!valuation) return;

        valuation.querySelectorAll('.text-\\[9px\\]:not([data-valuation-font-bumped])').forEach(node => {
            node.classList.remove('text-[9px]');
            node.classList.add('text-[10px]');
            node.dataset.valuationFontBumped = '1';
        });

        valuation.querySelectorAll('.text-\\[10px\\]:not([data-valuation-font-bumped])').forEach(node => {
            node.classList.remove('text-[10px]');
            node.classList.add('text-[11px]');
            node.dataset.valuationFontBumped = '1';
        });
    }

    function apply() {
        balanceTopCards();
        liftSmallTypography();
    }

    function schedule(delay = 40) {
        clearTimeout(timer);
        timer = setTimeout(apply, delay);
    }

    document.addEventListener('click', event => {
        if (event.target.closest?.('#valuation')) schedule(60);
    });
    document.addEventListener('input', event => {
        if (event.target.closest?.('#valuation')) schedule(60);
    });
    window.addEventListener('sethistock:analysis-ready', () => schedule(180));
    window.addEventListener('sethistock:financial-history-ready', () => schedule(140));
    window.addEventListener('resize', () => schedule(120));

    schedule(80);
    setTimeout(apply, 220);

    window.SethiStockValuationV2VisualPolish = { apply, version: VERSION };
})();
