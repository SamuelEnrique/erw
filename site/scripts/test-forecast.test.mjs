// Session 4203 (chain 239): every formula of lib/forecast.ts against arithmetic done by hand from the parameter files
// and the JEDI rows (tests/fixtures/forecast/jedi_rows.json, eight states of nlr_jedi_multipliers). docs/methods/forecast.md
// gives the formulas. Run: node --test site/scripts/test-forecast.test.mjs (tests/test_session4203_forecast.py runs it).
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const F = await import("../lib/forecast.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = {
  jediCosts: data("jedi_costs.json"), eiaCapex: data("eia_capex.json"), deflator: data("deflator.json"), capacity: data("capacity_factors.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), property: data("property_rules.json"), taxable: data("jedi_taxable.json"), gas: data("gas.json"),
  exemptions: data("sales_exemptions.json"),
};
const ROWS = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "forecast", "jedi_rows.json"), "utf8")).rows;
const near = (a, b, rel = 1e-9, msg = "") => assert.ok(Math.abs(a - b) <= rel * Math.max(1, Math.abs(b)), `${msg} ${a} is not ${b}`);
const per = (tech, st, ph, e, m) => ROWS.find((r) => r.entity === `nlr_jedi:${tech}:${st}:${ph}:${e}` && r.variable === m).value;
const idx = P.deflator.index;
const toNow = (y) => idx["2025"] / idx[String(y)];

test("the deflator converts a year's dollars to 2025's by the index ratio", () => {
  near(F.to2025(P, 2017), 128.90425 / 99.99975);
  near(F.to2025(P, 2010), 128.90425 / 89.6185);
  near(F.to2025(P, 2025), 1);
  assert.throws(() => F.to2025(P, 1990));
});

test("defaults: EIA's state capex in 2025 dollars, its construction time rounded up to years, its operating life", () => {
  const d = F.defaults(P, "land_based_wind", "tx");
  near(d.capex, Math.round(1408 * (idx["2025"] / idx["2023"]) * 100) / 100, 1e-12, "Texas wind capex (EIA Houston 1,408 in 2023 dollars)");
  assert.equal(d.build, 1); assert.equal(d.life, 25); assert.equal(d.mw, 200); assert.equal(d.rate, 7); assert.equal(d.local, 100);
  const g = F.defaults(P, "natural_gas", "tx");
  assert.equal(g.build, 2); assert.equal(g.life, 40); assert.equal(g.heat, 6266); assert.equal(g.cf, 0.65); assert.equal(g.instate, 0);
  const geo = F.defaults(P, "geothermal", "tx");
  near(geo.capex, Math.round(3963 * (idx["2025"] / idx["2023"]) * 100) / 100, 1e-12, "no Texas figure: EIA's base case");
  assert.equal(geo.taxable, null);
  const ca = F.defaults(P, "geothermal", "ca");
  const cities = P.eiaCapex.technologies.geothermal.states.ca.cities.map((c) => c.usd_per_kw);
  near(ca.capex, Math.round((cities.reduce((a, b) => a + b, 0) / cities.length) * (idx["2025"] / idx["2023"]) * 100) / 100, 1e-12, "California: the mean of its cities");
  const pv = F.defaults(P, "utility_pv", "tx");
  assert.equal(pv.ilr, P.capacity.utility_pv_ilr.states.tx.median);
  near(pv.sales, (0.0625 + 0.0195) * 100, 1e-12, "Texas sales tax 6.25 plus 1.95");
});

test("construction at JEDI's own spending gives JEDI's own figure, and scales with spending only", () => {
  const tech = "land_based_wind", st = "tx";
  const cost = P.jediCosts.technologies[tech].states[st].cost_usd_per_mw;       // JEDI 2017 dollars per MW
  const x = { ...F.defaults(P, tech, st), mw: 300, capex: (cost / 1000) * toNow(2017) };  // JEDI's spending in 2025 dollars
  const r = F.run(x, ROWS, P);
  assert.ok(r.ok, r.why);
  near(r.construction.jobs.total, per(tech, st, "construction", "total", "jobs") * 300, 1e-9, "jobs");
  near(r.construction.earnings.onsite, per(tech, st, "construction", "onsite", "earnings") * 300 * toNow(2017), 1e-9, "earnings in 2025 dollars");
  // the same spending on half the MW gives the same construction effects
  const half = F.run({ ...x, mw: 150, capex: x.capex * 2 }, ROWS, P);
  near(half.construction.jobs.total, r.construction.jobs.total, 1e-9, "spending, not MW");
  // twice the capex, twice the construction; the operations do not move
  const dbl = F.run({ ...x, capex: x.capex * 2 }, ROWS, P);
  near(dbl.construction.jobs.supply_chain, 2 * r.construction.jobs.supply_chain);
  near(dbl.operations.jobs.total, r.operations.jobs.total);
  // local content scales both phases
  const loc = F.run({ ...x, local: 80 }, ROWS, P);
  near(loc.construction.jobs.total, 0.8 * r.construction.jobs.total);
  near(loc.operations.earnings.total, 0.8 * r.operations.earnings.total);
});

test("operations: JEDI per MW times MW (DC for PV) times local content, each year", () => {
  const x = { ...F.defaults(P, "utility_pv", "ca"), mw: 100, ilr: 1.3 };
  const r = F.run(x, ROWS, P);
  near(r.operations.jobs.total, per("utility_pv", "ca", "operations", "total", "jobs") * 130);
  near(r.operations.earnings.induced, per("utility_pv", "ca", "operations", "induced", "earnings") * 130 * toNow(2010));
  // operating spending as a percent of JEDI's default scales the operating figures only
  const om = F.run({ ...x, om: 45 }, ROWS, P);
  near(om.operations.jobs.onsite, 0.45 * r.operations.jobs.onsite);
  near(om.construction.jobs.total, r.construction.jobs.total);
  const op = r.years.filter((y) => y.phase === "operations");
  assert.equal(op.length, x.life);
  near(op[7].jobs.total, r.operations.jobs.total);
});

test("construction is spread evenly over the construction years, and the sums add up", () => {
  const x = { ...F.defaults(P, "natural_gas", "la") };
  const r = F.run(x, ROWS, P);
  const c = r.years.filter((y) => y.phase === "construction");
  assert.equal(c.length, 2); assert.equal(c[0].year, 2027); assert.equal(c[1].year, 2028);
  near(c[0].jobs.total, r.construction.jobs.total / 2);
  assert.equal(r.years.find((y) => y.phase === "operations").year, 2029);
  near(r.sums.jobs, r.construction.jobs.total + r.operations.jobs.total * x.life, 1e-9, "job-years over the life");
});

test("income tax: brackets, deductions, exemptions and credits of a single filer", () => {
  const I = P.income.states;
  assert.equal(F.incomeTax(I.tx, 80000), 0);
  // Illinois: 4.95 percent flat, no standard deduction, the personal exemption
  near(F.incomeTax(I.il, 60000), (60000 - (I.il.standard_deduction_single ?? 0) - I.il.personal_exemption_single) * 0.0495);
  // Iowa: 3.8 percent after the standard deduction, less the personal credit
  near(F.incomeTax(I.ia, 50000), (50000 - I.ia.standard_deduction_single) * 0.038 - I.ia.personal_credit_single);
  // Ohio: nothing below its first threshold
  const oh = I.oh.brackets.find((b) => b.rate > 0).over_usd;
  assert.equal(F.incomeTax({ ...I.oh, personal_exemption_single: 0 }, oh - 1), 0);
  // a bracket walk by hand: California at 60,000
  const ca = I.ca, t = 60000 - ca.standard_deduction_single - (ca.personal_exemption_single ?? 0);
  let tax = 0;
  for (let i = 0; i < ca.brackets.length; i++) {
    const lo = ca.brackets[i].over_usd, hi = ca.brackets[i + 1]?.over_usd ?? Infinity;
    if (t > lo) tax += (Math.min(t, hi) - lo) * ca.brackets[i].rate;
  }
  near(F.incomeTax(ca, 60000), Math.max(0, tax - (ca.personal_credit_single ?? 0)));
  assert.equal(F.incomeTax(I.ia, 1000), 0, "never below zero");
});

