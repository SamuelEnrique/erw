// Energy Research Warehouse (ERW) site, session 186: the finance of /cost-of-power/seller's scenarios
// (lib/seller/finance.ts) against cases computed by hand, and against the battery page's library
// (lib/battery/finance.ts), whose arithmetic it repeats. No server, no browser, no network.
//
//   node scripts/test-seller-finance.mjs                 the assertions; exits 1 if any fails
//   node scripts/test-seller-finance.mjs --cases f.json  prints, as JSON, the results for the cases in f.json
//                                                        ([{ a: Assumptions, rev: USD per kW, energy: MWh per kW,
//                                                        month: USD per kW }]); tests/test_session186.py compares them
//                                                        with its Python mirror to 1e-6
import fs from "node:fs";

const F = await import("../lib/seller/finance.ts");
const BF = await import("../lib/battery/finance.ts");

const at = process.argv.indexOf("--cases");
if (at > 0) {
  const cases = JSON.parse(fs.readFileSync(process.argv[at + 1], "utf-8"));
  const out = cases.map(({ a, rev, energy, month }) => {
    const r = F.resultOf(a, rev);
    return { debt: r.debt, coverage: r.coverage, npv: r.npv, irr: r.irr, contract: F.contractPrice(a, energy), toll: F.breakevenToll(a), month: F.monthCoverage(a, month), flows: F.flows(a, rev),
      bars: F.sensitivity(a, rev).map((b) => ({ key: b.key, down: b.down, up: b.up, size: b.size })) };
  });
  // the exit waits until stdout has taken every byte (session 179: on Linux a pipe takes 64 KiB at a time)
  await new Promise((done) => process.stdout.write(JSON.stringify(out) + "\n", done));
  process.exit(0);
}

let failed = 0;
function check(ok, what, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}
const near = (a, b, tol = 1e-9) => a !== null && b !== null && Math.abs(a - b) <= tol;

// the defaults: Lazard's solar (1,375 USD per kW, 12.5 USD per kW a year, 35 years), 60 percent debt at 8 percent over the life
const solarNow = F.defaultsOf({ capex: 1375, fom: 12.5, life: 35 });
check(JSON.stringify(solarNow) === JSON.stringify({ capex: 1375, share: 60, rate: 8, term: 35, fom: 12.5, deg: 0, life: 35, hurdle: 12 }), "the defaults of solar (session 208: a hurdle rate of 12, Lazard's cost of equity)", JSON.stringify(solarNow));
check(F.defaultsOf({ capex: 1110, fom: 22, life: 20, deg: F.BATTERY_DEG }).deg === 2.6 && /2\.6 percent a year/.test(F.BATTERY_DEG_SOURCE) && /40% equity at a 12% cost/.test(F.SPECS.hurdle.source) && F.HURDLE === 12,
  "a battery's degradation default is Lazard's 2.6 percent a year, and the hurdle rate is the weighted cost 0.6 x 8 + 0.4 x 12");
// the hand cases below were worked at session 186's default hurdle rate of 8, and stay on it
const solar = { ...solarNow, hurdle: 8 };
check(F.KEYS.length === 8 && new Set(F.KEYS.map((k) => F.SPECS[k].letter)).size === 8, "eight assumptions, eight different letters");
check(JSON.stringify(F.KEYS) === JSON.stringify(["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle"]), "in the order asked");

// the debt payment: 0.08 / (1 - 1.08^-35) = 0.085803265; 1,375 x 0.6 x that = 70.7877 a kW, USD 7,078,769 for 100 MW
check(near(F.crf(0.08, 35), 0.08 / (1 - 1.08 ** -35), 1e-15) && near(F.crf(0.08, 35), 0.0858032646, 1e-9), "crf(8 percent, 35 years) = 0.085803265", String(F.crf(0.08, 35)));
check(near(F.crf(0, 20), 0.05), "crf at a rate of zero is 1 / years");
check(Math.round(F.debtService(solar) * 1000 * 100) === 7078769, "the default debt payment for 100 MW of solar is the page's USD 7,078,769", String(F.debtService(solar) * 100000));
check(Math.round(F.debtService(F.defaultsOf({ capex: 2100, fom: 32.25, life: 30 })) * 100000) === 11192257, "wind: USD 11,192,257");
check(Math.round(F.debtService(F.defaultsOf({ capex: 1110, fom: 22, life: 20 })) * 100000) === 6783357, "a 4-hour battery: USD 6,783,357");
check(Math.round(F.debtService(F.defaultsOf({ capex: 1300, fom: 13.5, life: 30 })) * 100000) === 6928540, "a gas peaker: USD 6,928,540");
check(F.debtYears({ ...solar, term: 40 }) === 35 && near(F.debtService({ ...solar, term: 40 }), F.debtService(solar)), "a term longer than the life is cut to the life");

