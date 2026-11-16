// Energy Research Warehouse (ERW) site, session 7400 (chain 303): the datacenter tracker's top block as one pure
// function, so the page (app/datacenters/Body.tsx), scripts/datacenter-tracker-figures.mjs and the replication
// (replication/datacenter_tracker/) read one computation. The arithmetic is session 166's and 240's, moved here from
// the component unchanged: the rows the sums count are in a named US state and not cancelled; a sum is of the MW a
// source states; "this week" is the seven UTC days that end on the day the page is drawn. Pure, no imports.
// Restated from lib/largeload.ts (US_STATES, countryOf, cancelled) so that Node runs this file alone, as lib/dcrollups.ts
// restates its own rule; tests/test_session7400_trackers.py holds the two files' lists and rules equal.
const US_STATES = new Set(["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
  "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "PR"]);
const countryOf = (country: string | undefined | null, state: string | undefined | null): string => (country ?? "") || (US_STATES.has(state ?? "") ? "US" : "");
const cancelled = (status: string | null | undefined): boolean => ["withdrawn", "cancelled"].includes((status ?? "").toLowerCase());

/** What the top block reads of a facility (app/datacenters/DatacentersTable.tsx's Facility holds each of these). */
export type TopRow = { country: string; status: string; mw: number | null; state: string; operator: string; site: string; firstStory: string };

/** A row of datacenter_facilities as the live set serves it, as far as the sums read it. */
export type LiveRow = { entity_id: string; name?: string | null; capacity_mw: number | string | null; status: string | null; operator: string | null;
  extra: Record<string, string> | null };
/** The seven fields of a facility the page's sums read, from a live row (app/datacenters/Body.tsx, toFacility, spreads
 * this): the country is "US" where a US state is stated, the MW is the stated capacity or null, never zero. */
export const topRowOf = (r: LiveRow): TopRow => {
  const x = r.extra ?? {};
  return {
    operator: r.operator ?? "", site: x.site_name ?? r.name ?? "", state: x.state ?? "", country: countryOf(x.country, x.state),
    mw: r.capacity_mw === null ? null : Number(r.capacity_mw), status: r.status ?? "", firstStory: x.first_story_at ?? "",
  };
};

const DAY = 86_400_000;

/** Session 166: the rows the totals and bars count: in a named US state, and not cancelled. */
export const counted = <T extends TopRow>(rows: T[]): T[] => rows.filter((f) => f.country === "US" && !cancelled(f.status));
/** Session 240: the first day of "this week": the seven UTC days that end on `today` (both included). */
export const weekStart = (today: string): string => new Date(Date.parse(`${today}T00:00:00Z`) - 6 * DAY).toISOString().slice(0, 10);
/** The facilities whose first story is dated in the week, newest first. The only date the table holds a facility by. */
export const firstReportedSince = <T extends TopRow>(rows: T[], start: string): T[] =>
  rows.filter((f) => f.firstStory && f.firstStory.slice(0, 10) >= start).sort((a, b) => b.firstStory.localeCompare(a.firstStory) || a.operator.localeCompare(b.operator) || a.site.localeCompare(b.site));

export type TopBlock<T extends TopRow> = {
  inTotals: T[]; noCountry: number; dropped: number; withMw: T[]; totalMw: number; noMw: number;
  byState: [string, number][]; byOperator: [string, number][]; byStatus: [string, number][];
  start: string; fresh: T[]; dated: number;
};

/** The top block's figures: the facilities held and counted, the megawatts stated with what the sum counts, by state,
 * by operator (the five largest) and by status, and the facilities first reported in the week to `today`. */
export function topBlock<T extends TopRow>(rows: T[], today: string): TopBlock<T> {
  const inTotals = counted(rows);
  const noCountry = rows.filter((f) => f.country !== "US").length;
  const dropped = rows.filter((f) => f.country === "US" && cancelled(f.status)).length;
  const withMw = inTotals.filter((f) => f.mw !== null);
  const totalMw = withMw.reduce((a, f) => a + (f.mw ?? 0), 0);
  const sumBy = (key: (f: T) => string, blank = false) => {
    const m = new Map<string, number>();
    for (const f of withMw) {
      const k = key(f);
      if (k || blank) m.set(k, (m.get(k) ?? 0) + (f.mw ?? 0));
    }
    return Array.from(m.entries()).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  };
  const start = weekStart(today);
  return {
    inTotals, noCountry, dropped, withMw, totalMw, noMw: inTotals.length - withMw.length,
    byState: sumBy((f) => f.state),
    byOperator: sumBy((f) => f.operator).slice(0, 5),
    byStatus: sumBy((f) => f.status, true),            // the megawatts by status, as the table has them (a blank status is "status not stated")
    start, fresh: firstReportedSince(rows, start), dated: rows.filter((f) => f.firstStory).length,
  };
}

export type OperatorGroupOf<T> = { operator: string; rows: T[]; mw: number; nMw: number };
/** Session 240, moved here by session 7400 (app/datacenters/DatacentersTable.tsx, byOperator): the rows by operator,
 *  the largest first: by the megawatts the page's sums count (a named US state, not cancelled, MW stated), then by the
 *  number of facilities, then by name; the rows with no operator stated are the last group. The rows keep their order. */
export function operatorGroups<T extends TopRow>(rows: T[]): OperatorGroupOf<T>[] {
  const m = new Map<string, OperatorGroupOf<T>>();
  for (const f of rows) {
    const g = m.get(f.operator) ?? { operator: f.operator, rows: [], mw: 0, nMw: 0 };
    g.rows.push(f);
    if (f.country === "US" && !cancelled(f.status) && f.mw !== null) { g.mw += f.mw; g.nMw += 1; }
    m.set(f.operator, g);
  }
  // the rows no source names an operator for are not an operator: their group comes last, whatever its megawatts
  return [...m.values()].sort((a, b) => Number(!a.operator) - Number(!b.operator) || b.mw - a.mw || b.rows.length - a.rows.length || a.operator.localeCompare(b.operator));
}

/** The top block's figures by their check keys (datacenters|...), as the page draws them. */
export function topFigures<T extends TopRow>(rows: T[], today: string): Record<string, number> {
  const t = topBlock(rows, today);
  const out: Record<string, number> = {
    "datacenters|count": rows.length, "datacenters|counted": t.inTotals.length, "datacenters|no_us_state": t.noCountry,
    "datacenters|cancelled": t.dropped, "datacenters|mw_total": t.totalMw, "datacenters|n_with_mw": t.withMw.length,
    [`datacenters|first_week|${t.start}`]: t.fresh.length, "datacenters|n_first_story": t.dated,
  };
  for (const [k, v] of t.byStatus) out[`datacenters|status_mw|${k}`] = v;
  for (const [k, v] of t.byState) out[`datacenters|state_mw|${k}`] = v;
  for (const [k, v] of t.byOperator) out[`datacenters|operator_mw|${k}`] = v;
  // the list's group lines, unfiltered: each operator's facilities and, where one states MW, the MW the sums count
  for (const g of operatorGroups(rows)) {
    out[`datacenters|operator_count|${g.operator}`] = g.rows.length;
    if (g.nMw) out[`datacenters|operator_mw|${g.operator}`] = g.mw;
  }
  return out;
}
