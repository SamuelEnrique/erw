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
  const L = 58, R = 12, TOP = 8, BOT = 26, plotW = Math.max(40, W - L - R), plotH = height - TOP - BOT;
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
          <div className="mb-1 flex flex-wrap gap-x-3 gap-y-0.5 text-xs" aria-hidden="true">
            {layers.map((l) => <span key={l.key} className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5" style={{ background: l.color }} />{l.label}</span>)}
            {demand ? <span className="flex items-center gap-1"><span className="inline-block h-0.5 w-4 bg-ink" />Demand</span> : null}
          </div>
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
            {at !== null ? <line x1={L + (at + 0.5) * bw} x2={L + (at + 0.5) * bw} y1={TOP} y2={TOP + plotH} stroke="var(--color-ink)" strokeWidth={0.8} /> : null}
          </svg>
          {at !== null ? (
            <div className="pointer-events-none absolute top-12 z-10 border border-rule bg-paper px-3 py-2 text-xs" style={{ left: Math.min(Math.max(0, L + (at + 0.5) * bw + 10), Math.max(0, W - 230)) }} data-hours-card={t[at]}>
              <div className="text-ink">{utc(t[at])} UTC ({local(t[at])})</div>
              {layers.map((l) => <div key={l.key} className="tabular-nums"><span className="mr-1 inline-block h-2 w-2" style={{ background: l.color }} />{l.label}: {show(l.values[at])}</div>)}
              {demand ? <div className="tabular-nums">Demand: {show(demand[at])}</div> : null}
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
