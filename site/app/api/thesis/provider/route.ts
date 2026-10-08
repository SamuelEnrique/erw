// Energy Research Warehouse (ERW) site, session 150: Thesis Builder (/thesis).
//   POST /api/thesis/provider   { run_id, provider, pasted }   a data provider's answer for one finished run
// `pasted` is the text a person pasted on /thesis, whole: the route finds the JSON in it, checks it against the format
// of the provider chosen (lib/thesis/providers.ts) and stores what the reader writes out, with the time and the
// SHA-256 of the pasted text, once a run and provider (migration 025).
//   harmonic, crunchbase   the answer is stored here.
//   pitchbook              nothing of the answer is stored here: it goes, as since session 135, to
//                          POST /api/thesis/pitchbook under the run's one-time key. This route then records only the
//                          time and the hash of the text it was read from, and only when the run already holds
//                          exactly the answer that text reads as.
// /api/* is not behind the release gate, so the route protects itself: it answers only a browser in the internal view
// (the cookie /internal/unlock sets). Anything else gets 404 with an empty body, as if the route were not there.
// 400 with a plain reason on any fault of the format (a format of another provider is named), 409 when the run
// already holds this provider's answer, 413 over 400 KB. No provider, connector or model is called from here.
import { createHash } from "node:crypto";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { COOKIE } from "@/lib/release";
import { MAX_BODY } from "@/lib/thesis/pitchbook";
import { PROVIDERS, checkPaste, isProviderId, sameJson, type ProviderPayload } from "@/lib/thesis/providers";
import { NO_STORE, acceptProvider, getRun, internalOk } from "@/lib/thesis/server";
import { RUN_ID } from "@/lib/thesis/view";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const hidden = () => new NextResponse(null, { status: 404, headers: NO_STORE });
const no = (reason: string, status: number) => NextResponse.json({ ok: false, reason }, { status, headers: NO_STORE });

export async function POST(req: NextRequest) {
  if (!(await internalOk(req.cookies.get(COOKIE)?.value))) return hidden();
  if (Number(req.headers.get("content-length") ?? 0) > MAX_BODY + 2000) return no("The answer is larger than 400 KB.", 413);
  let body: { run_id?: unknown; provider?: unknown; pasted?: unknown };
  try {
    const raw = await req.text();
    if (raw.length > MAX_BODY + 2000) return no("The answer is larger than 400 KB.", 413);
    body = JSON.parse(raw);
  } catch {
    return no("Send JSON: { run_id, provider, pasted }.", 400);
  }
  if (typeof body !== "object" || body === null || Array.isArray(body)) return no("Send JSON: { run_id, provider, pasted }.", 400);
  const extra = Object.keys(body).find((k) => !["run_id", "provider", "pasted"].includes(k));
  if (extra) return no(`The request holds a key it does not have: "${extra.slice(0, 40)}".`, 400);
  if (typeof body.run_id !== "string" || !RUN_ID.test(body.run_id)) return no("The run this answer is for is not named.", 400);
  if (!isProviderId(body.provider)) return no("The provider is not one of PitchBook, Harmonic and Crunchbase.", 400);
  if (typeof body.pasted !== "string" || !body.pasted.trim()) return no("Nothing was pasted.", 400);
  if (Buffer.byteLength(body.pasted, "utf8") > MAX_BODY) return no("The answer is larger than 400 KB.", 413);
  const runId = body.run_id, provider = PROVIDERS[body.provider];

  const read = checkPaste(provider.id, body.pasted, runId);
  if (!read.ok) return no(read.reason, 400);
  const sha256 = createHash("sha256").update(body.pasted, "utf8").digest("hex");
  try {
    if (provider.id === "pitchbook") {
      // the stamp of an answer the run already holds: the pasted text must read as exactly that answer
      const run = await getRun(runId);
      if (!run || !run.pitchbook || !sameJson(run.pitchbook, read.payload)) return no("This run does not hold the PitchBook answer this text reads as.", 409);
    }
    const r = await acceptProvider(runId, provider.id, provider.format, sha256, provider.id === "pitchbook" ? null : (read.payload as ProviderPayload));
    if (r && r.ok) return NextResponse.json({ ok: true, provider: provider.id, companies: read.payload.companies.length, sha256 }, { headers: NO_STORE });
    if (r && r.reason === "held") return no(`This run already holds ${provider.label}'s answer.`, 409);
    if (r && r.reason === "run") return no("No finished run is held under this address.", 404);
    return no("The answer is too large, or not in the shape the run expects.", 400);
  } catch (e) {
    console.error(`[erw] thesis/provider: ${(e as Error).message}`);
    return no("The answer could not be stored.", 502);
  }
}
