"use client";
// Session 182: a finding card's chart as small multiples. Every grid with public prices on one timeline (the same x
// axis in every panel; the y axes shared or each grid's own, as the note on the chart says), each grid's measure
// against its own fleet from EIA-860M, and a control that shows one grid large. The choice is kept in the address
// (?<param>=<grid>, and ?<param>_measure=<key>), so a link opens the same view. The one-grid view is the old
// single-grid card's chart (lib/findingchart.ts), with that grid's callouts, its regression table where there is one,
// the effect in plain words and its caveat. Every number comes from the card's JSON, which a test reproduces.
import { useEffect, useRef, useState } from "react";
import { useEChart } from "@/components/echarts";
import { optionFor, type ChartSpec } from "@/lib/findingchart";

type Box = { label: string; before: { period: string; text: string }; after: { period: string; text: string }; unit: string };
type Row = { measure: string; coef_per_gw: number | null; se: number | null; p: number | null; n: number; r2: number | null };
export type MultiPanel = {
  grid: string; words: string; title: string; first: string; last: string; values: Record<string, (number | null)[]>;
  fleet: (number | null)[]; days?: (number | null)[]; single: ChartSpec; callouts: Box[]; table: Row[]; in_words: string; caveat: string;
};
export type MultiSpec = {
  kind: "multiples"; param: string; x: string[]; x_label: string; measures: { key: string; label: string; unit: string; decimals: number }[];
  fleet_label: string; fleet_unit: string; axis_note: string; fleet_axis: "shared" | "own"; measure_axis: "shared" | "own";
  table_columns?: string[]; panels: MultiPanel[]; all_label: string;
};

const INK = "#1a1a1a", MUTED = "#6b6b6b", RULE = "#e5e5e5", LINE = "#1f5f8b", FLEET = "#2e7d4f";
const fmt = (v: number | null | undefined, nd = 1) => (v === null || v === undefined || Number.isNaN(v) ? "not held" : v.toLocaleString("en-US", { maximumFractionDigits: nd, minimumFractionDigits: nd }));
const fmtP = (p: number | null) => (p === null ? "not held" : p < 0.001 ? "< 0.001" : p.toFixed(3));
const top = (vs: (number | null)[][]) => Math.max(0, ...vs.flat().filter((v): v is number => v !== null && v !== undefined));
export const MIN_ROW = 84; // a panel shorter than this is unreadable as a row: the panels then stand side by side
/** A round number at or above v for a shared axis's top: 18,204.5 reads 20,000 and 70.96 reads 80. */
export function niceTop(v: number): number | undefined {
  if (!(v > 0)) return undefined;
  const p = 10 ** Math.floor(Math.log10(v));
  return [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].map((s) => s * p).find((t) => t >= v) ?? v;
}

