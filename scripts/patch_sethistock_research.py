from pathlib import Path

path = Path("sethistock.html")
html = path.read_text(encoding="utf-8")
script_tag = '    <script src="sethistock-research.js?v=20260831"></script>\n'

if "sethistock-research.js" not in html:
    marker = "</body>"
    position = html.lower().rfind(marker)
    if position < 0:
        raise RuntimeError("Could not find closing </body> tag in sethistock.html")
    html = html[:position] + script_tag + html[position:]
    path.write_text(html, encoding="utf-8")
