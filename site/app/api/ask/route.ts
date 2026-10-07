// Energy Research Warehouse (ERW) site: POST /api/ask, read-only question answering.
//
// Runs the loop in lib/chat/ask.ts on the server, with ANTHROPIC_API_KEY from the environment
// and the Supabase anon key for data (public rows only). Nothing is written anywhere.
// Rate limit: 10 questions per IP per hour. The count is kept in this server instance's
// memory, so on a platform that runs several instances (Vercel) each keeps its own count:
// the limit is per instance, a floor rather than a guarantee.
// Session 128: the ceilings that hold whatever the instance (lib/chat/limits.ts): before a question goes to a model the
// database is asked whether the day's and the month's spend are under their ceilings and whether this visitor is under
// the day's number of questions. When it says no, or cannot be asked, the answer is a plain message and no model is
// called. Each admitted question is numbered, and every model call it makes carries the number into the cost ledger.
import { NextResponse } from "next/server";
import { ask } from "@/lib/chat/ask";
import { scopeOf } from "@/lib/chat/tools";
import { cleanContext, cleanHistory, ercotProfile } from "@/lib/chat/ercot";
import { admit, questionId, readLimits, readSalt } from "@/lib/chat/limits";
import { rpc } from "@/lib/supabase";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const LIMIT = 10;
const WINDOW_MS = 3_600_000;
const MAX_QUESTION = 500;
const seen = new Map<string, number[]>();

function clientIp(req: Request): string {
  const fwd = req.headers.get("x-forwarded-for");
  if (fwd) return fwd.split(",")[0].trim();
  return req.headers.get("x-real-ip") ?? "unknown";
}

function allow(ip: string, now: number): { ok: boolean; retryAfter: number } {
  const recent = (seen.get(ip) ?? []).filter((t) => now - t < WINDOW_MS);
  if (recent.length >= LIMIT) {
    seen.set(ip, recent);
    return { ok: false, retryAfter: Math.ceil((recent[0] + WINDOW_MS - now) / 1000) };
  }
  recent.push(now);
  seen.set(ip, recent);
  return { ok: true, retryAfter: 0 };
}

