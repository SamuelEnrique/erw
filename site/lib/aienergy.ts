// Energy Research Warehouse (ERW) site, session 8012 (chain 505, part B2): the page "Energy per AI query, as published"
// reads data/ai_energy.json (warehouse/derived/ai_energy_page.py, from the table ai_energy_published; method
// docs/methods/ai_energy_published.md). This module holds the file's shape, the orders a reader can choose and the
// measures to filter by, with no import, so a test can run it under node. Nothing is computed from the figures: no
// average, no sum, no conversion, no ranking by value.

export type AiRow = {
  event_id: string; event_date: string; parties: string; source_url: string; x_publisher_kind: string; x_peer_reviewed: string;
  x_title: string; x_authors: string; x_page: string; x_printed: string; x_value: number | null; x_unit: string; x_measures: string;
  x_subject: string; x_period: string; x_basis: string; x_sha256: string; x_retrieved_at: string;
};
export type AiFile = { built: string; table: string; method: string; license: string; provenance: string[]; rows: AiRow[] };

export function readAiFile(raw: unknown): AiFile | null {
  const f = raw as AiFile | null;
  if (!f || typeof f !== "object" || !Array.isArray(f.rows) || !f.rows.length) return null;
  return f;
}

export const ORDERS = [
  { value: "publisher", label: "Publisher, A to Z" },
  { value: "measures", label: "What is measured, A to Z" },
  { value: "newest", label: "Date, newest first" },
  { value: "oldest", label: "Date, oldest first" },
] as const;
export type Order = (typeof ORDERS)[number]["value"];

/** The rows in a chosen order; ties keep the file's order. Never by the figure's size. */
export function ordered(rows: AiRow[], order: Order): AiRow[] {
  const idx = new Map(rows.map((r, i) => [r.event_id, i]));
  const tie = (a: AiRow, b: AiRow) => (idx.get(a.event_id) ?? 0) - (idx.get(b.event_id) ?? 0);
  const by: Record<Order, (a: AiRow, b: AiRow) => number> = {
    publisher: (a, b) => a.parties.localeCompare(b.parties) || a.event_date.localeCompare(b.event_date) || tie(a, b),
    measures: (a, b) => a.x_measures.localeCompare(b.x_measures) || a.parties.localeCompare(b.parties) || tie(a, b),
    newest: (a, b) => b.event_date.localeCompare(a.event_date) || tie(a, b),
    oldest: (a, b) => a.event_date.localeCompare(b.event_date) || tie(a, b),
  };
  return [...rows].sort(by[order]);
}

/** The measures as the rows word them, each once, A to Z. */
export function measures(rows: AiRow[]): string[] {
  return [...new Set(rows.map((r) => r.x_measures))].sort((a, b) => a.localeCompare(b));
}
export function publishers(rows: AiRow[]): string[] {
  return [...new Set(rows.map((r) => r.parties))].sort((a, b) => a.localeCompare(b));
}

/** A figure as the publication's number, in its own unit: digits as given, grouped, never converted. Session 11407
 *  (chain 770, the ruling readied for finding 6 of docs/reviews/ai-energy-model-audit-2026-11-26.md): when the row's
 *  printed words are given, the number is written with the digits they print ("0.10", not 0.1; "1.0×10−4", not
 *  0.0001), found as the first number of the words equal to the value; a value whose float is written with an
 *  exponent is never shown as 0. */
export function figure(v: number | null, printed?: string): string {
  if (v === null) return "";
  const p = printed ? printedDigits(v, printed) : null;
  if (p) return p;
  const s = String(v);
  if (/e/i.test(s)) return s;
  const [i, d] = s.split(".");
  return Number(i).toLocaleString("en-US") + (d ? `.${d}` : "");
}

/** The number of the printed words equal to v, with the digits printed (the integer part grouped), or null. */
export function printedDigits(v: number, printed: string): string | null {
  const re = /(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?:\s*[×x]\s*10\s*([−-]?\d+))?/g;
  for (const m of printed.matchAll(re)) {
    const int = m[1].replace(/,/g, "");
    const dec = m[2] ?? "";
    const exp = m[3] ? Number(m[3].replace("−", "-")) : 0;
    const n = Number(int + dec) * 10 ** exp;
    if (Math.abs(n - v) <= 1e-9 * Math.abs(v)) {
      return Number(int).toLocaleString("en-US") + dec + (m[3] ? `×10${m[3]}` : "");
    }
  }
  return null;
}
