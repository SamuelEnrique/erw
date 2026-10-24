// Energy Research Warehouse (ERW) site, session 1157 (chain 077): the stored example answers of the Grid tool's Ask
// panel (/grid), written from the recorded evaluations in warehouse/chat/eval/ to site/data/grid_ask_examples.json.
// No model call, no request: it reads committed files and writes one. warehouse/chat/ is chain 075's and is only read.
//
//   node scripts/build-grid-ask-examples.mjs           write the file
//   node scripts/build-grid-ask-examples.mjs --check   exit 1 when the committed file is not what the eval files give
//
// What is kept, for each grid (lib/gridtool.ts GRID_CHOICES, by its label as the eval files name it):
//   - an answer graded right by its run (verdict "right" and grade.ok true), answered or a refusal (not in the warehouse);
//   - from a run that recorded every tool call with its result (the `trace`); a run without one is left out whole, and
//     said so in the file (eval_s320_first_run.json recorded the count of calls only);
//   - every figure of the answer is in a tool result of that answer: the number check of lib/chat/ask.ts (numbers,
//     unverified), on the tool results only. A year (1990 to 2100), a list marker and a number the question itself
//     holds are not figures. Each figure is written with the call it came from: the table, the filter, the run's date;
//   - a question about one grid (a comparison of two grids is left out), once (the newest asking of the same words);
//   - at most five: the route the panel itself sends first (ERCOT: the panel's profile; the Lower 48: the general chat;
//     the other grids: the grid's own chat), then the newest run, then answers with figures before refusals, then id.
// Session 1187 (chain 091): a run whose grade is in a file of its own (chains 075 and 076's runs of 23 October,
// eval_s1113.py --grade) has it joined by question id from `grades`, each row checked against the run's (its status,
// its count of tool calls, its seconds, its cost: a row of another asking is not used). Graded right there is the
// grade on the keys: `ok` with `grade.ok` (session 1114's set), `now_ok` with `grade_now.ok` (session 320's set);
// an answer right only under the hold (a license refusal) or only with session 320's rulings taken its way is left
// out, and said so. When two runs asked the same words, the newest asking (its time, then its session) is the one
// kept (`newestAskings`), before the order above, so a later run of the same question replaces the earlier one.
// The hold of a license is not applied here: lib/gridask.ts applies it on the day the page is drawn (lib/license.ts).
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SITE = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const ROOT = path.join(SITE, "..");
export const OUT = path.join(SITE, "data", "grid_ask_examples.json");
export const MAX_EXAMPLES = 5;

// The grids of the panel, as lib/gridtool.ts names them (slug, the label the eval files use, the route the panel sends).
export const GRIDS = [
  ["ercot", "ERCOT", "panel"],
  ["caiso", "CAISO", "grid"],
  ["pjm", "PJM", "grid"],
  ["miso", "MISO", "grid"],
  ["nyiso", "NYISO", "grid"],
  ["isone", "ISO-NE", "grid"],
  ["spp", "SPP", "grid"],
  ["us48", "US48", "general"],
];

// The recorded runs read, newest first. `route` is how the run asked when a question carries no `via` of its own;
// `grades` is the file holding the run's grade when its questions carry none (session 1187).
export const RUNS = [
  { file: "warehouse/chat/eval/eval_s1133_s1114_run.json", grades: "warehouse/chat/eval/eval_s1133_s1114_grades.json", session: 1133, route: null },
  { file: "warehouse/chat/eval/eval_s1133_s320_run.json", grades: "warehouse/chat/eval/eval_s1133_s320_grades.json", session: 1133, route: null },
  { file: "warehouse/chat/eval/eval_s1114_run.json", grades: "warehouse/chat/eval/eval_s1114_grades.json", session: 1114, route: null },
  { file: "warehouse/chat/eval/eval_s1113_run.json", grades: "warehouse/chat/eval/eval_s1113_grades.json", session: 1113, route: null },
  { file: "warehouse/chat/eval/eval_s320_first_run.json", session: 320, route: null },
  { file: "warehouse/chat/eval/eval_s302_fixtures.json", session: 302, route: null },
  { file: "warehouse/chat/eval/eval_s267_fixtures.json", session: 267, route: "general" },
];

const VIA_WORDS = {
  panel: "the Grid panel's ERCOT profile (Ask ERCOT)",
  grid: "the grid's own chat",
  general: "the general chat of /ask",
};

