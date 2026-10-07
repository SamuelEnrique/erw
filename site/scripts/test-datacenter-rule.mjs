// Energy Research Warehouse (ERW) site, session 140: the flexible load judged on a forecast (/cost-of-power), tested
// on the saved real samples of session 138 (tests/fixtures/session138: ERCOT HB_HUBAVG, every hour of 2021 and of
// 2025, real time and day-ahead). No request, no browser.
//
//   node scripts/test-datacenter-rule.mjs
//
//   1. the forecast rule never uses a price from the hour it decides: the real-time prices can be replaced by any
//      numbers and no decision changes; a day's threshold is fixed before the day (no price of that day or of a later
//      day moves it); the decisions up to a day are the same when every later hour is cut away; an hour's own
//      day-ahead price, published the day before, is the only price of its day the decision reads;
//   2. the threshold of a day is the k-th dearest day-ahead hour of the prior 30 days, worked by hand for a real day;
//   3. the first 30 days, and a day whose prior 30 days are not held, are not decided: the load runs;
//   4. the load is never off in more hours of a year than the reader named, and once they are used it runs; so the
//      rule never beats the same number of hours chosen with perfect foresight; a shifting load never beats the day's
//      own best shift, and pays exactly that when it buys day-ahead;
//   5. the 30 days are read across the boundary between two years' files;
//   6. the clean share of a load's own hours: a flat load meets the mean of the hours' shares, an hour the load is
//      off in does not count, and an hour whose share is not held is left out, never filled.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const L = await import("../lib/datacenter.ts");
const fx = (y) => JSON.parse(fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "session138", `ercot_HB_HUBAVG_${y}.json`), "utf8"));
const F = { 2021: fx(2021), 2025: fx(2025) };

let failed = 0;
const ok = (cond, what) => { console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed++; };
const close = (a, b, tol = 1e-9) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b));
const same = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);
const FLAT = { run: "flat", n: 0, pct: 0, shift: 0 };
const OFF = [{ run: "hours", n: 100, pct: 0, shift: 0 }, { run: "hours", n: 500, pct: 0, shift: 0 }, { run: "share", n: 0, pct: 5, shift: 0 }];
const SHIFT = { run: "shift", n: 0, pct: 0, shift: 20 };
const TRIES = [...OFF, SHIFT];
const WINDOW = 24 * L.PRIOR_DAYS;

