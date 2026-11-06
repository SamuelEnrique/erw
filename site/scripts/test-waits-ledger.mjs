// Energy Research Warehouse (ERW) site, session 414: the ledger of /internal/waits (scripts/build-waits.mjs, "the
// ledger"), on written cases and on the repository's own reports and notes. No request, no package, no model.
//
//   node site/scripts/test-waits-ledger.mjs
//
// Exit 0 when every case holds, 1 otherwise. It prints one line a case that fails and one closing line.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  BLOCKS, BLOCK_RULES, LEDGER, blockOf, build, ledger, noteOrder, parseNote, parseReport, readNotes, reportId, resolveRun, sameAsk, sessionsNamed, spans, subjectOf, tokens,
} from "./build-waits.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");
let ran = 0;
const failed = [];
function ok(cond, what) { ran += 1; if (!cond) failed.push(what); }
function eq(a, b, what) { ok(JSON.stringify(a) === JSON.stringify(b), `${what}: ${JSON.stringify(a)} is not ${JSON.stringify(b)}`); }

// --- the words an item is compared by
const tk = tokens("The **four letters**: send, change or hold `warehouse/archive/restore.py` (session 359's tables)");
ok(tk.has("letter") && tk.has("send") && tk.has("change") && tk.has("hold"), "the words, a plural's s taken off");
ok(!tk.has("the") && !tk.has("four") && !tk.has("359") && !tk.has("session"), "no common word, number word, short number or the word session");
ok(tk.has("warehouse/archive/restore.py") && tk.has("restore") && !tk.has("warehouse"), "a path whole and by its parts, a common folder not");
ok(tk.has("table") && !tokens("status analysis").has("statu"), "tables is table; status and analysis keep their s");

// --- the sessions an item names
eq([...sessionsNamed("(session 359's question, unchanged)")], ["359"], "a session named");
eq([...sessionsNamed("sessions 359 and 379")].sort(), ["359", "379"], "two sessions named");
eq([...sessionsNamed("sessions 351 to 354")], ["351", "352", "353", "354"], "a run of sessions");
eq([...sessionsNamed("3. **368**: the empty columns")], ["368"], "a session in bold, as the notes write it");
eq([...sessionsNamed("452 rows fewer, 2026")], [], "a number that is not a session");

// --- the subject, and what an item blocks
ok(["**Redivis's free 10 GB is full**", "Redivis storage, 10 GB free, full", "Redivis's storage (the first item)", "The storage: the four choices"].every((t) => subjectOf(t) === "redivis-storage"), "four ways of naming the Redivis storage");
eq(subjectOf("The uploader's replace: upload the new copy under a temporary name"), null, "the uploader is not the storage");
eq(blockOf("a paid tier, or tables out of the draft").block, "money", "a paid tier is money");
eq(blockOf("whether the project's plan or the day's loads need a change").block, "money", "the database's plan is money");
eq(blockOf("For the data machine: the four intervals, if the page should show them").block, "pull", "for the data machine comes before page");
eq(blockOf("On a phone the first figure is two and a half screens down on the pages").block, "page", "on a phone comes before figure");
eq(blockOf("Whether the node should apply to the headline as well").block, "figure", "the headline is a figure");
eq(blockOf("A link from `/research` to its replication").block, "page", "an address of the site is a page");
eq(blockOf("Restore this machine from the archive").block, "pull", "a restore is a data pull");
eq(blockOf("The CLAUDE.md patch: the orchestrator applies it").block, "other", "none of the four");
eq(blockOf("a paid tier").said, "paid tier", "the words that placed it are kept");
ok(blockOf("a paid tier").rule === 1 && BLOCK_RULES[BLOCK_RULES.length - 1].block === "other", "the rule's number is kept; the last rule takes what is left");
ok(BLOCK_RULES.every((r) => BLOCKS.some((b) => b.key === r.block)), "every rule places in a block the page names");

