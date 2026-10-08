// Energy Research Warehouse (ERW) site, session 157: "What changed this week", the second view of the policy monitor
// (/policy?view=week, in review).
//
// The view lists the regulatory actions of the last seven and thirty days by agency and topic. Its rows are of two
// kinds, shown the same way:
//   an action     a row of policy_actions in the live set (the Federal Register's rules, proposed rules and notices of
//                 the federal agencies, and the news releases the table holds), with its read from policy_reads;
//   a docket row  a proceeding or an order of FERC or a state commission, from the site's own file
//                 data/policy/state_rules.json (the sentence rule of session 154 holds: lib/rules.ts words its hover).
// This file is what the page does with them: the tag rule applied to the rows read (one rule file, the warehouse's
// own: data/policy/tag_rules.json, the same content warehouse/derived/policy_action_tags.py applies), the grid an action
// is under (data/policy/grids.json), the windows, the filters and their address, the counts the chart draws, and the
// words of every hover. Pure functions: no request, no file read, no model. Node runs it with the site's alias loader
// (scripts/test-policy-week.mjs, scripts/check-policy.mjs, tests/test_session157_page.py).
//
// The rules the page keeps whatever a file says:
//   scope         federal regulators, state commissions and grid operators only. A row with a municipal phrase in
//                 anything the view would show, on its face or on hover, is not shown; it is counted, with why;
//   MISO          reads "paused while terms are reviewed" and shows no row;
//   a read        is a line a model wrote, marked "model's read" with the model on hover; else "no read yet";
//   a sentence    on a docket row's hover is the file's own, or the file's phrase where the regulator's text is not
//                 copied; no sentence is ever made here;
//   nothing       is filled: a status, a docket or a read that is not held is a short placeholder with a hover.
import { NO_READ_WHY, PAUSED_WORDS, PAUSE_WHY, dayWords, docketTip, docketWords, hoverKind, linkOf, readOf, statusOf, withheldOf, type RuleRow } from "@/lib/rules";

// ---- the page's two views and their address ---------------------------------------------------------------------------

export const VIEWS = [["all", "Every action, scored"], ["week", "What changed this week"]] as const;
export type View = (typeof VIEWS)[number][0];
/** The view an address asks for: anything but "week" is the page as it was before session 157. */
export const viewOf = (q: Record<string, string | undefined>): View => (q.view === "week" ? "week" : "all");
export const viewHref = (view: View): string => (view === "week" ? "/policy?view=week" : "/policy");
export const METHOD = { href: "/data/methods/policy_monitor", doc: "docs/methods/policy_monitor.md" } as const;

export const WINDOWS = [7, 30] as const;
export type Days = (typeof WINDOWS)[number];
export const NONE_WORDS = "none in this window";
export const NO_READ = "no read yet";
export { PAUSED_WORDS, PAUSE_WHY };

const text = (v: unknown): string => (typeof v === "string" ? v.trim() : typeof v === "number" && Number.isFinite(v) ? String(v) : "");
const list = <T,>(v: unknown): T[] => (Array.isArray(v) ? (v as T[]) : []);
const DAY = /^\d{4}-\d{2}-\d{2}$/;

// ---- the tag rule (a port of tag_action in warehouse/derived/policy_action_tags.py) ----------------------------------

export type TagTerm = { term: string; needs_any?: string[] };
export type TagSpec = { what?: string; terms: TagTerm[]; exclude_any?: string[]; exclude_docket_prefix?: string[]; exclude_docket_contains?: string[] };
export type TagRules = {
  version: string; fields_matched: string[]; strip: string[];
  agencies_in_scope: { federal: string[]; state: string[] }; action_types_in_scope: string[];
  municipal: { terms: string[] }; tags: Record<string, TagSpec>;
  dockets?: { list?: { docket: string; tags: string[]; grids?: string[] }[]; max_dockets_in_a_notice?: number };
};
export type TagHit = { tag: string; matched_term: string; matched_field: string };
/** What the rule reads of an action. A field the row lacks is the empty string. */
export type Tagged = { agency?: string | null; action_type?: string | null; docket?: string | null; [field: string]: unknown };

