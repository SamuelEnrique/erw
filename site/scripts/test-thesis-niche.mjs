// Energy Research Warehouse (ERW) site, session 169: Thesis Builder (/thesis), the gate on the niche
// (lib/thesis/niche.ts). The owner's ruling of 8 October 2026, on his own examples: what is refused, what passes, the
// curated table and its chips, the one small model call for inputs outside the table and what happens when it fails,
// and "Run anyway" stored with the run.
//
//   node --import ./scripts/alias-register.mjs scripts/test-thesis-niche.mjs
//
// Exit 1 on a failure. Nothing is requested and no model is called: the model's answers below are written for the
// test, and the one request this file watches (the forced submit) goes to a stand-in for fetch.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as n from "../lib/thesis/niche.ts";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (...p) => fs.readFileSync(path.join(site, ...p), "utf-8");
let count = 0;
const test = async (name, fn) => { await fn(); count += 1; console.log(`ok   ${name}`); };
const never = async () => { throw new Error("the model was asked"); };
const REFUSED = ["geothermal", "oil & gas", "oil & gas demand", "energy", "AI data centers"];
const CHIPS = ["Geothermal mapping and sensing", "Methane leak detection for oil and gas operators", "Long-duration storage for data centers"];
const PLACEHOLDER = "For example: AI software that maps hidden geothermal resources";

await test("the form's words are the owner's, word for word", () => {
  assert.equal(n.NICHE_LABEL, "Niche: one product or business, for one customer");
  assert.equal(n.NICHE_PLACEHOLDER, PLACEHOLDER);
  assert.equal(n.NICHE_HELP, "Name what a startup sells and to whom. A sector such as \"geothermal\" or \"oil & gas\" is too wide.");
  assert.deepEqual([...n.NICHE_EXAMPLES], CHIPS);
  assert.equal(n.refusalWords("oil & gas demand"), "“oil & gas demand” is a sector or a market topic, not a niche. Pick one of these, or write your own:");
  assert.equal(n.RUN_ANYWAY, "Run anyway");
});

await test("the owner's five refused inputs are refused by the rules", () => {
  const why = { geothermal: "few_words", "oil & gas": "sector_only", "oil & gas demand": "sector_only", energy: "few_words", "AI data centers": "sector_only" };
  for (const x of REFUSED) {
    const g = n.gate(x);
    assert.equal(g.verdict, "refuse", x);
    assert.equal(g.why, why[x], x);
  }
});

await test("his three example chips and his placeholder pass, and no model is asked", async () => {
  for (const x of [...CHIPS, PLACEHOLDER.replace("For example: ", ""), PLACEHOLDER, "Geothermal mapping and sensing, US startups"]) {
    assert.equal(n.gate(x).verdict, "pass", x);
    const d = await n.judge(x, never);
    assert.deepEqual([d.ok, d.by, d.suggestions.length, d.message], [true, "rules", 0, ""], x);
  }
});

await test("the two rules: fewer than two content words, or every content word a sector or market word", () => {
  const refused = ["solar", "the wind industry", "geothermal startups", "US energy market", "energy and power", "oil and gas market trends", "electricity demand growth", "nuclear power", "clean energy",
    "hydrogen economy", "EV batteries", "data centers", "AI and energy", "carbon markets", "renewables in Texas", "for data centers", "AI for energy", "power for oil and gas"];
  for (const x of refused) assert.equal(n.gate(x).verdict, "refuse", x);
  // something sold, or a customer after "for" with something before it
  const passed = { "drilling tools": "sells", "solar panel recycling": "sells", "grid monitoring software": "sells", "carbon removal verification": "sells", "storage for data centers": "customer",
    "gas turbines for Permian operators": "customer", "hydrogen for steel mills": "customer", "batteries for utilities": "customer" };
  for (const [x, why] of Object.entries(passed)) { const g = n.gate(x); assert.deepEqual([g.verdict, g.why], ["pass", why], x); }
  // neither rule speaks: two content words or more, not all of them sector words, nothing sold and no customer
  for (const x of ["perovskite tandem photovoltaics", "enhanced rock weathering", "vehicle to home"]) assert.equal(n.gate(x).verdict, "unsure", x);
});

