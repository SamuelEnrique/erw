// Energy Research Warehouse (ERW) site, session 2240 (chain 156): the AI-power view of the deals (/deals?view=ai).
//
// The deals the AI-power rule tags (warehouse/deals/fields.py: a named AI lab, hyperscaler, datacenter operator or
// AI-load buyer is a party, or the load is a datacenter), by buyer, by the kind of supply, by grid and by quarter: the
// deals of each group, and the MW and US dollars summed where the stories state them, with the count of those that
// state none beside each sum. A sum is of the stated figures only: a deal that states none is counted, never added as
// zero. Pure functions; the only import is a type, which Node strips (tests/test_session2240_deals.py).
import type { Deal } from "./deals2";

/** The kind of supply a deal is, from its kind (session 2232) and its technology as stated. */
export const SUPPLY: [string, string][] = [
  ["nuclear", "Nuclear"], ["gas", "Gas"], ["renewables_storage", "Renewables and storage"], ["grid", "Grid supply"],
  ["compute", "Compute capacity"], ["capital", "Capital and acquisitions"], ["other", "Other or not stated"],
];
export const SUPPLY_LABEL: Record<string, string> = Object.fromEntries(SUPPLY);

export function supplyOf(d: Deal): string {
  const t = d.technology.toLowerCase();
  if (["nuclear_restart_uprate", "smr"].includes(d.kind) || /nuclear|reactor|smr|fusion/.test(t)) return "nuclear";
  if (d.kind === "gas_buildout" || /\bgas\b|natural gas|lng|turbine/.test(t)) return "gas";
  if (d.kind === "storage" || /solar|wind|batter|storage|hydro|geotherm|renewable/.test(t)) return "renewables_storage";
  if (d.kind === "compute_capacity") return "compute";
  if (["ppa", "offtake", "behind_the_meter"].includes(d.kind)) return "grid";
  if (["capital", "m_and_a", "project_finance"].includes(d.kind)) return "capital";
  return "other";
}

/** The quarter of a deal's date, "2026-Q4". */
export const quarterOf = (d: Deal): string => `${d.date.slice(0, 4)}-Q${Math.floor((Number(d.date.slice(5, 7)) - 1) / 3) + 1}`;

/** The buyer of a deal as one name a company: the buyer, else (an equity raise, a loan) the party named first. */
export const buyerOf = (d: Deal): string => d.buyerName || d.buyer || d.sellerName || d.seller || "";

export const AI_DIMENSIONS: { id: string; label: string; of: (d: Deal) => string }[] = [
  { id: "buyer", label: "Buyer", of: buyerOf }, { id: "supply", label: "Kind of supply", of: supplyOf },
  { id: "grid", label: "Grid", of: (d) => d.grid }, { id: "quarter", label: "Quarter", of: quarterOf },
];

export type AiCell = { value: string; label: string; deals: number; mw: number | null; withMw: number; usd: number | null; withUsd: number };

/** The AI-tagged deals by one dimension, most deals first; "" (not stated) last, a quarter in time order. */
export function aiCells(deals: Deal[], dim: string): AiCell[] {
  const d0 = AI_DIMENSIONS.find((d) => d.id === dim);
  if (!d0) throw new Error(`unknown dimension ${dim}`);
  const by = new Map<string, Deal[]>();
  for (const d of deals.filter((x) => x.ai)) { const v = d0.of(d); by.set(v, [...(by.get(v) ?? []), d]); }
  const cells = [...by.entries()].map(([value, ds]) => {
    const mws = ds.flatMap((d) => (d.mw === null ? [] : [d.mw])), us = ds.flatMap((d) => (d.dollars === null ? [] : [d.dollars]));
    return { value, label: value === "" ? "not stated" : dim === "supply" ? SUPPLY_LABEL[value] ?? value : value, deals: ds.length,
      mw: mws.length ? mws.reduce((a, b) => a + b, 0) : null, withMw: mws.length,
      usd: us.length ? us.reduce((a, b) => a + b, 0) : null, withUsd: us.length };
  });
  if (dim === "quarter") return cells.sort((a, b) => a.value.localeCompare(b.value));
  return cells.sort((a, b) => (a.value === "" ? 1 : 0) - (b.value === "" ? 1 : 0) || b.deals - a.deals || a.label.localeCompare(b.label));
}

/** The ten AI-tagged deals with the most MW stated, and the ten with the most US dollars stated. */
export function largest(deals: Deal[], by: "mw" | "usd", n = 10): Deal[] {
  const f = (d: Deal) => (by === "mw" ? d.mw : d.dollars);
  return deals.filter((d) => d.ai && f(d) !== null).sort((a, b) => f(b)! - f(a)! || a.id.localeCompare(b.id)).slice(0, n);
}

/** The check key of a figure: deals|ai_<deals|mw|with_mw|usd|with_usd>|<dimension>|<value> ("-" for not stated). */
export const aiKey = (stat: "deals" | "mw" | "with_mw" | "usd" | "with_usd", dim: string, value: string) =>
  `deals|ai_${stat}|${dim}|${value === "" ? "-" : value}`;

// ---------------------------------------------------------------------------------------------------------------------
// Session 2241 (chain 156): the deals' four charts (/deals?view=charts). 1. MW stated by quarter and kind of supply
// (five groups); 2. the prices stated per MWh over time, by technology; 3. the AI-power deals' share of the MW stated,
// by quarter; 4. the counterparties with the most MW stated. Every figure has a key, deals|chart_<chart>|<x>|<series>,
// which scripts/check_deals.py recomputes from the warehouse's CSV by its own code and compares with these functions
// (site/scripts/deals-figures.mjs). A sum is of the stated figures; the deals that state none are counted beside it.

