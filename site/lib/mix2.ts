// Session 94: the energy mix, version 2 (/mix/v2, in review). The pure part: what the page chooses from its address and
// how it reads the site's own copy of generation_mix_hourly_profile and generation_mix_records (data/mix/<grid>.json,
// written by warehouse/derived/mix_profile.py; docs/methods/generation_mix_hourly.md). The numbers are the table's; the
// only arithmetic here is net load (demand less wind and solar, hour by hour) and what is read off it.
export const PROFILE = "generation_mix_hourly_profile";
export const RECORDS = "generation_mix_records";

export type Avg = Record<string, (number | null)[]>;
export type Period = { avg: Avg; side: string; days_held: number; months?: number; months_due?: number; missing?: string[]; days_in_month?: number } & Record<string, unknown>;
export type Rec = { variable: string; ts_utc: string; value: number; unit: string; period: string; side: string };
export type GridFile = {
  grid: string; name: string; tz: string; built: string; join: string | null; first: string; upto: string; sources: string[];
  months: Record<string, Period>; years: Record<string, Period>; records: Rec[];
};

/** The sources, in the order the stack is drawn (from the bottom), each with its token color. */
export const SOURCES = [
  { key: "nuclear", label: "Nuclear", color: "var(--color-fuel-nuclear)" },
  { key: "coal", label: "Coal", color: "var(--color-fuel-coal)" },
  { key: "natural_gas", label: "Natural gas", color: "var(--color-fuel-gas)" },
  { key: "hydro", label: "Hydro", color: "var(--color-fuel-hydro)" },
  { key: "other", label: "Other", color: "var(--color-fuel-other)" },
  { key: "wind", label: "Wind", color: "var(--color-fuel-wind)" },
  { key: "solar", label: "Solar", color: "var(--color-fuel-solar)" },
  { key: "storage", label: "Storage", color: "var(--color-fuel-storage)" },
] as const;
export const sourceOf = (key: string) => SOURCES.find((s) => s.key === key);

export const GRIDS = [
  { slug: "ercot", name: "ERCOT", place: "Texas (ERCOT)" },
  { slug: "caiso", name: "CAISO", place: "California (CAISO)" },
  { slug: "pjm", name: "PJM", place: "PJM" },
  { slug: "miso", name: "MISO", place: "MISO" },
  { slug: "spp", name: "SPP", place: "SPP" },
  { slug: "nyiso", name: "NYISO", place: "New York (NYISO)" },
  { slug: "isone", name: "ISO-NE", place: "New England (ISO-NE)" },
] as const;
export type GridSlug = (typeof GRIDS)[number]["slug"];
export type Files = Record<string, GridFile>;

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const calName = (cal: string) => MONTHS[Number(cal) - 1];
/** "April 2026" for a month, "2025" for a year. */
export const periodName = (p: string) => (p.length === 7 ? `${calName(p.slice(5))} ${p.slice(0, 4)}` : p);
export const hourName = (h: number) => `${String(h).padStart(2, "0")}:00`;
/** A number as the site writes it: MW and MWh whole, with separators. */
export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
/** A share or an intensity as the table holds it, to two decimals. */
export const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** What a period of a grid is: a month held, a year held, or nothing. */
export function periodOf(file: GridFile | undefined, p: string | undefined): Period | null {
  if (!file || !p) return null;
  return (p.length === 7 ? file.months[p] : file.years[p]) ?? null;
}

export type Choice = { grid: GridSlug; vs: GridSlug | null; period: string; cal: string };
/** The page's choices from its address. An unknown grid is the first; an unknown or unheld period is the grid's latest
 *  month; the second grid is dropped when it is the first; the calendar month for the view across years is the
 *  period's own, or April for a year (where the midday dip is deepest). */
export function choices(q: Record<string, string | undefined>, files: Files): Choice {
  const grid = (GRIDS.find((g) => g.slug === q.grid) ?? GRIDS[0]).slug;
  const other = GRIDS.find((g) => g.slug === q.vs)?.slug ?? null;
  const vs = other && other !== grid ? other : null;
  const file = files[grid];
  const latest = Object.keys(file?.months ?? {}).sort().at(-1) ?? "";
  const period = q.period && periodOf(file, q.period) ? q.period : latest;
  const cal = q.cal && /^(0[1-9]|1[0-2])$/.test(q.cal) ? q.cal : period.length === 7 ? period.slice(5) : "04";
  return { grid, vs, period, cal };
}

/** The address of a view: only what differs from the page as it opens is written. */
export function href(c: Partial<Choice> & { grid: string }): string {
  const q = new URLSearchParams();
  q.set("grid", c.grid);
  if (c.period) q.set("period", c.period);
  if (c.vs) q.set("vs", c.vs);
  if (c.cal) q.set("cal", c.cal);
  return `/mix/v2?${q.toString()}`;
}

/** The months a grid does not hold, from its first month to the table's last. */
export function missingMonths(file: GridFile): string[] {
  const out: string[] = [];
  let [y, m] = file.first.split("-").map(Number);
  for (;;) {
    const k = `${y}-${String(m).padStart(2, "0")}`;
    if (k > file.upto) break;
    if (!file.months[k]) out.push(k);
    if (++m > 12) { m = 1; y++; }
  }
  return out;
}

