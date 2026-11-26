// Chain 740 (lab-desktop window 3), session 10802: the datacenter of /impact (lib/dcimpact.ts) against arithmetic done
// by hand from the statutes and the parameter files, for three announced projects whose own documents state MW,
// investment and jobs (site/data/forecast/datacenter_announced.json): Meta in Richland Parish, Louisiana (LED, 13 July
// 2026), CleanArc in Caroline County, Virginia (VEDP, November 2025), Penzance in Berkeley County, West Virginia (the
// governor, 26 February 2026). Each tax line is worked in the comments; the test fails if the code and the hand sum differ.
// Run: node --test site/scripts/test-datacenter.test.mjs (tests/test_session10802_datacenter.py runs it).
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const D = await import("../lib/dcimpact.ts");
const F = await import("../lib/forecast.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = { announced: data("datacenter_announced.json"), rules: data("datacenter_rules.json"), wages: data("datacenter_wages.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), deflator: data("deflator.json") };
const near = (a, b, msg = "", rel = 1e-9) => assert.ok(Math.abs(a - b) <= rel * Math.max(1, Math.abs(b)), `${msg} ${a} is not ${b}`);

test("defaults: the announced projects' medians, JLARC's split, refresh and build time, CBP's wages in 2025 dollars", () => {
  const x = D.dcDefaults(P, "va");
  assert.equal(x.mw, 1800);                       // median of the 7 MW stated (3 to 5,000)
  near(x.invest, D.dcRound(1800 * 8.333333, 2));   // USD 8.333333 million a MW (median of 6), to the cent of a million
  near(x.perm, 375);                              // 1,800 MW x 0.208333 jobs a MW, to one decimal
  near(x.cons, D.dcRound((x.invest / 1000) * 325, 1));  // 325 construction jobs a USD billion (median of 6)
  assert.equal(x.bld, 19.6); assert.equal(x.eq, 68.2); assert.equal(x.land, 6.1); assert.equal(x.refresh, 5);
  assert.equal(x.build, 2);                       // 18 months in whole years
  assert.equal(x.life, 20);                       // a horizon, not a sourced life
  assert.equal(x.opwage, 152609);                 // CBP 2023 518210 payroll per job, 144,970.00 x 128.90425 / 122.452
  assert.equal(x.conswage, 74336);                // CBP 2023 2362 and 238, 70,614.93 x the same
  near(x.sales, 5.77);                            // Tax Foundation: 5.3 state plus 0.47 average local
  assert.equal(x.dcex, true); assert.equal(x.brate, null); assert.equal(x.mwh, null);
});

test("income tax: the datacenter's copy is lib/forecast.ts's", () => {
  for (const st of ["va", "la", "wv", "ny", "tx", "ca"]) for (const w of [0, 20000, 67440, 152609, 400000])
    near(D.dcIncomeTax(P.income.states[st], w), F.incomeTax(P.income.states[st], w), `${st} ${w}`);
});

