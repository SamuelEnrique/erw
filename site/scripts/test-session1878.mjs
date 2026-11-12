// Energy Research Warehouse (ERW) site, session 1878: the company database's and the capital view's faults of 12
// November 2026 (docs/reviews/companies-faults-2026-11-11.md), the pure part: lib/companydb.ts (rows 2 to 11) and
// lib/capitalview.ts (rows 13 to 16). Every company, deal and figure below is written for the test and is no one's.
//
//   node --import ./scripts/alias-register.mjs scripts/test-session1878.mjs
//
// Each line "ok   row N: ..." names the fault row it tests. Exit 1 on a failure. Nothing is read from site/data, nothing
// is written and nothing is requested.
import assert from "node:assert/strict";
import * as db from "../lib/companydb.ts";
import * as cv from "../lib/capitalview.ts";

let n = 0, bad = 0;
const t = (name, fn) => {
  try { fn(); n += 1; console.log(`ok   ${name}`); } catch (e) { bad += 1; console.log(`FAIL ${name}: ${e.message}`); }
};

const IX = {
  built: "2026-11-06T20:16:53Z", tables: ["ercot_interconnection_queue", "nrc_power_reactors", "eia860m_operating_generators", "policy_actions"],
  held_tables: ["energy_deals"], sources: {}, rules: ["eia_id", "reviewed_alias", "anchored_name", "name", "company_word"],
  confidence: { eia_id: 1, reviewed_alias: 0.95, anchored_name: 0.9, name: 0.85, company_word: 0.7 },
  kinds: { utility: 2, IPP: 1, other: 1 }, segments: {}, states: { TX: 3, CN: 1 }, grids: {}, columns: [],
};
const L = (link, t, row, role, mw, detail, fuel = "") => [link, t, row, role, "", 0, mw, "", "2026-01-01", fuel, "TX", "", detail];
const C = {
  id: "dev-1", entity_id: "company:dev-1", name: "Gamma Developer", held: {}, quarters: [],
  links: [
    L("q1", 0, "ercot_queue:1", "interconnection_customer", "100", "Active"),
    L("q2", 0, "ercot_queue:2", "interconnection_customer", "200", "Completed"),
    L("q3", 0, "ercot_queue:3", "interconnection_customer", "50", "withdrawn"),
    L("q4", 0, "ercot_queue:4", "interconnection_customer", "25.5", "Active"),
    L("r1", 1, "nrc_reactor:1", "licensee", "1000", ""),
    L("r2", 1, "nrc_reactor:1", "parent", "1000", ""),
    L("r3", 1, "nrc_reactor:2", "operator", "900", ""),
    L("g1", 2, "eia860m:1:1", "operator", "10", "plant 1", "solar"),
    L("g2", 2, "eia860m:1:2", "operator", "20", "plant 1", "solar"),
    L("g3", 2, "eia860m:2:1", "operator", "30", "plant 2", ""),
  ],
};
const links = db.linksOf(C, IX);

t("row 2: the queue figure's hover counts the positions summed, not the table's rows", () => {
  assert.equal(db.basisOf("queue_mw", "ercot_interconnection_queue", links), "the sum of the 2 rows of 4 neither withdrawn nor completed (2 positions)");
  const live = links.filter((l) => l.table === "ercot_interconnection_queue" && !["withdrawn", "Completed"].includes(l.detail));
  assert.equal(live.reduce((s, l) => s + Number(l.mw), 0), 125.5);   // what the builder sums
});
t("row 2: reactors are counted once, over the licensee, operator and parent rows", () => {
  assert.equal(db.basisOf("n_reactors", "nrc_power_reactors", links), "a count of 2 reactors it is the licensee or operator of, over 3 rows (licensee, operator or parent)");
});
t("row 2: operating MW and a fuel's MW name their generators and plants", () => {
  assert.equal(db.basisOf("plants_mw", "eia860m_operating_generators", links), "the sum of 3 rows, one an operating generator, at 2 plants");
  assert.equal(db.basisOf("mw_solar", "eia860m_operating_generators", links), "the sum of 2 rows of operating generators whose fuel is solar");
  assert.equal(db.basisOf("mw_other", "eia860m_operating_generators", links), "the sum of 1 row of operating generators whose fuel is other");
});

