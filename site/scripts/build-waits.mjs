// Energy Research Warehouse (ERW) site, session 188: what waits for the owner, read from the session reports.
//
// Reads, from the repository (one level above site/), as scripts/build-content.mjs reads the documents:
//   archive/sessions/SESSION_<N>_REPORT.md   every session report
//   archive/sessions/LAST_ANSWERED           the last report whose rulings the owner has answered (a person edits it)
// and writes site/content/waits.json, which /internal/waits imports. Runs before `next dev` and `next build`
// (package.json predev and prebuild, after build-content.mjs), so the page reads no file at request time and is as
// new as the build. Nothing here is written by a model, and nothing is reworded: every item is the report's own text,
// with the line it stands on.
//
// What waits, in a report after the last one answered:
//   1. every item (a list item, a table row, a paragraph) of a section whose heading says it is for the owner:
//      "For Samuel's ruling", "For Samuel", "To finish (Samuel)", "Open questions", "Proposed cuts, for your ruling",
//      "Held for your approval" and the like (WAIT_HEAD below);
//   2. any item elsewhere in the report that says so itself: "your ruling", "you rule", "to be confirmed by Samuel",
//      "Rule on items 3 and 16", "Samuel: fill ..." (INLINE below). The section "The prompt" is the owner's own
//      words and is not read; neither are the click-by-click steps ("What to review"), which quote the pages.
// What was decided without him ("Decisions made without you", "Decisions made alone") is kept beside it, folded: it
// does not wait, and he may overrule it. A report with nothing waiting is not listed.
//
// The folder being absent (a build that does not see the repository above site/) is said in the file, and the page
// says it: this script never fails a build, because the page it feeds is internal.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const REPO_URL = "https://github.com/SamuelEnrique/erw";
export const REPORTS = "archive/sessions";
export const MARKER = "archive/sessions/LAST_ANSWERED";
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

// a heading that says its section is for the owner
export const WAIT_HEAD = [
  /\bfor (samuel|you\b|your\b|the owner|a human|the human|a person)/i,
  /\((for )?samuel\)/i,
  /^(\d+\.\s*)?open questions?\b/i,
  /^questions?\b.*\bsamuel\b/i,
  /\bsamuel must\b/i,
  /,\s*yours\s*$/i,
  /^decide before\b/i,
  /\bneeds? (your|samuel's|the owner's) (ruling|approval|decision)\b/i,
];
// a heading that speaks of rulings already given, or is not a list of anything
export const NOT_WAIT_HEAD = /\b(applied|as built|settled|answered|closed)\b|^verdict\b/i;
// the click-by-click steps quote the pages' own words ("Waits for Samuel", "your ruling"): they are not read
export const STEPS_HEAD = /^what to (review|click)\b/i;
export const DECIDED_HEAD = /^(\d+\.\s*)?decisions? (i )?made (without (you|a human)|alone)\b/i;
export const PROMPT_HEAD = /^the prompt\b/i;

// an item that says itself that it waits for the owner
const WHOSE = "(?:your|samuel's|samuel’s|the owner's|the owner’s)";
export const INLINE = [
  // "your ruling", "Samuel's approval"; not "per your ruling", "as your ruling says": those were given
  new RegExp(`(?<!\\b(?:per|by|under|as|following|since|with|applied|from)\\s)\\b${WHOSE} (?:own )?(?:rulings?|approval|word|decision|sign-off)\\b`, "i"),
  /\b(?:you|samuel|the owner) (?:rule|rules|decide|decides)\b/i,
  /\bfor you to (?:decide|rule|confirm|approve|choose)\b/i,
  /\bto be confirmed by (?:samuel|you|the owner)\b/i,
  /\b(?:waits?|waiting) for (?:samuel|you\b|your\b|the owner)/i,
  /\bheld for (?:your|samuel's|the owner's)\b/i,
  /^\W*(?:rule on|rules to make)\b/i,
  /^\W*samuel\W{0,3}:/i,
  /\(samuel\)\W*$/i,
];
// an item of a section for the owner that says there is nothing
const NOTHING = /^\W*(?:nothing|none|no item|not applicable)\b/i;

/** An item's text without this page's own name and address, which hold the words "waits for Samuel". */
export function own(text) {
  return String(text).replace(/waits for samuel \(internal\)/gi, " ").replace(/\/internal\/waits\b/gi, " ").replace(/"waits for samuel"/gi, " ");
}

/** SESSION_180B_REPORT.md: { id: "180b", n: 180, suffix: "b", order: 18002 }; null for any other name. */
export function reportId(file) {
  const m = /^SESSION_(\d+)([A-Za-z]?)_REPORT\.md$/.exec(file);
  if (!m) return null;
  const n = Number(m[1]);
  const suffix = m[2].toLowerCase();
  return { id: `${n}${suffix}`, n, suffix, order: n * 100 + (suffix ? suffix.charCodeAt(0) - 96 : 0) };
}

