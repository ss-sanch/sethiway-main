from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text()

old = """    function emptyChart(id, message = 'Data Unavailable') {\n        const element = document.getElementById(id);\n        if (element) element.innerHTML = `<div class=\"flex h-full items-center justify-center text-gray-400 font-bold text-sm text-center px-5\">${message}</div>`;\n    }\n"""
new = """    function emptyChart(id, message = 'Data Unavailable') {\n        const element = document.getElementById(id);\n        if (!element) return;\n        if (typeof Plotly !== 'undefined' && (element.classList.contains('js-plotly-plot') || element._fullLayout)) {\n            try { Plotly.purge(element); } catch (_) {}\n        }\n        element.innerHTML = `<div class=\"flex h-full items-center justify-center text-gray-400 font-bold text-sm text-center px-5\">${message}</div>`;\n    }\n\n    function preparePlotContainer(id) {\n        const element = document.getElementById(id);\n        if (!element) return null;\n        const hasPlot = element.classList.contains('js-plotly-plot') || Boolean(element._fullLayout);\n        if (!hasPlot) element.innerHTML = '';\n        return element;\n    }\n"""
assert old in text, 'emptyChart block not found'
text = text.replace(old, new, 1)

text = text.replace(
"""    function drawSingleMetric(view, id, key, colour, options = {}) {\n        const trace = traceForMetric(view, key, options.name || key, colour, options);\n        if (!trace) return emptyChart(id);\n        const layout = chartLayout(view, false);\n""",
"""    function drawSingleMetric(view, id, key, colour, options = {}) {\n        const trace = traceForMetric(view, key, options.name || key, colour, options);\n        if (!trace) return emptyChart(id);\n        if (!preparePlotContainer(id)) return;\n        const layout = chartLayout(view, false);\n""",
1)

text = text.replace(
"""        if (!traces.length) return emptyChart('ind-margins');\n        const layout = chartLayout(view, true);\n""",
"""        if (!traces.length) return emptyChart('ind-margins');\n        if (!preparePlotContainer('ind-margins')) return;\n        const layout = chartLayout(view, true);\n""",
1)

text = text.replace(
"""        const chartElement = document.getElementById('ind-pe');\n        if (chartElement && !chartElement.classList.contains('js-plotly-plot')) chartElement.innerHTML = '';\n        const layout = chartLayout({ period: 'quarterly' }, false);\n""",
"""        if (!preparePlotContainer('ind-pe')) return;\n        const layout = chartLayout({ period: 'quarterly' }, false);\n""",
1)

text = text.replace(
"""        const chartElement = document.getElementById('ind-earnings');\n        if (chartElement && !chartElement.classList.contains('js-plotly-plot')) chartElement.innerHTML = '';\n        const layout = chartLayout({ period: 'quarterly' }, false);\n""",
"""        if (!preparePlotContainer('ind-earnings')) return;\n        const layout = chartLayout({ period: 'quarterly' }, false);\n""",
1)

text = text.replace(
"""        if (traces.length < 2) return emptyChart(id);\n        const layout = chartLayout(view, true);\n""",
"""        if (traces.length < 2) return emptyChart(id);\n        if (!preparePlotContainer(id)) return;\n        const layout = chartLayout(view, true);\n""",
1)

path.write_text(text)
print('GENERIC_PLACEHOLDER_PATCH_APPLIED')
