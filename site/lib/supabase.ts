// Energy Research Warehouse (ERW) site: the one way the site reads Supabase.
//
// PostgREST over plain fetch, with SUPABASE_URL and SUPABASE_ANON_KEY for every read. The
// anon key is subject to row-level security (warehouse/supabase/migrations/002_rls.sql):
// it sees public rows and nothing else. Since session 19 the site also inserts into subscribers,
// and since then the game's tables and the model-call ledger (migrations 005, 010, 013).
// Session 301 (docs/reviews/2026-10-10-security.md, H3 and M1): the site's writes (insertRow, and rpc with
// `privileged`) go with SUPABASE_SERVICE_KEY when the server holds it, so the anon key's insert policies on those
// tables can be dropped (migration 034) and a holder of the anon key can write nothing. Without the service key the
// writes still go with the anon key, as before, so the order of the change is free: key first, site second, policy
// last. The service key is read by writeConfig() only, never for a read, and like the other two variables it is
// server-side (no NEXT_PUBLIC_ prefix): none reaches a browser.
import "server-only";
import { ROW_LICENSE_FILTER, ROW_LICENSE_PUBLIC, gridOfEntity, licenseByGrid, licenseByRow, licenseHeldGrid, licenseHeldRow, licenseNeeded, licenseReason, rowLicenseHeld } from "./license";

/** A read that failed. Pages show its message as the reason for "no data". */
export class DataError extends Error {}
/** Session 215: a read of a table that is "license needed" today (lib/license.ts). Not a failed read: nothing was
 * asked. attempt() and required() turn it into its reason, whose prefix components/NoData.tsx draws as the catalogue's
 * words, "license needed", in the place the numbers would have been. */
export class LicenseNeeded extends DataError {
  table: string;
  constructor(table: string) {
    super(licenseReason(table));
    this.table = table;
  }
}

/** The ERW table a query names (table_name: "eq.<table>"), or "" when it names none (the catalogue, latest_prices). */
function tableOf(query: Record<string, string>): string {
  const t = query.table_name ?? "";
  return t.startsWith("eq.") ? t.slice(3) : "";
}

/** The grid a query asks for, by its entity or market filter ("entity": "eq.isone:.H.INTERNAL_HUB", "market": "eq.isone_dam"), or "". */
function gridOfQuery(query: Record<string, string>): string {
  const e = query.entity ?? "";
  if (e.startsWith("eq.")) return gridOfEntity(e.slice(3));
  if (e.startsWith("in.(")) {
    const grids = new Set(e.slice(4, -1).split(",").map((x) => gridOfEntity(x.trim().replace(/^"|"$/g, ""))));
    return grids.size === 1 ? [...grids][0] : "";
  }
  const m = query.market ?? "";
  if (m.startsWith("eq.")) return gridOfEntity(`${m.slice(3).split("_")[0]}:x`);
  return "";
}

/** Session 215: whether this read is held whole (throw), and, for a table held by grid with no grid named, that the
 * rows of the held grids are to be left out of what comes back. */
function licenseHold(query: Record<string, string>): { throw: boolean; filter: boolean; byRow?: boolean } {
  const t = tableOf(query);
  if (!t || !licenseNeeded(t)) return { throw: false, filter: false };
  if (licenseByRow(t)) return { throw: false, filter: false, byRow: true };  // session 499: the public rows only
  if (!licenseByGrid(t)) return { throw: true, filter: false };
  const g = gridOfQuery(query);
  if (g) return { throw: licenseHeldGrid(g), filter: false };
  return { throw: false, filter: true };
}
/** No database is named on this server: a build without its keys (the workflow's build before the secrets were set, a
 * first checkout). Not a read that failed: nothing was asked. */
export class NotConfigured extends DataError {}

/** Revalidation, in seconds: latest prices every 15 minutes, everything else hourly. */
export const LATEST = 900;
export const HOURLY = 3600;

const PAGE = 1000; // Supabase returns at most 1,000 rows per request

// Session 90: the waits between tries of a read cancelled by the statement timeout. A request waits 1 and 3 seconds
// (session 43). The build waits longer, 1, 3, 5, 8 and 12 seconds: it asks for every page's rows at once, on tables a
// deploy finds cold, and three deploys in a row (sessions 77, 87, 88) lost one read of the home page that way.
const BUILDING = process.env.NEXT_PHASE === "phase-production-build";
const WAITS = BUILDING ? [1000, 3000, 5000, 8000, 12000] : [1000, 3000];

