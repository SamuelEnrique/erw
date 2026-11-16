// Energy Research Warehouse (ERW) site, chain 302 (sessions 7200 and 7201): the large-load rules of US utilities on the
// All grids tab of /cost-of-power and in the monitor of /policy. Everything here reads one site file,
// data/siting/large_load_rules.json, which warehouse/derived/large_load_rules_page.py writes from three warehouse tables
// (utility_large_load_rules, utility_large_load_rule_changes, state_large_load_laws; docs/methods/large_load_research.md).
// This file has no import, so the page, the client table and the scripts (scripts/test-large-load-rules.mjs,
// scripts/check-values.mjs) share one set of functions. Nothing is computed from a value: a field is the document's own
// words, drawn whole or cut at a word with the whole in the hover; a held row or a withheld field carries no value at
// all (the builder writes none), and is drawn blank with "license needed" on hover.

export const FIELDS = ["threshold_mw", "contract_term", "min_demand", "collateral", "exit_fee", "study_timeline", "connection_timeline", "queue_size"] as const;
export type FieldId = (typeof FIELDS)[number];
export type FieldCell =
  | { kind: "value"; v: string; cite: string; registry?: string }
  | { kind: "not published"; cite: string }
  | { kind: "withheld"; registry?: string }
  | { kind: "registry"; registry: string; cite: string }
  | { kind: "see"; row: string | null; name?: string; held?: boolean }
  | { kind: "empty" };
export type Rule = {
  id: string; utility: string; state: string; region: string; grid: string; name: string; status: string; status_date: string; status_cite: string;
  date_kind: string; docket: string; docket_cite: string; fields: Record<FieldId, FieldCell>; url: string; title: string; read: string; clause: string;
  basis: string; notes: string; withheld: string[];
};
export type HeldRule = { id: string; utility: string; state: string; region: string; grid: string };
export type Change = {
  id: string; date: string; date_printed: string; date_kind: string; group: string; utility: string; state: string; rule: string; affects: string;
  docket: string; kind: string; what: string; cite: string; url: string; title: string; read: string;
};
export type HeldChange = { id: string; utility: string };
export type Law = {
  id: string; state: string; bill: string; session: string; title: string; status: string; status_date: string; date_kind: string; effective: string;
  status_cite: string; threshold: string; threshold_cite: string; requirements: string; url: string; doc: string; read: string; notes: string;
};
export type HeldLaw = { id: string; bill: string; state: string };
/** Session 7204: what the research records for a state with no row in the laws table: what was searched and found
 * nothing, that the legislature's site could not be read, or a bill that was read and is withheld (not shown). */
export type LawSearch = { state: string; kind: "none found" | "not read" | "withheld"; bill: string; words: string; source: string };
export type RulesFile = {
  tables: string[]; built: string; retrieved: Record<string, string>; method: string; fields: string[];
  rules: Rule[]; held_rules: HeldRule[]; changes: Change[]; held_changes: HeldChange[]; laws: Law[]; held_laws: HeldLaw[];
  law_searches?: LawSearch[];
  eia: Record<string, { rules: string[]; none?: string; note?: string }>;
  statewide: Record<string, { state: string; grid: string | null }>;
  counts: { rules: Record<string, number>; laws: Record<string, number>; changes: number; held: { rules: number; changes: number; laws: number } };
};

export const RULES_TABLE = "utility_large_load_rules", CHANGES_TABLE = "utility_large_load_rule_changes", LAWS_TABLE = "state_large_load_laws";
export const LICENSE_NEEDED = "license needed";
export const NOT_PUBLISHED = "not published";
/** The anchors of the sections, which the tab's cells and /policy link to. */
export const RULES_ANCHOR = "large-load-rules", CHANGES_ANCHOR = "large-load-changes", LAWS_ANCHOR = "large-load-laws";

/** The columns, in the order of the reader's questions (docs/reviews/large-load-on-site/questions.md): a plain noun and
 * the question it answers, which is the heading's hover. */
