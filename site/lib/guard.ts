// Energy Research Warehouse (ERW) site, session 177: what every route that spends money or writes asks first
// (docs/reviews/2026-10-10-security.md).
//
//   sameOrigin(req)   a browser on another site may not post here. A request that names an Origin (every browser does,
//                     on a POST) must name this site's own; one that names none (a script, a mail client) passes this
//                     test and meets the others.
//   scripted(req)     the user agent is empty, or is the stock one of a command-line client or a scraping library.
//   limited(req, bucket, limit, seconds)
//                     a limit per visitor that holds across the server's instances: the database counts
//                     (site_rate_admit, migration 028), and this instance's memory counts as well, as the routes always
//                     did. When the database cannot be asked (the migration is not applied, the secrets are not on
//                     the server, the call fails) the memory's count alone decides: the floor the routes had before.
//
// THE VISITOR. No address is stored anywhere. The key the database counts is HMAC-SHA256 of the UTC day and the
// address under ASK_VISITOR_SALT (the same key /api/ask's daily count uses, lib/chat/limits.ts): it cannot be turned
// back into an address without the secret, and it is another value tomorrow. The address itself lives only in this
// instance's memory, for the window of the limit.
//
// This is basic protection, and it says so: a script that sends a browser's user agent and no Origin passes the first
// two tests. What stops spending is the limit, and behind it the ceilings of lib/chat/limits.ts.
import "server-only";
import { createHmac, timingSafeEqual } from "node:crypto";
import { readSalt, utcDay, visitorKey } from "@/lib/chat/limits";

export function clientIp(req: Request): string {
  const fwd = req.headers.get("x-forwarded-for");
  if (fwd) return fwd.split(",")[0].trim();
  return req.headers.get("x-real-ip") ?? "unknown";
}

/** false when the request names an Origin (or a fetch site) that is not this site. */
export function sameOrigin(req: Request): boolean {
  if (req.headers.get("sec-fetch-site") === "cross-site") return false;
  const origin = req.headers.get("origin");
  if (origin === null || origin === "") return true;
  let theirs: string;
  try {
    theirs = new URL(origin).host;
  } catch {
    return false;                       // "null" (a sandboxed page) or anything that is not an address
  }
  const ours = [req.headers.get("x-forwarded-host"), req.headers.get("host")];
  try { ours.push(new URL(req.url).host); } catch { /* a relative address names no host */ }
  return ours.some((h) => !!h && h.split(",")[0].trim().toLowerCase() === theirs.toLowerCase());
}

const STOCK = /^(curl|wget|python-requests|python-urllib|python-httpx|aiohttp|go-http-client|scrapy|libwww-perl|java|okhttp|httpie|postmanruntime|insomnia|axios|got |node-fetch|php|ruby|apache-httpclient)/i;
/** true for an empty user agent or the stock one of a command-line client or a scraping library. Node's own fetch
 * ("node") is not in the list: the ERW's scripted checks use it. */
export function scripted(req: Request): boolean {
  const ua = (req.headers.get("user-agent") ?? "").trim();
  return ua.length < 4 || ua.length > 600 || STOCK.test(ua);
}

/** Does the body say it is JSON (or, for a form, a form)? A browser's cross-site form cannot say application/json. */
export function typed(req: Request, kind: "json" | "form"): boolean {
  const t = (req.headers.get("content-type") ?? "").toLowerCase();
  if (kind === "json") return t.startsWith("application/json") || t.startsWith("text/plain");  // sendBeacon posts text/plain
  return t.startsWith("application/x-www-form-urlencoded") || t.startsWith("multipart/form-data");
}

/** Two secrets compared in constant time (lengths apart). */
export function sameSecret(a: string, b: string): boolean {
  const x = Buffer.from(a, "utf8"), y = Buffer.from(b, "utf8");
  return x.length === y.length && x.length > 0 && timingSafeEqual(x, y);
}

// ---------------------------------------------------------------------------------------------------------------------
// the limit
// ---------------------------------------------------------------------------------------------------------------------
type Count = { ok: boolean; retryAfter: number };
const seen = new Map<string, number[]>();

/** This instance's own count: at most `limit` requests of a key in the last `windowMs`. */
export function memoryCount(key: string, limit: number, windowMs: number, now = Date.now(), store: Map<string, number[]> = seen): Count {
  if (store.size > 20_000) {
    for (const [k, v] of store) if (!v.some((t) => now - t < 86_400_000)) store.delete(k);   // never without end
  }
  const recent = (store.get(key) ?? []).filter((t) => now - t < windowMs);
  if (recent.length >= limit) {
    store.set(key, recent);
    return { ok: false, retryAfter: Math.max(1, Math.ceil((recent[0] + windowMs - now) / 1000)) };
  }
  recent.push(now);
  store.set(key, recent);
  return { ok: true, retryAfter: 0 };
}

export type RateCall = (args: { p_token: string; p_bucket: string; p_visitor: string; p_limit: number; p_window_s: number }) => Promise<{ ok?: boolean; reason?: string | null; retry_after?: number }>;
export type Limited = { ok: boolean; retryAfter: number; by: "database" | "memory" };

/** The decision, with everything it reads passed in (the tests call this). `visitor` null: one count for everybody
 * (a ceiling on the whole route, for example confirmation emails a day). */
export async function decide(o: {
  ip: string | null; bucket: string; limit: number; windowS: number; now: number; salt: string | null; token: string; call: RateCall | null; store?: Map<string, number[]>;
}): Promise<Limited> {
  const who = o.ip === null ? "everybody" : o.ip;
  const mem = memoryCount(`${o.bucket}\n${who}`, o.limit, o.windowS * 1000, o.now, o.store);
  if (!mem.ok) return { ok: false, retryAfter: mem.retryAfter, by: "memory" };
  if (!o.call || !o.salt || o.token.length < 24 || who === "unknown") return { ok: true, retryAfter: 0, by: "memory" };
  try {
    const r = await o.call({ p_token: o.token, p_bucket: o.bucket, p_visitor: visitorKey(who, utcDay(o.now), o.salt), p_limit: o.limit, p_window_s: o.windowS });
    if (r && r.ok === true) return { ok: true, retryAfter: 0, by: "database" };
    if (r && r.ok === false && r.reason === "limit") return { ok: false, retryAfter: Math.max(1, Number(r.retry_after) || o.windowS), by: "database" };
    return { ok: true, retryAfter: 0, by: "memory" };     // an answer that is neither: the memory's count stands
  } catch {
    return { ok: true, retryAfter: 0, by: "memory" };     // the database could not be asked: the floor the routes had
  }
}

/** One request against one limit. `everybody: true` counts all visitors together. */
export async function limited(req: Request, bucket: string, limit: number, windowS: number, opts: { everybody?: boolean } = {}): Promise<Limited> {
  const { rpc } = await import("@/lib/supabase");
  return decide({
    ip: opts.everybody ? null : clientIp(req), bucket, limit, windowS, now: Date.now(), salt: readSalt(), token: process.env.INTERNAL_COSTS_TOKEN ?? "",
    call: (a) => rpc("site_rate_admit", a as unknown as Record<string, string>),
  });
}

/** The visitor of a usage count, as the server sends it to the database: HMAC-SHA256 of the address and the user agent
 * under the server's secret, 64 hexadecimal characters. The database hashes it again under a salt it draws at random
 * each day and deletes when the day is over (migration 028); neither the address nor the user agent leaves this server. */
export function usageVisitor(ip: string, ua: string, secret: string): string {
  return createHmac("sha256", secret).update(`erw-usage\n${ip}\n${ua}`).digest("hex");
}
