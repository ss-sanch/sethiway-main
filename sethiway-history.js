(() => {
    const STORAGE_KEY = 'sethiwayLastDestination';
    const page = window.location.pathname.split('/').pop() || '';
    const toolNames = {
        'sethimacro.html': 'SethiMacro',
        'sethistock.html': 'SethiStock',
        'sethiportfolio.html': 'SethiPortfolio',
        'sethiquant.html': 'SethiQuant'
    };
    const tool = toolNames[page];
    if (!tool) return;

    const knownSections = {
        'job-market': 'Job Market',
        'inflation-rates': 'Inflation & Rates',
        'currencies': 'Currencies',
        'key-metrics': 'Key Metrics',
        'research-labs': 'Research Labs',
        'valuation': 'Valuations',
        'comparisons': 'Comparisons',
        'extra': 'Extra',
        'portfolio-lab': 'Portfolio Lab',
        'decisions': 'Decisions',
        'exposure': 'Exposure Map',
        'fx': 'FX Analytics',
        'risk': 'Portfolio Risk',
        'section-options': 'Options & Greeks',
        'section-backtest': 'Backtesting',
        'section-var': 'Market Risk Lab'
    };

    function fallbackSection(hash) {
        const clean = hash.replace(/^#/, '').replace(/^section-/, '').replace(/-/g, ' ').trim();
        return clean ? clean.replace(/\b\w/g, char => char.toUpperCase()) : '';
    }

    function currentLabel() {
        const details = [];
        const params = new URLSearchParams(window.location.search);
        if (page === 'sethistock.html') {
            const ticker = (params.get('ticker') || '').trim().toUpperCase();
            if (/^[A-Z0-9.^-]{1,20}$/.test(ticker)) details.push(ticker);
        }
        const hashKey = window.location.hash.replace(/^#/, '');
        if (hashKey) details.push(knownSections[hashKey] || fallbackSection(window.location.hash));
        return details.length ? `${tool} · ${details.join(' · ')}` : tool;
    }

    function saveDestination() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                href: `${page}${window.location.search}${window.location.hash}`,
                label: currentLabel(),
                updatedAt: Date.now()
            }));
        } catch {}
    }

    saveDestination();
    window.addEventListener('hashchange', saveDestination);
    window.addEventListener('popstate', saveDestination);

    if (page === 'sethistock.html') {
        if (!document.querySelector('script[data-sethistock-ui-stability]')) {
            const stabilityScript = document.createElement('script');
            stabilityScript.src = 'sethistock-ui-stability.js?v=4';
            stabilityScript.dataset.sethistockUiStability = '1';
            document.body.appendChild(stabilityScript);
        }

        // A single upstream Yahoo/yfinance stall must never leave SethiStock in an
        // endless "Analysing..." state. Only the heavy full-analysis route gets a
        // deadline; lightweight quote/chart/driver requests keep their own logic.
        if (!window.__sethiStockAnalysisDeadlineInstalled && typeof window.fetch === 'function') {
            window.__sethiStockAnalysisDeadlineInstalled = true;
            const nativeFetch = window.fetch.bind(window);
            window.fetch = (input, init = {}) => {
                const url = typeof input === 'string' ? input : String(input?.url || '');
                if (!url.includes('/api/stock/')) return nativeFetch(input, init);

                const controller = new AbortController();
                const upstreamSignal = init?.signal;
                if (upstreamSignal) {
                    if (upstreamSignal.aborted) controller.abort();
                    else upstreamSignal.addEventListener('abort', () => controller.abort(), { once: true });
                }

                return new Promise((resolve, reject) => {
                    let settled = false;
                    const timeout = setTimeout(() => {
                        if (settled) return;
                        settled = true;
                        controller.abort();
                        const error = new Error('Detailed analysis timed out after 50 seconds. Please retry; the data provider may be temporarily slow.');
                        error.status = 408;
                        reject(error);
                    }, 50000);

                    nativeFetch(input, { ...init, signal: controller.signal }).then(
                        response => {
                            if (settled) return;
                            settled = true;
                            clearTimeout(timeout);
                            resolve(response);
                        },
                        error => {
                            if (settled) return;
                            settled = true;
                            clearTimeout(timeout);
                            reject(error);
                        }
                    );
                });
            };
        }

        const SUPPORTED_DRIVER_TICKERS = new Set([
            'AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'JPM', 'V'
        ]);

        function normaliseDriverTicker(value) {
            return String(value || '').trim().toUpperCase();
        }

        function canonicalDriverTicker(value) {
            const ticker = normaliseDriverTicker(value);
            return ticker === 'GOOG' ? 'GOOGL' : ticker;
        }

        let driverModulePromise = null;
        function loadCompanyDriversModule() {
            if (window.SethiStockCompanyDrivers) return Promise.resolve(window.SethiStockCompanyDrivers);
            if (driverModulePromise) return driverModulePromise;

            driverModulePromise = new Promise((resolve, reject) => {
                const existing = document.querySelector('script[data-sethistock-company-drivers]');
                if (existing) {
                    existing.addEventListener('load', () => resolve(window.SethiStockCompanyDrivers), { once: true });
                    existing.addEventListener('error', reject, { once: true });
                    return;
                }

                const driverScript = document.createElement('script');
                driverScript.src = 'sethistock-company-drivers.js?v=4b1';
                driverScript.dataset.sethistockCompanyDrivers = '1';
                driverScript.addEventListener('load', () => resolve(window.SethiStockCompanyDrivers), { once: true });
                driverScript.addEventListener('error', error => {
                    driverModulePromise = null;
                    reject(error);
                }, { once: true });
                document.body.appendChild(driverScript);
            });
            return driverModulePromise;
        }

        // Phase 4B: Company Drivers no longer occupy the normal SethiStock page and
        // are not preloaded during every flagship analysis. Revenue opens them on demand.
        window.SethiStockLoadCompanyDriversModule = loadCompanyDriversModule;
        window.SethiStockHasRevenueDrivers = ticker => SUPPORTED_DRIVER_TICKERS.has(normaliseDriverTicker(ticker));
        window.SethiStockOpenRevenueDrivers = ticker => {
            const symbol = canonicalDriverTicker(ticker || (typeof state === 'object' ? state?.ticker : '') || document.getElementById('display-ticker')?.textContent);
            if (!SUPPORTED_DRIVER_TICKERS.has(symbol)) return Promise.resolve(false);
            return loadCompanyDriversModule().then(module => {
                if (!module?.open) return false;
                return module.open(symbol);
            }).catch(error => {
                console.warn('Revenue Drivers failed to open:', error);
                return false;
            });
        };
    }
})();
