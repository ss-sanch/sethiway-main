from pathlib import Path

path = Path('sethiportfolio.html')
text = path.read_text()

if 'id="portfolio-lab"' in text:
    raise SystemExit('Portfolio Lab already present')

text = text.replace(
    '#performance, #attribution, #benchmark, #drawdown, #holdings, #exposure, #fx, #risk, #rebalance, #analytics, #decisions, #journal, #changes { scroll-margin-top: 8rem; }',
    '#performance, #holdings, #portfolio-lab, #decisions, #attribution, #benchmark, #drawdown, #exposure, #fx, #risk, #rebalance, #analytics, #journal, #changes { scroll-margin-top: 8rem; }\n'
    '        .portfolio-lab-panel .section-intro { margin: 1.25rem 0 .85rem; padding-top: 1rem; grid-template-columns: fit-content(300px) minmax(0,1fr); }\n'
    '        .portfolio-lab-panel .section-intro:first-child { margin-top: 0; padding-top: 0; border-top: 0; }\n'
    '        .portfolio-lab-panel .section-intro h2 { font-size: 1.35rem; }\n'
    '        .portfolio-lab-panel .section-overview { padding: .8rem 1rem; font-size: .8rem; }\n'
    '        .portfolio-lab-tab[aria-selected="true"] { background: #111827; color: #fff; border-color: #111827; box-shadow: 0 1px 2px rgba(15,23,42,.08); }\n'
    '        .portfolio-lab-tab[aria-selected="false"] { background: #fff; color: #475569; border-color: #e5e7eb; }\n'
    '        .portfolio-lab-tab[aria-selected="false"]:hover { background: #f8fafc; color: #0f172a; }\n'
    '        .portfolio-lab-panel[hidden] { display: none !important; }',
    1,
)

old_nav = '''        <div class="max-w-[1500px] mx-auto px-5 md:px-8 flex flex-wrap items-center justify-between gap-x-3 sm:gap-x-6">
            <a href="index.html" class="flex items-center py-3 shrink-0" aria-label="SethiWay home">
                <img src="logo.png" alt="SethiWay" class="h-6 sm:h-10 w-auto invert">
            </a>
            <div class="portfolio-section-links order-last xl:order-none w-full xl:w-auto flex items-center gap-6 overflow-x-auto whitespace-nowrap text-sm font-bold text-gray-600 pb-3 xl:pb-0">
                <a href="#performance" class="hover:text-blue-600">Performance</a>
                <a href="#attribution" class="hover:text-blue-600">Attribution</a>
                <a href="#benchmark" class="hover:text-blue-600">Benchmark</a>
                <a href="#drawdown" class="hover:text-blue-600">Drawdown</a>
                <a href="#holdings" class="hover:text-blue-600">Holdings</a>
                <a href="#exposure" class="hover:text-blue-600">Exposure</a>
                <a href="#fx" class="hover:text-blue-600">FX</a>
                <a href="#risk" class="hover:text-blue-600">Risk</a>
                <a href="#rebalance" class="hover:text-blue-600">What-if</a>
                <a href="#analytics" class="hover:text-blue-600">Analytics</a>
                <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>
            </div>
            <div class="flex items-center gap-2 shrink-0">
                <a href="sethiportfolio-admin.html" class="px-3 py-2.5 border border-gray-200 bg-white text-gray-700 text-sm font-bold rounded-lg hover:border-blue-300 hover:text-blue-700 hover:bg-blue-50 transition shadow-sm" title="Open the protected SethiPortfolio control panel">Portfolio Admin</a>
                <a href="index.html" class="px-4 py-2.5 bg-gray-900 text-white text-sm font-bold rounded-lg hover:bg-gray-800 transition shadow-sm">Back to Hub</a>
            </div>
        </div>'''