/** The marker file: "last_answered: 171" and, optionally, "on: 2026-10-09"; a line beginning with # is a note. */
export function parseMarker(text) {
  const out = { path: MARKER, last: null, order: null, on: null, error: null };
  if (text === null || text === undefined) return { ...out, error: "the file is absent" };
  for (const ln of String(text).replace(/\r/g, "").split("\n")) {
    const t = ln.trim();
    if (!t || t.startsWith("#")) continue;
    const m = /^([a-z_]+)\s*:\s*(.*)$/i.exec(t);
    if (!m) return { ...out, error: `a line that is not "name: value": ${t.slice(0, 60)}` };
    const k = m[1].toLowerCase();
    const v = m[2].trim();
    if (k === "last_answered") {
      const id = reportId(`SESSION_${v.toUpperCase()}_REPORT.md`);
      if (!id) return { ...out, error: `last_answered is not a session number: ${v.slice(0, 40)}` };
      out.last = id.id;
      out.order = id.order;
    } else if (k === "on") {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(v) || Number.isNaN(Date.parse(`${v}T00:00:00Z`))) return { ...out, error: `on is not a date YYYY-MM-DD: ${v.slice(0, 40)}` };
      out.on = v;
    } else {
      return { ...out, error: `a name this file does not hold: ${k}` };
    }
  }
  if (out.last === null) return { ...out, error: "no line last_answered: <session number>" };
  return out;
}

export function headKind(text) {
  const h = text.trim();
  if (PROMPT_HEAD.test(h)) return "prompt";
  if (STEPS_HEAD.test(h)) return "steps";
  if (DECIDED_HEAD.test(h)) return "decided";
  if (!NOT_WAIT_HEAD.test(h) && WAIT_HEAD.some((re) => re.test(h))) return "wait";
  return "none";
}

/** The cells of a table's line. */
function cells(line) {
  const t = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  return t.split(/(?<!\\)\|/).map((c) => c.trim());
}

/** A section's lines ([{ n, text }]) as items: list items with what hangs under them, table rows, paragraphs. A
 * fenced block belongs to the item before it. Each item: { line, md, plain }. */
