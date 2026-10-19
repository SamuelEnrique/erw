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
  // Session 179, found by GitHub's runner at the landing: on Linux a pipe takes 64 KiB at a time, and process.exit()
  // right after console.log cut the JSON at byte 65,536. The exit now waits until stdout has taken every byte.
  await new Promise((done) => process.stdout.write(JSON.stringify(out) + "\n", done));
  process.exit(0);
}

let failed = 0;
function check(ok, what, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}
const near = (a, b, tol = 1e-9) => a !== null && b !== null && Math.abs(a - b) <= tol;

const now4 = F.defaultsOf({ capex: 1110, fom: 22 });
// session 208 (the owner's rulings of 12 October 2026): the debt share is Lazard's storage structure, 20 percent; the hurdle rate
// is Lazard's cost of equity, 12 percent; the contract's share and price are assumptions, 0 by default (fully merchant)
// session 297: six more, each at a default that moves nothing (no credit, the revenue cut, Lazard's fade, no augmentation at the ATB's energy cost, no repeat)
check(JSON.stringify(now4) === JSON.stringify({ capex: 1110, share: 20, rate: 8, term: 20, fom: 22, rte: 86, cycles: 1, deg: 2.6, life: 20, hurdle: 12, itc: 0, method: 0, fade: 2.6, aug: 0, augcost: 241, stress: 0, cshare: 0, cprice: 0 }), "the defaults of a 4-hour battery (session 208: debt share 20, hurdle rate 12, no contract; session 297: the six at their idle defaults)", JSON.stringify(now4));
check(/Lazard/.test(F.SPECS.hurdle.source) && /80% equity at a 12% cost/.test(F.SPECS.hurdle.source) && /Lazard/.test(F.SPECS.share.source) && /20% debt at an 8% interest rate/.test(F.SPECS.share.source) && /Lazard/.test(F.SPECS.deg.source) && /2\.6 percent a year/.test(F.SPECS.deg.source) && F.HURDLE === 12 && F.SHARE === 20 && F.DEG === 2.6, "the defaults state their source: the hurdle rate is the cost of equity, the debt share the storage cases'");
check(/fully merchant/.test(F.SPECS.cshare.source) && /fully merchant/.test(F.SPECS.cprice.source), "the contract's two defaults say the default is fully merchant");
// the hand cases below were worked at session 179's defaults, 60 percent debt, degradation 0 and a hurdle rate of 8, and stay on them
const d4 = { ...now4, share: 60, deg: 0, hurdle: 8 };
check(F.KEYS.length === 18 && new Set(F.KEYS.map((k) => F.SPECS[k].letter)).size === 18, "eighteen assumptions, eighteen different letters (session 297: six more)");

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
check(bars.length === 10 && bars.every((b, i) => i === 0 || bars[i - 1].size >= b.size) && !bars.some((b) => b.key === "cshare" || b.key === "cprice"), "ten bars at the default, sorted by size (session 211: no contract, no contract rows)", bars.map((b) => b.key).join(", "));
const withContract = F.sensitivity({ ...d4, cshare: 50, cprice: 10 }, rev, steps);
check(withContract.length === 12 && withContract.some((b) => b.key === "cshare") && withContract.some((b) => b.key === "cprice"), "with a contract in the scenario, twelve bars: the contract's share and price among them");
check(F.sensitivity({ ...d4, cprice: 10 }, rev, steps).length === 10, "a price with no share draws no contract row");
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