/** The five groups of chart 1, in the brand's series order (docs/brand.md, "Chart series"). */
export const GROUPS: [string, string, string][] = [
  ["nuclear", "Nuclear", "var(--chart-ink)"], ["gas", "Gas", "var(--color-accent)"],
  ["renewables_storage", "Renewables and storage", "var(--chart-blue)"], ["grid", "Grid supply", "var(--chart-grey)"],
  ["other", "Compute, capital and other", "var(--chart-light)"],
];
export const groupOf = (d: Deal): string => {
  const s = supplyOf(d);
  return ["nuclear", "gas", "renewables_storage", "grid"].includes(s) ? s : "other";
};

export type Stack = { quarter: string; parts: { group: string; mw: number; deals: number }[]; total: number; without: number };

/** Chart 1: by quarter, the MW stated by each group, and the deals of the quarter that state no MW. */
export function mwByQuarter(deals: Deal[]): Stack[] {
  const qs = [...new Set(deals.map(quarterOf))].sort();
  return qs.map((q) => {
    const inQ = deals.filter((d) => quarterOf(d) === q);
    const parts = GROUPS.map(([g]) => {
      const ds = inQ.filter((d) => groupOf(d) === g && d.mw !== null);
      return { group: g, mw: ds.reduce((a, d) => a + d.mw!, 0), deals: ds.length };
    });
    return { quarter: q, parts, total: parts.reduce((a, p) => a + p.mw, 0), without: inQ.filter((d) => d.mw === null).length };
  });
}

/** Chart 2: every priced PPA or offtake as a point; its technology folded to the four most common, else "other". */
export function pricePoints(deals: Deal[]): { id: string; date: string; price: number; tech: string; label: string }[] {
  const p = deals.filter((d) => ["ppa", "offtake"].includes(d.type) && d.price !== null);
  const counts = new Map<string, number>();
  for (const d of p) counts.set(d.technology || "not stated", (counts.get(d.technology || "not stated") ?? 0) + 1);
  const top = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 4).map(([t]) => t);
  return p.map((d) => {
    const t = d.technology || "not stated";
    return { id: d.id, date: d.date, price: d.price!, tech: top.includes(t) ? t : "other",
      label: [d.buyerName || d.buyer, d.sellerName || d.seller].filter(Boolean).join(" / ") || "parties not stated" };
  }).sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
}

export type Share = { quarter: string; aiMw: number; allMw: number; share: number | null; aiDeals: number; deals: number };

/** Chart 3: by quarter, the AI-power deals' share of the MW stated (null where no deal of the quarter states MW). */
export function aiShare(deals: Deal[]): Share[] {
  const qs = [...new Set(deals.map(quarterOf))].sort();
  return qs.map((q) => {
    const inQ = deals.filter((d) => quarterOf(d) === q);
    const withMw = inQ.filter((d) => d.mw !== null);
    const allMw = withMw.reduce((a, d) => a + d.mw!, 0), aiMw = withMw.filter((d) => d.ai).reduce((a, d) => a + d.mw!, 0);
    return { quarter: q, aiMw, allMw, share: allMw > 0 ? Math.round((1000 * aiMw) / allMw) / 10 : null,
      aiDeals: inQ.filter((d) => d.ai).length, deals: inQ.length };
  });
}

/** Chart 4: the counterparties with the most MW stated (each deal counted once for each of its two parties). */
export function topParties(deals: Deal[], n = 10): { name: string; mw: number; deals: number; withMw: number }[] {
  const by = new Map<string, { mw: number; deals: number; withMw: number }>();
  for (const d of deals) {
    const names = [...new Set([d.buyerName || d.buyer, d.sellerName || d.seller].flatMap((x) => x.split("; ")).map((x) => x.trim()).filter(Boolean))];
    for (const name of names) {
      const e = by.get(name) ?? { mw: 0, deals: 0, withMw: 0 };
      e.deals += 1;
      if (d.mw !== null) { e.mw += d.mw; e.withMw += 1; }
      by.set(name, e);
    }
  }
  return [...by.entries()].filter(([, e]) => e.withMw > 0).map(([name, e]) => ({ name, ...e }))
    .sort((a, b) => b.mw - a.mw || a.name.localeCompare(b.name)).slice(0, n);
}

/** Every figure of the four charts, by its key (what check_deals.py compares). */
export function figures(deals: Deal[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const s of mwByQuarter(deals)) {
    for (const p of s.parts) out[`deals|chart_mw|${s.quarter}|${p.group}`] = p.mw;
    out[`deals|chart_mw|${s.quarter}|without`] = s.without;
  }
  for (const p of pricePoints(deals)) out[`deals|chart_price|${p.id}|price`] = p.price;
  for (const s of aiShare(deals)) {
    if (s.share !== null) out[`deals|chart_ai|${s.quarter}|share`] = s.share;
    out[`deals|chart_ai|${s.quarter}|ai_mw`] = s.aiMw;
    out[`deals|chart_ai|${s.quarter}|all_mw`] = s.allMw;
  }
  for (const p of topParties(deals)) out[`deals|chart_party|${p.name}|mw`] = p.mw;
  return out;
}
