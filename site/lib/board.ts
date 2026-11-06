// Energy Research Warehouse (ERW) site, session 132: the price board and its markets workbench (/board).
//
// One page holds what /board, /board/v3, the version 4 work and /markets showed. Every figure of a row is in the
// site's own file (data/board.json, written by warehouse/derived/board_page.py); the workbench reads one small file
// a series (public/board/s/<id>.json) and one a power hub (public/board/h/<id>.json) when a row is opened. The
// functions here are pure: the page, the workbench and the tests (scripts/test-board.mjs) share them. Nothing is
// filled: a figure that is not held is null and the page shows a short placeholder. Method: docs/methods/price_board.md.

export type Move = { t: string; v: number; ch: number; pct: number | null };
// session 1116: "license" is a row of a grid whose own prices are held for a license on the day (holdRows, below)
export type Status = "ok" | "paused" | "licensed" | "license" | "not_held" | "working";
export type Row = {
  id: string; group: string; label: string; at: string; code: string; unit: string; freq: "D" | "W" | "M" | "Q" | "";
  tags: Record<string, string>; status: Status; note?: string; source?: number; formula?: string; also?: string[];
  curve?: { status: Status; note: string }; hourly?: string; hub?: string;
  last?: { t: string; v: number }; moves?: Partial<Record<MoveKey, Move | null>>;
  range?: { lo: number; hi: number; n: number; pos: number | null } | null;
  avg7?: { v: number; n: number }; avg30?: { v: number; n: number }; lo30?: number; hi30?: number;
  /** session 1613: the trailing twelve-month mean (the values held of the 365 days ending on the latest) and the latest less it */
  avg365?: { v: number; n: number; ch: number };
  spark?: { t0: string; d: number[]; v: number[] };
  /** session 1118: what a spread's newest value was made of (the builder's spark_inputs, dark_inputs, crack_inputs) */
  inputs?: { t: string; hub?: number; gas?: number; gas_t?: string; coal?: number; coal_t?: string; heat_rate?: number; gasoline?: number; diesel?: number; crude?: number; product?: number };
  /** session 1601: the row's time base and granularity in words (the builder's basis_of), in the name's hover */
  basis?: string;
  /** session 1611: the latest complete day's highest and lowest hour, each with the hour it began in the grid's local time */
  ext?: { t: string; tz: string; hi: Extreme; lo: Extreme; hours: number; w?: ExtWindow; m?: ExtWindow } | null;   // w, m: session 1612
  /** session 1601: a page that draws what the row summarizes (the node basis rows: the node view) */
  link?: { href: string; words: string };
};
/** Session 1601: the hover of a row's name: its code, formula, interval and source, one a line. Pure. */
export function nameTitle(row: Pick<Row, "code" | "formula" | "basis" | "source">, sources: string[]): string | undefined {
  return [row.code ? `Code: ${row.code}` : "", row.formula ? `Formula: ${row.formula}` : "", row.basis ? `Interval: ${row.basis}` : "",
    row.source !== undefined ? `Source: ${sources[row.source]}` : ""].filter(Boolean).join("\n") || undefined;
}
export type Extreme = { v: number; utc: string; local: string; day?: string };
/** Session 1612: a week's or a month's hours of a power row: its complete days, its peak hour, the hours above each threshold. */
export type ExtWindow = { days: number; first: string; hours: number; peak: Extreme; above: Record<string, number> };
export const THRESHOLDS = ["100", "250", "1000"] as const;
/** Session 1612: the hover of a week's or a month's line. Pure. */
export function windowWords(row: Pick<Row, "ext" | "unit">, k: "w" | "m"): string | null {
  const e = row.ext, x = e?.[k];
  if (!e || !x) return null;
  return `${x.days} complete days, ${dateWords(x.first)} to ${dateWords(e.t)}, ${x.hours} hours: the peak hour began at ${x.peak.local} on ${dateWords(x.peak.day ?? e.t)} (local time); hours above ${THRESHOLDS.map((n) => `${Number(n).toLocaleString("en-US")} USD/MWh: ${x.above[n]}`).join(", ")}`;
}
/** Session 1611: the words of a row's day extremes, for the cell's hover. Pure. */
export function extremeWords(row: Pick<Row, "ext" | "unit">): string | null {
  const e = row.ext;
  if (!e) return null;
  return `On ${dateWords(e.t)}, of its ${e.hours} hours: the highest began at ${e.hi.local}, the lowest at ${e.lo.local} (local time, ${e.tz}); each hour as the row's interval says`;
}
export type Filter = { key: string; label: string; options: [string, string][]; default: string };
export type Group = { id: string; title: string; filters: Filter[]; curve?: boolean; extra?: string; extremes?: boolean };   // extremes: session 1611
export type WeekRow = {
  hub: string; grid: string; label: string; code: string; last_da?: { t: string; v: number };
  means: Record<string, { v: number; ch: number | null; end: string }>;
  max_spread?: { v: number; start: string; end: string }; hours50?: { v: number; start: string; end: string }; vol?: { t: string; v: number };
};
export type Spike = { hub: string; grid: string; label: string; code: string; t: string; v: number; tz: string; freq: string };
export type BoardFile = {
  built: string; sources: string[]; heat_rate: number; coal_heat_rate: number; gas_back_days: number; slack_days: number;
  groups: Group[]; rows: Row[]; week: WeekRow[]; spikes: Spike[];
  /** session 1116: the grids held for a license on the day, by name, set by holdRows; their week rows and spikes are left out */
  held?: string[];
};
export type SeriesFile = { id: string; label: string; at: string; unit: string; freq: "D" | "W" | "M" | "Q"; t0: string; d: number[]; v: number[] };
/** Session 1135: the workbench's charts draw a quarterly series on the months' axis, each point at its own month. */
export const chartFreq = (f: "D" | "W" | "M" | "Q"): "D" | "W" | "M" => (f === "Q" ? "M" : f);
export type HourlyFile = { id: string; tz: string; t0: number; n: number; pk: string; da?: (number | null)[]; rt?: (number | null)[] };
export type Point = { t: number; v: number };

