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
  for (let t = Math.ceil(b.lo / step) * step; t <= b.hi + 1e-9; t += step) out.push(Math.round(t * 1e6) / 1e6);
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
    <div className="overflow-x-auto" data-chart-as-table={id ?? "1"}>
      <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 320 }}>
        <caption className="sr-only">{label}, as a table</caption>
        <thead><tr>{head.map((h, i) => <th key={i} scope="col" className={`px-3 py-1.5 font-normal ${i ? "text-right" : ""}`}>{h}</th>)}</tr></thead>
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
export function CategoryChart({ id, x, series, unit, unit2 = "", label, height = 300, notes, dim, every, zero = true, scale2 = true, refLines, children, nameOf, table: tableFirst = false }: {
  id: string; x: string[]; series: CatSeries[]; unit: string; unit2?: string; label: string; height?: number;
  notes?: (string | null)[]; dim?: boolean[]; every?: number; zero?: boolean; scale2?: boolean;
  /** horizontal reference lines on the left axis, each named (a month of debt payments; coverage at 1 and 1.25) */
  refLines?: { value: number; name: string; dashed?: boolean }[];
  children?: ReactNode; nameOf?: (i: number) => string; table?: boolean;
}) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(tableFirst);
  const [hover, setHover] = useState<number | null>(null);
  const n = x.length;
  const two = series.some((s) => s.axis === 1);
  const gutter = Math.min(150, Math.max(60, Math.max(0, ...series.filter((s) => (s.kind ?? "bar") !== "bar").map((s) => textWidth(s.name))) + 8));
  const L = 58, R = two ? 56 : 12, TOP = 24, BOT = 30;
  const plotR = W - R - gutter;
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
  const b1 = bounds(series.flatMap((s, k) => (s.axis === 1 && two ? [] : vals(k))), !zero);
  const b2 = bounds(series.flatMap((s, k) => (s.axis === 1 && two ? vals(k) : [])), scale2);
  const bw = (plotR - L) / Math.max(1, n);
  const cx = (i: number) => L + i * bw + bw / 2;
  const py = (v: number, b: Bounds) => TOP + ((b.hi - v) / (b.hi - b.lo || 1)) * (height - TOP - BOT);
  const bars = series.filter((s) => (s.kind ?? "bar") === "bar");
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
    return { k, y };
  }).filter((e): e is { k: number; y: number } => e !== null && (series[e.k].kind ?? "bar") !== "bar");
  ends.sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y < ends[i - 1].y + 13) ends[i].y = ends[i - 1].y + 13;
  const rows = x.map((c, i) => ({ key: `${c}-${i}`, cells: [nameOf ? nameOf(i) : c, ...series.map((s) => (s.values[i] === null || s.values[i] === undefined ? <NotHeld key={s.name} /> : num(s.values[i] as number, s.digits)))] }));
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="category" data-chart-width={W}>
      <Toggle label={label} table={table} setTable={setTable} id={id} />
      {table ? <DataTable label={label} id={id} head={["Period", ...series.map((s) => `${s.name}, ${unitOf(s)}`)]} rows={rows} /> : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label} onMouseMove={onMove} onMouseLeave={() => setHover(null)}
            data-n={n} data-plot-left={L} data-plot-right={plotR} data-points={n <= 100 ? JSON.stringify(series.map((s) => s.values)) : undefined}>
            <title>{label}</title>
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
                <text x={plotR - 2} y={py(r.value, b1) - 3} textAnchor="end" fontSize="11" fill="var(--color-accent)">{r.name}</text>
              </g>
            ))}
            {x.map((c, i) => (labelled(i) ? <text key={`x${i}`} x={cx(i)} y={height - BOT + 16} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{c}</text> : null))}
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
                if (held.length) area = `M${cx(held[0]).toFixed(1)},${py(stacked[k].from[held[0]], b).toFixed(1)} ` + held.map((i) => `L${pts[i]![0].toFixed(1)},${pts[i]![1].toFixed(1)}`).join(" ") + " " + [...held].reverse().map((i) => `L${cx(i).toFixed(1)},${py(stacked[k].from[i], b).toFixed(1)}`).join(" ") + " Z";
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
            <g data-direct-labels="1">
              {ends.map(({ k, y }) => <text key={series[k].name} x={plotR + (two ? 50 : 6)} y={y + 4} fontSize="12" fill={tokenColor(series[k].color)}>{series[k].name}</text>)}
              {bars.map((s, j) => <text key={s.name} x={L + 4 + j * (textWidth(s.name) + 14)} y={TOP - 6} fontSize="12" fill={tokenColor(s.color)}>{s.name}</text>)}
            </g>
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
export function HeatChart({ id, rows, cols, cells, unit, label, tips, marks, lo: loGiven, hi: hiGiven, legend, table: tableFirst = false }: {
  id: string; rows: string[]; cols: string[]; cells: (number | null)[][]; unit: string; label: string;
  /** [row][col]: the cell's own words for the hover (else "row, col: value unit") */
  tips?: string[][]; marks?: [number, number][]; lo?: number; hi?: number;
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
  const height = TOP + rows.length * ch + BOT;
  const strength = (v: number) => (hi > lo ? 0.08 + 0.92 * ((v - lo) / (hi - lo)) : 0.6);
  const everyC = Math.max(1, Math.ceil(Math.max(1, ...cols.map((c) => textWidth(c, 11))) / cw));
  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const c = Math.floor((e.clientX - r.left - L) / cw), rw = Math.floor((e.clientY - r.top - TOP) / ch);
    setHover(c >= 0 && c < cols.length && rw >= 0 && rw < rows.length ? [rw, c] : null);
  };
  const words = (r: number, c: number) => tips?.[r]?.[c] ?? (cells[r][c] === null || cells[r][c] === undefined ? `${rows[r]}, ${cols[c]}: not held` : `${rows[r]}, ${cols[c]}: ${num(cells[r][c] as number)} ${unit}`);
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-chart={id} data-svg-chart="heat" data-chart-width={W}>
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
              <rect key={`${i}-${j}`} x={L + j * cw} y={TOP + i * ch} width={cw} height={ch} fill={v === null || v === undefined ? `url(#${id}-blank)` : "var(--color-accent)"}
                fillOpacity={v === null || v === undefined ? 1 : strength(v)} stroke="var(--color-surface)" strokeWidth="0.75" data-cell={`${i}-${j}`} />
            )))}
            {marks?.map(([r, c]) => <rect key={`m${r}-${c}`} x={L + c * cw + cw / 2 - 3} y={TOP + r * ch + ch / 2 - 3} width="6" height="6" fill="var(--color-ink)" />)}
            {hover ? <rect x={L + hover[1] * cw} y={TOP + hover[0] * ch} width={cw} height={ch} fill="none" stroke="var(--color-ink)" strokeWidth="1.5" /> : null}
            <g data-direct-labels="1">
              <text x={L} y={height - 8} fontSize="11" fill="var(--color-muted)">{legend?.[0] ?? `${num(lo)} ${unit}`}</text>
              {Array.from({ length: 8 }, (_, k) => <rect key={k} x={L + 110 + k * 12} y={height - 17} width="12" height="10" fill="var(--color-accent)" fillOpacity={0.08 + 0.92 * (k / 7)} />)}
              <text x={L + 110 + 8 * 12 + 6} y={height - 8} fontSize="11" fill="var(--color-muted)">{legend?.[1] ?? `${num(hi)} ${unit}`}</text>
              <rect x={L + 110 + 8 * 12 + 6 + textWidth(legend?.[1] ?? `${num(hi)} ${unit}`, 11) + 14} y={height - 17} width="12" height="10" fill={`url(#${id}-blank)`} />
              <text x={L + 110 + 8 * 12 + 6 + textWidth(legend?.[1] ?? `${num(hi)} ${unit}`, 11) + 30} y={height - 8} fontSize="11" fill="var(--color-muted)">not held</text>
            </g>
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
export function ScatterChart({ id, points, xUnit, yUnit, label, height = 320, xName, yName, table: tableFirst = false }: {
  id: string; points: { name: string; x: number; y: number }[]; xUnit: string; yUnit: string; label: string; height?: number; xName?: string; yName?: string; table?: boolean;
}) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(tableFirst);
  const [hover, setHover] = useState<number | null>(null);
  const L = 62, R = 90, TOP = 16, BOT = 44;
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
      <Toggle label={label} table={table} setTable={setTable} id={id} />
      {table ? <DataTable label={label} id={id} head={["", `${xName ?? "x"}, ${xUnit}`, `${yName ?? "y"}, ${yUnit}`]} rows={points.map((p) => ({ key: p.name, cells: [p.name, num(p.x), num(p.y)] }))} /> : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={label} onMouseMove={onMove} onMouseLeave={() => setHover(null)} data-n={points.length}>
            <title>{label}</title>
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
                <g key={p.name} data-point={p.name}>
                  <circle cx={px(p.x)} cy={py(p.y)} r={hover === i ? 7 : 5.5} fill="var(--color-accent)" />
                  <text x={px(p.x) + 9} y={py(p.y) + 4} fontSize="12" fill="var(--color-ink)">{p.name}</text>
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
              return (
                <g key={r.name} data-box={r.name}>
                  <text x={L - 8} y={y + 4} textAnchor="end" fontSize="12" fill="var(--color-ink)">{r.name}</text>
                  <line x1={px(mn)} x2={px(a)} y1={y} y2={y} stroke="var(--color-ink)" strokeWidth="1" />
                  <line x1={px(c)} x2={px(mx)} y1={y} y2={y} stroke="var(--color-ink)" strokeWidth="1" />
                  <line x1={px(mn)} x2={px(mn)} y1={y - 6} y2={y + 6} stroke="var(--color-ink)" strokeWidth="1" />
                  <line x1={px(mx)} x2={px(mx)} y1={y - 6} y2={y + 6} stroke="var(--color-ink)" strokeWidth="1" />
                  <rect x={px(a)} y={y - 10} width={Math.max(1, px(c) - px(a))} height="20" fill="var(--color-panel)" stroke={hover === i ? "var(--color-accent)" : "var(--color-ink)"} strokeWidth="1" />
                  <rect x={px(md) - 1.5} y={y - 10} width="3" height="20" fill="var(--color-accent)" />
                  <text x={px(mx) + 6} y={y + 4} fontSize="11" fill="var(--color-muted)" data-direct-labels="1">{num(md)}</text>
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
