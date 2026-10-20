"use client";
// Energy Research Warehouse (ERW) site, session 133: the charts of the one energy mix page (/mix).
//
// Four charts, each drawn from plain arrays the page computes on the server. Every one answers the mouse with the
// value, the hour or date, and the series. A value that is not held is a gap, never a filled point.
//   HourStack  generation by source as stacked areas over a category axis (the 24 local hours), with lines over it
//              (demand) and, when a factor is chosen, lines on a second axis (price, temperature, carbon, imports)
//   Lines      lines over a category axis: years, grids or fuels laid over each other, a second axis when asked
//   Bars       grouped bars over a category axis
//   Heat       a grid of cells (months by hours)
// Session 317 (the owner's ruling of 13 October 2026): the four are drawn through the shared SVG set
// (components/svgchart.tsx) with the props they took on the canvas; the page hands the same arrays, no number moved.
import { CategoryChart, HeatChart, type CatSeries } from "@/components/svgchart";

export type Series = { name: string; color: string; values: (number | null)[]; axis?: 0 | 1; dash?: "solid" | "dashed" | "dotted"; width?: number; unit?: string };

export function HourStack({ x, layers, lines, unit, unit2, label, height = 300, name }: { x: string[]; layers: Series[]; lines: Series[]; unit: string; unit2?: string; label: string; height?: number; name: string }) {
  const series: CatSeries[] = [
    ...layers.map((l) => ({ ...l, kind: "area" as const, stack: "mix" })),
    ...lines.map((l) => ({ ...l, kind: "line" as const })),
  ];
  return <div data-chart="stack"><CategoryChart id={name} x={x} series={series} unit={unit} unit2={unit2} label={label} height={height} /></div>;
}

export function Lines({ x, series, unit, unit2, label, height = 300, name, zero, every }: { x: string[]; series: Series[]; unit: string; unit2?: string; label: string; height?: number; name: string; zero?: boolean; every?: number }) {
  return <div data-chart="lines"><CategoryChart id={name} x={x} series={series.map((l) => ({ ...l, kind: "line" as const }))} unit={unit} unit2={unit2} label={label} height={height} zero={Boolean(zero)} every={every} /></div>;
}

export function Bars({ x, series, unit, label, height = 260, name }: { x: string[]; series: Series[]; unit: string; label: string; height?: number; name: string }) {
  return <div data-chart="bars"><CategoryChart id={name} x={x} series={series.map((l) => ({ ...l, kind: "bar" as const }))} unit={unit} label={label} height={height} /></div>;
}

/** rows by columns; cells[r][c] is the value or null. The mouse reads the row, the column and the value. */
export function Heat({ rows, cols, cells, unit, label, name, marks }: { rows: string[]; cols: string[]; cells: (number | null)[][]; unit: string; label: string; height?: number; name: string; marks?: [number, number][] }) {
  return <div data-chart="heat"><HeatChart id={name} rows={rows} cols={cols} cells={cells} unit={unit} label={label} marks={marks} /></div>;
}
