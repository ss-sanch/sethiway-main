from pathlib import Path

path = Path('index.html')
text = path.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

# Replace the redundant top-right platform CTA with the admin sign-in control.
replace_once(
    '<a href="#platform" class="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-bold hover:bg-blue-600 transition shrink-0">Explore Platform</a>',
    '<button type="button" onclick="openAdminModal()" class="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-bold hover:bg-blue-600 transition shrink-0">Sign In</button>',
    'header Sign In button',
)

# Quick Launch now makes these hero CTAs unnecessary.
replace_once(
    '''                <div class="mt-4 flex flex-col sm:flex-row justify-center gap-3">\n                    <a href="#platform" class="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-black hover:bg-blue-700 transition shadow-sm">Explore the Platform →</a>\n                    <a href="sethiportfolio.html" class="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-white border border-gray-200 text-gray-900 text-sm font-black hover:border-amber-300 hover:bg-amber-50 transition">Open SethiPortfolio →</a>\n                </div>\n\n''',
    '',
    'hero CTA removal',
)

# Restore the existing admin access flow in a cleaner modal.
modal = '''\n    <div id="login-modal" class="hidden fixed inset-0 z-[100] items-center justify-center bg-gray-950/55 px-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="admin-login-title">\n        <div class="relative w-full max-w-md rounded-2xl border border-gray-200 bg-white p-7 shadow-2xl">\n            <button type="button" onclick="closeAdminModal()" class="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-lg text-gray-400 transition hover:bg-gray-100 hover:text-gray-900" aria-label="Close sign in">\n                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>\n            </button>\n            <div class="pr-10">\n                <p class="text-[10px] font-black uppercase tracking-[0.18em] text-blue-600">Admin Access</p>\n                <h2 id="admin-login-title" class="mt-1 text-2xl font-black text-gray-950">Sign in to the dashboard</h2>\n                <p class="mt-2 text-sm leading-relaxed text-gray-500">Enter the admin credentials to open the telemetry dashboard.</p>\n            </div>\n            <form id="admin-login-form" class="mt-6 space-y-4">\n                <div>\n                    <label for="portal-user" class="mb-1.5 block text-xs font-bold text-gray-500">Username</label>\n                    <input type="text" id="portal-user" autocomplete="username" class="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100" placeholder="Username">\n                </div>\n                <div>\n                    <label for="portal-pass" class="mb-1.5 block text-xs font-bold text-gray-500">Master password</label>\n                    <input type="password" id="portal-pass" autocomplete="current-password" class="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100" placeholder="Password">\n                </div>\n                <p id="portal-error" class="hidden text-xs font-semibold text-red-600">Those admin details are not recognised.</p>\n                <button type="submit" class="w-full rounded-xl bg-gray-900 px-5 py-3 text-sm font-black text-white transition hover:bg-blue-600">Open Dashboard</button>\n            </form>\n        </div>\n    </div>\n'''
replace_once('\n    <footer class="bg-gray-950 text-white px-6 lg:px-10 py-10">', modal + '\n    <footer class="bg-gray-950 text-white px-6 lg:px-10 py-10">', 'admin modal insertion')

# Reconnect the original admin dashboard handoff. admin.html performs the backend secret check.
script_anchor = '''<script>\n    const launcherForm = document.getElementById('stock-launcher');'''
script_replacement = '''<script>\n    const adminModal = document.getElementById('login-modal');\n    const adminLoginForm = document.getElementById('admin-login-form');\n    const adminUser = document.getElementById('portal-user');\n    const adminPass = document.getElementById('portal-pass');\n    const adminError = document.getElementById('portal-error');\n\n    function openAdminModal() {\n        adminModal.classList.remove('hidden');\n        adminModal.classList.add('flex');\n        adminError.classList.add('hidden');\n        setTimeout(() => adminUser.focus(), 0);\n    }\n\n    function closeAdminModal() {\n        adminModal.classList.add('hidden');\n        adminModal.classList.remove('flex');\n        adminError.classList.add('hidden');\n    }\n\n    adminModal.addEventListener('click', event => {\n        if (event.target === adminModal) closeAdminModal();\n    });\n\n    document.addEventListener('keydown', event => {\n        if (event.key === 'Escape' && !adminModal.classList.contains('hidden')) closeAdminModal();\n    });\n\n    adminLoginForm.addEventListener('submit', event => {\n        event.preventDefault();\n        const user = adminUser.value.trim().toLowerCase();\n        const password = adminPass.value;\n\n        if (user !== 'admin' || !password) {\n            adminError.classList.remove('hidden');\n            return;\n        }\n\n        adminError.classList.add('hidden');\n        localStorage.setItem('sethiway_vault_key', password);\n        window.location.href = 'admin.html';\n    });\n\n    const launcherForm = document.getElementById('stock-launcher');'''
replace_once(script_anchor, script_replacement, 'admin JavaScript restoration')

if 'Explore the Platform →' in text or 'Open SethiPortfolio →' in text:
    raise SystemExit('Redundant hero CTA remains')
if text.count('>Sign In</button>') != 1:
    raise SystemExit('Expected one header Sign In button')
if text.count('id="login-modal"') != 1 or text.count('id="admin-login-form"') != 1:
    raise SystemExit('Admin modal was not restored correctly')
if "localStorage.setItem('sethiway_vault_key', password)" not in text or "window.location.href = 'admin.html'" not in text:
    raise SystemExit('Admin dashboard handoff is missing')
if '—' in text:
    raise SystemExit('Em dash remains in homepage copy')

path.write_text(text)