test("the year's income tax is jobs times one filer's tax on the average earnings", () => {
  const x = F.defaults(P, "land_based_wind", "mn");
  const r = F.run(x, ROWS, P);
  const y = r.years.find((v) => v.phase === "operations");
  near(y.income, y.jobs.total * F.incomeTax(P.income.states.mn, y.earnings.total / y.jobs.total));
});

test("property tax: Nebraska's nameplate tax and South Dakota's in-lieu taxes", () => {
  const ne = F.run({ ...F.defaults(P, "land_based_wind", "ne"), mw: 200 }, ROWS, P);
  assert.equal(ne.years.find((y) => y.phase === "operations").property, 200 * 3518);
  const sdx = { ...F.defaults(P, "land_based_wind", "sd"), mw: 100, cf: 0.4 };
  const sd = F.run(sdx, ROWS, P);
  near(sd.years.find((y) => y.phase === "operations").property, 100 * 3000 + 100 * 8760 * 0.4 * 0.45);
  const sdpv = F.run({ ...F.defaults(P, "utility_pv", "sd"), mw: 50, cf: 0.2 }, ROWS, P);
  near(sdpv.years.find((y) => y.phase === "operations").property, 50 * 3000 + 50 * 8760 * 0.2 * 0.9);
  const small = F.run({ ...sdx, mw: 4 }, ROWS, P);
  assert.equal(small.property.held, false, "under 5 MW is not a wind farm in 10-35-16");
  assert.equal(F.run(F.defaults(P, "natural_gas", "ne"), ROWS, P).property.held, false, "no rule for a gas plant");
});

test("property tax: Minnesota's production tiers", () => {
  const at = (mw, tech = "land_based_wind") => F.propertyTax(P, { ...F.defaults(P, tech, "mn"), mw, cf: 0.4 }, 0).tax;
  near(at(20), 20 * 8760 * 0.4 * 1.2); near(at(12), 12 * 8760 * 0.4 * 0.36); near(at(2), 2 * 8760 * 0.4 * 0.12);
  assert.equal(at(0.2), null, "0.25 MW or less is exempt");
  near(at(5, "utility_pv"), 5 * 8760 * 0.4 * 1.2); assert.equal(at(1, "utility_pv"), null, "1 MW AC or less is exempt");
});

test("property tax: Iowa's special valuation by assessment year, only with the ordinance and a levy", () => {
  const x = { ...F.defaults(P, "land_based_wind", "ia"), mw: 100, capex: 1500 };
  assert.equal(F.propertyTax(P, x, 3).tax, null, "off by default");
  assert.equal(F.propertyTax(P, { ...x, iaval: true }, 3).tax, null, "no levy given");
  const v = { ...x, iaval: true, levy: 30 };
  const pct = [0, 5, 10, 15, 20, 25, 30, 30, 30];
  pct.forEach((p, i) => near(F.propertyTax(P, v, i).tax, 1500 * 100 * 1000 * (p / 100) * (30 / 1000), 1e-12, `year ${i + 1}`));
});

test("property tax: the reader's own rate falls straight to zero", () => {
  const x = { ...F.defaults(P, "land_based_wind", "de"), mw: 100, capex: 1500, own: 1.5, ownyears: 20 };
  near(F.propertyTax(P, x, 0).tax, 150e6 * 0.015);
  near(F.propertyTax(P, x, 10).tax, 150e6 * 0.5 * 0.015);
  assert.equal(F.propertyTax(P, x, 25).tax, 0);
  assert.equal(F.propertyTax(P, { ...x, own: null }, 0).tax, null, "Texas: no rule held");
});

test("sales tax: spending times the taxable share times the rate, less the exemption, over the construction years", () => {
  const x = { ...F.defaults(P, "natural_gas", "tx"), mw: 500, capex: 1000, sales: 8, exempt: 25 };
  const r = F.run(x, ROWS, P);
  const total = 500e6 * 0.605882 * 0.08 * 0.75;
  near(r.sums.sales, total, 1e-6); near(r.years[0].sales, total / 2, 1e-6);
  assert.equal(r.sales.note, "after the exemption");
  const geo = F.run(F.defaults(P, "geothermal", "ca"), ROWS, P);
  assert.equal(geo.sums.sales, null); assert.equal(geo.sales.held, false);
});

test("severance: the gas plant's in-state fuel at the heat rate, capacity factor and price", () => {
  let seen;
  const sev = (s, v, p) => { seen = { s, v, p }; return v * p * 0.075; };
  const x = { ...F.defaults(P, "natural_gas", "tx"), mw: 500, cf: 0.5, heat: 7000, instate: 40, gasprice: 3 };
  const r = F.run(x, ROWS, P, sev);
  const mcf = (500 * 8760 * 0.5 * 7000 / 1000) / 1.034;
  near(seen.v, mcf * 0.4); near(seen.p, 3 * 1.034);
  near(r.years.find((y) => y.phase === "operations").severance, mcf * 0.4 * 3 * 1.034 * 0.075);
  assert.equal(F.run({ ...x, instate: 0 }, ROWS, P, sev).severance.held, false);
  assert.equal(F.run(F.defaults(P, "land_based_wind", "tx"), ROWS, P, sev).sums.severance, null);
});

test("present value: each year discounted from the first construction year at the real rate", () => {
  const x = { ...F.defaults(P, "land_based_wind", "ne"), mw: 100, rate: 7 };
  const r = F.run(x, ROWS, P);
  let pv = 0;
  for (const y of r.years) if (y.property !== null) pv += y.property / 1.07 ** (y.year - x.start);
  near(r.pv.property, pv);
  near(r.pv.taxes, r.pv.property + r.pv.sales + r.pv.income);
  near(F.run({ ...x, rate: 0 }, ROWS, P).pv.property, r.sums.property);
});

test("a state JEDI does not cover, or an input out of range, gives no figure", () => {
  assert.equal(F.run(F.defaults(P, "land_based_wind", "zz"), ROWS, P).ok, false);
  assert.equal(F.run({ ...F.defaults(P, "land_based_wind", "tx"), mw: 0 }, ROWS, P).ok, false);
  assert.equal(F.run({ ...F.defaults(P, "land_based_wind", "tx"), build: 0 }, ROWS, P).ok, false);
});

test("a check key carries every input and gives the figure back", () => {
  const x = { ...F.defaults(P, "land_based_wind", "ia"), iaval: true, levy: 31.5, own: null };
  const k = F.inputsKey(x);
  const back = F.parseKey(`${k}|pv:taxes`);
  assert.deepEqual(back.x, x); assert.equal(back.figure, "pv:taxes");
  const r = F.run(x, ROWS, P);
  assert.equal(F.stat(r, "pv:taxes"), r.pv.taxes);
  assert.equal(F.stat(r, "c:jobs:total"), r.construction.jobs.total);
  assert.equal(F.stat(r, "y1:property"), r.years.find((y) => y.phase === "operations").property);
  assert.equal(F.stat(r, `year:${x.start}:sales`), r.years[0].sales);
  assert.equal(F.stat(r, "nonsense"), null);
  assert.equal(F.parseKey("impact|x"), null);
});

