// Energy Research Warehouse (ERW) site: one file of a finding of the hunt of 20 October 2026 (docs/findings/<day>/<slug>/).
//   GET /internal/findings/local?day=<YYYY-MM-DD>&slug=<slug>&name=<file>          the file, as a download
//   GET /internal/findings/local?day=<YYYY-MM-DD>&slug=<slug>&name=<file>&show=1   a picture shown in the page (pictures only)
// The files are what warehouse/analysis/findings/hunt_oct20.py wrote with the finding: extract.csv (the exact rows the
// headline comes from), series.csv, check.do (the Stata do-file), caption.md, the two charts and finding.json. They
// are read from content/findings/, which scripts/build-content.mjs copies from the repository at build (next.config.ts
// traces the folder for this route); nothing is read from a database and nothing is written. Only a browser in the
// internal view is answered (the cookie /internal/open sets); anything else gets 404 with an empty body, as the other
// routes of this folder do. A name outside the seven files, or a day or slug that is not a plain name, is 404. Never
// cached, never indexed.
import fs from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE } from "@/lib/release";
import { internalOk } from "@/lib/thesis/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex", "X-Content-Type-Options": "nosniff" } as const;
const hidden = (status = 404) => new NextResponse(null, { status, headers: NO_STORE });
const DAY = /^\d{4}-\d{2}-\d{2}$/;
const SLUG = /^[a-z0-9][a-z0-9_-]{2,80}$/;
const FILES: Record<string, string> = {
  "extract.csv": "text/csv; charset=utf-8", "series.csv": "text/csv; charset=utf-8", "check.do": "text/plain; charset=utf-8",
  "caption.md": "text/markdown; charset=utf-8", "finding.json": "application/json; charset=utf-8", "chart_square.png": "image/png", "chart_wide.png": "image/png",
};

export async function GET(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  const q = req.nextUrl.searchParams;
  const day = q.get("day") ?? "";
  const slug = q.get("slug") ?? "";
  const name = q.get("name") ?? "";
  const type = FILES[name];
  if (!DAY.test(day) || !SLUG.test(slug) || !type) return hidden();
  const file = path.join(process.cwd(), "content", "findings", day, slug, name);
  try {
    const body = await fs.readFile(file);
    const png = type === "image/png";
    const show = png && q.get("show") === "1";
    return new NextResponse(new Uint8Array(body), { status: 200, headers: { ...NO_STORE, "Content-Type": type, "Content-Disposition": `${show ? "inline" : "attachment"}; filename="${slug}-${name}"` } });
  } catch {
    return hidden();
  }
}
