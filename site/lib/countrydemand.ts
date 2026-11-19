// Energy Research Warehouse (ERW) site, session 8420 (chain 503, part C): /demand for the whole country. The types of
// the data machine's page files of demand (docs/state/page_files_regions.md, sections 2 and 3: `index.json`,
// `demand/<region>.json`, `demand/ba/<code>.json`), their reader, the place an address names, and the few sums the
// view computes from a file's daily series. A file's `growth` object is the area object of data/demand_growth.json and
// its `weather` object the grid object of data/demand_weather.json, so the page's own functions (lib/demandgrowth.ts,
// lib/demandweather.ts) and charts (components/demand/Growth.tsx, Weather.tsx) read them: nothing here is a second
// version of those. Sums and means of what a file holds; nothing filled, interpolated or scaled.
import { GRID_NAME, NEW_REGIONS, REGION_CODES, REGION_GRIDS, REGION_NAME, readRegionFile, type Arr } from "./countryfiles";
import type { Area, Period, Year } from "./demandgrowth";
import type { Grid } from "./demandweather";

/** One region of `index.json`. */
export type IndexRegion = { code: string; name: string; tz?: string; bas?: string[]; grids?: string[]; first_hour?: string; last_hour?: string };
/** One balancing authority of `index.json`. */
export type IndexBa = {
  code: string; name: string; region?: string; tz?: string; grid?: string | null; region_grids?: string[]; generation_only?: boolean; active?: boolean;
  retired?: string | null; first_hour?: string; last_hour?: string; files?: string[];
};
/** `site/data/regions/index.json` (the contract's section 2). */
export type IndexFile = { built?: string; tables?: string[]; method?: string; license?: string; fixture?: string; regions: IndexRegion[]; bas: IndexBa[] };

/** A file's daily series: one position a local day. */
export type Daily = { days: string[]; demand_mwh?: Arr; peak_mw?: Arr; peak_at?: (string | null)[]; hours?: (number | null)[] };
/** A file's `growth`: the three lines of data/demand_growth.json the page reads, and one area's year rows. */
export type Growth = Period & { years: Record<string, Year>; at?: Record<string, Record<string, string>> };
/** A region's `weather`: one grid object of data/demand_weather.json. `train` (the fit's years) is read when the file
 *  gives it; the keys of `holdout` are those years otherwise. */
export type PlaceWeather = Grid & { weather_table?: string; train?: number[] };
/** A region that covers nearly the ground of one of the seven grids: both averages by year, and why they differ. */
export type Alike = { grid: string; years: Record<string, { region_avg_demand_mw?: number; grid_avg_demand_mw?: number; difference_pct?: number }>; why?: string };
/** `site/data/regions/demand/<region>.json` and `demand/ba/<code>.json` (the contract's section 3). */
export type DemandPlaceFile = {
  built?: string; tables?: string[]; method?: string; license?: string; fixture?: string;
  code: string; name: string; tz: string; level: "region" | "ba"; basis?: string; bas_summed?: string[];
  screened?: { blank: number; not_positive: number; jumps: number };
  daily?: Daily; growth?: Growth; weather?: PlaceWeather; alike?: Alike;
};

/** A place the view can draw: one of EIA's thirteen regions, or a balancing authority by its EIA-930 code. */
export type Place = { level: "region" | "ba"; code: string };
/** The places drawn when the address names none: Tennessee and the Carolinas. The session's own default (8420). */
export const FIRST_A: Place = { level: "region", code: "TEN" };
export const FIRST_B: Place = { level: "region", code: "CAR" };
export const FIRST_WHY = "Tennessee and the Carolinas are drawn first: two of the six regions no page of the site drew before, and the two the page of Winter Storm Elliott draws first. This page's own choice (session 8420); no publisher's default stands behind it. Any region or balancing authority can take either place.";

/** How a place is written in the address: a region by its code ("ten"), a balancing authority as "ba-tva". */
export const placeKey = (p: Place) => (p.level === "ba" ? `ba-${p.code.toLowerCase()}` : p.code.toLowerCase());
export const samePlace = (x: Place | null, y: Place | null) => !!x && !!y && x.level === y.level && x.code === y.code;
/** The place an address value names, or null. Letters and digits only (the value becomes a file name). A bare code is a
 *  region when it is one of the thirteen and a balancing authority otherwise; with the index held, a balancing
 *  authority EIA does not list is no place. */
