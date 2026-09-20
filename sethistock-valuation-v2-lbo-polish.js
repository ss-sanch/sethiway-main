(() => {
    'use strict';

    if (window.__sethiStockValuationV2LboPolishInstalled) return;
    window.__sethiStockValuationV2LboPolishInstalled = true;

    const VERSION = '4d10';

    function ensureStyles() {
        if (document.querySelector('#sethistock-lbo-polish-styles')) return;
        const style = document.createElement('style');
        style.id = 'sethistock-lbo-polish-styles';
        style.textContent = `
            #valuation-lbo-details {
                max-width: 1120px;
                margin-left: auto;
                margin-right: auto;
                overflow: hidden;
            }
            #valuation-lbo-details > summary {
                padding: 16px 20px !important;
            }
            #valuation-lbo-details .lbo-polish-main {
                display: grid;
                grid-template-columns: minmax(0, 1fr);
                gap: 20px;
            }
            #valuation-lbo-details .lbo-input-card,
            #valuation-lbo-details .lbo-output-card {
                min-width: 0;
            }
            @media (min-width: 1024px) {
                #valuation-lbo-details .lbo-polish-main {
                    grid-template-columns: minmax(0, 1.55fr) minmax(290px, .85fr);
                }
            }
        `;
        document.head.appendChild(style);
    }

    function outputText(selector) {
        const node = document.querySelector(selector);
        const text = node?.textContent?.trim();
        return text && text !== '--' ? text : '--';
    }

    function updateSummary(details) {
        const state = details.open ? 'Close lab' : 'Open lab';
        const stateNode = details.querySelector('[data-lbo-state]');
        if (stateNode) stateNode.textContent = state;

        const irr = details.querySelector('#lbo-preview-irr');
        const mom = details.querySelector('#lbo-preview-mom');
        if (irr) irr.textContent = outputText('#lbo-irr');
        if (mom) mom.textContent = outputText('#lbo-mom');
    }

    function fieldById(id) {
        return document.querySelector('#' + id)?.closest('label') || null;
    }

    function makeInputGroup(title, copy, ids, columns = 2) {
        const card = document.createElement('section');
        card.className = 'lbo-input-card rounded-xl border border-gray-200 bg-gray-50 p-4';
        card.innerHTML = `
            <div class="mb-3">
                <p class="text-sm font-black text-gray-900">${title}</p>
                <p class="text-[11px] text-gray-500 mt-0.5">${copy}</p>
            </div>
            <div data-lbo-fields class="grid gap-3"></div>
        `;
        const grid = card.querySelector('[data-lbo-fields]');
        grid.style.gridTemplateColumns = columns === 3
            ? 'repeat(3, minmax(0, 1fr))'
            : 'repeat(2, minmax(0, 1fr))';
        ids.forEach(id => {
            const field = fieldById(id);
            if (field) grid.appendChild(field);
        });
        return card;
    }

    function polishOutputs(container) {
        if (!container) return;

        const irrCard = document.querySelector('#lbo-irr')?.closest('div.rounded-xl');
        const momCard = document.querySelector('#lbo-mom')?.closest('div.rounded-xl');
        const exitDebtCard = document.querySelector('#lbo-exit-debt')?.closest('div.rounded-lg');
        const debtPaidCard = document.querySelector('#lbo-debt-paid')?.closest('div.rounded-lg');

        container.className = 'lbo-output-card rounded-xl border border-gray-200 bg-white p-4';
        container.innerHTML = `
            <div class="mb-3">
                <p class="text-sm font-black text-gray-900">Sponsor returns</p>
                <p class="text-[11px] text-gray-500 mt-0.5">Headline equity-return outputs from the assumptions on the left.</p>
            </div>
            <div data-lbo-primary class="grid grid-cols-2 gap-3"></div>
            <div data-lbo-secondary class="grid grid-cols-2 gap-3 mt-3"></div>
        `;

        const primary = container.querySelector('[data-lbo-primary]');
        const secondary = container.querySelector('[data-lbo-secondary]');

        [irrCard, momCard].forEach(card => {
            if (!card) return;
            card.className = 'rounded-xl border border-gray-200 bg-gray-50 px-3 py-4 text-center';
            primary.appendChild(card);
        });
        [exitDebtCard, debtPaidCard].forEach(card => {
            if (!card) return;
            card.className = 'rounded-lg border border-gray-100 bg-gray-50 p-3';
            secondary.appendChild(card);
        });
    }

    function polishLbo() {
        ensureStyles();

        const details = document.querySelector('#valuation-lbo-details');
        if (!details || details.dataset.lboPolished === VERSION) {
            if (details) updateSummary(details);
            return;
        }

        details.dataset.lboPolished = VERSION;
        details.className = 'mt-6 bg-white rounded-2xl border border-gray-200 shadow-sm group';

        const summary = details.querySelector(':scope > summary');
        if (summary) {
            summary.className = 'cursor-pointer list-none flex items-center justify-between gap-4';
            summary.innerHTML = `
                <div class="min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                        <span class="px-2 py-1 rounded-md bg-indigo-50 border border-indigo-100 text-[10px] font-black text-indigo-700 uppercase tracking-widest">Advanced tool</span>
                        <h4 class="text-lg font-black text-gray-900">LBO Lab <span class="text-blue-600">→</span></h4>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">Compact sponsor-return model using entry/exit multiples, leverage and cash-sweep debt paydown.</p>
                </div>
                <div class="flex items-center gap-3 shrink-0">
                    <div class="hidden sm:flex items-center gap-2">
                        <div class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-center min-w-[82px]">
                            <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">IRR</p>
                            <p id="lbo-preview-irr" class="text-sm font-black text-gray-900">--</p>
                        </div>
                        <div class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-center min-w-[82px]">
                            <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">MoM</p>
                            <p id="lbo-preview-mom" class="text-sm font-black text-gray-900">--</p>
                        </div>
                    </div>
                    <span data-lbo-state class="text-xs font-black text-blue-600 uppercase tracking-widest">Open lab</span>
                </div>
            `;
        }

        const body = details.querySelector(':scope > div');
        const oldGrid = body?.querySelector(':scope > .grid');
        const oldInputs = oldGrid?.children?.[0];
        const oldOutputs = oldGrid?.children?.[1];

        if (body && oldGrid && oldInputs && oldOutputs) {
            body.className = 'border-t border-gray-100 p-5 md:p-6';

            const left = document.createElement('div');
            left.className = 'space-y-4';
            left.appendChild(makeInputGroup(
                'Deal structure',
                'Set valuation, leverage and the investment horizon.',
                ['lbo-entry-mult', 'lbo-exit-mult', 'lbo-debt-pct', 'lbo-years'],
                2
            ));
            left.appendChild(makeInputGroup(
                'Operating assumptions',
                'Flex financing cost, EBITDA growth and cash conversion.',
                ['lbo-interest', 'lbo-ebitda-growth', 'lbo-fcf-conversion'],
                3
            ));

            oldGrid.className = 'lbo-polish-main';
            oldGrid.innerHTML = '';
            oldGrid.appendChild(left);
            oldGrid.appendChild(oldOutputs);
            polishOutputs(oldOutputs);

            const note = body.querySelector('#lbo-baseline-note');
            if (note) {
                note.className = 'mt-4 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-[11px] font-semibold leading-relaxed text-amber-800';
            }
        }

        details.addEventListener('toggle', () => {
            setTimeout(() => updateSummary(details), 0);
        });

        details.addEventListener('input', () => {
            setTimeout(() => updateSummary(details), 0);
        });

        updateSummary(details);
    }

    document.addEventListener('click', event => {
        if (event.target.closest?.('#valuation')) setTimeout(polishLbo, 40);
    });
    document.addEventListener('input', event => {
        if (event.target.closest?.('#valuation-lbo-details')) setTimeout(polishLbo, 40);
    });

    window.addEventListener('sethistock:analysis-ready', () => setTimeout(polishLbo, 180));
    window.addEventListener('sethistock:financial-history-ready', () => setTimeout(polishLbo, 140));
    window.addEventListener('resize', () => setTimeout(polishLbo, 100));

    setTimeout(polishLbo, 80);
    setTimeout(polishLbo, 240);

    window.SethiStockValuationV2LboPolish = { apply: polishLbo, version: VERSION };
})();