// net present value and the internal rate of return
check(near(F.npv(10, [-100, 110]), 0, 1e-12), "npv(10 percent, [-100, 110]) = 0");
check(near(F.npv(0, [-100, 50, 50, 50]), 50), "npv at zero is the plain sum");
check(near(F.irr([-100, 110]), 10, 1e-6), "irr([-100, 110]) = 10 percent", String(F.irr([-100, 110])));
const three = F.irr([-100, 50, 50, 50]);
check(near(three, 23.3751928, 1e-5) && near(F.npv(three, [-100, 50, 50, 50]), 0, 1e-6), "irr([-100, 50, 50, 50]) = 23.3752 percent, and the value there is zero", String(three));
check(F.irr([-100, -5, -5]) === null && F.irr([100, 5]) === null, "no rate of return when every year has one sign");

// the flows to equity: capex 1,000, 60 percent debt at zero interest over 10 years is 60 a year; revenue 100, O&M 10
const z = { capex: 1000, share: 60, rate: 0, term: 10, fom: 10, deg: 0, life: 10, hurdle: 0 };
const fl = F.flows(z, 100);
check(fl.length === 11 && fl[0] === -400 && fl.slice(1).every((v) => near(v, 30)), "flows: -400 of equity, then 100 - 10 - 60 = 30 a year for ten years");
check(near(F.npv(0, fl), -100), "their plain sum is -100");
check(near(F.flows({ ...z, deg: 10 }, 100)[2], 90 - 10 - 60) && near(F.flows({ ...z, deg: 10 }, 100)[3], 81 - 10 - 60), "degradation: year 2 earns 90, year 3 earns 81");
check(near(F.flows({ ...z, term: 4 }, 100)[5], 90) && near(F.flows({ ...z, term: 4 }, 100)[4], 100 - 10 - 150), "after the debt's last year the payment is gone");

// coverage, and the two contract prices that set it to 1.25
check(near(F.coverage(z, 100), 1.5) && F.coverage({ ...z, share: 0 }, 100) === null, "coverage: (100 - 10) / 60 = 1.5; none with no debt");
check(near(F.monthCoverage(z, 100 / 12), 1.5) && near(F.monthCoverage(z, 0), -10 / 60), "a month's coverage: the month less a twelfth of O&M, over a twelfth of the debt");
const p = F.contractPrice(z, 2.5);   // 2.5 MWh a kW a year: (1.25 x 60 + 10) / 2.5 = 34
check(near(p, 34) && near((p * 2.5 - z.fom) / F.debtService(z), 1.25), "the contract price: (1.25 x 60 + 10) / 2.5 = 34 USD per MWh, and coverage at it is 1.25");
check(F.contractPrice({ ...z, share: 0 }, 2.5) === null && F.contractPrice(z, 0) === null, "no contract price with no debt or no energy");
const t = F.breakevenToll(z);
check(near(t, 85 / 12) && near((12 * t - z.fom) / F.debtService(z), 1.25), "the toll: (1.25 x 60 + 10) / 12 = 7.0833 USD per kW-month, and coverage at it is 1.25");