test("the run's Python script recomputes every total of the tool", async () => {
  const { pythonOf, csvOf, stataOf } = await import("../lib/forecastfiles.ts");
  const S = await import("../lib/severance.ts");
  const rules = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "severance_rules.json"), "utf8"));
  const sev = (state, v, p) => { const st = state.toUpperCase(); if (!rules.states[st]?.products?.gas) return null; const r = S.compute(rules, { state: st, product: "gas", volume: v, price: p }); return r.baseTotal + r.fees.reduce((a, f) => a + f.amount, 0); };
  const cases = [
    [{ ...F.defaults(P, "land_based_wind", "ia"), iaval: true, levy: 28 }, { ...F.defaults(P, "utility_pv", "mn"), mw: 80 }],
    [{ ...F.defaults(P, "natural_gas", "tx"), instate: 60 }, { ...F.defaults(P, "land_based_wind", "sd"), own: null }],
    [{ ...F.defaults(P, "geothermal", "ca") }, { ...F.defaults(P, "land_based_wind", "tx"), own: 1.2, ownyears: 20 }],
    [{ ...F.defaults(P, "land_based_wind", "ks") }, { ...F.defaults(P, "utility_pv", "ks"), own: 0.8, ownyears: 25 }],
    [{ ...F.defaults(P, "utility_pv", "or"), iaval: true, optrate: 6200 }, { ...F.defaults(P, "utility_pv", "or"), iaval: true, own: 1, ownyears: 30 }],
    [{ ...F.defaults(P, "land_based_wind", "wy") }, { ...F.defaults(P, "land_based_wind", "wy"), own: 1.1, ownyears: 20 }],
    [{ ...F.defaults(P, "utility_pv", "fl"), own: 1, ownyears: 30 }, { ...F.defaults(P, "land_based_wind", "fl"), own: 1.2, ownyears: 25, start: 2030 }],
    [{ ...F.defaults(P, "utility_pv", "nc"), own: 0.7, ownyears: 30 }, { ...F.defaults(P, "utility_pv", "vt"), own: 1.4, ownyears: 25 }],
    [{ ...F.defaults(P, "utility_pv", "mi"), iaval: true }, { ...F.defaults(P, "utility_pv", "mi"), iaval: true, optrate: 2000, life: 30 }],
    [{ ...F.defaults(P, "utility_pv", "nv"), iaval: true, own: 1.1, ownyears: 30 }, { ...F.defaults(P, "geothermal", "nv"), iaval: true, own: 1.1, ownyears: 30 }],
    [{ ...F.defaults(P, "utility_pv", "va"), mw: 100, own: 0.8, ownyears: 30 }, { ...F.defaults(P, "utility_pv", "va"), mw: 160, own: 0.8, ownyears: 30 }],
    [{ ...F.defaults(P, "land_based_wind", "il"), levy: 80 }, { ...F.defaults(P, "natural_gas", "wv") }],
    [{ ...F.defaults(P, "land_based_wind", "wv") }, { ...F.defaults(P, "utility_pv", "il"), levy: 75, life: 30 }],
    [{ ...F.defaults(P, "utility_pv", "ny"), own: 1.5, ownyears: 30 }, { ...F.defaults(P, "utility_pv", "dc"), own: 2, ownyears: 20 }],
  ];
  const { execFileSync } = await import("node:child_process");
  const py = process.env.ERW_PYTHON || "python";
  for (const [a, b] of cases) {
    const x = { a, b }, rows = { a: ROWS.filter((r) => r.entity.includes(`:${a.tech}:${a.state}:`)), b: ROWS.filter((r) => r.entity.includes(`:${b.tech}:${b.state}:`)) };
    const r = { a: F.run(a, rows.a, P, sev), b: F.run(b, rows.b, P, sev) };
    assert.ok(r.a.ok && r.b.ok);
    const file = path.join(fs.mkdtempSync(path.join(fs.realpathSync(process.env.TEMP || process.env.TMPDIR || "/tmp"), "fc-")), "run.py");
    fs.writeFileSync(file, pythonOf(P, x, rows, r));
    let out;
    try { out = execFileSync(py, ["-I", file], { encoding: "utf8" }); } catch (e) { if (e.code === "ENOENT") return; throw e; }
    assert.ok(!out.includes("DIFFERENT"), out);
    assert.equal((out.match(/same/g) || []).length, 14, out);
    const csv = csvOf(x, r);
    assert.equal(csv.split("\n").filter((l) => /^[AB],/.test(l)).length, a.build + a.life + b.build + b.life);
    const doFile = stataOf(P, x, rows, r);
    assert.ok(doFile.includes('display "Scenario A"') && doFile.includes('display "Scenario B"'));
    assert.ok(!doFile.includes("undefined") && !doFile.includes("NaN"), "no undefined or NaN written into the do-file");
  }
});

test("property tax: North Dakota's generation taxes, wind and the other sources", () => {
  const w = F.propertyTax(P, { ...F.defaults(P, "land_based_wind", "nd"), mw: 100, cf: 0.45 }, 0).tax;
  near(w, 100 * 2500 + 100 * 8760 * 0.45 * 0.5);
  const pv = F.propertyTax(P, { ...F.defaults(P, "utility_pv", "nd"), mw: 50, cf: 0.2 }, 0).tax;
  near(pv, 50 * 500 + 50 * 8760 * 0.2 * 1.0);
  const geo = F.propertyTax(P, { ...F.defaults(P, "geothermal", "nd"), mw: 20 }, 0).tax;
  near(geo, 20 * 500, 1e-12, "geothermal: the capacity tax only (no capacity factor held)");
});

test("planned projects: a plant's generators of one technology added, its earliest year, its state and county", () => {
  const rows = [
    { entity_id: "eia860:100:G1", name: "Prairie Sun", capacity_mw: "80", tech: "solar", state: "MN", county: "Lyon", date: "2028-06-01" },
    { entity_id: "eia860:100:G2", name: "Prairie Sun", capacity_mw: 40, tech: "solar", state: "MN", county: "Lyon", date: "2027-12-01" },
    { entity_id: "eia860:100:B1", name: "Prairie Sun", capacity_mw: 50, tech: "storage", state: "MN", county: "Lyon", date: "2027-12-01" },
    { entity_id: "eia860:200:W", name: "Ridge", capacity_mw: 150, tech: "wind", state: "IA", county: "Story", date: null },
  ];
  const g = F.groupPlanned(rows);
  assert.equal(g.length, 2, "storage is not one of the four technologies");
  const pv = g.find((p) => p.tech === "utility_pv");
  assert.deepEqual(pv, { id: "100-utility_pv", name: "Prairie Sun", tech: "utility_pv", state: "mn", county: "Lyon", mw: 120, year: 2027 });
  assert.equal(g.find((p) => p.tech === "land_based_wind").year, null);
});

test("sales tax: a statute's exemption is the default (Minnesota wind), elsewhere none", () => {
  const mn = F.defaults(P, "land_based_wind", "mn");
  assert.equal(mn.exempt, 100);
  const r = F.run(mn, ROWS, P);
  assert.equal(r.sums.sales, 0); assert.equal(r.sales.note, "after the exemption");
  assert.equal(F.defaults(P, "utility_pv", "mn").exempt, 100, "solar: 297A.67 subd. 29, read by the re-check of session 4301");
  assert.equal(F.defaults(P, "land_based_wind", "tx").exempt, 0);
});

test("a figure's text: jobs to one decimal under 100 and whole above, dollars short with USD", () => {
  assert.equal(F.displayOf("c:jobs:total", 515.128), "515");
  assert.equal(F.displayOf("o:jobs:total", 44.7358), "44.7");
  assert.equal(F.displayOf("year:2030:jobs", 3.04), "3");
  assert.equal(F.displayOf("c:earnings:total", 41045772.3), "USD 41 million");
  assert.equal(F.displayOf("sum:sales", 19915038.03), "USD 19.9 million");
  assert.equal(F.displayOf("pv:taxes", 2.345e9), "USD 2.35 billion");
  assert.equal(F.displayOf("y1:property", 703600), "USD 703,600");
});

