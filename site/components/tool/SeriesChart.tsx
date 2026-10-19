"use client";
// Session 296 (the owner's rulings of 15 October 2026, items 4, 5 and 9): one chart for a tool page, in the brand's
// manner (docs/brand.md, section 6; the battery page's year chart is the reference): stacked bars or lines, the series
// named on the chart in their own colors (no legend box), a figure written above each bar, an incomplete period
// hatched, the grid lines in the rule color and the zero line in ink, every color a token of app/tokens.css. Each
// chart has a Chart | Table toggle (item 9) and draws at one of three scales (item 5): linear; log (base 10, when every
// value is above zero: otherwise the chart says so and draws linear); adjusted, the battery page's own rule, where one
// period far above the others is drawn to the top of the scale with a break mark and its value written, so the rest
// stay readable. Plain SVG; no chart library. No number is computed here: the page hands it the values.
import { useState, type ReactNode } from "react";

export type Scale = "linear" | "log" | "adjusted";
export const SCALES: { key: Scale; label: string; words: string }[] = [
  { key: "linear", label: "Linear", words: "every value to one scale" },
  { key: "log", label: "Log", words: "base 10: equal steps are equal ratios; drawn only when every value is above zero" },
  { key: "adjusted", label: "Adjusted", words: "a period more than 2.5 times the next is drawn to the top of the scale with a break and its value written" },
];
export type ChartSeries = { name: string; color: string; values: (number | null)[] };
export type ChartCategory = { label: string; sub?: string; partial?: boolean };
type Props = {
  /** a name for the chart's own patterns and ids, unique on the page */
  id: string; title: string; unit: string; categories: ChartCategory[]; series: ChartSeries[];
  kind: "stacked" | "line"; scale: Scale;
  /** how a figure is written, above a bar and in the table */
  fmt?: (v: number) => string;
  /** one line under the chart, and a tip beside the title (the page's own) */
  note?: ReactNode; tip?: ReactNode;
  /** the words of the hover of one category ("2021: energy 3,431 ...") */
  says?: (i: number) => string;
  partialWords?: string;
  /** the table first: the chart on request */
  tableFirst?: boolean;
};

const W = 760, H = 300, L = 60, R = 12, TOP = 28, BOT = 44;
const nice = (span: number) => [0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000].find((s) => span / s <= 5) ?? 20000;
const plain = (v: number) => Math.round(v).toLocaleString("en-US");