test("Louisiana: Meta, Richland Parish, as LED's 13 July 2026 release states it (5,000 MW, USD 50 billion, 1,000 operational jobs, 7,500 construction jobs at peak)", () => {
  const x = D.dcDefaults(P, "la", { mw: 5000, invest: 50000, perm: 1000, cons: 7500, start: 2026, build: 5, life: 20, brate: 10, erate: 10 });
  const r = D.dcRun(x, P);
  assert.ok(r.ok);
  // Eligible under R.S. 47:305.73: 1,000 >= 50 jobs; spent before 2029 = 3 of 5 construction years x USD 50 billion = 30 billion >= 200 million.
  assert.equal(r.exemption.eligible, true);
  // Equipment = 50e9 x 68.2% = 34.1e9, bought over 2026 to 2030 and again in operating years 5, 10 and 15 (2036, 2041, 2046).
  // Rate 5.00 + 5.13 = 10.13 percent: 34.1e9 x 0.1013 = 3,454,330,000 a purchase; four purchases before the exemption = 13,817,320,000.
  near(r.sums.salesbefore, 13817320000, "LA sales before");
  // Exempt for the agreement's 20 years from 2026 (years before 2046): the build, 2036 and 2041: 3 x 3,454,330,000 = 10,362,990,000 forgone.
  near(r.sums.forgone, 10362990000, "LA forgone");
  near(r.sums.sales, 3454330000, "LA paid (2046's purchase)");
  // Property (Constitution art. VII, s. 18): building 50e9 x 19.6% = 9.8e9 at 10% = 980e6 assessed; equipment 34.1e9 at 15% = 5,115e6;
  // the reader's 10 percent of assessed value: 98,000,000 + 511,500,000 = 609,500,000 a year; 20 years = 12,190,000,000.
  near(D.dcStat(r, "y1:propb"), 98000000); near(D.dcStat(r, "y1:prope"), 511500000);
  near(r.sums.property, 12190000000, "LA property over the life");
  // Income tax (3 percent over a 12,875 standard deduction): operations (67,440 - 12,875) x 0.03 = 1,636.95 x 1,000 = 1,636,950 a year x 20;
  // construction (70,480 - 12,875) x 0.03 = 1,728.15 x 7,500 = 12,961,125 a year x 5.
  near(r.sums.income, 1636950 * 20 + 12961125 * 5, "LA income");
  // On site only: no public multiplier for Louisiana.
  assert.equal(r.chain.held, false); assert.equal(D.dcStat(r, "c:jobs:supply_chain"), null);
  near(D.dcStat(r, "c:earnings:total"), 7500 * 70480 * 5); near(D.dcStat(r, "o:earnings:total"), 1000 * 67440);  // construction over the 5-year build
  near(D.dcStat(r, "c:jobs:total"), 7500 * 5); near(D.dcStat(r, "year:2027:jobs"), 7500);
  assert.equal(r.elec.held, false);               // no Louisiana statute on electricity read
  // The same project without the exemption: every purchase taxed.
  const nx = D.dcRun({ ...x, dcex: false }, P);
  near(nx.sums.forgone, 0); near(nx.sums.sales, 13817320000);
});

test("Virginia: CleanArc, Caroline County, as VEDP's November 2025 release states it (nearly 1,000 MW, USD 3 billion, 50 jobs)", () => {
  const x = D.dcDefaults(P, "va", { mw: 1000, invest: 3000, perm: 50, start: 2026, build: 2, life: 20, mwh: 5000000 });
  const r = D.dcRun(x, P);
  assert.ok(r.ok);
  near(x.cons, D.dcRound(3 * 325, 1));            // the release states no construction figure: the default, 975
  // Code 58.1-609.3(18): USD 3 billion >= 150 million and 50 >= 50 jobs: eligible; purchases through 2034 exempt.
  assert.equal(r.exemption.eligible, true);
  // Equipment 3e9 x 68.2% = 2.046e9; at 5.77 percent 118,054,200 a purchase; bought in the build (2026-27) and in 2033, 2038, 2043.
  near(r.sums.salesbefore, 4 * 118054200, "VA before");
  near(r.sums.forgone, 2 * 118054200, "VA forgone: the build and 2033");
  near(r.sums.sales, 2 * 118054200, "VA paid: 2038 and 2043");
  // Consumption tax (58.1-2900): 5,000,000 MWh a year is 416,666,666.67 kWh a month:
  // 2,500 x 0.001595 + 47,500 x 0.001085 + 416,616,666.67 x 0.000875 = 364,595.108 a month, 4,375,141.30 a year.
  near(D.dcStat(r, "y1:elec"), 4375141.3, "VA electricity a year", 1e-9);
  near(r.sums.elec, 4375141.3 * 20, "VA electricity over 20 years", 1e-9);
  // JLARC's Virginia ratios, each construction year: jobs 975 x (35,110 + 9,945 + 13,992) / 35,110; earnings 975 x 74,336 x 4,282.3 / 2,646.6; over the 2-year build twice that.
  assert.equal(r.chain.held, true);
  near(D.dcStat(r, "c:jobs:total"), 2 * 975 * 59047 / 35110);
  near(D.dcStat(r, "c:earnings:total"), 2 * 975 * 74336 * (2646.6 + 843.8 + 791.9) / 2646.6);
  // Operations: 50 x (4,373 + 6,615 + 3,830) / 4,373 jobs; 50 x 152,609 x (419.4 + 552.2 + 216.8) / 419.4 earnings.
  near(D.dcStat(r, "o:jobs:total"), 50 * 14818 / 4373);
  near(D.dcStat(r, "o:earnings:total"), 50 * 152609 * 1188.4 / 419.4);
  // Income tax (2, 3, 5 and 5.75 percent over 3,000, 5,000 and 17,000; deduction 8,750, exemption 930), each job on the average wage.
  const vaTax = (w) => { const t = Math.max(0, w - 8750 - 930); return Math.min(t, 3000) * 0.02 + Math.max(0, Math.min(t, 5000) - 3000) * 0.03 + Math.max(0, Math.min(t, 17000) - 5000) * 0.05 + Math.max(0, t - 17000) * 0.0575; };
  const oj = 50 * 14818 / 4373, oe = 50 * 152609 * 1188.4 / 419.4;
  near(D.dcStat(r, "y1:income"), oj * vaTax(oe / oj), "VA operating income tax");
  // No property rate is held statewide: the line is not held until the reader types the locality's rates.
  assert.equal(r.property.held, false); assert.equal(r.sums.property, null);
});