await test("stop words are not content: geography, grammar, startups", () => {
  assert.deepEqual(n.gate("Geothermal mapping and sensing, US startups").content, ["geothermal", "mapping", "sensing"]);
  assert.deepEqual(n.gate("the US geothermal industry").content, ["geothermal"]);
  assert.deepEqual(n.wordsOf("AI Data-Centers & data centres"), ["ai", "datacenters", "and", "datacenters"]);
});

await test("the curated table holds the thirteen broad inputs, and the owner's two lists as he wrote them", () => {
  assert.deepEqual(n.TABLE.map((t) => t.id), ["geothermal", "oil_gas", "solar", "wind", "storage", "nuclear", "hydrogen", "grid", "ev", "carbon", "data_centers", "buildings", "ai_energy"]);
  const of = (id) => n.TABLE.find((t) => t.id === id).suggestions;
  assert.deepEqual(of("geothermal"), ["Geothermal resource mapping software", "Closed-loop geothermal well technology", "High-temperature drilling tools for geothermal", "Lithium extraction from geothermal brines"]);
  assert.deepEqual(of("oil_gas"), ["Methane leak detection for upstream operators", "Produced water treatment and reuse in the Permian", "Electrified frac and compression equipment", "AI drilling optimization software"]);
  for (const t of n.TABLE) {
    assert.ok(t.suggestions.length >= 3 && t.suggestions.length <= 5, t.id);
    assert.equal(new Set(t.suggestions).size, t.suggestions.length, t.id);
    for (const s of t.suggestions) {
      assert.equal(n.gate(s).verdict, "pass", `${t.id}: ${s}`);            // a chip never leads to a second refusal or a question
      assert.ok(!/[—–]/.test(s), s);
    }
  }
  for (const s of n.DEFAULT_SUGGESTIONS) assert.equal(n.gate(s).verdict, "pass", s);
  assert.ok(n.DEFAULT_SUGGESTIONS.length >= 3 && n.DEFAULT_SUGGESTIONS.length <= 5);
});

await test("each broad input of the table is refused with its own chips, and no model is asked", async () => {
  const broad = { geothermal: "geothermal", "oil and gas": "oil_gas", "oil & gas": "oil_gas", "oil & gas demand": "oil_gas", solar: "solar", wind: "wind", storage: "storage", "battery storage": "storage",
    nuclear: "nuclear", hydrogen: "hydrogen", grid: "grid", "the power grid": "grid", EV: "ev", "EVs": "ev", carbon: "carbon", "data centers": "data_centers", "AI data centers": "data_centers",
    buildings: "buildings", "AI and energy": "ai_energy", "AI": "ai_energy" };
  for (const [x, id] of Object.entries(broad)) {
    const d = await n.judge(x.length < 3 ? `${x} ` : x, never);
    assert.equal(d.ok, false, x);
    assert.deepEqual([d.by, d.topic, d.model_failed], ["table", id, false], x);
    assert.deepEqual(d.suggestions, n.TABLE.find((t) => t.id === id).suggestions, x);
    assert.equal(d.message, n.refusalWords(x), x);
  }
  const d = await n.judge("oil & gas demand", never);
  assert.deepEqual(d.suggestions, ["Methane leak detection for upstream operators", "Produced water treatment and reuse in the Permian", "Electrified frac and compression equipment", "AI drilling optimization software"]);
  assert.equal(d.message, "“oil & gas demand” is a sector or a market topic, not a niche. Pick one of these, or write your own:");
});

await test("outside the table one call is made; a refusal by the rules stands, the call gives the chips", async () => {
  let asked = 0;
  const ask = async (input) => { asked += 1; assert.equal(input, "energy"); return { verdict: "niche", reason: "written for the test", suggestions: ["Energy trading software for retailers", "energy", "Metering hardware for landlords", "Demand response software for factories", "  Energy trading software for retailers. "] }; };
  const d = await n.judge("energy", ask);
  assert.equal(asked, 1);
  assert.deepEqual([d.ok, d.by, d.why, d.topic, d.model_failed], [false, "model", "few_words", null, false]);      // the model said "niche"; the rule's refusal stands
  assert.deepEqual(d.suggestions, ["Energy trading software for retailers", "Metering hardware for landlords", "Demand response software for factories"]);      // "energy" itself would be refused; the repeat is dropped
});

