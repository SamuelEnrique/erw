// Energy Research Warehouse (ERW) site, session 1878: the pure part of /deals/capital (app/deals/capital/page.tsx), the
// companies faults of 12 November 2026 (docs/reviews/companies-faults-2026-11-11.md, rows 13 to 16): one color a deal
// type, the quarter chart's values and hover card with an absent type as no bar, USD billion written so a deal under
// USD 50 million is not "0", and the total line with no sum across types. No file is read here and nothing is fetched;
// scripts/test-capital-view.mjs tests it on rows written for the test.
import type { Tone } from "@/components/tool/GroupedBars";

export type Cell = { rows: number; usd: number; usd_rows: number; no_usd: number; mw: number };
export type Quarter = { quarter: string } & Record<string, Cell | string>;

/** One color a type, in the brand's series order (docs/brand.md, "Chart series"): four types, four colors. */
export const TONES: readonly Tone[] = ["accent", "ink", "blue", "muted"];
export const toneOf = (i: number): Tone => TONES[i % TONES.length];

/** USD as billions: one decimal from a billion, two under it, and two significant figures under ten million (so USD 30
 *  million is "0.03" and USD 2 million "0.002", never "0"). */
export function bn(v: number): string {
  if (!v) return "0";
  const b = v / 1e9;
  if (Math.abs(b) >= 1) return b.toLocaleString("en-US", { maximumFractionDigits: 1 });
  if (Math.abs(b) >= 0.01) return b.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return b.toLocaleString("en-US", { maximumSignificantDigits: 2 });
}

const cellOf = (q: Quarter, t: string): Cell | null => {
  const c = q[t];
  return c && typeof c !== "string" ? c : null;
};

/** A quarter's bars and hover card: a type with no deal in the quarter is no bar (null) and its card line says "none";
 *  a type with deals says its USD billion, its count of deals and how many state no USD. */
export function quarterBars(q: Quarter, types: string[], words: Record<string, string>) {
  const cells = types.map((t) => cellOf(q, t));
  const deals = (n: number) => `${n.toLocaleString("en-US")} ${n === 1 ? "deal" : "deals"}`;
  return {
    values: cells.map((c) => (c ? c.usd / 1e9 : null)),
    cards: cells.map((c) => (c ? `${bn(c.usd)} USD billion; ${deals(c.rows)}, ${c.no_usd.toLocaleString("en-US")} with no USD` : "none")),
    title: `${q.quarter}: ${types.map((t, i) => { const c = cells[i]; return c ? `${words[t] ?? t} ${deals(c.rows)}, ${c.no_usd} with no USD` : `${words[t] ?? t} none`; }).join("; ")}`,
  };
}

/** A seller as the largest deals' table writes it: one a story does not name says so, as the buyer does. */
export const named = (v: string): string => (v && v.trim() ? v : "not named");
