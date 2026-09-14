from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text(encoding='utf-8')

anchor = """    function looksLikeTicker(ticker) {\n        return /^[A-Z][A-Z0-9.-]{0,9}$/.test(String(ticker || '').trim().toUpperCase());\n    }\n"""
insert = anchor + """\n    function researchPayloadSettled(payload) {\n        const earnings = payload?.earnings_reaction;\n        const valuation = payload?.valuation_bands;\n        const studySettled = (study, dataKey) => {\n            if (!study || typeof study !== 'object') return false;\n            if (study.available === true) return Array.isArray(study[dataKey]);\n            if (study.available === false) return typeof study.reason === 'string' && study.reason.trim().length > 0;\n            return false;\n        };\n        return studySettled(earnings, 'events') && studySettled(valuation, 'observations');\n    }\n"""
if anchor not in text:
    raise SystemExit('looksLikeTicker anchor not found')
text = text.replace(anchor, insert, 1)

old_prime = """    function primeInitialData(ticker, payload) {\n        const symbol = canonicalSupplementaryTicker(ticker);\n        if (!looksLikeTicker(symbol) || !payload || typeof payload !== 'object') return;\n        const research = payload.research && typeof payload.research === 'object' ? payload.research : payload;\n        if (!research || typeof research !== 'object') return;\n        fastResearchCache.set(symbol, research);\n        if (canonicalSupplementaryTicker(financialTicker) === symbol || !financialTicker) {\n            researchData = research;\n            researchTicker = symbol;\n        }\n    }\n"""
new_prime = """    function primeInitialData(ticker, payload) {\n        const symbol = canonicalSupplementaryTicker(ticker);\n        if (!looksLikeTicker(symbol) || !payload || typeof payload !== 'object') return;\n        const research = payload.research && typeof payload.research === 'object' ? payload.research : payload;\n        if (!research || typeof research !== 'object') return;\n\n        // A cached /api/stock row can predate a successful research calculation and\n        // therefore contain the bare {available:false} placeholders. Do not promote\n        // those placeholders into the fast research cache as if they were final data.\n        const settled = researchPayloadSettled(research);\n        if (settled) fastResearchCache.set(symbol, research);\n        else fastResearchCache.delete(symbol);\n\n        if (canonicalSupplementaryTicker(financialTicker) === symbol || !financialTicker) {\n            researchData = settled ? research : null;\n            researchTicker = settled ? symbol : '';\n        }\n    }\n"""
if old_prime not in text:
    raise SystemExit('primeInitialData anchor not found')
text = text.replace(old_prime, new_prime, 1)

old_draw = """        renderFinancialCharts(fallbackView);\n        displayedView = fallbackView;\n        setStatus('Loading long-run SEC history…', 'loading');\n        loadFinancialHistory('annual').catch(() => null);\n"""
new_draw = """        renderFinancialCharts(fallbackView);\n        displayedView = fallbackView;\n\n        // The full stock-analysis cache is deliberately long-lived. If it contains an\n        // older placeholder research payload, hydrate only these two supplementary\n        // cards from the lightweight research endpoint instead of rebuilding the stock.\n        const supplementaryTicker = canonicalSupplementaryTicker(ticker);\n        if (researchTicker !== supplementaryTicker || !researchPayloadSettled(researchData)) {\n            loadFinancialResearch(ticker, prefetchGeneration).catch(() => null);\n        }\n\n        setStatus('Loading long-run SEC history…', 'loading');\n        loadFinancialHistory('annual').catch(() => null);\n"""
if old_draw not in text:
    raise SystemExit('drawFinancials anchor not found')
text = text.replace(old_draw, new_draw, 1)

path.write_text(text, encoding='utf-8')
print('RESEARCH_HYDRATION_PATCH_OK')
