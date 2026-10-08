// Energy Research Warehouse (ERW) site, session 154: "Rules in motion", the block in the section "How soon" of
// "What a datacenter pays" (/cost-of-power, in review).
//
// The block reads one site file, data/datacenter/rules.json, written whole by the warehouse's builder from the table of
// proceedings and orders and from the tagged policy actions held (docs/methods/datacenter_cost.md). This file is what
// the page does with it: which grid's rules an address shows, which rows are shown, their order, the fold, and the
// words of every hover. Pure functions, no imports: Node runs this file as it is (site/scripts/test-rules.mjs,
// site/scripts/check-datacenter.mjs, tests/test_session154_page.py).
//
// The rules the page keeps whatever the file says:
//   MISO          reads "paused while terms are reviewed" and shows no row, federal ones included;
//   a row         is shown only with the address of its source document (http or https), and only when none of its
//                 words is a municipal one: federal regulators, state commissions and grid operators only;
//   a read        is a line a model wrote from the document, marked as a model's read; a line the file does not mark
//                 as a model's is not shown, and the row reads "no read yet";
//   nothing       is filled: a date, a status or a docket the document does not state is a short placeholder.

export type RuleRow = {
  id: string; date: string; regulator: string; jurisdiction: string; state: string; docket: string; title: string;
  row_kind: string; topic: string; tags: string[]; status_as_worded: string; status_class: string; url: string;
  page: string | number | null; sentence: string; read: string | null; read_by: string | null; read_model: string | null;
  read_from: string | null; why_here: string | null;
  /** where the builder took the sentence from, when it says (for a federal action held with no document text: its title) */
  sentence_from?: string | null;
};
export type RuleGrid = { state: string; rows?: RuleRow[]; words?: string; why?: string };
export type RuleSource = { regulator: string; terms_url: string; terms_quote: string };
export type RulesFile = {
  built_at_utc: string; window_months: number; sources: RuleSource[]; grids: Record<string, RuleGrid>;
  federal_all_grids: RuleRow[]; not_on_page?: { count: number; why: string };
};

/** The grids an address can name for the block, in the page's order. */
export const RULE_GRIDS = ["ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"] as const;
/** Rows shown before the fold, in each of the two groups. */
export const SHOWN = 8;
export const PAUSED_WORDS = "paused while terms are reviewed";
/** The pause's hover, as the site words it on the energy mix page (components/mix/views.tsx), and what it means here. */
export const PAUSE_WHY = "MISO's terms forbid automated access to its site; its pulls are paused. No rule is listed under MISO until a person lifts the pause.";
export const NO_READ = "no read yet";
export const NO_READ_WHY = "No line is shown that a model did not write from the document.";
export const NOT_HELD_WHY = "The file of rules in motion is not in this page's files yet.";
export const NONE_WORDS = "none held";
/** Out of scope whatever the file holds: municipal permitting, zoning and local hearings. A row with one of these words
 * in anything the block would show, on its face or on hover, is not shown. */
export const MUNICIPAL = ["zoning", "permit", "city council", "county board"] as const;

const text = (v: unknown): string => (typeof v === "string" ? v.trim() : typeof v === "number" && Number.isFinite(v) ? String(v) : "");
const isRow = (r: unknown): r is RuleRow => !!r && typeof r === "object" && !Array.isArray(r);
const rowsOf = (v: unknown): RuleRow[] => (Array.isArray(v) ? v.filter(isRow) : []);

/** The grid whose rules an address shows: the one it names, when it is one of the seven (MISO and PJM too, which the
 * rest of the page does not open); else the grid the page opened. */
export function rulesGrid(asked: string | undefined, opened: string): string {
  const a = (asked ?? "").trim().toLowerCase();
  return (RULE_GRIDS as readonly string[]).includes(a) ? a : opened;
}

/** The file as read, or null when it is not a rules file (no grids, no federal list). Nothing is repaired. */
export function fileOf(v: unknown): RulesFile | null {
  if (!v || typeof v !== "object" || Array.isArray(v)) return null;
  const f = v as Partial<RulesFile>;
  if (!f.grids || typeof f.grids !== "object" || Array.isArray(f.grids) || !Array.isArray(f.federal_all_grids)) return null;
  return f as RulesFile;
}

