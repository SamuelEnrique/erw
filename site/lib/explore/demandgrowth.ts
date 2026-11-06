// Energy Research Warehouse (ERW) site, session 404: the demand growth explorer's own parts (/explore/demand-growth;
// the frame is components/explore/Explore.tsx). It reads eia930_demand_growth (docs/methods/demand_growth.md) as it
// stands in the live set and computes nothing: every figure it shows is one row of the table, with that row's check key.
// No read here, so the tests can run it in Node.
import { SLUGS } from "@/lib/demandgrowth";

export const TABLE = "eia930_demand_growth";
/** The year growth is measured from (the table's base year, the method note). */
export const BASE = 2019;

export type Row = { entity: string; variable: string; ts_utc: string; value: number };

/** The eight areas of the table, in the order /demand lists them, by the address's slug (the same slugs as /demand's). */
export const GRIDS: { slug: string; ba: string; name: string }[] = [
  { slug: "ercot", ba: "ERCO", name: "ERCOT" }, { slug: "caiso", ba: "CISO", name: "CAISO" }, { slug: "pjm", ba: "PJM", name: "PJM" },
  { slug: "miso", ba: "MISO", name: "MISO" }, { slug: "spp", ba: "SWPP", name: "SPP" }, { slug: "nyiso", ba: "NYIS", name: "NYISO" },
  { slug: "isone", ba: "ISNE", name: "ISO-NE" }, { slug: "us48", ba: "US48", name: "Lower 48" },
].filter((g) => SLUGS[g.slug] === g.ba);
export const entityOf = (ba: string) => `eia930:${ba}`;
export const DEFAULT_GRID = "ercot";   // the thesis's grid: /demand opens on ERCOT too
export const DEFAULT_WINDOW = "avg";

const pad = (n: number) => String(n).padStart(2, "0");
const MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/** A window of the year the growth is read over. `mw` is the demand in the window (a row for every year it holds);
 *  `growth` its growth since the base year, in percent: a row for every year (`perYear`) or, for a month or an hour of
 *  the day, on the last whole year's row only, with the change in MW beside it (`growthMw`). `latest` names the year
 *  growth is read at: the last whole year, or the newest (partial) year for the year so far. */
export type Win = { slug: string; label: string; short: string; mw: string; growth: string; growthMw?: string; perYear: boolean; latest: "whole" | "newest" };

export const WINDOWS: Win[] = [
  { slug: "avg", label: "Whole year, average hour", short: "average demand", mw: "avg_demand_mw", growth: "avg_demand_growth_since_2019_pct", perYear: true, latest: "whole" },
  { slug: "peak", label: "Whole year, highest hour", short: "peak demand", mw: "peak_demand_mw", growth: "peak_demand_growth_since_2019_pct", perYear: true, latest: "whole" },
  { slug: "ytd", label: "The year so far, average hour", short: "average demand, the year so far", mw: "ytd_avg_demand_mw", growth: "ytd_avg_demand_growth_since_2019_pct", perYear: true, latest: "newest" },
  ...MONTH_NAMES.map((m, i): Win => ({ slug: `m${pad(i + 1)}`, label: `${m}, average hour`, short: `average demand in ${m}`, mw: `avg_demand_mw_m${pad(i + 1)}`, growth: `growth_pct_m${pad(i + 1)}`, growthMw: `growth_mw_m${pad(i + 1)}`, perYear: false, latest: "whole" })),
  ...Array.from({ length: 24 }, (_, h): Win => ({ slug: `h${pad(h)}`, label: `${pad(h)}:00 local, average over the year`, short: `average demand at ${pad(h)}:00 local`, mw: `avg_demand_mw_h${pad(h)}`, growth: `growth_pct_h${pad(h)}`, growthMw: `growth_mw_h${pad(h)}`, perYear: false, latest: "whole" })),
];
export const windowOf = (slug: string) => WINDOWS.find((w) => w.slug === slug);

/** The variables every view reads, for every area (a few hundred rows): the three whole-year windows, their growth,
 *  the year on the year before, and the hours used. A month or an hour of the day adds its own three. */
export const COMMON = [
  "avg_demand_mw", "peak_demand_mw", "ytd_avg_demand_mw",
  "avg_demand_growth_since_2019_pct", "peak_demand_growth_since_2019_pct", "ytd_avg_demand_growth_since_2019_pct", "avg_demand_growth_yoy_pct",
  "hours_used", "hours_in_year", "ytd_hours_used", "ytd_hours_in_window",
];
export function variablesOf(w: Win): string[] {
  return w.growthMw ? [...COMMON, w.mw, w.growth, w.growthMw] : COMMON;
}

/** The label timestamp of a year, as the table writes it: the first day of the year. */
export const yearTs = (y: number) => `${y}-01-01T00:00:00Z`;
export const yearOf = (ts: string) => new Date(ts).getUTCFullYear();

/** One row's value, by entity, variable and year. */
export function valueOf(rows: Row[], entity: string, variable: string, year: number): number | undefined {
  return rows.find((r) => r.entity === entity && r.variable === variable && yearOf(r.ts_utc) === year)?.value;
}
/** The years an area has a row of the variable for, in order. */
export function yearsOf(rows: Row[], entity: string, variable: string): number[] {
  return Array.from(new Set(rows.filter((r) => r.entity === entity && r.variable === variable).map((r) => yearOf(r.ts_utc)))).sort((a, b) => a - b);
}
/** The last whole year of an area: the newest with an annual average (the newest year is partial and has none). */
export const lastWhole = (rows: Row[], entity: string) => yearsOf(rows, entity, "avg_demand_mw").at(-1);
/** The newest year of an area: the newest with a year-to-date average. */
export const newest = (rows: Row[], entity: string) => yearsOf(rows, entity, "ytd_avg_demand_mw").at(-1);
/** The year a window's growth is read at, for an area. */
export const latestOf = (rows: Row[], entity: string, w: Win) => (w.latest === "newest" ? newest(rows, entity) : lastWhole(rows, entity));

/** The end of the year-to-date window, from the table's header ("year to date: 1 January to the end of MM/YYYY of each
 *  year"): { month, year }, or null when the header does not say. */
export function ytdThrough(header: string[]): { month: number; year: number } | null {
  for (const l of header) {
    const m = l.match(/year to date: 1 January to the end of (\d{2})\/(\d{4})/);
    if (m) return { month: Number(m[1]), year: Number(m[2]) };
  }
  return null;
}
export const monthName = (m: number) => MONTH_NAMES[m - 1];

/** The address of a view. */
export const viewHref = (grid: string, win: string) => `/explore/demand-growth?grid=${grid}&window=${win}`;