test("West Virginia: Penzance, Berkeley County, as the governor's 26 February 2026 release states it (600 MW, USD 4 billion, 125 permanent, 1,000 construction)", () => {
  const x = { ...D.dcDefaults(P, "wv"), mw: 600, invest: 4000, perm: 125, cons: 1000, start: 2026, build: 2, life: 20 };
  const r = D.dcRun(x, P);
  assert.ok(r.ok);
  // No West Virginia datacenter statute is read (its code host does not answer): no exemption, before exemptions.
  assert.equal(r.exemption.held, false);
  // Equipment 4e9 x 68.2% = 2.728e9 at 6.0 + 0.6 = 6.6 percent = 180,048,000 a purchase; four purchases = 720,192,000.
  near(r.sums.salesbefore, 720192000); near(r.sums.forgone, 0); near(r.sums.sales, 720192000);
  // Income tax (2.11, 2.81, 3.16, 4.22, 4.58 percent over 10,000, 25,000, 40,000, 60,000; exemption 2,000):
  // operations 56,743 - 2,000 = 54,743: 211 + 421.5 + 474 + 14,743 x 0.0422 = 1,728.6546 x 125 = 216,081.825 a year.
  near(D.dcStat(r, "y1:income"), 216081.825, "WV operating income tax");
  assert.equal(r.sums.property, null); assert.equal(r.elec.held, false); assert.equal(r.chain.held, false);
});

test("a building's taxable share is taxed only where given, and Louisiana's exemption reaches it", () => {
  const base = { ...D.dcDefaults(P, "la"), mw: 600, invest: 4000, perm: 125, start: 2026, build: 2, life: 10 };
  const a = D.dcRun(base, P), b = D.dcRun({ ...base, matshare: 40 }, P);
  // building 4e9 x 19.6% = 784e6; 40% taxable at 10.13% = 31,767,680, all in the build, all forgone (construction covered).
  near(b.sums.salesbefore - a.sums.salesbefore, 784e6 * 0.4 * 0.1013);
  near(b.sums.forgone - a.sums.forgone, 784e6 * 0.4 * 0.1013);
  // Virginia's exemption does not reach "general building improvements or other fixtures".
  const v = { ...D.dcDefaults(P, "va"), mw: 600, invest: 4000, perm: 125, start: 2026, build: 2, life: 10 };
  const va = D.dcRun(v, P), vb = D.dcRun({ ...v, matshare: 40 }, P);
  near(vb.sums.forgone - va.sums.forgone, 0);
  near(vb.sums.salesbefore - va.sums.salesbefore, 784e6 * 0.4 * 0.0577);
});

