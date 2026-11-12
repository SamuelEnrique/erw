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
ok(keys.length === 5 && keys.every((k) => /^policy(cal|fig)\|/.test(k.key)), "every step and figure has its key (session 1876: no sum keys, the page shows no sum)");

// session 3062: the charts' data, the sums and the readers
const bm = M.byBodyMonth(rows, 1);
ok(bm.months.join() === "2026-08,2026-09,2026-10,2026-11" && bm.series.map((x) => x.name).join() === "FERC,Other", "records by month and body: the top bodies, the rest as Other");
ok(bm.series[0].values.join() === "1,0,0,1" && bm.series[1].values.join() === "0,1,1,0", "each month's count of each body");
const ss = M.sigBySector(rows);
ok(ss.sectors.join() === "gas,nuclear,oil" && ss.series.map((x) => x.values.join("")).join("|") === "001|010|100", "records by sector and band of significance; the unscored left out");
// session 1876 (policy faults row 28): the sums are gone; each month and unit gives its count and its largest figure
const fm = M.figureMonths(rows);
ok(fm.map((m) => `${m.month}|${m.unit}|${m.n}|${m.top.id}`).join() === "2026-11|Dth/d|1|a,2026-09|USD|1|c", "figures by month: newest month first, each unit's count and largest, no sum");
ok(M.pythonReader("x.csv").includes('pd.read_csv("x.csv", comment="#"') && M.stataReader("x.csv").includes('import delimited using "x.csv"'), "a Python and a Stata reader of the CSV");
ok(!M.keysOf({ rows }).some((k) => k.kind === "sum") && M.keysOf({ rows }).some((k) => k.key === M.figureKey(rows[2])), "no sum among the keys; the largest figure's key is its record's figure key");

// the data file the view reads
ok(file.records === file.rows.length && file.rows.length > 1000, `the file holds its ${file.records} records`);
ok(file.rows.every((r) => r.id && r.date && r.body && r.instrument && r.status && r.title && r.n >= 1 && r.bears_on?.table), "every row has its record id, date, body, instrument, status, title, documents and table");
ok(file.rows.every((r) => M.INSTRUMENT_WORDS[r.instrument] && M.STATUS_WORDS[r.status]), "every instrument and status has its words");
ok(file.rows.every((r) => !r.figure || (r.figure.words && r.figure.event_id)), "every figure has its words and its document");
ok(file.rows.every((r) => !r.next || /^\d{4}-\d{2}-\d{2}$/.test(r.next.date)), "every next step has its date");
ok(file.rows.every((r) => (r.steps ?? []).every((x) => M.KIND_WORDS[x.kind] && x.event_id && x.words)), "every step has its kind's words, its document and its words");
ok(file.rows.every((r) => !r.next || (r.steps ?? []).some((x) => x.date === r.next.date)), "a record's next step is one of its steps");
ok(file.rows.every((r) => !r.impact || (r.impact.quote && r.impact.text.includes("; it bears on "))), "every impact sentence has its quotation and its table");
ok(!new RegExp("[" + String.fromCharCode(0x2014, 0x2013) + "]").test(JSON.stringify(file)), "no em or en dash in the file");
const sorted = file.rows.every((r, i, a) => i === 0 || a[i - 1].date >= r.date);
ok(sorted, "the file is newest first");


// Session 1876: the policy monitor's faults of 12 November 2026 (docs/reviews/policy-faults-2026-11-11.md), one block a
// row. The made-up rows above stand in for the shapes; where a number is of the file of 6 November it is checked only on
// that file (a rebuilt file checks the same rule, not the number).
const of6Nov = file.built === "2026-11-06";
const T = "2026-11-12";
const opened = M.filterRows(file.rows, M.OPEN_FILTERS);