new_nav = '''        <div class="max-w-[1500px] mx-auto px-5 md:px-8">
            <div class="flex items-center gap-4 lg:gap-6 min-w-0">
                <a href="index.html" class="flex items-center py-3 shrink-0" aria-label="SethiWay home">
                    <img src="logo.png" alt="SethiWay" class="h-6 sm:h-10 w-auto invert">
                </a>
                <div class="portfolio-section-links hidden lg:flex flex-1 items-center justify-end gap-5 xl:gap-7 whitespace-nowrap text-sm font-bold text-gray-600 min-w-0">
                    <a href="#performance" class="hover:text-blue-600">Performance</a>
                    <a href="#holdings" class="hover:text-blue-600">Holdings</a>
                    <a href="#portfolio-lab" class="hover:text-blue-600">Portfolio Lab</a>
                    <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>
                </div>
                <div class="flex items-center gap-2 shrink-0 ml-auto lg:ml-0">
                    <a href="sethiportfolio-admin.html" class="px-3 py-2.5 border border-gray-200 bg-white text-gray-700 text-xs xl:text-sm font-bold rounded-lg hover:border-blue-300 hover:text-blue-700 hover:bg-blue-50 transition shadow-sm whitespace-nowrap" title="Open the protected SethiPortfolio control panel">Portfolio Admin</a>
                    <a href="index.html" class="px-3 xl:px-4 py-2.5 bg-gray-900 text-white text-xs xl:text-sm font-bold rounded-lg hover:bg-gray-800 transition shadow-sm whitespace-nowrap">Back to Hub</a>
                </div>
            </div>
            <div class="lg:hidden flex items-center gap-5 overflow-x-auto whitespace-nowrap text-xs font-black text-gray-600 pb-3">
                <a href="#performance" class="hover:text-blue-600">Performance</a>
                <a href="#holdings" class="hover:text-blue-600">Holdings</a>
                <a href="#portfolio-lab" class="hover:text-blue-600">Portfolio Lab</a>
                <a href="#decisions" class="hover:text-blue-600">Investment Decisions</a>
            </div>
        </div>'''
if old_nav not in text:
    raise SystemExit('Navigation anchor not found')
text = text.replace(old_nav, new_nav, 1)

lab_shell = r'''

            <!-- PORTFOLIO LAB -->
            <div id="portfolio-lab" class="section-intro"><h2>Portfolio Lab</h2><div class="section-overview"><strong>Deeper analysis, one workspace</strong>Keep the main portfolio view focused on performance and holdings, then open the analytical toolset you need without scrolling through every model at once.</div></div>
            <section id="portfolio-lab-shell" class="space-y-4">
                <div class="portfolio-data-card bg-white border border-gray-200 rounded-2xl shadow-sm p-4 md:p-5">
                    <div class="flex flex-col xl:flex-row xl:items-end xl:justify-between gap-4">
                        <div>
                            <p class="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Analysis Workspace</p>
                            <h3 class="text-xl md:text-2xl font-black text-gray-900">Choose the question you want to answer</h3>
                            <p id="portfolio-lab-context" class="text-sm text-gray-500 mt-1">Performance diagnostics brings attribution, benchmark behaviour, drawdowns and return efficiency into one focused view.</p>
                        </div>
                        <span class="self-start xl:self-auto text-[10px] font-black uppercase tracking-wider rounded-full bg-slate-50 text-slate-600 border border-slate-200 px-3 py-1.5">4 analysis workspaces</span>
                    </div>
                    <div class="grid grid-cols-2 xl:grid-cols-4 gap-2 mt-4" role="tablist" aria-label="Portfolio Lab tools">
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="performance" aria-selected="true" onclick="setPortfolioLabTab('performance')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">01</span><span class="block text-sm font-black mt-0.5">Performance Diagnostics</span><span class="block text-[10px] opacity-70 mt-1">Attribution · benchmark · drawdown · efficiency</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="risk" aria-selected="false" onclick="setPortfolioLabTab('risk')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">02</span><span class="block text-sm font-black mt-0.5">Risk &amp; Exposure</span><span class="block text-[10px] opacity-70 mt-1">Sector · geography · concentration · Euler risk</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="fx" aria-selected="false" onclick="setPortfolioLabTab('fx')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">03</span><span class="block text-sm font-black mt-0.5">FX</span><span class="block text-[10px] opacity-70 mt-1">Translation · sterling sensitivity · currency paths</span></button>
                        <button type="button" class="portfolio-lab-tab rounded-xl border px-3 py-3 text-left transition" data-lab-tab="whatif" aria-selected="false" onclick="setPortfolioLabTab('whatif')"><span class="block text-[9px] uppercase tracking-wider font-black opacity-70">04</span><span class="block text-sm font-black mt-0.5">What-If</span><span class="block text-[10px] opacity-70 mt-1">Reweight the live book without placing a trade</span></button>
                    </div>
                </div>
                <div id="lab-panel-performance" class="portfolio-lab-panel" data-lab-panel="performance"></div>
                <div id="lab-panel-risk" class="portfolio-lab-panel" data-lab-panel="risk" hidden></div>
                <div id="lab-panel-fx" class="portfolio-lab-panel" data-lab-panel="fx" hidden></div>
                <div id="lab-panel-whatif" class="portfolio-lab-panel" data-lab-panel="whatif" hidden></div>
            </section>
'''
anchor = '            <!-- PORTFOLIO EXPOSURE MAP -->'
if anchor not in text:
    raise SystemExit('Exposure anchor not found')