/** The small multiples as one ECharts option: a grid, an x axis and two y axes per panel, the x axes linked. */
export function multiOption(spec: MultiSpec, measureKey: string, W: number, H: number): Record<string, unknown> {
  const m = spec.measures.find((x) => x.key === measureKey) ?? spec.measures[0];
  const P = spec.panels;
  const rows = H / P.length >= MIN_ROW;
  const fleetMax = spec.fleet_axis === "shared" ? niceTop(top(P.map((p) => p.fleet))) : undefined;
  const measMax = spec.measure_axis === "shared" ? niceTop(top(P.map((p) => p.values[m.key] ?? []))) : undefined;
  const padTop = 6, padBottom = 30;
  const rowH = (H - padTop - padBottom) / P.length;
  const colW = (W - 8) / P.length;
  const place = (i: number) => (rows
    ? { left: 46, right: 52, top: padTop + i * rowH + 20, height: Math.max(20, rowH - 30) }
    : { left: 4 + i * colW + 40, width: Math.max(40, colW - 96), top: 30, bottom: padBottom + 6 });
  const label = { color: MUTED, fontSize: 10, formatter: (v: number | string) => (typeof v === "number" ? v.toLocaleString("en-US") : v) };
  return {
    animation: false,
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: INK },
    // on a phone the panel's title is cut to the grid, its node and its first period, so that it is read whole
    title: P.map((p, i) => ({ text: rows && W < 520 ? `${p.title.split(", every")[0]}, from ${p.first}` : p.title, left: rows ? 46 : 4 + i * colW + 6, top: rows ? padTop + i * rowH + 2 : 4,
      textStyle: { fontSize: rows ? 11 : 10, fontWeight: 600, color: INK, width: rows ? W - 100 : colW - 12, overflow: "truncate" } })),
    grid: P.map((_, i) => place(i)),
    axisPointer: { link: [{ xAxisIndex: "all" }] },
    tooltip: { trigger: "axis", confine: true, formatter: (ps: { dataIndex: number }[]) => {
      const i = ps[0]?.dataIndex ?? 0;
      const lines = [`${spec.x[i]}: ${m.label}; ${spec.fleet_label}`];
      for (const p of P) {
        const v = p.values[m.key]?.[i];
        const d = p.days?.[i];
        lines.push(v === null || v === undefined ? `${p.words}: not held`
          : `${p.words}: ${fmt(v, m.decimals)} ${m.unit}${d ? ` (${d} days)` : ""}; ${fmt(p.fleet[i], 0)} ${spec.fleet_unit}`);
      }
      return lines.join("<br/>");
    } },
    xAxis: P.map((_, i) => ({ type: "category", gridIndex: i, data: spec.x, boundaryGap: false,
      axisLabel: { ...label, show: rows ? i === P.length - 1 : true, hideOverlap: true }, axisTick: { show: false }, axisLine: { lineStyle: { color: RULE } },
      name: rows ? (i === P.length - 1 ? spec.x_label : "") : (i === Math.floor(P.length / 2) ? spec.x_label : ""), nameLocation: "middle", nameGap: 20, nameTextStyle: label })),
    yAxis: P.flatMap((_, i) => [
      { type: "value", gridIndex: i, position: "left", max: measMax, splitNumber: 2, axisLabel: label, splitLine: { lineStyle: { color: RULE } } },
      { type: "value", gridIndex: i, position: "right", max: fleetMax, splitNumber: 2, axisLabel: { ...label, color: FLEET }, splitLine: { show: false } },
    ]),
    series: P.flatMap((p, i) => [
      { name: `${p.words}: ${m.label}`, type: "line", xAxisIndex: i, yAxisIndex: 2 * i, data: p.values[m.key] ?? [], showSymbol: spec.x.length <= 12, symbolSize: 5,
        connectNulls: false, lineStyle: { width: 1.5, color: LINE }, itemStyle: { color: LINE } },
      { name: `${p.words}: ${spec.fleet_label}`, type: "line", xAxisIndex: i, yAxisIndex: 2 * i + 1, data: p.fleet, showSymbol: false, connectNulls: false,
        areaStyle: { color: FLEET, opacity: 0.12 }, lineStyle: { width: 1.2, color: FLEET }, itemStyle: { color: FLEET } },
    ]),
  };
}

function All({ spec, measure, label, height }: { spec: MultiSpec; measure: string; label: string; height: number }) {
  const [w, setW] = useState(0);
  const box = useEChart((chart) => {
    const el = box.current;
    if (!el) return;
    chart.setOption(multiOption(spec, measure, el.clientWidth, el.clientHeight), true);
  }, [spec, measure, w]);
  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setW(el.clientWidth));
    ro.observe(el);
    return () => ro.disconnect();
  }, [box]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" data-finding-chart="multiples" />;
}

function One({ spec, label }: { spec: ChartSpec; label: string }) {
  const box = useEChart((chart) => chart.setOption(optionFor(spec), true), [spec]);
  return <div ref={box} role="img" aria-label={label} style={{ height: 340 }} className="w-full" data-finding-chart={spec.kind} data-grid-chart="1" />;
}