test("thresholds: too few jobs or too little investment, no exemption", () => {
  const x = { ...D.dcDefaults(P, "va"), invest: 100, perm: 60, start: 2026, build: 2, life: 5 };
  assert.equal(D.dcRun(x, P).exemption.eligible, false);               // USD 100 million < 150 million
  assert.equal(D.dcRun({ ...x, invest: 500, perm: 40 }, P).exemption.eligible, false);  // 40 < 50 jobs
  // Louisiana: the investment must be spent before 2029; a build of 2030 to 2031 spends none.
  const l = { ...D.dcDefaults(P, "la"), invest: 5000, perm: 100, start: 2030, build: 2, life: 5 };
  assert.equal(D.dcRun(l, P).exemption.eligible, false);
});

test("property: the abatement and the building's straight line", () => {
  const x = { ...D.dcDefaults(P, "va"), mw: 100, invest: 1000, perm: 50, start: 2026, build: 1, life: 10, brate: 1, erate: 4, bldyears: 40, abate: 50, abateyears: 5 };
  const r = D.dcRun(x, P);
  // year 1: building 196e6 x 1% + equipment 682e6 x 4% = 1,960,000 + 27,280,000 = 29,240,000, half abated = 14,620,000
  near(D.dcStat(r, "y1:property"), 14620000);
  // operating year 6 (i = 5): no abatement; building 196e6 x (1 - 5/40) x 1% = 1,715,000; equipment 27,280,000
  near(D.dcStat(r, `year:${2026 + 1 + 5}:property`), 1715000 + 27280000);
});

test("Minnesota (297A.68 subd. 42): the state's rate only, for 35 years from the first purchase, USD 30 million", () => {
  const x = D.dcDefaults(P, "mn", { invest: 1000, perm: 50, start: 2026, build: 2, life: 40 });
  const r = D.dcRun(x, P);
  assert.equal(r.exemption.eligible, true);
  // equipment 1e9 x 68.2% = 682e6, bought in the build and in 2033, 2038, ... 2063 (eight purchases) at 8.14 percent:
  // 682e6 x 0.0814 = 55,514,800 each, 444,118,400 before the exemption.
  near(r.sums.salesbefore, 8 * 682e6 * 0.0814, "MN before");
  // exempt before 2061 (35 years from 2026): seven purchases, at the state's 6.88 percent: 7 x 682e6 x 0.0688 = 328,451,200.
  near(r.sums.forgone, 7 * 682e6 * 0.0688, "MN forgone");
  assert.equal(D.dcRun({ ...x, start: 2042 }, P).exemption.eligible, false);  // certified before 1 July 2042 only
  assert.equal(D.dcRun({ ...x, invest: 29 }, P).exemption.eligible, false);   // below USD 30 million
});

test("Maryland (Tax-General 11-239): 10 years, 20 with USD 250 million; 5 positions", () => {
  const big = D.dcRun(D.dcDefaults(P, "md", { invest: 300, perm: 5, start: 2026, build: 2, life: 20 }), P);
  // equipment 300e6 x 68.2% = 204.6e6 at 6 percent = 12,276,000 a purchase; build, 2033, 2038, 2043 all before 2046: 49,104,000.
  near(big.sums.forgone, 4 * 12276000, "MD 20 years");
  const small = D.dcRun(D.dcDefaults(P, "md", { invest: 200, perm: 5, start: 2026, build: 2, life: 20 }), P);
  // 200e6 x 68.2% = 136.4e6 at 6 percent = 8,184,000; before 2036 only the build and 2033: 16,368,000 of 32,736,000.
  near(small.sums.forgone, 2 * 8184000, "MD 10 years"); near(small.sums.salesbefore, 4 * 8184000);
  assert.equal(D.dcRun(D.dcDefaults(P, "md", { invest: 200, perm: 4 }), P).exemption.eligible, false);
});

