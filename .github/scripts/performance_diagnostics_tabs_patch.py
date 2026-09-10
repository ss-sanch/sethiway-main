from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

# Add compact second-level tab styling inside Performance Diagnostics.
css_anchor = "        .portfolio-lab-panel[hidden] { display: none !important; }"
css_add = """        .portfolio-lab-panel[hidden] { display: none !important; }
        .performance-diagnostic-tab[aria-selected=\"true\"] { background:#eff6ff; color:#1d4ed8; border-color:#bfdbfe; box-shadow:0 1px 2px rgba(37,99,235,.06); }
        .performance-diagnostic-tab[aria-selected=\"false\"] { background:#fff; color:#64748b; border-color:#e5e7eb; }
        .performance-diagnostic-tab[aria-selected=\"false\"]:hover { background:#f8fafc; color:#0f172a; }
        .performance-diagnostic-panel[hidden] { display:none !important; }"""
if css_anchor not in text:
    raise SystemExit('Portfolio Lab CSS anchor not found')
text = text.replace(css_anchor, css_add, 1)

# Track the selected sub-view.
state_anchor = "    let currentPortfolioLabTab = null;"
state_replace = """    let currentPortfolioLabTab = null;
    let currentPerformanceDiagnostic = 'attribution';"""
if state_anchor not in text:
    raise SystemExit('Portfolio Lab state anchor not found')
text = text.replace(state_anchor, state_replace, 1)

# Replace Performance Diagnostics loading with sub-view-aware rendering.
old_ensure = """            if (tab === 'performance') {
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
            } else if (tab === 'risk') {"""
new_ensure = """            if (tab === 'performance') {
                await ensurePerformanceDiagnosticData(currentPerformanceDiagnostic);
            } else if (tab === 'risk') {"""
if old_ensure not in text:
    raise SystemExit('Performance lazy-load block not found')
text = text.replace(old_ensure, new_ensure, 1)

# Build the second-level Performance Diagnostics switcher after moving sections into the lab.
insert_anchor = """    function initialisePortfolioLab() {
        Object.entries(portfolioLabMap).forEach(([tab, ids]) => {
            const panel = document.getElementById(`lab-panel-${tab}`);
            ids.forEach(id => moveSectionIntoLab(id, panel));
        });
        closePortfolioLab();
        applyPortfolioLabHash(false);
    }
"""
replacement = r'''    const performanceDiagnosticMap = {
        attribution: 'attribution',
        benchmark: 'benchmark',
        drawdown: 'drawdown',
        efficiency: 'analytics'
    };

    const performanceDiagnosticQuestions = {
        attribution: 'What actually drove the portfolio return?',
        benchmark: 'Did active management add value versus the benchmark?',
        drawdown: 'How difficult was the path to the return?',
        efficiency: 'How efficiently and consistently were returns earned?'
    };

    function initialisePerformanceDiagnostics() {
        const panel = document.getElementById('lab-panel-performance');
        if (!panel || panel.querySelector('[data-performance-diagnostic-tabs]')) return;

        const chooser = document.createElement('div');
        chooser.className = 'portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-3 md:p-4 mb-4';
        chooser.setAttribute('data-performance-diagnostic-tabs', '');
        chooser.innerHTML = `
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
                <div>
                    <p class="text-[10px] font-black uppercase tracking-widest text-blue-600">Performance Diagnostics</p>
                    <p id="performance-diagnostic-question" class="text-sm font-bold text-gray-700 mt-1">${performanceDiagnosticQuestions.attribution}</p>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 lg:min-w-[620px]" role="tablist" aria-label="Performance diagnostic views">
                    <button type="button" class="performance-diagnostic-tab rounded-lg border px-3 py-2 text-left transition" data-performance-diagnostic="attribution" aria-selected="true" onclick="setPerformanceDiagnostic('attribution')"><span class="block text-xs font-black">Attribution</span><span class="block text-[9px] opacity-70 mt-0.5">Return drivers</span></button>
                    <button type="button" class="performance-diagnostic-tab rounded-lg border px-3 py-2 text-left transition" data-performance-diagnostic="benchmark" aria-selected="false" onclick="setPerformanceDiagnostic('benchmark')"><span class="block text-xs font-black">Benchmark</span><span class="block text-[9px] opacity-70 mt-0.5">Relative behaviour</span></button>
                    <button type="button" class="performance-diagnostic-tab rounded-lg border px-3 py-2 text-left transition" data-performance-diagnostic="drawdown" aria-selected="false" onclick="setPerformanceDiagnostic('drawdown')"><span class="block text-xs font-black">Drawdown</span><span class="block text-[9px] opacity-70 mt-0.5">Path & rolling risk</span></button>
                    <button type="button" class="performance-diagnostic-tab rounded-lg border px-3 py-2 text-left transition" data-performance-diagnostic="efficiency" aria-selected="false" onclick="setPerformanceDiagnostic('efficiency')"><span class="block text-xs font-black">Return Efficiency</span><span class="block text-[9px] opacity-70 mt-0.5">Sharpe · Sortino · tails</span></button>
                </div>
            </div>`;
        panel.prepend(chooser);

        Object.entries(performanceDiagnosticMap).forEach(([key, sectionId]) => {
            const intro = document.getElementById(sectionId);
            const content = intro?.nextElementSibling;
            if (!intro || !content) return;
            const wrapper = document.createElement('div');
            wrapper.className = 'performance-diagnostic-panel';
            wrapper.dataset.performanceDiagnosticPanel = key;
            wrapper.hidden = key !== currentPerformanceDiagnostic;
            panel.insertBefore(wrapper, intro);
            wrapper.appendChild(intro);
            wrapper.appendChild(content);
        });
    }

    async function ensurePerformanceDiagnosticData(view) {
        if (!performanceDiagnosticMap[view]) view = 'attribution';
        if (view === 'attribution') {
            try {
                await loadAttributionOnDemand();
                if (portfolioData.dates.length && attributionLoaded) renderAttribution();
            } catch (error) {
                console.error('SethiPortfolio attribution lazy load failed:', error);
                const reconciliation = document.getElementById('attribution-reconciliation');
                if (reconciliation) reconciliation.textContent = `Attribution API: ${error.message || 'temporarily unavailable'}`;
            }
        } else if (!portfolioData.dates.length) {
            return;
        } else if (view === 'benchmark') {
            renderBenchmarkAnalytics();
        } else if (view === 'drawdown') {
            renderDrawdownRolling();
        } else if (view === 'efficiency') {
            renderAnalytics();
        }
    }

    function setPerformanceDiagnostic(view, updateHash=false) {
        if (!performanceDiagnosticMap[view]) view = 'attribution';
        currentPerformanceDiagnostic = view;
        document.querySelectorAll('[data-performance-diagnostic-panel]').forEach(panel => {
            panel.hidden = panel.dataset.performanceDiagnosticPanel !== view;
        });
        document.querySelectorAll('[data-performance-diagnostic]').forEach(button => {
            button.setAttribute('aria-selected', button.dataset.performanceDiagnostic === view ? 'true' : 'false');
        });
        const question = document.getElementById('performance-diagnostic-question');
        if (question) question.textContent = performanceDiagnosticQuestions[view];
        if (updateHash) history.replaceState(null, '', `#${performanceDiagnosticMap[view]}`);
        ensurePerformanceDiagnosticData(view).finally(() => {
            setTimeout(() => {
                document.querySelectorAll(`[data-performance-diagnostic-panel="${view}"] .js-plotly-plot`).forEach(plot => {
                    try { Plotly.Plots.resize(plot); } catch (_) {}
                });
                window.dispatchEvent(new Event('resize'));
            }, 50);
        });
    }

    function initialisePortfolioLab() {
        Object.entries(portfolioLabMap).forEach(([tab, ids]) => {
            const panel = document.getElementById(`lab-panel-${tab}`);
            ids.forEach(id => moveSectionIntoLab(id, panel));
        });
        initialisePerformanceDiagnostics();
        closePortfolioLab();
        applyPortfolioLabHash(false);
    }
'''
if insert_anchor not in text:
    raise SystemExit('Initialise Portfolio Lab block not found')
