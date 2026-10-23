// Energy Research Warehouse (ERW) site, session 1142 (chain 076's session 1130): the general chat's chart. Ask ERCOT has
// drawn the series an answer rests on since session 92 (lib/chat/ercot.ts seriesOf); the general chat drew none. Its
// answer now carries one series when it rests on one: the last result grouped by time (year, month, day or hour) of a
// table the answer cites, with at least three rows, its rows the tool's own, key by key and value by value, checked as
// Ask ERCOT's are (lib/chat/series.ts chartPoints, pointsAreRows). An answer that cites no such result carries none:
// never a chart for its own sake (session 137). Pure: no request.
import { chartPoints, pointsAreRows, type SeriesRow } from "./series";

type Json = Record<string, unknown>;
export type GeneralSeries = {
  result_id: string; table: string; title: string; group_by: string; kind: "line"; unit: string | null; rows: SeriesRow[];
  rows_matched: number | null; note: string | null; source_report: string | null; license: string | null; tier: string | null; chosen_by: string;
  check: { rows_fetched: number; rows: number; same: boolean; points: number; not_drawn: number };
};
export const TIME_GROUPS = ["year", "month", "day", "hour"];
export const MIN_ROWS = 3;

/** One query result as a series, or null when it is not one a line can show. */
export function seriesOfResult(n: number, args: Json, out: Json): GeneralSeries | null {
  const g = typeof args.group_by === "string" ? args.group_by : "";
  const result = out.result as Json[] | undefined;
  if (!TIME_GROUPS.includes(g) || !Array.isArray(result) || result.length < MIN_ROWS || typeof out.table !== "string") return null;
  const rows: SeriesRow[] = result.map((r) => ({
    key: String(r[g]), value: (typeof r.value === "number" ? r.value : typeof r.count === "number" ? r.count : null),
    ...(typeof r.n === "number" ? { n: r.n } : {}), ...(typeof r.at === "string" ? { at: r.at } : {}),
  }));
  const drawn = chartPoints(rows, g);
  const what = args.aggregation === "count" ? "count of rows" : `${args.aggregation} of ${args.variable ?? out.value_column ?? "value"}`;
  const units = (out.units as string[] | undefined) ?? [];
  return {
    result_id: `q${n}`, table: out.table, title: `${what}${args.entity ? `, ${args.entity}` : ""}, by ${g}`, group_by: g, kind: "line",
    unit: units.length === 1 ? units[0] : null, rows, rows_matched: typeof out.rows_matched === "number" ? out.rows_matched : null,
    note: typeof out.result_note === "string" ? out.result_note : null, source_report: typeof out.source_report === "string" ? out.source_report : null,
    license: typeof out.license === "string" ? out.license : null, tier: typeof out.tier === "string" ? out.tier : null,
    chosen_by: "the last result grouped by time of a table the answer cites",
    check: { rows_fetched: result.length, rows: rows.length, same: rows.length === result.length && pointsAreRows(rows, drawn, g), points: drawn.points.length, not_drawn: drawn.undrawn.length },
  };
}

/** The series an answer rests on: the last one of a cited table, or none. */
export function answerSeries(results: { tool: string; input: Json; out: Json }[], cited: string[]): GeneralSeries[] {
  const want = new Set(cited);
  const all = results.flatMap((r, i) => {
    if (r.tool === "query") { const s = seriesOfResult(i + 1, r.input, r.out); return s ? [s] : []; }
    if (r.tool === "compare") return (["a", "b"] as const).flatMap((k) => { const s = seriesOfResult(i + 1, (r.input[k] as Json) ?? {}, (r.out[k] as Json) ?? {}); return s ? [{ ...s, result_id: `q${i + 1}${k}` }] : []; });
    return [];
  }).filter((s) => want.has(s.table) && s.check.same && s.check.points >= 2);
  return all.slice(-1);
}
