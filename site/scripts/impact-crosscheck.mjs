// Chain 304 (session 7506): /impact beside two published documents the cross-check of 14 November did not hold
// (docs/methods/forecast.md, section 9, "Session 7506"; docs/reviews/forecast-crosscheck-2026-11-14.json holds the
// twenty-two before them and is not repeated here). Each document's own project runs through the page's own functions
// (lib/forecastui.ts resolve, lib/forecast.ts run) at the tool's defaults otherwise; the model's dollars are converted
// back to the document's year. No figure is adjusted to match. The published figures were read on 16 November 2026 from
// the publishers' own files (robots files first; the requests are in the session's report).
//
//   cd site; node --import ./scripts/tsx-register.mjs scripts/impact-crosscheck.mjs <nlr_jedi_multipliers.csv> [--json <file>]
import fs from "node:fs";

const F = await import("../lib/forecast.ts");
const D = await import("../lib/forecastdata.ts");
const U = await import("../lib/forecastui.ts");
const S = await import("../lib/severance.ts");

const args = process.argv.slice(2);
const jsonAt = args.indexOf("--json");
const jediFile = args.find((a, i) => !a.startsWith("--") && i !== jsonAt + 1);

function readRows(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const at = (k) => head.indexOf(k);
  return lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
    .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
}

