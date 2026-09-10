from pathlib import Path

path = Path('index.html')
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)


replace_once(
    '    <link rel="stylesheet" href="style.css">\n</head>',
    '''    <link rel="stylesheet" href="style.css">\n    <style>\n        html { scroll-behavior: smooth; scroll-padding-top: 5rem; }\n        @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }\n    </style>\n</head>''',
    'smooth scrolling styles',
)

badge = '''                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-200 bg-amber-50 text-amber-800 text-[10px] font-black uppercase tracking-wider mb-3">\n                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>\n                    New · SethiPortfolio is now live\n                </div>\n'''
replace_once(badge, '', 'old launch badge')

replace_once(
    '''                <p class="mt-3 text-base md:text-lg text-gray-500 max-w-3xl mx-auto leading-relaxed">\n                    Macro context, security analysis, portfolio management and quantitative risk — connected around real financial decisions.\n                </p>\n                <div class="mt-4 flex flex-col sm:flex-row justify-center gap-3">''',
    '''                <p class="mt-3 text-base md:text-lg text-gray-500 max-w-3xl mx-auto leading-relaxed">\n                    Macro context, security analysis, portfolio management and quantitative risk. Each tool is built around real financial decisions.\n                </p>\n                <div class="mt-4">\n                    <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-200 bg-blue-50 text-blue-700 text-[10px] font-black uppercase tracking-wider">\n                        <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>\n                        SethiPortfolio is now live\n                    </span>\n                </div>\n                <div class="mt-4 flex flex-col sm:flex-row justify-center gap-3">''',
    'hero copy and launch badge position',
)

replace_once(
    '''                <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-2 mb-4">\n                    <div>\n                        <p class="text-[10px] font-black uppercase tracking-[0.18em] text-blue-600">The Platform</p>\n                        <h2 class="text-2xl md:text-3xl font-black mt-1">Four tools. One connected workflow.</h2>\n                    </div>\n                    <p class="text-sm text-gray-500">Move from market context to security research, allocation and risk.</p>\n                </div>''',
    '''                <div class="mb-4">\n                    <p class="text-[10px] font-black uppercase tracking-[0.18em] text-blue-600">The Platform</p>\n                    <h2 class="text-2xl md:text-3xl font-black mt-1">Four tools. One connected workflow.</h2>\n                </div>''',
    'platform heading cleanup',
)

steps = [
    ('01', 'Macro', 'red'),
    ('02', 'Stock', 'emerald'),
    ('03', 'Portfolio', 'amber'),
]
for number, label, colour in steps:
    old = f'''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <span class="text-4xl font-black tracking-tighter text-{colour}-500">{number}</span>\n                            <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">{label}</span>\n                            <span class="hidden xl:block flex-1 h-px bg-gray-300 ml-4"></span>\n                            <span class="hidden xl:block text-2xl text-gray-300 ml-2">→</span>\n                        </div>'''
    new = f'''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <div class="flex items-baseline w-[150px] shrink-0">\n                                <span class="text-4xl font-black tracking-tighter text-{colour}-500">{number}</span>\n                                <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">{label}</span>\n                            </div>\n                            <div class="hidden xl:flex flex-1 items-center gap-2">\n                                <span class="flex-1 h-px bg-gray-300"></span>\n                                <span class="text-xl leading-none text-gray-300 -translate-y-px">→</span>\n                            </div>\n                        </div>'''
    replace_once(old, new, f'workflow step {number}')

replace_once(
    '''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <span class="text-4xl font-black tracking-tighter text-blue-500">04</span>\n                            <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Quant</span>\n                        </div>''',
    '''                        <div class="h-14 flex items-center px-1 mb-2">\n                            <div class="flex items-baseline w-[150px] shrink-0">\n                                <span class="text-4xl font-black tracking-tighter text-blue-500">04</span>\n                                <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Quant</span>\n                            </div>\n                        </div>''',
    'workflow step 04',
)

replace_once(
    '<div><h3 class="text-2xl font-bold">SethiPortfolio Vault</h3><p class="text-sm font-bold text-gray-500 mt-1">How is capital allocated and performing?</p></div>',
    '<div><h3 class="text-2xl font-bold">SethiPortfolio</h3><p class="text-sm font-bold text-gray-500 mt-1">How is capital allocated and performing?</p></div>',
    'portfolio card title',
)
replace_once('>Unlock Vault →</a>', '>Open Portfolio →</a>', 'portfolio card CTA')

replace_once(
    '''                    <h2 class="text-3xl md:text-4xl font-black mt-2">Built where finance, maths and software meet.</h2>\n                    <p class="mt-4 text-gray-500">The platform is less about displaying data and more about turning financial questions into usable analytical systems.</p>''',
    '''                    <h2 class="text-3xl md:text-4xl font-black mt-2">Built from the questions I wanted to answer.</h2>\n                    <p class="mt-4 text-gray-500">SethiWay started as a set of tools for analysing markets, companies and portfolios. The maths and code sit underneath those questions.</p>''',
    'behind SethiWay copy',
)

replace_once('Thanks — I’ll take a look.', 'Thanks. I’ll take a look.', 'feedback success copy')

if '—' in text:
    raise SystemExit('Em dash remains in user-facing index.html')

for banned in ('delve', 'testament', 'intersection', 'seamless'):
    if banned in text.lower():
        raise SystemExit(f'AI-style wording remains: {banned}')

path.write_text(text)
