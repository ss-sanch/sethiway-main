from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

# Portfolio Lab should start closed: chooser visible, all workspaces hidden.
text = text.replace(
    '<p id="portfolio-lab-context" class="text-sm text-gray-500 mt-1">Performance diagnostics brings attribution, benchmark behaviour, drawdowns and return efficiency into one focused view.</p>',
    '<p id="portfolio-lab-context" class="text-sm text-gray-500 mt-1">Select a workspace below. Advanced analytics are loaded only when you open them, keeping the main portfolio view faster and focused.</p>',
    1,
)
text = text.replace('data-lab-tab="performance" aria-selected="true"', 'data-lab-tab="performance" aria-selected="false"', 1)
text = text.replace(
    '<div id="lab-panel-performance" class="portfolio-lab-panel" data-lab-panel="performance"></div>',
    '<div id="lab-panel-performance" class="portfolio-lab-panel hidden" data-lab-panel="performance" hidden></div>',
    1,
)
for tab in ('risk', 'fx', 'whatif'):
    text = text.replace(
        f'<div id="lab-panel-{tab}" class="portfolio-lab-panel" data-lab-panel="{tab}" hidden></div>',
        f'<div id="lab-panel-{tab}" class="portfolio-lab-panel hidden" data-lab-panel="{tab}" hidden></div>',
        1,
    )

# Keep tiny pie labels safely within the composition card.
old_pie = """        Plotly.react('weights-chart', [{labels:chartLabels,values:chartValues,type:'pie',hole:.62,textinfo:'label+percent',hovertemplate:'%{label}: %{value:.2f}%<extra></extra>'}], {
            margin:{t:10,r:10,l:10,b:10}, paper_bgcolor:'rgba(0,0,0,0)', showlegend:false
        }, {displayModeBar:false,responsive:true});"""
new_pie = """        Plotly.react('weights-chart', [{labels:chartLabels,values:chartValues,type:'pie',hole:.62,textinfo:'label+percent',textposition:'auto',automargin:true,domain:{x:[0.03,0.88],y:[0.03,0.97]},hovertemplate:'%{label}: %{value:.2f}%<extra></extra>'}], {
            margin:{t:12,r:44,l:18,b:12}, paper_bgcolor:'rgba(0,0,0,0)', showlegend:false,
            uniformtext:{minsize:10,mode:'show'}
        }, {displayModeBar:false,responsive:true});"""
if old_pie not in text:
    raise SystemExit('Holdings pie anchor not found')
text = text.replace(old_pie, new_pie, 1)

# Add progressive-loading state.
old_globals = """    let portfolioSnapshot = null;
    let journalEntries = [];
    let currentRange = 'SI';"""
new_globals = """    let portfolioSnapshot = null;
    let journalEntries = [];
    let attributionLoaded = false;
    let decisionsLoaded = false;
    let decisionsLoading = false;
    const portfolioLabLoading = new Set();
    let currentRange = 'SI';"""
if old_globals not in text:
    raise SystemExit('Global state anchor not found')
text = text.replace(old_globals, new_globals, 1)

# Only refresh analytics that are actually visible.
old_range = """        renderPerformance();
        renderAttribution();
        renderBenchmarkAnalytics();
        renderDrawdownRolling();
        renderAnalytics();
        renderFxHistory();"""
new_range = """        renderPerformance();
        if (currentPortfolioLabTab === 'performance') {
            if (attributionLoaded) renderAttribution();
            renderBenchmarkAnalytics();
            renderDrawdownRolling();
            renderAnalytics();
        }
        if (currentPortfolioLabTab === 'fx' && fxAnalyticsData) renderFxHistory();"""
if old_range not in text:
    raise SystemExit('Range render anchor not found')
text = text.replace(old_range, new_range, 1)