// row 2: a choice counts what ticking it gives, the other filters kept
const o2 = M.options(rows, M.OPEN_FILTERS);
ok(o2.bodies.find((x) => x.key === "FERC").n === 1 && o2.bodies.find((x) => x.key === "BOEM").n === 0, "row 2: at the opening filters FERC counts 1 (not 2) and BOEM stays listed at 0");
ok(M.options(rows, { ...M.OPEN_FILTERS, bodies: ["FERC"] }).bodies.find((x) => x.key === "NRC").n === 1, "row 2: a list's own choice does not narrow its own counts");
ok(M.options(rows, { ...M.OPEN_FILTERS, bodies: ["NRC"] }).sectors.map((x) => `${x.key}:${x.n}`).join() === "nuclear:1,gas:0,oil:0", "row 2: another list's choice does");
const o2f = M.options(file.rows, M.OPEN_FILTERS);
for (const list of ["bodies", "instruments", "sectors", "statuses"]) {
  const key = { bodies: "body", instruments: "instrument", sectors: "sector", statuses: "status" }[list];
  ok(o2f[list].every((x) => x.n === M.filterRows(file.rows, { ...M.OPEN_FILTERS, [list]: [x.key] }).length), `row 2: every ${key} choice's number is what ticking it shows`);
}
if (of6Nov) ok(o2f.bodies.find((x) => x.key === "BSEE").n === 1 && o2f.bodies.find((x) => x.key === "FERC").n === 97, "row 2 (file of 6 November): BSEE 1 and FERC 97 at the opening filters");

// row 3: the sectors as words
ok(file.rows.every((r) => !r.sector || M.SECTOR_WORDS[r.sector]), "row 3: every sector of the file has its words");
ok(M.sectorWords("lng") === "LNG" && M.sectorWords("grid_conditions") === "Grid conditions" && M.sectorWords(undefined) === "", "row 3: lng is LNG, grid_conditions Grid conditions");
ok(M.options(file.rows).sectors.every((x) => x.label === M.SECTOR_WORDS[x.key]), "row 3: the filter lists the words");

// row 4: the week runs to the file's last document when the file stops before today
const c4 = M.calendarOf(withSteps, T, "2026-11-03");
ok(c4.stale && c4.weekTo === "2026-11-03" && c4.weekFrom === "2026-10-27" && c4.week.map((r) => r.id).join() === "p,s", "row 4: a file older than today: the seven days to its last document");
ok(c4.aheadTo === "2026-12-12", "row 4: the month ahead still runs from today");
ok(!M.calendarOf(withSteps, "2026-11-03", "2026-11-03").stale && M.calendarOf(withSteps, T).weekTo === T, "row 4: a file of today, or no last date given: the seven days to today");
ok(M.lastDateOf(file.rows) === file.rows[0].date, "row 4: the file's last document date is its newest row's");
if (of6Nov) ok(M.calendarOf(opened, T, M.lastDateOf(file.rows)).weekTo === "2026-11-05", "row 4 (file of 6 November): the week ends 2026-11-05");

// row 6: the steps the significance floor hides are counted, never "no dated step"
const s6 = [R({ id: "lo", significance: 2, steps: [{ kind: "comments_due", date: "2026-11-20", words: "w", event_id: "federalregister:7" }] }),
  R({ id: "hi", significance: 8, steps: [{ kind: "effective", date: "2026-12-01", words: "w", event_id: "federalregister:6" }] })];
ok(M.floorHidden(s6, M.OPEN_FILTERS, T) === 1 && M.floorHidden(s6, { ...M.OPEN_FILTERS, minSig: null }, T) === 0, "row 6: one step hidden by the floor; none with the floor lifted");
ok(M.floorHidden(s6, { ...M.OPEN_FILTERS, bodies: ["NRC"] }, T) === 0, "row 6: the other filters are kept");
const hidden6 = M.floorHidden(file.rows, M.OPEN_FILTERS, T);
ok(hidden6 === M.calendarOf(M.filterRows(file.rows, M.NO_FILTERS), T).ahead.length - M.calendarOf(opened, T).ahead.length, "row 6: on the file, the hidden count is the month ahead's steps less those shown");
if (of6Nov) ok(hidden6 === 5 && M.calendarOf(opened, T).ahead.length === 0, "row 6 (file of 6 November): five steps below significance 5, none above");

