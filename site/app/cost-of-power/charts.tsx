"use client";
// Session 37: the cost-of-power page's charts and calculator. Every value drawn here arrives from the server
// (page.tsx), read from the cost_of_power_* tables; the calculator multiplies the reader's inputs by those prices.
// Session 317 (the owner's ruling of 13 October 2026): the three charts are drawn through the shared SVG set
// (components/svgchart.tsx) with the props they took on the canvas: the rank as bars (a partial month hatched), the
// heat grid as a HeatChart, the cost against carbon as a ScatterChart with each grid named beside its point.
import { useMemo, useState } from "react";
import { CategoryChart, HeatChart, ScatterChart, num } from "@/components/svgchart";
import { cheapPrice, energy, type Cell, PERIODS, DEFAULTS } from "@/lib/cost";

export function RankBars({ bars, label }: { bars: { name: string; value: number; partial: boolean }[]; label: string }) {
  const sorted = [...bars].sort((a, b) => a.value - b.value);
  return <CategoryChart id="rank" x={sorted.map((b) => b.name)} unit="USD/MWh" label={label} height={Math.max(200, 60 + sorted.length * 26)}
    series={[{ name: "Load-weighted price", color: "accent", values: sorted.map((b) => b.value), kind: "bar", faint: sorted.map((b) => b.partial), digits: 2 }]}
    notes={sorted.map((b) => (b.partial ? "a partial month" : null))} />;
}

export function HeatGrid({ cells, label }: { cells: Cell[]; label: string }) {
  const months = useMemo(() => [...new Set(cells.map((c) => c.month))].sort(), [cells]);
  const grid = useMemo(() => months.map((m) => Array.from({ length: 24 }, (_, h) => cells.find((c) => c.month === m && c.hour === h)?.price ?? null)), [cells, months]);
  return <HeatChart id="heat" rows={months} cols={Array.from({ length: 24 }, (_, h) => String(h))} cells={grid} unit="USD/MWh" label={label} legend={["cheap", "dear"]}
    tips={months.map((m, i) => Array.from({ length: 24 }, (_, h) => (grid[i][h] === null ? `${m}, ${String(h).padStart(2, "0")}:00 local: not held` : `${m}, ${String(h).padStart(2, "0")}:00 local: ${num(grid[i][h] as number)} USD/MWh`)))} />;
}

export function CostCarbon({ points, label }: { points: { name: string; x: number; y: number }[]; label: string }) {
  return <ScatterChart id="cost-carbon" points={points} xUnit="kg CO2 per MWh generated" yUnit="USD/MWh" xName="" yName="" label={label} />;
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
  const input = "w-24 border border-rule bg-panel px-2 py-1 text-sm";
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-end gap-4 text-sm">
        <label className="flex flex-col">Facility, MW <input type="number" autoComplete="off" min={1} step={1} value={mw} onChange={(e) => setMw(Math.max(0, Number(e.target.value)))} className={input} /></label>
        <label className="flex flex-col">Load factor <input type="number" autoComplete="off" min={0.05} max={1} step={0.05} value={lf} onChange={(e) => setLf(Math.min(1, Math.max(0, Number(e.target.value))))} className={input} /></label>
        <label className="flex flex-col">Period
          <select value={period} onChange={(e) => setPeriod(e.target.value as "month" | "year" | "run")} className={input + " w-40"}>
            <option value="month">a month (30 days)</option>
            <option value="year">a year (365 days)</option>
            <option value="run">a training run of N days</option>
          </select>
        </label>
        {period === "run" ? <label className="flex flex-col">N days <input type="number" autoComplete="off" min={1} step={1} value={runDays} onChange={(e) => setRunDays(Math.max(1, Math.round(Number(e.target.value))))} className={input} /></label> : null}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm">
          <thead className="text-left text-xs text-muted">
            <tr><th scope="col" className="py-1">ISO</th><th scope="col">Flat load, USD</th><th scope="col">USD/MWh</th><th scope="col">Cheapest 80% of hours, USD</th><th scope="col">USD/MWh</th><th scope="col">Months</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.iso} className="border-t border-rule">
                <th scope="row" className="py-1 text-left font-normal">{r.iso}</th>
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
