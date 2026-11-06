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