export function items(lines) {
  const out = [];
  let cur = null;
  let fence = false;
  const flush = () => { if (cur) out.push(cur); cur = null; };
  for (const { n, text } of lines) {
    if (/^\s*(```|~~~)/.test(text)) {
      if (!cur) cur = { line: n, kind: "para", lines: [], blank: false };
      if (cur.blank) cur.lines.push("");
      cur.blank = false;
      cur.lines.push(text);
      fence = !fence;
      continue;
    }
    if (fence) { cur.lines.push(text); continue; }
    if (!text.trim()) { if (cur) cur.blank = true; continue; }
    const top = /^ {0,1}([-*+]|\d+[.)])\s+\S/.test(text);
    const hangs = /^(\s{2,}|\t)\S/.test(text);
    const table = /^\s*\|/.test(text);
    if (top) { flush(); cur = { line: n, kind: "item", lines: [text], blank: false }; continue; }
    if (table && !(cur && cur.kind === "item" && hangs)) {
      if (cur && cur.kind === "table" && !cur.blank) { cur.lines.push(text); cur.at.push(n); continue; }
      flush();
      cur = { line: n, kind: "table", lines: [text], at: [n], blank: false };
      continue;
    }
    if (cur && cur.kind === "item" && (hangs || !cur.blank)) {
      if (cur.blank) cur.lines.push("");
      cur.blank = false;
      cur.lines.push(text);
      continue;
    }
    if (cur && cur.kind === "para" && !cur.blank) { cur.lines.push(text); continue; }
    flush();
    cur = { line: n, kind: "para", lines: [text], blank: false };
  }
  flush();
  const made = [];
  for (const b of out) {
    if (b.kind !== "table") {
      made.push({ line: b.line, md: b.lines.join("\n"), plain: b.lines.join(" ") });
      continue;
    }
    // a table: each row is an item, said with the table's own column names
    const sep = b.lines.findIndex((l) => /^\s*\|?\s*:?-{2,}/.test(l));
    const head = sep > 0 ? cells(b.lines[sep - 1]) : [];
    for (let i = sep >= 0 ? sep + 1 : 0; i < b.lines.length; i += 1) {
      const row = cells(b.lines[i]);
      if (row.every((c) => !c)) continue;
      const md = row.map((c, j) => (head[j] ? `**${head[j]}:** ${c}` : c)).filter((c, j) => row[j]).join("  \n");
      made.push({ line: b.at[i], md, plain: row.join(" ") });
    }
  }
  return made;
}

/** The first date written in the report's first lines: { iso, words } or null. Never guessed. */
export function reportDate(lines) {
  const re = new RegExp(`\\b(\\d{1,2}) (${MONTHS.join("|")}) (\\d{4})\\b`);
  for (const ln of lines.slice(0, 14)) {
    const m = re.exec(ln);
    if (m) return { iso: `${m[3]}-${String(MONTHS.indexOf(m[2]) + 1).padStart(2, "0")}-${m[1].padStart(2, "0")}`, words: `${m[1]} ${m[2]} ${m[3]}` };
  }
  return null;
}

/** One report: its number, title and date, what waits and what was decided without the owner. */
export function parseReport(file, raw) {
  const id = reportId(file);
  const lines = String(raw).replace(/\r\n/g, "\n").split("\n");
  const h1 = lines.find((l) => /^# \S/.test(l));
  const heading = h1 ? h1.slice(2).trim() : file;
  const title = heading.replace(/^Session \d+[A-Za-z]?\b[^:]*:\s*/i, "") || heading;
  const date = reportDate(lines);
  const waits = [];
  const decided = [];
  // session 414: what a section for the owner holds when it says there is nothing ("Nothing new."), for the ledger's note
  const nothing = [];
  let h2 = { text: "", kind: "none" };
  let sec = { text: "The report's opening lines", kind: "none" };
  let buf = [];
  let fence = false;
  const close = () => {
    if (sec.kind !== "prompt" && sec.kind !== "steps") {
      for (const it of items(buf)) {
        const bare = it.plain.replace(/^\s*([-*+]|\d+[.)])\s+/, "").replace(/[*_`]/g, "");
        const says = INLINE.some((re) => re.test(own(bare)));
        if (sec.kind === "wait") {
          if (!(NOTHING.test(bare) && bare.length < 200 && !says)) waits.push({ section: sec.text, line: it.line, md: it.md, kind: "section" });
          else nothing.push({ section: sec.text, line: it.line, md: it.md });
        } else if (says) {
          waits.push({ section: sec.text, line: it.line, md: it.md, kind: "inline" });
        } else if (sec.kind === "decided") {
          decided.push({ section: sec.text, line: it.line, md: it.md });
        }
      }
    }
    buf = [];
  };
  lines.forEach((text, i) => {
    if (/^\s*(```|~~~)/.test(text)) fence = !fence;
    const m = fence ? null : /^(#{1,4}) +(.*\S)\s*$/.exec(text);
    if (!m) { buf.push({ n: i + 1, text }); return; }
    close();
    const level = m[1].length;
    const kind = headKind(m[2]);
    if (level <= 2) {
      h2 = { text: m[2], kind: level === 1 ? "none" : kind };
      sec = { text: level === 1 ? "The report's opening lines" : m[2], kind: h2.kind };
    } else {
      // a part of a section takes the section's kind unless its own heading says otherwise
      sec = { text: m[2], kind: kind !== "none" ? kind : h2.kind };
    }
  });
  close();
  waits.sort((a, b) => (a.kind === b.kind ? a.line - b.line : a.kind === "section" ? -1 : 1));
  return {
    ...id, file, path: `${REPORTS}/${file}`, heading, title, date: date ? date.iso : null, date_words: date ? date.words : null,
    url: `${REPO_URL}/blob/main/${REPORTS}/${file}`, waits, decided, nothing,
  };
}

// ---------------------------------------------------------------------------------------------------------------------
// Session 414: the ledger of one run of sessions (LEDGER below). Every item of a section for the owner ("For Samuel's
// ruling") in those reports, listed once: an item that a later report asks again is merged with it, and keeps the link
// to every report that asks it. Each is then put under what it blocks (BLOCKS), and the three that the state notes of
// docs/state/ rank highest by value are put first. Fixed rules and no model: each merge, each place and each rank keeps
// the rule that made it and the words that matched, and the page prints them, so a person can read why and overrule it.
// A report that lands later (a session run on another branch) is read by the next build, and its items join.

// Session 425: the run ends at the newest report present at the build ("newest"), so that a report that lands later
// joins the ledger without a change here; 351 to 413 until then. resolveRun turns "newest" into that number.
export const LEDGER = { from: 351, to: "newest" };

/** The run with its end as a number: "newest" is the highest session number among the reports read, from LEDGER.from. */
export function resolveRun(reports, run = LEDGER) {
  if (run.to !== "newest") return run;
  const ns = (reports ?? []).map((r) => r.n).filter((n) => Number.isFinite(n) && n >= run.from);
  return { from: run.from, to: ns.length ? Math.max(...ns) : run.from };
}
export const NOTES = "docs/state";

// an item that only sends the reader to another list and asks nothing of its own ("The items of the note's ...")
export const POINTER = /^\W*the (?:\w+ )?items of (?:the|a|this) (?:\w+ )?(?:note|list)\b/i;

// a subject several reports name in different words: items that match the same one are one item
export const SUBJECTS = [
  { key: "redivis-storage", label: "the Redivis storage", re: /\bredivis\W{0,3}s?\s+(?:free\s+)?(?:storage|10 GB)\b|\b10 GB\b|^\W*the storage\b/i },
];

// what an item blocks; the rules of BLOCK_RULES are tried in their order and the first that matches places the item
export const BLOCKS = [
  { key: "money", label: "Money", says: "a cost to pay or a plan to choose" },
  { key: "pull", label: "A data pull", says: "data to fetch, load, restore or publish, or a publisher to ask" },
  { key: "figure", label: "A ruling on a figure", says: "which number a page or a table states, and how" },
  { key: "page", label: "A public page", says: "what a page shows, links or offers, or who walks it" },
  { key: "other", label: "None of the four", says: "the machines, the repository, security, a method's sign-off: no rule above matched" },
];
export const BLOCK_RULES = [
  { block: "money", re: /\bpaid tier\b|\bupgrade\b|\bsubscription\b|\bbudget\b|\binvoice\b|\b(?:project|supabase|account)\W{0,2}s? plan\b|\bUSD \d/i },
  { block: "pull", re: /\bfor the data machine\b|\binformation request\b|\bnew source\b|\ba pull\b|\bdata access portal\b/i },
  { block: "page", re: /\bon a phone\b|\bphone width\b|\bat 390\b/i },
  { block: "figure", re: /\bheadline\b|\btwo figures\b|\bpublished figures\b|\bnewey-west\b|\bverdict\b|\ba cent\b|\btolerance\b|\bthreshold\b|\bbasis\b|\bcounts? as\b/i },
  { block: "page", re: /\bpages?\b|\bwalk(?:s|through)?\b|\bcards?\b|\bdownloads?\b|(?:^|[\s(`])\/[a-z][a-z-]+/i },
  { block: "pull", re: /\bpull\b|\bdata machine\b|\brestor(?:e|ed|ing)\b|\barchive\b|\blive set\b|\bload(?:s|ed|er|ing)?\b|\bletters?\b|\blicen[cs]e\b|\bredivis\b|\bupload(?:s|ed|er)?\b|\bsource\b/i },
  { block: "other", re: /[\s\S]/ },
];

