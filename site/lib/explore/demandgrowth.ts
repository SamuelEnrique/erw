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
/** Session 7517 (chain 304, part B): the peak window also reads the newest year's highest hour so far and its growth
 *  on the highest hour of the same months of the base year (PJM's newest record was in the table and not on the page;
 *  no year is written by hand in this file, as session 404's test holds). No other window reads them. */
export const PEAK_SO_FAR = ["ytd_peak_demand_mw", "ytd_peak_demand_growth_since_2019_pct"];
export function variablesOf(w: Win): string[] {
  return w.growthMw ? [...COMMON, w.mw, w.growth, w.growthMw] : w.slug === "peak" ? [...COMMON, ...PEAK_SO_FAR] : COMMON;
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

// Ruling alternative 1 (session 7709, branch wip/alt-demand-growth-1; not a default on main): California's growth with
// and without the batteries' charging, a second row beside the table's own. The rule is the method note's
// (docs/methods/demand_growth.md, "California: the batteries' charging inside EIA's demand"; replication/demand_growth/
// california_charging.py): a month's charging is, on that month's average day by CAISO's own data (shoulder_hours_monthly,
// iso:caiso_own, avg_battery_mw_hHH), the sum of the hours below zero, sign turned, over 24; a window is the mean of its
// months weighted by their days; "less the charging" takes the charging off the newer year only (2019's is not held: the
// fleet was 186 MW at the end of 2019). CAISO's own data starts later than EIA's (its first month is the first month of the first window), so no whole year is given without it.
export const SHOULDER_TABLE = "shoulder_hours_monthly";
export const OWN_ENTITY = "iso:caiso_own";
export const CHARGING_VARIABLES = Array.from({ length: 24 }, (_, h) => `avg_battery_mw_h${pad(h)}`);
export const MONTH_VARIABLES = Array.from({ length: 12 }, (_, m) => `avg_demand_mw_m${pad(m + 1)}`);
export type Charging = { year: number; months: number[]; base: number; eia: number; charging: number; growthPct: number; lessChargingPct: number };
const daysIn = (y: number, m: number) => new Date(Date.UTC(y, m, 0)).getUTCDate();
/** One window of months of a year, or null when a month lacks EIA's demand, 2019's or a whole day of charging. */
export function chargingWindow(eia: Row[], own: Row[], year: number, months: number[]): Charging | null {
  const e = entityOf("CISO");
  let days = 0, sumE = 0, sumB = 0, sumC = 0;
  for (const m of months) {
    const ts = `${year}-${pad(m)}`;
    const hours = CHARGING_VARIABLES.map((v) => own.find((r) => r.entity === OWN_ENTITY && r.variable === v && r.ts_utc.slice(0, 7) === ts)?.value);
    const ev = valueOf(eia, e, `avg_demand_mw_m${pad(m)}`, year), bv = valueOf(eia, e, `avg_demand_mw_m${pad(m)}`, BASE);
    if (ev === undefined || bv === undefined || hours.some((x) => x === undefined)) return null;
    const d = daysIn(year, m);
    days += d; sumE += ev * d; sumB += bv * d; sumC += (-(hours as number[]).filter((x) => x < 0).reduce((a, x) => a + x, 0) / 24) * d;
  }
  if (!days) return null;
  const base = sumB / days, eiaMw = sumE / days, charging = sumC / days;
  return { year, months, base, eia: eiaMw, charging, growthPct: 100 * (eiaMw / base - 1), lessChargingPct: 100 * ((eiaMw - charging) / base - 1) };
}
/** The windows the page gives: the last whole year's months CAISO's own data holds, and the newest year's months both hold. */
export function chargingWindows(eia: Row[], own: Row[]): Charging[] {
  const e = entityOf("CISO"), out: Charging[] = [];
  const held = (y: number, m: number) => chargingWindow(eia, own, y, [m]) !== null;
  // the two newest years with a month of EIA's demand (the page reads the twelve months' rows alone, not the year's)
  const ys = Array.from(new Set(MONTH_VARIABLES.flatMap((v) => yearsOf(eia, e, v)))).filter((y) => y !== BASE).sort((a, b) => a - b).slice(-2);
  for (const y of ys) {
    const months = Array.from({ length: 12 }, (_, i) => i + 1).filter((m) => held(y, m));
    // one run of months, from the first held to the last held with none missing between
    const run: number[] = [];
    for (const m of months) { if (run.length && m !== run[run.length - 1] + 1) break; run.push(m); }
    const w = run.length ? chargingWindow(eia, own, y, run) : null;
    if (w && !out.some((o) => o.year === y)) out.push(w);
  }
  return out;
}

/** The address of a view. */
export const viewHref = (grid: string, win: string) => `/explore/demand-growth?grid=${grid}&window=${win}`;
