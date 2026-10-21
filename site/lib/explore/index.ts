// Energy Research Warehouse (ERW) site, session 403: the shared parts of the signature explorers (platform tool 5,
// /explore/<name>). The first is /explore/ercot-peak-premium; sessions 404 and 405 build /explore/demand-growth and
// /explore/interconnection on the same pattern. What is the same on every explorer lives here and in
// components/explore/Explore.tsx: the filters read from the address (so every figure is drawn on the server and
// carries a check key), and the freshness line, read from the catalogue (never written by hand).
//
// This file holds no read, so a client component may import it; the catalogue read is in ./fresh.ts.
// No number is computed here: these helpers parse the address, name periods and dates, and say how old a table is.

export type Params = Record<string, string | string[] | undefined>;
export type Option = { value: string; label: string };

/** One value of the address: the first, when a name is given twice. */
export function param(sp: Params, name: string): string | undefined {
  const v = sp[name];
  return typeof v === "string" ? v : Array.isArray(v) ? v[0] : undefined;
}

/** A value of the address that must be one of `allowed`; anything else (or nothing) is the fallback. The second item
 *  says whether the address asked for something the page does not hold, so the page can say so in one line. */
export function choose(sp: Params, name: string, allowed: string[], fallback: string): [string, boolean] {
  const v = param(sp, name);
  if (v === undefined || v === "") return [fallback, false];
  return allowed.includes(v) ? [v, false] : [fallback, true];
}

export const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/** "29 September 2026" from an ISO timestamp (the UTC day). */
export function longDay(ts: string): string {
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return `${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

/** "28 September 2026 04:45 UTC" from an ISO timestamp. */
export function longTime(ts: string): string {
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return `${longDay(ts)} ${d.toISOString().slice(11, 16)} UTC`;
}

/** The period a series timestamp labels, by the table's interval: "2026" (P1Y), "September 2026" (P1M), a day (P1D),
 *  else the time. A series' ts_utc labels its period (docs/datastandard.md). */
export function periodOf(ts: string, interval: string | null | undefined): string {
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  if (interval === "P1Y") return String(d.getUTCFullYear());
  if (interval === "P1M") return `${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
  if (interval === "P1D") return longDay(ts);
  return longTime(ts);
}

/** The key form of a series timestamp, as check-values writes it: "2026-09-01T00:00:00Z". */
export function isoKey(ts: string): string {
  return new Date(ts).toISOString().replace(".000Z", "Z");
}
