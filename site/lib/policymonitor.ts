// Session 3060 (chain 166): the policy monitor's view of /policy (?view=monitor). Every value comes from one file,
// data/policy/monitor.json, which warehouse/policy/monitor_site.py builds from policy_actions and policy_reads: one row
// a record (the documents that name one proceeding), with its body, instrument, status, sector, grids, states, highest
// significance, next step, figure, impact sentence and sources. This module only filters, sorts and counts those rows;
// it computes no figure of its own. Tested by scripts/test-policy-monitor.mjs.

export type Step = { step: string; date: string; words: string };
export type Figure = { value: number; unit: string; words: string; event_id: string };
export type Impact = { text: string; quote: string; model: string; event_id: string };
export type MonitorRow = {
  id: string; date: string; first: string; body: string; instrument: string; title: string; status: string;
  sector?: string; significance?: number; grids?: string[]; states?: string[]; n: number;
  next?: Step; figure?: Figure; impact?: Impact; plain?: string; bears_on: { table: string; page: string };
  sources?: string[]; news?: string[]; history?: string[]; docket?: string;
};
export type MonitorFile = { built: string; documents: number; records: number; fields_from: Record<string, number>; about: string; rows: MonitorRow[] };

/** The words a reader sees for each instrument and status of the file (warehouse/policy/fields.py's vocabularies). */
export const INSTRUMENT_WORDS: Record<string, string> = {
  rule: "Final rule", proposed_rule: "Proposed rule", order: "Order", guidance: "Guidance", approval: "Approval",
  lease_sale: "Lease sale", award: "Award", application: "Application", complaint: "Complaint",
  environmental_review: "Environmental review", meeting: "Meeting or hearing", decision: "Decision", notice: "Notice",
  announcement: "Announcement",
};
export const STATUS_WORDS: Record<string, string> = {
  proposed: "Proposed", final: "Final", effective: "In effect", stayed: "Stayed", vacated: "Vacated", withdrawn: "Withdrawn",
  filed: "Filed", open: "Open for comment", scheduled: "Scheduled", issued: "Issued", announced: "Announced",
};
export const GRID_WORDS: Record<string, string> = { ercot: "ERCOT", pjm: "PJM", miso: "MISO", caiso: "CAISO", nyiso: "NYISO", isone: "ISO-NE", spp: "SPP" };

export type Filters = {
  bodies: string[]; instruments: string[]; sectors: string[]; grids: string[]; states: string[]; statuses: string[];
  from: string; to: string; minSig: number | null;
};
export const NO_FILTERS: Filters = { bodies: [], instruments: [], sectors: [], grids: [], states: [], statuses: [], from: "", to: "", minSig: null };
/** The view opens on what a reader came for: every record of significance 5 or more, any date. */
export const OPEN_FILTERS: Filters = { ...NO_FILTERS, minSig: 5 };

const any = (chosen: string[], have: string[] | undefined) => chosen.length === 0 || (have ?? []).some((x) => chosen.includes(x));
const one = (chosen: string[], v: string | undefined) => chosen.length === 0 || (v !== undefined && chosen.includes(v));

/** The rows the filters leave. A filter left empty holds every row; a row's date is its newest document's. */
export function filterRows(rows: MonitorRow[], f: Filters): MonitorRow[] {
  return rows.filter((r) =>
    one(f.bodies, r.body) && one(f.instruments, r.instrument) && one(f.sectors, r.sector) && any(f.grids, r.grids) &&
    any(f.states, r.states) && one(f.statuses, r.status) && (!f.from || r.date >= f.from) && (!f.to || r.date <= f.to) &&
    (f.minSig === null || (r.significance ?? -1) >= f.minSig));
}

export type SortKey = "date" | "body" | "instrument" | "title" | "status" | "sector" | "significance" | "next" | "figure" | "n";
export const SORT_KEYS: SortKey[] = ["date", "body", "instrument", "title", "status", "sector", "significance", "next", "figure", "n"];

/** One row's value for a sort key; an empty value always sorts last, whichever the direction. */
function keyOf(r: MonitorRow, k: SortKey): string | number | null {
  switch (k) {
    case "significance": return r.significance ?? null;
    case "next": return r.next?.date ?? null;
    case "figure": return r.figure ? r.figure.value : null;
    case "n": return r.n;
    case "sector": return r.sector ?? null;
    default: return (r as unknown as Record<string, string>)[k] ?? null;
  }
}

/** The rows sorted on one column (every column sorts); ties keep the newest first, then the record id. */
export function sortRows(rows: MonitorRow[], k: SortKey, dir: "asc" | "desc"): MonitorRow[] {
  const s = dir === "asc" ? 1 : -1;
  return [...rows].sort((a, b) => {
    const x = keyOf(a, k), y = keyOf(b, k);
    if (x === null && y !== null) return 1;
    if (y === null && x !== null) return -1;
    if (x !== null && y !== null && x !== y) return (x < y ? -1 : 1) * s;
    return a.date !== b.date ? (a.date < b.date ? 1 : -1) : a.id < b.id ? -1 : 1;
  });
}

