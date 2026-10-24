// Energy Research Warehouse (ERW) site, session 1403 (chain 100): the cleanest hours, live. The Clean tab's "the
// cleanest hours of the average day" (components/mix/views.tsx CleanView) is drawn from a committed build of
// clean_energy_summary (site/data/clean/<grid>.json, the carbon-free share by local hour, by month); beside it the panel
// grid_cleanweek_<grid> (components/grid/CleanWeekPanel.tsx) draws the newest 7 days of carbon_intensity_hourly for the
// grid in view in the same shape: the hour of day across, the day down. Pure functions, no import, so a node test and
// scripts/check-values.mjs load this file as it is (scripts/test-clean-week.mjs).
//
// The variable: intensity_generation, kg CO2 per MWh of the grid's own net generation. The committed view is a share of
// the grid's own generation (docs/methods/clean_energy.md, "Generation inside the grid, not imports"), so the live week
// is the intensity of the same generation, not intensity_demand (which counts imports and takes exports out). Lower is
// cleaner here; on the committed view higher is cleaner. The two are compared by their hours only, in words.
// The hours: local clock time in the grid's time zone, as the committed view's are (warehouse/derived/mix_profile.py
// GRIDS tz, written into each committed file as `tz`): a day of 23 or 25 hours on the days the clocks change.
// The window: the 7 local days that end with the newest local day whose hours are all held (23, 24 or 25), read from
// the grid's rows of the last 12 days. An hour not held is a blank cell; nothing is filled.
// The figures written on the page, each a key scripts/check-values.mjs recomputes with weekStat on the table's rows:
//   series_n|<table>|<variable>|<start>|<end>|<entity>      the hours of the window held (session 1154's kind)
//   series_min|<table>|<variable>|<start>|<end>|<entity>    the lowest hour of the window, the week's cleanest
//   series_max|<table>|<variable>|<start>|<end>|<entity>    the highest hour, the week's dirtiest (session 29's kind)
//   series_mean|<table>|<variable>|<start>|<end>|<entity>   the mean of the hours held (each hour once)
// The cells drawn and named on hover are the rows' own values, not written figures.

export const CARBON_TABLE = "carbon_intensity_hourly";
export const CLEAN_VARIABLE = "intensity_generation";
export const UNIT = "kg CO2/MWh";
/** The rows read: the grid's last 12 days, enough for 7 whole local days behind EIA's lag of three days or more. */
export const READ_DAYS = 12;
const H = 3_600_000;
/** Each ISO grid's balancing authority in the table (docs/grids/grids.json `entity`). */
export const CARBON_ENTITY: Record<string, string> = { caiso: "eia930:CISO", ercot: "eia930:ERCO", isone: "eia930:ISNE", miso: "eia930:MISO", nyiso: "eia930:NYIS", pjm: "eia930:PJM", spp: "eia930:SWPP" };

export type CarbonRow = { ts_utc: string; value: number; entity?: string; variable?: string };
export type Fig = { check: string; raw: number; tip: string };

export const isoZ = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
export const utcName = (t: number) => `${new Date(t).toISOString().slice(0, 13).replace("T", " ")}:00 UTC`;

/** Each hour of [start, end) held, its value; an hour written twice is held once (its last row); in time order. */
export function hourValues(rows: CarbonRow[], start = -Infinity, end = Infinity): [number, number][] {
  const by = new Map<number, number>();
  for (const r of rows) {
    const t = Date.parse(r.ts_utc);
    if (!Number.isFinite(t) || t < start || t >= end || t % H || typeof r.value !== "number" || !Number.isFinite(r.value)) continue;
    by.set(t, r.value);
  }
  return [...by.entries()].sort((a, b) => a[0] - b[0]);
}

/** A key's value, as check-values recomputes it: over the hours of [start, end) held, "n" the count, "min" the lowest,
 *  "max" the highest, "mean" their mean; undefined for the last three when no hour is held. */
export function weekStat(rows: CarbonRow[], stat: string, start: string, end: string): number | undefined {
  const hs = hourValues(rows, Date.parse(start), Date.parse(end)).map(([, v]) => v);
  if (stat === "n") return hs.length;
  if (!hs.length) return undefined;
  if (stat === "min") return Math.min(...hs);
  if (stat === "max") return Math.max(...hs);
  if (stat === "mean") return hs.reduce((a, v) => a + v, 0) / hs.length;
  throw new Error(`unknown statistic ${stat}`);
}

