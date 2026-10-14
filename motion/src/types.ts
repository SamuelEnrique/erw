// Energy Research Warehouse (ERW), session 274: what a motion video is drawn from. specs.mjs writes one of these from
// the rows that draw a chart (the chart of the week's file, or a finding's), and nothing else: no number is typed here.

export type Base = {
  id: string;            // the file's name: <source>_<width>x<height>.mp4
  kicker: string;        // "ERW, chart of the week, 2026-W41" or "ERW Research"
  title: string;
  subtitle: string;
  source: string;        // the chart's own source line
  width: number;
  height: number;
  frames: number;        // at 30 frames a second
};

export type Series = { name: string; values: (number | null)[]; axis: "left" | "other"; unit: string; bar: boolean };

export type DrawOn = Base & {
  type: "draw-on";
  x: string[];
  xLabel: string;
  yLabel: string;
  yRightLabel: string;   // the scale of the first series not on the left axis, drawn on the right
  series: Series[];
  leftOut: string[];     // series of the chart not drawn (a bar series on a third scale)
  band: { from: number; to: number; label: string } | null; // indices into x
  decimals: number;
};

export type CountUp = Base & {
  type: "count-up";
  value: number;
  decimals: number;
  unit: string;
  sentence: string;
};

export type RollCall = Base & {
  type: "roll-call";
  measure: string;
  rows: { label: string; value: number }[];
  unit: string;
  decimals: number;
  max: number;
};

export type Reorder = Base & {
  type: "reorder";
  labels: string[];
  before: { name: string; values: number[] };
  after: { name: string; values: number[] };
  unit: string;
  decimals: number;
};

export type Spec = DrawOn | CountUp | RollCall | Reorder;
