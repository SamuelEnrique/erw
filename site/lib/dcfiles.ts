// Chain 740 (lab-desktop window 3), session 10803: a datacenter run's files on /impact. The CSV holds both scenarios year
// by year (a plant scenario's rows as lib/forecastfiles.ts writes them); the Python script and the Stata do-file carry
// each datacenter scenario's inputs and every parameter the model read for it (the state's rule, Virginia's multipliers,
// the income tax brackets) and recompute every year with lib/dcimpact.ts's arithmetic, then compare their totals with
// the tool's. Imports nothing but types.
import type { DcInputs, DcParams, DcResult } from "./dcimpact";

type View = "a" | "b";
const VIEWS: View[] = ["a", "b"];
const f = (v: number | null) => (v === null ? "" : String(Math.round(v * 1e6) / 1e6));
const COLS = ["scenario", "year", "phase", "jobs_onsite", "jobs_supply_chain", "jobs_induced", "jobs_total", "earnings_total_usd2025",
  "equipment_bought_usd2025", "property_tax_building_usd2025", "property_tax_equipment_usd2025", "property_tax_usd2025",
  "sales_tax_before_exemption_usd2025", "sales_tax_forgone_usd2025", "sales_tax_paid_usd2025", "income_tax_usd2025", "electricity_tax_usd2025"];
export const DC_HEAD = (what: string) => [
  `# Energy Research Warehouse (ERW): Local impact, a datacenter, ${what}`,
  "# Size, investment and jobs: the reader's, or the medians of announced projects' own documents (site/data/forecast/datacenter_announced.json); the spending split, refresh cycle and build time: JLARC, Data Centers in Virginia 2024; Virginia's supply chain and induced ratios: JLARC Appendix D (Weldon Cooper Center, IMPLAN).",
  "# Wages: U.S. Census Bureau, County Business Patterns 2023. Sales and income tax tables: Tax Foundation, 2026 (CC BY-NC 4.0). Exemptions, property and electricity rules: each state's statute or agency page, as quoted in the ERW's rules.",
  "# Every dollar is a 2025 dollar. Gross effects, not net of what would have happened otherwise.",
];
export type Scenario = { dc: true; x: DcInputs; r: DcResult } | { dc: false; csvRows: string[]; inputs: unknown };

export function dcCsv(sc: Record<View, Scenario>): string {
  const lines = [...DC_HEAD("a run, year by year"), ...VIEWS.map((p) => `# scenario ${p.toUpperCase()}: ${JSON.stringify(sc[p].dc ? (sc[p] as { x: DcInputs }).x : (sc[p] as { inputs: unknown }).inputs)}`)];
  for (const p of VIEWS) {
    const s = sc[p];
    if (!s.dc) { lines.push(`# scenario ${p.toUpperCase()} is a plant: its columns are those of the plant download`, ...s.csvRows); continue; }
    lines.push(COLS.join(","));
    if (!s.r.ok) { lines.push(`# scenario ${p.toUpperCase()} has no figure: ${s.r.why}`); continue; }
    for (const y of s.r.years) {
      lines.push([p.toUpperCase(), y.year, y.phase, f(y.jobs.onsite), f(y.jobs.supply_chain), f(y.jobs.induced), f(y.jobs.total), f(y.earnings.total),
        f(y.equipment + y.building), f(y.propb), f(y.prope), f(y.property), f(y.salesbefore), f(y.forgone), f(y.sales), f(y.income), f(y.elec)].join(","));
    }
  }
  return lines.join("\n") + "\n";
}

