// Energy Research Warehouse (ERW) site, session 154: the pure functions of "Rules in motion" (/cost-of-power, the
// section "How soon"; lib/rules.ts). No request, no browser, no model.
//
//   node scripts/test-rules.mjs
//
// THE ROWS BELOW ARE MADE UP FOR THIS TEST: no regulator, docket, date, sentence or read in this file is real, and none
// of it is in any file the site ships (the page reads data/datacenter/rules.json and nothing else). They are shaped as
// the contract between the warehouse's builder and the page states (runs/session154/BRIEF_PAGE.md).
//
//   1. the grid an address names: PJM and MISO too; anything else is the grid the page opened;
//   2. the order: newest first, a row with no day last, the same whatever the file's order; nothing is changed in place;
//   3. the fold: eight shown, the rest behind it, no row lost and none twice;
//   4. the rows shown: one with no address of a source document is not shown, nor one whose words hold a municipal word
//      (on its face or on hover), nor a row listed twice; each is counted with why;
//   5. the block: MISO is the fixed words and no row, federal ones included, whatever the file holds; PJM shows rows and
//      the federal group; a grid with none says so with the file's reason; no file, or no entry, is "not held yet";
//   6. the status: the regulator's words where it words one, else the class, else "not stated";
//   7. the hover of the docket is the exact sentence with the page and the topic; the read is shown only when the file
//      marks it as a model's, with the model and what it was made from on hover; else "no read yet";
//   8. where data/datacenter/rules.json is on the machine: every grid of it gives a block, and what each shows is printed.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const R = await import("../lib/rules.ts");

