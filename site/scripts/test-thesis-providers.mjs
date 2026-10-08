// Energy Research Warehouse (ERW) site, session 150: Thesis Builder (/thesis), the data providers of the fetch stage
// (lib/thesis/providers.ts): PitchBook as the first provider of one interface, and Harmonic and Crunchbase beside it.
//
//   node --import ./scripts/alias-register.mjs scripts/test-thesis-providers.mjs
//
// Exit 1 on a failure. Nothing is written and nothing is requested: no provider, no connector and no model is called.
// Every company, person and figure below is made up for the test and is no company's (scripts/thesis-stub.mjs,
// scripts/thesis-providers-fixtures.mjs and tests/fixtures/session150/ say so of themselves).
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as pb from "../lib/thesis/pitchbook.ts";
import * as pv from "../lib/thesis/providers.ts";
import { DONE, KEY, fixtureAnswer } from "./thesis-stub.mjs";
import { RUN, crunchbaseAnswer, harmonicAnswer } from "./thesis-providers-fixtures.mjs";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const root = path.join(site, "..");
const read = (...p) => fs.readFileSync(path.join(root, ...p), "utf8");
const lf = (s) => s.replace(/\r\n/g, "\n");
const sha = (s) => crypto.createHash("sha256").update(s, "utf8").digest("hex");
const fixture = (name) => JSON.parse(read("tests", "fixtures", "session150", name));
let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };
const EM = String.fromCharCode(0x2014);

const REQ = fixture("pitchbook_request_main.json");
const READ = fixture("pitchbook_read_main.json");
const run = { run_id: REQ.inputs.run_id, niche: REQ.inputs.niche, request: REQ.request };
const exampleOf = (text) => JSON.parse(text.split("```json")[1].split("```")[0]);
// Session 158: Crunchbase answers are not kept, so checkPaste refuses one before it reads the text. Crunchbase's
// format and reader are kept as they were (a ruling can open the provider again, and a run that already holds an
// answer is still drawn), and are tested here by themselves: the same steps as checkPaste, without its refusal.
const PLAIN = "Crunchbase answers are not kept until its terms are ruled on";
const readAs = (id, pasted, runId, year) => {
  if (!pv.NOT_KEPT[id]) return pv.checkPaste(id, pasted, runId, year);
  const got = pb.extractJson(pasted);
  if (!got.ok) return got;
  const { key, ...payload } = got.value;
  if (payload.format !== pv.PROVIDERS[id].format) return { ok: false, reason: `the format is ${payload.format}` };
  const r = pv.PROVIDERS[id].read(payload, runId, year);
  return r.ok ? { ok: true, provider: id, payload: r.payload, key: typeof key === "string" && key.trim() ? key.trim() : null } : r;
};

test("three providers behind one interface, PitchBook first and the default", () => {
  assert.deepEqual(pv.providerList().map((p) => [p.id, p.label, p.format]), [["pitchbook", "PitchBook", "erw-pitchbook-1"], ["harmonic", "Harmonic", "erw-harmonic-1"], ["crunchbase", "Crunchbase", "erw-crunchbase-1"]]);
  assert.equal(pv.DEFAULT_PROVIDER, "pitchbook");
  for (const p of pv.providerList()) {
    for (const k of ["id", "label", "format", "terms", "received_note"]) assert.equal(typeof p[k], "string", `${p.id}.${k}`);
    for (const k of ["requestText", "read"]) assert.equal(typeof p[k], "function", `${p.id}.${k}`);
    assert.equal(pv.providerOfFormat(p.format).id, p.id);
  }
  assert.equal(pv.PROVIDERS.pitchbook.format, pb.FORMAT);
  assert.equal(pv.PROVIDERS.pitchbook.label, pb.LABEL);
  assert.equal(pv.PROVIDERS.pitchbook.received_note, pb.RECEIVED_NOTE);
});

test("PitchBook: the text of an erw-pitchbook-1 request is unchanged, byte for byte", () => {
  // the fixture holds a request as the code of main made it before this session; the provider hands back the text
  // the run saved and makes none of its own
  assert.equal(REQ.run_py_changed_when_made, false);
  assert.equal(sha(REQ.request.paste_text), REQ.paste_text_sha256);
  const text = pv.PROVIDERS.pitchbook.requestText(run);
  assert.equal(text, REQ.request.paste_text);
  assert.equal(Buffer.compare(Buffer.from(text, "utf8"), Buffer.from(REQ.request.paste_text, "utf8")), 0);
  assert.equal(sha(text), REQ.paste_text_sha256);
  // a saved request names no provider: it is read as PitchBook's, in code
  assert.equal("provider" in REQ.request, false);
  assert.equal(pv.providerOf(REQ.request), "pitchbook");
  assert.equal(pv.providerOf({}), "pitchbook");
  assert.equal(pv.providerOf(null), "pitchbook");
  assert.equal(pv.providerOf({ format: "erw-harmonic-1" }), "harmonic");
  assert.equal(pv.providerOf({ provider: "crunchbase", format: "erw-pitchbook-1" }), "crunchbase");
});

