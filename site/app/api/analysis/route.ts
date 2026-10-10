// Energy Research Warehouse (ERW) site, session 170: the findings' queue.
//   POST /api/analysis  { kind: "run", finding, params }     queues a finding with chosen inputs; answers { ok, id }
//   POST /api/analysis  { kind: "roundup", card_id }         chooses a card for this week's Roundup; answers { ok, week }
//   GET  /api/analysis                                       the queue: the latest requests with their state
//   GET  /api/analysis?id=<request>                          one request with its card, once the worker has written it
// /api/* is not behind the release gate, so this route protects itself as the thesis route does: it answers only a
// browser in the internal view (the cookie /internal/unlock sets); anything else gets 404 with an empty body. The
// database function (migration 027) checks the internal token again, counts the day's requests and writes the row;
// the data machine's worker (warehouse/analysis/findings/worker.py) takes queued rows when it is awake.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE } from "@/lib/release";
import { rpc } from "@/lib/supabase";
import { internalOk } from "@/lib/thesis/server";
import { loadCatalogue, roundupWeek } from "@/lib/findings";
import { sameOrigin } from "@/lib/guard";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } as const;
const hidden = () => new NextResponse(null, { status: 404, headers: NO_STORE });
const json = (body: unknown, status = 200) => NextResponse.json(body, { status, headers: NO_STORE });
const token = () => process.env.INTERNAL_COSTS_TOKEN ?? "";

export async function POST(req: NextRequest) {
  if (!sameOrigin(req)) return hidden();   // session 177: never from another site's page, whatever cookie comes with it
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  let body: { kind?: unknown; finding?: unknown; params?: unknown; card_id?: unknown };
  try {
    const raw = await req.text();
    if (raw.length > 2000) return json({ ok: false, reason: "too long" }, 400);
    body = JSON.parse(raw);
  } catch {
    return json({ ok: false, reason: "send JSON" }, 400);
  }
  if (typeof body !== "object" || body === null) return json({ ok: false, reason: "send JSON" }, 400);
  const catalogue = loadCatalogue();
  if (body.kind === "roundup") {
    const cardId = typeof body.card_id === "string" ? body.card_id : "";
    if (!/^[a-z0-9_.-]{3,120}$/i.test(cardId)) return json({ ok: false, reason: "no such card" }, 400);
    const week = roundupWeek();
    try {
      const r = await rpc<{ ok: boolean; reason?: string }>("analysis_request", { p_token: token(), p_kind: "roundup", p_finding: cardId.split("__")[0], p_params: JSON.stringify({ card_id: cardId, week }) });
      return r && r.ok ? json({ ok: true, week }) : json({ ok: false, reason: r?.reason ?? "not chosen" }, 400);
    } catch (e) {
      return json({ ok: false, reason: `the queue could not be written: ${(e as Error).message.slice(0, 120)}` }, 502);
    }
  }
  if (body.kind !== "run") return json({ ok: false, reason: "kind is run or roundup" }, 400);
  const entry = catalogue.find((c) => c.id === body.finding);
  if (!entry) return json({ ok: false, reason: "no such finding" }, 400);
  const given = (typeof body.params === "object" && body.params !== null ? body.params : {}) as Record<string, unknown>;
  const params: Record<string, string> = {};
  for (const [k, inp] of Object.entries(entry.inputs)) {
    const v = k in given ? String(given[k]) : String(inp.default);
    if (!inp.choices.map(String).includes(v)) return json({ ok: false, reason: `${inp.label}: not a choice` }, 400);
    params[k] = v;
  }
  try {
    const r = await rpc<{ ok: boolean; reason?: string; id?: string }>("analysis_request", { p_token: token(), p_kind: "run", p_finding: entry.id, p_params: JSON.stringify(params) });
    return r && r.ok ? json({ ok: true, id: r.id }) : json({ ok: false, reason: r?.reason === "day" ? "Today's requests are used up." : (r?.reason ?? "not queued") }, r?.reason === "day" ? 429 : 400);
  } catch (e) {
    return json({ ok: false, reason: `the queue could not be written: ${(e as Error).message.slice(0, 120)}` }, 502);
  }
}

export async function GET(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  // session 181: ?id=<request> answers that one request with its card (analysis_request_card, migration 029), so a
  // card asked for here can be read here; the deployed site holds no file of it
  const id = req.nextUrl.searchParams.get("id");
  if (id !== null) {
    if (!/^[A-Za-z0-9-]{6,60}$/.test(id)) return json({ request: null, reason: "no such request" }, 400);
    try {
      const row = await rpc<unknown | null>("analysis_request_card", { p_token: token(), p_id: id });
      return row ? json({ request: row }) : json({ request: null, reason: "no such request" }, 404);
    } catch (e) {
      return json({ request: null, reason: (e as Error).message.slice(0, 120) }, 502);
    }
  }
  try {
    const rows = await rpc<unknown[] | null>("analysis_requests_list", { p_token: token() });
    return json({ requests: rows ?? [] });
  } catch (e) {
    return json({ requests: [], reason: (e as Error).message.slice(0, 120) }, 502);
  }
}
