// Energy Research Warehouse (ERW) site, session 1155 (chain 077): CAISO's alerts, tied into the Grid tool. Pure
// functions over the rows of caiso_grid_emergencies (events: one row per notice type, region and Pacific day covered,
// from CAISO's Grid Emergencies History Report; docs/methods/california_reliability.md), read by the caller
// (lib/reliability.ts gridNotices). Tested on a committed fixture of real rows (scripts/test-caiso-alerts.mjs,
// scripts/fixtures/caiso_alerts.json). No import: node runs this file with its types stripped, and
// scripts/check-values.mjs imports it to recompute the awe|last and awe|ndays keys by the page's own rule.
//
// What is an alert (docs/methods/scarcity_hours_by_grid.md, "CAISO: an EEA or an alert in force", the same set as the
// table's own_signal): an Energy Emergency Alert (eea_watch, eea1 to eea3) or an alert (flex_alert; and alert, warning,
// stage1 to stage3, CAISO's notices before May 2022). Not alerts, and named apart: restricted maintenance operations
// (rmo: plants asked to put off maintenance) and transmission emergencies (local).
//
// The day: a notice row's day is its Pacific local day (event_date, CAISO's own clock). "Today" is the Pacific day of
// the moment the page was drawn. The table holds what the report printed when it was last read: a day after its newest
// notice is not held, so "no alert today" is said only for a day the table covers.
//
// The keys (scripts/check-values.mjs, family awe, with session 58's awe|days|<type>|<year>):
//   awe|last|<group>|<day>          the newest day on or before <day> with a notice of the group, YYYY-MM-DD (text)
//   awe|ndays|<group>|<from>|<to>   the distinct days from <from> to <to>, both included, with a notice of the group
//   awe|rows|<group>                the rows of the group, every day (session 1166: the Reliability section's "The table
//                                   holds N notices", components/grid/Reliability.tsx)
//   awe|newest|<group>              the newest day of any row of the group, YYYY-MM-DD (text; session 1166: its "the
//                                   latest on <day>")
// A group is one of GROUPS below; "any" is every type, so awe|last|any|<today> is the table's newest notice day.

export const ALERT_TABLE = "caiso_grid_emergencies";
export const ALERT_TZ = "America/Los_Angeles";

export const EEA_TYPES = ["eea_watch", "eea1", "eea2", "eea3"];
export const FLEX_TYPES = ["flex_alert"];
/** CAISO's alert notices before May 2022 (none since) */
export const OLD_ALERT_TYPES = ["alert", "warning", "stage1", "stage2", "stage3"];
/** an EEA or an alert: the set the scarcity table's own_signal counts */
export const SIGNAL_TYPES = [...EEA_TYPES, ...FLEX_TYPES, ...OLD_ALERT_TYPES];

export const GROUPS: Record<string, string[] | null> = {
  any: null,
  signal: SIGNAL_TYPES,
  eea: EEA_TYPES,
  flex_alert: FLEX_TYPES,
  rmo: ["rmo"],
  transmission_emergency: ["transmission_emergency"],
};

export const SHORT: Record<string, string> = {
  flex_alert: "Flex Alert", eea_watch: "EEA Watch", eea1: "EEA 1", eea2: "EEA 2", eea3: "EEA 3", alert: "Alert", warning: "Warning",
  stage1: "Stage 1 emergency", stage2: "Stage 2 emergency", stage3: "Stage 3 emergency", rmo: "Restricted Maintenance Operations",
  transmission_emergency: "Transmission emergency", vlrp: "Voluntary Load Reduction Program", load_interruption: "Load interruption",
};
export const shortName = (t: string) => SHORT[t] ?? t;

export type NoticeLike = { event_date: string; event_type: string; extra?: Record<string, string> | null; region?: string | null };

export const dayOf = (r: NoticeLike) => r.event_date.slice(0, 10);
const regionOf = (r: NoticeLike) => r.region ?? r.extra?.x_region ?? "";

/** Whether a notice type is in a group (an unknown group holds nothing). */
export function inGroup(type: string, group: string): boolean {
  if (!(group in GROUPS)) return false;
  const g = GROUPS[group];
  return g === null || g.includes(type);
}

/** The Pacific day (YYYY-MM-DD) of an instant. */
export function pacificDay(ms: number): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: ALERT_TZ, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(ms));
}