// White space as Python's str methods and its \s see it, so that both sides collapse the same runs.
// (Written from code points: no dash or space character other than the ASCII ones stands in this file.)
const cp = (...codes: number[]): string => String.fromCharCode(...codes);
const WS = new RegExp("[\\t\\n\\v\\f\\r\\x1c-\\x1f \\x85\\xa0" + cp(0x1680, 0x2000) + "-" + cp(0x200a, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000) + "]+", "g");
const DASH = new RegExp("[-" + cp(0x2010) + "-" + cp(0x2014) + "]", "g");
const raw = (v: unknown): string => (typeof v === "string" ? v : v === null || v === undefined ? "" : String(v));
/** Lower case, every hyphen and dash a space, white space collapsed. */
export function norm(s: unknown): string {
  return raw(s).toLowerCase().replace(DASH, " ").replace(WS, " ").trim();
}
const escaped = (s: string): string => s.replace(/[.*+?^${}()|[\]\\\/]/g, "\\$&");
const whole = new Map<string, RegExp>();
/** The term's words stand in the text (already normalized) as whole words, in order. */
export function has(term: string, normalized: string): boolean {
  let re = whole.get(term);
  if (!re) { re = new RegExp(`(?<![a-z0-9])${escaped(norm(term))}(?![a-z0-9])`); whole.set(term, re); }
  return re.test(normalized);
}
const parts = (docket: string): string[] => docket.split(/[;,]/);
/** The two letters that begin each docket number of the row (FERC writes "Docket No. CP13-499-006"). */
export function docketPrefixes(docket: unknown): string[] {
  const out: string[] = [];
  for (const part of parts(raw(docket))) { const m = /\b([A-Z]{2})\d{2}-\d/.exec(part); if (m) out.push(m[1]); }
  return out;
}
/** The docket field holds the docket number as a whole number (EL26-67 stands in "Docket No. EL26-67-000"). */
export function docketHolds(docket: unknown, number: string): boolean {
  return new RegExp(`(?<![A-Za-z0-9])${escaped(number)}(?![0-9])`).test(raw(docket));
}
/** The fields the rule matches in, as it reads them, and all of them joined. */
function fieldsOf(row: Tagged, rules: TagRules): { fields: Record<string, string>; both: string } {
  const fields: Record<string, string> = {};
  for (const f of rules.fields_matched) {
    let t = norm(row[f]);
    for (const s of rules.strip) { const cut = norm(s); if (cut) t = t.split(cut).join(" "); }
    fields[f] = t.replace(WS, " ").trim();
  }
  return { fields, both: rules.fields_matched.map((f) => fields[f]).join(" || ") };
}
/** The tags of one action by the rule file: at most one hit a tag; none when the action is out of scope or municipal. */
export function tagAction(row: Tagged, rules: TagRules): TagHit[] {
  const { fields, both } = fieldsOf(row, rules);
  const scope = rules.agencies_in_scope;
  if (![...scope.federal, ...scope.state].includes(raw(row.agency))) return [];
  if (!rules.action_types_in_scope.includes(raw(row.action_type))) return [];
  if (rules.municipal.terms.some((t) => has(t, both))) return [];
  const docket = raw(row.docket), prefixes = docketPrefixes(docket);
  const out: TagHit[] = [];
  for (const [tag, spec] of Object.entries(rules.tags)) {
    if (list<string>(spec.exclude_any).some((t) => has(t, both))) continue;
    if (prefixes.some((p) => list<string>(spec.exclude_docket_prefix).includes(p))) continue;
    if (list<string>(spec.exclude_docket_contains).some((c) => docket.toLowerCase().includes(c.toLowerCase()))) continue;
    let hit: TagHit | null = null;
    for (const f of rules.fields_matched) {
      for (const t of spec.terms) {
        if (has(t.term, fields[f]) && (!t.needs_any?.length || t.needs_any.some((n) => has(n, both)))) { hit = { tag, matched_term: t.term, matched_field: f }; break; }
      }
      if (hit) break;
    }
    if (!hit) {   // the dockets listed by number: a notice whose title is only the parties' names
      const many = parts(docket).filter((x) => /\d/.test(x)).length > (rules.dockets?.max_dockets_in_a_notice ?? 3);
      for (const d of many ? [] : list<{ docket: string; tags: string[] }>(rules.dockets?.list)) {
        if (d.tags.includes(tag) && docketHolds(docket, d.docket)) { hit = { tag, matched_term: d.docket, matched_field: "docket" }; break; }
      }
    }
    if (hit) out.push(hit);
  }
  return out;
}
/** The page's tags of an action: the rule on the row as read, united with the tags the warehouse's run gave it (by tag
 * name, in the rule's order; where both hold a tag the file's term and field are kept, since it read the printed text). */
