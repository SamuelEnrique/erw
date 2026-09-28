"use client";
// Session 23: an Automated Analysis chart. The option is the ECharts spec warehouse/analysis/style.py wrote
// (the house palette, the site's tokens); this mounts it with the site's one chart library (components/echarts.ts).
import { useEChart } from "./echarts";

export function EChartOption({ option, height = 360, label }: { option: unknown; height?: number; label: string }) {
  const box = useEChart((chart) => chart.setOption(option, true), [option]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" />;
}