export function SeriesChart({ id, title, unit, categories, series, kind, scale, fmt = plain, note, tip, says, partialWords = "Incomplete period", tableFirst = false }: Props) {
  const [table, setTable] = useState(tableFirst);
  const n = categories.length;
  // the figure of a category: the sum of its series (stacked), or each series' own value (lines)
  const totals = categories.map((_, i) => series.reduce((a, s) => a + (s.values[i] ?? 0), 0));
  const all = kind === "stacked" ? totals : series.flatMap((s) => s.values).filter((v): v is number => v !== null);
  const positive = all.every((v) => v > 0);
  const useLog = scale === "log" && positive && all.length > 0;
  const sorted = [...(kind === "stacked" ? totals : all)].sort((a, b) => b - a);
  const broken = scale === "adjusted" && sorted.length > 2 && sorted[0] > 2.5 * sorted[1];
  const hiRaw = broken ? sorted[1] : sorted[0] ?? 1;
  const negs = kind === "stacked" ? categories.map((_, i) => series.reduce((a, s) => a + Math.min(0, s.values[i] ?? 0), 0)) : all.map((v) => Math.min(0, v));
  const lo = useLog ? Math.min(...all) : Math.min(0, ...negs);
  const hi = useLog ? Math.max(...all) : (hiRaw * 1.15 || 1);
  const ly = (v: number) => Math.log10(v);
  const y = (v: number) => {
    if (useLog) { const a = ly(Math.max(v, lo)); return TOP + ((ly(hi) - a) / (ly(hi) - ly(lo) || 1)) * (H - TOP - BOT); }
    return TOP + ((hi - v) / (hi - lo || 1)) * (H - TOP - BOT);
  };
  const ticks: number[] = [];
  if (useLog) { for (let p = Math.floor(ly(lo)); p <= Math.ceil(ly(hi)); p++) ticks.push(10 ** p); }
  else { const step = nice(hi - lo); for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(Math.round(t * 1e6) / 1e6); }
  const bw = (W - L - R) / Math.max(1, n);
  const cx = (i: number) => L + i * bw + bw / 2;
  const capped = (v: number) => Math.min(v, useLog ? hi : hi);
  const names = (
    <g data-direct-labels="1">
      {series.map((s, k) => (
        <text key={s.name} x={W - R - (series.length - 1 - k) * 150} y={14} textAnchor="end" fontSize="12" fill={s.color}>{s.name}</text>
      ))}
      {categories.some((c) => c.partial) ? <text x={L + 4} y={14} fontSize="12" fill="var(--color-muted)">{partialWords}: hatched</text> : null}
    </g>
  );
  const toggle = (
    <span className="inline-grid grid-cols-2 border border-muted text-xs" role="group" aria-label={`${title}: chart or table`} data-chart-table={id}>
      {([["chart", "Chart"], ["table", "Table"]] as const).map(([k, label], i) => (
        <button key={k} type="button" aria-pressed={table === (k === "table")} data-show={k} onClick={() => setTable(k === "table")}
          className={`px-2.5 py-0.5 ${i ? "border-l border-muted" : ""} ${table === (k === "table") ? "bg-ink text-white" : "bg-white text-ink"}`}>{label}</button>
      ))}
    </span>
  );
  return (
    <figure className="mb-10 min-w-0" data-series-chart={id} data-scale={useLog ? "log" : broken ? "adjusted" : "linear"}>
      <figcaption className="mb-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b border-rule pb-1">
        <span className="font-serif text-xl text-accent">{title}{tip}</span>
        {toggle}
      </figcaption>
      {table ? (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm tabular-nums" style={{ minWidth: 320 }} data-chart-as-table={id}>
            <caption className="sr-only">{title}, as a table</caption>
            <thead><tr><th scope="col" className="px-3 py-1.5 font-normal">Period</th>{series.map((s) => <th key={s.name} scope="col" className="px-3 py-1.5 text-right font-normal">{s.name}, {unit}</th>)}{kind === "stacked" && series.length > 1 ? <th scope="col" className="px-3 py-1.5 text-right font-normal">Total, {unit}</th> : null}</tr></thead>
            <tbody>
              {categories.map((c, i) => (
                <tr key={c.label} className="border-b border-rule">
                  <th scope="row" className="px-3 py-1.5 font-normal">{c.label}{c.sub ? <span className="block text-xs text-muted">{c.sub}</span> : null}</th>
                  {series.map((s) => <td key={s.name} className="px-3 py-1.5 text-right">{s.values[i] === null ? <span className="text-muted">not held</span> : fmt(s.values[i]!)}</td>)}
                  {kind === "stacked" && series.length > 1 ? <td className="px-3 py-1.5 text-right">{fmt(totals[i])}</td> : null}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${title}, ${unit}${kind === "stacked" ? ", stacked" : ""}: ${series.map((s) => s.name).join(", ")}`}>
          <defs>
            {series.map((s, k) => (
              <pattern key={k} id={`${id}-hatch-${k}`} width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="var(--color-surface)" /><rect width="2.2" height="5" fill={s.color} /></pattern>
            ))}
          </defs>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke={t === 0 ? "var(--color-ink)" : "var(--color-rule)"} strokeWidth={t === 0 ? 1 : 0.75} />
              <text x={L - 6} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-muted)">{fmt(t)}</text>
            </g>
          ))}
          <text x={2} y={14} fontSize="11" fill="var(--color-muted)">{unit}</text>
          {names}
          {kind === "stacked" ? categories.map((c, i) => {
            const x0 = L + i * bw + bw * 0.18, w = bw * 0.64;
            const over = broken && totals[i] > hi;
            let up = 0, down = 0;
            const segs: { v0: number; v1: number; k: number }[] = [];
            series.forEach((s, k) => {
              const v = s.values[i] ?? 0;
              if (v >= 0) { segs.push({ v0: up, v1: up + v, k }); up += v; }
              else { segs.push({ v0: down + v, v1: down, k }); down += v; }
            });
            return (
              <g key={c.label}>
                {segs.map((sg) => {
                  const a1 = capped(sg.v1), a0 = useLog ? Math.max(sg.v0, lo) : capped(sg.v0);
                  if (a1 <= a0 && !useLog) return null;
                  const top = y(useLog ? Math.max(a1, lo) : a1), bottom = y(useLog ? Math.max(a0, lo) : a0);
                  if (bottom - top <= 0) return null;
                  return <rect key={sg.k} x={x0} width={w} y={top} height={Math.max(0.5, bottom - top)} fill={c.partial ? `url(#${id}-hatch-${sg.k})` : series[sg.k].color} stroke={c.partial ? series[sg.k].color : "none"} strokeWidth={c.partial ? 0.75 : 0} />;
                })}
                {over ? <path d={`M${x0 - 3},${TOP + 14} l${w / 4 + 1.5},-5 l${w / 4},5 l${w / 4},-5 l${w / 4 + 1.5},5`} fill="none" stroke="var(--color-surface)" strokeWidth="3" /> : null}
                <text x={cx(i)} y={(over ? TOP : y(capped(Math.max(up, useLog ? lo : 0)))) - 6} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{fmt(totals[i])}</text>
                <text x={cx(i)} y={H - BOT + 16} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{c.label}</text>
                {c.sub ? <text x={cx(i)} y={H - BOT + 30} textAnchor="middle" fontSize="10" fill="var(--color-muted)">{c.sub}</text> : null}
                <title>{says ? says(i) : `${c.label}: ${series.map((s) => `${s.name} ${s.values[i] === null ? "not held" : fmt(s.values[i]!)}`).join(", ")} ${unit}`}</title>
              </g>
            );
          }) : (
            <>
              {series.map((s, k) => {
                const pts = s.values.map((v, i) => (v === null ? null : [cx(i), y(capped(v))] as [number, number]));
                const d = pts.map((p, i) => (p ? `${i === 0 || !pts[i - 1] ? "M" : "L"}${p[0].toFixed(1)},${p[1].toFixed(1)}` : "")).join(" ");
                const last = [...pts].reverse().find((p) => p);
                return (
                  <g key={s.name} data-line={k}>
                    <path d={d} fill="none" stroke={s.color} strokeWidth="1.5" />
                    {last ? <text x={Math.min(last[0] + 4, W - R - 2)} y={last[1] - 4} textAnchor={last[0] > W - R - 80 ? "end" : "start"} fontSize="12" fill={s.color}>{s.name}</text> : null}
                    {pts.map((p, i) => (p ? <circle key={i} cx={p[0]} cy={p[1]} r="2" fill={s.color}><title>{`${categories[i].label}: ${s.name} ${fmt(s.values[i]!)} ${unit}`}</title></circle> : null))}
                  </g>
                );
              })}
              {categories.map((c, i) => (n <= 12 || i % Math.ceil(n / 10) === 0 || i === n - 1 ? <text key={c.label} x={cx(i)} y={H - BOT + 16} textAnchor="middle" fontSize="11" fill="var(--color-ink)">{c.label}</text> : null))}
            </>
          )}
        </svg>
      )}
      {scale === "log" && !useLog ? <p className="mt-2 max-w-3xl text-xs text-muted" data-log-refused="1">The log scale is not drawn: a value here is at or below zero, so the chart is linear.</p> : null}
      {note ? <p className="mt-2 max-w-3xl text-xs text-muted">{note}</p> : null}
    </figure>
  );
}