# Replace Portfolio Lab controller with closed-by-default + on-demand loading.
start = text.index('    const portfolioLabMap = {')
end = text.index('\n\n    function fxMoney(value) {', start)
new_lab = r'''    const portfolioLabMap = {
        performance: ['attribution', 'benchmark', 'drawdown', 'analytics'],
        risk: ['exposure', 'risk'],
        fx: ['fx'],
        whatif: ['rebalance']
    };
    const portfolioLabCopy = {
        performance: 'Performance Diagnostics is open. Attribution is fetched on demand; benchmark, drawdown and efficiency views reuse the performance series already loaded above.',
        risk: 'Risk & Exposure is open. Exposure classification and Euler risk are fetched only for this workspace.',
        fx: 'FX is open. Translation, sterling sensitivity and currency history are fetched only for this workspace.',
        whatif: 'What-If is open. The current holdings are reused locally; the backend is called only after you press Analyse Rebalance.'
    };
    const portfolioLabDefaultCopy = 'Select a workspace below. Advanced analytics are loaded only when you open them, keeping the main portfolio view faster and focused.';
    let currentPortfolioLabTab = null;

    function moveSectionIntoLab(sectionId, panel) {
        const intro = document.getElementById(sectionId);
        if (!intro || !panel) return;
        const content = intro.nextElementSibling;
        panel.appendChild(intro);
        if (content) panel.appendChild(content);
    }

    async function loadAttributionOnDemand() {
        if (attributionLoaded) return;
        const response = await fetch(`${API_BASE}/${PORTFOLIO_SLUG}/attribution`);
        if (!response.ok) {
            let detail = `Attribution request failed (${response.status})`;
            try { const body = await response.json(); detail = body.detail || detail; } catch (_) {}
            throw new Error(detail);
        }
        attributionData = await response.json() || { periods: {} };
        attributionLoaded = true;
    }

    async function ensurePortfolioLabData(tab) {
        if (!portfolioLabMap[tab] || portfolioLabLoading.has(tab)) return;
        portfolioLabLoading.add(tab);
        try {
            if (tab === 'performance') {
                try {
                    await loadAttributionOnDemand();
                } catch (error) {
                    console.error('SethiPortfolio attribution lazy load failed:', error);
                    const reconciliation = document.getElementById('attribution-reconciliation');
                    if (reconciliation) reconciliation.textContent = `Attribution API: ${error.message || 'temporarily unavailable'}`;
                }
                if (portfolioData.dates.length) {
                    if (attributionLoaded) renderAttribution();
                    renderBenchmarkAnalytics();
                    renderDrawdownRolling();
                    renderAnalytics();
                }
            } else if (tab === 'risk') {
                await Promise.all([
                    exposureData ? Promise.resolve() : loadExposureMap(),
                    riskAnalyticsData ? Promise.resolve() : loadRiskAnalytics()
                ]);
            } else if (tab === 'fx') {
                if (!fxAnalyticsData) await loadFxAnalytics();
                else renderFxHistory();
            } else if (tab === 'whatif') {
                if (portfolioSnapshot) initRebalanceEditor(portfolioSnapshot);
                else document.getElementById('rebalance-status').textContent = 'Loading the current portfolio before the simulator can be initialised…';
            }
        } finally {
            portfolioLabLoading.delete(tab);
            setTimeout(() => {
                document.querySelectorAll(`#lab-panel-${tab} .js-plotly-plot`).forEach(plot => {
                    try { Plotly.Plots.resize(plot); } catch (_) {}
                });
                window.dispatchEvent(new Event('resize'));
            }, 60);
        }
    }

    function closePortfolioLab() {
        currentPortfolioLabTab = null;
        document.querySelectorAll('[data-lab-panel]').forEach(panel => {
            panel.hidden = true;
            panel.classList.add('hidden');
        });
        document.querySelectorAll('[data-lab-tab]').forEach(button => button.setAttribute('aria-selected', 'false'));
        const context = document.getElementById('portfolio-lab-context');
        if (context) context.textContent = portfolioLabDefaultCopy;
    }

    function initialisePortfolioLab() {
        Object.entries(portfolioLabMap).forEach(([tab, ids]) => {
            const panel = document.getElementById(`lab-panel-${tab}`);
            ids.forEach(id => moveSectionIntoLab(id, panel));
        });
        closePortfolioLab();
        applyPortfolioLabHash(false);
    }

    function setPortfolioLabTab(tab, updateHash=true, scrollToLab=false) {
        if (!portfolioLabMap[tab]) return;
        currentPortfolioLabTab = tab;
        document.querySelectorAll('[data-lab-panel]').forEach(panel => {
            const active = panel.dataset.labPanel === tab;
            panel.hidden = !active;
            panel.classList.toggle('hidden', !active);
        });
        document.querySelectorAll('[data-lab-tab]').forEach(button => {
            button.setAttribute('aria-selected', button.dataset.labTab === tab ? 'true' : 'false');
        });
        const context = document.getElementById('portfolio-lab-context');
        if (context) context.textContent = portfolioLabCopy[tab];
        if (updateHash) history.replaceState(null, '', `#lab-${tab}`);
        if (scrollToLab) document.getElementById('portfolio-lab')?.scrollIntoView({behavior:'smooth', block:'start'});
        ensurePortfolioLabData(tab);
    }

    function labTabForHash(hash) {
        const value = String(hash || '').replace(/^#/, '');
        if (value.startsWith('lab-')) {
            const tab = value.slice(4);
            return portfolioLabMap[tab] ? tab : null;
        }
        for (const [tab, ids] of Object.entries(portfolioLabMap)) {
            if (ids.includes(value)) return tab;
        }
        return null;
    }

    function applyPortfolioLabHash(animate=true) {
        const hash = window.location.hash || '';
        const tab = labTabForHash(hash);
        if (!tab) {
            closePortfolioLab();
            return;
        }
        setPortfolioLabTab(tab, false, false);
        const rawId = hash.replace(/^#/, '');
        const rawTarget = document.getElementById(rawId);
        const target = rawId.startsWith('lab-')
            ? document.getElementById('portfolio-lab')
            : (rawTarget?.nextElementSibling || rawTarget);
        setTimeout(() => target?.scrollIntoView({behavior: animate ? 'smooth' : 'auto', block:'start'}), 30);
    }

    window.addEventListener('hashchange', () => applyPortfolioLabHash(true));'''
