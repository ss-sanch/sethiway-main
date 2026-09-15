from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text(encoding='utf-8')
old = '''    function emptyChart(id, message = 'Data Unavailable') {
        const element = document.getElementById(id);
        if (!element) return;
        if (typeof Plotly !== 'undefined' && (element.classList.contains('js-plotly-plot') || element._fullLayout)) {
            try { Plotly.purge(element); } catch (_) {}
        }
        element.innerHTML = `<div class="flex h-full items-center justify-center text-gray-400 font-bold text-sm text-center px-5">${message}</div>`;
    }

    function preparePlotContainer(id) {
        const element = document.getElementById(id);
        if (!element) return null;
        const hasPlot = element.classList.contains('js-plotly-plot') || Boolean(element._fullLayout);
        if (!hasPlot) element.innerHTML = '';
        return element;
    }
'''
new = '''    function emptyChart(id, message = 'Data Unavailable') {
        const element = document.getElementById(id);
        if (!element) return;
        if (typeof Plotly !== 'undefined' && (element.classList.contains('js-plotly-plot') || element._fullLayout)) {
            try { Plotly.purge(element); } catch (_) {}
        }
        element.innerHTML = `<div data-financial-placeholder="1" class="flex h-full items-center justify-center text-gray-400 font-bold text-sm text-center px-5">${message}</div>`;
    }

    function preparePlotContainer(id) {
        const element = document.getElementById(id);
        if (!element) return null;

        // Plotly.purge can leave its marker class behind even after an empty-state
        // placeholder has replaced the plot DOM. Treat the placeholder itself as the
        // source of truth so loading/unavailable text can never survive under a chart.
        const placeholder = element.querySelector('[data-financial-placeholder="1"]');
        if (placeholder) {
            if (typeof Plotly !== 'undefined' && (element.classList.contains('js-plotly-plot') || element._fullLayout)) {
                try { Plotly.purge(element); } catch (_) {}
            }
            element.innerHTML = '';
            element.classList.remove('js-plotly-plot');
        } else {
            const hasPlot = element.classList.contains('js-plotly-plot') || Boolean(element._fullLayout);
            if (!hasPlot) element.innerHTML = '';
        }
        return element;
    }
'''
if old not in text:
    raise SystemExit('target block not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('PLACEHOLDER_CLEANUP_PATCH_OK')
