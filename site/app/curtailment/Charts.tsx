"use client";
// Energy Research Warehouse (ERW) site, session 144: the charts of the one curtailment page (/curtailment). Two charts,
// each drawn from plain arrays the page computes on the server, and each answers the mouse:
//   XY    bars, lines and areas over a category axis (days, months, hours of the day, hours), stacked where asked, a
//         second axis for a share; the hover names the category, then each series with its value and unit, then the
//         page's own line for that category where it has one (the days held, the reason a share is missing)
//   Heat  a grid of cells, months by hours of the day; the hover is the page's own text for the cell, and a cell
//         with no hour held is hatched and says so
// A value that is not held is a gap, never a filled point.
// Session 317 (the owner's ruling of 13 October 2026): both are drawn through the shared SVG set (components/svgchart.tsx:
// CategoryChart, HeatChart) with the props they took on the canvas, so the page hands the same arrays and no number
// moved; the range slider (zoom) and the PNG download are gone, the table toggle stands in for them.
import { CategoryChart, HeatChart, type CatSeries } from "@/components/svgchart";

export type S = {
  name: string; color: string; values: (number | null)[]; kind?: "bar" | "line" | "area"; stack?: string; axis?: 0 | 1; unit?: string; dash?: boolean;
  /** decimals in the tooltip (default: none from 100 up, else two) */
  digits?: number;
};

export function XY({ id, x, series, unit, unit2, label, height = 280, notes, dim, every, zero = true }: {
  /** the chart's name in the page (data-chart) */
  id: string; x: string[]; series: S[]; unit: string; unit2?: string; label: string; height?: number;
  /** one more hover line per category */
  notes?: (string | null)[];
  /** categories drawn faint (the months outside the period chosen) */
  dim?: boolean[];
  /** a range slider under a long axis (session 317: the table stands in for it) */
  zoom?: boolean; every?: number; zero?: boolean;
}) {
  return <CategoryChart id={id} x={x} series={series as CatSeries[]} unit={unit} unit2={unit2} label={label} height={height} notes={notes} dim={dim} every={every} zero={zero} />;
}

export function Heat({ id, hours, months, values, tips, most, label }: {
  id: string; hours: string[]; months: string[];
  /** [month][hour]: the count, or null where no hour of the cell is held */
  values: (number | null)[][];
  /** [month][hour]: the cell's own text */
  tips: string[][]; most: number; label: string; height?: number;
}) {
  return <HeatChart id={id} rows={months} cols={hours} cells={values} tips={tips} unit="hours" label={label} lo={0} hi={Math.max(1, most)} legend={["0", `${Math.max(1, most)} hours`]} />;
}
