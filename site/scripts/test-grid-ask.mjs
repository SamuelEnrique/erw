// Energy Research Warehouse (ERW) site, session 1157 (chain 077): the stored example answers of the Grid tool's Ask
// panel. The build script (scripts/build-grid-ask-examples.mjs) and the selection on the day (lib/gridask.ts), on the
// committed eval files and on small fixtures. No request, no browser, no model.
//
//   node --import ./scripts/alias-register.mjs scripts/test-grid-ask.mjs
//
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const B = await import("./build-grid-ask-examples.mjs");
const A = await import("../lib/gridask.ts");
const L = await import("../lib/license.ts");

const SITE = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const ROOT = path.join(SITE, "..");
let failed = 0, n = 0;
const ok = (cond, what) => { n += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed += 1; };
const before = new Date("2026-10-20T12:00:00Z"), after = new Date("2026-10-23T12:00:00Z");

// ---- the committed file is what the eval files give
const built = B.build();
const committed = fs.readFileSync(B.OUT, "utf8").replace(/\r\n/g, "\n");
ok(B.render(built) === committed, "data/grid_ask_examples.json is what the build script writes from the eval files");
ok(B.render(B.build()) === B.render(built), "the build is the same twice (no clock, no order of the disk)");

// ---- every grid: five or fewer, graded right, every figure in a tool result of its own recorded run
const evals = new Map();
const evalOf = (file) => { if (!evals.has(file)) evals.set(file, JSON.parse(fs.readFileSync(path.join(ROOT, file), "utf8"))); return evals.get(file); };
for (const [slug] of B.GRIDS) {
  const g = built.grids[slug];
  ok(!!g && g.examples.length <= 5, `${slug}: five or fewer examples (${g?.examples.length})`);
  ok(new Set(g.examples.map((e) => e.question.toLowerCase())).size === g.examples.length, `${slug}: no question twice`);
  for (const e of g.examples) {
    const q = evalOf(e.file).questions.find((x) => x.id === e.question_id);
    // session 1187: a run whose grade is in a file of its own is read from that file, on its keys (not the hold's, not the rulings')
    const gfile = (B.RUNS.find((r) => r.file === e.file) ?? {}).grades;
    const gr = gfile ? evalOf(gfile).questions.find((x) => x.id === e.question_id) : null;
    const rightOnKeys = !!gr && ("now_ok" in gr ? gr.now_ok === true && gr.grade_now?.ok === true : gr.ok === true && gr.grade?.ok === true);
    ok(!!q && (gfile ? rightOnKeys && gr.trace_calls === q.trace.length && gr.seconds === q.seconds : q.verdict === "right" && q.grade?.ok === true), `${e.id}: graded right by its run`);
    ok(q && q.answer === e.answer && q.question === e.question, `${e.id}: the question and answer as stored`);
    ok(e.grid === slug, `${e.id}: of the grid it is shown for`);
    const outs = (q?.trace ?? []).filter((c) => !c.isError).map((c) => B.numbers(JSON.stringify(c.out)).map(([v]) => v));
    for (const s of e.sources) for (const f of s.figures) {
      const [[v, d]] = B.numbers(f);
      ok(outs.some((p) => B.inPool(v, d, p)), `${e.id}: ${f} is in a tool result of its run (${s.tables.join(",")})`);
    }
    ok(B.figuresOf(e.answer, e.question).length === e.sources.reduce((k, s) => k + s.figures.length, 0), `${e.id}: every figure of the answer has a source`);
    ok(e.refusal || e.sources.length > 0, `${e.id}: an answer with figures names their tables`);
  }
}
ok(built.files.some((f) => /eval_s320/.test(f.file) && f.kept === 0 && /not their results/.test(f.left_out ?? "")), "a run that kept no tool results is left out whole, and said so");
ok(built.files.every((f) => fs.existsSync(path.join(ROOT, f.file))), "every source file named exists");

