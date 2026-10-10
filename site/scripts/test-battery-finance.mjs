// Energy Research Warehouse (ERW) site, session 179: the finance of /cost-of-power/battery's scenarios
// (lib/battery/finance.ts) against cases computed by hand. No server, no browser, no network.
//
//   node scripts/test-battery-finance.mjs                 the assertions; exits 1 if any fails
//   node scripts/test-battery-finance.mjs --cases f.json  prints, as JSON, the results for the cases in f.json
//                                                         ([{ a: Assumptions, rev: USD per kW }]); tests/test_session179.py
//                                                         compares them with its Python mirror to 1e-6
import fs from "node:fs";

const F = await import("../lib/battery/finance.ts");

const at = process.argv.indexOf("--cases");
if (at > 0) {
  const cases = JSON.parse(fs.readFileSync(process.argv[at + 1], "utf-8"));
  const out = cases.map(({ a, rev }) => {
    const r = F.resultOf(a, rev);
    return { debt: r.debt, coverage: r.coverage, npv: r.npv, irr: r.irr, toll: r.toll, tail_years: r.tail.years, tail_pv: r.tail.pv, flows: F.flows(a, rev) };
  });
  console.log(JSON.stringify(out));
  process.exit(0);
}

let failed = 0;
function check(ok, what, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}
const near = (a, b, tol = 1e-9) => a !== null && b !== null && Math.abs(a - b) <= tol;

const d4 = F.defaultsOf({ capex: 1110, fom: 22 });
check(JSON.stringify(d4) === JSON.stringify({ capex: 1110, share: 60, rate: 8, term: 20, fom: 22, rte: 86, cycles: 1, deg: 0, life: 20, hurdle: 8 }), "the defaults of a 4-hour battery", JSON.stringify(d4));
check(F.KEYS.length === 10 && new Set(F.KEYS.map((k) => F.SPECS[k].letter)).size === 10, "ten assumptions, ten different letters");

// the capital recovery factor and the debt payment: 0.08 / (1 - 1.08^-20) = 0.101852209; 1,110 x 0.6 x that = 67.8336 a kW
check(near(F.crf(0.08, 20), 0.10185220882315059, 1e-12), "crf(8 percent, 20 years) = 0.101852209", String(F.crf(0.08, 20)));
check(near(F.crf(0, 20), 0.05), "crf at a rate of zero is 1 / years");
check(Math.round(F.debtService(d4) * 1000 * 100) === 6783357, "the default debt payment for 100 MW is the page's USD 6,783,357", String(F.debtService(d4) * 100000));
check(F.debtYears({ ...d4, term: 30 }) === 20 && near(F.debtService({ ...d4, term: 30 }), F.debtService(d4)), "a term longer than the life is cut to the life");

// net present value and the internal rate of return
check(near(F.npv(10, [-100, 110]), 0, 1e-12), "npv(10 percent, [-100, 110]) = 0");
check(near(F.npv(0, [-100, 50, 50, 50]), 50), "npv at zero is the plain sum");
check(near(F.npv(10, [0, 0, 121]), 100, 1e-9), "npv(10 percent, 121 in year 2) = 100");
check(near(F.irr([-100, 110]), 10, 1e-6), "irr([-100, 110]) = 10 percent", String(F.irr([-100, 110])));
check(near(F.irr([-100, 0, 121]), 10, 1e-6), "irr([-100, 0, 121]) = 10 percent");
const three = F.irr([-100, 50, 50, 50]);
check(near(three, 23.3751928, 1e-5) && near(F.npv(three, [-100, 50, 50, 50]), 0, 1e-6), "irr([-100, 50, 50, 50]) = 23.3752 percent, and the value there is zero", String(three));
check(F.irr([-100, -5, -5]) === null, "no rate of return when no year is positive");
check(F.irr([100, 5]) === null, "no rate of return when no year is negative");
check(F.irr([0, 0, 0]) !== undefined, "all-zero flows do not throw");