test("PitchBook: a pasted erw-pitchbook-1 answer is read as before, byte for byte, on session 135's fixtures", () => {
  // the reader itself is the file of session 135, untouched
  assert.equal(sha(lf(read("site", "lib", "thesis", "pitchbook.ts"))), READ.pitchbook_ts_sha256_lf, "lib/thesis/pitchbook.ts is not the file of main");
  assert.equal(READ.cases.length, 3);
  for (const c of READ.cases) {
    const r = pv.checkPaste("pitchbook", c.pasted, c.run_id, READ.this_year);
    assert.equal(r.ok, true, `${c.name}: ${r.reason}`);
    assert.equal(JSON.stringify(r.payload), c.read, c.name);              // what main stored, to the byte
    assert.equal(sha(JSON.stringify(r.payload)), c.read_sha256, c.name);
    const payload = Object.fromEntries(Object.entries(pb.extractJson(c.pasted).value).filter(([k]) => k !== "key"));
    assert.equal(JSON.stringify(pb.validatePitchbook(payload, c.run_id, READ.this_year).payload), c.read);   // and what the old path writes today
    assert.equal(JSON.stringify(pv.PROVIDERS.pitchbook.read(payload, c.run_id, READ.this_year).payload), c.read);
    assert.equal("provider" in r.payload, false, "a PitchBook answer is stored as before: no new key");
  }
  assert.equal(pv.checkPaste("pitchbook", READ.cases[2].pasted, DONE, 2026).key, KEY);   // the one-time key is handed back, never stored
  assert.equal(pv.checkPaste("pitchbook", READ.cases[0].pasted, READ.cases[0].run_id, 2026).key, null);
  // a refusal is the old reader's own, word for word
  const bad = JSON.stringify({ ...fixtureAnswer(), valuation: 1 });
  assert.equal(pv.checkPaste("pitchbook", bad, DONE, 2026).reason, pb.validatePitchbook(JSON.parse(bad), DONE, 2026).reason);
  assert.match(pv.checkPaste("pitchbook", bad, DONE, 2026).reason, /holds a key the format does not have: "valuation"/);
});

test("the pending request's format: the example a saved erw-pitchbook-1 request shows is still accepted, unchanged", () => {
  // run 20261006T193517Z-50a8be waits on a request of this format, written by the same code as the fixture. Its own
  // text holds its one-time key and is not read here; the format's own example stands in for it.
  const text = pv.PROVIDERS.pitchbook.requestText(run);
  const example = exampleOf(text);
  assert.equal(example.format, "erw-pitchbook-1");
  assert.equal(example.run_id, run.run_id);
  assert.equal(pv.checkPaste("pitchbook", text, run.run_id).ok, false, "the unfilled template is refused: its date is a placeholder");
  const filled = text.replace('"pulled_on": "YYYY-MM-DD"', '"pulled_on": "2026-10-07"');
  const r = pv.checkPaste("pitchbook", filled, run.run_id);
  assert.equal(r.ok, true, r.reason);
  assert.equal(r.key, REQ.inputs.key);
  assert.equal(r.payload.label, "PitchBook");
  assert.equal("key" in r.payload, false);
  const direct = pb.validatePitchbook(Object.fromEntries(Object.entries({ ...example, pulled_on: "2026-10-07" }).filter(([k]) => k !== "key")), run.run_id);
  assert.equal(direct.ok, true, direct.reason);
  assert.equal(JSON.stringify(r.payload), JSON.stringify(direct.payload));      // read through the interface as session 135's reader reads it
  assert.equal(r.payload.companies.length, 2);
  assert.equal(r.payload.companies[0].last_round.size_usd_m, 12.5);
});

for (const id of ["harmonic", "crunchbase"]) {
  const p = pv.PROVIDERS[id];
  test(`${p.label}: the request text is made from the run's saved request, and its own example passes its own reader`, () => {
    const text = p.requestText(run);
    assert.ok(text.startsWith(`You have a ${p.label} connector.`));
    for (const w of [`Run: ${run.run_id}`, `Niche: ${run.niche}`, "1. Example Storage Inc. (https://www.example.com)", "2. Sample Grid Co", `"format": "${p.format}"`, `"found": false`, "additional_companies",
      `report only what ${p.label} returns`, "do not estimate", "Use read-only tools only", "headquarters: United States"]) assert.ok(text.includes(w), `${id}: ${w}`);
    assert.ok(!text.includes("Listed Example Co"), "a company the run did not ask for is not asked for");
    assert.ok(!text.includes(REQ.inputs.key) && !/^Key:/m.test(text), "the one-time key is PitchBook's: it is in no other provider's request");
    assert.ok(!text.includes(EM));
    assert.ok(!/@/.test(text), "no address of anyone");
    for (const w of ["confidence", "score", "Q1", "tie"]) assert.ok(!new RegExp(`\\b${w}\\b`, "i").test(text), `${id}: the request holds "${w}"`);
    assert.equal(text, p.requestText(JSON.parse(JSON.stringify(run))), "the same run gives the same text");
    assert.equal(p.requestText({ run_id: "x", niche: "y", request: null }), "");
    assert.equal(p.requestText({ run_id: "x", niche: "y", request: { companies: [] } }), "");
    // the example block: refused as it stands (its date is a placeholder), accepted with the date filled, and every
    // field in it is a mapped one
    const example = exampleOf(text);
    assert.equal(readAs(id, text, run.run_id).ok, false);
    assert.match(readAs(id, text, run.run_id).reason, /"pulled_on"/);
    const r = readAs(id, text.replace('"pulled_on": "YYYY-MM-DD"', '"pulled_on": "2026-10-07"'), run.run_id);
    assert.equal(r.ok, true, r.reason);
    assert.equal(r.payload.provider, id);
    assert.equal(r.payload.label, p.label);
    assert.equal(r.payload.received_note, p.received_note);
    assert.equal(r.payload.companies.length, example.companies.length);
    assert.deepEqual(r.payload.companies[1], { name: `a company ${p.label} does not hold`, found: false, record: {} });
    assert.equal(JSON.stringify(r.payload).includes("not_mapped"), false, `${id}: the format's own example holds a field that is not mapped`);
    assert.equal(r.key, null);
  });
}