text = text.replace(anchor, lab_shell + '\n\n' + anchor, 1)

lab_js = r'''

    const portfolioLabMap = {
        performance: ['attribution', 'benchmark', 'drawdown', 'analytics'],
        risk: ['exposure', 'risk'],
        fx: ['fx'],
        whatif: ['rebalance']
    };
    const portfolioLabCopy = {
        performance: 'Performance diagnostics brings attribution, benchmark behaviour, drawdowns and return efficiency into one focused view.',
        risk: 'Risk & Exposure combines what the portfolio owns underneath the ticker weights with where Euler VaR and concentration actually sit.',
        fx: 'FX separates local-price returns from quote-currency translation and shows how sterling moves affect the foreign-quoted book.',
        whatif: 'What-If lets you change target weights and recompute concentration and Euler VaR without altering the live portfolio.'
    };
    let currentPortfolioLabTab = 'performance';

    function moveSectionIntoLab(sectionId, panel) {
        const intro = document.getElementById(sectionId);
        if (!intro || !panel) return;
        const content = intro.nextElementSibling;
        panel.appendChild(intro);
        if (content) panel.appendChild(content);
    }

    function initialisePortfolioLab() {
        Object.entries(portfolioLabMap).forEach(([tab, ids]) => {
            const panel = document.getElementById(`lab-panel-${tab}`);
            ids.forEach(id => moveSectionIntoLab(id, panel));
        });
        applyPortfolioLabHash(false);
    }

    function setPortfolioLabTab(tab, updateHash=true, scrollToLab=false) {
        if (!portfolioLabMap[tab]) tab = 'performance';
        currentPortfolioLabTab = tab;
        document.querySelectorAll('[data-lab-panel]').forEach(panel => {
            panel.hidden = panel.dataset.labPanel !== tab;
        });
        document.querySelectorAll('[data-lab-tab]').forEach(button => {
            button.setAttribute('aria-selected', button.dataset.labTab === tab ? 'true' : 'false');
        });
        const context = document.getElementById('portfolio-lab-context');
        if (context) context.textContent = portfolioLabCopy[tab];
        if (updateHash) history.replaceState(null, '', `#lab-${tab}`);
        if (scrollToLab) document.getElementById('portfolio-lab')?.scrollIntoView({behavior:'smooth', block:'start'});
        setTimeout(() => {
            document.querySelectorAll(`#lab-panel-${tab} .js-plotly-plot`).forEach(plot => {
                try { Plotly.Plots.resize(plot); } catch (_) {}
            });
            window.dispatchEvent(new Event('resize'));
        }, 60);
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
            setPortfolioLabTab(currentPortfolioLabTab, false, false);
            return;
        }
        setPortfolioLabTab(tab, false, false);
        const rawId = hash.replace(/^#/, '');
        const target = rawId.startsWith('lab-') ? document.getElementById('portfolio-lab') : document.getElementById(rawId);
        setTimeout(() => target?.scrollIntoView({behavior: animate ? 'smooth' : 'auto', block:'start'}), 30);
    }

    window.addEventListener('hashchange', () => applyPortfolioLabHash(true));
'''
anchor_js = "    function fxMoney(value) {"
if anchor_js not in text:
    raise SystemExit('JS insertion anchor not found')
text = text.replace(anchor_js, lab_js + '\n\n' + anchor_js, 1)

old_boot = '''    loadPortfolio();
    loadExposureMap();
    loadFxAnalytics();
    loadRiskAnalytics();'''
new_boot = '''    initialisePortfolioLab();
    loadPortfolio();
    loadExposureMap();
    loadFxAnalytics();
    loadRiskAnalytics();'''
if old_boot not in text:
    raise SystemExit('Boot anchor not found')
text = text.replace(old_boot, new_boot, 1)

path.write_text(text)