/** What a replication needs of one datacenter scenario */
export function dcBundle(P: DcParams, x: DcInputs, r: DcResult) {
  const rule = P.rules.states[x.state] ?? null;
  const m = P.rules.multipliers[x.state] ?? null;
  const st = P.income.states[x.state];
  return {
    inputs: x,
    rule: rule ? { sales_exemption: rule.sales_exemption ? { covers: rule.sales_exemption.covers, min_investment_usd: rule.sales_exemption.min_investment_usd, min_jobs: rule.sales_exemption.min_jobs,
      last_year: rule.sales_exemption.last_year ?? null, term_years: rule.sales_exemption.term_years ?? null, invest_before_year: rule.sales_exemption.invest_before_year ?? null,
      min_mw: rule.sales_exemption.min_mw ?? null, start_before_year: rule.sales_exemption.start_before_year ?? null, term_years_big: rule.sales_exemption.term_years_big ?? null,
      discretionary: !!rule.sales_exemption.discretionary, rate_part: rule.sales_exemption.rate_part ?? null,
      state_rate_pct: (P.sales.states[x.state]?.state_rate ?? 0) * 100 } : null,
      property: rule.property && (rule.property.min_investment_usd === undefined || x.invest * 1e6 >= rule.property.min_investment_usd)
        ? { building_ratio: rule.property.building_ratio, equipment_ratio: rule.property.equipment_ratio } : null,
      electricity: rule.electricity ? { blocks: rule.electricity.blocks, elective: rule.electricity.elective ?? null } : null } : null,
    multipliers: m ? { construction: { direct: m.construction.direct, indirect: m.construction.indirect, induced: m.construction.induced },
      operations: { direct: m.operations.direct, indirect: m.operations.indirect, induced: m.operations.induced } } : null,
    income: st ? { none: !!st.none, brackets: st.brackets, standard_deduction: st.standard_deduction_single ?? 0, exemption: st.personal_exemption_single ?? 0, credit: st.personal_credit_single ?? 0 } : null,
    totals: r.ok ? { jobs: r.sums.jobs, earnings: r.sums.earnings, property: r.sums.property, salesbefore: r.sums.salesbefore, forgone: r.sums.forgone, sales: r.sums.sales,
      income: r.sums.income, elec: r.sums.elec, pv_taxes: r.pv.taxes } : null,
  };
}

