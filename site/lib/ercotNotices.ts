// Energy Research Warehouse (ERW) site, session 1174 (chain 078): ERCOT's grid notices, tied into the Grid tool as
// CAISO's alerts are (session 1155, lib/caisoAlerts.ts). Pure functions over the rows of ercot_grid_notices (events: one
// row per notice and Central day it covers, from ERCOT's news releases since 2011 and its control room's operations
// messages since May 2026; docs/methods/ercot_grid_notices.md), read by the caller (lib/gridErcotNotices.ts). Tested on
// a committed fixture of real rows (scripts/test-ercot-notices.mjs, scripts/fixtures/ercot_notices.json). No import:
// node runs this file with its types stripped, and scripts/check-values.mjs imports it to recompute the ercotn| keys by
// the page's own rule.
//
// What is a call (the method's x_counts): a system-wide call on supply or demand, the notices grid_stress_days counts:
// an EEA level or rotating outages, a conservation appeal or a Voluntary Conservation Notice, a Power or Weather Watch,
// an Operating Condition Notice (OCN) for extreme weather, and a release ending an emergency (it was in force that day).
// Not calls, and named apart: the control room's Advisories and Watches on its own tools, tests, statements, other
// updates, and notices for the Rio Grande Valley only (x_counts "no").
//
// The day: a row's day is the Central day it covers (event_date, ERCOT's own clock, stored as midnight UTC). "Today"
// is the Central day of the moment the page was drawn. The table holds what ERCOT's pages showed when the ERW last read
// them: a day after its newest notice is not held, so "none in force today" is said only for a day the table covers.
//
// The keys (scripts/check-values.mjs, family ercotn):
//   ercotn|last|<group>|<day>          the newest day on or before <day> with a notice of the group, YYYY-MM-DD (text)
//   ercotn|ndays|<group>|<from>|<to>   the distinct days from <from> to <to>, both included, with a notice of the group
//   ercotn|read                        the UTC day of the newest retrieved_at of the rows: when the ERW last read ERCOT's pages
// A group is one of GROUPS below; "any" is every row, so ercotn|last|any|<today> is the table's newest notice day.

export const NOTICE_TABLE = "ercot_grid_notices";
export const NOTICE_TZ = "America/Chicago";

/** The kinds of a call, each a group of its own (the counted rows of these types) */
export const KINDS: Record<string, string[]> = {
  eea: ["eea3", "rotating_outages", "eea2", "eea1"],
  conservation: ["conservation_appeal", "voluntary_conservation"],
  watch: ["power_watch", "weather_watch"],
  ocn: ["ocn_weather"],
};
/** the groups a key may name: every row, the calls, each kind of call, and the rows that are not calls */
export const GROUPS = ["any", "call", ...Object.keys(KINDS), "other"];

export const KIND_NAME: Record<string, string> = {
  eea: "an Energy Emergency Alert or rotating outages",
  conservation: "a conservation appeal (or a Voluntary Conservation Notice)",
  watch: "a Weather Watch (in 2011, a Power Watch)",
  ocn: "an Operating Condition Notice for extreme weather",
};

export const SHORT: Record<string, string> = {
  eea3: "EEA 3", rotating_outages: "rotating outages", eea2: "EEA 2", eea1: "EEA 1", conservation_appeal: "conservation appeal",
  voluntary_conservation: "Voluntary Conservation Notice", power_watch: "Power Watch", weather_watch: "Weather Watch",
  ocn_weather: "OCN for extreme weather", update: "a notice ended or cancelled", ocn: "OCN", advisory: "Advisory", watch: "Watch",
  emergency_notice: "Emergency Notice", emergency_test: "test of the emergency notices", statement: "statement",
};
export const shortName = (t: string) => SHORT[t] ?? t;
const ORDER = [...KINDS.eea, ...KINDS.conservation, ...KINDS.watch, ...KINDS.ocn, "emergency_notice", "advisory", "watch", "ocn", "emergency_test", "statement", "update"];

export type NoticeLike = { event_date: string; event_type: string; extra?: Record<string, string> | null };

export const dayOf = (r: NoticeLike) => r.event_date.slice(0, 10);
const counted = (r: NoticeLike) => r.extra?.x_counts === "yes";
const regionOf = (r: NoticeLike) => r.extra?.x_region ?? "";

/** Whether a row is in a group (an unknown group holds nothing). */
export function inGroup(r: NoticeLike, group: string): boolean {
  if (group === "any") return true;
  if (group === "call") return counted(r);
  if (group === "other") return !counted(r);
  const k = KINDS[group];
  return Array.isArray(k) && counted(r) && k.includes(r.event_type);
}

