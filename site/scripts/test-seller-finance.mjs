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
check(JSON.stringify(solarNow) === JSON.stringify({ capex: 1375, share: 60, rate: 8, term: 35, fom: 12.5, deg: 0, life: 35, hurdle: 12, cshare: 0, cprice: 0, ppa: 35 }), "the defaults of solar (session 208: a hurdle rate of 12, Lazard's cost of equity; session 212: no contract; session 264: a PPA term of the life)", JSON.stringify(solarNow));
check(F.defaultsOf({ capex: 1110, fom: 22, life: 20, deg: F.BATTERY_DEG }).deg === 2.6 && /2\.6 percent a year/.test(F.BATTERY_DEG_SOURCE) && /40% equity at a 12% cost/.test(F.SPECS.hurdle.source) && F.HURDLE === 12,
  "a battery's degradation default is Lazard's 2.6 percent a year, and the hurdle rate is the weighted cost 0.6 x 8 + 0.4 x 12");
// the hand cases below were worked at session 186's default hurdle rate of 8, and stay on it
const solar = { ...solarNow, hurdle: 8 };
check(F.KEYS.length === 11 && new Set(F.KEYS.map((k) => F.SPECS[k].letter)).size === 11, "eleven assumptions, eleven different letters (session 212: the contract's share and price; session 264: the PPA term)");
check(JSON.stringify(F.KEYS) === JSON.stringify(["capex", "share", "rate", "term", "fom", "deg", "life", "hurdle", "cshare", "cprice", "ppa"]) && JSON.stringify(F.FINANCE_KEYS) === JSON.stringify(F.KEYS.slice(0, 8)), "in the order asked, the contract's three last (session 264: the PPA term eleventh)");
check(/fully merchant/.test(F.SPECS.cshare.source) && /fully merchant/.test(F.SPECS.cprice.source), "the contract's two defaults say the default is fully merchant");
check(F.contractUnits("energy").priceUnit === "USD per MWh" && F.contractUnits("toll").priceUnit === "USD per kW-month" && /energy/.test(F.contractUnits("energy").shareUnit) && /capacity/.test(F.contractUnits("toll").shareUnit), "an energy contract is a share of the energy at USD per MWh; a toll a share of the capacity at USD per kW-month");

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
check(["ac", "bs", "ar", "bt", "af", "bd", "al", "bh", "v"].every(F.isScenarioParam) && ["ds", "mw", "hr", "bmw", "dur", "asset", "ae", "az", "fom", "hub"].every((k) => !F.isScenarioParam(k)) && ["ay", "by"].every(F.isScenarioParam), "the scenarios' parameters are told from the page's own");
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

