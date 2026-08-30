from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Marker not found: {label}')
    s = s.replace(old, new, 1)

# OPTIONS: replace clipped-card approach with a purpose-built teaser + hidden details.
rep(
    '<div id="options-insights" class="max-w-[1600px] w-full mx-auto px-4 -mt-10 mb-16 max-h-[92px] overflow-hidden opacity-75 transition-all duration-300">',
    '<div id="options-insights" class="max-w-[1600px] w-full mx-auto px-4 -mt-10 mb-16">',
    'options outer preview'
)
rep(
'''                <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 md:p-6">\n                    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 mb-5">''',
'''                <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 md:p-6">\n                    <div id="options-preview-cue" class="flex items-center justify-between gap-4 rounded-xl border border-blue-100 bg-blue-50/40 px-4 py-3 mb-4">\n                        <div class="min-w-0"><p class="text-[10px] font-black uppercase tracking-widest text-blue-600">Next step</p><p class="text-sm font-bold text-gray-800 mt-0.5">Calculate an option to unlock payoff, break-even and risk interpretation.</p></div>\n                        <span class="shrink-0 text-[10px] font-black uppercase tracking-wider text-blue-700 bg-white border border-blue-200 rounded-full px-3 py-1.5">Run to unlock</span>\n                    </div>\n                    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 mb-5">''',
    'options teaser cue'
)
rep(
'''                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">''',
'''                    <div id="options-insights-detail" class="hidden">\n                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">''',
    'options detail wrapper start'
)
rep(
'''                    </div>\n                </div>\n            </div>\n        </section>\n\n        <!-- MARKOWITZ OPTIMISER''',
'''                    </div>\n                    </div>\n                </div>\n            </div>\n        </section>\n\n        <!-- MARKOWITZ OPTIMISER''',
    'options detail wrapper end'
)
rep(
"            insights.classList.remove('hidden', 'max-h-[92px]', 'overflow-hidden', 'opacity-75');\n            insights.classList.add('opacity-100');",
"            document.getElementById('options-preview-cue').classList.add('hidden');\n            document.getElementById('options-insights-detail').classList.remove('hidden');",
    'options expand js'
)

# BACKTEST: replace clipped teaser with explicit preview cue + hidden body.
rep(
    '<div id="backtest-insights" class="max-w-6xl mx-auto -mt-10 mb-16 bg-white rounded-2xl shadow-sm border border-gray-200 p-5 md:p-6 max-h-[92px] overflow-hidden opacity-75 transition-all duration-300">',
    '<div id="backtest-insights" class="max-w-6xl mx-auto -mt-10 mb-16 bg-white rounded-2xl shadow-sm border border-gray-200 p-5 md:p-6">',
    'backtest outer preview'
)
rep(
'''                <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-5">''',
'''                <div id="backtest-preview-cue" class="flex items-center justify-between gap-4 rounded-xl border border-teal-100 bg-teal-50/40 px-4 py-3 mb-4">\n                    <div class="min-w-0"><p class="text-[10px] font-black uppercase tracking-widest text-teal-600">Next step</p><p class="text-sm font-bold text-gray-800 mt-0.5">Analyse a strategy to unlock drawdowns, trade quality and risk-adjusted diagnostics.</p></div>\n                    <span class="shrink-0 text-[10px] font-black uppercase tracking-wider text-teal-700 bg-white border border-teal-200 rounded-full px-3 py-1.5">Run to unlock</span>\n                </div>\n                <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-5">''',
    'backtest teaser cue'
)
rep(
'''                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">''',
'''                <div id="backtest-insights-detail" class="hidden">\n                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">''',
    'backtest detail wrapper start'
)
rep(
'''                <div id="bt-learning-points" class="mt-4 rounded-xl bg-teal-50/50 border border-teal-100 p-4 text-sm text-gray-700 leading-relaxed">A strong backtest should be judged on more than total return: compare risk-adjusted ratios, drawdowns, benchmark performance and how often the strategy was actually invested.</div>\n            </div>\n        </section>''',
'''                <div id="bt-learning-points" class="mt-4 rounded-xl bg-teal-50/50 border border-teal-100 p-4 text-sm text-gray-700 leading-relaxed">A strong backtest should be judged on more than total return: compare risk-adjusted ratios, drawdowns, benchmark performance and how often the strategy was actually invested.</div>\n                </div>\n            </div>\n        </section>''',
    'backtest detail wrapper end'
)
rep(
"                const backtestInsights = document.getElementById('backtest-insights');\n                backtestInsights.classList.remove('max-h-[92px]', 'overflow-hidden', 'opacity-75');\n                backtestInsights.classList.add('opacity-100');",
"                document.getElementById('backtest-preview-cue').classList.add('hidden');\n                document.getElementById('backtest-insights-detail').classList.remove('hidden');",
    'backtest expand js'
)

p.write_text(s, encoding='utf-8')
