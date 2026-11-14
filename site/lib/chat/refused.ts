// Energy Research Warehouse (ERW) site, session 5256 (chain 238): a table a tool refuses to read, in a module of its own
// with no imports (so `node --test` reads it without a build), as warehouse/chat/tools.py and warehouse/chat/ask.py hold
// the same words and the same rule.
//
// The platform set's oi07 (docs/reviews/ask-eval-2026-11-13.md): asked for a figure of a table the catalogue lists and
// the live set does not hold, the chat was refused the table, said so rightly, and still answered as an answer, with
// that table as its source. Two causes, two mends:
//
//   the words   the refusal said where the table is and not how to answer, where a held table's refusal says both.
//               notLiveWords() says both. Session 5258: and that another table may hold what is asked. The first
//               wording said only "answer with not_in_warehouse true"; the held-out nu08 was refused EIA's generator
//               table, looked on all the same, and found the unit's capacity in energy_projects, which carries it.
//               The words must not forbid what rule 3 of the prompt asks for.
//   the rule    the loop counts every table list_tables names as read, so the citation passed. refusedRead() tells a
//               refusal of the table itself from any other tool error; lib/chat/ask.ts holds that an answer's citation
//               of a table refused and never read is a citation of a table no tool read, and sends the draft back.
//   the stop    told once that a table cannot be read, the model asked it again with other arguments (pw12 nine times,
//               oi07 six, after the words above were in place). A table refused whole is not asked again: a later call
//               that names it is answered with a note, as a call already made is (session 2222): nothing is read, the
//               call is counted, and a turn of such calls alone is followed by a call that may only write.

/** The refusal of a table the catalogue lists and the live set does not hold: where it is, and how to answer. */
export function notLiveWords(table: string): string {
  return `table ${table} is not in this site's live set; its full history is on Redivis. No tool here can read it, and no figure of it may be stated. Another table you can read may hold what is asked (a derived table often carries a source table's figures): look before you refuse. If none does, answer with not_in_warehouse true and say that ${table} is on Redivis and not in the live set this chat reads`;
}

/** The table a tool's error refuses whole, among those the call named: one not in the live set, or held whole for a
 * license. Null for any other error: MISO's pause and a held grid refuse rows of a table, not the table. */
export function refusedWhole(error: unknown, tables: string[]): string | null {
  if (typeof error !== "string") return null;
  return tables.find((t) => error.startsWith(`table ${t} is not in this site's live set`) || error.startsWith(`table ${t} is license needed`)) ?? null;
}

/** What a later call that names a table already refused whole is answered with: no read, the refusal's own words again. */
export function refusedAgainNote(table: string, words: string): string {
  return `table ${table} was already refused for this question and no call can read it: do not ask it again. ${words}`;
}

/** The tables a call names: a query's or a description's own, a compare's two. */
export function tablesNamed(name: string, input: unknown): string[] {
  const a = (input && typeof input === "object" ? input : {}) as Record<string, unknown>;
  const one = (x: unknown) => (x && typeof x === "object" && typeof (x as Record<string, unknown>).table === "string" ? [String((x as Record<string, unknown>).table)] : []);
  return name === "query" || name === "describe_table" ? one(a) : name === "compare" ? [...one(a.a), ...one(a.b)] : [];
}

/** Whether a tool's error refuses the table itself: not in the live set, held for a license, or MISO's pause. */
export function refusedRead(error: unknown): boolean {
  return typeof error === "string" && /is not in this site's live set|license needed|MISO is paused/.test(error);
}

