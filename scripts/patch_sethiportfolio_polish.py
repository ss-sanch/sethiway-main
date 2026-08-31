from pathlib import Path

p = Path('sethiportfolio.html')
s = p.read_text(encoding='utf-8')

# 1) Loading UI styles
needle = '    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>\n'
insert = needle + '''    <style>\n        #loading-progress { height: 3px; background: #dbeafe; overflow: hidden; }\n        #loading-progress-bar { height: 100%; width: 6%; background: #2563eb; transition: width .35s ease; }\n        .loading-card { position: relative; overflow: hidden; }\n        .loading-card::before { content: ''; position: absolute; inset: 0; z-index: 40; background: rgba(243,244,246,.72); backdrop-filter: blur(1px); }\n        .loading-card::after { content: ''; position: absolute; z-index: 41; top: 50%; left: 50%; width: 28px; height: 28px; margin: -14px 0 0 -14px; border: 3px solid #bfdbfe; border-top-color: #2563eb; border-radius: 9999px; animation: portfolio-spin .8s linear infinite; }\n        @keyframes portfolio-spin { to { transform: rotate(360deg); } }\n    </style>\n'''
if needle not in s:
    raise SystemExit('head needle missing')
s = s.replace(needle, insert, 1)

# 2) Blue loading bar just below SethiPortfolio header
needle = '''        <header class="py-4 px-6 border-b border-gray-200 bg-white text-center">\n            <h1 class="text-3xl md:text-4xl font-black tracking-tight text-gray-900">SETHI<span class="text-yellow-600">PORTFOLIO</span></h1>\n        </header>\n'''
replacement = needle + '''        <div id="loading-progress" aria-label="Loading portfolio data"><div id="loading-progress-bar"></div></div>\n'''
if needle not in s:
    raise SystemExit('header needle missing')
s = s.replace(needle, replacement, 1)

# 3) Remove explanatory subtitle and redundant 1Y button
s = s.replace('                            <p class="text-xs text-gray-500 mt-0.5">Rebased to 100 for a like-for-like comparison.</p>\n', '', 1)
s = s.replace('                                <button onclick="setRange(\'1Y\', this)" class="range-btn px-3 py-1.5 rounded-md text-gray-500">1Y</button>\n', '', 1)

# 4) Add period return strip above chart
needle = '                    <div id="performance-chart" style="height:365px"></div>\n'
replacement = '''                    <div id="period-returns" class="grid grid-cols-2 xl:grid-cols-4 gap-2 mb-1">\n                        <div class="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2"><div class="text-[9px] font-black uppercase tracking-wider text-gray-400">Sethi Fundamental</div><div id="period-return-portfolio" class="text-sm font-black mt-0.5 text-gray-900">—</div></div>\n                        <div class="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2"><div class="text-[9px] font-black uppercase tracking-wider text-gray-400">S&amp;P 500 TR</div><div id="period-return-sp500" class="text-sm font-black mt-0.5 text-gray-900">—</div></div>\n                        <div class="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2"><div class="text-[9px] font-black uppercase tracking-wider text-gray-400">Nasdaq-100 (QQQ)</div><div id="period-return-nasdaq" class="text-sm font-black mt-0.5 text-gray-900">—</div></div>\n                        <div class="rounded-lg border border-gray-100 bg-gray-50 px-3 py-2"><div class="text-[9px] font-black uppercase tracking-wider text-gray-400">VWRL</div><div id="period-return-vwrl" class="text-sm font-black mt-0.5 text-gray-900">—</div></div>\n                    </div>\n                    <div id="performance-chart" style="height:330px"></div>\n'''
if needle not in s:
    raise SystemExit('performance chart needle missing')
s = s.replace(needle, replacement, 1)

# 5) Remove 1Y range branch
s = s.replace("        else if (range === '1Y') cutoff.setFullYear(cutoff.getFullYear() - 1);\n", '', 1)

# 6) Insert period return calculator before renderPerformance
needle = '    function renderPerformance() {\n'
helper = '''    function updatePeriodReturns(start) {\n        const keys = ['portfolio', 'sp500', 'nasdaq', 'vwrl'];\n        keys.forEach(key => {\n            const series = portfolioData[key] || [];\n            const window = series.slice(start).filter(v => Number.isFinite(Number(v)));\n            const el = document.getElementById(`period-return-${key}`);\n            if (!el || window.length < 2 || Number(window[0]) === 0) { if (el) el.textContent = '—'; return; }\n            const change = (Number(window.at(-1)) / Number(window[0]) - 1) * 100;\n            el.textContent = fmtPct(change);\n            el.className = `text-sm font-black mt-0.5 ${change >= 0 ? 'text-emerald-600' : 'text-red-600'}`;\n        });\n    }\n\n    function renderPerformance() {\n'''
if needle not in s:
    raise SystemExit('renderPerformance needle missing')
s = s.replace(needle, helper, 1)

# 7) Update period return strip every time the range changes / chart renders
needle = '''    function renderPerformance() {\n        const start = rangeStartIndex(currentRange);\n        const dates = portfolioData.dates.slice(start);\n'''
replacement = '''    function renderPerformance() {\n        const start = rangeStartIndex(currentRange);\n        const dates = portfolioData.dates.slice(start);\n        updatePeriodReturns(start);\n'''
if needle not in s:
    raise SystemExit('renderPerformance body needle missing')
s = s.replace(needle, replacement, 1)

# 8) Add loading lifecycle helpers before loadPortfolio
needle = '    async function loadPortfolio() {\n'
helpers = '''    let loadingTimer;\n    function startLoadingState() {\n        const cards = document.querySelectorAll('main section > div, main > section.bg-white');\n        cards.forEach(card => card.classList.add('loading-card'));\n        const progress = document.getElementById('loading-progress');\n        const bar = document.getElementById('loading-progress-bar');\n        progress.style.display = 'block';\n        bar.style.width = '8%';\n        let pct = 8;\n        loadingTimer = setInterval(() => { pct = Math.min(88, pct + Math.max(2, (88 - pct) * .12)); bar.style.width = `${pct}%`; }, 220);\n    }\n\n    function finishLoadingState() {\n        clearInterval(loadingTimer);\n        const bar = document.getElementById('loading-progress-bar');\n        const progress = document.getElementById('loading-progress');\n        bar.style.width = '100%';\n        document.querySelectorAll('.loading-card').forEach(card => card.classList.remove('loading-card'));\n        setTimeout(() => { progress.style.display = 'none'; bar.style.width = '6%'; }, 350);\n    }\n\n    async function loadPortfolio() {\n        startLoadingState();\n'''
if needle not in s:
    raise SystemExit('loadPortfolio needle missing')
s = s.replace(needle, helpers, 1)

# 9) Ensure loading state resolves on both success and failure
needle = '''            document.getElementById('holdings-table').innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">Unable to load holdings.</td></tr>';\n        }\n    }\n\n    loadPortfolio();\n'''
replacement = '''            document.getElementById('holdings-table').innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">Unable to load holdings.</td></tr>';\n        } finally {\n            finishLoadingState();\n        }\n    }\n\n    loadPortfolio();\n'''
if needle not in s:
    raise SystemExit('loadPortfolio finally needle missing')
s = s.replace(needle, replacement, 1)

p.write_text(s, encoding='utf-8')
print('Patched sethiportfolio.html')
