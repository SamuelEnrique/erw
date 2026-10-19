// Energy Research Warehouse (ERW) site, session 318 (the owner's ruling of 13 October 2026: every chart in SVG with
// direct labels): the chart options the analysis engine writes (warehouse/analysis/style.py, lib/findingchart.ts,
// lib/chartforms.ts, components/analysis/MultiChart.tsx: ECharts options) read into the shared SVG set's props
// (components/svgchart.tsx, components/TimeChart.tsx). Pure: no fs, no fetch, no React, so the page, the picker's
// examples and the tests share it. Nothing is computed: every value is the option's own, and a color literal of the
// old palettes is the token components/echarts.ts maps it to (LITERAL_TOKENS), as the brand rule of session 238.
//
// What is read: a category axis with bar, line or area series (stacked where the option stacks them, a second y axis
// where a series names it, a horizontal reference line (markLine on yAxis), a band of categories (markArea on xAxis),
// a marked point (markPoint); a time axis with line series of [time, value] pairs; a value axis with scatter series of
// [x, y] pairs (a line series beside it is a fitted line); and a multi-grid option (several grids, each with its own
// axes) as a column of panels, each a category chart. A range slider, a legend box and a toolbox are not read: the
// shared set's table and direct labels stand in for them. What is not read is said (`unread`), never drawn wrong.
import { LITERAL_TOKENS } from "@/components/echarts";
import type { CatSeries } from "@/components/svgchart";
import type { TimeSeries } from "@/components/TimeChart";

type Opt = Record<string, unknown>;
type Axis = { type?: string; data?: unknown[]; name?: string; gridIndex?: number; position?: string; max?: number | string; min?: number | string } & Opt;
type Ser = { type?: string; name?: string; data?: unknown[]; stack?: string; yAxisIndex?: number; xAxisIndex?: number; areaStyle?: Opt; lineStyle?: Opt; itemStyle?: Opt;
  markLine?: { data?: { yAxis?: number; name?: string; lineStyle?: Opt }[]; label?: Opt; lineStyle?: Opt }; markArea?: { data?: [{ xAxis?: string; yAxis?: number; name?: string }, { xAxis?: string; yAxis?: number }][] };
  markPoint?: { data?: { coord?: [string | number, number]; name?: string }[] }; color?: string; symbolSize?: number } & Opt;

const list = <T,>(v: T | T[] | undefined): T[] => (v === undefined ? [] : Array.isArray(v) ? v : [v]);
const FALLBACK = ["series-1", "series-2", "series-3", "series-4", "series-5", "series-6", "series-7", "series-8"];
/** A color of the option as a token: a literal of the old palettes by the brand's map; a token name as it is; else by place. */
export function colorOf(c: unknown, i: number): string {
  if (typeof c === "string") {
    const t = LITERAL_TOKENS[c.toLowerCase()];
    if (t) return `var(${t})`;
    if (c.startsWith("var(") || c.startsWith("--")) return c.startsWith("--") ? `var(${c})` : c;
  }
  return FALLBACK[i % FALLBACK.length];
}
const seriesColor = (s: Ser, i: number) => colorOf(s.itemStyle?.color ?? s.lineStyle?.color ?? s.color, i);
const numOrNull = (v: unknown): number | null => {
  if (v === null || v === undefined || v === "") return null;
  if (typeof v === "object" && v !== null && "value" in (v as Opt)) return numOrNull((v as Opt).value);
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};
const nameOfAxis = (a: Axis | undefined) => String(a?.name ?? "");

export type CategoryRead = { kind: "category"; x: string[]; series: CatSeries[]; unit: string; unit2: string; refLines: { value: number; name: string; dashed?: boolean }[];
  shade: { from: number; to: number; label: string } | null; marks: { i: number; value: number; label: string }[]; xLabel: string; zero: boolean };
export type TimeRead = { kind: "time"; series: TimeSeries[]; unit: string; unit2: string; x: "minute" | "day" | "month" | "year" };
export type ScatterRead = { kind: "scatter"; points: { name: string; x: number; y: number }[]; xUnit: string; yUnit: string; fit: { x0: number; y0: number; x1: number; y1: number; name: string } | null };
export type PanelsRead = { kind: "panels"; titles: string[]; panels: CategoryRead[] };
export type Read = CategoryRead | TimeRead | ScatterRead | PanelsRead | { kind: "unread"; why: string };

