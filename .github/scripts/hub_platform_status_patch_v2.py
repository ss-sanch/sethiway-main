from pathlib import Path
p=Path('index.html')
s=p.read_text()
old='''            <button type="button" onclick="openAdminModal()" class="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-bold hover:bg-blue-600 transition shrink-0">Sign In</button>'''
new='''            <div class="flex items-center gap-3 shrink-0">
                <button id="platform-status-trigger" type="button" class="inline-flex items-center gap-2 text-xs font-bold text-gray-500 hover:text-gray-900 transition" aria-haspopup="dialog" aria-controls="platform-status-modal">
                    <span id="platform-status-dot" class="h-2 w-2 rounded-full bg-gray-300"></span>
                    <span id="platform-status-label">Checking status</span>
                </button>
                <button type="button" onclick="openAdminModal()" class="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-bold hover:bg-blue-600 transition">Sign In</button>
            </div>'''
assert old in s
s=s.replace(old,new,1)
anchor='''    <div id="login-modal" class="hidden fixed inset-0 z-[100] items-center justify-center bg-gray-950/55 px-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="admin-login-title">'''
modal='''    <div id="platform-status-modal" class="hidden fixed inset-0 z-[110] items-center justify-center bg-gray-950/40 px-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="platform-status-title">
        <div class="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl">
            <div class="flex items-start justify-between gap-4">
                <div><p class="text-[10px] font-black uppercase tracking-[0.18em] text-blue-600">Platform Status</p><h2 id="platform-status-title" class="mt-1 text-2xl font-black">Live services</h2><p class="mt-2 text-sm text-gray-500">Checks the data services behind SethiWay.</p></div>
                <button id="platform-status-close" type="button" class="rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs font-bold text-gray-500 hover:text-gray-900">Esc</button>
            </div>
            <div class="mt-5 divide-y divide-gray-100 rounded-xl border border-gray-200">
                <div class="flex items-center justify-between gap-4 px-4 py-4"><div><p class="text-sm font-black">Macro data service</p><p class="mt-0.5 text-xs text-gray-400">SethiMacro</p></div><div class="flex items-center gap-2"><span id="macro-status-dot" class="h-2 w-2 rounded-full bg-gray-300"></span><span id="macro-status-label" class="text-xs font-bold text-gray-500">Checking</span></div></div>
                <div class="flex items-center justify-between gap-4 px-4 py-4"><div><p class="text-sm font-black">Markets and portfolio service</p><p class="mt-0.5 text-xs text-gray-400">SethiStock, SethiPortfolio and SethiQuant</p></div><div class="flex items-center gap-2"><span id="markets-status-dot" class="h-2 w-2 rounded-full bg-gray-300"></span><span id="markets-status-label" class="text-xs font-bold text-gray-500">Checking</span></div></div>
            </div>
            <div class="mt-5 flex items-center justify-between gap-4"><p id="platform-status-updated" class="text-xs text-gray-400">Checking live services...</p><button id="platform-status-recheck" type="button" class="rounded-lg bg-gray-900 px-4 py-2 text-xs font-black text-white hover:bg-blue-600 transition">Recheck</button></div>
        </div>
    </div>

'''
assert anchor in s
s=s.replace(anchor,modal+anchor,1)
anchor2="    const adminModal = document.getElementById('login-modal');"
js=r'''    const platformStatusTrigger=document.getElementById('platform-status-trigger');
    const platformStatusModal=document.getElementById('platform-status-modal');
    const platformStatusClose=document.getElementById('platform-status-close');
    const platformStatusRecheck=document.getElementById('platform-status-recheck');
    const platformStatusDot=document.getElementById('platform-status-dot');
    const platformStatusLabel=document.getElementById('platform-status-label');
    const platformStatusUpdated=document.getElementById('platform-status-updated');
    const statusTargets={macro:{url:'https://sethimacro.sethiway.com/api/pillar-jobs',dot:document.getElementById('macro-status-dot'),label:document.getElementById('macro-status-label')},markets:{url:'https://sethistock-api.onrender.com/openapi.json',dot:document.getElementById('markets-status-dot'),label:document.getElementById('markets-status-label')}};
    const STATUS_CACHE_KEY='sethiwayPlatformStatus',STATUS_CACHE_MS=5*60*1000;
    function setServiceStatus(t,v){t.dot.className='h-2 w-2 rounded-full '+(v==='up'?'bg-emerald-500':v==='down'?'bg-red-500':'bg-gray-300');t.label.textContent=v==='up'?'Operational':v==='down'?'Unavailable':'Checking';t.label.className='text-xs font-bold '+(v==='up'?'text-emerald-700':v==='down'?'text-red-600':'text-gray-500');}
    function renderOverallStatus(r,at){const v=Object.values(r),all=v.length&&v.every(x=>x==='up'),bad=v.some(x=>x==='down');platformStatusDot.className='h-2 w-2 rounded-full '+(all?'bg-emerald-500':bad?'bg-amber-500':'bg-gray-300');platformStatusLabel.textContent=all?'Operational':bad?'Check status':'Checking status';if(at){const t=new Date(at).toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'});platformStatusUpdated.textContent=`Last checked ${t}`;}}
    function readCachedPlatformStatus(){try{const c=JSON.parse(sessionStorage.getItem(STATUS_CACHE_KEY)||'null');return c&&c.results&&c.checkedAt&&Date.now()-c.checkedAt<STATUS_CACHE_MS?c:null;}catch{return null;}}
    async function checkService(url){const c=new AbortController(),timer=setTimeout(()=>c.abort(),20000);try{const r=await fetch(url,{cache:'no-store',signal:c.signal});return r.ok?'up':'down';}catch{return'down';}finally{clearTimeout(timer);}}
    async function checkPlatformStatus(force=false){if(!force){const c=readCachedPlatformStatus();if(c){Object.entries(c.results).forEach(([k,v])=>setServiceStatus(statusTargets[k],v));renderOverallStatus(c.results,c.checkedAt);return;}}platformStatusRecheck.disabled=true;platformStatusRecheck.textContent='Checking...';Object.values(statusTargets).forEach(t=>setServiceStatus(t,'checking'));renderOverallStatus({},null);platformStatusUpdated.textContent='Checking live services...';const entries=await Promise.all(Object.entries(statusTargets).map(async([k,t])=>[k,await checkService(t.url)]));const results=Object.fromEntries(entries),checkedAt=Date.now();Object.entries(results).forEach(([k,v])=>setServiceStatus(statusTargets[k],v));renderOverallStatus(results,checkedAt);try{sessionStorage.setItem(STATUS_CACHE_KEY,JSON.stringify({results,checkedAt}));}catch{}platformStatusRecheck.disabled=false;platformStatusRecheck.textContent='Recheck';}
    function openPlatformStatus(){platformStatusModal.classList.remove('hidden');platformStatusModal.classList.add('flex');}
    function closePlatformStatus(){platformStatusModal.classList.add('hidden');platformStatusModal.classList.remove('flex');}
    platformStatusTrigger.addEventListener('click',openPlatformStatus);platformStatusClose.addEventListener('click',closePlatformStatus);platformStatusRecheck.addEventListener('click',()=>checkPlatformStatus(true));platformStatusModal.addEventListener('click',e=>{if(e.target===platformStatusModal)closePlatformStatus();});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!platformStatusModal.classList.contains('hidden'))closePlatformStatus();});checkPlatformStatus();

'''
assert anchor2 in s
s=s.replace(anchor2,js+anchor2,1)
assert '—' not in s
p.write_text(s)
