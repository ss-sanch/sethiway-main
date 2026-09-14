from pathlib import Path

branch_file = Path('sethistock-financial-history.js')
text = branch_file.read_text()

# 1) Persist early research responses so resetForTicker cannot throw them away.
old = """    let researchData = null;\n    let researchTicker = '';\n    const fastEbitdaPromises = new Map();\n    const fastEbitdaCache = new Map();\n"""
new = """    let researchData = null;\n    let researchTicker = '';\n    const fastResearchCache = new Map();\n    const fastEbitdaPromises = new Map();\n    const fastEbitdaCache = new Map();\n"""
assert old in text, 'research state block not found'
text = text.replace(old, new, 1)

# 2) Make the small EBITDA request use the same proven metric bundle as the full endpoint.
old = """        const query = new URLSearchParams({ period: 'annual', metrics: 'ebitda', limit: '5' });\n"""
new = """        const query = new URLSearchParams({ period: 'annual', metrics: SEC_METRICS.join(','), limit: '5' });\n"""
assert old in text, 'fast EBITDA query not found'
text = text.replace(old, new, 1)

# 3) Canonicalise the ticker check used by the fast EBITDA completion callback.
old = """            if (points.length && financialTicker === symbol && fallbackView?.sourceType === 'legacy') {\n"""
new = """            if (points.length && canonicalSupplementaryTicker(financialTicker) === symbol && fallbackView?.sourceType === 'legacy') {\n"""
assert old in text, 'fast EBITDA callback guard not found'
text = text.replace(old, new, 1)

# 4) Replace fire-and-forget research prefetch with a cache that can hydrate the cards immediately.
old = """    function primeSupplementaryFinancialData(ticker) {\n        const symbol = canonicalSupplementaryTicker(ticker);\n        if (!looksLikeTicker(symbol)) return;\n        if (typeof window.getSethiStockResearch === 'function') {\n            window.getSethiStockResearch(symbol).catch(error => {\n                console.debug(`Early research prefetch unavailable for ${symbol}:`, error);\n            });\n        }\n        requestFastEbitda(symbol).catch(() => null);\n    }\n"""
new = """    function primeSupplementaryFinancialData(ticker) {\n        const symbol = canonicalSupplementaryTicker(ticker);\n        if (!looksLikeTicker(symbol)) return;\n\n        if (typeof window.getSethiStockResearch === 'function') {\n            window.getSethiStockResearch(symbol)\n                .then(data => {\n                    if (!data) return null;\n                    fastResearchCache.set(symbol, data);\n\n                    // If the legacy financial cards already exist, hydrate the two research\n                    // cards immediately instead of waiting for the long-run SEC request.\n                    if (canonicalSupplementaryTicker(financialTicker) === symbol) {\n                        researchData = data;\n                        researchTicker = symbol;\n                        if (displayedView?.sourceType === 'legacy') {\n                            renderFinancialCards(displayedView);\n                            drawHistoricalPE();\n                            drawEarningsSurprise();\n                            if (expandedChartId === 'ind-earnings') renderEarningsDetail();\n                            if (expandedChartId === 'ind-pe' || expandedChartId === 'ind-earnings') {\n                                requestAnimationFrame(() => renderExpandedPlot(expandedChartId));\n                            }\n                        }\n                    }\n                    return data;\n                })\n                .catch(error => {\n                    console.debug(`Early research prefetch unavailable for ${symbol}:`, error);\n                    return null;\n                });\n        }\n\n        requestFastEbitda(symbol).catch(() => null);\n    }\n"""
assert old in text, 'primeSupplementaryFinancialData block not found'
text = text.replace(old, new, 1)

# 5) Store research responses loaded through the normal path too.
old = """            researchData = data;\n            researchTicker = symbol;\n"""
new = """            researchData = data;\n            researchTicker = canonicalSupplementaryTicker(symbol);\n            fastResearchCache.set(researchTicker, data);\n"""
assert old in text, 'loadFinancialResearch assignment not found'
text = text.replace(old, new, 1)

# 6) Restore any completed early research data when the main stock response creates the cards.
old = """        financialTicker = ticker;\n        researchData = null;\n        researchTicker = '';\n        fallbackView = buildLegacyView(fin);\n"""
new = """        financialTicker = ticker;\n        const supplementaryTicker = canonicalSupplementaryTicker(ticker);\n        researchData = fastResearchCache.get(supplementaryTicker) || null;\n        researchTicker = researchData ? supplementaryTicker : '';\n        fallbackView = buildLegacyView(fin);\n"""
assert old in text, 'resetForTicker research reset block not found'
text = text.replace(old, new, 1)

branch_file.write_text(text)

# 7) Harden the Company Drivers transition guard against the page's Null-Shield placeholder.
stability = Path('sethistock-ui-stability.js')
st = stability.read_text()
old = """        const section = document.getElementById('company-drivers');\n        if (!section) return;\n"""
new = """        const section = document.getElementById('company-drivers');\n        if (!section || section.is_null_shield || !section.dataset) return;\n"""
assert old in st, 'resetDriverSurface section guard not found'
st = st.replace(old, new, 1)
stability.write_text(st)

# 8) Mark Null-Shield placeholders explicitly and include EBITDA from /api/stock when available.
html_file = Path('sethistock.html')
h = html_file.read_text()
old = """                return { \n                    style: {}, \n                    classList: { add(){}, remove(){}, contains(){} },\n"""
new = """                return { \n                    is_null_shield: true,\n                    dataset: {},\n                    style: {}, \n                    classList: { add(){}, remove(){}, contains(){} },\n"""
assert old in h, 'Null-Shield object block not found'
h = h.replace(old, new, 1)

old = """                let cleanFin = { years: [], revenue: [], net: [], gross_margin: [], op_margin: [], net_margin: [], fcf: [], ocf: [], capex: [], cash: [], debt: [], shares: [] };\n"""
new = """                let cleanFin = { years: [], revenue: [], net: [], ebitda: [], gross_margin: [], op_margin: [], net_margin: [], fcf: [], ocf: [], capex: [], cash: [], debt: [], shares: [] };\n"""
assert old in h, 'cleanFin declaration not found'
h = h.replace(old, new, 1)

old = """                        cleanFin.net.push(data.financials.net[i]);\n                        cleanFin.gross_margin.push(data.financials.gross_margin[i]);\n"""
new = """                        cleanFin.net.push(data.financials.net[i]);\n                        cleanFin.ebitda.push(Array.isArray(data.financials.ebitda) ? data.financials.ebitda[i] : null);\n                        cleanFin.gross_margin.push(data.financials.gross_margin[i]);\n"""
assert old in h, 'cleanFin population point not found'
h = h.replace(old, new, 1)
html_file.write_text(h)

print('FAST_FALLBACK_V2_PATCH_OK')
