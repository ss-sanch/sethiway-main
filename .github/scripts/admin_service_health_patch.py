from pathlib import Path

p=Path('admin.html')
s=p.read_text()

anchor='''        <!-- Chart Grid -->'''
block='''        <!-- SERVICE HEALTH -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 mb-8">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <p class="text-[10px] font-black uppercase tracking-[0.18em] text-blue-600">Service Health</p>
                    <h3 class="text-lg font-black text-gray-900 mt-1">Live data services</h3>
                    <p class="text-xs text-gray-400 mt-1">Checks the backends used by the public SethiWay tools.</p>
                </div>
                <div class="flex items-center gap-3">
                    <span id="service-health-updated" class="text-xs font-semibold text-gray-400">Not checked yet</span>
                    <button id="service-health-recheck" type="button" onclick="checkServiceHealth(true)" class="px-3 py-2 rounded-lg bg-gray-900 text-white text-xs font-black hover:bg-blue-600 transition">Recheck</button>
                </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-5">
                <div class="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 flex items-center justify-between gap-4">
                    <div><p class="text-sm font-black text-gray-900">SethiMacro</p><p class="text-xs text-gray-400 mt-0.5">Macro data service</p></div>
                    <div class="flex items-center gap-2"><span id="service-macro-dot" class="h-2 w-2 rounded-full bg-gray-300"></span><span id="service-macro-label" class="text-xs font-bold text-gray-500">Waiting</span></div>
                </div>
                <div class="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 flex items-center justify-between gap-4">
                    <div><p class="text-sm font-black text-gray-900">Markets and portfolio</p><p class="text-xs text-gray-400 mt-0.5">SethiStock, SethiPortfolio and SethiQuant</p></div>
                    <div class="flex items-center gap-2"><span id="service-markets-dot" class="h-2 w-2 rounded-full bg-gray-300"></span><span id="service-markets-label" class="text-xs font-bold text-gray-500">Waiting</span></div>
                </div>
            </div>
        </div>

'''
assert anchor in s
s=s.replace(anchor,block+anchor,1)

old='''                renderDashboard(data);'''
new='''                renderDashboard(data);
                checkServiceHealth();'''
assert old in s
s=s.replace(old,new,1)

js_anchor='''        async function refreshDashboard() {'''
js=r'''        const SERVICE_HEALTH_CACHE_KEY = 'sethiwayAdminServiceHealth';
        const SERVICE_HEALTH_CACHE_MS = 5 * 60 * 1000;
        const SERVICE_HEALTH_TARGETS = {
            macro: {
                url: 'https://sethimacro.sethiway.com/api/pillar-jobs',
                dot: () => document.getElementById('service-macro-dot'),
                label: () => document.getElementById('service-macro-label')
            },
            markets: {
                url: 'https://sethistock-api.onrender.com/openapi.json',
                dot: () => document.getElementById('service-markets-dot'),
                label: () => document.getElementById('service-markets-label')
            }
        };

        function renderServiceHealthItem(target, status) {
            const dot = target.dot();
            const label = target.label();
            if (!dot || !label) return;
            const checking = status === 'checking';
            const up = status === 'up';
            dot.className = `h-2 w-2 rounded-full ${checking ? 'bg-gray-300' : up ? 'bg-emerald-500' : 'bg-red-500'}`;
            label.textContent = checking ? 'Checking' : up ? 'Operational' : 'Unavailable';
            label.className = `text-xs font-bold ${checking ? 'text-gray-500' : up ? 'text-emerald-700' : 'text-red-600'}`;
        }

        async function pingService(url) {
            const controller = new AbortController();
            const timer = setTimeout(() => controller.abort(), 30000);
            try {
                const response = await fetch(url, { cache: 'no-store', signal: controller.signal });
                return response.ok ? 'up' : 'down';
            } catch (error) {
                return 'down';
            } finally {
                clearTimeout(timer);
            }
        }

        function readServiceHealthCache() {
            try {
                const cached = JSON.parse(sessionStorage.getItem(SERVICE_HEALTH_CACHE_KEY) || 'null');
                if (!cached || !cached.checkedAt || !cached.results) return null;
                return Date.now() - cached.checkedAt < SERVICE_HEALTH_CACHE_MS ? cached : null;
            } catch (error) {
                return null;
            }
        }

        function renderServiceHealthTimestamp(checkedAt) {
            const el = document.getElementById('service-health-updated');
            if (!el || !checkedAt) return;
            const time = new Date(checkedAt).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
            el.textContent = `Last checked ${time}`;
        }

        async function checkServiceHealth(force = false) {
            const button = document.getElementById('service-health-recheck');
            if (!force) {
                const cached = readServiceHealthCache();
                if (cached) {
                    Object.entries(cached.results).forEach(([key, value]) => renderServiceHealthItem(SERVICE_HEALTH_TARGETS[key], value));
                    renderServiceHealthTimestamp(cached.checkedAt);
                    return;
                }
            }

            if (button) {
                button.disabled = true;
                button.textContent = 'Checking...';
            }
            Object.values(SERVICE_HEALTH_TARGETS).forEach(target => renderServiceHealthItem(target, 'checking'));

            const entries = await Promise.all(Object.entries(SERVICE_HEALTH_TARGETS).map(async ([key, target]) => [key, await pingService(target.url)]));
            const results = Object.fromEntries(entries);
            const checkedAt = Date.now();
            Object.entries(results).forEach(([key, value]) => renderServiceHealthItem(SERVICE_HEALTH_TARGETS[key], value));
            renderServiceHealthTimestamp(checkedAt);
            try {
                sessionStorage.setItem(SERVICE_HEALTH_CACHE_KEY, JSON.stringify({ results, checkedAt }));
            } catch (error) {}
            if (button) {
                button.disabled = false;
                button.textContent = 'Recheck';
            }
        }

'''
assert js_anchor in s
s=s.replace(js_anchor,js+js_anchor,1)

p.write_text(s)