function categoryRead(o: Opt, series: Ser[], xa: Axis | undefined, ys: Axis[]): CategoryRead {
  const x = (xa?.data ?? []).map((v) => String(v));
  const out: CatSeries[] = [];
  const refLines: CategoryRead["refLines"] = [];
  let shade: CategoryRead["shade"] = null;
  const marks: CategoryRead["marks"] = [];
  series.forEach((s, i) => {
    const t = s.type ?? "line";
    if (t !== "bar" && t !== "line") return;
    // a stacked line with an invisible stroke and an area is a band's edge (the supply bands, the board's seasons); the
    // lower edge, stacked under it with no area, carries nothing to draw: it is read as the band's floor
    const invisible = s.lineStyle && Number((s.lineStyle as Opt).opacity ?? 1) === 0;
    const values = (s.data ?? []).map(numOrNull);
    const kind: CatSeries["kind"] = t === "bar" ? "bar" : s.areaStyle ? "area" : "line";
    if (invisible && !s.areaStyle) return;
    out.push({ name: String(s.name ?? `Series ${i + 1}`), color: seriesColor(s, i), values, kind, stack: s.stack ? String(s.stack) : undefined, axis: s.yAxisIndex === 1 ? 1 : 0,
      dash: (s.lineStyle as Opt | undefined)?.type === "dashed" ? "dashed" : undefined, width: typeof (s.lineStyle as Opt | undefined)?.width === "number" ? ((s.lineStyle as Opt).width as number) : undefined });
    for (const m of s.markLine?.data ?? []) if (typeof m.yAxis === "number") refLines.push({ value: m.yAxis, name: String(m.name ?? ""), dashed: (m.lineStyle?.type ?? (s.markLine?.lineStyle as Opt | undefined)?.type) === "dashed" });
    for (const pair of s.markArea?.data ?? []) {
      const [a, b] = pair;
      if (a?.xAxis !== undefined && b?.xAxis !== undefined) { const f = x.indexOf(String(a.xAxis)), to = x.indexOf(String(b.xAxis)); if (f >= 0 && to >= 0) shade = { from: f, to, label: String(a.name ?? "") }; }
    }
    for (const m of s.markPoint?.data ?? []) if (m.coord) { const j = x.indexOf(String(m.coord[0])); if (j >= 0) marks.push({ i: j, value: Number(m.coord[1]), label: String(m.name ?? "") }); }
  });
  const scale = ys.some((y) => y.scale === true);
  return { kind: "category", x, series: out, unit: nameOfAxis(ys[0]), unit2: nameOfAxis(ys[1]), refLines, shade, marks, xLabel: nameOfAxis(xa), zero: !scale };
}

/** The option read into the shared set's props. */
export function readOption(option: unknown): Read {
  const o = (option ?? {}) as Opt;
  const series = list(o.series as Ser | Ser[] | undefined);
  const xs = list(o.xAxis as Axis | Axis[] | undefined), ys = list(o.yAxis as Axis | Axis[] | undefined);
  if (!series.length) return { kind: "unread", why: "the option holds no series" };
  const grids = list(o.grid as Opt | Opt[] | undefined);
  // a multi-grid option: panels, each with its own x axis (by gridIndex), read as a column of category charts
  if (grids.length > 1 && xs.length > 1) {
    const titles = list(o.title as Opt | Opt[] | undefined).map((t) => String(t.text ?? ""));
    const panels = xs.map((xa, g) => {
      const mine = series.filter((s) => (s.xAxisIndex ?? 0) === g).map((s) => ({ ...s, yAxisIndex: (ys.filter((y) => (y.gridIndex ?? 0) === g).findIndex((y) => y === ys[s.yAxisIndex ?? 0]) === 1 ? 1 : 0) }));
      const myYs = ys.filter((y) => (y.gridIndex ?? 0) === g);
      return categoryRead(o, mine, xa, myYs);
    });
    return { kind: "panels", titles, panels };
  }
  const xa = xs[0];
  const kind = xa?.type ?? (xa?.data ? "category" : "value");
  if (kind === "category") return categoryRead(o, series, xa, ys);
  if (kind === "time") {
    const ts: TimeSeries[] = series.filter((s) => (s.type ?? "line") === "line").map((s, i) => ({
      name: String(s.name ?? `Series ${i + 1}`), color: seriesColor(s, i), y2: s.yAxisIndex === 1 || undefined, dashed: (s.lineStyle as Opt | undefined)?.type === "dashed" || undefined,
      points: (s.data ?? []).map((p): [number, number | null] => { const [t, v] = Array.isArray(p) ? p : [null, null]; return [t === null ? NaN : new Date(String(t)).getTime(), numOrNull(v)]; }).filter((p) => Number.isFinite(p[0])),
    }));
    const span = Math.max(0, ...ts.map((s) => (s.points.length ? s.points[s.points.length - 1][0] - s.points[0][0] : 0)));
    return { kind: "time", series: ts, unit: nameOfAxis(ys[0]), unit2: nameOfAxis(ys[1]), x: span > 400 * 86_400_000 ? "month" : span > 3 * 86_400_000 ? "day" : "minute" };
  }
  if (kind === "value") {
    const sc = series.find((s) => s.type === "scatter");
    if (!sc) return { kind: "unread", why: "a value axis with no scatter series" };
    const points = (sc.data ?? []).map((p, i) => {
      const d = (typeof p === "object" && p !== null && !Array.isArray(p) ? (p as Opt) : { value: p }) as { value: unknown; name?: unknown; label?: unknown };
      const [x, y] = Array.isArray(d.value) ? d.value : [null, null];
      return { name: String(d.label ?? d.name ?? `${i + 1}`), x: Number(x), y: Number(y) };
    }).filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y));
    const line = series.find((s) => s.type === "line" && (s.data ?? []).length >= 2);
    const fit = line ? (() => { const d = line.data as [number, number][]; return { x0: Number(d[0][0]), y0: Number(d[0][1]), x1: Number(d[d.length - 1][0]), y1: Number(d[d.length - 1][1]), name: String(line.name ?? "fit") }; })() : null;
    return { kind: "scatter", points, xUnit: nameOfAxis(xa), yUnit: nameOfAxis(ys[0]), fit };
  }
  return { kind: "unread", why: `an axis of type ${kind}` };
}