export function uniteTags(mine: TagHit[], file: TagHit[] | undefined, rules: TagRules): TagHit[] {
  const held = list<TagHit>(file).filter((h) => h && typeof h.tag === "string");
  const order = Object.keys(rules.tags);
  const by = new Map<string, TagHit>();
  for (const h of mine) by.set(h.tag, h);
  for (const h of held) by.set(h.tag, h);
  return [...by.values()].filter((h) => order.includes(h.tag)).sort((a, b) => order.indexOf(a.tag) - order.indexOf(b.tag));
}
/** Out of scope whatever a file holds: the phrases the view never shows, with or without the rule file. */
export const MUNICIPAL = ["zoning", "city council", "county board"] as const;
/** The municipal phrase (the page's own three, then the rule file's) that a text holds (anywhere in it, so "rezoning" is caught by "zoning"), or null. */
export function municipalPhrase(s: string, rules: TagRules): string | null {
  const t = norm(s);
  return [...MUNICIPAL, ...rules.municipal.terms].find((w) => t.includes(norm(w))) ?? null;
}

// ---- the grid an action is under (data/policy/grids.json) -------------------------------------------------------------

export type GridsFile = { grids: { key: string; name: string; words: string[] }[]; paused?: Record<string, string>; rule?: string };
/** A grid's word stands in the text, not preceded and not followed by a letter or a digit: a word that holds a space in
 * any case, a single word in its own case. */
export function namesWord(word: string, s: string): boolean {
  const w = word.trim();
  if (!w) return false;
  return new RegExp(`(?<![A-Za-z0-9])${escaped(w)}(?![A-Za-z0-9])`, /\s/.test(w) ? "i" : "").test(s);
}
/** The grids an action is under: those its title, abstract or first paragraph name, and those of a listed docket that
 * tagged it. One that names no operator is under every grid (`all`). */
export function gridsOfAction(row: Tagged, hits: TagHit[], file: GridsFile, rules: TagRules): { grids: string[]; all: boolean } {
  const s = [raw(row.title), raw(row.abstract), raw(row.first_paragraph)].filter(Boolean).join(" ");
  const found = new Set<string>();
  for (const g of file.grids) if (list<string>(g.words).some((w) => namesWord(w, s))) found.add(g.key);
  const byName = new Map(file.grids.map((g) => [g.name, g.key]));
  for (const h of hits) {
    if (h.matched_field !== "docket") continue;
    const d = list<{ docket: string; grids?: string[] }>(rules.dockets?.list).find((x) => x.docket === h.matched_term);
    for (const name of list<string>(d?.grids)) { const k = byName.get(name); if (k) found.add(k); }
  }
  const grids = file.grids.map((g) => g.key).filter((k) => found.has(k));
  return { grids, all: grids.length === 0 };
}

// ---- the regulators and agencies of the filter (data/policy/refresh.json) --------------------------------------------

export type RefreshRegulator = {
  key: string; regulator: string; short: string; agency: string | null; jurisdiction: string; state?: string; refreshed: boolean;
  list_name?: string | null; list_url?: string | null; reason: string | null; refused?: { host: string; what: string }[];
  terms_class?: string | null; terms_url?: string | null; terms_quote?: string | null;
  last_run?: { at_utc: string; requests: number; new_rows: number; status: string; detail?: string } | null;
};
export type RefreshFeed = { agency: string; name: string; list_name?: string | null; refreshed: boolean; reason: string | null };
export type RefreshFile = { built_at_utc?: string; scope?: string; regulators: RefreshRegulator[]; federal_feeds?: RefreshFeed[] };

/** A choice of the agency filter: a federal agency, FERC or a state commission. */
export type Body = {
  key: string; label: string; name: string; jurisdiction: "federal" | "state";
  /** the same body's code in policy_actions, where it has one */
  agency: string | null;
  /** the short mark beside its name, and its hover: why its list is not refreshed, in the file's own words */
  mark: { words: string; why: string; kind: "not refreshed" | "in part" } | null;
  /** the hover of its name */
  why: string;
};
export const NOT_REFRESHED = "not refreshed";
export const IN_PART = "in part";
const SCOPE = ["federal", "state"];
const sentence = (s: string): string => (/[.!?]$/.test(s) ? s : `${s}.`);

/** The choices of the agency filter: the eleven regulators of the refresh file and the federal agencies of its feeds and
 * of the rows read, federal first. A regulator whose list refuses a plain request keeps its place, with its mark. */
