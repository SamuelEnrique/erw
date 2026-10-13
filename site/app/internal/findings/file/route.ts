// Energy Research Warehouse (ERW) site, session 233: one file of a draft of the weekly hunt.
//   GET /internal/findings/file?id=<draft>&name=<file>          the file, as a download
//   GET /internal/findings/file?id=<draft>&name=<file>&show=1   a picture shown in the page (pictures only)
// The files are what warehouse/analysis/findings/hunt.py prepared with the draft: the CSV, the Stata do-file, the
// Python mirror, the two LinkedIn pictures (1200 x 627 and 1080 x 1080) and the caption. Only a browser in the internal
// view is answered (the cookie /internal/open sets); anything else gets 404 with an empty body, as the other routes
// of this folder do. The database function checks the internal token again (scanner_draft_file, migration 031) and
// reads; nothing here writes, and nothing here posts a file anywhere. A file's name begins with its draft's id, so one
// draft's address cannot ask for another's file. Never cached, never indexed.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE } from "@/lib/release";
import { FILE_NAME, ID, draftFile } from "@/lib/scanner";
import { internalOk } from "@/lib/thesis/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex", "X-Content-Type-Options": "nosniff" } as const;
const hidden = (status = 404) => new NextResponse(null, { status, headers: NO_STORE });
const TYPES: [RegExp, string][] = [[/\.csv$/, "text/csv; charset=utf-8"], [/\.png$/, "image/png"], [/\.(do|py|txt)$/, "text/plain; charset=utf-8"]];

export async function GET(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  const id = req.nextUrl.searchParams.get("id") ?? "";
  const name = req.nextUrl.searchParams.get("name") ?? "";
  const type = TYPES.find(([re]) => re.test(name))?.[1];
  if (!ID.test(id) || !FILE_NAME.test(name) || !name.startsWith(id) || !type) return hidden();
  try {
    const f = await draftFile(id, name);
    if (!f || !f.content || (f.kind !== "text" && f.kind !== "png")) return hidden();
    const png = f.kind === "png";
    if (png !== (type === "image/png")) return hidden();
    const show = png && req.nextUrl.searchParams.get("show") === "1";
    const body = png ? new Uint8Array(Buffer.from(f.content, "base64")) : f.content;
    return new NextResponse(body, { status: 200, headers: { ...NO_STORE, "Content-Type": type, "Content-Disposition": `${show ? "inline" : "attachment"}; filename="${name}"` } });
  } catch {
    return hidden(502);
  }
}
