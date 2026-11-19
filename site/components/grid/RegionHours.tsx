"use client";
// Energy Research Warehouse (ERW) site, session 8605 (chain 504): a region's generation by source, hour by hour, for
// the newest 35 days of its mix file (the Mix tab of /grid?region=...).
//
// Why a chart of its own. On the Carolinas' real file solar, hydro and storage are below zero for hundreds of the 840
// hours (the night, a pumped storage plant pumping, batteries charging). The average day's chart draws a line down to
// zero wherever a source crosses it, which over 35 days is a comb; the time chart of the grid's own hourly mix fills
// the plot with the crossing sources. This one draws each hour as its own column by the mix library's rule (lib/mix2.ts
// `stack`, lib/gridregions.ts `hourStack`): what is above zero up from zero, what is below zero down from zero. An hour
// a source does not hold is a gap in that source, never a filled point. Demand is a line over the columns.
// The mouse reads the hour and every source's megawatts; a table holds the same hours.
import { useMemo, useState } from "react";
import { DataTable, Toggle, bounds, num, ticksOf, useWidth } from "@/components/svgchart";
import { LINE, stackNames, wrapName } from "@/lib/chartwrap";
import { hourStack } from "@/lib/gridregions";

export type HourLayer = { key: string; label: string; color: string; values: (number | null)[] };

const utc = (ms: number) => new Date(ms).toISOString().slice(0, 16).replace("T", " ");

