(() => {
    'use strict';

    if (window.__sethiStockValuationV2Installed) return;
    window.__sethiStockValuationV2Installed = true;

    const VERSION = '4d1';
    const MODEL = {
        mode: 'reverse',
        terminal: 'exit',
        sensitivity: 'exit',
        seededTicker: null,
        last: null,
        macroRealYield: 2.0
    };

    const clamp = (value, min, max) => Math.min(max, Math.max(min, Number(value)));
    const finite = value => Number.isFinite(Number(value));
    const num = (id, fallback = 0) => {
        const element = document.getElementById(id);
        const value = element ? Number(element.value) : NaN;
        return Number.isFinite(value) ? value : fallback;
    };
    const setText = (id, value) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    };
    const setValue = (id, value) => {
        const element = document.getElementById(id);
        if (element && finite(value)) element.value = Number(value);
    };
    const pct = (value, digits = 1) => finite(value) ? `${Number(value).toFixed(digits)}%` : 'N/A';
    const multiple = value => finite(value) ? `${Number(value).toFixed(1)}x` : 'N/A';
    const price = value => finite(value) && Number(value) >= 0 ? `$${Number(value).toFixed(2)}` : 'N/A';
    const money = value => {
        if (!finite(value)) return 'N/A';
        const amount = Number(value);
        const sign = amount < 0 ? '-' : '';
        const abs = Math.abs(amount);
        if (abs >= 1e12) return `${sign}$${(abs / 1e12).toFixed(2)}T`;
        if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(2)}B`;
        if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(1)}M`;
        return `${sign}$${abs.toFixed(0)}`;
    };
    const signedPct = value => finite(value) ? `${Number(value) >= 0 ? '+' : ''}${Number(value).toFixed(1)}%` : 'N/A';

    function parseCompactMoney(text) {
        const raw = String(text || '').replace(/,/g, '').trim();
        const match = raw.match(/\$?(-?[\d.]+)\s*([TMBK])?/i);
        if (!match) return null;
        const value = Number(match[1]);
        if (!Number.isFinite(value)) return null;
        const factor = ({ T: 1e12, B: 1e9, M: 1e6, K: 1e3 })[(match[2] || '').toUpperCase()] || 1;
        return value * factor;
    }

    function parseNumberText(id) {
        const raw = document.getElementById(id)?.textContent || '';
        const match = raw.replace(/,/g, '').match(/-?[\d.]+/);
        return match ? Number(match[0]) : null;
    }

    function currentState() {
        try {
            if (typeof state === 'object' && state) return state;
        } catch (_) {}
        return {};
    }

    function stockInputs() {
        const s = currentState();
        const livePrice = Number(s.price) || parseNumberText('display-price') || 0;
        const shares = Number(s.shares) || 0;
        const fcf = Number(s.fcf) || 0;
        const beta = parseNumberText('stat-beta') || 1.0;
        const marketCap = parseCompactMoney(document.getElementById('stat-mkt')?.textContent) || (livePrice > 0 && shares > 0 ? livePrice * shares : 0);
        const evEbitda = parseNumberText('stat-ev');
        const balanceLabel = String(document.getElementById('stat-balance-label')?.textContent || '').toLowerCase();
        const balanceRatioRaw = parseNumberText('stat-balance');
        const netDebtEbitda = finite(balanceRatioRaw) ? (balanceLabel.includes('cash') ? -Math.abs(balanceRatioRaw) : Number(balanceRatioRaw)) : null;

        let ebitda = Number(s.ebitda) || 0;
        if (!(ebitda > 0) && marketCap > 0 && finite(evEbitda) && finite(netDebtEbitda)) {
            const denominator = Number(evEbitda) - Number(netDebtEbitda);
            if (denominator > 0.5) ebitda = marketCap / denominator;
        }
        if (!(ebitda > 0) && fcf > 0) ebitda = fcf / 0.55;

        const netDebt = ebitda > 0 && finite(netDebtEbitda) ? ebitda * Number(netDebtEbitda) : 0;
        return {
            ticker: String(s.ticker || document.getElementById('display-ticker')?.textContent || '').trim().toUpperCase(),
            price: livePrice,
            shares,
            fcf,
            beta,
            marketCap,
            evEbitda,
            netDebtEbitda,
            netDebt,
            ebitda
        };
    }

    function markup() {
        return `
            <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-4 mb-5 border-b border-gray-200 pb-4">
                <div>
                    <div class="flex items-center gap-2">
                        <h3 class="text-2xl font-black text-gray-900">Advanced Valuation</h3>
                        <span class="px-2 py-1 rounded-md bg-indigo-50 border border-indigo-100 text-[9px] font-black text-indigo-700 uppercase tracking-widest">Model v2</span>
                        <button type="button" id="valuation-info-btn" class="inline-flex h-7 w-7 items-center justify-center rounded-full text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition" aria-label="Explain Advanced Valuation" title="Explain Advanced Valuation">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </button>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">What is priced in, what could the business be worth, and which assumptions matter?</p>
                </div>
                <div class="text-[10px] font-black text-emerald-700 uppercase tracking-widest">Client-side · no additional valuation request</div>
            </div>

            <input id="disc-num" type="hidden" value="7.0"><input id="disc-sld" type="hidden" value="7.0">

            <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
                ${snapshotCard('Current Price', 'val-snap-price', 'text-gray-900')}
                ${snapshotCard('Implied FCF CAGR', 'val-snap-implied', 'text-blue-700')}
                ${snapshotCard('Base Fair Value', 'val-snap-base', 'text-gray-900')}
                ${snapshotCard('Upside / Downside', 'val-snap-upside', 'text-gray-900')}
                ${snapshotCard('Discount Rate', 'val-snap-rate', 'text-indigo-700')}
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
                <section class="xl:col-span-3 bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
                        <div>
                            <h4 class="text-lg font-black text-gray-900">DCF Workbench</h4>
                            <p id="valuation-mode-copy" class="text-xs text-gray-500 mt-1">Solve the FCF growth rate today's share price requires.</p>
                        </div>
                        <div class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1 self-start">
                            <button type="button" data-valuation-mode="reverse" class="valuation-mode-btn px-4 py-2 rounded-md text-xs font-black transition">Reverse DCF</button>
                            <button type="button" data-valuation-mode="forward" class="valuation-mode-btn px-4 py-2 rounded-md text-xs font-black transition">Forward DCF</button>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div class="rounded-xl border border-gray-200 bg-gray-50 p-4">
                            <p class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-3">Core assumptions</p>
                            <div class="grid grid-cols-2 gap-3">
                                ${inputBox('Projection Years', 'val-years', 5, 1, 15, 1, '')}
                                <div id="val-growth-field">${inputBox('FCF Growth', 'val-growth', 10, -40, 80, 0.5, '%')}</div>
                                ${inputBox('Exit Multiple', 'val-exit-multiple', 18, 3, 60, 0.5, 'x')}
                                ${inputBox('Terminal Growth', 'val-perp-growth', 2.5, -1, 7, 0.1, '%')}
                            </div>
                            <div class="mt-4">
                                <p class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-2">Terminal method</p>
                                <div class="grid grid-cols-2 gap-2">
                                    <button type="button" data-terminal="exit" class="valuation-terminal-btn rounded-lg border px-3 py-2 text-xs font-black transition">Exit Multiple</button>
                                    <button type="button" data-terminal="gordon" class="valuation-terminal-btn rounded-lg border px-3 py-2 text-xs font-black transition">Gordon Growth</button>
                                </div>
                            </div>
                            <div id="val-reverse-result" class="mt-4 rounded-xl border border-blue-100 bg-blue-50 p-4">
                                <p class="text-[10px] font-black uppercase tracking-widest text-blue-600">Market-implied expectation</p>
                                <div class="flex items-end justify-between gap-3 mt-1">
                                    <div><span id="val-implied-growth" class="text-3xl font-black text-blue-700">--</span><span class="text-sm font-bold text-blue-600 ml-1">FCF CAGR</span></div>
                                    <span id="val-implied-context" class="text-[10px] font-bold text-blue-700 text-right">--</span>
                                </div>
                            </div>
                        </div>

                        <div class="rounded-xl border border-gray-200 bg-white p-4">
                            <div class="flex items-center justify-between gap-3 mb-3">
                                <div>
                                    <p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Discount-rate engine</p>
                                    <p class="text-xs text-gray-500 mt-1">Cost of Equity is the default for the current FCF definition; indicative WACC is shown alongside it.</p>
                                </div>
                                <div class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1">
                                    <button type="button" data-rate-basis="coe" class="valuation-rate-btn rounded-md px-2.5 py-1.5 text-[10px] font-black">CoE</button>
                                    <button type="button" data-rate-basis="wacc" class="valuation-rate-btn rounded-md px-2.5 py-1.5 text-[10px] font-black">WACC</button>
                                </div>
                            </div>
                            <div class="grid grid-cols-2 gap-3">
                                ${inputBox('Real Yield', 'val-real-yield', 2.0, -2, 8, 0.1, '%')}
                                ${inputBox('Inflation Exp.', 'val-inflation', 2.5, 0, 8, 0.1, '%')}
                                ${inputBox('Beta', 'val-beta', 1.0, 0.1, 3, 0.05, 'x')}
                                ${inputBox('Equity Risk Prem.', 'val-erp', 5.0, 2, 10, 0.1, '%')}
                                ${inputBox('Debt Weight', 'val-debt-weight', 10, 0, 70, 1, '%')}
                                ${inputBox('Pre-tax Cost Debt', 'val-cost-debt', 5.5, 1, 20, 0.1, '%')}
                                ${inputBox('Tax Rate', 'val-tax', 21, 0, 40, 1, '%')}
                            </div>
                            <div class="grid grid-cols-3 gap-2 mt-4 text-center">
                                ${miniStat('Nominal Rf', 'val-rf')}
                                ${miniStat('Cost Equity', 'val-coe')}
                                ${miniStat('Indicative WACC', 'val-wacc')}
                            </div>
                            <p id="val-rate-note" class="text-[10px] text-gray-400 mt-3 leading-relaxed">Macro real yield is inherited from the existing SethiMacro bridge when available. WACC uses an editable debt-weight proxy and should be treated as indicative until a full FCFF capital-structure model is added.</p>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3 mt-5">
                        ${targetCard('Exit Multiple DCF', 'val-target-exit', 'text-blue-700')}
                        ${targetCard('Gordon Growth DCF', 'val-target-gordon', 'text-emerald-700')}
                    </div>
                </section>

                <section class="xl:col-span-2 bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
                    <div class="flex items-start justify-between gap-3 mb-4">
                        <div>
                            <h4 class="text-lg font-black text-gray-900">Scenario Valuation</h4>
                            <p class="text-xs text-gray-500 mt-1">Bear, Base and Bull flex growth, discount rate and terminal assumptions coherently.</p>
                        </div>
                        <span id="val-scenario-method" class="px-2 py-1 rounded-md bg-gray-100 border border-gray-200 text-[9px] font-black text-gray-500 uppercase tracking-widest">Exit Multiple</span>
                    </div>
                    <div id="valuation-scenarios" class="space-y-3"></div>
                    <div class="mt-5 border-t border-gray-100 pt-4">
                        <div class="flex items-center justify-between text-xs"><span class="font-bold text-gray-500">Base assumptions</span><span id="val-base-assumptions" class="font-black text-gray-900">--</span></div>
                    </div>
                </section>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">
                <section class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
                    <div class="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-4">
                        <div>
                            <h4 class="text-lg font-black text-gray-900">Sensitivity Analysis</h4>
                            <p class="text-xs text-gray-500 mt-1">25 live valuations around the selected base assumptions.</p>
                        </div>
                        <div class="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1 self-start">
                            <button type="button" data-sensitivity="exit" class="valuation-sensitivity-btn rounded-md px-3 py-1.5 text-[10px] font-black">Rate × Exit</button>
                            <button type="button" data-sensitivity="gordon" class="valuation-sensitivity-btn rounded-md px-3 py-1.5 text-[10px] font-black">Rate × Growth</button>
                        </div>
                    </div>
                    <div id="valuation-sensitivity" class="overflow-x-auto"></div>
                </section>

                <section class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
                    <div class="mb-3">
                        <h4 class="text-lg font-black text-gray-900">Fair Value Range</h4>
                        <p class="text-xs text-gray-500 mt-1">Ranges now come from actual model sensitivities and scenarios rather than arbitrary ±15% bands.</p>
                    </div>
                    <div id="football-field" class="w-full h-[330px]"></div>
                </section>
            </div>

            <details id="valuation-lbo-details" class="mt-6 bg-white rounded-2xl border border-gray-200 shadow-sm group">
                <summary class="cursor-pointer list-none p-6 flex items-center justify-between gap-4">
                    <div>
                        <h4 class="text-lg font-black text-gray-900">LBO Lab <span class="text-blue-600">→</span></h4>
                        <p class="text-xs text-gray-500 mt-1">A simplified sponsor-return model using EBITDA, separate entry/exit multiples and cash-sweep debt paydown.</p>
                    </div>
                    <span class="text-xs font-black text-gray-400 uppercase tracking-widest group-open:text-blue-600">Open / Close</span>
                </summary>
                <div class="border-t border-gray-100 p-6">
                    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
                        <div class="xl:col-span-2 grid grid-cols-2 md:grid-cols-3 gap-3">
                            ${inputBox('Entry Multiple', 'lbo-entry-mult', 15, 3, 40, 0.5, 'x')}
                            ${inputBox('Exit Multiple', 'lbo-exit-mult', 15, 3, 40, 0.5, 'x')}
                            ${inputBox('Debt Funding', 'lbo-debt-pct', 55, 0, 85, 1, '%')}
                            ${inputBox('Interest Rate', 'lbo-interest', 7, 1, 20, 0.25, '%')}
                            ${inputBox('EBITDA Growth', 'lbo-ebitda-growth', 8, -20, 40, 0.5, '%')}
                            ${inputBox('FCF Conversion', 'lbo-fcf-conversion', 55, 5, 95, 1, '%')}
                            ${inputBox('Holding Period', 'lbo-years', 5, 1, 10, 1, ' yrs')}
                        </div>
                        <div class="grid grid-cols-2 xl:grid-cols-1 gap-3">
                            ${targetCard('Implied IRR', 'lbo-irr', 'text-gray-900')}
                            ${targetCard('Multiple on Money', 'lbo-mom', 'text-gray-900')}
                            ${miniStat('Exit Debt', 'lbo-exit-debt')}
                            ${miniStat('Debt Paid Down', 'lbo-debt-paid')}
                        </div>
                    </div>
                    <div id="lbo-baseline-note" class="mt-4 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-[10px] font-semibold text-amber-800"></div>
                </div>
            </details>

            <p id="dcf-warning" class="hidden mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-bold text-red-600">Insufficient positive FCF, share count or price to run the valuation engine.</p>
        `;
    }

    function snapshotCard(label, id, colour) {
        return `<div class="rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm"><p class="text-[9px] font-black uppercase tracking-widest text-gray-400">${label}</p><p id="${id}" class="mt-1 text-lg md:text-xl font-black ${colour}">--</p></div>`;
    }
    function targetCard(label, id, colour) {
        return `<div class="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-center"><p class="text-[9px] font-black uppercase tracking-widest text-gray-400">${label}</p><p id="${id}" class="mt-1 text-2xl font-black ${colour}">--</p></div>`;
    }
    function miniStat(label, id) {
        return `<div class="rounded-lg border border-gray-100 bg-gray-50 p-2"><p class="text-[8px] font-black uppercase tracking-widest text-gray-400">${label}</p><p id="${id}" class="mt-1 text-sm font-black text-gray-900">--</p></div>`;
    }
    function inputBox(label, id, value, min, max, step, suffix) {
        return `<label class="block"><span class="block text-[9px] font-black uppercase tracking-widest text-gray-400 mb-1.5">${label}</span><div class="relative"><input id="${id}" type="number" min="${min}" max="${max}" step="${step}" value="${value}" class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 pr-10 text-sm font-black text-gray-900 outline-none focus:border-blue-300 focus:ring-2 focus:ring-blue-100"><span class="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-black text-gray-400">${suffix}</span></div></label>`;
    }

    function buildUI() {
        const root = document.getElementById('valuation');
        if (!root) return false;
        root.innerHTML = markup();
        root.dataset.valuationV2 = VERSION;
        ensureInfoModal();
        bindUI();
        syncButtons();
        return true;
    }

    function ensureInfoModal() {
        if (document.getElementById('valuation-v2-info-modal')) return;
        const modal = document.createElement('div');
        modal.id = 'valuation-v2-info-modal';
        modal.className = 'hidden fixed inset-0 z-[170] flex items-center justify-center bg-black/60 backdrop-blur-sm';
        modal.innerHTML = `<div class="bg-white rounded-2xl shadow-2xl p-7 max-w-3xl w-full mx-4 max-h-[88vh] overflow-y-auto"><div class="flex items-start justify-between gap-5 border-b border-gray-100 pb-4 mb-5"><div><h2 class="text-2xl font-black text-gray-900">Advanced Valuation 2.0</h2><p class="text-sm text-gray-500 mt-1">A model guide for interpreting the new valuation workbench.</p></div><button type="button" id="valuation-info-close" class="text-3xl text-gray-400 hover:text-red-500">&times;</button></div><div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700 leading-relaxed"><div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-blue-700 mb-1">Reverse DCF</h4><p>Starts with today's share price and solves for the constant FCF CAGR needed to justify that price under your discount-rate and terminal assumptions.</p></div><div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-emerald-700 mb-1">Forward DCF</h4><p>Starts with your FCF growth assumption and calculates implied fair value using both an exit-multiple and Gordon Growth terminal value.</p></div><div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-indigo-700 mb-1">Discount Rate</h4><p>Cost of Equity uses nominal risk-free rate plus Beta × ERP. Indicative WACC additionally reflects an editable debt weight, cost of debt and tax shield.</p></div><div class="rounded-xl border border-gray-200 p-4"><h4 class="font-black text-gray-900 mb-1">Scenarios & Sensitivity</h4><p>Bear/Base/Bull and both 5×5 matrices are computed locally from the same assumptions. No extra valuation endpoint is called.</p></div></div><div class="mt-5 rounded-xl border border-amber-100 bg-amber-50 p-4 text-xs text-amber-800"><strong>Model note:</strong> SethiStock's current FCF is Operating Cash Flow minus CapEx, so Cost of Equity is the default discount basis. The WACC view is included as an indicative capital-structure lens rather than presented as a full FCFF model.</div></div>`;
        document.body.appendChild(modal);
        const close = () => modal.classList.add('hidden');
        modal.addEventListener('click', event => { if (event.target === modal) close(); });
        modal.querySelector('#valuation-info-close')?.addEventListener('click', close);
    }

    function bindUI() {
        document.getElementById('valuation-info-btn')?.addEventListener('click', () => document.getElementById('valuation-v2-info-modal')?.classList.remove('hidden'));
        document.querySelectorAll('[data-valuation-mode]').forEach(button => button.addEventListener('click', () => {
            MODEL.mode = button.dataset.valuationMode;
            syncButtons();
            render();
        }));
        document.querySelectorAll('[data-terminal]').forEach(button => button.addEventListener('click', () => {
            MODEL.terminal = button.dataset.terminal;
            syncButtons();
            render();
        }));
        document.querySelectorAll('[data-sensitivity]').forEach(button => button.addEventListener('click', () => {
            MODEL.sensitivity = button.dataset.sensitivity;
            syncButtons();
            renderSensitivity();
        }));
        document.querySelectorAll('[data-rate-basis]').forEach(button => button.addEventListener('click', () => {
            MODEL.rateBasis = button.dataset.rateBasis;
            syncButtons();
            render();
        }));
        document.getElementById('valuation')?.addEventListener('input', event => {
            if (event.target.matches('input[type="number"]')) render();
        });
        document.getElementById('valuation-lbo-details')?.addEventListener('toggle', renderLBO);
    }

    function syncButtons() {
        const setActive = (selector, key, value) => document.querySelectorAll(selector).forEach(button => {
            const active = button.dataset[key] === value;
            button.className = `${button.className.replace(/\sbg-blue-600|\stext-white|\sborder-blue-600|\sbg-white|\stext-gray-500/g, '')} ${active ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-500 border-gray-200'}`;
        });
        setActive('[data-valuation-mode]', 'valuationMode', MODEL.mode);
        setActive('[data-terminal]', 'terminal', MODEL.terminal);
        setActive('[data-sensitivity]', 'sensitivity', MODEL.sensitivity);
        MODEL.rateBasis = MODEL.rateBasis || 'coe';
        setActive('[data-rate-basis]', 'rateBasis', MODEL.rateBasis);
        const growth = document.getElementById('val-growth-field');
        if (growth) growth.classList.toggle('opacity-40', MODEL.mode === 'reverse');
        if (growth) growth.querySelector('input')?.toggleAttribute('disabled', MODEL.mode === 'reverse');
        setText('valuation-mode-copy', MODEL.mode === 'reverse' ? `Solve the FCF growth rate today's share price requires.` : 'Project your own FCF growth assumption into an implied fair value.');
        setText('val-scenario-method', MODEL.terminal === 'exit' ? 'Exit Multiple' : 'Gordon Growth');
    }

    function seedFromTicker(force = false) {
        const stock = stockInputs();
        if (!stock.ticker || (!force && MODEL.seededTicker === stock.ticker)) return;
        MODEL.seededTicker = stock.ticker;

        setValue('val-beta', clamp(stock.beta || 1, 0.1, 3));
        const legacyRate = num('disc-num', 7.0);
        MODEL.macroRealYield = clamp(legacyRate - 5.0, -1, 6);
        setValue('val-real-yield', MODEL.macroRealYield);

        const observedGrowth = parseNumberText('stat-rev-growth');
        const growth = finite(observedGrowth) ? clamp(observedGrowth, 3, 25) : 10;
        setValue('val-growth', growth);
        setValue('lbo-ebitda-growth', clamp(growth * 0.65, 2, 15));

        if (finite(stock.evEbitda) && stock.evEbitda > 3) {
            const exit = clamp(stock.evEbitda, 5, 35);
            setValue('val-exit-multiple', exit);
            setValue('lbo-entry-mult', exit);
            setValue('lbo-exit-mult', exit);
        }

        if (stock.marketCap > 0 && stock.netDebt > 0) {
            const debtWeight = clamp(stock.netDebt / (stock.marketCap + stock.netDebt) * 100, 3, 45);
            setValue('val-debt-weight', debtWeight);
        } else {
            setValue('val-debt-weight', 8);
        }
        if (stock.ebitda > 0 && stock.fcf > 0) {
            setValue('lbo-fcf-conversion', clamp(stock.fcf / stock.ebitda * 100, 15, 85));
        }
        render();
    }

    function rateEngine() {
        const realYield = num('val-real-yield', MODEL.macroRealYield);
        const inflation = num('val-inflation', 2.5);
        const beta = num('val-beta', 1.0);
        const erp = num('val-erp', 5.0);
        const debtWeight = clamp(num('val-debt-weight', 10), 0, 90) / 100;
        const costDebt = num('val-cost-debt', 5.5) / 100;
        const tax = clamp(num('val-tax', 21), 0, 60) / 100;
        const nominalRf = (realYield + inflation) / 100;
        const costEquity = nominalRf + beta * (erp / 100);
        const wacc = (1 - debtWeight) * costEquity + debtWeight * costDebt * (1 - tax);
        const selected = MODEL.rateBasis === 'wacc' ? wacc : costEquity;
        setText('val-rf', pct(nominalRf * 100));
        setText('val-coe', pct(costEquity * 100));
        setText('val-wacc', pct(wacc * 100));
        return { realYield, inflation, nominalRf, beta, erp, debtWeight, costDebt, tax, costEquity, wacc, selected };
    }

    function dcfValue({ fcf, shares, growth, rate, years, terminal = 'exit', exitMultiple, perpGrowth }) {
        if (!(fcf > 0) || !(shares > 0) || !(rate > -0.95) || years < 1) return null;
        let projected = fcf;
        let pv = 0;
        for (let year = 1; year <= years; year += 1) {
            projected *= (1 + growth);
            pv += projected / Math.pow(1 + rate, year);
        }
        let terminalValue = null;
        if (terminal === 'gordon') {
            if (!(rate > perpGrowth)) return null;
            terminalValue = projected * (1 + perpGrowth) / (rate - perpGrowth);
        } else {
            terminalValue = projected * exitMultiple;
        }
        const equityValue = pv + terminalValue / Math.pow(1 + rate, years);
        const implied = equityValue / shares;
        return Number.isFinite(implied) && implied >= 0 ? implied : null;
    }

    function solveImpliedGrowth(stock, rate, years, terminal, exitMultiple, perpGrowth) {
        if (!(stock.price > 0) || !(stock.fcf > 0) || !(stock.shares > 0)) return null;
        const valueAt = growth => dcfValue({ fcf: stock.fcf, shares: stock.shares, growth, rate, years, terminal, exitMultiple, perpGrowth });
        let low = -0.80;
        let high = 1.50;
        let lowValue = valueAt(low);
        let highValue = valueAt(high);
        if (!finite(lowValue) || !finite(highValue)) return null;
        if (stock.price < lowValue || stock.price > highValue) return null;
        for (let iteration = 0; iteration < 80; iteration += 1) {
            const mid = (low + high) / 2;
            const value = valueAt(mid);
            if (!finite(value)) return null;
            if (value < stock.price) low = mid;
            else high = mid;
        }
        return (low + high) / 2;
    }

    function scenarioSet(stock, rate, years, growth, exitMultiple, perpGrowth) {
        const configs = [
            { name: 'Bear', tone: 'red', growth: growth - 0.05, rate: rate + 0.0125, multiple: exitMultiple - 2, perp: perpGrowth - 0.005 },
            { name: 'Base', tone: 'blue', growth, rate, multiple: exitMultiple, perp: perpGrowth },
            { name: 'Bull', tone: 'green', growth: growth + 0.05, rate: Math.max(0.01, rate - 0.0125), multiple: exitMultiple + 2, perp: perpGrowth + 0.005 }
        ];
        return configs.map(config => {
            const value = dcfValue({
                fcf: stock.fcf,
                shares: stock.shares,
                growth: config.growth,
                rate: config.rate,
                years,
                terminal: MODEL.terminal,
                exitMultiple: Math.max(1, config.multiple),
                perpGrowth: config.perp
            });
            return { ...config, value, upside: stock.price > 0 && finite(value) ? (value / stock.price - 1) * 100 : null };
        });
    }

    function renderScenarios(scenarios) {
        const container = document.getElementById('valuation-scenarios');
        if (!container) return;
        const tones = {
            red: ['border-red-100', 'bg-red-50', 'text-red-700'],
            blue: ['border-blue-100', 'bg-blue-50', 'text-blue-700'],
            green: ['border-emerald-100', 'bg-emerald-50', 'text-emerald-700']
        };
        container.innerHTML = scenarios.map(scenario => {
            const tone = tones[scenario.tone];
            return `<div class="rounded-xl border ${tone[0]} ${tone[1]} p-4"><div class="flex items-center justify-between gap-3"><div><p class="text-[10px] font-black uppercase tracking-widest ${tone[2]}">${scenario.name}</p><p class="text-2xl font-black text-gray-900 mt-1">${price(scenario.value)}</p></div><div class="text-right"><p class="text-sm font-black ${finite(scenario.upside) && scenario.upside >= 0 ? 'text-emerald-600' : 'text-red-600'}">${signedPct(scenario.upside)}</p><p class="text-[9px] font-bold text-gray-400 uppercase tracking-widest">vs current</p></div></div><div class="grid grid-cols-3 gap-2 mt-3 text-[9px] font-bold text-gray-500"><span>Growth ${pct(scenario.growth * 100)}</span><span>Rate ${pct(scenario.rate * 100)}</span><span>${MODEL.terminal === 'exit' ? `Exit ${multiple(scenario.multiple)}` : `PGR ${pct(scenario.perp * 100)}`}</span></div></div>`;
        }).join('');
    }

    function matrixValues(stock, baseRate, years, baseGrowth, exitMultiple, perpGrowth, mode) {
        const rates = [-0.02, -0.01, 0, 0.01, 0.02].map(delta => Math.max(0.005, baseRate + delta));
        const columns = mode === 'exit'
            ? [-2, -1, 0, 1, 2].map(delta => Math.max(1, exitMultiple + delta))
            : [-0.01, -0.005, 0, 0.005, 0.01].map(delta => perpGrowth + delta);
        const rows = rates.map(rate => columns.map(column => dcfValue({
            fcf: stock.fcf,
            shares: stock.shares,
            growth: baseGrowth,
            rate,
            years,
            terminal: mode,
            exitMultiple: mode === 'exit' ? column : exitMultiple,
            perpGrowth: mode === 'gordon' ? column : perpGrowth
        })));
        return { rates, columns, rows };
    }

    function renderSensitivity() {
        if (!MODEL.last) return;
        const { stock, rate, years, growth, exitMultiple, perpGrowth } = MODEL.last;
        const matrix = matrixValues(stock, rate, years, growth, exitMultiple, perpGrowth, MODEL.sensitivity);
        const container = document.getElementById('valuation-sensitivity');
        if (!container) return;
        const header = matrix.columns.map(column => `<th class="px-2 py-2 text-[10px] font-black text-gray-500 bg-gray-50">${MODEL.sensitivity === 'exit' ? multiple(column) : pct(column * 100)}</th>`).join('');
        const rows = matrix.rows.map((values, rowIndex) => `<tr><th class="sticky left-0 bg-gray-50 px-2 py-2 text-[10px] font-black text-gray-500">${pct(matrix.rates[rowIndex] * 100)}</th>${values.map(value => {
            const upside = stock.price > 0 && finite(value) ? (value / stock.price - 1) * 100 : null;
            const tone = !finite(upside) ? 'bg-gray-50 text-gray-400' : upside >= 15 ? 'bg-emerald-50 text-emerald-700' : upside <= -15 ? 'bg-red-50 text-red-700' : 'bg-white text-gray-700';
            return `<td class="border border-gray-100 px-2 py-2 text-center ${tone}"><div class="text-xs font-black">${price(value)}</div><div class="text-[9px] font-bold opacity-70">${signedPct(upside)}</div></td>`;
        }).join('')}</tr>`).join('');
        container.innerHTML = `<table class="w-full border-collapse"><thead><tr><th class="px-2 py-2 text-[9px] font-black uppercase tracking-widest text-gray-400 bg-gray-50">Rate ↓</th>${header}</tr></thead><tbody>${rows}</tbody></table>`;
    }

    function renderFootballField(scenarios, exitMatrix, gordonMatrix, stock) {
        const element = document.getElementById('football-field');
        if (!element || typeof Plotly === 'undefined') return;
        const values = array => array.flat().filter(finite).map(Number);
        const exitValues = values(exitMatrix.rows);
        const gordonValues = values(gordonMatrix.rows);
        const scenarioValues = scenarios.map(item => item.value).filter(finite).map(Number);
        const low52 = Number(currentState()?.stats?.fiftyTwoWeekLow);
        const high52 = Number(currentState()?.stats?.fiftyTwoWeekHigh);
        const ranges = [];
        if (finite(low52) && finite(high52) && high52 > low52) ranges.push({ label: '52W Range', low: low52, high: high52, colour: '#94a3b8' });
        if (scenarioValues.length) ranges.push({ label: 'Bear → Bull', low: Math.min(...scenarioValues), high: Math.max(...scenarioValues), colour: '#2563eb' });
        if (exitValues.length) ranges.push({ label: 'Exit Sensitivity', low: Math.min(...exitValues), high: Math.max(...exitValues), colour: '#0f766e' });
        if (gordonValues.length) ranges.push({ label: 'Gordon Sensitivity', low: Math.min(...gordonValues), high: Math.max(...gordonValues), colour: '#16a34a' });
        if (!ranges.length) {
            Plotly.purge(element);
            element.innerHTML = '<div class="h-full flex items-center justify-center text-sm font-bold text-gray-400">Valuation ranges unavailable</div>';
            return;
        }
        const trace = {
            type: 'bar', orientation: 'h',
            y: ranges.map(item => item.label),
            x: ranges.map(item => item.high - item.low),
            base: ranges.map(item => item.low),
            marker: { color: ranges.map(item => item.colour) },
            text: ranges.map(item => `${price(item.low)} – ${price(item.high)}`),
            hovertemplate: '<b>%{y}</b><br>%{text}<extra></extra>',
            width: 0.46
        };
        const baseScenario = scenarios.find(item => item.name === 'Base');
        const shapes = stock.price > 0 ? [{ type: 'line', x0: stock.price, x1: stock.price, y0: -0.55, y1: ranges.length - 0.45, line: { color: '#ef4444', width: 2, dash: 'dash' } }] : [];
        if (baseScenario && finite(baseScenario.value)) shapes.push({ type: 'line', x0: baseScenario.value, x1: baseScenario.value, y0: -0.55, y1: ranges.length - 0.45, line: { color: '#2563eb', width: 2, dash: 'dot' } });
        Plotly.react(element, [trace], {
            margin: { t: 16, b: 35, l: 115, r: 10 }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
            xaxis: { showgrid: true, gridcolor: '#f1f5f9', tickprefix: '$', zeroline: false },
            yaxis: { showgrid: false, tickfont: { size: 11, color: '#475569' } },
            shapes,
            annotations: stock.price > 0 ? [{ x: stock.price, y: ranges.length - 0.35, text: 'Current', showarrow: false, font: { size: 9, color: '#ef4444' } }] : []
        }, { displayModeBar: false, responsive: true });
    }

    function renderLBO() {
        const details = document.getElementById('valuation-lbo-details');
        if (!details?.open) return;
        const stock = stockInputs();
        const ebitda = stock.ebitda;
        if (!(ebitda > 0)) {
            setText('lbo-irr', 'N/A'); setText('lbo-mom', 'N/A');
            setText('lbo-baseline-note', 'A usable EBITDA baseline is unavailable for this security.');
            return;
        }
        const entryMult = num('lbo-entry-mult', stock.evEbitda || 15);
        const exitMult = num('lbo-exit-mult', entryMult);
        const debtPct = clamp(num('lbo-debt-pct', 55), 0, 95) / 100;
        const interest = num('lbo-interest', 7) / 100;
        const growth = num('lbo-ebitda-growth', 8) / 100;
        const conversion = clamp(num('lbo-fcf-conversion', 55), 0, 100) / 100;
        const years = Math.max(1, Math.round(num('lbo-years', 5)));
        const entryEV = ebitda * entryMult;
        const entryDebt = entryEV * debtPct;
        const entryEquity = entryEV - entryDebt;
        let currentDebt = entryDebt;
        let currentEbitda = ebitda;
        for (let year = 1; year <= years; year += 1) {
            currentEbitda *= (1 + growth);
            const interestExpense = currentDebt * interest;
            const cashSweep = Math.max(0, currentEbitda * conversion - interestExpense);
            currentDebt = Math.max(0, currentDebt - cashSweep);
        }
        const exitEV = currentEbitda * exitMult;
        const exitEquity = exitEV - currentDebt;
        const mom = entryEquity > 0 && exitEquity > 0 ? exitEquity / entryEquity : null;
        const irr = finite(mom) ? (Math.pow(mom, 1 / years) - 1) * 100 : null;
        setText('lbo-irr', pct(irr));
        setText('lbo-mom', finite(mom) ? `${mom.toFixed(2)}x` : 'N/A');
        setText('lbo-exit-debt', money(currentDebt));
        setText('lbo-debt-paid', money(entryDebt - currentDebt));
        const source = finite(stock.evEbitda) && finite(stock.netDebtEbitda) ? 'EBITDA is derived from live Market Cap, EV/EBITDA and Net Debt/EBITDA.' : 'EBITDA uses the best available fallback from current FCF.';
        setText('lbo-baseline-note', `${source} This remains a simplified sponsor-return model: FCF conversion is used as the cash-sweep proxy and does not model detailed working capital, taxes or mandatory amortisation.`);
    }

    function render() {
        const root = document.getElementById('valuation');
        if (!root?.dataset.valuationV2) return;
        const stock = stockInputs();
        const warning = document.getElementById('dcf-warning');
        const valid = stock.price > 0 && stock.fcf > 0 && stock.shares > 0;
        warning?.classList.toggle('hidden', valid);
        if (!valid) {
            ['val-snap-price','val-snap-implied','val-snap-base','val-snap-upside','val-target-exit','val-target-gordon'].forEach(id => setText(id, 'N/A'));
            return;
        }

        const legacyRate = num('disc-num', 7.0);
        if (Math.abs((legacyRate - 5.0) - MODEL.macroRealYield) > 0.05 && legacyRate > 2 && legacyRate < 20) {
            MODEL.macroRealYield = clamp(legacyRate - 5.0, -2, 8);
            setValue('val-real-yield', MODEL.macroRealYield);
        }

        const rates = rateEngine();
        const rate = rates.selected;
        const years = Math.max(1, Math.round(num('val-years', 5)));
        const forwardGrowth = num('val-growth', 10) / 100;
        const exitMultiple = num('val-exit-multiple', 18);
        const perpGrowth = num('val-perp-growth', 2.5) / 100;
        const impliedGrowth = solveImpliedGrowth(stock, rate, years, MODEL.terminal, exitMultiple, perpGrowth);
        const modelGrowth = MODEL.mode === 'reverse' && finite(impliedGrowth) ? impliedGrowth : forwardGrowth;
        const exitValue = dcfValue({ fcf: stock.fcf, shares: stock.shares, growth: modelGrowth, rate, years, terminal: 'exit', exitMultiple, perpGrowth });
        const gordonValue = dcfValue({ fcf: stock.fcf, shares: stock.shares, growth: modelGrowth, rate, years, terminal: 'gordon', exitMultiple, perpGrowth });
        const baseValue = MODEL.terminal === 'exit' ? exitValue : gordonValue;
        const upside = finite(baseValue) ? (baseValue / stock.price - 1) * 100 : null;
        const scenarios = scenarioSet(stock, rate, years, modelGrowth, exitMultiple, perpGrowth);
        const exitMatrix = matrixValues(stock, rate, years, modelGrowth, exitMultiple, perpGrowth, 'exit');
        const gordonMatrix = matrixValues(stock, rate, years, modelGrowth, exitMultiple, perpGrowth, 'gordon');

        MODEL.last = { stock, rates, rate, years, growth: modelGrowth, exitMultiple, perpGrowth, impliedGrowth, exitValue, gordonValue, baseValue, scenarios };

        setText('val-snap-price', price(stock.price));
        setText('val-snap-implied', finite(impliedGrowth) ? pct(impliedGrowth * 100) : 'Outside range');
        setText('val-snap-base', price(baseValue));
        setText('val-snap-upside', signedPct(upside));
        setText('val-snap-rate', `${pct(rate * 100)} ${MODEL.rateBasis === 'wacc' ? 'WACC' : 'CoE'}`);
        setText('val-implied-growth', finite(impliedGrowth) ? pct(impliedGrowth * 100) : 'N/A');
        setText('val-implied-context', `${years}Y · ${pct(rate * 100)} · ${MODEL.terminal === 'exit' ? multiple(exitMultiple) : pct(perpGrowth * 100)}`);
        setText('val-target-exit', price(exitValue));
        setText('val-target-gordon', price(gordonValue));
        setText('val-base-assumptions', `${pct(modelGrowth * 100)} growth · ${pct(rate * 100)} rate`);

        renderScenarios(scenarios);
        renderSensitivity();
        renderFootballField(scenarios, exitMatrix, gordonMatrix, stock);
        renderLBO();
        syncButtons();
    }

    function install() {
        if (!buildUI()) return;
        window.calculateDCF = render;
        window.drawFootballField = () => render();
        window.renderLiveSensitivityMatrix = renderSensitivity;
        window.calculateLBO = renderLBO;
        window.SethiStockValuationV2 = { render, seedFromTicker, version: VERSION };
        window.addEventListener('sethistock:analysis-ready', () => setTimeout(() => seedFromTicker(true), 80));
        window.addEventListener('sethistock:financial-history-ready', () => setTimeout(() => render(), 40));
        setTimeout(() => seedFromTicker(true), 0);
    }

    install();
})();