// --- two items, one ask
const a = { session: "360", tokens: tokens("Whether to ask ERCOT for 2021's workbook (an information request), or leave the year out."), names: new Set(), subject: null };
const b = { session: "362", tokens: tokens("2021's four intervals: an information request to ERCOT, or leave the year out (session 360's question, unchanged)."), names: sessionsNamed("(session 360's question)"), subject: null };
eq(sameAsk(a, b)?.rule, "named", "a later report that names the first and shares its words");
eq(sameAsk(a, { ...b, session: "360" }), null, "one report's two items are never one");
eq(sameAsk(a, { session: "363", tokens: tokens("The loader's guard compares retrieved_at only."), names: new Set(["360"]), subject: null }), null, "naming a session is not enough without shared words");

// --- the notes' order and their lists
ok(noteOrder("review_2026-10-21_night_code.md").order < noteOrder("morning_2026-10-21.md").order, "a night note is older than the morning's of the same day");
ok(noteOrder("morning_2026-10-21.md").order < noteOrder("morning_2026-10-21_day.md").order, "the morning's note is older than the day's");
eq(noteOrder("notes.md"), null, "a note without a date is not read");
const n1 = parseNote("# A note\n\n## Waiting for you, highest value first\n\n1. **One** thing.\n2. **Two** things.\n\n## The queue\n\n1. not a wait\n");
ok(n1.length === 1 && n1[0].by_value && n1[0].items.length === 2 && n1[0].items[1].rank === 2, "a list ranked by value in its heading, and the list stops at the next heading");
const n2 = parseNote("## Waiting for you\n\nIn the order of their value:\n\n1. One.\n2. Two.\n");
ok(n2[0].by_value, "a list ranked by value in its first line");
const n3 = parseNote("## Waiting for you\n\n1. One.\n2. Two.\n");
ok(!n3[0].by_value && n3[0].items.length === 2, "a numbered list that does not say it is by value");
eq(spans([384, 386, 387, 388, 390, 391]), "384, 386 to 388, 390, 391", "the sessions not read, in words");

