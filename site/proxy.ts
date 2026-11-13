// Session 67: the release gate's curtain (lib/release.ts, docs/release-gate.md). A visitor who asks for a page in
// review is shown the short in-review page at the same address; a browser holding the internal cookie
// (/internal/unlock) sees every page. The API routes, the internal routes and static files never come here.
//
// Session 5101 (docs/reviews/security-faults-2026-11-13.md, row 1): the App Router's transport addresses come here too.
// The host serves a page as data as well, at <page>.rsc and at <page>.segments/<segment>.segment.rsc (Vercel does;
// `next start` answers 404 there). The matcher below left every address with an extension alone, so the curtain never
// saw the second form: on 13 November 2026 /about.segments/about/__PAGE__.segment.rsc answered a visitor with the
// whole page while /about was in review. The matcher now runs on an address that ends in .rsc, and such an address
// takes the status of the page it stands for: without the internal cookie it answers 404. A browser never asks for
// these by path: its own prefetch names the page (and says what it wants in a header), and is shown the in-review
// page as before.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE, cookieOpens, exempt, statusOf } from "@/lib/release";

const SEGMENTS = ".segments/";

/** The pages a transport address may stand for, and [] for any other path. Every reading is returned (Next reads
 * "<page>.segments/<segment>.segment.rsc" greedily, a host may read it otherwise): the address is as closed as the
 * most closed of them. "/index" is the home page's name in these addresses. */
export function pagesOf(path: string): string[] {
  const p = path.replace(/\/+$/, "");
  const low = p.toLowerCase();
  const out: string[] = [];
  const page = (s: string) => {
    const q = s.replace(/\/index$/i, "");
    out.push(q === "" ? "/" : q);
  };
  // the proxy may be handed the address with its last ".rsc" already taken off (Next's own adapter does that)
  if (low.endsWith(".segment.rsc") || low.endsWith(".segment")) {
    for (let i = low.indexOf(SEGMENTS); i >= 0; i = low.indexOf(SEGMENTS, i + 1)) page(p.slice(0, i));
  }
  if (low.endsWith(".rsc")) page(p.slice(0, -4));
  return out;
}

/** What a browser without the internal cookie is answered at a path: the page itself ("open"), the in-review page at
 * the same address ("curtain"), or 404 ("closed": a transport address of a page in review). */
export type Gets = "open" | "curtain" | "closed";
export function visitorGets(path: string): Gets {
  let plain = path;
  try { plain = decodeURIComponent(path); } catch { /* a malformed escape stays as it is */ }
  const pages = pagesOf(plain);
  if (pages.length > 0) return pages.every((p) => statusOf(p) === "live") ? "open" : "closed";
  return exempt(path) || statusOf(path) === "live" ? "open" : "curtain";
}

export async function proxy(req: NextRequest) {
  const path = req.nextUrl.pathname;
  const gets = visitorGets(path);
  if (gets === "open") return NextResponse.next();
  const token = process.env.INTERNAL_COSTS_TOKEN;
  const have = req.cookies.get(COOKIE)?.value;
  if (await cookieOpens(have, token)) return NextResponse.next();   // session 371: constant time (docs/security.md, S1)
  if (gets === "closed") {
    return new NextResponse("Not found", { status: 404, headers: { "X-Robots-Tag": "noindex", "Cache-Control": "private, no-store" } });
  }
  const url = req.nextUrl.clone();
  url.pathname = "/in-review";
  url.search = `?path=${encodeURIComponent(path)}`;
  const res = NextResponse.rewrite(url);
  res.headers.set("X-Robots-Tag", "noindex");
  res.headers.set("Cache-Control", "private, no-store");
  return res;
}

// An address with a file extension is left alone (a CSV route applies its page's status itself), unless the
// extension is .rsc in any case: those are the transport addresses above.
export const config = {
  matcher: ["/((?!api/|internal/|_next/|in-review$|(?!.*\\.[rR][sS][cC]$).*\\.[a-zA-Z0-9]+$).*)"],
};
