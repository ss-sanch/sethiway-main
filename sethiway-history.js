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
})();
