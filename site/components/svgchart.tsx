"use client";
// Energy Research Warehouse (ERW) site, session 317 (the owner's ruling of 13 October 2026: every chart in SVG with
// direct labels, in the brand's manner; session 303 moved the time-series chart, this session the rest). One shared
// component per kind, drawn in plain SVG, the brand's tokens only (no hex value is written here), each with a Chart |
// Table toggle, a hover card on fog with a rule-colored edge, the series named on the chart in their own colors (no
// legend box), the axis text 12 px that does not shrink (the chart is drawn for the width it measures and drawn again
// when it changes), and no number computed here: the page hands every value. The pages' own chart files
// (app/curtailment/Charts.tsx, components/mix/Charts.tsx, components/supply/SupplyCharts.tsx, components/BoxChart.tsx,
// app/cost-of-power/charts.tsx, LoadCharts.tsx, seller/SellerCharts.tsx) keep their names and props and draw through
// these, so no page changed its data or its numbers.
//
//   CategoryChart  bars, lines and areas over a category axis, stacked where asked, a second axis at the right, a
//                  category drawn faint (dim), a note per category in the hover; the kind of the canvas's XY, Lines,
//                  Bars and HourStack
//   HeatChart      a grid of cells, rows by columns, one sequential color (the accent at a strength by value) over
//                  the panel, a cell with no value hatched; the hover is the cell's own text where the page has one
//   BandChart      a series through its year against a band (lowest to highest of the years before), a dashed mean,
//                  last year thin, this year bold
//   ScatterChart   points with their names beside them
//   BoxPlot        five-number summaries as horizontal boxes on one scale
//
// What the canvas had and these do not: the range slider and the PNG download (the table stands in for both; a
// slider is the next ruling's).
import { useEffect, useRef, useState, type ReactNode } from "react";
import { emptyCell, scrollRegion } from "@/lib/cells";   // session 412: an empty header cell is a plain cell
import { stackNames, wrapName } from "@/lib/chartwrap";   // session 370: the names at the right in lines that fit

export const tokenColor = (c: string) => (c.startsWith("var(") ? c : c.startsWith("--") ? `var(${c})` : c.startsWith("series-") ? `var(--chart-${c})` : /^#|^rgb/.test(c) ? c : `var(--color-${c})`);
export const num = (v: number, digits?: number) => (digits === undefined
  ? v.toLocaleString("en-US", { maximumFractionDigits: Math.abs(v) >= 100 ? 0 : 2 })
  : v.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits }));
const axisNum = (v: number) => (Math.abs(v) >= 1e9 ? `${+(v / 1e9).toFixed(2)}B` : Math.abs(v) >= 1e6 ? `${+(v / 1e6).toFixed(2)}M` : Math.abs(v) >= 1e4 ? `${+(v / 1e3).toFixed(1)}k` : num(v));
const textWidth = (s: string, size = 12) => s.length * size * 0.56;
/** The axis step: 1, 2, 2.5 or 5 times a power of ten, the smallest that draws at most five steps over the span. */
export const nice = (span: number): number => {
  if (!(span > 0)) return 1;
  const p = 10 ** Math.floor(Math.log10(span / 5));
  for (const m of [1, 2, 2.5, 5, 10]) if (span / (m * p) <= 5) return m * p;
  return 10 * p;
};
type Bounds = { lo: number; hi: number };
/** The bounds of an axis: from zero (or the lowest value below it) to the highest, with room at the top; `scale`
 * lets an axis start above zero. */
export function bounds(values: number[], scale = false): Bounds {
  const held = values.filter((v) => Number.isFinite(v));
  if (!held.length) return { lo: 0, hi: 1 };
  let lo = Math.min(...held), hi = Math.max(...held);
  if (!scale) { lo = Math.min(0, lo); hi = Math.max(0, hi); }
  if (hi === lo) { hi = lo + (Math.abs(lo) || 1); }
  const pad = (hi - lo) * 0.08;
  return { lo: scale && lo > 0 ? Math.max(0, lo - pad) : lo < 0 ? lo - pad : lo, hi: hi + pad };
}
export function ticksOf(b: Bounds): number[] {
  const step = nice(b.hi - b.lo), out: number[] = [];
  for (let t = Math.ceil(b.lo / step) * step; t <= b.hi + 1e-9; t += step) out.push(Math.round(t * 1e6) / 1e6 || 0);  // session 416: || 0, so a tick at minus zero reads "0", not "-0" (as session 404 did in GroupedBars)
  return out;
}
/** The width of the element, measured, and measured again when it changes. */
export function useWidth<T extends HTMLElement>(initial = 760): [React.RefObject<T | null>, number] {
  const ref = useRef<T>(null);
  const [width, setWidth] = useState(initial);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver((es) => { const w = Math.round(es[0].contentRect.width); if (w > 0) setWidth(w); });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, Math.max(280, width)];
}