// Session 5276 (chain 256): a refusal's fixed words, by the loop. Rule 3 of the prompt asks for the words "not in the
// warehouse"; a held table's refusal says "license needed" and MISO's "paused" (the tools' own words). Of the 135
// refusals for want of a figure in the stored runs, two carried none of the three: "I can't give this figure" (oi09, 13
// November 2026) and "The warehouse does not hold this figure" (gp02, 14 November 2026), each right in substance. The
// reader's page and the grader both tell a refusal by its words. So a refusal of the general chat that carries none of
// them is given the first: the fixed sentence before the model's own, nothing of the model's changed. As
// warehouse/chat/ask.py with_refusal_words. Not for a profile's chat (Ask ERCOT's refusals have their own form).
export const REFUSAL_WORDS = ["not in the warehouse", "license needed", "paused"];
export const REFUSAL_FIRST = "Not in the warehouse.";
/** A refusal's text with its fixed words: as it is when it carries one of REFUSAL_WORDS, else REFUSAL_FIRST before it. */
export function withRefusalWords(answer: string): string {
  const low = answer.toLowerCase();
  return REFUSAL_WORDS.some((w) => low.includes(w)) ? answer : `${REFUSAL_FIRST} ${answer.trim()}`.trim();
}

// Session 6106 (chain 280): a refusal states no figure, and a held table is said to be held. The whole platform set
// asked once more on 14 November 2026 (134 questions, docs/reviews/ask-eval-2026-11-13.md) had two answers not right:
//
//   pw13  asked ERCOT's peak demand of the summer of 2028, the chat refused rightly ("Not in the warehouse. It holds no
//         forecast") and went on: "The only peak figure I found is a past one: ERCOT's 2025 peak demand was 83,597 MW".
//         The figure was fetched and cited, and rule 3 says a refusal states no numbers: a reader of a refusal must not
//         be left with a figure that answers another question. Of the 124 refusals in the stored runs of this loop it
//         is the only one that states a figure. A draft that refuses and states a figure is sent back once, as a draft
//         with an untraced number is (refusalFigures; a number the question itself holds is the asker's).
//   pj08  asked the MW active in ISO New England's queue, the chat was refused ISO-NE's own table (license needed), said
//         so in its own words ("is held because it needs a license") and answered from Berkeley Lab's public table. The
//         license file allows that table; the hold's fixed words were missing. An answer written after a table was
//         refused as license needed, and that does not carry the words, is given them by the loop (withHoldWords),
//         nothing of the model's changed: as a refusal is given its words (session 5276).
//
// For the general chat only, as withRefusalWords. The same in warehouse/chat/ask.py (refusal_figures, with_hold_words).
export const HOLD_WORDS = "license needed";
/** What a draft that refuses and states a figure is sent back with (ask.py REFUSAL_FIGURE). */
export function refusalFigureProblem(figures: string[]): string {
  return `a refusal that states a figure (${figures.join(", ")}): rule 3 says a refusal states no numbers. Remove it, or, if a tool result holds what the question asks for, answer the question with not_in_warehouse false`;
}

const FIGURE = /(?<![A-Za-z_\d.])(-?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?!\d)/g;   // ask.ts NUM, kept here so this module imports nothing
const namesDigits = (text: string, at: number) => at >= 2 && text[at - 1] === "-" && /[A-Za-z]/.test(text[at - 2]);

/** The figures a refusal states, as written: a number with decimals, or a whole number of 1,000 or more that is not a
 * year (1900 to 2100), as the evaluation's grader tells a figure in a refusal. A number the question holds, a name's
 * digits (EIA-930) and a list marker are not figures of the answer. */
export function refusalFigures(answer: string, question = ""): string[] {
  const text = (answer ?? "").replace(/−/g, "-");
  const asked = new Set<number>();
  const q = (question ?? "").replace(/−/g, "-");
  for (const m of q.matchAll(FIGURE)) {
    if (!namesDigits(q, (m.index ?? 0) + m[1].length)) asked.add(parseFloat(m[2].replace(/,/g, "") + (m[3] ?? "")));
  }
  const marks = new Set(Array.from(text.matchAll(/^\s*(\d+)[.)]\s/gm)).map((m) => parseFloat(m[1])));
  const out: string[] = [];
  for (const m of text.matchAll(FIGURE)) {
    const whole = m[2], frac = m[3] ?? "";
    if (namesDigits(text, (m.index ?? 0) + m[1].length)) continue;
    const v = parseFloat(whole.replace(/,/g, "") + frac);
    if (asked.has(v) || marks.has(v)) continue;
    if (frac || (v >= 1000 && !(v >= 1900 && v <= 2100))) {
      const s = whole + frac;
      if (!out.includes(s)) out.push(s);
    }
  }
  return out;
}

