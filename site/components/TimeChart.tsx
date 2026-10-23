"use client";
// Energy Research Warehouse (ERW) site: the time-series chart every page draws through (LineChart, StackedArea,
// Sparkline, and the pages that call it by name). Session 22 drew it on the chart library's canvas; session 303 (Samuel's ruling
// of 13 October 2026: the battery page's SVG charts with direct labels on the series, everywhere) draws it as plain SVG
// in the brand's manner (docs/brand.md, section 6; components/tool/SeriesChart.tsx is the reference): lines of 1.5 px,
// each series named at the end of its line in its own color (no legend box), stacked areas named at the right edge,
// grid lines in the rule color, the zero line in ink, axis text 12 px captions grey that does not shrink with the
// chart (the chart is drawn for the width it has, measured, and drawn again when that changes), a hover card on fog
// with a rule-colored edge (the period in sans, each series with its figure in mono), and a Chart | Table toggle so
// that everything the card says is reachable by keyboard and as a table. Every color is a token of app/tokens.css; no
// hex value is written here. The props are session 22's, unchanged, so no page changed its data or its numbers:
// points are [time in ms, value or null], x says how a time is written, stack draws areas, y2 a second axis at the
// right in unit2, step a staircase, dashed a dashed line, mini a bare sparkline (no axes, no labels, no card).
// Session 161: x "hour_of_day" is the one axis that is not time: the 24 local hours of a day, 0 to 23.
// What the canvas had and this does not: the range slider and the PNG download; the table stands in for both.
import { useEffect, useMemo, useRef, useState } from "react";

export type TimeSeries = {
  name: string;
  color: string; // a token name ("accent") or a CSS variable ("var(--color-fuel-gas)")
  points: [number, number | null][]; // [time in ms, value]
  step?: boolean;
  dashed?: boolean;
  y2?: boolean; // session 24: drawn on a second axis at the right, in unit2 (the temperature over /grid's demand)
};

type Props = {
  series: TimeSeries[];
  unit: string;
  ariaLabel: string;
  height?: number;
  stack?: boolean; // stacked areas (a mix); negative values are shown as they are, not stacked away
  x?: "minute" | "day" | "month" | "year" | "hour_of_day";
  mini?: boolean;
  file?: string; // kept for the pages that name one (the PNG download the canvas had is not drawn here)
  unit2?: string; // session 24: the unit of the y2 series
  refLines?: { value: number; name: string; dashed?: boolean }[];   // session 318: horizontal lines on the left axis, named (the board's average)
  share?: boolean;   // session 1152: the hover card gives each series' share of the sum of the series at that time (a stacked mix)
  marks?: { t: number; name: string }[];   // session 1152: vertical lines at a time, named at the top (the energy mix's peak hour)
};

const FMT: Record<string, (t: number) => string> = {
  minute: (t) => new Date(t).toISOString().slice(0, 16).replace("T", " ") + " UTC",
  day: (t) => new Date(t).toISOString().slice(0, 10),
  month: (t) => new Date(t).toISOString().slice(0, 7),
  year: (t) => new Date(t).toISOString().slice(0, 4),
  hour_of_day: (t) => `${String(Math.round(t)).padStart(2, "0")}:00`,
};
// the x axis's labels: shorter than the card's words where the card already says the day
const TICK: Record<string, (t: number, span: number) => string> = {
  minute: (t, span) => (span > 3 * 86_400_000 ? new Date(t).toISOString().slice(5, 10) : new Date(t).toISOString().slice(5, 16).replace("T", " ")),
  day: (t, span) => (span > 400 * 86_400_000 ? new Date(t).toISOString().slice(0, 7) : new Date(t).toISOString().slice(5, 10)),
  month: (t) => new Date(t).toISOString().slice(0, 7),
  year: (t) => new Date(t).toISOString().slice(0, 4),
  hour_of_day: (t) => `${String(Math.round(t)).padStart(2, "0")}:00`,
};