// session 208: the contract. At a share of 0 nothing moves; at 50 percent and USD 10 per kW-month the contracted half earns
// 60 a year and the merchant half earns half the market, for the debt's years; after them the whole battery is merchant.
{
  const c = { ...d4, term: 10, life: 12, fom: 10, cshare: 50, cprice: 10 };
  const rev = 100;
  check(near(F.contractYear(c), 60), "the contract's income a year: 0.5 x 10 x 12 = 60 per kW of the whole battery", String(F.contractYear(c)));
  check(near(F.incomeInYear(c, rev, 1), 60 + 50) && near(F.incomeInYear(c, rev, 10), 110) && near(F.incomeInYear(c, rev, 11), 100), "income: 110 in the debt's years, the market's 100 after them");
  check(near(F.coverage(c, rev), (110 - 10) / F.debtService(c)), "coverage with the contract: (60 + 50 - 10) / debt", String(F.coverage(c, rev)));
  const f = F.flows(c, rev), f0 = F.flows({ ...c, cshare: 0 }, rev);
  check(f.length === 13 && near(f[1], 110 - 10 - F.debtService(c)) && near(f[11], 100 - 10) && near(f0[1], 100 - 10 - F.debtService(c)), "the flows read the contract while the debt lasts, and the market after");
  check(JSON.stringify(F.resultOf({ ...c, cshare: 0, cprice: 10 }, rev)) === JSON.stringify(F.resultOf({ ...c, cshare: 0, cprice: 0 }, rev)), "a price with no share moves nothing");
  const old = { ...d4 };
  delete old.cshare; delete old.cprice;
  check(JSON.stringify(F.resultOf(old, rev)) === JSON.stringify(F.resultOf(d4, rev)), "an older set of assumptions, without the two contract keys, is read as no contract");
  check(near(F.breakevenToll(c), F.breakevenToll({ ...c, cshare: 0, cprice: 0 })) && near(F.merchantTail(c, rev).pv, F.merchantTail({ ...c, cshare: 0, cprice: 0 }, rev).pv), "the breakeven toll and the merchant tail do not read the contract");
  const bars = F.sensitivity(c, () => rev, F.ONLY_DEFAULT);
  check(bars.length === 12 && bars.some((b) => b.key === "cshare") && bars.some((b) => b.key === "cprice"), "twelve bars, the contract's two among them");
  check(F.sensitivity(d4, () => rev, F.ONLY_DEFAULT).find((b) => b.key === "cshare") === undefined, "at a share of 0 the contract's rows are not drawn at all (session 211)");
  const at50 = bars.find((b) => b.key === "cshare");
  check(at50.down !== null && at50.down.value === 40 && at50.up !== null && at50.up.value === 60, "at a share of 50 the share's row moves 10 points each way", JSON.stringify(at50));
}

