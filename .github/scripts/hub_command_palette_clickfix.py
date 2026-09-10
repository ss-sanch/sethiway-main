from pathlib import Path

path = Path('index.html')
text = path.read_text()

bubble = '''                <div class="mt-4">\n                    <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-200 bg-blue-50 text-blue-700 text-[10px] font-black uppercase tracking-wider">\n                        <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>\n                        SethiPortfolio is now live\n                    </span>\n                </div>\n'''
if text.count(bubble) != 1:
    raise SystemExit(f'Live bubble expected once, found {text.count(bubble)}')
text = text.replace(bubble, '', 1)

bad_hover = "            button.addEventListener('mouseenter', () => { commandSelection = index; renderCommandPaletteResults(); });\n"
if text.count(bad_hover) != 1:
    raise SystemExit(f'Re-rendering mouseenter handler expected once, found {text.count(bad_hover)}')
text = text.replace(bad_hover, "            button.addEventListener('mouseenter', () => { commandSelection = index; });\n", 1)

if 'SethiPortfolio is now live' in text:
    raise SystemExit('Live bubble text still present')
if "button.addEventListener('click', () => openCommand(index));" not in text:
    raise SystemExit('Command result click handler missing')
if "mouseenter', () => { commandSelection = index; renderCommandPaletteResults();" in text:
    raise SystemExit('Destructive hover re-render still present')
if '—' in text:
    raise SystemExit('Em dash remains in homepage copy')

path.write_text(text)