test("the request of Harmonic names the connector's documented tool categories and Harmonic's own field names only", () => {
  const text = pv.PROVIDERS.harmonic.requestText(run);
  for (const w of ["search or lookup tools", "enrichment tools", "saved search tools", "saved_searches", "funding_total", "last_funding_at", "is_current_position", "where your Harmonic plan includes deal data"]) assert.ok(text.includes(w), w);
  // every field the example shows is one the reader maps (checked above: nothing of it lands under not_mapped)
  const fields = new Set([...pv.HARMONIC_COMPANY, ...pv.HARMONIC_PERSON, ...pv.HARMONIC_EXPERIENCE, ...pv.HARMONIC_ROUND, ...pv.HARMONIC_ROUND_INVESTOR, ...pv.HARMONIC_INVESTOR].map(([f]) => f));
  assert.ok(fields.has("funding.funding_total") && fields.has("full_name") && fields.has("is_lead") && fields.has("aum_amount_usd"));
});
test("the request of Crunchbase names the connector's documented tools in plain words and Crunchbase's own field ids", () => {
  const text = pv.PROVIDERS.crunchbase.requestText(run);
  for (const w of ["entity resolution tool", "entity lookup tool", "search tools", "Never guess an identifier", "founder_identifiers", "raised_funding_rounds", "num_employees_enum", "value, currency, value_usd", "create or change no Crunchbase list"]) assert.ok(text.includes(w), w);
});

