(() => {
    'use strict';

    if (window.__sethiStockValuationV2InfoFixInstalled) return;
    window.__sethiStockValuationV2InfoFixInstalled = true;

    const VERSION = '4d7';

    function ensureModal() {
        let modal = document.getElementById('valuation-v2-info-modal');
        if (modal) return modal;

        modal = document.createElement('div');
        modal.id = 'valuation-v2-info-modal';
        modal.className = 'hidden fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'valuation-info-title');
        modal.setAttribute('aria-hidden', 'true');
        modal.innerHTML = `
            <div data-valuation-info-card class="bg-white rounded-2xl shadow-2xl p-7 max-w-3xl w-full mx-4 max-h-[88vh] overflow-y-auto">
                <div class="flex items-start justify-between gap-5 border-b border-gray-100 pb-4 mb-5">
                    <div>
                        <h2 id="valuation-info-title" class="text-2xl font-black text-gray-900">SethiStock Valuation Model</h2>
                        <p class="text-sm text-gray-500 mt-1">How Standard and Advanced views use the same underlying DCF engine.</p>
                    </div>
                    <button type="button" id="valuation-info-close" class="text-3xl leading-none text-gray-400 hover:text-red-500" aria-label="Close valuation guide">&times;</button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700 leading-relaxed">
                    <div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-blue-700 mb-1">Standard</h4><p>A forward DCF with the core assumptions exposed, plus scenario, sensitivity and fair-value range outputs.</p></div>
                    <div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-indigo-700 mb-1">Advanced</h4><p>Adds Reverse DCF, terminal-method controls, the full discount-rate engine, WACC and the LBO Lab.</p></div>
                    <div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-emerald-700 mb-1">Market-implied growth</h4><p>Solves for the constant FCF CAGR required for the DCF to match today's share price under the selected rate and terminal assumptions.</p></div>
                    <div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-gray-900 mb-1">Scenarios & sensitivity</h4><p>Bear/Base/Bull cases and the 5×5 matrices are recomputed locally from the same assumptions rather than using arbitrary valuation bands.</p></div>
                </div>
                <div class="mt-5 rounded-xl border border-amber-100 bg-amber-50 p-4 text-xs text-amber-800"><strong>Model note:</strong> Current FCF is Operating Cash Flow minus CapEx, so Cost of Equity is the default discount basis. WACC remains an indicative capital-structure view rather than a full FCFF model.</div>
            </div>`;
        document.body.appendChild(modal);
        return modal;
    }

    function openModal() {
        const modal = ensureModal();
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        modal.style.position = 'fixed';
        modal.style.inset = '0';
        modal.style.zIndex = '9999';
        modal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-active');
        requestAnimationFrame(() => modal.querySelector('#valuation-info-close')?.focus());
    }

    function closeModal() {
        const modal = document.getElementById('valuation-v2-info-modal');
        if (!modal) return;
        modal.classList.add('hidden');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-active');
        document.getElementById('valuation-info-btn')?.focus();
    }

    document.addEventListener('click', event => {
        if (event.target.closest?.('#valuation-info-btn')) {
            event.preventDefault();
            event.stopPropagation();
            openModal();
            return;
        }
        if (event.target.closest?.('#valuation-info-close')) {
            event.preventDefault();
            closeModal();
            return;
        }
        const modal = document.getElementById('valuation-v2-info-modal');
        if (modal && event.target === modal) closeModal();
    }, true);

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && document.getElementById('valuation-v2-info-modal')?.getAttribute('aria-hidden') === 'false') closeModal();
    });

    const modal = ensureModal();
    if (modal.classList.contains('hidden')) modal.style.display = 'none';

    window.SethiStockValuationV2InfoFix = { open: openModal, close: closeModal, version: VERSION };
})();