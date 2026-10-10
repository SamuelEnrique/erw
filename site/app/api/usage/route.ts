// Energy Research Warehouse (ERW) site, session 177: POST /api/usage, the usage counts (docs/methods/usage_counts.md).
// Body: {"event": "tool opened" | "input changed" | "scenario compared" | "download", "path": "/a/page"}.
//
// What is recorded (the database function site_usage_record, migration 028): the path (no query), the tool's name (from
// the menu's list, lib/usagepath.ts), the event, the UTC day, and a hash that stands for the visitor today and for
// nobody tomorrow. What is never recorded, here or in a log: the address, the user agent, a referrer, a query string, a
// cookie, an identifier kept in the browser.
//
// The hash. This server makes HMAC-SHA256 of the address and the user agent under a secret only it holds
// (ASK_VISITOR_SALT) and sends that; the database hashes it again under a salt it draws at random each UTC day, and
// when the day is over it keeps the day's counts and deletes that day's hashes and its salt. A visitor cannot be
// followed from one day to the next: the two days' hashes share nothing, and yesterday's salt no longer exists.
//
// Nothing is recorded, and the answer is the same 204, when: the browser asks not to be tracked (DNT: 1 or Sec-GPC: 1;
// the page's own script sends nothing in that case), the request is another site's or a stock script's, the path is not
// a page of this site, the server holds no secret, or the migration is not applied. The route sets no cookie.
import { COOKIE, statusOf } from "@/lib/release";
import { clientIp, limited, sameOrigin, scripted, typed, usageVisitor } from "@/lib/guard";
import { readSalt } from "@/lib/chat/limits";
import { rpc } from "@/lib/supabase";
import { internalOk } from "@/lib/thesis/server";
import { IN_REVIEW, cleanPath, isEvent, toolOf } from "@/lib/usagepath";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const done = () => new Response(null, { status: 204, headers: { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } });

function cookieOf(req: Request, name: string): string | undefined {
  for (const part of (req.headers.get("cookie") ?? "").split(";")) {
    const i = part.indexOf("=");
    if (i > 0 && part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return undefined;
}

export async function POST(req: Request) {
  if (req.headers.get("dnt") === "1" || req.headers.get("sec-gpc") === "1") return done();
  if (!sameOrigin(req) || scripted(req) || !typed(req, "json")) return done();
  let body: { event?: unknown; path?: unknown };
  try {
    const raw = await req.text();
    if (raw.length > 600) return done();
    body = JSON.parse(raw);
  } catch {
    return done();
  }
  if (typeof body !== "object" || body === null || !isEvent(body.event)) return done();
  const path = cleanPath(body.path);
  const secret = readSalt(), token = process.env.INTERNAL_COSTS_TOKEN ?? "", ip = clientIp(req);
  if (!path || !secret || token.length < 24 || ip === "unknown") return done();
  if (!(await limited(req, "usage", 600, 3600)).ok) return done();
  // a visitor who asked for a page in review was shown the in-review page: the count says so, under the page's path
  const opened = statusOf(path) === "live" || (await internalOk(cookieOf(req, COOKIE)));
  try {
    await rpc("site_usage_record", { p_token: token, p_path: path, p_tool: opened ? toolOf(path) : IN_REVIEW, p_event: body.event, p_visitor: usageVisitor(ip, req.headers.get("user-agent") ?? "", secret) });
  } catch {
    /* the migration is not applied, or the database did not answer: nothing is recorded, and nothing is logged */
  }
  return done();
}
