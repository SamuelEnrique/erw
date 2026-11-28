// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part B): "Every state on one page" (/states) reads one
// file a place, data/states/<st>.json, and data/states/index.json, written by the data machine
// (warehouse/derived/states_page.py; contract: docs/state/page_files_states.md; method: docs/methods/states_page.md).
// This module holds the files' shape, reads a file by a code the index names (never a visitor's words), and does the
// little arithmetic the page names: sums of months, shares, a year's twelve months. Nothing is filled: a figure the
// file does not hold is null and is drawn as "not held" with the file's reason.
import fs from "node:fs";
import path from "node:path";

export type Arr = (number | null)[];
type Part = { table: string; vintage?: string; source?: string; reason?: string };
export type Generation = Part & { unit: string; months: string[] | null; by_source: Record<string, Arr>; total: Arr; years: string[]; annual: Record<string, Arr>;
  last12: { from: string; to: string; total_mwh: number; mwh: Record<string, number | null>; share_pct: Record<string, number | null> }; hourly: null; hourly_reason: string };
export type Sector = "residential" | "commercial" | "industrial" | "transportation" | "all";
export type Retail = Part & { price_table: string; months: string[] | null; sales_mwh: Record<Sector, Arr>; price_usd_per_mwh: Record<Sector, Arr>; revenue_usd: Record<Sector, Arr>;
  revenue_note: string; years: string[]; annual_sales_mwh: Record<Sector, Arr>; annual_revenue_usd: Record<Sector, Arr>;
  last12: { from: string; to: string; by_sector: Record<Sector, { sales_mwh: number | null; revenue_usd: number | null; price_usd_per_mwh: number | null }> };
  customers: { month: string | null; by_sector: Record<Sector, number | null> } };
export type Plant = { plant_id: string; name: string; county: string; operator: string; balancing_authority: string | null; nameplate_mw: number; net_summer_mw: number | null;
  technology_group: string; technologies: Record<string, number>; lat: number | null; lon: number | null; generators: number };
type ByYear = Record<string, Record<string, { nameplate_mw: number | null; generators: number; under_construction_mw?: number | null }>>;
export type Plants = Part & { planned_table: string; retired_table: string; unit: string;
  capacity_by_technology: Record<string, { nameplate_mw: number | null; net_summer_mw: number | null; generators: number; energy_mwh?: number | null }>;
  capacity_total_mw: number | null; plants: number; largest: Plant[] | null; coming_by_year: ByYear; retiring_by_year: ByYear; retired_by_year: ByYear; retired_note: string };
export type Co2 = Part & { unit: string; years: string[] | null; tons_by_fuel: Record<string, Arr>; rate_kg_per_mwh: Arr };
export type Gas = Part & { production_table: string; unit: string; months: string[] | null; consumption: Record<string, Arr | null>; consumption_reason: Record<string, string>;
  marketed_production: Arr | null; production_reason?: string };
export type Energy = Part & { sector_tables: string[]; unit: string; years: string[] | null; by_source: Record<string, Arr | null>; by_sector: Record<string, Arr | null>; by_sector_reason: Record<string, string> };
export type Disposition = Part & { unit: string; years: string[] | null; values: Record<string, Arr | null>; note: string };
export type Authority = { code: string | null; name: string | null; region: string | null; grid: string | null; counties: number; population: number | null; share_pct: number | null; shared_counties: number; reason: string | null };
export type Serving = Part & { population_table?: string; population_year?: string; population?: number; by_authority: Authority[] | null; by_grid_pct?: Record<string, number | null>; basis?: string; shares_reason?: string | null; counties_without_population?: string[] };
export type Law = { law_id: string; bill: string; session: string; title: string; status: string; date: string; date_kind: string; effective: string | null; threshold: string | null; requirements: string | null; url: string; read: string | null };
export type StateFile = { built: string; state: string; name: string; method: string; license: string; tables: string[];
  generation: Generation; retail: Retail; plants: Plants; co2: Co2; gas: Gas; energy: Energy; disposition: Disposition; serving: Serving;
  large_load_laws: { table: string; source?: string; laws: Law[]; reason?: string };
  severance: { file: string; in_tool: boolean; address?: string; products?: string[]; source?: string; reason?: string } };
