// Session 78: California from the join (Samuel's ruling on session 73). From this hour California's generation and its
// carbon intensity of generation rest on CAISO's own supply by fuel; before it, on EIA-930. The date is one constant in
// the warehouse (JOIN in warehouse/derived/caiso_join.py); this is the site's copy of it, and tests/test_session78.py
// fails if the two differ. No other file of the site names the date.
export const CAISO_JOIN = "2025-12-16T08:00:00Z";

/** The join as a reader sees it: the Pacific day it starts, "16 December 2025". */
export function caisoJoinDay(): string {
  return new Date(CAISO_JOIN).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "America/Los_Angeles" });
}
