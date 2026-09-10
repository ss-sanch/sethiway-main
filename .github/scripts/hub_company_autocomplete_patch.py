from pathlib import Path

p=Path('index.html')
s=p.read_text()

old_form='''                    <form id="stock-launcher" class="flex flex-col sm:flex-row gap-2">
                        <label for="launcher-ticker" class="sr-only">Ticker</label>
                        <input id="launcher-ticker" name="ticker" type="text" autocomplete="off" spellcheck="false" maxlength="20" placeholder="Ticker, e.g. AAPL or ASML.AS" class="min-w-0 flex-1 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-gray-900 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100">
                        <button type="submit" class="shrink-0 rounded-xl bg-gray-900 px-5 py-3 text-sm font-black text-white transition hover:bg-blue-600">Open in SethiStock →</button>
                    </form>'''
new_form='''                    <form id="stock-launcher" class="flex flex-col sm:flex-row gap-2">
                        <label for="launcher-ticker" class="sr-only">Company or ticker</label>
                        <div class="relative min-w-0 flex-1">
                            <input id="launcher-ticker" name="ticker" type="text" autocomplete="off" spellcheck="false" maxlength="60" placeholder="Company or ticker, e.g. Microsoft or MSFT" aria-autocomplete="list" aria-controls="launcher-suggestions" aria-expanded="false" class="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-900 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100">
                            <div id="launcher-suggestions" class="hidden absolute left-0 right-0 top-full z-40 mt-2 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl" role="listbox" aria-label="Company suggestions"></div>
                        </div>
                        <button type="submit" class="shrink-0 rounded-xl bg-gray-900 px-5 py-3 text-sm font-black text-white transition hover:bg-blue-600">Open in SethiStock →</button>
                    </form>'''
assert old_form in s
s=s.replace(old_form,new_form,1)
s=s.replace('''                    <p id="launcher-error" class="hidden mt-2 px-1 text-xs font-semibold text-red-600">Enter a valid ticker symbol.</p>''','''                    <p id="launcher-error" class="hidden mt-2 px-1 text-xs font-semibold text-red-600">Choose a company or enter a valid ticker.</p>''',1)

