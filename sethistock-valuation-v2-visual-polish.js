(() => {
    'use strict';

    if (window.__sethiStockValuationV2VisualPolishInstalled) return;
    window.__sethiStockValuationV2VisualPolishInstalled = true;

    const VERSION = '4d15';
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

        const rightStack = scenarios.closest('[data-lbo-right-stack]');

        if (standardViewActive() && rightStack) {
            // Make the DCF card define the row height, then let the right stack fill it.
            // The compact LBO launcher keeps the right column naturally shorter, so the
            // left card no longer gains blank space while both column bottoms line up.
            grid.classList.remove('items-start');
            grid.style.alignItems = 'stretch';
            workbench.style.alignSelf = 'stretch';
            workbench.classList.remove('h-full');
            scenarios.style.alignSelf = 'start';

            rightStack.style.alignSelf = 'stretch';
            rightStack.style.height = '100%';
            rightStack.style.display = 'grid';
            rightStack.style.gridTemplateRows = 'auto minmax(0, 1fr)';
            rightStack.style.gap = '12px';

            const launcher = rightStack.querySelector('[data-lbo-launcher]');
            if (launcher) {
                launcher.style.height = '100%';
                launcher.style.display = 'flex';
                launcher.style.alignItems = 'center';
            }
        } else {
            grid.classList.add('items-start');
            grid.style.alignItems = 'start';
            workbench.style.alignSelf = 'start';
            scenarios.style.alignSelf = 'start';
            workbench.classList.remove('h-full');
            scenarios.classList.remove('h-full');

            if (rightStack) {
                rightStack.style.alignSelf = 'start';
                rightStack.style.height = 'auto';
                rightStack.style.display = 'grid';
                rightStack.style.gridTemplateRows = '';
                rightStack.style.gap = '16px';
            }
            const launcher = rightStack?.querySelector('[data-lbo-launcher]');
            if (launcher) {
                launcher.style.height = 'auto';
                launcher.style.display = '';
                launcher.style.alignItems = '';
            }
        }
    }

    function compactStandardRightColumn() {
        const valuation = root();
        if (!valuation) return;

        const scenarios = findSection(/^Scenario Valuation$/);
        const launcher = valuation.querySelector('[data-lbo-launcher]');
        const rightStack = scenarios?.closest('[data-lbo-right-stack]');
        const scenarioList = scenarios?.querySelector('#valuation-scenarios');
        const scenarioHeader = scenarios?.firstElementChild;
        const scenarioFooter = scenarioList?.nextElementSibling;
        const standard = standardViewActive();

        if (rightStack) {
            rightStack.classList.remove('space-y-4');
            rightStack.style.display = 'grid';
            rightStack.style.gap = standard ? '12px' : '16px';
        }

        if (scenarios) {
            scenarios.style.padding = standard ? '16px' : '';
        }
        if (scenarioHeader) {
            scenarioHeader.style.marginBottom = standard ? '10px' : '';
        }
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
            launcher.style.padding = standard ? '10px 12px' : '';
            const previewGrid = launcher.querySelector('[data-lbo-launcher-metrics]');
            if (previewGrid) {
                [...previewGrid.children].forEach(card => {
                    card.style.padding = standard ? '7px 10px' : '';
                });
            }
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
        compactStandardRightColumn();
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
