from pathlib import Path
p=Path('sethiportfolio.html')
t=p.read_text()
old="}, {rootMargin:'900px 0px'});"
new="}, {rootMargin:'400px 0px'});"
if old not in t:
    raise SystemExit('prefetch margin anchor not found')
p.write_text(t.replace(old,new,1))
