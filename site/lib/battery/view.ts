// Session 296 (the owner's rulings of 15 October 2026): what the reader chooses to see on /cost-of-power/battery, as
// the address carries it: the units (per kW, or the battery of the reader's size), which headline figures (up to six
// of eight), which charts (up to three of four) and at what scale, the income table's window (its first and last
// year and the stress events left out of it) and whether it is drawn as a chart, and the sensitivity's mode, percent
// and measure. Pure: no React, no imports, so the page reads it on the server and the box rewrites it in the browser.
// A parameter is written only where the choice differs from the default, so no parameter means the page as it was.

export type Units = "kw" | "battery";
export type HeadKey = "l12" | "bad" | "cover" | "npv" | "irr" | "toll" | "payback" | "npveq";
export type ChartKey = "revenue" | "after_costs" | "after_debt" | "debt";
export type Scale = "linear" | "log" | "adjusted";
export type Mode = "range" | "pct";
export type Measure = "npv" | "irr";
export type View = {
  units: Units; heads: HeadKey[]; charts: ChartKey[]; scale: Scale;
  /** the income table's window: its first and last calendar year (null: every year held) and the events left out */
  from: string | null; to: string | null; out: string[]; income: "table" | "chart";
  mode: Mode; pct: number; measure: Measure;
};
export const HEADS: { key: HeadKey; label: string; words: string }[] = [
  { key: "l12", label: "Last twelve months, all streams", words: "the last twelve months' revenue, USD per kW" },
  { key: "bad", label: "A bad month: the 10th percentile, last 36 months", words: "one month in ten of the last 36 earned this or less" },
  { key: "cover", label: "Debt coverage, last twelve months", words: "revenue less fixed O&M over the debt payments, scenario A" },
  { key: "npv", label: "NPV at the hurdle rate", words: "to equity, scenario A" },
  { key: "irr", label: "IRR", words: "to equity, scenario A" },
  { key: "toll", label: "Breakeven toll", words: "the price of a toll on the whole battery at which coverage is 1.25, scenario A" },
  { key: "payback", label: "Payback year", words: "the first year the cash flows to equity, added up without discounting, are no longer negative" },
  { key: "npveq", label: "NPV per dollar of equity", words: "scenario A's NPV over the equity paid in" },
];
export const CHARTS: { key: ChartKey; label: string; words: string }[] = [
  { key: "revenue", label: "Revenue by stream", words: "by calendar year, energy and ancillary services, USD per kW, from the table" },
  { key: "after_costs", label: "Cash after costs", words: "each year of scenario A's life: income less fixed O&M, USD per kW" },
  { key: "after_debt", label: "Cash after debt", words: "each year of scenario A's life: income less fixed O&M less the debt payment, USD per kW" },
  { key: "debt", label: "Debt", words: "each year of scenario A's life: the debt payment and the debt still owed, USD per kW" },
];
export const HEADS_MAX = 6, CHARTS_MAX = 3;
export const DEFAULT_VIEW: View = { units: "battery", heads: ["l12", "bad", "cover"], charts: ["revenue"], scale: "adjusted", from: null, to: null, out: [], income: "table", mode: "range", pct: 10, measure: "npv" };
const PARAMS = ["u", "hf", "ch", "sc", "wf", "wt", "lo", "it", "sm", "sp", "sx"];
export const isViewParam = (name: string) => PARAMS.includes(name);
const list = <T extends string>(raw: string | undefined, all: readonly T[], max: number): T[] | null => {
  if (raw === undefined || raw === "") return null;
  const out = raw.split("+").filter((k): k is T => (all as readonly string[]).includes(k));
  return [...new Set(out)].slice(0, max);
};
/** The view from the address, each choice defaulted and bounded. */
export function parseView(q: Record<string, string | undefined>): View {
  const v: View = { ...DEFAULT_VIEW, heads: [...DEFAULT_VIEW.heads], charts: [...DEFAULT_VIEW.charts], out: [] };
  if (q.u === "kw") v.units = "kw";
  const hf = list(q.hf, HEADS.map((h) => h.key), HEADS_MAX);
  if (hf && hf.length) v.heads = hf;
  const ch = list(q.ch, CHARTS.map((c) => c.key), CHARTS_MAX);
  if (ch) v.charts = ch;
  if (q.sc === "linear" || q.sc === "log") v.scale = q.sc;
  if (q.wf && /^\d{4}$/.test(q.wf)) v.from = q.wf;
  if (q.wt && /^\d{4}$/.test(q.wt)) v.to = q.wt;
  if (q.lo) v.out = [...new Set(q.lo.split("+").filter((s) => /^[a-z0-9_]+$/.test(s)))].sort();
  if (q.it === "chart") v.income = "chart";
  if (q.sm === "pct") v.mode = "pct";
  const p = Number(q.sp);
  if (q.sp !== undefined && Number.isFinite(p)) v.pct = Math.min(100, Math.max(1, Math.round(p)));
  if (q.sx === "irr") v.measure = "irr";
  return v;
}
/** The address parameters of a view: only what differs from the default. */
export function viewQuery(v: View): [string, string][] {
  const out: [string, string][] = [];
  const same = (a: string[], b: string[]) => a.length === b.length && a.every((x, i) => x === b[i]);
  if (v.units !== DEFAULT_VIEW.units) out.push(["u", v.units]);
  if (!same(v.heads, DEFAULT_VIEW.heads)) out.push(["hf", v.heads.join("+")]);
  if (!same(v.charts, DEFAULT_VIEW.charts)) out.push(["ch", v.charts.join("+")]);
  if (v.scale !== DEFAULT_VIEW.scale) out.push(["sc", v.scale]);
  if (v.from) out.push(["wf", v.from]);
  if (v.to) out.push(["wt", v.to]);
  if (v.out.length) out.push(["lo", [...v.out].sort().join("+")]);
  if (v.income !== DEFAULT_VIEW.income) out.push(["it", v.income]);
  if (v.mode !== DEFAULT_VIEW.mode) out.push(["sm", v.mode]);
  if (v.pct !== DEFAULT_VIEW.pct) out.push(["sp", String(v.pct)]);
  if (v.measure !== DEFAULT_VIEW.measure) out.push(["sx", v.measure]);
  return out;
}
/** The window's first and last year as the table uses them: the reader's, else the years held. */
export function windowOf(v: View, held: string[]): { from: string; to: string } | null {
  if (!held.length) return null;
  const from = v.from && held.includes(v.from) ? v.from : held[0];
  const to = v.to && held.includes(v.to) ? v.to : held[held.length - 1];
  return from <= to ? { from, to } : { from: to, to: from };
}
