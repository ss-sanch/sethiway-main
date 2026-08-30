from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')

# Remove the accidentally nested Backtest detail wrapper from the Options panel.
bad = '''                    <div id="options-insights-detail" class="hidden">\n                    <div id="backtest-insights-detail" class="hidden">\n                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">'''
good = '''                    <div id="options-insights-detail" class="hidden">\n                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">'''
if bad not in s:
    raise SystemExit('Accidental nested options/backtest wrapper not found')
s = s.replace(bad, good, 1)

# Wrap the Backtest diagnostics body so only the teaser/header is visible before execution.
marker = '''                <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-5">\n                    <div><p class="text-[10px] font-black uppercase tracking-widest text-teal-600 mb-1">Backtest Diagnostics</p><h3 class="text-xl font-black text-gray-900">Was the return actually worth the risk?</h3><p id="bt-insight-summary" class="text-sm text-gray-500 mt-1 max-w-3xl">Run a strategy to reveal drawdowns, trade quality, market exposure and risk-adjusted performance.</p></div>\n                    <button type="button" onclick="toggleModal('modal-backtest')" class="shrink-0 px-4 py-2 rounded-lg border border-teal-200 bg-teal-50 text-teal-700 text-xs font-black hover:bg-teal-100 transition">How to interpret this</button>\n                </div>\n                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">'''
replacement = '''                <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-5">\n                    <div><p class="text-[10px] font-black uppercase tracking-widest text-teal-600 mb-1">Backtest Diagnostics</p><h3 class="text-xl font-black text-gray-900">Was the return actually worth the risk?</h3><p id="bt-insight-summary" class="text-sm text-gray-500 mt-1 max-w-3xl">Run a strategy to reveal drawdowns, trade quality, market exposure and risk-adjusted performance.</p></div>\n                    <button type="button" onclick="toggleModal('modal-backtest')" class="shrink-0 px-4 py-2 rounded-lg border border-teal-200 bg-teal-50 text-teal-700 text-xs font-black hover:bg-teal-100 transition">How to interpret this</button>\n                </div>\n                <div id="backtest-insights-detail" class="hidden">\n                <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">'''
if marker not in s:
    raise SystemExit('Backtest diagnostics wrapper marker not found')
s = s.replace(marker, replacement, 1)

p.write_text(s, encoding='utf-8')