// session 296 (the owner's rulings of 15 October 2026): the ATB's 8-hour defaults, the payback year, NPV per dollar of
// equity, the years of a scenario, the two sensitivity modes and the sourced ranges
{
  check(F.atbCapex(8) === 2300 && F.atbCapex(4) === 1336 && F.atbCapex(2) === 854 && F.atbFom(8) === 92, "the ATB's cost: 241 per kWh times the hours plus 372 per kW; fixed O&M 4 percent (2,300 and 92 at 8 hours)", `${F.atbCapex(8)} ${F.atbFom(8)}`);
  check(/NREL\/TP-6A40-93281/.test(F.ATB.report) && F.ATB.rte === 85 && F.ATB.life === 15, "the ATB's report, efficiency and life are named");
  const z = { capex: 1000, share: 60, rate: 0, term: 10, fom: 10, rte: 86, cycles: 1, deg: 0, life: 10, hurdle: 0, cshare: 0, cprice: 0 };
  check(F.equityIn(z) === 400 && F.paybackYear(F.flows(z, 100)) === null, "capex 1,000 at 60 percent debt: 400 of equity; 30 a year for ten years never pays it back");
  check(F.paybackYear(F.flows(z, 150)) === 5, "at 150 of revenue, 80 a year: the fifth year pays the 400 back (80 x 5 = 400)", String(F.paybackYear(F.flows(z, 150))));
  check(F.paybackYear([-100, 60, 60]) === 2 && F.paybackYear([0, 5]) === 0 && F.paybackYear([-100, 10]) === null, "payback: the first year the running sum is no longer negative; 0 with nothing paid in; null when never");
  check(near(F.npvPerEquity(z, -100), -0.25) && F.npvPerEquity({ ...z, share: 100 }, 5) === null, "NPV per dollar of equity is NPV over the equity paid in; null with no equity");
  const rows = F.projection(z, 150);
  check(rows.length === 10 && near(rows[0].income, 150) && near(rows[0].afterCosts, 140) && near(rows[0].debt, 60) && near(rows[0].afterDebt, 80) && near(rows[0].balance, 540) && near(rows[9].balance, 0),
    "the projection: income 150, after costs 140, the debt payment 60, after debt 80, and the debt owed falls from 600 by 60 a year to 0", JSON.stringify(rows[0]));
  check(near(F.projection({ ...z, term: 4 }, 150)[5].debt, 0) && near(F.projection({ ...z, term: 4 }, 150)[5].afterDebt, 140), "after the debt's last year the payment and the balance are gone");
  check(near(F.projection({ ...z, rate: 8, term: 20, life: 20 }, 150)[19].balance, 0, 1e-6), "at 8 percent over 20 years the last payment leaves nothing owed");
  const steps = { rte: [86, 89, 92], cycles: [0.5, 1, 1.5, 2] };
  const pct = { kind: "pct", pct: 10 };
  check(F.movedValue("capex", z, -1, pct, steps) === 900 && F.movedValue("capex", z, 1, pct, steps) === 1100, "a percent step moves capital cost by 10 percent each way");
  check(F.movedValue("share", { ...z, share: 95 }, 1, pct, steps) === 100 && F.movedValue("term", z, 1, pct, steps) === 11, "a percent step is held inside the bounds, and a whole-number field stays whole");
  check(F.movedValue("rte", z, 1, pct, steps) === 92 && F.movedValue("rte", z, -1, pct, steps) === null && F.movedValue("cycles", z, 1, pct, steps) === 1.5 && F.movedValue("cycles", z, -1, pct, steps) === 0.5,
    "efficiency and cycles move to the nearest step held in that direction (86 up by 10 percent is 94.6: the step 92; down: no step below 86)");
  const r4 = F.rangesOf(4);
  check(r4.capex.low === 620 && r4.capex.high === 1600 && near(r4.fom.low, 12) && near(r4.fom.high, 53.44) && r4.share.low === 20 && r4.share.high === 60 && r4.rte.low === 85 && r4.rte.high === 92 && r4.deg.low === 0 && r4.deg.high === 2.6 && r4.life.low === 15 && r4.life.high === 20,
    "the 4-hour sourced ranges: Lazard's low and high cases, the ATB's 4 percent fixed O&M of its own 1,336 (53.44), 85 percent, 15 years and no degradation", JSON.stringify(r4.fom));
  check(Object.keys(r4).length === 6 && Object.values(r4).every((r) => /Lazard|Annual Technology Baseline/.test(r.source)), "six assumptions have a published range, each with its source; the others have none");
  const r8 = F.rangesOf(8);
  check(r8.capex.low === 1180 && r8.capex.high === 3040 && r8.capex.high > 2300 && r8.capex.low < 2300 && /extrapolation/.test(r8.capex.source), "the 8-hour capital range is the straight lines through Lazard's low cases and high cases, with the ATB's 2,300 inside", JSON.stringify(r8.capex));
  const rev = () => 100;
  const inRange = F.sensitivityIn(z, rev, steps, { kind: "range", ranges: r4 }, "npv");
  check(inRange.length === 6 && inRange.every((b) => b.down || b.up) && !inRange.some((b) => ["rate", "term", "hurdle", "cycles", "cshare", "cprice"].includes(b.key)), "the sourced range draws the six rows with a range and no other", inRange.map((b) => b.key).join(","));
  const cap = inRange.find((b) => b.key === "capex");
  check(cap.down.value === 620 && cap.up.value === 1600 && near(cap.down.npv, F.npv(0, F.flows({ ...z, capex: 620 }, 100))) && near(cap.up.npv, F.npv(0, F.flows({ ...z, capex: 1600 }, 100))), "the capital cost row moves to 620 and 1,600 and recomputes NPV at each");
  const rteRow = inRange.find((b) => b.key === "rte");
  check(rteRow.down.value === 86 && rteRow.up.value === 92, "the efficiency row takes the lowest and highest step inside the range (86 stands in for the ATB's 85)");
  const inPct = F.sensitivityIn(z, rev, steps, pct, "npv");
  check(inPct.length === 10 && inPct.every((b) => b.step === "10 percent") && inPct[0].size >= inPct[inPct.length - 1].size, "the percent step draws ten rows at the default (the contract's two only with a contract), sorted by size");
  const inIrr = F.sensitivityIn({ ...z, hurdle: 5 }, () => 150, steps, pct, "irr");
  const capIrr = inIrr.find((b) => b.key === "capex");
  check(capIrr && near(capIrr.base, F.irr(F.flows({ ...z, hurdle: 5 }, 150))) && capIrr.down.npv > capIrr.base, "measured in IRR the bars are rates of return: a lower capital cost gives a higher rate", JSON.stringify(capIrr));
  check(F.sensitivityIn(z, () => 5, steps, pct, "irr").length === 0 && F.sensitivityIn(z, () => 5, steps, pct, "npv").length === 10, "a scenario with no rate of return draws no bar in IRR, and its ten in NPV");
  check(F.NO_RANGE.rate !== undefined && F.NO_RANGE.term !== undefined && F.NO_RANGE.hurdle !== undefined && F.NO_RANGE.cycles !== undefined, "the assumptions without a range are named, with why");
}

