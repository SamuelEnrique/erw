// Energy Research Warehouse (ERW) site, session 148: ERCOT's reserve prices by day and by month, for Ask ERCOT.
//
// Pure functions, no imports (Node runs this file as it is, for site/scripts/test-ask-speed.mjs). Session 143's slow
// tail was data: one question read a year of hourly reserve prices (8,760 rows of ercot_as_prices, nine pages) and took
// 13.3 seconds. Two derived tables now hold those prices added up by ERCOT's local operating day and by month
// (warehouse/derived/ercot_as_prices_rollup.py, docs/methods/ercot_as_prices_rollup.md). This file is what the panel
// knows of them:
//
//   1. their names and what each holds, as the guide the model is given (rollupGuide), kept apart from
//      lib/chat/spec_ercot.json, which warehouse/chat/ercot.py exports and this file does not touch;
//   2. the rule the query tool enforces (hourlyRefusal): while the two tables are in the site's live set, a query of
//      the hourly table must give a start and may span at most MAX_HOURLY_DAYS days. A longer one is refused with a
//      message that names the two tables, so no question reads a year of hourly rows, whatever the model asks for;
//   3. the server switch: ASK_ROLLUP=off leaves the panel as session 143 left it (the two tables not offered, the
//      hourly table read as before). Unset, they are offered.
//
// The hourly table is unchanged and is still the one read for an hour, a day or a few weeks. The live battery page
// reads neither of the two new tables.

export const ROLLUP = { hourly: "ercot_as_prices", daily: "ercot_as_prices_daily", monthly: "ercot_as_prices_monthly" } as const;
export const ROLLUP_TABLES: string[] = [ROLLUP.daily, ROLLUP.monthly];
/** The longest span of hourly reserve prices one query may read while the two tables are held: the 35 days the site
 * keeps of every other interval table (warehouse/supabase/live_set.yaml, recent). */
export const MAX_HOURLY_DAYS = 35;
/** What each holds, for a refusal that names one as the nearest thing held. */
export const ROLLUP_HOLDS: Record<string, string> = {
  [ROLLUP.daily]: "Reserve (ancillary service) prices by day since 2018: each product's mean, lowest and highest hourly price of the day, and the hours held.",
  [ROLLUP.monthly]: "Reserve (ancillary service) prices by month since 2018: each product's mean, lowest and highest hourly price of the month, and the hours held.",
};
export const RESERVE_PRODUCTS = ["REGUP", "REGDN", "RRS", "NSPIN", "ECRS"] as const;

/** Whether the panel offers the two tables: always, unless the server says ASK_ROLLUP=off. */
export function rollupOffered(env: string | undefined = process.env.ASK_ROLLUP): boolean {
  return env !== "off";
}

/** The span of a query in whole or part days, from its start to its end (or to now when it gives no end); null when it
 * gives no start. `start` and `end` are ISO times. */
export function spanDays(start: string | null, end: string | null, nowMs: number): number | null {
  if (!start) return null;
  const a = Date.parse(start), b = end ? Date.parse(end) : nowMs;
  if (!Number.isFinite(a) || !Number.isFinite(b)) return null;
  return Math.max(0, (b - a) / 86_400_000);
}

/** Why a query of the hourly table is refused, or null when it may be read: it must give a start, and may span at most
 * MAX_HOURLY_DAYS days. The message is the model's to read: it names the tables to ask instead. */
export function hourlyRefusal(start: string | null, end: string | null, nowMs: number): string | null {
  const days = spanDays(start, end, nowMs);
  if (days !== null && days <= MAX_HOURLY_DAYS) return null;
  const what = days === null ? "this query gives no start, so it would read every hour held" : `this query spans ${Math.round(days)} days`;
  return `${ROLLUP.hourly} is read hour by hour for at most ${MAX_HOURLY_DAYS} days at a time, and ${what}. For a longer span read ${ROLLUP.monthly} (a row per product and month) or ${ROLLUP.daily} (a row per product and day): ` +
    "variable mcpc_dam_mean (the mean of the period's hourly prices), mcpc_dam_min, mcpc_dam_max or mcpc_dam_hours, the same entities, plain dates and no tz. " +
    `For single hours, give ${ROLLUP.hourly} a start and an end at most ${MAX_HOURLY_DAYS} days apart.`;
}

/** What the model is told of the two tables: appended to the profile's system prompt when they are offered. */
export function rollupGuide(): string {
  const n = MAX_HOURLY_DAYS;
  return `

RESERVE PRICES BY DAY AND BY MONTH (session 148). Two tables hold ${ROLLUP.hourly} added up by ERCOT's local operating day and by month (America/Chicago), derived by the ERW and held whole on the site. Read them, not the hourly table, for any reserve price over more than ${n} days. These lines govern where they differ from rule 12 and from the guide's entry for ${ROLLUP.hourly}.
- ${ROLLUP.daily} (public, tier derived): a row per product, day and variable. Entities as ${ROLLUP.hourly}: ercot:REGUP, ercot:REGDN, ercot:RRS and ercot:NSPIN since 2018-01-01, ercot:ECRS since 2023-06-10. Variables: mcpc_dam_mean (the mean of the day's hourly prices), mcpc_dam_min and mcpc_dam_max (the day's lowest and highest hourly price), USD per MW per hour; mcpc_dam_hours (the hours of the day that are held) and mcpc_dam_hours_in_day (the hours the day has), unit count.
- ${ROLLUP.monthly} (public, tier derived): the same by month, each row dated the month's first day. Variables: mcpc_dam_mean (the mean of the month's hourly prices), mcpc_dam_min, mcpc_dam_max, mcpc_dam_hours (the hours held) and mcpc_dam_hours_in_month (the hours the month has).
- How to ask them. Month by month, or one month's average: ${ROLLUP.monthly}, aggregation mean of mcpc_dam_mean, with group_by month for a series (each row is that month's own mean of its hours). Day by day, or a stretch of days: ${ROLLUP.daily}, aggregation mean of mcpc_dam_mean, with group_by day. A year's average, or year by year: ${ROLLUP.daily}, aggregation mean of mcpc_dam_mean, with group_by year for a series, and say it is the mean of the daily means. The highest price of a period: aggregation max of mcpc_dam_max (at is the day or month it fell in); the lowest: min of mcpc_dam_min. Both tables are dated by ERCOT's local day: give plain dates and no tz. Always give entity and variable.
- A short period. A day or a month whose mcpc_dam_hours is below its mcpc_dam_hours_in_day or mcpc_dam_hours_in_month is not whole (the month now running; a product's first month): its mean, lowest and highest are of the hours held only, and nothing is filled. When an answer rests on the newest month or on a product's first month, fetch its mcpc_dam_hours in the same turn and say that the month is partial. Never scale a short period.
- The hourly table. ${ROLLUP.hourly} is for single hours: one hour, the hours of a day or of a few weeks. A query of it must give a start and may span at most ${n} days: a longer one is refused by the tool. What the two tables cannot give over a longer span (a count of hours above a price, a median or a percentile of hourly prices) cannot be read here: give the nearest thing the two tables hold and say what they cannot give.
- When THE TABLES NOW lists either of the two as not in this site's live set, they are not loaded yet: read ${ROLLUP.hourly} as the guide says.`;
}