text = text[:start] + new_lab + text[end:]

# Defer journal + change log until the user approaches Investment Decisions.
insert_after = """    function renderTransactions(transactions) {
"""
idx = text.index(insert_after)
# place helper after the complete renderTransactions function by anchoring the loading-state declaration
anchor_loading = "\n    let loadingTimer;"
loading_idx = text.index(anchor_loading, idx)
decision_helpers = r'''

    async function loadInvestmentDecisions() {
        if (decisionsLoaded || decisionsLoading) return;
        decisionsLoading = true;
        try {
            const [journalRes, transactionsRes] = await Promise.all([
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/journal?limit=100`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/transactions`)
            ]);
            if (!journalRes.ok || !transactionsRes.ok) throw new Error('Investment Decisions data request failed.');
            const [journalPayload, transactionPayload] = await Promise.all([journalRes.json(), transactionsRes.json()]);
            renderJournal(journalPayload.journal);
            renderTransactions(transactionPayload.transactions);
            decisionsLoaded = true;
        } catch (error) {
            console.error('SethiPortfolio Investment Decisions lazy load failed:', error);
            document.getElementById('journal-count').textContent = 'Notes unavailable';
            document.getElementById('journal-list').innerHTML = '<div class="rounded-xl border border-dashed border-gray-200 p-7 text-sm text-gray-400 text-center">Unable to load investment notes right now.</div>';
            document.getElementById('change-log').innerHTML = '<div class="p-6 text-sm text-gray-400 text-center">Unable to load portfolio changes right now.</div>';
        } finally {
            decisionsLoading = false;
        }
    }

    function setupDeferredDecisionLoading() {
        const decisions = document.getElementById('decisions');
        if (!decisions) return;
        if (window.location.hash === '#decisions' || window.location.hash === '#journal' || window.location.hash === '#changes') {
            loadInvestmentDecisions();
            return;
        }
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver(entries => {
                if (entries.some(entry => entry.isIntersecting)) {
                    observer.disconnect();
                    loadInvestmentDecisions();
                }
            }, {rootMargin:'900px 0px'});
            observer.observe(decisions);
        } else {
            setTimeout(loadInvestmentDecisions, 1600);
        }
    }
'''
text = text[:loading_idx] + decision_helpers + text[loading_idx:]

