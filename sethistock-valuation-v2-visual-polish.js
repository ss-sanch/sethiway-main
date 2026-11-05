(() => {
    'use strict';

    if (window.__sethiStockValuationV2VisualPolishInstalled) return;
    window.__sethiStockValuationV2VisualPolishInstalled = true;

    const VERSION = '4d19';
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
        const rightStack = scenarios?.closest('[data-lbo-right-stack]');
        const launcher = rightStack?.querySelector('[data-lbo-launcher]');
        if (!workbench || !scenarios || !grid || !rightStack || !launcher) return;

        const gap = standardViewActive() ? 12 : 16;

        // Let the grid size the row as cached or live content arrives.
        grid.classList.remove('items-start');
        grid.style.alignItems = 'stretch';
        workbench.style.minWidth = '0';

        rightStack.classList.remove('space-y-4');
        rightStack.style.display = 'grid';
        rightStack.style.gridTemplateColumns = 'minmax(0, 1fr)';
        rightStack.style.gridTemplateRows = 'auto 1fr';
        rightStack.style.gap = gap + 'px';

        scenarios.classList.remove('xl:col-span-2');
    }

    function compactStandardRightColumn() {
        const valuation = root();
        if (!valuation) return;

        const scenarios = findSection(/^Scenario Valuation$/);
        const launcher = valuation.querySelector('[data-lbo-launcher]');
        const scenarioList = scenarios?.querySelector('#valuation-scenarios');
        const scenarioHeader = scenarios?.firstElementChild;
        const scenarioFooter = scenarioList?.nextElementSibling;
        const standard = standardViewActive();

        if (scenarios) scenarios.style.padding = standard ? '16px' : '';
        if (scenarioHeader) scenarioHeader.style.marginBottom = standard ? '10px' : '';

        if (scenarioList) {
            scenarioList.classList.remove('space-y-3', 'space-y-2');
            scenarioList.classList.add(standard ? 'space-y-2' : 'space-y-3');
            [...scenarioList.children].forEach(card => {
                card.style.padding = standard ? '10px 12px' : '';
                const meta = card.lastElementChild;
                if (meta) meta.style.marginTop = standard ? '8px' : '';
            });
        }

        if (scenarioFooter) {
            scenarioFooter.style.marginTop = standard ? '12px' : '';
            scenarioFooter.style.paddingTop = standard ? '10px' : '';
        }

        if (launcher) {
            launcher.style.padding = standard ? '12px' : '16px';
            const metrics = launcher.querySelector('[data-lbo-launcher-metrics]');
            if (metrics) {
                [...metrics.children].forEach(card => {
                    card.style.padding = standard ? '7px 10px' : '';
                });
            }
        }
    }

    function normaliseRealYieldDisplay() {
        const input = document.querySelector('#val-real-yield');
        const value = Number(input?.value);
        if (input && Number.isFinite(value) && document.activeElement !== input) {
            input.value = value.toFixed(1);
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
        compactStandardRightColumn();
        balanceTopCards();
        normaliseRealYieldDisplay();
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
    window.addEventListener('sethistock:snapshot-ready', () => schedule());
    window.addEventListener('sethistock:analysis-ready', () => schedule(180));
    window.addEventListener('sethistock:financial-history-ready', () => schedule(140));
    window.addEventListener('resize', () => schedule(120));

    schedule(80);
    setTimeout(apply, 220);

    window.SethiStockValuationV2VisualPolish = { apply, version: VERSION };
})();
