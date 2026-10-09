// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis).
//   POST /api/thesis/run   { niche, stage?, geography?, run_anyway? }   queues a run; answers { ok, run_id } or { ok: false, reason }
//   GET  /api/thesis/run?id=<run_id>                        answers { status, note } of one run, and nothing else of it
// /api/* is not behind the release gate, so this route protects itself: it answers only a browser in the internal view
// (the cookie /internal/unlock sets, as the proxy checks it). Anything else gets 404 with an empty body, as if the
// route were not there. The database function counts the day's runs and dispatches the workflow (migration 024).
//
// Session 169, the gate on the niche (lib/thesis/niche.ts, the same module the form reads): a sector or a market
// topic is refused here before the database is asked, with three to five narrower niches:
//   422 { ok: false, refused: true, reason: <the refusal's sentence>, suggestions: [...] }
// { run_anyway: true } starts the run all the same; what the gate read is then stored with the run (thesis_runs.gate,
// migration 026) and its report is flagged. Until that migration is applied a forced run cannot be stored, and is
// answered in plain words instead of being queued without its flag.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE } from "@/lib/release";
import { forcedOf, judge } from "@/lib/thesis/niche";
import { gateModel } from "@/lib/thesis/nicheModel";
import { NO_STORE, getRun, internalOk, submitForced, submitRun } from "@/lib/thesis/server";
import { RUN_ID } from "@/lib/thesis/view";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const hidden = () => new NextResponse(null, { status: 404, headers: NO_STORE });
const json = (body: unknown, status = 200) => NextResponse.json(body, { status, headers: NO_STORE });
const REASON: Record<string, string> = { day: "Today's runs are used up.", input: "Describe the niche in a sentence." };
const field = (v: unknown) => (typeof v === "string" ? v.replace(/\s+/g, " ").trim() : "");

export async function POST(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  let body: { niche?: unknown; stage?: unknown; geography?: unknown; run_anyway?: unknown };
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
  // session 169: the gate. A ticked "Run anyway" asks nothing of the model: the rules alone say whether the run is a
  // forced one (an input they pass is an ordinary run, whatever the box says).
  const forced = body.run_anyway === true ? forcedOf(niche) : null;
  if (body.run_anyway !== true) {
    const d = await judge(niche, gateModel());
    if (!d.ok) return json({ ok: false, refused: true, reason: d.message, suggestions: d.suggestions }, 422);
  }
  try {
    const r = forced ? await submitForced(niche, stage, geography, forced) : await submitRun(niche, stage, geography);
    if (r && r.ok && typeof r.run_id === "string") return json({ ok: true, run_id: r.run_id });
    const why = r && !r.ok ? r.reason : "";
    return json({ ok: false, reason: REASON[why] ?? "The run could not be queued." }, why === "day" ? 429 : 400);
  } catch (e) {
    console.error(`[erw] thesis/run: ${(e as Error).message}`);
    // a database that does not hold migration 026 yet has no place for the flag: the run is not queued without it
    if (forced && /thesis_submit_forced: HTTP 404/.test((e as Error).message)) return json({ ok: false, reason: "Run anyway is not switched on yet. Pick a narrower niche." }, 503);
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