export const DAY = 86_400_000;
export const HOUR = 3_600_000;
// session 1608: the year to date, against the last value held of the year before (the builder's year_end)
export const MOVES = [["d", "Day"], ["w", "Week"], ["m", "Month"], ["y", "Year"], ["ytd", "YTD"]] as const;
export type MoveKey = (typeof MOVES)[number][0];
export const PLACEHOLDER: Record<Exclude<Status, "ok">, string> = {
  paused: "paused while terms are reviewed", licensed: "licensed source needed", license: "license needed", not_held: "not held yet", working: "working on it",
};
export const FREQ_WORDS: Record<string, string> = { D: "daily", W: "weekly", M: "monthly", Q: "quarterly", "": "" };
/** Why a move is blank on a series that is not daily: a weekly series has no daily move, a monthly one no daily or weekly move. */
export const noMove = (freq: string, k: string) => (freq === "W" && k === "d") || (freq === "M" && (k === "d" || k === "w")) || (freq === "Q" && k !== "y" && k !== "ytd");
/** Session 1608 (the chain's rule: a move on a stale series is blank, with its status): the move a row shows, null when the
 *  row is stale on the day the board was built or the move is not held. Pure; the page and scripts/check-board.mjs share it. */
export function shownMove(row: Row, k: MoveKey, built: string): Move | null {
  if (closeAge(row, built)?.stale) return null;
  return row.moves?.[k] ?? null;
}