// Session 90: while the site is built, each build worker sends at most BUILD_READS reads at a time. The build renders
// some forty pages at once and each asks for its rows; the database answered the public key's statements late, past its
// 3 seconds, and cancelled them: pages were built, and cached, with "no data" where a table holds data. Waiting for a
// turn costs the build seconds and keeps every read inside its limit. A request outside the build is sent at once.
const BUILD_READS = 2;
let inFlight = 0;
const waiting: (() => void)[] = [];
async function turn<T>(f: () => Promise<T>): Promise<T> {
  if (!BUILDING) return f();
  // a read that waited is handed the slot of the one that finished, so the count never passes BUILD_READS
  if (inFlight >= BUILD_READS) await new Promise<void>((go) => waiting.push(go));
  else inFlight++;
  try {
    return await f();
  } finally {
    const next = waiting.shift();
    if (next) next();
    else inFlight--;
  }
}

// Session 580: the time of each read, for a measurement (docs/reviews/slow-reads-2026-10-22.md). Off unless the server
// or the build is started with ERW_READ_TIMING=1. Off, readClock() answers 0 without reading a clock and readLine()
// returns at once: the request is the one it was, sent and awaited by the same line. On, each request (one page of a
// read, or a count) prints one line, "[erw-read] " and a JSON object: kind ("rows" or "count"), table, query (the
// PostgREST parameters as sent), status ("failed" for a request that never answered), range (PostgREST's
// Content-Range: the rows answered, and the total for a count) and ms, the time from the request to its answer's
// headers, measured inside the build's turn so a wait for a slot is not counted. A retry is its own line.
// site/scripts/slow-reads.mjs reads those lines from a build's log. Nothing is written to a file or sent anywhere.
export function readTiming(v: string | undefined): boolean {
  return v === "1";
}
const READ_TIMING = readTiming(process.env.ERW_READ_TIMING);
function readClock(): number {
  return READ_TIMING ? performance.now() : 0;
}
function readLine(kind: "rows" | "count", table: string, qs: URLSearchParams, t0: number, r: Response | undefined): void {
  if (!READ_TIMING) return;
  const ms = Math.round(performance.now() - t0);
  const status = r ? String(r.status) : "failed";
  const range = r?.headers.get("content-range") ?? "";
  console.log(`[erw-read] ${JSON.stringify({ kind, table, query: qs.toString(), status, range, ms })}`);
}

function config(): { base: string; key: string } {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) {
    throw new NotConfigured("SUPABASE_URL or SUPABASE_ANON_KEY is not set on the server");
  }
  return { base: new URL(url).origin, key };
}

/** Session 301: the key a write goes with: the service key when the server holds it (row-level security does not
 * bind it, so the anon key's insert policies can go), else the anon key as before. */
function writeConfig(): { base: string; key: string; role: "service" | "anon" } {
  const c = config();
  const service = process.env.SUPABASE_SERVICE_KEY;
  return service ? { ...c, key: service, role: "service" } : { ...c, role: "anon" };
}
/** Which key the site's writes go with on this server (for a check, never a page). */
export function writeRole(): "service" | "anon" {
  return process.env.SUPABASE_SERVICE_KEY ? "service" : "anon";
}

// Session 148: the pages of one large read are asked for together, PAGES_TOGETHER at a time, outside the build. Until
// then a read of 9,000 rows was nine requests one after another (session 143: one read of a year of hourly reserve
// prices took 13.3 seconds). What a caller gets is what it always got: the same rows in the same order, and the same
// failure (restPaged below says why). While the site is built the reader is the one it always was, one page after
// another: session 90's rule that the build's reads take turns stands as it was written. ERW_PAGES_TOGETHER on the
// server sets another number from 1 to 8; 1 is the reader as it was before this session, everywhere.
export function pagesTogether(v: string | undefined, building = false): number {
  if (building) return 1;
  const n = Number(v);
  return v !== undefined && v !== "" && Number.isInteger(n) && n >= 1 && n <= 8 ? n : 4;
}
const PAGES_TOGETHER = pagesTogether(process.env.ERW_PAGES_TOGETHER, BUILDING);

