from pathlib import Path
import re

path = Path('index.html')
text = path.read_text()

# Centre the four primary nav links independently of the logo and right-hand CTA.
text = text.replace(
'''            <div class="hidden md:flex items-center gap-8 text-sm font-bold text-gray-600">''',
'''            <div class="hidden md:flex items-center gap-8 text-sm font-bold text-gray-600 absolute left-1/2 -translate-x-1/2">''',
1)
text = text.replace(
'''        <div class="max-w-[1720px] mx-auto px-6 lg:px-10 h-20 flex items-center justify-between gap-8">''',
'''        <div class="max-w-[1720px] mx-auto px-6 lg:px-10 h-20 flex items-center justify-between gap-8 relative">''',
1)

# Replace the oversized hero with a much more compact introduction.
hero = '''        <header class="px-6 lg:px-10 pt-8 md:pt-9 pb-5 bg-gradient-to-b from-white to-gray-50">
            <div class="max-w-4xl mx-auto text-center">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-200 bg-amber-50 text-amber-800 text-[10px] font-black uppercase tracking-wider mb-3">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    New · SethiPortfolio is now live
                </div>
                <h1 class="text-4xl md:text-5xl font-black tracking-tight leading-[1.02] text-gray-950">
                    One connected platform for <span class="text-blue-600">financial research and risk.</span>
                </h1>
                <p class="mt-3 text-base md:text-lg text-gray-500 max-w-3xl mx-auto leading-relaxed">
                    Macro context, security analysis, portfolio management and quantitative risk — connected around real financial decisions.
                </p>
                <div class="mt-4 flex flex-col sm:flex-row justify-center gap-3">
                    <a href="#platform" class="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-black hover:bg-blue-700 transition shadow-sm">Explore the Platform →</a>
                    <a href="sethiportfolio.html" class="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-white border border-gray-200 text-gray-900 text-sm font-black hover:border-amber-300 hover:bg-amber-50 transition">Open SethiPortfolio →</a>
                </div>
            </div>
        </header>'''