const num = (v: number) => (Math.abs(v) >= 100 ? Math.round(v).toLocaleString("en-US") : Number(v.toFixed(2)).toLocaleString("en-US", { maximumFractionDigits: 2 }));
const axisNum = (v: number) => (Math.abs(v) >= 1e6 ? `${+(v / 1e6).toFixed(2)}M` : Math.abs(v) >= 1e4 ? `${+(v / 1e3).toFixed(1)}k` : num(v));
const STEPS = [0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 20000, 25000, 50000, 100000, 200000, 500000, 1e6, 2e6, 5e6, 1e7];
const nice = (span: number) => STEPS.find((s) => span / s <= 5) ?? 2e7;
/** A series' color as a token: a CSS variable as given, or the token's name ("accent" is var(--color-accent), "series-3" is var(--chart-series-3)). */
export const tokenColor = (c: string) => (c.startsWith("var(") ? c : c.startsWith("series-") ? `var(--chart-${c})` : `var(--color-${c})`);

type Pt = [number, number | null];
/** Fewer points than pixels: in each column of pixels the lowest and the highest point stand, in time order, so a spike is kept. */
function thin(points: Pt[], columns: number): Pt[] {
  if (points.length <= columns * 2) return points;
  const held = points.filter((p) => p[1] !== null) as [number, number][];
  if (!held.length) return [];
  const t0 = held[0][0], t1 = held[held.length - 1][0], w = (t1 - t0) / columns || 1;
  const out: [number, number][] = [];
  let bucket = -1, lo: [number, number] | null = null, hi: [number, number] | null = null;
  const flush = () => {
    if (lo && hi) { const first = lo[0] <= hi[0] ? lo : hi, second = lo[0] <= hi[0] ? hi : lo; out.push(first); if (first !== second) out.push(second); }
    lo = hi = null;
  };
  for (const p of held) {
    const b = Math.floor((p[0] - t0) / w);
    if (b !== bucket) { flush(); bucket = b; }
    if (!lo || p[1] < lo[1]) lo = p;
    if (!hi || p[1] > hi[1]) hi = p;
  }
  flush();
  return out;
}

type Bounds = { lo: number; hi: number; step: number };
function bounds(vs: number[], fromZero: boolean): Bounds {
  if (!vs.length) return { lo: 0, hi: 1, step: 0.25 };
  let lo = Math.min(...vs), hi = Math.max(...vs);
  if (fromZero) lo = Math.min(0, lo);
  if (hi === lo) hi = lo + 1;
  const step = nice(hi - lo);
  return { lo: Math.floor(lo / step) * step, hi: Math.ceil(hi / step) * step, step };
}
/** Session 417: a year axis's ticks, on whole years only (1 January, UTC, where the pages put a year's point), every
 * year or every 2, 5, 10 ... so that at most n fit; times spaced evenly wrote a year twice where a chart holds few
 * years ("2020, 2020, 2021, 2023, 2024, 2024, 2026"). A single year is its one tick. */
export function yearTicks(t0: number, t1: number, n: number): number[] {
  const first = new Date(t0).getUTCFullYear(), y0 = t0 > Date.UTC(first, 0, 1) ? first + 1 : first, y1 = new Date(t1).getUTCFullYear();
  if (y1 < y0) return [t0];
  const step = [1, 2, 5, 10, 20, 25, 50, 100].find((k) => Math.floor((y1 - y0) / k) + 1 <= Math.max(1, n)) ?? 100;
  const out: number[] = [];
  for (let y = y0; y <= y1; y += step) out.push(Date.UTC(y, 0, 1));
  return out;
}
const ticksOf = (b: Bounds) => { const out: number[] = []; for (let v = b.lo; v <= b.hi + b.step / 2; v += b.step) out.push(Math.round(v * 1e6) / 1e6 || 0); return out; };  // session 416: || 0, no "-0" tick

const PAGE = 500;

