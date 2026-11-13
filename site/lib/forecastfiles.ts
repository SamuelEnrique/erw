// Session 4214 (chain 239): the forecast run's files. The CSV holds both scenarios year by year; the Python script and
// the Stata do-file carry each scenario's inputs and the parameters the model read for it (JEDI's 24 per-MW figures and
// its cost, the deflator, the tax rules of the state) and recompute every year with the arithmetic of lib/forecast.ts
// (docs/methods/forecast.md), then compare their totals with the tool's. Imports nothing but types.
import type { Inputs, Params, Result, Row } from "./forecast";

type View = "a" | "b";
const VIEWS: View[] = ["a", "b"];
const COLS = ["scenario", "year", "phase", "jobs_onsite", "jobs_supply_chain", "jobs_induced", "jobs_total", "earnings_total_usd2025",
  "output_total_usd2025", "property_tax_usd2025", "sales_tax_usd2025", "income_tax_usd2025", "severance_usd2025"];
const f = (v: number | null) => (v === null ? "" : String(Math.round(v * 1e6) / 1e6));
const HEAD = (what: string) => [
  `# Energy Research Warehouse (ERW): Local impact, ${what}`,
  "# Jobs, earnings and output: NLR's JEDI models (nlr_jedi_multipliers; NLR's data terms, https://www.nlr.gov/disclaimer: the user is granted the right, without any fee or cost, to use or copy the Data, provided that this entire notice appears in all copies of the Data; credit DOE/NLR/ALLIANCE; the Data are provided as is).",
  "# Capital cost, construction time, life, heat rate: EIA capital cost study for AEO2025 (Sargent & Lundy). Deflator: BEA's GDP implicit price deflator as EIA's STEO carries it (GDPDIUS).",
  "# Sales and income tax tables: Tax Foundation, 2026 (CC BY-NC 4.0). Property tax: the state's statute as quoted in the ERW's rules. Capacity factors: LBNL and EIA-860.",
  "# Every dollar is a 2025 dollar. Gross effects of an input-output model, not net of what would have happened otherwise.",
];

export function csvOf(x: Record<View, Inputs>, r: Record<View, Result>): string {
  const lines = [...HEAD("a run, year by year"), ...VIEWS.map((p) => `# scenario ${p.toUpperCase()}: ${JSON.stringify(x[p])}`), COLS.join(",")];
  for (const p of VIEWS) {
    if (!r[p].ok) { lines.push(`# scenario ${p.toUpperCase()} has no figure: ${r[p].why}`); continue; }
    for (const y of r[p].years) {
      lines.push([p.toUpperCase(), y.year, y.phase, f(y.jobs.onsite), f(y.jobs.supply_chain), f(y.jobs.induced), f(y.jobs.total), f(y.earnings.total),
        f(y.output.total), f(y.property), f(y.sales), f(y.income), f(y.severance)].join(","));
    }
  }
  return lines.join("\n") + "\n";
}

/** What a replication needs of one scenario, every number the model read for it */
export function bundle(P: Params, x: Inputs, rows: Row[], r: Result) {
  const per = (ph: string, e: string, m: string) => Number(rows.find((q) => q.entity.endsWith(`:${ph}:${e}`) && q.variable === m)?.value ?? NaN);
  const jc = P.jediCosts.technologies[x.tech];
  const st = P.income.states[x.state];
  const rules = (P.property.states[x.state]?.rules ?? []).filter((q) => q.technologies.includes(x.tech));
  // severance as tax per Mcf at the scenario's price: the first operating year's figure over its volume (lib/severance.ts's rules)
  const y1 = r.years.find((y) => y.phase === "operations");
  const mcf = x.mw * 8760 * x.cf * x.heat / 1000 / (P.gas.btu_per_cf / 1000) * (x.instate / 100);
  return {
    inputs: x,
    jedi: { dollar_year: jc?.dollar_year ?? null, cost_usd_per_mw: jc?.states[x.state]?.cost_usd_per_mw ?? null,
      construction: Object.fromEntries(["onsite", "supply_chain", "induced", "total"].map((e) => [e, Object.fromEntries(["jobs", "earnings", "output"].map((m) => [m, per("construction", e, m)]))])),
      operations: Object.fromEntries(["onsite", "supply_chain", "induced", "total"].map((e) => [e, Object.fromEntries(["jobs", "earnings", "output"].map((m) => [m, per("operations", e, m)]))])) },
    deflator: { y2025: P.deflator.index["2025"], jedi_year: jc ? P.deflator.index[String(jc.dollar_year)] : null },
    income: st ? { none: !!st.none, brackets: st.brackets, standard_deduction: st.standard_deduction_single ?? 0, exemption: st.personal_exemption_single ?? 0, credit: st.personal_credit_single ?? 0 } : null,
    property: rules,
    btu_per_cf: P.gas.btu_per_cf,
    severance_per_mcf: y1 && y1.severance !== null && mcf > 0 ? y1.severance / mcf : null,
    totals: r.ok ? { jobs: r.sums.jobs, earnings: r.sums.earnings, property: r.sums.property, sales: r.sums.sales, income: r.sums.income, severance: r.sums.severance, pv_taxes: r.pv.taxes } : null,
  };
}

