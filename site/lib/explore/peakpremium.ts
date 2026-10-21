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

/** Quarter hours in a full ERCOT operating year (the method note's completeness rule). */
export function fullYear(y: number): number {
  return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? 35_136 : 35_040;
}

/** Whether a month's interval count is short of a full month. A full month holds its days times 96 quarter hours, four
 *  fewer in the month the clocks go forward and four more in the month they go back (America/Chicago), so a count
 *  below days times 96 less four is a month not over: the newest month of the table, which the header calls partial. */
export function partialMonth(y: number, m: number, n: number): boolean {
  const days = new Date(Date.UTC(y, m, 0)).getUTCDate();
  return n < days * 96 - 4;
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
