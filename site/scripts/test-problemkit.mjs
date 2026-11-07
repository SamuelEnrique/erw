// Energy Research Warehouse (ERW) site, session 3650: the problem sets brought to a state an instructor can assign.
//
//   node --test scripts/test-problemkit.mjs        (from site/; no network, no build, no model)
//
// lib/problemkit.ts imports nothing, so node runs it as it is; lib/problems.ts and the pages read Supabase and the
// Next.js aliases, so they are read here as text: each question has its one-line computation with no typed number,
// each set a worked example, the five in a rising order that names the set's own five, and the pages draw the outcome
// line, the example first, the computation in each answer, every figure's source as its hover, the grids, tables and
// skills of each set, the CSV of each set (public tables only) and the instructors' hover.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { GUIDE, METHOD_NOTE, csvOf, figureRows, inOrder, instructorNote, keyWords, sourceOfKey, tablesOfKey } from "../lib/problemkit.ts";

const SITE = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => fs.readFileSync(path.join(SITE, p), "utf-8");
const PROBLEMS = read("lib/problems.ts");
const CITES = JSON.parse(read("data/table_citations.json"));
const VERDICTS = JSON.parse(read("data/table_verdicts.json"));
const cite = (t) => CITES[t];
const LETTER = { "know-your-grid": "a", "prices-and-your-bill": "b", "when-the-grid-broke": "c", "storage-and-taxes": "d", "networks-and-money": "e" };

/** The text of one set's section of lib/problems.ts, from its banner to the next. */
function section(letter) {
  const marks = [...PROBLEMS.matchAll(/\/\/ -{20,} set ([A-E])/g)];
  const i = marks.findIndex((m) => m[1] === letter.toUpperCase());
  assert.ok(i >= 0, `the banner of set ${letter}`);
  const end = marks[i + 1]?.index ?? PROBLEMS.indexOf("export const SETS");
  return PROBLEMS.slice(marks[i].index, end);
}

/** Each bracketed array that follows `<field>: ` in a text, brackets balanced (strings and template literals skipped). */
function arraysAfter(text, field) {
  const out = [];
  const re = new RegExp(`\\b${field}: (?:[a-zA-Z0-9]+ \\? )?\\[`, "g");
  for (const m of text.matchAll(re)) {
    let depth = 0, j = m.index + m[0].length - 1, quote = null;
    for (; j < text.length; j += 1) {
      const c = text[j];
      if (quote) { if (c === "\\") j += 1; else if (c === quote) quote = null; continue; }
      if (c === '"' || c === "`" || c === "'") { quote = c; continue; }
      if (c === "[") depth += 1;
      if (c === "]" && --depth === 0) break;
    }
    out.push(text.slice(m.index + m[0].length - 1, j + 1));
  }
  return out;
}
const outsideStrings = (s) => s.replace(/`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, "");

test("the guide names the five sets, each order the set's own five ids", () => {
  const slugs = [...PROBLEMS.matchAll(/\{ slug: "([a-z-]+)"/g)].map((m) => m[1]);
  assert.deepEqual(Object.keys(GUIDE).sort(), [...slugs].sort());
  for (const [slug, g] of Object.entries(GUIDE)) {
    const l = LETTER[slug];
    assert.deepEqual([...g.order].sort(), ["1", "2", "3", "4", "5"].map((n) => l + n), slug);
    assert.ok(g.grids.length && g.tables.length && g.skills.length, `${slug}: grids, tables and skills`);
  }
});

test("each set says in one line what a student can do after it", () => {
  for (const [slug, g] of Object.entries(GUIDE)) {
    assert.ok(g.can.length > 20 && g.can.length < 160, slug);
    assert.ok(!/[\n.]$/.test(g.can) && !g.can.includes("\n"), `${slug}: one line, the page adds the period`);
  }
});

test("each set's tables are the tables its section of lib/problems.ts reads, every one public and cited", () => {
  for (const [slug, g] of Object.entries(GUIDE)) {
    const named = new Set([...section(LETTER[slug]).matchAll(/"([a-z0-9_]+)"/g)].map((m) => m[1]).filter((t) => t in CITES));
    assert.deepEqual([...named].sort(), [...g.tables].sort(), slug);
    for (const t of g.tables) {
      assert.ok(CITES[t], `${t} has a citation`);
      // a table held row by row ("unsettled") is read for its public rows only (lib/supabase.ts); the set names no grid it holds
      const [verdict, words] = VERDICTS[t] ?? [];
      assert.ok(verdict === "public" || verdict === "unsettled", `${t}: ${verdict}`);
      if (verdict === "unsettled") for (const grid of g.grids) assert.ok(!words.includes(grid), `${slug} names ${grid}, whose rows of ${t} are held`);
    }
  }
});

test("the questions are put in the guide's order, an unnamed one after", () => {
  const qs = ["a1", "a2", "a3", "a4", "a5", "zz"].map((id) => ({ id }));
  assert.deepEqual(inOrder(qs, GUIDE["know-your-grid"].order).map((q) => q.id), ["a4", "a3", "a1", "a2", "a5", "zz"]);
  assert.deepEqual(inOrder(qs, []).map((q) => q.id), qs.map((q) => q.id));
  assert.match(PROBLEMS, /questions: inOrder\(built\.questions, GUIDE\[slug\]\?\.order \?\? \[\]\)/);
});

test("every set has a worked example, and every question and example its one-line computation", () => {
  for (const l of "ABCDE") {
    const s = section(l);
    assert.match(s, /async function set[A-E]\(\): Promise<Built>/, `set ${l} returns its example`);
    assert.match(s, /return \{ example, questions: \[q1, q2, q3, q4, q5\] \};/, `set ${l}`);
    assert.match(s, new RegExp(`id: "${l.toLowerCase()}x"`), `set ${l}'s example id`);
    const blocks = s.split(/const q\d: Question = |billQ = \(|const example: Question(?: \| null)? = /).slice(1);
    for (const b of blocks) assert.ok(/\bline: /.test(b.slice(0, 4000)), `set ${l}: a question without its line: ${b.slice(0, 80)}`);
  }
});

