from pathlib import Path

# Homepage
p = Path('index.html')
s = p.read_text()

anchor = '''                    <div id="hub-continue" class="hidden mt-2 items-center gap-2 px-1 text-xs">'''
recent_block = '''                    <div id="hub-recent-companies" class="hidden mt-2 items-center gap-2 px-1 text-xs">
                        <span class="shrink-0 font-medium text-gray-400">Recent:</span>
                        <div id="hub-recent-company-items" class="flex min-w-0 flex-wrap gap-1.5"></div>
                    </div>
'''
assert anchor in s
s = s.replace(anchor, recent_block + anchor, 1)

js_anchor = '''    const hubContinue = document.getElementById('hub-continue');'''
recent_js = r'''    const hubRecentCompanies = document.getElementById('hub-recent-companies');
    const hubRecentCompanyItems = document.getElementById('hub-recent-company-items');

    function getHubRecentCompanies() {
        try {
            const saved = JSON.parse(localStorage.getItem('sethiwayRecentTickers') || '[]');
            if (!Array.isArray(saved)) return [];
            const watchlist = new Set(getHubWatchlist());
            return [...new Set(saved
                .map(item => typeof item === 'string' ? item : item?.ticker)
                .map(ticker => String(ticker || '').trim().toUpperCase())
                .filter(ticker => /^[A-Z0-9.^-]{1,20}$/.test(ticker) && !watchlist.has(ticker))
            )].slice(0, 4);
        } catch {
            return [];
        }
    }

    function renderHubRecentCompanies() {
        const tickers = getHubRecentCompanies();
        hubRecentCompanyItems.replaceChildren();
        if (!tickers.length) {
            hubRecentCompanies.classList.add('hidden');
            hubRecentCompanies.classList.remove('flex');
            return;
        }

        tickers.forEach(ticker => {
            const link = document.createElement('a');
            link.href = `sethistock.html?ticker=${encodeURIComponent(ticker)}&source=hub-recent`;
            link.textContent = ticker;
            link.className = 'rounded-full border border-gray-200 bg-white px-2.5 py-1 font-bold text-gray-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700';
            hubRecentCompanyItems.appendChild(link);
        });

        hubRecentCompanies.classList.remove('hidden');
        hubRecentCompanies.classList.add('flex');
    }

    renderHubRecentCompanies();
    window.addEventListener('storage', event => {
        if (event.key === 'sethiwayRecentTickers' || event.key === 'sethiWatchlist') renderHubRecentCompanies();
    });

'''
assert js_anchor in s
s = s.replace(js_anchor, recent_js + js_anchor, 1)

old_cards = '''                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <a href="#top" onclick="setTimeout(() => document.getElementById('launcher-ticker').focus(), 250)" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Company Search</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Search Quick Launch by company name or ticker and choose the matching security.</p>
                    </a>

                    <button type="button" onclick="openCommandPalette()" class="group rounded-2xl border border-gray-200 bg-white p-5 text-left shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Command Palette</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Use Ctrl or Cmd + K to jump to a tool, section or ticker.</p>
                    </button>

                    <a href="#top" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Continue Shortcut</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Return to the last SethiWay tool, stock or section you were using.</p>
                    </a>
                </div>'''
new_cards = '''                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <a href="#top" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Recent Companies</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Jump back to recently analysed SethiStock names from Quick Launch.</p>
                    </a>

                    <a href="#top" onclick="setTimeout(() => document.getElementById('launcher-ticker').focus(), 250)" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Company Search</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Search Quick Launch by company name or ticker and choose the matching security.</p>
                    </a>

                    <button type="button" onclick="openCommandPalette()" class="group rounded-2xl border border-gray-200 bg-white p-5 text-left shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Command Palette</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Use Ctrl or Cmd + K to jump to a tool, section or ticker.</p>
                    </button>
                </div>'''
assert old_cards in s
s = s.replace(old_cards, new_cards, 1)
assert '—' not in s
p.write_text(s)

# SethiStock
p = Path('sethistock.html')
s = p.read_text()
submit_anchor = '''        document.getElementById('search-form').addEventListener('submit', async (e) => {'''
remember_fn = r'''        function rememberRecentSethiStockTicker(ticker) {
            const cleanTicker = String(ticker || '').trim().toUpperCase();
            if (!/^[A-Z0-9.^-]{1,20}$/.test(cleanTicker)) return;
            try {
                const raw = JSON.parse(localStorage.getItem('sethiwayRecentTickers') || '[]');
                const existing = Array.isArray(raw) ? raw
                    .map(item => typeof item === 'string' ? item : item?.ticker)
                    .map(item => String(item || '').trim().toUpperCase())
                    .filter(item => /^[A-Z0-9.^-]{1,20}$/.test(item)) : [];
                const updated = [cleanTicker, ...existing.filter(item => item !== cleanTicker)].slice(0, 8);
                localStorage.setItem('sethiwayRecentTickers', JSON.stringify(updated));
            } catch (error) {}
        }

'''
assert submit_anchor in s
s = s.replace(submit_anchor, remember_fn + submit_anchor, 1)
verified = '''                state.ticker = String(data.ticker || state.ticker).toUpperCase();
                document.getElementById('ticker-input').value = state.ticker;'''
verified_new = '''                state.ticker = String(data.ticker || state.ticker).toUpperCase();
                rememberRecentSethiStockTicker(state.ticker);
                document.getElementById('ticker-input').value = state.ticker;'''
assert verified in s
s = s.replace(verified, verified_new, 1)
p.write_text(s)