/** The Central day (YYYY-MM-DD) of an instant. */
export function centralDay(ms: number): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: NOTICE_TZ, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(ms));
}

/** The newest day on or before `asOf` with a notice of the group, or null (the ercotn|last key). */
export function lastDay(rows: NoticeLike[], group: string, asOf: string): string | null {
  let best: string | null = null;
  for (const r of rows) {
    const d = dayOf(r);
    if (d <= asOf && inGroup(r, group) && (best === null || d > best)) best = d;
  }
  return best;
}

/** The distinct days from `from` to `to` (both included) with a notice of the group (the ercotn|ndays key). */
export function nDays(rows: NoticeLike[], group: string, from: string, to: string): number {
  const s = new Set<string>();
  for (const r of rows) {
    const d = dayOf(r);
    if (d >= from && d <= to && inGroup(r, group)) s.add(d);
  }
  return s.size;
}

/** The UTC day of the newest retrieved_at of the rows (the ercotn|read key), or null. */
export function readDay(rows: NoticeLike[]): string | null {
  let best: string | null = null;
  for (const r of rows) {
    const t = r.extra?.retrieved_at;
    if (typeof t === "string" && t.length >= 10 && (best === null || t > best)) best = t;
  }
  return best === null ? null : best.slice(0, 10);
}

/** A key's value recomputed from the table's rows, as scripts/check-values.mjs does; undefined for a key it does not know. */
export function ercotnValue(rows: NoticeLike[], check: string): string | number | null | undefined {
  const p = check.split("|");
  if (p[0] !== "ercotn") return undefined;
  if (p[1] === "read" && p.length === 2) return readDay(rows);
  if (!GROUPS.includes(p[2])) return undefined;
  if (p[1] === "last" && p.length === 4) return lastDay(rows, p[2], p[3]);
  if (p[1] === "ndays" && p.length === 5) return nDays(rows, p[2], p[3], p[4]);
  return undefined;
}

export type Fig = { check: string; raw: number | string; tip: string };
export type DayNotices = { day: string; types: string[]; regions: string[]; fig: Fig };

const sortTypes = (types: string[]) => types.sort((a, b) => (ORDER.indexOf(a) + 1 || 99) - (ORDER.indexOf(b) + 1 || 99));

/** The notices of one day of a group: their types (in ORDER, the gravest first) and regions. */
function onDay(rows: NoticeLike[], group: string, day: string) {
  const types: string[] = [], regions: string[] = [];
  for (const r of rows) {
    if (dayOf(r) !== day || !inGroup(r, group)) continue;
    if (!types.includes(r.event_type)) types.push(r.event_type);
    const g = regionOf(r);
    if (g && !regions.includes(g)) regions.push(g);
  }
  return { types: sortTypes(types), regions };
}

export type NoticeState = {
  /** the Central day the page was drawn */
  today: string;
  /** the table's newest notice day (any row), keyed */
  newest: Fig | null;
  /** the UTC day the ERW last read ERCOT's pages, keyed */
  read: Fig | null;
  /** whether the table covers today (it holds a notice of today or of a later day) */
  covered: boolean;
  /** the calls of today, when the table covers today */
  todayCalls: string[];
  /** the last day with a call, and the last day of each kind of call, on or before today */
  lastCall: DayNotices | null;
  kinds: { kind: string; name: string; last: DayNotices | null }[];
  /** not calls: the last day with one */
  lastOther: DayNotices | null;
  /** this Central year's days with a call, and with a notice that is not one, to today */
  year: string;
  callDays: Fig;
  otherDays: Fig;
};

const SRC = `${NOTICE_TABLE} (ERCOT's news releases since 2011 and its control room's messages since May 2026; one row per notice and Central day it covers)`;
const CALL = "a call on supply or demand (an EEA or rotating outages, a conservation appeal, a watch, an OCN for extreme weather, or the end of an emergency)";
const OTHER = "a notice that is not a call (an Advisory or Watch on the control room's own tools, a test, a statement, an update, or a notice for the Rio Grande Valley only)";

