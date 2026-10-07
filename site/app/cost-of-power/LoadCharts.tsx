"use client";
// Session 138: the chart of "What a datacenter pays" (/cost-of-power). Every value drawn arrives from the server
// (page.tsx, lib/datacenter.ts); the chart answers the mouse: each bar shows its year, its figures and the months held.
import { baseStyle, token, useEChart } from "@/components/echarts";

export type YearBar = { y: string; flat: number | null; per: number | null; complete: boolean; months: number; down: number; foreseen?: number | null };
const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function YearCost({ rows, flex, off, label }: { rows: YearBar[]; flex: boolean; off: boolean; label: string }) {
  const box = useEChart((chart) => {
    const s = baseStyle();
    const bar = (key: "flat" | "per", color: string) => rows.map((r) => ({ value: r[key] === null ? null : Math.round((r[key] as number) * 100) / 100,
      itemStyle: { color, opacity: r.complete ? 1 : 0.4 } }));
    chart.setOption({
      textStyle: s.textStyle,
      grid: { left: 56, right: 16, top: 16, bottom: 30 },
      tooltip: { ...s.tooltip, trigger: "axis", axisPointer: { type: "shadow" },
        formatter: (ps: { dataIndex: number }[]) => {
          const r = rows[ps[0].dataIndex];
          const lines = [`<strong>${r.y}</strong>${r.complete ? "" : ` (${r.months} of 12 months held)`}`];
          if (r.flat !== null) lines.push(`Flat load: ${two(r.flat)} USD/MWh`);
          if (flex && r.per !== null) lines.push(`This load: ${two(r.per)} USD/MWh`);
          if (flex && r.per !== null && r.flat !== null) lines.push(`Saved: ${two(r.flat - r.per)} USD/MWh${off && r.down ? `, off in ${r.down.toLocaleString("en-US")} hours` : ""}`);
          if (flex && r.foreseen != null) lines.push(`If perfectly foreseen: ${two(r.foreseen)} USD/MWh${r.flat !== null ? ` (saved ${two(r.flat - r.foreseen)})` : ""}`);
          return lines.join("<br/>");
        } },
      xAxis: { type: "category", data: rows.map((r) => r.y), ...s.axis },
      yAxis: { type: "value", name: "USD/MWh", nameLocation: "middle", nameGap: 40, ...s.axis },
      series: [
        { name: "Flat load", type: "bar", data: bar("flat", flex ? token("muted") : token("accent")), barMaxWidth: 34 },
        ...(flex ? [{ name: "This load", type: "bar", data: bar("per", token("accent")), barMaxWidth: 34 },
          // session 140: the same load with its hours chosen knowing the year's prices, a mark beside the bars
          { name: "If perfectly foreseen", type: "scatter", symbol: "diamond", symbolSize: 9, itemStyle: { color: token("ink") },
            data: rows.map((r) => (r.foreseen == null ? null : Math.round(r.foreseen * 100) / 100)) }] : []),
      ],
    }, true);
  }, [rows, flex, off]);
  return <div ref={box} role="img" aria-label={label} data-year-cost="1" style={{ height: 300 }} className="w-full" />;
}
