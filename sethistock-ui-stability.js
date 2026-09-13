// SethiStock UI stability layer — ticker-transition guards, compact Driver charts,
// loading affordances and a tiny repeat-analysis memory cache.
(() => {
    'use strict';

    const STOCK_CACHE_TTL_MS = 2 * 60 * 1000;
    const DRIVER_CHART_HEIGHT = 180;
    const DRIVER_SUPPORTED = new Set(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'JPM', 'V']);
    const stockResponseCache = new Map();
    let expectedTicker = '';
    let analysisWaitToken = 0;

    const normaliseTicker = value => String(value || '').trim().toUpperCase();
    const canonicalDriverTicker = value => {
        const ticker = normaliseTicker(value);
        return ticker === 'GOOG' ? 'GOOGL' : ticker;
    };
    const validTicker = value => /^[A-Z0-9.^-]{1,20}$/.test(normaliseTicker(value));

    function ensureStyles() {
        if (document.getElementById('sethistock-stability-styles')) return;
        const style = document.createElement('style');
        style.id = 'sethistock-stability-styles';
        style.textContent = `
            .sethi-inline-spinner {
                display:inline-block;
                width:12px;
                height:12px;
                border:2px solid currentColor;
                border-right-color:transparent;
                border-radius:9999px;
                animation:sethi-spin .7s linear infinite;
                flex:0 0 auto;
            }
            @keyframes sethi-spin { to { transform:rotate(360deg); } }
            #driver-chart-grid .driver-card { overflow:hidden !important; }
            #driver-chart-grid [id^="driver-chart-"] {
                height:${DRIVER_CHART_HEIGHT}px !important;
                min-height:${DRIVER_CHART_HEIGHT}px !important;
                max-height:${DRIVER_CHART_HEIGHT}px !important;
                overflow:hidden !important;
            }
            #driver-chart-grid [id^="driver-chart-"] .js-plotly-plot,
            #driver-chart-grid [id^="driver-chart-"] .plot-container,
            #driver-chart-grid [id^="driver-chart-"] .svg-container {
                height:${DRIVER_CHART_HEIGHT}px !important;
                max-height:${DRIVER_CHART_HEIGHT}px !important;
            }
            @media (prefers-reduced-motion: reduce) {
                .sethi-inline-spinner { animation:none; }
            }
        `;
        document.head.appendChild(style);
    }

    function decorateFinancialHistoryStatus() {
        const status = document.getElementById('financial-history-status');
        if (!status) return false;

        const update = () => {
            const text = status.textContent.trim();
            const loading = /^Loading\b/i.test(text);
            if (loading) {
                if (!status.querySelector('.sethi-inline-spinner')) {
                    status.innerHTML = `<span class="sethi-inline-spinner" aria-hidden="true"></span><span>${escapeHtml(text)}</span>`;
                }
                status.style.display = 'flex';
                status.style.alignItems = 'center';
                status.style.justifyContent = 'flex-end';
                status.style.gap = '7px';
            } else {
                status.style.display = '';
                status.style.alignItems = '';
                status.style.justifyContent = '';
                status.style.gap = '';
            }
        };

        const observer = new MutationObserver(update);
        observer.observe(status, { childList: true, characterData: true, subtree: true });
        update();
        return true;
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function purgeDriverPlots(root) {
        if (!root || typeof Plotly === 'undefined' || typeof Plotly.purge !== 'function') return;
        root.querySelectorAll('[id^="driver-chart-"]').forEach(chart => {
            try { Plotly.purge(chart); } catch (_) {}
        });
    }

    function resetDriverSurface(ticker) {
        const section = document.getElementById('company-drivers');
        if (!section) return;
        const symbol = normaliseTicker(ticker);
        section.dataset.expectedTicker = canonicalDriverTicker(symbol);

        const grid = document.getElementById('driver-chart-grid');
        purgeDriverPlots(grid);
        if (grid) {
            grid.innerHTML = '';
            grid.classList.add('hidden');
        }
        document.getElementById('driver-summary')?.classList.add('hidden');
        const unavailable = document.getElementById('driver-unavailable');
        if (unavailable) {
            unavailable.innerHTML = '';
            unavailable.classList.add('hidden');
        }

        const theme = document.getElementById('driver-theme');
        if (theme) theme.textContent = 'Company-specific operating KPIs from verified SEC filing histories.';

        const empty = document.getElementById('driver-empty');
        if (empty) {
            empty.classList.remove('hidden');
            empty.innerHTML = `
                <div class="flex items-center justify-center gap-2 text-blue-600">
                    <span class="sethi-inline-spinner" aria-hidden="true"></span>
                    <p class="text-sm font-bold">Waiting for ${escapeHtml(symbol || 'stock')} analysis…</p>
                </div>
                <p class="text-xs text-gray-400 mt-2">Cached Driver cards will synchronise automatically after this ticker finishes loading.</p>`;
        }

        const status = document.getElementById('driver-status');
        if (status) {
            status.textContent = `Waiting for ${symbol || 'stock'} analysis…`;
            status.className = 'text-[11px] font-bold uppercase tracking-widest text-blue-600';
        }
    }

    function currentStateTicker() {
        const fromState = typeof state === 'object' ? normaliseTicker(state?.ticker) : '';
        const fromDisplay = normaliseTicker(document.getElementById('display-ticker')?.textContent);
        return fromState || fromDisplay;
    }

    function analysisReadyFor(ticker) {
        const button = document.getElementById('search-btn');
        const dashboard = document.getElementById('dashboard');
        return currentStateTicker() === ticker && !button?.disabled && dashboard?.classList.contains('opacity-100');
    }

    function synchroniseDrivers(rawTicker, token) {
        const driverTicker = canonicalDriverTicker(rawTicker);
        if (!DRIVER_SUPPORTED.has(driverTicker)) return;

        const apply = drivers => {
            if (!drivers || token !== analysisWaitToken || !analysisReadyFor(rawTicker)) return;
            const statusText = document.getElementById('driver-status')?.textContent || '';
            if (drivers.ticker !== driverTicker || /waiting|temporarily unavailable/i.test(statusText)) {
                drivers.load(driverTicker).catch(() => null);
            }
        };

        if (window.SethiStockCompanyDrivers) {
            apply(window.SethiStockCompanyDrivers);
            return;
        }
        if (typeof window.SethiStockLoadCompanyDriversModule === 'function') {
            window.SethiStockLoadCompanyDriversModule(false).then(apply).catch(() => null);
        }
    }

    function waitForCurrentAnalysis(ticker) {
        const token = ++analysisWaitToken;
        let attempts = 0;
        const poll = () => {
            if (token !== analysisWaitToken) return;
            attempts += 1;
            if (analysisReadyFor(ticker)) {
                synchroniseDrivers(ticker, token);
                return;
            }
            if (attempts < 240) setTimeout(poll, 250);
        };
        poll();
    }

    function bindTickerTransitionGuard() {
        const form = document.getElementById('search-form');
        const input = document.getElementById('ticker-input');
        if (!form || form.dataset.stabilityTickerGuard === '1') return;
        form.dataset.stabilityTickerGuard = '1';

        form.addEventListener('submit', () => {
            const ticker = normaliseTicker(input?.value);
            if (!validTicker(ticker)) return;
            expectedTicker = ticker;
            resetDriverSurface(ticker);
            waitForCurrentAnalysis(ticker);
        }, true);

        document.addEventListener('click', event => {
            const link = event.target.closest?.('a[href="#company-drivers"]');
            if (!link) return;
            setTimeout(() => {
                const ticker = currentStateTicker();
                const driverTicker = canonicalDriverTicker(ticker);
                const drivers = window.SethiStockCompanyDrivers;
                const statusText = document.getElementById('driver-status')?.textContent || '';
                if (ticker && DRIVER_SUPPORTED.has(driverTicker) && drivers && (drivers.ticker !== driverTicker || /waiting|temporarily unavailable/i.test(statusText))) {
                    resetDriverSurface(ticker);
                    drivers.load(driverTicker).catch(() => null);
                }
            }, 0);
        });

        // If an old async Driver request tries to repaint while a new stock is loading,
        // keep the stale surface hidden until the Driver module adopts the expected ticker.
        const guard = setInterval(() => {
            if (!expectedTicker) return;
            const drivers = window.SethiStockCompanyDrivers;
            const section = document.getElementById('company-drivers');
            if (!drivers || !section) return;
            const expectedDriverTicker = canonicalDriverTicker(expectedTicker);
            if (drivers.ticker && drivers.ticker !== expectedDriverTicker) {
                const grid = document.getElementById('driver-chart-grid');
                if (grid && !grid.classList.contains('hidden')) resetDriverSurface(expectedTicker);
            }
            if (analysisReadyFor(expectedTicker) && drivers.ticker === expectedDriverTicker) {
                expectedTicker = '';
            }
        }, 300);
        window.addEventListener('pagehide', () => clearInterval(guard), { once: true });
    }

    function installDriverPlotGuard() {
        if (window.__sethiDriverPlotGuardInstalled) return;
        const tryInstall = () => {
            if (!window.Plotly?.react) {
                setTimeout(tryInstall, 100);
                return;
            }
            if (window.__sethiDriverPlotGuardInstalled) return;
            window.__sethiDriverPlotGuardInstalled = true;
            const nativeReact = window.Plotly.react.bind(window.Plotly);
            window.Plotly.react = (target, data, layout = {}, config = {}) => {
                const element = typeof target === 'string' ? document.getElementById(target) : target;
                if (!element?.id?.startsWith('driver-chart-')) return nativeReact(target, data, layout, config);

                const compactLayout = {
                    ...layout,
                    height: DRIVER_CHART_HEIGHT,
                    autosize: false,
                    margin: { t: 8, r: 8, b: 34, l: 46 },
                    xaxis: {
                        ...(layout.xaxis || {}),
                        nticks: 6,
                        automargin: true,
                        tickfont: { ...((layout.xaxis || {}).tickfont || {}), size: 9 }
                    },
                    yaxis: {
                        ...(layout.yaxis || {}),
                        automargin: true,
                        tickfont: { ...((layout.yaxis || {}).tickfont || {}), size: 9 }
                    }
                };
                return nativeReact(element, data, compactLayout, config).then(result => {
                    try { window.Plotly.Plots?.resize(element); } catch (_) {}
                    return result;
                });
            };
        };
        tryInstall();
    }

    function installRepeatAnalysisCache() {
        if (window.__sethiStockRepeatCacheInstalled || typeof window.fetch !== 'function') return;
        window.__sethiStockRepeatCacheInstalled = true;
        const nativeFetch = window.fetch.bind(window);

        window.fetch = async (input, init = {}) => {
            const url = typeof input === 'string' ? input : String(input?.url || '');
            const method = String(init?.method || 'GET').toUpperCase();
            const isStockAnalysis = method === 'GET' && /\/api\/stock\/[A-Z0-9.%5E_-]+(?:\?|$)/i.test(url);
            if (!isStockAnalysis) return nativeFetch(input, init);

            const cached = stockResponseCache.get(url);
            if (cached && Date.now() - cached.savedAt < STOCK_CACHE_TTL_MS) {
                return new Response(cached.body, {
                    status: cached.status,
                    statusText: cached.statusText,
                    headers: cached.headers
                });
            }

            const response = await nativeFetch(input, init);
            if (response.ok) {
                try {
                    const clone = response.clone();
                    const body = await clone.text();
                    const headers = {};
                    clone.headers.forEach((value, key) => { headers[key] = value; });
                    stockResponseCache.set(url, {
                        body,
                        status: clone.status,
                        statusText: clone.statusText,
                        headers,
                        savedAt: Date.now()
                    });
                    while (stockResponseCache.size > 12) stockResponseCache.delete(stockResponseCache.keys().next().value);
                } catch (_) {}
            }
            return response;
        };
    }

    function boot() {
        ensureStyles();
        bindTickerTransitionGuard();
        installDriverPlotGuard();
        installRepeatAnalysisCache();

        if (!decorateFinancialHistoryStatus()) {
            let tries = 0;
            const timer = setInterval(() => {
                tries += 1;
                if (decorateFinancialHistoryStatus() || tries >= 80) clearInterval(timer);
            }, 250);
        }
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
    else boot();
})();