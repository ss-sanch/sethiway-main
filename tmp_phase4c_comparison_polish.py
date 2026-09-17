from pathlib import Path

html_path = Path('sethistock.html')
html = html_path.read_text()

old_header = '''                <div>
                    <h3 class="text-2xl font-black">Financial Comparisons</h3>
                    <p class="text-sm text-gray-500 mt-1">Compare profitability, cash conversion and balance-sheet strength across the full annual history already loaded above.</p>
                </div>'''
new_header = '''                <div>
                    <div class="flex items-center gap-2">
                        <h3 class="text-2xl font-black">Financial Comparisons</h3>
                        <button type="button" onclick="toggleModal('comparisons-info-modal')" aria-label="Explain Financial Comparisons" title="Explain Financial Comparisons" class="inline-flex h-7 w-7 items-center justify-center rounded-full text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </button>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">Compare profitability, cash conversion and balance-sheet strength across the full annual history already loaded above.</p>
                </div>'''
if old_header not in html:
    raise SystemExit('Financial Comparisons header marker not found')
html = html.replace(old_header, new_header, 1)

modal_marker = '    <div id="dcf-modal" class="hidden fixed inset-0 z-[150] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm transition-opacity duration-300">'
if modal_marker not in html:
    raise SystemExit('DCF modal marker not found')
comparison_modal = '''    <div id="comparisons-info-modal" class="hidden fixed inset-0 z-[150] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm transition-opacity duration-300">
        <div class="bg-white rounded-2xl shadow-2xl p-7 max-w-3xl w-full mx-4 transform scale-95 opacity-0 transition-all duration-300 overflow-y-auto max-h-[90vh]">
            <div class="flex justify-between items-start gap-6 mb-5 border-b border-gray-100 pb-4">
                <div>
                    <h2 class="text-2xl font-black text-gray-900">Financial Comparisons Guide</h2>
                    <p class="text-sm text-gray-500 mt-1">Four annual comparisons designed to answer a different question about operating quality and balance-sheet strength.</p>
                </div>
                <button type="button" onclick="toggleModal('comparisons-info-modal')" aria-label="Close Financial Comparisons guide" class="text-gray-400 hover:text-red-500 text-3xl leading-none">&times;</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700 leading-relaxed">
                <section class="rounded-xl border border-gray-200 p-4">
                    <h4 class="font-black text-gray-900 mb-1">Revenue vs Net Income</h4>
                    <p>Shows whether earnings are scaling with sales. The footer highlights current net margin and whether margin has expanded or contracted over five years.</p>
                </section>
                <section class="rounded-xl border border-gray-200 p-4">
                    <h4 class="font-black text-gray-900 mb-1">Cash vs Total Debt</h4>
                    <p>Compares liquidity with gross leverage. Net debt and Debt / Cash help show how much balance-sheet pressure remains after cash is considered.</p>
                </section>
                <section class="rounded-xl border border-gray-200 p-4">
                    <h4 class="font-black text-gray-900 mb-1">Operating CF vs Free Cash Flow</h4>
                    <p>Shows how much operating cash survives after capital spending. FCF conversion helps distinguish accounting cash generation from genuinely distributable cash.</p>
                </section>
                <section class="rounded-xl border border-gray-200 p-4">
                    <h4 class="font-black text-gray-900 mb-1">Operating CF vs CapEx</h4>
                    <p>Shows capital intensity. CapEx / OCF indicates how much operating cash must be reinvested before cash can be retained for debt reduction, buybacks or other uses.</p>
                </section>
            </div>
            <div class="mt-5 rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-xs font-semibold text-blue-800">
                These charts reuse the annual financial history already loaded in Key Financial Metrics. They do not trigger an additional data request.
            </div>
            <div class="mt-6 pt-4 text-center border-t border-gray-100">
                <button type="button" onclick="toggleModal('comparisons-info-modal')" class="bg-gray-900 text-white font-bold py-2 px-7 rounded-lg hover:bg-gray-700 transition">Close</button>
            </div>
        </div>
    </div>

'''
html = html.replace(modal_marker, comparison_modal + modal_marker, 1)
html_path.write_text(html)

