"use client";
// Energy Research Warehouse (ERW) site, session 135: the charts of Thesis Builder (/thesis). Both answer the mouse
// with the series, the category and the value with its unit, and neither offers a download: a run is never exported.
//
//   TrendChart    a trend's own table as bars or a line (lib/thesis/view.ts, chartOf: a cell that is not a number is
//                 left out, never drawn as zero)
//   FunnelChart   the deal funnel's stages, one bar each, in the order the report gives them
// Session 318 (the owner's ruling of 13 October 2026): both drawn through the shared SVG set (components/svgchart.tsx)
// with the data they took on the canvas; the colors are the site's categorical tokens in their fixed order.
import { CategoryChart, HorizontalBars, num } from "@/components/svgchart";
import type { ChartData } from "@/lib/thesis/view";

// the site's categorical colors in their fixed order (app/tokens.css); a chart of one series is drawn in the accent
const ORDER = ["fuel-gas", "fuel-coal", "fuel-nuclear", "fuel-wind", "fuel-solar", "fuel-hydro", "fuel-storage", "fuel-other"];

export function TrendChart({ data, height = 280 }: { data: ChartData; height?: number }) {
  const many = data.series.length > 1;
  return (
    <div data-chart="trend">
      <CategoryChart id="thesis-trend" x={data.categories} unit={data.unit} label={`${data.title}${data.unit ? `, ${data.unit}` : ""}: ${data.series.map((s) => s.name).join(", ")} by ${data.categories.length} categories; the table below holds the same numbers`} height={height}
        series={data.series.map((s, i) => ({ name: s.name, color: many ? ORDER[i % ORDER.length] : "accent", values: s.data, kind: data.kind === "bar" ? "bar" : "line", width: 2 }))} zero={data.kind === "bar"} />
    </div>
  );
}

export function FunnelChart({ stages }: { stages: { id: string; label: string; n: number }[] }) {
  return (
    <div data-chart="funnel">
      <HorizontalBars id="thesis-funnel" rows={stages.map((s) => ({ name: s.label, value: s.n }))} unit="companies" label={`Deal funnel: ${stages.map((s) => `${s.label} ${s.n}`).join(", ")}`} fmt={(v) => num(v)} />
    </div>
  );
}