test("no line, answer or example carries a typed number", () => {
  const lines = arraysAfter(PROBLEMS, "line");
  assert.ok(lines.length >= 28, `found ${lines.length} lines`);  // 25 questions (two bills share one) and 5 examples, set A's fifth a variable
  for (const arr of [...lines, ...arraysAfter(PROBLEMS, "answer")]) {
    const out = outsideStrings(arr);
    assert.equal(out.match(/(?<![\w.$])\d+(\.\d+)?(?![\w])/), null, arr.slice(0, 120));
  }
});

test("every key form lib/problems.ts writes has its source words, each table's citation in them", () => {
  const forms = new Set([...PROBLEMS.matchAll(/k: `([a-z_]+)\|/g)].map((m) => m[1]));
  for (const f of ["series", "calc"]) forms.add(f);
  const sample = {
    series: "series|eia930_all_demand|eia930:ERCO|demand_mw|2026-10-13T00:00:00Z",
    series_max: "series_max|eia930_all_demand|demand_mw|2026-10-13T00:00:00Z|2026-10-14T00:00:00Z|eia930:ERCO",
    series_sum: "series_sum|eia930_all_generation|net_generation_mw|2026-10-13T00:00:00Z|2026-10-14T00:00:00Z|eia930:CISO",
    calc: "calc|ratio|series~event_window_daily~ercot:HB_HUBAVG~rt_max~2021-02-15T00:00:00Z~uri_2021|series~event_window_daily~ercot:HB_HUBAVG~rt_max~2019-02-15T00:00:00Z~uri_2021",
    bill: "bill|TX|wholesale|2026-09-01T00:00:00Z", battery: "battery|round_trip_pct", sev: "sev|TX|oil|1000|2026-09|base",
    sevcert: "sevcert|tx_lp_gas|2026-08", sevcredit: "sevcredit|tx_lp_gas|2026-08", spotmean: "spotmean|eia:wti_cushing|2026-09",
    net: "net|ties|ERCO|2026-11-05T12:00:00Z", mr: "mr|iso=ercot|capture:2026-09", mrs: "mrs|iso=ercot|uri_2021|days", fullday: "fullday|know-your-grid|2026-10-13",
  };
  for (const f of forms) {
    assert.ok(sample[f], `a sample key for the form ${f}`);
    const w = sourceOfKey(sample[f], cite);
    assert.ok(w && w.endsWith(`Method: ${METHOD_NOTE}.`), `${f}: ${w}`);
    for (const t of tablesOfKey(sample[f])) assert.ok(w.includes(CITES[t]), `${f}: the citation of ${t}`);
  }
  assert.equal(sourceOfKey("nosuch|x", cite), undefined);
  assert.match(keyWords(sample.calc), /^the ratio of \(event_window_daily: ercot:HB_HUBAVG, rt_max, 2021-02-15, event uri_2021\)/);
  assert.deepEqual(tablesOfKey("calc|pct|series~a_table~e~v~t|series~b_table~e~v~t"), ["a_table", "b_table"]);
  assert.deepEqual(tablesOfKey("bill|CA|total"), []);
});

test("a set's figures as CSV: once each, the example first, a held table's figure left out", () => {
  const v = (k, x, u) => ({ k, v: x, u });
  const A = v("series|eia930_all_demand|eia930:ERCO|demand_mw|t", 72605, "MW"), B = v("series|eia930_all_demand|eia930:CISO|demand_mw|t", 30000, "MW");
  const H = v("series|held_table|x|y|t", 1, "");
  const ex = { id: "ax", answer: [A, " and ", B], steps: [[A]], line: [A, " / ", B] };
  const qs = [{ id: "a1", answer: ["see ", B, H], steps: [[v("calc|ratio|a|b", Number.NaN)]], line: [] }];
  const rows = figureRows(ex, qs, (k) => k.includes("held_table"));
  assert.deepEqual(rows.map((r) => [r.question, r.key]), [["ax", A.k], ["ax", B.k]]);
  const csv = csvOf("know-your-grid", 'Know "your" grid', rows, "2026-11-06T02:00:00Z", cite);
  const lines = csv.trimEnd().split("\n");
  assert.ok(lines.slice(0, 3).every((l) => l.startsWith("# ")) && lines[1].includes("2026-11-06T02:00:00Z"));
  assert.equal(lines[3], "question,key,table,value,unit,source");
  assert.ok(lines[4].startsWith(`ax,${A.k},eia930_all_demand,72605,MW,"eia930_all_demand: eia930:ERCO, demand_mw, t. Source: `));
  assert.equal(lines.length, 6);
});

test("the set page draws the outcome, the example first, each answer's computation and every figure's source", () => {
  const page = read("app/learn/problems/[slug]/page.tsx");
  assert.match(page, /data-can><strong>After this set<\/strong> a student can \{GUIDE\[slug\]\.can\}\./);
  assert.ok(page.indexOf("<Example q={got.data.example} />") > 0 && page.indexOf("<Example q={got.data.example} />") < page.indexOf("got.data.questions.map"));
  assert.match(page, /<summary className="cursor-pointer text-accent">Show answer<\/summary>[\s\S]*data-line><strong>Computation\.<\/strong> <span className="font-mono"><Parts parts=\{q\.line\} \/>/);
  assert.match(page, /<Num check=\{p\.k\} raw=\{p\.v\} source=\{sourceOfKey\(p\.k, cite\)\}>/);
});

test("the index lists each set's grids, tables, skills and CSV, and the instructors' hover holds the keys and the note", () => {
  const index = read("app/learn/problems/page.tsx");
  assert.match(index, /Grid: \{GUIDE\[s\.slug\]\.grids\.join\(", "\)\}\. Tables: /);
  assert.match(index, /Skills: \{GUIDE\[s\.slug\]\.skills\.join\(", "\)\}\. <a href=\{`\/learn\/problems\/\$\{s\.slug\}\/data\.csv`\} download>/);
  assert.match(index, /<Tip label="for instructors" id="instructors">For instructors\. \{instructorNote\(\)\}<\/Tip>/);
  const note = instructorNote();
  assert.ok(note.includes(METHOD_NOTE));
  for (const [slug, g] of Object.entries(GUIDE)) assert.ok(note.includes(`${slug}: ${g.tables.join(", ")}`), slug);
});

test("the CSV route answers in review only the internal view and drops what is not public", () => {
  const route = read("app/learn/problems/[slug]/data.csv/route.ts");
  assert.match(route, /const internal = await cookieOpens\(/);
  assert.match(route, /statusOf\(`\/learn\/problems\/\$\{slug\}`\) === "review"\) return text\(/);
  assert.match(route, /figureRows\(set\.example, set\.questions, \(k\) => heldBy\(k\) !== null\)/);
});

test("no em or en dash in the files of this session", () => {
  for (const p of ["lib/problemkit.ts", "lib/problems.ts", "lib/problemEditions.ts", "app/learn/problems/page.tsx", "app/learn/problems/[slug]/page.tsx", "app/learn/problems/[slug]/data.csv/route.ts", "scripts/test-problemkit.mjs"]) {
    assert.ok(!/[\u2013\u2014]/.test(read(p)), p);
  }
});