export function dcPython(P: DcParams, sc: Record<View, Scenario>): string {
  const data = Object.fromEntries(VIEWS.filter((p) => sc[p].dc).map((p) => { const s = sc[p] as { x: DcInputs; r: DcResult }; return [p.toUpperCase(), dcBundle(P, s.x, s.r)]; }));
  return `${DC_HEAD("replication in Python").join("\n")}
# Recomputes each datacenter scenario with the arithmetic of the ERW's model (site/lib/dcimpact.ts) and compares each
# total with the tool's. A plant scenario is replicated by the plant download. Run: python erw_local_impact_datacenter.py
import json

DATA = json.loads(${JSON.stringify(JSON.stringify(data))})


def income_tax(t, w):
    if t is None or t["none"] or w <= 0:
        return 0.0
    taxable = max(0.0, w - (t["standard_deduction"] or 0) - (t["exemption"] or 0))
    tax, b = 0.0, t["brackets"]
    for i, br in enumerate(b):
        lo = br["over_usd"]
        hi = b[i + 1]["over_usd"] if i + 1 < len(b) else float("inf")
        if taxable > lo:
            tax += (min(taxable, hi) - lo) * br["rate"]
    return max(0.0, tax - (t["credit"] or 0))


def run(d):
    x, rule, m = d["inputs"], d["rule"], d["multipliers"]
    usd = x["invest"] * 1e6
    bld, eq = usd * x["bld"] / 100, usd * x["eq"] / 100
    ex = rule["sales_exemption"] if rule else None
    prop = rule["property"] if rule else None
    elec_rule = rule["electricity"] if rule else None

    def chain(onsite, wage, phase):
        jobs = {"onsite": onsite, "supply_chain": 0.0, "induced": 0.0}
        earn = {"onsite": onsite * wage, "supply_chain": 0.0, "induced": 0.0}
        if m:
            p = m[phase]
            for k, part in (("supply_chain", "indirect"), ("induced", "induced")):
                jobs[k] = onsite * p[part]["jobs"] / p["direct"]["jobs"]
                earn[k] = earn["onsite"] * p[part]["earnings_musd"] / p["direct"]["earnings_musd"]
        return sum(jobs.values()), sum(earn.values())

    eligible, share = False, 1.0
    if ex and not ex["discretionary"]:
        spent = usd if ex["invest_before_year"] is None else usd * max(0, min(x["build"], ex["invest_before_year"] - x["start"])) / x["build"]
        eligible = (spent >= ex["min_investment_usd"] and x["perm"] >= ex["min_jobs"]
                    and (ex["min_mw"] is None or x["mw"] >= ex["min_mw"])
                    and (ex["start_before_year"] is None or x["start"] < ex["start_before_year"]))
        if ex["rate_part"] == "state":
            share = min(1.0, ex["state_rate_pct"] / (x["sales"] or 1))

    def in_term(year):
        if ex["last_year"] is not None and year > ex["last_year"]:
            return False
        term = ex["term_years"]
        if ex["term_years_big"] and usd >= ex["term_years_big"]["min_investment_usd"]:
            term = ex["term_years_big"]["years"]
        if term is not None and year >= x["start"] + term:
            return False
        return True

    def sales(equipment, building, year):
        b_tax = 0.0 if x["matshare"] is None else building * x["matshare"] / 100 * x["sales"] / 100
        e_tax = equipment * x["sales"] / 100
        applies = eligible and x["dcex"] and in_term(year)
        forgone = ((e_tax if "equipment" in ex["covers"] else 0) + (b_tax if "construction" in ex["covers"] else 0)) * share if applies else 0.0
        return e_tax + b_tax, forgone

    elec = None
    if elec_rule and x["mwh"] is not None:
        month, lo, tax = x["mwh"] * 1000 / 12, 0.0, 0.0
        for blk in elec_rule["blocks"]:
            hi = blk["upto_kwh"] if blk["upto_kwh"] is not None else float("inf")
            if month > lo:
                tax += (min(month, hi) - lo) * blk["usd_per_kwh"]
            lo = hi
        elec = tax * 12
        alt = elec_rule.get("elective")
        if alt and x["mwh"] * 1000 >= alt["min_annual_kwh"]:
            # a schedule a large buyer may elect instead, by the year's kWh: the lower tax is taken
            year_kwh, lo, elected = x["mwh"] * 1000, 0.0, 0.0
            for blk in alt["annual_blocks"]:
                hi = blk["upto_kwh"] if blk["upto_kwh"] is not None else float("inf")
                if year_kwh > lo:
                    elected += (min(year_kwh, hi) - lo) * blk["usd_per_kwh"]
                lo = hi
            elec = min(elec, elected)

    tot = {"jobs": 0.0, "earnings": 0.0, "property": 0.0, "salesbefore": 0.0, "forgone": 0.0, "sales": 0.0, "income": 0.0, "elec": None, "pv_taxes": 0.0}
    pv_prop = 0.0
    prop_all = True
    disc = lambda y: 1 / (1 + x["rate"] / 100) ** (y - x["start"])
    cj, ce = chain(x["cons"], x["conswage"], "construction")
    for i in range(x["build"]):
        y = x["start"] + i
        before, forgone = sales(eq / x["build"], bld / x["build"], y)
        inc = cj * income_tax(d["income"], ce / cj) if cj > 0 else 0.0
        tot["jobs"] += cj; tot["earnings"] += ce; tot["salesbefore"] += before; tot["forgone"] += forgone
        tot["sales"] += before - forgone; tot["income"] += inc
        tot["pv_taxes"] += (before - forgone + inc) * disc(y)
    oj, oe = chain(x["perm"], x["opwage"], "operations")
    for i in range(x["life"]):
        y = x["start"] + x["build"] + i
        equipment = eq if x["refresh"] > 0 and i > 0 and i % x["refresh"] == 0 else 0.0
        before, forgone = sales(equipment, 0.0, y)
        bval = bld * (max(0.0, 1 - i / x["bldyears"]) if x["bldyears"] else 1.0)
        ab = 1 - x["abate"] / 100 if x["abate"] > 0 and (x["abateyears"] is None or i < x["abateyears"]) else 1.0
        br = prop["building_ratio"] if prop else 1.0
        er = prop["equipment_ratio"] if prop else 1.0
        pb = None if x["brate"] is None else bval * br * x["brate"] / 100 * ab
        age = i % x["refresh"] if x["refresh"] > 0 else i
        eqval = eq * max(x["eqfloor"], x["eqv1"] - x["eqstep"] * age) / 100
        pe = None if x["erate"] is None else eqval * er * x["erate"] / 100 * ab
        p = pb + pe if pb is not None and pe is not None else None
        if p is None:
            prop_all = False
        inc = oj * income_tax(d["income"], oe / oj) if oj > 0 else 0.0
        tot["jobs"] += oj; tot["earnings"] += oe; tot["salesbefore"] += before; tot["forgone"] += forgone
        tot["sales"] += before - forgone; tot["income"] += inc
        tot["property"] += p or 0.0
        if elec is not None:
            tot["elec"] = (tot["elec"] or 0.0) + elec
        pv_prop += (p or 0.0) * disc(y)
        tot["pv_taxes"] += (before - forgone + inc + (elec or 0.0)) * disc(y)
    if not prop_all:
        tot["property"] = None
    else:
        tot["pv_taxes"] += pv_prop  # the tool counts property in the taxes only when every operating year has it
    return tot, prop_all


for name, d in DATA.items():
    got, prop_all = run(d)
    want = d["totals"]
    if want is None:
        print(name, "has no figure in the tool")
        continue
    for k in ("jobs", "earnings", "property", "salesbefore", "forgone", "sales", "income", "elec"):
        a, b = got[k], want[k]
        ok = (a is None and b is None) or (a is not None and b is not None and abs(a - b) <= 1e-6 * max(1.0, abs(b)))
        print(f"{name} {k}: script {a} tool {b} {'ok' if ok else 'DIFFERS'}")
    if True:
        print(f"{name} pv_taxes: script {got['pv_taxes']} tool {want['pv_taxes']} {'ok' if abs(got['pv_taxes'] - want['pv_taxes']) <= 1e-6 * max(1.0, abs(want['pv_taxes'])) else 'DIFFERS'}")
`;
}

