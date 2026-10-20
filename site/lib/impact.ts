// Energy Research Warehouse (ERW) site, session 347: the economic impact tool, /impact ("What a project does for a
// state"), tool 17 of the platform. Every figure is NLR's JEDI model's, per MW, from nlr_jedi_multipliers (sessions 345
// and 347: each workbook's own formulas evaluated for each state), times the reader's project; the tax rules are
// impact_tax_rules (session 346). docs/methods/economic_impact.md says what JEDI assumes and cannot see.
//
// This file is the page's arithmetic and scripts/check-values.mjs's: a figure's check key names its inputs and its
// stat (impact|<technology>|<state>|<mw>|<capex>|<local>|<life>|<stat>), and stat() recomputes it from the rows of the
// table. No import with a path alias: check-values imports this file as it is.
//
// The reader's three levers act as JEDI's arithmetic does, in proportion. JEDI multiplies each line of spending by a
// local share and a multiplier, so every effect is proportional to the spending: the project's MW scales both phases,
// the capital cost (a percent of JEDI's default) scales the construction phase, and the local content (a percent of
// JEDI's default shares) scales both. The last is the one approximation: JEDI applies a share to each line, and the
// page scales all of a phase's lines by one factor. At the defaults (JEDI's project, 100 and 100) every figure is JEDI's.

export const TABLE = "nlr_jedi_multipliers";
export const TAX_TABLE = "impact_tax_rules";
export const METHOD = "/data/methods/economic_impact";

export type Phase = "construction" | "operations";
export type Effect = "onsite" | "supply_chain" | "induced" | "total";
export type Measure = "jobs" | "earnings" | "output";
export const PHASES: Phase[] = ["construction", "operations"];
export const EFFECTS: Effect[] = ["onsite", "supply_chain", "induced", "total"];
export const MEASURES: Measure[] = ["jobs", "earnings", "output"];
export const EFFECT_WORDS: Record<Effect, string> = { onsite: "On site", supply_chain: "Supply chain", induced: "Induced", total: "Total" };
export const EFFECT_TIPS: Record<Effect, string> = {
  onsite: "The people on the site: construction crews, then the plant's own staff (JEDI's \"project development and onsite labor\"; the direct effect).",
  supply_chain: "The state's businesses that sell to the project, and the businesses that sell to them (JEDI's supply chain line; the indirect effect).",
  induced: "The spending of those wages in the state's shops, restaurants and services (JEDI's induced impacts).",
  total: "The three added. The table checks that JEDI's own total is their sum in every state.",
};

export type TechKey = "land_based_wind" | "utility_pv" | "natural_gas" | "geothermal";
export type Tech = {
  key: TechKey; label: string; model: string; version: string; file: string; url: string; page: string; sheet: string;
  /** the summary row of each phase and effect (jobs, earnings and output are its columns B, C and D) */
  rows: Record<Phase, Record<Effect, number>>;
  /** the MW the model's default project is counted in */
  basis: string;
  /** the one setting changed besides the location */
  setting?: string;
};
const NLR = "https://www.nlr.gov/docs/libraries/analysis/";
export const TECHS: Tech[] = [
  { key: "land_based_wind", label: "Land-based wind", model: "JEDI Land-based Wind Model", version: "W9.14.18", file: "01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm",
    url: `${NLR}01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm?sfvrsn=e1d95728_2`, page: "https://www.nlr.gov/analysis/jedi/wind", sheet: "SummaryResults",
    rows: { construction: { onsite: 28, supply_chain: 29, induced: 30, total: 31 }, operations: { onsite: 34, supply_chain: 35, induced: 36, total: 37 } }, basis: "nameplate MW" },
  { key: "utility_pv", label: "Utility-scale solar PV", model: "JEDI Photovoltaics Model", version: "PV05.20.21", file: "jedi-pv-model.xlsm",
    url: `${NLR}jedi-pv-model.xlsm?sfvrsn=837efebd_2`, page: "https://www.nlr.gov/analysis/jedi/pv", sheet: "SummaryResults",
    rows: { construction: { onsite: 30, supply_chain: 38, induced: 39, total: 40 }, operations: { onsite: 46, supply_chain: 47, induced: 48, total: 49 } }, basis: "MW of DC nameplate",
    setting: "the model's System Application set to its own Utility option (the workbook is saved with a residential project)" },
  { key: "natural_gas", label: "Natural gas", model: "JEDI Natural Gas Model", version: "NG4.17.17", file: "01d-jedi-ngas-model_rel-ng4-17-17.xlsm",
    url: `${NLR}01d-jedi-ngas-model_rel-ng4-17-17.xlsm?sfvrsn=d9ff898_2`, page: "https://www.nlr.gov/analysis/jedi/natural-gas", sheet: "SummaryResults",
    rows: { construction: { onsite: 27, supply_chain: 30, induced: 31, total: 32 }, operations: { onsite: 35, supply_chain: 36, induced: 37, total: 38 } }, basis: "nameplate MW" },
  { key: "geothermal", label: "Geothermal", model: "JEDI Geothermal Model", version: "GT12.23.16", file: "01d-jedi-geothermal-model-rel-gt12-23-16.xlsm",
    url: `${NLR}01d-jedi-geothermal-model-rel-gt12-23-16.xlsm`, page: "https://www.nlr.gov/analysis/jedi/geothermal", sheet: "Summary Results",
    rows: { construction: { onsite: 23, supply_chain: 26, induced: 27, total: 28 }, operations: { onsite: 31, supply_chain: 32, induced: 33, total: 34 } }, basis: "nameplate MW (the model's plant is 10 MW net)" },
];
/** The technology the reader may ask for that JEDI has no model of: named, never filled. */
export const NOT_MODELED = { key: "battery_storage", label: "Battery storage", why: "NLR publishes no JEDI model for battery storage (the thirteen models on https://www.nlr.gov/analysis/jedi/models, read 20 October 2026, have none), so this page shows no figure for it." };
export const techOf = (k: string): Tech | null => TECHS.find((t) => t.key === k) ?? null;

