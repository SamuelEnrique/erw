// Energy Research Warehouse (ERW) site, session 1157 (chain 077): the stored example answers of the Grid tool's Ask
// panel (/grid), by grid. The examples are stored texts: answers a recorded evaluation of /api/ask graded right, each
// figure traced to the tool result it came from (data/grid_ask_examples.json, written by
// scripts/build-grid-ask-examples.mjs from warehouse/chat/eval/). No model is called here or on the page.
//
// The hold of a license (lib/license.ts) is applied on the day the page is drawn: an example a figure of which comes
// from a table held for the grid is not shown, and in its place stand the words the live Ask's tools give for that
// read (lib/supabase.ts LicenseNeeded: licenseReason(table), "license needed: <publishers>: the publisher's own page
// asks for permission; none is recorded yet"). A figure's grid is its entity's (lib/license.ts gridOfEntity), or the
// example's own grid when the call named no entity of a grid (eia930:ISNE, a market filter, none).
import stored from "@/data/grid_ask_examples.json";
import { gridOfEntity, licenseHeldRow, licenseReason } from "@/lib/license";

export type AskExampleSource = { tool: string; tables: string[]; filter: string; entities: string[]; figures: string[] };
export type AskExample = {
  id: string;
  grid: string;
  file: string;
  session: number;
  question_id: string;
  run: string;
  asked_at_utc: string;
  via: string;
  model: string | null;
  question: string;
  answer: string;
  refusal: boolean;
  verdict: string;
  sources: AskExampleSource[];
};
export type AskExampleGrid = { label: string; usable: number; examples: AskExample[] };
export type StoredExamples = { max_examples: number; grids: Record<string, AskExampleGrid> };

/** An example as the panel draws it: `held` names the held table and the refusal's words, or is null. */
export type ShownExample = AskExample & { held: { table: string; words: string } | null };

const STORED = stored as unknown as StoredExamples;
export const ASK_EXAMPLES_MAX: number = STORED.max_examples;

/** The table held for this example's grid on the day that one of its figures comes from, or null. */
export function heldTableOf(e: Pick<AskExample, "grid" | "sources">, now: Date = new Date()): string | null {
  for (const s of e.sources) {
    const ents = s.entities.length ? s.entities : [""];
    for (const t of s.tables) {
      for (const ent of ents) {
        const entity = gridOfEntity(ent) ? ent : `iso:${e.grid}`;
        if (licenseHeldRow(t, entity, now)) return t;
      }
    }
  }
  return null;
}

/** The refusal's words for a held table: the live Ask's (lib/supabase.ts LicenseNeeded, licenseReason). */
export const heldWords = (table: string) => licenseReason(table);

/** The examples of one grid as drawn on the day, from a stored file (the committed one unless given). */
export function gridAskExamples(slug: string, now: Date = new Date(), file: StoredExamples = STORED): { label: string; usable: number; shown: ShownExample[] } {
  const g = file.grids[slug];
  if (!g) return { label: slug, usable: 0, shown: [] };
  const shown = g.examples.slice(0, file.max_examples).map((e) => {
    const t = heldTableOf(e, now);
    return { ...e, held: t ? { table: t, words: heldWords(t) } : null };
  });
  return { label: g.label, usable: g.usable, shown };
}

const NUMBER_WORDS = ["No", "One", "Two", "Three", "Four", "Five"];

/** The line above the examples: how many stored answers there are, said plainly when fewer than the panel holds. */
export function examplesLine(n: number, label: string, max: number = ASK_EXAMPLES_MAX): string {
  const who = label === "US48" ? "the Lower 48" : label;
  if (n >= max) return `${NUMBER_WORDS[max] ?? max} stored answers for ${who}, asked of the warehouse and graded right.`;
  const word = NUMBER_WORDS[n] ?? String(n);
  return `${word} stored answer${n === 1 ? "" : "s"} for ${who} so far, asked of the warehouse and graded right.`;
}
