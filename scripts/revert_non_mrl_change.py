from pathlib import Path
p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')
old = '<section id="section-portfolio" class="scroll-mt-24 mb-16">\n            <div class="max-w-[1800px] mx-auto pt-8 border-t border-gray-200 mb-4 flex flex-col lg:flex-row lg:items-center gap-4">'
new = '<section id="section-portfolio" class="scroll-mt-24 mb-16">\n            <div class="max-w-7xl mx-auto pt-10 border-t border-gray-200 mb-6 flex flex-col lg:flex-row lg:items-center gap-6">'
if old not in s:
    raise SystemExit('Expected Portfolio Optimiser header pattern not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Reverted unrelated Portfolio Optimiser layout change.')
