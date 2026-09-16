// SethiStock Phase 2E — SEC-backed Annual / Quarterly / TTM financial history.
// Loaded after sethistock.html's legacy renderer so the existing stock endpoint remains
// an immediate fallback while the richer SEC history hydrates independently.

(() => {
    const PERIOD_LABELS = { annual: 'Annual', quarterly: 'Quarterly', ttm: 'TTM' };
    const SEC_METRICS = [
        'revenue', 'net_income', 'ebitda', 'gross_margin', 'operating_margin', 'net_margin',
        'operating_cash_flow', 'free_cash_flow', 'capex', 'cash', 'debt', 'shares'
    ];
    const BASE_SEC_METRICS = SEC_METRICS.filter(metric => metric !== 'ebitda');
    const FRONTEND_METRICS = {
        revenue: 'revenue',
        net_income: 'net',
        ebitda: 'ebitda',
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
    let desiredWindow = 'max';
    let expandedChartId = null;
    let prefetchGeneration = 0;
    let requestId = 0;
    let requestController = null;
    const financialMemoryCache = new Map();
    let researchData = null;
    let researchTicker = '';
    const fastResearchCache = new Map();
    const fastEbitdaPromises = new Map();
    const fastEbitdaCache = new Map();

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

    function canonicalSupplementaryTicker(ticker) {
        const symbol = String(ticker || '').trim().toUpperCase();
        return symbol === 'GOOG' ? 'GOOGL' : symbol;
    }

    function looksLikeTicker(ticker) {
        return /^[A-Z][A-Z0-9.-]{0,9}$/.test(String(ticker || '').trim().toUpperCase());
    }

    function researchPayloadSettled(payload) {
        const earnings = payload?.earnings_reaction;
        const valuation = payload?.valuation_bands;
        const studyHasData = (study, dataKey) => {
            if (!study || typeof study !== 'object' || study.available !== true) return false;
            return Array.isArray(study[dataKey]) && study[dataKey].length > 0;
        };
        return studyHasData(earnings, 'events') && studyHasData(valuation, 'observations');
    }

    function annualCategoryLabel(point, index = 0) {
        const label = String(point?.label || '').trim();
        const labelledYear = label.match(/(?:FY\s*)?((?:19|20)\d{2})/i);
        if (labelledYear) return labelledYear[1];
        const end = String(point?.end || '');
        const datedYear = end.match(/^((?:19|20)\d{2})/);
        return datedYear ? datedYear[1] : (label || String(index + 1));
    }

    function collapseAnnualPlotPoints(points) {
        const byYear = new Map();
        (points || []).forEach((point, index) => {
            const category = annualCategoryLabel(point, index);
            const previous = byYear.get(category);
            // SEC can expose more than one annual context for the same fiscal year.
            // Keep the latest filing-period end so Plotly receives exactly one bar per year.
            if (!previous || String(point?.end || '') >= String(previous?.end || '')) {
                byYear.set(category, { ...point, annualCategory: category });
            }
        });
        return Array.from(byYear.values()).sort((a, b) => {
            const ay = Number(a.annualCategory);
            const by = Number(b.annualCategory);
            if (Number.isFinite(ay) && Number.isFinite(by)) return ay - by;
            return String(a.annualCategory).localeCompare(String(b.annualCategory));
        });
    }

    function extractFastEbitdaPoints(payload) {
        const series = Array.isArray(payload?.metrics?.ebitda?.series) ? payload.metrics.ebitda.series : [];
        return series
            .map(point => ({
                ...point,
                value: finiteNumber(point?.value),
                end: point?.end || null,
                label: point?.label || point?.end || ''
            }))
            .filter(point => point.end && point.value !== null)
            .sort((a, b) => String(a.end).localeCompare(String(b.end)))
            .slice(-5);
    }

    function applyFastEbitdaFallback(ticker, view) {
        const symbol = canonicalSupplementaryTicker(ticker);
        const points = fastEbitdaCache.get(symbol);
        if (!view || view.sourceType !== 'legacy' || !Array.isArray(points) || !points.length) return false;
        if (!view.metricPoints) view.metricPoints = {};
        view.metricPoints.ebitda = points.map(point => ({ ...point }));
        return true;
    }

    function requestFastEbitda(ticker) {
        const symbol = canonicalSupplementaryTicker(ticker);
        if (!looksLikeTicker(symbol)) return Promise.resolve([]);
        if (fastEbitdaCache.has(symbol)) return Promise.resolve(fastEbitdaCache.get(symbol));
        if (fastEbitdaPromises.has(symbol)) return fastEbitdaPromises.get(symbol);

        const query = new URLSearchParams({ period: 'annual', metrics: 'ebitda', limit: '5' });
        const promise = fetchJsonWithRetry(
            `${API_URL}/api/sec/${encodeURIComponent(symbol)}/fundamentals/series?${query.toString()}`,
            {},
            1
        ).then(payload => {
            const points = extractFastEbitdaPoints(payload);
            if (points.length) fastEbitdaCache.set(symbol, points);

            if (points.length && canonicalSupplementaryTicker(financialTicker) === symbol && fallbackView?.sourceType === 'legacy') {
                applyFastEbitdaFallback(symbol, fallbackView);
                if (displayedView?.sourceType === 'legacy') {
                    renderFinancialCards(fallbackView);
                    drawSingleMetric(fallbackView, 'ind-ebitda', 'ebitda', '#0f766e', { name: 'EBITDA' });
                    if (expandedChartId === 'ind-ebitda') requestAnimationFrame(() => renderExpandedPlot('ind-ebitda'));
                }
            }
            return points;
        }).catch(error => {
            console.debug(`Fast EBITDA fallback unavailable for ${symbol}:`, error);
            return [];
        }).finally(() => {
            if (!fastEbitdaCache.has(symbol)) fastEbitdaPromises.delete(symbol);
        });

        fastEbitdaPromises.set(symbol, promise);
        return promise;
    }

    function primeSupplementaryFinancialData(ticker) {
        const symbol = canonicalSupplementaryTicker(ticker);
        if (!looksLikeTicker(symbol)) return;

        if (typeof window.getSethiStockResearch === 'function') {
            window.getSethiStockResearch(symbol)
                .then(data => {
                    if (!data) return null;
                    fastResearchCache.set(symbol, data);

                    // If the legacy financial cards already exist, hydrate the two research
                    // cards immediately instead of waiting for the long-run SEC request.
                    if (canonicalSupplementaryTicker(financialTicker) === symbol) {
                        researchData = data;
                        researchTicker = symbol;
                        if (displayedView?.sourceType === 'legacy') {
                            renderFinancialCards(displayedView);
                            drawHistoricalPE();
                            drawEarningsSurprise();
                            if (expandedChartId === 'ind-earnings') renderEarningsDetail();
                            if (expandedChartId === 'ind-pe' || expandedChartId === 'ind-earnings') {
                                requestAnimationFrame(() => renderExpandedPlot(expandedChartId));
                            }
                        }
                    }
                    return data;
                })
                .catch(error => {
                    console.debug(`Early research prefetch unavailable for ${symbol}:`, error);
                    return null;
                });
        }

        requestFastEbitda(symbol).catch(() => null);
    }

    function primeInitialData(ticker, payload) {
        const symbol = canonicalSupplementaryTicker(ticker);
        if (!looksLikeTicker(symbol) || !payload || typeof payload !== 'object') return;
        const research = payload.research && typeof payload.research === 'object' ? payload.research : payload;
        if (!research || typeof research !== 'object') return;

        // A cached /api/stock row can predate a successful research calculation and
        // therefore contain the bare {available:false} placeholders. Do not promote
        // those placeholders into the fast research cache as if they were final data.
        const settled = researchPayloadSettled(research);
        if (settled) fastResearchCache.set(symbol, research);
        else fastResearchCache.delete(symbol);

        if (canonicalSupplementaryTicker(financialTicker) === symbol || !financialTicker) {
            researchData = settled ? research : null;
            researchTicker = settled ? symbol : '';
        }
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
            ebitda: Array.isArray(fin?.ebitda) ? fin.ebitda.slice() : [],
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
        if (points.length < 2) return { '1Y': '-', '3Y': '-', '5Y': '-', 'MAX': '-' };
        const latest = points[points.length - 1];
        const result = {};
        [1, 3, 5].forEach(years => {
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


    function deltaBetween(past, latest) {
        const pastValue = finiteNumber(past?.value);
        const latestValue = finiteNumber(latest?.value);
        if (pastValue === null || latestValue === null) return '-';
        const delta = latestValue - pastValue;
        return `${delta > 0 ? '+' : ''}${delta.toFixed(2)}pp`;
    }

    function getMarginDeltaStats(view) {
        const points = validMetricPoints(view, 'net_margin');
        if (points.length < 2) return { '1Y': '-', '3Y': '-', '5Y': '-', 'MAX': '-' };
        const latest = points[points.length - 1];
        const result = {};
        [1, 3, 5].forEach(years => {
            const past = nearestHistoricalPoint(points, latest, years);
            result[`${years}Y`] = past ? deltaBetween(past, latest) : '-';
        });
        result.MAX = deltaBetween(points[0], latest);
        return result;
    }

    function researchPct(value, digits = 1) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number.toFixed(digits)}%`;
    }

    function researchMult(value, digits = 1) {
        const number = finiteNumber(value);
        return number === null ? 'N/A' : `${number.toFixed(digits)}x`;
    }

    function filterDatedItems(items, dateKey, windowValue = desiredWindow) {
        if (!Array.isArray(items) || !items.length || windowValue === 'max') return items || [];
        const years = Number(windowValue);
        if (!Number.isFinite(years) || years <= 0) return items;
        const valid = items.filter(item => !Number.isNaN(new Date(item?.[dateKey]).getTime()));
        if (!valid.length) return items;
        const latest = new Date(valid[valid.length - 1][dateKey]);
        const cutoff = new Date(latest);
        cutoff.setUTCFullYear(cutoff.getUTCFullYear() - years);
        return valid.filter(item => new Date(item[dateKey]) >= cutoff);
    }

    function statsForCard(card, view) {
        if (card.mode === 'margin') {
            const values = getMarginDeltaStats(view);
            return {
                labels: ['1Y Δ', '3Y Δ', '5Y Δ', 'MAX Δ'],
                values: ['1Y', '3Y', '5Y', 'MAX'].map(key => values[key]),
                classes: ['1Y', '3Y', '5Y', 'MAX'].map(key => growthColour(values[key]))
            };
        }
        if (card.mode === 'valuation') {
            const study = researchData?.valuation_bands;
            const bands = study?.bands || {};
            return {
                labels: ['Current', 'Median', 'Percentile', 'P25–P75'],
                values: [
                    researchMult(study?.current_pe),
                    researchMult(bands.median),
                    study?.current_percentile == null ? 'N/A' : researchPct(study.current_percentile, 0),
                    bands.p25 == null || bands.p75 == null ? 'N/A' : `${Number(bands.p25).toFixed(1)}–${Number(bands.p75).toFixed(1)}x`
                ],
                classes: ['text-blue-600', 'text-slate-700', 'text-blue-600', 'text-slate-500']
            };
        }
        if (card.mode === 'earnings') {
            const summary = researchData?.earnings_reaction?.summary || {};
            const avg5 = finiteNumber(summary.average_5d_move_pct);
            return {
                labels: ['Beat Rate', 'Avg |1D|', 'Avg 5D', 'Quarters'],
                values: [
                    researchPct(summary.eps_beat_rate_pct, 0),
                    researchPct(summary.average_abs_1d_move_pct),
                    researchPct(avg5),
                    summary.quarters == null ? 'N/A' : String(summary.quarters)
                ],
                classes: [
                    finiteNumber(summary.eps_beat_rate_pct) !== null && Number(summary.eps_beat_rate_pct) >= 50 ? 'text-green-600' : 'text-slate-700',
                    'text-slate-700',
                    avg5 === null ? 'text-gray-400' : (avg5 < 0 ? 'text-red-500' : 'text-green-600'),
                    'text-slate-500'
                ]
            };
        }
        const growth = getGrowthStats(view, card.key);
        return {
            labels: ['1Y CAGR', '3Y CAGR', '5Y CAGR', 'MAX'],
            values: ['1Y', '3Y', '5Y', 'MAX'].map(key => growth[key]),
            classes: ['1Y', '3Y', '5Y', 'MAX'].map(key => growthColour(growth[key]))
        };
    }

    function renderEarningsDetail() {
        const detail = document.getElementById('financial-detail-ind-earnings');
        if (!detail) return;
        const study = researchData?.earnings_reaction;
        if (!study?.available || !study.events?.length) {
            detail.innerHTML = '<div class="py-6 text-center text-sm font-semibold text-gray-400">Detailed earnings history is unavailable for this security.</div>';
            return;
        }
        const rows = study.events.map(event => {
            const surprise = finiteNumber(event.surprise_pct);
            const move1 = finiteNumber(event.move_1d_pct);
            const move5 = finiteNumber(event.move_5d_pct);
            const colour = value => value === null ? 'text-gray-400' : (value < 0 ? 'text-red-600' : 'text-green-600');
            return `<tr class="border-t border-gray-100">
                <td class="py-2.5 pr-3 font-bold text-gray-700 whitespace-nowrap">${event.earnings_date || '—'}</td>
                <td class="py-2.5 px-3 text-gray-600">${event.eps_estimate == null ? 'N/A' : Number(event.eps_estimate).toFixed(2)}</td>
                <td class="py-2.5 px-3 text-gray-600">${event.reported_eps == null ? 'N/A' : Number(event.reported_eps).toFixed(2)}</td>
                <td class="py-2.5 px-3 font-black ${colour(surprise)}">${surprise === null ? 'N/A' : researchPct(surprise)}</td>
                <td class="py-2.5 px-3 font-black ${colour(move1)}">${move1 === null ? 'N/A' : researchPct(move1)}</td>
                <td class="py-2.5 pl-3 font-black ${colour(move5)}">${move5 === null ? 'N/A' : researchPct(move5)}</td>
            </tr>`;
        }).join('');
        detail.innerHTML = `<div class="border-t border-gray-100 pt-3 mt-1">
            <div class="flex items-center justify-between gap-3 mb-2">
                <div><p class="text-[10px] font-black text-purple-600 uppercase tracking-widest">Event Detail</p><p class="text-xs text-gray-500">EPS result and subsequent share-price reaction.</p></div>
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Yahoo Finance · ${study.events.length} events</span>
            </div>
            <div class="overflow-x-auto max-h-[30vh] overflow-y-auto">
                <table class="w-full text-left text-xs">
                    <thead class="sticky top-0 bg-white text-gray-400 uppercase tracking-wider">
                        <tr><th class="py-2 pr-3">Earnings</th><th class="py-2 px-3">EPS Est.</th><th class="py-2 px-3">EPS Actual</th><th class="py-2 px-3">Surprise</th><th class="py-2 px-3">1D</th><th class="py-2 pl-3">5D</th></tr>
                    </thead><tbody>${rows}</tbody>
                </table>
            </div>
        </div>`;
    }

    async function loadFinancialResearch(ticker, generation = prefetchGeneration) {
        const symbol = String(ticker || '').trim().toUpperCase();
        if (!symbol) return null;
        try {
            const loader = typeof window.getSethiStockResearch === 'function'
                ? window.getSethiStockResearch(symbol)
                : fetch(`https://sethistock-api.onrender.com/api/research/${encodeURIComponent(symbol)}`).then(response => {
                    if (!response.ok) throw new Error(`Research API returned ${response.status}`);
                    return response.json();
                });
            const data = await loader;
            if (generation !== prefetchGeneration || symbol !== String(state.ticker || '').trim().toUpperCase()) return null;
            researchData = data;
            researchTicker = canonicalSupplementaryTicker(symbol);
            fastResearchCache.set(researchTicker, data);
            if (displayedView) {
                renderFinancialCards(displayedView);
                renderFinancialCharts(displayedView);
                if (expandedChartId === 'ind-earnings') {
                    renderEarningsDetail();
                    const sourceDetail = document.getElementById('financial-detail-ind-earnings');
                    const modalDetail = document.getElementById('financial-expanded-detail');
                    if (sourceDetail && modalDetail) modalDetail.innerHTML = sourceDetail.innerHTML;
                }
                if (expandedChartId) requestAnimationFrame(() => renderExpandedPlot(expandedChartId));
            }
            return data;
        } catch (error) {
            console.debug(`Phase 4A research cards unavailable for ${symbol}:`, error);
            return null;
        }
    }

    function syncWindowControls(windowValue) {
        document.querySelectorAll('.financial-window-btn').forEach(button => {
            button.classList.toggle('active', String(button.dataset.financialWindow) === String(windowValue));
        });
    }

    function filterPointsToWindow(points, windowValue = desiredWindow) {
        if (!Array.isArray(points) || !points.length || windowValue === 'max') return points || [];
        const years = Number(windowValue);
        if (!Number.isFinite(years) || years <= 0) return points;
        const latestDate = new Date(points[points.length - 1]?.end);
        if (Number.isNaN(latestDate.getTime())) return points;
        const cutoff = new Date(latestDate);
        cutoff.setUTCFullYear(cutoff.getUTCFullYear() - years);
        return points.filter(point => {
            const date = new Date(point?.end);
            return !Number.isNaN(date.getTime()) && date >= cutoff;
        });
    }

    function closeExpandedChart() {
        const modal = document.getElementById('financial-chart-modal');
        const plot = document.getElementById('financial-expanded-plot');
        if (plot && typeof Plotly !== 'undefined') {
            try { Plotly.purge(plot); } catch (_) {}
        }
        if (modal && modal.parentNode) modal.parentNode.removeChild(modal);
        expandedChartId = null;
        document.body.classList.remove('modal-active');
    }

    function renderExpandedPlot(chartId) {
        const source = document.getElementById(chartId);
        const target = document.getElementById('financial-expanded-plot');
        if (!source || !target) return;

        if (!Array.isArray(source.data) || source.data.length === 0) {
            target.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-weight:700;">Chart data is still loading.</div>';
            return;
        }

        const traces = source.data.map(trace => {
            const clone = { ...trace };
            if (clone.type === 'bar' && Array.isArray(clone.text) && clone.text.length) {
                clone.textposition = 'outside';
                clone.textfont = { ...(clone.textfont || {}), color: '#334155', size: 11 };
                clone.cliponaxis = false;
            }
            return clone;
        });
        const sourceLayout = source.layout || {};
        const layout = {
            ...sourceLayout,
            autosize: true,
            width: undefined,
            height: undefined,
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#ffffff',
            margin: {
                t: 18,
                r: 24,
                b: sourceLayout.showlegend ? 64 : 48,
                l: 64
            },
            hoverlabel: {
                bgcolor: '#ffffff',
                bordercolor: '#cbd5e1',
                font: { color: '#0f172a', size: 13 },
                align: 'left',
                namelength: -1
            }
        };

        Plotly.react(target, traces, layout, { displayModeBar: false, responsive: true });
        requestAnimationFrame(() => Plotly.Plots.resize(target));
    }

    function toggleExpandedChart(chartId) {
        if (expandedChartId === chartId) {
            closeExpandedChart();
            return;
        }

        closeExpandedChart();
        const card = document.querySelector(`[data-financial-card="${chartId}"]`);
        const source = document.getElementById(chartId);
        if (!card || !source) return;

        expandedChartId = chartId;
        document.body.classList.add('modal-active');

        const title = card.querySelector('h4')?.textContent?.trim() || 'Financial Metric';
        const badge = document.getElementById(`fin-period-${chartId}`)?.textContent?.trim() || '';
        const modal = document.createElement('div');
        modal.id = 'financial-chart-modal';
        modal.style.position = 'fixed';
        modal.style.inset = '0';
        modal.style.zIndex = '220';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.padding = '36px';

        const earnings = chartId === 'ind-earnings';
        modal.innerHTML = `
            <button id="financial-modal-backdrop" type="button" aria-label="Close expanded chart" style="position:absolute;inset:0;border:0;background:rgba(15,23,42,.48);cursor:default;"></button>
            <section role="dialog" aria-modal="true" aria-label="${title}" style="position:relative;z-index:1;width:min(1040px,calc(100vw - 72px));height:min(660px,calc(100vh - 96px));background:#fff;border:1px solid #e2e8f0;border-radius:18px;box-shadow:0 24px 60px rgba(15,23,42,.22);display:flex;flex-direction:column;overflow:hidden;">
                <header style="height:64px;flex:0 0 64px;display:flex;align-items:center;justify-content:space-between;padding:0 22px;border-bottom:1px solid #eef2f7;background:#fff;">
                    <div style="display:flex;align-items:center;gap:12px;min-width:0;">
                        <h3 style="margin:0;color:#334155;font-size:15px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${title}</h3>
                        ${badge ? `<span style="padding:4px 8px;border:1px solid #e2e8f0;border-radius:7px;background:#f8fafc;color:#94a3b8;font-size:9px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;">${badge}</span>` : ''}
                    </div>
                    <button id="financial-modal-close" type="button" aria-label="Close expanded chart" style="width:34px;height:34px;border:1px solid #e2e8f0;border-radius:9px;background:#fff;color:#64748b;font-size:20px;line-height:1;cursor:pointer;">×</button>
                </header>
                <div style="flex:1;min-height:0;padding:16px 18px ${earnings ? '8px' : '18px'};background:#fff;display:flex;flex-direction:column;">
                    <div id="financial-expanded-plot" style="width:100%;${earnings ? 'height:300px;flex:0 0 300px;' : 'height:100%;flex:1;min-height:0;'}"></div>
                    ${earnings ? '<div id="financial-expanded-detail" style="flex:1;min-height:0;overflow:auto;padding:6px 8px 0;"></div>' : ''}
                </div>
            </section>`;

        document.body.appendChild(modal);
        document.getElementById('financial-modal-backdrop')?.addEventListener('click', closeExpandedChart);
        document.getElementById('financial-modal-close')?.addEventListener('click', closeExpandedChart);

        if (earnings) {
            renderEarningsDetail();
            const sourceDetail = document.getElementById('financial-detail-ind-earnings');
            const modalDetail = document.getElementById('financial-expanded-detail');
            if (sourceDetail && modalDetail) modalDetail.innerHTML = sourceDetail.innerHTML;
        }

        requestAnimationFrame(() => {
            requestAnimationFrame(() => renderExpandedPlot(chartId));
        });
    }

    function bindExpandButtons() {
        document.querySelectorAll('.financial-expand-btn').forEach(button => {
            button.addEventListener('click', () => toggleExpandedChart(button.dataset.chartId));
        });
    }

    function bindRevenueDriverButton() {
        const button = document.getElementById('financial-segment-button');
        if (!button || button.dataset.bound === '1') return;
        button.dataset.bound = '1';
        button.addEventListener('click', () => {
            const ticker = String((typeof state === 'object' ? state?.ticker : '') || document.getElementById('display-ticker')?.textContent || '').trim().toUpperCase();
            if (!ticker || typeof window.SethiStockOpenRevenueDrivers !== 'function') return;
            window.SethiStockOpenRevenueDrivers(ticker).catch?.(() => null);
        });
    }

    function syncRevenueDriverButton() {
        const button = document.getElementById('financial-segment-button');
        if (!button) return;
        const ticker = String((typeof state === 'object' ? state?.ticker : '') || document.getElementById('display-ticker')?.textContent || '').trim().toUpperCase();
        const supported = typeof window.SethiStockHasRevenueDrivers === 'function'
            ? window.SethiStockHasRevenueDrivers(ticker)
            : ['AAPL','MSFT','GOOG','GOOGL','AMZN','META','NVDA','TSLA','NFLX','JPM','V'].includes(ticker);
        button.classList.toggle('hidden', !supported);
        button.disabled = !supported;
    }

    function renderFinancialCards(view) {
        const cards = [
            { id: 'ind-rev', key: 'revenue', title: 'Revenue' },
            { id: 'ind-ebitda', key: 'ebitda', title: 'EBITDA' },
            { id: 'ind-net', key: 'net', title: 'Net Income' },
            { id: 'ind-margins', key: 'net_margin', title: 'Margin Profile', mode: 'margin' },
            { id: 'ind-ocf', key: 'ocf', title: 'Operating Cash Flow' },
            { id: 'ind-fcf', key: 'fcf', title: 'Free Cash Flow' },
            { id: 'ind-capex', key: 'capex', title: 'Capital Expenditure' },
            { id: 'ind-cash', key: 'cash', title: 'Cash Equivalents' },
            { id: 'ind-debt', key: 'debt', title: 'Total Debt' },
            { id: 'ind-shares', key: 'shares', title: 'Shares Outstanding' },
            { id: 'ind-pe', title: 'P/E (TTM) History', mode: 'valuation' },
            { id: 'ind-earnings', title: 'Earnings Surprise', mode: 'earnings' }
        ];
        const container = document.getElementById('individual-charts-container');
        if (!container) return;
        const periodLabel = humanPeriod(view?.period || 'annual');

        if (container.dataset?.phase4DashboardReady !== '1') {
            let html = '';
            cards.forEach(card => {
                const initialBadge = card.mode === 'valuation' ? 'TTM' : card.mode === 'earnings' ? 'Events' : periodLabel;
                html += `
                    <div class="financial-card bg-white px-4 pt-4 pb-3 rounded-2xl shadow-sm border border-gray-200 flex flex-col h-[330px] relative" data-financial-card="${card.id}">
                        <div class="flex items-center justify-between gap-3 mb-1">
                            <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">${card.title}</h4>
                            <div class="flex items-center gap-2">
                                ${card.id === 'ind-rev' ? `<button id="financial-segment-button" type="button" class="financial-segment-btn hidden items-center gap-1 px-2.5 py-1 rounded-lg border border-blue-200 bg-blue-50 text-[9px] font-black text-blue-700 uppercase tracking-wider hover:bg-blue-100 hover:border-blue-300 transition whitespace-nowrap" title="Open company revenue segments and operating drivers">By Segment <span aria-hidden="true">→</span></button>` : ''}
                                <span id="fin-period-${card.id}" class="px-2 py-1 rounded-md bg-gray-50 border border-gray-100 text-[9px] font-black text-gray-400 uppercase tracking-widest">${initialBadge}</span>
                                <button type="button" class="financial-expand-btn inline-flex h-7 w-7 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-400 hover:text-blue-600 hover:border-blue-300 hover:bg-blue-50 transition" data-chart-id="${card.id}" aria-label="Expand ${card.title} chart" title="Expand chart">
                                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
                                </button>
                            </div>
                        </div>
                        <div id="${card.id}" class="w-full flex-1 min-h-0 mt-0"></div>
                        <div id="financial-detail-${card.id}" class="hidden"></div>
                        <div class="grid grid-cols-4 gap-2 mt-1 pt-2.5 border-t border-gray-100">
                            ${[0,1,2,3].map(index => `<div class="text-center min-w-0"><p id="fin-label-${card.id}-${index}" class="text-[9px] text-gray-400 font-bold uppercase truncate">—</p><p id="fin-stat-${card.id}-${index}" class="font-semibold text-xs text-gray-400 truncate">-</p></div>`).join('')}
                        </div>
                    </div>`;
            });
            container.innerHTML = html;
            if (container.dataset) container.dataset.phase4DashboardReady = '1';
            bindExpandButtons();
            bindRevenueDriverButton();
        }

        syncRevenueDriverButton();
        cards.forEach(card => {
            const badge = document.getElementById(`fin-period-${card.id}`);
            if (badge) {
                if (card.mode === 'valuation') badge.textContent = 'TTM';
                else if (card.mode === 'earnings') badge.textContent = 'Events';
                else badge.textContent = view?.period === 'ttm' && ['cash', 'debt', 'shares'].includes(card.key)
                    ? 'Point-in-time'
                    : periodLabel;
            }
            const stats = statsForCard(card, view);
            for (let index = 0; index < 4; index += 1) {
                const label = document.getElementById(`fin-label-${card.id}-${index}`);
                const value = document.getElementById(`fin-stat-${card.id}-${index}`);
                if (label) label.textContent = stats.labels[index] || '—';
                if (value) {
                    value.textContent = stats.values[index] ?? '-';
                    value.className = `font-semibold text-xs ${stats.classes[index] || 'text-gray-400'} truncate`;
                }
            }
        });
    }

    function emptyChart(id, message = 'Data Unavailable') {
        const element = document.getElementById(id);
        if (!element) return;
        if (typeof Plotly !== 'undefined' && (element.classList.contains('js-plotly-plot') || element._fullLayout)) {
            try { Plotly.purge(element); } catch (_) {}
        }
        element.innerHTML = `<div data-financial-placeholder="1" class="flex h-full items-center justify-center text-gray-400 font-bold text-sm text-center px-5">${message}</div>`;
    }

    function preparePlotContainer(id) {
        const element = document.getElementById(id);
        if (!element) return null;

        // Plotly.purge can leave its marker class behind even after an empty-state
        // placeholder has replaced the plot DOM. Treat the placeholder itself as the
        // source of truth so loading/unavailable text can never survive under a chart.
        const placeholder = element.querySelector('[data-financial-placeholder="1"]');
        if (placeholder) {
            if (typeof Plotly !== 'undefined' && (element.classList.contains('js-plotly-plot') || element._fullLayout)) {
                try { Plotly.purge(element); } catch (_) {}
            }
            element.innerHTML = '';
            element.classList.remove('js-plotly-plot');
        } else {
            const hasPlot = element.classList.contains('js-plotly-plot') || Boolean(element._fullLayout);
            if (!hasPlot) element.innerHTML = '';
        }
        return element;
    }

    function chartLayout(view, showLegend = false) {
        return {
            margin: { t: 6, b: showLegend ? 40 : 28, l: 44, r: 6 },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            showlegend: showLegend,
            autosize: true,
            hovermode: 'x unified',
            hoverlabel: {
                bgcolor: '#ffffff',
                bordercolor: '#cbd5e1',
                font: { color: '#0f172a', size: 12 },
                align: 'left',
                namelength: -1
            },
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
        const rawPoints = filterPointsToWindow(validMetricPoints(view, key));
        if (!rawPoints.length) return null;
        const annualBars = view.period === 'annual' && options.forceLine !== true;
        const points = annualBars ? collapseAnnualPlotPoints(rawPoints) : rawPoints;
        const trace = {
            x: annualBars ? points.map(point => point.annualCategory) : points.map(point => point.end),
            y: points.map(point => point.value),
            name,
            customdata: points.map(point => point.label),
            text: points.map(point => metricDisplayValue(key, point.value)),
            hovertemplate: '%{customdata}<br>%{text}<extra></extra>'
        };
        if (annualBars) {
            trace.type = 'bar';
            trace.marker = { color: colour, line: { width: 0 } };
            // Keep normal dashboard bars clean; exact values remain available on hover.
            // The expanded modal restores outside labels where there is enough room.
            trace.textposition = 'none';
            trace.cliponaxis = false;
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
        if (!preparePlotContainer(id)) return;
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
        if (!preparePlotContainer('ind-margins')) return;
        const layout = chartLayout(view, true);
        layout.yaxis.tickformat = '.1f';
        layout.yaxis.ticksuffix = '%';
        Plotly.react('ind-margins', traces, layout, { displayModeBar: false, responsive: true });
    }

    function drawHistoricalPE() {
        const study = researchData?.valuation_bands;
        if (!study?.available || !study.observations?.length) return emptyChart('ind-pe', researchData ? 'Historical P/E unavailable' : 'Loading valuation history…');
        const observations = filterDatedItems([...study.observations].sort((a, b) => String(a.date).localeCompare(String(b.date))), 'date');
        if (!observations.length) return emptyChart('ind-pe', 'No P/E observations in this window');
        const trace = {
            x: observations.map(item => item.date),
            y: observations.map(item => item.pe),
            type: 'scatter', mode: 'lines+markers',
            line: { color: '#2563eb', width: 2.4 },
            marker: { size: 5, color: '#ffffff', line: { color: '#2563eb', width: 1.5 } },
            customdata: observations.map(item => [item.price, item.ttm_eps]),
            hovertemplate: '%{x}<br>P/E: %{y:.1f}x<br>Price: $%{customdata[0]:.2f}<br>TTM EPS: %{customdata[1]:.3f}<extra></extra>'
        };
        if (!preparePlotContainer('ind-pe')) return;
        const layout = chartLayout({ period: 'quarterly' }, false);
        layout.yaxis.tickformat = '.1f';
        layout.yaxis.ticksuffix = 'x';
        layout.shapes = [];
        const median = finiteNumber(study?.bands?.median);
        const current = finiteNumber(study?.current_pe);
        if (median !== null) layout.shapes.push({ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: median, y1: median, line: { color: '#94a3b8', width: 1.5, dash: 'dash' } });
        if (current !== null) layout.shapes.push({ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: current, y1: current, line: { color: '#111827', width: 1.5, dash: 'dot' } });
        Plotly.react('ind-pe', [trace], layout, { displayModeBar: false, responsive: true });
    }

    function drawEarningsSurprise() {
        const study = researchData?.earnings_reaction;
        if (!study?.available || !study.events?.length) return emptyChart('ind-earnings', researchData ? 'Earnings surprise history unavailable' : 'Loading earnings history…');
        const events = filterDatedItems([...study.events].sort((a, b) => String(a.earnings_date).localeCompare(String(b.earnings_date))), 'earnings_date')
            .filter(event => finiteNumber(event.surprise_pct) !== null);
        if (!events.length) return emptyChart('ind-earnings', 'No EPS surprise observations in this window');
        const y = events.map(event => Number(event.surprise_pct));
        const trace = {
            x: events.map(event => event.earnings_date),
            y,
            type: 'bar',
            marker: { color: y.map(value => value >= 0 ? '#16a34a' : '#dc2626') },
            customdata: events.map(event => [event.eps_estimate, event.reported_eps, event.move_1d_pct, event.move_5d_pct]),
            hovertemplate: '%{x}<br>EPS surprise: %{y:.1f}%<br>Estimate: %{customdata[0]}<br>Actual: %{customdata[1]}<br>1D: %{customdata[2]:.1f}%<br>5D: %{customdata[3]:.1f}%<extra></extra>'
        };
        if (!preparePlotContainer('ind-earnings')) return;
        const layout = chartLayout({ period: 'quarterly' }, false);
        layout.yaxis.tickformat = '.1f';
        layout.yaxis.ticksuffix = '%';
        layout.bargap = 0.28;
        Plotly.react('ind-earnings', [trace], layout, { displayModeBar: false, responsive: true });
    }

    function drawComparison(view, id, first, second) {
        const nonAnnual = view.period !== 'annual';
        const trace1 = traceForMetric(view, first.key, first.name, first.colour, { forceLine: nonAnnual });
        const trace2 = traceForMetric(view, second.key, second.name, second.colour, { forceLine: nonAnnual });
        const traces = [trace1, trace2].filter(Boolean);
        if (traces.length < 2) return emptyChart(id);
        if (!preparePlotContainer(id)) return;
        const layout = chartLayout(view, true);
        if (view.period === 'annual') layout.barmode = 'group';
        Plotly.react(id, traces, layout, { displayModeBar: false, responsive: true });
    }

    function renderFinancialCharts(view) {
        if (!view) return;
        drawSingleMetric(view, 'ind-rev', 'revenue', '#3b82f6', { name: 'Revenue' });
        drawSingleMetric(view, 'ind-ebitda', 'ebitda', '#0f766e', { name: 'EBITDA' });
        drawSingleMetric(view, 'ind-net', 'net', '#a855f7', { name: 'Net Income' });
        drawMargins(view);
        drawSingleMetric(view, 'ind-ocf', 'ocf', '#10b981', { name: 'Operating Cash Flow' });
        drawSingleMetric(view, 'ind-fcf', 'fcf', '#059669', { name: 'Free Cash Flow' });
        drawSingleMetric(view, 'ind-capex', 'capex', '#ef4444', { name: 'Capital Expenditure' });
        drawSingleMetric(view, 'ind-cash', 'cash', '#0ea5e9', { name: 'Cash' });
        drawSingleMetric(view, 'ind-debt', 'debt', '#f97316', { name: 'Debt' });
        drawSingleMetric(view, 'ind-shares', 'shares', '#64748b', { name: 'Shares' });
        drawHistoricalPE();
        drawEarningsSurprise();

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
        syncWindowControls(desiredWindow);
        renderFinancialCharts(view);
        setQualityAlert(view);
        setStatus(statusOverride || historyDescriptor(view), statusTone);
    }

    async function fetchSecHistoryPayload(ticker, period, signal = null) {
        const request = async metrics => {
            const query = new URLSearchParams({ period, metrics: metrics.join(','), limit: '200' });
            return fetchJsonWithRetry(
                `${API_URL}/api/sec/${encodeURIComponent(ticker)}/fundamentals/series?${query.toString()}`,
                signal ? { signal } : {},
                1
            );
        };
        try {
            return await request(SEC_METRICS);
        } catch (error) {
            if (signal?.aborted || error?.name === 'AbortError') throw error;
            console.debug(`EBITDA SEC series not yet available for ${ticker}; using baseline fundamentals.`);
            return request(BASE_SEC_METRICS);
        }
    }

    async function fetchFinancialHistoryIntoCache(ticker, period, generation = prefetchGeneration) {
        const key = `${ticker}|${period}`;
        const cached = financialMemoryCache.get(key);
        if (cached && Date.now() - cached.savedAt < FINANCIAL_CACHE_TTL_MS) return cached.view;
        try {
            const payload = await fetchSecHistoryPayload(ticker, period);
            if (generation !== prefetchGeneration || ticker !== String(state.ticker || '').trim().toUpperCase()) return null;
            const view = transformSecPayload(payload);
            if (!view.metricPoints.revenue?.length) return null;
            rememberFinancialView(key, view);
            return view;
        } catch (error) {
            console.debug(`Phase 4A ${period} prefetch skipped for ${ticker}:`, error);
            return null;
        }
    }

    function prefetchOtherPeriods(ticker, loadedPeriod) {
        const generation = prefetchGeneration;
        const periods = ['annual', 'quarterly', 'ttm'].filter(period => period !== loadedPeriod);
        const run = () => periods.reduce((promise, period) => promise.then(() => fetchFinancialHistoryIntoCache(ticker, period, generation)), Promise.resolve());
        if ('requestIdleCallback' in window) requestIdleCallback(run, { timeout: 1200 });
        else setTimeout(run, 250);
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
            const payload = await fetchSecHistoryPayload(ticker, period, requestController.signal);
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
        prefetchGeneration += 1;
        desiredWindow = 'max';
        closeExpandedChart();
        financialTicker = ticker;
        const supplementaryTicker = canonicalSupplementaryTicker(ticker);
        researchData = fastResearchCache.get(supplementaryTicker) || null;
        researchTicker = researchData ? supplementaryTicker : '';
        fallbackView = buildLegacyView(fin);
        applyFastEbitdaFallback(ticker, fallbackView);
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
        else {
            fallbackView = buildLegacyView(fin);
            applyFastEbitdaFallback(ticker, fallbackView);
        }
        renderFinancialCards(fallbackView);
    };

    drawFinancials = function(fin) {
        const ticker = String(state.ticker || '').trim().toUpperCase();
        if (!fallbackView || financialTicker !== ticker) resetForTicker(ticker, fin);
        else {
            fallbackView = buildLegacyView(fin);
            applyFastEbitdaFallback(ticker, fallbackView);
        }

        // The main stock payload now contains recent EBITDA plus P/E / earnings
        // research, so all 12 cards render in one pass. Long-run SEC history upgrades
        // the same cards independently and never blocks the first financial render.
        renderFinancialCharts(fallbackView);
        displayedView = fallbackView;

        // The full stock-analysis cache is deliberately long-lived. If it contains an
        // older placeholder research payload, hydrate only these two supplementary
        // cards from the lightweight research endpoint instead of rebuilding the stock.
        const supplementaryTicker = canonicalSupplementaryTicker(ticker);
        if (researchTicker !== supplementaryTicker || !researchPayloadSettled(researchData)) {
            loadFinancialResearch(ticker, prefetchGeneration).catch(() => null);
        }

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

    document.querySelectorAll('.financial-window-btn').forEach(button => {
        button.addEventListener('click', () => {
            const nextWindow = button.dataset.financialWindow || 'max';
            if (String(nextWindow) === String(desiredWindow)) return;
            desiredWindow = nextWindow;
            syncWindowControls(desiredWindow);
            if (displayedView) renderFinancialCharts(displayedView);
        });
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && expandedChartId) toggleExpandedChart(expandedChartId);
    });

    window.addEventListener('sethistock:analysis-start', () => {
        prefetchGeneration += 1;
        requestId += 1;
        if (requestController) requestController.abort();
        requestController = null;
        closeExpandedChart();
    });

    // Expose a tiny debugging surface for production smoke tests without coupling the
    // rest of SethiStock to the implementation details of this module.
    window.SethiStockFinancialHistory = {
        get period() { return desiredPeriod; },
        get source() { return displayedView?.sourceType || null; },
        get periodCount() { return displayedView?.periodCount || 0; },
        primeInitialData,
        load: loadFinancialHistory
    };
})();