// ---- the rules, on fixtures
const run = { file: "fixture.json", session: 9, route: "general" };
const call = (table, out, input = {}) => ({ tool: "query", input: { table, ...input }, out, isError: false });
const Q = (id, over) => ({ id, grid: "SPP", question: `Question ${id}?`, answer: "It was 12.34 USD/MWh.", verdict: "right", grade: { ok: true }, status: "answered", asked_at_utc: "2026-10-01T00:00:00Z", trace: [call("cost_of_power_monthly", { result: [{ value: 12.3402 }] }, { entity: "spp:SPPNORTH_HUB" })], ...over });
const fx = B.examplesOfRun(run, { questions: [
  Q("a1"),
  Q("a2", { verdict: "wrong", grade: { ok: false } }),
  Q("a3", { answer: "It was 99.9 USD/MWh." }),
  Q("a4", { grid: "SPP vs ERCOT" }),
  Q("a5", { trace: null }),
  Q("a6", { answer: "On 1 May 2025 (2025-05-01) it was 12.34.", question: "In 2025?" }),
  Q("a7", { status: "not_in_warehouse", answer: "Not in the warehouse.", trace: [] }),
  Q("a8", { trace: [{ ...call("cost_of_power_monthly", { error: "x 12.34" }), isError: true }] }),
] });
const keptIds = fx.kept.map((e) => e.question_id).sort().join(",");
ok(keptIds === "a1,a6,a7", `only answers graded right, one grid, traced (kept ${keptIds})`);
ok(fx.left.find((l) => l.question_id === "a3")?.why.includes("99.9"), "a figure no tool returned is named as the reason");
ok(fx.left.find((l) => l.question_id === "a8")?.why.includes("12.34"), "a figure only an error held is not traced");
ok(fx.kept.find((e) => e.question_id === "a1").sources[0].figures.join() === "12.34" && fx.kept.find((e) => e.question_id === "a1").sources[0].filter === "entity=spp:SPPNORTH_HUB", "a figure carries its table and filter");
ok(B.figuresOf("On 1 May 2025 (2025-05-01) it was 12.34.", "").map((f) => f.raw).join() === "12.34", "dates and years are not figures");
const many = Array.from({ length: 8 }, (_, i) => ({ ...fx.kept[0], id: `x${i}`, question_id: `q${i}`, question: `Q${i}`, session: 100 + i, asked_at_utc: `2026-10-0${i + 1}T00:00:00Z`, via: i === 0 ? "grid" : "general" }));
const ch = B.chooseForGrid("spp", [...many, { ...many[7], id: "dup" }]);
ok(ch.examples.length === 5 && ch.usable === 8, `at most five shown, the rest counted (${ch.examples.length} of ${ch.usable})`);
ok(ch.examples[0].via === "grid" && ch.examples[1].session === 107, "the panel's own route first, then the newest run");

