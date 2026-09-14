from pathlib import Path

html_path = Path('sethistock.html')
html = html_path.read_text(encoding='utf-8')
html_original = html

# 1) Add a lifecycle controller for the expensive full-analysis + quote pair.
needle = "        let chartAbortController = null;\n"
assert needle in html, 'chart controller marker missing'
html = html.replace(needle, needle + "        let analysisAbortController = null;\n", 1)

# 2) Abort the previous ticker lifecycle before launching another expensive analysis.
needle = "            state.ticker = document.getElementById('ticker-input').value.trim().toUpperCase();\n            window.__sethiStockLastAnalysisReady = null;\n"
assert needle in html, 'submit lifecycle marker missing'
html = html.replace(needle, "            state.ticker = document.getElementById('ticker-input').value.trim().toUpperCase();\n            if (analysisAbortController) analysisAbortController.abort();\n            const analysisController = new AbortController();\n            analysisAbortController = analysisController;\n            window.__sethiStockLastAnalysisReady = null;\n", 1)

# 3) Make both above-the-fold lifecycle requests cancellable. Price Action already has
# its own controller and will independently cancel its previous request.
old = "                const fullDataPromise = fetchJsonWithRetry(`${API_URL}/api/stock/${encodeURIComponent(requestedTicker)}`, {}, 1);\n"
assert old in html, 'full analysis request missing'
html = html.replace(old, "                const fullDataPromise = fetchJsonWithRetry(`${API_URL}/api/stock/${encodeURIComponent(requestedTicker)}`, { signal: analysisController.signal }, 1);\n", 1)
old = "                const quoteHydrationPromise = fetchJsonWithRetry(`${API_URL}/api/quote/${encodeURIComponent(requestedTicker)}`, {}, 1)\n"
assert old in html, 'quote request missing'
html = html.replace(old, "                const quoteHydrationPromise = fetchJsonWithRetry(`${API_URL}/api/quote/${encodeURIComponent(requestedTicker)}`, { signal: analysisController.signal }, 1)\n", 1)

# 4) Ignore an obsolete ticker's AbortError instead of painting a false failure state.
old = "            } catch (err) {\n                clearInterval(loadingInterval);\n                dash.classList.remove('opacity-50');\n"
assert old in html, 'analysis catch marker missing'
html = html.replace(old, "            } catch (err) {\n                clearInterval(loadingInterval);\n                if (err?.name === 'AbortError') return;\n                dash.classList.remove('opacity-50');\n", 1)

# 5) Release only the controller belonging to the current lifecycle.
old = "            } finally {\n                if (analysisSequence === window.__sethiStockAnalysisSequence) {\n                    btn.innerHTML = 'Analyse'; btn.disabled = false;\n                }\n            }\n"
assert old in html, 'analysis finally marker missing'
html = html.replace(old, "            } finally {\n                if (analysisAbortController === analysisController) analysisAbortController = null;\n                if (analysisSequence === window.__sethiStockAnalysisSequence) {\n                    btn.innerHTML = 'Analyse'; btn.disabled = false;\n                }\n            }\n", 1)

assert html != html_original, 'sethistock.html unchanged'
html_path.write_text(html, encoding='utf-8')

# Financial-history lifecycle: abort old SEC work immediately on a ticker change and
# stop auto-prefetching Quarterly/TTM. Those views now load only when clicked.
fin_path = Path('sethistock-financial-history.js')
fin = fin_path.read_text(encoding='utf-8')
fin_original = fin

# Remove the automatic post-Annual period prefetch trigger.
old = "            rememberFinancialView(key, view);\n            prefetchOtherPeriods(ticker, period);\n            if (ticker === String(state.ticker || '').trim().toUpperCase() && desiredPeriod === period) {\n"
assert old in fin, 'SEC prefetch trigger missing'
fin = fin.replace(old, "            rememberFinancialView(key, view);\n            if (ticker === String(state.ticker || '').trim().toUpperCase() && desiredPeriod === period) {\n", 1)

# Abort the active long-run SEC request as soon as a new ticker lifecycle starts.
marker = "    // Expose a tiny debugging surface for production smoke tests without coupling the\n"
assert marker in fin, 'financial export marker missing'
lifecycle = """    window.addEventListener('sethistock:analysis-start', () => {\n        prefetchGeneration += 1;\n        requestId += 1;\n        if (requestController) requestController.abort();\n        requestController = null;\n        closeExpandedChart();\n    });\n\n"""
fin = fin.replace(marker, lifecycle + marker, 1)

assert fin != fin_original, 'financial history unchanged'
fin_path.write_text(fin, encoding='utf-8')
print('FRONTEND_RUNTIME_PATCH_OK')
