(() => {
    'use strict';

    const $ = id => document.getElementById(id);
    const quotes = new Map([
        ['MSFT', { name: 'Microsoft', price: 428.60, currency: 'USD', change: 0.86, pe: 31.2, path: [100, 101, 106, 104, 110, 113, 115] }],
        ['AAPL', { name: 'Apple', price: 241.73, currency: 'USD', change: -0.42, pe: 28.6, path: [100, 104, 101, 106, 108, 106, 111] }],
        ['NVDA', { name: 'NVIDIA', price: 152.39, currency: 'USD', change: 1.71, pe: 34.8, path: [100, 111, 107, 118, 115, 123, 129] }],
        ['VWRP.L', { name: 'Vanguard FTSE All-World', price: 119.84, currency: 'GBP', change: 0.24, pe: null, path: [100, 102, 105, 102, 108, 109, 111] }],
        ['GOOGL', { name: 'Alphabet', price: 189.32, currency: 'USD', change: 0.63, pe: 21.4, path: [100, 103, 105, 110, 107, 113, 117] }],
        ['JPM', { name: 'JPMorgan Chase', price: 270.18, currency: 'USD', change: -0.18, pe: 14.1, path: [100, 104, 108, 106, 111, 115, 114] }],
        ['AZN.L', { name: 'AstraZeneca', price: 118.42, currency: 'GBP', change: -0.31, pe: 17.1, path: [100, 99, 101, 105, 103, 107, 108] }]
    ]);
    const benchmarks = {
        sp500: { label: 'S&P 500', path: [100, 103, 105, 103, 106, 110, 112] },
        global: { label: 'MSCI World', path: [100, 102, 104, 102, 106, 108, 110] },
        founder: { label: 'SethiPortfolio sample', path: [100, 104, 107, 104, 109, 113, 116] }
    };
    const gbp = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 });
    const signed = (value, unit) => (value > 0 ? '+' : '') + value.toFixed(1) + unit;
    const mark = quote => quote.price * (quote.currency === 'USD' ? 0.76 : 1);
    let resizeChart;

    window.SethiWayPreviewQuotes = quotes;

    function drawChart(canvas, portfolioPath, benchmarkPath) {
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
        ctx.fillText('Start', x(0), height - 2);
        ctx.fillText('Month 6', width - 52, height - 2);
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

        function render() {
            const portfolio = state.portfolios[state.selected];
            select.replaceChildren(...state.portfolios.map(({ name }, index) => new Option(name, index)));
            select.value = String(state.selected);
            select.hidden = state.portfolios.length < 2;
            $('paper-name').textContent = portfolio.name;
            comparator.value = state.benchmark;
            const benchmark = benchmarks[state.benchmark];
            const holdings = Object.entries(portfolio.positions).map(([ticker, shares]) => ({
                ticker, shares, quote: quotes.get(ticker), value: shares * mark(quotes.get(ticker))
            }));
            const values = benchmark.path.map((_, i) => portfolio.cash + holdings.reduce((sum, holding) => (
                sum + holding.value * holding.quote.path[i] / holding.quote.path.at(-1)
            ), 0));
            const path = values[0] ? values.map(value => value / values[0] * 100) : null;
            const gain = path ? path.at(-1) - 100 : 0;
            const benchmarkGain = benchmark.path.at(-1) - 100;
            $('paper-value').textContent = gbp.format(values.at(-1));
            $('paper-cash').textContent = gbp.format(portfolio.cash);
            $('paper-return').textContent = values[0] ? signed(gain, '%') : '—';
            $('paper-excess').textContent = values[0] ? signed(gain - benchmarkGain, ' pp') : '—';
            $('paper-chart-summary').textContent = values[0]
                ? 'Blue · My Portfolio ' + signed(gain, '%') + '   |   Dashed · ' + benchmark.label + ' ' + signed(benchmarkGain, '%')
                : 'Add a holding or cash to compare this portfolio.';
            const rows = holdings.sort((a, b) => b.value - a.value).map(({ ticker, shares, value }) => {
                const row = document.createElement('li');
                row.className = 'flex items-center justify-between gap-3 py-2';
                const link = document.createElement('a');
                link.href = 'sethistock.html?ticker=' + encodeURIComponent(ticker);
                link.className = 'font-semibold text-blue-700';
                link.textContent = ticker;
                const details = document.createElement('span');
                details.className = 'text-right tabular-nums text-slate-700';
                details.textContent = shares.toLocaleString('en-GB') + ' shares · ' + gbp.format(value) + ' · ' + (100 * value / values.at(-1)).toFixed(1) + '%';
                row.append(link, details);
                return row;
            });
            $('paper-holdings').replaceChildren(...rows);
            if (!rows.length) $('paper-holdings').append(Object.assign(document.createElement('li'), { textContent: 'No holdings yet.', className: 'text-slate-600' }));
            canvas.hidden = !path;
            paths = path ? [path, benchmark.path] : null;
            if (paths) drawChart(canvas, ...paths);
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
        resizeChart?.disconnect();
        resizeChart = new ResizeObserver(() => {
            if (paths) drawChart(canvas, ...paths);
        });
        resizeChart.observe(canvas);
        render();
    };
})();