# Loading overlay should cover only the critical Performance/Holdings cards.
old_start_loading = """    function startLoadingState() {
        const cards = document.querySelectorAll('main .portfolio-data-card');
        cards.forEach(card => card.classList.add('loading-card'));"""
new_start_loading = """    function startLoadingState() {
        const cards = document.querySelectorAll('#performance + section .portfolio-data-card, #holdings + section .portfolio-data-card');
        cards.forEach(card => card.classList.add('loading-card'));"""
if old_start_loading not in text:
    raise SystemExit('Loading state anchor not found')
text = text.replace(old_start_loading, new_start_loading, 1)

# Critical path: portfolio snapshot + performance only. Everything else is lazy.
old_loader = r'''    async function loadPortfolio() {
        startLoadingState();
        try {
            const [portfolioRes, performanceRes, attributionRes, journalRes, transactionsRes] = await Promise.all([
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/performance`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/attribution`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/journal?limit=100`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/transactions`)
            ]);
            if (![portfolioRes,performanceRes,attributionRes,journalRes,transactionsRes].every(r=>r.ok)) throw new Error('One or more portfolio API requests failed.');
            const [portfolioPayload, performance, attributionPayload, journalPayload, transactionPayload] = await Promise.all([
                portfolioRes.json(), performanceRes.json(), attributionRes.json(), journalRes.json(), transactionsRes.json()
            ]);
            attributionData = attributionPayload || { periods: {} };
            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;
            portfolioSnapshot = snapshot;
            const sp500 = performance.benchmarks['^SP500TR']?.values || [];
            const nasdaq = performance.benchmarks['QQQ']?.values || [];
            const vwrl = performance.benchmarks['VWRL.L']?.values || [];
            portfolioData = {dates:performance.dates || [], portfolio:performance.portfolio || [], sp500, nasdaq, vwrl};

            document.getElementById('portfolio-name').textContent = info.name;
            document.getElementById('portfolio-description').textContent = info.description || '';
            document.getElementById('portfolio-value').textContent = fmtGBP(snapshot.portfolio_value);
            const totalReturn = (snapshot.portfolio_value / info.initial_capital - 1) * 100;
            document.getElementById('total-return').textContent = fmtPct(totalReturn);
            document.getElementById('total-return').className = `text-xl font-black mt-0.5 ${totalReturn >= 0 ? 'text-emerald-700' : 'text-red-600'}`;
            document.getElementById('since-date').textContent = new Date(`${info.inception_date}T00:00:00`).toLocaleDateString('en-GB',{month:'short',year:'numeric'});
            const spReturn = sp500.length ? sp500.at(-1)-100 : 0;
            document.getElementById('vs-sp500').textContent = fmtPp(totalReturn-spReturn);
            document.getElementById('holdings-status').textContent = `Priced ${new Date(snapshot.pricing_timestamp).toLocaleString('en-GB')}`;

            renderPerformance(); renderAttribution(); renderBenchmarkAnalytics(); renderDrawdownRolling(); renderHoldings(snapshot); initRebalanceEditor(snapshot); renderAnalytics();
            renderJournal(journalPayload.journal); renderTransactions(transactionPayload.transactions);
        } catch (error) {
            console.error('SethiPortfolio load failed:', error);
            document.getElementById('data-status').textContent = 'Live data temporarily unavailable · please retry shortly';
            document.getElementById('performance-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load live portfolio data.</div>';
            document.getElementById('attribution-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load performance attribution.</div>';
            document.getElementById('attribution-table').innerHTML = '<tr><td colspan="4" class="px-4 py-8 text-center text-gray-400">Unable to load attribution.</td></tr>';
            document.getElementById('benchmark-active-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load benchmark analytics.</div>';
            document.getElementById('benchmark-regression-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load benchmark regression.</div>';
            document.getElementById('drawdown-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load drawdown history.</div>';
            document.getElementById('rolling-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load rolling analytics.</div>';
            document.getElementById('holdings-table').innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">Unable to load holdings.</td></tr>';
        } finally {
            finishLoadingState();
        }
    }

    initialisePortfolioLab();
    loadPortfolio();
    loadExposureMap();
    loadFxAnalytics();
    loadRiskAnalytics();'''
