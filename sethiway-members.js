(() => {
    'use strict';

    const url = 'https://gqqftksplktxfrilltsx.supabase.co';
    const publishableKey = 'sb_publishable_zjKjFfN1wTq9ocpje09Z1A_xgLe0UiK';
    const sessionKey = 'sethiway-member-session';
    const guestKey = 'sethiWatchlist';
    const syncKey = 'sethiway-member-watchlist-change';
    const watchlistTable = 'sethiway_member_watchlist';
    const ownerView = location.pathname.endsWith('/admin.html') || (location.pathname.endsWith('/account.html')
        && ['owner', 'preview'].includes(new URLSearchParams(location.search).get('view')));
    const tickerPattern = /^[A-Z0-9.^=-]{1,20}$/;

    let clientPromise;
    let session = null;
    let memberTickers = [];
    let accountError = null;
    let refreshVersion = 0;

    const readStorage = key => {
        try { return localStorage.getItem(key); } catch { return null; }
    };

    function guestTickers() {
        try {
            const items = JSON.parse(readStorage(guestKey) || '[]');
            return Array.isArray(items) ? [...new Set(items.filter(item => typeof item === 'string' && tickerPattern.test(item)))] : [];
        } catch {
            return [];
        }
    }

    function notify() {
        window.dispatchEvent(new Event('sethiway:member-change'));
    }

    function readWatchlist() {
        return session ? [...memberTickers] : guestTickers();
    }

    async function refreshWatchlist() {
        if (!session || ownerView) return;
        const accountId = session.user.id;
        const version = ++refreshVersion;
        const client = await connect();
        if (session?.user.id !== accountId || version !== refreshVersion) return;
        const { data, error } = await client.from(watchlistTable).select('ticker')
            .eq('user_id', accountId).order('created_at').order('ticker');
        if (session?.user.id !== accountId || version !== refreshVersion) return;
        accountError = error ? 'Your saved tickers are temporarily unavailable.' : null;
        if (!error) memberTickers = data.map(row => row.ticker);
        notify();
    }

    function acceptSession(next, authEvent) {
        if (next?.user.is_anonymous) next = null;
        const changed = next?.user.id !== session?.user.id;
        session = next;
        if (changed) {
            memberTickers = [];
            accountError = null;
            refreshVersion++;
        }
        if (authEvent === 'PASSWORD_RECOVERY') {
            window.dispatchEvent(new Event('sethiway:password-recovery'));
        }
        if (changed || authEvent === 'INITIAL_SESSION') {
            notify();
            if (next) {
                refreshWatchlist().catch(reportSyncError);
                connect().then(client => client.rpc('sethiway_record_member_activity'))
                    .then(({ error }) => { if (error) console.warn('Member activity could not be recorded.'); })
                    .catch(() => {});
            }
        }
    }

    function reportSyncError() {
        if (!session) return;
        accountError = 'Your saved tickers are temporarily unavailable.';
        notify();
    }

    function connect() {
        if (!['sethiway.com', 'www.sethiway.com', 'localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) {
            return Promise.reject(new Error('Account sign-in is available on SethiWay.'));
        }
        if (!clientPromise) {
            clientPromise = new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.119.0/dist/umd/supabase.js';
                script.integrity = 'sha384-uteMfOloLDGt042uDz+xHGF3ym63/WQ6rFq7murQRG8Ih7QrXGEGNtWd8688sb4O';
                script.crossOrigin = 'anonymous';
                script.onerror = () => reject(new Error('The account service could not load. Refresh to retry.'));
                script.onload = async () => {
                    try {
                        const client = window.supabase.createClient(url, publishableKey, {
                            auth: { storageKey: sessionKey, flowType: 'pkce' }
                        });
                        const { data, error } = await client.auth.getSession();
                        if (error && !['session_not_found', 'refresh_token_not_found'].includes(error.code)) throw error;
                        acceptSession(data.session, 'INITIAL_SESSION');
                        client.auth.onAuthStateChange((event, next) => {
                            // Run outside the Auth callback so follow-up queries can use the session.
                            setTimeout(() => acceptSession(next, event), 0);
                        });
                        resolve(client);
                    } catch (error) {
                        reject(error);
                    }
                };
                document.head.append(script);
            });
        }
        return clientPromise;
    }

    async function setTicker(ticker, save) {
        if (!tickerPattern.test(ticker)) throw new Error('Enter a valid ticker.');
        if (clientPromise || readStorage(sessionKey)) await connect();
        const accountId = session?.user.id;
        if (!accountId) {
            const tickers = guestTickers().filter(item => item !== ticker);
            localStorage.setItem(guestKey, JSON.stringify(save ? [...tickers, ticker] : tickers));
            notify();
            return;
        }
        const client = await connect();
        if (session?.user.id !== accountId) throw new Error('Your account changed. Try again.');
        const query = client.from(watchlistTable);
        const { error } = await (save
            ? query.upsert({ ticker }, { onConflict: 'user_id,ticker', ignoreDuplicates: true })
            : query.delete().eq('user_id', accountId).eq('ticker', ticker));
        if (error) throw new Error('Could not update your watchlist. Try again.');
        if (session?.user.id === accountId) {
            memberTickers = memberTickers.filter(item => item !== ticker);
            if (save) memberTickers.push(ticker);
            accountError = null;
            notify();
            announceChange();
            await refreshWatchlist();
        }
    }

    function announceChange() {
        try { localStorage.setItem(syncKey, String(Date.now())); } catch { /* optional tab sync */ }
    }

    async function importGuestWatchlist() {
        const tickers = guestTickers();
        if (!session || !tickers.length) return;
        const accountId = session.user.id;
        const client = await connect();
        if (session?.user.id !== accountId) return;
        const { error } = await client.from(watchlistTable).upsert(tickers.map(ticker => ({ ticker })), {
            onConflict: 'user_id,ticker', ignoreDuplicates: true
        });
        if (error) throw new Error('Could not import your watchlist. Try again.');
        announceChange();
        await refreshWatchlist();
    }

    async function readMarketSnapshots(tickers) {
        const client = await connect();
        const quotes = new Map();
        for (let offset = 0; offset < tickers.length; offset += 30) {
            const { data, error } = await client.from('sethistock_public_snapshots')
                .select('ticker,quote_payload,quote_updated_at,analysis_updated_at,valuation:analysis_payload->stats->>pe')
                .in('ticker', tickers.slice(offset, offset + 30)).abortSignal(AbortSignal.timeout(5000));
            if (error) throw error;
            for (const row of data) {
                const quote = row.quote_payload;
                if (!Number.isFinite(quote?.current_price) || quote.current_price <= 0) continue;
                const pe = typeof row.valuation === 'string' ? Number.parseFloat(row.valuation) : NaN;
                quotes.set(row.ticker, {
                    price: quote.current_price, change: quote.pct_change, pe: Number.isFinite(pe) ? pe : null,
                    updatedAt: row.quote_updated_at
                });
            }
        }
        return quotes;
    }

    async function openWorkspaceStorage(accountId) {
        const client = await connect();
        const table = 'sethiway_member_workspace';
        const assertAccount = () => {
            if (session?.user.id !== accountId) throw new Error('Your account changed. Sign in again.');
        };
        assertAccount();
        const { data, error } = await client.from(table).select('kind, payload, revision').eq('user_id', accountId);
        assertAccount();
        if (error) throw new Error('Could not load your saved workspace. Refresh to try again.');
        const documents = new Map(data.map(row => [row.kind, row]));
        const queues = new Map();
        const blocked = new Set();
        return {
            get(kind) { return documents.get(kind)?.payload; },
            save(kind, payload) {
                const snapshot = JSON.parse(JSON.stringify(payload));
                const previous = queues.get(kind) || Promise.resolve();
                const write = previous.catch(() => {}).then(async () => {
                    assertAccount();
                    if (blocked.has(kind)) throw new Error('This was updated in another tab or device. Refresh before editing again.');
                    const current = documents.get(kind);
                    const result = await (current
                        ? client.from(table).update({ payload: snapshot, revision: current.revision + 1 })
                            .eq('user_id', accountId).eq('kind', kind).eq('revision', current.revision)
                            .select('kind, payload, revision').maybeSingle()
                        : client.from(table).upsert({ user_id: accountId, kind, payload: snapshot }, {
                            onConflict: 'user_id,kind', ignoreDuplicates: true
                        }).select('kind, payload, revision').maybeSingle());
                    assertAccount();
                    if (result.error) throw new Error('Your changes could not be saved. Try editing again.');
                    if (!result.data) {
                        blocked.add(kind);
                        throw new Error('This was updated in another tab or device. Refresh before editing again.');
                    }
                    documents.set(kind, result.data);
                });
                queues.set(kind, write);
                return write;
            }
        };
    }

    window.SethiWayMembers = {
        connect, readWatchlist, guestTickers, setTicker, importGuestWatchlist, openWorkspaceStorage, readMarketSnapshots,
        hasStoredSession: () => Boolean(readStorage(sessionKey)),
        get session() { return session; },
        get watchlistError() { return accountError; }
    };
    window.addEventListener('storage', event => {
        if (event.key === guestKey && !session) notify();
        if (event.key === syncKey && session) refreshWatchlist().catch(reportSyncError);
    });
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && session) refreshWatchlist().catch(reportSyncError);
    });

    function updateAccountLinks() {
        document.querySelectorAll('[data-member-link]').forEach(link => {
            link.textContent = session ? 'My Workspace' : 'Sign In';
        });
    }
    window.addEventListener('sethiway:member-change', updateAccountLinks);
    notify();
    if (readStorage(sessionKey)) connect().catch(() => {});
})();
