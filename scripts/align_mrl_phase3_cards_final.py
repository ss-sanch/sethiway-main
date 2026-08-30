from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')
old = '#market-risk-lab #stress-chart { height: 417px !important; }'
new = '#market-risk-lab #stress-chart { height: 438px !important; }'
if old not in s:
    raise SystemExit('Expected 417px MRL desktop height marker not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('MRL wide-desktop chart height updated from 417px to 438px.')
# trigger final alignment workflow