await test("where no rule speaks the call's verdict decides", async () => {
  const wide = await n.judge("perovskite tandem photovoltaics", async () => ({ verdict: "too_wide", reason: "a technology family", suggestions: ["Perovskite tandem cell materials", "Perovskite coating equipment for module makers", "Perovskite durability testing services"] }));
  assert.deepEqual([wide.ok, wide.by, wide.suggestions.length], [false, "model", 3]);
  assert.equal(wide.message, n.refusalWords("perovskite tandem photovoltaics"));
  const fine = await n.judge("perovskite tandem photovoltaics", async () => ({ verdict: "niche", reason: "", suggestions: [] }));
  assert.deepEqual([fine.ok, fine.by, fine.suggestions.length], [true, "model", 0]);
});

await test("the call failing: the rules decide", async () => {
  const fails = [async () => { throw new Error("written for the test: the call timed out"); }, async () => null, async () => "not json", async () => ({ verdict: "maybe", suggestions: [] }), async () => ({ reason: "no verdict" })];
  for (const ask of fails) {
    const refusedByRule = await n.judge("energy", ask);              // refused by the rules, outside the table
    assert.deepEqual([refusedByRule.ok, refusedByRule.by, refusedByRule.model_failed], [false, "rules", true]);
    assert.deepEqual(refusedByRule.suggestions, n.DEFAULT_SUGGESTIONS);
    const open = await n.judge("perovskite tandem photovoltaics", ask);      // no rule speaks: it passes
    assert.deepEqual([open.ok, open.by, open.model_failed, open.suggestions.length], [true, "rules", true, 0]);
  }
  // no model at all (no key, the switch off, the hour's calls used): the same, and nothing is marked as failed
  const a = await n.judge("energy"), b = await n.judge("perovskite tandem photovoltaics", null);
  assert.deepEqual([a.ok, a.by, a.model_failed, a.suggestions.length], [false, "rules", false, 5]);
  assert.deepEqual([b.ok, b.by, b.model_failed], [true, "rules", false]);
});

await test("a refusal always shows three to five chips, whatever the model gives", async () => {
  for (const suggestions of [[], ["oil"], ["Energy trading software for retailers"], Array.from({ length: 9 }, (_, i) => `Metering hardware for landlords number ${i}`), ["<b>software</b> for you", "see https://example.invalid software", "x".repeat(200)]]) {
    const d = await n.judge("energy", async () => ({ verdict: "too_wide", reason: "", suggestions }));
    assert.ok(d.suggestions.length >= 3 && d.suggestions.length <= 5, JSON.stringify(suggestions).slice(0, 60));
    for (const s of d.suggestions) assert.notEqual(n.gate(s).verdict, "refuse", s);
    assert.ok(d.suggestions.every((s) => !/[<>]|https?:/.test(s)));
  }
});

await test("a model's answer is read as data: its dashes, its length and its shape", () => {
  const a = n.readAnswer({ verdict: "too_wide", reason: "wide — very", suggestions: ["Sensors — for wells", 7, null, "short", "Drilling tools for geothermal wells."] });
  assert.deepEqual(a, { verdict: "too_wide", reason: "wide , very", suggestions: ["Sensors , for wells", "Drilling tools for geothermal wells"] });
  assert.equal(n.readAnswer(null), null);
  assert.equal(n.readAnswer({ verdict: "refuse" }), null);
  assert.equal(n.GATE_MODEL, "claude-haiku-4-5");
  assert.deepEqual(n.GATE_SCHEMA.required, ["verdict", "reason", "suggestions"]);
  assert.equal(n.gatePrompt("  oil  &  gas "), "Input: \"oil & gas\"");
});

await test("Run anyway: what is stored with the run", () => {
  const at = new Date("2026-10-09T08:00:00.000Z");
  assert.deepEqual(n.forcedOf("oil & gas demand", at), { forced: true, why: "sector_only", topic: "oil_gas", at: "2026-10-09T08:00:00.000Z" });
  assert.deepEqual(n.forcedOf("energy", at), { forced: true, why: "few_words", topic: null, at: "2026-10-09T08:00:00.000Z" });
  assert.deepEqual(n.forcedOf("perovskite tandem photovoltaics", at), { forced: true, why: "open", topic: null, at: "2026-10-09T08:00:00.000Z" });
  assert.equal(n.forcedOf("Methane leak detection for oil and gas operators", at), null);      // a ticked box on a niche is an ordinary run
});