export function placeOf(v: string | undefined, index: IndexFile | null): Place | null {
  const m = /^(ba-)?([a-z0-9]{2,8})$/.exec((v ?? "").trim().toLowerCase());
  if (!m) return null;
  const code = m[2].toUpperCase();
  if (!m[1] && (REGION_CODES as readonly string[]).includes(code)) return { level: "region", code };
  if (index && !index.bas?.some((b) => b.code === code)) return null;
  return { level: "ba", code };
}
/** The file of a place, under site/data/regions/. */
export const placeFilePath = (p: Place) => (p.level === "ba" ? `demand/ba/${p.code.toLowerCase()}.json` : `demand/${p.code.toLowerCase()}.json`);
export const demandPlaceFile = (p: Place) => readRegionFile<DemandPlaceFile>(placeFilePath(p));
export const regionsIndex = () => readRegionFile<IndexFile>("index.json");

/** The address of the view with its choices. */
export function countryHref(c: { a?: Place | null; b?: Place | null | "none"; days?: string; figure?: string; year?: string }, hash = ""): string {
  const parts = ["view=country"];
  if (c.a) parts.push(`a=${placeKey(c.a)}`);
  if (c.b) parts.push(`b=${c.b === "none" ? "none" : placeKey(c.b)}`);
  if (c.days && c.days !== "all") parts.push(`days=${c.days}`);
  if (c.figure) parts.push(`figure=${c.figure}`);
  if (c.year) parts.push(`year=${c.year}`);
  return `/demand?${parts.join("&")}${hash ? `#${hash}` : ""}`;
}

export const baOf = (index: IndexFile | null, code: string) => index?.bas?.find((b) => b.code === code) ?? null;
export const regionOfIndex = (index: IndexFile | null, code: string) => index?.regions?.find((r) => r.code === code) ?? null;
/** A place's name: the file's, else the index's, else EIA's name of a region, else the code. */
export function placeName(p: Place, index: IndexFile | null, file?: DemandPlaceFile | null): string {
  if (file?.name) return file.name;
  if (p.level === "region") return regionOfIndex(index, p.code)?.name ?? REGION_NAME[p.code] ?? p.code;
  return baOf(index, p.code)?.name ?? p.code;
}
/** The thirteen regions in EIA's order, from the index where it is held and from the contract's names otherwise. */
export function regionRows(index: IndexFile | null): IndexRegion[] {
  return (REGION_CODES as readonly string[]).map((code) => regionOfIndex(index, code) ?? { code, name: REGION_NAME[code], grids: REGION_GRIDS[code] });
}
export const isNewRegion = (code: string) => NEW_REGIONS.includes(code);
export const gridWords = (codes: string[] | undefined) => (codes ?? []).map((g) => GRID_NAME[g] ?? g);

/** The area object the page's functions read, from a file's `growth` (null when the file holds none). */
export function areaOf(f: DemandPlaceFile): Area | null {
  if (!f.growth?.years) return null;
  return { name: f.name, tz: f.tz, years: f.growth.years, at: f.growth.at ?? {}, screened: f.screened ?? { blank: 0, not_positive: 0, jumps: 0 } };
}
export const periodOf = (g: Growth): Period => ({ base: g.base, last_year: g.last_year, ytd_through: g.ytd_through });

const num = (v: number | null | undefined): v is number => typeof v === "number" && Number.isFinite(v);
/** The years the daily series holds a day of, in order. */
export const dailyYears = (d: Daily | undefined): string[] => [...new Set((d?.days ?? []).map((x) => x.slice(0, 4)))].sort();
/** The positions of the days drawn: every day, or the days of one year. */
function drawn(d: Daily, days: string): number[] {
  const out: number[] = [];
  d.days.forEach((x, i) => { if (days === "all" || x.startsWith(`${days}-`)) out.push(i); });
  return out;
}
export type DailySummary = {
  days: number; held: number; first: string; last: string; mwh: number;
  topDay: { day: string; mwh: number } | null; lowDay: { day: string; mwh: number } | null; topHour: { day: string; mw: number; at: string | null } | null;
};
/** The days drawn in a few figures: how many, how many hold a whole day's demand, the first and the last, the sum of the
 *  held days' demand, the day of most and of least demand among the held, and the highest hour. Null with no day. */