// ------------------------------------------------------------------ the number check (as lib/chat/ask.ts)

const NUM = /(?<![A-Za-z_\d.])(-?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?!\d)/g;

/** The numbers of a text with their decimals, as lib/chat/ask.ts numbers(): [value, decimals, as written]. */
export function numbers(text) {
  const t = String(text ?? "").replace(/−/g, "-");
  const out = [];
  for (const m of t.matchAll(NUM)) {
    let sign = m[1];
    const whole = m[2], frac = m[3] ?? "";
    const at = m.index ?? 0;
    if (sign) {
      const before = at > 0 ? t[at - 1] : " ";
      if (!(/\s/.test(before) || "([:,=".includes(before) || at === 0)) sign = "";
    }
    out.push([parseFloat(sign + whole.replace(/,/g, "") + frac), frac ? frac.length - 1 : 0, (sign + whole + frac)]);
  }
  return out;
}

const listMarkers = (text) => new Set(Array.from(String(text).matchAll(/^\s*(\d+)[.)]\s/gm)).map((m) => parseFloat(m[1])));
const isYear = (v, d) => d === 0 && Number.isInteger(v) && v >= 1990 && v <= 2100;

/** Whether a figure written with d decimals is in a pool of numbers, at the rounding it was written to (as unverified()). */
export function inPool(v, d, pool) {
  const tol = 0.5 * 10 ** -d + 1e-9;
  return pool.some((p) => Math.abs(Math.abs(p) - Math.abs(v)) <= tol);
}

const MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December";
/** A text with its dates and clock times taken out: "2025-05-01", "2026-10-04T05:00Z", "16:00", "1 May 2025", "May 1".
 *  A date says which period a figure is of; it is not a figure. */
export function withoutDates(text) {
  return String(text ?? "")
    .replace(/\b\d{4}-\d{2}(?:-\d{2})?(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?Z?)?/g, " ")
    .replace(/\b\d{1,2}:\d{2}(?::\d{2})?\b/g, " ")
    .replace(new RegExp(`\\b\\d{1,2}(?=\\s+(?:${MONTHS})\\b)`, "g"), " ")
    .replace(new RegExp(`\\b(${MONTHS})\\s+\\d{1,2}\\b(?![,.]?\\d)`, "g"), "$1 ");
}

/** The figures of an answer: its numbers that are not a date, a year, a list marker or a number of the question itself. */
export function figuresOf(answer, question) {
  const markers = listMarkers(answer);
  const asked = numbers(question).map(([v]) => v);
  const seen = new Set();
  const out = [];
  for (const [v, d, raw] of numbers(withoutDates(answer))) {
    if (isYear(v, d) || (d === 0 && markers.has(v)) || inPool(v, d, asked)) continue;
    if (seen.has(raw)) continue;
    seen.add(raw);
    out.push({ v, d, raw });
  }
  return out;
}

// ------------------------------------------------------------------ one call: its table, its filter, its entity

/** The table, the filter and the entity of one recorded call. A compare call names its two sides. */
export function callSource(call) {
  const input = call.input ?? {};
  const sides = call.tool === "compare" ? [input.a ?? {}, input.b ?? {}] : [input];
  const tables = [...new Set(sides.map((s) => s.table).filter(Boolean))];
  const filterOf = (s) => Object.entries(s).filter(([k]) => k !== "table").map(([k, v]) => `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`).join(", ");
  const filter = call.tool === "compare" ? sides.map((s, i) => `${i ? "b" : "a"}: ${s.table ?? ""} ${filterOf(s)}`.trim()).join("; ") : filterOf(input);
  const ents = sides.map((s) => (typeof s.entity === "string" ? s.entity : (s.where && typeof s.where.entity === "string" ? s.where.entity : null))).filter(Boolean);
  return { tool: call.tool, tables, filter, entities: [...new Set(ents)] };
}

// Calls that read rows answer for a figure before calls that describe a table or list tables.
const READS = new Set(["query", "compare", "series"]);

/** Each figure of an answer with the call whose result holds it, or the figures no call returned. */
export function traceFigures(answer, question, trace) {
  const calls = (trace ?? []).filter((c) => !c.isError && c.out && !c.out.error);
  const ordered = [...calls.filter((c) => READS.has(c.tool)), ...calls.filter((c) => !READS.has(c.tool))];
  const pools = ordered.map((c) => numbers(JSON.stringify(c.out)).map(([v]) => v));
  const traced = [];
  const untraced = [];
  for (const f of figuresOf(answer, question)) {
    const i = pools.findIndex((p) => inPool(f.v, f.d, p));
    if (i < 0) untraced.push(f.raw);
    else traced.push({ figure: f.raw, call: ordered[i] });
  }
  return { traced, untraced };
}

