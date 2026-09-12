from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text(encoding='utf-8')
start = text.index('    function renderFinancialCards(view) {')
end = text.index('    function emptyChart(', start)

replacement = r'''    function renderFinancialCards(view) {
        const cards = [
            { id: 'ind-rev', key: 'revenue', title: 'Revenue' },
            { id: 'ind-net', key: 'net', title: 'Net Income' },
            { id: 'ind-margins', key: 'net_margin', title: 'Margin Profile' },
            { id: 'ind-ocf', key: 'ocf', title: 'Operating Cash Flow' },
            { id: 'ind-fcf', key: 'fcf', title: 'Free Cash Flow' },
            { id: 'ind-capex', key: 'capex', title: 'Capital Expenditure' },
            { id: 'ind-cash', key: 'cash', title: 'Cash Equivalents' },
            { id: 'ind-debt', key: 'debt', title: 'Total Debt' },
            { id: 'ind-shares', key: 'shares', title: 'Shares Outstanding' }
        ];
        const container = document.getElementById('individual-charts-container');
        if (!container) return;
        const periodLabel = humanPeriod(view?.period || 'annual');

        // Build the shell once. Keeping the Plotly target nodes stable means period
        // switches can genuinely use Plotly.react instead of recreating nine charts.
        if (container.dataset?.phase2eReady !== '1') {
            let html = '';
            cards.forEach(card => {
                html += `
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col min-h-[350px]">
                        <div class="flex items-center justify-between gap-3 mb-2">
                            <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest">${card.title}</h4>
                            <span id="fin-period-${card.id}" class="px-2 py-1 rounded-md bg-gray-50 border border-gray-100 text-[9px] font-black text-gray-400 uppercase tracking-widest">${periodLabel}</span>
                        </div>
                        <div id="${card.id}" class="h-56 w-full mt-auto mb-2"></div>
                        <div class="grid grid-cols-4 gap-2 mt-4 pt-4 border-t border-gray-100">
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">1Y CAGR</p><p id="fin-growth-${card.id}-1Y" class="font-semibold text-xs text-gray-400">-</p></div>
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">2Y CAGR</p><p id="fin-growth-${card.id}-2Y" class="font-semibold text-xs text-gray-400">-</p></div>
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">3Y CAGR</p><p id="fin-growth-${card.id}-3Y" class="font-semibold text-xs text-gray-400">-</p></div>
                            <div class="text-center"><p class="text-[9px] text-gray-400 font-bold uppercase">MAX</p><p id="fin-growth-${card.id}-MAX" class="font-semibold text-xs text-gray-400">-</p></div>
                        </div>
                    </div>`;
            });
            container.innerHTML = html;
            if (container.dataset) container.dataset.phase2eReady = '1';
        }

        cards.forEach(card => {
            const growth = getGrowthStats(view, card.key);
            const badge = document.getElementById(`fin-period-${card.id}`);
            if (badge) {
                badge.textContent = view?.period === 'ttm' && ['cash', 'debt', 'shares'].includes(card.key)
                    ? 'Point-in-time'
                    : periodLabel;
            }
            ['1Y', '2Y', '3Y', 'MAX'].forEach(horizon => {
                const value = growth[horizon];
                const element = document.getElementById(`fin-growth-${card.id}-${horizon}`);
                if (!element) return;
                element.textContent = value;
                element.className = `font-semibold text-xs ${growthColour(value)}`;
            });
        });
    }

'''

path.write_text(text[:start] + replacement + text[end:], encoding='utf-8')
print('PHASE2E_DOM_OPTIMISED')