test("each operating year's MWh and taxable value (Iowa's valuation, the reader's own rate)", () => {
  const ia = { ...F.defaults(P, "land_based_wind", "ia"), mw: 100, capex: 1500, cf: 0.4, iaval: true, levy: 30 };
  const r = F.run(ia, ROWS, P);
  const op = r.years.filter((y) => y.phase === "operations");
  near(op[0].mwh, 100 * 8760 * 0.4); assert.equal(op[0].value, 0); near(op[3].value, 150e6 * 0.15);
  assert.equal(r.years[0].mwh, null, "a construction year produces nothing");
  near(F.stat(r, `year:${op[3].year}:value`), 150e6 * 0.15);
  assert.equal(F.displayOf(`year:${op[3].year}:mwh`, 350400.4), "350,400");
  const own = F.run({ ...F.defaults(P, "land_based_wind", "la"), mw: 100, capex: 1500, own: 1, ownyears: 10 }, ROWS, P);
  near(own.years.find((y) => y.phase === "operations").value, 150e6);
  assert.equal(F.run({ ...F.defaults(P, "land_based_wind", "ne"), mw: 100 }, ROWS, P).years.at(-1).value, null, "a capacity tax is not on a value");
  assert.equal(F.run(F.defaults(P, "geothermal", "ca"), ROWS, P).years.at(-1).mwh, null, "no capacity factor held");
});

test("property tax: Kansas's ten-year exemption, then no rule held (the life has no total) or the reader's own rate", () => {
  const ks = { ...F.defaults(P, "land_based_wind", "ks"), mw: 100, capex: 1500 };
  const r = F.run(ks, ROWS, P);
  assert.ok(r.ok, r.why);
  const op = r.years.filter((y) => y.phase === "operations");
  assert.deepEqual(op.slice(0, 10).map((y) => y.property), Array(10).fill(0));
  assert.equal(op[10].property, null);
  assert.equal(r.sums.property, null, "the life has no total");
  assert.equal(r.property.held, false);
  assert.match(r.property.note, /exempt for its first 10 years/);
  const own = F.run({ ...ks, own: 1, ownyears: 20 }, ROWS, P);
  assert.ok(own.property.held); near(own.sums.property, op.slice(10).reduce((a, _, j) => a + 150e6 * Math.max(0, 1 - (10 + j) / 20) * 0.01, 0));
});
test("property tax: Kansas's exemption by operating year", () => {
  const ks = { ...F.defaults(P, "land_based_wind", "ks"), mw: 100, capex: 1500 };
  assert.equal(F.propertyTax(P, ks, 0).tax, 0); assert.equal(F.propertyTax(P, ks, 9).tax, 0);
  assert.equal(F.propertyTax(P, ks, 10).tax, null, "no rule held after ten years");
  near(F.propertyTax(P, { ...ks, own: 1, ownyears: 20 }, 10).tax, 150e6 * 0.5 * 0.01, 1e-12, "the reader's own rate fills the later years");
  assert.equal(F.propertyTax(P, { ...F.defaults(P, "natural_gas", "ks") }, 0).tax, null, "gas is not a renewable resource of the paragraph");
});

test("property tax: Oregon's solar fee in lieu by county agreement, within its range, for its years", () => {
  const or = { ...F.defaults(P, "utility_pv", "or"), mw: 50 };
  assert.equal(or.optrate, 7000); assert.equal(or.iaval, false);
  assert.equal(F.propertyTax(P, or, 0).tax, null, "off by default");
  const on = { ...or, iaval: true };
  near(F.propertyTax(P, on, 0).tax, 50 * 7000); near(F.propertyTax(P, on, 19).tax, 50 * 7000);
  assert.equal(F.propertyTax(P, on, 20).tax, null, "no rule held after the agreement's 20 years");
  near(F.propertyTax(P, { ...on, optrate: 4000 }, 0).tax, 50 * 5500, 1e-12, "held to the statute's minimum");
  assert.equal(F.defaults(P, "land_based_wind", "or").optrate, null, "the fee is a solar project's");
});

test("sales tax: North Dakota exempts a solar or gas power plant's purchases, not a new wind plant's", () => {
  assert.equal(F.defaults(P, "utility_pv", "nd").exempt, 100);
  assert.equal(F.defaults(P, "natural_gas", "nd").exempt, 100);
  assert.equal(F.defaults(P, "land_based_wind", "nd").exempt, 0);
});

test("Wyoming's wind excise: USD 1 a MWh from the fourth operating year, the reader's own property tax added", () => {
  const wy = { ...F.defaults(P, "land_based_wind", "wy"), mw: 100, cf: 0.4, capex: 1500 };
  assert.equal(F.propertyTax(P, wy, 0).tax, 0); assert.equal(F.propertyTax(P, wy, 2).tax, 0);
  near(F.propertyTax(P, wy, 3).tax, 100 * 8760 * 0.4 * 1);
  const own = { ...wy, own: 1, ownyears: 25 };
  near(F.propertyTax(P, own, 0).tax, 150e6 * 0.01, 1e-12, "the property tax during the excise's exempt years");
  near(F.propertyTax(P, own, 5).tax, 100 * 8760 * 0.4 + 150e6 * (1 - 5 / 25) * 0.01);
  assert.equal(F.propertyTax(P, F.defaults(P, "utility_pv", "wy"), 0).tax, null, "the excise is wind's");
});

test("a production tax applied is reported whatever its rule's id (fault 20)", () => {
  assert.equal(F.run({ ...F.defaults(P, "land_based_wind", "wy"), mw: 100 }, ROWS, P).property.production, true);
  assert.equal(F.run({ ...F.defaults(P, "land_based_wind", "mn"), mw: 100 }, ROWS, P).property.production, true);
  assert.equal(F.run({ ...F.defaults(P, "land_based_wind", "ne"), mw: 100 }, ROWS, P).property.production, false);
  assert.equal(F.run(F.defaults(P, "land_based_wind", "tx"), ROWS, P).property.production, false);
});

test("Florida's device exemption: the reader's own rate on 20 percent of the base through 2037, all of it after", () => {
  const fl = { ...F.defaults(P, "utility_pv", "fl"), mw: 100, capex: 1500, start: 2027, build: 1, own: 1.5, ownyears: 30 };
  // the first operating year is 2028
  near(F.propertyTax(P, fl, 0).tax, 150e6 * 1 * 0.2 * 0.015);
  near(F.propertyTax(P, fl, 9).tax, 150e6 * (1 - 9 / 30) * 0.2 * 0.015, 1e-12, "2037, the last exempt year");
  near(F.propertyTax(P, fl, 10).tax, 150e6 * (1 - 10 / 30) * 0.015, 1e-12, "2038, the section expired");
  assert.equal(F.propertyTax(P, { ...fl, own: null }, 0).tax, null, "no rate given, no figure");
  near(F.propertyTax(P, { ...F.defaults(P, "natural_gas", "fl"), mw: 100, capex: 1500, own: 1.5, ownyears: 30 }, 0).tax, 150e6 * 0.015, 1e-12, "gas is not a renewable device");
});

test("Arizona's valuation at 20 percent of depreciated cost through 2040, on the reader's own rate", () => {
  const az = { ...F.defaults(P, "utility_pv", "az"), mw: 100, capex: 1500, start: 2027, build: 1, own: 1, ownyears: 35 };
  near(F.propertyTax(P, az, 0).tax, 150e6 * 0.2 * 0.01);
  near(F.propertyTax(P, az, 12).tax, 150e6 * (1 - 12 / 35) * 0.2 * 0.01, 1e-12, "2040, the last year");
  near(F.propertyTax(P, az, 13).tax, 150e6 * (1 - 13 / 35) * 0.01, 1e-12, "2041");
});