export const STATES: [string, string][] = [
  ["al", "Alabama"], ["ak", "Alaska"], ["az", "Arizona"], ["ar", "Arkansas"], ["ca", "California"], ["co", "Colorado"], ["ct", "Connecticut"],
  ["de", "Delaware"], ["dc", "District of Columbia"], ["fl", "Florida"], ["ga", "Georgia"], ["hi", "Hawaii"], ["id", "Idaho"], ["il", "Illinois"],
  ["in", "Indiana"], ["ia", "Iowa"], ["ks", "Kansas"], ["ky", "Kentucky"], ["la", "Louisiana"], ["me", "Maine"], ["md", "Maryland"],
  ["ma", "Massachusetts"], ["mi", "Michigan"], ["mn", "Minnesota"], ["ms", "Mississippi"], ["mo", "Missouri"], ["mt", "Montana"], ["ne", "Nebraska"],
  ["nv", "Nevada"], ["nh", "New Hampshire"], ["nj", "New Jersey"], ["nm", "New Mexico"], ["ny", "New York"], ["nc", "North Carolina"],
  ["nd", "North Dakota"], ["oh", "Ohio"], ["ok", "Oklahoma"], ["or", "Oregon"], ["pa", "Pennsylvania"], ["ri", "Rhode Island"],
  ["sc", "South Carolina"], ["sd", "South Dakota"], ["tn", "Tennessee"], ["tx", "Texas"], ["ut", "Utah"], ["vt", "Vermont"], ["va", "Virginia"],
  ["wa", "Washington"], ["wv", "West Virginia"], ["wi", "Wisconsin"], ["wy", "Wyoming"], ["us", "United States (national)"],
];
export const stateName = (s: string) => STATES.find(([k]) => k === s)?.[1] ?? s.toUpperCase();
/** the states whose tax rules the ERW holds (impact_tax_rules) */
export const TAX_STATES = ["tx", "la", "nm"];

export type Inputs = {
  tech: TechKey; state: string;
  /** MW of the reader's project; null is JEDI's default project */
  mw: number | null;
  /** the capital cost as a percent of JEDI's default */
  capex: number;
  /** the local content as a percent of JEDI's default shares */
  local: number;
  /** years of operation; null is none given (JEDI states no life) */
  life: number | null;
  /** the abatement scenario: off by default, and with no rule held it applies nothing */
  abate: boolean;
};
export const DEFAULTS: Inputs = { tech: "land_based_wind", state: "tx", mw: null, capex: 100, local: 100, life: null, abate: false };
export const BOUNDS = { mw: [1, 10000], capex: [25, 400], local: [0, 200], life: [1, 60] } as const;

