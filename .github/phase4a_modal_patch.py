from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text()

start = text.index('    function clearExpandedCardStyles(card) {')
end = text.index('    function bindExpandButtons() {', start)

replacement = r'''    function closeExpandedChart() {
        const modal = document.getElementById('financial-chart-modal');
        const plot = document.getElementById('financial-expanded-plot');
        if (plot && typeof Plotly !== 'undefined') {
            try { Plotly.purge(plot); } catch (_) {}
        }
        if (modal && modal.parentNode) modal.parentNode.removeChild(modal);
        expandedChartId = null;
        document.body.classList.remove('modal-active');
    }

    function renderExpandedPlot(chartId) {
        const source = document.getElementById(chartId);
        const target = document.getElementById('financial-expanded-plot');
        if (!source || !target) return;

        if (!Array.isArray(source.data) || source.data.length === 0) {
            target.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-weight:700;">Chart data is still loading.</div>';
            return;
        }

        const traces = source.data.map(trace => ({ ...trace }));
        const sourceLayout = source.layout || {};
        const layout = {
            ...sourceLayout,
            autosize: true,
            width: undefined,
            height: undefined,
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#ffffff',
            margin: {
                t: 18,
                r: 24,
                b: sourceLayout.showlegend ? 64 : 48,
                l: 64
            },
            hoverlabel: {
                bgcolor: '#ffffff',
                bordercolor: '#cbd5e1',
                font: { color: '#0f172a', size: 13 },
                align: 'left',
                namelength: -1
            }
        };

        Plotly.react(target, traces, layout, { displayModeBar: false, responsive: true });
        requestAnimationFrame(() => Plotly.Plots.resize(target));
    }

    function toggleExpandedChart(chartId) {
        if (expandedChartId === chartId) {
            closeExpandedChart();
            return;
        }

        closeExpandedChart();
        const card = document.querySelector(`[data-financial-card="${chartId}"]`);
        const source = document.getElementById(chartId);
        if (!card || !source) return;

        expandedChartId = chartId;
        document.body.classList.add('modal-active');

        const title = card.querySelector('h4')?.textContent?.trim() || 'Financial Metric';
        const badge = document.getElementById(`fin-period-${chartId}`)?.textContent?.trim() || '';
        const modal = document.createElement('div');
        modal.id = 'financial-chart-modal';
        modal.style.position = 'fixed';
        modal.style.inset = '0';
        modal.style.zIndex = '220';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.padding = '36px';

        const earnings = chartId === 'ind-earnings';
        modal.innerHTML = `
            <button id="financial-modal-backdrop" type="button" aria-label="Close expanded chart" style="position:absolute;inset:0;border:0;background:rgba(15,23,42,.48);cursor:default;"></button>
            <section role="dialog" aria-modal="true" aria-label="${title}" style="position:relative;z-index:1;width:min(1040px,calc(100vw - 72px));height:min(660px,calc(100vh - 96px));background:#fff;border:1px solid #e2e8f0;border-radius:18px;box-shadow:0 24px 60px rgba(15,23,42,.22);display:flex;flex-direction:column;overflow:hidden;">
                <header style="height:64px;flex:0 0 64px;display:flex;align-items:center;justify-content:space-between;padding:0 22px;border-bottom:1px solid #eef2f7;background:#fff;">
                    <div style="display:flex;align-items:center;gap:12px;min-width:0;">
                        <h3 style="margin:0;color:#334155;font-size:15px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${title}</h3>
                        ${badge ? `<span style="padding:4px 8px;border:1px solid #e2e8f0;border-radius:7px;background:#f8fafc;color:#94a3b8;font-size:9px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;">${badge}</span>` : ''}
                    </div>
                    <button id="financial-modal-close" type="button" aria-label="Close expanded chart" style="width:34px;height:34px;border:1px solid #e2e8f0;border-radius:9px;background:#fff;color:#64748b;font-size:20px;line-height:1;cursor:pointer;">×</button>
                </header>
                <div style="flex:1;min-height:0;padding:16px 18px ${earnings ? '8px' : '18px'};background:#fff;display:flex;flex-direction:column;">
                    <div id="financial-expanded-plot" style="width:100%;${earnings ? 'height:300px;flex:0 0 300px;' : 'height:100%;flex:1;min-height:0;'}"></div>
                    ${earnings ? '<div id="financial-expanded-detail" style="flex:1;min-height:0;overflow:auto;padding:6px 8px 0;"></div>' : ''}
                </div>
            </section>`;

        document.body.appendChild(modal);
        document.getElementById('financial-modal-backdrop')?.addEventListener('click', closeExpandedChart);
        document.getElementById('financial-modal-close')?.addEventListener('click', closeExpandedChart);

        if (earnings) {
            renderEarningsDetail();
            const sourceDetail = document.getElementById('financial-detail-ind-earnings');
            const modalDetail = document.getElementById('financial-expanded-detail');
            if (sourceDetail && modalDetail) modalDetail.innerHTML = sourceDetail.innerHTML;
        }

        requestAnimationFrame(() => {
            requestAnimationFrame(() => renderExpandedPlot(chartId));
        });
    }

'''

text = text[:start] + replacement + text[end:]

old_reset = '''        expandedChartId = null;\n        document.body.classList.remove('modal-active');\n        document.querySelectorAll('.financial-card').forEach(clearExpandedCardStyles);\n        const existingBackdrop = document.getElementById('financial-chart-backdrop');\n        if (existingBackdrop && existingBackdrop.parentNode) existingBackdrop.parentNode.removeChild(existingBackdrop);'''
new_reset = '''        closeExpandedChart();'''
if old_reset not in text:
    raise SystemExit('reset modal cleanup block not found')
text = text.replace(old_reset, new_reset, 1)

old_research = '''                if (expandedChartId === 'ind-earnings') renderEarningsDetail();'''
new_research = '''                if (expandedChartId === 'ind-earnings') {\n                    renderEarningsDetail();\n                    const sourceDetail = document.getElementById('financial-detail-ind-earnings');\n                    const modalDetail = document.getElementById('financial-expanded-detail');\n                    if (sourceDetail && modalDetail) modalDetail.innerHTML = sourceDetail.innerHTML;\n                }\n                if (expandedChartId) requestAnimationFrame(() => renderExpandedPlot(expandedChartId));'''
if old_research not in text:
    raise SystemExit('research modal refresh block not found')
text = text.replace(old_research, new_research, 1)

path.write_text(text)