export type IndexRow = { state: string; name: string; file: string; bytes: number; generation_last12_mwh: number | null; largest_source_last12: string | null;
  largest_source_share_pct: number | null; price_all_last12_usd_per_mwh: number | null; capacity_mw: number | null; grids: string[] | null; laws: number };
export type StatesIndex = { built: string; method: string; license: string; tables: string[]; contract: string; generation_months: [string, string]; states: IndexRow[] };

export const GEN_SOURCES = ["coal", "natural_gas", "nuclear", "hydro", "wind", "solar", "other_renewables", "oil_and_other", "not_itemized"] as const;
export const SECTORS: { key: Sector; label: string }[] = [
  { key: "residential", label: "Homes (residential)" }, { key: "commercial", label: "Businesses (commercial)" },
  { key: "industrial", label: "Industry" }, { key: "transportation", label: "Transportation" }, { key: "all", label: "All sectors" },
];
export const TECH_WORDS: Record<string, string> = {
  natural_gas: "Natural gas", coal: "Coal", nuclear: "Nuclear", hydro: "Hydro (pumped storage is under batteries)", wind: "Wind", solar: "Solar", storage: "Batteries and pumped storage",
  petroleum: "Petroleum", biomass: "Biomass", geothermal: "Geothermal", other: "Other",
};
export const CO2_WORDS: Record<string, string> = { all: "All fuels", coal: "Coal", natural_gas: "Natural gas", petroleum: "Petroleum", other: "Other" };
export const GAS_WORDS: Record<string, string> = { residential: "Homes", commercial: "Businesses", industrial: "Industry", electric_power: "Power plants" };
export const SEDS_WORDS: Record<string, string> = {
  total: "Total energy", coal: "Coal", natural_gas: "Natural gas", petroleum: "Petroleum", nuclear: "Nuclear electric power", renewables: "Renewable energy",
  // session 10223 (the states audit, finding 8): SEDS's total holds the energy that made the electricity sold (the fuels,
  // and the net flow of electricity into the state), so this row is not added to the rows above it
  electricity_retail_sales: "Electricity sold to customers (already counted in the total)",
};

const DIR = () => path.join(process.cwd(), "data", "states");
const CODE = /^[a-z]{2}$/;

/** The index, or null when the folder is not on the server. */
export function readIndex(): StatesIndex | null {
  try { return JSON.parse(fs.readFileSync(path.join(DIR(), "index.json"), "utf8")) as StatesIndex; } catch { return null; }
}

/** One place's file, by a code the index names; null for any other word or a missing file. */
export function readState(index: StatesIndex | null, code: string): StateFile | null {
  const c = code.toLowerCase();
  if (!index || !CODE.test(c) || !index.states.some((r) => r.state.toLowerCase() === c)) return null;
  try { return JSON.parse(fs.readFileSync(path.join(DIR(), `${c}.json`), "utf8")) as StateFile; } catch { return null; }
}

/** Seconds at the first of a month "YYYY-MM", as the charts take them. */
export const monthT = (m: string) => Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 1) / 1000;
export const yearT = (y: string) => Date.UTC(Number(y), 0, 1) / 1000;

/** The points of a monthly array from a first year on, nulls left out. */
export function monthPoints(months: string[] | null, a: Arr | null | undefined, from = 0, scale = 1): { t: number; v: number }[] {
  if (!months || !a) return [];
  const out: { t: number; v: number }[] = [];
  months.forEach((m, i) => { const v = a[i]; if (v !== null && v !== undefined && Number(m.slice(0, 4)) >= from) out.push({ t: monthT(m), v: v * scale }); });
  return out;
}
export function yearPoints(years: string[] | null, a: Arr | null | undefined, scale = 1): { t: number; v: number }[] {
  if (!years || !a) return [];
  const out: { t: number; v: number }[] = [];
  years.forEach((y, i) => { const v = a[i]; if (v !== null && v !== undefined) out.push({ t: yearT(y), v: v * scale }); });
  return out;
}

/** A value of an annual array by year, or null. */
export function atYear(years: string[] | null, a: Arr | null | undefined, y: string): number | null {
  if (!years || !a) return null;
  const i = years.indexOf(y);
  return i < 0 ? null : a[i] ?? null;
}

/** The whole years of the generation part (every source of the year holds twelve months), newest last. */
export function wholeGenYears(f: StateFile): string[] {
  const g = f.generation;
  if (!g.months) return [];
  return g.years.filter((_, i) => g.annual.total[i] !== null);
}

