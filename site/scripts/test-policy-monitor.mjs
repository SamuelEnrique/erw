// Session 3060 (chain 166): the policy monitor's view (lib/policymonitor.ts) and its data file (data/policy/monitor.json,
// built by warehouse/policy/monitor_site.py). No build, no network.
//   node --import ./scripts/alias-register.mjs scripts/test-policy-monitor.mjs
import { readFileSync } from "node:fs";

const M = await import("../lib/policymonitor.ts");
const file = JSON.parse(readFileSync(new URL("../data/policy/monitor.json", import.meta.url), "utf-8"));
let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };

const R = (o) => ({ id: "x", date: "2026-10-01", first: "2026-10-01", body: "FERC", instrument: "notice", title: "t", status: "issued", n: 1, bears_on: { table: "policy_actions", page: "/policy" }, ...o });
const rows = [
  R({ id: "a", date: "2026-11-01", body: "FERC", instrument: "order", status: "issued", sector: "gas", significance: 7, grids: ["pjm"], states: ["PA"], next: { step: "comments due", date: "2026-12-01", words: "w" }, figure: { value: 750000, unit: "Dth/d", words: "w", event_id: "e" } }),
  R({ id: "b", date: "2026-10-15", body: "NRC", instrument: "application", status: "filed", sector: "nuclear", significance: 5, states: ["MI"] }),
  R({ id: "c", date: "2026-09-01", body: "BOEM", instrument: "lease_sale", status: "proposed", sector: "oil", significance: 3, figure: { value: 42000000, unit: "USD", words: "w", event_id: "e" } }),
  R({ id: "d", date: "2026-08-01", body: "FERC", instrument: "application", status: "filed" }),
];

// the filters
ok(M.filterRows(rows, M.NO_FILTERS).length === 4, "no filter holds every row");
ok(M.filterRows(rows, M.OPEN_FILTERS).map((r) => r.id).join() === "a,b", "the view opens at significance 5 or more");
ok(M.filterRows(rows, { ...M.NO_FILTERS, bodies: ["FERC"] }).map((r) => r.id).join() === "a,d", "by body");
ok(M.filterRows(rows, { ...M.NO_FILTERS, instruments: ["application"], statuses: ["filed"] }).map((r) => r.id).join() === "b,d", "by instrument and status");
ok(M.filterRows(rows, { ...M.NO_FILTERS, grids: ["pjm"] }).map((r) => r.id).join() === "a", "by grid");
ok(M.filterRows(rows, { ...M.NO_FILTERS, states: ["MI", "PA"] }).map((r) => r.id).join() === "a,b", "by state, any of those chosen");
ok(M.filterRows(rows, { ...M.NO_FILTERS, from: "2026-09-01", to: "2026-10-31" }).map((r) => r.id).join() === "b,c", "by date range, both ends kept");
ok(M.filterRows(rows, { ...M.NO_FILTERS, sectors: ["oil"] }).map((r) => r.id).join() === "c", "by sector");

// the sort: every column, an empty value last either way
for (const k of M.SORT_KEYS) ok(M.sortRows(rows, k, "asc").length === 4 && M.sortRows(rows, k, "desc").length === 4, `sorts on ${k}`);
ok(M.sortRows(rows, "significance", "desc").map((r) => r.id).join() === "a,b,c,d", "significance, most first, the unscored last");
ok(M.sortRows(rows, "significance", "asc").map((r) => r.id).join() === "c,b,a,d", "significance, least first, the unscored still last");
ok(M.sortRows(rows, "figure", "desc").map((r) => r.id).join() === "c,a,b,d", "figure: a row without one sorts last (then newest first)");
ok(M.sortRows(rows, "next", "asc")[0].id === "a", "the next step's date");

