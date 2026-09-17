(() => {
    'use strict';

    if (window.__sethiStockValuationV2PolishInstalled) return;
    window.__sethiStockValuationV2PolishInstalled = true;

    const VERSION = '4d2';
    let timer = null;

    const numberFromText = value => {
        const match = String(value || '').replace(/,/g, '').match(/-?[\d.]+/);
        return match ? Number(match[0]) : null;
    };

    const isReverseMode = () => document.querySelector('[data-valuation-mode="reverse"]')?.classList.contains('bg-blue-600') === true;

    function removeLegacyValuationUI() {
        const legacyMatrixTitle = [...document.querySelectorAll('h3')].find(node =>
            node.textContent.trim() === 'Live DCF Sensitivity Matrix'
        );
        const legacyMatrix = legacyMatrixTitle?.closest('.bg-gray-50');
        if (legacyMatrix && !legacyMatrix.closest('#valuation')) legacyMatrix.remove();

        const legacyLboTitle = [...document.querySelectorAll('h3')].find(node =>
            node.textContent.trim() === 'Mini-LBO (Leveraged Buyout) Model'
        );
        const legacyLbo = legacyLboTitle?.closest('.bg-gray-50');
        if (legacyLbo && !legacyLbo.closest('#valuation')) legacyLbo.remove();
    }

    function polishCopyAndLayout() {
        const root = document.getElementById('valuation');
        if (!root?.dataset.valuationV2) return;

        const clientSideNote = [...root.querySelectorAll('div')].find(node =>
            node.textContent.trim() === 'Client-side · no additional valuation request'
        );
        if (clientSideNote) clientSideNote.textContent = 'Uses loaded data · zero extra requests';

        const sections = [...root.querySelectorAll('section')];
        const workbench = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'DCF Workbench');
        const scenarios = sections.find(section => section.querySelector('h4')?.textContent.trim() === 'Scenario Valuation');
        const topGrid = workbench?.parentElement;
        if (topGrid) topGrid.classList.add('items-start');
        if (scenarios) scenarios.classList.add('self-start');

        const baseValue = document.getElementById('val-snap-base');
        const baseLabel = baseValue?.previousElementSibling;
        if (baseLabel) baseLabel.textContent = isReverseMode() ? 'Implied Value Check' : 'Base Fair Value';
    }

    function polishRealYield() {
        const input = document.getElementById('val-real-yield');
        if (!input) return;
        const value = Number(input.value);
        if (Number.isFinite(value)) input.value = value.toFixed(1);
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

    function suppressDuplicateBaseMarker() {
        if (!isReverseMode() || typeof Plotly === 'undefined') return;
        const field = document.getElementById('football-field');
        if (!field?._fullLayout?.shapes || field._fullLayout.shapes.length < 2) return;

        const current = numberFromText(document.getElementById('val-snap-price')?.textContent);
        const base = numberFromText(document.getElementById('val-snap-base')?.textContent);
        if (!Number.isFinite(current) || !Number.isFinite(base)) return;

        const tolerance = Math.max(0.01, Math.abs(current) * 0.0001);
        if (Math.abs(current - base) <= tolerance) {
            Plotly.relayout(field, { 'shapes[1].visible': false });
        }
    }

    function applyPolish() {
        removeLegacyValuationUI();
        polishCopyAndLayout();
        polishRealYield();
        polishGrowthField();
        suppressDuplicateBaseMarker();
    }

    function schedulePolish(delay = 0) {
        clearTimeout(timer);
        timer = setTimeout(applyPolish, delay);
    }

    document.addEventListener('click', event => {
        const button = event.target.closest?.('[data-valuation-mode]');
        if (!button) return;
        const input = document.getElementById('val-growth');
        if (!input) return;

        if (button.dataset.valuationMode === 'reverse') {
            if (!input.dataset.forwardGrowth) input.dataset.forwardGrowth = input.value;
        } else if (button.dataset.valuationMode === 'forward' && input.dataset.forwardGrowth) {
            input.value = input.dataset.forwardGrowth;
            delete input.dataset.forwardGrowth;
        }
        schedulePolish(0);
    }, true);

    document.addEventListener('input', event => {
        if (event.target.id === 'val-growth' && !isReverseMode()) {
            delete event.target.dataset.forwardGrowth;
        }
        if (event.target.closest?.('#valuation')) schedulePolish(0);
    });

    document.addEventListener('click', event => {
        if (event.target.closest?.('#valuation')) schedulePolish(0);
    });

    document.addEventListener('toggle', event => {
        if (event.target.id === 'valuation-lbo-details') schedulePolish(0);
    }, true);

    window.addEventListener('sethistock:analysis-ready', () => schedulePolish(120));
    window.addEventListener('sethistock:financial-history-ready', () => schedulePolish(80));
    window.addEventListener('resize', () => schedulePolish(80));

    schedulePolish(0);
    setTimeout(applyPolish, 150);

    window.SethiStockValuationV2Polish = { apply: applyPolish, version: VERSION };
})();