text = text.replace(insert_anchor, replacement, 1)

# Opening Performance Diagnostics should select its current sub-view and render only that view.
old_set_tab = """        if (updateHash) history.replaceState(null, '', `#lab-${tab}`);
        if (scrollToLab) document.getElementById('portfolio-lab')?.scrollIntoView({behavior:'smooth', block:'start'});
        ensurePortfolioLabData(tab);
    }
"""
new_set_tab = """        if (updateHash) history.replaceState(null, '', `#lab-${tab}`);
        if (scrollToLab) document.getElementById('portfolio-lab')?.scrollIntoView({behavior:'smooth', block:'start'});
        if (tab === 'performance') setPerformanceDiagnostic(currentPerformanceDiagnostic, false);
        else ensurePortfolioLabData(tab);
    }
"""
if old_set_tab not in text:
    raise SystemExit('setPortfolioLabTab tail not found')
text = text.replace(old_set_tab, new_set_tab, 1)

# Deep links into a performance diagnostic open the matching sub-view.
old_hash = """        setPortfolioLabTab(tab, false, false);
        const rawId = hash.replace(/^#/, '');
        const rawTarget = document.getElementById(rawId);"""
new_hash = """        const rawId = hash.replace(/^#/, '');
        if (tab === 'performance') {
            const diagnostic = Object.entries(performanceDiagnosticMap).find(([, sectionId]) => sectionId === rawId)?.[0];
            if (diagnostic) currentPerformanceDiagnostic = diagnostic;
        }
        setPortfolioLabTab(tab, false, false);
        const rawTarget = document.getElementById(rawId);"""
if old_hash not in text:
    raise SystemExit('Portfolio Lab hash block not found')
text = text.replace(old_hash, new_hash, 1)

# Range changes only rerender the active Performance Diagnostics sub-view.
old_range = """        if (currentPortfolioLabTab === 'performance') {
            if (attributionLoaded) renderAttribution();
            renderBenchmarkAnalytics();
            renderDrawdownRolling();
            renderAnalytics();
        }
        if (currentPortfolioLabTab === 'fx' && fxAnalyticsData) renderFxHistory();"""
new_range = """        if (currentPortfolioLabTab === 'performance') {
            if (currentPerformanceDiagnostic === 'attribution' && attributionLoaded) renderAttribution();
            else if (currentPerformanceDiagnostic === 'benchmark') renderBenchmarkAnalytics();
            else if (currentPerformanceDiagnostic === 'drawdown') renderDrawdownRolling();
            else if (currentPerformanceDiagnostic === 'efficiency') renderAnalytics();
        }
        if (currentPortfolioLabTab === 'fx' && fxAnalyticsData) renderFxHistory();"""
if old_range not in text:
    raise SystemExit('Range lazy render block not found')
text = text.replace(old_range, new_range, 1)

path.write_text(text)
