// Energy Research Warehouse (ERW) site, session 8012 (chain 505, part B1): the page "Energy use by industry" reads one
// file, data/industry.json, written by the data machine (warehouse/derived/industry_page.py; contract: section 9 of
// docs/state/page_files_regions.md; method: docs/methods/industry_page.md). This module holds the file's shape and the
// page's few sums, with no import, so a test can run it under node as it stands. Facts only: every figure is the file's
// own, or a sum of the file's own months for a year in which all twelve are held; nothing is filled, scaled or ranked
// beyond the order of the file's own figures.

export type Arr = (number | null)[];
export type IndustryEntry = {
  naics: string; name: string; rank_us_total?: number | null;
  by_region: Record<string, Record<string, number | null>>;
  electricity_mwh?: Record<string, Record<string, number | null>>;
};
export type IndustryFile = {
  built: string; method: string; license: string; tables: string[]; sources: Record<string, string>;
  monthly: { unit: string; months: string[]; labels: Record<string, string>; by_source: Record<string, Arr> };
  industries: { survey_year: number; unit: string; regions: string[]; fuels: string[]; ranked_3_digit: string[]; industries: Record<string, IndustryEntry>; note: string };
  states_annual: { unit: string; years: number[]; states: Record<string, { consumption_tbtu: Record<string, Arr>; expenditures_usd: Record<string, Arr>; price_usd_per_mmbtu: Arr }> };
  electricity_sales_monthly: { unit: string; months: string[]; states: Record<string, Arr> };
  outlook: { unit: string; release: string; years: string[]; cases: Record<string, string>; history_years: string[]; industries: Record<string, Record<string, Record<string, Arr>>> };
};

/** The file whole, or null when it is not that file (a key the page reads is missing). */
export function readIndustry(raw: unknown): IndustryFile | null {
  const f = raw as IndustryFile | null;
  if (!f || typeof f !== "object") return null;
  if (!f.monthly?.months || !f.monthly?.by_source || !f.industries?.industries || !f.states_annual?.states || !f.electricity_sales_monthly?.states || !f.outlook?.industries) return null;
  // the file writes the State Energy Data System's years as strings ("1990"); the page counts them as numbers
  return { ...f, states_annual: { ...f.states_annual, years: f.states_annual.years.map((y) => Number(y)) } };
}

// ---- words the page uses for the file's keys (the file's own labels where it gives them)

/** MECS's fuels in the survey's own words (EIA, 2022 MECS, Table 3.2's column heads). */
export const MECS_FUELS: { key: string; label: string }[] = [
  { key: "total", label: "Total" },
  { key: "net_electricity", label: "Net electricity" },
  { key: "natural_gas", label: "Natural gas" },
  { key: "coal", label: "Coal" },
  { key: "coke_and_breeze", label: "Coke and breeze" },
  { key: "residual_fuel_oil", label: "Residual fuel oil" },
  { key: "distillate_fuel_oil", label: "Distillate fuel oil" },
  { key: "hgl", label: "HGL (excluding natural gasoline)" },
  { key: "hydrogen", label: "Hydrogen" },
  { key: "other", label: "Other" },
];
export const MECS_REGIONS: { key: string; label: string }[] = [
  { key: "us", label: "United States" }, { key: "northeast", label: "Northeast" }, { key: "midwest", label: "Midwest" },
  { key: "south", label: "South" }, { key: "west", label: "West" },
];
/** The Monthly Energy Review's industrial sources drawn on the page, in Table 2.4's order. */
export const MONTHLY_KEYS = ["total", "end_use_total", "natural_gas", "petroleum", "electricity_retail_sales", "electrical_system_losses", "renewables", "coal"];
/** The State Energy Data System's industrial sources drawn on the page. */
export const SEDS_SOURCES: { key: string; label: string }[] = [
  { key: "total", label: "Total" }, { key: "natural_gas", label: "Natural gas" }, { key: "petroleum", label: "Petroleum" },
  { key: "electricity", label: "Electricity" }, { key: "electrical_system_losses", label: "Electrical system losses" },
  { key: "renewables", label: "Renewables" }, { key: "coal", label: "Coal" },
];
export const SEDS_EXPENDITURES: { key: string; label: string }[] = [
  { key: "total", label: "Total" }, { key: "natural_gas", label: "Natural gas" }, { key: "petroleum", label: "Petroleum" },
  { key: "electricity", label: "Electricity" }, { key: "coal", label: "Coal" },
];
/** The Annual Energy Outlook's industries as the file names them, in words. */
export const OUTLOOK_INDUSTRIES: Record<string, string> = {
  refining: "Refining", food: "Food", paper: "Paper", bulk_chemicals: "Bulk chemicals", glass: "Glass", cement_and_lime: "Cement and lime",
  iron_and_steel: "Iron and steel", aluminum: "Aluminum", metal_based_durables: "Metal-based durables", other_manufacturing: "Other manufacturing",
  nonmanufacturing: "Nonmanufacturing",
};

