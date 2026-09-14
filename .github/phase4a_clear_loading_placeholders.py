from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text()

old = """        const layout = chartLayout({ period: 'quarterly' }, false);\n        layout.yaxis.tickformat = '.1f';\n        layout.yaxis.ticksuffix = 'x';"""
new = """        const chartElement = document.getElementById('ind-pe');\n        if (chartElement && !chartElement.classList.contains('js-plotly-plot')) chartElement.innerHTML = '';\n        const layout = chartLayout({ period: 'quarterly' }, false);\n        layout.yaxis.tickformat = '.1f';\n        layout.yaxis.ticksuffix = 'x';"""
if old not in text:
    raise SystemExit('P/E render target not found')
text = text.replace(old, new, 1)

old = """        const layout = chartLayout({ period: 'quarterly' }, false);\n        layout.yaxis.tickformat = '.1f';\n        layout.yaxis.ticksuffix = '%';\n        layout.bargap = 0.28;"""
new = """        const chartElement = document.getElementById('ind-earnings');\n        if (chartElement && !chartElement.classList.contains('js-plotly-plot')) chartElement.innerHTML = '';\n        const layout = chartLayout({ period: 'quarterly' }, false);\n        layout.yaxis.tickformat = '.1f';\n        layout.yaxis.ticksuffix = '%';\n        layout.bargap = 0.28;"""
if old not in text:
    raise SystemExit('Earnings render target not found')
text = text.replace(old, new, 1)

path.write_text(text)
