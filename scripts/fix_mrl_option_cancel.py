from pathlib import Path
p = Path('sethiquant.html')
s = p.read_text(encoding='utf-8')
s = s.replace("onclick=\"toggleModal('modal-risk-options')\" class=\"absolute top-4 right-4", "onclick=\"cancelRiskOptions()\" class=\"absolute top-4 right-4", 1)
s = s.replace("        let activeRiskOptions = [];\n", "        let activeRiskOptions = [];\n        let riskOptionsSnapshot = [];\n", 1)
s = s.replace("        function openOptionsOverlay() {\n            renderRiskOptionsEditor();", "        function openOptionsOverlay() {\n            riskOptionsSnapshot = JSON.parse(JSON.stringify(activeRiskOptions));\n            renderRiskOptionsEditor();", 1)
marker = "        function addRiskOption() {\n"
insert = "        function cancelRiskOptions() {\n            activeRiskOptions = JSON.parse(JSON.stringify(riskOptionsSnapshot));\n            updateOptionBadge();\n            toggleModal('modal-risk-options');\n        }\n\n"
if marker not in s:
    raise SystemExit('addRiskOption marker not found')
s = s.replace(marker, insert + marker, 1)
p.write_text(s, encoding='utf-8')
for marker in ['riskOptionsSnapshot', 'function cancelRiskOptions()', 'onclick="cancelRiskOptions()"']:
    if marker not in s:
        raise SystemExit(f'Missing marker {marker}')
print('Option modal cancel state fixed.')
