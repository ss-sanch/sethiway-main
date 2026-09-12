from pathlib import Path

path = Path('sethistock.html')
raw = path.read_bytes()
newline = '\r\n' if b'\r\n' in raw else '\n'
text = raw.decode('utf-8').replace('\r\n', '\n')

def replace_once(old, new):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected one match, found {count}: {old[:120]!r}')
    text = text.replace(old, new, 1)

replace_once(
'''        let state = { ticker: "", period: "1y", interval: "1d", type: "line", fcf: 0, shares: 0, price: 0, stats: null, chartData: null };
        let watchlist = JSON.parse(localStorage.getItem('sethiWatchlist')) || [];
''',
'''        let state = { ticker: "", period: "1y", interval: "1d", type: "line", fcf: 0, shares: 0, price: 0, stats: null, chartData: null };
        let watchlist = JSON.parse(localStorage.getItem('sethiWatchlist')) || [];
        let chartRequestId = 0;
        let chartAbortController = null;
        const chartMemoryCache = new Map();
        const CHART_MEMORY_TTL_MS = 5 * 60 * 1000;
        const CHART_MEMORY_MAX = 48;

        const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

        async function fetchJsonWithRetry(url, options = {}, retries = 1) {
            let lastError = null;
            for (let attempt = 0; attempt <= retries; attempt++) {
                try {
                    const res = await fetch(url, options);
                    let payload = null;
                    try { payload = await res.json(); } catch (_) {}
                    if (!res.ok) {
                        const err = new Error(payload?.detail || `Request failed (${res.status})`);
                        err.status = res.status;
                        if (res.status < 500 || attempt === retries) throw err;
                        lastError = err;
                    } else {
                        return payload;
                    }
                } catch (err) {
                    if (err?.name === 'AbortError') throw err;
                    lastError = err;
                    const retryableHttp = !err?.status || err.status >= 500;
                    if (!retryableHttp || attempt === retries) throw err;
                }
                await sleep(600 * (attempt + 1));
            }
            throw lastError || new Error('Request failed');
        }

        function normaliseChartData(data) {
            const empty = { dates: [], opens: [], highs: [], lows: [], closes: [] };
            if (!data || typeof data !== 'object') return empty;
            const dates = Array.isArray(data.dates) ? data.dates : [];
            const opens = Array.isArray(data.opens) ? data.opens : [];
            const highs = Array.isArray(data.highs) ? data.highs : [];
            const lows = Array.isArray(data.lows) ? data.lows : [];
            const closes = Array.isArray(data.closes) ? data.closes : [];
            const size = Math.min(dates.length, opens.length, highs.length, lows.length, closes.length);
            const clean = { dates: [], opens: [], highs: [], lows: [], closes: [] };
            for (let i = 0; i < size; i++) {
                const close = Number(closes[i]);
                if (!dates[i] || !Number.isFinite(close) || close <= 0) continue;
                const open = Number(opens[i]);
                const high = Number(highs[i]);
                const low = Number(lows[i]);
                clean.dates.push(dates[i]);
                clean.opens.push(Number.isFinite(open) && open > 0 ? open : close);
                clean.highs.push(Number.isFinite(high) && high > 0 ? high : close);
                clean.lows.push(Number.isFinite(low) && low > 0 ? low : close);
                clean.closes.push(close);
            }
            return clean;
        }

        function rememberChart(key, data) {
            chartMemoryCache.delete(key);
            chartMemoryCache.set(key, { data, savedAt: Date.now() });
            while (chartMemoryCache.size > CHART_MEMORY_MAX) {
                chartMemoryCache.delete(chartMemoryCache.keys().next().value);
            }
        }

        function renderPeriodReturn() {
            const pill = document.getElementById('period-pct-pill');
            const closes = state.chartData?.closes || [];
            if (closes.length < 2) {
                pill.classList.add('hidden');
                return;
            }
            const first = Number(closes[0]);
            const last = Number(closes[closes.length - 1]);
            if (!Number.isFinite(first) || !Number.isFinite(last) || first <= 0) {
                pill.classList.add('hidden');
                return;
            }
            const pct = ((last - first) / first) * 100;
            if (!Number.isFinite(pct)) {
                pill.classList.add('hidden');
                return;
            }
            pill.innerText = (pct > 0 ? '+' : '') + pct.toFixed(2) + '%';
            pill.className = pct >= 0
                ? "px-3 py-1 text-sm font-bold text-white rounded-full bg-green-500 shadow-sm transition-colors duration-300"
                : "px-3 py-1 text-sm font-bold text-white rounded-full bg-red-500 shadow-sm transition-colors duration-300";
            pill.classList.remove('hidden');
        }
'''
)

