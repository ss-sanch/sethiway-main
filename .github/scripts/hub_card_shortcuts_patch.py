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
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <span class="px-2 py-1 text-xs font-semibold text-red-600 bg-red-50 rounded border border-red-100">Macro Regime</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-emerald-600 bg-emerald-50 rounded border border-emerald-100">Global Calendar</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100">AI Analysis</span>\n                                </div>''',
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <a href="sethimacro.html#job-market" class="px-2 py-1 text-xs font-semibold text-red-600 bg-red-50 rounded border border-red-100 hover:bg-red-100 transition" title="Open the Job Market section">Job Market</a>\n                                    <a href="sethimacro.html#inflation-rates" class="px-2 py-1 text-xs font-semibold text-emerald-600 bg-emerald-50 rounded border border-emerald-100 hover:bg-emerald-100 transition" title="Open Inflation &amp; Rates">Inflation &amp; Rates</a>\n                                    <a href="sethimacro.html#currencies" class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100 hover:bg-purple-100 transition" title="Open the Currencies section">Currencies</a>\n                                </div>''',
    'Macro shortcuts',
)

replace_once(
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <span class="px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded border border-blue-100">Reverse DCF</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-emerald-600 bg-emerald-50 rounded border border-emerald-100">Mini-LBO</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100">Risk &amp; Market Data</span>\n                                </div>''',
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <a href="sethistock.html#key-metrics" class="px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded border border-blue-100 hover:bg-blue-100 transition" title="Open SethiStock key metrics">Key Metrics</a>\n                                    <a href="sethistock.html#research-labs" class="px-2 py-1 text-xs font-semibold text-emerald-600 bg-emerald-50 rounded border border-emerald-100 hover:bg-emerald-100 transition" title="Open SethiStock Research Labs">Research Labs</a>\n                                    <a href="sethistock.html#valuation" class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100 hover:bg-purple-100 transition" title="Open SethiStock valuations">Valuations</a>\n                                </div>''',
    'Stock shortcuts',
)

replace_once(
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <span class="px-2 py-1 text-xs font-semibold text-amber-700 bg-amber-50 rounded border border-amber-100">Portfolio Risk</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-fuchsia-600 bg-fuchsia-50 rounded border border-fuchsia-100">FX Analytics</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-teal-700 bg-teal-50 rounded border border-teal-100">What-If</span>\n                                </div>''',
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <a href="sethiportfolio.html#performance" class="px-2 py-1 text-xs font-semibold text-amber-700 bg-amber-50 rounded border border-amber-100 hover:bg-amber-100 transition" title="Open portfolio performance">Performance</a>\n                                    <a href="sethiportfolio.html#portfolio-lab" class="px-2 py-1 text-xs font-semibold text-fuchsia-600 bg-fuchsia-50 rounded border border-fuchsia-100 hover:bg-fuchsia-100 transition" title="Open Portfolio Lab">Portfolio Lab</a>\n                                    <a href="sethiportfolio.html#decisions" class="px-2 py-1 text-xs font-semibold text-teal-700 bg-teal-50 rounded border border-teal-100 hover:bg-teal-100 transition" title="Open investment decisions">Decisions</a>\n                                </div>''',
    'Portfolio shortcuts',
)

replace_once(
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <span class="px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded border border-blue-100">Options &amp; Greeks</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100">Backtesting</span>\n                                    <span class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 rounded border border-gray-200">Market Risk Lab</span>\n                                </div>''',
    '''<div class="flex flex-wrap gap-2 mb-6">\n                                    <a href="sethiquant.html#section-options" class="px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded border border-blue-100 hover:bg-blue-100 transition" title="Open Options Valuation">Options &amp; Greeks</a>\n                                    <a href="sethiquant.html#section-backtest" class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100 hover:bg-purple-100 transition" title="Open Strategy Backtest">Backtesting</a>\n                                    <a href="sethiquant.html#section-var" class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 rounded border border-gray-200 hover:bg-gray-200 transition" title="Open Market Risk Lab">Market Risk Lab</a>\n                                </div>''',
    'Quant shortcuts',
)

required = [
    'sethimacro.html#job-market', 'sethimacro.html#inflation-rates', 'sethimacro.html#currencies',
    'sethistock.html#key-metrics', 'sethistock.html#research-labs', 'sethistock.html#valuation',
    'sethiportfolio.html#performance', 'sethiportfolio.html#portfolio-lab', 'sethiportfolio.html#decisions',
    'sethiquant.html#section-options', 'sethiquant.html#section-backtest', 'sethiquant.html#section-var',
]
for target in required:
    if text.count(target) != 1:
        raise SystemExit(f'Missing or duplicated shortcut target: {target}')
if '—' in text:
    raise SystemExit('Em dash remains in homepage copy')

path.write_text(text)
