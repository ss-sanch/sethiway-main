(() => {
    'use strict';

    const $ = id => document.getElementById(id);
    const quotes = new Map([
        ['MSFT', { name: 'Microsoft', price: 428.60, currency: 'USD', change: 0.86, pe: 31.2 }],
        ['AAPL', { name: 'Apple', price: 241.73, currency: 'USD', change: -0.42, pe: 28.6 }],
        ['NVDA', { name: 'NVIDIA', price: 152.39, currency: 'USD', change: 1.71, pe: 34.8 }],
        ['VWRP.L', { name: 'Vanguard FTSE All-World', price: 119.84, currency: 'GBP', change: 0.24, pe: null }],
        ['GOOGL', { name: 'Alphabet', price: 189.32, currency: 'USD', change: 0.63, pe: 21.4 }],
        ['JPM', { name: 'JPMorgan Chase', price: 270.18, currency: 'USD', change: -0.18, pe: 14.1 }],
        ['AZN.L', { name: 'AstraZeneca', price: 118.42, currency: 'GBP', change: -0.31, pe: 17.1 }]
    ]);
    const benchmarks = {
        sp500: { ticker: 'SPY', label: 'S&P 500 (SPY)', currency: 'USD' },
        founder: { ticker: 'SethiPortfolio', label: 'SethiPortfolio', currency: 'GBP' }
    };
    const fxTicker = 'USDGBP=X';
    // The chart feed quotes AZN.L in pence and VWRP.L in pounds.
    const londonPence = new Set(['AZN.L']);
    const api = 'https://sethistock-api.onrender.com/api/';
    const dayMs = 86400000;
    const gbp = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 });
    const dateLabel = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
    const signed = (value, unit) => (value > 0 ? '+' : '') + value.toFixed(1) + unit;
    let resizeChart;
    let activeRequest;
    const historyCache = new Map();

    window.SethiWayPreviewQuotes = quotes;

    async function readHistory(ticker, signal) {
        const cached = historyCache.get(ticker);
        if (cached && Date.now() < cached.expires) return cached.rows;
        try {
            const isFounder = ticker === benchmarks.founder.ticker;
            const path = isFounder ? 'portfolio/fundamental/performance'
                : 'chart/' + encodeURIComponent(ticker) + '?period=1y&interval=1d';
            const response = await fetch(api + path, {
                signal: AbortSignal.any([signal, AbortSignal.timeout(35000)])
            });
            if (!response.ok) throw new Error();
            const data = await response.json();
            if (isFounder && data.base_currency !== 'GBP') throw new Error();
            const { dates } = data;
            const closes = isFounder ? data.portfolio : data.closes;
            if (!Array.isArray(dates) || !Array.isArray(closes) || dates.length !== closes.length) throw new Error();
            const today = new Date().toISOString().slice(0, 10);
            const divisor = londonPence.has(ticker) ? 100 : 1;
            const byDate = new Map();
            dates.forEach((date, index) => {
                const day = typeof date === 'string' ? date.slice(0, 10) : '';
                const close = closes[index];
                if (/^\d{4}-\d{2}-\d{2}$/.test(day) && day < today && Number.isFinite(close) && close > 0) {
                    byDate.set(day, close / divisor);
                }
            });
            const rows = [...byDate].sort(([a], [b]) => a.localeCompare(b));
            if (rows.length < 2) throw new Error();
            historyCache.set(ticker, { rows, expires: Date.now() + 300000 });
            return rows;
        } catch {
            return null;
        }
    }

    function comparisonSources(benchmark, holdings) {
        const symbols = holdings.map(({ ticker }) => ticker);
        if (benchmark.currency === 'USD' || symbols.some(ticker => quotes.get(ticker).currency === 'USD')) symbols.push(fxTicker);
        return symbols;
    }

    function comparePortfolio(cash, holdings, histories, benchmark, sources) {
        const latest = [benchmark.ticker, ...sources].map(ticker => histories.get(ticker).at(-1)[0]).sort()[0];
        const start = new Date(latest);
        const day = start.getUTCDate();
        start.setUTCDate(1);
        start.setUTCMonth(start.getUTCMonth() - 6);
        const monthEnd = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth() + 1, 0));
        start.setUTCDate(Math.min(day, monthEnd.getUTCDate()));
        const cutoff = start.toISOString().slice(0, 10);
        const cursors = new Map(sources.map(ticker => [ticker, 0]));
        let points = [];
        for (const [date, benchmarkClose] of histories.get(benchmark.ticker)) {
            if (date < cutoff) continue;
            if (date > latest) break;
            const prices = new Map();
            for (const ticker of sources) {
                const series = histories.get(ticker);
                let index = cursors.get(ticker);
                while (series[index + 1]?.[0] <= date) index++;
                cursors.set(ticker, index);
                const [asOf, price] = series[index];
                if (asOf <= date && Date.parse(date) - Date.parse(asOf) <= 7 * dayMs) prices.set(ticker, price);
            }
            if (prices.size !== sources.length) {
                points = [];
                continue;
            }
            const fx = prices.get(fxTicker);
            const holdingValues = holdings.map(({ ticker, shares }) => shares * prices.get(ticker) * (quotes.get(ticker).currency === 'USD' ? fx : 1));
            const value = cash + holdingValues.reduce((sum, holdingValue) => sum + holdingValue, 0);
            points.push({ date, value, benchmark: benchmarkClose * (benchmark.currency === 'USD' ? fx : 1), holdingValues });
        }
        return points.length >= 2 ? points : null;
    }

    function drawChart(canvas, portfolioPath, benchmarkPath, dates) {
        const { width, height } = canvas.getBoundingClientRect();
        if (!width || !height) return;
        const scale = window.devicePixelRatio || 1;
        canvas.width = Math.round(width * scale);
        canvas.height = Math.round(height * scale);
        const ctx = canvas.getContext('2d');
        ctx.scale(scale, scale);

        const points = [...portfolioPath, ...benchmarkPath];
        const low = Math.floor((Math.min(...points) - 1) / 5) * 5;
        const high = Math.ceil((Math.max(...points) + 1) / 5) * 5;
        const chartWidth = width - 46;
        const chartHeight = height - 28;
        const y = value => 8 + (high - value) / (high - low) * chartHeight;
        const x = index => 33 + index / (portfolioPath.length - 1) * chartWidth;
        ctx.font = '11px system-ui';
        ctx.strokeStyle = '#e2e8f0';
        ctx.fillStyle = '#475569';
        for (let i = 0; i <= 4; i++) {
            const value = low + (high - low) / 4 * i;
            ctx.beginPath();
            ctx.moveTo(x(0), y(value));
            ctx.lineTo(x(portfolioPath.length - 1), y(value));
            ctx.stroke();
            ctx.fillText(value.toFixed(0), 1, y(value) + 3);
        }
        ctx.fillText(dateLabel.format(new Date(dates[0])), x(0), height - 2);
        ctx.textAlign = 'right';
        ctx.fillText(dateLabel.format(new Date(dates.at(-1))), x(dates.length - 1), height - 2);
        for (const [path, colour, dash] of [[benchmarkPath, '#64748b', [5, 4]], [portfolioPath, '#1d4ed8', []]]) {
            ctx.beginPath();
            ctx.strokeStyle = colour;
            ctx.lineWidth = 2.5;
            ctx.setLineDash(dash);
            path.forEach((value, index) => index ? ctx.lineTo(x(index), y(value)) : ctx.moveTo(x(index), y(value)));
            ctx.stroke();
        }
    }

    window.initialisePreviewPortfolio = (userId, storage, reportSave) => {
        const storageKey = 'sethiway-visual-portfolios-' + userId;
        const stored = storage ? storage.get('paper_portfolios') : JSON.parse(sessionStorage.getItem(storageKey) || 'null');
        const state = stored || {
            selected: 0,
            benchmark: 'sp500',
            portfolios: storage ? [{ name: 'My paper portfolio', cash: 0, positions: {} }] : [{ name: 'Example portfolio', cash: 1250, positions: { 'MSFT': 12, 'VWRP.L': 34, 'AAPL': 8, 'AZN.L': 20, 'JPM': 9 } }]
        };
        const form = $('paper-form');
        const select = $('paper-portfolio-select');
        const comparator = $('paper-benchmark');
        const canvas = $('paper-chart');
        const positionInputs = new Map();
        let creating = false;
        let paths;
        const save = () => {
            if (storage) reportSave(storage.save('paper_portfolios', state), 'paper_portfolios');
            else sessionStorage.setItem(storageKey, JSON.stringify(state));
        };

        function renderHoldings(holdings, point) {
            const rows = holdings.map(({ ticker, shares }, index) => ({ ticker, shares, value: point?.holdingValues[index] }))
                .sort((a, b) => (b.value ?? 0) - (a.value ?? 0)).map(({ ticker, shares, value }) => {
                const row = document.createElement('li');
                row.className = 'flex items-center justify-between gap-3 py-2';
                const link = document.createElement('a');
                link.href = 'sethistock.html?ticker=' + encodeURIComponent(ticker);
                link.className = 'font-semibold text-blue-700';
                link.textContent = ticker;
                const details = document.createElement('span');
                details.className = 'text-right tabular-nums text-slate-700';
                details.textContent = shares.toLocaleString('en-GB') + ' shares';
                if (value !== undefined) details.textContent += ' · ' + gbp.format(value) + ' · ' + (100 * value / point.value).toFixed(1) + '%';
                row.append(link, details);
                return row;
            });
            $('paper-holdings').replaceChildren(...rows);
            if (!rows.length) $('paper-holdings').append(Object.assign(document.createElement('li'), { textContent: 'No holdings yet.', className: 'text-slate-600' }));
        }

        async function render() {
            activeRequest?.abort();
            const request = new AbortController();
            activeRequest = request;
            const portfolio = state.portfolios[state.selected];
            select.replaceChildren(...state.portfolios.map(({ name }, index) => new Option(name, index)));
            select.value = String(state.selected);
            select.hidden = state.portfolios.length < 2;
            $('paper-name').textContent = portfolio.name;
            const benchmark = Object.hasOwn(benchmarks, state.benchmark) ? benchmarks[state.benchmark] : benchmarks.sp500;
            comparator.value = benchmark === benchmarks.founder ? 'founder' : 'sp500';
            const holdings = Object.entries(portfolio.positions).map(([ticker, shares]) => ({ ticker, shares }));
            canvas.hidden = true;
            paths = null;
            $('paper-retry').hidden = true;
            $('paper-value').textContent = holdings.length ? '—' : gbp.format(portfolio.cash);
            $('paper-cash').textContent = gbp.format(portfolio.cash);
            $('paper-return').textContent = '—';
            $('paper-excess').textContent = '—';
            const summary = $('paper-chart-summary');
            renderHoldings(holdings);
            if (!holdings.length && !portfolio.cash) {
                summary.textContent = 'Add a holding or cash to compare this portfolio.';
                return;
            }
            summary.textContent = 'Loading historical performance…';
            const sources = comparisonSources(benchmark, holdings);
            const tickers = [benchmark.ticker, ...sources];
            const histories = new Map(await Promise.all(tickers.map(async ticker => [ticker, await readHistory(ticker, request.signal)])));
            if (request.signal.aborted) return;
            const missing = tickers.filter(ticker => !histories.get(ticker));
            const points = missing.length ? null : comparePortfolio(portfolio.cash, holdings, histories, benchmark, sources);
            if (!points) {
                summary.textContent = missing.length ? 'Historical data unavailable for ' + missing.join(', ') + '.' : 'There is too little overlapping history to compare these holdings.';
                $('paper-retry').hidden = false;
                return;
            }
            const first = points[0];
            const last = points.at(-1);
            const portfolioPath = points.map(point => 100 * point.value / first.value);
            const benchmarkPath = points.map(point => 100 * point.benchmark / first.benchmark);
            const gain = portfolioPath.at(-1) - 100;
            const benchmarkGain = benchmarkPath.at(-1) - 100;
            $('paper-value').textContent = gbp.format(last.value);
            $('paper-return').textContent = signed(gain, '%');
            $('paper-excess').textContent = signed(gain - benchmarkGain, ' pp');
            summary.textContent = 'My Portfolio ' + signed(gain, '%') + ' · ' + benchmark.label + ' ' + signed(benchmarkGain, '%') + ' · As of ' + dateLabel.format(new Date(last.date));
            canvas.setAttribute('aria-label', 'Paper portfolio and ' + benchmark.label + ' performance in GBP');
            renderHoldings(holdings, last);
            canvas.hidden = false;
            paths = [portfolioPath, benchmarkPath, points.map(point => point.date)];
            drawChart(canvas, ...paths);
        }

        $('paper-positions').replaceChildren(...[...quotes.keys()].map(ticker => {
            const label = document.createElement('label');
            label.className = 'grid gap-1 text-xs font-semibold';
            label.textContent = ticker;
            const input = document.createElement('input');
            input.type = 'number';
            input.min = '0';
            input.max = '1000000';
            input.step = '0.01';
            input.className = 'min-w-0 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm';
            label.append(input);
            positionInputs.set(ticker, input);
            return label;
        }));

        function showEditor(makeNew) {
            creating = makeNew;
            const portfolio = state.portfolios[state.selected];
            $('paper-title').value = creating ? '' : portfolio.name;
            $('paper-cash-input').value = creating ? 10000 : portfolio.cash;
            for (const [ticker, input] of positionInputs) input.value = creating ? '' : portfolio.positions[ticker] || '';
            $('paper-confirmation').textContent = '';
            form.hidden = false;
            $('paper-title').focus();
        }

        $('paper-create').onclick = () => showEditor(true);
        $('paper-edit').onclick = () => showEditor(false);
        $('paper-cancel').onclick = () => {
            form.hidden = true;
            $(creating ? 'paper-create' : 'paper-edit').focus();
        };
        form.onsubmit = event => {
            event.preventDefault();
            const name = $('paper-title').value.trim();
            if (!name) {
                $('paper-title').focus();
                return;
            }
            const positions = Object.fromEntries([...positionInputs].map(([ticker, input]) => [ticker, Number(input.value)]).filter(([, units]) => units > 0));
            const portfolio = { name, cash: Number($('paper-cash-input').value), positions };
            if (creating) state.selected = state.portfolios.length;
            state.portfolios[state.selected] = portfolio;
            save();
            form.hidden = true;
            render();
            $('paper-confirmation').textContent = 'Saved ' + name + '.';
            $(creating ? 'paper-create' : 'paper-edit').focus();
        };
        select.onchange = () => {
            state.selected = Number(select.value);
            save();
            form.hidden = true;
            $('paper-confirmation').textContent = '';
            render();
        };
        comparator.onchange = () => {
            state.benchmark = comparator.value;
            save();
            render();
        };
        $('paper-retry').onclick = render;
        resizeChart?.disconnect();
        resizeChart = new ResizeObserver(() => {
            if (paths) drawChart(canvas, ...paths);
        });
        resizeChart.observe(canvas);
        render();
    };
})();