export function MultiChart({ spec, label }: { spec: MultiSpec; label: string }) {
  const grids = spec.panels.map((p) => p.grid);
  const [sel, setSel] = useState("all");
  const [measure, setMeasure] = useState(spec.measures[0].key);
  const read = useRef(false);
  useEffect(() => {
    if (read.current) return;
    read.current = true;
    const q = new URLSearchParams(window.location.search);
    const g = q.get(spec.param), k = q.get(`${spec.param}_measure`);
    if (g && grids.includes(g)) setSel(g);
    if (k && spec.measures.some((x) => x.key === k)) setMeasure(k);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const keep = (g: string, k: string) => {
    const u = new URL(window.location.href);
    if (g === "all") u.searchParams.delete(spec.param); else u.searchParams.set(spec.param, g);
    if (k === spec.measures[0].key) u.searchParams.delete(`${spec.param}_measure`); else u.searchParams.set(`${spec.param}_measure`, k);
    window.history.replaceState(null, "", u.toString());
  };
  const pick = (g: string) => { setSel(g); keep(g, measure); };
  const pickMeasure = (k: string) => { setMeasure(k); keep(sel, k); };
  const panel = spec.panels.find((p) => p.grid === sel);
  const btn = (on: boolean) => `border px-2 py-1 text-xs ${on ? "border-ink bg-ink text-paper" : "border-rule bg-panel text-ink"}`;
  return (
    <div data-multi={spec.param} data-multi-view={sel}>
      <div className="multi-controls mb-2 mt-2 flex flex-wrap items-center gap-1" role="group" aria-label="Grid shown">
        <button type="button" className={btn(sel === "all")} aria-pressed={sel === "all"} onClick={() => pick("all")} data-multi-pick="all">{spec.all_label}</button>
        {spec.panels.map((p) => (
          <button key={p.grid} type="button" className={btn(sel === p.grid)} aria-pressed={sel === p.grid} onClick={() => pick(p.grid)} data-multi-pick={p.grid}>{p.words}</button>
        ))}
      </div>
      {panel ? (
        <div data-multi-grid={panel.grid}>
          <p className="text-xs font-semibold">{panel.title}</p>
          <One spec={panel.single} label={`${label}: ${panel.words}`} />
          <div className="mt-2 grid gap-3 sm:grid-cols-3">
            {panel.callouts.map((c, i) => (
              <div key={i} className="border border-rule bg-panel p-3" data-grid-callout={i}>
                <div className="text-[11px] uppercase tracking-wide text-muted">{c.label}</div>
                <div className="mt-1 text-sm"><span className="text-muted">{c.before.period}: </span><strong className="text-lg" data-grid-before={i}>{c.before.text}</strong><span className="text-muted">{c.unit ? ` ${c.unit}` : ""}</span></div>
                <div className="text-sm"><span className="text-muted">{c.after.period}: </span><strong className="text-lg" data-grid-after={i}>{c.after.text}</strong><span className="text-muted">{c.unit ? ` ${c.unit}` : ""}</span></div>
              </div>
            ))}
          </div>
          {panel.table.length ? (
            <div className="mt-3 overflow-x-auto" data-grid-table={panel.grid}>
              <table className="w-full max-w-3xl text-xs">
                <thead>
                  <tr className="border-b border-rule text-left text-muted">
                    {(spec.table_columns ?? ["Measure", "Coefficient", "SE", "p", "n", "R2"]).map((h, i) => <th key={h} className={i === 0 ? "py-1 pr-3" : "py-1 pr-3 text-right"}>{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {panel.table.map((r) => (
                    <tr key={r.measure} className="border-b border-rule">
                      <td className="py-1 pr-3">{r.measure}</td><td className="py-1 pr-3 text-right font-mono">{fmt(r.coef_per_gw, 2)}</td>
                      <td className="py-1 pr-3 text-right font-mono">{fmt(r.se, 2)}</td><td className="py-1 pr-3 text-right font-mono">{fmtP(r.p)}</td>
                      <td className="py-1 pr-3 text-right font-mono">{r.n}</td><td className="py-1 pr-3 text-right font-mono">{fmt(r.r2, 2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
          <p className="mt-2 max-w-3xl text-sm" data-grid-words={panel.grid}>{panel.in_words}</p>
          <p className="mt-1 max-w-3xl text-xs text-muted" data-grid-caveat={panel.grid}>{panel.caveat}</p>
        </div>
      ) : (
        <div>
          <div className="multi-controls mb-1 flex flex-wrap items-center gap-1" role="group" aria-label="Measure shown">
            {spec.measures.map((x) => (
              <button key={x.key} type="button" className={btn(measure === x.key)} aria-pressed={measure === x.key} onClick={() => pickMeasure(x.key)} data-multi-measure={x.key}>{x.label}</button>
            ))}
          </div>
          <p className="text-[11px] leading-snug text-muted" data-multi-note="1">
            <span style={{ color: LINE }}>Line</span>: {(spec.measures.find((x) => x.key === measure) ?? spec.measures[0]).label.toLowerCase()}.{" "}
            <span style={{ color: FLEET }}>Shaded</span>: {spec.fleet_label}. {spec.axis_note}
          </p>
          <All spec={spec} measure={measure} label={label} height={spec.panels.length * 112 + 40} />
          <ul className="multi-words mt-2 max-w-3xl list-none space-y-1 p-0 text-xs" data-multi-words="1">
            {spec.panels.map((p) => <li key={p.grid}>{p.in_words} <span className="text-muted">{p.caveat}</span></li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