/** The Chart | Table toggle every chart carries. */
export function Toggle({ label, table, setTable, id }: { label: string; table: boolean; setTable: (t: boolean) => void; id?: string }) {
  return (
    <div className="mb-1 flex items-baseline justify-end">
      <span className="inline-grid grid-cols-2 border border-muted text-xs" role="group" aria-label={`${label}: chart or table`} data-chart-table={id ?? "1"}>
        {([["chart", "Chart"], ["table", "Table"]] as const).map(([k, l], i) => (
          <button key={k} type="button" aria-pressed={table === (k === "table")} data-show={k} onClick={() => setTable(k === "table")}
            className={`px-2.5 py-0.5 ${i ? "border-l border-muted" : ""} ${table === (k === "table") ? "bg-ink text-white" : "bg-white text-ink"}`}>{l}</button>
        ))}
      </span>
    </div>
  );
}
/** A table of rows by columns, the shape every chart's table takes. */
export function DataTable({ label, head, rows, id }: { label: string; head: ReactNode[]; rows: { key: string; cells: ReactNode[] }[]; id?: string }) {
  return (
    <div className="overflow-x-auto" data-chart-as-table={id ?? "1"} {...scrollRegion(`${label}, as a table`)}>
      <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 320 }}>
        <caption className="sr-only">{label}, as a table</caption>
        <thead><tr>{head.map((h, i) => (emptyCell(h) ? <td key={i} data-empty-head="1" className="px-3 py-1.5" /> : <th key={i} scope="col" className={`px-3 py-1.5 font-normal ${i ? "text-right" : ""}`}>{h}</th>))}</tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key} className="border-b border-rule">
              {r.cells.map((c, i) => (i === 0 ? <th key={i} scope="row" className="px-3 py-1.5 font-normal">{c}</th> : <td key={i} className="px-3 py-1.5 text-right font-mono">{c}</td>))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
const NotHeld = () => <span className="font-sans text-muted">not held</span>;
/** The hover card on fog, at a horizontal position inside the chart's box. */
function Card({ left, width, children }: { left: number; width: number; children: ReactNode }) {
  return <div className="pointer-events-none absolute top-6 z-10 border border-rule bg-paper px-3 py-2 text-xs" style={{ left: Math.min(Math.max(0, left), Math.max(0, width - 240)) }} data-chart-card="1">{children}</div>;
}

// ---------------------------------------------------------------------------------------------------------------------
// CategoryChart
// ---------------------------------------------------------------------------------------------------------------------
export type CatSeries = {
  name: string; color: string; values: (number | null)[];
  kind?: "bar" | "line" | "area"; stack?: string; axis?: 0 | 1; unit?: string; dash?: boolean | "solid" | "dashed" | "dotted"; width?: number; digits?: number;
  /** a mark on each category instead of a line (the perfectly foreseen diamond) */
  mark?: boolean;
  /** a per-category opacity (a year short of twelve months drawn pale) */
  faint?: boolean[];
};
export function CategoryChart({ id, x, series, unit, unit2 = "", label, height = 300, notes, dim, every, zero = true, scale2 = true, refLines, children, nameOf, table: tableFirst = false, shade, marks, small = false, yMax, y2Max, band }: {
  id: string; x: string[]; series: CatSeries[]; unit: string; unit2?: string; label: string; height?: number;
  notes?: (string | null)[]; dim?: boolean[]; every?: number; zero?: boolean; scale2?: boolean;
  /** horizontal reference lines on the left axis, each named (a month of debt payments; coverage at 1 and 1.25) */
  refLines?: { value: number; name: string; dashed?: boolean }[];
  children?: ReactNode; nameOf?: (i: number) => string; table?: boolean;
  /** session 318: a band of categories shaded and named (the days an impact study compares), points marked and named
   * (a scanner's flagged point), the picker's small example (no toggle, no card, no names), and a shared top of an
   * axis across panels */
  shade?: { from: number; to: number; label: string }; marks?: { i: number; value: number; label: string }[]; small?: boolean; yMax?: number; y2Max?: number;
  /** a band between two series of the left axis, named at its right edge (the range of the years before, on the board) */
  band?: { lo: (number | null)[]; hi: (number | null)[]; name: string };
}) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(tableFirst);
  const [hover, setHover] = useState<number | null>(null);
  const n = x.length;
  const two = series.some((s) => s.axis === 1);
  const gutter = small ? 4 : Math.min(150, Math.max(60, Math.max(0, ...series.filter((s) => (s.kind ?? "bar") !== "bar").map((s) => textWidth(s.name))) + 8));
  const L = small ? 34 : 58, R = small ? 6 : two ? 56 : 12, BOT = small ? 16 : 30;
  const plotR = W - R - gutter;
  // session 331: a bar series is named at the top, after the unit (they overlapped it), in as many rows as the width
  // needs (at a phone's width the names ran past the drawing); the plot starts under the last row
  const bars = series.filter((s) => (s.kind ?? "bar") === "bar");
  const barNames: { name: string; color: string; x: number; y: number }[] = [];
  if (!small) {
    const edge = two ? plotR : W - 4;
    let bx = L + textWidth(unit) + 14, by = 11;
    for (const s of bars) {
      const w = textWidth(s.name);
      if (bx + w > edge && bx > L + 4) { bx = L + 4; by += 14; }
      barNames.push({ name: s.name, color: s.color, x: bx, y: by });
      bx += w + 14;
    }
  }
  const TOP = small ? 6 : Math.max(24, (barNames.length ? barNames[barNames.length - 1].y : 0) + 13);
  // stacks: each stack's running top per category; a bar or an area in a stack is drawn from the stack below it
  const tops = new Map<string, number[]>(), bottoms = new Map<string, number[]>();
  const stacked = series.map((s) => {
    if (!s.stack) return { from: s.values.map(() => 0), to: s.values };
    const up = tops.get(s.stack) ?? new Array<number>(n).fill(0), down = bottoms.get(s.stack) ?? new Array<number>(n).fill(0);
    const from: number[] = [], to: (number | null)[] = [];
    s.values.forEach((v, i) => {
      if (v === null || v === undefined) { from.push(0); to.push(null); return; }
      if (v >= 0) { from.push(up[i]); up[i] += v; to.push(up[i]); } else { from.push(down[i]); down[i] += v; to.push(down[i]); }
    });
    tops.set(s.stack, up); bottoms.set(s.stack, down);
    return { from, to };
  });
  const vals = (k: number) => stacked[k].to.filter((v): v is number => v !== null);
  const b1raw = bounds([...series.flatMap((s, k) => (s.axis === 1 && two ? [] : vals(k))), ...(band ? [...band.lo, ...band.hi].filter((v): v is number => v !== null) : [])], !zero);
  const b2raw = bounds(series.flatMap((s, k) => (s.axis === 1 && two ? vals(k) : [])), scale2);
  const b1 = yMax !== undefined ? { lo: Math.min(0, b1raw.lo), hi: yMax } : b1raw;
  const b2 = y2Max !== undefined ? { lo: Math.min(0, b2raw.lo), hi: y2Max } : b2raw;
  const bw = (plotR - L) / Math.max(1, n);
  const cx = (i: number) => L + i * bw + bw / 2;
  const py = (v: number, b: Bounds) => TOP + ((b.hi - v) / (b.hi - b.lo || 1)) * (height - TOP - BOT);
  const barGroups = [...new Set(bars.map((s) => s.stack ?? `_${s.name}`))];
  const barW = Math.max(2, (bw * 0.7) / Math.max(1, barGroups.length));
  const everyK = every ?? (n > 12 ? Math.ceil(Math.max(1, ...x.map((s) => textWidth(s, 11))) / bw) : 1);
  const labelled = (i: number) => i % Math.max(1, everyK) === 0;
  const dimAt = (i: number) => (dim?.[i] ? 0.4 : 1);
  const unitOf = (s: CatSeries) => s.unit ?? (s.axis === 1 ? unit2 : unit);
  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const i = Math.max(0, Math.min(n - 1, Math.floor((e.clientX - r.left - L) / bw)));
    setHover(i);
  };
  // the names at the right for lines and areas; a bar series is named above its first bar
  const ends = series.map((s, k) => {
    const b = s.axis === 1 && two ? b2 : b1;
    const last = [...stacked[k].to].reverse().findIndex((v) => v !== null);
    if (last < 0) return null;
    const i = n - 1 - last;
    const v = stacked[k].to[i]!;
    const y = s.stack && (s.kind ?? "bar") === "area" ? (py(v, b) + py(stacked[k].from[i], b)) / 2 : py(v, b);
    return { k, y, lines: [] as string[] };
  }).filter((e): e is { k: number; y: number; lines: string[] } => e !== null && (series[e.k].kind ?? "bar") !== "bar");
  // session 370: a name wider than the room at the right is drawn in lines that fit (on /research/card/* the names ran
  // past the chart's box, at 390 px and at 1280); each name keeps the room of its lines below it, and the last stays
  // inside the drawing's height (lib/chartwrap.ts)
  const endX = plotR + (two ? 50 : 6);
  for (const e of ends) e.lines = wrapName(series[e.k].name, W - endX - 2);
  stackNames(ends, height - 6);
  const rows = x.map((c, i) => ({ key: `${c}-${i}`, cells: [nameOf ? nameOf(i) : c, ...series.map((s) => (s.values[i] === null || s.values[i] === undefined ? <NotHeld key={s.name} /> : num(s.values[i] as number, s.digits)))] }));
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="category" data-chart-width={W}>
      {small ? null : <Toggle label={label} table={table} setTable={setTable} id={id} />}
      {table && !small ? <DataTable label={label} id={id} head={["Period", ...series.map((s) => `${s.name}, ${unitOf(s)}`)]} rows={rows} /> : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label} onMouseMove={small ? undefined : onMove} onMouseLeave={() => setHover(null)}
            data-n={n} data-plot-left={L} data-plot-right={plotR} data-points={n <= 100 ? JSON.stringify(series.map((s) => s.values)) : undefined}>
            <title>{label}</title>
            {shade && shade.from >= 0 && shade.to >= shade.from ? (
              <g data-shade={shade.label}>
                <rect x={L + shade.from * bw} y={TOP} width={(shade.to - shade.from + 1) * bw} height={height - TOP - BOT} fill="var(--color-accent)" fillOpacity="0.1" />
                {small ? null : <text x={L + shade.from * bw + 3} y={TOP + 12} fontSize="11" fill="var(--color-muted)">{shade.label}</text>}
              </g>
            ) : null}
            <defs>
              {series.map((s, k) => <pattern key={k} id={`${id}-hatch-${k}`} width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="var(--color-surface)" /><rect width="2.2" height="5" fill={tokenColor(s.color)} /></pattern>)}
            </defs>
            {ticksOf(b1).map((v) => (
              <g key={`y${v}`}>
                <line x1={L} x2={plotR} y1={py(v, b1)} y2={py(v, b1)} stroke={v === 0 ? "var(--color-ink)" : "var(--color-rule)"} strokeWidth={v === 0 ? 1 : 0.75} />
                <text x={L - 6} y={py(v, b1) + 4} textAnchor="end" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text>
              </g>
            ))}
            {two ? ticksOf(b2).map((v) => <text key={`y2${v}`} x={plotR + 6} y={py(v, b2) + 4} textAnchor="start" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text>) : null}
            <text x={L} y={11} fontSize="12" fill="var(--color-muted)">{unit}</text>
            {two ? <text x={plotR + 6} y={11} fontSize="12" fill="var(--color-muted)">{unit2}</text> : null}
            {refLines?.map((r) => (
              <g key={r.name}>
                <line x1={L} x2={plotR} y1={py(r.value, b1)} y2={py(r.value, b1)} stroke="var(--color-accent)" strokeWidth="1" strokeDasharray={r.dashed ? "4 3" : undefined} />
                {/* session 584: a name wider than the plot is drawn in lines that fit it, the last on the line (a
                    reference's long name ran 120 px past the drawing's left edge on /research at 390 px) */}
                {(() => { const ls = wrapName(r.name, Math.max(40, plotR - L - 4), 11); return (
                  <text x={plotR - 2} y={py(r.value, b1) - 3 - 13 * (ls.length - 1)} textAnchor="end" fontSize="11" fill="var(--color-accent)">
                    {ls.length === 1 ? r.name : ls.map((ln, j) => <tspan key={j} x={plotR - 2} dy={j ? 13 : 0}>{ln}</tspan>)}
                  </text>); })()}
              </g>
            ))}
            {/* session 584: a category's name stays inside the drawing (the last month of a small example ran 3 px past
                its right edge at 390 px); one that fits is drawn at its category's middle as before */}
            {x.map((c, i) => (labelled(i) ? <text key={`x${i}`} x={Math.max(Math.min(cx(i), W - 1 - textWidth(c, 11) * 0.55), textWidth(c, 11) * 0.55 + 1)} y={height - BOT + 16} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{c}</text> : null))}
            {series.map((s, k) => {
              const b = s.axis === 1 && two ? b2 : b1, color = tokenColor(s.color), kind = s.kind ?? "bar";
              if (kind === "bar") {
                const g = barGroups.indexOf(s.stack ?? `_${s.name}`);
                return (
                  <g key={s.name} data-series={s.name}>
                    {s.values.map((v, i) => {
                      if (v === null || v === undefined) return null;
                      const y0 = py(stacked[k].from[i], b), y1 = py(stacked[k].to[i]!, b);
                      const x0 = cx(i) - (barGroups.length * barW) / 2 + g * barW;
                      return <rect key={i} x={x0} y={Math.min(y0, y1)} width={barW} height={Math.max(0.5, Math.abs(y1 - y0))} fill={s.faint?.[i] ? `url(#${id}-hatch-${k})` : color} opacity={dimAt(i)} />;
                    })}
                  </g>
                );
              }
              if (s.mark) {
                return <g key={s.name} data-series={s.name}>{s.values.map((v, i) => (v === null || v === undefined ? null : <path key={i} d={`M${cx(i)},${py(v, b) - 5} l5,5 l-5,5 l-5,-5 Z`} fill={color} />))}</g>;
              }
              const pts = stacked[k].to.map((v, i) => (v === null ? null : [cx(i), py(v, b)] as [number, number]));
              let d = "", open = false;
              pts.forEach((p) => { if (!p) { open = false; return; } d += `${open ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)} `; open = true; });
              let area = "";
              if (kind === "area") {
                const held = pts.map((p, i) => (p ? i : -1)).filter((i) => i >= 0);
                // session 588: the area's base is held inside the plot; on an axis whose floor is above zero (the right
                // scale of the five-grid cards, 12k on CAISO's) the shading ran from zero, below the axis and out of
                // its panel. The top line is the series' own; no value moves, only the shading below the floor is not drawn
                const base = (i: number) => Math.min(height - BOT, Math.max(TOP, py(stacked[k].from[i], b)));
                if (held.length) area = `M${cx(held[0]).toFixed(1)},${base(held[0]).toFixed(1)} ` + held.map((i) => `L${pts[i]![0].toFixed(1)},${pts[i]![1].toFixed(1)}`).join(" ") + " " + [...held].reverse().map((i) => `L${cx(i).toFixed(1)},${base(i).toFixed(1)}`).join(" ") + " Z";
              }
              const dash = s.dash === true || s.dash === "dashed" ? "4 3" : s.dash === "dotted" ? "1.5 3" : undefined;
              return (
                <g key={s.name} data-series={s.name}>
                  {area ? <path d={area} fill={color} fillOpacity={s.stack ? 0.85 : 0.4} stroke="none" /> : null}
                  <path d={d} fill="none" stroke={color} strokeWidth={s.width ?? (kind === "area" ? 1 : 1.8)} strokeDasharray={dash} strokeLinejoin="round" />
                  {n <= 40 && kind === "line" ? pts.map((p, i) => (p ? <circle key={i} cx={p[0]} cy={p[1]} r="2.2" fill={color} /> : null)) : null}
                </g>
              );
            })}
            {band ? (() => {
              const held = x.map((_, i) => (band.lo[i] !== null && band.hi[i] !== null ? i : -1)).filter((i) => i >= 0);
              if (!held.length) return null;
              const d = `M${cx(held[0]).toFixed(1)},${py(band.hi[held[0]]!, b1).toFixed(1)} ` + held.map((i) => `L${cx(i).toFixed(1)},${py(band.hi[i]!, b1).toFixed(1)}`).join(" ") + " " + [...held].reverse().map((i) => `L${cx(i).toFixed(1)},${py(band.lo[i]!, b1).toFixed(1)}`).join(" ") + " Z";
              const last = held[held.length - 1];
              return <g data-band-name={band.name}><path d={d} fill="var(--color-rule)" fillOpacity="0.55" stroke="none" />{small ? null : <text x={plotR + 6} y={(py(band.hi[last]!, b1) + py(band.lo[last]!, b1)) / 2 + 4} fontSize="12" fill="var(--color-muted)">{band.name}</text>}</g>;
            })() : null}
            {marks?.map((m) => (
              <g key={`${m.i}-${m.label}`} data-mark={m.label}>
                {/* session 533: a named mark's ring is filled with the page, as the PNG's is, so it holds on an ink bar */}
                <circle cx={cx(m.i)} cy={py(m.value, b1)} r={small ? 3 : 6} fill={m.label ? "var(--color-surface)" : "none"} stroke="var(--color-accent)" strokeWidth="2" />
                {small || !m.label ? null : (() => {
                  // session 533: a mark's label is its figure and, after the first ", ", its key (the chart of the
                  // week's "28.08 USD/MWh, week of ..."): two lines, the figure in bold, at the brand's 12 px. Its
                  // place is chosen as the PNG's is (warehouse/analysis/style.py): left or right of the ring, above
                  // or below, the one that crosses the fewest bars and points of the left axis and stays inside the
                  // chart, beside the ring first on the side away from the nearer edge
                  const [fig, ...rest] = m.label.split(", ");
                  const key = rest.join(", ");
                  const mx = cx(m.i), my = py(m.value, b1);
                  const w = Math.max(textWidth(fig, 12), key ? textWidth(key, 12) : 0) + 4, h = key ? 30 : 16;
                  const zeroY = py(Math.min(Math.max(0, b1.lo), b1.hi), b1);
                  const spans: [number, number, number, number][] = [];
                  series.forEach((s) => {
                    if (s.axis === 1 && two) return;
                    const bar = (s.kind ?? "bar") === "bar";
                    s.values.forEach((v, i) => {
                      if (v === null || v === undefined || (i === m.i && v === m.value)) return;
                      const y = py(v, b1);
                      if (bar) { spans.push([cx(i) - bw / 2, cx(i) + bw / 2, Math.min(y, zeroY), Math.max(y, zeroY)]); return; }
                      const nxt = s.values[i + 1];
                      const y2 = nxt === null || nxt === undefined ? y : py(nxt, b1);
                      spans.push([cx(i), cx(i + 1), Math.min(y, y2), Math.max(y, y2)]);   // the segment to the next point
                    });
                  });
                  const place = (left: boolean, up: boolean, lift = 0) => {
                    const x0 = left ? mx - 9 - w : mx + 9, top = up ? my - 9 - h - lift : my + 9 + lift;
                    const out = x0 < 2 || x0 + w > W - 2 || top < 2 || top + h > height - BOT ? 1000 : 0;
                    const hits = spans.filter(([a0, a1, b0, b1_]) => a1 >= x0 && a0 <= x0 + w && b1_ >= top && b0 <= top + h).length;
                    return { left, up, x0, top, lift, score: out + hits };
                  };
                  // how far past the ring the label must sit to clear what is drawn under it (then a hairline joins them)
                  const clear = (left: boolean, up: boolean) => {
                    const x0 = left ? mx - 9 - w : mx + 9;
                    const under = spans.filter(([a0, a1]) => a1 >= x0 && a0 <= x0 + w);
                    return up ? Math.max(0, ...under.map(([, , b0]) => my - 9 - (b0 - 4)))
                      : Math.max(0, ...under.map(([, , , b1_]) => b1_ + 4 - (my + 9)));
                  };
                  const first = mx > L + (plotR - L) * 0.5;
                  const near = [place(first, true), place(first, false), place(!first, true), place(!first, false)];
                  const tries = [...near, ...near.map((t) => place(t.left, t.up, clear(t.left, t.up))).filter((t) => t.lift > 0)];
                  const best = tries.reduce((a, b) => (b.score < a.score || (b.score === a.score && b.lift < a.lift) ? b : a));
                  const x0 = Math.max(2, Math.min(W - 2 - w, best.x0));
                  const tx = best.left ? x0 + w : x0;
                  const y0 = best.top + 12;
                  return (
                    <>
                      {best.lift > 0 ? <line x1={mx} y1={my + (best.up ? -7 : 7)} x2={best.left ? x0 + w - 4 : x0 + 4} y2={best.up ? best.top + h : best.top}
                        stroke="var(--color-accent)" strokeWidth="1" data-mark-leader="1" /> : null}
                      <text x={tx} y={y0} textAnchor={best.left ? "end" : "start"} fontSize="12" fill="var(--color-accent)" data-mark-label="1"
                        data-mark-place={`${best.left ? "left" : "right"} ${best.up ? "above" : "below"}${best.lift > 0 ? " apart" : ""}`}
                        stroke="var(--color-surface)" strokeWidth="3" strokeLinejoin="round" paintOrder="stroke">
                        <tspan fontWeight="600">{fig}</tspan>
                        {key ? <tspan x={tx} dy={15} fill="var(--color-muted)">{key}</tspan> : null}
                      </text>
                    </>
                  );
                })()}
              </g>
            ))}
            {small ? null : <g data-direct-labels="1">
              {ends.map(({ k, y, lines }) => (
                <text key={series[k].name} x={endX} y={y + 4} fontSize="12" fill={tokenColor(series[k].color)}>
                  {lines.length === 1 ? series[k].name : lines.map((l, j) => <tspan key={j} x={endX} dy={j ? 13 : 0}>{j < lines.length - 1 ? `${l} ` : l}</tspan>)}
                </text>
              ))}
              {barNames.map((b) => <text key={b.name} x={b.x} y={b.y} fontSize="12" fill={tokenColor(b.color)}>{b.name}</text>)}
            </g>}
            {hover !== null ? <line x1={cx(hover)} x2={cx(hover)} y1={TOP} y2={height - BOT} stroke="var(--color-muted)" strokeWidth="1" strokeDasharray="3 3" /> : null}
          </svg>
          {hover !== null ? (
            <Card left={cx(hover) + 10} width={W}>
              <div className="text-ink">{nameOf ? nameOf(hover) : x[hover]}</div>
              {series.map((s) => { const v = s.values[hover]; return v === null || v === undefined ? null : (
                <div key={s.name} className="flex justify-between gap-4"><span style={{ color: tokenColor(s.color) }}>{s.name}: </span><span className="font-mono text-ink">{num(v, s.digits)} {unitOf(s)}</span></div>
              ); })}
              {notes?.[hover] ? <div className="mt-1 max-w-[220px] text-muted">{notes[hover]}</div> : null}
              {children}
            </Card>
          ) : null}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// HeatChart
