from pathlib import Path

p = Path('sethiportfolio-admin.html')
s = p.read_text(encoding='utf-8')

old_login = '''            const health = await apiFetch('/admin/health');\n            if (!health.authenticated || !health.writes_configured) throw new Error('Admin writes are not fully configured.');\n'''
new_login = '''            const health = await apiFetch('/admin/health');\n            if (!health.authenticated || !health.writes_configured) throw new Error('Admin writes are not fully configured.');\n            if (!health.admin_ledger || !health.allocation_corrections) throw new Error('Backend deployment is missing the latest SethiPortfolio correction capabilities.');\n'''
if old_login not in s:
    raise SystemExit('login health marker missing')
s = s.replace(old_login, new_login, 1)

old_refresh = '''            await apiFetch('/admin/health');\n            const [portfolioResponse, txnData, journalData] = await Promise.all([\n                fetch(`${API}/${PORTFOLIO}`),\n                apiFetch(`/admin/${PORTFOLIO}/transactions`),\n                apiFetch(`/admin/${PORTFOLIO}/journal`)\n            ]);\n'''
new_refresh = '''            const health = await apiFetch('/admin/health');\n            if (!health.admin_ledger || !health.allocation_corrections) throw new Error('Backend deployment is missing the latest SethiPortfolio correction capabilities.');\n            const [portfolioResponse, txnData, journalData] = await Promise.all([\n                fetch(`${API}/${PORTFOLIO}`),\n                apiFetch(`/admin/${PORTFOLIO}/ledger`),\n                apiFetch(`/admin/${PORTFOLIO}/journal`)\n            ]);\n'''
if old_refresh not in s:
    raise SystemExit('refresh marker missing')
s = s.replace(old_refresh, new_refresh, 1)

p.write_text(s, encoding='utf-8')
