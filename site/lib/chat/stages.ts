// Energy Research Warehouse (ERW) site, session 143: where the seconds of an answer go.
//
// Pure functions, no imports (Node runs this file as it is, for site/scripts/test-ask-speed.mjs). Every answer of the
// loop in lib/chat/ask.ts records the milliseconds of each stage, and the stages sum to the whole, exactly:
//
//   planning   the model calls that decide what to read (a call that ends by asking for tools)
//   fetching   the tool calls: the database queries and the file reads, the calls of one turn read together
//   drawing    building the series a chart or table is drawn from and checking each against the rows fetched
//   writing    the model call that writes the answer, and the check of its numbers
//   other      everything else: the admission by the database before any model call, the list of models, the cost
//              ledger's rows. It is what is left of the whole once the four stages are taken away, so the five sum to it.
//
// The record is for the evaluation and the server's log. Nothing of it is shown on a page.

export type Stage = "planning" | "fetching" | "drawing" | "writing" | "other";
export const STAGES: Stage[] = ["planning", "fetching", "drawing", "writing", "other"];
/** One timed step: a model call (with its model, the milliseconds to its first text and its output tokens), the tool
 * calls of one turn (with each tool's own milliseconds, which overlap and are not summed), the check, the drawing. */
export type Step = { stage: Stage; what: string; ms: number } & Record<string, unknown>;
export type StageMs = Record<Stage, number> & { total: number };

export function stageClock(t0: number, now: () => number = Date.now) {
  const steps: Step[] = [];
  let words: number | null = null;
  return {
    steps,
    /** A step that took `ms` milliseconds. */
    add(stage: Stage, what: string, ms: number, extra: Record<string, unknown> = {}): void {
      steps.push({ stage, what, ms: Math.max(0, Math.round(ms)), ...extra });
    },
    /** Run f and record how long it took. */
    async time<T>(stage: Stage, what: string, f: () => Promise<T> | T, extra: Record<string, unknown> = {}): Promise<T> {
      const t = now();
      try { return await f(); } finally { steps.push({ stage, what, ms: Math.max(0, Math.round(now() - t)), ...extra }); }
    },
    /** The moment the answer's words could be shown: once, the first time. */
    wordsAt(at: number = now()): void { if (words === null) words = Math.max(0, Math.round(at - t0)); },
    /** Milliseconds from the request to the answer's words, or null when they were never sent before the whole. */
    get wordsMs(): number | null { return words; },
    /** The stages in whole milliseconds. "other" is the whole less the four named stages, so the five sum to total. */
    done(end: number = now()): StageMs {
      return sumStages(steps, Math.max(0, Math.round(end - t0)));
    },
  };
}

/** The stages of a list of steps against a whole: the four named stages as recorded, "other" what is left. */
export function sumStages(steps: Step[], total: number): StageMs {
  const out: StageMs = { planning: 0, fetching: 0, drawing: 0, writing: 0, other: 0, total };
  for (const s of steps) if (s.stage !== "other") out[s.stage] += s.ms;
  const named = out.planning + out.fetching + out.drawing + out.writing;
  // steps are timed one after another on one clock, so they cannot pass the whole by more than rounding; when rounding
  // does, the whole is the sum, never less than its parts
  if (named > total) out.total = named;
  out.other = out.total - named;
  return out;
}

/** The closing quote of the JSON string that starts at text[open] ('"'), or -1 while the string is not yet whole. */
export function stringEnd(text: string, open: number): number {
  for (let i = open + 1; i < text.length; i++) {
    if (text[i] === "\\") { i += 1; continue; }
    if (text[i] === '"') return i;
  }
  return -1;
}

/** Session 143: the part of a draft that is whole once its "answer" string has closed, from the JSON text received so
 * far. The answer's schema puts form, not_in_warehouse, series and premise before answer, so when the answer's string
 * closes those are whole too, and the words can be checked before the rest (the citations, the follow-ups) is written.
 * null while the answer is not yet whole, or when the text so far cannot be read. Nothing is guessed: the text up to the
 * closing quote, closed with a brace, must parse as it stands. */
export function partialDraft(text: string): Record<string, unknown> | null {
  const m = /"answer"\s*:\s*"/.exec(text);
  if (!m) return null;
  // the key must be the object's own, not a word inside an earlier string: every string before it must have closed
  const open = m.index + m[0].length - 1;
  const end = stringEnd(text, open);
  if (end < 0) return null;
  try {
    const o = JSON.parse(text.slice(0, end + 1) + "}") as Record<string, unknown>;
    return typeof o.answer === "string" ? o : null;
  } catch {
    return null;
  }
}