test("North Carolina's 80 percent solar exclusion, no end year, on the reader's own rate; wind is not a solar system", () => {
  const nc = { ...F.defaults(P, "utility_pv", "nc"), mw: 100, capex: 1500, start: 2027, build: 1, own: 0.7, ownyears: 30 };
  near(F.propertyTax(P, nc, 0).tax, 150e6 * 0.2 * 0.007);
  near(F.propertyTax(P, nc, 20).tax, 150e6 * (1 - 20 / 30) * 0.2 * 0.007, 1e-12, "2048: no end year");
  near(F.propertyTax(P, { ...F.defaults(P, "land_based_wind", "nc"), mw: 100, capex: 1500, own: 0.7, ownyears: 30 }, 0).tax, 150e6 * 0.007, 1e-12, "wind taxed in full");
});

test("Michigan's solar specific tax: off by default; USD 7,000 per MW AC for 20 years by local option; 2 MW at least", () => {
  const mi = { ...F.defaults(P, "utility_pv", "mi"), mw: 100 };
  assert.equal(mi.optrate, 7000);
  assert.equal(F.propertyTax(P, mi, 0).tax, null, "the option is off");
  near(F.propertyTax(P, { ...mi, iaval: true }, 0).tax, 700000);
  near(F.propertyTax(P, { ...mi, iaval: true, optrate: 2000 }, 19).tax, 200000, 1e-12, "the reduced rate, the 20th year");
  assert.equal(F.propertyTax(P, { ...mi, iaval: true }, 20).tax, null, "after 20 years no rule is held");
  near(F.propertyTax(P, { ...mi, iaval: true, optrate: 9000 }, 0).tax, 700000, 1e-12, "held to the statute's rate");
  assert.equal(F.propertyTax(P, { ...mi, iaval: true, mw: 1.5 }, 0).tax, null, "below 2 MW AC no facility qualifies");
});

test("Vermont's uniform capacity tax, USD 4 per kW, with the reader's own property tax added", () => {
  const vt = { ...F.defaults(P, "utility_pv", "vt"), mw: 20, capex: 1500 };
  near(F.propertyTax(P, vt, 0).tax, 80000);
  near(F.propertyTax(P, { ...vt, own: 1, ownyears: 25 }, 5).tax, 80000 + 30e6 * (1 - 5 / 25) * 0.01);
  assert.equal(F.propertyTax(P, { ...vt, mw: 0.04 }, 0).tax, null, "under 50 kW: exempt from the capacity tax, no rule held");
  const w = { ...F.defaults(P, "land_based_wind", "vt"), mw: 20, cf: 0.3 };
  near(F.propertyTax(P, w, 0).tax, 20 * 8760 * 0.3 * 3, 1e-12, "wind: the education tax of 5402c (session 4301)");
});

test("Wisconsin's payments to the municipality and county, USD 5,000 per MW a year, 1 MW at least, no gas rule", () => {
  near(F.propertyTax(P, { ...F.defaults(P, "land_based_wind", "wi"), mw: 100 }, 0).tax, 500000);
  near(F.propertyTax(P, { ...F.defaults(P, "utility_pv", "wi"), mw: 50 }, 30).tax, 250000, 1e-12, "every operating year");
  assert.equal(F.propertyTax(P, { ...F.defaults(P, "utility_pv", "wi"), mw: 0.5 }, 0).tax, null, "under 1 MW: no rule held");
  assert.equal(F.propertyTax(P, { ...F.defaults(P, "natural_gas", "wi"), mw: 500 }, 0).tax, null, "gas: no rule held");
});

test("Nevada's abatement: off by default; where approved 55 percent off the reader's own rate for 20 years from the first construction year", () => {
  const nv = { ...F.defaults(P, "utility_pv", "nv"), mw: 100, capex: 1500, start: 2027, build: 1, own: 1, ownyears: 30 };
  near(F.propertyTax(P, nv, 0).tax, 150e6 * 0.01, 1e-12, "off: the whole rate");
  const on = { ...nv, iaval: true };
  near(F.propertyTax(P, on, 0).tax, 150e6 * 0.45 * 0.01);
  near(F.propertyTax(P, on, 18).tax, 150e6 * (1 - 18 / 30) * 0.45 * 0.01, 1e-12, "the 20th year from 2027");
  near(F.propertyTax(P, on, 19).tax, 150e6 * (1 - 19 / 30) * 0.01, 1e-12, "after the 20 years");
  assert.equal(F.propertyTax(P, { ...on, own: null }, 0).tax, null, "no rate, no figure");
});

test("Maryland: counties tax 50 percent of generating equipment's value, every technology, on the reader's own rate", () => {
  for (const t of ["land_based_wind", "utility_pv", "natural_gas", "geothermal"]) {
    const md = { ...F.defaults(P, t, "md"), mw: 100, capex: 1500, own: 1.2, ownyears: 25 };
    near(F.propertyTax(P, md, 0).tax, 150e6 * 0.5 * 0.012, 1e-12, t);
    near(F.propertyTax(P, md, 10).tax, 150e6 * (1 - 10 / 25) * 0.5 * 0.012, 1e-12, t + ", year 11");
  }
  assert.equal(F.propertyTax(P, { ...F.defaults(P, "utility_pv", "md"), own: null }, 0).tax, null, "no rate, no figure");
});

test("Virginia's solar exemption: 80, 70 and 60 percent by years in service, more than 5 and less than 150 MW AC", () => {
  const va = { ...F.defaults(P, "utility_pv", "va"), mw: 100, capex: 1500, own: 0.8, ownyears: 30 };
  near(F.propertyTax(P, va, 0).tax, 150e6 * 0.2 * 0.008);
  near(F.propertyTax(P, va, 4).tax, 150e6 * (1 - 4 / 30) * 0.2 * 0.008, 1e-12, "the fifth year");
  near(F.propertyTax(P, va, 5).tax, 150e6 * (1 - 5 / 30) * 0.3 * 0.008, 1e-12, "the sixth year");
  near(F.propertyTax(P, va, 10).tax, 150e6 * (1 - 10 / 30) * 0.4 * 0.008, 1e-12, "the eleventh year");
  near(F.propertyTax(P, va, 25).tax, 150e6 * (1 - 25 / 30) * 0.4 * 0.008, 1e-12, "and after");
  near(F.propertyTax(P, { ...va, mw: 200, capex: 750 }, 0).tax, 150e6 * 0.008, 1e-12, "150 MW or more: no exemption");
  near(F.propertyTax(P, { ...va, mw: 5, capex: 30000 }, 0).tax, 150e6 * 0.008, 1e-12, "5 MW: not this clause");
});

test("a state's own assessment (valuation without the option): applies without the switch, its published levy the default", () => {
  // a rule built here for the test only: 10 percent assessed, falling 10 points a year to a floor of 3, levy USD 60 per 1,000
  const rule = { id: "test_assessed", technologies: ["utility_pv"], kind: "valuation", schedule_pct: [10, 9, 8, 7, 6, 5, 4], then_pct: 3, default_levy: 60, levy_words: "test" };
  const P2 = { ...P, property: { ...P.property, states: { ...P.property.states, zz: { name: "Test", rules: [rule] } } } };
  const x = { ...F.defaults(P2, "utility_pv", "tx"), state: "zz", mw: 100, capex: 1500, levy: F.defaults(P2, "utility_pv", "zz").levy };
  assert.equal(x.levy, 60);
  near(F.propertyTax(P2, x, 0).tax, 150e6 * 0.10 * 0.060);
  near(F.propertyTax(P2, x, 9).tax, 150e6 * 0.03 * 0.060, 1e-12, "the floor");
  assert.equal(F.propertyTax(P2, { ...x, levy: null }, 0).tax, null, "no levy, no figure");
  assert.equal(F.defaults(P, "land_based_wind", "ia").levy, null, "Iowa: no statewide levy held");
  assert.equal(F.propertyTax(P, { ...F.defaults(P, "land_based_wind", "ia"), levy: 30 }, 3).tax, null, "Iowa still needs its ordinance");
});

