// Energy Research Warehouse (ERW) site, session 182, part 4: the chart forms of Automated Analysis's request flow.
// Step two of the flow asks how an analysis is shown. This file holds the five forms, the rule that says which forms
// can honestly show an analysis's data (the fit), the rule for the default (the form the analysis's own code declares),
// and the drawing of a card's chart spec or of a weekly template's chart in another form. Pure: no fs, no fetch, no
// React, so the page, the picker's examples, the node test and the browser check share it. No form changes a number:
// every drawing reads the values the card's JSON or the template's weekly file holds, and hover shows them.
//
// The default: the form the analysis's own code declares (its chart kind). A timeline or the hours of a day is drawn
// as lines, groups compared side by side as paired bars, parts of one whole as stacked bars, many grids as small
// multiples, two measures of each day as points with a fitted line. The word on the page is "Default for this
// analysis": a default chart form is how the author drew it, it is not advice about energy.
import { optionFor, type ChartSeries, type ChartSpec } from "./findingchart";

export type FormId = "lines" | "bars" | "stacked" | "multiples" | "points";
export type FormDef = { id: FormId; name: string; shows: string; fits: string };
export const MAX_BAR_POSITIONS = 31;   // more positions than a month of days and paired bars are too thin to read
export const MAX_PANELS = 6;           // more panels than this and a small multiple is too small to read
export const FORMS: FormDef[] = [
  { id: "lines", name: "Lines", shows: "Each series is a line along the axis.",
    fits: "An ordered axis (months, years, days, hours of the day) with two positions or more; series in different units only where the analysis's own drawing gives each unit its axis." },
  { id: "bars", name: "Paired bars", shows: "The series stand side by side at each position.",
    fits: `Series in one unit, on at most ${MAX_BAR_POSITIONS} positions.` },
  { id: "stacked", name: "Stacked bars", shows: "The series are stacked into one bar a position.",
    fits: "Series that are parts of one whole (shares that sum to 100 percent, or counts that sum to a total)." },
  { id: "multiples", name: "Small multiples", shows: "One panel a series or a grid, the same axis under all, each panel on its own scale.",
    fits: `Two to ${MAX_PANELS} series or grids.` },
  { id: "points", name: "Points with a fitted line", shows: "One point a day: one measure against the other.",
    fits: "Pairs of two measures. No other form keeps the pairing, so it is the only form of such an analysis." },
];
export const formName = (f: FormId) => FORMS.find((x) => x.id === f)?.name ?? f;
export const isForm = (v: unknown): v is FormId => FORMS.some((f) => f.id === v);

/** The form each chart kind of a finding card declares: the default of an analysis that draws that kind. */
export const NATIVE: Record<string, FormId> = {
  line_with_fleet: "lines", lines: "lines", flag_line: "lines", grouped_bar: "bars", bars_free: "bars", stacked_bar_pct: "stacked", scatter: "points", multiples: "multiples",
};

/** What the fit rule reads of a chart: nothing else decides which forms are offered. */
export type Shape = {
  native: FormId | null;   // the form the analysis's own code declares; null draws nothing (a refused card)
  ordered: boolean;        // the axis is ordered: dates, months, years or hours
  oneUnit: boolean;        // every series is in the same unit
  positions: number;       // positions on the axis
  series: number;          // series, or grids
  whole: boolean;          // the series are parts of one whole
  pairs: boolean;          // pairs of two measures (a scatter)
  fixed: boolean;          // the drawing marks a flagged point or reference lines (a scanner draft): its own form only
};

const ORDERED = /^(\d{4}(-\d{2}){0,2}|\d{1,2}(:00)?)$/;   // 2024, 2024-05, 2024-05-15, 17, 17:00

/** The fit rule: the forms that can honestly show a chart of this shape, the default first. */
export function formsOf(s: Shape): FormId[] {
  if (!s.native) return [];
  if (s.pairs || s.fixed) return [s.native];
  const fit: Record<FormId, boolean> = {
    lines: s.ordered && s.positions >= 2 && (s.oneUnit || s.native === "lines"),
    bars: s.oneUnit && s.positions <= MAX_BAR_POSITIONS,
    stacked: s.whole,
    multiples: s.series >= 2 && s.series <= MAX_PANELS,
    points: false,
  };
  fit[s.native] = true;
  return [s.native, ...FORMS.map((f) => f.id).filter((f) => f !== s.native && fit[f])];
}

// ---- a finding card's chart spec ----