/** Decimals a unit is written with: gallons to a tenth of a cent, large prices whole, everything else to the cent. */
export function places(unit: string, v = 0): number {
  if (unit === "USD/gal") return 3;
  if (Math.abs(v) >= 10_000) return 0;
  return 2;
}
export const fmt = (v: number, unit: string) => v.toLocaleString("en-US", { minimumFractionDigits: places(unit, v), maximumFractionDigits: places(unit, v) });
export const signed = (v: number, unit: string) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${fmt(Math.abs(v), unit)}`;
export const pct = (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toFixed(1)}%`;
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
/** "29 Sep 2026" from a day; a monthly value is written "Sep 2026". */
export function dateWords(t: string, freq = "D"): string {
  const [y, m, d] = t.slice(0, 10).split("-").map(Number);
  return freq === "M" || freq === "Q" ? `${MON[m - 1]} ${y}` : `${d} ${MON[m - 1]} ${y}`;
}
export const shortDate = (t: string, freq = "D") => (freq === "M" || freq === "Q" ? dateWords(t, "M") : dateWords(t).replace(/ \d{4}$/, ""));
export const isoDay = (ms: number) => new Date(ms).toISOString().slice(0, 10);
export const isoHour = (ms: number) => new Date(ms).toISOString().slice(0, 13).replace("T", " ") + ":00 UTC";
/** A UTC hour in a grid's local time, "03 Oct 14:00". */
export function localHour(ms: number, tz: string): string {
  return new Intl.DateTimeFormat("en-GB", { timeZone: tz, day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(ms));
}

// Session 1116: the hold of 21 October 2026 on the board. The builder (warehouse/derived/board_page.py) holds ISO-NE's and
// NYISO's hub rows, but their peak and off-peak rows, spreads, day-ahead less real time, battery spreads, ancillary
// prices, week rows and spikes come from tables held for those grids too (price_board_peak_offpeak, price_board_spreads,
// nyiso_as_prices, iso_hub_prices_history: site/data/license_status.json) and were drawn. holdRows makes every row of a
// held grid "license needed" in place, its name kept and its figures dropped, and leaves the grid's week rows and spikes
// out; the page calls it on the server, so no held figure reaches the browser. MISO's rows stay "paused" (its pause
// says more than its license) and PJM's "licensed source needed". Pure: the held grids are given (lib/license.ts).
const GRID_OF_ID: Record<string, string> = { isone: "ISO-NE", nyiso: "NYISO", miso: "MISO", pjm: "PJM", ercot: "ERCOT", caiso: "CAISO", spp: "SPP" };
export const gridOfRow = (r: { id: string; tags?: Record<string, string> }): string => r.tags?.grid ?? GRID_OF_ID[r.id.split("-")[0]] ?? "";
// ext: session 1611; basis and heat_ref: session 1632 (a held row prints its status words and no digit, its interval's words included)
const FIGURES = ["last", "moves", "range", "avg7", "avg30", "avg365", "lo30", "hi30", "ext", "basis", "heat_ref", "spark", "hourly", "inputs"] as const;
export function heldNote(grid: string): string {
  return `${grid}'s own terms ask for permission to republish its prices, and none is recorded yet (docs/licenses.md, site/data/license_status.json): license needed. This row is held, not shown, until a permission is recorded.`;
}
/** Session 1193: a group's rows split for drawing: the rows shown in place (every row but a held grid's), and the held
 *  grids' rows by grid, in the order each grid first appears. The rows themselves are not changed. Pure. */
export function heldLines(rows: Row[]): { shown: Row[]; held: { grid: string; rows: Row[] }[] } {
  const shown: Row[] = [];
  const held = new Map<string, Row[]>();
  for (const r of rows) {
    if (r.status !== "license") { shown.push(r); continue; }
    const g = gridOfRow(r) || "Held";
    held.set(g, [...(held.get(g) ?? []), r]);
  }
  return { shown, held: [...held].map(([grid, rs]) => ({ grid, rows: rs })) };
}

export function holdRows(file: BoardFile, heldGrids: string[]): BoardFile {
  const held = new Set(heldGrids.filter((g) => g !== "MISO" && g !== "PJM"));
  if (!held.size) return { ...file, held: [] };
  const rows = file.rows.map((r) => {
    if (!held.has(gridOfRow(r)) || r.status === "not_held") return r;
    const out: Row = { ...r, status: "license", note: heldNote(gridOfRow(r)) };
    for (const k of FIGURES) delete (out as Record<string, unknown>)[k];
    return out;
  });
  return { ...file, rows, week: file.week.filter((w) => !held.has(w.grid)), spikes: file.spikes.filter((x) => !held.has(x.grid)), held: [...held].sort() };
}

// Session 1116: how old a close is, and when it is stale. The age is counted as session 804 counts the Digest's fuel
// closes ("EIA's newest close when this was written, 7 days before this issue"): whole UTC days from the value's date to
// the day the board's file was built. A daily series is stale past 10 days (session 304, the owner's ruling of
// 18 October 2026: EIA posts spot prices weekly and late), a weekly one past a week more, and a monthly one (dated the
// first day of its month) past four months and the same 10 days: EIA's monthly series come about two months after
// their month. The one function every row and tile reads.
export const STALE_DAYS: Record<"D" | "W" | "M" | "Q", number> = { D: 10, W: 17, M: 132, Q: 135 };   // Q (session 1135): a quarter, a month, and the 10 days
/** Session 1134: by the publisher's calendar. A power market posts every day, weekends and holidays included (its
 *  day-ahead prices the day before), so a daily row of the power groups is stale past 3 days; EIA's daily fuel closes
 *  are trading days, posted weekly and late, and keep the 10 days of session 304's ruling. */
export const POWER_GROUPS = new Set(["power", "peak", "spark", "da_rt", "battery", "as", "hubspread"]);   // hubspread: session 1606
export const STALE_POWER_DAYS = 3;
export const staleDays = (row: Pick<Row, "freq" | "group">): number => (row.freq === "D" && POWER_GROUPS.has(row.group) ? STALE_POWER_DAYS : STALE_DAYS[row.freq as "D" | "W" | "M" | "Q"]);
export function ageDays(t: string, built: string): number {
  return Math.round((Date.parse(`${built.slice(0, 10)}T00:00:00Z`) - Date.parse(`${t.slice(0, 10)}T00:00:00Z`)) / DAY);
}
export function closeAge(row: Row, built: string): { days: number; stale: boolean; words: string } | null {
  if (!row.last || !row.freq) return null;
  const days = ageDays(row.last.t, built);
  const when = dateWords(built);
  const words = days > 0 ? `${days} ${days === 1 ? "day" : "days"} before the board was built on ${when}`
    : days === 0 ? `the day the board was built (${when})` : `${-days} ${days === -1 ? "day" : "days"} after the board was built on ${when}: a day-ahead price for a coming day`;
  const limit = staleDays(row);
  const stale = days > limit;
  const what = row.freq === "D" && POWER_GROUPS.has(row.group) ? "a market's daily price" : `a ${FREQ_WORDS[row.freq]} series`;
  return { days, stale, words: stale ? `${words}. Stale: ${what} is marked stale past ${limit} days (docs/methods/price_board.md)` : words };
}

/** Session 1118: the hover words of a spread's newest value, from its inputs: the hub's day-ahead mean and its day, the
 *  gas or coal price and its own day or month, the stated heat rate; the crack's three prices. Null for any other row. */
export function inputsWords(row: Row): string | null {
  const i = row.inputs;
  if (!i) return null;
  const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 3 });
  if (i.gas !== undefined && i.gas_t && i.hub !== undefined) {
    const gas = `Henry Hub ${two(i.gas)} USD/MMBtu on ${dateWords(i.gas_t)}`;
    return i.heat_rate !== undefined
      ? `Made of: the hub's day-ahead mean ${two(i.hub)} USD/MWh on ${dateWords(i.t)}, less ${i.heat_rate} MMBtu/MWh (the stated heat rate) times ${gas}`
      : `Made of: the hub's day-ahead mean ${two(i.hub)} USD/MWh on ${dateWords(i.t)}, over ${gas}`;
  }
  if (i.coal !== undefined && i.coal_t && i.hub !== undefined && i.heat_rate !== undefined)
    return `Made of: the hub's day-ahead mean ${two(i.hub)} USD/MWh over ${dateWords(i.t, "M")}, less ${i.heat_rate} MMBtu/MWh (the stated heat rate) times US coal delivered to power plants, ${two(i.coal)} USD/MMBtu in ${dateWords(i.coal_t, "M")}`;
  if (i.gasoline !== undefined && i.diesel !== undefined && i.crude !== undefined)
    return `Made of, on ${dateWords(i.t)}: gasoline ${two(i.gasoline)} and diesel ${two(i.diesel)} USD/gal, crude ${two(i.crude)} USD/bbl`;
  // session 1607: a crack of one product, its gallon and the crude's barrel
  if (i.product !== undefined && i.crude !== undefined)
    return `Made of, on ${dateWords(i.t)}: the product ${two(i.product)} USD/gal, crude ${two(i.crude)} USD/bbl`;
  return null;
}

