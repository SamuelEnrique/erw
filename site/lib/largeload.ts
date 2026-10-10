// Energy Research Warehouse (ERW) site, session 106: the datacenter tracker, version 2 (/datacenters/v2, in review).
//
// ERCOT's Large Load Interconnection Status Update, as far as it states figures in words: the MW that have received
// Approval to Energize, and the peak ERCOT has observed from those loads (the sum of each load's own highest hour of
// the month, and the highest hour of the loads together). The site's copy of the table ercot_large_load_status
// (data/large_load_status.json, warehouse/derived/large_load_snapshot.py). Pure functions over that file.

export type Report = {
  day: string; document: string; url: string; month_as_written: string;
  approved?: number; nonsimultaneous?: number; simultaneous?: number; new_count?: number; new_mw?: number;
};
export type LoadFile = { table: string; built: string; retrieved: string; rows: number; source: string; reports: Report[] };

export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const dayWords = (d: string) => `${Number(d.slice(8, 10))} ${MONTHS[Number(d.slice(5, 7)) - 1]} ${d.slice(0, 4)}`;

/** The newest report that states each of the three figures, and the first one, for the change between them. */
export function span(f: LoadFile): { first: Report; last: Report } | null {
  const whole3 = f.reports.filter((r) => r.approved !== undefined && r.nonsimultaneous !== undefined && r.simultaneous !== undefined);
  return whole3.length ? { first: whole3[0], last: whole3[whole3.length - 1] } : null;
}

/** The reports whose own two peaks cannot both be right: the peak of the loads together above the sum of their own peaks. */
export const impossible = (f: LoadFile): Report[] => f.reports.filter((r) => r.simultaneous !== undefined && r.nonsimultaneous !== undefined && r.simultaneous > r.nonsimultaneous);

/** A report's month as ERCOT wrote it, when it is not the report's own month and year (the reports of early 2026 say 2025). */
export function monthMismatch(r: Report): boolean {
  if (!r.month_as_written) return false;
  const [m, y] = r.month_as_written.split(" ");
  const mi = MONTHS.indexOf(m);
  if (mi < 0) return false;
  return !(Number(y) === Number(r.day.slice(0, 4)) && mi === Number(r.day.slice(5, 7)) - 1);
}

/** The summary sentence. Null when no report states the three figures. */
export function summary(f: LoadFile): string | null {
  const s = span(f);
  if (!s) return null;
  const { first, last } = s;
  const share = (100 * last.nonsimultaneous!) / last.approved!;
  return `By ERCOT's report of ${dayWords(last.day)}, ${whole(last.approved!)} MW of large load had its approval to energize, and ERCOT had observed ${whole(last.nonsimultaneous!)} MW of it running`
    + ` (${share.toFixed(0)} percent). On ${dayWords(first.day)} the two figures were ${whole(first.approved!)} and ${whole(first.nonsimultaneous!)} MW.`;
}

/** The 50 states, the District of Columbia and Puerto Rico, as postal codes (session 166; the builder's own list,
 * energy_projects.STATES): a row with one of these is in the US. */
export const US_STATES = new Set(["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
  "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "PR"]);
/** Session 166: a row's country. The table's own country column where it has one ("US" when a US state is stated, else
 * empty: no source records a country); before the table is reloaded, the state code says it. "" means no source states it. */
export const countryOf = (country: string | undefined | null, state: string | undefined | null): string => (country ?? "") || (US_STATES.has(state ?? "") ? "US" : "");
/** Session 166: cancelled, in the entities vocabulary (the extractor's "cancelled" is written "withdrawn"). */
export const cancelled = (status: string | null | undefined): boolean => ["withdrawn", "cancelled"].includes((status ?? "").toLowerCase());

/** Facilities held, as the page counts them: the ERW's own table of datacenters (news, operators' lists, queues). */
export type Facility = { name: string | null; operator: string | null; status: string | null; capacity_mw: number | null; state: string; kind: string; country: string };
export function facilityCounts(rows: Facility[]): { all: number; us: number; noCountry: number; texas: number; withMw: number; mw: number; texasWithMw: number; texasMw: number; byKind: Record<string, number> } {
  const tx = rows.filter((r) => r.state === "TX");
  const mwOf = (x: Facility[]) => x.filter((r) => typeof r.capacity_mw === "number" && Number.isFinite(r.capacity_mw));
  const byKind: Record<string, number> = {};
  for (const r of rows) byKind[r.kind || "not stated"] = (byKind[r.kind || "not stated"] ?? 0) + 1;
  const us = rows.filter((r) => r.country === "US").length;
  return { all: rows.length, us, noCountry: rows.length - us, texas: tx.length, withMw: mwOf(rows).length, mw: mwOf(rows).reduce((a, r) => a + (r.capacity_mw as number), 0),
    texasWithMw: mwOf(tx).length, texasMw: mwOf(tx).reduce((a, r) => a + (r.capacity_mw as number), 0), byKind };
}