for (const y of [2021, 2025]) {
  const rt = L.expand(F[y], "HB_HUBAVG", "rt"), da = L.expand(F[y], "HB_HUBAVG", "da");

  // 1a. the settled price of an hour is never read: any real-time prices give the same decisions
  const noise = rt.map((v, i) => (v === null ? null : ((i * 7919) % 1000) - 250));
  ok(TRIES.every((x) => same(L.ruleWeights([rt], [da], x).w[0], L.ruleWeights([noise], [da], x).w[0])),
    `${y}: with every real-time price replaced by another number, no decision of ${TRIES.length} loads changes`);

  // 1b. a day's threshold is fixed before the day: a price of that day, or of any later day, does not move it
  const day0 = 200, h0 = 24 * day0 + 17, bumped = da.slice();
  for (let i = 24 * day0; i < da.length; i++) if (bumped[i] !== null) bumped[i] = bumped[i] * 3 + 500;
  ok(OFF.every((x) => same(L.ruleThresholds([da], x)[0].slice(0, day0 + 1), L.ruleThresholds([bumped], x)[0].slice(0, day0 + 1))),
    `${y}: with every day-ahead price from day ${day0 + 1} on changed, the thresholds of that day and of every day before are unchanged`);
  const one = da.slice();
  one[h0] = 9000;
  let before = true;
  for (const x of TRIES) {
    const a = L.ruleWeights([rt], [da], x).w[0], b = L.ruleWeights([rt], [one], x).w[0];
    for (let i = 0; i < 24 * day0; i++) if (a[i] !== b[i]) before = false;
  }
  ok(before, `${y}: changing one hour's day-ahead price changes no decision of any day before it`);
  const early = da.slice(), e0 = 24 * 35 + 17;
  early[e0] = 9000;
  ok(OFF.every((x) => L.ruleWeights([rt], [early], x).w[0][e0] === 0), `${y}: an hour whose day-ahead price is 9,000, on day 36 with its year's hours not yet used, is shed`);

  // 1c. no look-ahead: the decisions up to a day are the same whatever every later price is
  const cut = 24 * 150;
  const later = (p) => p.map((v, i) => (i < cut || v === null ? v : ((i * 104729) % 3000) - 100));
  ok(TRIES.every((x) => same(L.ruleWeights([rt], [da], x).w[0].slice(0, cut), L.ruleWeights([later(rt)], [later(da)], x).w[0].slice(0, cut))),
    `${y}: the first 150 days' decisions are the same with every later price, day-ahead and real time, replaced by another number`);

  // 2. the threshold by hand, for a day and 100 hours a year; the hours shed that day are those at or above it,
  // dearest first, as far as the year's hours left allow
  const x100 = OFF[0], th = L.ruleThresholds([da], x100)[0];
  const w = L.ruleWeights([rt], [da], x100).w[0];
  let byHand = true, shown = "", used = 0;
  for (let n = 0; n < th.length; n++) {
    const d = 24 * n;
    if (th[n] === null) continue;
    const prior = da.slice(d - WINDOW, d).filter((v) => v !== null).sort((a, b) => b - a);
    const k = Math.max(1, Math.round((100 / 8760) * prior.length));
    if (th[n] !== prior[k - 1] || k !== 8) byHand = false;
    const over = [];
    for (let i = d; i < d + 24; i++) if (da[i] !== null && da[i] >= th[n] && rt[i] !== null) over.push(i);
    over.sort((a, b) => da[b] - da[a] || a - b);
    const take = new Set(over.slice(0, Math.max(0, 100 - used)));
    for (let i = d; i < d + 24; i++) if ((take.has(i) ? 0 : rt[i] === null ? 0 : 1) !== w[i]) byHand = false;
    if (take.size && !shown) shown = `first on day ${n + 1}: ${take.size} hours at or above ${th[n].toFixed(2)} USD/MWh, the 8th dearest of the prior ${prior.length} hours`;
    used += take.size;
  }
  ok(byHand && used <= 100, `${y}: every day's threshold and every hour shed, worked by hand, are the rule's (${used} hours off; ${shown})`);

  // 3. the first 30 days are not decided
  const r = L.ruleWeights([rt], [da], x100);
  ok(r.undecided[0] === L.PRIOR_DAYS && r.w[0].slice(0, WINDOW).every((v, i) => v === (rt[i] === null ? 0 : 1)), `${y}: the first ${L.PRIOR_DAYS} days are not decided and the load runs in each of their hours held (${r.undecided[0]} days not decided, ${r.decided[0]} decided)`);
  const holed = da.slice();
  for (let i = 24 * 100; i < 24 * 110; i++) holed[i] = null;  // ten days of day-ahead prices not held
  const rh = L.ruleWeights([rt], [holed], x100), thh = L.ruleThresholds([holed], x100)[0];
  ok(thh[101] !== null && thh.slice(102, 130).every((v) => v === null) && thh[141] !== null && rh.undecided[0] > r.undecided[0], `${y}: with ten days of day-ahead prices missing, a day is decided while 95 percent of its prior 30 days are held (one missing day in 30 still is) and not decided otherwise (${rh.undecided[0]} days not decided)`);

  // 4. the budget, and the rule against perfect foresight
  for (const buy of ["rt", "da"]) {
    const pay = buy === "rt" ? rt : da;
    const flat = L.span(L.monthsOfYear(y, pay, L.weights(pay, FLAT)));
    for (const x of OFF) {
      const fw = L.ruleWeights([pay], [da], x).w[0];
      const f = L.span(L.monthsOfYear(y, pay, fw));
      const off = fw.filter((v, i) => v === 0 && pay[i] !== null).length, budget = L.shedBudget(x, pay.length);
      const sameHours = L.span(L.monthsOfYear(y, pay, L.weights(pay, { run: "hours", n: off, pct: 0, shift: 0 })));
      const asked = L.span(L.monthsOfYear(y, pay, L.weights(pay, x)));
      ok(off <= budget && f.down === off && f.per >= sameHours.per - 1e-9 && f.per >= asked.per - 1e-9,
        `${y} ${buy}: ${x.run} ${x.run === "hours" ? x.n : x.pct}: the rule was off in ${off} of the ${budget} hours allowed and paid ${f.per.toFixed(2)}; perfectly foreseen ${asked.per.toFixed(2)}; flat ${flat.per.toFixed(2)}: it kept ${(100 * (flat.per - f.per) / (flat.per - asked.per)).toFixed(0)} percent of the foreseen saving`);
    }
    const fs20 = L.span(L.monthsOfYear(y, pay, L.ruleWeights([pay], [da], SHIFT).w[0])), hs20 = L.span(L.monthsOfYear(y, pay, L.weights(pay, SHIFT)));
    ok(fs20.cost >= hs20.cost - 1e-6 && close(fs20.energy, flat.energy, 1e-12) && (buy !== "da" || close(fs20.cost, hs20.cost, 1e-9)),
      `${y} ${buy}: a load shifting 20 percent by day-ahead prices pays ${fs20.per.toFixed(2)}, never less than the day's own best shift (${hs20.per.toFixed(2)})${buy === "da" ? ", and exactly that when it buys day-ahead" : ""}; flat ${flat.per.toFixed(2)}`);
  }
  // once the year's hours are used the load runs: with a budget of 5 hours, nothing is shed after the fifth
  const w5 = L.ruleWeights([rt], [da], { run: "hours", n: 5, pct: 0, shift: 0 }).w[0];
  const offAt = w5.map((v, i) => (v === 0 && rt[i] !== null ? i : -1)).filter((i) => i >= 0);
  ok(offAt.length === 5, `${y}: a load allowed 5 hours a year is off in exactly 5, the last on day ${Math.floor(offAt[4] / 24) + 1}, and runs in every hour after`);

  // 5. the 30 days are read across the boundary between two files
  const at = 24 * 180;
  ok(OFF.every((x) => { const a = L.ruleThresholds([da], x)[0], b = L.ruleThresholds([da.slice(0, at), da.slice(at)], x); return same(a, [...b[0], ...b[1]]); })
    && same(L.ruleWeights([rt], [da], SHIFT).w[0], L.ruleWeights([rt.slice(0, at), rt.slice(at)], [da.slice(0, at), da.slice(at)], SHIFT).w.flat()),
    `${y}: the year given as two files gives the thresholds the one file gives (the prior 30 days are read across the boundary)`);
}

