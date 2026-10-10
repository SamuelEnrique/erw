// Energy Research Warehouse (ERW) site, session 181: one ruling on a scanner draft.
//   POST /internal/findings/state  { id, state }     state: approved, dismissed or full_card_asked; answers { ok, state, at }
// Guarded as session 177's routes are: never from another site's page (sameOrigin), a JSON body (typed), only a
// browser in the internal view (the cookie /internal/open sets; anything else gets 404 with an empty body), a limit
// per visitor (limited), and the database function checks the internal token again (scanner_draft_set_state,
// migration 029) and keeps the change with its time. No token is read from the address.
//
// "Ask for a full card": where the scanner named an analysis for the flag (card.scanner.full_card: the impact study on
// the flagged series around the flagged date), that request is queued through the same function /analysis uses
// (analysis_request, migration 027) and its id is kept on the draft; the data machine's worker computes it. Where it
// named none, the draft is only marked: a session writes the card. Nothing here writes a sentence.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { limited, sameOrigin, typed } from "@/lib/guard";
import { COOKIE } from "@/lib/release";
import { ID, STATES, listDrafts, setDraftState, type DraftState } from "@/lib/scanner";
import { rpc } from "@/lib/supabase";
import { internalOk } from "@/lib/thesis/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } as const;
const hidden = () => new NextResponse(null, { status: 404, headers: NO_STORE });
const json = (body: unknown, status = 200, more: Record<string, string> = {}) => NextResponse.json(body, { status, headers: { ...NO_STORE, ...more } });

export async function POST(req: NextRequest) {
  if (!sameOrigin(req)) return hidden();
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  if (!typed(req, "json")) return json({ ok: false, reason: "send JSON" }, 415);
  const lim = await limited(req, "findings_state", 120, 3600);
  if (!lim.ok) return json({ ok: false, reason: "Too many rulings in an hour; wait and try again." }, 429, { "Retry-After": String(lim.retryAfter) });
  let body: { id?: unknown; state?: unknown };
  try {
    const raw = await req.text();
    if (raw.length > 500) return json({ ok: false, reason: "too long" }, 400);
    body = JSON.parse(raw);
  } catch {
    return json({ ok: false, reason: "send JSON" }, 400);
  }
  if (typeof body !== "object" || body === null) return json({ ok: false, reason: "send JSON" }, 400);
  const id = typeof body.id === "string" ? body.id : "";
  const state = body.state as DraftState;
  if (!ID.test(id)) return json({ ok: false, reason: "no such draft" }, 400);
  if (!STATES.includes(state)) return json({ ok: false, reason: "state is approved, dismissed or full_card_asked" }, 400);
  try {
    let requestId: string | undefined;
    let note = "";
    if (state === "full_card_asked") {
      const draft = (await listDrafts()).find((d) => d.id === id);
      if (!draft) return json({ ok: false, reason: "no such draft" }, 404);
      const full = draft.card.scanner?.full_card;
      if (full && !draft.request_id) {
        const params = Object.fromEntries(Object.entries(full.params).map(([k, v]) => [k, String(v)]));
        const q = await rpc<{ ok: boolean; reason?: string; id?: string }>("analysis_request", { p_token: process.env.INTERNAL_COSTS_TOKEN ?? "", p_kind: "run", p_finding: full.finding, p_params: JSON.stringify(params) });
        if (!q || !q.ok || !q.id) return json({ ok: false, reason: q?.reason === "day" ? "Today's analysis requests are used up; ask again tomorrow." : `the analysis could not be queued: ${q?.reason ?? "no answer"}` }, q?.reason === "day" ? 429 : 502);
        requestId = q.id;
        note = `the impact study is queued for the data machine (request ${q.id}); its card appears on /analysis when the worker has run`;
      } else if (draft.request_id) {
        note = `already asked (request ${draft.request_id})`;
      } else {
        note = "marked: no analysis of the engine fits this series, so a session writes the card";
      }
    }
    const r = await setDraftState(id, state, requestId);
    if (!r || !r.ok) return json({ ok: false, reason: r?.reason ?? "not changed" }, r?.reason === "no such draft" ? 404 : 400);
    return json({ ok: true, id, state: r.state, from: r.from, at: r.at, note, request_id: requestId ?? null });
  } catch (e) {
    return json({ ok: false, reason: `the review list could not be written: ${(e as Error).message.slice(0, 120)}` }, 502);
  }
}
