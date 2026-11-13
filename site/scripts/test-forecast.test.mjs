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
  const x = { ...F.defaults(P, "land_based_wind", "tx"), mw: 100, capex: 1500, own: 1.5, ownyears: 20 };
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
  assert.equal(r.sales.note, "after the reader's exemption");
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