export const FIELD_HEAD: Record<FieldId, string> = {
  threshold_mw: "Smallest load", contract_term: "Contract length", min_demand: "Minimum bill", collateral: "Collateral", exit_fee: "Exit fee",
  study_timeline: "Study time", connection_timeline: "Time to energize", queue_size: "Queue",
};
export const FIELD_TIP: Record<FieldId, string> = {
  threshold_mw: "The smallest load the rule covers, as the document prints it: megawatts, and where it prints them a load factor or a site.",
  contract_term: "How long a customer must sign for, as the document prints it.",
  min_demand: "What a customer pays when it uses less: the minimum bill or the take-or-pay share, as the document prints it.",
  collateral: "What a customer must post before anything is built: deposits, letters of credit and guarantees, as the document prints them.",
  exit_fee: "What leaving early costs, as the document prints it.",
  study_timeline: "How long the utility's studies take, as the document prints it.",
  connection_timeline: "When the load can energize: the timed steps from request to service, as the document prints them.",
  queue_size: "How much large load is ahead: the utility's own count of requests or megawatts, from its own filing.",
};
/** A question the tables hold no column for (the questions page, row 6): written so, not filled in. */
export const UPGRADES_WORDS = "no column";
export const UPGRADES_TIP = "Who pays for the upgrades is not a column of the table: some rules print it inside the minimum bill, the collateral or the exit fee, or the ERW's notes on the row. Nothing is filled in here.";

export const RULE_STATUSES = ["in effect", "approved", "proposed", "ordered", "denied", "withdrawn"] as const;
export const LAW_STATUSES = ["in effect", "enacted", "passed", "passed one chamber", "introduced", "vetoed", "died"] as const;
export const STATUS_TIP: Record<string, string> = {
  "in effect": "The rule's sheets or sections are in force.",
  approved: "The regulator or the board has approved it; it is not yet in force, or the document read gives no effective date.",
  proposed: "Filed or published for decision; not decided. A proposal can change.",
  ordered: "A regulator has ordered it; the utility's compliance sheets were not read as in force.",
  denied: "The regulator denied it.",
  withdrawn: "Withdrawn by its filer.",
};
export const LAW_STATUS_TIP: Record<string, string> = {
  "in effect": "Signed, and its effective date has passed.",
  enacted: "Signed into law; its effective date is later, or the text read prints none.",
  passed: "Passed both chambers; the governor's signature was not read.",
  "passed one chamber": "Passed one chamber of the legislature.",
  introduced: "Introduced; not passed by either chamber.",
  vetoed: "Vetoed by the governor.",
  died: "The session ended without its passage.",
};
export const GRID_WORDS: Record<string, string> = { ercot: "ERCOT", pjm: "PJM", miso: "MISO", spp: "SPP", nyiso: "NYISO", caiso: "CAISO", isone: "ISO-NE", other: "No ISO" };
export const GRID_KEYS = ["ercot", "pjm", "miso", "spp", "nyiso", "caiso", "isone", "other"] as const;
export const CHANGE_GROUPS: [string, string][] = [["south_changes", "South"], ["east_changes", "East"], ["midwest_changes", "Midwest"], ["west_changes", "West"], ["operators_federal", "Grid operators and FERC"]];
export const CHANGE_KIND_WORDS: Record<string, string> = { filed: "filed", "hearing set": "hearing set", "order issued": "order issued", approved: "approved", suspended: "suspended", "in effect": "in effect", amended: "amended", other: "other" };

/** A text cut at a word, at most `n` characters, with three dots; whole when it fits. */
export function cut(text: string, n: number): string {
  const s = text.trim();
  if (s.length <= n) return s;
  const head = s.slice(0, n + 1), at = head.lastIndexOf(" ");
  return `${(at > n * 0.5 ? head.slice(0, at) : s.slice(0, n)).replace(/[,;:.\s]+$/, "")}...`;
}
/** The two-letter states a row's state column names ("VA, MD, DE"; "ND, SD, MT, WY and other member states"). */
export const statesOf = (state: string): string[] => state.match(/\b[A-Z]{2}\b/g) ?? [];
const SEARCHED = /^searched:\s*/i;

/** What a field's cell draws: the words, the hover, and how a script knows it. A value is the document's words, cut at
 * a word for the cell and whole in the hover with its cite. Nothing is drawn for a withheld field but its hover. */
