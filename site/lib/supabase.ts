// Energy Research Warehouse (ERW) site: the one way the site reads Supabase.
//
// PostgREST over plain fetch, with SUPABASE_URL and SUPABASE_ANON_KEY only. The
// anon key is subject to row-level security (warehouse/supabase/migrations/002_rls.sql):
// it sees public rows and nothing else. The service key is never read here. Since session 19
// it also inserts into subscribers, the one table the anon key may write (migration 005).
// Both variables are server-side (no NEXT_PUBLIC_ prefix), so neither reaches a browser.
import "server-only";

/** A read that failed. Pages show its message as the reason for "no data". */
export class DataError extends Error {}
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

function config(): { base: string; key: string } {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) {
    throw new NotConfigured("SUPABASE_URL or SUPABASE_ANON_KEY is not set on the server");
  }
  return { base: new URL(url).origin, key };
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
        const r = await fetch(`${base}/rest/v1/${table}?${qs}`, {
          headers: { apikey: key, Authorization: `Bearer ${key}` },
          next: { revalidate, tags: [table] },
        });
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
  const { base, key } = config();
  const qs = new URLSearchParams({ ...query, limit: "1" });
  const res = await turn(() => fetch(`${base}/rest/v1/${table}?${qs}`, {
    headers: { apikey: key, Authorization: `Bearer ${key}`, Prefer: "count=exact" },
    next: { revalidate, tags: [table] },
  }));
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
    console.error(`[erw] a required read failed; this render is not cached: ${reason}`);
    throw e instanceof DataError ? e : new DataError(reason);
  }
}

/**
 * Session 19: add one row to a table the anon key may insert into (subscribers, migration 005).
 * Asks for no row back: the anon key cannot read that table.
 */
/** Session 23: call a database function the anon key may execute (subscribe_confirm, subscribe_unsubscribe). */
export async function rpc<T>(fn: string, args: Record<string, string>): Promise<T> {
  const { base, key } = config();
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
  const { base, key } = config();
  const res = await fetch(`${base}/rest/v1/${table}`, {
    method: "POST",
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json", Prefer: "return=minimal" },
    body: JSON.stringify(row),
    cache: "no-store",
  });
  if (!res.ok) throw new DataError(`Supabase ${table}: HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
}