// ---- the monthly part (Monthly Energy Review, Table 2.4)

/** A month "YYYY-MM" as seconds at its first instant (UTC), as the site's line charts take points. */
export const monthT = (m: string) => Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1, 1) / 1000;
/** The newest month whose total is held, or null. */
export function lastMonth(f: IndustryFile): string | null {
  const t = f.monthly.by_source.total ?? [];
  for (let i = f.monthly.months.length - 1; i >= 0; i -= 1) if (t[i] !== null && t[i] !== undefined) return f.monthly.months[i];
  return null;
}
/** A source's held months from a year on, as chart points. */
export function monthlyPoints(f: IndustryFile, key: string, fromYear: number): { t: number; v: number }[] {
  const a = f.monthly.by_source[key] ?? [];
  const out: { t: number; v: number }[] = [];
  f.monthly.months.forEach((m, i) => { const v = a[i]; if (Number(m.slice(0, 4)) >= fromYear && v !== null && v !== undefined) out.push({ t: monthT(m), v }); });
  return out;
}
/** A source's figure for one month, or null. */
export function monthValue(f: IndustryFile, key: string, month: string): number | null {
  const i = f.monthly.months.indexOf(month);
  const v = i < 0 ? null : (f.monthly.by_source[key] ?? [])[i];
  return v === undefined ? null : v;
}
/** The sum of a year's twelve months, or null unless all twelve are held. */
export function yearSum(f: IndustryFile, key: string, year: number): number | null {
  let s = 0;
  for (let m = 1; m <= 12; m += 1) {
    const v = monthValue(f, key, `${year}-${String(m).padStart(2, "0")}`);
    if (v === null) return null;
    s += v;
  }
  return s;
}
/** The sum of the twelve months ending with a month ("YYYY-MM"), or null unless all twelve are held. Session 11407
 * (the audit of 26 November 2026, finding 7, readied for Samuel's ruling): the twelve months beside the one month. */
export function twelveMonthSum(f: IndustryFile, key: string, month: string): number | null {
  let y = Number(month.slice(0, 4)), m = Number(month.slice(5, 7)), s = 0;
  for (let k = 0; k < 12; k += 1) {
    const v = monthValue(f, key, `${y}-${String(m).padStart(2, "0")}`);
    if (v === null) return null;
    s += v;
    m -= 1;
    if (m === 0) { m = 12; y -= 1; }
  }
  return s;
}
/** The newest year with all twelve months of the total held. */
export function lastWholeYear(f: IndustryFile): number | null {
  const last = lastMonth(f);
  if (!last) return null;
  for (let y = Number(last.slice(0, 4)); y >= Number(f.monthly.months[0].slice(0, 4)); y -= 1) if (yearSum(f, "total", y) !== null) return y;
  return null;
}