type Multi = {
  kind: "multiples"; x: string[]; x_label: string; measures: { key: string; label: string; unit: string; decimals: number }[];
  panels: { grid: string; words: string; values: Record<string, (number | null)[]> }[];
};
const kindOf = (c: unknown) => (c as { kind?: string } | null)?.kind ?? "none";
export const isMulti = (c: unknown): boolean => kindOf(c) === "multiples";
/** A card of many grids as such (the card's type does not name the kind; MultiChart draws it), else null. */
export const asMulti = (c: unknown): Multi | null => (isMulti(c) ? (c as Multi) : null);
const allOrdered = (x: unknown[]) => x.length > 0 && x.every((v) => ORDERED.test(String(v)));

export function shapeOfSpec(c: ChartSpec): Shape {
  const m = asMulti(c);
  if (m) return { native: "multiples", ordered: allOrdered(m.x), oneUnit: true, positions: m.x.length, series: m.panels.length, whole: false, pairs: false, fixed: false };
  const kind = kindOf(c);
  const series = c.series ?? [];
  return {
    native: NATIVE[kind] ?? null, ordered: allOrdered(c.x ?? []), oneUnit: new Set(series.map((s) => s.unit)).size <= 1, positions: (c.x ?? []).length, series: series.length,
    whole: kind === "stacked_bar_pct", pairs: kind === "scatter", fixed: Boolean(c.mark || c.ref_lines?.length),
  };
}
export const formsOfSpec = (c: ChartSpec) => formsOf(shapeOfSpec(c));

const INK = "#1a1a1a", MUTED = "#6b6b6b", RULE = "#e5e5e5", MARK = "#c4541c";
const PALETTE = ["#1f5f8b", "#c4541c", "#2e7d4f", "#8a6d3b", "#6a4c93", "#9a9a9a"];
const fmt = (v: number | null | undefined, nd = 1) => (v === null || v === undefined || Number.isNaN(v) ? "not held" : v.toLocaleString("en-US", { maximumFractionDigits: nd, minimumFractionDigits: nd }));
const decimalsOf = (unit: string, nd: number) => (unit === "MW" ? 0 : unit === "hours" ? 2 : nd);

const SMALL_TITLE_ROW = 28;
type Panel = { title: string; unit: string; values: (number | null)[]; type: "line" | "bar"; decimals?: number };
type Opt = Record<string, unknown>;

/** Small multiples as one ECharts option: one panel a series, the same axis under all, each panel on its own scale. */
export function panelsOption(d: { x: string[]; xLabel: string; panels: Panel[]; decimals?: number }, H: number, small = false): Opt {
  const n = d.panels.length, nd = d.decimals ?? 1;
  const top0 = small ? 2 : 6, bottom = small ? 16 : 44, left = small ? 34 : 64, right = small ? 6 : 24;
  const rowH = (H - top0 - bottom) / Math.max(1, n);
  const titled = !small || rowH >= SMALL_TITLE_ROW;   // an example's rows too short for a title carry none: hover names the panel
  const head = !titled ? 2 : small ? 11 : 17;
  const label = { color: MUTED, fontSize: small ? 8 : 10, hideOverlap: true };
  return {
    animation: false,
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: INK },
    title: d.panels.map((p, i) => ({ show: titled, text: small ? p.title : `${p.title}${p.unit ? `, ${p.unit}` : ""}`, left, top: top0 + i * rowH,
      textStyle: { fontSize: small ? 8 : 11, fontWeight: 600, color: INK, width: small ? 120 : 600, overflow: "truncate" } })),
    grid: d.panels.map((_, i) => ({ left, right, top: top0 + i * rowH + head, height: Math.max(8, rowH - head - (small ? 3 : 10)) })),
    axisPointer: { link: [{ xAxisIndex: "all" }] },
    tooltip: { trigger: "axis", confine: true, formatter: (ps: { dataIndex: number }[]) => {
      const i = ps[0]?.dataIndex ?? 0;
      return [d.x[i], ...d.panels.map((p) => `${p.title}: ${fmt(p.values[i], p.decimals ?? decimalsOf(p.unit, nd))} ${p.unit}`)].join("<br/>");
    } },
    xAxis: d.panels.map((_, i) => ({ type: "category", gridIndex: i, data: d.x, axisLabel: { ...label, show: i === n - 1 }, axisTick: { show: false }, axisLine: { lineStyle: { color: RULE } },
      name: i === n - 1 && !small ? d.xLabel : "", nameLocation: "middle", nameGap: 26, nameTextStyle: { color: MUTED, fontSize: 10 } })),
    yAxis: d.panels.map((_, i) => ({ type: "value", gridIndex: i, splitNumber: 2, axisLabel: label, splitLine: { lineStyle: { color: RULE } } })),
    series: d.panels.map((p, i) => ({ name: p.title, type: p.type, xAxisIndex: i, yAxisIndex: i, data: p.values, showSymbol: !small && d.x.length <= 30, symbolSize: 4, connectNulls: false,
      lineStyle: { width: 1.5, color: PALETTE[i % PALETTE.length] }, itemStyle: { color: PALETTE[i % PALETTE.length] } })),
  };
}

