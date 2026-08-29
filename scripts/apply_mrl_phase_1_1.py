from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')

old = '''        @media (min-width: 1536px) {
            #market-risk-lab { width: min(1800px, calc(100vw - 3rem)); }
        }
'''
new = '''        @media (min-width: 1536px) {
            #market-risk-lab { width: min(1800px, calc(100vw - 3rem)); }
            #market-risk-lab #model-chart,
            #market-risk-lab #pnl-chart,
            #market-risk-lab #corr-chart { height: 380px !important; }
        }
'''

if old not in s:
    raise SystemExit('Expected MRL desktop media query not found')

s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

for marker in ['#model-chart', '#pnl-chart', '#corr-chart', 'height: 380px !important']:
    if marker not in s:
        raise SystemExit(f'Missing expected marker: {marker}')

print('Phase 1.1 MRL desktop chart-height polish applied.')
