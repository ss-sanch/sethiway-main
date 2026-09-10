from pathlib import Path

p = Path('index.html')
s = p.read_text()

old_nav = '''    <nav class="sticky top-0 z-50 border-b border-gray-200 bg-white/95 backdrop-blur">
        <div class="max-w-[1720px] mx-auto px-6 lg:px-10 h-20 flex items-center justify-between gap-8 relative">
            <a href="#top" class="flex items-center shrink-0">
                <img src="logo.png" alt="SethiWay" class="h-10 w-auto invert">
            </a>
            <div class="hidden md:flex items-center gap-8 text-sm font-bold text-gray-600 absolute left-1/2 -translate-x-1/2">
                <a href="#platform" class="hover:text-blue-600 transition">Platform</a>
                <a href="#about" class="hover:text-blue-600 transition">About</a>
                <a href="#feedback" class="hover:text-blue-600 transition">Feedback</a>
            </div>
            <button type="button" onclick="openAdminModal()" class="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-bold hover:bg-blue-600 transition shrink-0">Sign In</button>
        </div>
    </nav>'''

new_nav = '''    <nav id="site-nav" class="sticky top-0 z-50 border-b border-gray-200 bg-white/95 backdrop-blur">
        <div class="max-w-[1720px] mx-auto px-6 lg:px-10 h-20 flex items-center justify-between gap-4 md:gap-8 relative">
            <a href="#top" class="flex items-center shrink-0">
                <img src="logo.png" alt="SethiWay" class="h-9 sm:h-10 w-auto invert">
            </a>
            <div class="hidden md:flex items-center gap-8 text-sm font-bold text-gray-600 absolute left-1/2 -translate-x-1/2">
                <a href="#platform" class="hover:text-blue-600 transition">Platform</a>
                <a href="#about" class="hover:text-blue-600 transition">About</a>
                <a href="#feedback" class="hover:text-blue-600 transition">Feedback</a>
            </div>
            <div class="flex items-center gap-2 sm:gap-3 shrink-0">
                <button type="button" onclick="openAdminModal()" class="hidden sm:inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-bold hover:bg-blue-600 transition">Sign In</button>
                <button id="mobile-nav-trigger" type="button" class="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-700 transition hover:border-blue-200 hover:text-blue-600" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open navigation">
                    <svg id="mobile-nav-open-icon" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                    <svg id="mobile-nav-close-icon" class="hidden h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
        </div>
        <div id="mobile-nav" class="hidden md:hidden border-t border-gray-100 bg-white">
            <div class="max-w-[1720px] mx-auto px-6 py-3">
                <div class="grid gap-1 text-sm font-bold text-gray-700">
                    <a href="#platform" class="mobile-nav-link rounded-lg px-3 py-2.5 transition hover:bg-gray-50 hover:text-blue-600">Platform</a>
                    <a href="#about" class="mobile-nav-link rounded-lg px-3 py-2.5 transition hover:bg-gray-50 hover:text-blue-600">About</a>
                    <a href="#feedback" class="mobile-nav-link rounded-lg px-3 py-2.5 transition hover:bg-gray-50 hover:text-blue-600">Feedback</a>
                    <button type="button" onclick="closeMobileNav(); openAdminModal();" class="sm:hidden mt-1 rounded-lg bg-gray-900 px-3 py-2.5 text-left text-white transition hover:bg-blue-600">Sign In</button>
                </div>
            </div>
        </div>
    </nav>'''

assert old_nav in s
s = s.replace(old_nav, new_nav, 1)

script_anchor = '''<script>
    const commandPalette = document.getElementById('command-palette');'''
mobile_js = '''<script>
    const siteNav = document.getElementById('site-nav');
    const mobileNav = document.getElementById('mobile-nav');
    const mobileNavTrigger = document.getElementById('mobile-nav-trigger');
    const mobileNavOpenIcon = document.getElementById('mobile-nav-open-icon');
    const mobileNavCloseIcon = document.getElementById('mobile-nav-close-icon');

    function setMobileNav(open) {
        mobileNav.classList.toggle('hidden', !open);
        mobileNavTrigger.setAttribute('aria-expanded', open ? 'true' : 'false');
        mobileNavTrigger.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
        mobileNavOpenIcon.classList.toggle('hidden', open);
        mobileNavCloseIcon.classList.toggle('hidden', !open);
    }

    function closeMobileNav() {
        setMobileNav(false);
    }

    mobileNavTrigger.addEventListener('click', () => {
        setMobileNav(mobileNav.classList.contains('hidden'));
    });

    document.querySelectorAll('.mobile-nav-link').forEach(link => {
        link.addEventListener('click', closeMobileNav);
    });

    document.addEventListener('click', event => {
        if (!mobileNav.classList.contains('hidden') && !siteNav.contains(event.target)) closeMobileNav();
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !mobileNav.classList.contains('hidden')) closeMobileNav();
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth >= 768) closeMobileNav();
    });

    const commandPalette = document.getElementById('command-palette');'''
assert script_anchor in s
s = s.replace(script_anchor, mobile_js, 1)

old_cards = '''                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <a href="#top" onclick="setTimeout(() => document.getElementById('launcher-ticker').focus(), 250)" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Company Search</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Search Quick Launch by company name or ticker and choose the matching security.</p>
                    </a>

                    <button type="button" onclick="openCommandPalette()" class="group rounded-2xl border border-gray-200 bg-white p-5 text-left shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Command Palette</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Use Ctrl or Cmd + K to jump to a tool, section or ticker.</p>
                    </button>

                    <a href="#top" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Continue Shortcut</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Return to the last SethiWay tool, stock or section you were using.</p>
                    </a>
                </div>'''

new_cards = '''                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button type="button" onclick="if (window.innerWidth < 768) { window.scrollTo({ top: 0, behavior: 'smooth' }); setTimeout(() => setMobileNav(true), 350); }" class="group rounded-2xl border border-gray-200 bg-white p-5 text-left shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Mobile Navigation</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Platform, About, Feedback and Sign In are now accessible from smaller screens.</p>
                    </button>

                    <a href="#top" onclick="setTimeout(() => document.getElementById('launcher-ticker').focus(), 250)" class="group rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Company Search</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Search Quick Launch by company name or ticker and choose the matching security.</p>
                    </a>

                    <button type="button" onclick="openCommandPalette()" class="group rounded-2xl border border-gray-200 bg-white p-5 text-left shadow-sm hover:border-blue-200 hover:shadow-md transition">
                        <div class="flex items-center justify-between gap-3">
                            <span class="text-[10px] font-black uppercase tracking-[0.16em] text-gray-400">Hub</span>
                            <span class="text-blue-600 group-hover:translate-x-0.5 transition-transform">→</span>
                        </div>
                        <h3 class="mt-3 text-lg font-black text-gray-950">Command Palette</h3>
                        <p class="mt-2 text-sm leading-relaxed text-gray-500">Use Ctrl or Cmd + K to jump to a tool, section or ticker.</p>
                    </button>
                </div>'''

assert old_cards in s
s = s.replace(old_cards, new_cards, 1)

assert '—' not in s
p.write_text(s)