export function bodiesOf(refresh: RefreshFile | null, agencies: string[]): Body[] {
  const out: Body[] = [], seen = new Set<string>(), codes = new Set<string>();
  const regs = list<RefreshRegulator>(refresh?.regulators).filter((r) => r && text(r.key) && SCOPE.includes(text(r.jurisdiction)));
  const feeds = list<RefreshFeed>(refresh?.federal_feeds).filter((f) => f && text(f.agency));
  const feedMark = (code: string): Body["mark"] => {
    const mine = feeds.filter((f) => f.agency === code), off = mine.filter((f) => f.refreshed === false && text(f.reason));
    if (!off.length) return null;
    const all = off.length === mine.length;
    return { words: all ? NOT_REFRESHED : IN_PART, kind: all ? "not refreshed" : "in part", why: off.map((f) => sentence(text(f.reason))).join(" ") };
  };
  const from = (names: string[]): string => (names.length ? ` Refreshed from: ${names.join("; ")}.` : "");
  const feedLists = (code: string | null): string[] => (code ? feeds.filter((f) => f.agency === code && f.refreshed !== false).map((f) => text(f.list_name)).filter(Boolean) : []);
  const push = (b: Body) => { if (!seen.has(b.key)) { seen.add(b.key); out.push(b); if (b.agency) codes.add(b.agency); } };
  const ofReg = (r: RefreshRegulator): Body => {
    const refused = list<{ host: string; what: string }>(r.refused).filter((x) => x && text(x.host));
    const reason = text(r.reason);
    // a list that refuses a plain request: the file's reason, word for word; a host of it that does: what it answered
    const mark: Body["mark"] = r.refreshed === false
      ? { words: NOT_REFRESHED, kind: "not refreshed", why: reason || "Its list is not refreshed; the file gives no reason." }
      : refused.length ? { words: IN_PART, kind: "in part", why: refused.map((x) => `${text(x.host)}: ${sentence(text(x.what) || "refuses a plain request")}`).join(" ") }
        : feedMark(text(r.agency));
    const lists = [r.refreshed !== false ? text(r.list_name) : "", ...feedLists(text(r.agency) || null)].filter(Boolean);
    return { key: text(r.key), label: text(r.short) || text(r.regulator), name: text(r.regulator), jurisdiction: r.jurisdiction as "federal" | "state", agency: text(r.agency) || null, mark,
      why: `${text(r.regulator)}.${from(lists)}` };
  };
  const federal = (code: string): Body => {
    const name = text(feeds.find((x) => x.agency === code)?.name) || code;
    return { key: code.toLowerCase(), label: code, name, jurisdiction: "federal", agency: code, mark: feedMark(code), why: `${name}.${from(feedLists(code))}` };
  };
  for (const r of regs) if (r.jurisdiction === "federal") push(ofReg(r));
  for (const f of feeds) if (!codes.has(f.agency) && !regs.some((r) => r.agency === f.agency)) push(federal(f.agency));
  for (const a of agencies) if (a && !codes.has(a) && !regs.some((r) => r.agency === a)) push(federal(a));
  for (const r of regs) if (r.jurisdiction === "state") push(ofReg(r));
  return out;
}

// ---- the topics of the filter ----------------------------------------------------------------------------------------

export type Topic = { key: string; label: string; kind: "tag" | "topic"; why: string };
const TAG_LABELS: Record<string, string> = { large_load: "Large loads", interconnection: "Interconnection", transmission_cost: "Transmission cost", tax_credit: "Tax credits" };
export const topicKey = (worded: string): string => worded.trim().toLowerCase().replace(/\s+/g, "-");
/** The eight topics: the rule's four tags (given to an action by the written rule), then the four topics of the docket rows. */
export function topicsOf(rules: TagRules, stateTopics: string[]): Topic[] {
  const tags: Topic[] = Object.entries(rules.tags).map(([k, spec]) => ({ key: k, kind: "tag", label: TAG_LABELS[k] ?? k.replace(/_/g, " "),
    why: `A tag given to an action by a written rule, version ${rules.version}, not by a model. ${text(spec.what)}` }));
  const seen = new Set(tags.map((t) => t.key));
  const topics: Topic[] = [];
  for (const w of stateTopics) {
    const k = topicKey(text(w));
    if (!k || seen.has(k)) continue;
    seen.add(k);
    topics.push({ key: k, kind: "topic", label: text(w).replace(/^./, (c) => c.toUpperCase()), why: "A topic of the proceedings and orders of FERC and the state commissions, as their file states it." });
  }
  return [...tags, ...topics];
}

