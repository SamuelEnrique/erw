"use client";
// Session 37: the cost-of-power page's charts and calculator. Every value drawn here arrives from the server
// (page.tsx), read from the cost_of_power_* tables; the calculator multiplies the reader's inputs by those prices.
import { useMemo, useState } from "react";
import { baseStyle, num, token, useEChart } from "@/components/echarts";
import { cheapPrice, energy, type Cell, PERIODS, DEFAULTS } from "@/lib/cost";

export function RankBars({ bars, label }: { bars: { name: string; value: number; partial: boolean }[]; label: string }) {
  const box = useEChart((chart) => {
    const s = baseStyle();
    const sorted = [...bars].sort((a, b) => a.value - b.value);
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 70, right: 60, top: 10, bottom: 30 },
      tooltip: { ...s.tooltip, trigger: "item", formatter: (p: { name: string; value: number }) => `${p.name}: ${num(p.value)} USD/MWh` },
      xAxis: { type: "value", name: "USD/MWh", nameLocation: "middle", nameGap: 22, ...s.axis },
      yAxis: { type: "category", data: sorted.map((b) => b.name), ...s.axis },
      series: [{
        type: "bar",
        data: sorted.map((b) => ({ value: b.value, itemStyle: { color: b.partial ? token("muted") : token("accent") } })),
        label: { show: true, position: "right", color: token("ink"), fontSize: 11, formatter: (p: { value: number }) => num(p.value) },
      }],
    }, true);
  }, [bars]);
  return <div ref={box} role="img" aria-label={label} style={{ height: 40 + bars.length * 34 }} className="w-full" />;
}

export function HeatGrid({ cells, label }: { cells: Cell[]; label: string }) {
  const months = useMemo(() => [...new Set(cells.map((c) => c.month))].sort(), [cells]);
  const box = useEChart((chart) => {
    const s = baseStyle();
    const vals = cells.map((c) => c.price);
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 60, right: 10, top: 8, bottom: 56 },
      tooltip: { ...s.tooltip, formatter: (p: { value: [number, number, number] }) => `${months[p.value[1]]}, ${String(p.value[0]).padStart(2, "0")}:00 local: ${num(p.value[2])} USD/MWh` },
      xAxis: { type: "category", data: Array.from({ length: 24 }, (_, h) => String(h)), name: "hour of day, local", nameLocation: "middle", nameGap: 22, ...s.axis, splitArea: { show: false } },
      yAxis: { type: "category", data: months, ...s.axis },
      visualMap: { min: Math.min(...vals), max: Math.max(...vals), calculable: false, orient: "horizontal", left: "center", bottom: 0, itemHeight: 90, itemWidth: 10,
        text: ["dear", "cheap"], textStyle: { color: token("muted"), fontSize: 10 }, inRange: { color: [token("panel"), token("var(--color-fuel-wind)"), token("accent")] } },
      series: [{ type: "heatmap", data: cells.map((c) => [c.hour, months.indexOf(c.month), c.price]) }],
    }, true);
  }, [cells, months]);
  return <div ref={box} role="img" aria-label={label} style={{ height: 90 + months.length * 18 }} className="w-full" />;
}

export function CostCarbon({ points, label }: { points: { name: string; x: number; y: number }[]; label: string }) {
  const box = useEChart((chart) => {
    const s = baseStyle();
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 56, right: 24, top: 16, bottom: 44 },
      tooltip: { ...s.tooltip, trigger: "item", formatter: (p: { data: { name: string; value: [number, number] } }) => `${p.data.name}: ${num(p.data.value[1])} USD/MWh, ${num(p.data.value[0])} kg CO2/MWh` },
      xAxis: { type: "value", name: "kg CO2 per MWh generated", nameLocation: "middle", nameGap: 26, scale: true, ...s.axis },
      yAxis: { type: "value", name: "USD/MWh", nameLocation: "middle", nameGap: 40, scale: true, ...s.axis },
      series: [{
        type: "scatter", symbolSize: 12, itemStyle: { color: token("accent") },
        label: { show: true, position: "right", color: token("ink"), fontSize: 11, formatter: (p: { data: { name: string } }) => p.data.name },
        data: points.map((p) => ({ name: p.name, value: [p.x, p.y] })),
      }],
    }, true);
  }, [points]);
  return <div ref={box} role="img" aria-label={label} style={{ height: 320 }} className="w-full" />;
}

type HubIn = { iso: string; flat: number | null; cells: Cell[]; months: string };
const usd = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 0 });

/** The reader's calculator: their inputs times the prices the server read. */
export function Calculator({ hubs }: { hubs: HubIn[] }) {
  const [mw, setMw] = useState(DEFAULTS.mw);
  const [lf, setLf] = useState(DEFAULTS.loadFactor);
  const [period, setPeriod] = useState<"month" | "year" | "run">("run");
  const [runDays, setRunDays] = useState(DEFAULTS.days);
  const days = period === "run" ? runDays : PERIODS[period];
  const rows = useMemo(() => hubs.map((h) => {
    const c80 = cheapPrice(h.cells);
    return { ...h, c80, eFlat: energy(mw, lf, days), e80: energy(mw, lf, days, DEFAULTS.share) };
  }).sort((a, b) => (a.flat ?? Infinity) - (b.flat ?? Infinity)), [hubs, mw, lf, days]);
  const input = "w-24 rounded border border-rule bg-panel px-2 py-1 text-sm";
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-end gap-4 text-sm">
        <label className="flex flex-col">Facility, MW <input type="number" min={1} step={1} value={mw} onChange={(e) => setMw(Math.max(0, Number(e.target.value)))} className={input} /></label>
        <label className="flex flex-col">Load factor <input type="number" min={0.05} max={1} step={0.05} value={lf} onChange={(e) => setLf(Math.min(1, Math.max(0, Number(e.target.value))))} className={input} /></label>
        <label className="flex flex-col">Period
          <select value={period} onChange={(e) => setPeriod(e.target.value as "month" | "year" | "run")} className={input + " w-40"}>
            <option value="month">a month (30 days)</option>
            <option value="year">a year (365 days)</option>
            <option value="run">a training run of N days</option>
          </select>
        </label>
        {period === "run" ? <label className="flex flex-col">N days <input type="number" min={1} step={1} value={runDays} onChange={(e) => setRunDays(Math.max(1, Math.round(Number(e.target.value))))} className={input} /></label> : null}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm">
          <thead className="text-left text-xs text-muted">
            <tr><th className="py-1">ISO</th><th>Flat load, USD</th><th>USD/MWh</th><th>Cheapest 80% of hours, USD</th><th>USD/MWh</th><th>Months</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.iso} className="border-t border-rule">
                <td className="py-1">{r.iso}</td>
                <td>{r.flat === null ? "not held" : usd(r.eFlat * r.flat)}</td>
                <td>{r.flat === null ? "" : num(Math.round(r.flat * 100) / 100)}</td>
                <td>{r.c80 === null ? "not held" : usd(r.e80 * r.c80)}</td>
                <td>{r.c80 === null ? "" : num(Math.round(r.c80 * 100) / 100)}</td>
                <td className="text-xs text-muted">{r.months}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-1 text-xs text-muted">
        Energy: {usd(energy(mw, lf, days))} MWh flat, {usd(energy(mw, lf, days, DEFAULTS.share))} MWh in the cheapest 80 percent of hours. Wholesale energy
        only, at the ISO&apos;s main hub.
      </p>
    </div>
  );
}