// row 14: the impact sentence without its "; it bears on" clause
ok(M.impactText("A rule takes effect November 16, 2026; it bears on epa_needs_units (/data#epa_needs_units).") === "A rule takes effect November 16, 2026.", "row 14: the clause is cut, the sentence ends with its full stop");
ok(M.impactText("No clause here.") === "No clause here.", "row 14: a sentence without the clause is as it was");
const imp = file.rows.filter((r) => r.impact);
ok(imp.every((r) => !M.impactText(r.impact.text).includes("it bears on") && M.impactText(r.impact.text).endsWith(".") && !M.impactText(r.impact.text).includes("/data#")), `row 14: none of the file's ${imp.length} impact sentences keeps the clause`);
if (of6Nov) ok(imp.length === 53, "row 14 (file of 6 November): 53 impact sentences");

// row 16: the next step as of the page's day
const n16 = R({ id: "n", steps: [{ kind: "comments_due", date: "2026-10-01", words: "w1", event_id: "federalregister:1" }, { kind: "effective", date: "2026-11-20", words: "w2", event_id: "federalregister:2" }] });
const p16 = R({ id: "m", steps: [{ kind: "meeting", date: "2026-05-27", words: "w", event_id: "federalregister:3" }, { kind: "comments_due", date: "2026-04-01", words: "w", event_id: "federalregister:4" }] });
ok(M.nextOf(n16, T).date === "2026-11-20" && !M.nextOf(n16, T).passed, "row 16: the first step on or after today");
ok(M.nextOf(p16, T).date === "2026-05-27" && M.nextOf(p16, T).passed, "row 16: all past: the last step, marked passed");
ok(M.nextOf(R({}), T) === null, "row 16: no step, no next step");
ok(M.sortRows([p16, R({ id: "z" }), n16], "next", "asc", T).map((r) => r.id).join() === "n,m,z" && M.sortRows([p16, R({ id: "z" }), n16], "next", "desc", T).map((r) => r.id).join() === "n,m,z", "row 16: a step ahead sorts before a passed one, either way; none last");
const drawn16 = file.rows.map((r) => M.nextOf(r, T)).filter(Boolean);
ok(drawn16.every((x) => x.date >= T || x.passed), "row 16: on the file no step before today is drawn as ahead");
if (of6Nov) ok(drawn16.filter((x) => !x.passed).length === file.rows.filter((r) => (r.steps ?? []).some((s) => s.date >= T)).length, "row 16 (file of 6 November): a step ahead exactly where the record holds one");

// row 17: the next step cell's key is one the tracer knows
const known = new Set(M.keysOf(file).map((k) => k.key));
const keyed17 = file.rows.filter((r) => M.nextOf(r, T));
ok(keyed17.length > 0 && keyed17.every((r) => { const x = M.nextOf(r, T); return x.event_id && known.has(M.stepKey(r, x)); }), `row 17: each of the ${keyed17.length} next steps drawn has a key of keysOf and its document`);

// row 19: the figure sort compares within a unit
const f19 = [["u", 5e9, "USD"], ["m", 1400, "MW"], ["g", 2, "GW"], ["k", 500, "kW"], ["d", 321200, "Dth/d"], ["v", 345, "kV"]].map(([id, value, unit]) => R({ id, figure: { value, unit, words: "w", event_id: "e" } }));
ok(M.sortRows(f19, "figure", "desc").map((r) => r.id).join() === "u,g,m,k,d,v", "row 19: USD, then MW with GW and kW in MW, then the others by unit name");
ok(M.sortRows(f19, "figure", "asc").map((r) => r.id).join() === "u,k,m,g,d,v", "row 19: ascending keeps the units' order, the values turn");
const s19 = M.sortRows(opened, "figure", "desc").filter((r) => r.figure);
const tiers = s19.map((r) => M.figureTier(r.figure.unit));
ok(tiers.every((t, i) => i === 0 || tiers[i - 1] <= t), "row 19: on the file, no unit's figure ranks among another's");

