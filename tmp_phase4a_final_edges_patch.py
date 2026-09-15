from pathlib import Path
import re

path = Path('sethistock-financial-history.js')
text = path.read_text(encoding='utf-8')

old = '''    function researchPayloadSettled(payload) {
        const earnings = payload?.earnings_reaction;
        const valuation = payload?.valuation_bands;
        const studySettled = (study, dataKey) => {
            if (!study || typeof study !== 'object') return false;
            if (study.available === true) return Array.isArray(study[dataKey]);
            if (study.available === false) return typeof study.reason === 'string' && study.reason.trim().length > 0;
            return false;
        };
        return studySettled(earnings, 'events') && studySettled(valuation, 'observations');
    }
'''
new = '''    function researchPayloadSettled(payload) {
        const earnings = payload?.earnings_reaction;
        const valuation = payload?.valuation_bands;
        const studyHasData = (study, dataKey) => {
            if (!study || typeof study !== 'object' || study.available !== true) return false;
            return Array.isArray(study[dataKey]) && study[dataKey].length > 0;
        };
        return studyHasData(earnings, 'events') && studyHasData(valuation, 'observations');
    }

    function annualCategoryLabel(point, index = 0) {
        const label = String(point?.label || '').trim();
        const labelledYear = label.match(/(?:FY\\s*)?((?:19|20)\\d{2})/i);
        if (labelledYear) return labelledYear[1];
        const end = String(point?.end || '');
        const datedYear = end.match(/^((?:19|20)\\d{2})/);
        return datedYear ? datedYear[1] : (label || String(index + 1));
    }

    function collapseAnnualPlotPoints(points) {
        const byYear = new Map();
        (points || []).forEach((point, index) => {
            const category = annualCategoryLabel(point, index);
            const previous = byYear.get(category);
            // SEC can expose more than one annual context for the same fiscal year.
            // Keep the latest filing-period end so Plotly receives exactly one bar per year.
            if (!previous || String(point?.end || '') >= String(previous?.end || '')) {
                byYear.set(category, { ...point, annualCategory: category });
            }
        });
        return Array.from(byYear.values()).sort((a, b) => {
            const ay = Number(a.annualCategory);
            const by = Number(b.annualCategory);
            if (Number.isFinite(ay) && Number.isFinite(by)) return ay - by;
            return String(a.annualCategory).localeCompare(String(b.annualCategory));
        });
    }
'''
if old not in text:
    raise SystemExit('researchPayloadSettled block not found')
text = text.replace(old, new, 1)

pattern = re.compile(r'''    function traceForMetric\(view, key, name, colour, options = \{\}\) \{\n        const points = filterPointsToWindow\(validMetricPoints\(view, key\)\);\n        if \(!points\.length\) return null;\n        const annualBars = view\.period === 'annual' && options\.forceLine !== true;\n        const trace = \{\n            x: points\.map\(point => point\.end\),\n            y: points\.map\(point => point\.value\),\n            name,\n            customdata: points\.map\(point => point\.label\),''')
replacement = '''    function traceForMetric(view, key, name, colour, options = {}) {
        const rawPoints = filterPointsToWindow(validMetricPoints(view, key));
        if (!rawPoints.length) return null;
        const annualBars = view.period === 'annual' && options.forceLine !== true;
        const points = annualBars ? collapseAnnualPlotPoints(rawPoints) : rawPoints;
        const trace = {
            x: annualBars ? points.map(point => point.annualCategory) : points.map(point => point.end),
            y: points.map(point => point.value),
            name,
            customdata: points.map(point => point.label),'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'traceForMetric prefix replacement count={count}')

path.write_text(text, encoding='utf-8')
print('PHASE4A_EDGE_PATCH_OK')