// session 212: the contract as two scenario assumptions (the battery page's form, session 208)
{
  const c = { ...solar, term: 10, life: 12, fom: 10, cshare: 50, cprice: 30, ppa: 10 };   // session 264: the PPA term is the debt's here, as every contract was until then
  const energy = { kind: "energy", energyKw: 2.2 };   // 2.2 MWh a year per kW: 50 percent of it at USD 30 is 33 a kW
  check(near(F.contractYear(c, energy), 33) && near(F.contractYear({ ...c, cshare: 0 }, energy), 0) && near(F.contractYear(c), 180), "an energy contract pays share x energy x price; a toll pays share x price x 12; none at a share of 0");
  check(near(F.merchantShare(c), 0.5) && near(F.merchantShare({ ...c, cshare: 0 }), 1) && near(F.merchantShare({ capex: 1 }), 1), "the merchant share is the rest; 1 without the key");
  const fl = F.flows(c, 100, energy), f0 = F.flows({ ...c, cshare: 0 }, 100, energy);
  check(near(fl[1], 33 + 50 - 10 - F.debtService(c)) && near(fl[10], 33 + 50 - 10 - F.debtService(c)) && near(fl[11], 100 - 10) && near(fl[12], 100 - 10), "the contract runs for the debt's years, the market on the rest; after them the whole plant in the market");
  check(f0.every((v, i) => near(v, F.flows({ ...c, cshare: 0 }, 100)[i])), "at a share of 0 the flows are what they were");
  check(near(F.coverage(c, 100, energy), (33 + 50 - 10) / F.debtService(c)) && near(F.coverage({ ...c, cshare: 0 }, 100, energy), F.coverage({ ...c, cshare: 0 }, 100)), "coverage reads the contract; none at a share of 0");
  check(JSON.stringify(F.resultOf({ ...c, cshare: 0, cprice: 30 }, 100, energy)) === JSON.stringify(F.resultOf({ ...c, cshare: 0, cprice: 0 }, 100, energy)), "a price with no share moves nothing");
  const old = { ...c }; delete old.cshare; delete old.cprice;
  check(JSON.stringify(F.resultOf(old, 100, energy)) === JSON.stringify(F.resultOf({ ...c, cshare: 0, cprice: 0 }, 100, energy)), "an older set of assumptions, without the two contract keys, is read as no contract");
  check(near(F.contractPrice(c, 2.2), F.contractPrice({ ...c, cshare: 0 }, 2.2)) && near(F.breakevenToll(c), F.breakevenToll({ ...c, cshare: 0 })), "the breakeven contract price and the toll do not read the contract");
  const bars = F.sensitivity(c, 100, energy);
  check(bars.length === 11 && bars.some((b) => b.key === "cshare") && bars.some((b) => b.key === "cprice") && bars.some((b) => b.key === "ppa"), "with a contract, eleven bars, the contract's three among them (session 264: the PPA term)");
  check(F.sensitivity({ ...c, cshare: 0 }, 100, energy).length === 8 && !F.sensitivity({ ...c, cshare: 0, cprice: 30 }, 100, energy).some((b) => b.key === "cprice"), "at a share of 0 the contract's rows are not drawn at all (as session 211 on the battery)");
  const sh = bars.find((b) => b.key === "cshare");
  check(sh.down.value === 40 && sh.up.value === 60 && near(sh.up.npv, F.npv(c.hurdle, F.flows({ ...c, cshare: 60 }, 100, energy))), "the share's row moves 10 points each way");
  check(F.isScenarioParam("an") && F.isScenarioParam("bp") && !F.isScenarioParam("ax"), "the contract's letters n and p are scenario parameters");
  const sc = F.parseScenarios({ an: "50", ap: "30", bn: "200" }, solarNow);
  check(sc.a.cshare === 50 && sc.a.cprice === 30 && sc.b.cshare === 100, "the address carries the contract, bounded");
  check(F.carry("?iso=ercot&an=50&ap=30&ac=1500", false) === "&an=50&ap=30", "a change of asset keeps the contract and drops the costs");
}

// session 235: the breakeven PPA price (the contract price at which NPV is zero) and "Make B a PPA"
{
  const energy = { kind: "energy", energyKw: 2.2 };
  const m = { ...solar, cshare: 0, cprice: 0 };                       // a merchant scenario: the breakeven is for the whole plant
  const zero = (a, c) => Math.abs(F.npv(a.hurdle, F.flows(a, 60, c))) < 1e-7;
  const p = F.breakevenPpa(m, 60, energy);
  check(F.ppaShare(m) === 100 && F.ppaShare({ ...m, cshare: 40 }) === 40 && F.ppaShare({ capex: 1 }) === 100, "the breakeven is at the scenario's own share, or the whole plant when it holds no contract");
  check(p !== null && p > 0 && zero({ ...m, cshare: 100, cprice: p }, energy), "at the breakeven PPA price for the whole plant, NPV is zero", String(p));
  const half = { ...solar, term: 10, life: 12, cshare: 50, cprice: 30 };
  const ph = F.breakevenPpa(half, 60, energy);
  check(ph !== null && zero({ ...half, cprice: ph }, energy), "at a share of 50 percent and a term shorter than the life, NPV is zero at the breakeven price", String(ph));
  check(near(ph, F.breakevenPpa({ ...half, cprice: 999 }, 60, energy)), "the breakeven price does not read the scenario's own contract price");
  const h0 = { ...m, hurdle: 0 };
  check(zero({ ...h0, cshare: 100, cprice: F.breakevenPpa(h0, 60, energy) }, energy), "at a hurdle rate of zero too");
  const toll = F.breakevenPpa(m, 60);                                  // a toll: USD per kW-month on the capacity
  check(toll !== null && zero({ ...m, cshare: 100, cprice: toll }) && near(toll * 12, p * 2.2, 1e-7), "a toll's breakeven sets NPV to zero, and pays the same dollars a year as the energy price does");
  check(F.breakevenPpa(m, 60, { kind: "energy", energyKw: 0 }) === null, "no breakeven price with no energy to price");
  const rich = F.breakevenPpa({ ...half, cshare: 10 }, 5000, energy);
  check(rich !== null && rich < 0, "where the market alone clears the hurdle, the breakeven price is below zero (the page says so in words)");
  const b = F.asPpa(m, 60, energy);
  check(b.cshare === 100 && b.cprice >= p && b.cprice - p < 0.01 + 1e-9 && Number.isInteger(Math.round(b.cprice * 1e6) / 1e4) && F.npv(b.hurdle, F.flows(b, 60, energy)) >= 0, "Make B a PPA: the whole plant at the breakeven price rounded up to the cent, so NPV is zero or just above", JSON.stringify(b));
  check(Object.keys(m).every((k) => k === "cshare" || k === "cprice" || b[k] === m[k]), "and no other assumption moves");
  check(solarNow.cshare === 0 && solarNow.cprice === 0, "the defaults stay merchant");
  check(F.asPpa(m, 60, { kind: "energy", energyKw: 0 }) === null, "no PPA to make where there is no energy");
}