export type Option = { key: string; label: string; n: number };

/** Each filter's choices, with how many rows of the file hold each, most first (ties by name). */
export function options(rows: MonitorRow[]): Record<"bodies" | "instruments" | "sectors" | "grids" | "states" | "statuses", Option[]> {
  const count = (vals: (string | undefined)[][], label: (k: string) => string): Option[] => {
    const m = new Map<string, number>();
    for (const vs of vals) for (const v of new Set(vs.filter(Boolean) as string[])) m.set(v, (m.get(v) ?? 0) + 1);
    return [...m.entries()].map(([key, n]) => ({ key, label: label(key), n })).sort((a, b) => b.n - a.n || (a.label < b.label ? -1 : 1));
  };
  return {
    bodies: count(rows.map((r) => [r.body]), (k) => k),
    instruments: count(rows.map((r) => [r.instrument]), (k) => INSTRUMENT_WORDS[k] ?? k),
    sectors: count(rows.map((r) => [r.sector]), (k) => k.replace(/_/g, " ")),
    grids: count(rows.map((r) => r.grids ?? []), (k) => GRID_WORDS[k] ?? k),
    states: count(rows.map((r) => r.states ?? []), (k) => k),
    statuses: count(rows.map((r) => [r.status]), (k) => STATUS_WORDS[k] ?? k),
  };
}

/** The filters an address names (?body=FERC,NRC&instrument=order&...&from=2026-10-01&sig=5), so a view can be linked. */
export function filtersOf(q: Record<string, string | undefined>): Filters {
  const list = (k: string) => (q[k] ? q[k]!.split(",").map((s) => s.trim()).filter(Boolean) : []);
  const date = (k: string) => (q[k] && /^\d{4}-\d{2}-\d{2}$/.test(q[k]!) ? q[k]! : "");
  const sig = q.sig === "all" ? null : q.sig && /^\d+$/.test(q.sig) ? Math.min(10, Number(q.sig)) : OPEN_FILTERS.minSig;
  return { bodies: list("body"), instruments: list("instrument"), sectors: list("sector"), grids: list("grid"), states: list("state"),
    statuses: list("status"), from: date("from"), to: date("to"), minSig: sig };
}

/** The address of a set of filters (the inverse of filtersOf). */
export function hrefOf(f: Filters): string {
  const p: string[] = ["view=monitor"];
  const add = (k: string, v: string[]) => { if (v.length) p.push(`${k}=${v.map(encodeURIComponent).join(",")}`); };
  add("body", f.bodies); add("instrument", f.instruments); add("sector", f.sectors); add("grid", f.grids); add("state", f.states); add("status", f.statuses);
  if (f.from) p.push(`from=${f.from}`);
  if (f.to) p.push(`to=${f.to}`);
  if (f.minSig !== OPEN_FILTERS.minSig) p.push(`sig=${f.minSig === null ? "all" : f.minSig}`);
  return `/policy?${p.join("&")}`;
}

const cell = (v: string | number | undefined | null) => {
  const s = v === undefined || v === null ? "" : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
export const CSV_COLS = ["record_id", "date", "first_date", "body", "instrument", "status", "title", "sector", "significance", "grids", "states",
  "next_step", "next_step_date", "next_step_words", "figure_value", "figure_unit", "figure_words", "impact", "bears_on_table",
  "documents", "docket", "sources", "news"] as const;

/** The filtered rows as CSV, with every source, so a reader takes away what they see and where each value is from. */
export function toCsv(rows: MonitorRow[], built: string): string {
  const lines = [`# ERW policy monitor: ${rows.length} records as filtered on the page, from data/policy/monitor.json (built ${built} by warehouse/policy/monitor_site.py from policy_actions and policy_reads). Method: docs/methods/policy_monitor.md.`,
    CSV_COLS.join(",")];
  for (const r of rows) {
    lines.push([r.id, r.date, r.first, r.body, r.instrument, r.status, r.title, r.sector, r.significance, (r.grids ?? []).join(";"), (r.states ?? []).join(";"),
      r.next?.step, r.next?.date, r.next?.words, r.figure?.value, r.figure?.unit, r.figure?.words, r.impact?.text, r.bears_on.table, r.n, r.docket,
      (r.sources ?? []).join(" "), (r.news ?? []).join(" ")].map(cell).join(","));
  }
  return lines.join("\n") + "\n";
}

/** A figure as the file holds it, in its unit: USD in millions or billions, others with their unit. */
export function figureText(f: Figure): string {
  if (f.unit === "USD") {
    const v = f.value;
    return v >= 1e9 ? `USD ${(v / 1e9).toLocaleString("en-US", { maximumFractionDigits: 2 })} billion`
      : v >= 1e6 ? `USD ${(v / 1e6).toLocaleString("en-US", { maximumFractionDigits: 2 })} million` : `USD ${v.toLocaleString("en-US")}`;
  }
  return `${f.value.toLocaleString("en-US")} ${f.unit}`;
}
