from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

old = """        const traces = [
            {key:'portfolio', values:portfolioRolling, meta:seriesMeta.portfolio},
            {key:'benchmark', values:benchmarkRolling, meta:seriesMeta[currentBenchmark]},
        ].map(item => ({
            x: dates.slice(displayStart),
            y: item.values.slice(displayStart),
            name: item.meta.name,
            type:'scatter', mode:'lines', connectgaps:false,
            line:{color:item.meta.color, width:item.key === 'portfolio' ? 3 : 2, dash:item.key === 'portfolio' ? 'solid' : item.meta.dash},
            hovertemplate:`%{x}<br>${metricLabel}: %{y:.2f}%<extra>${item.meta.name}</extra>`
        }));
        const hasData = traces.some(trace => trace.y.some(Number.isFinite));
        if (!hasData) {
            chart.innerHTML = `<div class=\"h-full flex items-center justify-center text-center px-6 text-sm text-gray-400\">Not enough history for a ${windowLabel} ${metricLabel.toLowerCase()} in the selected period.</div>`;
            return;
        }
"""

new = """        let chartStart = -1;
        for (let i = displayStart; i < dates.length; i++) {
            if (Number.isFinite(portfolioRolling[i]) || Number.isFinite(benchmarkRolling[i])) {
                chartStart = i;
                break;
            }
        }
        if (chartStart < 0) {
            chart.innerHTML = `<div class=\"h-full flex items-center justify-center text-center px-6 text-sm text-gray-400\">Not enough history for a ${windowLabel} ${metricLabel.toLowerCase()} in the selected period.</div>`;
            return;
        }

        const traces = [
            {key:'portfolio', values:portfolioRolling, meta:seriesMeta.portfolio},
            {key:'benchmark', values:benchmarkRolling, meta:seriesMeta[currentBenchmark]},
        ].map(item => ({
            x: dates.slice(chartStart),
            y: item.values.slice(chartStart),
            name: item.meta.name,
            type:'scatter', mode:'lines', connectgaps:false,
            line:{color:item.meta.color, width:item.key === 'portfolio' ? 3 : 2, dash:item.key === 'portfolio' ? 'solid' : item.meta.dash},
            hovertemplate:`%{x}<br>${metricLabel}: %{y:.2f}%<extra>${item.meta.name}</extra>`
        }));
"""

if old not in text:
    raise SystemExit('Rolling chart anchor not found')
text = text.replace(old, new, 1)
path.write_text(text)