test("fault 22: every property rule carries its hover words with a citation, and the own rate's words where it acts on one", () => {
  for (const [s, v] of Object.entries(P.property.states)) for (const r of v.rules) {
    assert.ok(r.tip && /\(.*\d.*\)/.test(r.tip), `${s} ${r.id}: a tip with its citation in brackets`);
    if (r.kind === "own_exempt" || r.adds_to_property) assert.ok(r.own_tip, `${s} ${r.id}: the own rate's words`);
  }
});

test("a valuation by a statutory value per MW, an assessment ratio and a straight line with a floor", () => {
  // built for the test: USD 500,000 per MW, a third assessed, 4 points a year to a floor of 30, levy USD 80 per 1,000
  const rule = { id: "test_mw_value", technologies: ["land_based_wind"], kind: "valuation", usd_per_mw_value: 500000, assessment_ratio: 1 / 3, depr_pct_per_year: 4, floor_pct: 30, tip: "test (x 1)" };
  const P2 = { ...P, property: { ...P.property, states: { ...P.property.states, zz: { name: "Test", rules: [rule] } } } };
  const x = { ...F.defaults(P, "land_based_wind", "tx"), state: "zz", mw: 100, levy: 80 };
  near(F.propertyTax(P2, x, 0).tax, 100 * 500000 / 3 * 0.080);
  near(F.propertyTax(P2, x, 10).tax, 100 * 500000 * 0.60 / 3 * 0.080, 1e-12, "year 11: 60 percent");
  near(F.propertyTax(P2, x, 24).tax, 100 * 500000 * 0.30 / 3 * 0.080, 1e-12, "the floor");
});

test("a note rule holds no figure and leaves the reader's own rate; an exemption in operating years for a plant built before a year", () => {
  const note = { id: "test_note", technologies: ["utility_pv"], kind: "note", tip: "Test: ordinary local tax (Code 1)." };
  const ex = { id: "test_op", technologies: ["land_based_wind"], kind: "own_exempt", exempt_share: 1, op_years: 15, built_before: 2029, tip: "Test (Law 2)", own_tip: "t" };
  const P2 = { ...P, property: { ...P.property, states: { ...P.property.states, zz: { name: "Test", rules: [note, ex] } } } };
  const pv = { ...F.defaults(P, "utility_pv", "tx"), state: "zz", mw: 100, capex: 1500, own: 1, ownyears: 30 };
  assert.equal(F.propertyTax(P2, { ...pv, own: null }, 0).tax, null);
  near(F.propertyTax(P2, pv, 0).tax, 150e6 * 0.01, 1e-12, "the reader's own rate");
  const w = { ...F.defaults(P, "land_based_wind", "tx"), state: "zz", mw: 100, capex: 1500, start: 2027, build: 1, own: 1, ownyears: 30 };
  assert.equal(F.propertyTax(P2, w, 14).tax, 0, "the 15th operating year: exempt");
  near(F.propertyTax(P2, w, 15).tax, 150e6 * (1 - 15 / 30) * 0.01, 1e-12, "then the own rate");
  near(F.propertyTax(P2, { ...w, start: 2029 }, 0).tax, 150e6 * 0.01, 1e-12, "built after 2029: no exemption");
});

test("session 4296: each state's rule reproduces a hand-worked example from its statute's figures", () => {
  const base = (t, s, o = {}) => ({ ...F.defaults(P, t, s), mw: 100, capex: 1500, start: 2027, build: 1, cf: 0.3, ...o });
  const T = (t, s, o, i = 0) => F.propertyTax(P, base(t, s, o), i).tax;
  const MWH = 100 * 8760 * 0.3;
  // Illinois: USD 360,000 x 1.61 per MW (wind), 218,000 x 1.31 (solar); age over 25 to a floor of 30; a third; levy 80
  near(T("land_based_wind", "il", { levy: 80 }), 100 * 579600 * 0.96 * 0.3333 * 0.08);
  near(T("land_based_wind", "il", { levy: 80 }, 20), 100 * 579600 * 0.30 * 0.3333 * 0.08, 1e-12, "the floor");
  near(T("utility_pv", "il", { levy: 80 }, 4), 100 * 285580 * 0.80 * 0.3333 * 0.08);
  assert.equal(T("natural_gas", "il", {}), null, "Illinois gas: a note");
  // Montana: 3 percent (wind, gas), 6 percent (solar) of value, plus USD 0.20 per MWh
  near(T("land_based_wind", "mt", { levy: 50 }), 150e6 * 0.97 * 0.03 * 0.05 + MWH * 0.2);
  near(T("land_based_wind", "mt", { levy: 50 }, 25), 150e6 * 0.15 * 0.03 * 0.05 + MWH * 0.2, 1e-12, "Montana: the floor");
  near(T("utility_pv", "mt", { levy: 50 }), 150e6 * 0.97 * 0.06 * 0.05 + MWH * 0.2);
  // West Virginia: B&O USD 22.78 per kW of taxable capacity (wind 12, solar 8, gas 40 percent), property at 60 percent, levy 19.2
  near(T("land_based_wind", "wv", {}), 100 * 22.78 * 1000 * 0.12 + 150e6 * (0.79 * 0.05 + 0.21) * 0.6 * 0.0192);
  near(T("utility_pv", "wv", {}), 100 * 22.78 * 1000 * 0.08 + 150e6 * 0.6 * 0.0192);
  near(T("natural_gas", "wv", {}), 100 * 22.78 * 1000 * 0.40 + 150e6 * 0.6 * 0.0192);
  // Rhode Island: USD 5 per kW AC
  near(T("utility_pv", "ri", {}), 100 * 5 * 1000);
  // Kentucky solar: 15 cents per 100, state only
  near(T("utility_pv", "ky", {}), 150e6 * 0.15 / 100);
  // California 1 percent; Washington USD 8.96 per 1,000; Georgia 40 percent at 24.712 mills
  near(T("natural_gas", "ca", {}), 150e6 * 0.01);
  near(T("utility_pv", "wa", {}), 150e6 * 0.96 * 8.96 / 1000);
  near(T("land_based_wind", "wa", {}, 30), 150e6 * 0.15 * 8.96 / 1000, 1e-12, "Washington: the floor");
  near(T("natural_gas", "wa", {}), 150e6 * 0.925 * 8.96 / 1000, 1e-12, "Washington gas: column 7.5 (session 6001; at cost before)");
  near(T("land_based_wind", "ga", {}), 150e6 * 0.95 * 0.4 * 24.712 / 1000);
  near(T("land_based_wind", "ga", {}, 20), 150e6 * 0.15 * 0.4 * 24.712 / 1000, 1e-12, "Georgia: the residual");
  // Tennessee: 55 percent; solar valued at 12.5 percent of installed cost
  near(T("utility_pv", "tn", { levy: 50 }), 150e6 * 0.125 * 0.55 * 0.05);
  near(T("land_based_wind", "tn", { levy: 50 }), 150e6 * 0.333333 * 0.55 * 0.05, 1e-6, "Tennessee wind: one third (session 6003; at cost before)");
  // New Mexico a third; South Carolina 10.5 percent plus half a mill per kWh; Texas market value; Ohio 7 percent
  near(T("utility_pv", "nm", { levy: 30 }), 150e6 * 0.98 * 0.3333 * 0.03, 1e-12, "New Mexico solar: Table 20 (session 6003; at cost before)");
  near(T("natural_gas", "sc", { levy: 300 }), 150e6 * 0.105 * 0.3 + MWH * 0.5);
  near(T("land_based_wind", "tx", { levy: 15 }), 150e6 * 0.015);
  near(T("utility_pv", "oh", { levy: 70 }), 150e6 * 0.983 * 0.07 * 0.07);
  near(T("utility_pv", "oh", { levy: 70 }, 29), 150e6 * 0.15 * 0.07 * 0.07, 1e-12, "Ohio: the floor at 30");
  // New York: exempt 15 operating years if built before 2030, then the reader's rate
  assert.equal(T("utility_pv", "ny", { own: 2, ownyears: 30 }, 14), 0);
  near(T("utility_pv", "ny", { own: 2, ownyears: 30 }, 15), 150e6 * (1 - 15 / 30) * 0.02);
  // Pennsylvania wind: turbines not assessed; DC solar exempt from personal property tax
  assert.equal(T("land_based_wind", "pa", {}), 0);
  assert.equal(T("utility_pv", "dc", { own: 3, ownyears: 10 }), 0);
  // a note: no figure, the reader's own rate where typed
  for (const s of ["al", "ak", "ar", "co", "ct", "de", "hi", "id", "in", "la", "ma", "me", "mo", "ms", "nh", "nj", "ok", "ut"]) {
    assert.equal(T("land_based_wind", s, {}), null, s);
    near(T("land_based_wind", s, { own: 1, ownyears: 25 }), 150e6 * 0.01, 1e-12, s);
  }
  // sales: Colorado's state share, Washington's refund, New York, New Jersey, Maryland, Kentucky, Rhode Island
  assert.equal(F.defaults(P, "utility_pv", "co").exempt, Math.round(10000 * 0.029 / (0.029 + 0.0499)) / 100, "the state rate over state and local: 36.76");
  assert.equal(F.defaults(P, "land_based_wind", "wa").exempt, 50);
  assert.equal(F.defaults(P, "natural_gas", "ny").exempt, 100);
  assert.equal(F.defaults(P, "utility_pv", "nj").exempt, 100);
  assert.equal(F.defaults(P, "utility_pv", "md").exempt, 100);
  assert.equal(F.defaults(P, "utility_pv", "ky").exempt, 67.2);
  assert.equal(F.defaults(P, "land_based_wind", "ri").exempt, 100);
  assert.equal(F.defaults(P, "utility_pv", "fl").exempt, 0);
  assert.equal(Object.keys(P.property.states).length, 51, "every state and DC");
});