// the flows to equity: capex 1,000, 60 percent debt at zero interest over 10 years is 60 a year; revenue 100, O&M 10
const z = { capex: 1000, share: 60, rate: 0, term: 10, fom: 10, rte: 86, cycles: 1, deg: 0, life: 10, hurdle: 0 };
const fl = F.flows(z, 100);
check(fl.length === 11 && fl[0] === -400 && fl.slice(1).every((v) => near(v, 30)), "flows: -400 of equity, then 100 - 10 - 60 = 30 a year for ten years");
check(near(F.npv(0, fl), -100), "their plain sum is -100");
check(near(F.flows({ ...z, deg: 10 }, 100)[2], 90 - 10 - 60) && near(F.flows({ ...z, deg: 10 }, 100)[3], 81 - 10 - 60), "degradation: year 2 earns 90, year 3 earns 81");
check(near(F.flows({ ...z, term: 4 }, 100)[5], 90) && near(F.flows({ ...z, term: 4 }, 100)[4], 100 - 10 - 150), "after the debt's last year the payment is gone");

// coverage, the breakeven toll and the merchant tail
check(near(F.coverage(z, 100), 1.5), "coverage: (100 - 10) / 60 = 1.5");
check(F.coverage({ ...z, share: 0 }, 100) === null && F.breakevenToll({ ...z, share: 0 }) === null, "no debt: no coverage and no toll");
check(near(F.breakevenToll(z), (1.25 * 60 + 10) / 12), "breakeven toll: (1.25 x 60 + 10) / 12 = 7.0833 a kW-month", String(F.breakevenToll(z)));
check(near((12 * F.breakevenToll(d4) - d4.fom) / F.debtService(d4), 1.25, 1e-12), "at the breakeven toll, coverage is 1.25");
check(near(F.coverage(d4, 81.40219), 0.87570, 1e-4), "the default case covers its debt 0.88 times", String(F.coverage(d4, 81.40219)));
const t0 = F.merchantTail({ ...z, term: 10, life: 12 }, 100);
check(t0.years === 2 && t0.from === 11 && t0.to === 12 && near(t0.pv, 180), "tail: two years after a ten-year term, 90 a year at a hurdle rate of zero", JSON.stringify(t0));
const t1 = F.merchantTail({ ...z, term: 10, life: 12, hurdle: 10 }, 100);
check(near(t1.pv, 90 / 1.1 ** 11 + 90 / 1.1 ** 12, 1e-9), "tail at 10 percent: 90 / 1.1^11 + 90 / 1.1^12");
check(F.merchantTail(d4, 81.4).years === 0 && F.merchantTail(d4, 81.4).pv === 0, "the defaults have no tail: the term is the life");

// the address
const steps = { rte: [86, 89, 92], cycles: [0.5, 1, 1.5, 2] };
const s0 = F.parseScenarios({}, d4, steps);
check(F.differing(s0.a, s0.b).length === 0 && s0.view === "a" && F.scenarioQuery(s0, d4).length === 0, "no parameter: both scenarios are the defaults and the address stays bare");
const s1 = F.parseScenarios({ ac: "1300", ah: "10", bc: "1100", be: "92", by: "2", v: "b", bt: "10.4", bs: "150", bd: "abc", ae: "87" }, d4, steps);
check(s1.a.capex === 1300 && s1.a.hurdle === 10 && s1.b.capex === 1100 && s1.b.rte === 92 && s1.b.cycles === 2 && s1.view === "b", "the address sets both scenarios and the one in view");
check(s1.b.term === 10 && s1.b.share === 100 && s1.b.deg === 0 && s1.a.rte === 86, "a value is bounded; one that cannot be read, or a step not held, takes the default");
const q1 = F.scenarioQuery(s1, d4);
const back = F.parseScenarios(Object.fromEntries(q1), d4, steps);
check(JSON.stringify(back) === JSON.stringify(s1), "the address round trip gives the same scenarios", q1.map((p) => p.join("=")).join("&"));
check(F.parseScenarios({ be: "92" }, d4, F.ONLY_DEFAULT).b.rte === 86, "with only the default step held, another step in the address is not used");
check(F.differenceWords({ ...d4, capex: 1300, hurdle: 10 }, { ...d4, capex: 1100, hurdle: 8 }) === "B: capex USD 1,100 per kW against 1,300; hurdle rate 8 percent against 10.", "the last row's words", F.differenceWords({ ...d4, capex: 1300, hurdle: 10 }, { ...d4, capex: 1100, hurdle: 8 }));
check(F.differenceWords(d4, d4) === "A and B hold the same assumptions.", "the last row when nothing differs");
check(F.carry("?grid=ercot&ac=1300&af=30&bh=9&v=b&mw=50", true) === "&ac=1300&af=30&bh=9&v=b" && F.carry("?grid=ercot&ac=1300&af=30&bh=9&v=b", false) === "&bh=9&v=b" && F.carry("?grid=ercot&ds=5", true) === "", "the page's other links carry the scenarios; a change of duration drops the capital cost and the fixed O&M");
check(["grid", "dur", "strat", "mw", "fom", "ds"].every((k) => !F.isScenarioParam(k)), "no scenario parameter is one of the page's own six");

