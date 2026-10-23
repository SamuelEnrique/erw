// Energy Research Warehouse (ERW) site, session 822: the deal tracker's public rows.
//
// energy_deals is held whole for a license (lib/license.ts; session 465): every deal was extracted from news stories
// and the outlets' pages ask for permission. Chain 080 sorts the deals by the publishers of their evidence rows
// (warehouse/deals/public_rows.py, session 821): a deal at least one of whose evidence rows comes from a publisher whose
// terms the ERW reads as public (docs/licenses.md, "may be public") is shown, with that evidence as its source and no
// held outlet's name or address; a deal every row of which asks for permission is held and counted; a deal resting on
// a publisher whose page was not read is unsettled and counted. The reader writes site/data/deals_public.json from the
// archive's copy of the two tables; the live set is not asked for a held table's rows (lib/supabase.ts throws), so the
// shown rows come from that file, each row as the live set would serve it, and scripts/check-values.mjs reads each
// shown row's figures again from the live set by its id (dealpub|<id>|mw, |dollars) and the counts against the live
// set's row count (dealpub|counts|shown is the live count less the held and the unsettled of the file: a stale file
// fails the check). Pure functions, no imports: Node runs this file as it is for tests/test_session822.py.

export type PublicEvidence = { publisher: string; url: string; date: string };

/** A shown row of site/data/deals_public.json: the live set's row shape (lib/data.ts DealRow) with its public evidence. */
export type PublicDealRow = {
  event_id: string; event_date: string; event_type: string; parties: string | null; entity_ids: string | null;
  mw: number | null; price: number | null; currency: string | null; status: string | null; source: string; source_url: string;
  extra: Record<string, string>;
  public_evidence: PublicEvidence[];
  /** how many publishers whose terms ask for permission, or are not read, also carry the deal: a count, never a name */
  other_publishers: number;
};

export type PublicDealsFile = {
  written_by: string;
  retrieved: string;
  rule: string;
  counts: { shown: number; held: number; unsettled: number };
  /** session 823: the held and unsettled deals by the month of their date, a count a month and nothing of a row */
  held_by_month?: Record<string, number>;
  shown: PublicDealRow[];
};

// Session 823: the tracker's and the comparables' figures over the shown rows only. The keys name the public family so
// that components/Num.tsx draws them (a deals| key names the held table); scripts/check-values.mjs recomputes each from
// the live set's rows whose ids the file lists as shown, through lib/deals2.ts's own functions.
export type TrackerStat = "deals" | "mw" | "with_mw" | "with_price" | "with_dollars" | "dollars";
/** dealpub|tracker|all|<stat> (every shown deal) and dealpub|tracker|selection|<stat> (the page with no selection: the same). */
export const trackerKey = (scope: "all" | "selection", stat: TrackerStat): string => `dealpub|tracker|${scope}|${stat}`;
/** dealpub|comp_<stat>|<dimension>|<value>, as lib/deals2.ts compKey names the held table's. */
export const compPubKey = (stat: "deals" | "with_price" | "with_mw" | "median_price" | "median_mw", dim: string, value: string): string =>
  `dealpub|comp_${stat}|${dim}|${value === "" ? "-" : value}`;

/** The words of the hover tip beside a figure computed over the shown rows only. */
export function shownOnlyTip(c: { shown: number; held: number; unsettled: number }): string {
  const other = c.held + c.unsettled;
  return `Computed over the ${c.shown} shown ${c.shown === 1 ? "deal" : "deals"} only; ${other} held or unsettled ${other === 1 ? "deal is" : "deals are"} not counted (license needed).`;
}

/** The tracker's months with the held counts beside the shown: the range runs from the first month of either to the
 * last, a month with neither is a zero. `shown` is lib/deals2.ts months() over the shown rows. */
export function monthsWithHeld(shown: { month: string; n: number }[], held: Record<string, number> | undefined): { month: string; n: number; held: number }[] {
  const h = held ?? {};
  const keys = [...shown.map((m) => m.month), ...Object.keys(h)].sort();
  if (!keys.length) return [];
  const n = new Map(shown.map((m) => [m.month, m.n]));
  const out: { month: string; n: number; held: number }[] = [];
  let [y, m] = keys[0].split("-").map(Number);
  const last = keys[keys.length - 1];
  for (;;) {
    const k = `${y}-${String(m).padStart(2, "0")}`;
    out.push({ month: k, n: n.get(k) ?? 0, held: h[k] ?? 0 });
    if (k >= last) break;
    if (++m > 12) { m = 1; y++; }
  }
  return out;
}

