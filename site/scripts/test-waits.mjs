// Energy Research Warehouse (ERW) site, session 188: the reader of what waits for the owner (scripts/build-waits.mjs),
// on written cases and on the repository's own reports. No request, no package: node's standard library only.
//
//   node site/scripts/test-waits.mjs
//
// Exit 0 when every case holds, 1 otherwise. It prints one line a case that fails and one closing line.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build, headKind, items, own, parseMarker, parseReport, reportDate, reportId, INLINE } from "./build-waits.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");
let ran = 0;
const failed = [];
function ok(cond, what) { ran += 1; if (!cond) failed.push(what); }
function eq(a, b, what) { ok(JSON.stringify(a) === JSON.stringify(b), `${what}: ${JSON.stringify(a)} is not ${JSON.stringify(b)}`); }
const says = (t) => INLINE.some((re) => re.test(t));

// --- names and the order of reports
eq(reportId("SESSION_186_REPORT.md"), { id: "186", n: 186, suffix: "", order: 18600 }, "a report's number");
eq(reportId("SESSION_180B_REPORT.md"), { id: "180b", n: 180, suffix: "b", order: 18002 }, "a lettered report");
eq(reportId("SESSION_186_PROMPT.md"), null, "a prompt file is not a report");
eq(reportId("LAST_ANSWERED"), null, "the marker is not a report");
ok(reportId("SESSION_180_REPORT.md").order < reportId("SESSION_180B_REPORT.md").order && reportId("SESSION_180B_REPORT.md").order < reportId("SESSION_181_REPORT.md").order, "180, 180b, 181 in order");

// --- the marker file
eq(parseMarker("# a note\nlast_answered: 171\non: 2026-10-09\n").last, "171", "the marker's number");
eq(parseMarker("last_answered: 171\r\non: 2026-10-09\r\n").on, "2026-10-09", "the marker with Windows line ends");
eq(parseMarker("last_answered: 180b\n").order, 18002, "a lettered number in the marker");
eq(parseMarker("last_answered: 180B\n").last, "180b", "the letter in either case");
ok(parseMarker(null).error !== null, "an absent marker is an error");
ok(parseMarker("# only notes\n").error !== null, "a marker with no number is an error");
ok(parseMarker("last_answered: soon\n").error !== null, "a marker whose number is a word is an error");
ok(parseMarker("last_answered: 171\non: 9 October\n").error !== null, "a marker whose day is not a date is an error");
ok(parseMarker("last_answered: 171\nanswered_by: x\n").error !== null, "a name the file does not hold is an error");
ok(parseMarker("171\n").error !== null, "a bare number is an error");

// --- headings
for (const h of ["For Samuel's ruling", "For Samuel", "For Samuel: one list", "To finish (Samuel)", "What could not be cited (for Samuel)", "Open questions",
  "Open questions for the human", "7. Open questions for Samuel, and what was skipped", "Proposed cuts, for your ruling (each with its saving)",
  "Held for your approval", "Questions for Samuel", "What Samuel must do", "Left from the landing, yours", "For you to decide", "Needs your ruling"]) {
  eq(headKind(h), "wait", `the heading "${h}"`);
}
for (const h of ["To finish", "For the coordinator", "Your rulings, applied", "Rulings applied", "Thesis Builder: the four rulings as built", "Read these first",
  "Verdict: ready to open, once two things are ruled", "The landing", "Checks run", "Found, not changed"]) {
  eq(headKind(h), "none", `the heading "${h}"`);
}
for (const h of ["Decisions made without you", "Decisions made without a human", "Decisions made alone", "Decisions I made without you", "Decisions made without you (part 4)", "9. Decisions made without a human"]) {
  eq(headKind(h), "decided", `the heading "${h}"`);
}
eq(headKind("The prompt"), "prompt", "the owner's own words");
for (const h of ["What to review", "What to review (internal view)", "What to click on /analysis (internal view first)", "What to click"]) {
  eq(headKind(h), "steps", `the heading "${h}"`);
}

