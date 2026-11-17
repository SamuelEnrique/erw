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
  /** Session 7019 (chain 301, done-line request 20): rows and priced rows by quarter of execution, product group and delivery authority (absent until a load after session 7019). */
  by_quarter_group_ba?: { quarter: string; group: string; ba: string; rows: number; priced: number }[];
  /** Session 99: the largest buyers and sellers, from the whole quarter's file (the loader stores it with the summary; absent until a load after session 99). */
  largest?: Largest;
  /** Session 125: megawatts, prices read from the words, tags and changes by quarter (warehouse/derived/eqr_terms.py; absent until a load after session 125). */
  terms?: Terms;
};
export type MwParty = { rank: number; name: string; mw: number; contracts_with_mw: number; contracts: number; rank_contracts: number; contracts_over: number };
export type MwList = { parties: number; mw: number; contracts_with_mw: number; top: MwParty[] };
export type Change = { quarter: string; product: string; contracts_in_force: number; rows_in_force: number; contracts_new?: number; contracts_gone?: number; contracts_kept?: number };
export type Terms = {
  quarter: string | null; top: number; rows: number; mw_ceiling: number | null;
  mw: { rows_stated: number; rows_over: number; by_product: Record<string, { contracts: number; contracts_with_mw: number; contracts_over: number }> };
  prices: { filed_number: number; none: number; words_only: number; read: number; read_usd_per_mwh: number; read_by_unit: Record<string, number>; unread: Record<string, number> };
  buyers: { rows_merged: number };
  tags: { tolling_rows: number; tolling_contracts: number; storage_rows: number; storage_words_elsewhere: Record<string, number>; storage_words_rows: number };
  by_mw: Record<"buyer" | "seller", Record<"energy" | "capacity" | "tolling", MwList>>;
  changes: Change[];
};
/** Why no price was read from a rate filed as words, in the order the rule tests them (warehouse/derived/eqr_terms.py). */
export const UNREAD = [
  { key: "no_dollar_amount", label: "No dollar amount in the words", example: "a market-based rate, a tariff's name, a formula in words" },
  { key: "several_amounts", label: "More than one dollar amount", example: "a schedule by year, peak and off-peak, tiers" },
  { key: "no_unit", label: "A dollar amount with no unit after it", example: "a deposit, a facilities charge, a figure per kW with no period" },
  { key: "conditional", label: "One amount with its unit, and a condition", example: "escalating, plus other charges, a cap, an if, a factor, a year" },
  { key: "other_numbers", label: "Another number beside it that is not a quantity", example: "an amendment's number, a schedule's number" },
  { key: "units_disagree", label: "The unit in the words is not the unit filed", example: "a capacity price derived from an energy rate" },
] as const;
/** The fields outside the product fields in which the words storage, battery or BESS stand. */
export const STORAGE_FIELDS = [
  { key: "seller_name", label: "the seller's name" }, { key: "rate_description", label: "the rate description" },
  { key: "agreement_id", label: "the agreement's identifier" }, { key: "tariff_reference", label: "the tariff reference" },
] as const;
/** The changes of one product, oldest quarter first. */
export function changesOf(t: Terms, product: string): Change[] {
  return t.changes.filter((c) => c.product === product).sort((a, b) => a.quarter.localeCompare(b.quarter));
}
export type Party = { rank: number; name: string; contracts: number; rows: number; counterparties: number; mw_filed: number; rows_with_mw: number };
export type PartyList = { parties: number; contracts: number; rows: number; top: Party[] };
export type Largest = {
  quarter: string | null; top: number;
  names: { filed: number; after_rules: number; merged_groups: number; merged_names: number; doubtful_pairs: number };
  lists: Record<"buyer" | "seller", Record<"energy" | "capacity" | "tolling", PartyList>>;
};
/** The three products of the largest buyers and sellers view. */
export const LARGEST_PRODUCTS = [
  { slug: "energy", label: "Energy" }, { slug: "capacity", label: "Capacity" }, { slug: "tolling", label: "Tolling energy" },
] as const;
export type LargestProduct = (typeof LARGEST_PRODUCTS)[number];
/** The view a reader asked for: the contracts by quarter signed (the page as it was), or the largest buyers and sellers. */
export function viewOf(q: Record<string, string | undefined>): { view: "quarter" | "largest" | "mw" | "terms"; product: LargestProduct } {
  const view = q.view === "largest" || q.view === "mw" || q.view === "terms" ? q.view : "quarter";   // session 125: by megawatts stated, and what the filings state
  return { view, product: LARGEST_PRODUCTS.find((p) => p.slug === q.product) ?? LARGEST_PRODUCTS[0] };
}
export const largestHref = (product: string) => `/contracts?view=largest&product=${product}`;
export const mwHref = (product: string) => `/contracts?view=mw&product=${product}`;

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
  const ba = q.ba && /^[A-Za-z0-9 ._-]{1,40}$/.test(q.ba) ? baOf(q.ba) : null;   // session 7501: as the panel names it
  return { quarter, product, ba };
}

const up = (v: string | null) => (v ?? "").trim().toUpperCase();

/** Session 7501: a balancing authority is compared as the panel lists it (byBa below): trimmed, and "not stated" for a
 * row that files none. Until then the panel's largest entry, "not stated", opened a list of no rows: the filter looked
 * for a row whose balancing authority was the words "not stated". */