test("session 4299: the states' own 2026 income tax where they changed it after the table (Georgia, Utah, South Carolina, West Virginia)", () => {
  assert.equal(P.income.states.ga.brackets[0].rate, 0.0499); assert.equal(P.income.states.ga.standard_deduction_single, 15000);
  assert.equal(P.income.states.ut.brackets[0].rate, 0.0445);
  assert.deepEqual(P.income.states.wv.brackets.map((b) => b.rate), [0.0211, 0.0281, 0.0316, 0.0422, 0.0458]);
  // South Carolina: 5.21 percent of income less USD 966 from USD 30,000, the same as the brackets
  const sc = (y) => P.income.states.sc.brackets.reduce((t, b, k, a) => t + Math.max(0, Math.min(y, a[k + 1]?.over_usd ?? Infinity) - b.over_usd) * b.rate, 0);
  near(sc(40000), 0.0521 * 40000 - 966, 1e-9);
});

test("fault 23: every property rule's words open with its state's name (the hover's letter leads them)", () => {
  for (const [s, v] of Object.entries(P.property.states)) for (const r of v.rules) {
    const name = v.name;
    assert.ok(r.tip.startsWith(name + ":") || r.tip.startsWith(name.split(" ")[0]) || (s === "dc" && r.tip.startsWith("District of Columbia")), `${s} ${r.id}: ${r.tip.slice(0, 30)}`);
  }
});

test("session 4301: Vermont's wind education tax, Iowa's generation tax, Nevada's 10 MW minimum, Minnesota's solar sales exemption", () => {
  const b = (t, s, o = {}) => ({ ...F.defaults(P, t, s), mw: 100, capex: 1500, cf: 0.3, start: 2027, build: 1, ...o });
  const MWH = 100 * 8760 * 0.3;
  near(F.propertyTax(P, b("land_based_wind", "vt"), 0).tax, MWH * 3);
  near(F.propertyTax(P, b("land_based_wind", "vt", { own: 1, ownyears: 25 }), 0).tax, MWH * 3 + 150e6 * 0.01, 1e-12, "the town's rate added");
  near(F.propertyTax(P, b("utility_pv", "ia"), 0).tax, MWH * 0.6);
  assert.equal(F.propertyTax(P, b("land_based_wind", "ia"), 0).tax, null, "Iowa wind: the special valuation, off by default");
  near(F.propertyTax(P, b("utility_pv", "nv", { iaval: true, own: 1, ownyears: 30 }), 0).tax, 150e6 * 0.45 * 0.01);
  near(F.propertyTax(P, b("utility_pv", "nv", { iaval: true, own: 1, ownyears: 30, mw: 8, capex: 18750 }), 0).tax, 150e6 * 0.01, 1e-12, "under 10 MW: no abatement");
  assert.equal(F.defaults(P, "utility_pv", "mn").exempt, 100);
  assert.equal(F.defaults(P, "utility_pv", "az").exempt, 0);
});

test("session 6000: Montana's 19-year life confirmed against the Department of Revenue's PDF by word position", () => {
  // page 27 of the 2026 schedules, the percent good column under economic life 19, read by word position (runs/s6000/mt_col.py)
  const pdf19 = [97, 93, 89, 85, 81, 77, 72, 68, 63, 57, 52, 47, 42, 37, 33, 29, 25, 23, 21, 20];
  for (const id of ["mt_class14", "mt_class13"]) {
    const r = P.property.states.mt.rules.find((x) => x.id === id);
    assert.deepEqual(r.schedule_pct, pdf19, id);
    assert.equal(r.then_pct, 15, `${id}: 15 percent after the 20th year`);
  }
  assert.match(P.property.sources.mt_pp_dep_2026.checked, /Renewable Energy Generation 87 \(11\) 19/);
  // a hand-worked year: a 100 MW gas plant at USD 1,500 per kW, class fourteen (3 percent), levy 600 mills, its 8th year (68 percent)
  const x = { ...F.defaults(P, "natural_gas", "mt"), mw: 100, capex: 1500, start: 2027, build: 1, levy: 600 };
  // plus Montana's electrical energy producers' license tax, USD 0.20 per MWh, at the gas default capacity factor (0.65)
  assert.equal(x.cf, 0.65);
  near(F.propertyTax(P, x, 7).tax, 150e6 * 0.68 * 0.03 * 0.6 + 100 * 8760 * 0.65 * 0.2, 1e-12, "1,836,000 + 113,880 = 1,949,880");
});

test("session 6001: Washington's gas plant by column 7.5, its geothermal plant at cost; California's wind fixtures by Table 4's 17-year column", () => {
  const b = (t, s, o = {}) => ({ ...F.defaults(P, t, s), mw: 100, capex: 1500, start: 2027, build: 1, cf: 0.3, ...o });
  const T = (t, s, i, o) => F.propertyTax(P, b(t, s, o), i).tax;
  // Washington, 'Steam & Gas fired (fixed equipment)', Trend I column 7.5 (21 years), levy USD 8.96 per 1,000:
  // age 1: 150,000,000 x 0.925 x 0.00896 = 1,243,200; age 5 (the trend lifts it): 0.859; age 33: 0.153; then the 15 percent minimum
  near(T("natural_gas", "wa", 0), 1243200, 1e-12, "age 1");
  near(T("natural_gas", "wa", 4), 150e6 * 0.859 * 0.00896, 1e-12, "age 5");
  near(T("natural_gas", "wa", 32), 150e6 * 0.153 * 0.00896, 1e-12, "age 33");
  near(T("natural_gas", "wa", 40), 150e6 * 0.15 * 0.00896, 1e-12, "the minimum");
  near(T("geothermal", "wa", 10), 150e6 * 0.00896, 1e-12, "geothermal: at cost, no column names it");
  // California wind, AH 581 Table 4 (2026), 17-year column, 1 percent: age 1 96 percent, age 10 53, age 27 1, held after
  near(T("land_based_wind", "ca", 0), 150e6 * 0.96 * 0.01, 1e-12, "150,000,000 x 0.96 x 0.01 = 1,440,000");
  near(T("land_based_wind", "ca", 9), 150e6 * 0.53 * 0.01);
  near(T("land_based_wind", "ca", 26), 150e6 * 0.01 * 0.01, 1e-12, "age 27");
  near(T("land_based_wind", "ca", 29), 150e6 * 0.01 * 0.01, 1e-12, "the last factor held");
  near(T("utility_pv", "ca", 9), 150e6 * 0.01, 1e-12, "solar: at cost, no life assigned");
  near(T("natural_gas", "ca", 9), 150e6 * 0.01, 1e-12, "gas: at cost");
  const wind = P.property.states.ca.rules.find((r) => r.id === "ca_wind_fixtures");
  assert.match(wind.tip, /2017\/020/); assert.match(wind.tip, /Table 4/);
  for (const id of ["wa_gas_property", "wa_geothermal_property", "ca_wind_fixtures", "ca_prop13"]) {
    const r = [...P.property.states.wa.rules, ...P.property.states.ca.rules].find((x) => x.id === id);
    for (const k of ["cite", "cite2", "cite3"]) if (r[k]) assert.ok(P.property.sources[r[k]], `${id} ${k}`);
  }
});

