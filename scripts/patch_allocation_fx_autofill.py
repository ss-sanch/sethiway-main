from pathlib import Path

p=Path('sethiportfolio-admin.html')
s=p.read_text(encoding='utf-8')
old="""                if(['GBP','USD','EUR'].includes(data.currency)){ el('allocation-target-currency').value=data.currency; }\n                if(data.currency==='GBP') el('allocation-target-fx').value='1';\n                el('allocation-target-price').value=Number(data.reference_close).toFixed(4);\n                status.textContent=`✓ Verified · ${data.name}${data.exchange?' · '+data.exchange:''} · ${data.currency}${previous}`;\n"""
new="""                if(['GBP','USD','EUR'].includes(data.currency)){ el('allocation-target-currency').value=data.currency; }\n                el('allocation-target-fx').value=Number(data.fx_rate_to_base||1).toFixed(6);\n                el('allocation-target-price').value=Number(data.reference_close).toFixed(4);\n                const fxInfo=data.currency==='GBP' ? ' · FX 1.000000' : ` · FX ${Number(data.fx_rate_to_base).toFixed(6)} ${data.currency}/GBP${data.fx_used_previous_session?' from '+prettyDate(data.fx_price_date):' on '+prettyDate(data.fx_price_date)}`;\n                status.textContent=`✓ Verified · ${data.name}${data.exchange?' · '+data.exchange:''} · ${data.currency}${previous}${fxInfo}`;\n"""
if old not in s: raise SystemExit('target verification block missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('allocation FX autofill patched')