// ---- the industries (2022 Manufacturing Energy Consumption Survey)

export type Ranked = { naics: string; name: string; total: number | null; fuels: Record<string, number | null> };
/** The three-digit industries with a region's figures, largest total first; an industry whose total EIA withholds in
 * that region stands last, in the file's order. */
export function rankedIndustries(f: IndustryFile, region: string): Ranked[] {
  const rows = f.industries.ranked_3_digit.map((n) => {
    const e = f.industries.industries[n];
    const fuels = e?.by_region?.[region] ?? {};
    return { naics: n, name: e?.name ?? n, total: fuels.total ?? null, fuels };
  });
  const held = rows.filter((r) => r.total !== null).sort((a, b) => (b.total as number) - (a.total as number));
  return [...held, ...rows.filter((r) => r.total === null)];
}
/** Every industry of the file, as choices: three-digit industries first in the file's rank, each followed by its own
 * finer industries in code order, the finer ones marked by their depth. */
export function industryChoices(f: IndustryFile): { value: string; label: string }[] {
  const all = Object.values(f.industries.industries);
  const out: { value: string; label: string }[] = [];
  for (const top of f.industries.ranked_3_digit) {
    const e = f.industries.industries[top];
    if (!e) continue;
    out.push({ value: top, label: `${e.name} (NAICS ${top})` });
    all.filter((x) => x.naics !== top && x.naics.startsWith(top)).sort((a, b) => a.naics.localeCompare(b.naics))
      .forEach((x) => out.push({ value: x.naics, label: `${"- ".repeat(Math.min(3, x.naics.length - 3))}${x.name} (NAICS ${x.naics})` }));
  }
  return out;
}
/** An industry's share of the three-digit industries' sum in a region, percent, or null when a total is withheld. */
export function shareOfSum(f: IndustryFile, naics: string, region: string): number | null {
  const rows = rankedIndustries(f, region);
  if (rows.some((r) => r.total === null)) return null;
  const sum = rows.reduce((a, r) => a + (r.total as number), 0);
  const me = f.industries.industries[naics]?.by_region?.[region]?.total;
  return me === null || me === undefined || !sum ? null : (100 * me) / sum;
}

// ---- the states (State Energy Data System) and electricity sold to industry (Form EIA-861M)