test("session 6002: Kentucky's wind turbines are manufacturing machinery (Form 61A200(P)); South Carolina and West Virginia stay at cost with the reason in the hover", () => {
  const b = (t, s, o = {}) => ({ ...F.defaults(P, t, s), mw: 100, capex: 1500, start: 2027, build: 1, cf: 0.3, ...o });
  const T = (t, s, i, o) => F.propertyTax(P, b(t, s, o), i).tax;
  // Kentucky wind: 15 cents per 100 of value, state only: 150,000,000 x 0.15 / 100 = 225,000 in every year (no table)
  near(T("land_based_wind", "ky", 0), 225000);
  near(T("land_based_wind", "ky", 20), 225000, 1e-12, "held at cost");
  assert.equal(T("natural_gas", "ky", 0), null, "gas: still a note");
  assert.match(P.property.states.ky.rules.find((r) => r.id === "ky_solar_machinery").tip, /Wind|wind turbines/);
  // South Carolina: 10.5 percent at cost, levy 300 mills, plus half a mill per kWh; the allowance class not assigned
  near(T("natural_gas", "sc", 5, { levy: 300 }), 150e6 * 0.105 * 0.3 + 100 * 8760 * 0.3 * 0.5, 1e-12, "4,725,000 + 131,400");
  assert.match(P.property.states.sc.rules.find((r) => r.id === "sc_property").tip, /12-37-930/);
  // West Virginia solar: B&O on 8 percent of capacity plus property at cost, 60 percent, levy 19.2
  near(T("utility_pv", "wv", 5), 100 * 22.78 * 1000 * 0.08 + 150e6 * 0.6 * 0.0192);
  assert.match(P.property.states.wv.rules.find((r) => r.id === "wv_property").tip, /110CSR1M/);
});

test("session 6003: New Mexico's Unregulated Electric tables, Tennessee wind's one third, Texas solar's 10-year life (Harris CAD's schedule)", () => {
  const b = (t, s, o = {}) => ({ ...F.defaults(P, t, s), mw: 100, capex: 1500, start: 2027, build: 1, cf: 0.3, ...o });
  const T = (t, s, i, o) => F.propertyTax(P, b(t, s, o), i).tax;
  // New Mexico, a third of value, levy 30 mills: Table 20 solar 98 percent at age 1, 22 at age 20, the 20 percent floor at 21
  near(T("utility_pv", "nm", 0, { levy: 30 }), 150e6 * 0.98 * 0.3333 * 0.03, 1e-12, "150,000,000 x 0.98 x 0.3333 x 0.03 = 1,469,853");
  near(T("utility_pv", "nm", 19, { levy: 30 }), 150e6 * 0.22 * 0.3333 * 0.03);
  near(T("utility_pv", "nm", 25, { levy: 30 }), 150e6 * 0.20 * 0.3333 * 0.03, 1e-12, "the floor");
  // wind Table 25: 100 - 80 x (age - 0.5) / 25; age 10: 69.6
  near(T("land_based_wind", "nm", 9, { levy: 30 }), 150e6 * 0.696 * 0.3333 * 0.03);
  // gas (combined cycle, class 49.13) and geothermal, Table 28: age 1 98.6, age 28 21.4, then 20
  near(T("natural_gas", "nm", 0, { levy: 30 }), 150e6 * 0.986 * 0.3333 * 0.03);
  near(T("geothermal", "nm", 27, { levy: 30 }), 150e6 * 0.214 * 0.3333 * 0.03);
  near(T("geothermal", "nm", 28, { levy: 30 }), 150e6 * 0.20 * 0.3333 * 0.03, 1e-12, "the floor");
  // Tennessee wind: a third of installed cost, 55 percent, levy 50 mills, every year; gas at cost
  near(T("land_based_wind", "tn", 0, { levy: 50 }), 150e6 * 0.333333 * 0.55 * 0.05, 1e-6, "= 1,374,999");
  near(T("land_based_wind", "tn", 15, { levy: 50 }), 150e6 * 0.333333 * 0.55 * 0.05, 1e-6);
  near(T("natural_gas", "tn", 15, { levy: 50 }), 150e6 * 0.55 * 0.05, 1e-12, "gas: at cost");
  // Texas solar, levy 15 mills: Harris CAD's 10-year Solar/Ind column, 92 percent at age 1, 21 at age 10, 20 from age 11
  near(T("utility_pv", "tx", 0, { levy: 15 }), 150e6 * 0.92 * 0.015, 1e-12, "150,000,000 x 0.92 x 0.015 = 2,070,000");
  near(T("utility_pv", "tx", 9, { levy: 15 }), 150e6 * 0.21 * 0.015);
  near(T("utility_pv", "tx", 30, { levy: 15 }), 150e6 * 0.20 * 0.015, 1e-12, "the 23.26 floor");
  near(T("land_based_wind", "tx", 10, { levy: 15 }), 150e6 * 0.015, 1e-12, "wind: at cost, no schedule published");
  for (const s of ["nm", "tn", "tx"]) for (const r of P.property.states[s].rules) for (const k of ["cite", "cite2", "cite3"]) if (r[k]) assert.ok(P.property.sources[r[k]], `${s} ${r.id} ${k}`);
});

test("session 6004: the six studies added to the cross-check, each with its region, reproduce the saved ratios", async () => {
  const X = await import("./forecast-crosscheck.mjs");
  const ids = ["nc_wind_nrel", "livingston_il", "corona_nm", "lsu_la_cc", "msu_mi_gas", "jedi_geo_co"];
  for (const id of ids) {
    const s = X.STUDIES.find((t) => t.id === id);
    assert.ok(s && s.region && s.url && s.published_words && Object.keys(s.published).length, id);
  }
  // Louisiana: USD 600 per kW of 2000, in 2025 dollars by the deflator's ratio
  const la = X.STUDIES.find((t) => t.id === "lsu_la_cc");
  near(la.cost_usd / (la.mw * 1000) * F.to2025(P, 2000), 600 * idx["2025"] / idx["2000"], 1e-12);
  const saved = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "docs", "reviews", "forecast-crosscheck-2026-11-14.json"), "utf8")).studies;
  const out = X.crosscheck(ROWS).filter((r) => ids.includes(r.id) && r.id !== "jedi_geo_co");  // the fixture holds no Colorado geothermal
  assert.equal(out.length, 5);
  for (const r of out) {
    const t = saved.find((x) => x.id === r.id);
    r.lines.forEach((l, k) => { if (l.ratio !== null) near(l.ratio, t.lines[k].ratio, 1e-9, `${r.id} ${l.figure}`); });
  }
});
