from pathlib import Path

path = Path('index.html')
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

# Remove redundant nav item. Platform already lands on the workflow/tool section.
replace_once(
    '                <a href="#workflow" class="hover:text-blue-600 transition">How It Works</a>\n',
    '',
    'How It Works nav item',
)

# Replace the split line + glyph connectors with a single continuous SVG arrow.
steps = [
    ('01', 'Macro', 'red'),
    ('02', 'Stock', 'emerald'),
    ('03', 'Portfolio', 'amber'),
]
for number, label, colour in steps:
    old = f'''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <div class="flex items-baseline w-[150px] shrink-0">\n                                <span class="text-4xl font-black tracking-tighter text-{colour}-500">{number}</span>\n                                <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">{label}</span>\n                            </div>\n                            <div class="hidden xl:flex flex-1 items-center gap-2">\n                                <span class="flex-1 h-px bg-gray-300"></span>\n                                <span class="text-xl leading-none text-gray-300 -translate-y-px">→</span>\n                            </div>\n                        </div>'''
    new = f'''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <div class="flex items-center w-[150px] shrink-0">\n                                <span class="text-4xl leading-none font-black tracking-tighter text-{colour}-500">{number}</span>\n                                <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">{label}</span>\n                            </div>\n                            <svg class="hidden xl:block flex-1 h-3 ml-4 overflow-visible" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">\n                                <path d="M0 5 H98 M93.5 1.2 L98 5 L93.5 8.8" fill="none" stroke="#d1d5db" stroke-width="1" vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round"/>\n                            </svg>\n                        </div>'''
    replace_once(old, new, f'workflow connector {number}')

# Keep the final step aligned identically, just without an outgoing arrow.
replace_once(
    '''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <div class="flex items-baseline w-[150px] shrink-0">\n                                <span class="text-4xl font-black tracking-tighter text-blue-500">04</span>\n                                <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Quant</span>\n                            </div>\n                        </div>''',
    '''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <div class="flex items-center w-[150px] shrink-0">\n                                <span class="text-4xl leading-none font-black tracking-tighter text-blue-500">04</span>\n                                <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Quant</span>\n                            </div>\n                        </div>''',
    'workflow final step alignment',
)

# Restore the preferred Portfolio naming and make all four project marks consistent.
replace_once(
    '<span class="text-3xl font-black tracking-tighter">SETHI<span class="text-yellow-500">PORTFOLIO</span></span>',
    '<span class="text-3xl font-black tracking-tighter">SETHI<span class="text-yellow-500">PORTFOLIO.</span></span>',
    'SethiPortfolio mark punctuation',
)
replace_once(
    '<div><h3 class="text-2xl font-bold">SethiPortfolio</h3><p class="text-sm font-bold text-gray-500 mt-1">How is capital allocated and performing?</p></div>',
    '<div><h3 class="text-2xl font-bold">SethiPortfolio Vault</h3><p class="text-sm font-bold text-gray-500 mt-1">How is capital allocated and performing?</p></div>',
    'SethiPortfolio Vault title',
)

# Guard the copy/style rules already agreed.
if 'How It Works' in text:
    raise SystemExit('Redundant How It Works nav item remains')
if '—' in text:
    raise SystemExit('Em dash remains in index.html')
if text.count('preserveAspectRatio="none" aria-hidden="true"') != 3:
    raise SystemExit('Expected three continuous workflow arrows')
if 'PORTFOLIO.</span>' not in text:
    raise SystemExit('SethiPortfolio mark is missing full stop')
if 'SethiPortfolio Vault' not in text:
    raise SystemExit('SethiPortfolio Vault title is missing')

path.write_text(text)