// ---------------------------------------------------------------------------------------------------------------------
export function HeatChart({ id, rows, cols, cells, unit, label, tips, marks, colMarks, lo: loGiven, hi: hiGiven, legend, table: tableFirst = false }: {
  id: string; rows: string[]; cols: string[]; cells: (number | null)[][]; unit: string; label: string;
  /** [row][col]: the cell's own words for the hover (else "row, col: value unit") */
  tips?: string[][]; marks?: [number, number][];
  /** session 1155: columns marked on the column axis, a small triangle under the column (the scarcity strip's CAISO alert
   *  days); off by default, so no other chart changes. The caller says what the mark means beside the chart. */
  colMarks?: number[]; lo?: number; hi?: number;
  /** the words at the two ends of the scale */
  legend?: [string, string]; table?: boolean;
}) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(tableFirst);
  const [hover, setHover] = useState<[number, number] | null>(null);
  const held = cells.flat().filter((v): v is number => v !== null && v !== undefined);
  const lo = loGiven ?? (held.length ? Math.min(...held) : 0), hi = hiGiven ?? (held.length ? Math.max(...held) : 1);
  const L = Math.min(110, Math.max(44, Math.max(0, ...rows.map((r) => textWidth(r, 11))) + 10)), R = 10, TOP = 8, BOT = 48;
  const cw = (W - L - R) / Math.max(1, cols.length), ch = 18;
  // session 584: the legend's words are measured before the height; where the scale and "no value held" do not fit on one
  // line even from the left edge (a phone's 390 px: "no value held" ran past the drawing), the key for a blank cell is
  // drawn on a line of its own below the scale, and the drawing is that line taller
  const w0 = legend?.[0] ?? `${num(lo)} ${unit}`, w1 = legend?.[1] ?? `${num(hi)} ${unit}`;
  const span = textWidth(w0, 11) + 8 + 8 * 12 + 6 + textWidth(w1, 11) + 30 + textWidth("no value held", 11);
  const split = 4 + span > W - 4;
  // on its own line the scale may still be wider than the drawing (the face's figures run wider than textWidth's
  // estimate): there the words are measured with a margin and the ramp's eight cells narrow to the room left, 6 px at least
  const tw = (s: string) => textWidth(s, 11) * (split ? 1.12 : 1);
  const cell = split ? Math.max(6, Math.min(12, (W - 8 - tw(w0) - 8 - 6 - tw(w1)) / 8)) : 12;
  const height = TOP + rows.length * ch + BOT + (split ? 16 : 0);
  const strength = (v: number) => (hi > lo ? 0.08 + 0.92 * ((v - lo) / (hi - lo)) : 0.6);
  // session 351 (the owner's ruling of 20 October 2026): one color for a magnitude; where the figure is signed (its values
  // cross zero) a two-hue ramp, the accent above zero and the blue below, each cell's strength its distance from zero
  const signed = lo < 0 && hi > 0, far = Math.max(-lo, hi);
  const fillOf = (v: number) => (signed ? (v < 0 ? "var(--chart-blue)" : "var(--color-accent)") : "var(--color-accent)");
  const opacityOf = (v: number) => (signed ? 0.08 + 0.92 * (Math.abs(v) / (far || 1)) : strength(v));
  const everyC = Math.max(1, Math.ceil(Math.max(1, ...cols.map((c) => textWidth(c, 11))) / cw));
  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const c = Math.floor((e.clientX - r.left - L) / cw), rw = Math.floor((e.clientY - r.top - TOP) / ch);
    setHover(c >= 0 && c < cols.length && rw >= 0 && rw < rows.length ? [rw, c] : null);
  };
  const words = (r: number, c: number) => tips?.[r]?.[c] ?? (cells[r][c] === null || cells[r][c] === undefined ? `${rows[r]}, ${cols[c]}: not held` : `${rows[r]}, ${cols[c]}: ${num(cells[r][c] as number)} ${unit}`);
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="heat" data-chart-width={W} data-heat-scale={signed ? "diverging" : "one"}>
      <Toggle label={label} table={table} setTable={setTable} id={id} />
      {table ? <DataTable label={label} id={id} head={["", ...cols]} rows={rows.map((r, i) => ({ key: r, cells: [r, ...cells[i].map((v, j) => (v === null || v === undefined ? <NotHeld key={j} /> : num(v)))] }))} /> : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label} onMouseMove={onMove} onMouseLeave={() => setHover(null)}
            data-plot-left={L} data-plot-top={TOP} data-cell-w={cw} data-cell-h={ch} data-rows={rows.length} data-cols={cols.length}>
            <title>{label}</title>
            <defs><pattern id={`${id}-blank`} width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="var(--color-surface)" /><rect width="1.5" height="5" fill="var(--color-rule)" /></pattern></defs>
            {rows.map((r, i) => <text key={r} x={L - 6} y={TOP + i * ch + ch / 2 + 4} textAnchor="end" fontSize="11" fill="var(--color-ink)">{r}</text>)}
            {cols.map((c, j) => (j % everyC === 0 ? <text key={c} x={L + j * cw + cw / 2} y={height - BOT + 14} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{c}</text> : null))}
            {cells.map((row, i) => row.map((v, j) => (
              <rect key={`${i}-${j}`} x={L + j * cw} y={TOP + i * ch} width={cw} height={ch} fill={v === null || v === undefined ? `url(#${id}-blank)` : fillOf(v)}
                fillOpacity={v === null || v === undefined ? 1 : opacityOf(v)} stroke="var(--color-surface)" strokeWidth="0.75" data-cell={`${i}-${j}`} />
            )))}
            {marks?.map(([r, c]) => <rect key={`m${r}-${c}`} x={L + c * cw + cw / 2 - 3} y={TOP + r * ch + ch / 2 - 3} width="6" height="6" fill="var(--color-ink)" />)}
            {colMarks?.map((c) => { const x = L + c * cw + cw / 2, y = TOP + rows.length * ch + 1; return <path key={`c${c}`} d={`M${x - 4} ${y + 4.5}L${x + 4} ${y + 4.5}L${x} ${y}Z`} fill="var(--color-ink)" data-col-mark={c} />; })}
            {hover ? <rect x={L + hover[1] * cw} y={TOP + hover[0] * ch} width={cw} height={ch} fill="none" stroke="var(--color-ink)" strokeWidth="1.5" /> : null}
            {/* session 331: the scale starts after its first word (it stood 110 px past the row labels whatever that word's
                width, and ran past a phone's drawing); the whole legend starts at the left edge where it would not fit */}
            {(() => {
              const x0 = L + span <= W - 4 ? L : 4, sx = x0 + tw(w0) + 8, hx = sx + 8 * cell + 6;
              const ly = split ? height - 24 : height - 8, bx = split ? 4 : hx + textWidth(w1, 11) + 14, by = split ? height - 8 : ly;
              return (
                <g data-direct-labels="1" data-legend-split={split ? "1" : undefined}>
                  <text x={x0} y={ly} fontSize="11" fill="var(--color-muted)">{w0}</text>
                  {signed
                    ? Array.from({ length: 8 }, (_, k) => <rect key={k} x={sx + k * cell} y={ly - 9} width={cell} height="10" fill={k < 4 ? "var(--chart-blue)" : "var(--color-accent)"} fillOpacity={0.08 + 0.92 * (Math.abs(k - 3.5) - 0.5) / 3} data-diverging="1" />)
                    : Array.from({ length: 8 }, (_, k) => <rect key={k} x={sx + k * cell} y={ly - 9} width={cell} height="10" fill="var(--color-accent)" fillOpacity={0.08 + 0.92 * (k / 7)} />)}
                  <text x={hx} y={ly} fontSize="11" fill="var(--color-muted)">{w1}</text>
                  <rect x={bx} y={by - 9} width="12" height="10" fill={`url(#${id}-blank)`} />
                  <text x={bx + 16} y={by} fontSize="11" fill="var(--color-muted)">no value held</text>
                </g>
              );
            })()}
          </svg>
          {hover ? <Card left={L + hover[1] * cw + 10} width={W}><div className="max-w-[260px] text-ink">{words(hover[0], hover[1])}</div></Card> : null}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// BandChart