// the address
const d = solar;
const s = F.parseScenarios({ ac: "1200", bh: "10", bt: "12.6", al: "99", ad: "x", v: "b", mw: "50", ds: "1" }, d);
check(s.a.capex === 1200 && s.b.hurdle === 10 && s.b.term === 13 && s.a.life === 40 && s.a.deg === 0 && s.view === "b", "the address: read, bounded, whole where whole, defaulted where unreadable", JSON.stringify(s));
check(JSON.stringify(F.scenarioQuery(s, d)) === JSON.stringify([["ac", "1200"], ["al", "40"], ["bt", "13"], ["bh", "10"], ["v", "b"]]), "only what differs from the defaults is written", JSON.stringify(F.scenarioQuery(s, d)));
check(F.scenarioQuery(F.parseScenarios({}, d), d).length === 0, "no parameter means the defaults, and the defaults write none");
check(["ac", "bs", "ar", "bt", "af", "bd", "al", "bh", "v"].every(F.isScenarioParam) && ["ds", "mw", "hr", "bmw", "dur", "asset", "ae", "ay", "fom", "hub"].every((k) => !F.isScenarioParam(k)), "the scenarios' parameters are told from the page's own");
check(F.carry("iso=ercot&ac=1200&bh=10&at=20&bl=25&bf=9&v=b&mw=50", true) === "&ac=1200&bh=10&at=20&bl=25&bf=9&v=b", "the page's other addresses carry the scenarios");
check(F.carry("iso=ercot&ac=1200&bh=10&at=20&bl=25&bf=9&v=b&mw=50", false) === "&bh=10&v=b", "a change of asset drops the capital cost, fixed O&M, term and life");
check(F.differenceWords(d, d) === "A and B hold the same assumptions." && F.differenceWords({ ...d, capex: 1200 }, { ...d, hurdle: 10 }) === "B: capex USD 1,375 per kW against 1,200; hurdle rate 10 percent against 8.", "the last row in words", F.differenceWords({ ...d, capex: 1200 }, { ...d, hurdle: 10 }));

// the sensitivity: eight bars, sorted, each side the NPV with one assumption moved by its step
const bars = F.sensitivity(d, 59.85);
check(bars.length === 8 && bars.every((b, i) => i === 0 || bars[i - 1].size >= b.size), "eight bars, sorted by size", bars.map((b) => b.key).join(", "));
const cap = bars.find((b) => b.key === "capex");
check(cap.down.value === 1275 && cap.up.value === 1475 && near(cap.down.npv, F.resultOf({ ...d, capex: 1275 }, 59.85).npv) && near(cap.up.npv, F.resultOf({ ...d, capex: 1475 }, 59.85).npv), "capital cost by USD 100 per kW, each side recomputed");
check(bars.find((b) => b.key === "deg").down === null && bars.find((b) => b.key === "deg").up.value === 1, "degradation at 0 has no lower step");
const term = bars.find((b) => b.key === "term");
check(term.up.value === 40 && near(term.up.npv, term.base), "a term raised past the life is cut to the life: that side does not move NPV");

// the arithmetic is the battery page's: the same assumptions give the same numbers in both libraries
{
  let seed = 186, worst = 0, n = 0, both = 0;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  for (let i = 0; i < 400; i++) {
    const a = { capex: Math.round(rnd() * 300000) / 100, share: Math.round(rnd() * 1000) / 10, rate: Math.round(rnd() * 1500) / 100, term: 1 + Math.floor(rnd() * 40), fom: Math.round(rnd() * 8000) / 100,
      deg: Math.round(rnd() * 600) / 100, life: 1 + Math.floor(rnd() * 40), hurdle: Math.round(rnd() * 2500) / 100 };
    const rev = Math.round(rnd() * 6000000) / 10000;
    const x = F.resultOf(a, rev), y = BF.resultOf({ ...a, rte: 86, cycles: 1 }, rev);
    const gap = (u, v) => (u === null || v === null ? (u === v ? 0 : Infinity) : Math.abs(u - v));
    worst = Math.max(worst, gap(x.debt, y.debt), gap(x.coverage, y.coverage), gap(x.npv, y.npv), gap(x.irr, y.irr), gap(F.breakevenToll(a), y.toll));
    n++; if (x.irr !== null) both++;
  }
  check(worst === 0, `${n} seeded cases: the debt payment, coverage, NPV, IRR and the toll equal the battery page's library exactly`, `largest gap ${worst}; ${both} with a rate of return`);
}

console.log(failed ? `\n${failed} FAILED` : "\nall passed");
process.exit(failed ? 1 : 0);
