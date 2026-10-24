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
//
// Session 1405 (chain 100): the examples of the tab on screen first. Each example's tab is read from the tables its
// tool calls read (its sources), through ASK_TABLE_TAB, the one map from a table to a tab, built from the tab lists of
// lib/gridtables.ts (GRID_VIEW_TABLES) so the two cannot part. The selection is unchanged (the same five at most a
// grid); only the order moves, and ties keep the stored order.
import stored from "@/data/grid_ask_examples.json";
import { gridOfEntity, licenseHeldRow, licenseReason } from "@/lib/license";
import { GRID_VIEW_TABLES } from "@/lib/gridtables";
import type { GridView } from "@/lib/gridtool";

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

/** The tab a stored answer belongs to: the Network tab's (which the Gravity tab shares: both draw the same tables), the
 * Mix tab's or the Clean tab's. */
export type AskTab = "network" | "mix" | "clean";

/** The tab of a tab on screen: Gravity reads the Network tab's tables (lib/gridtables.ts), so it orders as Network. */
export const askTabOfView = (view: GridView): AskTab => (view === "gravity" ? "network" : view);

// Session 1405: the tab lists of lib/gridtables.ts overlap (the Mix and Clean tabs draw the same files, and the Network
// tab's list names carbon, demand and hub price tables too), so a table's tab is decided in this order:
//   network  a table of the Network tab's list that the Mix tab's list does not name, or an interchange table of it
//   clean    a table of the Clean tab's list that the Mix tab's list does not name, or a carbon, emissions or clean
//            energy table of it
//   mix      any other table of the Mix tab's list (generation, demand, prices, the mix, storage)
// A table on no tab's list (the cost of power, merchant revenue, the battery stack, the curtailment, ...) has no tab.
const IS_CARBON = /^carbon_|emissions|^clean_energy_/;
function tabOfTable(t: string): AskTab | null {
  const net = GRID_VIEW_TABLES.network.includes(t), mix = GRID_VIEW_TABLES.mix.includes(t), clean = GRID_VIEW_TABLES.clean.includes(t);
  if (net && (!mix || t.includes("interchange"))) return "network";
  if (clean && (!mix || IS_CARBON.test(t))) return "clean";
  if (mix) return "mix";
  return null;
}

/** Every table a tab of the Grid tool names (lib/gridtables.ts), with the one tab a stored answer that reads it belongs to. */
export const ASK_TABLE_TAB: Readonly<Record<string, AskTab>> = Object.freeze(Object.fromEntries(
  [...new Set(Object.values(GRID_VIEW_TABLES).flat())].sort().flatMap((t) => { const tab = tabOfTable(t); return tab ? [[t, tab]] : []; }),
));

/** The tabs of a stored answer: the tabs of the tables its tool calls read, in the order first read; none for a refusal
 * or an answer whose tables no tab names. */
export function askTabsOf(e: Pick<AskExample, "sources">): AskTab[] {
  const tabs: AskTab[] = [];
  for (const s of e.sources) for (const t of s.tables) { const tab = ASK_TABLE_TAB[t]; if (tab && !tabs.includes(tab)) tabs.push(tab); }
  return tabs;
}

/** The examples ordered for the tab on screen: those that read a table of its tab first, then the rest, each part in
 * the order given (a stable sort: ties keep the stored order). The same examples, none added or dropped. */
export function orderByTab<T extends Pick<AskExample, "sources">>(examples: readonly T[], view: GridView): T[] {
  const tab = askTabOfView(view);
  const mine = examples.filter((e) => askTabsOf(e).includes(tab));
  return [...mine, ...examples.filter((e) => !mine.includes(e))];
}

/** The examples of one grid as drawn on the day, from a stored file (the committed one unless given); with a tab
 * (session 1405), the examples of that tab first (orderByTab), the selection unchanged. */
export function gridAskExamples(slug: string, now: Date = new Date(), file: StoredExamples = STORED, view: GridView | null = null): { label: string; usable: number; shown: ShownExample[] } {
  const g = file.grids[slug];
  if (!g) return { label: slug, usable: 0, shown: [] };
  const picked = g.examples.slice(0, file.max_examples);
  const shown = (view ? orderByTab(picked, view) : picked).map((e) => {
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
