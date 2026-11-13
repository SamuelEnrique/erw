// Session 67: /internal/lock clears the internal view's cookies (lib/release.ts): the browser is a visitor again.
// Session 5102 (docs/reviews/security-faults-2026-11-13.md, row 15): not at another site's request. A page elsewhere
// could lock a reviewer's browser with an image whose address is this one; a request the browser itself marks
// cross-site (Sec-Fetch-Site, a header no page's script can set) now goes to the home page and clears nothing. The
// site's own link, an address typed, and a script that sends no such header lock as before.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE, VIEW } from "@/lib/release";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const res = NextResponse.redirect(new URL("/", req.url), 303);
  res.headers.set("X-Robots-Tag", "noindex");
  res.headers.set("Cache-Control", "private, no-store");
  if (req.headers.get("sec-fetch-site") === "cross-site") return res;
  res.cookies.set(COOKIE, "", { httpOnly: true, path: "/", maxAge: 0 });
  res.cookies.set(VIEW, "", { path: "/", maxAge: 0 });
  return res;
}
