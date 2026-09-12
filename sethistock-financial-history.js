// SethiStock Phase 2E — SEC-backed Annual / Quarterly / TTM financial history.
// Loaded after sethistock.html's legacy renderer so the existing stock endpoint remains
// an immediate fallback while the richer SEC history hydrates independently.

(() => {
    const PERIOD_LABELS = { annual: 'Annual', quarterly: 'Quarterly', ttm: 'TTM' };
    const SEC_METRICS = [
        'revenue', 'net_income', 'gross_margin', 'operating_margin', 'net_margin',
        'operating_cash_flow', 'free_cash_flow', 'capex', 'cash', 'debt', 'shares'
    ];
    const FRONTEND_METRICS = {
        revenue: 'revenue',
        net_income: 'net',
        gross_margin: 'gross_margin',
        operating_margin: 'op_margin',
        net_margin: 'net_margin',
        operating_cash_flow: 'ocf',
        free_cash_flow: 'fcf',
        capex: 'capex',
        cash: 'cash',
        debt: 'debt',
        shares: 'shares'
    };
    const RATIO_KEYS = new Set(['gross_margin', 'op_margin', 'net_margin']);
    const FINANCIAL_CACHE_TTL_MS = 30 * 60 * 1000;
    const FINANCIAL_CACHE_MAX = 30;

    let financialTicker = '';
    let fallbackView = null;
    let displayedView = null;
    let desiredPeriod = 'annual';
    let requestId = 0;
    let requestController = null;
    const financialMemoryCache = new Map();

    function finiteNumber(value) {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    }

    function humanPeriod(period) {
        return PERIOD_LABELS[period] || 'Annual';
    }

    function compactNumber(value) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        return new Intl.NumberFormat('en-GB', {
            notation: 'compact',
            maximumFractionDigits: Math.abs(number) >= 1e9 ? 2 : 1
        }).format(number);
    }

    function metricDisplayValue(key, value) {
        const number = finiteNumber(value);
        if (number === null) return 'N/A';
        if (RATIO_KEYS.has(key)) return `${number.toFixed(1)}%`;
        if (key === 'shares') return `${compactNumber(number)} shares`;
        return `$${compactNumber(number)}`;
    }

    function normaliseLegacyDate(year) {
        const match = String(year ?? '').match(/(19|20)\d{2}/);
        return match ? `${match[0]}-12-31` : String(year ?? '');
    }

    function metricPointsFromAligned(view, key) {
        const values = Array.isArray(view?.[key]) ? view[key] : [];
        const dates = Array.isArray(view?.dates) ? view.dates : [];
        const labels = Array.isArray(view?.labels) ? view.labels : [];
        const points = [];
        for (let index = 0; index < values.length; index++) {
            const value = finiteNumber(values[index]);
            if (value === null) continue;
            points.push({
                value,
                end: dates[index] || null,
                label: labels[index] || dates[index] || ''
            });
        }
        return points;
    }

    function buildLegacyView(fin) {
        const years = Array.isArray(fin?.years) ? fin.years.slice() : [];
        const dates = years.map(normaliseLegacyDate);
        const labels = years.map(year => String(year));
        const view = {
            period: 'annual',
            source: 'Legacy annual data',
            sourceType: 'legacy',
            dates,
            labels,
            years: labels,
            qualityWarnings: 0,
            periodCount: years.length,
            revenue: Array.isArray(fin?.revenue) ? fin.revenue.slice() : [],
            net: Array.isArray(fin?.net) ? fin.net.slice() : [],
            gross_margin: Array.isArray(fin?.gross_margin) ? fin.gross_margin.slice() : [],
            op_margin: Array.isArray(fin?.op_margin) ? fin.op_margin.slice() : [],
            net_margin: Array.isArray(fin?.net_margin) ? fin.net_margin.slice() : [],
            fcf: Array.isArray(fin?.fcf) ? fin.fcf.slice() : [],
            ocf: Array.isArray(fin?.ocf) ? fin.ocf.slice() : [],
            capex: Array.isArray(fin?.capex) ? fin.capex.slice() : [],
            cash: Array.isArray(fin?.cash) ? fin.cash.slice() : [],
            debt: Array.isArray(fin?.debt) ? fin.debt.slice() : [],
            shares: Array.isArray(fin?.shares) ? fin.shares.slice() : [],
            metricPoints: {}
        };
        Object.keys(FRONTEND_METRICS).forEach(secMetric => {
            const key = FRONTEND_METRICS[secMetric];
            view.metricPoints[key] = metricPointsFromAligned(view, key);
        });
        return view;
    }

    function transformSecPayload(payload) {
        if (!payload || payload.period_engine_version !== '2d-v1' || !payload.metrics) {
            throw new Error('Historical fundamentals payload is unavailable.');
        }

        const dateSet = new Set();
        const labelByDate = new Map();
        const metricPoints = {};
        let qualityWarnings = 0;

        for (const [secMetric, frontendKey] of Object.entries(FRONTEND_METRICS)) {
            const metric = payload.metrics?.[secMetric] || {};
            const rawSeries = Array.isArray(metric.series) ? metric.series : [];
            const points = [];

            rawSeries.forEach(point => {
                const end = point?.end;
                let value = finiteNumber(point?.value);
                if (!end || value === null) return;
                if (RATIO_KEYS.has(frontendKey)) value *= 100;
                const label = point.label || end;
                points.push({ ...point, value, end, label });
                dateSet.add(end);
                if (!labelByDate.has(end) || secMetric === 'revenue') labelByDate.set(end, label);
            });
            points.sort((a, b) => String(a.end).localeCompare(String(b.end)));
            metricPoints[frontendKey] = points;

            const reconciliation = metric?.quality?.reconciliation_points || {};
            qualityWarnings += Number(reconciliation.basis_mismatch || 0);
        }

        const dates = Array.from(dateSet).sort();
        const labels = dates.map(date => labelByDate.get(date) || date);
        const view = {
            period: payload.period,
            source: payload.source || 'SEC EDGAR Company Facts',
            sourceType: 'sec',
            dates,
            labels,
            years: labels,
            fiscalCalendar: payload.fiscal_calendar || {},
            storage: payload.storage || null,
            metricPoints,
            qualityWarnings,
            periodCount: metricPoints.revenue?.length || 0
        };

        for (const key of Object.values(FRONTEND_METRICS)) {
            const byEnd = new Map((metricPoints[key] || []).map(point => [point.end, point.value]));
            view[key] = dates.map(date => byEnd.has(date) ? byEnd.get(date) : null);
        }
        return view;
    }

    function rememberFinancialView(key, view) {
        financialMemoryCache.delete(key);
        financialMemoryCache.set(key, { view, savedAt: Date.now() });
        while (financialMemoryCache.size > FINANCIAL_CACHE_MAX) {
            financialMemoryCache.delete(financialMemoryCache.keys().next().value);
        }
    }

    function setStatus(message, tone = 'neutral') {
        const element = document.getElementById('financial-history-status');
        if (!element) return;
        element.textContent = message;
        const toneClass = tone === 'error'
            ? 'text-red-600'
            : tone === 'success'
                ? 'text-emerald-700'
                : tone === 'loading'
                    ? 'text-blue-600'
                    : 'text-gray-400';
        element.className = `text-[11px] font-bold uppercase tracking-widest mt-2 text-right ${toneClass}`;
    }

    function setQualityAlert(view) {
        const alert = document.getElementById('financial-history-alert');
        if (!alert) return;
        if (view?.qualityWarnings > 0) {
            alert.textContent = 'Some reported quarters use a different accounting basis from later-restated annual figures. SethiStock preserves the reported periods and excludes incompatible windows from TTM calculations.';
            alert.classList.remove('hidden');
        } else {
            alert.classList.add('hidden');
            alert.textContent = '';
        }
    }

    function syncPeriodControls(period) {
        document.querySelectorAll('.financial-period-btn').forEach(button => {
            button.classList.toggle('active', button.dataset.financialPeriod === period);
        });
        const comparisonLabel = document.getElementById('comparison-period-label');
        if (comparisonLabel) comparisonLabel.textContent = humanPeriod(period);
    }

    function historyDescriptor(view) {
        if (!view) return 'Historical fundamentals unavailable';
        if (view.sourceType !== 'sec') return 'Legacy annual fallback';
        const points = view.metricPoints?.revenue || [];
        if (!points.length) return `SEC EDGAR · ${humanPeriod(view.period)}`;
        const first = points[0]?.label || points[0]?.end;
        const last = points[points.length - 1]?.label || points[points.length - 1]?.end;
        return `SEC EDGAR · ${first}–${last} · ${points.length} ${humanPeriod(view.period).toLowerCase()} periods`;
    }

    function validMetricPoints(view, key) {
        const stored = view?.metricPoints?.[key];
        if (Array.isArray(stored) && stored.length) {
            return stored.filter(point => finiteNumber(point.value) !== null);
        }
        return metricPointsFromAligned(view, key);
    }

    function cagrBetween(past, latest) {
        const pastValue = finiteNumber(past?.value);
        const latestValue = finiteNumber(latest?.value);
        if (pastValue === null || latestValue === null || pastValue <= 0 || latestValue <= 0) return 'N/A';
        const pastDate = new Date(past.end);
        const latestDate = new Date(latest.end);
        const elapsedYears = (latestDate - pastDate) / (365.25 * 24 * 60 * 60 * 1000);
        if (!Number.isFinite(elapsedYears) || elapsedYears <= 0.45) return 'N/A';
        const cagr = (Math.pow(latestValue / pastValue, 1 / elapsedYears) - 1) * 100;
        if (!Number.isFinite(cagr)) return 'N/A';
        return `${cagr > 0 ? '+' : ''}${cagr.toFixed(2)}%`;
    }

    function nearestHistoricalPoint(points, latest, yearsBack) {
        const target = new Date(latest.end);
        if (Number.isNaN(target.getTime())) return null;
        target.setUTCFullYear(target.getUTCFullYear() - yearsBack);
        let best = null;
        let bestDistance = Infinity;
        points.forEach(point => {
            if (point === latest) return;
            const date = new Date(point.end);
            if (Number.isNaN(date.getTime()) || date >= new Date(latest.end)) return;
            const distance = Math.abs(date - target);
            if (distance < bestDistance) {
                best = point;
                bestDistance = distance;
            }
        });
        // A quarterly period can move by several weeks across fiscal calendars; beyond
        // roughly half a year we no longer call it a comparable N-year observation.
        return bestDistance <= 190 * 24 * 60 * 60 * 1000 ? best : null;
    }

    function getGrowthStats(view, key) {
        const points = validMetricPoints(view, key);
        if (points.length < 2) return { '1Y': '-', '2Y': '-', '3Y': '-', 'MAX': '-' };
        const latest = points[points.length - 1];
        const result = {};
        [1, 2, 3].forEach(years => {
            const past = nearestHistoricalPoint(points, latest, years);
            result[`${years}Y`] = past ? cagrBetween(past, latest) : '-';
        });
        result.MAX = cagrBetween(points[0], latest);
        return result;
    }

    function growthColour(value) {
        if (!value || value === 'N/A' || value === '-') return 'text-gray-400';
        return value.startsWith('-') ? 'text-red-500' : 'text-green-500';
    }

    function renderFinancialCards(view) {
        const cards = [
            { id: 'ind-rev', key: 'revenue', title: 'Revenue' },
            { id: 'ind-net', key: 'net', title: 'Net Income' },
            { id: 'ind-margins', key: 'net_margin', title: 'Margin Profile' },
            { id: 'ind-ocf', key: 'ocf', title: 'Operating Cash Flow' },
            { id: 'ind-fcf', key: 'fcf', title: 'Free Cash Flow' },
            { id: 'ind-capex', key: 'capex', title: 'Capital Expenditure' },
            { id: 'ind-cash', key: 'cash', title: 'Cash Equivalents' },
            { id: 'ind-debt', key: 'debt', title: 'Total Debt' },
            { id: 'ind-shares', key: 'shares', title: 'Shares Outstanding' }
        ];
        const container = document.getElementById('individual-charts-container');
        if (!container) return;
        const periodLabel = humanPeriod(view?.period || 'annual');

        // Build the shell once. Keeping the Plotly target nodes stable means period
        // switches can genuinely use Plotly.react instead of recreating nine charts.
        if (container.dataset?.phase2eReady !== '1') {
            let html = '';
            cards.forEach(card => {
                html += `
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col min-h-[350px]">
                        <div class="flex items-center justify-between gap-3 mb-2">
                            <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">${card.title}</h4>
                            <span id="fin-period-${card.id}" class="px-2 py-1 rounded-md bg-gray-50 border border-gray-100 text-[9px] font-black text-gray-400 uppercase tracking-widest">${periodLabel}</span>
                        </div>
                        <div id="${card.id}" class="h-56 w-full mt-auto mb-2"></div>
                        <div class="grid grid-cols-4 gap-2 mt-4 pt-4 border-t border-gray-100">
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">1Y CAGR</p><p id="fin-growth-${card.id}-1Y" class="font-semibold text-xs text-gray-400">-</p></div>
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">2Y CAGR</p><p id="fin-growth-${card.id}-2Y" class="font-semibold text-xs text-gray-400">-</p></div>
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">3Y CAGR</p><p id="fin-growth-${card.id}-3Y" class="font-semibold text-xs text-gray-400">-</p></div>
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">MAX</p><p id="fin-growth-${card.id}-MAX" class="font-semibold text-xs text-gray-400">-</p></div>
                        </div>
                    </div>`;
            });
            container.innerHTML = html;
            if (container.dataset) container.dataset.phase2eReady = '1';
        }

        cards.forEach(card => {
            const growth = getGrowthStats(view, card.key);
            const badge = document.getElementById(`fin-period-${card.id}`);
            if (badge) {
                badge.textContent = view?.period === 'ttm' && ['cash', 'debt', 'shares'].includes(card.key)
                    ? 'Point-in-time'
                    : periodLabel;
            }
            ['1Y', '2Y', '3Y', 'MAX'].forEach(horizon => {
                const value = growth[horizon];
                const element = document.getElementById(`fin-growth-${card.id}-${horizon}`);
                if (!element) return;
                element.textContent = value;
                element.className = `font-semibold text-xs ${growthColour(value)}`;
            });
        });
    }

    function emptyChart(id, message = 'Data Unavailable') {
        const element = document.getElementById(id);
        if (element) element.innerHTML = `<div class="flex h-full items-center justify-center text-gray-400 font-bold text-sm text-center px-5">${message}</div>`;
    }

    function chartLayout(view, showLegend = false) {
        return {
            margin: { t: 12, b: showLegend ? 45 : 34, l: 48, r: 10 },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            showlegend: showLegend,
            autosize: true,
            hovermode: 'x unified',
            xaxis: {
                type: 'date',
                showgrid: false,
                nticks: view.period === 'annual' ? 10 : 8,
                tickformat: view.period === 'annual' ? '%Y' : '%b %Y',
                tickfont: { color: '#64748b', size: 10 },
                automargin: true
            },
            yaxis: {
                showgrid: true,
                gridcolor: '#f1f5f9',
                zerolinecolor: '#e2e8f0',
                tickformat: '~s',
                tickfont: { color: '#64748b', size: 10 },
                automargin: true
            },
            legend: showLegend ? { orientation: 'h', xanchor: 'center', x: 0.5, y: -0.18, font: { size: 10 } } : undefined
        };
    }

    function traceForMetric(view, key, name, colour, options = {}) {
        const points = validMetricPoints(view, key);
        if (!points.length) return null;
        const annualBars = view.period === 'annual' && options.forceLine !== true;
        const trace = {
            x: points.map(point => point.end),
            y: points.map(point => point.value),
            name,
            customdata: points.map(point => point.label),
            text: points.map(point => metricDisplayValue(key, point.value)),
            hovertemplate: '%{customdata}<br>%{text}<extra></extra>'
        };
        if (annualBars) {
            trace.type = 'bar';
            trace.marker = { color: colour, line: { width: 0 } };
        } else {
            trace.type = 'scatter';
            trace.mode = view.period === 'quarterly' ? 'lines+markers' : 'lines';
            trace.line = { color: colour, width: 2.4 };
            trace.marker = { color: colour, size: 5 };
            trace.connectgaps = false;
        }
        return trace;
    }

    function drawSingleMetric(view, id, key, colour, options = {}) {
        const trace = traceForMetric(view, key, options.name || key, colour, options);
        if (!trace) return emptyChart(id);
        const layout = chartLayout(view, false);
        if (RATIO_KEYS.has(key)) layout.yaxis.tickformat = '.1f';
        Plotly.react(id, [trace], layout, { displayModeBar: false, responsive: true });
    }

    function drawMargins(view) {
        const specs = [
            ['gross_margin', 'Gross (%)', '#8b5cf6'],
            ['op_margin', 'Operating (%)', '#22c55e'],
            ['net_margin', 'Net (%)', '#3b82f6']
        ];
        const traces = specs
            .map(([key, name, colour]) => traceForMetric(view, key, name, colour, { forceLine: true }))
            .filter(Boolean);
        if (!traces.length) return emptyChart('ind-margins');
        const layout = chartLayout(view, true);
        layout.yaxis.tickformat = '.1f';
        layout.yaxis.ticksuffix = '%';
        Plotly.react('ind-margins', traces, layout, { displayModeBar: false, responsive: true });
    }

    function drawComparison(view, id, first, second) {
        const nonAnnual = view.period !== 'annual';
        const trace1 = traceForMetric(view, first.key, first.name, first.colour, { forceLine: nonAnnual });
        const trace2 = traceForMetric(view, second.key, second.name, second.colour, { forceLine: nonAnnual });
        const traces = [trace1, trace2].filter(Boolean);
        if (traces.length < 2) return emptyChart(id);
        const layout = chartLayout(view, true);
        if (view.period === 'annual') layout.barmode = 'group';
        Plotly.react(id, traces, layout, { displayModeBar: false, responsive: true });
    }

    function renderFinancialCharts(view) {
        if (!view) return;
        drawSingleMetric(view, 'ind-rev', 'revenue', '#3b82f6', { name: 'Revenue' });
        drawSingleMetric(view, 'ind-net', 'net', '#a855f7', { name: 'Net Income' });
        drawSingleMetric(view, 'ind-ocf', 'ocf', '#10b981', { name: 'Operating Cash Flow' });
        drawSingleMetric(view, 'ind-fcf', 'fcf', '#059669', { name: 'Free Cash Flow' });
        drawSingleMetric(view, 'ind-capex', 'capex', '#ef4444', { name: 'Capital Expenditure' });
        drawSingleMetric(view, 'ind-cash', 'cash', '#0ea5e9', { name: 'Cash' });
        drawSingleMetric(view, 'ind-debt', 'debt', '#f97316', { name: 'Debt' });
        drawSingleMetric(view, 'ind-shares', 'shares', '#64748b', { name: 'Shares' });
        drawMargins(view);

        drawComparison(view, 'comp-rev-net',
            { key: 'revenue', name: 'Revenue', colour: '#94a3b8' },
            { key: 'net', name: 'Net Income', colour: '#3b82f6' });
        drawComparison(view, 'comp-cash-debt',
            { key: 'cash', name: 'Cash', colour: '#0ea5e9' },
            { key: 'debt', name: 'Debt', colour: '#f97316' });
        drawComparison(view, 'comp-fcf-ocf',
            { key: 'ocf', name: 'Operating CF', colour: '#10b981' },
            { key: 'fcf', name: 'Free Cash Flow', colour: '#059669' });
        drawComparison(view, 'comp-ocf-capex',
            { key: 'ocf', name: 'Operating CF', colour: '#10b981' },
            { key: 'capex', name: 'CapEx', colour: '#ef4444' });
    }

    function renderView(view, statusTone = 'success', statusOverride = null) {
        displayedView = view;
        desiredPeriod = view.period || 'annual';
        state.financialPeriod = desiredPeriod;
        syncPeriodControls(desiredPeriod);
        renderFinancialCards(view);
        renderFinancialCharts(view);
        setQualityAlert(view);
        setStatus(statusOverride || historyDescriptor(view), statusTone);
    }

    async function loadFinancialHistory(period = desiredPeriod) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!ticker) return null;
        desiredPeriod = period;
        state.financialPeriod = period;
        syncPeriodControls(period);

        const key = `${ticker}|${period}`;
        const cached = financialMemoryCache.get(key);
        if (cached && Date.now() - cached.savedAt < FINANCIAL_CACHE_TTL_MS) {
            if (ticker === String(state.ticker || '').trim().toUpperCase() && desiredPeriod === period) {
                renderView(cached.view);
            }
            return cached.view;
        }

        const thisRequest = ++requestId;
        if (requestController) requestController.abort();
        requestController = new AbortController();
        setStatus(`Loading ${humanPeriod(period)} SEC history…`, 'loading');

        try {
            const query = new URLSearchParams({
                period,
                metrics: SEC_METRICS.join(','),
                limit: '200'
            });
            const payload = await fetchJsonWithRetry(
                `${API_URL}/api/sec/${encodeURIComponent(ticker)}/fundamentals/series?${query.toString()}`,
                { signal: requestController.signal },
                1
            );
            if (thisRequest !== requestId) return null;
            const view = transformSecPayload(payload);
            if (!view.metricPoints.revenue?.length) throw new Error('Revenue history unavailable.');
            rememberFinancialView(key, view);
            if (ticker === String(state.ticker || '').trim().toUpperCase() && desiredPeriod === period) {
                renderView(view);
            }
            return view;
        } catch (error) {
            if (error?.name === 'AbortError') return null;
            console.warn(`Phase 2E ${period} fundamentals failed for ${ticker}:`, error);
            if (period === 'annual' && fallbackView && financialTicker === ticker) {
                renderView(fallbackView, 'error', 'SEC history unavailable · showing legacy annual data');
            } else {
                const keepPeriod = displayedView?.period || 'annual';
                desiredPeriod = keepPeriod;
                state.financialPeriod = keepPeriod;
                syncPeriodControls(keepPeriod);
                setStatus(`${humanPeriod(period)} SEC history unavailable · keeping ${humanPeriod(keepPeriod)}`, 'error');
            }
            return null;
        } finally {
            if (thisRequest === requestId) requestController = null;
        }
    }

    function resetForTicker(ticker, fin) {
        if (requestController) requestController.abort();
        requestController = null;
        requestId += 1;
        financialTicker = ticker;
        fallbackView = buildLegacyView(fin);
        displayedView = fallbackView;
        desiredPeriod = 'annual';
        state.financialPeriod = 'annual';
        syncPeriodControls('annual');
        setQualityAlert(fallbackView);
        setStatus('Loading long-run SEC history…', 'loading');
    }

    // Override only the two legacy chart-rendering functions. The main stock request,
    // DCF, peers, research labs and Phase 1 price/quote loading remain untouched.
    injectFinancialHTML = function(fin) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);
        else fallbackView = buildLegacyView(fin);
        renderFinancialCards(fallbackView);
    };

    drawFinancials = function(fin) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);
        else fallbackView = buildLegacyView(fin);

        // Keep the existing short history visible instantly, then hydrate the SEC view.
        renderFinancialCharts(fallbackView);
        displayedView = fallbackView;
        setStatus('Loading long-run SEC history…', 'loading');
        loadFinancialHistory('annual').catch(() => null);
    };

    document.querySelectorAll('.financial-period-btn').forEach(button => {
        button.addEventListener('click', () => {
            const period = button.dataset.financialPeriod;
            if (!period || period === desiredPeriod && displayedView?.period === period) return;
            loadFinancialHistory(period).catch(() => null);
        });
    });

    // Expose a tiny debugging surface for production smoke tests without coupling the
    // rest of SethiStock to the implementation details of this module.
    window.SethiStockFinancialHistory = {
        get period() { return desiredPeriod; },
        get source() { return displayedView?.sourceType || null; },
        get periodCount() { return displayedView?.periodCount || 0; },
        load: loadFinancialHistory
    };
})();
