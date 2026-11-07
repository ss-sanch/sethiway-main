function resizeQuantPlots(container) {
    requestAnimationFrame(() => {
        container.querySelectorAll('.js-plotly-plot').forEach(plot => {
            if (plot.getClientRects().length) window.Plotly?.Plots.resize(plot).catch(() => {});
        });
    });
}

(() => {
    const portfolio = new URLSearchParams(location.search).get('portfolio')?.trim();
    if (portfolio && !location.hash) {
        window.addEventListener('load', () => {
            if (!location.hash) document.getElementById('section-var').scrollIntoView({ behavior: 'instant' });
        }, { once: true });
    }

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