// ------------------------------------------------------------------ the selection

/** A run's questions with the grade of its grades file joined by id (session 1187), and the ids that file could not
 *  grade, with why. A row is used only when it is of this asking: the same status, count of tool calls, seconds and
 *  cost as the run's question. Right is the grade on the keys; the hold's grade and the rulings' are not used. */
export function joinGrades(questions, grades) {
  const rows = new Map((grades?.questions ?? []).map((g) => [g.id, g]));
  const why = new Map();
  const out = (questions ?? []).map((q) => {
    const g = rows.get(q.id);
    if (!g) { why.set(q.id, "the grades file holds no row for it"); return { ...q, verdict: undefined, grade: undefined }; }
    const same = g.status === q.status && g.trace_calls === (Array.isArray(q.trace) ? q.trace.length : null) && g.seconds === q.seconds && g.cost_usd === q.cost_usd;
    if (!same) { why.set(q.id, "the grades file's row is of another asking"); return { ...q, verdict: undefined, grade: undefined }; }
    const onKeys = "now_ok" in g ? g.now_ok === true && g.grade_now?.ok === true : g.ok === true && g.grade?.ok === true;
    if (!onKeys && g.held_ok === true) why.set(q.id, "graded right only under the hold (a license refusal), not on its key");
    else if (!onKeys && g.if_ruled_ok === true) why.set(q.id, "graded right only with session 320's rulings taken its way, not on its key");
    return { ...q, verdict: onKeys ? "right" : "wrong", grade: { ok: onKeys } };
  });
  return { questions: out, why };
}

const gradedRight = (q) => q.verdict === "right" && q.grade && q.grade.ok === true && (q.status === "answered" || q.status === "not_in_warehouse");
const words = (s) => String(s).toLowerCase().replace(/\s+/g, " ").trim();

/** One run's usable examples and what was left out, with why. `run` is a RUNS entry, `data` the file read. */
export function examplesOfRun(run, data, grades = null) {
  const kept = [];
  const left = [];
  const labels = new Map(GRIDS.map(([slug, label]) => [label, slug]));
  const joined = grades ? joinGrades(data.questions, grades) : { questions: data.questions ?? [], why: new Map() };
  for (const q of joined.questions) {
    const why = (w) => left.push({ question_id: q.id, why: w });
    if (!labels.has(q.grid)) { why(`not one grid (${q.grid})`); continue; }
    if (!gradedRight(q)) { why(joined.why.get(q.id) ?? `graded ${q.verdict ?? "without a verdict"}`); continue; }
    if (!Array.isArray(q.trace)) { why("the run recorded no tool results for it"); continue; }
    const { traced, untraced } = traceFigures(q.answer, q.question, q.trace);
    if (untraced.length) { why(`a figure no tool returned: ${untraced.join(", ")}`); continue; }
    // the figures by the call they came from, in the order of the calls
    const byCall = new Map();
    for (const t of traced) {
      if (!byCall.has(t.call)) byCall.set(t.call, []);
      byCall.get(t.call).push(t.figure);
    }
    const sources = [...byCall.entries()].map(([call, figures]) => ({ ...callSource(call), figures }));
    const via = q.via ?? run.route ?? "general";
    kept.push({
      id: `s${run.session}:${q.id}`,
      grid: labels.get(q.grid),
      file: run.file,
      session: run.session,
      question_id: q.id,
      run: `session ${run.session}'s evaluation, asked ${String(q.asked_at_utc).slice(0, 10)} through POST /api/ask, ${VIA_WORDS[via] ?? via}`,
      asked_at_utc: q.asked_at_utc,
      via,
      model: q.model ?? null,
      question: q.question,
      answer: q.answer,
      refusal: q.status === "not_in_warehouse",
      verdict: q.verdict,
      sources,
    });
  }
  return { kept, left };
}

/** One asking of each question's words: when two runs asked the same words, the panel's own route first (as before),
 *  then the newest asking by its time, then by its session, then the run read first (RUNS is newest first). */