// Session 825: the FERC EQR rows beside a shown deal (warehouse/deals/eqr_join.py, site/data/deals_eqr.json): the
// count of filed contracts whose seller and buyer are the deal's parties, in the deal's quarter and in any quarter the
// warehouse holds. ferc_eqr_contracts is internal by the ERW's own record, so the file carries counts and words only
// (no filed term), and the panel on the row draws "license needed" where the terms would be. The count's key is
// dealpub|eqr|<deal>|in_quarter or |any_quarter; scripts/check-values.mjs reads it from the file once the live set's
// summary says the table is the one the file was joined against (its row count).
export type EqrDealRow = { quarter: string; how: string; in_quarter: number; any_quarter: number; products: string[]; quarters: string[] };
export type EqrFile = { written_by: string; contracts_rows: number; quarters_held: string[]; rule: string; deals: Record<string, EqrDealRow> };
export const eqrKey = (id: string, scope: "in_quarter" | "any_quarter"): string => `dealpub|eqr|${id}|${scope}`;

/** The panel's sentence for one deal: what was looked for, what was found, and that the terms are held. */
export function eqrWords(e: EqrDealRow, quartersHeld: string[]): string {
  const q = e.quarter.replace("_", " ");
  const held = quartersHeld.map((x) => x.replace("_", " ")).join(", ") || "none";
  const looked = e.how === "two parties" ? "a filed contract whose seller and buyer are two of this deal's parties" : "a filed contract naming this deal's one party as seller or buyer";
  const inQ = quartersHeld.includes(e.quarter)
    ? `${e.in_quarter} ${e.in_quarter === 1 ? "row matches" : "rows match"} in ${q}`
    : `${q}'s filings are not held yet (a quarter's reports are filed after it ends)`;
  const any = `${e.any_quarter} ${e.any_quarter === 1 ? "row matches" : "rows match"} in the ${quartersHeld.length === 1 ? "quarter" : "quarters"} held (${held})`;
  return `Looked for ${looked}: ${inQ}; ${any}.`;
}

// Session 826: two deals compared side by side (app/deals/Compare.tsx). The pair is read from the address (?a=, ?b=),
// each an id of a shown row; anything else is no pair, with the reason. USD per MW is the one figure computed there.
export const abKey = (id: string, stat: "usd_per_mw"): string => `dealpub|ab|${id}|${stat}`;
export function abPair(sp: Record<string, string | undefined>, ids: string[]): { a: string | null; b: string | null; why: string } {
  const a = sp.a && ids.includes(sp.a) ? sp.a : null;
  const b = sp.b && ids.includes(sp.b) ? sp.b : null;
  if (a && b && a !== b) return { a, b, why: "" };
  if (a && b) return { a, b: null, why: "A and B are the same deal: choose two." };
  if ((sp.a && !a) || (sp.b && !b)) return { a, b, why: "A deal in the address is not one of the shown rows, so it is not drawn." };
  return { a, b, why: "Choose two of the shown deals above." };
}
/** The value over the size, only where the deal states both; null otherwise (nothing is estimated). */
export function usdPerMw(d: { mw: number | null; dollars: number | null }): number | null {
  return d.mw !== null && d.mw > 0 && d.dollars !== null ? d.dollars / d.mw : null;
}

export const SORTS = ["shown", "held", "unsettled"] as const;
export type Sort = (typeof SORTS)[number];

/** The check key of a count: dealpub|counts|shown, |held, |unsettled. */
export const countKey = (sort: Sort): string => `dealpub|counts|${sort}`;
/** The check key of a shown row's figure: dealpub|<deal id>|mw, |dollars. */
export const rowKey = (id: string, field: "mw" | "dollars"): string => `dealpub|${id}|${field}`;

/** The three counts as the page draws them, from the file; the total is what the live set must hold. */
export function publicCounts(file: Pick<PublicDealsFile, "counts" | "shown">): { shown: number; held: number; unsettled: number; total: number } {
  const { held, unsettled } = file.counts;
  const shown = file.shown.length;
  return { shown, held, unsettled, total: shown + held + unsettled };
}

/** True when the file is consistent: its shown count is its rows, every row has public evidence, and no row's source,
 * source_url or story_urls is outside its public evidence (no held outlet's address). The page refuses a file that fails. */
export function fileIsSound(file: PublicDealsFile): boolean {
  if (file.counts.shown !== file.shown.length) return false;
  for (const r of file.shown) {
    if (!r.public_evidence.length) return false;
    const urls = new Set(r.public_evidence.map((e) => e.url));
    const pubs = new Set(r.public_evidence.map((e) => e.publisher));
    if (!urls.has(r.source_url) || !pubs.has(r.source)) return false;
    for (const u of (r.extra.story_urls ?? "").split(";").filter(Boolean)) if (!urls.has(u)) return false;
  }
  return true;
}

/** The words above the table (docs/brand.md: a cell that holds nothing says so, never a dash; the catalogue's words
 * for a held figure are "license needed"). Returned as parts so the page can key each count. */
export function heldLine(c: { shown: number; held: number; unsettled: number }): { held: string; unsettled: string; shown: string } {
  return {
    held: `${c.held === 1 ? "deal rests" : "deals rest"} on publishers whose terms ask for permission; license needed.`,
    unsettled: c.unsettled ? `${c.unsettled === 1 ? "deal rests" : "deals rest"} on a publisher whose terms have not been read.` : "",
    shown: `${c.shown === 1 ? "deal is" : "deals are"} shown: each rests on a source whose terms the ERW reads as public, named on the row.`,
  };
}