export async function POST(req: Request) {
  let question: unknown, grid: unknown, profile: unknown, context: unknown, history: unknown, stream: unknown;
  try {
    ({ question, grid, profile, context, history, stream } = (await req.json()) as { question?: unknown; grid?: unknown; profile?: unknown; context?: unknown; history?: unknown; stream?: unknown });
  } catch {
    return NextResponse.json({ error: "send JSON: {\"question\": \"...\"}" }, { status: 400 });
  }
  if (typeof question !== "string" || !question.trim()) {
    return NextResponse.json({ error: "question is required" }, { status: 400 });
  }
  // session 35: a grid page's scoped chat (/ask?grid=<slug>)
  if (grid !== undefined && grid !== null && grid !== "" && (typeof grid !== "string" || !scopeOf(grid))) {
    return NextResponse.json({ error: "unknown grid" }, { status: 400 });
  }
  // session 92: Ask ERCOT, the reference version (/ask/ercot): {profile: "ercot", context: the view the reader came from}
  if (profile !== undefined && profile !== null && profile !== "" && profile !== "ercot") {
    return NextResponse.json({ error: "unknown profile" }, { status: 400 });
  }
  if (question.length > MAX_QUESTION) {
    return NextResponse.json({ error: `a question is at most ${MAX_QUESTION} characters` }, { status: 400 });
  }
  const now = Date.now();
  const gate = allow(clientIp(req), now);
  if (!gate.ok) {
    return NextResponse.json(
      { error: `limit reached: ${LIMIT} questions per hour; try again in ${Math.ceil(gate.retryAfter / 60)} minutes` },
      { status: 429, headers: { "Retry-After": String(gate.retryAfter) } },
    );
  }
  // session 128: the spending ceilings and the visitor's daily number, counted by the database. A refusal is logged
  // with its reason and nothing about the visitor or the question.
  const limits = readLimits();
  const admitted = await admit(clientIp(req), now, limits, readSalt(), (a) => rpc("site_ask_admit", a as unknown as Record<string, string>));
  if (!admitted.ok) {
    console.log(JSON.stringify({ erw_ask: { at: new Date(now).toISOString(), status: "refused", reason: admitted.reason, why: admitted.why } }));
    return NextResponse.json({ error: admitted.message, refused: admitted.reason }, { status: admitted.status, headers: { "Cache-Control": "no-store" } });
  }
  const qid = questionId();
  const asked = question.trim();
  // session 143: the stages of an answer are counted from the request's arrival; the admission above is its first step
  const timing = { startedAt: now, before: [{ stage: "other" as const, what: "admit", ms: Date.now() - now }] };
  // session 121: the per-question line of the log also holds what the question cost and how long it took
  const logged = (r: Record<string, unknown>) => console.log(JSON.stringify({ erw_ask: { at: new Date(now).toISOString(), grid: grid || (profile === "ercot" ? "ercot (reference)" : null), question: asked,
    status: r.status ?? "answered", question_id: qid, cost_usd: r.cost_usd ?? null, seconds: r.seconds ?? null, seconds_first: r.seconds_first ?? null, tool_calls: r.tool_calls ?? null, turns_before: cleanHistory(history).length,
    seconds_words: r.seconds_words ?? null, stages_ms: r.stages_ms ?? null } }));
  // session 121, Ask ERCOT only: {stream: true} answers as lines of JSON, one per thing a reader can be shown: first
  // {"type":"reading","table":...} as each query starts, then {"type":"result",...} (the same object the plain answer
  // is) or {"type":"error","error":...}. The answer itself is never sent in pieces: it is checked whole first.
  // Session 143: between the two a line {"type":"words","answer":...} may come: the answer's words, whole, once their
  // numbers, their form and their premise have passed the check, while the citations, the series and the questions to
  // ask next are still being written; the result that follows is the whole answer, checked as before. Should the whole
  // draft not bear the words out, {"type":"withdrawn"} takes them back before anything else is sent.
  if (profile === "ercot" && stream === true) {
    const enc = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      async start(ctrl) {
        const send = (o: unknown) => ctrl.enqueue(enc.encode(JSON.stringify(o) + "\n"));
        send({ type: "started" });
        try {
          const r = await ask(asked, undefined, null, ercotProfile(), cleanContext(context), { history: cleanHistory(history), onEvent: send, questionId: qid, ...timing });
          logged(r);
          send({ type: "result", ...r });
        } catch (e) {
          console.log(JSON.stringify({ erw_ask: { at: new Date(now).toISOString(), question: asked, status: "error" } }));
          console.error(`[erw ask] ${(e as Error).message}`);
          send({ type: "error", error: `the question could not be answered: ${(e as Error).message}` });
        }
        ctrl.close();
      },
    });
    return new Response(body, { headers: { "Content-Type": "application/x-ndjson; charset=utf-8", "Cache-Control": "no-store", "X-Accel-Buffering": "no" } });
  }
  try {
    const r = profile === "ercot"
      ? await ask(asked, undefined, null, ercotProfile(), cleanContext(context), { history: cleanHistory(history), questionId: qid, ...timing })
      : await ask(question.trim(), undefined, typeof grid === "string" && grid ? grid : null, null, null, { questionId: qid });
    // session 21 (/terms): each question is logged without identity: the time, the question and the
    // outcome, never the IP address (which lives only in memory, for the hourly limit) or any other identifier
    console.log(JSON.stringify({ erw_ask: { at: new Date(now).toISOString(), grid: grid || (profile === "ercot" ? "ercot (reference)" : null), question: question.trim(), status: (r as { status?: string }).status ?? "answered", question_id: qid, cost_usd: (r as { cost_usd?: number | null }).cost_usd ?? null } }));
    return NextResponse.json(r);
  } catch (e) {
    console.log(JSON.stringify({ erw_ask: { at: new Date(now).toISOString(), question: question.trim(), status: "error" } }));
    console.error(`[erw ask] ${(e as Error).message}`);
    return NextResponse.json({ error: `the question could not be answered: ${(e as Error).message}` }, { status: 502 });
  }
}
