from pathlib import Path
import re

path = Path('sethistock.html')
text = path.read_text()
pattern = re.compile(r'    function ensureResearchUI\(\) \{.*?\n    \}\n\n    function setResearchStatus', re.S)
replacement = '''    function ensureResearchUI() {
        return; // Retired: P/E History and Earnings Surprise now live in Key Financial Metrics.
    }

    function setResearchStatus'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'Expected one ensureResearchUI cleanup, got {count}')
path.write_text(text)
print('PHASE4C_RESEARCH_UI_CLEANED')