// ---- session 1187: the runs of chains 075 and 076 (23 October), their grades in files of their own
const NEW_RUNS = ["eval_s1133_s1114_run.json", "eval_s1133_s320_run.json", "eval_s1114_run.json", "eval_s1113_run.json"];
for (const name of NEW_RUNS) {
  const r = B.RUNS.find((x) => x.file.endsWith("/" + name));
  ok(!!r && !!r.grades && fs.existsSync(path.join(ROOT, r.grades)), `${name}: in RUNS with its grades file`);
  const f = built.files.find((x) => x.file === r?.file);
  ok(!!f && f.grades === r.grades && /^[0-9a-f]{16}$/.test(f.grades_sha256_16 ?? "") && f.kept > 0, `${name}: read, its grades file hashed, ${f?.kept} answers kept`);
  ok(evalOf(r.file).questions.every((q) => Array.isArray(q.trace)), `${name}: every answer kept its tool calls with their results`);
}
ok(B.RUNS.every((r, i) => i === 0 || B.RUNS[i - 1].session >= r.session), "RUNS are read newest first");
const leftOf = (name, id) => built.files.find((x) => x.file.endsWith("/" + name)).left.find((l) => l.question_id === id)?.why ?? "";
ok(/only under the hold/.test(leftOf("eval_s1113_run.json", "g07")), "an answer right only under the hold (a license refusal) is left out, and said so");
ok(/rulings/.test(leftOf("eval_s1113_run.json", "b01")), "an answer right only with session 320's rulings taken its way is left out, and said so");
ok(/graded wrong/.test(leftOf("eval_s1114_run.json", "t06")), "an answer wrong on its key is left out");
ok(built.grids.spp.examples.some((e) => e.id === "s1133:t01") && !built.grids.spp.examples.some((e) => e.id === "s1114:t01"), "SPP's t01, asked by sessions 1114 and 1133: the newer asking shown, the older not");
for (const [slug] of B.GRIDS) {
  for (const e of built.grids[slug].examples) {
    const later = B.RUNS.flatMap((r) => (evalOf(r.file).questions ?? []).filter((q) => q.question === e.question && String(q.asked_at_utc) > String(e.asked_at_utc)).map((q) => ({ r, q })));
    const usedLater = later.filter(({ r, q }) => built.files.find((x) => x.file === r.file)?.left?.every((l) => l.question_id !== q.id) && (q.via ?? r.route ?? "general") === e.via);
    ok(usedLater.length === 0, `${e.id}: no newer kept asking of the same words by the same route`);
  }
}
// joinGrades on fixtures: the two forms of grade, a row of another asking, a missing row
const tq = (id, over = {}) => Q(id, { verdict: undefined, grade: undefined, seconds: 10, cost_usd: 0.1, ...over });
const jg = B.joinGrades([tq("k1"), tq("k2"), tq("k3"), tq("k4"), tq("k5"), tq("k6"), tq("k7")], { questions: [
  { id: "k1", status: "answered", trace_calls: 1, seconds: 10, cost_usd: 0.1, ok: true, grade: { ok: true } },
  { id: "k2", status: "answered", trace_calls: 1, seconds: 10, cost_usd: 0.1, now_ok: true, grade_now: { ok: true }, held_ok: true },
  { id: "k3", status: "answered", trace_calls: 1, seconds: 10, cost_usd: 0.1, now_ok: false, grade_now: { ok: false }, held_ok: true, if_ruled_ok: true },
  { id: "k4", status: "answered", trace_calls: 1, seconds: 10, cost_usd: 0.1, now_ok: false, grade_now: { ok: false }, held_ok: false, if_ruled_ok: true },
  { id: "k5", status: "answered", trace_calls: 2, seconds: 10, cost_usd: 0.1, ok: true, grade: { ok: true } },
  { id: "k7", status: "answered", trace_calls: 1, seconds: 10, cost_usd: 0.1, ok: true, grade: { ok: false } },
] });
const jv = Object.fromEntries(jg.questions.map((q) => [q.id, q.verdict ?? "none"]));
ok(jv.k1 === "right" && jv.k2 === "right", "a grades row right on its key (ok, or now_ok) makes the answer right");
ok(jv.k3 === "wrong" && /under the hold/.test(jg.why.get("k3")) && jv.k4 === "wrong" && /rulings/.test(jg.why.get("k4")), "right only under the hold or only with the rulings is not right");
ok(jv.k5 === "none" && /another asking/.test(jg.why.get("k5")), "a grades row of another asking (its count of calls differs) is not used");
ok(jv.k6 === "none" && /no row/.test(jg.why.get("k6")), "a question the grades file does not hold has no verdict");
ok(jv.k7 === "wrong", "ok without grade.ok is not right");
const fj = B.examplesOfRun(run, { questions: [tq("k1"), tq("k3"), tq("k5")] }, { questions: [
  { id: "k1", status: "answered", trace_calls: 1, seconds: 10, cost_usd: 0.1, ok: true, grade: { ok: true } },
  { id: "k3", status: "answered", trace_calls: 1, seconds: 10, cost_usd: 0.1, now_ok: false, grade_now: { ok: false }, held_ok: true },
] });
ok(fj.kept.map((e) => e.question_id).join() === "k1" && fj.kept[0].verdict === "right" && fj.left.map((l) => l.question_id).join() === "k3,k5", "a run with a grades file keeps only its answers right on their keys");
// the order rule: the newest asking of the same words, before the order of the panel
const base = { ...fx.kept[0], grid: "spp", question: "Same words?", via: "grid" };
const older = { ...base, id: "s1114:t01", session: 1114, question_id: "t01", asked_at_utc: "2026-10-23T19:43:43Z" };
const newer = { ...base, id: "s1133:t01", session: 1133, question_id: "t01", asked_at_utc: "2026-10-23T23:05:33Z" };
ok(B.chooseForGrid("spp", [older, newer]).examples.map((e) => e.id).join() === "s1133:t01" && B.chooseForGrid("spp", [newer, older]).examples.map((e) => e.id).join() === "s1133:t01", "two runs asked the same words the same day: the later asking kept, whatever the order read");
const sameTime = { ...older, id: "s1200:t01", session: 1200 };
ok(B.chooseForGrid("spp", [older, sameTime]).examples[0].id === "s1200:t01", "asked at the same time: the later session kept");
const otherRoute = { ...newer, id: "s1300:t01", session: 1300, via: "general", asked_at_utc: "2026-10-24T00:00:00Z" };
ok(B.chooseForGrid("spp", [older, otherRoute]).examples[0].id === "s1114:t01", "the panel's own route still comes before a newer asking by another route");
ok(B.chooseForGrid("spp", [older, newer]).usable === 1, "one question asked twice is one usable question");
ok(B.chooseForGrid("spp", [{ ...older, refusal: true }, newer]).examples[0].id === "s1133:t01" && B.chooseForGrid("spp", [older, { ...newer, refusal: true }]).examples[0].id === "s1133:t01", "the newer asking is kept whether it or the older is a refusal");