export function pythonOf(P: Params, x: Record<View, Inputs>, rows: Record<View, Row[]>, r: Record<View, Result>): string {
  const data = Object.fromEntries(VIEWS.map((p) => [p.toUpperCase(), bundle(P, x[p], rows[p], r[p])]));
  return `${HEAD("replication in Python").join("\n")}
# Recomputes both scenarios with the arithmetic of the ERW's forecast model and compares each total with the tool's.
# Run: python erw_local_impact_run.py
import json, math

DATA = json.loads(${JSON.stringify(JSON.stringify(data))})
EFFECTS = ["onsite", "supply_chain", "induced", "total"]


def income_tax(t, w):
    if t is None or t["none"] or w <= 0:
        return 0.0
    taxable = max(0.0, w - t["standard_deduction"] - t["exemption"])
    b, tax = t["brackets"], 0.0
    for i, br in enumerate(b):
        lo = br["over_usd"]
        hi = b[i + 1]["over_usd"] if i + 1 < len(b) else math.inf
        if taxable > lo:
            tax += (min(taxable, hi) - lo) * br["rate"]
    return max(0.0, tax - t["credit"])


def property_tax(d, i):
    x, mw = d["inputs"], d["inputs"]["mw"]
    cf = x["cf"] if x["cf"] is not None else 0.0  # geothermal holds none: no production tax applies to it
    mwh, spend, total, used = mw * 8760 * cf, x["capex"] * mw * 1000, 0.0, False
    for r in d["property"]:
        if r.get("min_mw") is not None and mw < r["min_mw"]:
            continue
        if r["kind"] == "capacity":
            total += mw * r["usd_per_mw_year"]; used = True
        elif r["kind"] == "production":
            rate = r.get("usd_per_mwh")
            if rate is None:
                rate = 0.0
                for t in r["tiers"]:
                    lo = t.get("min_mw_exclusive", t.get("min_mw_ac_exclusive", 0))
                    if mw > lo and (t.get("max_mw") is None or mw <= t["max_mw"]):
                        rate = t["usd_per_mwh"]; break
            if rate > 0:
                total += mwh * rate; used = True
        elif r["kind"] == "valuation":
            if not x["iaval"]:
                continue
            if x["levy"] is None:
                return None
            pct = r["schedule_pct"][i] if i < len(r["schedule_pct"]) else r["then_pct"]
            total += spend * pct / 100 * x["levy"] / 1000; used = True
    if used:
        return total
    if x["own"] is not None and x["ownyears"]:
        return spend * max(0.0, 1 - i / x["ownyears"]) * x["own"] / 100
    return None


def run(d):
    x, j = d["inputs"], d["jedi"]
    to_now = d["deflator"]["y2025"] / d["deflator"]["jedi_year"]
    spend = x["capex"] * x["mw"] * 1000
    s_jedi, local = spend / to_now, x["local"] / 100
    basis = x["mw"] * x["ilr"] if x["tech"] == "utility_pv" else x["mw"]
    c = {m: {e: j["construction"][e][m] / j["cost_usd_per_mw"] * s_jedi * local * (1 if m == "jobs" else to_now) for e in EFFECTS} for m in ("jobs", "earnings", "output")}
    o = {m: {e: j["operations"][e][m] * basis * local * x["om"] / 100 * (1 if m == "jobs" else to_now) for e in EFFECTS} for m in ("jobs", "earnings", "output")}
    sales = spend * x["taxable"] / 100 * x["sales"] / 100 * (1 - x["exempt"] / 100) if x["taxable"] is not None else None
    years = []
    for i in range(x["build"]):
        jobs, earn = c["jobs"]["total"] / x["build"], c["earnings"]["total"] / x["build"]
        years.append(dict(year=x["start"] + i, jobs=jobs, earnings=earn, property=None, sales=None if sales is None else sales / x["build"],
                          income=jobs * income_tax(d["income"], earn / jobs) if jobs > 0 else 0.0, severance=None))
    sev = None
    if x["tech"] == "natural_gas" and d["severance_per_mcf"] is not None:
        mcf = x["mw"] * 8760 * x["cf"] * x["heat"] / 1000 / (d["btu_per_cf"] / 1000) * x["instate"] / 100
        sev = mcf * d["severance_per_mcf"]
    for i in range(x["life"]):
        jobs, earn = o["jobs"]["total"], o["earnings"]["total"]
        years.append(dict(year=x["start"] + x["build"] + i, jobs=jobs, earnings=earn, property=property_tax(d, i), sales=None,
                          income=jobs * income_tax(d["income"], earn / jobs) if jobs > 0 else 0.0, severance=sev))
    disc = lambda y: 1 / (1 + x["rate"] / 100) ** (y - x["start"])
    tot = lambda k: sum(y[k] for y in years if y[k] is not None) if any(y[k] is not None for y in years) else None
    pv = sum((y[k] or 0) * disc(y["year"]) for y in years for k in ("property", "sales", "income", "severance"))
    return dict(jobs=tot("jobs"), earnings=tot("earnings"), property=tot("property"), sales=tot("sales"), income=tot("income"), severance=tot("severance"), pv_taxes=pv)


for name, d in DATA.items():
    if d["totals"] is None:
        print(name, "has no figure in the tool")
        continue
    got = run(d)
    print("Scenario", name)
    for k, want in d["totals"].items():
        mine = got[k]
        same = (mine is None and want is None) or (mine is not None and want is not None and abs(mine - want) <= 1e-6 * max(1.0, abs(want)))
        print(f"  {k:<10} tool {want!s:>22}  this script {mine!s:>22}  {'same' if same else 'DIFFERENT'}")
`;
}