export function newestAskings(examples, route) {
  const best = new Map();
  const better = (a, b) =>
    ((a.via === route ? 0 : 1) - (b.via === route ? 0 : 1))
    || String(b.asked_at_utc).localeCompare(String(a.asked_at_utc))
    || (b.session - a.session);
  for (const e of examples) {
    const w = words(e.question);
    const now = best.get(w);
    if (!now || better(e, now) < 0) best.set(w, e);
  }
  const keep = new Set(best.values());
  return examples.filter((e) => keep.has(e));
}

/** The examples of one grid, chosen from every run's kept examples: at most MAX_EXAMPLES, in the order the file says. */
export function chooseForGrid(slug, kept) {
  const route = (GRIDS.find(([s]) => s === slug) ?? [])[2];
  const all = kept.filter((e) => e.grid === slug);
  const mine = newestAskings(all, route);
  mine.sort((a, b) =>
    (a.via === route ? 0 : 1) - (b.via === route ? 0 : 1)
    || String(b.asked_at_utc).slice(0, 10).localeCompare(String(a.asked_at_utc).slice(0, 10))
    || (a.refusal ? 1 : 0) - (b.refusal ? 1 : 0)
    || a.question_id.localeCompare(b.question_id));
  const seen = new Set();
  const out = [];
  for (const e of mine) {
    const w = words(e.question);
    if (seen.has(w)) continue;
    seen.add(w);
    out.push(e);
    if (out.length === MAX_EXAMPLES) break;
  }
  // usable: the distinct questions of the grid that pass, shown or not
  return { examples: out, usable: new Set(all.map((e) => words(e.question))).size };
}

// the hash of the file as git holds it: line ends as LF, so a Windows checkout (CRLF) and a Linux one agree
const sha = (buf) => crypto.createHash("sha256").update(String(buf).replace(/\r\n/g, "\n")).digest("hex").slice(0, 16);

/** The whole file, from the runs as read from disk. */
export function build(read = (rel) => fs.readFileSync(path.join(ROOT, rel))) {
  const files = [];
  const kept = [];
  for (const run of RUNS) {
    const buf = read(run.file);
    const data = JSON.parse(String(buf));
    const traced = (data.questions ?? []).some((q) => Array.isArray(q.trace));
    if (!traced) {
      files.push({ file: run.file, sha256_16: sha(buf), questions: (data.questions ?? []).length, kept: 0, left_out: "the run recorded the count of tool calls, not their results, so no figure of it can be traced to a tool result" });
      continue;
    }
    const gbuf = run.grades ? read(run.grades) : null;
    const r = examplesOfRun(run, data, gbuf ? JSON.parse(String(gbuf)) : null);
    kept.push(...r.kept);
    files.push({ file: run.file, sha256_16: sha(buf), ...(gbuf ? { grades: run.grades, grades_sha256_16: sha(gbuf) } : {}), questions: (data.questions ?? []).length, kept: r.kept.length, left: r.left });
  }
  const grids = {};
  for (const [slug, label] of GRIDS) {
    const { examples, usable } = chooseForGrid(slug, kept);
    grids[slug] = { label, usable, examples };
  }
  return {
    _about: "Session 1157 (chain 077): the stored example answers of the Ask panel on /grid, by grid. Each is an answer a recorded evaluation graded right, with every figure traced to the tool result it came from (table, filter, the run's date). No model call wrote or reads this file. Written by site/scripts/build-grid-ask-examples.mjs from the files named in `files`; lib/gridask.ts applies the license holds of lib/license.ts on the day the page is drawn.",
    built_by: "site/scripts/build-grid-ask-examples.mjs",
    max_examples: MAX_EXAMPLES,
    files,
    grids,
  };
}

export const render = (obj) => JSON.stringify(obj, null, 1) + "\n";

const main = path.resolve(process.argv[1] ?? "") === fileURLToPath(import.meta.url);
if (main) {
  const text = render(build());
  if (process.argv.includes("--check")) {
    const now = fs.existsSync(OUT) ? fs.readFileSync(OUT, "utf8").replace(/\r\n/g, "\n") : "";
    if (now !== text) { console.error(`${path.relative(ROOT, OUT)} is not what the eval files give: run node scripts/build-grid-ask-examples.mjs`); process.exit(1); }
    console.log(`${path.relative(ROOT, OUT)} is current`);
  } else {
    fs.writeFileSync(OUT, text);
    const g = JSON.parse(text).grids;
    for (const [slug, v] of Object.entries(g)) console.log(`${slug}: ${v.examples.length} shown of ${v.usable} usable`);
  }
}
