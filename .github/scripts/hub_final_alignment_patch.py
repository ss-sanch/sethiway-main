from pathlib import Path

path = Path('index.html')
text = path.read_text()

old_arrow = 'class="hidden xl:block flex-1 h-3 ml-4 overflow-visible"'
new_arrow = 'class="hidden xl:block flex-1 h-3 ml-4 overflow-visible translate-y-[2px]"'
count = text.count(old_arrow)
if count != 3:
    raise SystemExit(f'Expected 3 workflow arrows, found {count}')
text = text.replace(old_arrow, new_arrow)

old_cta = '>Open Portfolio →</a>'
new_cta = '>Unlock Vault →</a>'
if text.count(old_cta) != 1:
    raise SystemExit(f'Expected one Portfolio CTA, found {text.count(old_cta)}')
text = text.replace(old_cta, new_cta, 1)

if text.count('translate-y-[2px]') != 3:
    raise SystemExit('Workflow arrow optical alignment was not applied to all three arrows')
if 'SethiPortfolio Vault' not in text:
    raise SystemExit('SethiPortfolio Vault title missing')
if 'PORTFOLIO.</span>' not in text:
    raise SystemExit('SethiPortfolio mark punctuation missing')
if 'How It Works' in text:
    raise SystemExit('Redundant How It Works navigation returned')
if '—' in text:
    raise SystemExit('Em dash remains in homepage copy')

path.write_text(text)
