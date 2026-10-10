// Energy Research Warehouse (ERW) site, session 181: the scanner's approved drafts, for /analysis.
//   GET /internal/findings/approved     answers { drafts: [{ id, flag_date, approved_at, card }] }
// Only a browser in the internal view is answered (the cookie /internal/open sets); anything else gets 404 with an
// empty body, as /api/analysis does. The list holds approved drafts and nothing else: a draft not yet ruled on, a
// dismissed one and one waiting for a full card are never in it (scanner_drafts_list with the state, migration 029).
// Never cached, never indexed. When the list cannot be read (the migration is not applied) it answers no draft and says why.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE } from "@/lib/release";
import { listDrafts } from "@/lib/scanner";
import { internalOk } from "@/lib/thesis/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } as const;

export async function GET(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return new NextResponse(null, { status: 404, headers: NO_STORE });
  try {
    const drafts = (await listDrafts("approved")).map((d) => ({ id: d.id, flag_date: d.flag_date, approved_at: (d.state_at ?? d.raised_at).slice(0, 10), card: d.card }));
    return NextResponse.json({ drafts }, { headers: NO_STORE });
  } catch (e) {
    return NextResponse.json({ drafts: [], reason: (e as Error).message.slice(0, 120) }, { status: 502, headers: NO_STORE });
  }
}
