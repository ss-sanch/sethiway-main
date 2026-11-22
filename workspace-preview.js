(() => {
    'use strict';

    const modules = {
        stocks: 'Watchlist',
        portfolio: 'My Portfolio',
        macro: 'Macro Briefing',
        tools: 'Pinned Tools'
    };
    const topics = {
        inflation: ['UK inflation', 'sethimacro.html#chart-inflation', 'Example headline · UK price growth slows', 'CPI · 2.6% y/y vs 2.7% prior'],
        rates: ['US central bank rates', 'sethimacro.html#chart-cb-rates', 'Example headline · Fed leaves rates unchanged', 'Fed target range · 3.75–4.00%'],
        jobs: ['US labour market', 'sethimacro.html#job-market', 'Example headline · US hiring picks up', 'Non-farm payrolls · +145k vs +125k prior'],
        currencies: ['Currencies', 'sethimacro.html#currencies', 'Example headline · Sterling strengthens', 'GBP/USD · 1.32']
    };
    const tools = {
        dcf: ['Reverse DCF', 'sethistock.html?ticker=MSFT#valuation'],
        risk: ['Market Risk Lab', 'sethiquant.html#section-var'],
        attribution: ['Portfolio Attribution', 'sethiportfolio.html#attribution'],
        options: ['Options Valuation', 'sethiquant.html#section-options'],
        backtest: ['Strategy Backtest', 'sethiquant.html#section-backtest']
    };
    const $ = id => document.getElementById(id);

    function renderLinks(id, choices, selected, emptyText) {
        const list = $(id);
        list.replaceChildren();
        for (const key of selected) {
            const [label, href, kind, reading] = choices[key];
            const row = document.createElement('li');
            row.className = 'py-2.5';
            const link = document.createElement('a');
            link.className = 'text-sm font-semibold text-blue-700 hover:underline';
            link.textContent = label;
            link.href = href;
            if (kind) {
                const context = document.createElement('p');
                context.className = 'mb-1 text-xs font-medium text-slate-600';
                context.textContent = kind;
                row.append(context);
            }
            row.append(link);
            if (reading) {
                const metric = document.createElement('p');
                metric.className = 'mt-1 text-xs tabular-nums text-slate-700';
                metric.textContent = reading;
                row.append(metric);
            }
            list.append(row);
        }
        if (!selected.length) {
            const row = document.createElement('li');
            row.className = 'text-sm text-gray-600';
            row.textContent = emptyText;
            list.append(row);
        }
    }

    function checkbox(label, checked, onChange) {
        const control = document.createElement('label');
        control.className = 'flex items-center gap-2 text-sm';
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.checked = checked;
        input.addEventListener('change', () => onChange(input.checked));
        control.append(input, label);
        return control;
    }

    window.initialiseWorkspace = (userId, storage, reportSave) => {
        const storageKey = 'sethiway-visual-workspace-v2-' + userId;
        const stored = storage ? storage.get('layout') : JSON.parse(sessionStorage.getItem(storageKey) || 'null');
        const prefs = stored || {
            order: Object.keys(modules),
            hidden: [],
            topics: ['inflation', 'rates', 'jobs', 'currencies'],
            tools: ['dcf', 'risk', 'attribution', 'options', 'backtest']
        };
        const save = () => {
            if (storage) reportSave(storage.save('layout', prefs), 'layout');
            else sessionStorage.setItem(storageKey, JSON.stringify(prefs));
        };
        const workspace = $('workspace-modules');
        const panels = new Map([...workspace.children].map(panel => [panel.dataset.module, panel]));

        const toggle = $('customise-workspace');
        let editing = false;

        function renderVisibility() {
            for (const [key, panel] of panels) {
                const hidden = prefs.hidden.includes(key);
                panel.hidden = hidden && !editing;
                panel.querySelector('[data-module-content]').hidden = hidden;
                panel.querySelector('[data-module-placeholder]').hidden = !hidden || !editing;
                panel.querySelector('[data-module-settings]').hidden = !editing;
            }
        }

        function renderOrder() {
            for (const key of prefs.order) workspace.append(panels.get(key));
        }

        function setEditing(next) {
            editing = next;
            workspace.toggleAttribute('data-editing', editing);
            toggle.setAttribute('aria-pressed', String(editing));
            toggle.textContent = editing ? 'Done customising' : 'Customise workspace';
            $('workspace-edit-hint').hidden = !editing;
            renderVisibility();
        }

        function renderOrderControls(focusKey, focusOffset) {
            for (const [index, key] of prefs.order.entries()) {
                const container = panels.get(key).querySelector('[data-module-controls]');
                const visibility = checkbox('Show card', !prefs.hidden.includes(key), checked => {
                    prefs.hidden = prefs.hidden.filter(item => item !== key);
                    if (!checked) prefs.hidden.push(key);
                    save();
                    renderVisibility();
                });
                const actions = document.createElement('div');
                actions.className = 'flex flex-wrap gap-1';
                for (const [offset, label] of [[-1, 'Move up'], [1, 'Move down']]) {
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.textContent = label;
                    button.setAttribute('aria-label', 'Move ' + modules[key] + (offset < 0 ? ' up' : ' down'));
                    button.className = 'rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-bold text-slate-700 hover:border-blue-600 disabled:border-slate-200 disabled:bg-slate-50 disabled:text-slate-400';
                    const target = index + offset;
                    button.disabled = target < 0 || target >= prefs.order.length;
                    button.addEventListener('click', () => {
                        [prefs.order[index], prefs.order[target]] = [prefs.order[target], prefs.order[index]];
                        save();
                        renderOrder();
                        renderOrderControls(key, prefs.order[target + offset] ? offset : -offset);
                    });
                    actions.append(button);
                    if (focusKey === key && focusOffset === offset) requestAnimationFrame(() => button.focus());
                }
                container.replaceChildren(visibility, actions);
            }
        }

        $('macro-description').textContent = storage ? 'Open the SethiMacro releases and indicators you follow.' : 'Sample releases for the topics you follow.';
        const macroTopics = storage ? Object.fromEntries(Object.entries(topics).map(([key, item]) => [key, item.slice(0, 2)])) : topics;
        for (const [key, choices, controls, list, empty] of [
            ['topics', macroTopics, 'macro-controls', 'macro-topics', 'Choose topics in Macro Briefing settings.'],
            ['tools', tools, 'tool-controls', 'pinned-tools', 'Choose tools in Pinned Tools settings.']
        ]) {
            const draw = () => renderLinks(list, choices, prefs[key], empty);
            $(controls).replaceChildren(...Object.entries(choices).map(([id, [label]]) =>
                checkbox(label, prefs[key].includes(id), checked => {
                    prefs[key] = prefs[key].filter(item => item !== id);
                    if (checked) prefs[key].push(id);
                    save();
                    draw();
                })
            ));
            draw();
        }
        renderOrder();
        renderOrderControls();
        toggle.onclick = () => setEditing(!editing);
        setEditing(false);
        window.initialisePreviewPortfolio(userId, storage, reportSave);
    };
})();