/** The tables a tool refused as license needed, from the loop's record of the tables refused whole and the words. */
export function heldTables(refusedWords: Map<string, string> | Record<string, string>): string[] {
  const entries = refusedWords instanceof Map ? Array.from(refusedWords.entries()) : Object.entries(refusedWords ?? {});
  return entries.filter(([t, w]) => typeof w === "string" && w.startsWith(`table ${t} is ${HOLD_WORDS}`)).map(([t]) => t).sort();
}

/** An answer written after a table was refused as license needed: as it is when it carries the words, else a fixed
 * sentence that names the table before it. */
export function withHoldWords(answer: string, held: string[]): string {
  if (!held.length || (answer ?? "").toLowerCase().includes(HOLD_WORDS)) return answer;
  return `${held.join(", ")}: ${HOLD_WORDS}, so no figure of ${held.length === 1 ? "it" : "them"} is given here. ${(answer ?? "").trim()}`.trim();
}

// Session 6109 (chain 280): an answer that stops in the middle of a sentence. The lab's l02 of 14 November 2026 was
// refused energy_deals, a table held for a license, and the answer that reached the reader was "This is not in the
// warehouse. The energy_deals table, which holds power purchase agreements, is held for a license (": the model closed
// the answer's string where it meant to quote the hold's words. One of the 888 stored answers ends so. A draft whose
// answer ends on an opening bracket, a comma, a colon or a semicolon is sent back once (ask.py cut_short, CUT_SHORT).
export const CUT_SHORT = "an answer that stops in the middle of a sentence: write the whole answer again, as plain sentences, with no double quotation marks inside it";
/** Whether an answer stops in the middle of a sentence. An empty answer is another check's. */
export function cutShort(answer: string): boolean {
  const t = (answer ?? "").trimEnd();
  return t.length > 0 && "([{,:;".includes(t[t.length - 1]);
}

// Session 6113 (chain 280): a table of the ERW's record that the site's catalogue does not list. The catalogue lists the
// tables a visitor may hear of; a table whose license is not settled or internal is never in it, and a table that has
// just landed is not in it until the next load. The briefing names every table of the record. Asked on 14 November 2026
// about the week's new tables (utility_large_load_rules, forecast_tool_parameters), the chat refused rightly, six of six,
// and three of the six took all 12 tool calls looking; one of them (ru07) went on from a neighbour table: "No large-load
// rule has the status denied", said of a table of statements, not of rules. The tools answered a call that named such a
// table "no public table named ...; call list_tables". They now say what it is, in the words of a table not in the
// live set (so the loop counts it refused whole, and does not ask it again), and the list's note says the same.
// As warehouse/chat/tools.py not_listed_words and NOT_LISTED_NOTE.
export const NOT_LISTED_NOTE = "A table the briefing names and this list does not is a table of the record this site cannot read: describe_table says why. A question about such a table is answered 'not in the warehouse' with the table named, never from another table.";
/** The refusal of a table of the record the catalogue does not list. `verdict`: the license record's word for the table
 * (site/data/table_verdicts.json): public, or anything else (unsettled, internal). */
export function notListedWords(table: string, verdict: string): string {
  const why = verdict === "public" ? "it is a table of the ERW's record that is not loaded here" : "it is a table of the ERW's record whose license is not settled (license needed), so the ERW does not publish it";
  return `table ${table} is not in this site's live set: ${why}. No tool here can read it, and no figure of it may be stated. Another table you can read may hold what is asked (a derived table often carries a source table's figures): look before you refuse, and never answer for ${table} from a table that holds something else. If none does, answer with not_in_warehouse true and say that ${table} is not in the live set this chat reads`;
}