// row 22: the open row's keys as words and links
ok(M.proceedingOf("docket:EPA-HQ-OAR-2025-0124;rin:2060-AW55;ferc:CP26-581;nrc:NRC-2026-5116;project:2538-106;doe:15-62-LNG;irs:REG-121244-23;osmre:WY-055-FOR").map((p) => p.words).join("|")
  === "Docket EPA-HQ-OAR-2025-0124|RIN 2060-AW55|FERC docket CP26-581|NRC docket NRC-2026-5116|FERC project 2538-106|DOE docket 15-62-LNG|IRS REG-121244-23|OSMRE WY-055-FOR", "row 22: one proceeding id of each prefix in words");
ok(file.rows.every((r) => M.proceedingOf(r.docket).every((p) => p.words !== p.id)), "row 22: every proceeding id of the file has its words");
const h22 = M.historyOf({ ...R({}), history: ["2026-08-26,2026-11-03 rule final federalregister:2026-17445,federalregister:2026-22421", "2026-09-14 meeting scheduled nrc:0750999be55a"],
  sources: ["https://example.invalid/documents/2026/11/03/2026-22421/x", "https://example.invalid/documents/2026/08/26/2026-17445/y", "https://www.nrc.example.invalid/z.pdf"] });
ok(h22[0].dates.join() === "2026-08-26,2026-11-03" && h22[0].instrument === "rule" && h22[0].docs.map((d) => `${d.label}>${d.href.split("/")[7]}`).join() === "FR 2026-17445>2026-17445,FR 2026-22421>2026-22421", "row 22: a history line's dates, instrument and each Register document linked to its own address");
ok(h22[1].docs[0].href === "https://www.nrc.example.invalid/z.pdf" && h22[1].docs[0].label === "nrc.example.invalid", "row 22: the one other document left takes the one address left, labelled by its host");
const h22b = M.historyOf({ ...R({}), history: ["2026-09-14 meeting scheduled nrc:a", "2026-09-15 meeting scheduled nrc:b"], sources: ["https://example.invalid/1", "https://example.invalid/2"] });
ok(h22b.every((h) => !h.docs[0].href && h.docs[0].label === h.docs[0].id), "row 22: two such documents and two addresses: no link is guessed");
const fr22 = file.rows.flatMap((r) => M.historyOf(r).flatMap((h) => h.docs)).filter((d) => d.id.startsWith("federalregister:"));
ok(fr22.length > 0 && fr22.every((d) => d.href && d.href.includes(d.id.slice(16))), `row 22: each of the file's ${fr22.length} Register documents links to its own page`);
ok(file.rows.every((r) => M.historyOf(r).every((h) => M.INSTRUMENT_WORDS[h.instrument] && M.STATUS_WORDS[h.status])), "row 22: every history line's instrument and status has its words");

// row 23: fifty rows at a time
ok(M.MONITOR_PAGE === 50, "row 23: the table draws 50 rows, then 50 more on a click");

// row 26: the part month's label
ok(M.monthLabels(["2026-10", "2026-11"], "2026-11-05").join() === "2026-10,2026-11 to the 5th", "row 26: the last month, not over, carries the day it runs to");
ok(M.monthLabels(["2026-11"], "2026-11-30").join() === "2026-11" && M.monthLabels(["2026-02"], "2026-02-28").join() === "2026-02", "row 26: a whole month is a month");
ok(["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-11", "2026-11-22", "2026-11-23"].map((d) => M.monthLabels(["2026-11"], d)[0].split(" ").pop()).join() === "1st,2nd,3rd,11th,22nd,23rd", "row 26: the ordinals");
if (of6Nov) ok(M.monthLabels(M.byBodyMonth(file.rows).months, M.lastDateOf(file.rows)).pop() === "2026-11 to the 5th", "row 26 (file of 6 November): the chart's last month is 2026-11 to the 5th");

