// Energy Research Warehouse (ERW) site, session 7564 (the Research read, row 1): a finding card holds a grid held under
// its publisher's terms everywhere it shows a figure, not only in its callouts (ruling 6a of the Research pack held the
// callouts; the why paragraph, the footnote and the charts still printed NYISO's and ISO-NE's figures from tables held
// since 21 October 2026: "its evening share rose from 43.3 to 62.5 percent", "ISO-NE's zones went from 18.6 to 5.5
// percent", their panels and bars). Applied where the cards are read (lib/findings.ts), so every page that draws a card
// draws it held. A held grid's panel or series leaves the chart and is named in its placeholders with "license needed",
// as MISO's and PJM's are; a sentence of the why or the footnote that names a held grid and carries a figure is taken
// out, and one line says how many and why. The card's file is not changed.
import { LICENSE_NEEDED, licenseNeeded, licenseTitle } from "./license";
import type { Card } from "./findings";

/** The grids a card may draw that are held as a whole, each by its own price table's hold. */
export const HELD_GRID_TABLE: Record<string, string> = { nyiso: "nyiso_rtm_zone_prices", isone: "isone_rtm_zone_prices" };
const GRID_NAME: Record<string, string> = { nyiso: "NYISO", isone: "ISO-NE" };
// the words a sentence names a grid by: its name, and the region the cards write it as ("New York City's zone")
const GRID_RE: Record<string, RegExp> = { nyiso: /\bNYISO\b|\bNew York\b/, isone: /\bISO-NE\b|\bNew England\b/ };

export function heldGrids(now: Date = new Date()): string[] {
  return Object.entries(HELD_GRID_TABLE).filter(([, t]) => licenseNeeded(t, now)).map(([g]) => g);
}

const gridOfName = (s: string, held: string[]) => held.find((g) => GRID_RE[g].test(s) || s.trim().toLowerCase() === g);
const placeholder = (g: string) => ({ grid: g, words: GRID_NAME[g], text: `${LICENSE_NEEDED}: ${licenseTitle(HELD_GRID_TABLE[g])}` });

type Spec = Card["chart"] & { panels?: { grid: string }[] };
function holdSpec(spec: Spec | undefined, held: string[]): { spec: Spec | undefined; out: string[] } {
  if (!spec) return { spec, out: [] };
  const out = new Set<string>();
  const series = (spec.series ?? []).filter((s) => { const g = gridOfName(s.name ?? "", held); if (g) out.add(g); return !g; });
  const panels = spec.panels?.filter((p) => { const g = held.includes(p.grid) ? p.grid : undefined; if (g) out.add(g); return !g; });
  if (!out.size) return { spec, out: [] };
  const had = new Set((spec.placeholders ?? []).map((p) => p.grid));
  const placeholders = [...(spec.placeholders ?? []), ...[...out].filter((g) => !had.has(g)).map(placeholder)];
  return { spec: { ...spec, series, ...(panels ? { panels } : {}), placeholders }, out: [...out] };
}

/** The sentences of a paragraph that name a held grid and carry a figure, taken out, with one line in their place. */
export function holdWords(text: string, held: string[]): { text: string; n: number; grids: string[] } {
  if (!text || !held.length) return { text, n: 0, grids: [] };
  const parts = text.split(/(?<=[.!?])\s+(?=[A-Z(])/);
  const grids = new Set<string>();
  const kept = parts.filter((s) => {
    const named = held.filter((g) => GRID_RE[g].test(s));
    if (named.length && /\d/.test(s)) { named.forEach((g) => grids.add(g)); return false; }
    return true;
  });
  const n = parts.length - kept.length;
  if (!n) return { text, n: 0, grids: [] };
  const names = [...grids].map((g) => GRID_NAME[g]).join(" and ");
  return { text: [...kept, `${n === 1 ? "One sentence" : `${n} sentences`} with figures of ${names} ${n === 1 ? "is" : "are"} held (${LICENSE_NEEDED}: the publisher's own page asks for permission).`].join(" "), n, grids: [...grids] };
}

export function holdCard(card: Card, held: string[] = heldGrids()): Card {
  if (!held.length) return card;
  const main = holdSpec(card.chart as Spec, held);
  const more = card.more_charts?.map((m) => ({ ...m, spec: holdSpec(m.spec as Spec, held).spec as Card["chart"] }));
  const why = holdWords(card.why ?? "", held);
  const foot = holdWords(card.footnote ?? "", held);
  const out = new Set([...main.out, ...why.grids, ...foot.grids]);
  if (!out.size) return card;
  const had = new Set((card.placeholders ?? []).map((p) => p.grid));
  return {
    ...card,
    chart: main.spec as Card["chart"],
    ...(more ? { more_charts: more } : {}),
    why: why.text, footnote: foot.text,
    placeholders: [...(card.placeholders ?? []), ...[...out].filter((g) => !had.has(g)).map(placeholder)],
  };
}