const DAY = /^(\d{4})-(\d{2})-(\d{2})$/;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
/** "2026-10-08" as "8 Oct 2026"; null when the row holds no such day. */
export function dayWords(iso: unknown): string | null {
  const m = DAY.exec(text(iso));
  if (!m) return null;
  const mo = Number(m[2]), d = Number(m[3]);
  if (mo < 1 || mo > 12 || d < 1 || d > 31) return null;
  return `${d} ${MONTHS[mo - 1]} ${m[1]}`;
}

/** The address of the source document, when it is one a link may carry. */
export function linkOf(r: RuleRow): string | null {
  const u = text(r.url);
  return /^https?:\/\/[^\s"'<>]+$/i.test(u) ? u : null;
}

/** Every word of a row that the block would show, on its face or on hover. */
export function wordsOf(r: RuleRow): string {
  return [r.regulator, r.docket, r.title, r.topic, ...(Array.isArray(r.tags) ? r.tags : []), r.status_as_worded, r.status_class, r.sentence, r.read, r.read_from, r.read_model, r.why_here, r.state, r.jurisdiction, r.row_kind, r.sentence_from]
    .map(text).filter(Boolean).join(" \n ");
}
/** The municipal word a text holds, or null. */
export function municipalWord(s: string): string | null {
  const t = s.toLowerCase().replace(/\s+/g, " ");
  return MUNICIPAL.find((w) => t.includes(w)) ?? null;
}

/** A reason the file gives, as a hover may carry it: not one that holds a municipal word (then the page's own words). */
export function safeWhy(why: unknown, instead: string): string {
  const w = text(why);
  return w && !municipalWord(w) ? w : instead;
}

/** Newest first; a row with no day last; then by regulator, docket and id, so the order never depends on the file's. */
export function sortRows(rows: RuleRow[]): RuleRow[] {
  const key = (r: RuleRow) => (dayWords(r.date) ? text(r.date) : "");
  return [...rows].sort((a, b) => {
    const ka = key(a), kb = key(b);
    if (ka !== kb) return ka < kb ? 1 : -1;
    for (const f of ["regulator", "docket", "id"] as const) {
      const x = text(a[f]), y = text(b[f]);
      if (x !== y) return x < y ? -1 : 1;
    }
    return 0;
  });
}

/** `word`: the municipal word found, kept for the record and never shown (the hover says only that one was). */
export type Dropped = { id: string; why: string; word?: string };
/** The rows of a list that the block shows, in its order, and the ones it does not, each with why. */
export function choose(list: unknown): { rows: RuleRow[]; dropped: Dropped[] } {
  const rows: RuleRow[] = [], dropped: Dropped[] = [], seen = new Set<string>();
  for (const r of rowsOf(list)) {
    const id = text(r.id) || `${text(r.regulator)} ${text(r.docket)} ${text(r.date)}`.trim();
    const word = municipalWord(wordsOf(r));
    if (!linkOf(r)) dropped.push({ id, why: "no address of a source document" });
    else if (word) dropped.push({ id, why: "a word of it is outside this page's scope", word });
    else if (seen.has(id)) dropped.push({ id, why: "listed twice" });
    else { seen.add(id); rows.push(r); }
  }
  return { rows: sortRows(rows), dropped };
}
/** The hover of the count of rows in the file that the block does not show: each by its id, with why. */
export function droppedTip(dropped: Dropped[]): string {
  return `Not shown: ${dropped.map((d) => `${municipalWord(d.id) ? "a row" : d.id} (${d.why})`).join("; ")}.`;
}

/** The first `n` rows, and the rest behind the fold. */
export function foldOf<T>(rows: T[], n: number = SHOWN): { shown: T[]; folded: T[] } {
  return { shown: rows.slice(0, n), folded: rows.slice(n) };
}

export type Block = {
  grid: string;
  /** shown: rows of the grid; none: the file holds none for it; paused: the fixed words and no row at all;
   * missing: the file, or the grid's entry in it, is not there. */
  state: "shown" | "none" | "paused" | "missing";
  words: string | null; why: string | null;
  rows: RuleRow[]; federal: RuleRow[]; dropped: Dropped[];
};
/** What the block shows for a grid. */
export function blockOf(file: RulesFile | null, grid: string): Block {
  const entry = file?.grids?.[grid];
  if (grid === "miso" || entry?.state === "paused")
    return { grid, state: "paused", words: grid === "miso" ? PAUSED_WORDS : text(entry?.words) || PAUSED_WORDS, why: grid === "miso" ? PAUSE_WHY : safeWhy(entry?.why, "Its pulls are paused."), rows: [], federal: [], dropped: [] };
  if (!file) return { grid, state: "missing", words: null, why: NOT_HELD_WHY, rows: [], federal: [], dropped: [] };
  const fed = choose(file.federal_all_grids);
  if (!entry || (entry.state !== "shown" && entry.state !== "none"))
    return { grid, state: "missing", words: null, why: "The file of rules in motion holds no entry for this grid.", rows: [], federal: fed.rows, dropped: fed.dropped };
  const own = entry.state === "shown" ? choose(entry.rows) : { rows: [], dropped: [] };
  // a row is listed once: under the grid when the file lists it in both places
  const mine = new Set(own.rows.map((r) => text(r.id)).filter(Boolean));
  const federal = fed.rows.filter((r) => !mine.has(text(r.id)));
  const dropped = [...own.dropped, ...fed.dropped];
  if (!own.rows.length) return { grid, state: "none", words: NONE_WORDS, why: safeWhy(entry.why, "No proceeding or order in motion is held for this grid."), rows: [], federal, dropped };
  return { grid, state: "shown", words: null, why: null, rows: own.rows, federal, dropped };
}

const CLASSES = ["open", "decided", "closed", "not stated"];
/** The status a row shows: the regulator's own words where it words one, else the class; the class is on hover. */
export function statusOf(r: RuleRow): { words: string; stated: boolean; why: string } {
  const worded = text(r.status_as_worded), cls = CLASSES.includes(text(r.status_class)) ? text(r.status_class) : "not stated";
  const kind = text(r.row_kind);
  const of = kind ? ` The row is ${/^[aeiou]/i.test(kind) ? "an" : "a"} ${kind}.` : "";
  if (worded) return { words: worded, stated: true, why: `The regulator's own words. Class: ${cls}.${of}` };
  if (cls === "not stated") return { words: "not stated", stated: false, why: `The document states no status.${of}` };
  return { words: cls, stated: true, why: `The document words no status; ${cls} is its class.${of}` };
}

/** The link's words: the regulator and the docket number. */
export function docketWords(r: RuleRow): string {
  const who = text(r.regulator), no = text(r.docket);
  return who && no ? `${who}, ${no}` : who || no || "source document";
}
/** The link's hover: the exact sentence, the page and the topic. */
export function docketTip(r: RuleRow): string {
  const s = text(r.sentence), page = text(r.page), topic = text(r.topic);
  const tags = Array.isArray(r.tags) ? r.tags.map(text).filter(Boolean) : [], from = text(r.sentence_from);
  return [s ? `"${s}"` : "No sentence of the document is held for this row.", s && from ? `Sentence from: ${from}.` : "", page ? `Page ${page} of the document.` : "", topic ? `Topic: ${topic}.` : "", tags.length ? `Tags: ${tags.join(", ")}.` : ""].filter(Boolean).join(" ");
}

/** The read a row shows: the line and the hover of its mark, or no line and the placeholder's reason. */
export function readOf(r: RuleRow): { line: string | null; why: string } {
  const line = text(r.read);
  if (!line || r.read_by !== "model") return { line: null, why: NO_READ_WHY };
  const model = text(r.read_model), from = text(r.read_from);
  return { line, why: `A model's read${model ? `, by ${model}` : ""}: one line written from ${from || "the row's sentence and its document"}. Not the regulator's words.` };
}

/** The regulators whose terms the file quotes, once each, in the file's order. */
export function sourcesOf(file: RulesFile | null): RuleSource[] {
  const seen = new Set<string>(), out: RuleSource[] = [];
  for (const s of Array.isArray(file?.sources) ? file!.sources : []) {
    const who = text(s?.regulator);
    if (!who || seen.has(who)) continue;
    seen.add(who);
    out.push({ regulator: who, terms_url: /^https?:\/\/[^\s"'<>]+$/i.test(text(s.terms_url)) ? text(s.terms_url) : "", terms_quote: text(s.terms_quote) });
  }
  return out;
}
/** The hover of a regulator's terms: its own words as the file quotes them. */
export function termsTip(s: RuleSource): string {
  return s.terms_quote ? safeWhy(`"${s.terms_quote}"`, "Its terms are quoted in the Method note.") : "";
}
/** What the file says it holds and does not put on the page: the count and the reason, when there is any. */
export function leftOf(file: RulesFile | null): { count: number; why: string } | null {
  const n = Number(file?.not_on_page?.count);
  return Number.isFinite(n) && n > 0 ? { count: n, why: safeWhy(file!.not_on_page!.why, "Held in the warehouse and not shown on this page.") } : null;
}