/** The newest day on or before `asOf` with a notice of the group, or null (the awe|last key). */
export function lastDay(rows: NoticeLike[], group: string, asOf: string): string | null {
  let best: string | null = null;
  for (const r of rows) {
    const d = dayOf(r);
    if (d <= asOf && inGroup(r.event_type, group) && (best === null || d > best)) best = d;
  }
  return best;
}

/** The distinct days from `from` to `to` (both included) with a notice of the group (the awe|ndays key). */
export function nDays(rows: NoticeLike[], group: string, from: string, to: string): number {
  const s = new Set<string>();
  for (const r of rows) {
    const d = dayOf(r);
    if (d >= from && d <= to && inGroup(r.event_type, group)) s.add(d);
  }
  return s.size;
}

/** A key's value recomputed from the table's rows, as scripts/check-values.mjs does: awe|last|... and awe|ndays|...;
 *  undefined for another awe key (session 58's awe|days is recomputed there by its own query). */
export function aweValue(rows: NoticeLike[], check: string): string | number | null | undefined {
  const p = check.split("|");
  if (p[0] !== "awe" || !(p[2] in GROUPS)) return undefined;
  if (p[1] === "last" && p.length === 4) return lastDay(rows, p[2], p[3]);
  if (p[1] === "ndays" && p.length === 5) return nDays(rows, p[2], p[3], p[4]);
  // session 1166: every row of the group, and its newest day (no bound: the section counts the whole table)
  if (p[1] === "rows" && p.length === 3) return rows.filter((r) => inGroup(r.event_type, p[2])).length;
  if (p[1] === "newest" && p.length === 3) return lastDay(rows, p[2], "9999-12-31");
  return undefined;
}

export type Fig = { check: string; raw: number | string; tip: string };
export type DayNotices = { day: string; types: string[]; regions: string[]; fig: Fig };

/** The notices of one day of a group: their types (in GROUPS order of the signal first) and regions. */
function onDay(rows: NoticeLike[], group: string, day: string) {
  const types: string[] = [], regions: string[] = [];
  for (const r of rows) {
    if (dayOf(r) !== day || !inGroup(r.event_type, group)) continue;
    if (!types.includes(r.event_type)) types.push(r.event_type);
    const g = regionOf(r);
    if (g && !regions.includes(g)) regions.push(g);
  }
  const order = [...SIGNAL_TYPES, "rmo", "transmission_emergency"];
  types.sort((a, b) => (order.indexOf(a) + 1 || 99) - (order.indexOf(b) + 1 || 99));
  return { types, regions };
}

export type AlertState = {
  /** the Pacific day the page was drawn */
  today: string;
  /** the table's newest notice day (any type), keyed */
  newest: Fig | null;
  /** whether the table covers today (it holds a notice of today or of a later day) */
  covered: boolean;
  /** the alert notices of today, when the table covers today */
  todayAlerts: string[];
  /** the last day with an EEA or an alert, the last Flex Alert, the last EEA, on or before today */
  lastSignal: DayNotices | null;
  lastFlex: DayNotices | null;
  lastEea: DayNotices | null;
  /** not alerts: the last restricted maintenance day and the last transmission emergency day */
  lastRmo: DayNotices | null;
  lastTx: DayNotices | null;
  /** this Pacific year's days with an EEA or an alert, and with restricted maintenance, to today */
  year: string;
  signalDays: Fig;
  rmoDays: Fig;
};

const SRC = `${ALERT_TABLE} (CAISO's Grid Emergencies History Report; one row per notice type, region and Pacific day)`;