// ---- a row of the view -----------------------------------------------------------------------------------------------

export type Action = {
  event_id: string; event_date: string; status: string | null; source_url: string | null; agency: string | null; action_type: string | null;
  title: string | null; abstract: string | null; docket: string | null; rin?: string | null; fr_document_number: string | null; why: string | null; model_id: string | null;
  /** not in the live set until the table's next load: null today */
  first_paragraph?: string | null; model_recheck?: string | null; model_rechecked_at?: string | null;
};
export type ActionRead = { action_event_id: string; plain_read: string | null; model_id: string | null; recheck?: string | null; rechecked_at?: string | null };
export type StateRow = {
  id: string; date: string; regulator: string; regulator_key: string; jurisdiction: string; state: string; docket: string; title: string; row_kind: string;
  topics: string[]; large_load: boolean; status_as_worded: string | null; status_class: string; url: string; page: string | number | null;
  sentence: string | null; sentence_withheld: string | null; sentence_from?: string | null; sentence_kind?: string | null; flags?: string[]; terms_class?: string | null;
  read: string | null; read_by: string | null; read_model: string | null; read_from: string | null; grids: string[]; all_grids: boolean; why_here: string | null; in_motion?: boolean;
};
export type StateFile = { built_at_utc?: string; as_of?: string; tables?: Record<string, number>; topics: string[]; rows: StateRow[]; not_in_file?: { count: number; by_reason?: Record<string, number> } };
export type ActionTagsFile = { built_at_utc?: string; rule_version?: string; actions_read?: number; tags: Record<string, TagHit[]>; first_paragraph?: Record<string, string> };

/** One line of the list, whichever kind it is: everything the face and the hovers show, already worded. */
export type WeekRow = {
  id: string; kind: "action" | "docket"; date: string; body: string;
  status: { words: string; stated: boolean; why: string };
  link: { href: string; words: string; tip: string; hover: "sentence" | "withheld" | "abstract" | "first paragraph" | "title" };
  title: string; titleWhy: string;
  topics: { key: string; why: string }[];
  grids: string[]; allGrids: boolean; largeLoad: boolean;
  read: { line: string | null; why: string };
};
export type Dropped = { id: string; why: string };

