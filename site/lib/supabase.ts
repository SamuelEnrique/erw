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
  const { base, key } = config();
  const rows: T[] = [];
  for (let offset = 0; offset < max; offset += PAGE) {
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
    const batch = (await res.json()) as T[];
    rows.push(...batch);
    if (batch.length < PAGE) break;
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
