// Session 67: /internal/lock clears the internal view's cookies (lib/release.ts): the browser is a visitor again.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE, VIEW } from "@/lib/release";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const res = NextResponse.redirect(new URL("/", req.url), 303);
  res.cookies.set(COOKIE, "", { httpOnly: true, path: "/", maxAge: 0 });
  res.cookies.set(VIEW, "", { path: "/", maxAge: 0 });
  res.headers.set("X-Robots-Tag", "noindex");
  res.headers.set("Cache-Control", "private, no-store");
  return res;
}