const fmts = new Map<string, Intl.DateTimeFormat>();
function fmt(tz: string): Intl.DateTimeFormat {
  let f = fmts.get(tz);
  if (!f) {
    f = new Intl.DateTimeFormat("en-US", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", hourCycle: "h23", timeZoneName: "short" });
    fmts.set(tz, f);
  }
  return f;
}
/** The local day (YYYY-MM-DD), hour (0 to 23) and zone's short name ("CDT") of an instant in a time zone. */
export function localOf(t: number, tz: string): { day: string; hour: number; zone: string } {
  const p = Object.fromEntries(fmt(tz).formatToParts(new Date(t)).map((x) => [x.type, x.value]));
  return { day: `${p.year}-${p.month}-${p.day}`, hour: Number(p.hour) % 24, zone: p.timeZoneName ?? tz };
}
/** The first hour (UTC) of a local day: the US zones' offsets are whole hours, so the hours are searched in turn. */
export function dayStart(day: string, tz: string): number {
  const g = Date.parse(`${day}T00:00:00Z`);
  for (let t = g - 2 * H; t <= g + 16 * H; t += H) if (localOf(t, tz).day === day) return t;
  throw new Error(`no hour of ${day} in ${tz}`);
}
const nextDay = (day: string) => new Date(Date.parse(`${day}T12:00:00Z`) + 24 * H).toISOString().slice(0, 10);
const prevDay = (day: string, n = 1) => new Date(Date.parse(`${day}T12:00:00Z`) - n * 24 * H).toISOString().slice(0, 10);

/** The 7 local days that end with the newest local day whose hours are all held; null when no day is whole. */
export function weekWindow(rows: CarbonRow[], tz: string): { t0: number; t1: number; days: string[] } | null {
  const n = new Map<string, number>();
  for (const [t] of hourValues(rows)) { const d = localOf(t, tz).day; n.set(d, (n.get(d) ?? 0) + 1); }
  const whole = [...n.entries()].filter(([d, k]) => k === (dayStart(nextDay(d), tz) - dayStart(d, tz)) / H).map(([d]) => d).sort();
  if (!whole.length) return null;
  const last = whole[whole.length - 1];
  const days = Array.from({ length: 7 }, (_, i) => prevDay(last, 6 - i));
  return { t0: dayStart(days[0], tz), t1: dayStart(nextDay(last), tz), days };
}

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
/** A local day as a row's label: "Tue 20 Oct". */
export const dayLabel = (day: string) => { const d = new Date(`${day}T12:00:00Z`); return `${DOW[d.getUTCDay()]} ${d.getUTCDate()} ${MON[d.getUTCMonth()]}`; };
const hh = (h: number) => `${String(h).padStart(2, "0")}:00`;
/** An hour as a reader says it: its local day and hour with the zone, and the UTC hour. */
export function hourWords(t: number, tz: string): string {
  const l = localOf(t, tz);
  return `${dayLabel(l.day)}, ${hh(l.hour)} ${l.zone} (${utcName(t)})`;
}
const kg = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

export type CleanWeek = {
  entity: string;
  tz: string;
  t0: number;
  t1: number;
  /** the local days, oldest first (the rows) */
  days: string[];
  /** [day][local hour]: the hour's intensity, or null where not held (or no such hour) */
  cells: (number | null)[][];
  /** [day][local hour]: the hover's words, the hour, the day and the kg per MWh */
  tips: string[][];
  /** the hours in the window (167, 168 or 169 across a clock change) */
  of: number;
  n: Fig;
  min: { t: number; local: number; at: [number, number]; fig: Fig } | null;
  max: { t: number; local: number; at: [number, number]; fig: Fig } | null;
  mean: Fig | null;
};

/** The week's cells, hover words and keyed figures for one balancing authority's rows, in its time zone. */
export function cleanWeek(rows: CarbonRow[], entity: string, tz: string): CleanWeek | null {
  const mine = rows.filter((r) => (r.entity === undefined || r.entity === entity) && (r.variable === undefined || r.variable === CLEAN_VARIABLE));
  const w = weekWindow(mine, tz);
  if (!w) return null;
  const { t0, t1, days } = w;
  const hs = hourValues(mine, t0, t1);
  const at = new Map(hs);
  const cells: (number | null)[][] = days.map(() => Array(24).fill(null));
  const tips: string[][] = days.map((d) => Array.from({ length: 24 }, (_, h) => `${dayLabel(d)}, ${hh(h)}: no such hour (the clocks went forward)`));
  const place = new Map<number, [number, number]>();
  for (let t = t0; t < t1; t += H) {
    const l = localOf(t, tz), r = days.indexOf(l.day), v = at.get(t);
    if (r < 0) continue;
    const words = `${dayLabel(l.day)}, ${hh(l.hour)} ${l.zone} (${utcName(t)}): ${v === undefined ? "not held" : `${kg(v)} ${UNIT}`}`;
    if (place.has(t)) continue;
    const seen = [...place.values()].some(([a, b]) => a === r && b === l.hour);
    if (seen) { tips[r][l.hour] += `; then ${words}`; continue; }   // the hour the clocks went back repeats: the first is drawn
    place.set(t, [r, l.hour]);
    cells[r][l.hour] = v ?? null;
    tips[r][l.hour] = words;
  }
  const key = (kind: string) => `${kind}|${CARBON_TABLE}|${CLEAN_VARIABLE}|${isoZ(t0)}|${isoZ(t1)}|${entity}`;
  const span = `${utcName(t0)} to ${utcName(t1)} (${dayLabel(days[0])} to ${dayLabel(days[6])}, ${tz})`;
  const src = `${CARBON_TABLE}, ${entity}, ${CLEAN_VARIABLE}`;
  const of = Math.round((t1 - t0) / H);
  const n: Fig = { check: key("series_n"), raw: hs.length, tip: `${src}: the hours held from ${span}` };
  if (!hs.length) return { entity, tz, t0, t1, days, cells, tips, of, n, min: null, max: null, mean: null };
  const lo = hs.reduce((a, h) => (h[1] < a[1] ? h : a));   // the first on a tie
  const hi = hs.reduce((a, h) => (h[1] > a[1] ? h : a));
  const pos = (t: number) => place.get(t) ?? [days.indexOf(localOf(t, tz).day), localOf(t, tz).hour] as [number, number];
  return {
    entity, tz, t0, t1, days, cells, tips, of, n,
    min: { t: lo[0], local: localOf(lo[0], tz).hour, at: pos(lo[0]), fig: { check: key("series_min"), raw: lo[1], tip: `${src}: the lowest hour from ${span}, the hour from ${hourWords(lo[0], tz)}: ${UNIT}` } },
    max: { t: hi[0], local: localOf(hi[0], tz).hour, at: pos(hi[0]), fig: { check: key("series_max"), raw: hi[1], tip: `${src}: the highest hour from ${span}, the hour from ${hourWords(hi[0], tz)}: ${UNIT}` } },
    mean: { check: key("series_mean"), raw: weekStat(mine, "mean", isoZ(t0), isoZ(t1))!, tip: `${src}: the mean of the ${hs.length} hours held from ${span}, each hour once: ${UNIT}` },
  };
}

/** The committed month the week is set against: the week's local month (of its last day) in the year the committed view
 *  shows when that year holds it, else in the newest year that does; null when no year holds that month. */
export function refMonth(months: string[], lastDay: string, year: string | null): string | null {
  const mm = lastDay.slice(5, 7);
  if (year && months.includes(`${year}-${mm}`)) return `${year}-${mm}`;
  const same = months.filter((m) => m.slice(5, 7) === mm).sort();
  return same.length ? same[same.length - 1] : null;
}

/** The committed average day's dirtiest local hour (the lowest carbon-free share; the first on a tie), or null. */
export function dirtiestOf(day: (number | null)[]): number | null {
  let best: number | null = null;
  day.forEach((v, h) => { if (v !== null && (best === null || v < (day[best] as number))) best = h; });
  return best;
}

/** The line that sets the week against the committed average day of a month, in words: hours only, no new number. */
export function compareWords(week: CleanWeek, ref: { month: string; cleanest: number[]; dirtiest: number | null; hoursName: string }): string {
  const name = new Date(`${ref.month}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
  if (!week.min || !week.max) return `No hour of the week is held, so it is not set against ${name}'s average day.`;
  const c = ref.cleanest.includes(week.min.local)
    ? `the week's cleanest hour, ${hh(week.min.local)}, is one of ${name}'s four cleanest hours of the average day (${ref.hoursName})`
    : `the week's cleanest hour, ${hh(week.min.local)}, is not one of ${name}'s four cleanest hours of the average day (${ref.hoursName})`;
  const d = ref.dirtiest === null ? `${name}'s average day holds no dirtiest hour`
    : ref.dirtiest === week.max.local ? `its dirtiest hour, ${hh(week.max.local)}, is ${name}'s dirtiest hour of the average day too`
    : `its dirtiest hour, ${hh(week.max.local)}, is not ${name}'s dirtiest hour of the average day (${hh(ref.dirtiest)})`;
  return `Against the committed average day of ${name}: ${c}; ${d}.`;
}
