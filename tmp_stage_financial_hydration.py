from pathlib import Path

p = Path('sethistock-financial-history.js')
s = p.read_text()

old = "const query = new URLSearchParams({ period: 'annual', metrics: SEC_METRICS.join(','), limit: '5' });"
new = "const query = new URLSearchParams({ period: 'annual', metrics: 'ebitda', limit: '5' });"
if old not in s:
    raise SystemExit('fast EBITDA query anchor missing')
s = s.replace(old, new, 1)

old = """        fallbackView = buildLegacyView(fin);\n        applyFastEbitdaFallback(ticker, fallbackView);\n        primeSupplementaryFinancialData(ticker);\n        displayedView = fallbackView;"""
new = """        fallbackView = buildLegacyView(fin);\n        applyFastEbitdaFallback(ticker, fallbackView);\n        displayedView = fallbackView;"""
if old not in s:
    raise SystemExit('reset anchor missing')
s = s.replace(old, new, 1)

old = """    drawFinancials = function(fin) {\n        const ticker = String(state.ticker || '').trim().toUpperCase();\n        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);\n        else {\n            fallbackView = buildLegacyView(fin);\n            applyFastEbitdaFallback(ticker, fallbackView);\n        }\n\n        // Keep the existing short history visible instantly, then hydrate the SEC view.\n        renderFinancialCharts(fallbackView);\n        displayedView = fallbackView;\n        setStatus('Loading long-run SEC history…', 'loading');\n        loadFinancialHistory('annual').catch(() => null);\n        loadFinancialResearch(ticker, prefetchGeneration).catch(() => null);\n    };"""
new = """    drawFinancials = function(fin) {\n        const ticker = String(state.ticker || '').trim().toUpperCase();\n        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);\n        else {\n            fallbackView = buildLegacyView(fin);\n            applyFastEbitdaFallback(ticker, fallbackView);\n        }\n\n        // Keep the existing short history visible instantly. Then stage the two\n        // supplementary requests before the heavy long-run SEC hydration so Render\n        // is not hit by a burst of expensive requests at analysis start.\n        renderFinancialCharts(fallbackView);\n        displayedView = fallbackView;\n        setStatus('Loading recent research and EBITDA…', 'loading');\n\n        const generation = prefetchGeneration;\n        const symbol = canonicalSupplementaryTicker(ticker);\n        (async () => {\n            try {\n                await loadFinancialResearch(symbol, generation);\n            } catch (_) {}\n\n            if (generation !== prefetchGeneration || canonicalSupplementaryTicker(financialTicker) !== symbol) return;\n\n            try {\n                await requestFastEbitda(symbol);\n            } catch (_) {}\n\n            if (generation !== prefetchGeneration || canonicalSupplementaryTicker(financialTicker) !== symbol) return;\n            if (fallbackView?.sourceType === 'legacy') {\n                applyFastEbitdaFallback(symbol, fallbackView);\n                renderFinancialCards(fallbackView);\n                renderFinancialCharts(fallbackView);\n                displayedView = fallbackView;\n            }\n\n            setStatus('Loading long-run SEC history…', 'loading');\n            loadFinancialHistory('annual').catch(() => null);\n        })();\n    };"""
if old not in s:
    raise SystemExit('drawFinancials anchor missing')
s = s.replace(old, new, 1)

start = """    // Start the lightweight supplementary requests as soon as a ticker search begins.\n    // They are independent from the long-run SEC hydration, so the three newer cards\n    // can populate alongside the legacy 4-year fallback instead of waiting behind it.\n    window.addEventListener('sethistock:analysis-start', event => {\n        const ticker = canonicalSupplementaryTicker(event?.detail?.ticker);\n        if (looksLikeTicker(ticker)) primeSupplementaryFinancialData(ticker);\n    });\n    window.addEventListener('sethistock:analysis-ready', event => {\n        const ticker = canonicalSupplementaryTicker(event?.detail?.ticker);\n        if (looksLikeTicker(ticker)) primeSupplementaryFinancialData(ticker);\n    });\n    if (window.__sethiStockLastAnalysisReady?.ticker) {\n        primeSupplementaryFinancialData(window.__sethiStockLastAnalysisReady.ticker);\n    }\n\n"""
if start not in s:
    raise SystemExit('early request listener block missing')
s = s.replace(start, "", 1)

p.write_text(s)
