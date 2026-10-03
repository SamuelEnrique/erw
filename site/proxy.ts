// Session 67: the release gate's curtain (lib/release.ts, docs/release-gate.md). A visitor who asks for a page in
// review is shown the short in-review page at the same address; a browser holding the internal cookie
// (/internal/unlock) sees every page. The API routes, the internal routes and static files never come here.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE, digest, exempt, statusOf } from "@/lib/release";

export async function proxy(req: NextRequest) {
  const path = req.nextUrl.pathname;
  if (exempt(path) || statusOf(path) === "live") return NextResponse.next();
  const token = process.env.INTERNAL_COSTS_TOKEN;
  const have = req.cookies.get(COOKIE)?.value;
  if (token && have && have === (await digest(token))) return NextResponse.next();
  const url = req.nextUrl.clone();
  url.pathname = "/in-review";
  url.search = `?path=${encodeURIComponent(path)}`;
  const res = NextResponse.rewrite(url);
  res.headers.set("X-Robots-Tag", "noindex");
  res.headers.set("Cache-Control", "private, no-store");
  return res;
}

export const config = {
  matcher: ["/((?!api/|internal/|_next/|in-review$|.*\\.[a-zA-Z0-9]+$).*)"],
};