/** The sources a period holds anything of (a source that is zero in every hour is left out of the stack and the legend). */
export function sourcesIn(p: Period): (typeof SOURCES)[number][] {
  return SOURCES.filter((s) => (p.avg[s.key] ?? []).some((v) => v !== null && v !== 0));
}

export type Band = { key: string; label: string; color: string; upper: number[]; lower: number[] };
/** The stack of an average day: for each source its band by hour. What is above zero is stacked up from zero, what is
 *  below zero (batteries charging) down from zero, so a charging hour is not hidden inside the stack. */
export function stack(p: Period): { up: Band[]; down: Band[]; hi: number; lo: number } {
  const up: Band[] = [], down: Band[] = [];
  const top = Array(24).fill(0) as number[], bottom = Array(24).fill(0) as number[];
  for (const s of sourcesIn(p)) {
    const v = (p.avg[s.key] ?? []).map((x) => x ?? 0);
    if (v.some((x) => x > 0)) {
      const lower = [...top];
      v.forEach((x, h) => { top[h] += Math.max(0, x); });
      up.push({ key: s.key, label: s.label, color: s.color, lower, upper: [...top] });
    }
    if (v.some((x) => x < 0)) {
      const upper = [...bottom];
      v.forEach((x, h) => { bottom[h] += Math.min(0, x); });
      down.push({ key: s.key, label: s.label, color: s.color, upper, lower: [...bottom] });
    }
  }
  return { up, down, hi: Math.max(...top), lo: Math.min(...bottom) };
}

/** Net load by hour: demand less wind and solar; null where any of the three is not held. */
export function netLoad(p: Period): (number | null)[] {
  const d = p.avg.demand ?? [], w = p.avg.wind ?? [], s = p.avg.solar ?? [];
  return Array.from({ length: 24 }, (_, h) => (d[h] == null || w[h] == null || s[h] == null ? null : Math.round((d[h]! - w[h]! - s[h]!) * 10) / 10));
}

export type Point = { hour: number; value: number };
const best = (v: (number | null)[], from: number, to: number, pick: (a: number, b: number) => boolean): Point | null => {
  let out: Point | null = null;
  for (let h = from; h <= to; h++) {
    const x = v[h];
    if (x != null && (out === null || pick(x, out.value))) out = { hour: h, value: x };
  }
  return out;
};
export const highest = (v: (number | null)[], from = 0, to = 23) => best(v, from, to, (a, b) => a > b);
export const lowest = (v: (number | null)[], from = 0, to = 23) => best(v, from, to, (a, b) => a < b);

export type DuckYear = { year: string; month: string; side: string; days: number; net: (number | null)[]; solar: (number | null)[]; solarPeak: Point | null; low: Point | null; evening: Point | null; ramp: number | null };
/** One calendar month across the years: each year's net load and solar by hour, the midday low of net load (09:00 to
 *  16:00), its evening high (from 16:00) and the ramp between them, when the low comes first. */
export function acrossYears(file: GridFile, cal: string): DuckYear[] {
  return Object.keys(file.months).filter((m) => m.slice(5) === cal).sort().map((m) => {
    const p = file.months[m];
    const net = netLoad(p), solar = p.avg.solar ?? [];
    const low = lowest(net, 9, 16), evening = highest(net, 16, 23);
    return { year: m.slice(0, 4), month: m, side: p.side, days: p.days_held, net, solar, solarPeak: highest(solar), low, evening,
      ramp: low && evening ? Math.round((evening.value - low.value) * 10) / 10 : null };
  });
}

/** The largest source of a period by its share, and the shares in the table's order of size. */
export function shares(p: Period): { key: string; label: string; color: string; share: number; mwh: number }[] {
  return SOURCES.map((s) => ({ key: s.key, label: s.label, color: s.color, share: Number(p[`${s.key}_share_pct`] ?? 0), mwh: Number(p[`${s.key}_mwh`] ?? 0) }))
    .sort((a, b) => b.share - a.share);
}

export const RECORD_ROWS = [
  { variable: "solar_share_max_pct", label: "Highest solar share of an hour", unit: "percent of generation" },
  { variable: "wind_share_max_pct", label: "Highest wind share of an hour", unit: "percent of generation" },
  { variable: "wind_solar_share_max_pct", label: "Highest wind and solar share of an hour", unit: "percent of generation" },
  { variable: "cleanest_hour_kgco2_per_mwh", label: "Cleanest hour", unit: "kg CO2 per MWh" },
  { variable: "dirtiest_hour_kgco2_per_mwh", label: "Dirtiest hour", unit: "kg CO2 per MWh" },
] as const;
/** A grid's record: for the whole history (period "all") or for a local year. */
export function recordOf(file: GridFile, variable: string, period: string): Rec | undefined {
  const name = period === "all" ? variable : `year_${variable}`;
  return file.records.find((r) => r.variable === name && r.period === period);
}

/** The hour of a record in the grid's own time: "29 April 2026, 11:00". */
export function localHour(ts: string, tz: string): string {
  const d = new Date(ts);
  const day = d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: tz });
  const hour = d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: tz });
  return `${day}, ${hour}`;
}

/** Which data a period rests on, in words. */
export const sideName = (side: string) => (side === "caiso" ? "CAISO's own data" : side === "eia930" ? "EIA-930" : "EIA-930 and CAISO's own data");