old_js='''    const launcherForm = document.getElementById('stock-launcher');
    const launcherTicker = document.getElementById('launcher-ticker');
    const launcherError = document.getElementById('launcher-error');

    launcherForm.addEventListener('submit', event => {
        event.preventDefault();
        const ticker = launcherTicker.value.trim().toUpperCase();
        const validTicker = /^[A-Z0-9.^-]{1,20}$/.test(ticker);

        if (!validTicker) {
            launcherError.classList.remove('hidden');
            launcherTicker.focus();
            return;
        }

        launcherError.classList.add('hidden');
        window.location.href = `sethistock.html?ticker=${encodeURIComponent(ticker)}&source=hub`;
    });

    launcherTicker.addEventListener('input', () => launcherError.classList.add('hidden'));
'''
new_js=r'''    const launcherForm = document.getElementById('stock-launcher');
    const launcherTicker = document.getElementById('launcher-ticker');
    const launcherError = document.getElementById('launcher-error');
    const launcherSuggestions = document.getElementById('launcher-suggestions');
    let launcherSuggestionTimer = null;
    let launcherSuggestionController = null;
    let launcherSuggestionItems = [];
    let launcherSuggestionSelection = -1;

    function hideLauncherSuggestions() {
        launcherSuggestions.classList.add('hidden');
        launcherSuggestions.replaceChildren();
        launcherSuggestionItems = [];
        launcherSuggestionSelection = -1;
        launcherTicker.setAttribute('aria-expanded', 'false');
    }

    function openLauncherTicker(ticker, source = 'hub-company-search') {
        const cleanTicker = String(ticker || '').trim().toUpperCase();
        if (!/^[A-Z0-9.^-]{1,20}$/.test(cleanTicker)) return;
        window.location.href = `sethistock.html?ticker=${encodeURIComponent(cleanTicker)}&source=${encodeURIComponent(source)}`;
    }

    function renderLauncherSuggestions(items) {
        launcherSuggestionItems = items;
        launcherSuggestions.replaceChildren();
        if (!items.length) {
            hideLauncherSuggestions();
            return;
        }

        items.forEach((item, index) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.setAttribute('role', 'option');
            button.className = `flex w-full items-center gap-3 px-4 py-3 text-left transition ${index === launcherSuggestionSelection ? 'bg-blue-50' : 'hover:bg-gray-50'}`;

            const symbol = document.createElement('span');
            symbol.className = 'w-20 shrink-0 text-sm font-black text-gray-900';
            symbol.textContent = item.symbol;

            const name = document.createElement('span');
            name.className = 'min-w-0 flex-1 truncate text-sm text-gray-500';
            name.textContent = item.name || 'Security';

            const arrow = document.createElement('span');
            arrow.className = 'shrink-0 text-sm font-bold text-gray-300';
            arrow.textContent = '→';

            button.append(symbol, name, arrow);
            button.addEventListener('mouseenter', () => { launcherSuggestionSelection = index; });
            button.addEventListener('click', () => openLauncherTicker(item.symbol));
            launcherSuggestions.appendChild(button);
        });
        launcherSuggestions.classList.remove('hidden');
        launcherTicker.setAttribute('aria-expanded', 'true');
    }

    async function fetchLauncherSuggestions(query) {
        const cleanQuery = query.trim();
        if (cleanQuery.length < 2) {
            hideLauncherSuggestions();
            return;
        }
        if (launcherSuggestionController) launcherSuggestionController.abort();
        launcherSuggestionController = new AbortController();
        try {
            const response = await fetch(`https://sethistock-api.onrender.com/autocomplete?q=${encodeURIComponent(cleanQuery)}`, { signal: launcherSuggestionController.signal });
            if (!response.ok) throw new Error('Autocomplete unavailable');
            const data = await response.json();
            const items = Array.isArray(data.results) ? data.results
                .map(item => ({ symbol: String(item.symbol || '').trim().toUpperCase(), name: String(item.name || '').trim() }))
                .filter(item => /^[A-Z0-9.^-]{1,20}$/.test(item.symbol))
                .slice(0, 5) : [];
            renderLauncherSuggestions(items);
        } catch (error) {
            if (error.name !== 'AbortError') hideLauncherSuggestions();
        }
    }

    launcherForm.addEventListener('submit', event => {
        event.preventDefault();
        const ticker = launcherTicker.value.trim().toUpperCase();
        const validTicker = /^[A-Z0-9.^-]{1,20}$/.test(ticker);
        if (!validTicker) {
            launcherError.classList.remove('hidden');
            launcherTicker.focus();
            return;
        }
        launcherError.classList.add('hidden');
        openLauncherTicker(ticker, 'hub');
    });

    launcherTicker.addEventListener('input', () => {
        launcherError.classList.add('hidden');
        clearTimeout(launcherSuggestionTimer);
        launcherSuggestionSelection = -1;
        launcherSuggestionTimer = setTimeout(() => fetchLauncherSuggestions(launcherTicker.value), 250);
    });

    launcherTicker.addEventListener('keydown', event => {
        if (launcherSuggestions.classList.contains('hidden') || !launcherSuggestionItems.length) return;
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            launcherSuggestionSelection = (launcherSuggestionSelection + 1) % launcherSuggestionItems.length;
            renderLauncherSuggestions(launcherSuggestionItems);
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            launcherSuggestionSelection = (launcherSuggestionSelection - 1 + launcherSuggestionItems.length) % launcherSuggestionItems.length;
            renderLauncherSuggestions(launcherSuggestionItems);
        } else if (event.key === 'Enter' && launcherSuggestionSelection >= 0) {
            event.preventDefault();
            openLauncherTicker(launcherSuggestionItems[launcherSuggestionSelection].symbol);
        } else if (event.key === 'Escape') {
            hideLauncherSuggestions();
        }
    });

    document.addEventListener('click', event => {
        if (!launcherForm.contains(event.target)) hideLauncherSuggestions();
    });
'''
assert old_js in s
s=s.replace(old_js,new_js,1)

old1='''                    <button type="button" onclick="openCommandPalette()" class="group rounded-2xl border border-gray-200 bg-white p-5 text-left shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Command Palette</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Use Ctrl or Cmd + K to jump to a tool, section or ticker.</p>
                    </button>'''
new1='''                    <a href="#top" onclick="setTimeout(() => document.getElementById('launcher-ticker').focus(), 250)" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Company Search</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Search Quick Launch by company name or ticker and choose the matching security.</p>
                    </a>'''
assert old1 in s
s=s.replace(old1,new1,1)

old2='''                    <a href="#top" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Continue Shortcut</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Return to the last SethiWay tool, stock or section you were using.</p>
                    </a>'''
new2=old1
assert old2 in s
s=s.replace(old2,new2,1)

old3='''                    <a href="#top" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Watchlist Shortcuts</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Saved SethiStock tickers now appear inside Quick Launch for one-click access.</p>
                    </a>'''
new3=old2
assert old3 in s
s=s.replace(old3,new3,1)

assert '—' not in s
p.write_text(s)
