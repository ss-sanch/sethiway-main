// DOM integration regression: `node tests/test-stock-loading.cjs` (jsdom required).
'use strict';
const assert = require('node:assert/strict');
const { JSDOM, ResourceLoader, VirtualConsole } = require('jsdom');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const chart = { dates:['2025-10-01','2026-10-01'], opens:[90,99], highs:[101,101], lows:[89,98], closes:[100,100] };
const financials = { years:['2025','2026'] };
for(const metric of ['revenue','net','ebitda','gross_margin','op_margin','net_margin','fcf','ocf','capex','cash','debt','shares']) financials[metric]=[100,110];
const stock = {ticker:'MSFT',current_price:100,change:1,pct_change:1,shares:1000,fcf:100,
    financials,stats:{sethi_score:70},summary:'Test company',peers:[],insiders:[],chart_preview:chart,
    risk_profile:{daily_var_95:2,annualized_volatility:20},research:{},_meta:{served_from_cache:true}};
const plotStub = `window.Plotly={newPlot:plot,react:plot,purge(){},Plots:{resize(){}}};
function plot(target,data,layout){const el=typeof target==='string'?document.getElementById(target):target;if(el){el.data=data;el.layout=layout;el.on=()=>{};}return Promise.resolve(el);}`;
class Resources extends ResourceLoader {
    fetch(url){
        const parsed=new URL(url);
        if(parsed.hostname==='cdn.plot.ly')return Promise.resolve(Buffer.from(plotStub));
        if(parsed.hostname==='cdn.tailwindcss.com')return Promise.resolve(Buffer.from(''));
        if(parsed.hostname==='sethiway.com') {
            const file=path.join(root,parsed.pathname);
            return Promise.resolve(fs.existsSync(file)?fs.readFileSync(file):Buffer.from(''));
        }
        return null;
    }
}
const errors=[],warnings=[],requests=[];
let failed=false;
let probeAttempts=0;
function openPage() {
    const virtualConsole=new VirtualConsole();
    virtualConsole.on('jsdomError',error=>errors.push(error.message));
    virtualConsole.on('warn',text=>warnings.push(text));
    return new JSDOM(fs.readFileSync(path.join(root,'sethistock.html'),'utf8'),{
        url:'https://sethiway.com/sethistock.html',runScripts:'dangerously',resources:new Resources(),
        pretendToBeVisual:true,virtualConsole,
        beforeParse(window){
            window.AbortController=AbortController;
            window.Response=Response;
            window.crypto.randomUUID=require('node:crypto').randomUUID;
            window.fetch=async (input,init={})=>{
                const url=new URL(typeof input==='string'?input:input.url);requests.push(url.href);
                let payload={};let status=200;
                if(url.hostname.endsWith('supabase.co'))payload=[];
                else if(url.pathname==='/api/runtime/status') {
                    probeAttempts++;
                    // A transient platform failure must be retried without marking ready.
                    if(probeAttempts===1)throw new TypeError('Failed to fetch');
                    payload={process_uptime_seconds:1000};
                }
                else if(url.pathname==='/autocomplete')payload={results:[{symbol:'MSFT',name:'Name <img src=x onerror=alert(1)>'}]};
                else if(url.pathname.startsWith('/api/stock/')){payload=stock;if(failed){status=503;payload={detail:'Data provider temporarily unavailable'};}}
                else if(url.pathname.startsWith('/api/quote/')){payload={ticker:'MSFT',current_price:100,change:1,pct_change:1};if(failed){status=503;payload={detail:'Data provider temporarily unavailable'};}}
                else if(url.pathname.startsWith('/api/chart/'))payload=chart;
                else if(url.pathname.startsWith('/api/research/'))payload={ticker:'MSFT',earnings_reaction:{available:false},valuation_bands:{available:false}};
                else if(url.pathname==='/api/pillar-rates')payload={};
                else if(url.pathname.startsWith('/api/sec/'))payload={metrics:{},series:{},period:'annual'};
                return new Response(JSON.stringify(payload),{status,headers:{'content-type':'application/json'}});
            };
        }
    });
}
async function until(check){const end=Date.now()+6000;while(!check()){if(Date.now()>end)throw new Error('DOM wait timed out: '+check+'\n'+errors.join('\n'));await new Promise(resolve=>setTimeout(resolve,20));}}
(async()=>{
    let dom=openPage();
    try {
        let w=dom.window,d=w.document;
        await until(()=>w.__sethiStockRepeatCacheInstalled);
        assert.equal(d.getElementById('not-mounted'),null);
        assert.equal(w.__sethiStockLastServerReadyAt,undefined,'Failed readiness must not mark ready');
        d.getElementById('ticker-input').value='msft';w.fetchSuggestions('msft');
        await until(()=>d.querySelector('#search-suggestions li'));
        assert.equal(d.querySelectorAll('#search-suggestions img').length,0,'Provider names must be plain text');
        d.querySelector('#search-suggestions li').click();
        await until(()=>d.getElementById('display-ticker').innerText==='MSFT'&&!d.getElementById('search-btn').disabled);
        await new Promise(resolve=>setTimeout(resolve,500));
        assert.equal(d.getElementById('stat-var').innerText,'2%');
        assert.equal(d.getElementById('stat-vol').innerText,'20%');
        assert.ok(probeAttempts>=2);
        assert.ok(!requests.some(url=>url.includes('sethistock-backend.onrender.com')));
        assert.ok(!warnings.some(text=>/Null-Shield|GHOST ID/.test(text)),warnings.join('\n'));
        assert.deepEqual(errors,[]);
        assert.ok(!d.getElementById('error-message').innerText,d.getElementById('error-message').innerText);
        dom.window.close();
        failed=true;dom=openPage();w=dom.window;d=w.document;
        await until(()=>w.__sethiStockRepeatCacheInstalled);
        d.getElementById('ticker-input').value='MSFT';d.getElementById('search-form').requestSubmit();
        await until(()=>!d.getElementById('search-btn').disabled);
        assert.match(d.getElementById('error-message').innerText,/Data provider temporarily unavailable/);
        assert.deepEqual(errors,[]);
        console.log('Stock loading DOM checks passed: readiness retry, native DOM, autocomplete selection, safe labels, full hydration and failure recovery.');
    } finally {dom.window.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