const num = (v: string | undefined) => (v === undefined || v.trim() === "" ? NaN : Number(v));
const clamp = (v: number, [lo, hi]: readonly [number, number]) => Math.min(hi, Math.max(lo, v));

/** The reader's inputs from the address, each outside its bounds brought inside them, and what was typed and not used. */
export function inputsOf(q: Record<string, string | undefined>): { x: Inputs; notes: string[] } {
  const notes: string[] = [];
  const tech = techOf(q.tech ?? "")?.key ?? DEFAULTS.tech;
  if (q.tech && q.tech !== tech) notes.push(q.tech === NOT_MODELED.key ? NOT_MODELED.why : `"${q.tech}" is not a technology JEDI models here, so the page shows ${techOf(tech)!.label.toLowerCase()}.`);
  const state = STATES.some(([k]) => k === (q.state ?? "").toLowerCase()) ? (q.state as string).toLowerCase() : DEFAULTS.state;
  if (q.state && q.state.toLowerCase() !== state) notes.push(`"${q.state}" is not a state of the list, so the page shows ${stateName(state)}.`);
  const pick = (k: "mw" | "capex" | "local" | "life", whole: boolean) => {
    const v = num(q[k]);
    if (!Number.isFinite(v)) return null;
    const c = clamp(whole ? Math.round(v) : v, BOUNDS[k]);
    if (c !== v) notes.push(`${k} ${q[k]} is outside ${BOUNDS[k][0]} to ${BOUNDS[k][1]}, so ${c} is used.`);
    return c;
  };
  const mw = pick("mw", false), capex = pick("capex", true), local = pick("local", true), life = pick("life", true);
  return { x: { tech, state, mw, capex: capex ?? DEFAULTS.capex, local: local ?? DEFAULTS.local, life, abate: q.abate === "1" }, notes };
}

export type Row = { entity: string; variable: string; ts_utc: string; value: number };
export const entity = (tech: string, state: string, phase: string, effect: string) => `nlr_jedi:${tech}:${state}:${phase}:${effect}`;
/** JEDI's value per MW (or the project's MW, or a phase's local share) in the rows of one technology and state */
export function perMw(rows: Row[], x: { tech: string; state: string }, phase: string, effect: string, measure: string): number | null {
  const r = rows.find((r) => r.entity === entity(x.tech, x.state, phase, effect) && r.variable === measure);
  return r ? Number(r.value) : null;
}
export const projectMw = (rows: Row[], x: { tech: string; state: string }) => perMw(rows, x, "all", "project", "project_mw");
/** The MW the figures are for: the reader's, else JEDI's default project's */
export const mwOf = (rows: Row[], x: Inputs) => x.mw ?? projectMw(rows, x);

/** The key of the inputs, for the check keys: impact|<tech>|<state>|<mw>|<capex>|<local>|<life> (mw "jedi" for JEDI's own) */
export const inputsKey = (x: Inputs) => ["impact", x.tech, x.state, x.mw ?? "jedi", x.capex, x.local, x.life ?? "-"].join("|");
export function parseKey(key: string): { x: Inputs; stat: string } {
  const p = key.split("|");
  return { x: { tech: p[1] as TechKey, state: p[2], mw: p[3] === "jedi" ? null : Number(p[3]), capex: Number(p[4]), local: Number(p[5]),
    life: p[6] === "-" ? null : Number(p[6]), abate: false }, stat: p.slice(7).join("|") };
}

/** The factor the reader's levers apply to JEDI's per-MW figure of a phase */
export function factor(x: Inputs, phase: Phase, mw: number): number {
  return mw * (x.local / 100) * (phase === "construction" ? x.capex / 100 : 1);
}

/** One figure of the page, by its stat:
 *   <phase>:<effect>:<measure>   the reader's project (construction: over the build; operations: each year)
 *   life:<effect>:<measure>      operations over the reader's life (null when no life is given)
 *   mw                           the MW the figures are for
 *   state:<state>:<phase>:<effect>:<measure>  the same project in another state
 *   state_rank:<phase>:<measure> the state's place among the 51 (1 is the most), at JEDI's per-MW total
 *   swing:<lever>:<phase>:<measure> the total at the lever's swing (mw +50%, capex +25 points, local +25 points, life +5 years) */
