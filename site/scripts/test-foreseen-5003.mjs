// Energy Research Warehouse (ERW) site, session 5003 (chain 233): "if perfectly foreseen" takes the rule's hour budget
// in a partial year (the owner's ruling of 12 October 2026; docs/methods/datacenter_pays_algorithm.md, section 10,
// item 15). No request, no model: lib/datacenter.ts's weights() on made-up years of prices.
//
//   node scripts/test-foreseen-5003.mjs        exits 1 if an assertion fails
import assert from "node:assert/strict";
const L = await import("../lib/datacenter.ts");

const year = (hours, held) => Array.from({ length: hours }, (_, i) => (i < held ? 10 + (i % 97) : null));
const off = (w) => w.filter((v, i) => v === 0).length;
const offHeld = (p, w) => w.filter((v, i) => v === 0 && p[i] !== null).length;

// a whole year of 8,760 hours: the budget of 100 hours is 100
let p = year(8760, 8760);
assert.equal(offHeld(p, L.weights(p, { run: "hours", n: 100, pct: 0, shift: 0 })), 100);
// a year held in part (7,500 of 8,760 hours): the rule's budget, 100, not the share 86 that session 138 gave
p = year(8760, 7500);
assert.equal(offHeld(p, L.weights(p, { run: "hours", n: 100, pct: 0, shift: 0 })), 100);
assert.equal(L.shedBudget({ run: "hours", n: 100, pct: 0, shift: 0 }, 8760), 100);
// a leap year: the rule's budget is round(100 x 8,784 / 8,760) = 100
p = year(8784, 3000);
assert.equal(offHeld(p, L.weights(p, { run: "hours", n: 100, pct: 0, shift: 0 })), L.shedBudget({ run: "hours", n: 100, pct: 0, shift: 0 }, 8784));
// never more than the hours held
p = year(8760, 40);
assert.equal(offHeld(p, L.weights(p, { run: "hours", n: 100, pct: 0, shift: 0 })), 40);
// a share: the rule's budget is the share of the year's hours, in a year held in part as well
p = year(8760, 4380);
assert.equal(offHeld(p, L.weights(p, { run: "share", n: 0, pct: 5, shift: 0 })), Math.round(0.05 * 8760));
// the hours chosen are the dearest held
p = year(8760, 8760);
const w = L.weights(p, { run: "hours", n: 10, pct: 0, shift: 0 });
const chosen = p.filter((v, i) => w[i] === 0), rest = p.filter((v, i) => w[i] !== 0);
assert.ok(Math.min(...chosen) >= Math.max(...rest));
// a flat load and a shift are as they were
assert.equal(off(L.weights(year(48, 48), { run: "flat", n: 0, pct: 0, shift: 0 })), 0);
console.log("test-foreseen-5003: 8 assertions passed");
