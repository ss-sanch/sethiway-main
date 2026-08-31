from pathlib import Path

html_path = Path('sethistock.html')
js_path = Path('sethistock-research.js')
html = html_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')

nav_old = '<a href="#valuation" class="hover:text-blue-600 transition">Valuations</a>'
nav_new = '<a href="#research-labs" class="hover:text-blue-600 transition">Research</a>\n            ' + nav_old
if 'href="#research-labs"' not in html:
    html = html.replace(nav_old, nav_new, 1)

section = '''
        <section id="research-labs" class="mt-12 scroll-mt-24">
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-3 mb-6 border-b border-gray-200 pb-4">
                <div>
                    <div class="flex items-center gap-3">
                        <h3 class="text-2xl font-black text-gray-900">Research Labs</h3>
                        <span class="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-100 text-[10px] font-black text-blue-700 uppercase tracking-widest">New</span>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">How the stock behaves around earnings and how today's valuation compares with its own history.</p>
                </div>
                <p id="research-status" class="text-xs font-bold text-gray-400 uppercase tracking-widest">Search a stock to initialise</p>
            </div>
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <article class="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-200">
                    <div class="mb-6">
                        <p class="text-[10px] font-black text-purple-600 uppercase tracking-widest mb-1">Event Study</p>
                        <h4 class="text-xl font-black text-gray-900">Earnings Reaction Study</h4>
                        <p class="text-sm text-gray-500 mt-1">Historical share-price reactions around reported earnings.</p>
                    </div>
                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Avg |1D Move|</p><p id="earnings-avg-abs" class="text-2xl font-black text-gray-900">--</p></div>
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Positive Reactions</p><p id="earnings-positive" class="text-2xl font-black text-gray-900">--</p></div>
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">EPS Beat Rate</p><p id="earnings-beat" class="text-2xl font-black text-gray-900">--</p></div>
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Avg 5D Move</p><p id="earnings-5d" class="text-2xl font-black text-gray-900">--</p></div>
                    </div>
                    <div id="earnings-reaction-chart" class="w-full h-[300px]"></div>
                    <div id="earnings-reaction-empty" class="hidden py-16 text-center text-sm font-semibold text-gray-400"></div>
                    <div class="overflow-x-auto mt-3 max-h-[260px] overflow-y-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="sticky top-0 bg-white text-gray-400 uppercase tracking-wider"><tr><th class="py-2 pr-3">Earnings</th><th class="py-2 px-3">EPS Surprise</th><th class="py-2 px-3">1D</th><th class="py-2 pl-3">5D</th></tr></thead>
                            <tbody id="earnings-reaction-table" class="divide-y divide-gray-100"></tbody>
                        </table>
                    </div>
                </article>
                <article class="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-200">
                    <div class="mb-6">
                        <p class="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">Self-Relative Valuation</p>
                        <h4 class="text-xl font-black text-gray-900">Historical Valuation Bands</h4>
                        <p class="text-sm text-gray-500 mt-1">Current trailing P/E versus reconstructed post-earnings P/E history.</p>
                    </div>
                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Current P/E</p><p id="valuation-current" class="text-2xl font-black text-gray-900">--</p></div>
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Historical Median</p><p id="valuation-median" class="text-2xl font-black text-gray-900">--</p></div>
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Current Percentile</p><p id="valuation-percentile" class="text-2xl font-black text-gray-900">--</p></div>
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4"><p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Position</p><p id="valuation-label" class="text-sm font-black text-gray-900 leading-tight mt-2">--</p></div>
                    </div>
                    <div id="valuation-band-chart" class="w-full h-[300px]"></div>
                    <div id="valuation-band-empty" class="hidden py-16 text-center text-sm font-semibold text-gray-400"></div>
                    <div class="mt-4 bg-blue-50/70 border border-blue-100 rounded-xl p-4">
                        <p class="text-[11px] leading-relaxed text-blue-900"><strong>Method:</strong> after each earnings release, SethiStock sums the latest four reported quarterly EPS figures and divides the post-release share price by that trailing EPS. This keeps the comparison historical rather than applying today's earnings backwards.</p>
                    </div>
                </article>
            </div>
        </section>

'''

if 'id="research-labs"' not in html:
    marker = '        <div id="valuation" class="mt-12 scroll-mt-24">'
    if marker not in html:
        raise RuntimeError('Valuation section marker not found')
    html = html.replace(marker, section + marker, 1)

external = '    <script src="sethistock-research.js?v=20260831"></script>'
if external in html:
    inline = '    <script id="sethistock-research-inline">\n' + js + '\n    </script>'
    html = html.replace(external, inline, 1)

assert html.count('id="research-labs"') == 1
assert '<a href="#research-labs" class="hover:text-blue-600 transition">Research</a>' in html
assert 'id="sethistock-research-inline"' in html
assert 'sethistock-research.js?v=20260831' not in html

html_path.write_text(html, encoding='utf-8')
