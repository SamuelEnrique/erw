"use client";
// Session 170: a finding card's chart. The spec comes from the card's JSON; the ECharts option (with its tooltip
// formatters, functions, so built here on the client) comes from lib/findingchart.ts. Hover shows every series.
// Session 182: a spec of kind "multiples" (every grid on one timeline, and a control that shows one grid large) is
// drawn by MultiChart; every other kind is drawn as before.
import { useEChart } from "@/components/echarts";
import { optionFor, type ChartSpec } from "@/lib/findingchart";
import { MultiChart, type MultiSpec } from "./MultiChart";

function OneChart({ spec, label, height = 340 }: { spec: ChartSpec; label: string; height?: number }) {
  const box = useEChart((chart) => chart.setOption(optionFor(spec), true), [spec]);
  return <div ref={box} role="img" aria-label={label} style={{ height }} className="w-full" data-finding-chart={spec.kind} />;
}

export function CardChart({ spec, label, height = 340 }: { spec: ChartSpec; label: string; height?: number }) {
  if ((spec as { kind: string }).kind === "multiples") return <MultiChart spec={spec as unknown as MultiSpec} label={label} />;
  return <OneChart spec={spec} label={label} height={height} />;
}
