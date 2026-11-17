// Energy Research Warehouse (ERW) site, session 403: the ERCOT peak premium explorer's own parts
// (/explore/ercot-peak-premium; the frame is components/explore/Explore.tsx). It reads the two derived tables
// ercot_peak_premium_annual and ercot_peak_premium_monthly (docs/methods/ercot_peak_premium.md) as they stand, and
// computes nothing: every figure it shows is a row of one of them, with that row's check key.

export const ANNUAL = "ercot_peak_premium_annual";
export const MONTHLY = "ercot_peak_premium_monthly";
export const THESIS_HUB = "ercot:HB_HUBAVG";   // the hub of the thesis (the method note)

export type Row = { entity: string; variable: string; ts_utc: string; value: number };

/** The four time-of-day blocks, by the local (America/Chicago) hour an interval starts (the method note's table). */
export const BLOCKS = [
  { key: "overnight", label: "Overnight", hours: "21:00 to 12:00" },
  { key: "midday", label: "Midday", hours: "12:00 to 16:00" },
  { key: "peak", label: "Peak", hours: "16:00 to 21:00" },
  { key: "all", label: "All intervals", hours: "24 hours" },
] as const;
export const STATS = ["min", "q1", "median", "q3", "max"] as const;

/** The thesis's figures (the method note's "Thesis reproduction" table and the metrics it defines), in the order shown. */
export const FIGURES = [
  { v: "all_median", label: "Median, all intervals", unit: "USD/MWh" },
  { v: "all_p999", label: "99.9th percentile, all intervals", unit: "USD/MWh" },
  { v: "worst_interval_multiple", label: "Worst-interval multiple (99.9th percentile over the median)", unit: "ratio" },
  { v: "peak_iqr", label: "Peak-block IQR (Q3 minus Q1, 16:00 to 21:00)", unit: "USD/MWh" },
  { v: "peak_minus_midday_median", label: "Peak median minus midday median", unit: "USD/MWh" },
  { v: "midday_min", label: "Midday minimum", unit: "USD/MWh" },
  { v: "n_scarcity", label: "Intervals at or above 1,000 USD/MWh", unit: "count" },
  { v: "n_negative", label: "Intervals at or below 0 USD/MWh", unit: "count" },
  { v: "n_intervals", label: "15-minute intervals in the period", unit: "count" },
] as const;

/** Ruling alternative 1 (session 7708, branch wip/alt-ercot-peak-premium-1; not a default on main): the means and the
 *  traded block beside the medians, the figures a published source can be held to. Each is a row of the table, written
 *  by the branch's builder (warehouse/derived/ercot_peak_premium.py); a table built before it holds none of them. */
export const MEANS = [
  { v: "peak_median", label: "Peak median (16:00 to 21:00), as on the page", unit: "USD/MWh" },
  { v: "peak_mean", label: "Peak mean (16:00 to 21:00)", unit: "USD/MWh" },
  { v: "all_median", label: "Median, all intervals", unit: "USD/MWh" },
  { v: "all_mean", label: "Mean, all intervals", unit: "USD/MWh" },
  { v: "all_mean_load_weighted", label: "Mean weighted by ERCOT's system load, all intervals", unit: "USD/MWh" },
  { v: "traded_median", label: "Median, 06:00 to 22:00 on weekdays (the traded block)", unit: "USD/MWh" },
  { v: "traded_mean", label: "Mean, 06:00 to 22:00 on weekdays (the traded block)", unit: "USD/MWh" },
] as const;

/** Session 7516 (chain 304, part B): the figures drawn for two hubs side by side (the address's `vs`), in the order
 *  shown: the peak block first, then the blocks it is read against, then the thesis's tail figures. Each is a row of the
 *  table for its own hub; the page takes no difference between the two. */
export const SIDE = [
  { v: "peak_median", label: "Peak median (16:00 to 21:00)", unit: "USD/MWh" },
  { v: "peak_q1", label: "Peak Q1", unit: "USD/MWh" },
  { v: "peak_q3", label: "Peak Q3", unit: "USD/MWh" },
  { v: "peak_iqr", label: "Peak-block IQR (Q3 minus Q1)", unit: "USD/MWh" },
  { v: "midday_median", label: "Midday median (12:00 to 16:00)", unit: "USD/MWh" },
  { v: "peak_minus_midday_median", label: "Peak median minus midday median", unit: "USD/MWh" },
  { v: "overnight_median", label: "Overnight median (21:00 to 12:00)", unit: "USD/MWh" },
  { v: "all_median", label: "Median, all intervals", unit: "USD/MWh" },
  { v: "all_p999", label: "99.9th percentile, all intervals", unit: "USD/MWh" },
  { v: "all_max", label: "Maximum, all intervals", unit: "USD/MWh" },
  { v: "n_scarcity", label: "Intervals at or above 1,000 USD/MWh", unit: "count" },
  { v: "n_negative", label: "Intervals at or below 0 USD/MWh", unit: "count" },
  { v: "n_intervals", label: "15-minute intervals in the period", unit: "count" },
] as const;

/** Quarter hours in a full ERCOT operating year (the method note's completeness rule). */
export function fullYear(y: number): number {
  return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? 35_136 : 35_040;
}

/** Quarter hours in a full calendar month of America/Chicago: its days times 96, four fewer in the month the clocks go
 *  forward (March) and four more in the month they go back (November), as the United States has set them since 2007
 *  (the tables start in 2015). */
export function fullMonth(y: number, m: number): number {
  const days = new Date(Date.UTC(y, m, 0)).getUTCDate();
  return days * 96 + (m === 3 ? -4 : m === 11 ? 4 : 0);
}

/** Whether a month's interval count is short of a full month: the newest month of the table, which the header calls
 *  partial. Session 7507 (chain 304): held to the month's exact count. Until then the rule was "below days times 96
 *  less four" for every month, so a month up to an hour short (two hours in November) was drawn as complete and could
 *  become a view's default second year. */
export function partialMonth(y: number, m: number, n: number): boolean {
  return n < fullMonth(y, m);
}

/** The label timestamp of a period, as the tables write it: a year's first day, or a month's. */
export function periodTs(year: number, month: number | null): string {
  return `${year}-${String(month ?? 1).padStart(2, "0")}-01T00:00:00Z`;
}

/** One row's value, by variable and label timestamp, among the rows of one hub. */
export function valueOf(rows: Row[], variable: string, ts: string): number | undefined {
  const t = new Date(ts).getTime();
  return rows.find((r) => r.variable === variable && new Date(r.ts_utc).getTime() === t)?.value;
}

/** The "Last input interval" of a table's header (the newest interval the tables were computed from), or null. */
export function lastInput(header: string[]): string | null {
  const l = header.find((x) => x.startsWith("Last input interval:"));
  const m = l?.match(/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)/);
  return m ? m[1] : null;
}