test("an answer in another provider's format is refused, and the page is told plainly which format it was given", () => {
  const h = JSON.stringify(harmonicAnswer()), c = JSON.stringify(crunchbaseAnswer()), p = JSON.stringify(fixtureAnswer());
  assert.equal(pv.checkPaste("pitchbook", h, RUN).reason, 'This answer is in the format "erw-harmonic-1", Harmonic\'s. The provider chosen is PitchBook, which takes "erw-pitchbook-1". Choose Harmonic above, or paste PitchBook\'s answer.');
  assert.equal(pv.checkPaste("harmonic", p, RUN).reason, 'This answer is in the format "erw-pitchbook-1", PitchBook\'s. The provider chosen is Harmonic, which takes "erw-harmonic-1". Choose PitchBook above, or paste Harmonic\'s answer.');
  // session 158: the words for a format are the function's, as before (three assertions that went through checkPaste
  // with Crunchbase chosen, or with Crunchbase's answer, now ask the function itself or expect the plain refusal)
  assert.match(pv.formatFault("crunchbase", "erw-harmonic-1"), /"erw-harmonic-1", Harmonic's\. The provider chosen is Crunchbase/);
  assert.equal(pv.checkPaste("harmonic", c, RUN).reason, `${PLAIN}.`);
  assert.equal(pv.checkPaste("pitchbook", c, RUN).reason, `${PLAIN}.`);
  assert.equal(pv.checkPaste("harmonic", JSON.stringify({ ...harmonicAnswer(), format: "erw-harmonic-2" }), RUN).reason, 'This answer names the format "erw-harmonic-2". The provider chosen is Harmonic, which takes "erw-harmonic-1".');
  assert.equal(pv.formatFault("crunchbase", undefined), 'This answer names no format. The provider chosen is Crunchbase, which takes "erw-crunchbase-1".');
  assert.equal(pv.checkPaste("harmonic", "no json here", RUN).reason, "No JSON object could be read in the pasted text.");
  assert.equal(pv.checkPaste("harmonic", "  ", RUN).reason, "Nothing was pasted.");
  for (const [id, text] of [["harmonic", h], ["pitchbook", p]]) assert.equal(pv.checkPaste(id, "Here it is:\n```json\n" + text + "\n```\nDone.", RUN, 2026).ok, true, id);
  assert.equal(readAs("crunchbase", "Here it is:\n```json\n" + c + "\n```\nDone.", RUN, 2026).ok, true, "Crunchbase's reader still reads its format");
});

test("session 158: a Crunchbase answer is refused with the plain words before the pasted text is read, and nothing of it reaches the store", () => {
  assert.deepEqual(pv.NOT_KEPT, { crunchbase: PLAIN });
  assert.equal(pv.notKept("crunchbase"), `${PLAIN}.`);
  assert.equal(pv.notKept("pitchbook"), null);
  assert.equal(pv.notKept("harmonic"), null);
  assert.equal(pv.NOT_KEPT_MARK, "not yet available");
  // whatever is pasted, the answer is the same and holds nothing of the text: a good answer, one wrapped in a code
  // block, a text with no JSON, an empty text (each of which checkPaste answers differently for a provider it reads)
  const good = JSON.stringify(crunchbaseAnswer());
  for (const text of [good, "Here it is:\n```json\n" + good + "\n```", "no json here", "  ", JSON.stringify(harmonicAnswer()), JSON.stringify({ ...crunchbaseAnswer(), run_id: "another-run" })]) {
    assert.deepEqual(pv.checkPaste("crunchbase", text, RUN, 2026), { ok: false, reason: `${PLAIN}.` });
  }
  // an answer in Crunchbase's format under another provider: the same words, and the page is not told to choose Crunchbase
  for (const id of ["pitchbook", "harmonic"]) {
    assert.equal(pv.formatFault(id, "erw-crunchbase-1"), `${PLAIN}.`);
    assert.equal(pv.checkPaste(id, good, RUN, 2026).ok, false);
    assert.ok(!/Choose Crunchbase/.test(pv.checkPaste(id, good, RUN, 2026).reason));
  }
  // the route: the refusal stands before the pasted text is looked at, before the reader, the hash and the store
  const route = read("site", "app", "api", "thesis", "provider", "route.ts");
  const at = (w) => { const i = route.indexOf(w); assert.ok(i > 0, `the route does not hold ${w}`); return i; };
  const refuse = at("const held = notKept(body.provider);");
  assert.ok(route.slice(refuse).startsWith("const held = notKept(body.provider);\n  if (held) return no(held, 400);") || route.slice(refuse).startsWith("const held = notKept(body.provider);\r\n  if (held) return no(held, 400);"));
  for (const later of ["typeof body.pasted", "Buffer.byteLength(body.pasted", "checkPaste(provider.id", 'createHash("sha256")', "getRun(runId)", "acceptProvider(runId"]) assert.ok(refuse < at(later), `the refusal must stand before ${later}`);
  assert.ok(at("if (!isProviderId(body.provider))") < refuse);
  assert.equal(route.split("acceptProvider(").length, 2, "the store is asked in one place only");
  assert.ok(!/console\.(log|error|warn)\([^)]*pasted/.test(route), "nothing of the pasted text is written to a log");
  // the panel: such a provider is never the one chosen, so its request text is never in the box to copy
  const panel = read("site", "components", "thesis", "PitchbookPanel.tsx");
  assert.ok(panel.includes("PROVIDER_IDS.filter((id) => !have(id) && !notKept(id))"));
  assert.ok(panel.includes("data-thesis-provider-unavailable={id}") && panel.includes("title={off}") && panel.includes("disabled={done || busy || !!off}"));
  // the format, the request text and the reader are kept as they were
  assert.equal(pv.PROVIDERS.crunchbase.format, "erw-crunchbase-1");
  assert.equal(pv.providerOfFormat("erw-crunchbase-1").id, "crunchbase");
  assert.equal(pv.validateCrunchbase(crunchbaseAnswer(), RUN).ok, true);
});

test("session 158: PitchBook and Harmonic are as they were", () => {
  assert.equal(pv.checkPaste("harmonic", JSON.stringify(harmonicAnswer()), RUN).ok, true);
  assert.equal(pv.checkPaste("pitchbook", JSON.stringify(fixtureAnswer()), RUN, 2026).ok, true);
  assert.equal(pv.formatFault("pitchbook", "erw-harmonic-1"), 'This answer is in the format "erw-harmonic-1", Harmonic\'s. The provider chosen is PitchBook, which takes "erw-pitchbook-1". Choose Harmonic above, or paste PitchBook\'s answer.');
  assert.equal(sha(pv.PROVIDERS.pitchbook.requestText(run)), REQ.paste_text_sha256);
});

const H = () => pv.checkPaste("harmonic", JSON.stringify(harmonicAnswer()), RUN).payload;
const C = () => readAs("crunchbase", JSON.stringify(crunchbaseAnswer()), RUN).payload;      // session 158: the reader by itself (see readAs)

test("Harmonic: a documented field with its documented shape is mapped; everything else is kept as given, not mapped", () => {
  const p = H();
  assert.deepEqual(Object.keys(p), ["format", "provider", "run_id", "pulled_on", "label", "received_note", "companies", "additional_companies", "lists", "not_mapped"]);
  assert.deepEqual([p.format, p.provider, p.label, p.pulled_on], ["erw-harmonic-1", "harmonic", "Harmonic", "2026-10-07"]);
  assert.deepEqual(p.not_mapped, { fixture_envelope_extra: ["kept", "as", "given"] });
  const c = p.companies[0];
  assert.equal(c.record.name, "Example Storage");
  assert.equal(c.record.id, "1000001");                                             // an id is kept as text
  assert.equal(c.record["funding.funding_total"], 18200000);
  assert.equal(c.record["founding_date.date"], "2019-01-01");
  assert.equal(c.record["funding.last_funding_at"], "2025-03-14T00:00:00Z");       // as given
  assert.deepEqual(c.record["funding.investors"], ["Fixture Fund One", "Fixture Fund Two"]);
  assert.equal(c.record["location.city"], "Austin");
  assert.equal(c.record["funding.valuation_info.amount"], 61000000);
  assert.ok(!("stage" in c.record), "a documented field with another shape is not mapped");
  // what was not mapped is the entry as given, without the mapped fields, in its own nesting
  assert.deepEqual(c.not_mapped, { company: { stage: 7, fixture_undocumented_field: { nested: "kept as given" } }, fixture_entry_extra: "kept as given" });
  assert.equal(c.rounds.length, 2);
  assert.deepEqual(c.rounds[1].not_mapped, { fixture_round_extra: "kept as given" });
  assert.deepEqual(c.rounds[1].investors[1], { record: { investor_name: "Fixture Fund Two", is_lead: false }, not_mapped: { fixture_investor_extra: 1 } });
  assert.equal(c.rounds[1].record["valuation_info.amount"], 61000000);
  assert.equal(c.people.length, 3);
  assert.deepEqual(c.people[1].not_mapped, { fixture_person_extra: "kept as given" });
  assert.deepEqual(c.people[0].experience[0].record, { title: "Co-Founder and Chief Executive", company_name: "Example Storage", is_current_position: true });
  assert.deepEqual(pv.notMappedOf(c), ["company.fixture_undocumented_field.nested", "company.stage", "fixture_entry_extra", "people.fixture_person_extra", "rounds.fixture_round_extra", "rounds.investors.fixture_investor_extra"]);
  assert.deepEqual(p.companies[1], { name: "Sample Grid Co", found: true, record: { name: "Sample Grid Co", headcount: 8, "location.location": "Reno, Nevada, United States" } });
  assert.equal(p.additional_companies[0].why, "Fixture: matched the search words.");
  assert.equal(p.additional_companies[0].record["funding.funding_total"], 1500000);
  assert.deepEqual(p.lists.map((l) => [l.name, l.of, l.results.length]), [["Fixture saved search of companies", "companies", 1], ["Fixture saved search of investors", "investors", 1], ["Fixture saved search of people", "people", 1]]);
  assert.deepEqual(p.lists[1].results[0], { name: "Fixture Fund Three", record: { type: "fixture investor type", check_size_min_usd: 250000, check_size_max_usd: 2000000, investment_count: 31 }, not_mapped: { record: { fixture_investor_field: "kept as given" } } });
  assert.deepEqual(p.lists[2].results[0].record, { full_name: "E. Fixture", linkedin_headline: "Fixture headline" });
  // nothing given is lost: every leaf value of the pasted answer is in what is stored
  const leaves = (v) => (v !== null && typeof v === "object" ? Object.values(v).flatMap(leaves) : [String(v)]);
  const stored = JSON.stringify(p);
  for (const leaf of leaves(harmonicAnswer())) assert.ok(stored.includes(JSON.stringify(leaf).slice(1, -1)) || stored.includes(leaf), `lost: ${leaf}`);
});
test("Harmonic: the envelope is the ERW's own and is checked strictly; a record's content never refuses an answer", () => {
  const bad = (f, re) => { const a = harmonicAnswer(); f(a); const r = pv.checkPaste("harmonic", JSON.stringify(a), RUN); assert.equal(r.ok, false); assert.match(r.reason, re); };
  bad((a) => { a.run_id = "another-run"; }, /"run_id" is not the run/);
  bad((a) => { delete a.pulled_on; }, /"pulled_on" is required/);
  bad((a) => { a.pulled_on = "2026-02-30"; }, /not a day of the calendar/);
  bad((a) => { a.pulled_on = "07/10/2026"; }, /"pulled_on" is required/);
  bad((a) => { delete a.companies; }, /"companies" is required/);
  bad((a) => { a.companies = Array.from({ length: 301 }, (_, i) => ({ name: `Company ${i}`, found: false })); }, /"companies" holds 301; at most 300/);
  bad((a) => { a.additional_companies = Array.from({ length: 101 }, (_, i) => ({ name: `Company ${i}`, found: false, why: "w" })); }, /"additional_companies" holds 101; at most 100/);
  bad((a) => { a.companies[0] = "Example Storage Inc."; }, /companies\[0\] must be an object/);
  bad((a) => { delete a.companies[0].name; }, /companies\[0\]\.name is required/);
  bad((a) => { a.companies[0].name = "n".repeat(121); }, /name is longer than 120 characters/);
  bad((a) => { a.companies[0].found = "yes"; }, /companies\[0\]\.found is required/);
  bad((a) => { delete a.additional_companies[0].why; }, /additional_companies\[0\]\.why is required/);
  bad((a) => { a.saved_searches = {}; }, /"saved_searches" must be a list/);
  bad((a) => { a.saved_searches[0].of = "deals"; }, /saved_searches\[0\]\.of must be "companies", "investors" or "people"/);
  bad((a) => { delete a.saved_searches[1].results; }, /saved_searches\[1\]\.results is required/);
  bad((a) => { delete a.saved_searches[1].results[0].name; }, /saved_searches\[1\]\.results\[0\]\.name is required/);
  for (const x of [null, [], "text", 3]) assert.equal(pv.validateHarmonic(x, RUN).ok, false);
  // a record's content: negative, of another type, absent, or not a record at all. The answer is accepted and the value kept as given.
  const odd = harmonicAnswer();
  odd.companies[0].company.headcount = -3;
  odd.companies[0].company.funding.funding_total = "18.2M";
  odd.companies[0].company.funding.investors = [{ name: "Fixture Fund One" }];
  odd.companies[0].people = "three people";
  odd.companies[1].company = "Sample Grid Co";
  odd.companies.push({ name: "Nowhere Power", found: false, company: { headcount: 3 } });
  odd.saved_searches = null;
  delete odd.additional_companies;
  const r = pv.checkPaste("harmonic", JSON.stringify(odd), RUN);
  assert.equal(r.ok, true, r.reason);
  const c = r.payload.companies[0];
  assert.ok(!("headcount" in c.record) && !("funding.funding_total" in c.record) && !("funding.investors" in c.record) && !c.people);
  assert.equal(c.not_mapped.company.headcount, -3);
  assert.equal(c.not_mapped.company.funding.funding_total, "18.2M");
  assert.deepEqual(c.not_mapped.company.funding.investors, [{ name: "Fixture Fund One" }]);
  assert.equal(c.not_mapped.people, "three people");
  assert.deepEqual(r.payload.companies[1], { name: "Sample Grid Co", found: true, record: {}, not_mapped: { company: "Sample Grid Co" } });
  assert.deepEqual(r.payload.companies[2], { name: "Nowhere Power", found: false, record: {}, not_mapped: { company: { headcount: 3 } } });   // not found: nothing of it is read
  assert.deepEqual([r.payload.additional_companies, r.payload.lists], [[], []]);
  // a key that would reach an object's prototype is kept as a plain field and touches nothing
  const proto = JSON.parse('{"format":"erw-harmonic-1","run_id":"' + RUN + '","pulled_on":"2026-10-07","companies":[{"name":"X Fixture","found":true,"company":{"__proto__":{"headcount":9},"headcount":4}}]}');
  const q = pv.validateHarmonic(proto, RUN);
  assert.equal(q.ok, true);
  assert.equal(q.payload.companies[0].record.headcount, 4);
  assert.equal({}.headcount, undefined);
});

test("Crunchbase: the documented fields and objects are mapped; everything else is kept as given, not mapped", () => {
  const p = C();
  assert.deepEqual([p.format, p.provider, p.label], ["erw-crunchbase-1", "crunchbase", "Crunchbase"]);
  assert.equal("not_mapped" in p, false);
  const c = p.companies[0];
  assert.deepEqual(c.record.identifier, { value: "Example Storage", permalink: "example-storage-fixture", entity_def_id: "organization" });
  assert.deepEqual(c.record.funding_total, { value: 18000000, currency: "USD", value_usd: 18000000 });
  assert.deepEqual(c.record.founded_on, { value: "2018-01-01", precision: "year" });
  assert.equal(c.record.num_employees_enum, "c_00011_00050");
  assert.deepEqual(c.record.location_identifiers.map((x) => x.value), ["Austin", "Texas", "United States"]);
  assert.ok(!("valuation" in c.record), "a money field that is not Crunchbase's money object is not mapped");
  assert.equal(c.record.valuation_date, "2025-03-14");
  assert.deepEqual(c.not_mapped, { organization: { valuation: "sixty million", fixture_undocumented_field: 3 }, cards: { fixture_card: [{ identifier: { value: "kept as given" } }] } });
  assert.equal(c.people.length, 2);
  assert.deepEqual(c.people[0].record, { identifier: { value: "A. Fixture" }, primary_job_title: "Fixture title" });
  assert.equal(c.rounds.length, 2);
  assert.deepEqual(c.rounds[1].record.money_raised, { value: 5000000, currency: "EUR" });
  assert.deepEqual(p.companies[1], { name: "Sample Grid Co", found: false, record: {} });
  assert.deepEqual(p.additional_companies[0].record, { identifier: { value: "Crunchbase Fixture Later LLC" }, num_funding_rounds: 1 });
  assert.deepEqual(p.lists, []);
  const bad = (f, re) => { const a = crunchbaseAnswer(); f(a); const r = readAs("crunchbase", JSON.stringify(a), RUN); assert.equal(r.ok, false); assert.match(r.reason, re); };
  bad((a) => { a.run_id = "another-run"; }, /"run_id" is not the run/);
  bad((a) => { a.companies[0].found = 1; }, /found is required/);
  bad((a) => { a.additional_companies = {}; }, /"additional_companies" must be a list/);
  // an object with a key its schema does not have is kept whole, not mapped in part
  const odd = crunchbaseAnswer();
  odd.companies[0].organization.funding_total = { value: 18000000, currency: "USD", value_usd: 18000000, fixture_extra: true };
  odd.companies[0].organization.founder_identifiers = [{ value: "A. Fixture" }, { fixture: "no name" }];
  odd.companies[0].organization.founded_on = { value: "2018", precision: "year" };
  const r = readAs("crunchbase", JSON.stringify(odd), RUN).payload.companies[0];
  assert.ok(!("funding_total" in r.record) && !("founder_identifiers" in r.record) && !("founded_on" in r.record));
  assert.deepEqual(r.not_mapped.organization.funding_total, { value: 18000000, currency: "USD", value_usd: 18000000, fixture_extra: true });
  assert.deepEqual(r.not_mapped.organization.founder_identifiers, [{ value: "A. Fixture" }, { fixture: "no name" }]);
});

// ---- the run's facts
const T0 = "2026-10-06T15:00:00+00:00";
const pbPayload = () => pb.validatePitchbook(fixtureAnswer(), DONE, 2026).payload;
const hText = JSON.stringify(harmonicAnswer()), cText = JSON.stringify(crunchbaseAnswer());
const runWith = (...ids) => ({
  pitchbook: ids.includes("pitchbook") ? pbPayload() : null, pitchbook_received_at: ids.includes("pitchbook") ? T0 : null,
  providers: [
    ...(ids.includes("pitchbook+hash") ? [{ provider: "pitchbook", format: "erw-pitchbook-1", pasted_at: "2026-10-06T15:00:01+00:00", pasted_sha256: "a".repeat(64), payload: null }] : []),
    ...(ids.includes("harmonic") ? [{ provider: "harmonic", format: "erw-harmonic-1", pasted_at: "2026-10-07T09:00:00+00:00", pasted_sha256: sha(hText), payload: H() }] : []),
    ...(ids.includes("crunchbase") ? [{ provider: "crunchbase", format: "erw-crunchbase-1", pasted_at: "2026-10-07T10:00:00+00:00", pasted_sha256: sha(cText), payload: C() }] : []),
  ],
});

test("a run written before this session holds PitchBook's answer and no provider field: it reads as PitchBook's", () => {
  const old = { pitchbook: pbPayload(), pitchbook_received_at: T0 };            // no "providers" at all, as every stored run is
  const held = pv.heldOf(old);
  assert.equal(held.length, 1);
  assert.deepEqual([held[0].provider, held[0].format, held[0].pasted_at, held[0].sha256], ["pitchbook", "erw-pitchbook-1", T0, null]);
  assert.deepEqual(pv.heldOf({ pitchbook: null, pitchbook_received_at: null, providers: null }), []);
  assert.deepEqual(pv.heldOf({}), []);
  const facts = pv.factsFor(held, "example storage, inc");
  // the figures and their words are the ones the page has shown since session 135
  assert.deepEqual(facts.map((f) => `${f.label}: ${f.value}`), ["Total raised: USD 18 million", "Last round: Series A, Mar 2025, USD 12.5 million", "Financing status: Venture Capital-Backed",
    "Headquarters: Austin, TX", "Founded: 2019", "Employees: 42", "Founders: A. Fixture, C. Fixture", "Investors: Fixture Fund One, Fixture Fund Two"]);
  assert.ok(facts.every((f) => f.provider === "pitchbook" && f.format === "erw-pitchbook-1" && f.pasted_at === T0 && f.sha256 === null));
  assert.equal(pv.disagreements(facts).size, 0);
  assert.deepEqual(pv.factsFor(held, "Sample Grid Co"), []);                    // not found: no figure
  // once the hash of the pasted text is held for it, the same answer carries it
  const now = pv.heldOf(runWith("pitchbook", "pitchbook+hash"))[0];
  assert.deepEqual([now.pasted_at, now.sha256], ["2026-10-06T15:00:01+00:00", "a".repeat(64)]);
});

test("every fact a provider adds carries the provider, the format, the time pasted and the hash of the pasted text", () => {
  const held = pv.heldOf(runWith("pitchbook", "harmonic", "crunchbase"));
  assert.deepEqual(held.map((h) => h.provider), ["pitchbook", "harmonic", "crunchbase"]);
  const facts = pv.factsFor(held, "Example Storage Inc.");
  assert.ok(facts.length >= 30, String(facts.length));
  for (const f of facts) {
    assert.ok(pv.isProviderId(f.provider) && f.format === pv.PROVIDERS[f.provider].format && typeof f.pasted_at === "string" && f.pasted_at && f.label && f.value && f.field, JSON.stringify(f));
    if (f.provider !== "pitchbook") assert.match(f.sha256, /^[0-9a-f]{64}$/);
  }
  assert.equal(facts.find((f) => f.provider === "harmonic").sha256, sha(hText));
  assert.equal(facts.find((f) => f.provider === "crunchbase").sha256, sha(cText));
  const by = (id) => Object.fromEntries(facts.filter((f) => f.provider === id).map((f) => [f.fact, f.value]));
  assert.deepEqual(by("harmonic"), {
    legal_name: "Example Storage, Inc.", total_raised: "18,200,000", last_round: "fixture round type, 14 Mar 2025, 12,500,000", last_round_leads: "Fixture Fund One",
    post_valuation: "USD 61 million", valuation: "USD 61 million", ownership_status: "fixture ownership", hq: "Austin, Texas, United States", founded_year: "2019", employees: "42",
    founders: "A. Fixture, C. Fixture", people: "A. Fixture (Co-Founder and Chief Executive), C. Fixture (Cofounder), D. Fixture (Head of Sales)", investors: "Fixture Fund One, Fixture Fund Two",
    description: "Fixture description from the second provider.", website: "https://www.example.com", rounds: "2",
  });
  assert.deepEqual(by("crunchbase"), {
    legal_name: "Example Storage, Inc.", total_raised: "USD 18 million", last_round: "series_a, 14 Mar 2025, USD 12.5 million", last_round_leads: "Fixture Fund One",
    funding_stage: "early_stage_venture", status: "operating", hq: "Austin, Texas, United States", founded_year: "2018", employees: "11 to 50", founders: "A. Fixture, C. Fixture",
    people: "A. Fixture (Fixture title), C. Fixture", top_investors: "Fixture Fund One, Fixture Fund Two", description: "Fixture description from the third provider.", website: "https://www.example.com",
    rounds: "2", profile: "https://www.example.com/fixture-profile",
  });
  // the order is the facts', then the providers': the same fact of three providers stands together
  const raised = facts.filter((f) => f.fact === "total_raised");
  assert.deepEqual(raised.map((f) => [f.provider, f.value]), [["pitchbook", "USD 18 million"], ["harmonic", "18,200,000"], ["crunchbase", "USD 18 million"]]);
  assert.match(raised[1].note, /does not state the currency/);
  const hover = pv.hoverOf(raised[1]);
  for (const w of ["Figures as returned from Harmonic through the user's own account; not checked by the ERW.", pv.TERMS.harmonic, "Format erw-harmonic-1.", "Pasted 7 Oct 2026, 09:00 UTC.", `Hash of the pasted text: ${sha(hText).slice(0, 12)}.`]) assert.ok(hover.includes(w), w);
  assert.ok(pv.hoverOf(raised[0]).includes("Hash of the pasted text: not held."));
});

test("where two providers give the same fact differently both are kept and the fact is marked; none is averaged, preferred or dropped", () => {
  const facts = pv.factsFor(pv.heldOf(runWith("pitchbook", "harmonic", "crunchbase")), "Example Storage Inc.");
  const marked = pv.disagreements(facts);
  // total raised: 18.0, 18.2 and 18.0 million. Headquarters: "Austin, TX" against "Austin, Texas, United States". Founded: 2019, 2019, 2018.
  // The last round's date is March 2025 for all three (to the month PitchBook gives) and its amount the same: not marked.
  // 42 employees is inside Crunchbase's range of 11 to 50: not marked. The founders are the same two names: not marked.
  assert.deepEqual([...marked].sort(), ["founded_year", "hq", "total_raised"]);
  for (const id of marked) assert.equal(facts.filter((f) => f.fact === id).length, 3, `${id}: a value was dropped`);
  assert.deepEqual(facts.filter((f) => f.fact === "founded_year").map((f) => f.value), ["2019", "2019", "2018"]);
  assert.ok(!facts.some((f) => /18\.1|18,100,000|2018\.6/.test(f.value)), "no value is an average of two");
  // two providers alone
  const two = pv.factsFor(pv.heldOf(runWith("pitchbook", "crunchbase")), "Example Storage Inc.");
  assert.deepEqual([...pv.disagreements(two)].sort(), ["founded_year", "hq"]);
  // a company one provider found and another did not: the one that found it gives its facts, nothing is marked
  const grid = pv.factsFor(pv.heldOf(runWith("pitchbook", "harmonic", "crunchbase")), "Sample Grid Co");
  assert.deepEqual(grid.map((f) => [f.provider, f.fact, f.value]), [["harmonic", "hq", "Reno, Nevada, United States"], ["harmonic", "employees", "8"]]);
  assert.equal(pv.disagreements(grid).size, 0);
  // how two values are compared
  assert.equal(pv.differs({ k: "money", v: 18e6 }, { k: "money", v: 18e6 + 0.2 }), false);
  assert.equal(pv.differs({ k: "money", v: 18e6 }, { k: "money", v: 18e6 + 1 }), true);
  assert.equal(pv.differs({ k: "count", v: 51 }, { k: "range", lo: 11, hi: 50 }), true);
  assert.equal(pv.differs({ k: "range", lo: 10001, hi: null }, { k: "count", v: 250000 }), false);
  assert.equal(pv.differs({ k: "text", v: "Austin, TX" }, { k: "text", v: "austin tx" }), false);
  assert.equal(pv.differs({ k: "names", v: ["a fixture"] }, { k: "names", v: ["a fixture", "c fixture"] }), true);
  assert.equal(pv.differs({ k: "round", date: "2025-03", amount: 12.5e6 }, { k: "round", date: "2025-03-14", amount: null }), false);
  assert.equal(pv.differs({ k: "round", date: "2025-03", amount: 12.5e6 }, { k: "round", date: "2025-04-01", amount: 12.5e6 }), true);
  assert.equal(pv.differs({ k: "round", date: "2025-03", amount: 12.5e6 }, { k: "round", date: "2025-03-14", amount: 13e6 }), true);
  assert.equal(pv.differs({ k: "year", v: 2019 }, { k: "text", v: "2019" }), null);
  assert.equal(pv.differs(undefined, { k: "year", v: 2019 }), null);
});

test("the stamp of a PitchBook answer is recorded only for the text that reads as the stored answer, whatever the order of its keys", () => {
  const stored = pbPayload();
  const shuffled = Object.fromEntries(Object.entries(stored).reverse().map(([k, v]) => [k, Array.isArray(v) ? v.map((c) => Object.fromEntries(Object.entries(c).reverse())) : v]));
  assert.notEqual(JSON.stringify(stored), JSON.stringify(shuffled));              // a database hands keys back in its own order
  assert.equal(pv.sameJson(stored, shuffled), true);
  assert.equal(pv.sameJson(stored, pv.checkPaste("pitchbook", JSON.stringify(fixtureAnswer()), DONE, 2026).payload), true);
  const other = pbPayload();
  other.companies[0].total_raised_usd_m = 18.5;
  assert.equal(pv.sameJson(stored, other), false);
  assert.equal(pv.sameJson(stored, null), false);
  assert.equal(pv.sameJson([1, 2], [2, 1]), false);                                // the order of a list is part of it
});

test("the two lists of providers say the same: the site's and the server's (warehouse/thesis/providers.py)", () => {
  const py = read("warehouse", "thesis", "providers.py");
  const flat = py.replace(/"\s*\n\s*"/g, "").replace(/\\"/g, '"');
  for (const p of pv.providerList()) {
    assert.ok(py.includes(`"${p.id}", "${p.label}", "${p.format}"`), `${p.id}: id, label and format`);
    const own = p.terms.split(" not published, redistributed or kept in the public warehouse.")[1].trim();
    assert.ok(own.length > 40 && flat.includes(own), `${p.id}: the provider's own terms sentence`);
    assert.ok(p.terms.startsWith(`${p.label} figures here are your own licensed copy: brought by you from your own account, shown to you, and not published, redistributed or kept in the public warehouse.`));
  }
  assert.ok(py.includes("your own licensed copy: brought by you from your own account, shown to you, and not"));
  // session 158: the providers whose answers are not kept, and the plain words, are the same on both sides
  const held = /^NOT_KEPT\s*=\s*\{([^}]*)\}/m.exec(py);
  assert.ok(held, "warehouse/thesis/providers.py holds no NOT_KEPT");
  assert.deepEqual(Object.fromEntries([...held[1].matchAll(/"([a-z]+)"\s*:\s*"([^"]*)"/g)].map((m) => [m[1], m[2]])), pv.NOT_KEPT);
  assert.ok(/^def kept\(provider_id\):/m.test(py));
  assert.ok(read("warehouse", "thesis", "run.py").includes("FORMAT = pv.PITCHBOOK.format"));
});

test("every mapped field names the page of documentation it rests on, and the method note lists it", () => {
  const note = read("docs", "methods", "thesis_builder.md");
  const groups = { HARMONIC_COMPANY: "H", HARMONIC_ROUND: "H", HARMONIC_ROUND_INVESTOR: "H", HARMONIC_PERSON: "H", HARMONIC_EXPERIENCE: "H", HARMONIC_INVESTOR: "H", CRUNCHBASE_ORGANIZATION: "C", CRUNCHBASE_ROUND: "C", CRUNCHBASE_PERSON: "C" };
  let fields = 0;
  for (const [g, letter] of Object.entries(groups)) {
    for (const [field, kind, doc] of pv[g]) {
      fields += 1;
      assert.ok(pv.DOCS[doc] && doc.startsWith(letter), `${g}.${field}: ${doc}`);
      assert.ok(typeof kind === "string" && kind);
      assert.ok(note.includes("`" + field + "`"), `the method note does not list ${g}.${field}`);
    }
  }
  assert.equal(fields, 31 + 9 + 4 + 7 + 6 + 10 + 29 + 10 + 7);
  for (const d of Object.values(pv.DOCS)) {
    assert.match(d.sha256, /^[0-9a-f]{64}$/);
    assert.match(d.retrieved, /^2026-10-08T00:\d\d:\d\dZ$/);
    assert.ok(note.includes(d.url) && note.includes(d.sha256), `the method note does not hold ${d.id}: its address and hash`);
  }
  for (const p of pv.providerList()) assert.ok(note.includes(p.format) && note.includes(p.terms.split(": \"")[1]?.slice(0, 60) ?? "was not read"), p.id);
});

test("no em dash in the new files, and no provider, connector or model is called from them", () => {
  const files = [["site", "lib", "thesis", "providers.ts"], ["site", "scripts", "test-thesis-providers.mjs"], ["site", "scripts", "thesis-providers-fixtures.mjs"], ["warehouse", "thesis", "providers.py"],
    ["site", "components", "thesis", "ProviderBlock.tsx"], ["site", "app", "api", "thesis", "provider", "route.ts"], ["warehouse", "supabase", "migrations", "025_thesis_providers.sql"]];
  for (const f of files) {
    const text = read(...f);
    assert.ok(!text.includes(EM), f.join("/"));
  }
  for (const f of [["site", "lib", "thesis", "providers.ts"], ["warehouse", "thesis", "providers.py"]]) {
    const text = read(...f);
    for (const w of ["fetch(", "http.request", "urllib", "requests.", "anthropic", "messages.create", "mcp.api.harmonic.ai", "mcp.crunchbase.com", "API_KEY", "process.env", "os.environ"]) assert.ok(!text.includes(w), `${f.join("/")} holds ${w}`);
  }
});
console.log(`${n} tests pass`);