// session 297: the investment tax credit, the fade method with augmentation, and the stress repeats
{
  const d = F.defaultsOf({ capex: 1110, fom: 22 });
  const ctx = { peak: 3430.6, hours: 4 };
  check(JSON.stringify(F.resultOf(d, 81.4, ctx)) === JSON.stringify(F.resultOf(d, 81.4)) && JSON.stringify(F.flows(d, 81.4, ctx)) === JSON.stringify(F.flows(d, 81.4)), "at the defaults the context moves nothing: no credit, the revenue cut, no repeat");
  const old = { ...d };
  for (const k of ["itc", "method", "fade", "aug", "augcost", "stress"]) delete old[k];
  check(JSON.stringify(F.flows(old, 81.4, ctx)) === JSON.stringify(F.flows(d, 81.4, ctx)), "an older set of assumptions, without the six keys, is read at their defaults");
  // the credit: 30 percent of 1,110 at year 0, against the equity paid in (80 percent of 1,110 = 888)
  const withItc = F.flows({ ...d, itc: 30 }, 81.4);
  check(near(withItc[0], -888 + 333) && withItc.slice(1).every((v, i) => near(v, F.flows(d, 81.4)[i + 1])), "the credit is taken at year 0 only: -888 + 333 = -555", String(withItc[0]));
  check(F.npv(12, withItc) > F.npv(12, F.flows(d, 81.4)) && near(F.npv(12, withItc) - F.npv(12, F.flows(d, 81.4)), 333), "NPV rises by the credit itself, undiscounted at year 0");
  // the fade method: capacity (1 - 0.026)^(t-1) with no augmentation, revenue following it; the revenue cut not applied
  const fadeNone = { ...d, method: 1, fade: 2.6, aug: 0, deg: 0 };
  check(near(F.revenueInYear(fadeNone, 100, 1, ctx), 100) && near(F.revenueInYear(fadeNone, 100, 3, ctx), 100 * 0.974 ** 2) && near(F.revenueInYear(fadeNone, 100, 20, ctx), 100 * 0.974 ** 19), "under the fade method revenue follows the capacity, (1 - fade)^(t - 1) with no augmentation");
  check(near(F.revenueInYear({ ...fadeNone, deg: 10 }, 100, 3, ctx), 100 * 0.974 ** 2), "the revenue cut is not applied under the fade method");
  // augmentation every 5 years: the capacity restarts at 1 in years 6, 11 and 16; the cost in years 5, 10 and 15 (not 20) is the lost share x hours x cost per kWh
  const aug5 = { ...d, method: 1, fade: 2.6, aug: 5, augcost: 241 };
  check(near(F.revenueInYear(aug5, 100, 5, ctx), 100 * 0.974 ** 4) && near(F.revenueInYear(aug5, 100, 6, ctx), 100) && near(F.revenueInYear(aug5, 100, 11, ctx), 100), "augmentation every 5 years restores the capacity in years 6, 11 and 16");
  const lost = 1 - 0.974 ** 5;
  check(near(F.augmentationCost(aug5, 5, ctx), lost * 4 * 241) && near(F.augmentationCost(aug5, 10, ctx), lost * 4 * 241) && F.augmentationCost(aug5, 20, ctx) === 0 && F.augmentationCost(aug5, 4, ctx) === 0 && F.augmentationCost(d, 5, ctx) === 0,
    "the augmentation cost: the capacity lost over the period, times the hours, times the cost per kWh, in years 5, 10 and 15 and not the last; 0 under the revenue cut", String(F.augmentationCost(aug5, 5, ctx)));
  const fl5 = F.flows(aug5, 100, ctx);
  check(near(fl5[5], F.incomeInYear(aug5, 100, 5, ctx) - 22 - F.debtService(aug5) - lost * 4 * 241) && near(fl5[6], F.incomeInYear(aug5, 100, 6, ctx) - 22 - F.debtService(aug5)), "the flows pay the augmentation in its year");
  check(near(F.projection(aug5, 100, ctx)[4].afterCosts, 100 * 0.974 ** 4 - 22 - lost * 4 * 241), "the projection counts the augmentation as a cost of its year");
  check(F.augmentationCost({ ...aug5, hours: undefined }, 5, {}) === 0, "with no hours in the context no augmentation cost is charged (nothing invented)");
  // the stress repeats: each adds the peak event's window revenue once, spread evenly over the life
  const st = { ...d, stress: 2 };
  check(near(F.revenueInYear(st, 100, 1, ctx), 100 + 2 * 3430.6 / 20) && near(F.revenueInYear(st, 100, 7, ctx), 100 * 0.974 ** 6 + 2 * 3430.6 / 20), "two repeats add 2 x 3,430.6 / 20 to each year", String(F.revenueInYear(st, 100, 1, ctx)));
  check(near(F.npv(0, F.flows(st, 100, ctx)) - F.npv(0, F.flows(d, 100, ctx)), 2 * 3430.6), "the plain sum rises by the two windows' revenue");
  check(F.revenueInYear(st, 100, 1, {}) === 100 && F.coverage(st, 100) === F.coverage(d, 100), "without a peak event in the context a repeat adds nothing; coverage never reads the repeats");
  // the rows the sensitivity draws
  check(F.sensitivityKeys(d).length === 10 && F.sensitivityKeys({ ...d, itc: 30 }).includes("itc") && F.sensitivityKeys({ ...d, stress: 1 }).includes("stress") && !F.sensitivityKeys(d).includes("method"),
    "ten rows at the defaults; the credit's and the stress row with a value; the method never");
  const fk = F.sensitivityKeys({ ...d, method: 1 });
  check(fk.includes("fade") && fk.includes("aug") && fk.includes("augcost") && !fk.includes("method") && fk.length === 13, "under the fade method its three rows join (thirteen)", fk.join(","));
  const steps = { rte: [86, 89, 92], cycles: [0.5, 1, 1.5, 2] }, pct = { kind: "pct", pct: 10 };
  check(F.movedValue("aug", { ...d, method: 1, aug: 5 }, 1, pct, steps) === 7 && F.movedValue("aug", { ...d, method: 1, aug: 5 }, -1, pct, steps) === 3 && F.movedValue("aug", { ...d, method: 1, aug: 0 }, -1, pct, steps) === null && F.movedValue("method", d, 1, pct, steps) === null,
    "the augmentation period moves to the next choice; the method does not move");
  check(F.bound("aug", 4, d, steps) === 0 && F.bound("aug", 7, d, steps) === 7 && F.bound("method", 2, d, steps) === 0 && F.bound("itc", 90, d, steps) === 70, "a choice outside the list takes the default; the credit is held to 70");
  check(F.isScenarioParam("ai") && F.isScenarioParam("bx") && F.isScenarioParam("ao") && !F.isScenarioParam("av"), "the six new letters are the scenarios' (i, o, g, m, k, x), and v is not");
  const words = F.differenceWords(d, { ...d, method: 1, aug: 5, stress: 1 });
  check(words === "B: degradation method capacity fade with augmentation against revenue cut; augmentation every 5 years against none; repeats of the peak stress event 1 against 0.", "the row in words names the choices", words);
}

console.log(failed ? `${failed} FAILED` : "all passed");
process.exit(failed ? 1 : 0);
