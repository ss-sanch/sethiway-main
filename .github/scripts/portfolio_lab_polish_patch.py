from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

# 1) Centre the four primary header links independently of left/right utility widths.
old_header = '''            <div class="flex items-center gap-4 lg:gap-6 min-w-0">
                <a href="index.html" class="flex items-center py-3 shrink-0" aria-label="SethiWay home">
                    <img src="logo.png" alt="SethiWay" class="h-6 sm:h-10 w-auto invert">
                </a>
                <div class="portfolio-section-links hidden lg:flex flex-1 items-center justify-end gap-5 xl:gap-7 whitespace-nowrap text-sm font-bold text-gray-600 min-w-0">
                    <a href="#performance" class="hover:text-blue-600">Performance</a>
                    <a href="#holdings" class="hover:text-blue-600">Holdings</a>
                    <a href="#portfolio-lab" class="hover:text-blue-600">Portfolio Lab</a>
                    <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>
                </div>
                <div class="flex items-center gap-2 shrink-0 ml-auto lg:ml-0">
                    <a href="sethiportfolio-admin.html" class="px-3 py-2.5 border border-gray-200 bg-white text-gray-700 text-xs xl:text-sm font-bold rounded-lg hover:border-blue-300 hover:text-blue-700 hover:bg-blue-50 transition shadow-sm whitespace-nowrap" title="Open the protected SethiPortfolio control panel">Portfolio Admin</a>
                    <a href="index.html" class="px-3 xl:px-4 py-2.5 bg-gray-900 text-white text-xs xl:text-sm font-bold rounded-lg hover:bg-gray-800 transition shadow-sm whitespace-nowrap">Back to Hub</a>
                </div>
            </div>
            <div class="lg:hidden flex items-center gap-5 overflow-x-auto whitespace-nowrap text-xs font-black text-gray-600 pb-3">'''
new_header = '''            <div class="relative flex items-center gap-4 min-w-0">
                <a href="index.html" class="flex items-center py-3 shrink-0" aria-label="SethiWay home">
                    <img src="logo.png" alt="SethiWay" class="h-6 sm:h-10 w-auto invert">
                </a>
                <div class="portfolio-section-links hidden xl:flex absolute left-1/2 -translate-x-1/2 items-center justify-center gap-7 whitespace-nowrap text-sm font-bold text-gray-600">
                    <a href="#performance" class="hover:text-blue-600">Performance</a>
                    <a href="#holdings" class="hover:text-blue-600">Holdings</a>
                    <a href="#portfolio-lab" class="hover:text-blue-600">Portfolio Lab</a>
                    <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>
                </div>
                <div class="flex items-center gap-2 shrink-0 ml-auto">
                    <a href="sethiportfolio-admin.html" class="px-3 py-2.5 border border-gray-200 bg-white text-gray-700 text-xs xl:text-sm font-bold rounded-lg hover:border-blue-300 hover:text-blue-700 hover:bg-blue-50 transition shadow-sm whitespace-nowrap" title="Open the protected SethiPortfolio control panel">Portfolio Admin</a>
                    <a href="index.html" class="px-3 xl:px-4 py-2.5 bg-gray-900 text-white text-xs xl:text-sm font-bold rounded-lg hover:bg-gray-800 transition shadow-sm whitespace-nowrap">Back to Hub</a>
                </div>
            </div>
            <div class="xl:hidden flex items-center justify-center gap-5 overflow-x-auto whitespace-nowrap text-xs font-black text-gray-600 pb-3">'''
if old_header not in text:
    raise SystemExit('Header block not found')
text = text.replace(old_header, new_header, 1)

# 2) Match the composition card height to Position Detail and give the donut room to breathe.
old_holdings = '''            <section class="grid grid-cols-1 xl:grid-cols-[420px_minmax(0,1fr)] gap-5 items-start">
                <div class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6">
                    <div class="mb-2"><p class="text-[10px] font-black uppercase tracking-widest text-amber-600 mb-1">Composition</p><h3 class="text-xl font-black">Where is the capital allocated?</h3></div>
                    <div id="weights-chart" style="height:315px"></div>
                    <div class="grid grid-cols-2 gap-3 mt-1">'''
new_holdings = '''            <section class="grid grid-cols-1 xl:grid-cols-[420px_minmax(0,1fr)] gap-5 items-stretch">
                <div class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-6 h-full flex flex-col">
                    <div class="mb-2"><p class="text-[10px] font-black uppercase tracking-widest text-amber-600 mb-1">Composition</p><h3 class="text-xl font-black">Where is the capital allocated?</h3></div>
                    <div id="weights-chart" class="flex-1 min-h-[390px]"></div>
                    <div class="grid grid-cols-2 gap-3 mt-3">'''