export function stataOf(P: Params, x: Record<View, Inputs>, rows: Record<View, Row[]>, r: Record<View, Result>): string {
  const out: string[] = [...HEAD("replication in Stata").map((l) => `* ${l.slice(2)}`),
    "* Recomputes both scenarios with the arithmetic of the ERW's forecast model and compares each total with the tool's.",
    "* Run: do erw_local_impact_run.do", "clear all", "set more off", "tempfile all", "local first = 1"];
  const q = (v: number | null) => (v === null ? "." : String(v));
  for (const p of VIEWS) {
    const d = bundle(P, x[p], rows[p], r[p]);
    const xi = d.inputs, j = d.jedi;
    if (!d.totals || j.cost_usd_per_mw === null || d.deflator.jedi_year === null) { out.push(`display "Scenario ${p.toUpperCase()} has no figure in the tool"`); continue; }
    const P_ = p.toUpperCase();
    out.push("", `* ---- scenario ${P_}: ${xi.tech}, ${xi.state}, ${xi.mw} MW`, "clear",
      `scalar to_now = ${d.deflator.y2025} / ${d.deflator.jedi_year}`,
      `scalar spend = ${xi.capex} * ${xi.mw} * 1000`, "scalar s_jedi = spend / to_now", `scalar local = ${xi.local} / 100`,
      `scalar basis = ${xi.tech === "utility_pv" ? `${xi.mw} * ${xi.ilr}` : xi.mw}`,
      `scalar c_jobs = ${j.construction.total.jobs} / ${j.cost_usd_per_mw} * s_jedi * local`,
      `scalar c_earn = ${j.construction.total.earnings} / ${j.cost_usd_per_mw} * s_jedi * local * to_now`,
      `scalar o_jobs = ${j.operations.total.jobs} * basis * local * ${xi.om} / 100`,
      `scalar o_earn = ${j.operations.total.earnings} * basis * local * ${xi.om} / 100 * to_now`,
      `scalar sales_all = ${xi.taxable === null ? "." : `spend * ${xi.taxable} / 100 * ${xi.sales} / 100 * (1 - ${xi.exempt} / 100)`}`,
      `set obs ${xi.build + xi.life}`, `gen int year = ${xi.start} + _n - 1`, `gen byte build = _n <= ${xi.build}`,
      `gen double jobs = cond(build, c_jobs / ${xi.build}, o_jobs)`, `gen double earnings = cond(build, c_earn / ${xi.build}, o_earn)`,
      "gen double w = earnings / jobs",
      `gen double taxable_w = max(0, w - ${d.income?.standard_deduction ?? 0} - ${d.income?.exemption ?? 0})`, "gen double tax_one = 0");
    if (d.income && !d.income.none) {
      d.income.brackets.forEach((b, i) => {
        const hi = d.income!.brackets[i + 1]?.over_usd;
        out.push(`replace tax_one = tax_one + (min(taxable_w, ${hi === undefined ? "taxable_w" : hi}) - ${b.over_usd}) * ${b.rate} if taxable_w > ${b.over_usd}`);
      });
      out.push(`replace tax_one = max(0, tax_one - ${d.income.credit})`);
    }
    out.push("gen double income = jobs * tax_one", "gen double sales = cond(build, sales_all / " + xi.build + ", .)",
      "gen int i = _n - 1 - " + xi.build, "gen double property = .");
    // property: the same rules as the model, written out for this state and technology
    const spend = `${xi.capex} * ${xi.mw} * 1000`, mwh = `${xi.mw} * 8760 * ${xi.cf}`;
    const parts: string[] = [];
    let valuation: string | null = null;
    for (const rl of d.property) {
      if (rl.min_mw !== undefined && xi.mw < rl.min_mw) continue;
      if (rl.kind === "capacity") parts.push(`${xi.mw} * ${rl.usd_per_mw_year}`);
      else if (rl.kind === "production") {
        let rate = rl.usd_per_mwh ?? 0;
        if (rl.usd_per_mwh === undefined) for (const t of rl.tiers ?? []) { const lo = t.min_mw_exclusive ?? t.min_mw_ac_exclusive ?? 0; if (xi.mw > lo && (t.max_mw === undefined || xi.mw <= t.max_mw)) { rate = t.usd_per_mwh; break; } }
        if (rate > 0 && Number.isFinite(xi.cf)) parts.push(`${mwh} * ${rate}`);  // geothermal holds no capacity factor
      } else if (rl.kind === "valuation" && xi.iaval && xi.levy !== null) {
        const s = rl.schedule_pct ?? [];
        valuation = `${spend} * cond(i < ${s.length}, ${s.map((v, k) => `(i == ${k}) * ${v}`).join(" + ")}, ${rl.then_pct}) / 100 * ${xi.levy} / 1000`;
      }
    }
    if (valuation) parts.push(valuation);
    if (parts.length) out.push(`replace property = ${parts.join(" + ")} if !build`);
    else if (xi.own !== null && xi.ownyears) out.push(`replace property = ${spend} * max(0, 1 - i / ${xi.ownyears}) * ${xi.own} / 100 if !build`);
    out.push(`gen double severance = ${d.severance_per_mcf === null ? "." : `cond(build, ., ${xi.mw} * 8760 * ${xi.cf} * ${xi.heat} / 1000 / (${d.btu_per_cf} / 1000) * ${xi.instate} / 100 * ${d.severance_per_mcf})`}`,
      `gen double disc = 1 / (1 + ${xi.rate} / 100) ^ (year - ${xi.start})`,
      "egen double t_jobs = total(jobs)", "egen double t_earn = total(earnings)", "egen double t_income = total(income)",
      "egen double t_prop = total(property), missing", "egen double t_sales = total(sales), missing", "egen double t_sev = total(severance), missing",
      "gen double pvt = (cond(missing(property), 0, property) + cond(missing(sales), 0, sales) + income + cond(missing(severance), 0, severance)) * disc",
      "egen double t_pv = total(pvt)",
      `display "Scenario ${P_}"`,
      `display "  jobs       tool ${q(d.totals.jobs)}   do-file " t_jobs[1]`,
      `display "  earnings   tool ${q(d.totals.earnings)}   do-file " t_earn[1]`,
      `display "  property   tool ${q(d.totals.property)}   do-file " t_prop[1]`,
      `display "  sales      tool ${q(d.totals.sales)}   do-file " t_sales[1]`,
      `display "  income     tool ${q(d.totals.income)}   do-file " t_income[1]`,
      `display "  severance  tool ${q(d.totals.severance)}   do-file " t_sev[1]`,
      `display "  pv taxes   tool ${q(d.totals.pv_taxes)}   do-file " t_pv[1]`,
      `gen str1 scenario = "${P_}"`,
      "if `first' == 0 append using `all'", "save `all', replace", "local first = 0");
  }
  out.push("", "use `all', clear", "list scenario year jobs earnings property sales income severance, sepby(scenario)", "");
  return out.join("\n");
}
