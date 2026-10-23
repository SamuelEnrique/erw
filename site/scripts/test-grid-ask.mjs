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
    ok(!!q && q.verdict === "right" && q.grade?.ok === true, `${e.id}: graded right by its run`);
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
