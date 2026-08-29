from pathlib import Path

p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')
old = '#market-risk-lab #corr-chart { height: 380px !important; }'
new = '#market-risk-lab #corr-chart { height: 393px !important; }'
if old not in s:
    raise SystemExit('Expected 380px MRL chart height rule not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Aligned MRL chart cards to 393px wide-screen chart height.')
# Trigger one-off alignment workflow.