/** The state line of CAISO's alerts on the Pacific day of `nowMs`, from every row of the table. */
export function alertState(rows: NoticeLike[], nowMs: number): AlertState {
  const today = pacificDay(nowMs);
  const last = (group: string, what: string): DayNotices | null => {
    const d = lastDay(rows, group, today);
    if (d === null) return null;
    const { types, regions } = onDay(rows, group, d);
    return { day: d, types, regions, fig: { check: `awe|last|${group}|${today}`, raw: d, tip: `${SRC}: the newest Pacific day on or before ${today} with ${what}.` } };
  };
  const top = lastDay(rows, "any", today);
  // the table covers today when it holds a notice of today or of a later day (its newest row, whatever the day)
  const covered = rows.some((r) => dayOf(r) >= today);
  const year = today.slice(0, 4);
  const count = (group: string, what: string): Fig => ({
    check: `awe|ndays|${group}|${year}-01-01|${today}`, raw: nDays(rows, group, `${year}-01-01`, today),
    tip: `${SRC}: the distinct Pacific days from ${year}-01-01 to ${today} with ${what}.`,
  });
  return {
    today,
    newest: top === null ? null : { check: `awe|last|any|${today}`, raw: top, tip: `${SRC}: the newest Pacific day with a notice of any type, on or before ${today}. A later day is not held.` },
    covered,
    todayAlerts: covered ? onDay(rows, "signal", today).types : [],
    lastSignal: last("signal", "an Energy Emergency Alert or an alert (Flex Alert; before May 2022, Alert, Warning or a stage emergency)"),
    lastFlex: last("flex_alert", "a Flex Alert"),
    lastEea: last("eea", "an Energy Emergency Alert (EEA Watch, EEA 1, 2 or 3)"),
    lastRmo: last("rmo", "a Restricted Maintenance Operations notice (not an alert)"),
    lastTx: last("transmission_emergency", "a transmission emergency (not an alert)"),
    year,
    signalDays: count("signal", "an Energy Emergency Alert or an alert"),
    rmoDays: count("rmo", "a Restricted Maintenance Operations notice"),
  };
}

export type AlertDays = {
  /** the column of each day (index into `days`) with an EEA or an alert */
  cols: number[];
  /** each such day's alert types */
  byDay: Map<string, string[]>;
  /** the days of `days` with restricted maintenance or a transmission emergency (not marked) */
  rmo: string[]; tx: string[];
  /** the keyed counts over the days given */
  signal: Fig; rmoFig: Fig;
};

/** The alert days among `days` (YYYY-MM-DD, ascending): the scarcity strip's day axis or a chart's months. A notice's
 *  day is its Pacific local day, set on the column of the same date. */
export function alertDays(rows: NoticeLike[], days: string[]): AlertDays {
  const from = days[0], to = days[days.length - 1];
  const byDay = new Map<string, string[]>();
  const rmo = new Set<string>(), tx = new Set<string>();
  for (const r of rows) {
    const d = dayOf(r);
    if (d < from || d > to) continue;
    if (inGroup(r.event_type, "signal")) { const t = byDay.get(d) ?? []; if (!t.includes(r.event_type)) t.push(r.event_type); byDay.set(d, t); }
    if (r.event_type === "rmo") rmo.add(d);
    if (r.event_type === "transmission_emergency") tx.add(d);
  }
  const cols = days.map((d, j) => (byDay.has(d) ? j : -1)).filter((j) => j >= 0);
  return {
    cols, byDay, rmo: [...rmo].sort(), tx: [...tx].sort(),
    signal: { check: `awe|ndays|signal|${from}|${to}`, raw: nDays(rows, "signal", from, to), tip: `${SRC}: the distinct Pacific days from ${from} to ${to} with an Energy Emergency Alert or an alert.` },
    rmoFig: { check: `awe|ndays|rmo|${from}|${to}`, raw: nDays(rows, "rmo", from, to), tip: `${SRC}: the distinct Pacific days from ${from} to ${to} with a Restricted Maintenance Operations notice (not an alert).` },
  };
}

/** The months (YYYY-MM-01, ascending) with an EEA or an alert day, and each month's alert days: for a monthly chart. */
export function alertMonths(rows: NoticeLike[], months: string[]): { from: string; to: string; months: { month: string; days: string[] }[]; signal: Fig } {
  const from = months[0];
  const lastMonth = months[months.length - 1];
  const y = Number(lastMonth.slice(0, 4)), m = Number(lastMonth.slice(5, 7));
  const to = new Date(Date.UTC(y, m, 0)).toISOString().slice(0, 10);   // the last day of the newest month
  const by = new Map<string, Set<string>>();
  for (const r of rows) {
    const d = dayOf(r);
    if (d < from || d > to || !inGroup(r.event_type, "signal")) continue;
    const k = `${d.slice(0, 7)}-01`;
    (by.get(k) ?? by.set(k, new Set()).get(k)!).add(d);
  }
  return {
    from, to,
    months: months.filter((k) => by.has(k)).map((k) => ({ month: k, days: [...by.get(k)!].sort() })),
    signal: { check: `awe|ndays|signal|${from}|${to}`, raw: nDays(rows, "signal", from, to), tip: `${SRC}: the distinct Pacific days from ${from} to ${to} with an Energy Emergency Alert or an alert.` },
  };
}
