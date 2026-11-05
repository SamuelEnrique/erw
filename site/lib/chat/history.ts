// Energy Research Warehouse (ERW) site, session 1129: a conversation on the general chat, as Ask ERCOT has held one since
// session 121 (lib/chat/ercot.ts cleanHistory, historyText). The last turns, each its question, its answer and what its
// queries read (session 1115's reads), go into the first message before the new question, in Ask ERCOT's own words
// (lib/chat/spec_ercot.json history_head, history_turn); the numbers of an earlier answer count as given (they were
// checked when it was written) and its cited tables as read; every new number is still fetched and checked. With no
// earlier turn the first message is byte for byte what it was. Pure: no request.
import spec from "./spec_ercot.json";

const S = spec as unknown as { history_head: string; history_turn: string; max_history: number; max_history_answer: number };
export type PastTurn = { question: string; answer: string; queries: string[]; tables: string[] };

const TABLE = /^[a-z][a-z0-9_]*$/;
const sorted = (v: unknown): unknown => (Array.isArray(v) ? v.map(sorted) : v && typeof v === "object"
  ? Object.fromEntries(Object.keys(v as Record<string, unknown>).sort().map((k) => [k, sorted((v as Record<string, unknown>)[k])])) : v);

/** The turns a browser sent, cleaned: the last few, each with a question and an answer, its reads (or a profile's
 *  calls) as compact queries, and the tables it cited. Anything else is dropped. */
export function cleanTurns(raw: unknown): PastTurn[] {
  if (!Array.isArray(raw)) return [];
  const text = (v: unknown, n: number) => (typeof v === "string" ? v.trim().slice(0, n) : "");
  const out: PastTurn[] = [];
  for (const h of raw.slice(-S.max_history)) {
    if (!h || typeof h !== "object") continue;
    const r = h as Record<string, unknown>;
    const question = text(r.question, 500), answer = text(r.answer, S.max_history_answer);
    if (!question || !answer) continue;
    const queries: string[] = [];
    for (const x of (Array.isArray(r.reads) ? r.reads : []).slice(0, 8)) {
      if (!x || typeof x !== "object" || typeof (x as Record<string, unknown>).table !== "string") continue;
      const q = JSON.stringify(sorted(x));
      if (q.length <= 1200) queries.push(`query ${q}`);
    }
    const tables = (Array.isArray(r.citations) ? r.citations : []).map((c) => String((c as Record<string, unknown> | null)?.table ?? "")).filter((t) => TABLE.test(t));
    out.push({ question, answer, queries, tables });
  }
  return out;
}

/** The first message: the conversation so far, then the day and the question; with no turn, exactly as before. */
export function generalOpening(question: string, today: string, past: PastTurn[]): string {
  const now = `Today is ${today} (UTC).\n\nQuestion: ${question}`;
  if (!past.length) return now;
  const parts = [S.history_head];
  past.forEach((t, i) => parts.push(S.history_turn.replace("{n}", String(i + 1)).replace("{question}", () => t.question)
    .replace("{answer}", () => t.answer).replace("{queries}", () => t.queries.join("; ") || "none")));
  return `${parts.join("\n\n")}\n\n${now}`;
}
