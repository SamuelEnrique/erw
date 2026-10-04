// Energy Research Warehouse (ERW) site, session 83: the contracts tracker (/contracts, in review). The page's model.
// The rows are FERC Electric Quarterly Report contracts (ferc_eqr_contracts, an internal table: warehouse/connectors/
// ferc_eqr_contracts.py), read through two database functions that answer only with the internal token
// (warehouse/supabase/migrations/020_eqr_contracts.sql). The page counts and filters the rows it is given and does no
// other arithmetic. No imports from the app: Node runs this file as it is.

export const TABLE = "ferc_eqr_contracts";

export type Contract = {
  event_id: string; event_date: string; status: string | null; mw: number | null; price: number | null;
  seller: string | null; buyer: string | null; affiliate: string | null; agreement: string | null;
  product_type: string | null; product: string | null; class: string | null; term: string | null;
  commencement: string | null; termination: string | null; quantity: string | null; units: string | null;
  rate: string | null; rate_units: string | null; rate_description: string | null;
  pod_ba: string | null; pod_location: string | null; quarter: string | null;
};
export type Summary = {
  rows: number; priced: number; first: string | null; last: string | null; quarters: string[];
  by_month: { month: string; rows: number; priced: number }[];
  by_product: { product: string; rows: number; priced: number }[];
  by_ba: { ba: string; rows: number }[];
};

/** The product groups a reader can pick. FERC's product names come in more than one spelling, so they are compared in
 * capitals. "power" is what a credit investor means by a contract: energy, capacity and tolling. */
export const PRODUCTS = [
  { slug: "power", label: "Energy, capacity and tolling", match: (p: string) => ["ENERGY", "CAPACITY", "TOLLING ENERGY"].includes(p) },
  { slug: "energy", label: "Energy", match: (p: string) => p === "ENERGY" },
  { slug: "capacity", label: "Capacity", match: (p: string) => p === "CAPACITY" },
  { slug: "tolling", label: "Tolling energy", match: (p: string) => p === "TOLLING ENERGY" },
  { slug: "all", label: "Every product", match: (_p: string) => true },
] as const;
export type Product = (typeof PRODUCTS)[number];

/** A quarter of execution, "2026-Q2", and its dates [from, to). */
export function quarterOf(month: string): string {
  return `${month.slice(0, 4)}-Q${Math.floor((Number(month.slice(5, 7)) - 1) / 3) + 1}`;
}
export function quarterDates(q: string): { from: string; to: string } {
  const y = Number(q.slice(0, 4)), n = Number(q.slice(6));
  const m = (n - 1) * 3 + 1;
  const pad = (v: number) => String(v).padStart(2, "0");
  return { from: `${y}-${pad(m)}-01`, to: n === 4 ? `${y + 1}-01-01` : `${y}-${pad(m + 3)}-01` };
}

/** The quarters of execution the live set holds, newest first, with their row counts. */
export function quarters(s: Summary): { quarter: string; rows: number; priced: number }[] {
  const m = new Map<string, { rows: number; priced: number }>();
  for (const b of s.by_month) {
    const q = quarterOf(b.month);
    const g = m.get(q) ?? { rows: 0, priced: 0 };
    g.rows += b.rows;
    g.priced += b.priced;
    m.set(q, g);
  }
  return [...m.entries()].map(([quarter, g]) => ({ quarter, ...g })).sort((a, b) => b.quarter.localeCompare(a.quarter));
}

/** The quarter the newest filings were made for, "2026-Q2" (the table's x_quarter is "2026_Q2"); null when none. */
export function filedQuarter(s: Summary): string | null {
  const q = s.quarters.filter((x) => /^\d{4}_Q[1-4]$/.test(x)).sort().at(-1);
  return q ? q.replace("_", "-") : null;
}

/** The quarters a reader can pick: those up to the quarter filed for. A filer's execution date after it (a contract
 * signed between the quarter's end and the filing, or a typing error: one row is dated 2915) is held as filed and
 * counted, not listed. */
export function listed(held: { quarter: string; rows: number; priced: number }[], filed: string | null) {
  const upTo = held.filter((h) => !filed || h.quarter <= filed);
  const later = held.filter((h) => filed && h.quarter > filed);
  return { upTo, laterRows: later.reduce((a, h) => a + h.rows, 0), laterLast: later.length ? later[0].quarter : null };
}

export function choices(q: Record<string, string | undefined>, held: string[]) {
  const quarter = q.q && held.includes(q.q) ? q.q : held[0] ?? null;
  const product = PRODUCTS.find((p) => p.slug === q.product) ?? PRODUCTS[0];
  const ba = q.ba && /^[A-Za-z0-9 ._-]{1,40}$/.test(q.ba) ? q.ba : null;
  return { quarter, product, ba };
}

const up = (v: string | null) => (v ?? "").trim().toUpperCase();

export function filter(rows: Contract[], product: Product, ba: string | null): Contract[] {
  return rows.filter((r) => product.match(up(r.product)) && (!ba || (r.pod_ba ?? "") === ba));
}

/** "20250723" as FERC files a date, to "2025-07-23"; anything else as filed. */
export function fercDate(v: string | null): string {
  const s = (v ?? "").trim();
  return /^\d{8}$/.test(s) ? `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6)}` : s;
}

/** The term in years, start to end, when both are dates; null otherwise (many contracts file no end). */
export function termYears(r: Contract): number | null {
  const a = fercDate(r.commencement), b = fercDate(r.termination);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(a) || !/^\d{4}-\d{2}-\d{2}$/.test(b)) return null;
  const y = (Date.parse(`${b}T00:00:00Z`) - Date.parse(`${a}T00:00:00Z`)) / (365.25 * 86400e3);
  return Number.isFinite(y) && y >= 0 ? y : null;
}

/** What the filer wrote for the price: the number with its units, or the words. Never both invented. */
export function rateText(r: Contract): { text: string; numeric: boolean } {
  const n = (r.rate ?? "").trim();
  if (n !== "") return { text: `${n}${r.rate_units ? ` ${r.rate_units}` : ""}`, numeric: true };
  const w = (r.rate_description ?? "").trim();
  return { text: w === "" ? "not stated" : w, numeric: false };
}

export function counts(rows: Contract[]) {
  const set = (f: (r: Contract) => string | null) => new Set(rows.map(f).filter((v): v is string => !!v)).size;
  return {
    rows: rows.length,
    agreements: new Set(rows.map((r) => `${r.seller}|${r.agreement}`)).size,
    sellers: set((r) => r.seller), buyers: set((r) => r.buyer),
    priced: rows.filter((r) => (r.rate ?? "").trim() !== "").length,
    affiliate: rows.filter((r) => up(r.affiliate) === "Y").length,
  };
}

/** The delivery balancing authorities of the rows, most rows first. */
export function byBa(rows: Contract[]): { ba: string; rows: number }[] {
  const m = new Map<string, number>();
  for (const r of rows) m.set((r.pod_ba ?? "").trim() || "not stated", (m.get((r.pod_ba ?? "").trim() || "not stated") ?? 0) + 1);
  return [...m.entries()].map(([ba, n]) => ({ ba, rows: n })).sort((a, b) => b.rows - a.rows || a.ba.localeCompare(b.ba));
}
