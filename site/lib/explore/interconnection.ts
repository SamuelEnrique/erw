// Energy Research Warehouse (ERW) site, session 405: the interconnection explorer's own parts
// (/explore/interconnection; the frame is components/explore/Explore.tsx, the shared helpers ./index.ts). It reads
// iso_queue_statistics (warehouse/derived/queue_statistics.py; docs/methods/energy_projects.md, "Queue statistics") as
// it stands and computes nothing: every figure it shows is one row of that table, or one count its header states, with
// the check key of that row or that count.
//
// This file holds no read and imports nothing, so a client component may import it and node can run it in the tests.

export const TABLE = "iso_queue_statistics";
export const METHOD = "/data/methods/energy_projects";

/** The six queues, in the order of the map's Queues tab (app/map/QueuesView.tsx): the grid's prefix and its name. */
export const QUEUES: [string, string][] = [["caiso", "CAISO"], ["ercot", "ERCOT"], ["nyiso", "NYISO"], ["miso", "MISO"], ["spp", "SPP"], ["isone", "ISO-NE"]];

/** What a queue does not hold, in the method note's words (the same lines as the map's Queues tab). */
export const NOT_HELD: Record<string, string> = {
  // session 7509 (chain 304): what "Entered" does not hold for CAISO and ERCOT, found by the cross-check against Berkeley
  // Lab's Queued Up (docs/methods/interconnection_explorer.md, "The cross-check"); the map's tab keeps its own lines
  caiso: "CAISO's public queue report lists only a few of the requests that entered in 2023 and none that entered later, so its counts for 2023 are the report's rows, far fewer than the requests made that year; Berkeley Lab's Queued Up, on the interconnection queue page, counts them.",
  // session 7518 (chain 304, part B): what ERCOT's "completed" is. The library the queue connector reads ERCOT's report
  // through (gridstatus 0.36.0, ercot.py) writes "Completed" when the report's "IA Signed" date is filled, so the table's
  // positions_operating for ERCOT is the positions with a signed agreement: on the pull of 30 September 2026 all 44 such
  // positions of entry year 2025 have a projected operation date still to come and none a date of approval to synchronize
  ercot: "ERCOT's report lists active and completed positions only, so no withdrawn count and no withdrawal rate are held, and \"Entered\" counts the positions of an entry year that are still in the report, not every request made that year. For ERCOT the count other queues call \"Reached operation\" is the positions whose interconnection agreement is signed, most of a recent year's not yet built, so it is headed \"Agreement signed\" here, and \"No agreement yet\" is the rest; \"Waits counted\" is the positions the report gives a day of approval to synchronize, and the wait runs from the day the screening study started to that day.",
  miso: "MISO's queue holds no in-service date, so no wait is held.",
  isone: "ISO-NE's queue holds no in-service date, so no wait is held.",
  spp: "SPP's wait reads its Commercial Operation Date, which its queue fills for active and withdrawn positions too: for an operating position it may be the date requested, not achieved.",
};

/** The four statuses a position of an entry year is counted in (the method note: each ISO's own words as the queue
 *  connector maps them). The four make up the positions entered; a status a queue does not hold has no row. `short`
 *  names the series on the chart, where four long names overrun a phone's width. */
export const STATUSES = [
  { key: "operating", label: "Reached operation", short: "Operating", color: "var(--color-fuel-nuclear)" },
  { key: "withdrawn", label: "Withdrawn", short: "Withdrawn", color: "var(--color-muted)" },
  { key: "waiting", label: "Still waiting", short: "Waiting", color: "var(--color-accent)" },
  { key: "status_not_stated", label: "Status not stated", short: "No status", color: "var(--color-not-reported)" },
] as const;

export type StatusKey = (typeof STATUSES)[number]["key"];

/** Session 7518 (chain 304, part B): a queue whose status is not what the common word says is headed by what it is.
 *  ERCOT's report has no word for a plant in operation: the table's `operating` group is the positions with a signed
 *  interconnection agreement, and its `waiting` group those with none (NOT_HELD.ercot; the method note, "What a queue
 *  does not hold"). The variables keep their names (positions_operating, mw_waiting): only the words drawn change. */