/** A source's share of the year's total generation, percent; null when either is not held. The total is the sum of
 * the sources the file holds for the year. */
export function genShare(f: StateFile, src: string, y: string): number | null {
  const g = f.generation;
  if (!g.months) return null;
  const v = atYear(g.years, g.annual[src], y), t = atYear(g.years, g.annual.total, y);
  return v === null || t === null || !t ? null : (100 * v) / t;
}

// Session 11407 (the states audit of 26 November 2026, finding 6, readied for Samuel's ruling): round once. The files
// carry the twelve months' price and shares already rounded (to 0.01), and the page rounded them again, one in the last
// digit off in 34 cells. These compute each from the figures the file holds unrounded enough (revenue and sales, MWh,
// people), so the page rounds once; where the parts are not held, the file's own figure (null stays null).
/** The twelve months' price, USD a MWh: revenue over sales. */
export function price12(b: { sales_mwh: number | null; revenue_usd: number | null; price_usd_per_mwh: number | null } | null | undefined): number | null {
  if (!b) return null;
  return b.revenue_usd !== null && b.sales_mwh !== null && b.sales_mwh ? b.revenue_usd / b.sales_mwh : b.price_usd_per_mwh;
}
/** A source's share of the twelve months, percent: its MWh over the total's. */
export function share12(l: Generation["last12"] | null | undefined, src: string): number | null {
  if (!l) return null;
  const v = l.mwh[src];
  return v !== null && v !== undefined && l.share_pct[src] !== null && l.total_mwh ? (100 * v) / l.total_mwh : l.share_pct[src] ?? null;
}
/** An authority's share of the state's people, percent: its people over the state's. */
export function peopleShare(s: Serving, a: Authority): number | null {
  return a.population !== null && a.share_pct !== null && s.population ? (100 * a.population) / s.population : a.share_pct;
}

/** A source's share of each whole year, as points. */
export function sharePoints(f: StateFile, src: string): { t: number; v: number }[] {
  return wholeGenYears(f).map((y) => ({ y, v: genShare(f, src, y) })).filter((p) => p.v !== null).map((p) => ({ t: yearT(p.y), v: p.v as number }));
}

/** Years of a ByYear table, those from `from` on, sorted; and its groups, largest first. */
export function byYearTable(t: Record<string, Record<string, { nameplate_mw: number | null }>>, from?: number): { years: string[]; groups: string[] } {
  const years = Object.keys(t).filter((y) => from === undefined || y === "no date" || Number(y) >= from).sort();
  const sums: Record<string, number> = {};
  for (const y of years) for (const [g, v] of Object.entries(t[y])) sums[g] = (sums[g] ?? 0) + (v.nameplate_mw ?? 0);
  return { years, groups: Object.keys(sums).sort((a, b) => sums[b] - sums[a]) };
}

/** The largest primary authority's region, lower case, for the Grid tool's link; null when the file names none. */
export function gridRegion(f: StateFile): string | null {
  const a = (f.serving.by_authority ?? []).find((r) => r.region);
  return a?.region ? a.region.toLowerCase() : null;
}

/** The newest year of CO2 with a figure for all fuels. */
export function lastCo2(f: StateFile): { year: string; tons: number | null; rate: number | null } | null {
  const c = f.co2;
  if (!c.years) return null;
  for (let i = c.years.length - 1; i >= 0; i--) {
    const v = c.tons_by_fuel.all?.[i] ?? null;
    if (v !== null) return { year: c.years[i], tons: v, rate: c.rate_kg_per_mwh[i] ?? null };
  }
  return null;
}

/** The sum of a monthly array over a whole year, only when all twelve months are held. */
export function yearOfMonths(months: string[] | null, a: Arr | null | undefined, y: string): number | null {
  if (!months || !a) return null;
  let s = 0, n = 0;
  months.forEach((m, i) => { if (m.slice(0, 4) === y) { const v = a[i]; if (v !== null && v !== undefined) { s += v; n++; } } });
  return n === 12 ? s : null;
}

/** The newest whole calendar year of a monthly part. */
export function lastWholeYear(months: string[] | null): string | null {
  if (!months || !months.length) return null;
  const last = months[months.length - 1];
  return last.endsWith("-12") ? last.slice(0, 4) : String(Number(last.slice(0, 4)) - 1);
}
