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
        'company-drivers': 'Company Drivers',
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

        document.querySelectorAll('nav a[href="#key-metrics"]').forEach(financialLink => {
            if (financialLink.nextElementSibling?.getAttribute('href') === '#company-drivers') return;
            financialLink.insertAdjacentHTML('afterend', '<a href="#company-drivers" class="hover:text-blue-600 transition">Drivers</a>');
        });

        const SUPPORTED_DRIVER_TICKERS = new Set([
            'AAPL', 'MSFT', 'GOOG', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'JPM', 'V'
        ]);

        function normaliseDriverTicker(value) {
            return String(value || '').trim().toUpperCase();
        }

        // Phase 3D stores immutable KPI snapshots in Supabase. For the flagship
        // universe, load the lightweight UI module automatically as soon as a search
        // starts so cached Company Drivers are ready by the time the user reaches them.
        // Cold/stale extraction still remains isolated from the core stock analysis.
        let driverModulePromise = null;
        function loadCompanyDriversModule(scrollAfterLoad = false) {
            if (window.SethiStockCompanyDrivers) {
                if (scrollAfterLoad) document.querySelector('#company-drivers')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                return Promise.resolve(window.SethiStockCompanyDrivers);
            }
            if (driverModulePromise) {
                if (scrollAfterLoad) driverModulePromise.then(() => document.querySelector('#company-drivers')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
                return driverModulePromise;
            }

            driverModulePromise = new Promise((resolve, reject) => {
                const existing = document.querySelector('script[data-sethistock-company-drivers]');
                if (existing) {
                    existing.addEventListener('load', () => resolve(window.SethiStockCompanyDrivers), { once: true });
                    existing.addEventListener('error', reject, { once: true });
                    return;
                }

                const driverScript = document.createElement('script');
                driverScript.src = 'sethistock-company-drivers.js?v=3e6';
                driverScript.dataset.sethistockCompanyDrivers = '1';
                driverScript.addEventListener('load', () => {
                    resolve(window.SethiStockCompanyDrivers);
                    if (scrollAfterLoad) {
                        requestAnimationFrame(() => document.querySelector('#company-drivers')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
                    }
                }, { once: true });
                driverScript.addEventListener('error', reject, { once: true });
                document.body.appendChild(driverScript);
            });
            return driverModulePromise;
        }

        // Exposed for the stability layer so a completed analysis can explicitly
        // synchronise the current ticker even if the module was still loading.
        window.SethiStockLoadCompanyDriversModule = loadCompanyDriversModule;

        const searchForm = document.querySelector('#search-form');
        const tickerInput = document.querySelector('#ticker-input');
        if (searchForm && searchForm.dataset.driverAutoloadBound !== '1') {
            searchForm.dataset.driverAutoloadBound = '1';
            searchForm.addEventListener('submit', () => {
                const ticker = normaliseDriverTicker(tickerInput?.value);
                if (SUPPORTED_DRIVER_TICKERS.has(ticker)) {
                    loadCompanyDriversModule(false).catch(() => null);
                }
            }, true);
        }

        document.querySelectorAll('a[href="#company-drivers"]').forEach(link => {
            link.addEventListener('click', event => {
                if (document.querySelector('#company-drivers')) return;
                event.preventDefault();
                loadCompanyDriversModule(true).catch(() => null);
            });
        });

        // Keep proximity loading as a fallback for unsupported/newly-added tickers,
        // while flagship names now initialise automatically from the persistent cache.
        const comparisons = document.querySelector('#comparisons');
        if ('IntersectionObserver' in window && comparisons) {
            const observer = new IntersectionObserver(entries => {
                if (!entries.some(entry => entry.isIntersecting)) return;
                observer.disconnect();
                loadCompanyDriversModule(false).catch(() => null);
            }, { rootMargin: '900px 0px', threshold: 0.01 });
            observer.observe(comparisons);
        }

        const initialTicker = normaliseDriverTicker(new URLSearchParams(window.location.search).get('ticker'));
        if (SUPPORTED_DRIVER_TICKERS.has(initialTicker)) {
            loadCompanyDriversModule(false).catch(() => null);
        }

        if (window.location.hash === '#company-drivers') {
            loadCompanyDriversModule(true).catch(() => null);
        }
    }
})();