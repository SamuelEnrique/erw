// Energy Research Warehouse (ERW) site, session 121: what Ask ERCOT's chart is drawn from, and the check of it.
//
// Pure functions, no imports (Node runs this file as it is, for tests/test_session121.py and
// site/scripts/check-series.mjs). A series is the rows a tool returned for one query; the page draws a line through
// the rows it can place on a time axis. chartPoints is the one place that decides which rows those are, so that the
// page can say how many of the fetched rows the chart shows and name the ones it does not, and so that a test can set
// the drawn points against the fetched rows, value by value.

export type SeriesRow = { key: string; value: number | null; n?: number; at?: string };
export type Point = { t: number; v: number };
export type Drawn = {
  /** the points of the line, in the rows' order */
  points: Point[];
  /** the keys of the rows that are not on the chart, and why: no value held, or a key that is not a time */
  undrawn: { key: string; why: "no value" | "not a time" }[];
};

/** A group key as the tools write it ("2021", "2021-03", "2021-03-05", "2021-03-05 14:00") to seconds. */
export function keySeconds(key: string): number | null {
  const m = key.match(/^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?(?: (\d{2}):00)?$/);
  if (!m) return null;
  return Date.UTC(Number(m[1]), m[2] ? Number(m[2]) - 1 : 0, m[3] ? Number(m[3]) : 1, m[4] ? Number(m[4]) : 0) / 1000;
}

/** Session 161: the group whose keys are the 24 local hours of a day, "00" to "23" (lib/chat/forms.ts, HOUR_OF_DAY). */
export const HOUR_GROUP = "hour_of_day";
/** A key of that group as its hour, 0 to 23; null for anything else. */
export function keyHour(key: string): number | null {
  return /^([01]\d|2[0-3])$/.test(key) ? Number(key) : null;
}
/** Where a row's key stands on the chart's axis: seconds for a time, the hour for the hours of a day (`group`). */
export const keyAt = (key: string, group?: string): number | null => (group === HOUR_GROUP ? keyHour(key) : keySeconds(key));

/** The points a line chart of these rows shows, and the rows it leaves to the table. Nothing is filled between points.
 * `group` is the series' group_by: for the hours of a day a point's t is its hour, 0 to 23, and not a time. */
export function chartPoints(rows: SeriesRow[], group?: string): Drawn {
  const points: Point[] = [], undrawn: Drawn["undrawn"] = [];
  for (const r of rows) {
    const t = keyAt(r.key, group);
    if (r.value === null || r.value === undefined || !Number.isFinite(r.value)) undrawn.push({ key: r.key, why: "no value" });
    else if (t === null) undrawn.push({ key: r.key, why: "not a time" });
    else points.push({ t, v: r.value });
  }
  return { points, undrawn };
}

/** Whether a chart is drawn at all: a series over time with at least two points to join. */
export const isDrawn = (kind: string, d: Drawn): boolean => kind === "line" && d.points.length >= 2;

/** The drawn points against the fetched rows: every point is a fetched row's own key and value, in the rows' order,
 * and every fetched row is either a point or named as not drawn. True when the chart shows the rows and nothing else. */
export function pointsAreRows(rows: SeriesRow[], d: Drawn, group?: string): boolean {
  if (d.points.length + d.undrawn.length !== rows.length) return false;
  let i = 0;
  const left = new Set(d.undrawn.map((u) => u.key));
  for (const r of rows) {
    if (left.has(r.key)) continue;
    const p = d.points[i++];
    if (!p || p.t !== keyAt(r.key, group) || p.v !== r.value) return false;
  }
  return i === d.points.length;
}
