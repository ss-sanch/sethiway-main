(() => {
    'use strict';

    // This replacement exists only on the visual review branch.
    if (!['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) return;

    const roleKey = 'sethiway-visual-review-role';
    const roles = ['member', 'owner'];
    const storedRole = sessionStorage.getItem(roleKey);
    let role = roles.includes(storedRole) ? storedRole : null;
    const notify = () => window.dispatchEvent(new Event('sethiway:member-change'));
    const userSession = () => role ? {
        user: { id: role, email: role + '@example.test' },
        access_token: 'local-visual-review-' + role
    } : null;
    const watchlistKey = () => 'sethiway-visual-tickers-' + (role || 'guest');
    const readWatchlist = () => JSON.parse(sessionStorage.getItem(watchlistKey())
        || (role ? '["MSFT","VWRP.L"]' : '[]'));
    const setRole = next => {
        role = next;
        if (next) sessionStorage.setItem(roleKey, next);
        else sessionStorage.removeItem(roleKey);
        notify();
    };

    const fakeEmail = email => /^[a-z0-9._+-]+@example\.test$/i.test(email);
    const fakeOnly = email => fakeEmail(email)
        ? { data: { session: null } }
        : { error: new Error('Use a sample email ending in @example.test for this preview.') };
    const client = {
        auth: {
            async signInWithPassword({ email, password }) {
                const requested = email.trim().toLowerCase().split('@')[0];
                if (!fakeEmail(email) || !roles.includes(requested) || password !== 'demo-password') {
                    return { error: new Error('Use a sample account.') };
                }
                setRole(requested);
                return { data: { session: userSession() } };
            },
            async signUp({ email }) { return fakeOnly(email); },
            async resetPasswordForEmail(email) { return fakeOnly(email); },
            async signOut() { setRole(null); return {}; }
        },
        async rpc(name) {
            if (name === 'sethiway_is_owner') return { data: role === 'owner' };
            if (name === 'sethiway_owner_metrics' && role === 'owner') {
                return { data: { verified_members: 12, active_members: 3, recorded_browsers: 8 } };
            }
            return { error: { code: '42501' } };
        }
    };
    window.SethiWayMembers = {
        get session() { return userSession(); },
        get watchlistError() { return null; },
        hasStoredSession: () => Boolean(role),
        connect: async () => client,
        readWatchlist,
        guestTickers: () => [],
        async setTicker(ticker, save) {
            if (!/^[A-Z0-9.^=-]{1,20}$/.test(ticker)) throw new Error('Enter a valid ticker.');
            const tickers = readWatchlist().filter(item => item !== ticker);
            if (save) tickers.push(ticker);
            sessionStorage.setItem(watchlistKey(), JSON.stringify(tickers));
            notify();
        }
    };

    const fetchLive = window.fetch.bind(window);
    window.fetch = (input, init) => {
        const url = new URL(typeof input === 'string' ? input : (input.url || input.href), location.href);
        if (url.pathname === '/api/admin/telemetry') {
            const owner = role === 'owner' && new Headers(init?.headers).get('Authorization') === 'Bearer local-visual-review-owner';
            return Promise.resolve(Response.json(owner ? {
                total_events: 20,
                project_breakdown: { SethiStock: 10, SethiMacro: 6, SethiQuant: 4 },
                top_tickers: [{ ticker: 'MSFT', count: 8 }, { ticker: 'AAPL', count: 6 }],
                recent_logs: [{ project: 'SethiStock', action: 'search', ticker: 'MSFT', created_at: new Date().toISOString() }],
                markowitz_logs: [],
                load_performance: { samples: 3, avg_quote_ms: 450, avg_full_ms: 1400 },
                recent_stock_loads: [],
                ticker_loads: []
            } : {}, { status: owner ? 200 : 403 }));
        }
        if (location.pathname.endsWith('/admin.html') && ['/openapi.json', '/api/pillar-jobs'].includes(url.pathname)) {
            return Promise.resolve(Response.json({}));
        }
        if (url.pathname.includes('/api/telemetry') || url.hostname === 'api.web3forms.com') {
            return Promise.resolve(Response.json({ preview: true }));
        }
        const method = String(init?.method || input.method || 'GET').toUpperCase();
        if (url.origin !== location.origin && !['GET', 'HEAD'].includes(method)) {
            return Promise.resolve(Response.json({ error: 'External submissions are disabled in the local preview.' }, { status: 403 }));
        }
        return fetchLive(input, init);
    };

    const banner = document.createElement('aside');
    banner.setAttribute('aria-label', 'Local visual review');
    banner.style.cssText = 'display:flex;flex-wrap:wrap;align-items:center;gap:.75rem;padding:.8rem 1.25rem;background:#eff6ff;color:#1e3a8a;border-bottom:1px solid #bfdbfe;font:600 14px system-ui';
    const label = document.createElement('span');
    label.textContent = 'Local visual review · Sample accounts and metrics';
    banner.append(label);
    for (const [next, text, href] of [['member', 'Try as member', 'account.html'], ['owner', 'Try as owner', 'admin.html'], [null, 'Open sign-in form', 'account.html']]) {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = text;
        button.style.cssText = 'padding:.4rem .65rem;background:white;border:1px solid #bfdbfe;border-radius:.4rem;cursor:pointer';
        button.addEventListener('click', () => {
            if (next) sessionStorage.setItem(roleKey, next);
            else sessionStorage.removeItem(roleKey);
            location.assign(href);
        });
        banner.append(button);
    }
    document.body.prepend(banner);
    function updateLinks() {
        document.querySelectorAll('[data-member-link]').forEach(link => {
            link.textContent = role ? 'My Workspace' : 'Sign In';
        });
    }
    window.addEventListener('sethiway:member-change', updateLinks);
    updateLinks();
    notify();
})();