export const STATUS_WORDS: Record<string, Partial<Record<StatusKey, { label: string; short: string }>>> = {
  ercot: { operating: { label: "Agreement signed", short: "Signed" }, waiting: { label: "No agreement yet", short: "No agreement" } },
};
/** Why a queue has words of its own, for the tip beside its name in the six queues' table (whose columns keep the common words). */
export const STATUS_WHY: Record<string, string> = {
  ercot: "ERCOT's report has no word for a plant in operation. A position is counted in the first when the report gives a day its interconnection agreement was signed, most of a recent year's not yet built, and in the second when it gives none.",
};
/** The words one queue's status is drawn with: its own where it has them, else the common ones. */
export function statusWords(iso: string, key: StatusKey): { label: string; short: string } {
  const s = STATUSES.find((x) => x.key === key)!;
  return STATUS_WORDS[iso]?.[key] ?? { label: s.label, short: s.short };
}

/** Session 7518: the hover of the wait's chart: whose waits a point counts, and the two other pages that count a wait
 *  another way (by the year a plant came online, from Berkeley Lab's Queued Up). Facts, no view. */
export function waitTip(iso: string): string {
  const own = iso === "ercot" ? " ERCOT's wait runs from the day a position's screening study started to the day the report says it was approved to synchronize."
    : iso === "spp" ? " SPP's in-service date is its Commercial Operation Date, which may be the date requested." : "";
  return "A point counts only the positions of an entry year that have already reached operation with both dates; \"Waits counted\" in the table below says how many. "
    + "A position still waiting is in no point, and if it is built its wait will be longer than the time since it entered: a recent entry year's median stands on its fastest positions and is not final." + own
    + " Two other pages count a wait by the year a plant came online, not the year it entered, from Berkeley Lab's Queued Up: the interconnection queue page, and \"Time to connect\" on the All grids tab of the cost of power page (the plants that came online in its last three years). The three are different counts and do not give one number.";
}

/** Session 7518: the extra columns of the six queues' table when the count is positions: the withdrawn share and the
 *  wait of the one entry year, queue beside queue. */
export const QUEUE_COLUMNS: [string, string][] = [["withdrawal_rate", "Withdrawn, share of entered"], ["wait_years_median", "Median wait, years"], ["wait_positions", "Waits counted"]];

/** Session 7518: where Berkeley Lab's Queued Up counts a queue this page does not show (PJM, which the ERW holds no
 *  queue table of, and the three held queues): the interconnection queue page's own address for the grid. */
export const QUEUED_UP_GRIDS = ["pjm", "miso", "nyiso", "isone"];
export const queuedUpHref = (grid: string) => `/queues?grid=${grid}&tech=all`;

export const MEASURES = [
  { key: "positions", label: "Positions", unit: "positions" },
  { key: "mw", label: "MW", unit: "MW" },
] as const;
export type Measure = (typeof MEASURES)[number]["key"];

export type Row = { entity: string; variable: string; ts_utc: string; value: number };

/** The entity of one queue's entry year, as the table writes it: "ercot:queue_2019". */
export const entityOf = (iso: string, year: number | string) => `${iso}:queue_${year}`;
/** The label timestamp of an entry year. */
export const yearTs = (year: number | string) => `${year}-01-01T00:00:00Z`;
/** The entry year an entity names, or null. */
export function yearOf(entity: string): number | null {
  const m = /:queue_(\d{4})$/.exec(entity);
  return m ? Number(m[1]) : null;
}

/** One row's value among a queue's rows, by entry year and variable. */
export function valueOf(rows: Row[], iso: string, year: number, variable: string): number | undefined {
  const e = entityOf(iso, year);
  const r = rows.find((x) => x.entity === e && x.variable === variable);
  return r === undefined ? undefined : Number(r.value);
}

/** Ruling alternative 2 (session 7710, branch wip/alt-interconnection-2; not a default on main): the page opens on the
 *  newest complete entry year with at least this many positions entered, not the newest complete year whatever its count
 *  (CAISO's 2023, 4 positions, as main opens). */