// the choices and the address
const o = M.options(rows);
ok(o.bodies[0].key === "FERC" && o.bodies[0].n === 2, "each choice counts its rows, most first");
ok(o.instruments.find((x) => x.key === "lease_sale").label === "Lease sale", "an instrument's words");
const f = { ...M.NO_FILTERS, bodies: ["FERC", "NRC"], grids: ["pjm"], from: "2026-09-01", minSig: 7 };
ok(JSON.stringify(M.filtersOf(Object.fromEntries(new URLSearchParams(M.hrefOf(f).split("?")[1])))) === JSON.stringify(f), "an address gives back its filters");
ok(M.hrefOf(M.OPEN_FILTERS) === "/policy?view=monitor", "the opening filters need no words in the address");
ok(M.filtersOf({ sig: "all" }).minSig === null && M.filtersOf({ from: "nonsense" }).from === "", "sig=all is every significance; a date that is no date is left");

// the CSV and the figures' words
const csv = M.toCsv(rows, "2026-11-06").trim().split("\n");
ok(csv.length === 2 + rows.length && csv[1] === M.CSV_COLS.join(","), "the CSV: a provenance line, the header, one line a row");
ok(M.figureText({ value: 42000000, unit: "USD" }) === "USD 42 million" && M.figureText({ value: 750000, unit: "Dth/d" }) === "750,000 Dth/d", "a figure in its unit");

// session 3061: the calendar and the keys
const withSteps = [
  R({ id: "p", date: "2026-11-03", steps: [{ kind: "comments_due", date: "2026-11-20", words: "w", event_id: "federalregister:9" }, { kind: "effective", date: "2027-01-01", words: "w", event_id: "federalregister:9" }] }),
  R({ id: "q", date: "2026-10-01", steps: [{ kind: "meeting", date: "2026-11-07", words: "w", event_id: "federalregister:8" }] }),
  R({ id: "s", date: "2026-10-29" }),
];
const c = M.calendarOf(withSteps, "2026-11-06");
ok(c.weekFrom === "2026-10-30" && c.aheadTo === "2026-12-06", "the week is the seven days to today, the month the thirty days on");
ok(c.week.map((r) => r.id).join() === "p", "the past week: records whose newest document is in it");
ok(c.ahead.map((x) => `${x.row.id}:${x.step.date}`).join() === "q:2026-11-07,p:2026-11-20", "the month ahead: every step in it, soonest first, none after it");
ok(M.stepKey(withSteps[0], withSteps[0].steps[0]) === "policycal|p|federalregister:9|comments_due|2026-11-20", "a step's key names its record, document, kind and date");
ok(M.figureKey(rows[0]) === "policyfig|a|e|750000|Dth/d" && M.figureKey(rows[1]) === "", "a figure's key; none without one");
const keys = M.keysOf({ rows: withSteps.concat(rows) });
ok(keys.length === 5 && keys.every((k) => k.key.startsWith("policycal|") || k.key.startsWith("policyfig|")), "every step and figure has its key");

// the data file the view reads
ok(file.records === file.rows.length && file.rows.length > 1000, `the file holds its ${file.records} records`);
ok(file.rows.every((r) => r.id && r.date && r.body && r.instrument && r.status && r.title && r.n >= 1 && r.bears_on?.table), "every row has its record id, date, body, instrument, status, title, documents and table");
ok(file.rows.every((r) => M.INSTRUMENT_WORDS[r.instrument] && M.STATUS_WORDS[r.status]), "every instrument and status has its words");
ok(file.rows.every((r) => !r.figure || (r.figure.words && r.figure.event_id)), "every figure has its words and its document");
ok(file.rows.every((r) => !r.next || /^\d{4}-\d{2}-\d{2}$/.test(r.next.date)), "every next step has its date");
ok(file.rows.every((r) => (r.steps ?? []).every((x) => M.KIND_WORDS[x.kind] && x.event_id && x.words)), "every step has its kind's words, its document and its words");
ok(file.rows.every((r) => !r.next || (r.steps ?? []).some((x) => x.date === r.next.date)), "a record's next step is one of its steps");
ok(file.rows.every((r) => !r.impact || (r.impact.quote && r.impact.text.includes("; it bears on "))), "every impact sentence has its quotation and its table");
ok(!/[—–]/.test(JSON.stringify(file)), "no em or en dash in the file");
const sorted = file.rows.every((r, i, a) => i === 0 || a[i - 1].date >= r.date);
ok(sorted, "the file is newest first");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exit(1);