let failed = 0, n = 0;
const ok = (cond, what) => { n += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed += 1; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// MADE UP: a row of the contract's shape, for the tests only
const row = (id, date, more = {}) => ({
  id, date, regulator: "Made-up Commission", jurisdiction: "state", state: "ZZ", docket: `MU-${id}`, title: `Made-up proceeding ${id}`, row_kind: "proceeding", topic: "large-load tariff",
  tags: ["large_load"], status_as_worded: "", status_class: "open", url: `https://example.invalid/doc/${id}.pdf`, page: "3", sentence: `Made-up sentence of document ${id}.`,
  read: null, read_by: null, read_model: null, read_from: null, why_here: "made-up mapping", ...more,
});
const MADE_UP = {
  built_at_utc: "2026-10-08T05:00:00Z", window_months: 12,
  sources: [{ regulator: "Made-up Commission", terms_url: "https://example.invalid/terms", terms_quote: "Made-up terms." }, { regulator: "Made-up Commission", terms_url: "", terms_quote: "" }],
  grids: {
    ercot: { state: "shown", rows: [row("e1", "2026-01-05"), row("e2", "2026-09-30", { read: "Made-up line.", read_by: "model", read_model: "made-up-model", read_from: "the sentence and the page around it" })] },
    pjm: { state: "shown", rows: Array.from({ length: 11 }, (_, i) => row(`p${i + 1}`, `2026-${String(i + 1).padStart(2, "0")}-15`)) },
    miso: { state: "shown", rows: [row("m1", "2026-05-01")] },   // the file is wrong on purpose: the page still shows no row
    caiso: { state: "none", why: "Made-up reason: nothing found." },
    spp: { state: "paused", words: "made-up pause", rows: [row("s1", "2026-02-02")] },
  },
  federal_all_grids: [row("f1", "2026-03-03", { jurisdiction: "federal", state: "", row_kind: "federal action" }), row("p3", "2026-03-15")],
  not_on_page: { count: 0, why: "" },
};
const F = R.fileOf(MADE_UP);

// 1. the grid an address names
ok(R.rulesGrid("pjm", "ercot") === "pjm" && R.rulesGrid("miso", "caiso") === "miso" && R.rulesGrid(" PJM ", "ercot") === "pjm", "an address that names PJM or MISO shows that grid's block, although the page opens neither");
ok(R.rulesGrid(undefined, "nyiso") === "nyiso" && R.rulesGrid("", "spp") === "spp" && R.rulesGrid("nowhere", "ercot") === "ercot" && R.rulesGrid("caiso", "caiso") === "caiso", "any other address shows the block of the grid the page opened");
ok(same([...R.RULE_GRIDS], ["ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"]) && R.SHOWN === 8, "seven grids, in the page's order; eight rows before the fold");

// 2. the order
{
  const rows = [row("a", "2025-12-01"), row("b", ""), row("c", "2026-10-01"), row("d", "2026-10-01", { regulator: "A made-up board" }), row("e", "not a day"), row("f", "2026-02-30")];
  const before = JSON.stringify(rows), got = R.sortRows(rows).map((r) => r.id);
  ok(same(got.slice(0, 4), ["d", "c", "f", "a"]), `newest first, and on one day by regulator, docket and id (${got.join(" ")})`);
  ok(same(got.slice(4).sort(), ["b", "e"]) && JSON.stringify(rows) === before, "a row with no day is last; the list given is not changed in place");
  ok(same(R.sortRows([...rows].reverse()).map((r) => r.id), got), "the order is the same whatever order the file lists the rows in");
}

// 3. the fold
{
  const ids = Array.from({ length: 11 }, (_, i) => i);
  const f = R.foldOf(ids);
  ok(f.shown.length === 8 && f.folded.length === 3 && same([...f.shown, ...f.folded], ids), "eleven rows: eight shown, three behind the fold, none lost and none twice");
  ok(R.foldOf(ids.slice(0, 8)).folded.length === 0 && R.foldOf([]).shown.length === 0 && R.foldOf(ids, 2).shown.length === 2, "eight rows or fewer: no fold");
}

// 4. the rows shown
{
  const list = [row("ok1", "2026-04-01"), row("nourl", "2026-04-02", { url: "" }), row("script", "2026-04-03", { url: "javascript:alert(1)" }), row("z", "2026-04-04", { sentence: "Made-up: the Zoning board met." }),
    row("p", "2026-04-05", { read: "Made-up: a permit is needed.", read_by: "model" }), row("cc", "2026-04-06", { title: "Made-up: the city\n council hearing" }), row("cb", "2026-04-07", { why_here: "made-up: the County Board said so" }),
    row("ok1", "2026-04-08"), "not a row", null, row("ok2", "2026-04-09", { url: "http://example.invalid/plain" })];
  const c = R.choose(list);
  ok(same(c.rows.map((r) => r.id), ["ok2", "ok1"]) && c.rows[1].date === "2026-04-01", `the rows shown are the ones with a source address and no municipal word, newest first (${c.rows.map((r) => r.id).join(" ")})`);
  ok(same(c.dropped.map((d) => d.id), ["nourl", "script", "z", "p", "cc", "cb", "ok1"]) && same(c.dropped.slice(2, 6).map((d) => d.word), ["zoning", "permit", "city council", "county board"]),
    "not shown, each with why: no address (2), a municipal word in the sentence, the read, the title and the mapping's reason (4), listed twice (1)");
  ok(c.dropped.every((d) => R.municipalWord(d.why) === null) && R.municipalWord("Transmission cost allocation for large loads") === null && R.MUNICIPAL.length === 4, "the reason shown on hover holds no municipal word itself");
  ok(R.choose(undefined).rows.length === 0 && R.choose({}).rows.length === 0, "a list that is not a list shows nothing");
  const tip = R.droppedTip([...c.dropped, { id: "made-up-zoning-7", why: "a word of it is outside this page's scope", word: "zoning" }]);
  ok(tip.startsWith("Not shown: nourl (no address of a source document); ") && tip.endsWith("a row (a word of it is outside this page's scope).") && R.municipalWord(tip) === null, "the count of rows not shown names each by its id with why on hover, and holds no municipal word");
}

// 5. the block
{
  const miso = R.blockOf(F, "miso");
  ok(miso.state === "paused" && miso.words === "paused while terms are reviewed" && miso.rows.length === 0 && miso.federal.length === 0 && /paused/.test(miso.why), "MISO: the fixed words, the pause's reason on hover, and no row, although the made-up file lists one and federal rows exist");
  ok(R.blockOf(null, "miso").state === "paused" && R.blockOf(null, "miso").words === R.PAUSED_WORDS, "MISO reads the same with no file at all");
  const pjm = R.blockOf(F, "pjm");
  ok(pjm.state === "shown" && pjm.rows.length === 11 && pjm.rows[0].id === "p11" && pjm.rows[10].id === "p1", "PJM: its eleven rows, newest first");
  ok(same(pjm.federal.map((r) => r.id), ["f1"]) && same(R.blockOf(F, "ercot").federal.map((r) => r.id), ["p3", "f1"]), "the federal group follows; a row the file lists under the grid and under federal is shown once, under the grid");
  const none = R.blockOf(F, "caiso");
  ok(none.state === "none" && none.words === "none held" && none.why === "Made-up reason: nothing found." && none.rows.length === 0 && none.federal.length === 2, "a grid with none: a short placeholder with the file's reason, and the federal group");
  const gone = R.blockOf(F, "nyiso"), nofile = R.blockOf(null, "ercot");
  ok(gone.state === "missing" && gone.federal.length === 2 && nofile.state === "missing" && nofile.federal.length === 0 && nofile.why === R.NOT_HELD_WHY, 'no entry for the grid, or no file: "not held yet" with why');
  const spp = R.blockOf(F, "spp");
  ok(spp.state === "paused" && spp.words === "made-up pause" && spp.rows.length === 0 && spp.federal.length === 0, "a grid the file marks paused shows the file's words and no row");
  ok(R.fileOf(null) === null && R.fileOf([]) === null && R.fileOf({ grids: {} }) === null && R.fileOf({ grids: [], federal_all_grids: [] }) === null && F !== null, "a thing that is not a rules file is not read as one");
}

// 6. the status
{
  const a = R.statusOf(row("s", "2026-01-01", { status_as_worded: "Pending before the Commission", status_class: "open" }));
  const b = R.statusOf(row("s", "2026-01-01", { status_as_worded: "", status_class: "decided", row_kind: "order" }));
  const c = R.statusOf(row("s", "2026-01-01", { status_as_worded: " ", status_class: "not stated" })), d = R.statusOf(row("s", "2026-01-01", { status_class: "something else" }));
  ok(a.words === "Pending before the Commission" && a.stated && /Class: open/.test(a.why), "a status the regulator words is shown as worded, with its class on hover");
  ok(b.words === "decided" && b.stated && /an order/.test(b.why) && c.words === "not stated" && !c.stated && d.words === "not stated", 'else the class; a row with neither reads "not stated", and a class the contract does not name is not shown');
}

// 7. the hovers and the read
{
  const r = row("h", "2026-06-01", { sentence: 'Made-up: the tariff "applies" to loads of 75 MW or more.', page: 12, topic: "large-load tariff", tags: ["large_load", "interconnection"] });
  const tip = R.docketTip(r);
  ok(tip.startsWith(`"${r.sentence}"`) && tip.includes("Page 12 of the document.") && tip.includes("Topic: large-load tariff.") && tip.includes("Tags: large_load, interconnection."), "the docket's hover is the exact sentence, then the page, the topic and the tags");
  ok(R.docketTip(row("h", "2026-06-01", { sentence: "", page: null, topic: "", tags: [] })) === "No sentence of the document is held for this row." && R.docketWords(r) === "Made-up Commission, MU-h" && R.docketWords(row("h", "", { docket: "" })) === "Made-up Commission",
    "a row with no sentence says so; the link reads the regulator and the docket number");
  const m = R.readOf(row("r", "2026-06-01", { read: "Made-up line.", read_by: "model", read_model: "made-up-model", read_from: "the sentence and the page around it" }));
  ok(m.line === "Made-up line." && m.why.includes("made-up-model") && m.why.includes("the sentence and the page around it") && /model's read/.test(m.why), "a read the file marks as a model's is shown, with the model and what it was made from on hover");
  const u = R.readOf(row("r", "2026-06-01", { read: "Made-up line nobody signed.", read_by: null })), z = R.readOf(row("r", "2026-06-01"));
  ok(u.line === null && z.line === null && u.why === R.NO_READ_WHY && R.NO_READ === "no read yet", 'a line the file does not mark as a model\'s is not shown: the row reads "no read yet"');
  ok(R.dayWords("2026-10-08") === "8 Oct 2026" && R.dayWords("2026-13-01") === null && R.dayWords("") === null && R.dayWords(null) === null && R.dayWords("8 October 2026") === null, "a day is shown as 8 Oct 2026; anything else is no day");
  ok(R.linkOf(r) === "https://example.invalid/doc/h.pdf" && R.linkOf(row("x", "", { url: "ftp://example.invalid/x" })) === null && R.linkOf(row("x", "", { url: 'https://example.invalid/"x' })) === null, "only an http or https address is a link");
  ok(same(R.sourcesOf(F).map((s) => s.regulator), ["Made-up Commission"]) && R.sourcesOf(null).length === 0, "each regulator's terms are listed once");
  ok(R.docketTip(row("t", "2026-06-01", { sentence: "Made-up title of a notice", sentence_from: "title", page: null })).startsWith('"Made-up title of a notice" Sentence from: title.'), "where the builder says the sentence is the document's title, the hover says so");
  ok(R.termsTip({ regulator: "M", terms_url: "", terms_quote: "Made-up terms." }) === '"Made-up terms."' && R.municipalWord(R.termsTip({ regulator: "M", terms_url: "", terms_quote: "Made-up: reuse is permitted." })) === null && R.termsTip({ regulator: "M", terms_url: "", terms_quote: "" }) === "",
    "a regulator's terms are its own words on hover; a quote with a municipal word in it is left to the Method note");
  ok(R.leftOf(F) === null && same(R.leftOf({ ...MADE_UP, not_on_page: { count: 2, why: "Made-up reason." } }), { count: 2, why: "Made-up reason." }) && R.municipalWord(R.leftOf({ ...MADE_UP, not_on_page: { count: 1, why: "made-up: a zoning matter" } }).why) === null
    && R.safeWhy("", "x") === "x" && R.blockOf({ ...MADE_UP, grids: { caiso: { state: "none", why: "made-up: the County Board" } } }, "caiso").why === "No proceeding or order in motion is held for this grid.",
    "what the file holds and does not put on the page is a count with the file's reason; a reason with a municipal word in it is not carried to a hover");
}

// 8. the real file, where it is on the machine
{
  const at = path.join(here, "..", "data", "datacenter", "rules.json");
  if (!fs.existsSync(at)) console.log("note: data/datacenter/rules.json is not on this machine; the real file was not read");
  else {
    const real = R.fileOf(JSON.parse(fs.readFileSync(at, "utf8")));
    ok(real !== null, "data/datacenter/rules.json is a rules file");
    if (real) {
      const lines = [];
      let fine = true;
      for (const g of R.RULE_GRIDS) {
        const b = R.blockOf(real, g);
        const all = [...b.rows, ...b.federal];
        if (g === "miso" && (b.state !== "paused" || all.length)) fine = false;
        if (!all.every((r) => R.linkOf(r) && R.municipalWord(R.wordsOf(r)) === null)) fine = false;
        lines.push(`${g}: ${b.state}, ${b.rows.length} rows (${b.rows.filter((r) => R.readOf(r).line).length} with a read), federal ${b.federal.length} (${b.federal.filter((r) => R.readOf(r).line).length} with a read), not shown ${b.dropped.length}`);
      }
      ok(fine, "the real file: MISO shows no row, and every row shown has a source address and no municipal word");
      for (const l of lines) console.log(`     ${l}`);
    }
  }
}

console.log(failed ? `${failed} of ${n} failed` : `all ${n} passed`);
// the exit code is set and Node ends by itself: process.exit() here has ended with a libuv assertion on Windows (exit 127)
process.exitCode = failed ? 1 : 0;
