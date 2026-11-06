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
  next?: Step; steps?: { kind: string; date: string; words: string; event_id: string }[]; figure?: Figure; impact?: Impact; plain?: string; bears_on: { table: string; page: string };
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

// Session 3061 (chain 166): the calendar. A record's steps are every dated step its documents state (the file's
// `steps`, warehouse/policy/monitor_site.py), each with the words it stands in and its document; the calendar shows the
// actions of the past week and the steps of the month ahead. Each date and each figure the page shows carries a key
// that scripts/check_policy.py traces to its row of policy_actions.
export type CalStep = { kind: string; date: string; words: string; event_id: string };
export const KIND_WORDS: Record<string, string> = {
  effective: "takes effect", expires: "ends", comments_due: "comments due", intervention_due: "interventions or hearing requests due",
  review_due: "environmental document due", decision_due: "decision due", meeting: "meeting or session",
};

const day = (iso: string, plus: number) => {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + plus);
  return d.toISOString().slice(0, 10);
};

export type Calendar = { today: string; weekFrom: string; aheadTo: string; week: MonitorRow[]; ahead: { row: MonitorRow; step: CalStep }[] };

/** The past week's actions (a record whose newest document is dated in the seven days to today, newest first) and the
 *  month ahead's steps (every step dated from today to thirty days on, soonest first). */
export function calendarOf(rows: MonitorRow[], today: string): Calendar {
  const weekFrom = day(today, -7), aheadTo = day(today, 30);
  const week = rows.filter((r) => r.date >= weekFrom && r.date <= today).sort((a, b) => (a.date !== b.date ? (a.date < b.date ? 1 : -1) : a.id < b.id ? -1 : 1));
  const ahead: { row: MonitorRow; step: CalStep }[] = [];
  for (const r of rows) for (const s of ((r as MonitorRow & { steps?: CalStep[] }).steps ?? [])) if (s.date >= today && s.date <= aheadTo) ahead.push({ row: r, step: s });
  ahead.sort((a, b) => (a.step.date !== b.step.date ? (a.step.date < b.step.date ? -1 : 1) : a.row.id < b.row.id ? -1 : a.row.id > b.row.id ? 1 : a.step.kind < b.step.kind ? -1 : 1));
  return { today, weekFrom, aheadTo, week, ahead };
}

/** The check key of a step the page shows: scripts/check_policy.py finds the step in its document's row. */
export const stepKey = (r: MonitorRow, s: { kind: string; date: string; event_id?: string }) => `policycal|${r.id}|${s.event_id ?? ""}|${s.kind}|${s.date}`;
/** The check key of a figure the page shows. */
export const figureKey = (r: MonitorRow) => (r.figure ? `policyfig|${r.id}|${r.figure.event_id}|${r.figure.value}|${r.figure.unit}` : "");

/** Every key the monitor's page can show, with the values a check needs, as scripts/policy-figures.mjs prints them. */
export function keysOf(file: MonitorFile): { key: string; record: string; event_id: string; kind: string; date?: string; value?: number; unit?: string }[] {
  const out: { key: string; record: string; event_id: string; kind: string; date?: string; value?: number; unit?: string }[] = [];
  for (const r of file.rows) {
    for (const s of ((r as MonitorRow & { steps?: CalStep[] }).steps ?? [])) out.push({ key: stepKey(r, s), record: r.id, event_id: s.event_id, kind: s.kind, date: s.date });
    if (r.figure) out.push({ key: figureKey(r), record: r.id, event_id: r.figure.event_id, kind: "figure", value: r.figure.value, unit: r.figure.unit });
  }
  // session 3062: the charts' sums, each with the records whose figures it adds
  for (const s of figureSums(file.rows)) out.push({ key: sumKey(s), record: s.records.join(";"), event_id: "", kind: "sum", date: s.month, value: s.value, unit: s.unit });
  return out;
}

// Session 3062 (chain 166): the monitor's charts and downloads. The charts describe every record of the file (not the
// filtered set), so each summed figure has one value that scripts/check_policy.py can trace; the counts and sums are
// of the records' own fields, nothing estimated.
export const monthOf = (iso: string) => iso.slice(0, 7);
export function monthsOf(rows: MonitorRow[]): string[] {
  return [...new Set(rows.map((r) => monthOf(r.date)))].sort();
}

