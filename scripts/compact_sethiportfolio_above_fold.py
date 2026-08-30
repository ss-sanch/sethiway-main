from pathlib import Path

p = Path('sethiportfolio.html')
s = p.read_text(encoding='utf-8')

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Marker not found: {label}')
    s = s.replace(old, new, 1)

rep(
'''        <header class="pt-14 pb-10 flex flex-col justify-center items-center text-center px-6 border-b border-gray-200 bg-white">\n            <h1 class="text-5xl font-black tracking-tight mb-4 text-gray-900">SETHI<span class="text-yellow-600">PORTFOLIO</span></h1>\n            <p class="text-lg text-gray-500 max-w-3xl font-light">\n                A transparent investment journal tracking portfolio decisions, performance and the reasoning behind every allocation.\n            </p>\n        </header>\n\n        <main class="max-w-[1500px] mx-auto px-5 md:px-8 py-10 space-y-8">''',
'''        <header class="py-5 px-6 border-b border-gray-200 bg-white">\n            <div class="max-w-[1500px] mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-2">\n                <h1 class="text-3xl md:text-4xl font-black tracking-tight text-gray-900">SETHI<span class="text-yellow-600">PORTFOLIO</span></h1>\n                <p class="text-sm text-gray-500 md:text-right max-w-2xl">Transparent portfolio decisions, performance and the reasoning behind every allocation.</p>\n            </div>\n        </header>\n\n        <main class="max-w-[1500px] mx-auto px-5 md:px-8 py-5 space-y-4">''',
'compact hero and main spacing')

rep(
'''            <section class="bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-7">\n                <div class="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-5">''',
'''            <section class="bg-white border border-gray-200 rounded-2xl shadow-sm p-4 md:p-5">\n                <div class="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4">''',
'identity compact shell')

rep(
'''                        <div class="flex flex-wrap items-center gap-3 mb-2">''',
'''                        <div class="flex flex-wrap items-center gap-2 mb-1.5">''',
'identity badges spacing')

rep(
'''                        <h2 class="text-3xl font-black tracking-tight text-gray-900">Fundamental Portfolio</h2>\n                        <p class="text-sm md:text-base text-gray-500 mt-2 leading-relaxed">\n                            A bottom-up equity portfolio focused on durable business quality, valuation discipline, cash-flow resilience and long-term capital allocation. Every material portfolio change will be linked to a dated investment note.\n                        </p>''',
'''                        <h2 class="text-2xl md:text-3xl font-black tracking-tight text-gray-900">Fundamental Portfolio</h2>\n                        <p class="text-sm text-gray-500 mt-1.5 leading-relaxed">\n                            Bottom-up equities focused on durable quality, valuation discipline and long-term capital allocation. Every material change links to a dated investment note.\n                        </p>''',
'identity copy compact')

rep(
'''                    <div class="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-2 gap-3 xl:w-[440px]">\n                        <div class="rounded-xl bg-gray-900 text-white p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Portfolio Value</p><p class="text-2xl font-black mt-1">£100,000</p></div>\n                        <div class="rounded-xl bg-emerald-50 border border-emerald-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-emerald-700">Total Return</p><p class="text-2xl font-black mt-1 text-emerald-700">+12.8%</p></div>\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Vs S&amp;P 500</p><p class="text-2xl font-black mt-1 text-gray-900">+3.6pp</p></div>\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 p-4"><p class="text-[10px] uppercase tracking-widest font-black text-gray-400">Since</p><p class="text-2xl font-black mt-1 text-gray-900">Jun 2026</p></div>\n                    </div>\n                </div>\n                <p class="text-[10px] text-gray-400 mt-5 border-t border-gray-100 pt-4">V1 uses illustrative data to validate the public dashboard layout. It does not represent the live SethiPortfolio holdings or track record.</p>''',
'''                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 xl:w-[620px]">\n                        <div class="rounded-xl bg-gray-900 text-white px-4 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Portfolio Value</p><p class="text-xl font-black mt-0.5">£100,000</p></div>\n                        <div class="rounded-xl bg-emerald-50 border border-emerald-100 px-4 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-emerald-700">Total Return</p><p class="text-xl font-black mt-0.5 text-emerald-700">+12.8%</p></div>\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 px-4 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Vs S&amp;P 500</p><p class="text-xl font-black mt-0.5 text-gray-900">+3.6pp</p></div>\n                        <div class="rounded-xl bg-gray-50 border border-gray-100 px-4 py-3"><p class="text-[9px] uppercase tracking-widest font-black text-gray-400">Since</p><p class="text-xl font-black mt-0.5 text-gray-900">Jun 2026</p></div>\n                    </div>\n                </div>\n                <div class="mt-3 flex justify-end"><span class="text-[9px] text-gray-400 bg-gray-50 border border-gray-100 rounded-full px-3 py-1">Illustrative V1 data · not a live track record</span></div>''',
'identity kpis compact')

rep(
'''            <section class="bg-white border border-gray-200 rounded-2xl shadow-sm p-5 md:p-7">\n                <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-4">''',
'''            <section class="bg-white border border-gray-200 rounded-2xl shadow-sm p-4 md:p-5">\n                <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3 mb-2">''',
'performance compact shell')

rep(
'''                        <h3 class="text-2xl font-black text-gray-900">Portfolio vs Benchmarks</h3>\n                        <p class="text-sm text-gray-500 mt-1">Rebased to 100 at the start of the selected period for a like-for-like comparison.</p>''',
'''                        <h3 class="text-xl md:text-2xl font-black text-gray-900">Portfolio vs Benchmarks</h3>\n                        <p class="text-xs text-gray-500 mt-0.5">Rebased to 100 for a like-for-like comparison.</p>''',
'performance heading compact')

rep(
'''                <div class="flex flex-wrap gap-2 mb-3">''',
'''                <div class="flex flex-wrap gap-2 mb-1">''',
'benchmark toggle spacing')

rep(
'''                <div id="performance-chart" style="height:420px"></div>''',
'''                <div id="performance-chart" style="height:330px"></div>''',
'performance chart height')

p.write_text(s, encoding='utf-8')
