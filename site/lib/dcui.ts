// Chain 740 (lab-desktop window 3), session 10803: the datacenter's fields on /impact and its address. A datacenter is
// the fifth entry of the technology list (its place, DC_IX, is after the four JEDI plants); its fields have names of
// their own (dmw, invest, perm, ...), so no plant field or address moves. A field the reader has not set is NaN in the
// scenario's Values and follows its default for the state (lib/dcimpact.ts, dcDefaults): an investment not given
// follows the MW, permanent jobs the MW, construction workers the investment.
import { TECHS } from "./impact";
import { dcDefaults, dcWage, type DcInputs, type DcParams } from "./dcimpact";

export const DC_IX = TECHS.length;
export const isDcIx = (i: number) => i === DC_IX;
export type DcGroup = "project" | "spending" | "jobs" | "taxes" | "value";
export const DC_GROUPS: { key: DcGroup; title: string; open: boolean }[] = [
  { key: "project", title: "Project", open: true },
  { key: "spending", title: "Spending", open: false },
  { key: "jobs", title: "Jobs and wages", open: true },
  { key: "taxes", title: "Taxes", open: false },
  { key: "value", title: "Present value", open: true },
];
/** One datacenter field: its address name, the model's input it sets, its range and its default's words */
export type DcField = {
  name: string; input: keyof DcInputs; label: string; unit: string; min: number; max: number; whole: boolean; group: DcGroup;
  nullable?: boolean; options?: { value: number; label: string }[];
  source: (state: string, P: DcParams) => string;
};
const n = (v: number, d = 0) => v.toLocaleString("en-US", { maximumFractionDigits: d });
const range = (P: DcParams, k: keyof DcParams["announced"]["defaults"], d = 3) => {
  const s = P.announced.defaults[k];
  return `the median of ${s.n} announced projects (${n(s.low!, d)} to ${n(s.high!, d)}${P.announced.computed ? `; computed ${P.announced.computed}` : ""})`;
};

