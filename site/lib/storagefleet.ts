// Energy Research Warehouse (ERW) site, session 7542 (chain 304, part C: /storage read as a lender's analyst reads it,
// docs/reviews/storage-read-2026-11-16.md). Pure helpers of the fleet tab (app/storage/page.tsx): a page file may export
// only what Next.js allows, so they live here, where a test can import them.

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/** The read's row 2: the EIA-860M inventory the fleet's rows are of, as "September 2026" (the newest vintage among
 *  them), so the fleet tab names its month as the build-out and owners tabs do; "" when no row carries one. */
export function inventory(units: { vintage?: string | null }[]): string {
  const v = units.map((u) => u.vintage ?? "").filter((s) => /^\d{4}-\d{2}$/.test(s)).sort().at(-1);
  return v ? `${MONTHS[Number(v.slice(5, 7)) - 1]} ${v.slice(0, 4)}` : "";
}

/** The read's row 6: the days between a sparkline's first and last that the table does not hold, for its hover
 *  ("; not held: 2026-11-04 to 2026-11-08"); "" when none is missing. A day is the row's date (its local day). */
export function notHeld(rows: { ts_utc: string }[]): string {
  if (rows.length < 2) return "";
  const have = new Set(rows.map((r) => r.ts_utc.slice(0, 10)));
  const runs: [string, string][] = [];
  const d = new Date(`${rows[0].ts_utc.slice(0, 10)}T00:00:00Z`);
  const end = rows[rows.length - 1].ts_utc.slice(0, 10);
  for (; d.toISOString().slice(0, 10) < end; d.setUTCDate(d.getUTCDate() + 1)) {
    const s = d.toISOString().slice(0, 10);
    if (have.has(s)) continue;
    const last = runs.at(-1);
    const prev = new Date(d.getTime() - 86_400_000).toISOString().slice(0, 10);
    if (last && last[1] === prev) last[1] = s;
    else runs.push([s, s]);
  }
  return runs.length ? `; not held: ${runs.map(([a, b]) => (a === b ? a : `${a} to ${b}`)).join(", ")}` : "";
}

/** The read's row 7: what the daily cycle's discharge counts, and the other count of ERCOT's on the site. */
export const DISCHARGED_TITLE = "The day's battery output above zero, added hour by hour: each grid's battery net generation as reported to EIA-930 (CAISO: its own Today's Outlook). It is the fleet's net output, so a battery charging while another discharges cancels within the hour. For ERCOT, the page What Texas's batteries were awarded day-ahead (/cost-of-power/battery/awards) adds each resource's own discharge from ERCOT's files, which is not netted and so stands above this count for the same month.";
