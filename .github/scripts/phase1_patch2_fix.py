from pathlib import Path
import re
import subprocess
import tempfile

p = Path('sethiportfolio-admin.html')
text = p.read_text()
old = '''            el('auth-status').textContent = 'Authenticated · writes enabled';
            el('auth-status').className = 'hidden sm:inline-flex text-[10px] font-black uppercase tracking-wider text-emerald-700';
            await refreshAdminData();
        } catch (error) {'''
new = '''            el('auth-status').textContent = 'Authenticated · writes enabled';
            el('auth-status').className = 'hidden sm:inline-flex text-[10px] font-black uppercase tracking-wider text-emerald-700';
            await refreshAdminData();
            await applyInboundPortfolioIntent();
        } catch (error) {'''
count = text.count(old)
if count != 1:
    raise SystemExit(f'admin login handoff selector: expected 1 match, found {count}')
p.write_text(text.replace(old, new, 1))

for path, marker in [
    ('sethiportfolio.html', 'portfolio-watchlist-ribbon'),
    ('sethistock.html', 'openPortfolioAdminFromStock'),
    ('sethiportfolio-admin.html', 'applyInboundPortfolioIntent'),
    ('sethiportfolio-admin.html', 'await applyInboundPortfolioIntent();'),
    ('sethiquant.html', 'importPortfolioFromQuery'),
]:
    if marker not in Path(path).read_text():
        raise SystemExit(f'Missing expected marker {marker} in {path}')

for path in ['sethiportfolio.html', 'sethistock.html', 'sethiportfolio-admin.html', 'sethiquant.html']:
    html = Path(path).read_text()
    blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', html, flags=re.S | re.I)
    for i, block in enumerate(blocks):
        if not block.strip():
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
            f.write(block)
            temp = f.name
        result = subprocess.run(['node', '--check', temp], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f'JavaScript syntax check failed for {path} script {i}:\n{result.stderr}')

print('Phase 1 pass 2 selector fixed; all integration markers and inline JavaScript validated.')