/** The rows of a group that the chosen filters let through, in the file's order. */
export function rowsOf(file: BoardFile, group: Group, chosen: Record<string, string>): Row[] {
  return file.rows.filter((r) => (r.group === group.id || r.also?.includes(group.id)) && group.filters.every((f) => {
    const want = chosen[f.key] ?? f.default;
    return want === "all" || r.tags[f.key] === undefined || r.tags[f.key] === want;
  }));
}
/** The trend line's points of a row as [{t, v}] (session 1609: up to 90, the span by step). */
export function sparkOf(r: Row): { t: string; v: number }[] {
  if (!r.spark) return [];
  const t0 = Date.parse(`${r.spark.t0}T00:00:00Z`);
  return r.spark.d.map((d, i) => ({ t: isoDay(t0 + d * DAY), v: r.spark!.v[i] }));
}
/** A series file as points in time (UTC milliseconds). */
export function pointsOf(f: SeriesFile): Point[] {
  const t0 = Date.parse(`${f.t0}T00:00:00Z`);
  return f.d.map((d, i) => ({ t: t0 + d * DAY, v: f.v[i] }));
}
/** One market of an hourly file as points; hours not held are left out, never filled. */
export function hourlyOf(f: HourlyFile, market: "da" | "rt"): Point[] {
  const a = f[market] ?? [];
  const out: Point[] = [];
  for (let i = 0; i < a.length; i++) if (a[i] !== null) out.push({ t: (f.t0 + i) * HOUR, v: a[i] as number });
  return out;
}
/** Whether an hour of an hourly file is on-peak (the builder's rule, in the file's pk string). */
export const isPeak = (f: HourlyFile, t: number) => f.pk[t / HOUR - f.t0] === "1";

export const WINDOWS: [string, string, number][] = [["1w", "Week", 7], ["1m", "Month", 31], ["3m", "3 months", 92], ["6m", "6 months", 183], ["1y", "Year", 366], ["2y", "2 years", 731], ["5y", "5 years", 1827], ["all", "All", 0]];
/** The points inside a window: a preset counted back from the newest point, or the dates given (inclusive). */
export function windowed(p: Point[], w: string, from?: string, to?: string): Point[] {
  if (!p.length) return p;
  if (from || to) {
    const a = from ? Date.parse(`${from}T00:00:00Z`) : -Infinity, b = to ? Date.parse(`${to}T00:00:00Z`) + DAY : Infinity;
    return p.filter((x) => x.t >= a && x.t < b);
  }
  const days = WINDOWS.find((x) => x[0] === w)?.[2] ?? 0;
  if (!days) return p;
  const start = p[p.length - 1].t - days * DAY;
  return p.filter((x) => x.t > start);
}
/** The two series on the times both hold, with their spread (a - b) and ratio (a / b, where b is not zero). */
export function joined(a: Point[], b: Point[]): { t: number; a: number; b: number; spread: number; ratio: number | null }[] {
  const m = new Map(b.map((x) => [x.t, x.v]));
  const out = [];
  for (const x of a) {
    const y = m.get(x.t);
    if (y !== undefined) out.push({ t: x.t, a: x.v, b: y, spread: x.v - y, ratio: y !== 0 ? x.v / y : null });
  }
  return out;
}
export type Summary = { n: number; mean: number; min: number; max: number; minT: number; maxT: number; median: number };
export function summary(p: Point[]): Summary | null {
  if (!p.length) return null;
  let lo = p[0], hi = p[0], sum = 0;
  for (const x of p) { sum += x.v; if (x.v < lo.v) lo = x; if (x.v > hi.v) hi = x; }
  const s = p.map((x) => x.v).sort((x, y) => x - y);
  const median = s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2;
  return { n: p.length, mean: sum / p.length, min: lo.v, max: hi.v, minT: lo.t, maxT: hi.t, median };
}
/** Daily means of hourly points by UTC day are not made here: a daily figure is always the builder's, by local day. */

/** The standard deviation of the last `n` changes between consecutive points (the markets page's volatility), or null. */
export function volatility(p: Point[], n = 30): number | null {
  if (p.length < n + 1) return null;
  const tail = p.slice(-(n + 1));
  const ch = tail.slice(1).map((x, i) => x.v - tail[i].v);
  const mean = ch.reduce((a, b) => a + b, 0) / ch.length;
  return Math.sqrt(ch.reduce((a, b) => a + (b - mean) ** 2, 0) / (ch.length - 1));
}
export type Distribution = {
  n: number; above: number; negative: number; top: Point[]; peakMean: number | null; offMean: number | null; peakN: number; offN: number;
};
/** The distribution block of a window: observations above a threshold, negative ones, the ten highest, and, for an
 *  hourly series, the on-peak and off-peak means. */
export function distribution(p: Point[], threshold: number, hourly?: HourlyFile): Distribution {
  let above = 0, negative = 0, ps = 0, pn = 0, os = 0, on = 0;
  for (const x of p) {
    if (x.v > threshold) above += 1;
    if (x.v < 0) negative += 1;
    if (hourly) { if (isPeak(hourly, x.t)) { ps += x.v; pn += 1; } else { os += x.v; on += 1; } }
  }
  const top = [...p].sort((a, b) => b.v - a.v || a.t - b.t).slice(0, 10);
  return { n: p.length, above, negative, top, peakMean: pn ? ps / pn : null, offMean: on ? os / on : null, peakN: pn, offN: on };
}
/** Bins of a histogram: `bins` equal steps from the lowest to the highest value. */
export function histogram(p: Point[], bins = 30): { lo: number; hi: number; n: number }[] {
  const s = summary(p);
  if (!s || s.max === s.min) return s ? [{ lo: s.min, hi: s.max, n: s.n }] : [];
  const w = (s.max - s.min) / bins;
  const out = Array.from({ length: bins }, (_, i) => ({ lo: s.min + i * w, hi: s.min + (i + 1) * w, n: 0 }));
  for (const x of p) out[Math.min(bins - 1, Math.floor((x.v - s.min) / w))].n += 1;
  return out;
}

/** The slot of a point within its year, so the same dates of different years line up: the day of the year (a daily
 *  series; 29 February shares 28 February's slot), the week (weekly) or the month (monthly). */