// two items ask the same thing when (a) they match one subject, (b) one names the other's session and they share at
// least NAMED.words words, NAMED.share of the shorter's, or (c) they share SAME.words words, SAME.share of the shorter's.
// (b) and (c) merge one item with one: an item that matches two of another report's items restates both, and is kept
// beside each of them instead of joining them into one.
export const NAMED = { words: 3, share: 0.2 };
export const SAME = { words: 5, share: 0.6 };

// the notes: a section "Waiting for you" or "What waits for Samuel"; it ranks by value only where it says so
export const NOTE_HEAD = /^(?:what )?wait(?:s|ing) for (?:you|samuel)\b/i;
export const BY_VALUE = /\bhighest value first\b|\bin the order of (?:their )?value\b|\bby value\b/i;
const DAY_PART = [["night", 0], ["morning", 1], ["day", 2], ["pm", 3], ["afternoon", 3], ["evening", 4]];

const STOP = new Set(("the and for whether should this that with from its are not now but was were has have had been into than then them "
  + "they their there these those which what when where while who will would could can may might must about after again all any because "
  + "before being both down each few here how more most once only other our out over own same some such too under until very you your one "
  + "two three four five six seven eight nine ten also just per via item today none nothing new session samuel ruling question wait note "
  + "does did done keep make made take give see seen yet still every less much many like ask asked than it's "
  // the folders and file kinds that paths share without sharing a subject
  + "site data docs json csv warehouse scripts runs tests lib app components content").split(" "));

/** The words an item is compared by: lower case, no markup, no short or common word, a plural's s taken off; a path or
 * file name is kept whole and also by its parts. */
export function tokens(text) {
  const t = String(text).toLowerCase().replace(/\[([^\]]*)\]\([^)]*\)/g, "$1").replace(/[*`"“”]/g, " ");
  const out = new Set();
  for (const m of t.matchAll(/[a-z0-9][a-z0-9_./-]*[a-z0-9]/g)) {
    const w = m[0];
    const parts = /[/.]/.test(w) && !/^[\d.,]+$/.test(w) ? w.split(/[/.]+/) : [];
    for (const x of [w, ...parts]) {
      let y = x;
      if (/^[a-z]{4,}s$/.test(y) && !/(ss|us|is)$/.test(y)) y = y.slice(0, -1);
      if (y.length < 3 || STOP.has(y) || /^\d{1,3}$/.test(y)) continue;
      out.add(y);
    }
  }
  return out;
}

/** The sessions an item names: "session 359", "sessions 359 and 379", "sessions 351 to 356", "**368**". */
export function sessionsNamed(text) {
  const out = new Set();
  const t = String(text).replace(/[`]/g, "");
  for (const m of t.replace(/\*/g, "").matchAll(/\bsessions?\s+(\d{3}[a-z]?)((?:\s*(?:,|and|or|to)\s*\d{3}[a-z]?\b)*)/gi)) {
    const rest = m[2].match(/\d{3}[a-z]?/gi) ?? [];
    const nums = [m[1], ...rest].map((x) => x.toLowerCase());
    if (rest.length === 1 && /^\s*to\b/i.test(m[2]) && /^\d+$/.test(nums[0]) && /^\d+$/.test(nums[1]) && Number(nums[1]) - Number(nums[0]) <= 100) {
      for (let k = Number(nums[0]); k <= Number(nums[1]); k += 1) out.add(String(k));
    } else nums.forEach((x) => out.add(x));
  }
  for (const m of t.matchAll(/\*\*(\d{3}[a-z]?)\*\*/g)) out.add(m[1].toLowerCase());
  return out;
}