export type Drawn = { kind: FieldCell["kind"] | "held"; words: string; whole: string; tip: string; row?: string };
export function drawn(c: FieldCell | undefined, f: FieldId, limit = 110): Drawn {
  if (!c || c.kind === "empty") return { kind: "empty", words: "", whole: "", tip: "" };
  if (c.kind === "value") {
    const from = c.registry ? ` Held in the ERW's registry of filed schedules (warehouse/sources/${c.registry}).` : "";
    return { kind: "value", words: cut(c.v, limit), whole: c.v, tip: `${c.v} As the document prints it: ${c.cite}${from}` };
  }
  if (c.kind === "not published") {
    const what = c.cite.replace(SEARCHED, "").trim();
    return { kind: c.kind, words: NOT_PUBLISHED, whole: NOT_PUBLISHED, tip: `The documents read do not state it.${what ? ` Searched: ${what}` : ""}` };
  }
  if (c.kind === "withheld")
    return { kind: c.kind, words: "", whole: LICENSE_NEEDED, tip: `${LICENSE_NEEDED}: this field rests only on a document whose publisher's terms ask permission before it is shown${c.registry ? ` (the ERW's registry file warehouse/sources/${c.registry} is held for the same reason)` : ""}. ${FIELD_HEAD[f]} is not printed.` };
  if (c.kind === "registry")
    return { kind: c.kind, words: "in the registry", whole: "in the registry", tip: `The ERW's registry of filed schedules holds this field and it is not repeated here: warehouse/sources/${c.registry}.` };
  // a queue figure the same utility's other row holds
  if (c.held) return { kind: "held", words: "", whole: LICENSE_NEEDED, tip: `${LICENSE_NEEDED}: the figure is in a row of the same utility that is held for a license (${c.row}).`, row: c.row ?? undefined };
  return { kind: "see", words: "see its other row", whole: "see its other row", tip: `The same utility's row holds the figure${c.name ? `: ${c.name}` : ""}.`, row: c.row ?? undefined };
}

/** Every rule, public and held, as one list for the table: a held row is its name and place and nothing more. */
export type Line = { id: string; utility: string; state: string; region: string; grid: string; held: boolean; rule?: Rule };
export function lines(file: Pick<RulesFile, "rules" | "held_rules">): Line[] {
  return [...file.rules.map((r) => ({ id: r.id, utility: r.utility, state: r.state, region: r.region, grid: r.grid, held: false, rule: r })),
    ...file.held_rules.map((r) => ({ ...r, held: true }))];
}
export type RuleFilters = { states: string[]; grids: string[]; statuses: string[]; find: string };
export const NO_RULE_FILTERS: RuleFilters = { states: [], grids: [], statuses: [], find: "" };
/** "held" is a status of the filter: the rows held for a license, whose own status is not printed. */
export const HELD_STATUS = "held";
export function filterLines(rows: Line[], f: RuleFilters): Line[] {
  const want = f.find.trim().toLowerCase();
  return rows.filter((r) => (!f.states.length || statesOf(r.state).some((s) => f.states.includes(s)))
    && (!f.grids.length || f.grids.includes(r.grid))
    && (!f.statuses.length || f.statuses.includes(r.held ? HELD_STATUS : r.rule!.status))
    && (!want || r.utility.toLowerCase().includes(want) || (r.rule?.name ?? "").toLowerCase().includes(want)));
}
export type RuleSort = "utility" | "state" | "grid" | "status" | "date" | FieldId;
export const RULE_SORTS: RuleSort[] = ["utility", "state", "grid", "status", "date", ...FIELDS];
/** Sorted by a column; a row with nothing printed in it (held, withheld, not published) last either way. A field sorts
 * by its words, since the table prints words, not numbers: the order is the alphabet's, and the page says so. */
export function sortLines(rows: Line[], by: RuleSort, dir: "asc" | "desc"): Line[] {
  const key = (r: Line): string | null => {
    if (by === "utility") return r.utility.toLowerCase();
    if (by === "state") return r.state || null;
    if (by === "grid") return GRID_WORDS[r.grid] ?? r.grid;
    if (r.held || !r.rule) return null;
    if (by === "status") return String(RULE_STATUSES.indexOf(r.rule.status as (typeof RULE_STATUSES)[number]) + 10);
    if (by === "date") return /^\d{4}/.test(r.rule.status_date) ? r.rule.status_date : null;
    const c = r.rule.fields[by];
    return c?.kind === "value" ? c.v.toLowerCase() : null;
  };
  const sign = dir === "asc" ? 1 : -1;
  return [...rows].sort((a, b) => {
    const ka = key(a), kb = key(b);
    if (ka === null || kb === null) return ka === kb ? a.utility.localeCompare(b.utility) || a.id.localeCompare(b.id) : ka === null ? 1 : -1;
    return sign * ka.localeCompare(kb, "en", { numeric: true }) || a.utility.localeCompare(b.utility) || a.id.localeCompare(b.id);
  });
}
export type Option = { key: string; label: string; n: number };
/** The filters' choices, each with the rows it holds. */
export function ruleOptions(rows: Line[]): { states: Option[]; grids: Option[]; statuses: Option[] } {
  const states = new Map<string, number>();
  for (const r of rows) for (const s of statesOf(r.state)) states.set(s, (states.get(s) ?? 0) + 1);
  const grids = GRID_KEYS.map((g) => ({ key: g as string, label: GRID_WORDS[g], n: rows.filter((r) => r.grid === g).length })).filter((o) => o.n);
  const statuses = [...RULE_STATUSES.map((s) => ({ key: s as string, label: s, n: rows.filter((r) => !r.held && r.rule!.status === s).length })),
    { key: HELD_STATUS, label: LICENSE_NEEDED, n: rows.filter((r) => r.held).length }].filter((o) => o.n);
  return { states: [...states.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([k, n]) => ({ key: k, label: k, n })), grids, statuses };
}

/** The rules a row of the tab reaches: its utilities' own (by EIA number), the rules that bind every utility of its
 * state (or of its state inside its grid), the utilities read with no rule found, and the utilities not read. */
export type RowRules = {
  own: string[]; statewide: string[];
  none: { number: string; name: string; words: string; note: string }[];
  unread: { number: string; name: string }[];
  inState: number;
};
export function rowRules(file: Pick<RulesFile, "eia" | "statewide" | "rules" | "held_rules">, utilities: { number: string; name: string }[], state: string | null, grid: string): RowRules {
  const own: string[] = [], none: RowRules["none"] = [], unread: RowRules["unread"] = [], seen = new Set<string>();
  for (const u of utilities) {
    if (seen.has(u.number)) continue;
    seen.add(u.number);
    const e = file.eia[u.number];
    if (!e) unread.push(u);
    else if (e.rules.length) { for (const id of e.rules) if (!own.includes(id)) own.push(id); }
    else none.push({ number: u.number, name: u.name, words: e.none ?? "", note: e.note ?? "" });
  }
  const statewide = state ? Object.entries(file.statewide).filter(([id, s]) => s.state === state && (!s.grid || s.grid === grid) && !own.includes(id)).map(([id]) => id) : [];
  const inState = state ? lines(file).filter((r) => statesOf(r.state).includes(state)).length : 0;
  return { own, statewide, none, unread, inState };
}
export function lineOf(file: Pick<RulesFile, "rules" | "held_rules">, id: string): Line | undefined {
  return lines(file).find((r) => r.id === id);
}
/** A date as the table prints it: a day, a month, or "not published". */
export const dateWords = (d: string) => (/^\d{4}-\d{2}(-\d{2})?$/.test(d) ? d : d || NOT_PUBLISHED);
/** Session 7600 (the browser read of 16 November, row 6): a status and its date in one line. Where the document prints
 * no date the line says whose "not published" it is ("in effect, date not published"), not "in effect, not published",
 * which read as the rule itself not being published. */
export const statusDateWords = (date: string) => (/^\d{4}-\d{2}(-\d{2})?$/.test(date) ? date : `date ${dateWords(date)}`);
export const statusWords = (status: string, date: string) => `${status}, ${statusDateWords(date)}`;
/** Session 7600 (row 5): names in the order met, each once: a row of the tab names a utility once however many of its
 * roles (the zone's own utility, the county's wires utility) carry it. */
export const uniqueNames = (names: string[]): string[] => [...new Set(names.map((n) => n.trim()).filter(Boolean))];
export function statusTip(r: Rule): string {
  return `${STATUS_TIP[r.status] ?? ""} ${r.date_kind === "date read" ? `No date of its own is printed: ${dateWords(r.status_date)} is the day or the month the document was read or dated.` : `Dated ${dateWords(r.status_date)} in the document.`} ${r.status_cite}`.trim();
}

/** What a change names: a rule of the table (public or held), a file of the ERW's registry, or a rule not yet a row. */
export type Affects = { kind: "rule"; id: string; held: boolean; utility: string } | { kind: "registry"; file: string } | { kind: "new" } | { kind: "none" };
export function affectsOf(file: Pick<RulesFile, "rules" | "held_rules">, c: Pick<Change, "affects">): Affects {
  const a = (c.affects ?? "").trim();
  if (!a) return { kind: "none" };
  if (a === "new") return { kind: "new" };
  const l = lineOf(file, a);
  if (l) return { kind: "rule", id: l.id, held: l.held, utility: l.utility };
  return { kind: "registry", file: a };
}
export const groupWords = (g: string) => CHANGE_GROUPS.find(([k]) => k === g)?.[1] ?? g;
export function filterChanges(rows: Change[], groups: string[], states: string[] = []): Change[] {
  return rows.filter((c) => (!groups.length || groups.includes(c.group)) && (!states.length || statesOf(c.state).some((s) => states.includes(s))));
}
/** Session 7600 (the browser read, row 8): the date a change is ordered by is the date its row draws. A change whose
 * document prints a month only is drawn as that month ("2026-09"), and the file dates it to the day it was read (13
 * November): ordered by that day, seven months stood above 13 November in a list headed "newest first". Here a month is
 * ordered as its month, above the days of the same month (its day is not known), and rows of one date keep the file's
 * order. */
export const changeOrderKey = (c: Pick<Change, "date" | "date_printed" | "date_kind">): string => {
  const drawnDate = c.date_kind === "date read" || c.date_printed !== c.date ? c.date_printed || c.date : c.date;
  return /^\d{4}-\d{2}$/.test(drawnDate) ? `${drawnDate}-99` : drawnDate;
};
export function orderChanges<T extends Pick<Change, "date" | "date_printed" | "date_kind">>(rows: T[]): T[] {
  return rows.map((c, i) => ({ c, i, k: changeOrderKey(c) })).sort((a, b) => (a.k < b.k ? 1 : a.k > b.k ? -1 : a.i - b.i)).map((x) => x.c);
}

/** Session 7600 (the browser read, rows 1 and 2): where a hover's box is drawn. The boxes of this section are wide (a
 * document's words and its cite) and their triggers stand inside tables that scroll sideways, so a box placed under its
 * trigger by the style sheet alone was cut by the table's frame and by the window's edge (at 390 px, nearly every one).
 * The page places the box against the window instead: under the trigger where it fits, above it where there is more
 * room, never past an edge, and no taller than the room it has. Sizes in CSS pixels; `trigger` is the trigger's box in
 * the window, `tip` the box's own size, `win` the window's. */
export type TipPlace = { left: number; top: number; maxHeight: number; above: boolean };
export function placeTip(trigger: { left: number; top: number; right: number; bottom: number }, tip: { width: number; height: number }, win: { width: number; height: number }, margin = 8, gap = 2): TipPlace {
  const width = Math.min(tip.width, Math.max(0, win.width - 2 * margin));
  const left = Math.max(margin, Math.min(trigger.left, win.width - margin - width));
  const below = Math.max(0, win.height - margin - (trigger.bottom + gap)), over = Math.max(0, trigger.top - gap - margin);
  const above = tip.height > below && over > below;
  const maxHeight = Math.max(0, Math.floor(above ? over : below));
  const height = Math.min(tip.height, maxHeight);
  return { left: Math.round(left), top: Math.round(above ? trigger.top - gap - height : trigger.bottom + gap), maxHeight, above };
}

/** A law's requirements, as the table writes them: "topic: words [cite] || topic: words [cite]". */
export type Requirement = { topic: string; words: string; cite: string };
export function requirementsOf(law: Pick<Law, "requirements">): Requirement[] {
  return (law.requirements ?? "").split(" || ").map((p) => p.trim()).filter(Boolean).map((p) => {
    const m = /^([a-z][a-z ,/-]*): ([\s\S]*?)(?: \[([\s\S]*)\])?$/.exec(p);
    return m ? { topic: m[1], words: m[2].trim(), cite: (m[3] ?? "").trim() } : { topic: "other", words: p, cite: "" };
  });
}
export function lawsOf(file: Pick<RulesFile, "laws" | "held_laws">, states: string[]): { laws: Law[]; held: HeldLaw[] } {
  const keep = (s: string) => !states.length || states.includes(s);
  return { laws: file.laws.filter((l) => keep(l.state)), held: file.held_laws.filter((l) => keep(l.state)) };
}
/** Session 7204: what the page says of a state the laws table holds no row for. Never "no law": the research found
 * none where it searched, could not read some legislatures' sites, read and withheld one bill, and did not search two
 * states at all. `words` is the hover: the research's own, or the file where they hold a lead from the news. */
export const NOT_SHOWN = "not shown";
export const SEARCH_WORDS: Record<LawSearch["kind"] | "not searched", string> = { "none found": "none found where searched", "not read": "not read", withheld: "read and not shown", "not searched": "not searched" };
export function lawSearchOf(searches: LawSearch[] | undefined, state: string): { kind: LawSearch["kind"] | "not searched"; bill: string; words: string; tip: string } {
  const s = (searches ?? []).find((x) => x.state === state);
  if (!s) return { kind: "not searched", bill: "", words: SEARCH_WORDS["not searched"], tip: `The ERW's read of the states' laws on large loads (13 and 14 November 2026) did not search ${state}. It may have a law.` };
  if (s.kind === "withheld")
    return { kind: s.kind, bill: s.bill, words: SEARCH_WORDS.withheld, tip: `${NOT_SHOWN}: the ERW read ${state} ${s.bill}, and its values are not printed. ${s.words}` };
  const where = s.words ? `What was searched: ${s.words}` : `What was searched is in the research file (${s.source}); its words hold a lead from the news, which is not verified and is not printed here.`;
  return { kind: s.kind, bill: "", words: SEARCH_WORDS[s.kind], tip: s.kind === "not read" ? `The legislature's own site could not be read, so ${state} is not ruled out. ${where}` : `No law or bill on large loads was found for ${state} where the ERW searched. It is not proof that none exists. ${where}` };
}
/** The address of the utilities' rules of a state, on the All grids tab. */
export const rulesHref = (state?: string) => `/cost-of-power?view=allgrids${state ? `&rstate=${encodeURIComponent(state)}` : ""}#${RULES_ANCHOR}`;

/** The states with a law or a bill, for the tab's link to /policy. */
export const lawStates = (file: Pick<RulesFile, "laws" | "held_laws">): string[] => [...new Set([...file.laws.map((l) => l.state), ...file.held_laws.map((l) => l.state)].filter(Boolean))].sort();
export const lawsHref = (state?: string) => `/policy?view=monitor${state ? `&state=${encodeURIComponent(state)}` : ""}#${LAWS_ANCHOR}`;
export function lawStatusTip(l: Law): string {
  return `${LAW_STATUS_TIP[l.status] ?? ""} ${l.date_kind === "date read" ? `No date of its own is printed in the text read: ${dateWords(l.status_date)}.` : `Dated ${dateWords(l.status_date)} in the text.`} ${l.status_cite}`.trim();
}

// ---------------------------------------------------------------------------------------------------------------------
// the downloads: the rows shown, as CSV, with a Python and a Stata reader of that file
// ---------------------------------------------------------------------------------------------------------------------
const csvCell = (v: string | number | undefined | null) => {
  const s = v === undefined || v === null ? "" : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
export const RULE_CSV_COLS = ["rule_id", "license", "utility", "state", "grid", "iso_or_region", "rule", "status", "status_date", "status_cite", "docket",
  ...FIELDS.flatMap((f) => [f, `${f}_cite`]), "source_url", "source_title", "date_read", "notes"];
export const RULES_CSV_NAME = "erw-large-load-rules.csv";
/** One row a rule. A field's cell is the document's words, "not published", a pointer ("see row: <id>", "in the
 * registry: <file>") or, for a withheld field and every field of a held row, "license needed" and no cite. */
export function rulesCsv(rows: Line[], file: Pick<RulesFile, "built" | "retrieved">, address: string): string {
  const out = [`# Energy Research Warehouse (ERW): US utilities' large-load connection rules, the rows shown on ${address}. Table ${RULES_TABLE} (retrieved ${file.retrieved?.[RULES_TABLE] ?? ""}); the page file was built ${file.built}. Each value is the document's own words; its cite is the page or section and the words. A row or a field marked "${LICENSE_NEEDED}" is held: its publisher's terms ask permission. Method: docs/methods/large_load_research.md.`,
    RULE_CSV_COLS.join(",")];
  for (const l of rows) {
    if (l.held || !l.rule) {
      out.push([l.id, "internal", l.utility, l.state, GRID_WORDS[l.grid] ?? l.grid, l.region, LICENSE_NEEDED, LICENSE_NEEDED, "", "", "", ...FIELDS.flatMap(() => [LICENSE_NEEDED, ""]), "", "", "", ""].map(csvCell).join(","));
      continue;
    }
    const r = l.rule;
    const cells = FIELDS.flatMap((f) => {
      const c = r.fields[f];
      if (!c || c.kind === "empty") return ["", ""];
      if (c.kind === "value") return [c.v, c.cite];
      if (c.kind === "not published") return [NOT_PUBLISHED, c.cite];
      if (c.kind === "withheld") return [LICENSE_NEEDED, ""];
      if (c.kind === "registry") return [`in the registry: ${c.registry}`, ""];
      return [c.held ? LICENSE_NEEDED : `see row: ${c.row ?? ""}`, ""];
    });
    out.push([r.id, "public", r.utility, r.state, GRID_WORDS[r.grid] ?? r.grid, r.region, r.name, r.status, r.status_date, r.status_cite, r.docket, ...cells, r.url, r.title, r.read, r.notes].map(csvCell).join(","));
  }
  return out.join("\n") + "\n";
}
export const CHANGE_CSV_COLS = ["change_id", "date", "date_printed", "date_kind", "region", "utility", "state", "rule", "affects", "docket", "kind", "what", "cite", "source_url", "source_title", "date_read"];
export const CHANGES_CSV_NAME = "erw-large-load-rule-changes.csv";
/** Session 7600 (the browser read, row 9): `held` are the changes held for a license that the table draws under the
 * rows (their utility named, every other cell blank): the file carries them the same way, as the rules' and the laws'
 * files carry their held rows, so the file has the rows the reader sees. */
export function changesCsv(rows: Change[], file: Pick<RulesFile, "built" | "retrieved">, address: string, held: HeldChange[] = []): string {
  return [`# Energy Research Warehouse (ERW): changes to US utilities' large-load rules, 15 August to 13 November 2026, the rows shown on ${address}. Table ${CHANGES_TABLE} (retrieved ${file.retrieved?.[CHANGES_TABLE] ?? ""}); the page file was built ${file.built}.${held.length ? ` A row marked "${LICENSE_NEEDED}" is held: its publisher's terms ask permission.` : ""} Method: docs/methods/large_load_research.md.`,
    CHANGE_CSV_COLS.join(","),
    ...rows.map((c) => [c.id, c.date, c.date_printed, c.date_kind, groupWords(c.group), c.utility, c.state, c.rule, c.affects, c.docket, c.kind, c.what, c.cite, c.url, c.title, c.read].map(csvCell).join(",")),
    ...held.map((h) => [h.id, "", "", "", "", h.utility, "", LICENSE_NEEDED, "", "", LICENSE_NEEDED, LICENSE_NEEDED, "", "", "", ""].map(csvCell).join(","))].join("\n") + "\n";
}
export const LAW_CSV_COLS = ["law_id", "state", "bill", "session", "title", "status", "status_date", "date_kind", "effective_date", "status_cite", "threshold", "threshold_cite", "requirements", "source_url", "source_title", "date_read", "notes"];
export const LAWS_CSV_NAME = "erw-state-large-load-laws.csv";
export function lawsCsv(rows: Law[], held: HeldLaw[], file: Pick<RulesFile, "built" | "retrieved">, address: string): string {
  return [`# Energy Research Warehouse (ERW): state laws and bills on large electric loads, 2025 and 2026 sessions, the rows shown on ${address}. Table ${LAWS_TABLE} (retrieved ${file.retrieved?.[LAWS_TABLE] ?? ""}); the page file was built ${file.built}. A row marked "${LICENSE_NEEDED}" is held: its publisher's terms ask permission. Method: docs/methods/large_load_research.md.`,
    LAW_CSV_COLS.join(","),
    ...rows.map((l) => [l.id, l.state, l.bill, l.session, l.title, l.status, l.status_date, l.date_kind, l.effective, l.status_cite, l.threshold, l.threshold_cite, l.requirements, l.url, l.doc, l.read, l.notes].map(csvCell).join(",")),
    ...held.map((l) => [l.id, l.state, l.bill, "", LICENSE_NEEDED, LICENSE_NEEDED, "", "", "", "", LICENSE_NEEDED, "", LICENSE_NEEDED, "", "", "", ""].map(csvCell).join(","))].join("\n") + "\n";
}
/** A Python (pandas) and a Stata reader of a CSV the page hands out: the provenance line skipped, every column text. */
export function pythonReader(csvName: string, cols: string[], what: string): string {
  return [`# Energy Research Warehouse (ERW): a reader of ${csvName}, ${what}.`,
    "# Method: docs/methods/large_load_research.md. Every value is the document's own words; its cite is in the column beside it.",
    `# Columns: ${cols.join(", ")}.`,
    "import pandas as pd", "", `df = pd.read_csv("${csvName}", comment="#", dtype=str, keep_default_na=False)`, "print(df.shape)", "print(df.head())", ""].join("\n");
}
export function stataReader(csvName: string, cols: string[], what: string): string {
  return [`* Energy Research Warehouse (ERW): a reader of ${csvName}, ${what}.`,
    "* Method: docs/methods/large_load_research.md. Every value is the document's own words; its cite is in the column beside it.",
    `* Columns: ${cols.join(", ")}.`,
    `import delimited using "${csvName}", varnames(2) rowrange(3) stringcols(_all) bindquote(strict) maxquotedrows(unlimited) clear`, "describe", ""].join("\n");
}

// ---------------------------------------------------------------------------------------------------------------------
// the counts the page draws, each a check key (scripts/check-values.mjs recomputes them from the same file)
// ---------------------------------------------------------------------------------------------------------------------
/** largeload|rules|public, |held, |all, |status|<status>, |state|<ST>, |grid|<grid>;
 *  largeload|changes|public, |held, |group|<group>; largeload|laws|public, |held, |status|<status>, |state|<ST>. */
export function largeLoadStat(file: RulesFile, key: string): number | undefined {
  const p = key.split("|");
  if (p[0] !== "largeload") return undefined;
  const all = lines(file);
  if (p[1] === "rules") {
    if (p[2] === "public") return file.rules.length;
    if (p[2] === "held") return file.held_rules.length;
    if (p[2] === "all") return all.length;
    if (p[2] === "status") return file.rules.filter((r) => r.status === p[3]).length;
    if (p[2] === "state") return all.filter((r) => statesOf(r.state).includes(p[3])).length;
    if (p[2] === "grid") return all.filter((r) => r.grid === p[3]).length;
  }
  if (p[1] === "changes") {
    if (p[2] === "public") return file.changes.length;
    if (p[2] === "held") return file.held_changes.length;
    if (p[2] === "group") return file.changes.filter((c) => c.group === p[3]).length;
  }
  if (p[1] === "laws") {
    if (p[2] === "public") return file.laws.length;
    if (p[2] === "held") return file.held_laws.length;
    if (p[2] === "status") return file.laws.filter((l) => l.status === p[3]).length;
    if (p[2] === "state") return file.laws.filter((l) => l.state === p[3]).length + file.held_laws.filter((l) => l.state === p[3]).length;
  }
  return undefined;
}