/** The state line of ERCOT's notices on the Central day of `nowMs`, from every row of the table. */
export function noticeState(rows: NoticeLike[], nowMs: number): NoticeState {
  const today = centralDay(nowMs);
  const last = (group: string, what: string): DayNotices | null => {
    const d = lastDay(rows, group, today);
    if (d === null) return null;
    const { types, regions } = onDay(rows, group, d);
    return { day: d, types, regions, fig: { check: `ercotn|last|${group}|${today}`, raw: d, tip: `${SRC}: the newest Central day on or before ${today} with ${what}.` } };
  };
  const top = lastDay(rows, "any", today);
  const rd = readDay(rows);
  const covered = rows.some((r) => dayOf(r) >= today);
  const year = today.slice(0, 4);
  const count = (group: string, what: string): Fig => ({
    check: `ercotn|ndays|${group}|${year}-01-01|${today}`, raw: nDays(rows, group, `${year}-01-01`, today),
    tip: `${SRC}: the distinct Central days from ${year}-01-01 to ${today} with ${what}.`,
  });
  return {
    today,
    newest: top === null ? null : { check: `ercotn|last|any|${today}`, raw: top, tip: `${SRC}: the newest Central day with a notice of any kind, on or before ${today}. A later day is not held.` },
    read: rd === null ? null : { check: "ercotn|read", raw: rd, tip: `${SRC}: the UTC day of the newest retrieved_at of its rows, when the ERW last read ERCOT's pages (each read rewrites every row's).` },
    covered,
    todayCalls: covered ? onDay(rows, "call", today).types : [],
    lastCall: last("call", CALL),
    kinds: Object.keys(KINDS).map((k) => ({ kind: k, name: KIND_NAME[k], last: last(k, KIND_NAME[k]) })),
    lastOther: last("other", OTHER),
    year,
    callDays: count("call", CALL),
    otherDays: count("other", OTHER),
  };
}

export type CallDays = {
  /** the column of each day (index into `days`) with a call */
  cols: number[];
  /** each such day's call types */
  byDay: Map<string, string[]>;
  /** the days of `days` with a notice that is not a call (not marked) */
  other: string[];
  /** the keyed counts over the days given */
  call: Fig; otherFig: Fig;
};

/** The call days among `days` (YYYY-MM-DD, ascending): the scarcity strip's day axis. A notice's day is its Central
 *  local day, set on the column of the same date (the strip's days are Central standard time days). */
export function callDays(rows: NoticeLike[], days: string[]): CallDays {
  const from = days[0], to = days[days.length - 1];
  const byDay = new Map<string, string[]>();
  const other = new Set<string>();
  for (const r of rows) {
    const d = dayOf(r);
    if (d < from || d > to) continue;
    if (inGroup(r, "call")) { const t = byDay.get(d) ?? []; if (!t.includes(r.event_type)) t.push(r.event_type); byDay.set(d, t); }
    else other.add(d);
  }
  for (const t of byDay.values()) sortTypes(t);
  const cols = days.map((d, j) => (byDay.has(d) ? j : -1)).filter((j) => j >= 0);
  return {
    cols, byDay, other: [...other].sort(),
    call: { check: `ercotn|ndays|call|${from}|${to}`, raw: nDays(rows, "call", from, to), tip: `${SRC}: the distinct Central days from ${from} to ${to} with ${CALL}.` },
    otherFig: { check: `ercotn|ndays|other|${from}|${to}`, raw: nDays(rows, "other", from, to), tip: `${SRC}: the distinct Central days from ${from} to ${to} with ${OTHER}.` },
  };
}

/** The months (YYYY-MM-01, ascending) with a call day, and each month's call days: for a monthly chart. */
export function callMonths(rows: NoticeLike[], months: string[]): { from: string; to: string; months: { month: string; days: string[] }[]; call: Fig } {
  const from = months[0];
  const lastMonth = months[months.length - 1];
  const y = Number(lastMonth.slice(0, 4)), m = Number(lastMonth.slice(5, 7));
  const to = new Date(Date.UTC(y, m, 0)).toISOString().slice(0, 10);   // the last day of the newest month
  const by = new Map<string, Set<string>>();
  for (const r of rows) {
    const d = dayOf(r);
    if (d < from || d > to || !inGroup(r, "call")) continue;
    const k = `${d.slice(0, 7)}-01`;
    (by.get(k) ?? by.set(k, new Set()).get(k)!).add(d);
  }
  return {
    from, to,
    months: months.filter((k) => by.has(k)).map((k) => ({ month: k, days: [...by.get(k)!].sort() })),
    call: { check: `ercotn|ndays|call|${from}|${to}`, raw: nDays(rows, "call", from, to), tip: `${SRC}: the distinct Central days from ${from} to ${to} with ${CALL}.` },
  };
}
