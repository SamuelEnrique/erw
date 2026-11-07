// Energy Research Warehouse (ERW) site, sessions 3304 to 3306 (chain 200): the company pages' pure rules
// (lib/companydb.ts): the query an address asks for, the filters, the pages, the years in spans, the CSVs and the
// readers. Every company and figure below is written for the test and is no company's.
//
//   node --import ./scripts/alias-register.mjs scripts/test-companies.mjs
//
// Exit 1 on a failure. Nothing is read from site/data, nothing is written and nothing is requested.
import assert from "node:assert/strict";
import * as db from "../lib/companydb.ts";

let n = 0;
const t = (name, fn) => { fn(); n += 1; console.log(`ok ${n} ${name}`); };

const IX = {
  built: "2026-11-06T19:00:00Z", method: "docs/methods/companies.md", tables: ["eia860m_operating_generators", "energy_deals", "policy_actions"],
  held_tables: ["energy_deals"], held_links: { energy_deals: 3 }, held_only: 1, n_directory: 4, n_listed: 3,
  sources: { eia860m_operating_generators: "eia:860m test", policy_actions: "federalregister test" },
  columns: ["id", "name", "kind", "segment", "hq_state", "states", "grids", "n_plants", "plants_mw", "planned_mw", "n_queue", "queue_mw", "n_reactors", "n_policy_actions", "footprint_mw", "n_links", "aka", "first_seen", "last_seen"],
  link_columns: [], rules: ["eia_id", "reviewed_alias", "anchored_name", "name", "company_word"],
  confidence: { eia_id: 1, reviewed_alias: 0.95, anchored_name: 0.9, name: 0.85, company_word: 0.7 },
  kinds: { utility: 1, IPP: 1, regulator: 1 }, segments: { gas: 1, solar: 1 }, states: { TX: 2, CA: 1 }, grids: { ERCOT: 2, CAISO: 1 },
  rows: [
    ["eia-1", "Alpha Power Co", "utility", "gas", "TX", "TX;CA", "ERCOT;CAISO", 3, 900, 50, 0, 0, 0, 0, 950, 10, "Alpha Power | Alpha Pwr", "1990-01-01", "2026-01-01"],
    ["eia-2", "Beta Solar LLC", "IPP", "solar", "", "TX", "ERCOT", 1, 100, 0, 2, 300, 0, 0, 400, 4, "", "2020-01-01", "2025-06-01"],
    ["energy-department", "Energy Department", "regulator", "", "", "", "", 0, 0, 0, 0, 0, 0, 12, 0, 12, "DOE", "2025-10-01", "2026-11-01"],
  ],
};
const rows = db.indexRows(IX);

t("index rows carry their columns", () => {
  assert.equal(rows[0].name, "Alpha Power Co");
  assert.equal(rows[1].queue_mw, 300);
  assert.equal(rows[0].n_deals, undefined);   // the held table's figure is not in the index
});

t("a query keeps only values the index holds", () => {
  const q = db.queryOf({ q: " alpha ", kind: "utility", state: "tx", grid: "PJM", has: "deals", page: "2" }, IX);
  assert.deepEqual(q, { q: "alpha", kind: "utility", segment: "", state: "TX", grid: "", has: "", page: 2 });
  assert.equal(db.queryOf({ has: "queue", page: "-4" }, IX).page, 1);
  assert.equal(db.queryOf({ has: "queue" }, IX).has, "queue");
  assert.equal(db.queryOf({ has: "facilities" }, IX).has, "");   // a held table's filter is no filter
});

t("the filters", () => {
  assert.deepEqual(db.filterRows(rows, { ...db.NO_QUERY, state: "TX" }).map((r) => r.id), ["eia-1", "eia-2"]);
  assert.deepEqual(db.filterRows(rows, { ...db.NO_QUERY, has: "queue" }).map((r) => r.id), ["eia-2"]);
  assert.deepEqual(db.filterRows(rows, { ...db.NO_QUERY, has: "policy" }).map((r) => r.id), ["energy-department"]);
  assert.deepEqual(db.filterRows(rows, { ...db.NO_QUERY, q: "doe" }).map((r) => r.id), ["energy-department"]);   // another name
  assert.deepEqual(db.filterRows(rows, { ...db.NO_QUERY, q: "alpha pwr" }).map((r) => r.id), ["eia-1"]);
  assert.deepEqual(db.filterRows(rows, { ...db.NO_QUERY, q: "alpha zeta" }).map((r) => r.id), []);
  assert.deepEqual(db.filterRows(rows, { ...db.NO_QUERY, grid: "CAISO", kind: "utility" }).map((r) => r.id), ["eia-1"]);
});

t("the pages", () => {
  const xs = Array.from({ length: 120 }, (_, i) => i);
  assert.deepEqual(db.pageOf(xs, 1).rows.length, 50);
  assert.deepEqual(db.pageOf(xs, 3).rows, xs.slice(100));
  assert.equal(db.pageOf(xs, 9).page, 3);
  assert.equal(db.pageOf([], 1).pages, 1);
});