// ---------------------------------------------------------------------------------------------------------------------
export function BandChart({ id, x, lo, hi, avg, last, cur, names, unit, label, height = 300, fmt = num, dateOf, table: tableFirst = false }: {
  id: string; x: string[]; lo: (number | null)[]; hi: (number | null)[]; avg: (number | null)[]; last: (number | null)[]; cur: (number | null)[];
  /** the names of the band, the mean, last year and this year */
  names: [string, string, string, string]; unit: string; label: string; height?: number; fmt?: (v: number) => string; dateOf?: (i: number) => string; table?: boolean;
}) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(tableFirst);
  const [hover, setHover] = useState<number | null>(null);
  const n = x.length;
  const gutter = Math.min(150, Math.max(70, Math.max(...names.map((s) => textWidth(s))) + 8));
  const L = 62, R = 12, TOP = 22, BOT = 28, plotR = W - R - gutter;
  const b = bounds([...lo, ...hi, ...avg, ...last, ...cur].filter((v): v is number => v !== null), true);
  const px = (i: number) => L + (i / Math.max(1, n - 1)) * (plotR - L);
  const py = (v: number) => TOP + ((b.hi - v) / (b.hi - b.lo || 1)) * (height - TOP - BOT);
  const line = (vs: (number | null)[]) => { let d = "", open = false; vs.forEach((v, i) => { if (v === null) { open = false; return; } d += `${open ? "L" : "M"}${px(i).toFixed(1)},${py(v).toFixed(1)} `; open = true; }); return d; };
  const heldBand = x.map((_, i) => (lo[i] !== null && hi[i] !== null ? i : -1)).filter((i) => i >= 0);
  const band = heldBand.length ? `M${px(heldBand[0]).toFixed(1)},${py(hi[heldBand[0]]!).toFixed(1)} ` + heldBand.map((i) => `L${px(i).toFixed(1)},${py(hi[i]!).toFixed(1)}`).join(" ") + " " + [...heldBand].reverse().map((i) => `L${px(i).toFixed(1)},${py(lo[i]!).toFixed(1)}`).join(" ") + " Z" : "";
  const everyK = Math.max(1, Math.ceil((n * Math.max(1, ...x.map((s) => textWidth(s, 11)))) / (plotR - L)));
  const onMove = (e: React.MouseEvent<SVGSVGElement>) => { const r = e.currentTarget.getBoundingClientRect(); setHover(Math.max(0, Math.min(n - 1, Math.round(((e.clientX - r.left - L) / (plotR - L)) * (n - 1))))); };
  const endOf = (vs: (number | null)[]) => { const i = vs.map((v, j) => (v === null ? -1 : j)).filter((j) => j >= 0).pop(); return i === undefined ? null : py(vs[i]!); };
  const ends = [{ name: names[3], y: endOf(cur), color: "var(--color-accent)" }, { name: names[2], y: endOf(last), color: "var(--color-fuel-gas)" }, { name: names[1], y: endOf(avg), color: "var(--color-muted)" },
    { name: names[0], y: heldBand.length ? (py(hi[heldBand[heldBand.length - 1]]!) + py(lo[heldBand[heldBand.length - 1]]!)) / 2 : null, color: "var(--color-muted)" }]
    .filter((e): e is { name: string; y: number; color: string } => e.y !== null).sort((a, c) => a.y - c.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y < ends[i - 1].y + 13) ends[i].y = ends[i - 1].y + 13;
  const cell = (v: number | null) => (v === null ? <NotHeld /> : fmt(v));
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="band" data-chart-width={W}>
      <Toggle label={label} table={table} setTable={setTable} id={id} />
      {table ? <DataTable label={label} id={id} head={["Period", `${names[3]}, ${unit}`, `${names[2]}, ${unit}`, `${names[1]}, ${unit}`, `${names[0]}, low`, `${names[0]}, high`]}
        rows={x.map((c, i) => ({ key: `${c}-${i}`, cells: [dateOf ? dateOf(i) : c, cell(cur[i]), cell(last[i]), cell(avg[i]), cell(lo[i]), cell(hi[i])] }))} /> : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label} onMouseMove={onMove} onMouseLeave={() => setHover(null)} data-n={n} data-plot-left={L} data-plot-right={plotR}>
            <title>{label}</title>
            {ticksOf(b).map((v) => (
              <g key={v}>
                <line x1={L} x2={plotR} y1={py(v)} y2={py(v)} stroke={v === 0 ? "var(--color-ink)" : "var(--color-rule)"} strokeWidth={v === 0 ? 1 : 0.75} />
                <text x={L - 6} y={py(v) + 4} textAnchor="end" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text>
              </g>
            ))}
            <text x={L} y={11} fontSize="12" fill="var(--color-muted)">{unit}</text>
            {x.map((c, i) => (i % everyK === 0 ? <text key={i} x={px(i)} y={height - BOT + 16} textAnchor={i === 0 ? "start" : "middle"} fontSize="11" fill="var(--color-ink)">{c}</text> : null))}
            {band ? <path d={band} fill="var(--color-rule)" fillOpacity="0.6" stroke="none" /> : null}
            <path d={line(avg)} fill="none" stroke="var(--color-muted)" strokeWidth="1.2" strokeDasharray="4 3" />
            <path d={line(last)} fill="none" stroke="var(--color-fuel-gas)" strokeWidth="1.2" />
            <path d={line(cur)} fill="none" stroke="var(--color-accent)" strokeWidth="2.4" strokeLinejoin="round" />
            <g data-direct-labels="1">{ends.map((e) => <text key={e.name} x={plotR + 6} y={e.y + 4} fontSize="12" fill={e.color}>{e.name}</text>)}</g>
            {hover !== null ? <line x1={px(hover)} x2={px(hover)} y1={TOP} y2={height - BOT} stroke="var(--color-muted)" strokeWidth="1" strokeDasharray="3 3" /> : null}
          </svg>
          {hover !== null ? (
            <Card left={px(hover) + 10} width={W}>
              <div className="text-ink">{dateOf ? dateOf(hover) : x[hover]}</div>
              {([[names[3], cur[hover], "var(--color-accent)"], [names[2], last[hover], "var(--color-fuel-gas)"], [names[1], avg[hover], "var(--color-muted)"]] as [string, number | null, string][]).map(([nm, v, c]) => (v === null ? null : (
                <div key={nm} className="flex justify-between gap-4"><span style={{ color: c }}>{nm}: </span><span className="font-mono text-ink">{fmt(v)} {unit}</span></div>
              )))}
              {lo[hover] !== null && hi[hover] !== null ? <div className="flex justify-between gap-4"><span className="text-muted">{names[0]}: </span><span className="font-mono text-ink">{fmt(lo[hover]!)} to {fmt(hi[hover]!)} {unit}</span></div> : null}
            </Card>
          ) : null}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// ScatterChart