// Session 537: a page whose read failed is asked again soon, not after its whole interval. A page is cached for the
// shortest revalidation among the reads made while it was rendered. A read that failed (the statement timeout past
// session 90's retries, a refused request, an HTTP error) leaves the page with "no data" in that place, and until this
// session the page was kept that way for its own interval: an hour, or until the next deploy for a page with none
// (session 461's check-routes: 15 pages built on a slow live set). Now a failed read also asks Next for a revalidation
// of RETRY seconds, through unstable_cache, the one public call whose interval Next takes into the page's own (a fetch
// that failed is never kept in Next's data cache: only a 200 is). So the page that lost a read is regenerated on the
// first request after RETRY seconds, in the background as every regeneration is (that request is answered with the
// page as it was, the next one with the new page), and a page whose reads all succeeded never comes here and keeps its
// interval exactly. Nothing is read from the database for the mark: it is one small entry in Next's own cache, kept per
// page. A read held for a license (LicenseNeeded) and a server with no database named (NotConfigured) are not failed
// reads and are not marked. required() reads keep failing the build, and a render that throws is never cached, as
// before. Outside Next (the node scripts that import this file, the tests) there is no page and no mark.
export const RETRY = 60;
let askAgainMark: (() => Promise<boolean>) | null = null;
export async function markFailedRead(e: unknown): Promise<boolean> {
  if (e instanceof LicenseNeeded || e instanceof NotConfigured) return false;
  if (!process.env.NEXT_RUNTIME) return false;   // not inside Next: a script or a test, with no page to mark
  try {
    if (!askAgainMark) {
      const { unstable_cache } = await import("next/cache");
      askAgainMark = unstable_cache(async () => true, ["erw-failed-read"], { revalidate: RETRY });
    }
    await askAgainMark();
    return true;
  } catch (m) {
    console.error(`[erw] a failed read could not shorten the page's revalidation: ${(m as Error).message}`);
    return false;
  }
}
async function askAgainOnFailure<T>(f: () => Promise<T>): Promise<T> {
  try {
    return await f();
  } catch (e) {
    await markFailedRead(e);
    throw e;
  }
}

/** One page of a read: the request, its retries and its failure, exactly as the reader always made them. */
async function onePage<T>(base: string, key: string, table: string, query: Record<string, string>, revalidate: number, offset: number, max: number): Promise<T[]> {
  const qs = new URLSearchParams({ ...query, limit: String(Math.min(PAGE, max - offset)), offset: String(offset) });
  let res: Response | null = null;
  let body = "";
  // session 39: a retry of a statement timeout (Postgres 57014). A build that runs right after the loader's VACUUM FULL,
  // or while the daily run loads, meets cold or busy tables, and seven grid pages at once took the anon role past its
  // 3 s limit. Session 43: two retries, after 1 and 3 seconds (one retry still lost the NYISO and SPP queue reads).
  for (let attempt = 0; attempt <= WAITS.length; attempt++) {
    try {
      // the body of a failed answer is read inside the turn, so the slot is held until the request is over
      [res, body] = await turn(async () => {
        const t0 = readClock();   // session 580: 0 and no clock unless ERW_READ_TIMING=1
        let r: Response | undefined;
        try {
          r = await fetch(`${base}/rest/v1/${table}?${qs}`, {
            headers: { apikey: key, Authorization: `Bearer ${key}` },
            next: { revalidate, tags: [table] },
          });
        } finally {
          readLine("rows", table, qs, t0, r);
        }
        return [r, r.ok ? "" : (await r.text()).slice(0, 200)] as [Response, string];
      });
    } catch (e) {
      throw new DataError(`Supabase ${table}: request failed (${(e as Error).message})`);
    }
    if (res.ok) break;
    if (attempt < WAITS.length && res.status === 500 && body.includes("57014")) {
      await new Promise((r) => setTimeout(r, WAITS[attempt]));
      continue;
    }
    break;
  }
  if (!res || !res.ok) {
    throw new DataError(`Supabase ${table}: HTTP ${res ? res.status : "none"} ${body}`);
  }
  return (await res.json()) as T[];
}

/**
 * Rows of one Supabase table. `query` holds PostgREST parameters, for example
 * { select: "entity,value", table_name: "eq.news_index", order: "ts_utc" }.
 * Pages through the result 1,000 rows at a time, up to `max` rows.
 */
export async function rest<T>(
  table: string,
  query: Record<string, string>,
  revalidate: number,
  max = 50_000,
): Promise<T[]> {
  return restPaged<T>(table, query, revalidate, max, PAGES_TOGETHER);
}

