"use client";
// Five-number summaries as horizontal boxes on one scale (session 22): the ERCOT peak-premium explorer's time-of-day
// blocks. Hover gives the five numbers. Session 317 (the owner's ruling of 13 October 2026): drawn through the shared
// SVG set (components/svgchart.tsx, BoxPlot) with the rows it took on the canvas; the zoom and the PNG download are
// gone, the table toggle stands in for them.
import { BoxPlot } from "./svgchart";

export type BoxRow = { name: string; stats: [number, number, number, number, number] }; // min, q1, median, q3, max

export function BoxChart({ rows, unit, ariaLabel, file = "erw-boxes" }: { rows: BoxRow[]; unit: string; ariaLabel: string; file?: string }) {
  return <BoxPlot id={file} rows={rows} unit={unit} label={ariaLabel} />;
}
