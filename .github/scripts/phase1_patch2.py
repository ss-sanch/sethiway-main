from pathlib import Path
import re
import subprocess
import tempfile


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match in {path}, found {count}")
    p.write_text(text.replace(old, new, 1))


def validate_inline_js(path):
    text = Path(path).read_text()
    blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', text, flags=re.S | re.I)
    for i, block in enumerate(blocks):
        if not block.strip():
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
            f.write(block)
            temp = f.name
        result = subprocess.run(['node', '--check', temp], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"JavaScript syntax check failed for {path} script {i}:\n{result.stderr}")


# SETHIPORTFOLIO: shared watchlist + direct research CTA ----------------------
replace_once(
    'sethiportfolio.html',
    '''                    <div class="p-5 md:p-6 border-b border-gray-100 flex items-center justify-between gap-4">
                        <div><p class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Holdings</p><h3 class="text-xl font-black">Position Detail</h3></div>
                        <span id="holdings-status" class="text-xs text-gray-400">Live market snapshot</span>
                    </div>
                    <div class="overflow-x-auto">''',
    '''                    <div class="p-5 md:p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                        <div><p class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Holdings</p><h3 class="text-xl font-black">Position Detail</h3></div>
                        <div class="flex flex-wrap items-center gap-2 sm:justify-end">
                            <span id="holdings-status" class="text-xs text-gray-400">Live market snapshot</span>
                            <a href="sethistock.html?source=portfolio" class="text-xs font-black text-blue-700 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 hover:bg-blue-100 hover:border-blue-200 transition">Research a Stock →</a>
                        </div>
                    </div>
                    <div id="portfolio-watchlist-ribbon" class="hidden px-5 py-3 border-b border-gray-100 bg-blue-50/35 flex flex-col md:flex-row md:items-center gap-2 md:gap-3">
                        <span class="text-[10px] font-black uppercase tracking-widest text-blue-700 shrink-0">Research Watchlist</span>
                        <div id="portfolio-watchlist" class="flex flex-wrap gap-2 flex-1"></div>
                        <a href="sethistock.html?source=portfolio-watchlist" class="text-[11px] font-black text-blue-700 hover:text-blue-900 shrink-0">Open SethiStock →</a>
                    </div>
                    <div class="overflow-x-auto">''',
    'portfolio watchlist ribbon',
)

replace_once(
    'sethiportfolio.html',
    '''    function renderHoldings(snapshot) {''',
    '''    function readSharedWatchlist() {
        try {
            const saved = JSON.parse(localStorage.getItem('sethiWatchlist') || '[]');
            return Array.isArray(saved) ? saved.filter(Boolean).map(t => String(t).toUpperCase()) : [];
        } catch (_) { return []; }
    }

    function renderPortfolioWatchlist() {
        const ribbon = document.getElementById('portfolio-watchlist-ribbon');
        const container = document.getElementById('portfolio-watchlist');
        if (!ribbon || !container) return;
        const watchlist = readSharedWatchlist();
        ribbon.classList.toggle('hidden', watchlist.length === 0);
        container.innerHTML = watchlist.map(t => `<a href="sethistock.html?ticker=${encodeURIComponent(t)}&source=portfolio-watchlist" class="px-2.5 py-1 rounded-full bg-white border border-blue-100 text-[11px] font-black text-blue-700 hover:border-blue-300 hover:bg-blue-50 transition">${t}</a>`).join('');
    }

    window.addEventListener('storage', event => { if (event.key === 'sethiWatchlist') renderPortfolioWatchlist(); });
    renderPortfolioWatchlist();

    function renderHoldings(snapshot) {''',
    'portfolio shared watchlist logic',
)


# SETHISTOCK: direct Add to Portfolio handoff ---------------------------------
replace_once(
    'sethistock.html',
    '''                            <button id="watchlist-btn" onclick="toggleWatchlist()" class="px-3 py-1 text-xs font-bold uppercase tracking-widest rounded-full border border-gray-200 text-gray-400 hover:text-yellow-500 hover:border-yellow-500 transition-colors">☆ Save</button>''',
    '''                            <button id="watchlist-btn" onclick="toggleWatchlist()" class="px-3 py-1 text-xs font-bold uppercase tracking-widest rounded-full border border-gray-200 text-gray-400 hover:text-yellow-500 hover:border-yellow-500 transition-colors">☆ Save</button>
                            <button type="button" onclick="openPortfolioAdminFromStock()" class="px-3 py-1 text-xs font-bold uppercase tracking-widest rounded-full border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 hover:border-blue-300 transition-colors" title="Send this ticker to the protected SethiPortfolio admin page">＋ Add to Portfolio</button>''',
    'sethistock add-to-portfolio button',
)

replace_once(
    'sethistock.html',
    '''        function updateWatchlistBtn() {''',
    '''        function openPortfolioAdminFromStock() {
            if (!state.ticker) return;
            const params = new URLSearchParams({ action: 'buy', ticker: state.ticker, source: 'sethistock' });
            window.location.href = `sethiportfolio-admin.html?${params.toString()}`;
        }

        function updateWatchlistBtn() {''',
    'sethistock portfolio handoff logic',
)


# SETHIPORTFOLIO ADMIN: pre-fill ticker sent from SethiStock ------------------
replace_once(
    'sethiportfolio-admin.html',
    '''    let allocationCorrectionPreviewPayload = '';

    const money =''',
    '''    let allocationCorrectionPreviewPayload = '';
    const inboundParams = new URLSearchParams(window.location.search);
    const inboundTicker = (inboundParams.get('ticker') || '').trim().toUpperCase();
    const inboundAction = (inboundParams.get('action') || '').trim().toLowerCase();

    async function applyInboundPortfolioIntent() {
        if (!adminSecret || !inboundTicker || inboundAction !== 'buy') return;
        el('allocation-target-symbol').value = inboundTicker;
        el('txn-symbol').value = inboundTicker;
        el('txn-side').value = 'BUY';
        resetAllocationVerification('target');
        if (el('allocation-date').value) await verifyAllocationTicker('target');
        setMessage('global-message', `${inboundTicker} was sent from SethiStock. The active-allocation target has been pre-filled; review the verified market data before recording anything.`, 'info');
        el('allocation-target-symbol').scrollIntoView({ behavior:'smooth', block:'center' });
    }

    const money =''',
    'admin inbound intent',
)

replace_once(
    'sethiportfolio-admin.html',
    '''            await refreshAdminData();
        } catch (error) {''',
    '''            await refreshAdminData();
            await applyInboundPortfolioIntent();
        } catch (error) {''',
    'admin apply inbound intent after login',
)


for required in [
    ('sethiportfolio.html', 'portfolio-watchlist-ribbon'),
    ('sethistock.html', 'openPortfolioAdminFromStock'),
    ('sethiportfolio-admin.html', 'applyInboundPortfolioIntent'),
    ('sethiquant.html', 'importPortfolioFromQuery'),
]:
    if required[1] not in Path(required[0]).read_text():
        raise SystemExit(f"Missing expected Phase 1 marker {required[1]} in {required[0]}")

for page in ['sethiportfolio.html', 'sethistock.html', 'sethiportfolio-admin.html', 'sethiquant.html']:
    validate_inline_js(page)

print('Phase 1 watchlist/admin handoff patch applied and inline JavaScript syntax validated.')
