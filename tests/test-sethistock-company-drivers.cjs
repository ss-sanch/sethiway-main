// Regression checks for the public Phase 3E Revenue Drivers module.
// No browser or network required: evaluate only its pure helpers in a Node VM.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const original = fs.readFileSync(path.join(root, 'sethistock-company-drivers.js'), 'utf8');
const hook = '    window.SethiStockCompanyDrivers = {';
assert.equal(original.split(hook).length - 1, 1, 'The module API hook must be unique');
const source = original.replace(hook, [
    '    window.__driverTest = { finiteNumber, comparablePrior, yoyChange, renderHistoryErrorCard,',
    '        get requestId() { return requestId; } };',
    hook
].join('\n'));

const card = {
    children: [],
    replaceChildren() { this.children = []; },
    appendChild(child) { this.children.push(child); }
};
const document = {
    readyState: 'loading',
    addEventListener() {},
    querySelector(selector) { return selector === '#driver-card-sample' ? card : null; },
    querySelectorAll() { return []; },
    createElement(tag) {
        return {
            tag, children: [], className: '', textContent: '',
            append(...nodes) { this.children.push(...nodes); },
            appendChild(node) { this.children.push(node); }
        };
    },
    body: { classList: { remove() {} } }
};
const window = {};
const context = { document, window, URLSearchParams, AbortController, Intl, Date,
    CSS: { escape: value => value }, console, setTimeout };
vm.runInNewContext(source, context, { filename: 'sethistock-company-drivers.js' });
const helpers = window.__driverTest;
assert.ok(helpers, 'Driver test hooks were not installed');

// Blank disclosures must never become misleading zero points.
for (const value of [null, undefined, '', '  ', 'N/A', Number.NaN, Infinity]) {
    assert.equal(helpers.finiteNumber(value), null);
}
assert.equal(helpers.finiteNumber('0'), 0);
assert.equal(helpers.finiteNumber(0), 0);
assert.equal(helpers.finiteNumber('125000'), 125000);

// A true quarter/year match supports YoY; an adjacent quarter does not.
const latest = { end: '2026-06-30', period_type: 'quarter', value: 200 };
const previous = { end: '2025-06-30', period_type: 'quarter', value: 100 };
assert.equal(helpers.yoyChange({ display_format: 'currency' }, [previous, latest]).value, 100);
assert.equal(helpers.comparablePrior(
    [{ end: '2025-03-31', period_type: 'quarter', value: 100 }, latest], latest
), null);
assert.equal(helpers.comparablePrior(
    [{ end: '2025-06-30', period_type: 'annual', value: 100 }, latest], latest
), null);
assert.equal(helpers.yoyChange({ display_format: 'currency' },
    [{ end: '2025-06-30', period_type: 'quarter', value: null }, latest]), null);
assert.equal(helpers.yoyChange({ display_format: 'percentage' },
    [{ ...previous, value: 12 }, { ...latest, value: 15 }]).value, 3);

// A non-calendar fiscal-year end is still valid in annual mode.
window.SethiStockCompanyDrivers.setPeriod('annual');
const yearEnd = { end: '2026-01-25', period_type: 'annual', value: 110 };
const precedingYearEnd = { end: '2025-01-26', period_type: 'annual', value: 100 };
assert.equal(helpers.yoyChange({ display_format: 'currency' },
    [precedingYearEnd, yearEnd]).value, 10);

// Failed individual histories cannot leave their chart skeleton spinning.
helpers.renderHistoryErrorCard({ key: 'sample', label: 'Sample driver' });
assert.equal(card.children.length, 1);
assert.equal(card.children[0].children[0].textContent, 'Sample driver');
assert.match(card.children[0].children[1].textContent, /could not be loaded/);

// Closing the modal invalidates outstanding asynchronous loads.
const beforeClose = helpers.requestId;
window.SethiStockCompanyDrivers.close();
assert.equal(helpers.requestId, beforeClose + 1);

// Keep the existing low-cost, on-demand integration intact.
const financial = fs.readFileSync(path.join(root, 'sethistock-financial-history.js'), 'utf8');
const history = fs.readFileSync(path.join(root, 'sethiway-history.js'), 'utf8');
assert.match(financial, /id="financial-segment-button"/);
assert.match(financial, /SethiStockOpenRevenueDrivers/);
assert.match(history, /sethistock-company-drivers\.js/);
console.log('Phase 3E Company Drivers regression checks passed.');
