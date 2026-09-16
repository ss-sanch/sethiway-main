from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text(encoding='utf-8')

old = """    function bindExpandButtons() {\n        document.querySelectorAll('.financial-expand-btn').forEach(button => {\n            button.addEventListener('click', () => toggleExpandedChart(button.dataset.chartId));\n        });\n    }\n\n    function renderFinancialCards(view) {\n"""
new = """    function bindExpandButtons() {\n        document.querySelectorAll('.financial-expand-btn').forEach(button => {\n            button.addEventListener('click', () => toggleExpandedChart(button.dataset.chartId));\n        });\n    }\n\n    function bindRevenueDriverButton() {\n        const button = document.getElementById('financial-segment-button');\n        if (!button || button.dataset.bound === '1') return;\n        button.dataset.bound = '1';\n        button.addEventListener('click', () => {\n            const ticker = String((typeof state === 'object' ? state?.ticker : '') || document.getElementById('display-ticker')?.textContent || '').trim().toUpperCase();\n            if (!ticker || typeof window.SethiStockOpenRevenueDrivers !== 'function') return;\n            window.SethiStockOpenRevenueDrivers(ticker).catch?.(() => null);\n        });\n    }\n\n    function syncRevenueDriverButton() {\n        const button = document.getElementById('financial-segment-button');\n        if (!button) return;\n        const ticker = String((typeof state === 'object' ? state?.ticker : '') || document.getElementById('display-ticker')?.textContent || '').trim().toUpperCase();\n        const supported = typeof window.SethiStockHasRevenueDrivers === 'function'\n            ? window.SethiStockHasRevenueDrivers(ticker)\n            : ['AAPL','MSFT','GOOG','GOOGL','AMZN','META','NVDA','TSLA','NFLX','JPM','V'].includes(ticker);\n        button.classList.toggle('hidden', !supported);\n        button.disabled = !supported;\n    }\n\n    function renderFinancialCards(view) {\n"""
if old not in text:
    raise SystemExit('bindExpandButtons anchor not found')
text = text.replace(old, new, 1)

old = """                            <div class=\"flex items-center gap-2\">\n                                <span id=\"fin-period-${card.id}\" class=\"px-2 py-1 rounded-md bg-gray-50 border border-gray-100 text-[9px] font-black text-gray-400 uppercase tracking-widest\">${initialBadge}</span>\n"""
new = """                            <div class=\"flex items-center gap-2\">\n                                ${card.id === 'ind-rev' ? `<button id=\"financial-segment-button\" type=\"button\" class=\"financial-segment-btn hidden items-center gap-1 px-2.5 py-1 rounded-lg border border-blue-200 bg-blue-50 text-[9px] font-black text-blue-700 uppercase tracking-wider hover:bg-blue-100 hover:border-blue-300 transition whitespace-nowrap\" title=\"Open company revenue segments and operating drivers\">By Segment <span aria-hidden=\"true\">→</span></button>` : ''}\n                                <span id=\"fin-period-${card.id}\" class=\"px-2 py-1 rounded-md bg-gray-50 border border-gray-100 text-[9px] font-black text-gray-400 uppercase tracking-widest\">${initialBadge}</span>\n"""
if old not in text:
    raise SystemExit('Revenue card actions anchor not found')
text = text.replace(old, new, 1)

old = """            bindExpandButtons();\n        }\n\n        cards.forEach(card => {\n"""
new = """            bindExpandButtons();\n            bindRevenueDriverButton();\n        }\n\n        syncRevenueDriverButton();\n        cards.forEach(card => {\n"""
if old not in text:
    raise SystemExit('render binding anchor not found')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('PHASE4B_REVENUE_BUTTON_PATCH_OK')
