"use client";
// Session 170: a finding card's chart. The spec comes from the card's JSON; the option (lib/findingchart.ts) is what the
// canvas drew until session 318 (the owner's ruling of 13 October 2026): it is now read into the shared SVG set
// (lib/svgoption.ts, components/SvgOption.tsx), so every card's numbers are the same and the chart carries direct
// labels, a Chart | Table toggle and a hover card. Session 182: a spec of kind "multiples" (every grid on one timeline,
// and a control that shows one grid large) is drawn by MultiChart; every other kind is drawn as before.
import { SvgOption } from "@/components/SvgOption";
import { optionFor, type ChartSpec } from "@/lib/findingchart";
import { MultiChart, type MultiSpec } from "./MultiChart";

function OneChart({ spec, label, height = 340 }: { spec: ChartSpec; label: string; height?: number }) {
  return <SvgOption option={optionFor(spec)} label={label} height={height} id={`card-${spec.kind}`} data-finding-chart={spec.kind} />;
}

export function CardChart({ spec, label, height = 340 }: { spec: ChartSpec; label: string; height?: number }) {
  if ((spec as { kind: string }).kind === "multiples") return <MultiChart spec={spec as unknown as MultiSpec} label={label} />;
  return <OneChart spec={spec} label={label} height={height} />;
}