text, count = re.subn(r'        <header class="px-6 lg:px-10 pt-14.*?</header>', hero, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Hero block not found')

# Remove the standalone boxed workflow strip.
text, count = re.subn(r'\n        <section id="workflow".*?</section>\n', '\n', text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Workflow section not found')

# Restore the stronger original-style tool cards, with workflow numbers/arrows above them.
platform = '''        <section id="platform" class="px-6 lg:px-10 pt-3 pb-16 bg-gray-50">
            <div class="max-w-[1720px] mx-auto">
                <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-2 mb-4">
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-[0.18em] text-blue-600">The Platform</p>
                        <h2 class="text-2xl md:text-3xl font-black mt-1">Four tools. One connected workflow.</h2>
                    </div>
                    <p class="text-sm text-gray-500">Move from market context to security research, allocation and risk.</p>
                </div>

                <div id="workflow" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 xl:gap-7">
                    <div class="flex flex-col">
                        <div class="h-14 flex items-center px-1 mb-2">
                            <span class="text-4xl font-black tracking-tighter text-red-500">01</span>
                            <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Macro</span>
                            <span class="hidden xl:block flex-1 h-px bg-gray-300 ml-4"></span>
                            <span class="hidden xl:block text-2xl text-gray-300 ml-2">→</span>
                        </div>
                        <article class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 flex flex-col flex-grow">
                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-red-500">MACRO.</span></span>
                            </div>
                            <div class="p-8 flex flex-col flex-grow">
                                <div class="flex justify-between items-start gap-3 mb-4">
                                    <div><h3 class="text-2xl font-bold">SethiMacro Dashboard</h3><p class="text-sm font-bold text-gray-500 mt-1">What environment are markets operating in?</p></div>
                                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold uppercase rounded-full tracking-wide shrink-0">Live</span>
                                </div>
                                <p class="text-gray-600 font-light leading-relaxed mb-6 flex-grow">Track macro indicators, central-bank divergence, market conditions and global economic events in one research dashboard.</p>
                                <div class="flex flex-wrap gap-2 mb-6">
                                    <span class="px-2 py-1 text-xs font-semibold text-red-600 bg-red-50 rounded border border-red-100">Macro Regime</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-emerald-600 bg-emerald-50 rounded border border-emerald-100">Global Calendar</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100">AI Analysis</span>
                                </div>
                                <a href="sethimacro.html" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition w-full">Launch Dashboard →</a>
                            </div>
                        </article>
                    </div>

                    <div class="flex flex-col">
                        <div class="h-14 flex items-center px-1 mb-2">
                            <span class="text-4xl font-black tracking-tighter text-emerald-500">02</span>
                            <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Stock</span>
                            <span class="hidden xl:block flex-1 h-px bg-gray-300 ml-4"></span>
                            <span class="hidden xl:block text-2xl text-gray-300 ml-2">→</span>
                        </div>
                        <article class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 flex flex-col flex-grow">
                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-green-500">STOCK.</span></span>
                            </div>
                            <div class="p-8 flex flex-col flex-grow">
                                <div class="flex justify-between items-start gap-3 mb-4">
                                    <div><h3 class="text-2xl font-bold">SethiStock Analytics</h3><p class="text-sm font-bold text-gray-500 mt-1">What is this business worth?</p></div>
                                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold uppercase rounded-full tracking-wide shrink-0">Live</span>
                                </div>
                                <p class="text-gray-600 font-light leading-relaxed mb-6 flex-grow">Analyse a single equity through fundamentals, valuation, price behaviour and research tools built around an investable security.</p>
                                <div class="flex flex-wrap gap-2 mb-6">
                                    <span class="px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded border border-blue-100">Reverse DCF</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-emerald-600 bg-emerald-50 rounded border border-emerald-100">Mini-LBO</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100">Risk & Market Data</span>
                                </div>
                                <a href="sethistock.html" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition w-full">Launch Application →</a>
                            </div>
                        </article>
                    </div>

                    <div class="flex flex-col">
                        <div class="h-14 flex items-center px-1 mb-2">
                            <span class="text-4xl font-black tracking-tighter text-amber-500">03</span>
                            <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Portfolio</span>
                            <span class="hidden xl:block flex-1 h-px bg-gray-300 ml-4"></span>
                            <span class="hidden xl:block text-2xl text-gray-300 ml-2">→</span>
                        </div>
                        <article class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 flex flex-col flex-grow">
                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-yellow-500">PORTFOLIO</span></span>
                            </div>
                            <div class="p-8 flex flex-col flex-grow">
                                <div class="flex justify-between items-start gap-3 mb-4">
                                    <div><h3 class="text-2xl font-bold">SethiPortfolio Vault</h3><p class="text-sm font-bold text-gray-500 mt-1">How is capital allocated and performing?</p></div>
                                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold uppercase rounded-full tracking-wide shrink-0">Live</span>
                                </div>
                                <p class="text-gray-600 font-light leading-relaxed mb-6 flex-grow">Track holdings, benchmark-relative performance, exposures, portfolio risk, FX effects and hypothetical rebalancing.</p>
                                <div class="flex flex-wrap gap-2 mb-6">
                                    <span class="px-2 py-1 text-xs font-semibold text-amber-700 bg-amber-50 rounded border border-amber-100">Portfolio Risk</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-fuchsia-600 bg-fuchsia-50 rounded border border-fuchsia-100">FX Analytics</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-teal-700 bg-teal-50 rounded border border-teal-100">What-If</span>
                                </div>
                                <a href="sethiportfolio.html" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition w-full">Unlock Vault →</a>
                            </div>
                        </article>
                    </div>

                    <div class="flex flex-col">
                        <div class="h-14 flex items-center px-1 mb-2">
                            <span class="text-4xl font-black tracking-tighter text-blue-500">04</span>
                            <span class="ml-3 text-xs font-black uppercase tracking-[0.18em] text-gray-500">Quant</span>
                        </div>
                        <article class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 flex flex-col flex-grow">
                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-blue-500">QUANT.</span></span>
                            </div>
                            <div class="p-8 flex flex-col flex-grow">
                                <div class="flex justify-between items-start gap-3 mb-4">
                                    <div><h3 class="text-2xl font-bold">SethiQuant Terminal</h3><p class="text-sm font-bold text-gray-500 mt-1">What does the risk look like?</p></div>
                                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold uppercase rounded-full tracking-wide shrink-0">Live</span>
                                </div>
                                <p class="text-gray-600 font-light leading-relaxed mb-6 flex-grow">Price options, explore portfolio construction, test strategies and analyse market risk with quantitative models and simulations.</p>
                                <div class="flex flex-wrap gap-2 mb-6">
                                    <span class="px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded border border-blue-100">Options & Greeks</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-purple-600 bg-purple-50 rounded border border-purple-100">Backtesting</span>
                                    <span class="px-2 py-1 text-xs font-semibold text-gray-700 bg-gray-100 rounded border border-gray-200">Market Risk Lab</span>
                                </div>
                                <a href="sethiquant.html" class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition w-full">Launch Terminal →</a>
                            </div>
                        </article>
                    </div>
                </div>
            </div>
        </section>'''
text, count = re.subn(r'        <section id="platform".*?</section>', platform, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Platform section not found')

# Normalise About body copy typography.
text = text.replace('''<p class="mt-5 text-lg leading-relaxed text-gray-600">I study BSc MORSE''', '''<p class="mt-5 text-lg leading-relaxed text-gray-600">I study BSc MORSE''', 1)
text = text.replace('''<p class="mt-4 text-gray-600 leading-relaxed">The goal is simple:''', '''<p class="mt-4 text-lg text-gray-600 leading-relaxed">The goal is simple:''', 1)

path.write_text(text)