new_loader = r'''    async function loadPortfolio() {
        startLoadingState();
        try {
            const [portfolioRes, performanceRes] = await Promise.all([
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}`),
                fetch(`${API_BASE}/${PORTFOLIO_SLUG}/performance`)
            ]);
            if (!portfolioRes.ok || !performanceRes.ok) throw new Error('Core portfolio data request failed.');
            const [portfolioPayload, performance] = await Promise.all([portfolioRes.json(), performanceRes.json()]);
            const info = portfolioPayload.portfolio, snapshot = portfolioPayload.snapshot;
            portfolioSnapshot = snapshot;
            const sp500 = performance.benchmarks['^SP500TR']?.values || [];
            const nasdaq = performance.benchmarks['QQQ']?.values || [];
            const vwrl = performance.benchmarks['VWRL.L']?.values || [];
            portfolioData = {dates:performance.dates || [], portfolio:performance.portfolio || [], sp500, nasdaq, vwrl};

            document.getElementById('portfolio-name').textContent = info.name;
            document.getElementById('portfolio-description').textContent = info.description || '';
            document.getElementById('portfolio-value').textContent = fmtGBP(snapshot.portfolio_value);
            const totalReturn = (snapshot.portfolio_value / info.initial_capital - 1) * 100;
            document.getElementById('total-return').textContent = fmtPct(totalReturn);
            document.getElementById('total-return').className = `text-xl font-black mt-0.5 ${totalReturn >= 0 ? 'text-emerald-700' : 'text-red-600'}`;
            document.getElementById('since-date').textContent = new Date(`${info.inception_date}T00:00:00`).toLocaleDateString('en-GB',{month:'short',year:'numeric'});
            const spReturn = sp500.length ? sp500.at(-1)-100 : 0;
            document.getElementById('vs-sp500').textContent = fmtPp(totalReturn-spReturn);
            document.getElementById('holdings-status').textContent = `Priced ${new Date(snapshot.pricing_timestamp).toLocaleString('en-GB')}`;

            renderPerformance();
            renderHoldings(snapshot);
            if (currentPortfolioLabTab) ensurePortfolioLabData(currentPortfolioLabTab);
        } catch (error) {
            console.error('SethiPortfolio core load failed:', error);
            document.getElementById('data-status').textContent = 'Live data temporarily unavailable · please retry shortly';
            document.getElementById('performance-chart').innerHTML = '<div class="h-full flex items-center justify-center text-sm text-gray-400">Unable to load live portfolio data.</div>';
            document.getElementById('holdings-table').innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-gray-400">Unable to load holdings.</td></tr>';
        } finally {
            finishLoadingState();
        }
    }

    initialisePortfolioLab();
    setupDeferredDecisionLoading();
    loadPortfolio();'''
if old_loader not in text:
    raise SystemExit('Core loader block not found')
text = text.replace(old_loader, new_loader, 1)

path.write_text(text)