const TYPE: Record<string, string> = { rule: "Final rule", proposed_rule: "Proposed rule", notice: "Notice", press_release: "News release" };
const RECHECK: Record<string, (day: string | null) => string> = {
  rechecked: (day) => `Rechecked against the source text${day ? ` on ${day}` : ""}.`,
  "not rechecked": () => "Not rechecked against the source text.",
  "source not reachable": () => "Source not reachable when rechecked.",
};
/** The words a recheck adds to a read's hover; nothing where the row holds no recheck. */
export function recheckWords(state: unknown, at: unknown): string {
  const f = RECHECK[text(state)];
  return f ? f(dayWords(text(at).slice(0, 10))) : "";
}
const httpOf = (u: unknown): string | null => { const s = text(u); return /^https?:\/\/[^\s"'<>]+$/i.test(s) ? s : null; };
const an = (w: string): string => (/^[aeiou]/i.test(w) ? "an" : "a");

/** The status an action shows: the source's own words; where its record words none, the document's type. */
export function actionStatus(a: Action): WeekRow["status"] {
  const worded = text(a.status), type = TYPE[text(a.action_type)] ?? "";
  if (worded && text(a.action_type) === "press_release") return { words: worded, stated: true, why: "A news release of the agency, as the table holds it." };
  if (worded) return { words: worded, stated: true, why: `The action line of the Federal Register's record, in its own words.${type ? ` The document is ${an(type)} ${type.toLowerCase()}.` : ""}` };
  if (type) return { words: type, stated: false, why: "The Federal Register's record words no action line for this document; this is its document type." };
  return { words: "not stated", stated: false, why: "The source words no status for this document." };
}
/** The one-line read of an action: the impact read's plain line; else the scorer's one line; both a model's. */
export function actionRead(a: Action, read: ActionRead | null | undefined): WeekRow["read"] {
  const plain = text(read?.plain_read), why = text(a.why);
  if (plain) {
    const model = text(read?.model_id), re = recheckWords(read?.recheck, read?.rechecked_at);
    return { line: plain, why: `A model's read${model ? `, by ${model}` : ""}: one line written from the action's own text, kept only where the quotations it rests on were found word for word in that text. Not the agency's words.${re ? ` ${re}` : ""}` };
  }
  if (why) {
    const model = text(a.model_id), re = recheckWords(a.model_recheck, a.model_rechecked_at);
    return { line: why, why: `A model's read${model ? `, by ${model}` : ""}: the scorer's one line, written from the title and the Register's summary, or from the first paragraph of the printed text where the summary is empty. Not the agency's words.${re ? ` ${re}` : ""}` };
  }
  return { line: null, why: NO_READ_WHY };
}
/** The link of an action: the agency and its docket or document number; the Register's summary on hover, or the first
 * paragraph of the printed text, or (where neither is held) the title, each named for what it is. */
export function actionLink(a: Action, href: string): WeekRow["link"] {
  const agency = text(a.agency), dockets = raw(a.docket).split(";").map((x) => x.trim()).filter(Boolean), fr = text(a.fr_document_number);
  const number = dockets[0] || (fr ? `FR Doc. ${fr}` : text(a.action_type) === "press_release" ? "news release" : "source document");
  const abstract = text(a.abstract), first = text(a.first_paragraph), title = text(a.title);
  const lead = abstract ? `"${abstract}" The Federal Register's summary.` : first ? `"${first}" The first paragraph of the printed text.`
    : title ? `No summary of this document is held. Its title: "${title}"` : "No summary of this document is held.";
  const more = [dockets.length > 1 ? `Also: ${dockets.slice(1).join(", ")}.` : "", fr && dockets.length ? `Federal Register document ${fr}.` : ""].filter(Boolean).join(" ");
  return { href, words: agency ? `${agency}, ${number}` : number, tip: more ? `${lead} ${more}` : lead, hover: abstract ? "abstract" : first ? "first paragraph" : "title" };
}
const TAG_FIELD: Record<string, string> = { title: "title", abstract: "summary", first_paragraph: "first paragraph of the printed text", docket: "docket field (a docket the rule lists by number)" };

/** An action as a row of the view, or the reason it is not shown. */
export function actionRow(a: Action, read: ActionRead | null | undefined, hits: TagHit[], under: { grids: string[]; all: boolean }, bodies: Body[], topics: Topic[], rules: TagRules): { row: WeekRow | null; dropped: Dropped | null } {
  const id = text(a.event_id), date = text(a.event_date).slice(0, 10), href = httpOf(a.source_url);
  const body = bodies.find((b) => b.agency === text(a.agency));
  if (!DAY.test(date)) return { row: null, dropped: { id, why: "no day" } };
  if (!href) return { row: null, dropped: { id, why: "no address of a source document" } };
  if (!body) return { row: null, dropped: { id, why: "an agency outside this page's scope" } };
  const known = new Set(topics.map((t) => t.key));
  const row: WeekRow = {
    id, kind: "action", date, body: body.key, status: actionStatus(a), link: actionLink(a, href), title: text(a.title), titleWhy: "",
    topics: hits.filter((h) => known.has(h.tag)).map((h) => ({ key: h.tag, why: `Tagged by the written rule, version ${rules.version}: "${h.matched_term}" in the ${TAG_FIELD[h.matched_field] ?? h.matched_field}.` })),
    grids: under.grids, allGrids: under.all, largeLoad: hits.some((h) => h.tag === "large_load"), read: actionRead(a, read),
  };
  return municipalPhrase(wordsOf(row), rules) ? { row: null, dropped: { id, why: "a phrase of it is outside this page's scope" } } : { row, dropped: null };
}
/** A docket row of the state file as the block "Rules in motion" reads one (lib/rules.ts words its status and hovers). */
export function asRule(s: StateRow): RuleRow {
  return {
    id: text(s.id), date: text(s.date), regulator: text(s.regulator), jurisdiction: text(s.jurisdiction), state: text(s.state), docket: text(s.docket), title: text(s.title),
    row_kind: text(s.row_kind), topic: list<string>(s.topics).map(text).filter(Boolean).join("; "), tags: [], status_as_worded: s.status_as_worded, status_class: text(s.status_class), url: text(s.url),
    page: s.page, sentence: s.sentence, read: s.read, read_by: s.read_by, read_model: s.read_model, read_from: s.read_from, why_here: s.why_here, sentence_from: s.sentence_from, sentence_withheld: s.sentence_withheld,
  };
}
/** A proceeding or an order as a row of the view, or the reason it is not shown. */
export function docketRow(s: StateRow, bodies: Body[], topics: Topic[], rules: TagRules): { row: WeekRow | null; dropped: Dropped | null } {
  const r = asRule(s), id = r.id || `${r.regulator} ${r.docket} ${r.date}`.trim(), href = linkOf(r);
  const body = bodies.find((b) => b.key === text(s.regulator_key));
  if (!SCOPE.includes(r.jurisdiction)) return { row: null, dropped: { id, why: "a body outside this page's scope" } };
  if (!dayWords(r.date)) return { row: null, dropped: { id, why: "no day" } };
  if (!href) return { row: null, dropped: { id, why: "no address of a source document" } };
  if (!body) return { row: null, dropped: { id, why: "a regulator the refresh file does not list" } };
  if (!text(r.sentence) && !withheldOf(r)) return { row: null, dropped: { id, why: "neither a sentence of its document nor the reason it is not copied" } };
  const known = new Map(topics.map((t) => [t.key, t]));
  const kind = hoverKind(r);
  const row: WeekRow = {
    id, kind: "docket", date: r.date, body: body.key, status: statusOf(r),
    link: { href, words: docketWords(r), tip: docketTip(r), hover: kind === "withheld" ? "withheld" : "sentence" },
    title: r.title, titleWhy: text(s.why_here),
    topics: list<string>(s.topics).map((w) => topicKey(text(w))).filter((k) => known.has(k)).map((k) => ({ key: k, why: known.get(k)!.why })),
    grids: list<string>(s.grids).map(text).filter(Boolean), allGrids: s.all_grids === true, largeLoad: s.large_load === true, read: readOf(r),
  };
  return municipalPhrase(wordsOf(row), rules) ? { row: null, dropped: { id, why: "a phrase of it is outside this page's scope" } } : { row, dropped: null };
}
/** Every word of a row that the view would show, on its face or on hover. */
export function wordsOf(r: WeekRow): string {
  return [r.status.words, r.link.words, r.link.tip, r.title, r.titleWhy, r.read.line ?? ""].filter(Boolean).join(" \n ");
}
/** The hover of the count of rows held that the view does not show: each by its id, with why. */
export function droppedTip(dropped: Dropped[], rules: TagRules): string {
  return `Not shown: ${dropped.map((d) => `${municipalPhrase(d.id, rules) ? "a row" : d.id} (${d.why})`).join("; ")}.`;
}

// ---- the windows -----------------------------------------------------------------------------------------------------

/** The UTC day of a time, "2026-10-08". */
export const dayOf = (ms: number): string => new Date(ms).toISOString().slice(0, 10);
/** The first day of a window: `days` days before `today` (a UTC day). */
export function sinceDay(today: string, days: number): string {
  const [y, m, d] = today.split("-").map(Number);
  return dayOf(Date.UTC(y, m - 1, d) - days * 86_400_000);
}
/** A row is of the last `days` days when its day is on or after the window's first. A document the Federal Register
 * has dated a day or two ahead is of the window too. */
export function inWindow(date: string, today: string, days: number): boolean {
  return DAY.test(date) && date >= sinceDay(today, days);
}
export function windowWhy(today: string, days: number): string {
  return `Dated ${dayWords(sinceDay(today, days))} or later: the ${days} days counted back from today, ${dayWords(today)} (UTC). An action's day is its publication or release day; a docket row's is its document's.`;
}

// ---- the filters and their address ----------------------------------------------------------------------------------

export type Chosen = { days: Days; agency: string; topic: string; grid: string; large: boolean };
export type Known = { bodies: string[]; topics: string[]; grids: string[] };
export const NOTHING: Chosen = { days: 7, agency: "", topic: "", grid: "", large: false };
/** What an address chooses. A value the view does not know is no choice. */
export function chosenOf(q: Record<string, string | undefined>, known: Known): Chosen {
  const pick = (v: string | undefined, among: string[]) => { const s = (v ?? "").trim().toLowerCase(); return among.includes(s) ? s : ""; };
  return { days: q.days === "30" ? 30 : 7, agency: pick(q.agency, known.bodies), topic: pick(q.topic, known.topics), grid: pick(q.grid, known.grids), large: q.large === "1" };
}
/** The address of the view with these choices; a choice not made is not in it. */
export function weekHref(c: Chosen): string {
  const q = new URLSearchParams({ view: "week" });
  if (c.days === 30) q.set("days", "30");
  if (c.agency) q.set("agency", c.agency);
  if (c.topic) q.set("topic", c.topic);
  if (c.grid) q.set("grid", c.grid);
  if (c.large) q.set("large", "1");
  return `/policy?${q}`;
}
/** A grid whose rows are never listed: MISO, whatever a file says. */
export const paused = (grid: string): boolean => grid === "miso";
/** A row is under a grid when it names it, or names no operator (then it is under every grid but MISO). */
export function underGrid(r: WeekRow, grid: string): boolean {
  if (!grid) return true;
  if (paused(grid)) return false;
  return r.allGrids || r.grids.includes(grid);
}
export function matches(r: WeekRow, c: Chosen, today: string, skip: { agency?: boolean; topic?: boolean } = {}): boolean {
  return inWindow(r.date, today, c.days) && underGrid(r, c.grid) && (!c.large || r.largeLoad)
    && (skip.agency || !c.agency || r.body === c.agency) && (skip.topic || !c.topic || r.topics.some((t) => t.key === c.topic));
}
/** Newest first; then by agency, link words and id, so the order never depends on a file's or a table's. */
export function sortRows(rows: WeekRow[]): WeekRow[] {
  return [...rows].sort((a, b) => (a.date !== b.date ? (a.date < b.date ? 1 : -1) : a.body !== b.body ? (a.body < b.body ? -1 : 1) : a.link.words !== b.link.words ? (a.link.words < b.link.words ? -1 : 1) : a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}
/** The rows the list shows. */
export function shownRows(rows: WeekRow[], c: Chosen, today: string): WeekRow[] {
  return paused(c.grid) ? [] : sortRows(rows.filter((r) => matches(r, c, today)));
}
/** The list in groups, one an agency, in the filter's order; an agency with no row has no group. */
export function groupsOf(rows: WeekRow[], bodies: Body[]): { body: Body; rows: WeekRow[] }[] {
  return bodies.map((body) => ({ body, rows: rows.filter((r) => r.body === body.key) })).filter((g) => g.rows.length > 0);
}

// ---- the chart: counts by agency and topic ---------------------------------------------------------------------------

export type Line = { body: Body; total: number; byTopic: number[]; none: number };
/** The counts the chart draws: for the window, the grid and the large-load choice (not the agency or the topic chosen,
 * which the chart marks instead), one line an agency that holds a row, a count a topic. A row with two topics counts
 * under each; `none` counts the rows with no topic. */
export function countsOf(rows: WeekRow[], c: Chosen, today: string, bodies: Body[], topics: Topic[]): { lines: Line[]; max: number; total: number } {
  const inView = paused(c.grid) ? [] : rows.filter((r) => matches(r, c, today, { agency: true, topic: true }));
  const lines: Line[] = [];
  for (const body of bodies) {
    const mine = inView.filter((r) => r.body === body.key);
    if (!mine.length) continue;
    lines.push({ body, total: mine.length, byTopic: topics.map((t) => mine.filter((r) => r.topics.some((x) => x.key === t.key)).length), none: mine.filter((r) => r.topics.length === 0).length });
  }
  return { lines, max: Math.max(0, ...lines.flatMap((l) => l.byTopic)), total: inView.length };
}
/** The words a count answers the mouse with. */
export function cellTip(line: Line, topic: Topic | null, n: number, days: number): string {
  const what = topic ? (topic.kind === "tag" ? `tagged ${topic.label.toLowerCase()}` : `on ${topic.label.toLowerCase()}`) : "in all";
  return `${line.body.label}: ${n} ${n === 1 ? "action" : "actions"} ${what} in the last ${days} days`;
}
/** The reason a choice leaves nothing, for the placeholder's hover. */
export function emptyWhy(c: Chosen, today: string, bodies: Body[], topics: Topic[], gridNames: Record<string, string>): string {
  const said = [c.agency ? `of ${bodies.find((b) => b.key === c.agency)?.label ?? c.agency}` : "", c.topic ? `on ${(topics.find((t) => t.key === c.topic)?.label ?? c.topic).toLowerCase()}` : "",
    c.grid ? `under ${gridNames[c.grid] ?? c.grid.toUpperCase()}` : "", c.large ? "that touches large loads" : ""].filter(Boolean).join(" ");
  return `No action${said ? ` ${said}` : ""} is held that is dated ${dayWords(sinceDay(today, c.days))} or later.`;
}
