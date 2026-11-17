// Energy Research Warehouse (ERW) site, session 7565 (docs/reviews/grid-read-2026-11-16.md, rows 1 and 2): two lines of
// the Grid tool's words, kept here so the components that draw them export nothing new (scripts/page_tables.py reads a
// component's export blocks). They name no table: the components name their own.

/** The Mix tab's lead and the demand block: the hour shown is the daily table's newest, not EIA's. */
export const DAILY_TABLE_TIP = "EIA publishes a grid's hourly demand an hour or so after the hour; the warehouse's demand table loads it once a day, after the UTC day ends, so this hour can be a day or more behind EIA. The Network tab's hourly snapshot holds newer hours.";

/** The carbon block when its four-day window is empty: the table holds the grid's intensity, in older hours. */
export const CARBON_WINDOW_WORDS = (iso: string): string =>
  `the warehouse holds ${iso}'s carbon intensity, but its newest hour is more than four days old, older than this block reads.`;