/** Records by month of their newest document, one series a body: the `top` bodies by count, the rest as "Other". */
export function byBodyMonth(rows: MonitorRow[], top = 6): { months: string[]; series: { name: string; values: number[] }[] } {
  const months = monthsOf(rows);
  const count = new Map<string, number>();
  for (const r of rows) count.set(r.body, (count.get(r.body) ?? 0) + 1);
  const named = [...count.entries()].sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1)).slice(0, top).map(([b]) => b);
  const names = [...named, ...(count.size > named.length ? ["Other"] : [])];
  const series = names.map((name) => ({ name, values: months.map((m) => rows.filter((r) => monthOf(r.date) === m && (name === "Other" ? !named.includes(r.body) : r.body === name)).length) }));
  return { months, series };
}

export const SIG_BANDS = [["0 to 4", 0, 4], ["5 to 6", 5, 6], ["7 to 10", 7, 10]] as const;
/** Records by sector, one series a band of significance (the scorer's sector and significance; a record unscored is left out). */
export function sigBySector(rows: MonitorRow[], top = 12): { sectors: string[]; series: { name: string; values: number[] }[] } {
  const scored = rows.filter((r) => r.sector && r.significance !== undefined && r.significance !== null);
  const count = new Map<string, number>();
  for (const r of scored) count.set(r.sector!, (count.get(r.sector!) ?? 0) + 1);
  const sectors = [...count.entries()].sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1)).slice(0, top).map(([s]) => s);
  return { sectors, series: SIG_BANDS.map(([name, lo, hi]) => ({ name, values: sectors.map((s) => scored.filter((r) => r.sector === s && r.significance! >= lo && r.significance! <= hi).length) })) };
}

export const SUM_UNITS = ["MW", "USD"] as const;
export type Sum = { unit: string; month: string; value: number; records: string[] };
/** The figures a record states as its own, in MW or USD, summed by month: only where disclosed, each with its records. */
export function figureSums(rows: MonitorRow[]): Sum[] {
  const out = new Map<string, Sum>();
  for (const r of rows) {
    if (!r.figure || !(SUM_UNITS as readonly string[]).includes(r.figure.unit)) continue;
    const k = `${r.figure.unit}|${monthOf(r.date)}`;
    const s = out.get(k) ?? { unit: r.figure.unit, month: monthOf(r.date), value: 0, records: [] };
    s.value += r.figure.value;
    s.records.push(r.id);
    out.set(k, s);
  }
  return [...out.values()].sort((a, b) => (a.unit !== b.unit ? (a.unit < b.unit ? -1 : 1) : a.month < b.month ? -1 : 1));
}
/** A sum's check key: scripts/check_policy.py adds the figures of its records, each traced, and compares. */
export const sumKey = (s: Sum) => `policysum|${s.unit}|${s.month}|${s.value}|${s.records.length}`;

/** A Python and a Stata reader of the CSV the page hands out (toCsv), with its provenance line skipped. */
export function pythonReader(csvName: string): string {
  return [`# ERW policy monitor: a reader of ${csvName}, the records as filtered on /policy?view=monitor.`,
    "# Method: docs/methods/policy_monitor.md. Every source of a record is in its sources column.",
    "import pandas as pd", "", `df = pd.read_csv("${csvName}", comment="#", dtype=str, keep_default_na=False)`,
    'df["significance"] = pd.to_numeric(df["significance"], errors="coerce")',
    'df["figure_value"] = pd.to_numeric(df["figure_value"], errors="coerce")', "print(df.shape)", ""].join("\n");
}
export function stataReader(csvName: string): string {
  return [`* ERW policy monitor: a reader of ${csvName}, the records as filtered on /policy?view=monitor.`,
    "* Method: docs/methods/policy_monitor.md. Every source of a record is in its sources column.",
    `import delimited using "${csvName}", varnames(2) rowrange(3) stringcols(_all) clear`,
    "destring significance figure_value documents, replace force", "describe", ""].join("\n");
}
