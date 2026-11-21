(() => {
    'use strict';

    const modules = {
        stocks: 'Stocks',
        macro: 'Macro',
        tools: 'Pinned Tools'
    };
    const topics = {
        inflation: ['Inflation', 'sethimacro.html#chart-inflation'],
        rates: ['Central bank rates', 'sethimacro.html#chart-cb-rates'],
        jobs: ['Labour market', 'sethimacro.html#job-market'],
        currencies: ['Currencies', 'sethimacro.html#currencies']
    };
    const tools = {
        dcf: ['Reverse DCF', 'sethistock.html?ticker=MSFT#valuation'],
        risk: ['Market Risk Lab', 'sethiquant.html#section-var'],
        attribution: ['Portfolio Attribution', 'sethiportfolio.html#attribution'],
        options: ['Options Valuation', 'sethiquant.html#section-options']
    };
    const $ = id => document.getElementById(id);

    function renderLinks(id, choices, selected, emptyText) {
        const list = $(id);
        list.replaceChildren();
        for (const key of selected) {
            const [label, href] = choices[key];
            const row = document.createElement('li');
            row.className = 'py-2.5';
            const link = document.createElement('a');
            link.className = 'text-sm font-semibold text-blue-700 hover:underline';
            link.textContent = label;
            link.href = href;
            row.append(link);
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

    window.initialiseWorkspace = userId => {
        const storageKey = 'sethiway-visual-workspace-' + userId;
        const stored = sessionStorage.getItem(storageKey);
        const prefs = stored ? JSON.parse(stored) : {
            order: Object.keys(modules),
            hidden: [],
            topics: ['inflation', 'rates'],
            tools: ['dcf', 'risk']
        };
        const save = () => sessionStorage.setItem(storageKey, JSON.stringify(prefs));
        const workspace = $('workspace-modules');
        const panels = new Map([...workspace.children].map(panel => [panel.dataset.module, panel]));

        function renderModules() {
            for (const key of prefs.order) {
                const panel = panels.get(key);
                panel.hidden = prefs.hidden.includes(key);
                workspace.append(panel);
            }
        }

        function renderOrderControls(focusKey, focusOffset) {
            const container = $('module-controls');
            container.replaceChildren();
            for (const [index, key] of prefs.order.entries()) {
                const row = document.createElement('div');
                row.className = 'flex flex-wrap items-center justify-between gap-2';
                row.append(checkbox(modules[key], !prefs.hidden.includes(key), checked => {
                    prefs.hidden = prefs.hidden.filter(item => item !== key);
                    if (!checked) prefs.hidden.push(key);
                    save();
                    renderModules();
                }));
                const actions = document.createElement('div');
                actions.className = 'flex gap-1';
                for (const [offset, label] of [[-1, 'Up'], [1, 'Down']]) {
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.textContent = label;
                    button.setAttribute('aria-label', 'Move ' + modules[key] + ' ' + label.toLowerCase());
                    button.className = 'rounded-md px-2 py-1 text-sm font-semibold text-blue-700 hover:bg-blue-50 disabled:text-gray-400';
                    const target = index + offset;
                    button.disabled = target < 0 || target >= prefs.order.length;
                    button.addEventListener('click', () => {
                        [prefs.order[index], prefs.order[target]] = [prefs.order[target], prefs.order[index]];
                        save();
                        renderModules();
                        renderOrderControls(key, target + offset < 0 || target + offset >= prefs.order.length ? -offset : offset);
                    });
                    actions.append(button);
                    if (focusKey === key && focusOffset === offset) requestAnimationFrame(() => button.focus());
                }
                row.append(actions);
                container.append(row);
            }
        }

        for (const [key, choices, controls, list, empty] of [
            ['topics', topics, 'macro-controls', 'macro-topics', 'Choose macro topics under Customise workspace.'],
            ['tools', tools, 'tool-controls', 'pinned-tools', 'Choose tools under Customise workspace.']
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
        renderModules();
        renderOrderControls();
    };
})();