export function RegionHours({ id, t, layers, demand, tz, label, height = 300 }: { id: string; /** each hour's start, milliseconds */ t: number[]; layers: HourLayer[]; demand?: (number | null)[];
  /** the region's time zone, for the hover's local hour */ tz: string; label: string; height?: number }) {
  const [wrap, W] = useWidth<HTMLDivElement>();
  const [table, setTable] = useState(false);
  const [at, setAt] = useState<number | null>(null);
  const n = t.length;
  const stacks = useMemo(() => t.map((_, i) => hourStack(layers.map((l) => l.values[i]))), [t, layers]);
  const b = useMemo(() => bounds([...stacks.map((s) => s.top), ...stacks.map((s) => s.bottom), ...(demand ?? []).filter((v): v is number => v !== null && v !== undefined)]), [stacks, demand]);
  // session 8611 (docs/brand.md, section 6): each source is named at the right end of its columns, in its own color, as
  // the site's other charts name their series; there is no legend row above the plot
  const L = 58, R = W < 520 ? 78 : 104, TOP = 8, BOT = 26, plotW = Math.max(40, W - L - R), plotH = height - TOP - BOT;
  const bw = plotW / Math.max(1, n);
  const y = (v: number) => TOP + plotH * (1 - (v - b.lo) / (b.hi - b.lo || 1));
  const r1 = (v: number) => Math.round(v * 100) / 100;
  // one path a source: a column an hour, from the band's lower end to its upper. A column is a quarter of a pixel wider
  // than its hour, so that two neighbours leave no seam (columns snapped to whole pixels left a white line every 140 hours)
  const paths = useMemo(() => layers.map((l, k) => {
    let d = "";
    for (let i = 0; i < n; i += 1) {
      const band = stacks[i].bands[k];
      if (!band) continue;
      d += `M${r1(L + i * bw)},${r1(y(band[0]))}V${r1(y(band[1]))}h${r1(Math.max(bw, 0.5) + (i < n - 1 ? 0.25 : 0))}V${r1(y(band[0]))}Z`;
    }
    return { key: l.key, color: l.color, d };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }), [layers, stacks, n, bw, b.lo, b.hi, plotH]);
  // demand: a line, broken where an hour is not held
  const line = useMemo(() => {
    if (!demand) return "";
    let d = "", pen = false;
    for (let i = 0; i < n; i += 1) {
      const v = demand[i];
      if (v === null || v === undefined) { pen = false; continue; }
      d += `${pen ? "L" : "M"}${r1(L + (i + 0.5) * bw)},${r1(y(v))}`;
      pen = true;
    }
    return d;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demand, n, bw, b.lo, b.hi, plotH]);
  // the names at the right: each source at the middle of its band in the newest hour that holds one, demand at its
  // newest value; a name that would lie on another is moved down, and a long one is wrapped (lib/chartwrap.ts)
  const ends = useMemo(() => {
    const out: { key: string; name: string; color: string; y: number; lines: string[] }[] = [];
    layers.forEach((l, k) => {
      for (let i = n - 1; i >= 0; i -= 1) { const band = stacks[i].bands[k]; if (band) { out.push({ key: l.key, name: l.label, color: l.color, y: y((band[0] + band[1]) / 2), lines: [] }); break; } }
    });
    if (demand) for (let i = n - 1; i >= 0; i -= 1) { const v = demand[i]; if (v !== null && v !== undefined) { out.push({ key: "demand", name: "Demand", color: "var(--color-ink)", y: y(v), lines: [] }); break; } }
    for (const e of out) e.lines = wrapName(e.name, R - 10);
    return stackNames(out, height - 6);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [layers, stacks, demand, n, b.lo, b.hi, plotH, R, height]);
  // a mark on the time axis at each UTC midnight a whole number of weeks from the first
  const marks = useMemo(() => {
    const first = t.findIndex((ms) => new Date(ms).getUTCHours() === 0);
    const out: { i: number; text: string }[] = [];
    const every = W < 520 ? 14 : 7;
    for (let i = first; i >= 0 && i < n; i += 24 * every) out.push({ i, text: new Date(t[i]).toISOString().slice(5, 10) });
    return out;
  }, [t, n, W]);
  const local = (ms: number) => new Intl.DateTimeFormat("en-US", { timeZone: tz, weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(ms));
  const show = (v: number | null | undefined) => (v === null || v === undefined ? "not held" : `${num(Math.round(v) || 0, 0)} MW`);
  return (
    <div ref={wrap} className="relative" data-region-hours-chart={id} data-hours={n}>
      <Toggle label={label} table={table} setTable={setTable} id={id} />
      {table ? (
        <div className="max-h-96 overflow-y-auto">
          <DataTable id={id} label={label} head={["Hour, UTC", ...layers.map((l) => `${l.label}, MW`), ...(demand ? ["Demand, MW"] : [])]}
            rows={t.map((ms, i) => ({ key: String(ms), cells: [utc(ms), ...layers.map((l) => (l.values[i] === null || l.values[i] === undefined ? "not held" : num(Math.round(l.values[i] as number) || 0, 0))), ...(demand ? [demand[i] === null || demand[i] === undefined ? "not held" : num(Math.round(demand[i] as number), 0)] : [])] }))} />
        </div>
      ) : (
        <>
          <svg width={W} height={height} role="img" aria-label={`${label}. Each hour is a column: sources above zero are stacked up from zero, sources below zero down from zero. The table holds every hour.`} className="block max-w-full"
            onPointerMove={(e) => { const box = e.currentTarget.getBoundingClientRect(); const i = Math.floor((e.clientX - box.left - L) / bw); setAt(i >= 0 && i < n ? i : null); }} onPointerLeave={() => setAt(null)}>
            <text x={L} y={TOP + 4} className="fill-muted" fontSize="12" textAnchor="end" dx={-6}>MW</text>
            {ticksOf(b).map((v) => (
              <g key={v}>
                <line x1={L} x2={L + plotW} y1={y(v)} y2={y(v)} stroke={v === 0 ? "var(--color-ink)" : "var(--color-rule)"} strokeWidth={v === 0 ? 1 : 0.6} />
                {y(v) > TOP + 14 ? <text x={L - 6} y={y(v) + 4} fontSize="12" textAnchor="end" className="fill-muted">{Math.abs(v) >= 1e4 ? `${+(v / 1e3).toFixed(1)}k` : num(v)}</text> : null}
              </g>
            ))}
            <g>
              {paths.map((p) => (p.d ? <path key={p.key} d={p.d} fill={p.color} data-hours-layer={p.key} /> : null))}
            </g>
            {line ? <path d={line} fill="none" stroke="var(--color-ink)" strokeWidth={1.2} data-hours-demand="1" /> : null}
            {marks.map((m) => (
              <g key={m.i}>
                <line x1={L + m.i * bw} x2={L + m.i * bw} y1={TOP + plotH} y2={TOP + plotH + 4} stroke="var(--color-muted)" />
                <text x={L + m.i * bw} y={height - 6} fontSize="12" textAnchor="middle" className="fill-muted">{m.text}</text>
              </g>
            ))}
            {ends.map((e) => (
              <text key={e.key} x={L + plotW + 6} y={e.y + 4} fontSize="12" fill={e.color} data-hours-name={e.key}>
                {e.lines.map((line, i) => <tspan key={i} x={L + plotW + 6} dy={i ? LINE : 0}>{line}</tspan>)}
              </text>
            ))}
            {at !== null ? <line x1={L + (at + 0.5) * bw} x2={L + (at + 0.5) * bw} y1={TOP} y2={TOP + plotH} stroke="var(--color-ink)" strokeWidth={0.8} /> : null}
          </svg>
          {at !== null ? (
            // the site's hover card (docs/brand.md, section 6): the period, then each series named in its color with its figure in mono
            <div className="pointer-events-none absolute top-6 z-10 border border-rule bg-paper px-3 py-2 text-xs" style={{ left: Math.min(Math.max(0, L + (at + 0.5) * bw + 10), Math.max(0, W - 240)) }} data-hours-card={t[at]} data-chart-card="1">
              <div className="text-ink">{utc(t[at])} UTC ({local(t[at])})</div>
              {layers.map((l) => <div key={l.key} className="flex justify-between gap-4"><span style={{ color: l.color }}>{l.label}: </span><span className="font-mono text-ink">{show(l.values[at])}</span></div>)}
              {demand ? <div className="flex justify-between gap-4"><span className="text-ink">Demand: </span><span className="font-mono text-ink">{show(demand[at])}</span></div> : null}
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
