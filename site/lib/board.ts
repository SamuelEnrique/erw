// Energy Research Warehouse (ERW) site, session 132: the price board and its markets workbench (/board).
//
// One page holds what /board, /board/v3, the version 4 work and /markets showed. Every figure of a row is in the
// site's own file (data/board.json, written by warehouse/derived/board_page.py); the workbench reads one small file
// a series (public/board/s/<id>.json) and one a power hub (public/board/h/<id>.json) when a row is opened. The
// functions here are pure: the page, the workbench and the tests (scripts/test-board.mjs) share them. Nothing is
// filled: a figure that is not held is null and the page shows a short placeholder. Method: docs/methods/price_board.md.

export type Move = { t: string; v: number; ch: number; pct: number | null };
export type Status = "ok" | "paused" | "licensed" | "not_held" | "working";
export type Row = {
  id: string; group: string; label: string; at: string; code: string; unit: string; freq: "D" | "W" | "M" | "";
  tags: Record<string, string>; status: Status; note?: string; source?: number; formula?: string; also?: string[];
  curve?: { status: Status; note: string }; hourly?: string; hub?: string;
  last?: { t: string; v: number }; moves?: Record<"d" | "w" | "m" | "y", Move | null>;
  range?: { lo: number; hi: number; n: number; pos: number | null } | null;
  avg7?: { v: number; n: number }; avg30?: { v: number; n: number }; lo30?: number; hi30?: number;
  spark?: { t0: string; d: number[]; v: number[] };
};
export type Filter = { key: string; label: string; options: [string, string][]; default: string };
export type Group = { id: string; title: string; filters: Filter[]; curve?: boolean; extra?: string };
export type WeekRow = {
  hub: string; grid: string; label: string; code: string; last_da?: { t: string; v: number };
  means: Record<string, { v: number; ch: number | null; end: string }>;
  max_spread?: { v: number; start: string; end: string }; hours50?: { v: number; start: string; end: string }; vol?: { t: string; v: number };
};
export type Spike = { hub: string; grid: string; label: string; code: string; t: string; v: number; tz: string; freq: string };
export type BoardFile = {
  built: string; sources: string[]; heat_rate: number; coal_heat_rate: number; gas_back_days: number; slack_days: number;
  groups: Group[]; rows: Row[]; week: WeekRow[]; spikes: Spike[];
};
export type SeriesFile = { id: string; label: string; at: string; unit: string; freq: "D" | "W" | "M"; t0: string; d: number[]; v: number[] };
export type HourlyFile = { id: string; tz: string; t0: number; n: number; pk: string; da?: (number | null)[]; rt?: (number | null)[] };
export type Point = { t: number; v: number };

export const DAY = 86_400_000;
export const HOUR = 3_600_000;
export const MOVES = [["d", "Day"], ["w", "Week"], ["m", "Month"], ["y", "Year"]] as const;
export const PLACEHOLDER: Record<Exclude<Status, "ok">, string> = {
  paused: "paused while terms are reviewed", licensed: "licensed source needed", not_held: "not held yet", working: "working on it",
};
export const FREQ_WORDS: Record<string, string> = { D: "daily", W: "weekly", M: "monthly", "": "" };
/** Why a move is blank on a series that is not daily: a weekly series has no daily move, a monthly one no daily or weekly move. */
export const noMove = (freq: string, k: string) => (freq === "W" && k === "d") || (freq === "M" && (k === "d" || k === "w"));

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
  return freq === "M" ? `${MON[m - 1]} ${y}` : `${d} ${MON[m - 1]} ${y}`;
}
export const shortDate = (t: string, freq = "D") => (freq === "M" ? dateWords(t, "M") : dateWords(t).replace(/ \d{4}$/, ""));
export const isoDay = (ms: number) => new Date(ms).toISOString().slice(0, 10);
export const isoHour = (ms: number) => new Date(ms).toISOString().slice(0, 13).replace("T", " ") + ":00 UTC";
/** A UTC hour in a grid's local time, "03 Oct 14:00". */
export function localHour(ms: number, tz: string): string {
  return new Intl.DateTimeFormat("en-GB", { timeZone: tz, day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(ms));
}

/** The rows of a group that the chosen filters let through, in the file's order. */
export function rowsOf(file: BoardFile, group: Group, chosen: Record<string, string>): Row[] {
  return file.rows.filter((r) => (r.group === group.id || r.also?.includes(group.id)) && group.filters.every((f) => {
    const want = chosen[f.key] ?? f.default;
    return want === "all" || r.tags[f.key] === undefined || r.tags[f.key] === want;
  }));
}
/** The last 30 points of a row as [{t, v}]. */
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