// session 264: the PPA term, the eleventh assumption
{
  const energy = { kind: "energy", energyKw: 2.2 };
  check(solarNow.ppa === 35 && F.defaultsOf({ capex: 2100, fom: 32.25, life: 30 }).ppa === 30 && F.defaultsOf({ capex: 1110, fom: 22, life: 20 }).ppa === 20, "the PPA term's default is the asset's life: 35, 30, 20");
  check(F.SPECS.ppa.letter === "y" && F.SPECS.ppa.min === 1 && F.SPECS.ppa.max === 40 && F.SPECS.ppa.whole && F.SPECS.ppa.label === "PPA term" && F.SPECS.ppa.unit === "years", "PPA term, years: letter y, 1 to 40, whole");
  const c = { ...solar, term: 10, life: 20, fom: 10, cshare: 50, cprice: 30, ppa: 15 };
  const fl = F.flows(c, 100, energy);
  check(F.contractYears(c) === 15 && near(fl[11], 33 + 50 - 10) && near(fl[15], 33 + 50 - 10) && near(fl[16], 100 - 10) && near(fl[10], 33 + 50 - 10 - F.debtService(c)), "the contract runs for the PPA term (15 years), the debt for its own (10)");
  check(F.contractYears({ ...c, ppa: 40 }) === 20, "a PPA term longer than the life is cut to the life");
  const old = { ...c }; delete old.ppa;
  check(F.contractYears(old) === 10, "a set without the key runs the contract for the debt's years, as before");
  const at = (y) => F.breakevenPpa({ ...c, ppa: y }, 60, energy);
  check(at(5) > at(15) && Math.abs(F.npv(c.hurdle, F.flows({ ...c, ppa: 5, cprice: at(5) }, 60, energy))) < 1e-7, "a shorter PPA needs a higher breakeven price, and NPV is zero at it");
  const dflt = { ...solar, cshare: 0, cprice: 0 };
  check(near(F.breakevenPpa(dflt, 59.85, energy), F.breakevenPpa({ ...dflt, ppa: undefined }, 59.85, energy)), "at the default the breakeven PPA price is what it was");
  const s1 = F.parseScenarios({ at: "20" }, solar), s2 = F.parseScenarios({ at: "20", ay: "12" }, solar), s3 = F.parseScenarios({ ay: "99" }, solar);
  check(s1.a.ppa === 35 && s2.a.ppa === 12 && s3.a.ppa === 40 && s1.b.ppa === 35, "the PPA term is never read from the debt's term (a shared address opens what the browser showed); a typed PPA term is read; a value past 40 is held at 40");
  check(F.carry("ay=12&by=20&v=b", false) === "&v=b" && F.carry("ay=12", true) === "&ay=12", "a change of asset drops the PPA term, whose default is the asset's");
}

console.log(failed ? `\n${failed} FAILED` : "\nall passed");
process.exit(failed ? 1 : 0);
