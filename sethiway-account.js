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
    const sample = ['MSFT', 'VWRP.L', 'AAPL'];

    let mode = 'signin';
    let client;
    let busy = false;
    let renderedUser;
    let displayVersion = 0;
    let previewTickers = [...sample];

    function message(text) {
        status.textContent = text || '';
        status.hidden = !text;
    }

    function setMode(next) {
        mode = next;
        const labels = {
            signin: ['Sign in to SethiWay', 'Find your saved tickers on any device.', 'Sign in'],
            signup: ['Create a SethiWay account', 'Verify your email to start saving tickers.', 'Create account'],
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
        $('account-password').autocomplete = ['signup', 'recovery'].includes(next) ? 'new-password' : 'current-password';
        $('account-password').minLength = ['signup', 'recovery'].includes(next) ? 8 : 0;
        $('account-password').value = '';
        $('auth-links').hidden = next === 'recovery';
        document.querySelectorAll('[data-auth-mode]').forEach(link => {
            link.hidden = next === 'signin' ? link.dataset.authMode === 'signin' : link.dataset.authMode !== 'signin';
        });
    }

    function renderWatchlist() {
        if ($('workspace').hidden) return;
        const tickers = isPreview ? previewTickers : members.readWatchlist();
        $('empty-watchlist').hidden = tickers.length > 0;
        $('import-watchlist').hidden = isPreview || !members.guestTickers().some(ticker => !tickers.includes(ticker));
        $('saved-tickers').replaceChildren(...tickers.map(ticker => {
            const row = document.createElement('li');
            row.className = 'flex items-center justify-between gap-2 py-2';
            const link = document.createElement('a');
            link.textContent = ticker;
            link.href = 'sethistock.html?ticker=' + encodeURIComponent(ticker);
            link.className = 'font-bold text-blue-700';
            const remove = document.createElement('button');
            remove.type = 'button';
            remove.textContent = 'Remove';
            remove.setAttribute('aria-label', 'Remove ' + ticker);
            remove.className = 'text-sm font-semibold text-gray-600';
            remove.addEventListener('click', () => changeTicker(ticker, false));
            row.append(link, remove);
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
        const version = ++displayVersion;
        for (const id of ['auth-panel', 'workspace', 'owner-link']) $(id).hidden = true;
        if (!user || mode === 'recovery') {
            $('auth-panel').hidden = false;
            message(needsOwner ? 'Sign in with the owner account to continue.' : '');
            return;
        }
        message(needsOwner ? 'Checking owner access…' : '');
        if (!needsOwner) {
            $('member-identity').textContent = user.email || 'Signed in';
            $('workspace').hidden = false;
            renderWatchlist();
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
            } else if (submittedMode === 'signup') {
                result = await client.auth.signUp({ email, password, options: { emailRedirectTo: accountUrl } });
            } else if (submittedMode === 'forgot') {
                result = await client.auth.resetPasswordForEmail(email, { redirectTo: accountUrl + '?recovery=1' });
            } else {
                result = await client.auth.updateUser({ password });
            }
            if (result.error) throw result.error;
            if (submittedMode === 'signup' && !result.data.session) {
                setMode('signin');
                message('Check your email for a verification link, then sign in.');
            } else if (submittedMode === 'forgot') {
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

    $('sign-out').addEventListener('click', async () => {
        try {
            const { error } = await client.auth.signOut({ scope: 'local' });
            if (error) throw error;
            location.replace(accountUrl);
        } catch {
            message('Could not sign out. Try again.');
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
