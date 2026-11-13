// Session 67: the internal view of the release gate (lib/release.ts). Opening it sets two 90-day cookies and goes to
// the home page: an httpOnly one holding a digest of the token, which the proxy checks, and a readable one that only
// tells the menu to draw itself as the internal view. From session 67 to session 5157 a link did that, with the token
// in its address; since session 177 the form at /internal/open does it, with the token in the request's body.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE, MAX_AGE, VIEW, digest } from "@/lib/release";

export const dynamic = "force-dynamic";

// Session 5157 (docs/security.md, H1 and L5; docs/reviews/security-faults-2026-11-13.md, rows 3 and 4): the old link is
// retired. A GET opens nothing and sets no cookie, whatever its address carries: the answer is the 404 a wrong token
// always got, so the address reads as if the route were not there. The token is not read from the address at all, so
// nothing is compared. The one door is the form at /internal/open, which posts the token in the request's body (below).
export async function GET() {
  return new NextResponse("Not found", { status: 404, headers: { "X-Robots-Tag": "noindex", "Cache-Control": "private, no-store", "Referrer-Policy": "no-referrer" } });
}

// Session 177: the same door without the token in any address (docs/release-gate.md). POST /internal/unlock with the
// token in the request's body (the form at /internal/open) sets the two cookies and goes to the home page. It is the
// one door since session 5157 retired the link.
//   a right token            always opens, whatever was tried before: the limit below never keeps the owner out
//   a wrong or missing one   goes back to the form (state "no"); ten wrong tries an hour from one address, then "wait"
//   another site's form      404, as if the route were not there
// Nothing of the token is logged, put in an address or sent back.
export async function POST(req: NextRequest) {
  const { limited, sameOrigin, sameSecret } = await import("@/lib/guard");
  const hide = { "X-Robots-Tag": "noindex", "Cache-Control": "private, no-store", "Referrer-Policy": "no-referrer" };
  const token = process.env.INTERNAL_COSTS_TOKEN;
  if (!token || !sameOrigin(req)) return new NextResponse("Not found", { status: 404, headers: hide });
  const back = (state: string) => {
    const r = NextResponse.redirect(new URL(`/internal/open?state=${state}`, req.url), 303);
    for (const [k, v] of Object.entries(hide)) r.headers.set(k, v);
    return r;
  };
  let given = "", trap = "";
  try {
    const raw = await req.text();
    if (raw.length > 2000) return back("no");
    const form = new URLSearchParams(raw);
    given = (form.get("token") ?? "").trim();
    trap = form.get("website") ?? "";
  } catch {
    return back("no");
  }
  if (trap !== "" || !sameSecret(given, token)) {
    return back((await limited(req, "unlock", 10, 3600)).ok ? "no" : "wait");
  }
  const res = NextResponse.redirect(new URL("/", req.url), 303);
  const secure = req.nextUrl.protocol === "https:";
  res.cookies.set(COOKIE, await digest(token), { httpOnly: true, secure, sameSite: "lax", path: "/", maxAge: MAX_AGE });
  res.cookies.set(VIEW, "internal", { httpOnly: false, secure, sameSite: "lax", path: "/", maxAge: MAX_AGE });
  for (const [k, v] of Object.entries(hide)) res.headers.set(k, v);
  return res;
}
