(() => {
    'use strict';

    const members = window.SethiWayMembers;
    const params = new URLSearchParams(location.search);
    const view = params.get('view');
    const isPreview = view === 'preview';
    const needsOwner = isPreview || view === 'owner';
    const accountUrl = new URL('account.html', location.href).href;
    const $ = id => document.getElementById(id);
    const status = $('account-status');
    const authForm = $('auth-form');
    const sample = ['MSFT', 'VWRP.L', 'AAPL', 'NVDA', 'AZN.L', 'GOOGL', 'JPM'];

    let mode = 'signin';
    let client;
    let busy = false;
    let renderedUser;
    let displayVersion = 0;
    let previewTickers = [...sample];
    let renderedTickers;
    let quoteVersion = 0;
    let marketQuotes = new Map();
    let quoteStatus = 'No snapshot available';
    const pendingSaves = new Set();
    const saveErrors = new Map();

    function reportSave(task, kind) {
        const status = $('workspace-save-status');
        const version = displayVersion;
        pendingSaves.add(task);
        status.textContent = 'Saving workspace…';
        task.then(() => {
            if (version === displayVersion) saveErrors.delete(kind);
        }, error => {
            if (version === displayVersion) saveErrors.set(kind, error.message);
        }).finally(() => {
            pendingSaves.delete(task);
            if (version === displayVersion) status.textContent = [...saveErrors.values()][0]
                || (pendingSaves.size ? 'Saving workspace…' : 'Workspace saved.');
        });
    }

    function message(text) {
        status.textContent = text || '';
        status.hidden = !text;
    }

    function setMode(next) {
        mode = next;
        const labels = {
            signin: ['Sign in to SethiWay', 'Save stocks, follow macro topics and pin your favourite tools.', 'Sign in'],
            forgot: ['Reset your password', 'We’ll email you a password reset link.', 'Send reset link'],
            recovery: ['Choose a new password', 'Use at least eight characters.', 'Update password']
        };
        const [title, intro, button] = labels[next];
        $('auth-title').textContent = title;
        $('auth-intro').textContent = intro;
        $('auth-submit').textContent = button;
        $('email-field').hidden = next === 'recovery';
        $('account-email').required = next !== 'recovery';
        $('password-field').hidden = next === 'forgot';
        $('account-password').required = next !== 'forgot';
        $('account-password').autocomplete = next === 'recovery' ? 'new-password' : 'current-password';
        $('account-password').minLength = next === 'recovery' ? 8 : 0;
        $('account-password').value = '';
        $('auth-links').hidden = next === 'recovery';
        document.querySelectorAll('[data-auth-mode]').forEach(link => {
            link.hidden = next === 'signin' ? link.dataset.authMode === 'signin' : link.dataset.authMode !== 'signin';
        });
    }

    function renderWatchlist(force = false) {
        if ($('workspace').hidden) return;
        const tickers = isPreview ? previewTickers : members.readWatchlist();
        const tickerKey = JSON.stringify(tickers);
        if (!isPreview && !force && tickerKey !== renderedTickers) {
            renderedTickers = tickerKey;
            marketQuotes = new Map();
            quoteStatus = 'Loading quote…';
            const version = ++quoteVersion;
            if (tickers.length) members.readMarketSnapshots(tickers).then(quotes => {
                if (version !== quoteVersion) return;
                marketQuotes = quotes;
                quoteStatus = 'No snapshot available';
                renderWatchlist(true);
            }).catch(() => {
                if (version !== quoteVersion) return;
                quoteStatus = 'Quotes temporarily unavailable';
                renderWatchlist(true);
            });
        }
        $('watchlist-description').textContent = isPreview ? 'Sample quotes · local currency · forward P/E' : 'SethiStock snapshots · quoted units · P/E';
        $('empty-watchlist').hidden = tickers.length > 0;
        $('import-watchlist').hidden = isPreview || !members.guestTickers().some(ticker => !tickers.includes(ticker));
        $('saved-tickers').replaceChildren(...tickers.map(ticker => {
            const row = document.createElement('li');
            row.className = 'flex items-start justify-between gap-2 py-2.5';
            const link = document.createElement('a');
            link.textContent = ticker;
            link.href = 'sethistock.html?ticker=' + encodeURIComponent(ticker);
            link.className = 'text-sm font-bold text-blue-700 hover:underline';
            const remove = document.createElement('button');
            remove.type = 'button';
            remove.textContent = '×';
            remove.setAttribute('aria-label', 'Remove ' + ticker);
            remove.className = 'rounded px-1.5 text-base leading-tight text-slate-600 hover:bg-slate-100';
            remove.addEventListener('click', () => changeTicker(ticker, false));
            const identity = document.createElement('div');
            identity.className = 'min-w-0';
            identity.append(link);
            const quote = isPreview ? window.SethiWayPreviewQuotes.get(ticker) : marketQuotes.get(ticker);
            const name = document.createElement('p');
            name.className = 'truncate text-xs text-slate-600';
            name.textContent = isPreview ? quote?.name || 'No sample quote' : quote?.updatedAt
                ? 'Quote · ' + new Date(quote.updatedAt).toLocaleString('en-GB', { timeZone: 'UTC', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) + ' UTC'
                : quoteStatus;
            identity.append(name);
            const right = document.createElement('div');
            right.className = 'flex shrink-0 items-start gap-1.5';
            if (quote) {
                const metrics = document.createElement('div');
                metrics.className = 'text-right tabular-nums';
                const price = document.createElement('p');
                price.className = 'text-sm font-bold text-slate-900';
                price.textContent = new Intl.NumberFormat('en-GB', quote.currency
                    ? { style: 'currency', currency: quote.currency }
                    : { maximumFractionDigits: 2 }).format(quote.price);
                const detail = document.createElement('p');
                detail.className = 'text-xs text-slate-600';
                const change = document.createElement('span');
                change.className = quote.change >= 0 ? 'font-semibold text-emerald-700' : 'font-semibold text-red-700';
                change.textContent = Number.isFinite(quote.change) ? (quote.change > 0 ? '+' : '') + quote.change.toFixed(2) + '%' : '—';
                detail.append(change, ' · ', quote.pe === null ? '—' : quote.pe.toFixed(1) + '×');
                metrics.append(price, detail);
                right.append(metrics);
            }
            right.append(remove);
            row.append(identity, right);
            return row;
        }));
        if (!isPreview && members.watchlistError) message(members.watchlistError);
    }

    async function displayAccount() {
        const user = members.session?.user;
        if (renderedUser === user?.id && displayVersion) {
            renderWatchlist();
            return;
        }
        renderedUser = user?.id;
        renderedTickers = undefined;
        quoteVersion++;
        saveErrors.clear();
        marketQuotes = new Map();
        const version = ++displayVersion;
        for (const id of ['auth-panel', 'workspace', 'owner-link', 'sign-out', 'workspace-retry']) $(id).hidden = true;
        if (!user || mode === 'recovery') {
            $('auth-panel').hidden = false;
            message(needsOwner ? 'Sign in with the owner account to continue.' : '');
            return;
        }
        message(needsOwner ? 'Checking owner access…' : '');
        if (!needsOwner) {
            $('member-identity').textContent = user.email || 'Signed in';
            $('sign-out').hidden = false;
            message('Loading your workspace…');
            let storage;
            try {
                storage = await members.openWorkspaceStorage(user.id);
            } catch (error) {
                if (version === displayVersion) {
                    renderedUser = null;
                    message(error.message);
                    $('workspace-retry').hidden = false;
                }
                return;
            }
            if (version !== displayVersion || members.session?.user.id !== user.id) return;
            $('workspace').hidden = false;
            message('');
            $('workspace-save-status').textContent = '';
            renderWatchlist();
            initialiseWorkspace(user.id, storage, reportSave);
        }
        const { data: owner, error } = await client.rpc('sethiway_is_owner');
        if (version !== displayVersion) return;
        if (!owner || error) {
            if (needsOwner) message(error ? 'Owner access could not be checked. Refresh to try again.' : 'This page is available to the site owner only.');
            return;
        }
        if (!needsOwner) {
            $('owner-link').hidden = false;
            return;
        }
        if (!isPreview) {
            location.replace('admin.html');
            return;
        }
        $('member-identity').textContent = 'Demo member';
        $('preview-controls').hidden = false;
        $('leave-preview').hidden = false;
        $('sign-out').hidden = true;
        $('workspace').hidden = false;
        message('');
        renderWatchlist();
        initialiseWorkspace('member-preview');
    }

    function handleDisplayError() {
        message('The account service is temporarily unavailable. Refresh to try again.');
    }

    async function changeTicker(ticker, save) {
        if (busy) return;
        if (!/^[A-Z0-9.^=-]{1,20}$/.test(ticker)) {
            message('Enter a valid ticker.');
            return;
        }
        busy = true;
        try {
            if (isPreview) {
                previewTickers = previewTickers.filter(item => item !== ticker);
                if (save) previewTickers.push(ticker);
            } else if (members.session) {
                await members.setTicker(ticker, save);
            } else {
                return;
            }
            message(save ? ticker + ' saved.' : ticker + ' removed.');
            if (save) $('workspace-ticker').value = '';
            renderWatchlist();
        } catch (error) {
            message(error.message);
        } finally {
            busy = false;
        }
    }

    document.querySelectorAll('[data-auth-mode]').forEach(link => link.addEventListener('click', () => {
        setMode(link.dataset.authMode);
        message('');
    }));

    authForm.addEventListener('submit', async event => {
        event.preventDefault();
        if (!client || busy) return;
        const email = $('account-email').value.trim();
        const password = $('account-password').value;
        const submit = $('auth-submit');
        const submittedMode = mode;
        busy = submit.disabled = true;
        try {
            let result;
            if (submittedMode === 'signin') {
                result = await client.auth.signInWithPassword({ email, password });
            } else if (submittedMode === 'forgot') {
                result = await client.auth.resetPasswordForEmail(email, { redirectTo: accountUrl + '?recovery=1' });
            } else {
                result = await client.auth.updateUser({ password });
            }
            if (result.error) throw result.error;
            if (submittedMode === 'forgot') {
                setMode('signin');
                message('If an account exists for that address, you’ll receive a reset link.');
            } else if (submittedMode === 'recovery') {
                location.replace(accountUrl);
            }
        } catch (error) {
            message(submittedMode === 'signin'
                ? 'Could not sign in. Check your details and confirm your email first.'
                : error.message || 'Something went wrong. Try again.');
        } finally {
            busy = submit.disabled = false;
            $('account-password').value = '';
        }
    });

    $('workspace-retry').addEventListener('click', () => displayAccount().catch(handleDisplayError));
    $('sign-out').addEventListener('click', async () => {
        $('sign-out').disabled = true;
        $('workspace').inert = true;
        try {
            await Promise.allSettled([...pendingSaves]);
            const { error } = await client.auth.signOut({ scope: 'local' });
            if (error) throw error;
            location.replace(accountUrl);
        } catch {
            message('Could not sign out. Try again.');
        } finally {
            $('sign-out').disabled = false;
            $('workspace').inert = false;
        }
    });
    $('import-watchlist').addEventListener('click', async () => {
        if (busy || isPreview) return;
        busy = true;
        try {
            await members.importGuestWatchlist();
            message('Tickers from this browser added to your account.');
            renderWatchlist();
        } catch (error) {
            message(error.message);
        } finally {
            busy = false;
        }
    });
    $('add-ticker').addEventListener('submit', event => {
        event.preventDefault();
        changeTicker($('workspace-ticker').value.trim().toUpperCase(), true);
    });
    $('empty-preview').addEventListener('click', () => {
        const reset = $('empty-preview').textContent === 'Restore sample tickers';
        previewTickers = reset ? [...sample] : [];
        $('empty-preview').textContent = reset ? 'Show empty state' : 'Restore sample tickers';
        message('');
        renderWatchlist();
    });

    setMode('signin');
    window.addEventListener('sethiway:password-recovery', () => {
        setMode('recovery');
        renderedUser = null;
        if (client) displayAccount().catch(handleDisplayError);
    });
    window.addEventListener('sethiway:member-change', () => {
        if (client) displayAccount().catch(handleDisplayError);
    });
    members.connect().then(connection => {
        client = connection;
        if (params.has('recovery') && members.session) setMode('recovery');
        return displayAccount();
    }).catch(handleDisplayError);
})();
