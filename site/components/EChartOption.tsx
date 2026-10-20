"use client";
// Session 23: an Automated Analysis chart. The option is the ECharts spec warehouse/analysis/style.py wrote (the house
// palette, the site's tokens); session 318 (the owner's ruling of 13 October 2026) reads it into the shared SVG set
// (lib/svgoption.ts, components/SvgOption.tsx) instead of mounting it on the canvas.
import { SvgOption } from "./SvgOption";

export function EChartOption({ option, height = 360, label }: { option: unknown; height?: number; label: string }) {
  return <SvgOption option={option} height={height} label={label} id="week" data-week-chart-svg="1" />;
}