export function TimeChart({ series, unit, ariaLabel, height = 260, stack = false, x = "minute", mini = false, unit2 = "", refLines, share = false, marks }: Props) {
  const wrap = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(760);
  const [table, setTable] = useState(false);
  const [page, setPage] = useState(0);
  const [hover, setHover] = useState<{ t: number; px: number } | null>(null);
  useEffect(() => {
    const el = wrap.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver((es) => { const w = Math.round(es[0].contentRect.width); if (w > 0) setWidth(w); });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const has2 = !mini && series.some((s) => s.y2);
  const hod = x === "hour_of_day";
  const fmt = FMT[x];
  // the frame: axis text at the left (and at the right for y2), the series' names in a gutter at the right
  const L = mini ? 1 : 58, R = mini ? 1 : has2 ? 56 : 12, TOP = mini ? 2 : 22, BOT = mini ? 2 : 26;
  const gutter = mini ? 0 : Math.min(150, Math.max(70, Math.max(0, ...series.map((s) => s.name.length)) * 6.2));
  const W = Math.max(120, width), plotR = W - R - gutter;

  // the data, aligned on time: every x the series hold, sorted; a stack sums the series at each x in their order
  const model = useMemo(() => {
    const xs = [...new Set(series.flatMap((s) => s.points.map((p) => p[0])))].sort((a, b) => a - b);
    const at = series.map((s) => new Map<number, number | null>(s.points.map((p) => [p[0], p[1]])));
    let stacked: (number | null)[][] | null = null;
    // session 1152: each stacked value's base, the running sum of its own side (above or below zero) before it. A band
    // was drawn from the series below it, which on a mixed-sign stack (a battery charging) is on the other side of zero:
    // the band above a negative one ran from below zero to its top. Where every value is held and positive, the base is
    // the series below's top, as before
    let bases: number[][] | null = null;
    if (stack) {
      const up = new Array<number>(xs.length).fill(0), down = new Array<number>(xs.length).fill(0);
      bases = series.map(() => new Array<number>(xs.length).fill(0));
      stacked = series.map((_, k) => xs.map((t, i) => {
        const v = at[k].get(t);
        if (v === null || v === undefined) return null;
        if (v >= 0) { bases![k][i] = up[i]; up[i] += v; return up[i]; }
        bases![k][i] = down[i]; down[i] += v; return down[i];
      }));
    }
    const vals = (k: number): (number | null)[] => (stacked ? stacked[k] : xs.map((t) => at[k].get(t) ?? null));
    const left = series.flatMap((s, k) => (s.y2 && has2 ? [] : vals(k))).filter((v): v is number => v !== null);
    const right = series.flatMap((s, k) => (s.y2 && has2 ? vals(k) : [])).filter((v): v is number => v !== null);
    return { xs, at, stacked, bases, b1: bounds(left, stack), b2: bounds(right, false) };
  }, [series, stack, has2]);

  const { xs, at, stacked, bases, b1, b2 } = model;
  const t0 = hod ? 0 : xs[0] ?? 0, t1 = hod ? 23 : xs[xs.length - 1] ?? 1;
  const px = (t: number) => L + ((t - t0) / (t1 - t0 || 1)) * (plotR - L);
  const py = (v: number, b: Bounds) => TOP + ((b.hi - v) / (b.hi - b.lo || 1)) * (height - TOP - BOT);
  const xTicks = hod ? [0, 4, 8, 12, 16, 20, 23] : (() => { const n = Math.max(2, Math.min(7, Math.floor((plotR - L) / 110))); return x === "year" ? yearTicks(t0, t1, n) : Array.from({ length: n }, (_, i) => t0 + ((t1 - t0) * i) / (n - 1)); })();

  // each series' path, thinned to the pixels it has; a stacked series is an area from the series below it (or zero) to its own top
  const drawn = series.map((s, k) => {
    const b = s.y2 && has2 ? b2 : b1;
    const pts: Pt[] = stacked ? xs.map((t, i) => [t, stacked[k][i]]) : s.points;
    const thinned = thin(pts, Math.max(10, Math.round(plotR - L)));
    const segs: string[] = [];
    let open = false, prevY = "";
    for (const p of thinned) {
      if (p[1] === null) { open = false; continue; }
      const X = px(p[0]).toFixed(1), Y = py(p[1], b).toFixed(1);
      if (!open) { segs.push(`M${X},${Y}`); open = true; }
      else if (s.step) segs.push(`L${X},${prevY}`, `L${X},${Y}`);
      else segs.push(`L${X},${Y}`);
      prevY = Y;
    }
    let area = "";
    if (stacked && bases) {
      const held = xs.map((_, i) => (stacked[k][i] === null ? -1 : i)).filter((i) => i >= 0);
      if (held.length) {
        const top = (i: number) => `${px(xs[i]).toFixed(1)},${py(stacked[k][i]!, b).toFixed(1)}`;
        const base = (i: number) => `${px(xs[i]).toFixed(1)},${py(bases[k][i], b).toFixed(1)}`;
        area = `M${base(held[0])} ` + held.map((i) => `L${top(i)}`).join(" ") + " " + [...held].reverse().map((i) => `L${base(i)}`).join(" ") + " Z";
      }
    }
    const lastHeld = [...pts].reverse().find((p) => p[1] !== null);
    let endY: number | null = lastHeld ? py(lastHeld[1]!, b) : null;
    if (stacked && bases && lastHeld && endY !== null) {
      const i = xs.indexOf(lastHeld[0]);
      const bl = bases[k][i];
      endY = (endY + py(bl, b)) / 2;   // the name at the middle of the band's right edge
    }
    return { s, d: segs.join(" "), area, endY, color: tokenColor(s.color) };
  });

  // the names at the right, pushed apart so none covers another
  // session 332: a name wider than the gutter (capped at 150 px) ran past the drawing at every width; it is written on as
  // many lines as the gutter needs, broken between words, and the names below it make room for its lines
  const fitW = Math.max(40, gutter - 8);
  const lines = (name: string): string[] => {
    if (name.length * 6.2 <= fitW) return [name];
    const out: string[] = [];
    let cur = "";
    for (const w of name.split(" ")) { const t = cur ? `${cur} ${w}` : w; if (t.length * 6.2 > fitW && cur) { out.push(cur); cur = w; } else cur = t; }
    if (cur) out.push(cur);
    return out;
  };
  const labels = drawn.map((d, k) => ({ k, y: d.endY ?? py(0, b1), n: lines(d.s.name).length })).sort((a, b) => a.y - b.y);
  for (let i = 1; i < labels.length; i++) if (labels[i].y < labels[i - 1].y + 13 * labels[i - 1].n) labels[i].y = labels[i - 1].y + 13 * labels[i - 1].n;
  // session 584: the last name's last line is kept inside the drawing before the names above it make room (six grids'
  // names on a phone, or a three-line name at the bottom, ran up to 77 px below the chart and were cut); where all of
  // them do not fit between the top and the bottom, the first stays in view and the rest follow it down as before
  const floorY = height - 8;
  if (labels.length) { const z = labels[labels.length - 1]; if (z.y + 13 * (z.n - 1) > floorY) z.y = floorY - 13 * (z.n - 1); }
  for (let i = labels.length - 2; i >= 0; i--) if (labels[i].y > labels[i + 1].y - 13 * labels[i].n) labels[i].y = labels[i + 1].y - 13 * labels[i].n;
  if (labels.length && labels[0].y < 10) { labels[0].y = 10; for (let i = 1; i < labels.length; i++) if (labels[i].y < labels[i - 1].y + 13 * labels[i - 1].n) labels[i].y = labels[i - 1].y + 13 * labels[i - 1].n; }

  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!xs.length) return;
    const r = e.currentTarget.getBoundingClientRect();
    const t = t0 + ((e.clientX - r.left - L) / (plotR - L)) * (t1 - t0);
    let lo = 0, hi = xs.length - 1;
    while (lo < hi) { const m = (lo + hi) >> 1; if (xs[m] < t) lo = m + 1; else hi = m; }
    const i = lo > 0 && Math.abs(xs[lo - 1] - t) < Math.abs(xs[lo] - t) ? lo - 1 : lo;
    setHover({ t: xs[i], px: px(xs[i]) });
  };
  const unitOf = (s: TimeSeries) => (s.y2 && has2 ? unit2 : unit);
  // session 1152: a value's share of the sum of every series at the time (negative values, a battery charging, count as they are)
  const shareOf = (v: number, t: number) => { const sum = at.reduce((a, m) => a + (m.get(t) ?? 0), 0); return sum ? `, ${((v / sum) * 100).toFixed(1)}%` : ""; };
  const pages = Math.ceil(xs.length / PAGE);

  if (mini) {
    return (
      <svg viewBox={`0 0 ${W} ${height}`} width="100%" height={height} role="img" aria-label={ariaLabel} data-time-chart="mini" preserveAspectRatio="none">
        <title>{ariaLabel}</title>
        {drawn.map((d) => <path key={d.s.name} d={d.d} fill="none" stroke={d.color} strokeWidth="1.5" strokeDasharray={d.s.dashed ? "4 3" : undefined} vectorEffect="non-scaling-stroke" />)}
      </svg>
    );
  }
  return (
    <div ref={wrap} className="relative w-full min-w-0" data-time-chart={stack ? "stacked" : "lines"} data-x={x}>
      <div className="mb-1 flex items-baseline justify-end">
        <span className="inline-grid grid-cols-2 border border-muted text-xs" role="group" aria-label={`${ariaLabel}: chart or table`} data-chart-table="1">
          {([["chart", "Chart"], ["table", "Table"]] as const).map(([k, label], i) => (
            <button key={k} type="button" aria-pressed={table === (k === "table")} data-show={k} onClick={() => setTable(k === "table")}
              className={`px-2.5 py-0.5 ${i ? "border-l border-muted" : ""} ${table === (k === "table") ? "bg-ink text-white" : "bg-white text-ink"}`}>{label}</button>
          ))}
        </span>
      </div>
      {table ? (
        <div className="overflow-x-auto" data-chart-as-table="1">
          <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 320 }}>
            <caption className="sr-only">{ariaLabel}, as a table</caption>
            <thead><tr><th scope="col" className="px-3 py-1.5 font-normal">Period</th>{series.map((s) => <th key={s.name} scope="col" className="px-3 py-1.5 text-right font-normal">{s.name}, {unitOf(s)}</th>)}</tr></thead>
            <tbody>
              {xs.slice(page * PAGE, (page + 1) * PAGE).map((t) => (
                <tr key={t} className="border-b border-rule">
                  <th scope="row" className="px-3 py-1.5 font-normal">{fmt(t)}</th>
                  {series.map((s, k) => { const v = at[k].get(t); return <td key={s.name} className="px-3 py-1.5 text-right font-mono">{v === null || v === undefined ? <span className="font-sans text-muted">not held</span> : num(v)}</td>; })}
                </tr>
              ))}
            </tbody>
          </table>
          {pages > 1 ? (
            <p className="mt-1 flex items-center gap-3 text-xs text-muted" data-table-pages={pages}>
              <span>Rows {page * PAGE + 1} to {Math.min(xs.length, (page + 1) * PAGE)} of {xs.length.toLocaleString("en-US")}.</span>
              <button type="button" className="border border-muted px-2 py-0.5 text-ink disabled:opacity-40" disabled={page === 0} onClick={() => setPage(page - 1)}>Earlier</button>
              <button type="button" className="border border-muted px-2 py-0.5 text-ink disabled:opacity-40" disabled={page >= pages - 1} onClick={() => setPage(page + 1)}>Later</button>
            </p>
          ) : null}
        </div>
      ) : (
        <>
          <svg viewBox={`0 0 ${W} ${height}`} width={W} height={height} className="block max-w-full" role="img" aria-label={ariaLabel} onMouseMove={onMove} onMouseLeave={() => setHover(null)}
            data-n={xs.length} data-points={xs.length <= 100 ? JSON.stringify(series.map((s, k) => xs.map((t) => [t, at[k].get(t) ?? null]))) : undefined}>
            <title>{ariaLabel}</title>
            {ticksOf(b1).map((v) => (
              <g key={`y${v}`}>
                <line x1={L} x2={plotR} y1={py(v, b1)} y2={py(v, b1)} stroke={v === 0 ? "var(--color-ink)" : "var(--color-rule)"} strokeWidth={v === 0 ? 1 : 0.75} />
                <text x={L - 6} y={py(v, b1) + 4} textAnchor="end" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text>
              </g>
            ))}
            {has2 ? ticksOf(b2).map((v) => <text key={`y2${v}`} x={plotR + 6} y={py(v, b2) + 4} textAnchor="start" fontSize="12" fill="var(--color-muted)">{axisNum(v)}</text>) : null}
            {refLines?.map((r) => (
              <g key={r.name}>
                <line x1={L} x2={plotR} y1={py(r.value, b1)} y2={py(r.value, b1)} stroke="var(--color-accent)" strokeWidth="1" strokeDasharray={r.dashed ? "4 3" : undefined} />
                <text x={plotR - 2} y={py(r.value, b1) - 3} textAnchor="end" fontSize="11" fill="var(--color-accent)">{r.name}</text>
              </g>
            ))}
            <text x={L} y={11} fontSize="12" fill="var(--color-muted)">{unit}</text>
            {has2 ? <text x={plotR + 6} y={11} fontSize="12" fill="var(--color-muted)">{unit2}</text> : null}
            {xTicks.map((t, i) => (
              <text key={`x${i}`} x={px(t)} y={height - BOT + 16} textAnchor={x === "year" ? (t === t0 ? "start" : t === t1 ? "end" : "middle") : i === 0 ? "start" : i === xTicks.length - 1 ? "end" : "middle"} fontSize="12" fill="var(--color-muted)">{TICK[x](t, t1 - t0)}</text>
            ))}
            {drawn.map((d) => (d.area ? <path key={`a${d.s.name}`} d={d.area} fill={d.color} fillOpacity="0.85" stroke="var(--color-surface)" strokeWidth="0.75" /> : null))}
            {drawn.map((d) => (d.area ? null : <path key={`l${d.s.name}`} d={d.d} fill="none" stroke={d.color} strokeWidth="1.5" strokeDasharray={d.s.dashed ? "4 3" : undefined} strokeLinejoin="round" />))}
            <g data-direct-labels="1">
              {labels.map(({ k, y }) => <text key={drawn[k].s.name} x={plotR + (has2 ? 50 : 6)} y={y + 4} fontSize="12" fill={drawn[k].color}>{lines(drawn[k].s.name).map((ln, j) => <tspan key={j} x={plotR + (has2 ? 50 : 6)} dy={j ? 13 : 0}>{ln}</tspan>)}</text>)}
            </g>
            {marks?.filter((m) => m.t >= t0 && m.t <= t1).map((m) => (
              <g key={`m${m.t}`} data-chart-mark={m.name}>
                <line x1={px(m.t)} x2={px(m.t)} y1={TOP} y2={height - BOT} stroke="var(--color-accent)" strokeWidth="1" strokeDasharray="2 2" />
                <text x={px(m.t)} y={TOP - 4} textAnchor={px(m.t) > (L + plotR) / 2 ? "end" : "start"} fontSize="12" fill="var(--color-accent)">{m.name}</text>
              </g>
            ))}
            {hover ? <line x1={hover.px} x2={hover.px} y1={TOP} y2={height - BOT} stroke="var(--color-muted)" strokeWidth="1" strokeDasharray="3 3" /> : null}
          </svg>
          {hover ? (
            <div className="pointer-events-none absolute top-6 z-10 border border-rule bg-paper px-3 py-2 text-xs" style={{ left: Math.min(Math.max(0, hover.px + 10), Math.max(0, W - 230)) }} data-chart-card="1">
              <div className="text-ink">{fmt(hover.t)}</div>
              {series.map((s, k) => { const v = at[k].get(hover.t); return (
                <div key={s.name} className="flex justify-between gap-4"><span style={{ color: tokenColor(s.color) }}>{s.name}</span><span className="font-mono text-ink">{v === null || v === undefined ? "not held" : `${num(v)} ${unitOf(s)}${share ? shareOf(v, hover.t) : ""}`}</span></div>
              ); })}
              {marks?.filter((m) => m.t === hover.t).map((m) => <div key={`m${m.t}`} className="text-accent" data-chart-card-mark="1">{m.name}</div>)}
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
