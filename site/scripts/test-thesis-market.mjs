// Energy Research Warehouse (ERW) site, session 169: Thesis Builder (/thesis), the report of the market research and
// its connector tabs (lib/thesis/view.ts): the tabs, which report is drawn the new way, and what a pasted PitchBook
// answer puts in each connector tab.
//
//   node --import ./scripts/alias-register.mjs scripts/test-thesis-market.mjs
//
// Exit 1 on a failure. Nothing is requested. The answers are the stand-in's made-up ones (scripts/thesis-stub.mjs).
import assert from "node:assert/strict";
import * as pb from "../lib/thesis/pitchbook.ts";
import * as v from "../lib/thesis/view.ts";
import { MARKET_ANSWER, fixtureReport, marketReport } from "./thesis-stub.mjs";

let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };

test("the tabs: the market research's, then the connector tabs; every earlier address still opens its tab", () => {
  assert.deepEqual(v.TABS.map((t) => t.id), ["scope", "trends", "capital", "policy", "risks", "incumbents", "timing", "references", "landscape", "funnel", "pipeline", "success", "investors"]);
  for (const id of ["scope", "trends", "landscape", "funnel", "pipeline", "capital", "incumbents", "risks", "policy"]) assert.equal(v.choiceOf({ run: "x", tab: id }).tab, id);
  assert.equal(v.CONNECTOR_NOTE, "Connect PitchBook or Harmonic to fill this");
});

test("a report of version 2 is the market research; one written before is not", () => {
  assert.equal(v.isMarket(marketReport()), true);
  assert.equal(v.isMarket(fixtureReport()), false);
  assert.equal(v.isMarket(null), false);
});

test("the columns: the owner's for companies, the report's own when it names them", () => {
  assert.deepEqual(v.columnsOf(marketReport(), "landscape"), ["Company", "What it sells", "Founders", "Stage", "Raised", "Investors", "Founded", "Location", "Signal", "Source"]);
  assert.deepEqual(v.columnsOf(fixtureReport(), "investors"), v.CONNECTOR_COLUMNS.investors);
  for (const id of v.CONNECTOR_IDS) assert.ok(v.columnsOf(marketReport(), id).length >= 5, id);
});

test("no answer, or an answer with no company found: the tab is the placeholder", () => {
  for (const id of v.CONNECTOR_IDS) {
    assert.equal(v.connectorRows(null, id), null);
    assert.equal(v.connectorRows({ ...MARKET_ANSWER, additional_companies: [{ name: "x", found: false }] }, id), null);
  }
});

test("a pasted PitchBook answer fills each connector tab, every row labeled PitchBook's", () => {
  const land = v.connectorRows(MARKET_ANSWER, "landscape");
  assert.deepEqual(land[0], ["Fixture Seed Co", "Fixture sensors", "A. Fixture", "Seed", "USD 4 million", "Fund One, Fund Two", "2021", "Austin, TX", "Seed, Mar 2025, USD 3 million", "PitchBook, pulled 9 Oct 2026"]);
  assert.equal(land.length, 2);                                        // a company PitchBook did not find is not a row
  assert.deepEqual(v.connectorRows(MARKET_ANSWER, "pipeline").map((r) => r[0]), ["Fixture Seed Co"]);      // early stage, not exited
  assert.deepEqual(v.connectorRows(MARKET_ANSWER, "success"), [["Fixture Exit Co", "Fixture software", "Merger/Acquisition", "Jun 2024", "USD 20 million", "Fund One", "PitchBook, pulled 9 Oct 2026"]]);
  assert.deepEqual(v.connectorRows(MARKET_ANSWER, "investors"), [
    ["Fund One", "2: Fixture Seed Co, Fixture Exit Co", "Fixture Seed Co", "Mar 2025", "PitchBook, pulled 9 Oct 2026"],
    ["Fund Two", "1: Fixture Seed Co", "", "Mar 2025", "PitchBook, pulled 9 Oct 2026"]]);
  const funnel = v.connectorRows(MARKET_ANSWER, "funnel");
  assert.deepEqual(funnel[0], ["Fixture Seed Co", "Fixture sensors", "Seed", "Sourced", "2026-10-09", "PitchBook", "", "", "keyword: fixture", "PitchBook, pulled 9 Oct 2026"]);
  for (const id of v.CONNECTOR_IDS) for (const row of v.connectorRows(MARKET_ANSWER, id)) assert.equal(row.length, v.columnsOf(marketReport(), id).length, `${id}: a row has a cell per column`);
});

test("a company asked for and found again under PitchBook's own name is one row", () => {
  const twice = { ...MARKET_ANSWER, companies: [{ name: "Fixture Seed", found: true, pitchbook_name: "Fixture Seed Co" }] };
  assert.equal(v.connectorRows(twice, "landscape").length, 2);
});

test("a paste for a run that names no company passes the PitchBook gate as before, and then fills the tabs", () => {
  const { label, received_note, ...raw } = MARKET_ANSWER;      // what a Claude chat answers: no label, no note
  assert.ok(label && received_note);
  const r = pb.validatePitchbook(raw, "fixture-market-pb", 2026);
  assert.equal(r.ok, true, r.reason);
  assert.equal(r.payload.companies.length, 0);
  assert.equal(v.connectorRows(r.payload, "landscape").length, 2);
});

console.log(`${n} tests pass`);
