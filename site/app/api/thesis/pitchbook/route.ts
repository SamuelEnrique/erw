// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis).
//   POST /api/thesis/pitchbook   { run_id, key, payload }   the PitchBook stage's answer for one run, accepted once
// No cookie: the run's one-time key is the credential (43 characters of randomness, erased when used; migration 024).
// The payload is checked strictly and labeled before anything is stored (lib/thesis/pitchbook.ts); the database
// function checks the key, the size and the outer shape again. 400 with a plain reason on any violation of the format,
// 403 when the key is wrong or already used, 413 over 400 KB. The body may also be the payload itself carrying "key".
import { NextResponse } from "next/server";
import { MAX_BODY, readSubmission, validatePitchbook } from "@/lib/thesis/pitchbook";
import { NO_STORE, acceptPitchbook } from "@/lib/thesis/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const no = (reason: string, status: number) => NextResponse.json({ ok: false, reason }, { status, headers: NO_STORE });
const WRONG_KEY = "The key is wrong or was already used.";

/** The body as text, read no further than the limit; null when it is larger. */
async function bodyText(req: Request): Promise<string | null> {
  if (Number(req.headers.get("content-length") ?? 0) > MAX_BODY) return null;
  if (!req.body) return "";
  const reader = req.body.getReader();
  const parts: Uint8Array[] = [];
  let size = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > MAX_BODY) {
      await reader.cancel();
      return null;
    }
    parts.push(value);
  }
  const all = new Uint8Array(size);
  let at = 0;
  for (const p of parts) { all.set(p, at); at += p.byteLength; }
  return new TextDecoder().decode(all);
}

export async function POST(req: Request) {
  let raw: string | null;
  try {
    raw = await bodyText(req);
  } catch {
    return no("The request could not be read.", 400);
  }
  if (raw === null) return no("The answer is larger than 400 KB.", 413);
  let body: unknown;
  try {
    body = JSON.parse(raw);
  } catch {
    return no("Send JSON: { run_id, key, payload }.", 400);
  }
  const sub = readSubmission(body);
  if (!sub.ok) return no(sub.reason, 400);
  const checked = validatePitchbook(sub.payload, sub.run_id);
  if (!checked.ok) return no(checked.reason, 400);
  // a key shorter than any the database writes is wrong: the function would answer the same
  if (sub.key.length < 32) return no(WRONG_KEY, 403);
  try {
    const r = await acceptPitchbook(sub.run_id, sub.key, checked.payload);
    if (r && r.ok) return NextResponse.json({ ok: true, companies: checked.payload.companies.length }, { headers: NO_STORE });
    if (r && r.reason === "key") return no(WRONG_KEY, 403);
    return no("The answer is too large, or not in the shape the run expects.", 400);
  } catch (e) {
    console.error(`[erw] thesis/pitchbook: ${(e as Error).message}`);
    return no("The answer could not be stored.", 502);
  }
}