// ---------------------------------------------------------------------------------------------------------------------
export function ScatterChart({ id, points, xUnit, yUnit, label, height = 320, xName, yName, table: tableFirst = false, fit, labels = true, small = false }: {
  id: string; points: { name: string; x: number; y: number }[]; xUnit: string; yUnit: string; label: string; height?: number; xName?: string; yName?: string; table?: boolean;
  /** session 318: a fitted line through the cloud, named; the names beside the points (off for a cloud of days); the picker's small example */
  fit?: { x0: number; y0: number; x1: number; y1: number; name: string }; labels?: boolean; small?: boolean;
}) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(tableFirst);
  const [hover, setHover] = useState<number | null>(null);
  const L = small ? 30 : 62, R = small ? 6 : labels ? 90 : 16, TOP = small ? 6 : 16, BOT = small ? 14 : 44;
  const bx = bounds(points.map((p) => p.x), true), by = bounds(points.map((p) => p.y), true);
  const px = (v: number) => L + ((v - bx.lo) / (bx.hi - bx.lo || 1)) * (W - L - R);
  const py = (v: number) => TOP + ((by.hi - v) / (by.hi - by.lo || 1)) * (height - TOP - BOT);
  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top;
    let best = -1, dist = 20 * 20;
    points.forEach((p, i) => { const d = (px(p.x) - mx) ** 2 + (py(p.y) - my) ** 2; if (d < dist) { dist = d; best = i; } });
    setHover(best >= 0 ? best : null);
  };
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="scatter" data-chart-width={W}>
      {small ? null : <Toggle label={label} table={table} setTable={setTable} id={id} />}
      {table && !small ? <DataTable label={label} id={id} head={["", `${xName ?? "x"}, ${xUnit}`, `${yName ?? "y"}, ${yUnit}`]} rows={points.map((p, i) => ({ key: `${p.name}-${i}`, cells: [p.name, num(p.x), num(p.y)] }))} /> : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label} onMouseMove={small ? undefined : onMove} onMouseLeave={() => setHover(null)} data-n={points.length}>
            <title>{label}</title>
            {fit ? <g data-fit={fit.name}><line x1={px(fit.x0)} y1={py(fit.y0)} x2={px(fit.x1)} y2={py(fit.y1)} stroke="var(--color-ink)" strokeWidth="1.5" />{small ? null : <text x={px(fit.x1) - 4} y={py(fit.y1) - 6} textAnchor="end" fontSize="12" fill="var(--color-ink)">{fit.name}</text>}</g> : null}
            {ticksOf(by).map((v) => (
              <g key={`y${v}`}><line x1={L} x2={W - R} y1={py(v)} y2={py(v)} stroke="var(--color-rule)" strokeWidth="0.75" /><text x={L - 6} y={py(v) + 4} textAnchor="end" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text></g>
            ))}
            {ticksOf(bx).map((v) => (
              <g key={`x${v}`}><line x1={px(v)} x2={px(v)} y1={TOP} y2={height - BOT} stroke="var(--color-rule)" strokeWidth="0.75" /><text x={px(v)} y={height - BOT + 16} textAnchor="middle" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text></g>
            ))}
            <text x={L} y={11} fontSize="12" fill="var(--color-muted)">{yName ?? ""} {yUnit}</text>
            <text x={W - R} y={height - 6} textAnchor="end" fontSize="12" fill="var(--color-muted)">{xName ?? ""} {xUnit}</text>
            <g data-direct-labels="1">
              {points.map((p, i) => (
                <g key={`${p.name}-${i}`} data-point={p.name}>
                  <circle cx={px(p.x)} cy={py(p.y)} r={small ? 2 : hover === i ? 7 : labels ? 5.5 : 3.5} fill="var(--color-accent)" fillOpacity={labels ? 1 : 0.6} />
                  {labels && !small ? <text x={px(p.x) + 9} y={py(p.y) + 4} fontSize="12" fill="var(--color-ink)">{p.name}</text> : null}
                </g>
              ))}
            </g>
          </svg>
          {hover !== null ? <Card left={px(points[hover].x) + 12} width={W}><div className="text-ink">{points[hover].name}</div><div className="font-mono text-ink">{num(points[hover].y)} {yUnit}, {num(points[hover].x)} {xUnit}</div></Card> : null}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// BoxPlot