// ---- the hold on the day (lib/gridask.ts, lib/license.ts)
const nyAfter = A.gridAskExamples("nyiso", after);
ok(nyAfter.shown.length > 0 && nyAfter.shown.every((e) => e.held), "NYISO after 21 October: every stored answer read a held table and is not shown");
ok(nyAfter.shown.every((e) => e.held.words === L.licenseReason(e.held.table) && e.held.words.startsWith("license needed: ")), "the refusal is the live Ask's words for a held read (licenseReason)");
ok(A.gridAskExamples("nyiso", before).shown.every((e) => !e.held), "before the hold's day nothing is held");
const ne = A.gridAskExamples("isone", after).shown;
ok(ne.some((e) => e.held) && ne.some((e) => !e.held && e.sources.every((s) => s.tables.includes("carbon_intensity_monthly"))), "ISO-NE: held tables dropped, the public carbon answers kept");
ok(A.gridAskExamples("ercot", after).shown.every((e) => !e.held), "ERCOT: a table held for other grids does not hold ERCOT's rows");
const fake = { max_examples: 5, grids: { spp: { label: "SPP", usable: 2, examples: [
  { ...fx.kept[0], grid: "spp", sources: [{ tool: "query", tables: ["news_index"], filter: "", entities: [], figures: ["12.34"] }] },
  { ...fx.kept[0], grid: "spp", id: "s9:b", sources: [{ tool: "query", tables: ["cost_of_power_monthly"], filter: "", entities: [], figures: ["12.34"] }] },
] } } };
const fk = A.gridAskExamples("spp", after, fake).shown;
ok(fk[0].held?.table === "news_index" && fk[1].held === null, "a table held whole is held for any grid; one held by grid only for its grids");
ok(A.gridAskExamples("nowhere", after).shown.length === 0, "an unknown grid has no examples");

// ---- the words of the count
ok(A.examplesLine(2, "SPP") === "Two stored answers for SPP so far, asked of the warehouse and graded right.", "fewer than five: said plainly");
ok(A.examplesLine(0, "MISO").startsWith("No stored answers for MISO so far"), "none: said plainly");
ok(A.examplesLine(1, "MISO").startsWith("One stored answer for MISO so far"), "one: singular");
ok(A.examplesLine(5, "US48").startsWith("Five stored answers for the Lower 48, asked"), "five: no 'so far'");

// ---- no model, no request
for (const f of ["scripts/build-grid-ask-examples.mjs", "lib/gridask.ts", "components/grid/AskExamples.tsx"]) {
  const src = fs.readFileSync(path.join(SITE, f), "utf8");
  const code = src.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
  const imports = [...code.matchAll(/^\s*import[^;]*?from\s+["']([^"']+)["']/gm)].map((m) => m[1]);
  ok(imports.every((m) => !/anthropic|lib\/chat|app\/ask|components\/ask/.test(m)) && !/fetch\s*\(|XMLHttpRequest/.test(code), `${f}: no model, no request, no chat module (imports ${imports.join(" ")})`);
}
ok(!committed.includes(String.fromCharCode(0x2014)), "the data file holds no em dash");

console.log(`\n${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