// row 28: no sum; each month and unit, its count and its largest
const fm28 = M.figureMonths(file.rows);
ok(fm28.every((m) => m.top.figure.unit === m.unit && file.rows.filter((r) => r.figure && r.figure.unit === m.unit && M.monthOf(r.date) === m.month).every((r) => r.figure.value <= m.top.figure.value)), "row 28: each month's figure is the largest of its unit");
ok(fm28.reduce((a, m) => a + m.n, 0) === file.rows.filter((r) => r.figure).length, "row 28: every record stating a figure is counted once");
ok(fm28.every((m) => known.has(M.figureKey(m.top))), "row 28: each largest figure's key is one the tracer knows");
if (of6Nov) { const d = fm28.find((m) => m.month === "2025-12" && m.unit === "USD"); ok(d && d.n === 11 && d.top.figure.value === 18e9, "row 28 (file of 6 November): December 2025, 11 records in USD, the largest USD 18 billion, no sum"); }

// row 29: the CSV holds the plain read, the impact's basis, the figure's document and the steps
// a whole CSV text to its records (a quoted field may hold a comma, a quote or a line break), the comment line dropped
const records = (text) => { const out = []; let row = [], cur = "", q = false;
  for (let i = 0; i < text.length; i++) { const ch = text[i];
    if (q) { if (ch === '"' && text[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
    else if (ch === '"') q = true; else if (ch === ",") { row.push(cur); cur = ""; } else if (ch === "\n") { row.push(cur); out.push(row); row = []; cur = ""; } else cur += ch; }
  if (cur || row.length) { row.push(cur); out.push(row); }
  return out.filter((x) => !x[0].startsWith("#")); };
const parse = (line) => records(line)[0];
const r29 = R({ id: "pr", plain: "A plain read, with a comma.", figure: { value: 9, unit: "MW", words: "w", event_id: "federalregister:5" },
  impact: { text: "It does a thing; it bears on t (/data#t).", quote: "q", model: "m", event_id: "federalregister:6" },
  steps: [{ kind: "comments_due", date: "2026-11-20", words: "w", event_id: "federalregister:7" }] });
const c29 = M.toCsv([r29], "2026-11-06", T).trim().split("\n");
const col = (name) => parse(c29[2])[M.CSV_COLS.indexOf(name)];
ok(parse(c29[1]).length === M.CSV_COLS.length && parse(c29[2]).length === M.CSV_COLS.length, "row 29: the header and the row have every column");
ok(col("plain_read") === "A plain read, with a comma." && col("impact") === "It does a thing." && col("impact_quote") === "q" && col("impact_model") === "m" && col("impact_document") === "federalregister:6", "row 29: the plain read, and the impact sentence with its quotation, model and document");
ok(col("figure_document") === "federalregister:5" && col("steps") === "comments_due=2026-11-20@federalregister:7" && col("next_step_date") === "2026-11-20" && col("next_step_passed") === "no", "row 29: the figure's document, every step, the next step as the page draws it");
const c29f = records(M.toCsv(opened, file.built, T)).slice(1);
const plainShown = opened.filter((r) => !r.impact && r.plain).length;
ok(c29f.length === opened.length && c29f.filter((x) => !x[M.CSV_COLS.indexOf("impact")] && x[M.CSV_COLS.indexOf("plain_read")]).length === plainShown, `row 29: on the file the ${plainShown} rows showing a plain read carry it in the CSV`);
ok(M.pythonReader("x.csv").includes("plain_read") && M.stataReader("x.csv").includes("next_step_passed"), "row 29: the readers name the columns");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exit(1);