if old_holdings not in text:
    raise SystemExit('Holdings block not found')
text = text.replace(old_holdings, new_holdings, 1)

# 3) Remove repeated section-intro headers inside Portfolio Lab.
old_lab_css = '''        .portfolio-lab-panel .section-intro { margin: 1.25rem 0 .85rem; padding-top: 1rem; grid-template-columns: fit-content(300px) minmax(0,1fr); }
        .portfolio-lab-panel .section-intro:first-child { margin-top: 0; padding-top: 0; border-top: 0; }
        .portfolio-lab-panel .section-intro h2 { font-size: 1.35rem; }
        .portfolio-lab-panel .section-overview { padding: .8rem 1rem; font-size: .8rem; }'''
new_lab_css = '''        .portfolio-lab-panel .section-intro { display: none; }
        .portfolio-lab-panel > section + section { margin-top: 1rem; }'''
if old_lab_css not in text:
    raise SystemExit('Portfolio Lab CSS block not found')
text = text.replace(old_lab_css, new_lab_css, 1)

# 4) Put richer question-led descriptions directly into workspace cards.
old_tabs = '''                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="performance" aria-selected="true" onclick="setPortfolioLabTab('performance')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">01</span><span class="block text-sm font-black mt-0.5">Performance Diagnostics</span><span class="block text-[10px] opacity-70 mt-1">Attribution · benchmark · drawdown · efficiency</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="risk" aria-selected="false" onclick="setPortfolioLabTab('risk')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">02</span><span class="block text-sm font-black mt-0.5">Risk &amp; Exposure</span><span class="block text-[10px] opacity-70 mt-1">Sector · geography · concentration · Euler risk</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="fx" aria-selected="false" onclick="setPortfolioLabTab('fx')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">03</span><span class="block text-sm font-black mt-0.5">FX</span><span class="block text-[10px] opacity-70 mt-1">Translation · sterling sensitivity · currency paths</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="whatif" aria-selected="false" onclick="setPortfolioLabTab('whatif')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">04</span><span class="block text-sm font-black mt-0.5">What-If</span><span class="block text-[10px] opacity-70 mt-1">Reweight the live book without placing a trade</span></button>'''
new_tabs = '''                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3.5 text-left transition" data-lab-tab="performance" aria-selected="true" onclick="setPortfolioLabTab('performance')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">01</span><span class="block text-sm font-black mt-0.5">Performance Diagnostics</span><span class="block text-[11px] leading-relaxed opacity-75 mt-1.5">What drove my return, how did I compare with benchmarks, and how difficult was the path?</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3.5 text-left transition" data-lab-tab="risk" aria-selected="false" onclick="setPortfolioLabTab('risk')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">02</span><span class="block text-sm font-black mt-0.5">Risk &amp; Exposure</span><span class="block text-[11px] leading-relaxed opacity-75 mt-1.5">What am I actually exposed to, and where does the portfolio's concentration and Euler risk sit?</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3.5 text-left transition" data-lab-tab="fx" aria-selected="false" onclick="setPortfolioLabTab('fx')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">03</span><span class="block text-sm font-black mt-0.5">FX</span><span class="block text-[11px] leading-relaxed opacity-75 mt-1.5">Did the security move, or did sterling move — and how sensitive is portfolio NAV to GBP?</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3.5 text-left transition" data-lab-tab="whatif" aria-selected="false" onclick="setPortfolioLabTab('whatif')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">04</span><span class="block text-sm font-black mt-0.5">What-If</span><span class="block text-[11px] leading-relaxed opacity-75 mt-1.5">What if I change my positions — does the proposed allocation improve concentration or portfolio risk?</span></button>'''
if old_tabs not in text:
    raise SystemExit('Portfolio Lab tab block not found')
text = text.replace(old_tabs, new_tabs, 1)

# Deep links now scroll to the visible section card because the mini intro is hidden.
old_target = '''        const rawId = hash.replace(/^#/, '');
        const target = rawId.startsWith('lab-') ? document.getElementById('portfolio-lab') : document.getElementById(rawId);
        setTimeout(() => target?.scrollIntoView({behavior: animate ? 'smooth' : 'auto', block:'start'}), 30);'''
new_target = '''        const rawId = hash.replace(/^#/, '');
        const rawTarget = document.getElementById(rawId);
        const target = rawId.startsWith('lab-')
            ? document.getElementById('portfolio-lab')
            : (rawTarget?.nextElementSibling || rawTarget);
        setTimeout(() => target?.scrollIntoView({behavior: animate ? 'smooth' : 'auto', block:'start'}), 30);'''
if old_target not in text:
    raise SystemExit('Portfolio Lab hash target block not found')
text = text.replace(old_target, new_target, 1)

path.write_text(text)