// monthsRuled: the forecast and the hindsight months of the real files; a flat load is the same under both
{
  const files = [F[2021], F[2025]];
  const a = L.monthsRuled(files, "HB_HUBAVG", "rt", FLAT, "forecast"), b = L.monthsRuled(files, "HB_HUBAVG", "rt", FLAT, "hindsight");
  ok(a.months.length === 24 && a.months.every((r, i) => close(r.cost, b.months[i].cost)), "a flat load is the same under the rule and under foresight, in each of the 24 months held");
  const x = OFF[0];
  const f = L.monthsRuled(files, "HB_HUBAVG", "rt", x, "forecast"), h = L.monthsRuled(files, "HB_HUBAVG", "rt", x, "hindsight");
  const f21 = L.span(f.months.filter((r) => r.m.startsWith("2021"))), h21 = L.span(h.months.filter((r) => r.m.startsWith("2021")));
  ok(f21.per > h21.per && f21.per < f21.flat && f.da && f.decided > 600 && f21.down <= 100 && h21.down === 100,
    `2021, real time, 100 hours: the rule paid ${f21.per.toFixed(2)} USD/MWh (off in ${f21.down} hours), perfect foresight ${h21.per.toFixed(2)}, a flat load ${f21.flat.toFixed(2)} (${f.decided} days decided, ${f.undecided} not)`);
  const noDa = { ...F[2025], regions: { HB_HUBAVG: { rt: F[2025].regions.HB_HUBAVG.rt } } };
  const n = L.monthsRuled([noDa], "HB_HUBAVG", "rt", x, "forecast");
  ok(n.months.length === 0 && n.da === false, "a region with no day-ahead price gives no forecast figure for a flexible load, rather than a figure from another rule");
  const words = L.ruleWords(x);
  ok(words.includes("8th dearest") && words.includes("100 hours of the calendar year") && words.includes("never sees the price the hour settles at")
    && L.ruleWords(SHIFT).includes("4.8 dearest day-ahead hours") && L.ruleWords(FLAT) === "", "the rule is stated in words for the hover: the 8th dearest hour of the prior 30 days and the 100 hours of the year; 4.8 hours a day for a 20 percent shift");
}

// 6. the clean share of the load's own hours
{
  const p = [10, 20, null, 40, 50, 60], c = [50, null, 70, 80, 20, 100];
  const flat = L.cleanShare(c, p, [1, 1, 0, 1, 1, 1]);
  ok(close(flat.load, (50 + 80 + 20 + 100) / 4) && close(flat.flat, flat.load) && flat.hours === 4, "a flat load meets the mean of the hours' carbon-free shares, over the hours where price and share are both held (an hour without one of them is left out)");
  const off = L.cleanShare(c, p, [1, 1, 0, 1, 0, 1]);
  ok(close(off.load, (50 + 80 + 100) / 3) && close(off.flat, 62.5), "an hour the load is off in does not count toward its own share; the flat figure beside it is over the same hours");
  const shift = L.cleanShare(c, p, [2, 1, 0, 1, 0, 1]);
  ok(close(shift.load, (2 * 50 + 80 + 100) / 4), "energy moved into an hour counts with its weight");
  ok(L.cleanShare([null, null], [1, 2], [1, 1]).load === null, "no hour held: no figure");
  ok(same(L.expandSeries({ s: 2, v: [1, null, 3] }, 6), [null, null, 1, null, 3, null]), "a stored series is laid out by hour with nulls where not held");
}

console.log(failed ? `${failed} FAILED` : "all passed");
process.exit(failed ? 1 : 0);