export function slotOf(t: number, freq: "D" | "W" | "M"): number {
  const d = new Date(t);
  if (freq === "M") return d.getUTCMonth();
  const start = Date.UTC(d.getUTCFullYear(), 0, 1);
  let doy = Math.floor((t - start) / DAY);
  const leap = new Date(Date.UTC(d.getUTCFullYear(), 1, 29)).getUTCMonth() === 1;
  if (leap && doy >= 59) doy -= 1;
  return freq === "W" ? Math.min(51, Math.floor(doy / 7)) : doy;
}
export const SLOTS = { D: 365, W: 52, M: 12 } as const;
export function slotLabel(slot: number, freq: "D" | "W" | "M"): string {
  if (freq === "M") return MON[slot];
  const d = new Date(Date.UTC(2023, 0, 1) + (freq === "W" ? slot * 7 : slot) * DAY);
  return `${d.getUTCDate()} ${MON[d.getUTCMonth()]}`;
}
export type Seasonal = { years: number[]; lines: Record<number, (number | null)[]>; lo: (number | null)[]; hi: (number | null)[]; bandYears: number[] };
/** This year against the same dates in prior years: one line a year by slot, and the lowest and highest of the five
 *  years before the newest as a band. A slot a year does not hold is null in that year's line. The band of a daily
 *  series is by the week: the lowest and highest value those five years hold in the seven days the slot falls in (a
 *  fuel has no weekend, so a band by the single day would narrow wherever a year's date fell on one); of a weekly or
 *  monthly series, by the slot itself. It covers a slot when at least one of the five years holds a value there. */
export function seasonal(p: Point[], freq: "D" | "W" | "M"): Seasonal {
  const n = SLOTS[freq];
  const lines: Record<number, (number | null)[]> = {};
  for (const x of p) {
    const y = new Date(x.t).getUTCFullYear();
    (lines[y] ??= Array<number | null>(n).fill(null))[slotOf(x.t, freq)] = x.v;
  }
  const years = Object.keys(lines).map(Number).sort((a, b) => a - b);
  const newest = years[years.length - 1];
  const bandYears = years.filter((y) => y < newest && y >= newest - 5);
  const lo = Array<number | null>(n).fill(null), hi = Array<number | null>(n).fill(null);
  const span = freq === "D" ? 7 : 1;
  for (let i = 0; i < n; i += span) {
    const vals: number[] = [];
    for (const y of bandYears) for (let k = i; k < Math.min(n, i + span); k++) { const v = lines[y][k]; if (v !== null) vals.push(v); }
    if (vals.length) for (let k = i; k < Math.min(n, i + span); k++) { lo[k] = Math.min(...vals); hi[k] = Math.max(...vals); }
  }
  return { years, lines, lo, hi, bandYears };
}