export const DC_FIELDS: DcField[] = [
  { name: "dmw", input: "mw", label: "Size", unit: "MW", min: 1, max: 20000, whole: false, group: "project",
    source: (_s, P) => `The MW the reader's project states. Default: ${range(P, "mw_stated", 0)}, each in its document's own measure (IT capacity, critical IT, critical grid capacity, or the power required): a size, not a load. Announced projects are listed above.` },
  { name: "invest", input: "invest", label: "Investment", unit: "USD million, 2025", min: 1, max: 500000, whole: false, group: "project",
    source: (_s, P) => `Land, building, equipment and other spending together. Default: the MW times ${range(P, "investment_per_mw")} USD million a MW, in 2025 dollars (each announcement's dollars by the GDP price index).` },
  { name: "dstart", input: "start", label: "First construction year", unit: "", min: 2026, max: 2060, whole: true, group: "project",
    source: () => "The first full calendar year from today: a choice. Every dollar is a 2025 dollar whatever the year." },
  { name: "dbuild", input: "build", label: "Construction", unit: "years", min: 1, max: 15, whole: true, group: "project",
    source: (_s, P) => P.rules.build.words },
  { name: "dlife", input: "life", label: "Operation", unit: "years", min: 1, max: 60, whole: true, group: "project",
    source: (_s, P) => P.rules.life.words },
  { name: "bld", input: "bld", label: "Building and site", unit: "% of investment", min: 0, max: 100, whole: false, group: "spending",
    source: (_s, P) => P.rules.split.words },
  { name: "eq", input: "eq", label: "Equipment", unit: "% of investment", min: 0, max: 100, whole: false, group: "spending",
    source: (_s, P) => `${P.rules.split.words} Servers, network, storage, power and cooling equipment: what a datacenter exemption covers.` },
  { name: "land", input: "land", label: "Land", unit: "% of investment", min: 0, max: 100, whole: false, group: "spending",
    source: (_s, P) => `${P.rules.split.words} Land bears no sales tax and is not in the property tax base here (land is not modeled for a plant either).` },
  { name: "refresh", input: "refresh", label: "Equipment bought again every", unit: "years", min: 0, max: 30, whole: true, group: "spending",
    source: (_s, P) => `${P.rules.refresh.words} 0: bought once.` },
  { name: "perm", input: "perm", label: "Permanent jobs on site", unit: "jobs", min: 0, max: 50000, whole: false, group: "jobs",
    source: (_s, P) => `Default: the MW times ${range(P, "permanent_jobs_per_mw")} jobs a MW. By the investment instead, ${range(P, "permanent_jobs_per_billion", 1)} jobs a USD billion: the reader's choice. JLARC (Virginia, 2024): about half of a datacenter's workers are contractors.` },
  { name: "cons", input: "cons", label: "Construction workers on site", unit: "each construction year", min: 0, max: 100000, whole: false, group: "jobs",
    source: (_s, P) => `Default: the investment times ${range(P, "construction_jobs_per_billion", 0)} construction jobs a USD billion, as announced: a headcount at peak where the document says so, held in every construction year, so an upper reading of the average year.` },
  { name: "opwage", input: "opwage", label: "Earnings per permanent job", unit: "USD a year, 2025", min: 0, max: 1000000, whole: true, group: "jobs",
    source: (s, P) => `Census County Business Patterns ${P.wages.year}, NAICS 518210 in this state: annual payroll over employment, in 2025 dollars. 518210 is wider than datacenters (JLARC: 15 percent of Virginia's 518210 jobs were datacenter jobs in 2016).${dcWage(P, s, "operations") === null ? " No figure for this state: type one." : ""}` },
  { name: "conswage", input: "conswage", label: "Earnings per construction job", unit: "USD a year, 2025", min: 0, max: 1000000, whole: true, group: "jobs",
    source: (_s, P) => `Census County Business Patterns ${P.wages.year}, NAICS 2362 (nonresidential building construction) and 238 (specialty trade contractors) in this state together: annual payroll over employment, in 2025 dollars.` },
  { name: "dsales", input: "sales", label: "Sales tax rate", unit: "%", min: 0, max: 15, whole: false, group: "taxes",
    source: () => "The state's rate plus its population-weighted average local rate, midyear 2026. Tax Foundation (CC BY-NC 4.0)." },
  { name: "matshare", input: "matshare", label: "Building's taxable purchases", unit: "% of its cost", min: 0, max: 100, whole: false, group: "taxes", nullable: true,
    source: () => "The materials share of the building's cost that bears sales tax. No public document read gives it for a datacenter: not given, and the building's sales tax is left out until the reader types one." },
  { name: "dcex", input: "dcex", label: "The state's datacenter exemption", unit: "", min: 0, max: 1, whole: true, group: "taxes",
    options: [{ value: 1, label: "Applied where the project qualifies" }, { value: 0, label: "Not applied" }],
    source: (s, P) => P.rules.states[s]?.sales_exemption?.tip ?? "No datacenter sales tax exemption of this state has been read: the sales tax is before exemptions." },
  { name: "brate", input: "brate", label: "Property tax on the building", unit: "% of assessed value", min: 0, max: 60, whole: false, group: "taxes", nullable: true,
    source: (s, P) => P.rules.states[s]?.property?.tip ?? "No rule of this state for a datacenter's property has been read: a rate typed here is the reader's own, on the building's cost." },
  { name: "erate", input: "erate", label: "Property tax on the equipment", unit: "% of assessed value", min: 0, max: 60, whole: false, group: "taxes", nullable: true,
    source: (s, P) => P.rules.states[s]?.property?.tip ?? "No rule of this state for a datacenter's property has been read: a rate typed here is the reader's own, on the equipment's cost." },
  { name: "eqv1", input: "eqv1", label: "Equipment's taxable value, first year", unit: "% of its cost", min: 0, max: 100, whole: false, group: "taxes",
    source: () => "Default 100: the equipment held at its cost, an upper bound (no state's schedule for datacenter equipment is read). A county's own schedule is typed here and below: Loudoun County's for computer equipment in a data center from 2026 is 60, 45, 30, 15 and 10 percent of original cost in its first five years (type 60, 15 and 10). The age restarts when the equipment is bought again." },
  { name: "eqstep", input: "eqstep", label: "Falls each year by", unit: "points", min: 0, max: 100, whole: false, group: "taxes",
    source: () => "The points of cost the equipment's taxable value loses each year of its cycle. Default 0 (held at cost)." },
  { name: "eqfloor", input: "eqfloor", label: "No lower than", unit: "% of its cost", min: 0, max: 100, whole: false, group: "taxes",
    source: () => "The floor of the equipment's taxable value. Default 0." },
  { name: "bldyears", input: "bldyears", label: "Building's value falls to 0 over", unit: "years", min: 1, max: 100, whole: true, group: "taxes", nullable: true,
    source: () => "The reader's own: the years over which the building's taxable value falls in a straight line. Not given: held at its cost, an upper bound." },
  { name: "pabate", input: "abate", label: "Property tax abated", unit: "%", min: 0, max: 100, whole: false, group: "taxes",
    source: () => "An abatement or payment in lieu agreed with the county or parish, as a share of the property tax. Default none: such agreements are negotiated, not statutes." },
  { name: "abateyears", input: "abateyears", label: "Abated for", unit: "operating years", min: 1, max: 60, whole: true, group: "taxes", nullable: true,
    source: () => "The agreement's years, from the first operating year. Not given: every year." },
  { name: "mwh", input: "mwh", label: "Electricity bought", unit: "MWh a year", min: 0, max: 200000000, whole: false, group: "taxes", nullable: true,
    source: (s, P) => `${P.rules.states[s]?.electricity?.tip ?? "No tax per kWh of this state on a datacenter's electricity has been read (Virginia, Illinois and Ohio are)."} No public document read gives a datacenter's load: not given until the reader types it (the MW times 8,760 times the share of the year at full load).` },
  { name: "drate", input: "rate", label: "Discount rate, real", unit: "%", min: 0, max: 20, whole: false, group: "value",
    source: () => "OMB Circular A-94's base case for benefit-cost analysis, 7 percent real. Its Appendix C gives 2.0 percent for 30-year Treasury borrowing (2026), the rate for cost-effectiveness analysis." },
];
export const DC_NAMES = DC_FIELDS.map((f) => f.name).concat(["dcproj"]);