if (!jediFile || !fs.existsSync(jediFile)) {
  console.error("give the path of nlr_jedi_multipliers.csv");
  process.exitCode = 2;
} else {
  const P = D.params();
  const jedi = F.pack(readRows(jediFile));
  const rules = D.gasSeverance();
  const sev = (state, volume, price) => {
    const st = state.toUpperCase();
    if (!rules.states[st]?.products?.gas) return null;
    const r = S.compute(rules, { state: st, product: "gas", volume, price });
    return r.baseTotal + r.fees.reduce((a, f) => a + f.amount, 0);
  };
  const model = (query) => {
    const v = U.parse(query).a;
    const x = U.resolve(P, v);
    return { x, r: F.run(x, F.unpack(jedi, x.tech, x.state), P, sev) };
  };
  const rows = [];
  const add = (doc, figure, ours, theirs, quote, why) => rows.push({ document: doc, figure, ours, theirs, ours_over_theirs: typeof ours === "number" && typeof theirs === "number" && theirs !== 0 ? Math.round((ours / theirs) * 100) / 100 : null, quote, why });

  // ---- 1. NREL's own published JEDI results: Colorado wind and gas (JEDI II, 2006) -------------------------------------
  const J = "NREL/CP-500-40085";
  const back05 = 1 / F.to2025(P, 2005);                                // the model's 2025 dollars in the paper's 2005 dollars
  const wind = model({ tech: "land_based_wind", state: "co", mw: "680", cost: String(1400 * F.to2025(P, 2005)) });
  const cw = wind.r.construction, ow = wind.r.operations;
  const shares = "two releases of the model twelve years apart: the paper ran JEDI II with IMPLAN's 2001 state data and its own Colorado inputs (it prints no local share for wind's equipment); the tool holds the 2018 release of JEDI Wind (2016 state data) at JEDI's default Colorado shares, and scales JEDI's 2017 cost mix to the paper's cost, USD 2,213 per kW in 2025 dollars. The paper does not say enough to split the gap between the two";
  add(J, "Colorado wind, 680 MW at USD 1,400 per kW of 2005: construction jobs, total", cw.jobs.total, 1618, "Colorado wind [...] During construction period [...] Total Impacts (Direct, Indirect, Induced) 1,618 $58.55 $183.90 (PDF page 11)", shares);
  add(J, "the same: construction jobs, direct (the tool: on site)", cw.jobs.onsite, 866, "Direct Impacts 866 $32.85 $108.79; Construction Sector Only 830", "the two lines are not the same thing: the paper's direct line is nearly all its construction sector (830 of the 866); the tool's on-site line is JEDI Wind's project development and onsite labor. Direct and indirect together: the paper 1,222, the tool 1,880 (1.54)");
  add(J, "the same: construction jobs, indirect (the tool: supply chain)", cw.jobs.supply_chain, 356, "Indirect Impacts 356 $12.96 $35.01", "see the line above: the split between direct and indirect differs between the two releases (an inference from the two lines' names; the paper does not define its direct line further)");
  add(J, "the same: construction jobs, induced", cw.jobs.induced, 395, "Induced Impacts 395 $12.74 $40.10", shares);
  add(J, "the same: construction earnings, USD million of 2005", cw.earnings.total * back05 / 1e6, 58.55, "Total Impacts (Direct, Indirect, Induced) 1,618 $58.55 $183.90; the table prints no unit, the paper's charts are in millions of 2005 dollars (an inference: USD 36,200 a job-year)", shares);
  add(J, "the same: construction output, USD million of 2005", cw.output.total * back05 / 1e6, 183.9, "the same line", shares);
  add(J, "the same: operating jobs a year, total", ow.jobs.total, 259, "During operating years (annual) [...] Total Impacts (Direct, Indirect, Induced) 259 $12.69 $26.60", "the paper's 88 plant workers for 680 MW are 0.13 a MW; the 2018 release's default in Colorado is 0.045 on-site operating jobs a MW (nlr_jedi_multipliers)");
  add(J, "the same: operating jobs a year, plant workers (the tool: on site)", ow.jobs.onsite, 88, "Plant Workers Only 88 $6.73", "the same");
  add(J, "the same: operating earnings a year, USD million of 2005", ow.earnings.total * back05 / 1e6, 12.69, "Total Impacts (Direct, Indirect, Induced) 259 $12.69 $26.60", "follows the jobs");
  add(J, "the same: operating output a year, USD million of 2005", ow.output.total * back05 / 1e6, 26.6, "the same line", "follows the jobs");
  const gas = model({ tech: "natural_gas", state: "co", mw: "270" });
  add(J, "Colorado gas, 270 MW: operating jobs a year, plant workers (the tool: on site)", gas.r.operations.jobs.onsite, 14, "Colorado natural gas [...] Plant Workers Only 14 $1.61 $1.61", "the paper states no installed cost, so only the operating lines, which do not scale with cost, are set beside it");
  add(J, "the same: operating jobs a year, total", gas.r.operations.jobs.total, 369, "Total Impacts (Direct, Indirect, Induced) 369 $17.17 $68.81", "the paper buys 40 percent of the plant's gas from Colorado wells at USD 7 per MMBtu, which JEDI counts as local spending; the tool's default, JEDI's saved share, is 0 percent");

  // ---- 2. one state's own fiscal notes: Nevada, Lone Mountain Geothermal (ORNI 56 LLC), Esmeralda County, 2026 ---------
  const N = "Nevada, application 26-0814G";
  const invest = 178446043, mw = 36;
  const cost = invest / (mw * 1000);
  // the reader's own inputs a Nevada assessor's figures give: the county's rate of USD 3.1191 per 100 of assessed value, on
  // Nevada's assessed value of 35 percent of taxable value (the note's first-year tax over its taxable value), is 1.0917
  // percent of cost; the note depreciates improvements 1.5 percent a year, a straight line to 0 over 66.7 years, and the
  // tool's field takes at most 60
  const own = 3.1191 * 0.35;
  const nv = model({ tech: "geothermal", state: "nv", mw: String(mw), cost: String(cost), iaval: "1", own: String(own), ownyears: "60" });
  const first = nv.r.years.filter((y) => y.phase === "operations");
  const twenty = first.slice(0, 20).reduce((a, y) => a + y.property, 0);
  const before = model({ tech: "geothermal", state: "nv", mw: String(mw), cost: String(cost), own: String(own), ownyears: "60" });
  const beforeYears = before.r.years.filter((y) => y.phase === "operations");
  add(N, "construction jobs: the tool's on-site job-years; the order's full-time construction jobs", nv.r.construction.jobs.onsite, 211, "the Facility would create an estimated 211 full-time construction jobs over the course of construction which would pay an average hourly wage of $60.00 per hour (Director's order, 4 November 2026, page 2)", "the order counts workers employed, at least 155 in the second quarter of construction; the tool counts job-years of 2,080 hours. The order's Nevada payroll at its wage is 87 job-years (10,857,600 / 60 / 2,080)");
  add(N, "construction earnings on site, USD", nv.r.construction.earnings.onsite, 10857600, "Construction Payroll in Nevada residents $10,857,600.00 (order, page 4); dollar year not stated, taken as 2025", "the order counts the payroll of Nevada residents only (at least 50 percent of the construction employees); JEDI's on-site line also holds project development and benefits");
  add(N, "operating jobs on site, each year", nv.r.operations.jobs.onsite, 0, "the Facility would create approximately 0 full-time operational jobs (order, page 2); Operational Payroll in Nevada: $0.00 (page 4)", "the applicant states no operating employee at the plant; JEDI's 2016 geothermal model staffs every plant");
  add(N, "property tax due before abatement, first operating year, USD", beforeYears[0].property, 1948119, "Total Taxes Due, First Year After Completion: $ 1,948,119 (Department of Taxation, property tax fiscal note, worksheets of 24 August 2026, page 3)", "the same base and rate by construction: the rate typed is the note's own (USD 3.1191 per 100 on 35 percent of value); the note's taxable value is USD 178,450,621, the order's investment USD 178,446,043");
  add(N, "property tax paid after the 55 percent abatement, first operating year, USD", first[0].property, 876653, "Total Taxes Available to Local Governments after abatement: $ 876,653 (the same page)", "the tool's rule for NRS 701A.370 (55 percent abated) gives the Department's figure");
  add(N, "property tax due before abatement, 20 years, USD", beforeYears.slice(0, 20).reduce((a, y) => a + y.property, 0), 33410592, "Total Taxes Due during Period of Abatement (20 years): $ 33,410,592", "the Department depreciates improvements 1.5 percent a year and personal property by its manual's schedule (taxable value USD 127.6 million in 2048); the tool's value falls in a straight line over the 60 years typed");
  add(N, "property tax paid after abatement, the first 20 operating years, USD", twenty, 15034766, "Total Taxes Available to Local Governments after abatement: $ 15,034,766 (20 years)", "the tool counts the abatement's 20 years from the first construction year, so operating years 19 and 20 are taxed in full; the Department abates 20 fiscal years from 2028-29");
  add(N, "sales and use tax on the build, USD", nv.r.sales.held ? F.stat(nv.r, "sum:sales") : "not held (JEDI's geothermal model has no sales tax line)", 405537, "purchase a total of $4,736,195.00 [...] during the first fiscal year [...] $1,184,049.00 [...] during the second year; Sales Tax Rate 6.850% (Department of Taxation, sales and use tax fiscal impact, 19 August 2026): 5,920,244 at 6.85 percent, of which USD 251,610 abated", "the tool holds no taxable share for geothermal. The two Nevada notes disagree on the base: the Budget Division's note of the same month states purchases subject to the tax of USD 86,426,913, 48 percent of the investment");
  for (const r of rows) console.log(`${r.document} | ${r.figure} | ours ${typeof r.ours === "number" ? Math.round(r.ours * 100) / 100 : r.ours} | theirs ${r.theirs} | ${r.ours_over_theirs ?? "none"}`);
  const body = {
    written_by: "site/scripts/impact-crosscheck.mjs, session 7506 (chain 304), 16 November 2026; continues docs/reviews/forecast-crosscheck-2026-11-14.json",
    documents: {
      [J]: { publisher: "National Renewable Energy Laboratory (now the National Laboratory of the Rockies)", title: "JEDI II: Jobs and Economic Development Impacts from Coal, Natural Gas, and Wind Power (Tegen, Goldberg and Milligan), conference paper NREL/CP-500-40085", date: "June 2006", url: "https://docs.nlr.gov/docs/fy06osti/40085.pdf", read: "2026-11-16, PDF page 11 (Figure 4), pages 8 and 9 (inputs)", dollars: "2005", inputs: "wind 680 MW, capacity factor 35 percent, construction $1400/kW; gas 270 MW, capacity factor 87 percent, 40 percent of its gas from Colorado, $7/MMBtu, installed cost not stated" },
      [N]: { publisher: "State of Nevada: Governor's Office of Energy (the Director's findings and order), Department of Taxation (two fiscal notes), Governor's Finance Office, Budget Division (fiscal note)", title: "Renewable energy tax abatement application 26-0814G, ORNI 56 LLC, Lone Mountain Geothermal Power Project, Esmeralda County (NRS 701A.300 to 701A.390)", date: "fiscal notes 19 and 24 August 2026; order signed 4 November 2026", url: "https://www.energy.nv.gov/programs/renewable-energy-tax-abatement-reta-program/renewable-energy-tax-abatement-projects-2026/", read: "2026-11-16", inputs: `36 MW AC nameplate (30 MW net in the property tax note), capital investment USD 178,446,043 (USD ${Math.round(cost)} per kW; dollar year not stated, taken as 2025); the tool's defaults otherwise (2 construction years, 40 operating years); for the property tax the reader's own rate ${Math.round(own * 10000) / 10000} percent of cost, falling to 0 over 60 years, the local option on` },
    },
    inputs: { wind_co: wind.x, gas_co: gas.x, geothermal_nv: nv.x },
    rows,
  };
  if (jsonAt >= 0 && args[jsonAt + 1]) { fs.writeFileSync(args[jsonAt + 1], `${JSON.stringify(body, null, 1)}\n`); console.log(`wrote ${args[jsonAt + 1]}`); }
}
