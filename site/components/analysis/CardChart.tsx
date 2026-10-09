"use client";
// Session 170: a finding card's chart. The spec comes from the card's JSON; the ECharts option (with its tooltip
// formatters, functions, so built here on the client) comes from lib/findingchart.ts. Hover shows every series.
import { useEChart } from "@/components/echarts";
import { optionFor, type ChartSpec } from "@/lib/findingchart";

export function CardChart({ spec, label, height = 340 }: { spec: ChartSpec; label: string; height?: number }) {
  const box = useEChart((chart) => chart.setOption(optionFor(spec), true), [spec]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" data-finding-chart={spec.kind} />;
}