export function stat(rows: Row[], x: Inputs, s: string, all?: Row[]): number | null {
  const mw = mwOf(rows, x);
  if (mw === null) return null;
  const p = s.split(":");
  if (s === "mw") return mw;
  if (p[0] === "construction" || p[0] === "operations") {
    const v = perMw(rows, x, p[0], p[1], p[2]);
    return v === null ? null : v * factor(x, p[0] as Phase, mw);
  }
  if (p[0] === "life") {
    if (x.life === null) return null;
    const v = perMw(rows, x, "operations", p[1], p[2]);
    return v === null ? null : v * factor(x, "operations", mw) * x.life;
  }
  if (p[0] === "swing") {
    const [, lever, phase, measure] = p;
    const y: Inputs = { ...x, mw };
    if (lever === "mw") y.mw = mw * 1.5;
    else if (lever === "capex") y.capex = x.capex + 25;
    else if (lever === "local") y.local = x.local + 25;
    else if (lever === "life") y.life = (x.life ?? 0) + 5;
    else return null;
    if (phase === "life") return y.life === null ? null : stat(rows, y, `life:total:${measure}`);
    return stat(rows, y, `${phase}:total:${measure}`);
  }
  if (p[0] === "state") {
    // state:<state>:<phase>:<effect>:<measure>, the reader's project built in another state (every state's rows in `all`)
    if (!all) return null;
    const [, k, phase, effect, measure] = p;
    const v = perMw(all, { tech: x.tech, state: k }, phase, effect, measure);
    return v === null ? null : v * factor(x, phase as Phase, mw);
  }
  if (p[0] === "state_rank") {
    if (!all) return null;
    const [, phase, measure] = p;
    const vals = STATES.filter(([k]) => k !== "us").map(([k]) => ({ k, v: perMw(all, { tech: x.tech, state: k }, phase, "total", measure) }))
      .filter((r): r is { k: string; v: number } => r.v !== null).sort((a, b) => b.v - a.v);
    const i = vals.findIndex((r) => r.k === x.state);
    return i < 0 ? null : i + 1;
  }
  return null;
}

/** The number of states JEDI gives a figure for, for one technology (the gas model has none for DC and Hawaii) */
export const statesHeld = (all: Row[], tech: string) =>
  new Set(all.filter((r) => r.variable === "jobs" && r.entity.startsWith(`nlr_jedi:${tech}:`) && !r.entity.includes(":us:")).map((r) => r.entity.split(":")[2])).size;

/** JEDI's line, in words, for a figure's hover */
export function lineWords(t: Tech, phase: Phase, effect: Effect, measure: Measure, state: string): string {
  const col = { jobs: "B", earnings: "C", output: "D" }[measure];
  return `${t.model} ${t.version}, sheet ${t.sheet}, cell ${col}${t.rows[phase][effect]}, with Project Location ${stateName(state)}, divided by the default project's ${t.basis}${t.setting ? `; ${t.setting}` : ""}`;
}

export const UNIT: Record<Phase, Record<Measure, string>> = {
  construction: { jobs: "job-years", earnings: "USD", output: "USD" },
  operations: { jobs: "jobs each year", earnings: "USD a year", output: "USD a year" },
};
/** a figure as the page writes it, as scripts/check-values.mjs reads it: a count whole with commas, any other number to
 *  two decimals; dollars of a million or more short ("63.46 million"), as the deals table writes them (the Num inside
 *  <span data-format="usd">: usdShort), and below a million to two decimals like any other number */
export const usdShort = (v: number, measure: string) => (measure === "earnings" || measure === "output") && Math.abs(v) >= 1e6;
export function fmt(v: number, measure: Measure | "mw" | "rank"): string {
  if (measure === "earnings" || measure === "output") {
    const t = (x: number) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
    if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
    if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  }
  return Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** The address of a view, with only what differs from the defaults */
export function hrefOf(x: Partial<Inputs> & { tech: string; state: string }): string {
  const q = new URLSearchParams();
  if (x.tech !== DEFAULTS.tech) q.set("tech", x.tech);
  if (x.state !== DEFAULTS.state) q.set("state", x.state);
  if (x.mw !== undefined && x.mw !== null) q.set("mw", String(x.mw));
  if (x.capex !== undefined && x.capex !== DEFAULTS.capex) q.set("capex", String(x.capex));
  if (x.local !== undefined && x.local !== DEFAULTS.local) q.set("local", String(x.local));
  if (x.life !== undefined && x.life !== null) q.set("life", String(x.life));
  if (x.abate) q.set("abate", "1");
  const s = q.toString();
  return `/impact${s ? `?${s}` : ""}`;
}
