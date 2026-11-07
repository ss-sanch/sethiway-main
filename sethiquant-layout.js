function resizeQuantPlots(container) {
    requestAnimationFrame(() => {
        container.querySelectorAll('.js-plotly-plot').forEach(plot => {
            if (plot.getClientRects().length) window.Plotly?.Plots.resize(plot).catch(() => {});
        });
    });
}

(() => {
    const workspaces = [...document.querySelectorAll('.quant-workspace')];
    const links = [...document.querySelectorAll('.site-header a[href^="#section-"], .quant-mobile-workspaces a')];
    const defaultWorkspace = new URLSearchParams(location.search).get('portfolio')?.trim()
        ? document.getElementById('section-var')
        : workspaces[0];

    function showWorkspace(event) {
        const hashTarget = document.getElementById(location.hash.slice(1));
        const selected = hashTarget?.closest('.quant-workspace') || defaultWorkspace;
        workspaces.forEach(workspace => {
            workspace.hidden = workspace !== selected;
        });
        links.forEach(link => {
            if (link.hash === '#' + selected.id) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
        });
        if (event) {
            if (hashTarget && hashTarget !== selected && selected.contains(hashTarget)) {
                hashTarget.scrollIntoView({ behavior: 'instant' });
            } else {
                window.scrollTo({ top: 0, behavior: 'instant' });
            }
        }
        resizeQuantPlots(selected);
    }

    showWorkspace();
    window.addEventListener('hashchange', showWorkspace);

    const resultButtons = [...document.querySelectorAll('[data-quant-result]')];
    resultButtons.forEach(button => {
        button.addEventListener('click', () => {
            resultButtons.forEach(item => {
                const selected = item === button;
                item.setAttribute('aria-pressed', String(selected));
                const panel = document.getElementById(item.dataset.quantResult);
                panel.hidden = !selected;
                if (selected) resizeQuantPlots(panel);
            });
        });
    });

    const payoff = document.getElementById('options-insights');
    payoff.addEventListener('toggle', () => {
        if (payoff.open) resizeQuantPlots(payoff);
    });
})();