js_path = Path('sethistock-financial-history.js')
js = js_path.read_text()

marker = '''    function drawComparison(view, id, first, second) {
        const rows = comparisonRows(view, first.key, second.key);'''
if marker not in js:
    raise SystemExit('drawComparison marker not found')
helpers = '''    function comparisonRelationship(id, row) {
        if (id === 'comp-rev-net') {
            return ['Net Margin', comparisonPct(row.first ? row.second / row.first * 100 : null)];
        }
        if (id === 'comp-cash-debt') {
            return ['Net Debt', comparisonMoney(row.second - row.first)];
        }
        if (id === 'comp-fcf-ocf') {
            return ['FCF Conversion', comparisonPct(row.first ? row.second / row.first * 100 : null)];
        }
        const ratio = row.first ? row.second / row.first * 100 : null;
        const retained = row.first - row.second;
        return ['CapEx / OCF', `${comparisonPct(ratio)} · Retained ${comparisonMoney(retained)}`];
    }

    function comparisonDarkenColour(hex, factor = 0.76) {
        const match = String(hex || '').match(/^#([0-9a-f]{6})$/i);
        if (!match) return hex;
        const value = match[1];
        const channel = offset => Math.max(0, Math.min(255, Math.round(parseInt(value.slice(offset, offset + 2), 16) * factor)));
        return `#${[0, 2, 4].map(offset => channel(offset).toString(16).padStart(2, '0')).join('')}`;
    }

    function comparisonBarColours(colour, count) {
        const latest = comparisonDarkenColour(colour);
        return Array.from({ length: count }, (_, index) => index === count - 1 ? latest : colour);
    }

'''
js = js.replace(marker, helpers + marker, 1)

old_block = '''        const custom = rows.map(row => [
            metricDisplayValue(first.key, row.first),
            metricDisplayValue(second.key, row.second),
            row.first !== 0 ? `${(row.second / row.first * 100).toFixed(1)}%` : 'N/A'
        ]);
        const hover = `%{x}<br>${first.name}: %{customdata[0]}<br>${second.name}: %{customdata[1]}<br>${second.name} / ${first.name}: %{customdata[2]}<extra></extra>`;
        const traces = [
            { x: rows.map(row => row.year), y: rows.map(row => row.first), type: 'bar', name: first.name, marker: { color: first.colour, line: { width: 0 } }, customdata: custom, hovertemplate: hover },
            { x: rows.map(row => row.year), y: rows.map(row => row.second), type: 'bar', name: second.name, marker: { color: second.colour, line: { width: 0 } }, customdata: custom, hovertemplate: hover }
        ];'''
new_block = '''        const custom = rows.map(row => {
            const [relationshipLabel, relationshipValue] = comparisonRelationship(id, row);
            return [
                metricDisplayValue(first.key, row.first),
                metricDisplayValue(second.key, row.second),
                relationshipLabel,
                relationshipValue
            ];
        });
        const firstHover = `<b>%{x}</b><br>${first.name}: %{customdata[0]}<br>%{customdata[2]}: %{customdata[3]}<extra></extra>`;
        const secondHover = `<b>%{x}</b><br>${second.name}: %{customdata[1]}<extra></extra>`;
        const traces = [
            {
                x: rows.map(row => row.year),
                y: rows.map(row => row.first),
                type: 'bar',
                name: first.name,
                marker: { color: comparisonBarColours(first.colour, rows.length), line: { width: 0 } },
                customdata: custom,
                hovertemplate: firstHover
            },
            {
                x: rows.map(row => row.year),
                y: rows.map(row => row.second),
                type: 'bar',
                name: second.name,
                marker: { color: comparisonBarColours(second.colour, rows.length), line: { width: 0 } },
                customdata: custom,
                hovertemplate: secondHover
            }
        ];'''
if old_block not in js:
    raise SystemExit('Comparison trace block not found')
js = js.replace(old_block, new_block, 1)
js_path.write_text(js)

print('PHASE4C_COMPARISON_POLISH_APPLIED')