/**
 * Session 148: the reader behind rest, with the number of pages asked for at a time given (rest gives the server's;
 * scripts/compare-paged-reads.mjs and the tests give 1 and 4 and compare). `together` 1 is the reader as it always was:
 * a page is asked for only when the one before it came back full.
 *
 * With `together` above 1 the first page is still asked for alone, by the same request as before, so a read of fewer
 * than 1,000 rows (almost every read of the site) is unchanged in every respect. Only when it comes back full are the
 * next pages asked for, `together` at a time, and they are taken in their order:
 *   - a full page is added and the next is looked at;
 *   - a page of fewer than 1,000 rows is the last: the rows are returned, and whatever a page asked for beyond it
 *     answered, rows or a failure, is not part of the read (the reader as it was never asked for it);
 *   - a page that failed, with every page before it full, fails the read with that page's own error: the page the
 *     reader as it was would have stopped at, and the error it would have thrown.
 * So the rows, their order and the failure are the serial reader's. What differs is when the requests are sent, and that
 * up to `together` less one requests may go to pages beyond the end, which answer with no rows.
 */
export async function restPaged<T>(
  table: string,
  query: Record<string, string>,
  revalidate: number,
  max: number,
  together: number,
): Promise<T[]> {
  // session 215: a held table is not asked for; a table held by grid, read with no grid named, loses the held grids' rows
  const hold = licenseHold(query);
  if (hold.throw) throw new LicenseNeeded(tableOf(query));
  if (hold.byRow) {
    // session 499: a table held by row is asked for its public rows only, and what comes back is checked again
    const rows = await askAgainOnFailure(() => restPages<T>(table, publicRowsQuery(query), revalidate, max, together));
    return rows.filter((r) => !rowLicenseHeld(r as Record<string, unknown>));
  }
  const rows = await askAgainOnFailure(() => restPages<T>(table, query, revalidate, max, together));
  if (!hold.filter) return rows;
  const t = tableOf(query);
  return rows.filter((r) => !licenseHeldRow(t, (r as { entity?: string }).entity ?? ""));
}

async function restPages<T>(table: string, query: Record<string, string>, revalidate: number, max: number, together: number): Promise<T[]> {
  const { base, key } = config();
  const rows: T[] = [];
  const page = (offset: number) => onePage<T>(base, key, table, query, revalidate, offset, max);
  if (!(together > 1)) {
    for (let offset = 0; offset < max; offset += PAGE) {
      const batch = await page(offset);
      rows.push(...batch);
      if (batch.length < PAGE) break;
    }
    return rows;
  }
  if (max <= 0) return rows;
  const first = await page(0);
  rows.push(...first);
  if (first.length < PAGE) return rows;
  for (let offset = PAGE; offset < max; ) {
    const asked: Promise<T[]>[] = [];
    for (let i = 0; i < together && offset < max; i++, offset += PAGE) asked.push(page(offset));
    // a page beyond the last may fail after the read has returned: its failure is nobody's, and must not go unhandled
    for (const p of asked) p.catch(() => {});
    for (const p of asked) {
      const batch = await p;          // in order: the first page that failed, with every page before it full, throws here
      rows.push(...batch);
      if (batch.length < PAGE) return rows;
    }
  }
  return rows;
}

/** The number of rows matching `query`, without reading them (PostgREST exact count). */
export async function restCount(table: string, query: Record<string, string>, revalidate: number): Promise<number> {
  if (licenseHold(query).throw) throw new LicenseNeeded(tableOf(query));  // session 215; a count over a table held by grid is the table's own
  // session 499: a count over a table held by row counts its public rows
  if (licenseHold(query).byRow) return restCountRaw(table, publicRowsQuery(query), revalidate);
  return askAgainOnFailure(() => countOf(table, query, revalidate));
}

/** Session 499: the query for the public rows of a table held by row (the row's own license, `extra->>row_license`;
 *  session 441's method, lib/license.ts). */
export function publicRowsQuery(query: Record<string, string>): Record<string, string> {
  return { ...query, [ROW_LICENSE_FILTER]: `eq.${ROW_LICENSE_PUBLIC}` };
}

/** Session 499: the query for the held rows of a table held by row: every row whose license is not public, a missing
 *  one included. Counted, never read. */
export function heldRowsQuery(query: Record<string, string>): Record<string, string> {
  const held = `${ROW_LICENSE_FILTER}.is.null,${ROW_LICENSE_FILTER}.neq.${ROW_LICENSE_PUBLIC}`;
  if (!query.or) return { ...query, or: `(${held})` };
  const { or, ...rest } = query;  // a query that has its own `or` keeps it: both must hold
  return { ...rest, and: `(or${or},or(${held}))` };
}

/** Session 499: how many rows of a table held by row are held (a count, not a row of it); null for any other table. */
export async function restHeldRowCount(table: string, query: Record<string, string>, revalidate: number): Promise<number | null> {
  if (!licenseHold(query).byRow) return null;
  return restCountRaw(table, heldRowsQuery(query), revalidate);
}

