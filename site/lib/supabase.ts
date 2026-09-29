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

/** Revalidation, in seconds: latest prices every 15 minutes, everything else hourly. */
export const LATEST = 900;
export const HOURLY = 3600;

const PAGE = 1000; // Supabase returns at most 1,000 rows per request

function config(): { base: string; key: string } {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) {
    throw new DataError("SUPABASE_URL or SUPABASE_ANON_KEY is not set on the server");
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
    let res: Response;
    try {
      res = await fetch(`${base}/rest/v1/${table}?${qs}`, {
        headers: { apikey: key, Authorization: `Bearer ${key}` },
        next: { revalidate, tags: [table] },
      });
    } catch (e) {
      throw new DataError(`Supabase ${table}: request failed (${(e as Error).message})`);
    }
    if (!res.ok) {
      const body = (await res.text()).slice(0, 200);
      throw new DataError(`Supabase ${table}: HTTP ${res.status} ${body}`);
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
  const res = await fetch(`${base}/rest/v1/${table}?${qs}`, {
    headers: { apikey: key, Authorization: `Bearer ${key}`, Prefer: "count=exact" },
    next: { revalidate, tags: [table] },
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

export async function insertRow(table: string, row: Record<string, string | boolean | string[] | number | null>): Promise<void> {
  const { base, key } = config();
  const res = await fetch(`${base}/rest/v1/${table}`, {
    method: "POST",
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json", Prefer: "return=minimal" },
    body: JSON.stringify(row),
    cache: "no-store",
  });
  if (!res.ok) throw new DataError(`Supabase ${table}: HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
}