await test("a forced run is queued through thesis_submit_forced with its gate", async () => {
  const before = { fetch: globalThis.fetch, url: process.env.SUPABASE_URL, key: process.env.SUPABASE_ANON_KEY, token: process.env.INTERNAL_COSTS_TOKEN };
  const calls = [];
  try {
    Object.assign(process.env, { SUPABASE_URL: "https://stand-in.invalid", SUPABASE_ANON_KEY: "a-stand-in-not-a-key", INTERNAL_COSTS_TOKEN: "a-stand-in-token-of-enough-length" });
    globalThis.fetch = async (url, init) => { calls.push({ url: String(url), body: JSON.parse(init.body) }); return new Response(JSON.stringify({ ok: true, run_id: "fixture-forced-1", dispatched: false }), { status: 200, headers: { "content-type": "application/json" } }); };
    const server = await import("../lib/thesis/server.ts");
    const gate = n.forcedOf("oil & gas demand", new Date("2026-10-09T08:00:00.000Z"));
    const r = await server.submitForced("oil & gas demand", "", "United States", gate);
    assert.deepEqual(r, { ok: true, run_id: "fixture-forced-1", dispatched: false });
    assert.equal(calls.length, 1);
    assert.ok(calls[0].url.endsWith("/rest/v1/rpc/thesis_submit_forced"), calls[0].url);
    assert.deepEqual(calls[0].body, { p_token: "a-stand-in-token-of-enough-length", p_niche: "oil & gas demand", p_stage: "", p_geography: "United States", p_gate: { forced: true, why: "sector_only", topic: "oil_gas", at: "2026-10-09T08:00:00.000Z" } });
  } finally {
    globalThis.fetch = before.fetch;
    for (const [k, v] of [["SUPABASE_URL", before.url], ["SUPABASE_ANON_KEY", before.key], ["INTERNAL_COSTS_TOKEN", before.token]]) { if (v === undefined) delete process.env[k]; else process.env[k] = v; }
  }
});

await test("the same module decides in the form and in the route", () => {
  const form = read("components", "thesis", "RunForm.tsx"), route = read("app", "api", "thesis", "run", "route.ts");
  assert.match(form, /from "@\/lib\/thesis\/niche"/);
  assert.match(route, /from "@\/lib\/thesis\/niche"/);
  assert.match(form, /\bgate\(asked\)/);
  assert.match(route, /await judge\(niche, gateModel\(\)\)/);
  assert.match(route, /refused: true/);
  assert.match(route, /submitForced\(niche, stage, geography, forced\)/);
  for (const w of ["NICHE_LABEL", "NICHE_PLACEHOLDER", "NICHE_HELP", "NICHE_EXAMPLES", "RUN_ANYWAY", "refusalWords"]) assert.ok(form.includes(w), `the form does not use ${w}`);
  // the form and the pure module hold no key and call no model; the call lives in the server's module alone
  const pure = read("lib", "thesis", "niche.ts");
  for (const text of [form, pure]) for (const w of ["@anthropic-ai/sdk", "process.env", "server-only", "fetch(\"https"]) assert.ok(!text.includes(w), `holds ${w}`);
  const model = read("lib", "thesis", "nicheModel.ts");
  assert.ok(model.includes("import \"server-only\"") && model.includes("maxRetries: 0") && model.includes("THESIS_GATE_MODEL"));
});

await test("the migration adds a column and a function and replaces nothing of 024", () => {
  const sql = fs.readFileSync(path.join(site, "..", "warehouse", "supabase", "migrations", "026_thesis_gate.sql"), "utf-8");
  assert.match(sql, /alter table public\.thesis_runs add column if not exists gate jsonb;/);
  assert.match(sql, /create or replace function public\.thesis_submit_forced\(p_token text, p_niche text, p_stage text, p_geography text, p_gate jsonb\)/);
  assert.match(sql, /r := public\.thesis_submit\(p_token, p_niche, p_stage, p_geography\);/);
  for (const f of ["thesis_submit(", "thesis_list(", "thesis_get(", "thesis_pitchbook_accept(", "thesis_token_ok("]) assert.ok(!sql.includes(`create or replace function public.${f}`), `replaces ${f}`);
  assert.ok(!/drop (table|function|policy)|create policy|disable row level/i.test(sql));
  assert.match(sql, /'site_ask', 'site_ask_ercot', 'site_thesis_gate'/);
});

console.log(`${count} tests pass`);
