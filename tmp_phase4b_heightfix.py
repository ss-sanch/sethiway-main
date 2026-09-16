from pathlib import Path

path = Path('sethistock-company-drivers.js')
text = path.read_text()
old_desktop = "#driver-dialog { width:min(1240px,calc(100vw - 48px)); height:min(720px,calc(100vh - 72px)); max-height:calc(100vh - 48px); }"
new_desktop = "#driver-dialog { width:min(1240px,calc(100vw - 48px)); height:auto; max-height:min(720px,calc(100vh - 72px)); }"
old_mobile = "#driver-dialog { width:calc(100vw - 24px); height:calc(100vh - 32px); max-height:calc(100vh - 32px); }"
new_mobile = "#driver-dialog { width:calc(100vw - 24px); height:auto; max-height:calc(100vh - 32px); }"
if old_desktop not in text:
    raise SystemExit('desktop dialog sizing rule not found')
if old_mobile not in text:
    raise SystemExit('mobile dialog sizing rule not found')
text = text.replace(old_desktop, new_desktop, 1)
text = text.replace(old_mobile, new_mobile, 1)
path.write_text(text)