export const OPENING_MIN_POSITIONS = 20;
/** The year the page opens on: the newest of `complete` with at least OPENING_MIN_POSITIONS entered, else the newest of
 *  `complete`, else null. */
export function openingYear(rows: Row[], iso: string, complete: number[]): number | null {
  const tens = complete.filter((y) => (valueOf(rows, iso, y, "positions_entered") ?? 0) >= OPENING_MIN_POSITIONS);
  return tens.length ? tens[tens.length - 1] : complete.length ? complete[complete.length - 1] : null;
}

/** The commit that fixed the build's read (session 367, 005b590d, 20 October 2026 19:45:54 UTC): a table whose header
 *  says it was built before this was built by the faulty read (the method note, "A fault in the first build"). */
export const FIXED_AT = "2026-10-20T19:45:54Z";

/** The time the table was built, from its header's "Retrieved: 20261020T093659Z (UTC) by ..." line, ISO form, or null. */
export function builtAt(header: string[]): string | null {
  const l = header.find((x) => x.startsWith("Retrieved:"));
  const m = l?.match(/(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z/);
  return m ? `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}Z` : null;
}

/** Whether the table as it stands is the faulty build's: built before the fix, or of a time the header does not say. */
export function faultyBuild(header: string[]): boolean {
  const b = builtAt(header);
  return b === null || new Date(b).getTime() < new Date(FIXED_AT).getTime();
}

/** When one queue's input was retrieved, from the header's "Inputs read:" line ("ercot_interconnection_queue (1758
 *  rows; retrieved 20261019T203101Z; ..."), ISO form, or null. */
export function inputRetrieved(header: string[], iso: string): string | null {
  const l = header.find((x) => x.startsWith("Inputs read:"));
  const m = l?.match(new RegExp(`(?:^|[:;] )${iso}_interconnection_queue \\([^)]*?retrieved (\\d{4})(\\d{2})(\\d{2})T(\\d{2})(\\d{2})(\\d{2})Z`));
  return m ? `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}Z` : null;
}

/** The header's line of the positions with no queue date (counted in no year). */
export const UNDATED = "Positions with no queue date";

/** A count the header states for one queue, on the line that begins with `prefix` ("...: ERCOT 456, CAISO 169"), or
 *  null. The queue is named as the header names it (ISO-NE, not isone). */
export function headerCount(header: string[], prefix: string, name: string): number | null {
  const l = header.find((x) => x.startsWith(prefix));
  if (!l) return null;
  const items = l.slice(l.indexOf(":") + 1).split(",").map((s) => s.trim());
  const it = items.find((s) => s.startsWith(`${name} `));
  const n = it ? Number(it.slice(name.length + 1).replace(/,/g, "")) : NaN;
  return Number.isFinite(n) ? n : null;
}

/** The check key of a count the header states: series_hdr|<table>|iso:<grid>|<line prefix>|<name>. It names the grid as
 *  an entity, so a held grid's count is held as its rows are (components/Num.tsx); scripts/check-values.mjs reads it. */
export const headerKey = (iso: string, prefix: string, name: string) => `series_hdr|${TABLE}|iso:${iso}|${prefix}|${name}`;

/** Whether an entry year is not over: the year the queue's input was retrieved in (its positions are still entering). */
export function partialYear(year: number, retrieved: string | null, now = new Date()): boolean {
  const y = retrieved ? new Date(retrieved).getUTCFullYear() : now.getUTCFullYear();
  return year >= y;
}

/** Session 7509 (chain 304): how a figure is written, by its variable. A count of positions is whole; MW, the withdrawn
 *  share and a wait in years always carry two decimals. Until then lib/format.ts's shown() wrote a value that happened
 *  to be whole without them: "550" above "162.10" in the MW column, a share of "1" above "0.86". The text still begins
 *  with what scripts/check-values.mjs expects of the raw value. */
export function figureText(variable: string, v: number): string {
  const whole = variable.startsWith("positions_") || variable === "wait_positions";
  return whole ? Math.round(v).toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
