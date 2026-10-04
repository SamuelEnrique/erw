// Session 97: the demand growth explorer (/demand, in review). The pure part: what the page chooses from its address and
// how it reads the site's own copy of eia930_demand_growth (data/demand_growth.json, written by
// warehouse/derived/demand_growth.py; docs/methods/demand_growth.md). No arithmetic: every number is a row of the
// table. Weather is not removed, and the page says so.
export const TABLE = "eia930_demand_growth";

export type Year = Record<string, number>;
export type Area = { name: string; tz: string; years: Record<string, Year>; at: Record<string, Record<string, string>>; screened: { blank: number; not_positive: number; jumps: number } };
export type BreakRow = { year: number; before_mw: number; after_mw: number; ratio: number };
export type DemandFile = {
  table: string; built: string; base: number; last_year: number; ytd_through: string; jump: number; near_year: number; near_cell: number;
  order: string[]; areas: Record<string, Area>; caiso_break: { join: string; rows: BreakRow[] };
};

export const SLUGS: Record<string, string> = { ercot: "ERCO", caiso: "CISO", pjm: "PJM", miso: "MISO", spp: "SWPP", nyiso: "NYIS", isone: "ISNE", us48: "US48" };
export const slugOf = (ba: string) => Object.keys(SLUGS).find((s) => SLUGS[s] === ba)!;
export const RANKS = [
  { slug: "avg", field: "avg_demand_growth_since_2019_pct", name: "Average demand" },
  { slug: "peak", field: "peak_demand_growth_since_2019_pct", name: "Peak demand" },
  { slug: "ytd", field: "ytd_avg_demand_growth_since_2019_pct", name: "The year so far" },
] as const;
export type Rank = (typeof RANKS)[number];

/** The page's choices from its address: an area it does not know is the first, a ranking it does not know the first. */
export function choices(q: Record<string, string | undefined>): { ba: string; rank: Rank } {
  return { ba: SLUGS[q.area ?? ""] ?? SLUGS.ercot, rank: RANKS.find((r) => r.slug === q.rank) ?? RANKS[0] };
}
export const href = (area: string, rank: string) => `/demand?area=${area}&rank=${rank}`;

export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
/** A growth figure with its sign: "+27.22" or "-2.73". */
export const signed = (v: number) => `${v > 0 ? "+" : ""}${two(v)}`;
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const monthName = (m: number) => MONTHS[m - 1];
export const hourName = (h: number) => `${String(h).padStart(2, "0")}:00`;
const pad = (n: number) => String(n).padStart(2, "0");

/** The whole years of an area, in order, each with its figures. */
export function wholeYears(a: Area): { year: string; row: Year }[] {
  return Object.keys(a.years).sort().filter((y) => a.years[y].avg_demand_mw !== undefined).map((y) => ({ year: y, row: a.years[y] }));
}
/** The year so far: the newest year's row (it holds only year-to-date figures) and the same window of the base year. */
export function yearToDate(f: DemandFile, a: Area): { year: string; row: Year; base: Year } | null {
  const y = Object.keys(a.years).sort().at(-1)!;
  const row = a.years[y];
  return row.ytd_avg_demand_mw === undefined || Number(y) <= f.last_year ? null : { year: y, row, base: a.years[String(f.base)] };
}

/** The hour of a peak in the area's own time: "18 August 2025, 17:00". */
export function localHour(ts: string, tz: string): string {
  const d = new Date(ts);
  return `${d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: tz })}, ${d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: tz })}`;
}

export type Cell = { month: number; hour: number; mw: number; pct: number };
/** Where growth concentrates: the change from the base year to the last whole year in each month-and-hour cell the
 *  table holds (a cell missing in either year is absent, not zero). */
export function cells(f: DemandFile, a: Area): Cell[] {
  const r = a.years[String(f.last_year)] ?? {};
  const out: Cell[] = [];
  for (let m = 1; m <= 12; m++) for (let h = 0; h < 24; h++) {
    const mw = r[`growth_mw_m${pad(m)}_h${pad(h)}`], pct = r[`growth_pct_m${pad(m)}_h${pad(h)}`];
    if (mw !== undefined && pct !== undefined) out.push({ month: m, hour: h, mw, pct });
  }
  return out;
}
export const byMonth = (f: DemandFile, a: Area) => Array.from({ length: 12 }, (_, i) => ({ month: i + 1, mw: a.years[String(f.last_year)]?.[`growth_mw_m${pad(i + 1)}`], pct: a.years[String(f.last_year)]?.[`growth_pct_m${pad(i + 1)}`] }));
export const byHour = (f: DemandFile, a: Area) => Array.from({ length: 24 }, (_, h) => ({ hour: h, mw: a.years[String(f.last_year)]?.[`growth_mw_h${pad(h)}`], pct: a.years[String(f.last_year)]?.[`growth_pct_h${pad(h)}`] }));
/** The cell that grew most and the one that grew least (or fell most), by percent. */
export function extremes(cs: Cell[]): { most: Cell; least: Cell } | null {
  if (!cs.length) return null;
  return { most: cs.reduce((a, b) => (b.pct > a.pct ? b : a)), least: cs.reduce((a, b) => (b.pct < a.pct ? b : a)) };
}

export type Ranked = { ba: string; name: string; value: number | undefined; avg?: number; peak?: number; ytd?: number };
/** The ranking: every area by a growth measure, largest first; an area that lacks the measure last. The measure of the
 *  whole years is read off the last whole year's row, the year so far off the newest year's. */
export function ranking(f: DemandFile, rank: Rank): Ranked[] {
  const rows = f.order.map((ba) => {
    const a = f.areas[ba], last = a.years[String(f.last_year)] ?? {}, newest = a.years[Object.keys(a.years).sort().at(-1)!] ?? {};
    const r = { ba, name: a.name, avg: last.avg_demand_growth_since_2019_pct, peak: last.peak_demand_growth_since_2019_pct, ytd: newest.ytd_avg_demand_growth_since_2019_pct };
    return { ...r, value: r[rank.slug] };
  });
  return rows.sort((x, y) => (x.value === undefined ? 1 : y.value === undefined ? -1 : y.value - x.value));
}