// --- a written run: three reports, two notes
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "erw-ledger-"));
try {
  fs.mkdirSync(path.join(tmp, "docs", "state"), { recursive: true });
  const rep = (n, body) => parseReport(`SESSION_${n}_REPORT.md`, `# Session ${n} report: a case\n\n20 October 2026, a written case.\n\n## For Samuel's ruling\n\n${body}\n\n## Files\n\n- none\n`);
  const r900 = rep(900, [
    "- **Redivis's free 10 GB is full**: upgrade the account, or take tables out of the draft.",
    "- Whether to ask ERCOT for 2021's workbook (an information request), or leave the year out.",
    "- Whether a card should state the Newey-West error in its sentence where it moves the verdict's p across 0.05.",
    "- Whether the step flag should keep a draft from the review list, or stay a flag.",
  ].join("\n"));
  const r901 = rep(901, "- Nothing new.");
  const r902 = rep(902, [
    "- Redivis storage, 10 GB free, full: a paid tier, or tables out of the draft.",
    "- 2021's four intervals: an information request to ERCOT, or leave the year out (session 900's question, unchanged).",
    "- Session 900's two questions, now on the page: whether a card should state the Newey-West error in its sentence, and whether the step flag should keep a draft from the review list.",
    "- The items of the note's \"Waiting for you\".",
  ].join("\n"));
  const r903 = parseReport("SESSION_903_REPORT.md", "# Session 903 report: no section\n\n20 October 2026.\n\n## Files\n\n- none\n");
  fs.writeFileSync(path.join(tmp, "docs", "state", "morning_2026-10-21.md"), "# Morning\n\n## Waiting for you, highest value first\n\n1. **The step flag** (session 900): whether it keeps a draft from the review list.\n2. **Something no report asks**, a pull of the moon.\n3. **Redivis storage (10 GB, full)**: a paid tier.\n");
  fs.writeFileSync(path.join(tmp, "docs", "state", "review_2026-10-21_night_code.md"), "# Night\n\n## Waiting for you\n\n1. **2021's four intervals**: the information request to ERCOT (sessions 900 and 902).\n");
  fs.writeFileSync(path.join(tmp, "docs", "state", "review_2026-10-11_code.md"), "# Older than the run\n\n## Waiting for you, highest value first\n\n1. **Newey-West** in a card's sentence (session 900).\n");
  const notes = readNotes(tmp);
  eq(notes.map((n) => n.file), ["morning_2026-10-21.md", "review_2026-10-21_night_code.md", "review_2026-10-11_code.md"], "the notes, newest first");
  const L = ledger([r903, r902, r901, r900], notes, { error: null, order: 89900, last: "899" }, { from: 900, to: 905 });
  eq(L.held, ["900", "901", "902", "903"], "the reports of the run, in order");
  eq(L.missing, "904, 905", "the sessions of the run with no report yet");
  eq([L.counts.lines, L.counts.items, L.counts.merged], [7, 4, 3], "seven lines are four items (the pointer is not a line)");
  const by = (re) => L.groups.find((g) => re.test(g.md));
  const store = by(/paid tier/), year = by(/2021/), nw = by(/Newey-West/), flag = by(/step flag/);
  ok(store && year && nw && flag, "each of the four asks is one item");
  eq(store.sessions, ["900", "902"], "the storage, asked twice, keeps both sessions");
  ok(store.asked.every((x) => /\?plain=1#L\d+$/.test(x.url)), "each asking links to its line");
  ok(/both ask about the Redivis storage/.test(store.reasons[0]), "the reason of a merge by subject is said");
  eq(year.sessions, ["900", "902"], "a later report that names the first is merged with it");
  ok(/session 902 names session 900, and they share/.test(year.reasons[0]), "the reason of a merge by name is said, with the words");
  ok(nw.asked.length === 1 && nw.restated.length === 1 && flag.restated.length === 1 && nw.restated[0].session === "902", "an item that restates two stays beside each, and they stay two");
  eq([store.block, year.block, nw.block, flag.block], ["money", "pull", "figure", "other"], "what each blocks");
  eq(L.groups.filter((g) => g.first).sort((x, y) => x.first.place - y.first.place).map((g) => [g.first.place, g.first.rank, /step flag/.test(g.md)]), [[1, 1, true], [2, 3, false]], "the first: the note's order by value, an item no report asks skipped");
  ok(store.first.note === "morning_2026-10-21.md" && store.first.place === 2, "the storage is second, from the note that ranks by value");
  ok(year.first === null && year.ranks.length === 1 && year.ranks[0].by_value === false, "a numbered list not said to be by value is shown beside the item and puts nothing first");
  ok(!L.notes_read.some((n) => n.file === "review_2026-10-11_code.md"), "a note older than the run is not read");
  eq(L.quiet.map((q) => [q.session, q.lines.map((x) => x.why)]), [["901", ["says there is nothing new"]], ["902", ["sends the reader to another list"]]], "what is not listed, and why");
  eq(L.silent.map((s) => s.session), ["903"], "a report with no section for the owner is named");
  eq(Object.values(L.counts.by_block).reduce((x, y) => x + y, 0), L.counts.items, "the blocks' counts add up to the items");
  const none = ledger([r900], [], { error: null, order: 89900, last: "899" }, { from: 900, to: 900 });
  ok(none.counts.first === 0 && none.groups.every((g) => g.first === null && g.ranks.length === 0), "with no note, nothing is put first and nothing is ranked");
  const answered = ledger([r902], [], { error: null, order: 90100, last: "901" }, { from: 900, to: 902 });
  ok(answered.missing === "" && answered.answered_to === "901", "reports marked answered are not counted as missing");
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}

// --- session 425: the end of the run
eq(LEDGER, { from: 351, to: "newest" }, "the run is 351 to the newest report present");
eq(resolveRun([{ n: 360 }, { n: 475 }, { n: 300 }, { n: 9999 / 0 }]), { from: 351, to: 475 }, "newest is the highest session read, from 351");
eq(resolveRun([{ n: 300 }]), { from: 351, to: 351 }, "no report of the run: the run is its first session alone");
eq(resolveRun([{ n: 475 }], { from: 900, to: 902 }), { from: 900, to: 902 }, "a run with a number for its end is kept");
{
  const late = parseReport("SESSION_475_REPORT.md", ["# Session 475 report: a late one", "", "21 October 2026.", "", "## For Samuel's ruling", "", "- Whether the late report joins the ledger.", ""].join(String.fromCharCode(10)));
  const led = ledger([late], [], { error: null, order: null, last: null });
  ok(led.to === 475 && led.held.includes("475") && led.groups.length === 1, "a report numbered past 413 joins the ledger with its item");
}

// --- the repository's own reports and notes
const w = build(repo);
const L = w.ledger;
ok(L && L.error === null, `the repository's ledger is made (${L && L.error})`);
if (L && L.error === null) {
  // session 425: the run ends at the newest report of the folder the build read (those the marker has not answered)
  const files = fs.readdirSync(path.join(repo, "archive", "sessions")).map(reportId).filter(Boolean)
    .filter((id) => !(w.marker.error === null && id.order <= w.marker.order) && id.n >= LEDGER.from);
  const newest = files.length ? Math.max(...files.map((id) => id.n)) : LEDGER.from;
  eq([L.from, L.to], [LEDGER.from, newest], "the run the page names is LEDGER's, to the newest report present");
  ok(L.to > 413, "the run reaches past session 413 once newer reports are present");
  ok(L.held.length > 0 && L.held.every((id) => Number.parseInt(id, 10) >= L.from && Number.parseInt(id, 10) <= L.to), "every report read is of the run");
  const counted = new Set();
  for (const g of L.groups) {
    for (const x of g.asked) counted.add(`${x.session}:${x.line}`);
    ok(BLOCKS.some((b) => b.key === g.block), `${g.id}: a block the page names`);
    ok(g.asked.length >= 1 && g.sessions.length >= 1, `${g.id}: asked somewhere`);
    for (const x of [...g.asked, ...g.restated]) {
      const lines = fs.readFileSync(path.join(repo, ...x.path.split("/")), "utf-8").replace(/\r\n/g, "\n").split("\n");
      const at = (lines[x.line - 1] ?? "").replace(/^\s*([-*+]|\d+[.)])\s+/, "");
      ok(at.length > 0 && x.md.startsWith(at.slice(0, 40)), `${g.id}: session ${x.session}'s line ${x.line} holds its words`);
    }
  }
  const restatedOnly = new Set(L.groups.flatMap((g) => g.restated.map((x) => `${x.session}:${x.line}`)).filter((k) => !counted.has(k)));
  eq(counted.size + restatedOnly.size, L.counts.lines, "every line of the run is in one item, or beside the items it restates");
  eq(Object.values(L.counts.by_block).reduce((x, y) => x + y, 0), L.counts.items, "the repository's blocks add up to its items");
  ok(L.groups.filter((g) => g.first).length <= 3, "at most three first");
  ok(L.groups.filter((g) => g.first).every((g) => g.ranks.some((r) => r.by_value && r.note === g.first.note && r.rank === g.first.rank)), "each of the first is ranked by value in the note it names");
}
const src = fs.readFileSync(path.join(here, "build-waits.mjs"), "utf-8");
ok(!src.includes(String.fromCharCode(0x2014)), "no em dash in the reader");

for (const f of failed) console.log(`FAIL ${f}`);
console.log(`test-waits-ledger: ${ran - failed.length} of ${ran} held`);
process.exitCode = failed.length ? 1 : 0;