export function filter(rows: Contract[], product: Product, ba: string | null): Contract[] {
  return rows.filter((r) => product.match(up(r.product)) && (!ba || baOf(r.pod_ba) === baOf(ba)));
}

/** Session 7501: a balancing authority as the panel names it: FERC's code trimmed and in capitals (filers write "PSCO"
 * and "PSCo", "HUB" and "Hub": one authority, as a product's two spellings are one product), "not stated" for none. */
export function baOf(v: string | null): string {
  const s = up(v);
  return s === "" || s === "NOT STATED" ? "not stated" : s;
}

/** Session 7501: the day a listed quarter is held from, when that is after the quarter's first day (the live set keeps
 * the rows executed in the 1,000 days before a load, so the oldest quarter listed is held in part); null for a quarter
 * held whole or when no first day is known. */
export function heldFrom(quarter: string, first: string | null): string | null {
  if (!first || !/^\d{4}-\d{2}-\d{2}$/.test(first)) return null;
  const d = quarterDates(quarter);
  return first > d.from && first < d.to ? first : null;
}

/** Session 7501: the contracts in force of one product in the newest quarter filed for (the last row of "Contracts new
 * and gone"); null when the summary holds no such row. */
export function inForce(t: Terms, product: string): number | null {
  const c = changesOf(t, product).at(-1);
  return c ? c.contracts_in_force : null;
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

/** Session 7510: the days of a term the page draws as under one year (0.9 years or less to its one decimal), the first
 * and the last day both counted, so that a strip of one month reads 30 days beside its "0.1 years"; null for a longer
 * term or for none. */
export function termDays(r: Contract): number | null {
  const y = termYears(r);
  return y === null || Number(y.toFixed(1)) >= 1 ? null : Math.round(y * 365.25) + 1;
}

/** Session 7510: a count's noun, "row" for 1 and "rows" for any other count. */
export const some = (n: number, one: string, many = `${one}s`) => (n === 1 ? one : many);

/** Session 7510: the seven grids' balancing authority codes that are not the grid's own name, as lib/gridtool.ts names
 * them (CISO is CAISO, SWPP is SPP): the page gives the name on hover. A code the site names nowhere stays as filed. */
export function baName(code: string, grids: readonly { ba: string; label: string; name: string }[]): string | null {
  const g = grids.find((x) => x.ba === code);
  return g && g.label !== code ? `${g.name} (${g.label})` : null;
}

/** Session 7510: the quarter an address names when it is none of the quarters listed (the page then shows its newest
 * quarter and says so); null when the address names none, names a listed one, or holds anything but plain characters. */
export function quarterNotListed(q: string | undefined, held: string[]): string | null {
  return q && !held.includes(q) && /^[A-Za-z0-9 _-]{1,20}$/.test(q) ? q : null;
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

/** Session 7510: the rows whose rate is the number 0. A rate of zero is filed as a number, so `counts` has it among the
 * priced rows; the page says how many they are. Its own function: `counts` stays what session 83's test holds it to. */
export function zeroPriced(rows: Contract[]): number {
  return rows.filter((r) => (r.rate ?? "").trim() !== "" && Number((r.rate ?? "").trim()) === 0).length;
}

/** Ruling alternative 3 of /contracts (session 7701, branch wip/alt-contracts-3; not a default on main): a row whose
 * buyer is a market operator (PJM, MISO, SPP, ERCOT, CAISO, ISO New England, NYISO, or any "independent system
 * operator" or regional transmission organisation, by the words of the buyer's name as filed) is a sale into the market,
 * not a contract with a party, and is left out of the rows signed. The list of names is this branch's default, not a
 * ruling (docs/reviews/ruling-impact-contracts-2026-11-17.md, "What a ruling would also have to fix"). */
export const OPERATOR_BUYER = /\bPJM\b|MIDCONTINENT INDEPENDENT|\bMISO\b|MIDWEST INDEPENDENT TRANSMISSION|SOUTHWEST POWER POOL|\bSPP\b|ELECTRIC RELIABILITY COUNCIL|\bERCOT\b|CALIFORNIA INDEPENDENT SYSTEM|\bCAISO\b|\bISO NEW ENGLAND|\bISO-NE\b|NEW YORK INDEPENDENT SYSTEM|\bNYISO\b|INDEPENDENT SYSTEM OPERATOR|REGIONAL TRANSMISSION ORG/i;
export const isOperatorBuyer = (r: Contract) => OPERATOR_BUYER.test(r.buyer ?? "");
export const withoutOperators = (rows: Contract[]) => rows.filter((r) => !isOperatorBuyer(r));

/** The delivery balancing authorities of the rows, most rows first. */
export function byBa(rows: Contract[]): { ba: string; rows: number }[] {
  const m = new Map<string, number>();
  for (const r of rows) m.set(baOf(r.pod_ba), (m.get(baOf(r.pod_ba)) ?? 0) + 1);   // session 7501: one authority, whatever its capitals
  return [...m.entries()].map(([ba, n]) => ({ ba, rows: n })).sort((a, b) => b.rows - a.rows || a.ba.localeCompare(b.ba));
}
