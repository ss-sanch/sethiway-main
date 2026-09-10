from pathlib import Path

path = Path('index.html')
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

hero_buttons = '''                <div class="mt-4 flex flex-col sm:flex-row justify-center gap-3">\n                    <a href="#platform" class="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-black hover:bg-blue-700 transition shadow-sm">Explore the Platform →</a>\n                    <a href="sethiportfolio.html" class="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-white border border-gray-200 text-gray-900 text-sm font-black hover:border-amber-300 hover:bg-amber-50 transition">Open SethiPortfolio →</a>\n                </div>'''

launcher = hero_buttons + '''\n\n                <div class="mt-6 max-w-2xl mx-auto rounded-2xl border border-gray-200 bg-white p-3 shadow-sm text-left">\n                    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 px-1 mb-2">\n                        <span class="text-[10px] font-black uppercase tracking-[0.18em] text-gray-500">Quick Launch</span>\n                        <span class="text-xs text-gray-400">Open a company directly in SethiStock.</span>\n                    </div>\n                    <form id="stock-launcher" class="flex flex-col sm:flex-row gap-2">\n                        <label for="launcher-ticker" class="sr-only">Ticker</label>\n                        <input id="launcher-ticker" name="ticker" type="text" autocomplete="off" spellcheck="false" maxlength="20" placeholder="Ticker, e.g. AAPL or ASML.AS" class="min-w-0 flex-1 rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-gray-900 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100">\n                        <button type="submit" class="shrink-0 rounded-xl bg-gray-900 px-5 py-3 text-sm font-black text-white transition hover:bg-blue-600">Open in SethiStock →</button>\n                    </form>\n                    <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 px-1 text-xs font-bold text-gray-500">\n                        <span class="font-medium text-gray-400">Go straight to:</span>\n                        <a href="sethimacro.html" class="hover:text-red-500 transition">SethiMacro</a>\n                        <a href="sethiportfolio.html" class="hover:text-amber-500 transition">SethiPortfolio</a>\n                        <a href="sethiquant.html" class="hover:text-blue-500 transition">SethiQuant</a>\n                    </div>\n                    <p id="launcher-error" class="hidden mt-2 px-1 text-xs font-semibold text-red-600">Enter a valid ticker symbol.</p>\n                </div>'''

replace_once(hero_buttons, launcher, 'hero launcher insertion')

script_anchor = '''    const form = document.getElementById('idea-form');\n    const successMessage = document.getElementById('success-message');\n'''
script_replacement = '''    const launcherForm = document.getElementById('stock-launcher');\n    const launcherTicker = document.getElementById('launcher-ticker');\n    const launcherError = document.getElementById('launcher-error');\n\n    launcherForm.addEventListener('submit', event => {\n        event.preventDefault();\n        const ticker = launcherTicker.value.trim().toUpperCase();\n        const validTicker = /^[A-Z0-9.^-]{1,20}$/.test(ticker);\n\n        if (!validTicker) {\n            launcherError.classList.remove('hidden');\n            launcherTicker.focus();\n            return;\n        }\n\n        launcherError.classList.add('hidden');\n        window.location.href = `sethistock.html?ticker=${encodeURIComponent(ticker)}&source=hub`;\n    });\n\n    launcherTicker.addEventListener('input', () => launcherError.classList.add('hidden'));\n\n    const form = document.getElementById('idea-form');\n    const successMessage = document.getElementById('success-message');\n'''
replace_once(script_anchor, script_replacement, 'launcher JavaScript')

if text.count('id="stock-launcher"') != 1:
    raise SystemExit('Expected exactly one stock launcher')
if 'sethistock.html?ticker=${encodeURIComponent(ticker)}&source=hub' not in text:
    raise SystemExit('SethiStock deep link is missing')
if '—' in text:
    raise SystemExit('Em dash remains in homepage copy')

path.write_text(text)