/** The impact study's band of days after the event, carried into every form so that "the days are marked" stays true. */
function withBand(o: Opt, c: ChartSpec, every = false, small = false): Opt {
  const area = c.mark_area;
  if (!area) return o;
  const from = c.x.find((d) => d >= area.from) ?? c.x[c.x.length - 1];
  const to = [...c.x].reverse().find((d) => d <= area.to) ?? c.x[c.x.length - 1];
  const band = { silent: true, itemStyle: { color: MARK, opacity: 0.1 }, label: { show: !small, color: MUTED, fontSize: 10 }, data: [[{ xAxis: from, name: area.label }, { xAxis: to }]] };
  return { ...o, series: (o.series as Opt[]).map((s, i) => (i === 0 || every ? { ...s, markArea: band } : s)) };
}

/** The series a spec holds, as plain series: for a card of many grids, one series a grid for the chosen measure. */
export function plainSeries(c: ChartSpec, measure?: string): { x: string[]; xLabel: string; yLabel: string; decimals: number; suffix: string; series: ChartSeries[] } {
  const multi = asMulti(c);
  if (multi) {
    const m = multi.measures.find((x) => x.key === measure) ?? multi.measures[0];
    return { x: multi.x, xLabel: multi.x_label, yLabel: `${m.label}, ${m.unit}`, decimals: m.decimals, suffix: ` ${m.unit}`,
      series: multi.panels.map((p) => ({ name: p.words, type: "line", unit: m.unit, values: p.values[m.key] ?? [] })) };
  }
  const series = c.series.map((s) => ({ name: s.name, type: s.type, unit: s.unit, values: s.values }));
  return { x: c.x, xLabel: c.x_label, yLabel: c.y_left_label ?? "", decimals: c.decimals ?? 1, suffix: c.value_suffix ?? (series[0]?.unit ? ` ${series[0].unit}` : ""), series };
}

/** A card's chart in a form, as an ECharts option; null when the form does not fit, or when the form is the card's own
 *  small multiples (drawn by MultiChart, which also holds the one-grid view). */
export function specOption(c: ChartSpec, form: FormId, H = 340, measure?: string, small = false): Opt | null {
  const shape = shapeOfSpec(c);
  if (!formsOf(shape).includes(form)) return null;
  if (form === shape.native && !isMulti(c)) return optionFor(c);
  const p = plainSeries(c, measure);
  if (form === "multiples") {
    if (isMulti(c) && !small) return null;
    const o = panelsOption({ x: p.x, xLabel: p.xLabel, decimals: p.decimals, panels: p.series.map((s) => ({ title: s.name, unit: s.unit, values: s.values, type: s.type, decimals: isMulti(c) ? p.decimals : undefined })) }, H, small);
    return isMulti(c) ? o : withBand(o, c, true, small);
  }
  if (form !== "lines" && form !== "bars") return null;
  // the vertical axis's name is a caption the page prints above the chart (plainSeries().yLabel), not a name on the
  // axis: a long name on the axis was cut at the left edge and ran into the legend on a phone
  const drawn = optionFor({ kind: form === "lines" ? "lines" : "bars_free", x: p.x, x_label: p.xLabel, series: p.series, y_left_label: "", decimals: p.decimals, value_suffix: p.suffix });
  const o = { ...drawn, grid: { ...(drawn.grid as Opt), top: 52 } };
  return isMulti(c) ? o : withBand(o, c);
}

// ---- a weekly template's chart (the ECharts option warehouse/analysis/style.py wrote) ----

type Axis = { type?: string; data?: unknown[]; name?: string; axisLabel?: Opt } & Opt;
type Ser = { type?: string; name?: string; data?: unknown[]; stack?: string; yAxisIndex?: number } & Opt;
const one = <T,>(v: T | T[] | undefined): T | undefined => (Array.isArray(v) ? v[0] : v);

export function shapeOfOption(o: Opt): Shape {
  const series = (o.series ?? []) as Ser[];
  const xa = one(o.xAxis as Axis | Axis[] | undefined);
  const types = new Set(series.map((s) => s.type));
  const whole = series.some((s) => Boolean(s.stack));
  const native: FormId = types.has("scatter") ? "points" : types.has("bar") ? (whole ? "stacked" : "bars") : "lines";
  const cats = xa?.type === "category" ? xa.data ?? [] : [];
  return {
    native, ordered: xa?.type === "time" || allOrdered(cats), oneUnit: !(Array.isArray(o.yAxis) && o.yAxis.length > 1),
    positions: xa?.type === "category" ? cats.length : Math.max(0, ...series.map((s) => (s.data ?? []).length)), series: series.length, whole, pairs: native === "points", fixed: false,
  };
}
export const formsOfOption = (o: Opt) => formsOf(shapeOfOption(o));

