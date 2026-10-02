// Session 67: the internal view of the release gate (lib/release.ts). /internal/unlock?token=<INTERNAL_COSTS_TOKEN>
// sets two 90-day cookies and goes to the home page: an httpOnly one holding a digest of the token, which the proxy
// checks, and a readable one that only tells the menu to draw itself as the internal view. A wrong or missing token,
// or a server without the token, answers 404, as /internal/costs does.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE, MAX_AGE, VIEW, digest } from "@/lib/release";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const token = process.env.INTERNAL_COSTS_TOKEN;
  const given = req.nextUrl.searchParams.get("token");
  if (!token || !given || given !== token) return new NextResponse("Not found", { status: 404, headers: { "X-Robots-Tag": "noindex" } });
  const res = NextResponse.redirect(new URL("/", req.url), 303);
  const secure = req.nextUrl.protocol === "https:";
  res.cookies.set(COOKIE, await digest(token), { httpOnly: true, secure, sameSite: "lax", path: "/", maxAge: MAX_AGE });
  res.cookies.set(VIEW, "internal", { httpOnly: false, secure, sameSite: "lax", path: "/", maxAge: MAX_AGE });
  res.headers.set("X-Robots-Tag", "noindex");
  res.headers.set("Cache-Control", "private, no-store");
  res.headers.set("Referrer-Policy", "no-referrer");
  return res;
}
