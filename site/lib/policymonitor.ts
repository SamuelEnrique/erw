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
  /** session 3129: "out of scope: <why>" for a document that is no energy action (marked, never dropped) */
  scope?: string;
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
/** Session 1876 (policy faults row 3): the scorer's sector keys as a reader reads them, in the filter, the cell and the chart. */
export const SECTOR_WORDS: Record<string, string> = {
  policy: "Policy", nuclear: "Nuclear", renewables: "Renewables", gas: "Gas", generation: "Generation", oil: "Oil", other: "Other",
  lng: "LNG", storage: "Storage", transmission: "Transmission", transport: "Transport", grid_conditions: "Grid conditions",
  power_prices: "Power prices", geopolitics: "Geopolitics", interconnection: "Interconnection", capital: "Capital",
  company: "Company", deal: "Deal",
};
export const sectorWords = (k: string | undefined): string => (k ? SECTOR_WORDS[k] ?? k.replace(/_/g, " ") : "");

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

/** Session 1876 (policy faults row 19): MW and its multiples, put in MW for the figure sort only (the cell keeps its own unit). */
export const MW_PER: Record<string, number> = { MW: 1, GW: 1000, kW: 0.001 };
/** The order of the figure's units in its sort: USD, then MW (GW and kW with it), then the others by name. */
export const figureTier = (unit: string): string => (unit === "USD" ? "0" : unit in MW_PER ? "1" : `2|${unit}`);

/** One row's value for a sort key; an empty value always sorts last, whichever the direction. */
function keyOf(r: MonitorRow, k: SortKey, today = ""): string | number | null {
  switch (k) {
    case "significance": return r.significance ?? null;
    case "next": return nextOf(r, today)?.date ?? null;
    case "figure": return r.figure ? r.figure.value * (MW_PER[r.figure.unit] ?? 1) : null;
    case "n": return r.n;
    case "sector": return r.sector ?? null;
    default: return (r as unknown as Record<string, string>)[k] ?? null;
  }
}
/** Session 1876 (rows 16 and 19): a tier sorted before the value and the same way in both directions: a figure's unit
 *  (numbers of unlike units are not compared), and a next step ahead of the page's day before one already passed. */
function tierOf(r: MonitorRow, k: SortKey, today = ""): string {
  if (k === "figure") return r.figure ? figureTier(r.figure.unit) : "";
  if (k === "next") return nextOf(r, today)?.passed ? "1" : "0";
  return "";
}

/** The rows sorted on one column (every column sorts); ties keep the newest first, then the record id. `today` is the
 *  page's day, which the next step's sort reads (session 1876). */
export function sortRows(rows: MonitorRow[], k: SortKey, dir: "asc" | "desc", today = ""): MonitorRow[] {
  const s = dir === "asc" ? 1 : -1;
  return [...rows].sort((a, b) => {
    const x = keyOf(a, k, today), y = keyOf(b, k, today);
    if (x === null && y !== null) return 1;
    if (y === null && x !== null) return -1;
    const ta = tierOf(a, k, today), tb = tierOf(b, k, today);
    if (x !== null && y !== null && ta !== tb) return ta < tb ? -1 : 1;
    // session 3123: two numbers compare as numbers, anything else as text (strict TypeScript refuses "<" on string | number)
    if (x !== null && y !== null && x !== y) return (typeof x === "number" && typeof y === "number" ? (x < y ? -1 : 1) : String(x) < String(y) ? -1 : 1) * s;
    return a.date !== b.date ? (a.date < b.date ? 1 : -1) : a.id < b.id ? -1 : 1;
  });
}

export type Option = { key: string; label: string; n: number };

type ListKey = "bodies" | "instruments" | "sectors" | "grids" | "states" | "statuses";

/** Each filter's choices, with how many rows each would show if ticked, most first (ties by name). Session 1876 (policy
 *  faults row 2): a choice counts the rows the other filters leave (the significance floor and the dates included, the
 *  list's own choice excluded), so its number is what ticking it gives; every choice of the file stays listed, at 0 if
 *  the other filters leave none. With no filters it is the count of the file's rows, as before. */