t("row 3: one is one", () => {
  assert.equal(db.plural(1, "row", "rows"), "1 row");
  assert.equal(db.plural(0, "row", "rows"), "0 rows");
  assert.equal(db.plural(1234, "row", "rows"), "1,234 rows");
  assert.equal(db.leadRows(1, 1, 0), "1 public row of 1 table names it.");
  assert.equal(db.leadRows(143, 6, 2), "143 public rows of 6 tables name it; 2 held rows do too.");
  assert.equal(db.leadRows(6, 1, 1), "6 public rows of 1 table name it; 1 held row does too.");
});
t("row 3: the company CSV's held line", () => {
  const one = { ...C, held: { datacenter_facilities: 1 } };
  const csv = db.linksCsv(one, links, { built: IX.built, held_tables: ["datacenter_facilities"], sources: {} }, "https://x/rows");
  assert.ok(csv.includes(": 1 row of datacenter_facilities."), csv.split("\n")[3]);
});

t("row 4: every rule of the index has its words", () => {
  for (const r of IX.rules) assert.ok(db.RULE_WORDS[r] && db.RULE_WORDS[r] !== r, r);
  assert.equal(db.ruleWords("eia_id"), "EIA utility id");
  assert.equal(db.ruleWords("company_word"), "a company word added");
});

const ROWS = [
  { id: "eia-10", name: "Calpine Corp", states: "TX;NY", plants_mw: 0, planned_mw: 0, queue_mw: 0, n_policy_actions: 0, footprint_mw: 1045, kind: "other", segment: "", grids: "", aka: "", n_plants: 0, n_queue: 0, n_reactors: 0 },
  { id: "eia-11", name: "Calpine Corp", states: "TX", plants_mw: 0, planned_mw: 0, queue_mw: 0, n_policy_actions: 0, footprint_mw: 296, kind: "other", segment: "", grids: "", aka: "", n_plants: 0, n_queue: 0, n_reactors: 0 },
  { id: "beta-solar", name: "Beta Solar", states: "FL;TX;CA;NY;GA;AZ;CN", plants_mw: 50, planned_mw: 400, queue_mw: 20, n_policy_actions: 0, footprint_mw: 200, kind: "IPP", segment: "solar", grids: "", aka: "", n_plants: 1, n_queue: 1, n_reactors: 0 },
  { id: "agency", name: "Alpha Agency", states: "", plants_mw: 0, planned_mw: 0, queue_mw: 0, n_policy_actions: 9, footprint_mw: 0, kind: "utility", segment: "", grids: "", aka: "", n_plants: 0, n_queue: 0, n_reactors: 0 },
];

t("row 5: two rows of one name carry their ids", () => {
  const shared = db.sharedNames(ROWS);
  assert.deepEqual([...shared], ["Calpine Corp"]);
  assert.deepEqual(db.idTag("eia-10"), { text: "EIA 10", title: "EIA utility id 10" });
  assert.equal(db.idTag("edp-renewables").text, "edp-renewables");
});

t("row 6: the States cell holds every state in its hover, the count first; CN is labelled", () => {
  const c = db.statesCell("FL;TX;CA;NY;GA;AZ;CN");
  assert.equal(c.text, "FL, TX, CA ...");
  assert.equal(c.title, "7 states: FL, TX, CA, NY, GA, AZ, CN (Canada, as EIA-861 writes it)");
  assert.deepEqual(db.statesCell("TX"), { text: "TX", title: "1 state: TX" });
  assert.equal(db.statesCell("").title, "");
  assert.equal(db.stateLabel("CN", 20), "CN (Canada, as EIA-861 writes it) (20)");
  assert.equal(db.stateLabel("TX", 3), "TX (3)");
});

t("row 7: the deals frame only where a deal row names the company", () => {
  assert.equal(db.showDeals({ held: {}, quarters: [] }, true), false);
  assert.equal(db.showDeals({ held: { energy_deals: 3 }, quarters: [] }, true), true);
  assert.equal(db.showDeals({ held: {}, quarters: [] }, false), false);
  assert.equal(db.showDeals({ held: {}, quarters: [["2026Q1", 1, 0, 0]] }, false), true);
});

t("row 8: a series zero in every group is not drawn or named", () => {
  assert.deepEqual(db.liveSeries(db.yearGroups([["1970", 3372, 0, 0], ["2028", 0, 500, 0]])), ["operating", "planned"]);
  assert.deepEqual(db.liveSeries(db.yearGroups([["2023", 0, 0, 1091]])), ["queue"]);
  assert.deepEqual(db.liveSeries([]), []);
});

