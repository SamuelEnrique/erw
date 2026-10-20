"use client";
// A single stacked bar of shares (session 22): the day's generation mix on /grid and /mix. Hover gives each part in
// its unit and as a share. Negative parts (storage charging) are not drawn and are said so by the caller. Session 318
// (the owner's ruling of 13 October 2026): drawn through the shared SVG set (components/svgchart.tsx, ShareSegments),
// each part named on the bar with its share; the legend box and the PNG download are gone.
import { ShareSegments } from "./svgchart";

export type Part = { name: string; value: number; color: string };

export function ShareBar({ parts, unit, ariaLabel, file = "erw-mix" }: { parts: Part[]; unit: string; ariaLabel: string; file?: string }) {
  return <ShareSegments id={file} parts={parts} unit={unit} label={ariaLabel} />;
}
