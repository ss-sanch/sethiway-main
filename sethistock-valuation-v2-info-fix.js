(() => {
    'use strict';

    if (window.__sethiStockValuationV2InfoFixInstalled) return;
    window.__sethiStockValuationV2InfoFixInstalled = true;

    const VERSION = '4d8';
    let previousBodyOverflow = '';

    function buildModal() {
        document.getElementById('valuation-v2-info-modal')?.remove();

        const modal = document.createElement('div');
        modal.id = 'valuation-v2-info-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'valuation-info-title');
        modal.setAttribute('aria-hidden', 'true');
        modal.style.cssText = [
            'display:none',
            'position:fixed',
            'inset:0',
            'z-index:2147483000',
            'align-items:center',
            'justify-content:center',
            'padding:24px',
            'background:rgba(15,23,42,0.62)',
            'backdrop-filter:blur(4px)',
            '-webkit-backdrop-filter:blur(4px)'
        ].join(';');

        modal.innerHTML = `
            <div data-valuation-info-card style="background:#fff;border:1px solid #e5e7eb;border-radius:16px;box-shadow:0 25px 60px rgba(15,23,42,.28);padding:28px;max-width:768px;width:100%;max-height:88vh;overflow-y:auto;color:#111827;">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:20px;border-bottom:1px solid #f3f4f6;padding-bottom:16px;margin-bottom:20px;">
                    <div>
                        <h2 id="valuation-info-title" style="font-size:24px;line-height:1.2;font-weight:900;margin:0;">SethiStock Valuation Model</h2>
                        <p style="font-size:14px;line-height:1.5;color:#6b7280;margin:6px 0 0;">How Standard and Advanced views use the same underlying DCF engine.</p>
                    </div>
                    <button type="button" id="valuation-info-close" aria-label="Close valuation guide" style="border:0;background:transparent;color:#9ca3af;font-size:32px;line-height:1;cursor:pointer;padding:0 4px;">&times;</button>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;font-size:14px;line-height:1.55;color:#374151;">
                    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;"><h4 style="font-weight:900;color:#1d4ed8;margin:0 0 4px;">Standard</h4><p style="margin:0;">A forward DCF with the core assumptions exposed, plus scenario, sensitivity and fair-value range outputs.</p></div>
                    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;"><h4 style="font-weight:900;color:#4338ca;margin:0 0 4px;">Advanced</h4><p style="margin:0;">Adds Reverse DCF, terminal-method controls, the full discount-rate engine, WACC and the LBO Lab.</p></div>
                    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;"><h4 style="font-weight:900;color:#047857;margin:0 0 4px;">Market-implied growth</h4><p style="margin:0;">Solves for the constant FCF CAGR required for the DCF to match today's share price under the selected rate and terminal assumptions.</p></div>
                    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;"><h4 style="font-weight:900;color:#111827;margin:0 0 4px;">Scenarios & sensitivity</h4><p style="margin:0;">Bear/Base/Bull cases and the 5×5 matrices are recomputed locally from the same assumptions rather than using arbitrary valuation bands.</p></div>
                </div>
                <div style="margin-top:20px;border:1px solid #fde68a;background:#fffbeb;border-radius:12px;padding:16px;font-size:12px;line-height:1.55;color:#92400e;"><strong>Model note:</strong> Current FCF is Operating Cash Flow minus CapEx, so Cost of Equity is the default discount basis. WACC remains an indicative capital-structure view rather than a full FCFF model.</div>
            </div>`;

        document.body.appendChild(modal);
        return modal;
    }

    function ensureModal() {
        return document.getElementById('valuation-v2-info-modal') || buildModal();
    }

    function openModal() {
        const modal = ensureModal();
        previousBodyOverflow = document.body.style.overflow;
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => modal.querySelector('#valuation-info-close')?.focus());
    }

    function closeModal() {
        const modal = document.getElementById('valuation-v2-info-modal');
        if (!modal) return;
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = previousBodyOverflow;
        document.body.classList.remove('modal-active');
        document.getElementById('valuation-info-btn')?.focus();
    }

    document.addEventListener('click', event => {
        const infoButton = event.target.closest?.('#valuation-info-btn');
        if (infoButton) {
            event.preventDefault();
            event.stopImmediatePropagation();
            openModal();
            return;
        }

        const closeButton = event.target.closest?.('#valuation-info-close');
        if (closeButton) {
            event.preventDefault();
            event.stopImmediatePropagation();
            closeModal();
            return;
        }

        const modal = document.getElementById('valuation-v2-info-modal');
        if (modal && event.target === modal) {
            event.preventDefault();
            closeModal();
        }
    }, true);

    document.addEventListener('keydown', event => {
        const modal = document.getElementById('valuation-v2-info-modal');
        if (event.key === 'Escape' && modal?.getAttribute('aria-hidden') === 'false') {
            event.preventDefault();
            closeModal();
        }
    }, true);

    buildModal();

    window.SethiStockValuationV2InfoFix = {
        open: openModal,
        close: closeModal,
        rebuild: buildModal,
        version: VERSION
    };
})();