export function options(rows: MonitorRow[], f: Filters = NO_FILTERS): Record<ListKey, Option[]> {
  const count = (list: ListKey, vals: (r: MonitorRow) => (string | undefined)[], label: (k: string) => string): Option[] => {
    const keys = new Set<string>();
    for (const r of rows) for (const v of vals(r)) if (v) keys.add(v);
    const m = new Map<string, number>();
    for (const r of filterRows(rows, { ...f, [list]: [] })) for (const v of new Set(vals(r).filter(Boolean) as string[])) m.set(v, (m.get(v) ?? 0) + 1);
    return [...keys].map((key) => ({ key, label: label(key), n: m.get(key) ?? 0 })).sort((a, b) => b.n - a.n || (a.label < b.label ? -1 : 1));
  };
  return {
    bodies: count("bodies", (r) => [r.body], (k) => k),
    instruments: count("instruments", (r) => [r.instrument], (k) => INSTRUMENT_WORDS[k] ?? k),
    sectors: count("sectors", (r) => [r.sector], sectorWords),
    grids: count("grids", (r) => r.grids ?? [], (k) => GRID_WORDS[k] ?? k),
    states: count("states", (r) => r.states ?? [], (k) => k),
    statuses: count("statuses", (r) => [r.status], (k) => STATUS_WORDS[k] ?? k),
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
  "documents", "docket", "sources", "news",
  // session 1876 (policy faults row 29): the row's plain read, the impact sentence's basis, the figure's document and
  // every dated step (kind=date@document, joined by ";"), so the download holds what the page shows and where it is from
  "plain_read", "impact_quote", "impact_model", "impact_document", "figure_document", "steps", "next_step_passed"] as const;

/** Session 1876 (policy faults row 14): the impact sentence without its final "; it bears on <table> (/data#...)" clause,
 *  a table key printed as prose; the open row's "bears on" link is the one place the table is named. */
export const impactText = (t: string): string => t.replace(/;\s*it bears on [^;]*$/, ".").replace(/\.\.$/, ".");

/** The filtered rows as CSV, with every source, so a reader takes away what they see and where each value is from.
 *  `today` is the page's day: the next step is the one the page shows (nextOf). */
export function toCsv(rows: MonitorRow[], built: string, today = ""): string {
  const lines = [`# ERW policy monitor: ${rows.length} records as filtered on the page, from data/policy/monitor.json (built ${built} by warehouse/policy/monitor_site.py from policy_actions and policy_reads). Method: docs/methods/policy_monitor.md.`,
    CSV_COLS.join(",")];
  for (const r of rows) {
    const nx = nextOf(r, today);
    lines.push([r.id, r.date, r.first, r.body, r.instrument, r.status, r.title, r.sector, r.significance, (r.grids ?? []).join(";"), (r.states ?? []).join(";"),
      nx ? KIND_WORDS[nx.kind] ?? nx.kind : undefined, nx?.date, nx?.words, r.figure?.value, r.figure?.unit, r.figure?.words, r.impact ? impactText(r.impact.text) : undefined,
      r.bears_on.table, r.n, r.docket, (r.sources ?? []).join(" "), (r.news ?? []).join(" "),
      r.plain, r.impact?.quote, r.impact?.model, r.impact?.event_id, r.figure?.event_id,
      (r.steps ?? []).map((s) => `${s.kind}=${s.date}@${s.event_id}`).join(";"), nx ? (nx.passed ? "yes" : "no") : undefined].map(cell).join(","));
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
  // session 3141: a filing's deadline and a court petition's deadline (warehouse/policy/fields.py, KINDS)
  filing_due: "filings due", review_petition_due: "petitions for judicial review due",
};

const day = (iso: string, plus: number) => {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + plus);
  return d.toISOString().slice(0, 10);
};

export type Calendar = { today: string; weekFrom: string; weekTo: string; stale: boolean; aheadTo: string; week: MonitorRow[]; ahead: { row: MonitorRow; step: CalStep }[] };

/** The newest document date of a set of rows (the file's last document, when given every row of the file). */
export const lastDateOf = (rows: MonitorRow[]): string => rows.reduce((m, r) => (r.date > m ? r.date : m), "");

/** The past week's actions (a record whose newest document is dated in the seven days to today, newest first) and the
 *  month ahead's steps (every step dated from today to thirty days on, soonest first). Session 1876 (policy faults
 *  row 4): `last` is the file's newest document date; when it is before today the week is the seven days to it
 *  (`stale`), since the file holds nothing after it, and the month ahead still runs from today. */
export function calendarOf(rows: MonitorRow[], today: string, last = ""): Calendar {
  const stale = !!last && last < today;
  const weekTo = stale ? last : today;
  const weekFrom = day(weekTo, -7), aheadTo = day(today, 30);
  const week = rows.filter((r) => r.date >= weekFrom && r.date <= weekTo).sort((a, b) => (a.date !== b.date ? (a.date < b.date ? 1 : -1) : a.id < b.id ? -1 : 1));
  const ahead: { row: MonitorRow; step: CalStep }[] = [];
  for (const r of rows) for (const s of ((r as MonitorRow & { steps?: CalStep[] }).steps ?? [])) if (s.date >= today && s.date <= aheadTo) ahead.push({ row: r, step: s });
  ahead.sort((a, b) => (a.step.date !== b.step.date ? (a.step.date < b.step.date ? -1 : 1) : a.row.id < b.row.id ? -1 : a.row.id > b.row.id ? 1 : a.step.kind < b.step.kind ? -1 : 1));
  return { today, weekFrom, weekTo, stale, aheadTo, week, ahead };
}

/** Session 1876 (policy faults row 6): how many steps of the month ahead the significance floor hides, every other
 *  filter kept (the dates aside, as the calendar reads them). A deadline does not stop being one because its record
 *  scored low, so the calendar says how many there are and lifts the floor on a click. */
export function floorHidden(rows: MonitorRow[], f: Filters, today: string): number {
  if (f.minSig === null) return 0;
  const all = calendarOf(filterRows(rows, { ...f, from: "", to: "", minSig: null }), today).ahead.length;
  return all - calendarOf(filterRows(rows, { ...f, from: "", to: "" }), today).ahead.length;
}

export type NextStep = CalStep & { passed: boolean };
/** Session 1876 (policy faults row 16): the record's next step as of the page's day: the first of its steps dated on or
 *  after `today`, else its last step, marked passed. A record with no steps but the file's `next` keeps that. */
export function nextOf(r: MonitorRow, today: string): NextStep | null {
  const st = [...(r.steps ?? [])].sort((a, b) => (a.date !== b.date ? (a.date < b.date ? -1 : 1) : a.kind !== b.kind ? (a.kind < b.kind ? -1 : 1) : a.event_id < b.event_id ? -1 : a.event_id > b.event_id ? 1 : 0));
  if (st.length) {
    const ahead = st.find((s) => s.date >= today);
    return ahead ? { ...ahead, passed: false } : { ...st[st.length - 1], passed: true };
  }
  return r.next ? { kind: r.next.step, date: r.next.date, words: r.next.words, event_id: "", passed: !!today && r.next.date < today } : null;
}

/** Session 1876 (policy faults row 23): the table draws this many rows at a time, with a button for the next as many. */
export const MONITOR_PAGE = 50;

// Session 1876 (policy faults row 22): the open row's machine keys as words and links. A history line of the file is
// "<dates, comma joined> <instrument> <status> <documents, comma joined>"; each document links to its own source where
// the source can be told: a Federal Register document by its number in the address, another only where it is the one
// document of the record left with the one address left (otherwise its id stays, with no link: nothing guessed).
export type DocRef = { id: string; label: string; href?: string };
export type HistoryLine = { dates: string[]; instrument: string; status: string; docs: DocRef[] };

export function docLinks(r: MonitorRow): Record<string, string | undefined> {
  const ids = (r.history ?? []).flatMap((h) => (h.split(" ")[3] ?? "").split(",").filter(Boolean));
  const urls = r.sources ?? [];
  const out: Record<string, string | undefined> = {};
  const used = new Set<string>();
  for (const id of ids) {
    if (!id.startsWith("federalregister:")) continue;
    const num = id.slice("federalregister:".length);
    const u = urls.find((x) => x.includes(`/${num}/`) || x.endsWith(`/${num}`));
    if (u) { out[id] = u; used.add(u); }
  }
  const restIds = ids.filter((id) => !(id in out));
  const restUrls = urls.filter((u) => !used.has(u));
  if (restIds.length === 1 && restUrls.length === 1) out[restIds[0]] = restUrls[0];
  return out;
}

const hostOf = (u: string) => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return ""; } };
export const docLabel = (id: string, href?: string): string =>
  id.startsWith("federalregister:") ? `FR ${id.slice("federalregister:".length)}` : (href && hostOf(href)) || id;

