(() => {
    'use strict';

    const url = 'https://gqqftksplktxfrilltsx.supabase.co';
    const publishableKey = 'sb_publishable_zjKjFfN1wTq9ocpje09Z1A_xgLe0UiK';
    const sessionKey = 'sethiway-member-session';
    const guestKey = 'sethiWatchlist';
    const syncKey = 'sethiway-member-watchlist-change';
    const watchlistTable = 'sethiway_member_watchlist';
    const ownerView = location.pathname.endsWith('/account.html')
        && ['owner', 'preview'].includes(new URLSearchParams(location.search).get('view'));
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

    window.SethiWayMembers = {
        connect, readWatchlist, guestTickers, setTicker, importGuestWatchlist,
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