replace_once(
'''                const fullDataPromise = fetch(`${API_URL}/api/stock/${requestedTicker}`).then(async (res) => {
                    const payload = await res.json();
                    if (!res.ok) throw new Error(payload.detail || 'Failed to load stock analysis.');
                    return payload;
                });
                let fullAnalysisReady = false;
                const quoteHydrationPromise = fetch(`${API_URL}/api/quote/${requestedTicker}`)
                    .then(async (res) => res.ok ? await res.json() : null)
                    .then((quoteData) => {
''',
'''                const fullDataPromise = fetchJsonWithRetry(`${API_URL}/api/stock/${encodeURIComponent(requestedTicker)}`, {}, 1);
                let fullAnalysisReady = false;
                const quoteHydrationPromise = fetchJsonWithRetry(`${API_URL}/api/quote/${encodeURIComponent(requestedTicker)}`, {}, 1)
                    .then((quoteData) => {
'''
)

replace_once(
'''            } catch (err) {
                clearInterval(loadingInterval);
                if(loadingBubbleText) loadingBubbleText.innerText = "Data Sync Failed.";
                setTimeout(() => {
                    if (progContainer) progContainer.classList.add('opacity-0');
                    if (loadingBubble) loadingBubble.classList.add('hidden');
                }, 1500);
                document.getElementById('error-message').innerText = err.message;
                document.getElementById('error-message').classList.remove('hidden');
            } finally {
''',
'''            } catch (err) {
                clearInterval(loadingInterval);
                dash.classList.remove('opacity-50');
                dash.classList.add('opacity-100');
                if(loadingBubbleText) loadingBubbleText.innerText = "Data Sync Failed.";
                setTimeout(() => {
                    if (progContainer) progContainer.classList.add('opacity-0');
                    if (loadingBubble) loadingBubble.classList.add('hidden');
                }, 1500);
                const message = err?.message === 'Failed to fetch'
                    ? 'Detailed analysis could not reach the data server. Please retry.'
                    : (err?.message || 'Detailed analysis temporarily unavailable.');
                document.getElementById('error-message').innerText = message;
                document.getElementById('error-message').classList.remove('hidden');
            } finally {
'''
)

replace_once(
'''                const peerQuery = encodeURIComponent(peers.join(','));
                const peerResponse = await fetch(`${API_URL}/api/peers?tickers=${peerQuery}`);
                if (!peerResponse.ok) throw new Error('Failed to fetch competitors.');
                const peerPayload = await peerResponse.json();
''',
'''                const peerQuery = encodeURIComponent(peers.join(','));
                const peerPayload = await fetchJsonWithRetry(`${API_URL}/api/peers?tickers=${peerQuery}`, {}, 1);
'''
)