// --- an item that says itself that it waits
for (const t of ["They need your ruling (below).", "Open. Your ruling", "Open, your word. Recommend keeping both", "A NYISO pull: your approval, after your ruling on NYISO's terms",
  "Held for the owner's ruling: a new pull", "Rule on items 3, 16 and 19.", "Rules to make, Samuel: whether", "Samuel: fill the two bracketed items", "Run the do-file in Stata once (Samuel).",
  "with the publisher and ceiling you rule", "To be confirmed by Samuel.", "it waits for Samuel's own word", "The note for your sign-off: the file", "For you to decide: A or B"]) {
  ok(says(t), `an item that waits: "${t}"`);
}
for (const t of ["Closed: you ruled, 7 October", "Done per your ruling of 7 October.", "As your ruling says, the page is in review.", "Under your ruling the table stays internal.",
  "queued: it waits for the data machine", "The coordinator lands it.", "Nothing is held.", "The ruling of the commission is quoted."]) {
  ok(!says(t), `an item that does not wait: "${t}"`);
}
ok(!says(own('Heading "Waits for Samuel (internal)". Open /internal/waits.')), "the page's own name is not a wait");
ok(says(own("The file waits for Samuel's word (see /internal/waits).")), "an item that waits and names the page");

// --- a section's items
const lines = (text) => text.split("\n").map((t, i) => ({ n: i + 10, text: t }));
const got = items(lines(["1. First, on one line.", "2. Second,", "   carried over.", "", "   ```", "   a command", "   ```", "- A bullet", "  - a nested one", "", "A paragraph", "of two lines.", "",
  "| # | Cut | Saving |", "|---|---|---|", "| 1 | News on a cheaper model | USD 23 a month |", "| 2 | Fewer reads | USD 5 |"].join("\n")));
eq(got.map((g) => g.line), [10, 11, 17, 20, 25, 26], "where each item stands");
ok(got[1].md.includes("carried over.") && got[1].md.includes("a command"), "a fenced block belongs to the item before it");
ok(got[2].md.includes("a nested one"), "a nested item stays with its parent");
eq(got[3].md, "A paragraph\nof two lines.", "a paragraph is an item");
eq(got[4].md, "**#:** 1  \n**Cut:** News on a cheaper model  \n**Saving:** USD 23 a month", "a table row, said with the table's own column names");

// --- a whole report
const REPORT = `# Session 900 report: a tool, decisions

11 October 2026, 04:12 to about 05:05 UTC, unattended.

## Read these first

- Built: one section.
- Two defaults have no source. They need your ruling (below).

## What to review

1. Open the page. Heading "Waits for Samuel (internal)". The box says your ruling is recorded in a file.

## Decisions made without you

- The block stands after the contract.
- The usage count is held for your ruling.

## For Samuel's ruling

1. The hurdle rate's default.
2. The degradation rate's default,
   on both pages.

### A part of it

- A third thing.

## For the coordinator

1. Merge the branch.

## To finish

- Nothing is held.
- Rule on items 3 and 16.

## To finish (Samuel)

- Nothing.

## The prompt

"Report for Samuel's ruling and stop." Your approval is not needed.
`;
const r = parseReport("SESSION_900_REPORT.md", REPORT);
eq([r.id, r.title, r.date, r.date_words], ["900", "a tool, decisions", "2026-10-11", "11 October 2026"], "the report's number, title and date");
eq(r.waits.map((w) => [w.kind, w.line, w.section]), [["section", 21, "For Samuel's ruling"], ["section", 22, "For Samuel's ruling"], ["section", 27, "A part of it"],
  ["inline", 8, "Read these first"], ["inline", 17, "Decisions made without you"], ["inline", 36, "To finish"]], "what waits, its own section first");
eq(r.decided.map((d) => d.line), [16], "what was decided without the owner, less the item that waits");
ok(r.waits.every((w) => w.section !== "What to review"), "the click steps are not read, whatever words they quote from a page");
ok(r.waits.every((w) => !w.md.includes("Merge the branch") && !w.md.includes("Report for Samuel")), "the coordinator's list and the prompt are not read");
ok(r.url.endsWith("/blob/main/archive/sessions/SESSION_900_REPORT.md"), "the report's address on GitHub");
eq(parseReport("SESSION_901_REPORT.md", "# Session 901: nothing\n\nNo date here.\n\n## To finish\n\n- Nothing is held.\n").waits, [], "a report with nothing waiting");
eq(reportDate(["# Session 5", "", "Written on a day not named."]), null, "a date that is not written is not guessed");

