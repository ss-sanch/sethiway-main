from pathlib import Path
import re

drivers = Path('sethistock-company-drivers.js')
text = drivers.read_text()

replacement = r'''    function ensureStyles() {
        if (qs('#sethistock-driver-styles')) return;
        const style = document.createElement('style');
        style.id = 'sethistock-driver-styles';
        style.textContent = `
            #company-drivers { overscroll-behavior:contain; }
            #company-drivers.hidden { display:none !important; }
            #driver-dialog { width:min(1240px,calc(100vw - 48px)); height:min(720px,calc(100vh - 72px)); max-height:calc(100vh - 48px); }
            #driver-dialog-body { min-height:0; overflow-y:auto; }
            .driver-period-btn.active { background:#2563eb; color:#fff; border-color:#2563eb; }
            .driver-card { min-width:0; overflow:hidden; }
            .driver-card .modebar { display:none !important; }
            .driver-card [id^="driver-chart-"] { width:100% !important; max-width:100% !important; overflow:hidden !important; }
            .driver-card [id^="driver-chart-"] .js-plotly-plot,
            .driver-card [id^="driver-chart-"] .plot-container,
            .driver-card [id^="driver-chart-"] .svg-container { width:100% !important; max-width:100% !important; }
            @media (max-width: 720px) {
                #driver-dialog { width:calc(100vw - 24px); height:calc(100vh - 32px); max-height:calc(100vh - 32px); }
            }
            @media (prefers-reduced-motion: reduce) { .driver-loading-pulse { animation:none !important; } }
        `;
        document.head.appendChild(style);
    }

    function closeDrivers(returnToRevenue = false) {
        if (controller) controller.abort();
        controller = null;
        const section = qs('#company-drivers');
        if (section) section.classList.add('hidden');
        document.body.classList.remove('modal-active');
        if (returnToRevenue) {
            const revenueCard = qs('[data-financial-card="ind-rev"]');
            if (revenueCard) requestAnimationFrame(() => revenueCard.scrollIntoView({ behavior: 'smooth', block: 'center' }));
        }
    }

    function ensureUI() {
        ensureStyles();
        if (qs('#company-drivers')) return;

        const section = document.createElement('section');
        section.id = 'company-drivers';
        section.className = 'hidden fixed inset-0 z-[220] flex items-center justify-center p-3 sm:p-6 md:p-9';
        section.innerHTML = `
            <button id="driver-modal-backdrop" type="button" aria-label="Close revenue drivers" style="position:absolute;inset:0;border:0;background:rgba(15,23,42,.48);cursor:default;"></button>
            <div id="driver-dialog" role="dialog" aria-modal="true" aria-label="Revenue drivers" class="relative z-10 bg-white border border-gray-200 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
                <header class="shrink-0 border-b border-gray-200 bg-white px-5 md:px-6 py-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div class="min-w-0">
                        <p class="text-[9px] font-black text-blue-600 uppercase tracking-[0.18em] mb-1">Company Drivers · Revenue Engine</p>
                        <h2 id="driver-view-title" class="text-xl md:text-2xl font-black tracking-tight text-gray-900 truncate">Revenue Drivers</h2>
                        <p id="driver-theme" class="text-xs text-gray-500 mt-1 line-clamp-1">Revenue segments and direct operating drivers from verified company filings.</p>
                    </div>
                    <div class="flex items-center gap-3 shrink-0">
                        <div id="driver-period-controls" class="flex space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200" aria-label="Revenue driver period">
                            <button type="button" class="driver-period-btn active px-3.5 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-driver-period="quarterly">Quarterly</button>
                            <button type="button" class="driver-period-btn px-3.5 py-1.5 text-xs font-bold rounded-md text-gray-600 transition" data-driver-period="annual">Annual</button>
                        </div>
                        <button id="driver-close-button" type="button" aria-label="Close revenue drivers" class="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-500 hover:text-gray-900 hover:border-gray-300 transition text-xl">×</button>
                    </div>
                </header>

                <div id="driver-dialog-body" class="flex-1 px-5 md:px-6 py-4 bg-gray-50/70">
                    <div class="flex items-center justify-between gap-3 mb-3 min-h-[18px]">
                        <p id="driver-status" class="text-[9px] font-bold uppercase tracking-widest text-gray-400">Open a supported stock to load revenue drivers</p>
                    </div>
                    <div id="driver-summary" class="hidden mb-3 rounded-xl border border-blue-100 bg-blue-50/70 px-3.5 py-2 text-[10px] text-blue-900"></div>
                    <div id="driver-empty" class="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
                        <p class="text-sm font-bold text-gray-600">Revenue-driver histories will appear here.</p>
                        <p class="text-xs text-gray-400 mt-1">Only verified filing histories are charted; missing periods are never estimated.</p>
                    </div>
                    <div id="driver-chart-grid" class="hidden grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4"></div>
                    <div id="driver-unavailable" class="hidden mt-4 rounded-xl border border-gray-200 bg-white px-4 py-3"></div>
                </div>
            </div>`;
        document.body.appendChild(section);

        qs('#driver-modal-backdrop', section)?.addEventListener('click', () => closeDrivers(false));
        qs('#driver-close-button', section)?.addEventListener('click', () => closeDrivers(false));
        qsa('.driver-period-btn', section).forEach(button => {
            button.addEventListener('click', () => {
                const next = button.dataset.driverPeriod;
                if (!PERIODS.includes(next) || next === activePeriod) return;
                activePeriod = next;
                syncPeriodButtons();
                if (activeTicker && latestRegistry && latestCoverage) {
                    renderDrivers(activeTicker, latestRegistry, latestCoverage, next).catch(() => null);
                }
            });
        });
    }

    function syncPeriodButtons()'''

pattern = re.compile(r"    function ensureStyles\(\) \{.*?    function syncPeriodButtons\(\)", re.S)
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'Expected one ensureUI block replacement, got {count}')

old_open = '''        const section = qs('#company-drivers');
        section?.classList.remove('hidden');
        document.body.classList.add('modal-active');
        activePeriod = 'quarterly';
        syncPeriodButtons();
        await loadCompanyDrivers(symbol);'''
new_open = '''        const section = qs('#company-drivers');
        section?.classList.remove('hidden');
        document.body.classList.add('modal-active');
        activePeriod = 'quarterly';
        syncPeriodButtons();
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        await loadCompanyDrivers(symbol);'''
if old_open not in text:
    raise SystemExit('openDrivers block not found')
text = text.replace(old_open, new_open, 1)
drivers.write_text(text)

stability = Path('sethistock-ui-stability.js')
st = stability.read_text()
old_layout = '''                    height: DRIVER_CHART_HEIGHT,
                    autosize: false,
                    margin: { t: 8, r: 8, b: 34, l: 46 },'''
new_layout = '''                    height: DRIVER_CHART_HEIGHT,
                    width: undefined,
                    autosize: true,
                    margin: { t: 8, r: 8, b: 34, l: 46 },'''
if old_layout not in st:
    raise SystemExit('compact Plotly layout block not found')
st = st.replace(old_layout, new_layout, 1)
stability.write_text(st)

history = Path('sethiway-history.js')
ht = history.read_text()
if "sethistock-ui-stability.js?v=4" not in ht or "sethistock-company-drivers.js?v=4b1" not in ht:
    raise SystemExit('Expected cache-version markers not found')
ht = ht.replace("sethistock-ui-stability.js?v=4", "sethistock-ui-stability.js?v=5", 1)
ht = ht.replace("sethistock-company-drivers.js?v=4b1", "sethistock-company-drivers.js?v=4b2", 1)
history.write_text(ht)