export function dailySummary(d: Daily | undefined, days = "all"): DailySummary | null {
  if (!d?.days?.length) return null;
  const at = drawn(d, days);
  if (!at.length) return null;
  let held = 0, mwh = 0, top = -1, low = -1, hour = -1;
  for (const i of at) {
    const e = d.demand_mwh?.[i], p = d.peak_mw?.[i];
    if (num(e)) {
      held++; mwh += e;
      if (top < 0 || e > (d.demand_mwh![top] as number)) top = i;
      if (low < 0 || e < (d.demand_mwh![low] as number)) low = i;
    }
    if (num(p) && (hour < 0 || p > (d.peak_mw![hour] as number))) hour = i;
  }
  return {
    days: at.length, held, first: d.days[at[0]], last: d.days[at[at.length - 1]], mwh,
    topDay: top < 0 ? null : { day: d.days[top], mwh: d.demand_mwh![top] as number },
    lowDay: low < 0 ? null : { day: d.days[low], mwh: d.demand_mwh![low] as number },
    topHour: hour < 0 ? null : { day: d.days[hour], mw: d.peak_mw![hour] as number, at: d.peak_at?.[hour] ?? null },
  };
}
/** The time of a local day on a chart's axis: its date at 00:00 UTC, in milliseconds (the axis writes the date). */
export const dayMs = (day: string) => Date.parse(`${day}T00:00:00Z`);
/** A chart's points from the daily series: the day's highest hour, or its average (the day's MWh over the hours used,
 *  only where the file holds both). A day the file does not hold is a break in the line, never a filled point. */
export function dailyPoints(d: Daily | undefined, what: "peak" | "average", days = "all"): [number, number | null][] {
  if (!d?.days?.length) return [];
  return drawn(d, days).map((i): [number, number | null] => {
    if (what === "peak") { const p = d.peak_mw?.[i]; return [dayMs(d.days[i]), num(p) ? p : null]; }
    const e = d.demand_mwh?.[i], h = d.hours?.[i];
    return [dayMs(d.days[i]), num(e) && num(h) && h > 0 ? e / h : null];
  });
}
export type DayRow = { day: string; mwh: number | null; peak_mw: number | null; peak_at: string | null; hours: number | null };
/** The newest `n` days of the series, newest first, as the file holds them. */
export function newestDays(d: Daily | undefined, n: number): DayRow[] {
  if (!d?.days?.length) return [];
  const out: DayRow[] = [];
  for (let i = d.days.length - 1; i >= 0 && out.length < n; i--) {
    const e = d.demand_mwh?.[i], p = d.peak_mw?.[i], h = d.hours?.[i];
    out.push({ day: d.days[i], mwh: num(e) ? e : null, peak_mw: num(p) ? p : null, peak_at: d.peak_at?.[i] ?? null, hours: num(h) ? h : null });
  }
  return out;
}
/** How many of the newest days the view lists. The session's own choice (8420): a week. */
export const NEWEST_DAYS = 7;

/** The years a region's weather fit was made on: the file's `train`, else the years its `holdout` is keyed by. */
export function trainOf(w: PlaceWeather | undefined): number[] {
  if (!w) return [];
  if (Array.isArray(w.train) && w.train.length) return [...w.train].sort((x, y) => x - y);
  return Object.keys(w.holdout ?? {}).map(Number).filter(Number.isFinite).sort((x, y) => x - y);
}
/** A stand-in grid object for a place that holds no weather view, so the page's chart draws its row as "not held". */
export const noWeather = (name: string, tz: string): Grid => ({ name, tz, fit: {} as Grid["fit"], through: "", newest: Number.NEGATIVE_INFINITY, years: {}, holdout: {} });

/** The years of an alike object, in order, each with the two averages and the file's difference. */
export function alikeRows(a: Alike | undefined): { year: string; region: number | null; grid: number | null; pct: number | null }[] {
  return Object.keys(a?.years ?? {}).sort().map((year) => {
    const r = a!.years[year] ?? {};
    return { year, region: num(r.region_avg_demand_mw) ? r.region_avg_demand_mw : null, grid: num(r.grid_avg_demand_mw) ? r.grid_avg_demand_mw : null, pct: num(r.difference_pct) ? r.difference_pct : null };
  });
}

/** A local day in words: "1 August 2025". */
export const dayWords = (day: string) => new Date(`${day}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
/** "2026-11-17 05:00 UTC" from a file's hour. */
export const utcHourWords = (ts: string) => `${ts.slice(0, 10)} ${ts.slice(11, 16)} UTC`;