t("row 9: a last date after the build is a planned month", () => {
  assert.equal(db.seenLast("2029-11-01", "2026-11-06T20:16:53Z"), "2029-11-01 (planned)");
  assert.equal(db.seenLast("2026-01-01", "2026-11-06T20:16:53Z"), "2026-01-01");
  assert.equal(db.seenLast("", "2026-11-06"), "");
});

t("row 10: a fuel's share names the two figures it divides", () => {
  assert.equal(db.shareTitle("solar", 430, 9635.3), "mw_solar 430 of plants_mw 9,635 (company_directory)");
});

t("row 11: the order is read from the address, kept in it and in the download", () => {
  const q = db.queryOf({ sort: "planned" }, IX);
  assert.equal(q.sort, "planned");
  assert.equal(db.queryOf({ sort: "nonsense" }, IX).sort, "footprint");
  assert.equal(db.queryOf({}, IX).sort, "footprint");
  assert.equal(db.hrefOf("/companies", q), "/companies?sort=planned");
  assert.equal(db.hrefOf("/companies/rows", { ...q, kind: "IPP" }), "/companies/rows?kind=IPP&sort=planned");
  assert.equal(db.hrefOf("/companies", { ...q, sort: "footprint" }), "/companies");
});
t("row 11: filterRows orders by the column asked, a tie in the index's order", () => {
  const ids = (sort) => db.filterRows(ROWS, { ...db.NO_QUERY, sort }).map((r) => r.id);
  assert.deepEqual(ids("footprint"), ["eia-10", "eia-11", "beta-solar", "agency"]);
  assert.deepEqual(ids("planned"), ["beta-solar", "eia-10", "eia-11", "agency"]);
  assert.deepEqual(ids("operating"), ["beta-solar", "eia-10", "eia-11", "agency"]);
  assert.deepEqual(ids("queue"), ["beta-solar", "eia-10", "eia-11", "agency"]);
  assert.deepEqual(ids("policy"), ["agency", "eia-10", "eia-11", "beta-solar"]);
  assert.deepEqual(ids("name"), ["agency", "beta-solar", "eia-10", "eia-11"]);
  assert.deepEqual(db.filterRows(ROWS, { ...db.NO_QUERY, sort: "planned", state: "TX" }).map((r) => r.id), ["beta-solar", "eia-10", "eia-11"]);
  assert.equal(ROWS[0].id, "eia-10");   // the index itself is not reordered
});
t("row 11: the index CSV names its order", () => {
  const q = { ...db.NO_QUERY, sort: "queue" };
  const csv = db.indexCsv([], { built: IX.built, columns: ["id"], held_tables: [], held_only: 0 }, q, "https://x");
  assert.ok(csv.includes("# Order: sort=queue, the most ERCOT queue MW first."));
});

t("row 13: four types, four colors", () => {
  const tones = ["project_finance", "m_and_a", "debt", "equity_raise"].map((_, i) => cv.toneOf(i));
  assert.equal(new Set(tones).size, 4);
  assert.equal(tones[0], "accent");
});

const Q = { quarter: "2026Q1", m_and_a: { rows: 2, usd: 1.25e9, usd_rows: 1, no_usd: 1, mw: 0 }, debt: { rows: 1, usd: 3e7, usd_rows: 1, no_usd: 0, mw: 0 } };
t("row 14: a type absent from a quarter is no bar and its card says none; the counts are in the card", () => {
  const b = cv.quarterBars(Q, ["project_finance", "m_and_a", "debt"], { project_finance: "Project finance", m_and_a: "M&A", debt: "Debt" });
  assert.deepEqual(b.values, [null, 1.25, 0.03]);
  assert.deepEqual(b.cards, ["none", "1.3 USD billion; 2 deals, 1 with no USD", "0.03 USD billion; 1 deal, 0 with no USD"]);
  assert.equal(b.title, "2026Q1: Project finance none; M&A 2 deals, 1 with no USD; Debt 1 deal, 0 with no USD");
});

t("row 15: a deal under USD 50 million is not written 0 billion; a missing seller says not named", () => {
  assert.equal(cv.bn(3e7), "0.03");
  assert.equal(cv.bn(2e6), "0.002");
  assert.equal(cv.bn(0), "0");
  assert.equal(cv.bn(1.25e9), "1.3");
  assert.equal(cv.bn(4.56e8), "0.46");
  assert.equal(cv.named(""), "not named");
  assert.equal(cv.named("Beta Power"), "Beta Power");
});

console.log(bad ? `FAILED: ${bad} of ${n + bad}` : `${n} of ${n} passed`);
process.exit(bad ? 1 : 0);
