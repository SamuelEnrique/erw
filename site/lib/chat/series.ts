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

/** The points a line chart of these rows shows, and the rows it leaves to the table. Nothing is filled between points. */
export function chartPoints(rows: SeriesRow[]): Drawn {
  const points: Point[] = [], undrawn: Drawn["undrawn"] = [];
  for (const r of rows) {
    const t = keySeconds(r.key);
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
export function pointsAreRows(rows: SeriesRow[], d: Drawn): boolean {
  if (d.points.length + d.undrawn.length !== rows.length) return false;
  let i = 0;
  const left = new Set(d.undrawn.map((u) => u.key));
  for (const r of rows) {
    if (left.has(r.key)) continue;
    const p = d.points[i++];
    if (!p || p.t !== keySeconds(r.key) || p.v !== r.value) return false;
  }
  return i === d.points.length;
}
