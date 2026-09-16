from pathlib import Path

path = Path('sethistock-financial-history.js')
text = path.read_text(encoding='utf-8')
old = """        button.classList.toggle('hidden', !supported);\n        button.disabled = !supported;\n"""
new = """        button.classList.toggle('hidden', !supported);\n        button.classList.toggle('inline-flex', supported);\n        button.disabled = !supported;\n"""
if old not in text:
    raise SystemExit('syncRevenueDriverButton anchor not found')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('PHASE4B_BUTTON_DISPLAY_PATCH_OK')