// the sensitivity
const rev = (rte, cycles) => ({ "86|1": 81.4, "89|1": 83.06, "86|0.5": 64.08, "86|1.5": 83.57 })[`${rte}|${cycles}`] ?? null;
const bars = F.sensitivity(d4, rev, steps);
check(bars.length === 10 && bars.every((b, i) => i === 0 || bars[i - 1].size >= b.size), "ten bars, sorted by size");
const by = Object.fromEntries(bars.map((b) => [b.key, b]));
check(near(by.capex.down.npv, F.npv(8, F.flows({ ...d4, capex: 1010 }, 81.4))) && by.capex.down.value === 1010 && by.capex.up.value === 1210, "capital cost moves by USD 100 per kW each way");
check(by.deg.down === null && by.deg.up.value === 1, "degradation at 0 has no lower step");
check(by.rte.down === null && by.rte.up.value === 89 && near(by.rte.up.npv, F.npv(8, F.flows(d4, 83.06))), "efficiency moves one step, to the model's own run at 89 percent");
check(by.cycles.down.value === 0.5 && by.cycles.up.value === 1.5 && near(by.cycles.down.npv, F.npv(8, F.flows(d4, 64.08))), "cycles move one step each way");
const lone = F.sensitivity(d4, rev, F.ONLY_DEFAULT);
check(lone.find((b) => b.key === "rte").size === 0 && lone.find((b) => b.key === "cycles").size === 0, "with only the default step held, the two stepped assumptions have no bar");
check(F.sensitivity(d4, () => null, steps).length === 0, "no revenue, no chart");

// the file of steps against the live months
const c = { first: "2026-01", last: "2026-03", months: ["2026-01", "2026-02", "2026-03"], days: [31, 28, 31], table: [10, 20, 30], cells: { "86|1": [10, 20, 30], "92|2": [12, 24, 36] } };
const live = [{ m: "2026-01", held: true, total: 10, daysHeld: 31 }, { m: "2026-02", held: true, total: 20.004, daysHeld: 28 }, { m: "2026-03", held: true, total: 30, daysHeld: 31 }];
check(F.stepState(c, live, ["2026-01", "2026-02", "2026-03"]).ok === true, "the steps are offered while the file's months and default cell are the live table's");
check(F.stepState(c, [...live, { m: "2026-04", held: true, total: 5, daysHeld: 30 }], ["2026-02", "2026-03", "2026-04"]).why === "months", "a window that has moved past the file withdraws the steps");
check(F.stepState(c, live.map((r) => (r.m === "2026-02" ? { ...r, total: 20.02 } : r)), ["2026-01", "2026-02", "2026-03"]).why === "revised", "a revised month withdraws the steps");
check(F.stepState(c, live.map((r) => (r.m === "2026-03" ? { ...r, daysHeld: 30 } : r)), ["2026-01", "2026-02", "2026-03"]).why === "revised", "a different count of days withdraws the steps");
check(F.stepState(null, live, ["2026-01"]).why === "none", "no case in the file: only the default step");
check(F.stepsOffered({ rte_steps: [86, 89, 92], cycle_steps: [0.5, 1, 1.5, 2] }, { ok: false, why: "months", fileLast: null, liveLast: null }).rte.length === 1, "withdrawn steps leave the default alone");
check(F.cellTotals(c, 92, 2).get("2026-02") === 24 && F.cellTotals(c, 89, 1) === null, "a cell's totals by month; null for a cell not held");

console.log(failed ? `\n${failed} FAILED` : "\nall passed");
process.exit(failed ? 1 : 0);