/** The subject an item matches, or null. */
export function subjectOf(text) {
  const s = SUBJECTS.find((x) => x.re.test(text));
  return s ? s.key : null;
}

/** Where an item goes: { block, rule, said }, the first rule of BLOCK_RULES that its words match. */
export function blockOf(text) {
  const t = own(String(text).replace(/[*`]/g, ""));
  for (let i = 0; i < BLOCK_RULES.length; i += 1) {
    const m = BLOCK_RULES[i].re.exec(t);
    if (m) return { block: BLOCK_RULES[i].block, rule: i + 1, said: BLOCK_RULES[i].block === "other" ? null : m[0].trim() };
  }
  return { block: "other", rule: BLOCK_RULES.length, said: null };
}

// an item without its own list marker, so that "6. **Whether ...**" is not drawn as a list that starts at 6
const plainMd = (md) => String(md).replace(/^\s*([-*+]|\d+[.)])\s+/, "");
const plainOf = (md) => String(md).replace(/^\s*([-*+]|\d+[.)])\s+/, "").replace(/\s+/g, " ").trim();

/** Why two items ask the same thing, or null. a and b each hold { session, tokens, names, subject }. */
export function sameAsk(a, b) {
  if (a.session === b.session) return null;
  if (a.subject && a.subject === b.subject) return { rule: "subject", subject: a.subject, words: [] };
  const words = [...a.tokens].filter((w) => b.tokens.has(w)).sort();
  const share = words.length / (Math.min(a.tokens.size, b.tokens.size) || 1);
  if ((a.names.has(b.session) || b.names.has(a.session)) && words.length >= NAMED.words && share >= NAMED.share) return { rule: "named", words, share };
  if (words.length >= SAME.words && share >= SAME.share) return { rule: "same", words, share };
  return null;
}

/** A sentence that says why two items were taken for one. */
export function whySame(a, b, m) {
  const label = (SUBJECTS.find((s) => s.key === m.subject) ?? {}).label;
  if (m.rule === "subject") return `sessions ${a.session} and ${b.session} both ask about ${label}`;
  const who = a.names.has(b.session) ? `session ${a.session} names session ${b.session}` : b.names.has(a.session) ? `session ${b.session} names session ${a.session}` : `sessions ${a.session} and ${b.session}`;
  return `${who}, and they share ${m.words.length} words (${m.words.slice(0, 8).join(", ")}${m.words.length > 8 ? ", ..." : ""})`;
}

/** A note's order among notes: its date, then the part of the day its name says (night, morning, day, pm, evening). */
export function noteOrder(file) {
  const m = /(\d{4}-\d{2}-\d{2})/.exec(file);
  if (!m) return null;
  const after = file.slice(m.index + 10).toLowerCase();
  const before = file.slice(0, m.index).toLowerCase();
  const find = (s) => { for (const [w, p] of DAY_PART) if (new RegExp(`(^|[_.\\s-])${w}([_.\\s-]|$)`).test(s)) return p; return null; };
  const part = find(after) ?? find(before) ?? 1;
  return { date: m[1], part, order: `${m[1]}#${part}` };
}

/** A state note's lists of what waits: [{ heading, line, by_value, items: [{ line, rank, md }] }]. */
export function parseNote(raw) {
  const lines = String(raw).replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let cur = null;
  let fence = false;
  const close = () => {
    if (!cur) return;
    const its = items(cur.lines);
    const lead = its.find((x) => !/^\s*([-*+]|\d+[.)])\s/.test(x.md));
    cur.by_value = BY_VALUE.test(cur.heading) || (!!lead && its.indexOf(lead) === 0 && BY_VALUE.test(lead.md));
    let pos = 0;
    cur.items = its.filter((x) => /^\s*([-*+]|\d+[.)])\s/.test(x.md)).map((x) => {
      pos += 1;
      const num = /^\s*(\d+)[.)]\s/.exec(x.md);
      return { line: x.line, rank: num ? Number(num[1]) : pos, md: x.md };
    });
    delete cur.lines;
    delete cur.level;
    if (cur.items.length) out.push(cur);
    cur = null;
  };
  lines.forEach((text, i) => {
    if (/^\s*(```|~~~)/.test(text)) fence = !fence;
    const m = fence ? null : /^(#{1,4}) +(.*\S)\s*$/.exec(text);
    if (m) {
      if (cur && m[1].length > cur.level) { cur.lines.push({ n: i + 1, text }); return; }
      close();
      if (m[1].length >= 2 && NOTE_HEAD.test(m[2])) cur = { heading: m[2], line: i + 1, level: m[1].length, lines: [] };
      return;
    }
    if (cur) cur.lines.push({ n: i + 1, text });
  });
  close();
  return out;
}

/** Every dated note of docs/state/ with a list of what waits, newest first. */
export function readNotes(repo) {
  const dir = path.join(repo, ...NOTES.split("/"));
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const f of fs.readdirSync(dir).sort()) {
    if (!f.endsWith(".md")) continue;
    const o = noteOrder(f);
    if (!o) continue;
    const lists = parseNote(fs.readFileSync(path.join(dir, f), "utf-8"));
    if (lists.length) out.push({ file: f, path: `${NOTES}/${f}`, url: `${REPO_URL}/blob/main/${NOTES}/${f}`, ...o, lists });
  }
  return out.sort((a, b) => (a.order < b.order ? 1 : a.order > b.order ? -1 : a.file < b.file ? 1 : -1));
}

/** "384, 386 to 413" from a sorted list of numbers. */
export function spans(nums) {
  const out = [];
  for (let i = 0; i < nums.length; i += 1) {
    let j = i;
    while (j + 1 < nums.length && nums[j + 1] === nums[j] + 1) j += 1;
    out.push(j === i ? `${nums[i]}` : j === i + 1 ? `${nums[i]}, ${nums[j]}` : `${nums[i]} to ${nums[j]}`);
    i = j;
  }
  return out.join(", ");
}

// a note's item speaks of an item of the ledger when they match one subject, or the note names its session and they share
// NOTE_MATCH.named words, or they share NOTE_MATCH.words words, NOTE_MATCH.share of the shorter's. A note's item that
// speaks of several is ranked for each; the one it shares most with is the one it puts first.
export const NOTE_MATCH = { named: 3, words: 4, share: 0.4 };

/** How well a note's item matches a group: 0 when it does not. */
function noteScore(t, g) {
  let best = 0;
  for (const m of g.all) {
    const words = [...t.tokens].filter((w) => m.tokens.has(w)).length;
    const share = words / (Math.min(t.tokens.size, m.tokens.size) || 1);
    let s = 0;
    if (t.subject && t.subject === m.subject) s = 100 + words;
    else if (t.names.has(m.session) && words >= NOTE_MATCH.named) s = 50 + words;
    else if (words >= NOTE_MATCH.words && share >= NOTE_MATCH.share) s = words;
    if (s > best) best = s;
  }
  return best;
}

/** The ledger, from the parsed reports (parseReport) and the notes (readNotes). */
export function ledger(reports, notes, marker = { error: "not given", order: null }, run = LEDGER) {
  run = resolveRun(reports, run);
  const inRange = reports.filter((r) => r.n >= run.from && r.n <= run.to).sort((a, b) => a.order - b.order);
  const answered = marker && marker.error === null && marker.order !== null ? marker.order : null;
  const heldNums = [...new Set(inRange.map((r) => r.n))];
  const missing = [];
  for (let k = run.from; k <= run.to; k += 1) if (!heldNums.includes(k) && !(answered !== null && k * 100 <= answered)) missing.push(k);
  const quiet = [];
  const asks = [];
  for (const r of inRange) {
    const own_ = r.waits.filter((w) => w.kind === "section");
    const pointers = own_.filter((w) => POINTER.test(plainOf(w.md).replace(/[*_`]/g, "")));
    const told = [...(r.nothing ?? []).map((x) => ({ ...x, why: "says there is nothing new" })), ...pointers.map((x) => ({ section: x.section, line: x.line, md: x.md, why: "sends the reader to another list" }))];
    if (told.length) quiet.push({ session: r.id, url: r.url, lines: told.map((x) => ({ line: x.line, md: x.md, why: x.why })) });
    for (const w of own_) {
      if (pointers.includes(w)) continue;
      const plain = plainOf(w.md);
      asks.push({ session: r.id, n: r.n, order: r.order, url: r.url, path: r.path, title: r.title, date_words: r.date_words, section: w.section, line: w.line, md: w.md,
        tokens: tokens(plain), names: sessionsNamed(w.md), subject: subjectOf(plain.replace(/[*`]/g, "")) });
    }
  }
  // which items ask the same thing
  const parent = asks.map((_, i) => i);
  const root = (i) => (parent[i] === i ? i : (parent[i] = root(parent[i])));
  const join = (i, j) => { parent[root(i)] = root(j); };
  const pairs = [];
  for (let i = 0; i < asks.length; i += 1) for (let j = i + 1; j < asks.length; j += 1) {
    const m = sameAsk(asks[i], asks[j]);
    if (m) pairs.push({ i, j, m });
  }
  const partners = (i, session) => pairs.filter((p) => p.m.rule !== "subject" && ((p.i === i && asks[p.j].session === session) || (p.j === i && asks[p.i].session === session))).length;
  const why = new Map();
  const restates = [];
  for (const p of pairs) {
    const a = asks[p.i], b = asks[p.j];
    const one = p.m.rule === "subject" || (partners(p.i, b.session) === 1 && partners(p.j, a.session) === 1);
    if (one) { join(p.i, p.j); why.set(`${p.i}|${p.j}`, whySame(a, b, p.m)); continue; }
    if (partners(p.i, b.session) > 1) restates.push({ by: p.i, of: p.j, why: whySame(a, b, p.m) });
    if (partners(p.j, a.session) > 1) restates.push({ by: p.j, of: p.i, why: whySame(a, b, p.m) });
  }
  const joined = new Set(pairs.filter((p) => root(p.i) === root(p.j)).flatMap((p) => [p.i, p.j]));
  const onlyRestates = new Set(restates.map((x) => x.by).filter((i) => !joined.has(i)));
  const byRoot = new Map();
  asks.forEach((a, i) => {
    if (onlyRestates.has(i)) return;
    const k = root(i);
    if (!byRoot.has(k)) byRoot.set(k, []);
    byRoot.get(k).push(i);
  });
  const link = (a) => ({ session: a.session, line: a.line, path: a.path, url: `${a.url}?plain=1#L${a.line}`, report_url: a.url, section: a.section, md: plainMd(a.md) });
  let groups = [...byRoot.values()].map((idx) => {
    idx.sort((x, y) => asks[x].order - asks[y].order || asks[x].line - asks[y].line);
    const members = idx.map((i) => asks[i]);
    const latest = members[members.length - 1];
    const also = restates.filter((x) => idx.includes(x.of) && onlyRestates.has(x.by)).map((x) => x.by);
    const alsoUniq = [...new Set(also)].map((i) => asks[i]);
    const reasons = [];
    for (const [k, v] of why) { const [i, j] = k.split("|").map(Number); if (idx.includes(i) && idx.includes(j)) reasons.push(v); }
    for (const x of restates) if (idx.includes(x.of) && onlyRestates.has(x.by)) reasons.push(`${x.why}; session ${asks[x.by].session}'s item asks more than this one, so it is kept beside each item it restates`);
    const place = blockOf(members.map((m) => plainOf(m.md)).join(" \n "));
    return { members, latest, also: alsoUniq, all: [...members, ...alsoUniq], reasons, place };
  });
  // the notes: only those written since the first report of the run
  const since = inRange.map((r) => r.date).filter(Boolean).sort()[0] ?? null;
  const read = notes.filter((n) => since === null || n.date >= since);
  const ranks = groups.map(() => []);
  const firsts = [];
  for (const note of read) {
    for (const list of note.lists) {
      for (const it of list.items) {
        const t = { tokens: tokens(plainOf(it.md)), names: sessionsNamed(it.md), subject: subjectOf(plainOf(it.md).replace(/[*`]/g, "")) };
        let best = -1, bestScore = 0;
        groups.forEach((g, gi) => {
          const s = noteScore(t, g);
          if (s > 0) ranks[gi].push({ note: note.file, path: note.path, url: `${note.url}?plain=1#L${it.line}`, heading: list.heading, rank: it.rank, by_value: list.by_value, best: false, score: s });
          if (s > bestScore) { bestScore = s; best = gi; }
        });
        if (best >= 0) {
          const r = ranks[best].find((x) => x.note === note.file && x.rank === it.rank && x.heading === list.heading);
          if (r) r.best = true;
          if (list.by_value) firsts.push({ gi: best, note: note.file, path: note.path, url: `${note.url}?plain=1#L${it.line}`, heading: list.heading, rank: it.rank, date: note.date });
        }
      }
    }
  }
  // the three first: the notes that rank by value, newest first, each in its own order; one group once
  const top = [];
  for (const f of firsts) {
    if (top.length >= 3) break;
    if (!top.some((x) => x.gi === f.gi)) top.push(f);
  }
  const blockIndex = (k) => BLOCKS.findIndex((b) => b.key === k);
  const out = groups.map((g, gi) => ({
    id: `w${String(gi + 1).padStart(3, "0")}`,
    block: g.place.block, block_rule: g.place.rule, block_said: g.place.said,
    md: plainMd(g.latest.md), session: g.latest.session, path: g.latest.path, section: g.latest.section,
    sessions: [...new Set(g.all.map((m) => m.session))],
    asked: g.members.map(link), restated: g.also.map(link), reasons: g.reasons,
    ranks: ranks[gi].map(({ score, ...r }) => r),
    first: (() => { const k = top.findIndex((x) => x.gi === gi); return k < 0 ? null : { place: k + 1, note: top[k].note, path: top[k].path, url: top[k].url, heading: top[k].heading, rank: top[k].rank }; })(),
    order: g.latest.order, line: g.latest.line,
  }));
  out.sort((a, b) => blockIndex(a.block) - blockIndex(b.block) || b.order - a.order || a.line - b.line);
  const byBlock = Object.fromEntries(BLOCKS.map((b) => [b.key, out.filter((g) => g.block === b.key).length]));
  const lines = asks.length;
  return {
    from: run.from, to: run.to, error: null,
    held: inRange.map((r) => r.id), held_words: spans(heldNums), missing: spans(missing), answered_to: answered !== null && marker.last ? marker.last : null,
    notes_read: read.map((n) => ({ file: n.file, path: n.path, url: n.url, date: n.date, lists: n.lists.map((l) => ({ heading: l.heading, line: l.line, by_value: l.by_value, items: l.items.length })) })),
    ranked_by_value: read.some((n) => n.lists.some((l) => l.by_value)),
    counts: { reports: inRange.length, with_items: new Set(asks.map((a) => a.session)).size, lines, items: out.length, merged: lines - out.length, by_block: byBlock, first: top.length, unranked: out.filter((g) => g.ranks.length === 0).length },
    blocks: BLOCKS, rules: { block: BLOCK_RULES.map((r, i) => ({ n: i + 1, block: r.block, re: String(r.re) })), subjects: SUBJECTS.map((s) => ({ label: s.label, re: String(s.re) })), named: NAMED, same: SAME, note: NOTE_MATCH, by_value: String(BY_VALUE), pointer: String(POINTER) },
    groups: out.map(({ order, ...g }) => g), quiet,
    // a report of the run with no section for the owner at all
    silent: inRange.filter((r) => !asks.some((a) => a.session === r.id) && !quiet.some((q) => q.session === r.id)).map((r) => ({ session: r.id, url: r.url })),
  };
}

/** Everything the page shows, from a repository folder. */
export function build(repo, now = new Date()) {
  const dir = path.join(repo, ...REPORTS.split("/"));
  const base = { built_at: now.toISOString(), repo: REPO_URL, marker: parseMarker(null), unread: null, reports: [], decided_only: [], counts: { after: 0, listed: 0, items: 0 } };
  if (!fs.existsSync(dir)) return { ...base, unread: `${REPORTS} was not in the repository this build read` };
  const markerFile = path.join(repo, ...MARKER.split("/"));
  const marker = parseMarker(fs.existsSync(markerFile) ? fs.readFileSync(markerFile, "utf-8") : null);
  const all = [];
  for (const f of fs.readdirSync(dir).sort()) {
    const id = reportId(f);
    // a marker that cannot be read hides nothing: every report is read
    if (!id || (marker.error === null && id.order <= marker.order)) continue;
    all.push(parseReport(f, fs.readFileSync(path.join(dir, f), "utf-8")));
  }
  all.sort((a, b) => b.order - a.order);
  const reports = all.filter((r) => r.waits.length > 0);
  const decidedOnly = all.filter((r) => r.waits.length === 0 && r.decided.length > 0).map((r) => ({ id: r.id, title: r.title, url: r.url, date_words: r.date_words, count: r.decided.length }));
  // session 414: the ledger of LEDGER.from to LEDGER.to (session 425: to the newest report read); a fault in it is said on the page and never fails the build
  let led;
  try {
    led = ledger(all, readNotes(repo), marker);
  } catch (e) {
    led = { ...resolveRun(all), error: `the ledger could not be made: ${String(e && e.message ? e.message : e).slice(0, 200)}` };
  }
  return { ...base, marker, reports, decided_only: decidedOnly, counts: { after: all.length, listed: reports.length, items: reports.reduce((a, r) => a + r.waits.length, 0) }, ledger: led };
}

// run as a script: write site/content/waits.json
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const out = path.join(here, "..", "content", "waits.json");
  let made;
  try {
    made = build(path.resolve(here, "..", ".."));
  } catch (e) {
    made = { built_at: new Date().toISOString(), repo: REPO_URL, marker: parseMarker(null), unread: `the reports could not be read: ${String(e && e.message ? e.message : e).slice(0, 200)}`, reports: [], decided_only: [], counts: { after: 0, listed: 0, items: 0 } };
  }
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(made));
  console.log(made.unread ? `build-waits: ${made.unread}` : `build-waits: ${made.counts.listed} of ${made.counts.after} reports after session ${made.marker.last ?? "(marker unread)"} hold ${made.counts.items} waiting items`);
}