/** Session 506's merge: session 499's count, asked again on a failure as session 537's counts are. */
async function restCountRaw(table: string, query: Record<string, string>, revalidate: number): Promise<number> {
  return askAgainOnFailure(() => countOf(table, query, revalidate));
}

async function countOf(table: string, query: Record<string, string>, revalidate: number): Promise<number> {
  const { base, key } = config();
  const qs = new URLSearchParams({ ...query, limit: "1" });
  const url = `${base}/rest/v1/${table}?${qs}`;
  const res = await turn(async () => {
    const t0 = readClock();   // session 580: 0 and no clock unless ERW_READ_TIMING=1
    let r: Response | undefined;
    try {
      r = await fetch(url, {
        headers: { apikey: key, Authorization: `Bearer ${key}`, Prefer: "count=exact" },
        next: { revalidate, tags: [table] },
      });
    } finally {
      readLine("count", table, qs, t0, r);
    }
    return r;
  });
  if (!res.ok) throw new DataError(`Supabase ${table}: HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
  const range = res.headers.get("content-range") ?? "";
  const n = Number(range.split("/")[1]);
  if (!Number.isFinite(n)) throw new DataError(`Supabase ${table}: no count in the response`);
  return n;
}

/** Run a read and turn a failure into a reason, so a page section can say why it has no data. */
export async function attempt<T>(f: () => Promise<T>): Promise<{ ok: true; data: T } | { ok: false; reason: string }> {
  try {
    return { ok: true, data: await f() };
  } catch (e) {
    const reason = e instanceof DataError ? e.message : `unexpected error: ${(e as Error).message}`;
    console.error(`[erw] ${reason}`);
    return { ok: false, reason };
  }
}

/**
 * Session 90: a read a page will not be cached without. Like attempt, but a read that failed is thrown, not turned into
 * a reason. The home page is generated once and served from the cache for 15 minutes; with attempt, one read cancelled
 * while the page was generated left a tile reading "not held" for every visitor until the cache turned (after the
 * deploys of sessions 77, 87 and 88). A page that throws is never cached: when it is regenerated in the background the
 * last good page stays, and the next request tries again; when the site is built the build fails, so a deploy with a
 * hole in the home page does not go live. A server with no database named (NotConfigured) is not a failed read: the
 * page says so, as before. Nor is a build against a stand-in on this machine (scripts/buildout-stub.mjs and
 * shoulder-stub.mjs answer one table and nothing else): a database at localhost is a fixture, never the warehouse.
 */
const standIn = () => /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/.test(process.env.SUPABASE_URL ?? "");
export async function required<T>(f: () => Promise<T>): Promise<{ ok: true; data: T } | { ok: false; reason: string }> {
  try {
    return { ok: true, data: await f() };
  } catch (e) {
    const reason = e instanceof DataError ? e.message : `unexpected error: ${(e as Error).message}`;
    if (e instanceof NotConfigured || standIn()) return { ok: false, reason };
    if (e instanceof LicenseNeeded) return { ok: false, reason };  // session 215: a held table is not a failed read; the page shows the words
    console.error(`[erw] a required read failed; this render is not cached: ${reason}`);
    throw e instanceof DataError ? e : new DataError(reason);
  }
}

/**
 * Session 19: add one row to a table the anon key may insert into (subscribers, migration 005).
 * Asks for no row back: the anon key cannot read that table.
 */
/** Session 23: call a database function the anon key may execute (subscribe_confirm, subscribe_unsubscribe).
 * Session 301: `privileged` calls it with the write key (site_ask_admit, whose execute right the anon key loses in
 * migration 034), so no holder of the anon key can fill the question tools' counts. */
export async function rpc<T>(fn: string, args: Record<string, string>, opts: { privileged?: boolean } = {}): Promise<T> {
  const { base, key } = opts.privileged ? writeConfig() : config();
  const res = await fetch(`${base}/rest/v1/rpc/${fn}`, {
    method: "POST",
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(args),
    cache: "no-store",
  });
  if (!res.ok) throw new DataError(`Supabase rpc ${fn}: HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
  return (await res.json()) as T;
}

export async function insertRow(table: string, row: Record<string, string | boolean | string[] | number | number[] | null | object>): Promise<void> {
  const { base, key } = writeConfig();   // session 301: the service key when held (subscribers, game_scores, game_plays, site_api_calls)
  const res = await fetch(`${base}/rest/v1/${table}`, {
    method: "POST",
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json", Prefer: "return=minimal" },
    body: JSON.stringify(row),
    cache: "no-store",
  });
  if (!res.ok) throw new DataError(`Supabase ${table}: HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
}