export function dcStata(P: DcParams, sc: Record<View, Scenario>): string {
  const out: string[] = [...DC_HEAD("the tax arithmetic in Stata").map((l) => `* ${l.slice(2)}`),
    "* Recomputes each datacenter scenario's sales tax (before the exemption, forgone, paid), property tax, income tax and electricity tax,",
    "* and displays each total beside the tool's. A plant scenario is replicated by the plant download.", "clear all", "set more off"];
  for (const p of VIEWS) {
    const s = sc[p];
    if (!s.dc || !s.r.ok) continue;
    const b = dcBundle(P, s.x, s.r), x = s.x, ex = b.rule?.sales_exemption ?? null, pr = b.rule?.property ?? null;
    const usd = x.invest * 1e6, bld = usd * x.bld / 100, eq = usd * x.eq / 100;
    const spent = !ex ? 0 : ex.invest_before_year === null ? usd : usd * Math.max(0, Math.min(x.build, ex.invest_before_year - x.start)) / x.build;
    const eligible = !!ex && !ex.discretionary && spent >= ex.min_investment_usd && x.perm >= ex.min_jobs && (ex.min_mw === null || x.mw >= ex.min_mw) && (ex.start_before_year === null || x.start < ex.start_before_year) && x.dcex;
    const term = ex && ex.term_years_big && usd >= ex.term_years_big.min_investment_usd ? ex.term_years_big.years : ex?.term_years ?? null;
    const share = ex && ex.rate_part === "state" ? Math.min(1, ex.state_rate_pct / (x.sales || 1)) : 1;
    const chainJ = (ph: "construction" | "operations") => b.multipliers ? (b.multipliers[ph].direct.jobs + b.multipliers[ph].indirect.jobs + b.multipliers[ph].induced.jobs) / b.multipliers[ph].direct.jobs : 1;
    const chainE = (ph: "construction" | "operations") => b.multipliers ? (b.multipliers[ph].direct.earnings_musd + b.multipliers[ph].indirect.earnings_musd + b.multipliers[ph].induced.earnings_musd) / b.multipliers[ph].direct.earnings_musd : 1;
    const inc = b.income;
    out.push("", `* ---- scenario ${p.toUpperCase()}: datacenter, ${x.state}, ${x.mw} MW, USD ${x.invest} million ----`, "clear",
      `set obs ${x.build + x.life}`, "gen i = _n - 1", `gen year = ${x.start} + i`, `gen build = i < ${x.build}`, `gen op = i - ${x.build}`,
      `scalar rate = ${x.sales / 100}`, `scalar eq = ${eq}`, `scalar bld = ${bld}`,
      `gen equipment = cond(build, eq / ${x.build}, cond(${x.refresh} > 0 & op > 0 & mod(op, ${x.refresh}) == 0, eq, 0))`,
      `gen building = cond(build, bld / ${x.build}, 0)`,
      `gen salesbefore = equipment * rate${x.matshare === null ? "" : ` + building * ${x.matshare / 100} * rate`}`,
      `gen interm = ${!ex ? 0 : `(${ex.last_year === null ? 1 : `year <= ${ex.last_year}`}) & (${term === null ? 1 : `year < ${x.start + term}`})`}`,
      `gen forgone = ${eligible ? `${share} * interm * (${ex!.covers.includes("equipment") ? "equipment * rate" : "0"}${ex!.covers.includes("construction") && x.matshare !== null ? ` + building * ${x.matshare / 100} * rate` : ""})` : "0"}`,
      "gen sales = salesbefore - forgone",
      `gen jobs = cond(build, ${x.cons * chainJ("construction")}, ${x.perm * chainJ("operations")})`,
      `gen earnings = cond(build, ${x.cons * x.conswage * chainE("construction")}, ${x.perm * x.opwage * chainE("operations")})`,
      "gen wage = earnings / jobs",
      `gen taxable = max(0, wage - ${inc ? inc.standard_deduction + inc.exemption : 0})`, "gen tax1 = 0");
    if (inc && !inc.none) inc.brackets.forEach((br, i) => {
      const hi = i + 1 < inc.brackets.length ? inc.brackets[i + 1].over_usd : null;
      out.push(`replace tax1 = tax1 + (min(taxable, ${hi === null ? "taxable" : hi}) - ${br.over_usd}) * ${br.rate} if taxable > ${br.over_usd}`);
    });
    out.push(`replace tax1 = max(0, tax1 - ${inc ? inc.credit : 0})`, "gen income = jobs * tax1");
    if (x.brate !== null && x.erate !== null) {
      out.push(`gen ab = cond(${x.abate} > 0 & (${x.abateyears === null ? 1 : `op < ${x.abateyears}`}), 1 - ${x.abate / 100}, 1)`,
        `gen bval = bld * ${x.bldyears === null ? 1 : `max(0, 1 - op / ${x.bldyears})`}`,
        `gen age = cond(${x.refresh} > 0, mod(op, ${x.refresh}), op)`,
        `gen eqval = eq * max(${x.eqfloor}, ${x.eqv1} - ${x.eqstep} * age) / 100`,
        `gen property = cond(build, ., bval * ${pr?.building_ratio ?? 1} * ${x.brate / 100} * ab + eqval * ${pr?.equipment_ratio ?? 1} * ${x.erate / 100} * ab)`,
        "quietly summarize property", `display "property tax over the life: " %18.2f r(sum) "   tool: " %18.2f ${s.r.sums.property ?? 0}`);
    }
    for (const [v, t] of [["salesbefore", s.r.sums.salesbefore], ["forgone", s.r.sums.forgone], ["sales", s.r.sums.sales], ["income", s.r.sums.income]] as const)
      out.push(`quietly summarize ${v}`, `display "${v}: " %18.2f r(sum) "   tool: " %18.2f ${t ?? 0}`);
    // session 10821: the tax on the electricity bought, by the state's monthly blocks on a twelfth of the year's kWh, and
    // where the state lets a large buyer elect another schedule by the year's kWh (Ohio), the lower of the two
    const el = b.rule?.electricity ?? null;
    if (el && x.mwh !== null) {
      const blocks = (v: string, bl: { upto_kwh: number | null; usd_per_kwh: number }[]) => {
        let lo = 0; const parts: string[] = [];
        for (const k of bl) { parts.push(k.upto_kwh === null ? `max(0, ${v} - ${lo}) * ${k.usd_per_kwh}` : `max(0, min(${v}, ${k.upto_kwh}) - ${lo}) * ${k.usd_per_kwh}`); lo = k.upto_kwh ?? lo; }
        return parts.join(" + ");
      };
      out.push(`scalar kwh_month = ${x.mwh} * 1000 / 12`, `scalar elec_year = 12 * (${blocks("kwh_month", el.blocks)})`);
      const alt = (el as { elective?: { min_annual_kwh: number; annual_blocks: { upto_kwh: number | null; usd_per_kwh: number }[] } | null }).elective;
      if (alt && x.mwh * 1000 >= alt.min_annual_kwh)
        out.push(`scalar kwh_year = ${x.mwh} * 1000`, `scalar elec_year = min(elec_year, ${blocks("kwh_year", alt.annual_blocks)})`);
      out.push(`display "electricity tax over the operating years: " %18.2f ${x.life} * elec_year "   tool: " %18.2f ${s.r.sums.elec ?? 0}`);
    }
  }
  return out.join("\n") + "\n";
}