test("Florida (212.08(5)(r)): USD 150 million and a critical IT load of 100 MW; South Carolina certified before 2032; Nevada's abatement never applied", () => {
  assert.equal(D.dcRun(D.dcDefaults(P, "fl", { mw: 100, invest: 150, perm: 10 }), P).exemption.eligible, true);
  assert.equal(D.dcRun(D.dcDefaults(P, "fl", { mw: 99, invest: 1500, perm: 10 }), P).exemption.eligible, false);
  const sc = D.dcDefaults(P, "sc", { invest: 100, perm: 25, start: 2031, build: 2, life: 20 });
  const s = D.dcRun(sc, P);
  assert.equal(s.exemption.eligible, true);
  // equipment 68.2e6 at 7.49 percent = 5,108,180 a purchase: build (2031-32), 2038, 2043 (> 2041: taxed), 2048: two exempt.
  near(s.sums.forgone, 2 * 68.2e6 * 0.0749, "SC through 2041");
  assert.equal(D.dcRun({ ...sc, start: 2032 }, P).exemption.eligible, false);
  const nv = D.dcRun(D.dcDefaults(P, "nv", { invest: 5000, perm: 500 }), P);
  assert.equal(nv.exemption.held, true); assert.equal(nv.exemption.eligible, false); near(nv.sums.forgone, 0);
});

test("Arizona through the tenth full year (41-1519), North Carolina USD 75 million, Wisconsin USD 150 million and the building, Utah held as words", () => {
  const az = D.dcRun(D.dcDefaults(P, "az", { invest: 100, perm: 5, start: 2026, build: 2, life: 20 }), P);
  // equipment 68.2e6 at 8.54 percent = 5,824,280 a purchase; build (2026-27), 2033 before 2037; 2038 and 2043 taxed.
  assert.equal(az.exemption.eligible, true); near(az.sums.forgone, 2 * 68.2e6 * 0.0854, "AZ");
  assert.equal(D.dcRun(D.dcDefaults(P, "az", { invest: 49, perm: 5 }), P).exemption.eligible, false);
  assert.equal(D.dcRun(D.dcDefaults(P, "nc", { invest: 75, perm: 5 }), P).exemption.eligible, true);
  assert.equal(D.dcRun(D.dcDefaults(P, "nc", { invest: 74, perm: 5 }), P).exemption.eligible, false);
  const wi = D.dcRun(D.dcDefaults(P, "wi", { invest: 200, perm: 5, matshare: 40, start: 2026, build: 2, life: 10 }), P);
  // no term: every purchase forgone: build and 2033 equipment (2 x 136.4e6) and the building's 40 percent of 39.2e6, at 5.72 percent.
  near(wi.sums.forgone, (2 * 136.4e6 + 39.2e6 * 0.4) * 0.0572, "WI");
  const ut = D.dcRun(D.dcDefaults(P, "ut", { invest: 2000, perm: 100 }), P);
  assert.equal(ut.exemption.held, true); assert.equal(ut.exemption.eligible, false);
});

test("Montana's class seventeen: 0.9 percent of market value with USD 50 million, else no rule (the reader's rate on cost)", () => {
  const mt = D.dcRun(D.dcDefaults(P, "mt", { invest: 100, perm: 5, brate: 60, erate: 60 }), P);
  // building 19.6e6 x 0.009 x 60% = 105,840; equipment 68.2e6 x 0.009 x 60% = 368,280
  near(D.dcStat(mt, "y1:propb"), 105840); near(D.dcStat(mt, "y1:prope"), 368280);
  const small = D.dcRun(D.dcDefaults(P, "mt", { invest: 40, perm: 5, brate: 1, erate: 1 }), P);
  near(D.dcStat(small, "y1:propb"), 40e6 * 0.196 * 0.01);
});

test("a check key carries every input and gives the figure back", () => {
  const x = { ...D.dcDefaults(P, "la"), brate: 9.5, matshare: null };
  const k = D.dcKey(x);
  const p = D.dcParseKey(`${k}|sum:sales`);
  assert.deepEqual(p.x, x); assert.equal(p.figure, "sum:sales");
});