old_chart = '''        document.querySelectorAll('.tf-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                state.period = e.target.dataset.period; state.interval = e.target.dataset.interval;
                await fetchChart();
            });
        });
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                state.type = e.target.dataset.type;
                drawPriceChart();
            });
        });

        async function fetchChart() {
            try {
                const res = await fetch(`${API_URL}/api/chart/${state.ticker}?period=${state.period}&interval=${state.interval}`);
                state.chartData = await res.json();
                
                if (state.chartData && state.chartData.closes.length > 0) {
                    const first = state.chartData.closes[0];
                    const last = state.chartData.closes[state.chartData.closes.length - 1];
                    const pct = ((last - first) / first) * 100;
                    
                    const pill = document.getElementById('period-pct-pill');
                    pill.innerText = (pct > 0 ? '+' : '') + pct.toFixed(2) + '%';
                    pill.className = pct >= 0 
                        ? "px-3 py-1 text-sm font-bold text-white rounded-full bg-green-500 shadow-sm transition-colors duration-300" 
                        : "px-3 py-1 text-sm font-bold text-white rounded-full bg-red-500 shadow-sm transition-colors duration-300";
                    pill.classList.remove('hidden');
                } else {
                    document.getElementById('period-pct-pill').classList.add('hidden');
                }

                drawPriceChart();
            } catch (err) { console.error("Chart Error", err); }
        }

        function drawPriceChart() {
            if (!state.chartData || state.chartData.dates.length === 0) return;
            let trace = {};
            if (state.type === 'candlestick') {
                trace = { x: state.chartData.dates, open: state.chartData.opens, high: state.chartData.highs, low: state.chartData.lows, close: state.chartData.closes, type: 'candlestick', increasing: {line: {color: '#22c55e'}}, decreasing: {line: {color: '#ef4444'}} };
            } else {
                trace = { x: state.chartData.dates, y: state.chartData.closes, type: 'scatter', mode: 'lines', line: {color: '#2563eb', width: 2.5} };
            }
            const layout = { margin: {t: 10, b: 30, l: 40, r: 10}, xaxis: {showgrid: false, rangeslider: {visible: false}}, yaxis: {showgrid: true, gridcolor: '#f1f5f9'}, plot_bgcolor: 'transparent', paper_bgcolor: 'transparent', autosize: true };
            Plotly.newPlot('price-chart', [trace], layout, {displayModeBar: false, responsive: true});
        }
'''

new_chart = '''        document.querySelectorAll('.tf-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                state.period = e.target.dataset.period;
                state.interval = e.target.dataset.interval;
                fetchChart().catch(() => null);
            });
        });
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                state.type = e.target.dataset.type;
                drawPriceChart();
            });
        });

        async function fetchChart() {
            const ticker = String(state.ticker || '').trim().toUpperCase();
            const period = state.period;
            const interval = state.interval;
            if (!ticker) return null;

            const key = `${ticker}|${period}|${interval}`;
            const requestId = ++chartRequestId;
            if (chartAbortController) chartAbortController.abort();
            chartAbortController = new AbortController();

            const cached = chartMemoryCache.get(key);
            if (cached) {
                state.chartData = cached.data;
                renderPeriodReturn();
                drawPriceChart();
                if (Date.now() - cached.savedAt < CHART_MEMORY_TTL_MS) {
                    chartAbortController = null;
                    return cached.data;
                }
            }

            try {
                const raw = await fetchJsonWithRetry(
                    `${API_URL}/api/chart/${encodeURIComponent(ticker)}?period=${encodeURIComponent(period)}&interval=${encodeURIComponent(interval)}`,
                    { signal: chartAbortController.signal },
                    1
                );
                if (requestId !== chartRequestId) return null;

                const clean = normaliseChartData(raw);
                if (!clean.closes.length) {
                    if (!cached) document.getElementById('period-pct-pill').classList.add('hidden');
                    return cached?.data || clean;
                }

                rememberChart(key, clean);
                state.chartData = clean;
                renderPeriodReturn();
                drawPriceChart();
                return clean;
            } catch (err) {
                if (err?.name !== 'AbortError') console.warn('Chart request failed:', err);
                return cached?.data || null;
            } finally {
                if (requestId === chartRequestId) chartAbortController = null;
            }
        }

        function drawPriceChart() {
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
replace_once(old_chart, new_chart)

path.write_bytes(text.replace('\n', newline).encode('utf-8'))