export function historyOf(r: MonitorRow): HistoryLine[] {
  const links = docLinks(r);
  return (r.history ?? []).map((h) => {
    const [dates = "", instrument = "", status = "", docs = ""] = h.split(" ");
    return {
      dates: [...new Set(dates.split(",").filter(Boolean))], instrument, status,
      docs: docs.split(",").filter(Boolean).map((id) => ({ id, label: docLabel(id, links[id]), href: links[id] })),
    };
  });
}

/** The proceeding's ids as words ("FERC docket CP26-581", "RIN 2060-AW55"), each with its id kept for the hover. */
export const PROCEEDING_WORDS: Record<string, string> = {
  docket: "Docket", rin: "RIN", ferc: "FERC docket", nrc: "NRC docket", project: "FERC project", doe: "DOE docket", irs: "IRS", osmre: "OSMRE",
};
export function proceedingOf(docket: string | undefined): { id: string; words: string }[] {
  return (docket ?? "").split(";").filter(Boolean).map((id) => {
    const i = id.indexOf(":");
    const pre = i > 0 ? id.slice(0, i) : "";
    return { id, words: PROCEEDING_WORDS[pre] ? `${PROCEEDING_WORDS[pre]} ${id.slice(i + 1)}` : id };
  });
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
  // session 3062 added the charts' sums here; session 1876 (policy faults row 28) dropped the sums: the table by month
  // shows each unit's largest figure, whose key is its record's figure key above
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

/** Session 1876 (policy faults row 26): the chart's month labels; the month of the file's last document, when that is
 *  before the month's last day, carries the day it runs to ("2026-11 to the 5th"), so a part month is not drawn as a month. */
const ordinal = (n: number) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? "th" : ["th", "st", "nd", "rd"][n % 10] ?? "th"}`;
export function monthLabels(months: string[], last: string): string[] {
  if (!last) return months;
  const end = day(`${day(`${monthOf(last)}-01`, 32).slice(0, 7)}-01`, -1);
  return months.map((m) => (m === monthOf(last) && last < end ? `${m} to the ${ordinal(Number(last.slice(8, 10)))}` : m));
}

/** Session 1876 (policy faults row 28): the figures by month, with no sum (a sum added a terminal's cost to a penalty):
 *  for each month of a record's newest document and each unit, how many records state a figure in it and the largest,
 *  with its record. Months newest first; units USD, then MW, GW, kW, then the others by name. */
export type MonthFigure = { month: string; unit: string; n: number; top: MonitorRow };
const UNIT_ORDER = ["USD", "MW", "GW", "kW"];
const unitRank = (u: string) => (UNIT_ORDER.includes(u) ? `${UNIT_ORDER.indexOf(u)}` : `9|${u}`);
export function figureMonths(rows: MonitorRow[]): MonthFigure[] {
  const out = new Map<string, MonthFigure>();
  for (const r of rows) {
    if (!r.figure) continue;
    const k = `${monthOf(r.date)}|${r.figure.unit}`;
    const m = out.get(k);
    if (!m) out.set(k, { month: monthOf(r.date), unit: r.figure.unit, n: 1, top: r });
    else {
      m.n++;
      if (r.figure.value > m.top.figure!.value || (r.figure.value === m.top.figure!.value && r.id < m.top.id)) m.top = r;
    }
  }
  return [...out.values()].sort((a, b) => (a.month !== b.month ? (a.month < b.month ? 1 : -1) : unitRank(a.unit) < unitRank(b.unit) ? -1 : 1));
}

/** A Python and a Stata reader of the CSV the page hands out (toCsv), with its provenance line skipped. */
export function pythonReader(csvName: string): string {
  return [`# ERW policy monitor: a reader of ${csvName}, the records as filtered on /policy?view=monitor.`,
    "# Method: docs/methods/policy_monitor.md. Every source of a record is in its sources column.",
    `# Columns: ${CSV_COLS.join(", ")}.`,
    "# steps: kind=date@document, joined by \";\". plain_read: the impact read of policy_reads shown when no impact sentence is.",
    "import pandas as pd", "", `df = pd.read_csv("${csvName}", comment="#", dtype=str, keep_default_na=False)`,
    'df["significance"] = pd.to_numeric(df["significance"], errors="coerce")',
    'df["figure_value"] = pd.to_numeric(df["figure_value"], errors="coerce")', "print(df.shape)", ""].join("\n");
}
export function stataReader(csvName: string): string {
  return [`* ERW policy monitor: a reader of ${csvName}, the records as filtered on /policy?view=monitor.`,
    "* Method: docs/methods/policy_monitor.md. Every source of a record is in its sources column.",
    `* Columns: ${CSV_COLS.join(", ")}.`,
    "* steps: kind=date@document, joined by \";\". plain_read: the impact read of policy_reads shown when no impact sentence is.",
    `import delimited using "${csvName}", varnames(2) rowrange(3) stringcols(_all) clear`,
    "destring significance figure_value documents, replace force", "describe", ""].join("\n");
}