/** A template's chart in a form: the same option with its series redrawn; null when the form does not fit. */
export function reformOption(o: Opt, form: FormId, H = 360, small = false): Opt | null {
  const shape = shapeOfOption(o);
  if (!formsOf(shape).includes(form)) return null;
  if (form === shape.native) return o;
  const series = (o.series ?? []) as Ser[];
  if (form === "lines") return { ...o, series: series.map((s) => ({ ...s, stack: undefined, type: "line", showSymbol: true, symbolSize: 5 })) };
  if (form === "bars") return { ...o, series: series.map((s) => ({ ...s, stack: undefined, areaStyle: undefined, type: "bar" })) };
  if (form !== "multiples") return null;
  const n = series.length;
  const ys = (Array.isArray(o.yAxis) ? o.yAxis : [o.yAxis]) as Axis[];
  const xa = one(o.xAxis as Axis | Axis[]) ?? {};
  const top0 = small ? 2 : 30, bottom = small ? 16 : 44, head = small ? 11 : 18, left = small ? 34 : 64, right = small ? 6 : 24;
  const rowH = (H - top0 - bottom) / Math.max(1, n);
  const unit = (s: Ser) => ys[s.yAxisIndex ?? 0]?.name ?? "";
  return {
    ...o, legend: { show: false }, dataZoom: undefined, ...(small ? { toolbox: undefined } : {}),
    title: series.map((s, i) => ({ text: small || !unit(s) || String(s.name).includes(unit(s)) ? s.name : `${s.name}, ${unit(s)}`, left, top: top0 + i * rowH,
      textStyle: { fontSize: small ? 8 : 11, fontWeight: 600, color: "#2E2D29", width: small ? 120 : 600, overflow: "truncate" } })),
    grid: series.map((_, i) => ({ left, right, top: top0 + i * rowH + head, height: Math.max(8, rowH - head - (small ? 3 : 10)) })),
    axisPointer: { link: [{ xAxisIndex: "all" }] },
    xAxis: series.map((_, i) => ({ ...xa, gridIndex: i, name: i === n - 1 && !small ? xa.name : "", axisLabel: { ...(xa.axisLabel ?? {}), show: i === n - 1, ...(small ? { fontSize: 8 } : {}) } })),
    yAxis: series.map((s, i) => { const y = ys[s.yAxisIndex ?? 0] ?? {}; return { ...y, gridIndex: i, name: "", splitNumber: 2, axisLabel: { ...(y.axisLabel ?? {}), ...(small ? { fontSize: 8 } : {}) } }; }),
    series: series.map((s, i) => ({ ...s, stack: undefined, xAxisIndex: i, yAxisIndex: i })),
  };
}

// ---- the picker's examples: the same drawings, small ----

/** An option made small for the picker: no legend, no toolbox, no axis names, small labels. Hover is kept. */
export function compact(o: Opt): Opt {
  const small = (a: Axis | undefined): Axis => ({ ...(a ?? {}), name: "", splitNumber: 2, axisLabel: { ...(a?.axisLabel ?? {}), fontSize: 8, hideOverlap: true } });
  const axes = (a: unknown) => (Array.isArray(a) ? (a as Axis[]).map(small) : small(a as Axis | undefined));
  return {
    ...o, legend: { show: false }, toolbox: undefined, dataZoom: undefined, grid: { left: 4, right: 8, top: 8, bottom: 2, containLabel: true },
    xAxis: axes(o.xAxis), yAxis: axes(o.yAxis),
    series: ((o.series ?? []) as Ser[]).map((s) => ({ ...s, ...(s.type === "line" ? { showSymbol: false } : {}), ...(s.type === "scatter" ? { symbolSize: 3 } : {}),
      ...(s.markLine ? { markLine: { ...(s.markLine as Opt), label: { show: false } } } : {}), ...(s.markArea ? { markArea: { ...(s.markArea as Opt), label: { show: false } } } : {}) })),
  };
}

/** The example of a form for a card's chart: the card's own data, drawn small. */
export function thumbOfSpec(c: ChartSpec, form: FormId, H: number): Opt | null {
  if (form === "multiples") return specOption(c, form, H, undefined, true);
  const o = specOption(c, form, H);
  return o ? compact(o) : null;
}

/** The example of a form for a template's chart: the week's own data for the chosen inputs, drawn small. */
export function thumbOfOption(o: Opt, form: FormId, H: number): Opt | null {
  if (form === "multiples" && shapeOfOption(o).native !== "multiples") return reformOption(o, form, H, true);
  const r = reformOption(o, form, H);
  return r ? compact(r) : null;
}