// ---------------------------------------------------------------------------------------------------------------------
export type FiveNumbers = [number, number, number, number, number];   // min, q1, median, q3, max
export function BoxPlot({ id, rows, unit, label, table: tableFirst = false }: { id: string; rows: { name: string; stats: FiveNumbers }[]; unit: string; label: string; table?: boolean }) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(tableFirst);
  const [hover, setHover] = useState<number | null>(null);
  const L = Math.min(140, Math.max(60, Math.max(0, ...rows.map((r) => textWidth(r.name, 12))) + 12)), R = 16, TOP = 26, BOT = 40, RH = 44;
  const height = TOP + rows.length * RH + BOT;
  // the axis from the lowest first quartile to the highest third, with room; a whisker beyond it is drawn to the edge
  const q1 = Math.min(...rows.map((r) => r.stats[1])), q3 = Math.max(...rows.map((r) => r.stats[3]));
  const pad = Math.max(10, (q3 - q1) * 1.5);
  const b: Bounds = { lo: Math.floor(q1 - pad), hi: Math.ceil(q3 + pad) };
  const px = (v: number) => L + ((Math.min(b.hi, Math.max(b.lo, v)) - b.lo) / (b.hi - b.lo || 1)) * (W - L - R);
  const cy = (i: number) => TOP + i * RH + RH / 2;
  const onMove = (e: React.MouseEvent<SVGSVGElement>) => { const r = e.currentTarget.getBoundingClientRect(); const i = Math.floor((e.clientY - r.top - TOP) / RH); setHover(i >= 0 && i < rows.length ? i : null); };
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="box" data-chart-width={W}>
      <Toggle label={label} table={table} setTable={setTable} id={id} />
      {table ? <DataTable label={label} id={id} head={["", `min, ${unit}`, "Q1", "median", "Q3", "max"]} rows={rows.map((r) => ({ key: r.name, cells: [r.name, ...r.stats.map((v) => num(v))] }))} /> : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label} onMouseMove={onMove} onMouseLeave={() => setHover(null)} data-n={rows.length}>
            <title>{label}</title>
            {ticksOf(b).map((v) => (
              <g key={v}><line x1={px(v)} x2={px(v)} y1={TOP - 4} y2={height - BOT + 4} stroke={v === 0 ? "var(--color-ink)" : "var(--color-rule)"} strokeWidth={v === 0 ? 1 : 0.75} /><text x={px(v)} y={height - BOT + 18} textAnchor="middle" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text></g>
            ))}
            <text x={W - R} y={height - 6} textAnchor="end" fontSize="12" fill="var(--color-muted)">{unit}</text>
            {rows.map((r, i) => {
              const [mn, a, md, c, mx] = r.stats, y = cy(i);
              // session 328: a median's label that would pass the drawing's right edge (a whisker cut at the axis) is
              // written inside it, above the line, so it is never clipped
              const far = px(mx) + 6 + textWidth(num(md), 11) > W - 2;
              return (
                <g key={r.name} data-box={r.name}>
                  <text x={L - 8} y={y + 4} textAnchor="end" fontSize="12" fill="var(--color-ink)">{r.name}</text>
                  <line x1={px(mn)} x2={px(a)} y1={y} y2={y} stroke="var(--color-ink)" strokeWidth="1" />
                  <line x1={px(c)} x2={px(mx)} y1={y} y2={y} stroke="var(--color-ink)" strokeWidth="1" />
                  <line x1={px(mn)} x2={px(mn)} y1={y - 6} y2={y + 6} stroke="var(--color-ink)" strokeWidth="1" />
                  <line x1={px(mx)} x2={px(mx)} y1={y - 6} y2={y + 6} stroke="var(--color-ink)" strokeWidth="1" />
                  <rect x={px(a)} y={y - 10} width={Math.max(1, px(c) - px(a))} height="20" fill="var(--color-panel)" stroke={hover === i ? "var(--color-accent)" : "var(--color-ink)"} strokeWidth="1" />
                  <rect x={px(md) - 1.5} y={y - 10} width="3" height="20" fill="var(--color-accent)" />
                  <text x={far ? W - 2 : px(mx) + 6} y={far ? y - 13 : y + 4} textAnchor={far ? "end" : undefined} fontSize="11" fill="var(--color-muted)" data-direct-labels="1">{num(md)}</text>
                </g>
              );
            })}
          </svg>
          {hover !== null ? (
            <Card left={px(rows[hover].stats[2]) + 10} width={W}>
              <div className="text-ink">{rows[hover].name}</div>
              <div className="font-mono text-ink">min {num(rows[hover].stats[0])}, Q1 {num(rows[hover].stats[1])}, median {num(rows[hover].stats[2])}, Q3 {num(rows[hover].stats[3])}, max {num(rows[hover].stats[4])} {unit}</div>
            </Card>
          ) : null}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// HorizontalBars (session 318): one bar a row, the value written at its end (the deal funnel of /thesis)
