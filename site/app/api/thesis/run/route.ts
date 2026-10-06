// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis).
//   POST /api/thesis/run   { niche, stage?, geography? }   queues a run; answers { ok, run_id } or { ok: false, reason }
//   GET  /api/thesis/run?id=<run_id>                        answers { status, note } of one run, and nothing else of it
// /api/* is not behind the release gate, so this route protects itself: it answers only a browser in the internal view
// (the cookie /internal/unlock sets, as the proxy checks it). Anything else gets 404 with an empty body, as if the
// route were not there. The database function counts the day's runs and dispatches the workflow (migration 024).
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE } from "@/lib/release";
import { NO_STORE, getRun, internalOk, submitRun } from "@/lib/thesis/server";
import { RUN_ID } from "@/lib/thesis/view";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const hidden = () => new NextResponse(null, { status: 404, headers: NO_STORE });
const json = (body: unknown, status = 200) => NextResponse.json(body, { status, headers: NO_STORE });
const REASON: Record<string, string> = { day: "Today's runs are used up.", input: "Describe the niche in a sentence." };
const field = (v: unknown) => (typeof v === "string" ? v.replace(/\s+/g, " ").trim() : "");

export async function POST(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  let body: { niche?: unknown; stage?: unknown; geography?: unknown };
  try {
    const raw = await req.text();
    if (raw.length > 4000) return json({ ok: false, reason: REASON.input }, 400);
    body = JSON.parse(raw);
  } catch {
    return json({ ok: false, reason: REASON.input }, 400);
  }
  if (typeof body !== "object" || body === null) return json({ ok: false, reason: REASON.input }, 400);
  const niche = field(body.niche), stage = field(body.stage), geography = field(body.geography);
  // the same limits the database function holds, so a plain slip is answered without asking it
  if (niche.length < 8 || niche.length > 400 || stage.length > 80 || geography.length > 80) return json({ ok: false, reason: REASON.input }, 400);
  try {
    const r = await submitRun(niche, stage, geography);
    if (r && r.ok && typeof r.run_id === "string") return json({ ok: true, run_id: r.run_id });
    const why = r && !r.ok ? r.reason : "";
    return json({ ok: false, reason: REASON[why] ?? "The run could not be queued." }, why === "day" ? 429 : 400);
  } catch (e) {
    console.error(`[erw] thesis/run: ${(e as Error).message}`);
    return json({ ok: false, reason: "The run could not be queued." }, 502);
  }
}

export async function GET(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  const id = req.nextUrl.searchParams.get("id") ?? "";
  if (!RUN_ID.test(id)) return json({ status: null, note: "" }, 404);
  try {
    const run = await getRun(id);
    if (!run) return json({ status: null, note: "" }, 404);
    return json({ status: run.status, note: typeof run.note === "string" ? run.note : "" });
  } catch (e) {
    console.error(`[erw] thesis/run: ${(e as Error).message}`);
    return json({ status: null, note: "The run could not be read." }, 502);
  }
}