/** A CSV of rows: a header and one line a row; a field with a comma or a quote is quoted. */
export function csv(head: string[], rows: (string | number | null)[][]): string {
  const cell = (c: string | number | null) => (c === null ? "" : /[",\n]/.test(String(c)) ? `"${String(c).replace(/"/g, '""')}"` : String(c));
  return [head, ...rows].map((r) => r.map(cell).join(",")).join("\n") + "\n";
}

// Session 1137: the rows the board draws, as a CSV, from the file the page draws (after holdRows, so a held row carries
// no figure): a "#" header as the data standard writes one (what it is, where each row comes from, when it was built,
// the license), then one line a row. Every figure is the file's, as the page shows it; nothing is read again.
// Session 1311: a held row's line carries the hold's words (heldNote) in `hold`, as the page says them on the grid's
// line (session 1193), and the header counts the held rows by grid.
// Session 1614 (chain 165): the board as shown: the year to date's move, the twelve-month mean and the latest less it, the
// day's high and low hour with their local times (between "latest" and "source", so a held row's are empty as its other
// figures are), and the row's interval and the words of its status (before "hold", which stays last).
export const ROWS_HEAD = ["id", "group", "label", "at", "code", "unit", "freq", "status", "latest_date", "latest", "day_move", "week_move", "month_move", "year_move",
  "ytd_move", "avg_7d", "avg_30d", "avg_12m", "vs_12m", "low_365d", "high_365d", "day_high", "day_high_local", "day_low", "day_low_local",
  // session 1631 (chain 167): the week's and the month's peak hour and the hours above 100, 250 and 1,000, as the power rows' cells show them
  "week_peak", "week_hours_over_100", "week_hours_over_250", "week_hours_over_1000", "month_peak", "month_hours_over_100", "month_hours_over_250", "month_hours_over_1000",
  "source", "basis", "status_words", "hold"];
export function rowsCsv(file: BoardFile): string {
  const header = [
    "# Energy Research Warehouse (ERW): the price board's rows as /board draws them, one line a row (site/lib/board.ts rowsCsv)",
    `# Built: ${file.built} (the board's file, site/data/board.json, written by warehouse/derived/board_page.py from the ERW's tables)`,
    "# Source: each row's source column names the publisher and the ERW table; the method: docs/methods/price_board.md",
    "# License: every row with a value is public; a row whose status is license, licensed, paused or not_held carries no figure",
    ...(file.held?.length ? [`# Held for a license on the day the page was built: ${file.held.join(", ")} (license needed)`] : []),
    ...(file.held?.length ? [`# Held rows by grid: ${file.held.map((g) => `${g} ${file.rows.filter((r) => r.status === "license" && gridOfRow(r) === g).length}`).join(", ")}; each carries no figure, and its hold column the hold's words`] : []),
  ];
  const n = (v: number | null | undefined) => (typeof v === "number" ? v : null);
  const rows = file.rows.map((r) => [r.id, r.group, r.label, r.at, r.code, r.unit, r.freq, r.status, r.last?.t ?? null, n(r.last?.v),
    n(r.moves?.d?.ch), n(r.moves?.w?.ch), n(r.moves?.m?.ch), n(r.moves?.y?.ch), n(r.moves?.ytd?.ch), n(r.avg7?.v), n(r.avg30?.v), n(r.avg365?.v), n(r.avg365?.ch),
    n(r.range?.lo), n(r.range?.hi), n(r.ext?.hi.v), r.ext?.hi.local ?? null, n(r.ext?.lo.v), r.ext?.lo.local ?? null,
    ...(["w", "m"] as const).flatMap((k) => [n(r.ext?.[k]?.peak.v), ...THRESHOLDS.map((x) => n(r.ext?.[k]?.above[x]))]),
    r.source !== undefined ? file.sources[r.source] ?? null : null, r.basis ?? null, r.status === "ok" ? null : PLACEHOLDER[r.status],
    r.status === "license" ? heldNote(gridOfRow(r)) : null]);
  return `${header.join("\n")}\n${csv(ROWS_HEAD, rows)}`;
}

/** Session 1616 (chain 165): the least rows with values a group holds when the board is whole, for the groups it has; a
 *  group not in the file (a file built before the group) is not judged. The counts are about two thirds of the rows with
 *  values after the day's hold on the file of 5 November 2026 (power 22, peak 18, spark 9, da_rt 11, battery 22, as 27,
 *  gasprices 255, crude 44, products 9, oilspreads 2, world 9, retailfuel 40, heating 140, retailpower 248, plantfuel 143,
 *  metals 5, rates 3, carbon 4), and of what chain 165's builder adds to a new group, so a thinner build is caught and a
 *  day's gap is not. */
export const GROUP_FLOORS: Record<string, number> = {
  power: 14, peak: 12, spark: 6, hubspread: 4, da_rt: 7, battery: 14, as: 18, gas: 1, gasflows: 12, gasprices: 170, crude: 29,
  products: 6, oilspreads: 2, gasspreads: 1, world: 6, retailfuel: 27, heating: 93, retailpower: 165, plantfuel: 95, metals: 3, rates: 2, carbon: 3, costs: 1,
};
const FIGURE_KEYS = ["last", "moves", "range", "avg7", "avg30", "avg365", "lo30", "hi30", "ext", "basis", "spark", "inputs"] as const;   // basis: session 1632
const near = (a: number, b: number) => Math.abs(a - b) <= 0.0002 + 1e-9 * Math.abs(b);
/** Session 1616: the checks of the board's file alone, as the page draws it (after holdRows): a key per cell (unique ids,
 *  every figure a number), a floor a group, every placeholder's words with no digit and no figure, and the figures this
 *  chain added consistent with each other. Pure: scripts/check-board.mjs prints them, with or without a served page. */
export function boardFileChecks(file: BoardFile): { ok: boolean; what: string }[] {
  const out: { ok: boolean; what: string }[] = [];
  const add = (ok: boolean, what: string) => out.push({ ok, what });
  const ids = file.rows.map((r) => r.id);
  const dup = ids.filter((id, i) => ids.indexOf(id) !== i);
  add(dup.length === 0, `every row has its own id, so every cell's key is its own (${ids.length} rows)${dup.length ? `: repeated ${dup.slice(0, 5).join(", ")}` : ""}`);
  const ok = file.rows.filter((r) => r.status === "ok");
  const badNum = ok.filter((r) => !r.last || typeof r.last.v !== "number" || !Number.isFinite(r.last.v) || !/^\d{4}-\d{2}-\d{2}$/.test(r.last.t)
    || Object.values(r.moves ?? {}).some((m) => m && !Number.isFinite(m.ch)) || (r.source !== undefined && !file.sources[r.source]));
  add(badNum.length === 0, `every row with a value has its date, numbers that are numbers and a source (${ok.length} rows)${badNum.length ? `: ${badNum.slice(0, 5).map((r) => r.id).join(", ")}` : ""}`);
  const groups = new Set(file.groups.map((g) => g.id));
  const thin = Object.entries(GROUP_FLOORS).filter(([g]) => groups.has(g)).map(([g, floor]) => [g, ok.filter((r) => r.group === g).length, floor] as const).filter(([, n, floor]) => n < floor);
  const absent = Object.keys(GROUP_FLOORS).filter((g) => !groups.has(g));
  add(thin.length === 0, `every group holds its floor of rows with values${thin.length ? `: ${thin.map(([g, n, f]) => `${g} ${n} of ${f}`).join(", ")}` : ""}${absent.length ? ` (not in this file yet: ${absent.join(", ")})` : ""}`);
  const grey = file.rows.filter((r) => r.status !== "ok");
  const leaky = grey.filter((r) => FIGURE_KEYS.some((k) => (r as Record<string, unknown>)[k] !== undefined) || !PLACEHOLDER[r.status as Exclude<Status, "ok">] || /\d/.test(PLACEHOLDER[r.status as Exclude<Status, "ok">] ?? "0"));
  add(leaky.length === 0, `every row with no value shows its words ("licensed source needed" and the others), no digit and no figure (${grey.length} rows; ${grey.filter((r) => r.status === "licensed").length} licensed)${leaky.length ? `: ${leaky.slice(0, 5).map((r) => r.id).join(", ")}` : ""}`);
  const extBad = ok.filter((r) => r.ext && (r.ext.hi.v < r.ext.lo.v || (["w", "m"] as const).some((k) => {
    const x = r.ext![k];
    return x && (x.peak.v < r.ext!.hi.v - 1e-9 || x.above["100"] < x.above["250"] || x.above["250"] < x.above["1000"] || x.above["100"] > x.hours);
  })));
  add(extBad.length === 0, `every day's high is above its low, every week's and month's peak at least the day's high, and the hours above 100, 250 and 1,000 in order (${ok.filter((r) => r.ext).length} rows)${extBad.length ? `: ${extBad.slice(0, 5).map((r) => r.id).join(", ")}` : ""}`);
  const avgBad = ok.filter((r) => r.avg365 && r.last && !near(r.avg365.ch, r.last.v - r.avg365.v));
  add(avgBad.length === 0, `every twelve-month mean's difference is the latest less the mean (${ok.filter((r) => r.avg365).length} rows)${avgBad.length ? `: ${avgBad.slice(0, 5).map((r) => r.id).join(", ")}` : ""}`);
  const ytdBad = ok.filter((r) => r.moves?.ytd && r.last && Number(r.moves.ytd.t.slice(0, 4)) !== Number(r.last.t.slice(0, 4)) - 1);
  add(ytdBad.length === 0, `every year-to-date move is measured from the year before the latest (${ok.filter((r) => r.moves?.ytd).length} rows)${ytdBad.length ? `: ${ytdBad.slice(0, 5).map((r) => r.id).join(", ")}` : ""}`);
  const added = new Set(["hubspread", "gasflows", "gasspreads", "costs"]);
  const said = ok.filter((r) => added.has(r.group) && !r.basis && !r.formula);
  add(said.length === 0, `every row of the groups chain 165 added says its interval or its formula${said.length ? `: ${said.slice(0, 5).map((r) => r.id).join(", ")}` : ""}`);
  return out;
}

/** Session 1614: a reader of the rows' CSV (/board/rows), in Python or in Stata, for a reader who wants the board as it is
 *  shown in a session of their own: the "#" header printed and skipped, the rows loaded as they are, the held rows counted
 *  by their status words. The Stata reader keeps the owner's rules (no line continuation, one empty line between commands
 *  outside a loop and none inside one, every figure column destrung with force). Pure: the address is given. */
export function rowsReader(as: "py" | "do", url: string): string {
  const figures = ROWS_HEAD.slice(ROWS_HEAD.indexOf("latest"), ROWS_HEAD.indexOf("source")).filter((c) => !c.endsWith("_local"));
  if (as === "py") {
    return [
      "# Energy Research Warehouse (ERW): read the price board's rows as /board draws them (site/lib/board.ts rowsReader).",
      "# The CSV opens with its provenance, lines that begin with \"#\"; they are printed and skipped, and the rows are",
      "# loaded as they are. A held row carries no figure: its status_words say why, and its hold column the hold's words.",
      "# Needs pandas.",
      "import io",
      "import urllib.request",
      "",
      "import pandas as pd",
      "",
      `URL = "${url}"`,
      "text = urllib.request.urlopen(URL, timeout=300).read().decode(\"utf-8\")",
      "lines = text.splitlines()",
      "n = 0",
      "while n < len(lines) and lines[n].startswith(\"#\"):",
      "    n += 1",
      "print(\"\\n\".join(lines[:n]))",
      "board = pd.read_csv(io.StringIO(\"\\n\".join(lines[n:])), dtype={\"latest_date\": str, \"day_high_local\": str, \"day_low_local\": str})",
      "print(board.shape)",
      "print(board[\"status_words\"].fillna(\"shown\").value_counts())",
      "print(board[board[\"status\"] == \"ok\"][[\"id\", \"label\", \"at\", \"latest_date\", \"latest\", \"unit\"]].head(20))",
      "",
    ].join("\n");
  }
  return [
    "* Energy Research Warehouse (ERW): read the price board's rows as /board draws them (site/lib/board.ts rowsReader).",
    "* The CSV opens with its provenance, lines that begin with \"#\"; they are counted and skipped, the column names are",
    "* the first line after them. A held row carries no figure: its status_words say why, its hold column the hold's words.",
    "clear",
    "",
    "tempfile raw",
    "",
    `copy "${url}" \`raw'`,
    "",
    "tempname fh",
    "",
    "local n 0",
    "",
    "file open `fh' using `raw', read text",
    "",
    "file read `fh' line",
    "",
    "while r(eof) == 0 {",
    "    if substr(`\"`macval(line)'\"', 1, 1) != \"#\" continue, break",
    "    local n = `n' + 1",
    "    file read `fh' line",
    "}",
    "",
    "file close `fh'",
    "",
    "import delimited using `raw', varnames(`=`n' + 1') encoding(\"utf-8\") bindquote(strict) stringcols(_all) clear",
    "",
    ...figures.flatMap((c) => [`destring ${c}, replace force`, ""]),
    "tabulate status_words, missing",
    "",
    "describe",
    "",
  ].join("\n");
}

// The workbench's state, kept in the address so a view can be shared.
export type Bench = {
  s: string | null;        // the row opened
  o: string | null;        // a second series laid over it
  m: "none" | "spread" | "ratio";   // the line computed between the two
  w: string;               // the window (WINDOWS), unless from or to is given
  from: string; to: string;
  r: "h" | "d";            // hourly or the row's own series
  v: "price" | "season" | "dist";
  th: number;              // the distribution's threshold
  x: boolean;              // the panel at full width
};
export const BENCH: Bench = { s: null, o: null, m: "spread", w: "1y", from: "", to: "", r: "d", v: "price", th: 100, x: false };
const day = (v: string | null) => (v && /^\d{4}-\d{2}-\d{2}$/.test(v) ? v : "");
/** The state an address asks for. A row that is not on the board is no row. Opening a power hub with nothing else said
 *  is the last seven days of real time against day-ahead, by the hour. */
export function benchOf(q: URLSearchParams, file: BoardFile): Bench {
  const has = (id: string | null) => (id && file.rows.some((r) => r.id === id && r.status === "ok") ? id : null);
  const s = has(q.get("s"));
  const row = s ? file.rows.find((r) => r.id === s)! : null;
  const hub = !!row?.hourly && row.group === "power";
  const o = q.has("o") ? has(q.get("o")) : hub ? has(s!.replace(/-(da|rt)$/, (_, k) => (k === "da" ? "-rt" : "-da"))) : null;
  const w = WINDOWS.some((x) => x[0] === q.get("w")) ? q.get("w")! : hub ? "1w" : "1y";
  const m = q.get("m");
  const v = q.get("v");
  const r = q.get("r");
  const th = Number(q.get("th"));
  return {
    s, o: o === s ? null : o, m: m === "ratio" || m === "none" || m === "spread" ? m : "spread", w, from: day(q.get("from")), to: day(q.get("to")),
    r: r === "h" || r === "d" ? r : row?.hourly && w !== "all" && w !== "5y" && w !== "2y" ? "h" : "d",
    v: v === "season" || v === "dist" ? v : "price", th: q.get("th") !== null && Number.isFinite(th) ? th : row?.unit === "USD/MWh" ? 100 : NaN, x: q.get("x") === "1",
  };
}
/** The address of a state: only what differs from what the row would open with is written. */
export function benchQuery(b: Bench, file: BoardFile, keep?: URLSearchParams): string {
  const q = new URLSearchParams(keep);
  for (const k of ["s", "o", "m", "w", "from", "to", "r", "v", "th", "x"]) q.delete(k);
  if (!b.s) return q.toString();
  q.set("s", b.s);
  const base = benchOf(new URLSearchParams({ s: b.s }), file);
  if (b.o !== base.o) q.set("o", b.o ?? "");
  if (b.m !== base.m) q.set("m", b.m);
  if (b.w !== base.w) q.set("w", b.w);
  if (b.from) q.set("from", b.from);
  if (b.to) q.set("to", b.to);
  if (b.r !== base.r) q.set("r", b.r);
  if (b.v !== base.v) q.set("v", b.v);
  if (Number.isFinite(b.th) && b.th !== base.th) q.set("th", String(b.th));
  if (b.x) q.set("x", "1");
  return q.toString();
}

/** The headline strip: the lowest and highest grid on the newest day every priced main hub holds, for one market. */
export function gridExtremes(file: BoardFile, market: "da" | "rt") {
  const rows = file.rows.filter((r) => r.group === "power" && r.status === "ok" && r.tags.scope === "main" && r.tags.market === market);
  if (!rows.length) return null;
  const n = new Map<string, number>();
  for (const r of rows) for (const p of sparkOf(r)) n.set(p.t, (n.get(p.t) ?? 0) + 1);
  const most = Math.max(...n.values());
  const dayAt = [...n.entries()].filter(([, k]) => k === most).map(([t]) => t).sort().at(-1)!;
  const on = rows.flatMap((r) => { const p = sparkOf(r).find((x) => x.t === dayAt); return p ? [{ row: r, v: p.v }] : []; }).sort((a, b) => a.v - b.v);
  return { day: dayAt, low: on[0], high: on[on.length - 1], grids: on.length };
}
/** The prices nearest the top and the bottom of their own one-year range (spreads left out). */
export function rangeExtremes(file: BoardFile) {
  const BENCHMARKS = ["power", "gas", "crude", "products", "metals", "rates", "carbon"];
  const rows = file.rows.filter((r) => r.status === "ok" && !r.formula && BENCHMARKS.includes(r.group) && r.range && r.range.pos !== null && (r.tags.scope ?? "main") === "main" && (r.tags.kind ?? "daily") === "daily")
    .sort((a, b) => b.range!.pos! - a.range!.pos!);
  return rows.length ? { top: rows[0], bottom: rows[rows.length - 1] } : null;
}

// Session 240: the top block. The twelve numbers a trader checks first, by the id of their row on the wall, in the
// order they are drawn. THE ONE LIST: change a line here and the top block follows; the tile reads the same row of
// data/board.json by the same code as the wall below (fmt, signed, sparkOf), so the two cannot disagree.
// Chosen from what the board holds: power where a price is set most days and stays public after 20 October 2026
// (ERCOT, CAISO and SPP; ISO-NE's, NYISO's and MISO's rows are "license needed" from that day, PJM's already are, and
// MISO is paused), the gas that sets the power price and the spread between the two, the two crudes, the two products
// a refiner sells most of with the margin between crude and products, and one macro line. All twelve are daily.
export const TOP_TWELVE: string[] = [
  "ercot-hb-hubavg-da",                      // power: ERCOT Hub average, day-ahead
  "ercot-hb-hubavg-rt",                      // power: ERCOT Hub average, real time
  "caiso-th-sp15-gen-apnd-da",               // power: CAISO Southern California (SP15), day-ahead
  "spp-sppnorth-hub-da",                     // power: SPP North hub, day-ahead
  "eia-henry-hub-spot",                      // gas: Henry Hub, spot
  "ercot-hb-hubavg-spark",                   // power against gas: ERCOT spark spread, indicative
  "eia-wti-cushing-spot",                    // crude: WTI, Cushing, spot
  "eia-brent-spot",                          // crude: Brent, spot
  "eia-eer-epmru-pf4-y35ny-dpg-spot",        // products: gasoline, New York Harbor, spot
  "eia-eer-epd2dxl0-pf4-y35ny-dpg-spot",     // products: diesel, New York Harbor, spot
  "erw-crack-321-gulf-coast",                // products against crude: 3-2-1 crack spread, Gulf Coast
  "fred-dgs10",                              // macro: US Treasury yield, 10-year
];
/** The grids whose own prices show "license needed" from 20 October 2026, are licensed already or are paused: a row of
 *  theirs is never among the twelve (scripts/test-board.mjs holds the list to this). */
export const TOP_NEVER = /^(isone|nyiso|miso|pjm)-/;
/** The rows of the top block, in the list's order. An id the file does not hold is left out, never filled. */
export function topRows(file: BoardFile, ids: string[] = TOP_TWELVE): Row[] {
  return ids.flatMap((id) => { const r = file.rows.find((x) => x.id === id); return r ? [r] : []; });
}
/** A group's first row that holds a value, under its default filters: the number a closed group keeps in view. */
export function leadRow(file: BoardFile, group: Group): Row | null {
  return rowsOf(file, group, {}).find((r) => r.status === "ok" && !!r.last) ?? null;
}
