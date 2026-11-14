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
