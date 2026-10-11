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
    url: `${REPO_URL}/blob/main/${REPORTS}/${file}`, waits, decided,
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
  return { ...base, marker, reports, decided_only: decidedOnly, counts: { after: all.length, listed: reports.length, items: reports.reduce((a, r) => a + r.waits.length, 0) } };
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
