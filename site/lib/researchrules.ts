// Energy Research Warehouse (ERW) site, session 238: the rules by which the Research page (/research) files a finding
// under grids and topics, and reads which chart a Roundup carried. Pure: no fs, no bundle, so the page (through
// lib/research.ts) and the tests share it. The rules are stated in lib/research.ts and on the page itself.
import type { Card } from "./findings";

export const GRIDS: { id: string; label: string; words: RegExp; table: RegExp }[] = [
  { id: "ercot", label: "ERCOT", words: /\bERCOT\b/i, table: /^ercot_/ },
  { id: "caiso", label: "CAISO", words: /\bCAISO\b/i, table: /^caiso_/ },
  { id: "pjm", label: "PJM", words: /\bPJM\b/i, table: /^pjm_/ },
  { id: "miso", label: "MISO", words: /\bMISO\b/i, table: /^miso_/ },
  { id: "spp", label: "SPP", words: /\bSPP\b/i, table: /^spp_/ },
  { id: "nyiso", label: "NYISO", words: /\bNYISO\b/i, table: /^nyiso_/ },
  { id: "isone", label: "ISO-NE", words: /\bISO-NE\b/i, table: /^isone_/ },
];
export const NO_GRID = { id: "none", label: "Not one grid" };

export const TOPIC_RULES: { id: string; label: string; table: RegExp }[] = [
  { id: "fuel-prices", label: "Fuel prices", table: /fuel_spot/ },
  { id: "curtailment", label: "Curtailment", table: /curtailment/ },
  { id: "batteries", label: "Batteries", table: /storage|battery/ },
  { id: "generation", label: "Generation by fuel", table: /fuel_supply/ },
  // session 720: the queue's derived durations (interconnection_durations) are the queue's too
  { id: "queue", label: "Interconnection queue", table: /queue|interconnection_durations/ },
  { id: "demand", label: "Demand", table: /load|demand/ },
  { id: "interchange", label: "Interchange", table: /interchange/ },
  { id: "events", label: "Events", table: /^event_/ },
  { id: "generators", label: "Generators", table: /eia860m/ },
  // session 720: ERCOT's four peaks and the PUCT's transmission charge (the All grids tab's card)
  { id: "transmission", label: "Transmission charges", table: /4cp|transmission/ },
  { id: "power-prices", label: "Power prices", table: /prices/ },
];
export const OTHER_TOPIC = { id: "other", label: "Other tables" };

/** The grids a card names (ids of GRIDS, in that order), or ["none"]. */
export function gridsOf(card: Card): string[] {
  const words = [...Object.values(card.inputs_words ?? {}), ...((card.chart?.series ?? []) as { name?: string }[]).map((s) => s.name ?? ""), ...((card.chart?.x ?? []) as unknown[]).map(String)].join(" | ");
  const notHeld = new Set((card.placeholders ?? []).map((p) => p.grid.toLowerCase()));
  const found = GRIDS.filter((g) => !notHeld.has(g.id) && ((card.tables ?? []).some((t) => g.table.test(t)) || g.words.test(words))).map((g) => g.id);
  return found.length ? found : [NO_GRID.id];
}

/** The topics of a card: one for each table it read, in the order of TOPIC_RULES. */
export function topicsOf(card: Card): string[] {
  const hit = new Set((card.tables ?? []).map((t) => TOPIC_RULES.find((r) => r.table.test(t))?.id ?? OTHER_TOPIC.id));
  return [...TOPIC_RULES.map((r) => r.id), OTHER_TOPIC.id].filter((id) => hit.has(id));
}

export const gridLabel = (id: string) => GRIDS.find((g) => g.id === id)?.label ?? NO_GRID.label;
export const topicLabel = (id: string) => TOPIC_RULES.find((r) => r.id === id)?.label ?? OTHER_TOPIC.label;

/** The section "ERW's Chart of the Week" of a Roundup's markdown ("Chart of the week" in W39's); "" when it has none. */
export function chartSectionOf(md: string): string {
  const at = md.search(/^## .*Chart of the Week\s*$/im);
  if (at < 0) return "";
  const rest = md.slice(at).replace(/^[^\n]*\n?/, "");   // the lines after the section's title
  const end = rest.search(/^## /m);
  return (end < 0 ? rest : rest.slice(0, end)).trim();
}

/** The finding a Roundup chose for its chart of the week: the card whose picture the section shows
 *  (docs/analysis/findings/<card>_1600x900.png); null when the section shows the rule's pick, or there is none. */
export function chosenCardOf(section: string): string | null {
  return (section.match(/[.][.]\/analysis\/findings\/([a-z0-9_.-]+)_1600x900\.png/i) ?? [])[1] ?? null;
}
