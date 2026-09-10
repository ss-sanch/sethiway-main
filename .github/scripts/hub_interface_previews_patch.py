from pathlib import Path

p = Path('index.html')
s = p.read_text()

previews = [
    (
        '''                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-red-500">MACRO.</span></span>
                            </div>''',
        '''                            <div class="group relative h-48 overflow-hidden bg-gray-900 text-white">
                                <img src="assets/previews/sethimacro.jpg" alt="SethiMacro dashboard interface preview" loading="lazy" class="absolute inset-0 h-full w-full object-cover opacity-0 scale-[1.03] transition-all duration-500 ease-out group-hover:opacity-100 group-hover:scale-100">
                                <div class="absolute inset-0 flex items-center justify-center transition-opacity duration-300 group-hover:opacity-0">
                                    <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-red-500">MACRO.</span></span>
                                </div>
                            </div>'''
    ),
    (
        '''                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-green-500">STOCK.</span></span>
                            </div>''',
        '''                            <div class="group relative h-48 overflow-hidden bg-gray-900 text-white">
                                <img src="assets/previews/sethistock.jpg" alt="SethiStock analytics interface preview" loading="lazy" class="absolute inset-0 h-full w-full object-cover opacity-0 scale-[1.03] transition-all duration-500 ease-out group-hover:opacity-100 group-hover:scale-100">
                                <div class="absolute inset-0 flex items-center justify-center transition-opacity duration-300 group-hover:opacity-0">
                                    <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-green-500">STOCK.</span></span>
                                </div>
                            </div>'''
    ),
    (
        '''                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-yellow-500">PORTFOLIO.</span></span>
                            </div>''',
        '''                            <div class="group relative h-48 overflow-hidden bg-gray-900 text-white">
                                <img src="assets/previews/sethiportfolio.jpg" alt="SethiPortfolio risk analytics interface preview" loading="lazy" class="absolute inset-0 h-full w-full object-cover opacity-0 scale-[1.03] transition-all duration-500 ease-out group-hover:opacity-100 group-hover:scale-100">
                                <div class="absolute inset-0 flex items-center justify-center transition-opacity duration-300 group-hover:opacity-0">
                                    <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-yellow-500">PORTFOLIO.</span></span>
                                </div>
                            </div>'''
    ),
    (
        '''                            <div class="h-48 bg-gray-900 flex items-center justify-center text-white relative">
                                <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-blue-500">QUANT.</span></span>
                            </div>''',
        '''                            <div class="group relative h-48 overflow-hidden bg-gray-900 text-white">
                                <img src="assets/previews/sethiquant.jpg" alt="SethiQuant Market Risk Lab interface preview" loading="lazy" class="absolute inset-0 h-full w-full object-cover opacity-0 scale-[1.03] transition-all duration-500 ease-out group-hover:opacity-100 group-hover:scale-100">
                                <div class="absolute inset-0 flex items-center justify-center transition-opacity duration-300 group-hover:opacity-0">
                                    <span class="text-3xl font-black tracking-tighter">SETHI<span class="text-blue-500">QUANT.</span></span>
                                </div>
                            </div>'''
    ),
]

for old, new in previews:
    assert old in s
    s = s.replace(old, new, 1)

for filename in ('sethimacro.jpg', 'sethistock.jpg', 'sethiportfolio.jpg', 'sethiquant.jpg'):
    assert s.count(f'assets/previews/{filename}') == 1

assert '—' not in s
p.write_text(s)
