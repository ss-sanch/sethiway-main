from pathlib import Path
p = Path('sethistock-financial-history.js')
s = p.read_text()
old = """    injectFinancialHTML = function(fin) {\n        const ticker = String(state.ticker || '').trim().toUpperCase();\n        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);\n        else fallbackView = buildLegacyView(fin);\n        renderFinancialCards(fallbackView);\n    };\n\n    drawFinancials = function(fin) {\n        const ticker = String(state.ticker || '').trim().toUpperCase();\n        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);\n        else fallbackView = buildLegacyView(fin);\n\n        // Keep the existing short history visible instantly, then hydrate the SEC view.\n"""
new = """    injectFinancialHTML = function(fin) {\n        const ticker = String(state.ticker || '').trim().toUpperCase();\n        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);\n        else {\n            fallbackView = buildLegacyView(fin);\n            applyFastEbitdaFallback(ticker, fallbackView);\n        }\n        renderFinancialCards(fallbackView);\n    };\n\n    drawFinancials = function(fin) {\n        const ticker = String(state.ticker || '').trim().toUpperCase();\n        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);\n        else {\n            fallbackView = buildLegacyView(fin);\n            applyFastEbitdaFallback(ticker, fallbackView);\n        }\n\n        // Keep the existing short history visible instantly, then hydrate the SEC view.\n"""
assert old in s, 'inject/draw fallback block not found'
s = s.replace(old,new,1)
p.write_text(s)
print('FAST_EBITDA_RACE_PATCH_OK')