t("the address of a query", () => {
  assert.equal(db.hrefOf("/companies", db.NO_QUERY), "/companies");
  assert.equal(db.hrefOf("/companies", { ...db.NO_QUERY, kind: "IPP", q: "a b" }, { page: 2 }), "/companies?q=a+b&kind=IPP&page=2");
});

t("years one a year, and in spans when they are many", () => {
  const few = db.yearGroups([["2020", 1, 0, 0], ["2022", 2, 3, 4]]);
  assert.deepEqual(few.map((g) => g.label), ["2020", "2021", "2022"]);
  assert.deepEqual([few[2].operating, few[2].planned, few[2].queue], [2, 3, 4]);
  const many = db.yearGroups([["1951", 10, 0, 0], ["1999", 5, 0, 0], ["2026", 1, 2, 3]]);
  assert.equal(many[0].label, "1950");
  assert.equal(many[0].sub, "to 54");
  assert.equal(many[0].operating, 10);
  assert.equal(many[many.length - 1].label, "2025");
  assert.equal(many[many.length - 1].sub, "to 26");
  assert.equal(few[0].sub, undefined);
  assert.equal(many.reduce((s, g) => s + g.operating, 0), 16);
  assert.deepEqual(db.yearGroups([]), []);
});

const C = {
  id: "eia-1", entity_id: "company:eia-1", name: "Alpha Power Co", kind: "utility", kind_basis: "x", segment: "gas", segment_basis: "most MW",
  parent: "", parent_id: "", parent_basis: "", eia_utility_id: "1", hq_state: "TX", hq_basis: "y", states: ["TX"], grids: ["ERCOT"],
  first_seen: "1990-01-01", last_seen: "2026-01-01", figures: { plants_mw: 900 }, fuel: { gas: 900 }, years: [], quarters: [],
  held: { energy_deals: 2 }, min_confidence: 1,
  names: [],
  links: [["abc", 0, "eia860:9:1", "operator", "", 0, "900", "", "1990-01-01", "gas", "TX", "ERCOT", "plant 9"],
          ["def", 2, "federalregister:1", "agency", "Alpha, the \"utility\"", 3, "", "", "2026-01-01", "", "TX", "", "notice"]],
};

t("a company's links name their table and rule", () => {
  const ls = db.linksOf(C, IX);
  assert.equal(ls[0].table, "eia860m_operating_generators");
  assert.equal(ls[0].name, "Alpha Power Co");   // "" is the company's own name
  assert.equal(ls[1].rule, "name");
  assert.equal(ls[1].confidence, 0.85);
});

t("a company's CSV: provenance, the held count, quoted cells", () => {
  const csv = db.linksCsv(C, db.linksOf(C, IX), IX, "https://x/companies/eia-1/rows");
  const lines = csv.split("\n");
  assert.ok(lines[0].startsWith("# Energy Research Warehouse (ERW): Alpha Power Co (company:eia-1)"));
  assert.ok(csv.includes("# Held, not in this file (license needed: the publishers ask for permission): 2 rows of energy_deals."));
  assert.ok(csv.includes("# Source of eia860m_operating_generators: eia:860m test"));
  const head = lines.findIndex((l) => l.startsWith("company_id,"));
  assert.equal(lines[head], db.LINK_HEAD.join(","));
  assert.ok(lines[head + 2].includes('"Alpha, the ""utility"""'));
  assert.equal(lines.filter((l) => l && !l.startsWith("#")).length, 3);
});

t("the index CSV says its filters and the hold", () => {
  const q = { ...db.NO_QUERY, state: "TX" };
  const csv = db.indexCsv(db.filterRows(rows, q), IX, q, "https://x/companies/rows?state=TX");
  assert.ok(csv.includes("# Filters: q=(any), kind=(any), segment=(any), state=TX, grid=(any), has=(any)."));
  assert.ok(csv.includes("# Held (license needed): energy_deals; 1 companies named only in them are not listed"));
  assert.equal(csv.split("\n").filter((l) => l && !l.startsWith("#")).length, 3);
});

t("the readers", () => {
  const py = db.reader("py", "https://x/rows", "a test", ["mw"]);
  assert.ok(py.includes('URL = "https://x/rows"'));
  assert.ok(py.includes('rows["mw"] = pd.to_numeric(rows["mw"], errors="coerce")'));
  const st = db.reader("do", "https://x/rows", "a test", ["mw", "usd"]);
  assert.ok(st.includes("destring mw, replace force\n\ndestring usd, replace force"));
  assert.ok(!st.includes("///"));   // no line continuation
  // one empty line between commands outside the loop, none inside it
  const loop = st.slice(st.indexOf("while r(eof)"), st.indexOf("}") + 1);
  assert.ok(!loop.includes("\n\n"));
});

console.log(`${n} tests passed`);
