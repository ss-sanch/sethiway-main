from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text()

replacements = [
    ("""        card.style.position = '';
        card.style.left = '';
        card.style.top = '';
        card.style.width = '';
        card.style.maxWidth = '';
        card.style.height = '';
        card.style.transform = '';
        card.style.zIndex = '';
        card.style.boxShadow = '';
        card.style.overflow = '';""",
     """        card.style.position = '';
        card.style.left = '';
        card.style.right = '';
        card.style.top = '';
        card.style.bottom = '';
        card.style.width = '';
        card.style.maxWidth = '';
        card.style.height = '';
        card.style.margin = '';
        card.style.transform = '';
        card.style.zIndex = '';
        card.style.boxShadow = '';
        card.style.overflow = '';"""),
    ("backdrop.className = 'fixed inset-0 z-[150] bg-gray-900/55 backdrop-blur-sm';",
     "backdrop.className = 'fixed inset-0 z-[150] bg-gray-900/55';"),
    ("""        card.style.position = 'fixed';
        card.style.left = '50%';
        card.style.top = '7vh';
        card.style.width = '92vw';
        card.style.maxWidth = '1280px';
        card.style.height = '86vh';
        card.style.transform = 'translateX(-50%)';
        card.style.zIndex = '160';
        card.style.boxShadow = '0 30px 70px rgba(15, 23, 42, 0.28)';
        card.style.overflow = chartId === 'ind-earnings' ? 'auto' : 'hidden';""",
     """        // Avoid transforms on the enlarged Plotly container. Transformed SVGs can
        // land on fractional pixels and render soft; fixed edges + auto margins stay crisp.
        card.style.position = 'fixed';
        card.style.left = '0';
        card.style.right = '0';
        card.style.top = '6vh';
        card.style.bottom = '6vh';
        card.style.width = 'calc(100vw - 48px)';
        card.style.maxWidth = '1280px';
        card.style.height = '88vh';
        card.style.margin = '0 auto';
        card.style.transform = 'none';
        card.style.zIndex = '160';
        card.style.boxShadow = '0 30px 70px rgba(15, 23, 42, 0.28)';
        card.style.overflow = chartId === 'ind-earnings' ? 'auto' : 'hidden';"""),
    ("chart.style.height = 'calc(86vh - 118px)';", "chart.style.height = 'calc(88vh - 118px)';"),
    ("""        requestAnimationFrame(() => {
            renderFinancialCharts(displayedView);
            Plotly.Plots.resize(chartId);
        });""",
     """        // Wait for the fixed card to settle before Plotly measures its enlarged box.
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                renderFinancialCharts(displayedView);
                const expandedPlot = document.getElementById(chartId);
                if (expandedPlot) Plotly.Plots.resize(expandedPlot);
                setTimeout(() => {
                    if (expandedPlot?.isConnected) Plotly.Plots.resize(expandedPlot);
                }, 80);
            });
        });"""),
    ("""            autosize: true,
            hovermode: 'x unified',
            xaxis: {""",
     """            autosize: true,
            hovermode: 'x unified',
            hoverlabel: {
                bgcolor: '#ffffff',
                bordercolor: '#cbd5e1',
                font: { color: '#0f172a', size: 12 },
                align: 'left',
                namelength: -1
            },
            xaxis: {""")
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f'Patch target not found: {old[:100]!r}')
    text = text.replace(old, new, 1)

path.write_text(text)
print('EXPANDED_CHART_PATCH_APPLIED')