export function dcClamp(f: DcField, x: number): number {
  const y = Math.min(f.max, Math.max(f.min, x));
  return f.whole ? Math.round(y) : y;
}
/** The datacenter's inputs from a scenario's values: each field the reader set, else its default for the state */
export function dcResolve(P: DcParams, v: Record<string, number>, state: string): DcInputs {
  const set: Partial<DcInputs> = {};
  for (const f of DC_FIELDS) {
    const x = v[f.name];
    if (Number.isFinite(x)) (set as Record<string, unknown>)[f.input] = f.input === "dcex" ? x === 1 : x;
  }
  return dcDefaults(P, state, set);
}

/** The announced projects the left box offers (datacenter_announced.json's rows, trimmed for the browser) */
export type DcProject = { id: string; name: string; state: string; where: string; date: string; publisher: string; url: string;
  mw: number | null; measure: string | null; invest: number | null; perm: number | null; cons: number | null; consMeasure: string | null };
type Fig = { value: number; measure?: string; year?: number } | null;
export function dcProjects(rows: { id: string; name: string; state: string; county: string | null; place?: string; doc: { date: string; publisher: string; url: string };
  mw: Fig; investment: Fig; permanent_jobs: Fig; construction_jobs: Fig; investment_includes_generation?: boolean; investment_partial?: string }[], index: Record<string, number>): DcProject[] {
  return rows.map((r) => {
    const y = r.investment?.year ?? 2025;
    const k = index[String(y)] ? index["2025"] / index[String(y)] : 1;  // a 2026 announcement taken as 2025 dollars
    return {
      id: r.id, name: r.name, state: r.state, where: r.county ?? r.place ?? "", date: r.doc.date, publisher: r.doc.publisher, url: r.doc.url,
      mw: r.mw?.value ?? null, measure: r.mw?.measure ?? null,
      // the DOE Paducah figure includes power plants: not offered as the datacenter's investment
      invest: r.investment && !r.investment_includes_generation && !r.investment_partial ? Math.round((r.investment.value * k) / 1e4) / 100 : null,  // USD million, 2025
      perm: r.permanent_jobs && !String(r.permanent_jobs.measure).includes("kind not stated") ? r.permanent_jobs.value : null,
      cons: r.construction_jobs?.value ?? null, consMeasure: r.construction_jobs?.measure ?? null,
    };
  });
}
