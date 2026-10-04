// Energy Research Warehouse (ERW) site: POST /api/ask, read-only question answering.
//
// Runs the loop in lib/chat/ask.ts on the server, with ANTHROPIC_API_KEY from the environment
// and the Supabase anon key for data (public rows only). Nothing is written anywhere.
// Rate limit: 10 questions per IP per hour. The count is kept in this server instance's
// memory, so on a platform that runs several instances (Vercel) each keeps its own count:
// the limit is per instance, a floor rather than a guarantee.
import { NextResponse } from "next/server";
import { ask } from "@/lib/chat/ask";
import { scopeOf } from "@/lib/chat/tools";
import { cleanContext, ercotProfile } from "@/lib/chat/ercot";

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
  let question: unknown, grid: unknown, profile: unknown, context: unknown;
  try {
    ({ question, grid, profile, context } = (await req.json()) as { question?: unknown; grid?: unknown; profile?: unknown; context?: unknown });
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
  try {
    const r = profile === "ercot"
      ? await ask(question.trim(), undefined, null, ercotProfile(), cleanContext(context))
      : await ask(question.trim(), undefined, typeof grid === "string" && grid ? grid : null);
    // session 21 (/terms): each question is logged without identity: the time, the question and the
    // outcome, never the IP address (which lives only in memory, for the hourly limit) or any other identifier
    console.log(JSON.stringify({ erw_ask: { at: new Date(now).toISOString(), grid: grid || (profile === "ercot" ? "ercot (reference)" : null), question: question.trim(), status: (r as { status?: string }).status ?? "answered" } }));
    return NextResponse.json(r);
  } catch (e) {
    console.log(JSON.stringify({ erw_ask: { at: new Date(now).toISOString(), question: question.trim(), status: "error" } }));
    console.error(`[erw ask] ${(e as Error).message}`);
    return NextResponse.json({ error: `the question could not be answered: ${(e as Error).message}` }, { status: 502 });
  }
}