// ---------------------------------------------------------------------------------------------------------------------
export function HorizontalBars({ id, rows, unit, label, fmt = num }: { id: string; rows: { name: string; value: number }[]; unit: string; label: string; fmt?: (v: number) => string }) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(false);
  const L = Math.min(200, Math.max(60, Math.max(0, ...rows.map((r) => textWidth(r.name, 12))) + 12)), R = 70, TOP = 6, RH = 30, BOT = 10;
  const height = TOP + rows.length * RH + BOT;
  const hi = Math.max(1, ...rows.map((r) => r.value));
  const px = (v: number) => L + (Math.max(0, v) / hi) * (W - L - R);
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="hbars" data-chart-width={W}>
      <Toggle label={label} table={table} setTable={setTable} id={id} />
      {table ? <DataTable label={label} id={id} head={["", unit]} rows={rows.map((r) => ({ key: r.name, cells: [r.name, fmt(r.value)] }))} /> : (
        <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label}>
          <title>{label}</title>
          <g data-direct-labels="1">
            {rows.map((r, i) => (
              <g key={r.name} data-row={r.name}>
                <text x={L - 8} y={TOP + i * RH + RH / 2 + 4} textAnchor="end" fontSize="12" fill="var(--color-ink)">{r.name}</text>
                <rect x={L} y={TOP + i * RH + 6} width={Math.max(1, px(r.value) - L)} height={RH - 12} fill="var(--color-accent)" />
                <text x={px(r.value) + 6} y={TOP + i * RH + RH / 2 + 4} fontSize="12" fill="var(--color-ink)">{fmt(r.value)}</text>
              </g>
            ))}
          </g>
        </svg>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// ShareSegments (session 318): one bar of parts, each named with its share (the day's generation mix on the Grid tool)
// ---------------------------------------------------------------------------------------------------------------------
export function ShareSegments({ id, parts, unit, label }: { id: string; parts: { name: string; value: number; color: string }[]; unit: string; label: string }) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [hover, setHover] = useState<number | null>(null);
  const pos = parts.filter((p) => p.value > 0);
  const total = pos.reduce((a, p) => a + p.value, 0) || 1;
  const H = 22, TOP = 4, BOT = 34;
  const widths = pos.map((p) => (p.value / total) * W);
  const segs = pos.map((p, i) => ({ ...p, x0: widths.slice(0, i).reduce((a, w) => a + w, 0), w: widths[i], share: (100 * p.value) / total }));
  const fits = (s: { name: string; share: number; w: number }) => s.w > textWidth(`${s.name} ${s.share.toFixed(0)}%`, 11) + 6;
  const narrow = segs.filter((s) => !fits(s));
  // session 584: the parts too narrow for their names are named below the bar in as many lines as the width needs, the
  // parts kept whole (on a phone's 390 px the one line ran up to 150 px past the drawing); the drawing grows by a line each
  const notes: string[] = [];
  for (const t of narrow.map((s) => `${s.name} ${s.share.toFixed(1)}%`)) {
    const last = notes.length - 1, joined = last >= 0 ? `${notes[last]}; ${t}` : t;
    if (last >= 0 && textWidth(joined, 10) * 1.1 <= W - 2) notes[last] = joined; else if (last >= 0) { notes[last] += "; "; notes.push(t); } else notes.push(t);
  }
  const tall = TOP + H + BOT + 13 * Math.max(0, notes.length - 1);
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="shares" data-chart-width={W}>
      <svg viewBox={`0 0 ${W} ${tall}`} width={W} height={tall} className="block max-w-full" role="img" aria-label={label} onMouseLeave={() => setHover(null)}>
        <title>{label}</title>
        {segs.map((s, i) => (
          <g key={s.name} data-part={s.name} onMouseEnter={() => setHover(i)}>
            <rect x={s.x0} y={TOP} width={Math.max(0.5, s.w)} height={H} fill={tokenColor(s.color)} stroke="var(--color-panel)" strokeWidth="1" />
            {fits(s) ? <text x={s.x0 + s.w / 2} y={TOP + H / 2 + 4} textAnchor="middle" fontSize="11" fill="var(--color-paper)">{s.name} {s.share.toFixed(0)}%</text> : null}
          </g>
        ))}
        <g data-direct-labels="1">
          {notes.length ? <text x={0} y={TOP + H + 14} fontSize="10" fill="var(--color-muted)">{notes.map((ln, j) => <tspan key={j} x={0} dy={j ? 13 : 0}>{ln}</tspan>)}</text> : null}
        </g>
      </svg>
      {hover !== null && segs[hover] ? <Card left={segs[hover].x0 + 8} width={W}><div className="text-ink">{segs[hover].name}: <span className="font-mono">{num(segs[hover].value)} {unit}</span> ({segs[hover].share.toFixed(1)}%)</div></Card> : null}
    </div>
  );
}
