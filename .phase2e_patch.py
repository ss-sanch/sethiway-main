from pathlib import Path

path = Path('sethistock.html')
text = path.read_text(encoding='utf-8')

old_css = '.tf-btn.active, .type-btn.active { background-color: #2563eb; color: white; border-color: #2563eb; }'
new_css = '.tf-btn.active, .type-btn.active, .financial-period-btn.active { background-color: #2563eb; color: white; border-color: #2563eb; }'
assert old_css in text, 'active-button CSS anchor missing'
text = text.replace(old_css, new_css, 1)

old_financial = '''        <div id="key-metrics" class="scroll-mt-24">
            <h3 class="text-2xl font-black mt-10 mb-2 border-b pb-4">Key Financial Metrics</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6" id="individual-charts-container"></div>
        </div>
'''
new_financial = '''        <div id="key-metrics" class="scroll-mt-24">
            <div class="mt-10 mb-5 border-b border-gray-200 pb-4 flex flex-col lg:flex-row lg:items-end justify-between gap-4">
                <div>
                    <div class="flex items-center gap-3 flex-wrap">
                        <h3 class="text-2xl font-black">Key Financial Metrics</h3>
                        <span class="px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-[10px] font-black text-emerald-700 uppercase tracking-widest">SEC History</span>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">Long-run fundamentals from company filings, with consistent Annual, Quarterly and trailing-twelve-month views.</p>
                </div>
                <div class="flex flex-col items-start lg:items-end">
                    <div id="financial-period-controls" class="flex space-x-1 bg-gray-100 p-1 rounded-lg border border-gray-200" aria-label="Financial history period">
                        <button type="button" class="financial-period-btn active px-4 py-1.5 text-xs sm:text-sm font-bold rounded-md text-gray-600 transition" data-financial-period="annual">Annual</button>
                        <button type="button" class="financial-period-btn px-4 py-1.5 text-xs sm:text-sm font-bold rounded-md text-gray-600 transition" data-financial-period="quarterly">Quarterly</button>
                        <button type="button" class="financial-period-btn px-4 py-1.5 text-xs sm:text-sm font-bold rounded-md text-gray-600 transition" data-financial-period="ttm">TTM</button>
                    </div>
                    <p id="financial-history-status" class="text-[11px] font-bold uppercase tracking-widest mt-2 text-right text-gray-400">Search a stock to load filing history</p>
                </div>
            </div>
            <div id="financial-history-alert" class="hidden mb-5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs font-semibold leading-relaxed text-amber-900"></div>
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6" id="individual-charts-container"></div>
        </div>
'''
assert old_financial in text, 'financial section anchor missing'
text = text.replace(old_financial, new_financial, 1)

old_comparison = '''        <div id="comparisons" class="scroll-mt-24">
            <h3 class="text-2xl font-black mt-10 mb-2 border-b pb-4">Financial Comparisons</h3>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
'''
new_comparison = '''        <div id="comparisons" class="scroll-mt-24">
            <div class="mt-10 mb-2 border-b border-gray-200 pb-4 flex items-center justify-between gap-4">
                <h3 class="text-2xl font-black">Financial Comparisons</h3>
                <span id="comparison-period-label" class="px-2.5 py-1 rounded-md bg-gray-100 border border-gray-200 text-[10px] font-black text-gray-500 uppercase tracking-widest">Annual</span>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
'''
assert old_comparison in text, 'comparison section anchor missing'
text = text.replace(old_comparison, new_comparison, 1)

old_scripts = '''    </script>
    <script src="sethiway-history.js"></script>
</body>
</html>'''
new_scripts = '''    </script>
    <script src="sethistock-financial-history.js"></script>
    <script src="sethiway-history.js"></script>
</body>
</html>'''
assert old_scripts in text, 'footer script anchor missing'
text = text.replace(old_scripts, new_scripts, 1)

path.write_text(text, encoding='utf-8')
print('PHASE2E_HTML_PATCHED')
