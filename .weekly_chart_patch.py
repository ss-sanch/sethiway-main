from pathlib import Path

path = Path('sethistock.html')
raw = path.read_bytes()
newline = '\r\n' if b'\r\n' in raw else '\n'
text = raw.decode('utf-8').replace('\r\n', '\n')

old = '''        function drawPriceChart() {
            if (!state.chartData || state.chartData.dates.length === 0) return;
            let trace = {};
            if (state.type === 'candlestick') {
                trace = { x: state.chartData.dates, open: state.chartData.opens, high: state.chartData.highs, low: state.chartData.lows, close: state.chartData.closes, type: 'candlestick', increasing: {line: {color: '#22c55e'}}, decreasing: {line: {color: '#ef4444'}} };
            } else {
                trace = { x: state.chartData.dates, y: state.chartData.closes, type: 'scatter', mode: 'lines', line: {color: '#2563eb', width: 2.5} };
            }
            const layout = { margin: {t: 10, b: 30, l: 40, r: 10}, xaxis: {showgrid: false, rangeslider: {visible: false}}, yaxis: {showgrid: true, gridcolor: '#f1f5f9'}, plot_bgcolor: 'transparent', paper_bgcolor: 'transparent', autosize: true };
            Plotly.react('price-chart', [trace], layout, {displayModeBar: false, responsive: true});
        }
'''

new = '''        function drawPriceChart() {
            if (!state.chartData || state.chartData.dates.length === 0) return;

            const isWeeklyIntraday = state.period === '5d' && state.interval === '15m';
            let trace = {};
            if (state.type === 'candlestick') {
                trace = { x: state.chartData.dates, open: state.chartData.opens, high: state.chartData.highs, low: state.chartData.lows, close: state.chartData.closes, type: 'candlestick', increasing: {line: {color: '#22c55e'}}, decreasing: {line: {color: '#ef4444'}} };
            } else {
                let lineDates = state.chartData.dates;
                let lineCloses = state.chartData.closes;

                // On the 1W intraday view, keep each trading session visually separate.
                // This prevents Plotly drawing an artificial straight line from one day's close to the next day's open.
                if (isWeeklyIntraday) {
                    lineDates = [];
                    lineCloses = [];
                    let previousSession = null;
                    state.chartData.dates.forEach((date, index) => {
                        const session = String(date).slice(0, 10);
                        if (previousSession && session !== previousSession) {
                            lineDates.push(null);
                            lineCloses.push(null);
                        }
                        lineDates.push(date);
                        lineCloses.push(state.chartData.closes[index]);
                        previousSession = session;
                    });
                }

                trace = { x: lineDates, y: lineCloses, type: 'scatter', mode: 'lines', connectgaps: false, line: {color: '#2563eb', width: 2.5} };
            }

            const xaxis = { showgrid: false, rangeslider: {visible: false} };
            if (isWeeklyIntraday) {
                xaxis.rangebreaks = [
                    { bounds: ['sat', 'mon'] },
                    { pattern: 'hour', bounds: [16, 9.5] }
                ];
                xaxis.hoverformat = '%a %d %b, %H:%M';
            }

            const layout = { margin: {t: 10, b: 30, l: 40, r: 10}, xaxis: xaxis, yaxis: {showgrid: true, gridcolor: '#f1f5f9'}, plot_bgcolor: 'transparent', paper_bgcolor: 'transparent', autosize: true };
            Plotly.react('price-chart', [trace], layout, {displayModeBar: false, responsive: true});
        }
'''

if text.count(old) != 1:
    raise SystemExit(f'Expected exactly one drawPriceChart block, found {text.count(old)}')

text = text.replace(old, new, 1)
path.write_bytes(text.replace('\n', newline).encode('utf-8'))