export type StateRow = { st: string; total: number | null; value: number | null; price: number | null; expenditures: number | null };
/** Every state's figure of a source in a year, largest first; the nation ("US") is left out of the order. */
export function rankedStates(f: IndustryFile, year: number, source: string): StateRow[] {
  const i = f.states_annual.years.indexOf(year);
  const rows = Object.entries(f.states_annual.states).filter(([st]) => st !== "US").map(([st, s]) => ({
    st,
    total: i < 0 ? null : s.consumption_tbtu.total?.[i] ?? null,
    value: i < 0 ? null : s.consumption_tbtu[source]?.[i] ?? null,
    price: i < 0 ? null : s.price_usd_per_mmbtu?.[i] ?? null,
    expenditures: i < 0 ? null : s.expenditures_usd.total?.[i] ?? null,
  }));
  const held = rows.filter((r) => r.value !== null).sort((a, b) => (b.value as number) - (a.value as number));
  return [...held, ...rows.filter((r) => r.value === null)];
}
/** A state's figure of a source by year, as points (a year at its first instant). */
export function statePoints(f: IndustryFile, st: string, source: string, part: "consumption_tbtu" | "expenditures_usd" = "consumption_tbtu"): { t: number; v: number }[] {
  const a = f.states_annual.states[st]?.[part]?.[source] ?? [];
  const out: { t: number; v: number }[] = [];
  f.states_annual.years.forEach((y, i) => { const v = a[i]; if (v !== null && v !== undefined) out.push({ t: Date.UTC(y, 0, 1) / 1000, v }); });
  return out;
}
export function stateValue(f: IndustryFile, st: string, source: string, year: number, part: "consumption_tbtu" | "expenditures_usd" = "consumption_tbtu"): number | null {
  const i = f.states_annual.years.indexOf(year);
  const v = i < 0 ? null : f.states_annual.states[st]?.[part]?.[source]?.[i];
  return v === undefined ? null : v;
}
export function statePrice(f: IndustryFile, st: string, year: number): number | null {
  const i = f.states_annual.years.indexOf(year);
  const v = i < 0 ? null : f.states_annual.states[st]?.price_usd_per_mmbtu?.[i];
  return v === undefined ? null : v;
}
/** The newest year whose national total is held. */
export function lastStateYear(f: IndustryFile): number | null {
  const t = f.states_annual.states.US?.consumption_tbtu.total ?? [];
  for (let i = f.states_annual.years.length - 1; i >= 0; i -= 1) if (t[i] !== null && t[i] !== undefined) return f.states_annual.years[i];
  return null;
}
/** Percent change between two years of a state's source, or null. */
export function changePct(f: IndustryFile, st: string, source: string, from: number, to: number): number | null {
  const a = stateValue(f, st, source, from), b = stateValue(f, st, source, to);
  return a === null || b === null || !a ? null : (100 * (b - a)) / a;
}
export function salesPoints(f: IndustryFile, st: string, fromYear: number): { t: number; v: number }[] {
  const a = f.electricity_sales_monthly.states[st] ?? [];
  const out: { t: number; v: number }[] = [];
  f.electricity_sales_monthly.months.forEach((m, i) => { const v = a[i]; if (Number(m.slice(0, 4)) >= fromYear && v !== null && v !== undefined) out.push({ t: monthT(m), v }); });
  return out;
}
/** The sum of a state's electricity sales over a year's twelve months, MWh, or null unless all twelve are held. */
export function salesYear(f: IndustryFile, st: string, year: number): number | null {
  const a = f.electricity_sales_monthly.states[st] ?? [];
  let s = 0;
  for (let m = 1; m <= 12; m += 1) {
    const i = f.electricity_sales_monthly.months.indexOf(`${year}-${String(m).padStart(2, "0")}`);
    const v = i < 0 ? null : a[i];
    if (v === null || v === undefined) return null;
    s += v;
  }
  return s;
}

// ---- the outlook (Annual Energy Outlook, industrial sub-sector tables)

/** An industry's series names, the total first where the file names one. */
export function outlookSeries(f: IndustryFile, industry: string): string[] {
  const names = Object.keys(f.outlook.industries[industry] ?? {});
  const total = names.filter((n) => /Total$|Total Energy Use$/.test(n) && !/Ethanol/.test(n)).sort((a, b) => Number(/Total Energy Use/.test(b)) - Number(/Total Energy Use/.test(a)));
  return [...total, ...names.filter((n) => !total.includes(n)).sort()];
}
export function outlookPoints(f: IndustryFile, industry: string, series: string, kase: string): { t: number; v: number }[] {
  const a = f.outlook.industries[industry]?.[series]?.[kase] ?? [];
  const out: { t: number; v: number }[] = [];
  f.outlook.years.forEach((y, i) => { const v = a[i]; if (v !== null && v !== undefined) out.push({ t: Date.UTC(Number(y), 0, 1) / 1000, v }); });
  return out;
}
export function outlookValue(f: IndustryFile, industry: string, series: string, kase: string, year: string): number | null {
  const i = f.outlook.years.indexOf(year);
  const v = i < 0 ? null : f.outlook.industries[industry]?.[series]?.[kase]?.[i];
  return v === undefined ? null : v;
}

// ---- number words

export const tbtu = (v: number | null) => (v === null ? null : v.toLocaleString("en-US", { maximumFractionDigits: v >= 100 ? 0 : 1 }));
export const pct1 = (v: number | null) => (v === null ? null : `${v >= 0 ? "+" : ""}${v.toFixed(1)}%`);
