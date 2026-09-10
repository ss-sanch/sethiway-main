from pathlib import Path

path = Path('index.html')
text = path.read_text()

anchor = '''        <section class="py-20 px-6 lg:px-10 bg-white border-t border-gray-200">\n            <div class="max-w-7xl mx-auto">\n                <div class="text-center max-w-3xl mx-auto mb-10">\n                    <p class="text-[11px] font-black uppercase tracking-[0.18em] text-blue-600">Behind SethiWay</p>'''

if text.count(anchor) != 1:
    raise SystemExit(f'Behind SethiWay anchor: expected 1 match, found {text.count(anchor)}')

section = '''        <section id="recently-added" class="px-6 lg:px-10 pb-16 bg-gray-50">\n            <div class="max-w-[1720px] mx-auto border-t border-gray-200 pt-10">\n                <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-3 mb-6">\n                    <div>\n                        <p class="text-[10px] font-black uppercase tracking-[0.18em] text-blue-600">Recently Added</p>\n                        <h2 class="text-2xl md:text-3xl font-black mt-1">A few of the latest changes.</h2>\n                    </div>\n                    <p class="text-sm text-gray-500">Shortcuts to features added across the platform.</p>\n                </div>\n\n                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">\n                    <a href="#top" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">\n                        <div class="flex items-center justify-between gap-3">\n                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>\n                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>\n                        </div>\n                        <h3 class="mt-3 text-lg font-black text-gray-950">Quick Launch</h3>\n                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Enter a ticker on the homepage and open it directly in SethiStock.</p>\n                    </a>\n\n                    <a href="sethiportfolio.html#portfolio-lab" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-amber-200 hover:shadow-md transition">\n                        <div class="flex items-center justify-between gap-3">\n                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-amber-600">SethiPortfolio</span>\n                            <span class="text-amber-600 group-hover:translate-x-0.5 transition-transform">→</span>\n                        </div>\n                        <h3 class="mt-3 text-lg font-black text-gray-950">Portfolio Lab</h3>\n                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Review exposure, FX effects, portfolio risk and proposed reallocations in one place.</p>\n                    </a>\n\n                    <a href="sethiquant.html#section-var" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">\n                        <div class="flex items-center justify-between gap-3">\n                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-blue-600">SethiQuant</span>\n                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>\n                        </div>\n                        <h3 class="mt-3 text-lg font-black text-gray-950">Market Risk Lab</h3>\n                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Run VaR, correlation, stress tests and risk contribution analysis on a portfolio.</p>\n                    </a>\n                </div>\n            </div>\n        </section>\n\n'''

text = text.replace(anchor, section + anchor, 1)

checks = [
    'id="recently-added"',
    '>Quick Launch</h3>',
    'sethiportfolio.html#portfolio-lab',
    'sethiquant.html#section-var',
]
for item in checks:
    if text.count(item) != 1:
        raise SystemExit(f'Missing or duplicated recent item: {item}')
if '—' in text:
    raise SystemExit('Em dash remains in homepage copy')

path.write_text(text)
