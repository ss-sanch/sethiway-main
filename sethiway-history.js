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
            stabilityScript.src = 'sethistock-ui-stability.js?v=5';
            stabilityScript.dataset.sethistockUiStability = '1';
            document.body.appendChild(stabilityScript);
        }

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
                driverScript.src = 'sethistock-company-drivers.js?v=4b2';
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

        function loadValuationInfoFix() {
            if (window.SethiStockValuationV2InfoFix || document.querySelector('script[data-sethistock-valuation-v2-info-fix]')) return;
            const infoScript = document.createElement('script');
            infoScript.src = 'sethistock-valuation-v2-info-fix.js?v=4d9';
            infoScript.dataset.sethistockValuationV2InfoFix = '1';
            infoScript.addEventListener('error', error => console.warn('Advanced Valuation info modal fix failed to load:', error), { once: true });
            document.body.appendChild(infoScript);
        }

        function loadValuationVisualPolish() {
            if (window.SethiStockValuationV2VisualPolish) {
                loadValuationInfoFix();
                return;
            }
            const existing = document.querySelector('script[data-sethistock-valuation-v2-visual-polish]');
            if (existing) {
                existing.addEventListener('load', loadValuationInfoFix, { once: true });
                return;
            }
            const visualScript = document.createElement('script');
            visualScript.src = 'sethistock-valuation-v2-visual-polish.js?v=4d6';
            visualScript.dataset.sethistockValuationV2VisualPolish = '1';
            visualScript.addEventListener('load', loadValuationInfoFix, { once: true });
            visualScript.addEventListener('error', error => console.warn('Advanced Valuation visual polish failed to load:', error), { once: true });
            document.body.appendChild(visualScript);
        }

        function loadValuationPolish() {
            if (window.SethiStockValuationV2Polish) {
                loadValuationVisualPolish();
                return;
            }
            const existing = document.querySelector('script[data-sethistock-valuation-v2-polish]');
            if (existing) {
                existing.addEventListener('load', loadValuationVisualPolish, { once: true });
                return;
            }
            const polishScript = document.createElement('script');
            polishScript.src = 'sethistock-valuation-v2-polish.js?v=4d5';
            polishScript.dataset.sethistockValuationV2Polish = '1';
            polishScript.addEventListener('load', loadValuationVisualPolish, { once: true });
            polishScript.addEventListener('error', error => console.warn('Advanced Valuation 2.0 polish failed to load:', error), { once: true });
            document.body.appendChild(polishScript);
        }

        if (!document.querySelector('script[data-sethistock-valuation-v2]')) {
            const valuationScript = document.createElement('script');
            valuationScript.src = 'sethistock-valuation-v2.js?v=4d1';
            valuationScript.dataset.sethistockValuationV2 = '1';
            valuationScript.addEventListener('load', loadValuationPolish, { once: true });
            valuationScript.addEventListener('error', error => console.warn('Advanced Valuation 2.0 failed to load:', error), { once: true });
            document.body.appendChild(valuationScript);
        } else if (window.SethiStockValuationV2) {
            loadValuationPolish();
        } else {
            document.querySelector('script[data-sethistock-valuation-v2]')?.addEventListener('load', loadValuationPolish, { once: true });
        }
    }
})();