// --- a folder of reports
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "erw-waits-"));
try {
  const d = path.join(tmp, "archive", "sessions");
  fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(d, "SESSION_899_REPORT.md"), REPORT.replace("900", "899"));
  fs.writeFileSync(path.join(d, "SESSION_900_REPORT.md"), REPORT);
  fs.writeFileSync(path.join(d, "SESSION_900B_REPORT.md"), "# Session 900b report: a second pull\n\n## Decisions made without you\n\n- One thing.\n");
  fs.writeFileSync(path.join(d, "SESSION_901_REPORT.md"), "# Session 901 report: nothing left\n\n## To finish\n\n- Nothing is held.\n");
  fs.writeFileSync(path.join(d, "SESSION_902_REPORT.md"), REPORT.replace("900", "902"));
  fs.writeFileSync(path.join(d, "SESSION_902_PROMPT.md"), "## For Samuel\n\n- not a report\n");
  fs.writeFileSync(path.join(d, "LAST_ANSWERED"), "# a note\nlast_answered: 899\non: 2026-10-10\n");
  let b = build(tmp, new Date("2026-10-11T07:00:00Z"));
  eq(b.reports.map((x) => x.id), ["902", "900"], "the reports after the last one answered that hold something, newest first");
  eq(b.decided_only.map((x) => [x.id, x.count]), [["900b", 1]], "a report that holds only decisions is named, not listed");
  eq(b.counts, { after: 4, listed: 2, items: 12 }, "the counts");
  eq([b.marker.last, b.marker.on, b.marker.error, b.unread, b.built_at], ["899", "2026-10-10", null, null, "2026-10-11T07:00:00.000Z"], "the marker as read");
  fs.writeFileSync(path.join(d, "LAST_ANSWERED"), "last_answered: 902\n");
  b = build(tmp);
  eq([b.reports.length, b.counts.after], [0, 0], "every report answered: nothing is listed");
  fs.writeFileSync(path.join(d, "LAST_ANSWERED"), "last_answered: tomorrow\n");
  b = build(tmp);
  ok(b.marker.error !== null && b.reports.length === 3, "a marker that cannot be read hides nothing");
  fs.rmSync(path.join(d, "LAST_ANSWERED"));
  ok(build(tmp).marker.error !== null, "no marker is said");
  ok(build(path.join(tmp, "nowhere")).unread !== null, "a build that does not see the reports says so and lists nothing");
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}

// --- the repository's own reports: every item is the report's own words, on the line named
const real = build(repo);
ok(real.unread === null && real.marker.error === null, `the repository's reports and marker are read (${real.unread ?? real.marker.error ?? "read"})`);
ok(real.reports.every((x, i) => i === 0 || real.reports[i - 1].order > x.order), "newest first");
ok(real.reports.every((x) => x.order > real.marker.order && x.waits.length > 0), "only reports after the marker, each with something waiting");
ok(fs.existsSync(path.join(repo, "archive", "sessions", `SESSION_${String(real.marker.last).toUpperCase()}_REPORT.md`)), "the marker names a report that exists");
let checked = 0;
for (const x of real.reports) {
  const text = fs.readFileSync(path.join(repo, x.path), "utf-8").replace(/\r\n/g, "\n").split("\n");
  for (const it of [...x.waits, ...x.decided]) {
    checked += 1;
    const first = it.md.split("\n")[0];
    const src = text[it.line - 1] ?? "";
    // a list item or a paragraph is the line itself; a table row is the row's cells under the table's column names
    const same = first.startsWith("**") && src.trim().startsWith("|")
      ? first.replace(/^\*\*[^*]*:\*\* /, "").replace(/ {2}$/, "") === src.trim().replace(/^\|/, "").split(/(?<!\\)\|/)[0].trim()
      : src === first;
    ok(same, `session ${x.id}, line ${it.line}: the item is not the report's line`);
    ok(!it.md.includes(String.fromCharCode(0x2014)), `session ${x.id}, line ${it.line}: an em dash`);
  }
}
ok(real.reports.length === 0 || checked > 0, "items were compared with the reports");

console.log(failed.length ? failed.map((f) => `FAILED: ${f}`).join("\n") : "");
console.log(`test-waits: ${ran - failed.length} of ${ran} held (${real.counts.listed} reports listed after session ${real.marker.last}, ${real.counts.items} items, ${checked} lines compared)`);
process.exitCode = failed.length ? 1 : 0;
