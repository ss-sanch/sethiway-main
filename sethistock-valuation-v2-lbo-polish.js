(() => {
    'use strict';

    if (window.__sethiStockValuationV2LboPolishInstalled) return;
    window.__sethiStockValuationV2LboPolishInstalled = true;

    const VERSION = '4d16';
    let previousBodyOverflow = '';

    const valuationRoot = () => document.querySelector('#valuation');
    const detailsNode = () => document.querySelector('#valuation-lbo-details');

    function outputText(selector) {
        const text = document.querySelector(selector)?.textContent?.trim();
        return text && text !== '--' ? text : '--';
    }

    function findScenarioSection() {
        return [...valuationRoot()?.querySelectorAll('section') || []].find(section =>
            section.querySelector('h4')?.textContent?.trim() === 'Scenario Valuation'
        ) || null;
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
        if (!container || container.dataset.lboOutputPolished === VERSION) return;
        container.dataset.lboOutputPolished = VERSION;

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

    function compactLab(details) {
        if (!details || details.dataset.lboModalPolished === VERSION) return;

        const body = details.querySelector(':scope > div');
        const oldGrid = body?.querySelector(':scope > .grid');
        const oldInputs = oldGrid?.children?.[0];
        const oldOutputs = oldGrid?.children?.[1];

        if (body && oldGrid && oldInputs && oldOutputs) {
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

            body.className = 'p-5 md:p-6';
            oldGrid.className = 'grid grid-cols-1 lg:grid-cols-[minmax(0,1.55fr)_minmax(290px,.85fr)] gap-5';
            oldGrid.innerHTML = '';
            oldGrid.appendChild(left);
            oldGrid.appendChild(oldOutputs);
            polishOutputs(oldOutputs);

            const note = body.querySelector('#lbo-baseline-note');
            if (note) {
                note.className = 'mt-4 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-[11px] font-semibold leading-relaxed text-amber-800';
            }
        }

        const summary = details.querySelector(':scope > summary');
        if (summary) summary.style.display = 'none';

        details.className = 'bg-white';
        details.open = true;
        details.dataset.lboModalPolished = VERSION;
    }

    function ensureModal(details) {
        let modal = document.querySelector('#valuation-lbo-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'valuation-lbo-modal';
            modal.setAttribute('role', 'dialog');
            modal.setAttribute('aria-modal', 'true');
            modal.setAttribute('aria-labelledby', 'valuation-lbo-title');
            modal.setAttribute('aria-hidden', 'true');
            modal.style.cssText = [
                'display:none',
                'position:fixed',
                'inset:0',
                'z-index:2147482900',
                'align-items:center',
                'justify-content:center',
                'padding:24px',
                'background:rgba(15,23,42,.62)',
                'backdrop-filter:blur(4px)',
                '-webkit-backdrop-filter:blur(4px)'
            ].join(';');

            modal.innerHTML = `
                <div data-lbo-modal-card style="background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 25px 60px rgba(15,23,42,.28);max-width:1080px;width:100%;max-height:90vh;overflow-y:auto;">
                    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:18px;padding:20px 24px 16px;border-bottom:1px solid #f3f4f6;">
                        <div>
                            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                                <span style="padding:4px 8px;border-radius:6px;border:1px solid #e0e7ff;background:#eef2ff;color:#4338ca;font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:.08em;">LBO tool</span>
                                <h2 id="valuation-lbo-title" style="font-size:22px;line-height:1.2;font-weight:900;color:#111827;margin:0;">LBO Lab</h2>
                            </div>
                            <p style="font-size:13px;line-height:1.5;color:#6b7280;margin:6px 0 0;">Sponsor-return model using leverage, operating assumptions and exit multiples.</p>
                        </div>
                        <button type="button" id="valuation-lbo-close" aria-label="Close LBO Lab" style="border:0;background:transparent;color:#9ca3af;font-size:32px;line-height:1;cursor:pointer;padding:0 4px;">&times;</button>
                    </div>
                    <div data-lbo-modal-mount></div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        const mount = modal.querySelector('[data-lbo-modal-mount]');
        if (details && mount && details.parentElement !== mount) mount.appendChild(details);
        return modal;
    }

    function ensureRightStack() {
        const scenario = findScenarioSection();
        if (!scenario) return null;

        let stack = scenario.closest('[data-lbo-right-stack]');
        if (!stack) {
            const parent = scenario.parentElement;
            stack = document.createElement('div');
            stack.dataset.lboRightStack = '1';
            stack.className = 'xl:col-span-2 space-y-4 min-w-0';
            parent?.insertBefore(stack, scenario);
            stack.appendChild(scenario);
            scenario.classList.remove('xl:col-span-2');
        }
        return stack;
    }

    function ensureLauncher() {
        const stack = ensureRightStack();
        if (!stack) return null;

        let launcher = stack.querySelector('[data-lbo-launcher]');
        if (!launcher) {
            launcher = document.createElement('section');
            launcher.dataset.lboLauncher = '1';
            launcher.className = 'rounded-2xl border border-gray-200 bg-white shadow-sm p-4';
            launcher.innerHTML = `
                <div data-lbo-launcher-inner class="h-full flex flex-col justify-between gap-3">
                    <div class="flex items-start justify-between gap-3">
                        <div class="min-w-0">
                            <div class="flex items-center gap-2 flex-wrap">
                                <span class="px-2 py-1 rounded-md bg-indigo-50 border border-indigo-100 text-[10px] font-black text-indigo-700 uppercase tracking-widest">LBO tool</span>
                                <h4 class="text-base font-black text-gray-900">LBO Lab <span class="text-blue-600">→</span></h4>
                            </div>
                            <p class="text-[11px] leading-relaxed text-gray-500 mt-1">Sponsor-return lens using entry/exit multiples, leverage and cash-sweep debt paydown.</p>
                        </div>
                        <button type="button" data-open-lbo-modal class="shrink-0 px-3 py-2 rounded-lg border border-blue-100 bg-blue-50 text-[11px] font-black uppercase tracking-widest text-blue-700 hover:bg-blue-100 transition">Open Lab</button>
                    </div>
                    <div data-lbo-launcher-metrics class="grid grid-cols-2 gap-2">
                        <div class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-center">
                            <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Implied IRR</p>
                            <p data-lbo-preview-irr class="text-base font-black text-gray-900 mt-0.5">--</p>
                        </div>
                        <div class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-center">
                            <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Multiple on Money</p>
                            <p data-lbo-preview-mom class="text-base font-black text-gray-900 mt-0.5">--</p>
                        </div>
                    </div>
                </div>
            `;
            stack.appendChild(launcher);
        }
        return launcher;
    }

    function updatePreview() {
        const launcher = document.querySelector('[data-lbo-launcher]');
        if (!launcher) return;
        const irr = launcher.querySelector('[data-lbo-preview-irr]');
        const mom = launcher.querySelector('[data-lbo-preview-mom]');
        if (irr) irr.textContent = outputText('#lbo-irr');
        if (mom) mom.textContent = outputText('#lbo-mom');
    }

    function openModal() {
        const details = detailsNode();
        const modal = ensureModal(details);
        if (!details || !modal) return;

        details.style.display = '';
        details.open = true;
        window.calculateLBO?.();
        updatePreview();

        previousBodyOverflow = document.body.style.overflow;
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => modal.querySelector('#valuation-lbo-close')?.focus());
    }

    function closeModal() {
        const modal = document.querySelector('#valuation-lbo-modal');
        if (!modal) return;
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = previousBodyOverflow;
        document.querySelector('[data-open-lbo-modal]')?.focus();
    }

    function syncLayout() {
        const details = detailsNode();
        if (!details) return;

        compactLab(details);
        ensureModal(details);
        const launcher = ensureLauncher();

        if (launcher) launcher.style.display = '';

        details.style.display = '';
        details.open = true;
        window.calculateLBO?.();
        updatePreview();

        // The visual-polish module loads before this module. Re-run it after the
        // launcher is actually in the DOM so Standard view is aligned on first paint.
        requestAnimationFrame(() => {
            window.SethiStockValuationV2VisualPolish?.apply?.();
            requestAnimationFrame(() => window.SethiStockValuationV2VisualPolish?.apply?.());
        });
    }

    document.addEventListener('click', event => {
        if (event.target.closest?.('[data-open-lbo-modal]')) {
            event.preventDefault();
            event.stopPropagation();
            openModal();
            return;
        }
        if (event.target.closest?.('#valuation-lbo-close')) {
            event.preventDefault();
            closeModal();
            return;
        }

        const modal = document.querySelector('#valuation-lbo-modal');
        if (modal && event.target === modal) {
            event.preventDefault();
            closeModal();
            return;
        }

        if (event.target.closest?.('#valuation')) setTimeout(syncLayout, 40);
    }, true);

    document.addEventListener('input', event => {
        if (event.target.closest?.('#valuation-lbo-details')) {
            setTimeout(() => {
                window.calculateLBO?.();
                updatePreview();
            }, 0);
            return;
        }
        if (event.target.closest?.('#valuation')) setTimeout(syncLayout, 40);
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && document.querySelector('#valuation-lbo-modal')?.getAttribute('aria-hidden') === 'false') {
            event.preventDefault();
            closeModal();
        }
    }, true);

    window.addEventListener('sethistock:analysis-ready', () => setTimeout(syncLayout, 180));
    window.addEventListener('sethistock:financial-history-ready', () => setTimeout(syncLayout, 140));
    window.addEventListener('resize', () => setTimeout(syncLayout, 100));

    setTimeout(syncLayout, 80);
    setTimeout(syncLayout, 260);

    window.SethiStockValuationV2LboPolish = {
        apply: syncLayout,
        open: openModal,
        close: closeModal,
        version: VERSION
    };
})();