// Chain 302 (session 7201): the large-load rules on the All grids tab and in the policy monitor: lib/largeloadrules.ts
// against its page file, data/siting/large_load_rules.json (warehouse/derived/large_load_rules_page.py). No build, no network.
//   node --import ./scripts/alias-register.mjs scripts/test-large-load-rules.mjs
import { readFileSync } from "node:fs";

const L = await import("../lib/largeloadrules.ts");
const file = JSON.parse(readFileSync(new URL("../data/siting/large_load_rules.json", import.meta.url), "utf-8"));
let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const all = L.lines(file);

// the words
ok(L.cut("one two three", 50) === "one two three", "a text that fits is whole");
ok(L.cut("one two three four five six seven", 14) === "one two three..." && !L.cut("alpha, beta gamma", 7).includes(","), "a long text is cut at a word, no trailing comma");
ok(L.cut("x".repeat(300), 20).length === 23, "a text with no space is cut at the limit");
ok(L.statesOf("ND, SD, MT, WY and other member states").join() === "ND,SD,MT,WY" && L.statesOf("VA").join() === "VA" && L.statesOf("").length === 0, "the states a row names");
ok(L.dateWords("2026-10-08") === "2026-10-08" && L.dateWords("2026-10") === "2026-10" && L.dateWords("not published") === "not published", "a date is a day, a month or not published");

// the file and its counts
ok(file.rules.length === 100 && file.held_rules.length === 22 && all.length === 122, "100 public rules and 22 held: 122 lines");
ok(file.changes.length === 94 && file.held_changes.length === 4 && file.laws.length === 27 && file.held_laws.length === 1, "94 changes and 4 held; 27 laws and 1 held");
ok(L.FIELDS.length === 8 && L.FIELDS.every((f) => file.fields.includes(f)) && file.fields.every((f) => L.FIELDS.includes(f)), "the eight fields are the file's");
ok(file.rules.every((r) => L.RULE_STATUSES.includes(r.status)) && file.laws.every((l) => L.LAW_STATUSES.includes(l.status)), "every status is one the page words");
ok(file.rules.every((r) => L.GRID_KEYS.includes(r.grid)) && file.held_rules.every((r) => L.GRID_KEYS.includes(r.grid)), "every grid is one the filter names");
ok(file.changes.every((c) => L.CHANGE_GROUPS.some(([k]) => k === c.group)) && file.changes.every((c) => c.kind in L.CHANGE_KIND_WORDS), "every change's region and kind has its words");
for (const s of L.RULE_STATUSES) ok(L.largeLoadStat(file, `largeload|rules|status|${s}`) === (file.counts.rules[s] ?? 0), `the count of rules ${s} is the file's (${file.counts.rules[s] ?? 0})`);
// session 7626 (wip/alt-policy-2): the counts are of the laws in scope (Michigan's sales tax exemption, in effect, out)
for (const s of L.LAW_STATUSES) { const n = L.inScopeLaws(file.laws).filter((l) => l.status === s).length; ok(L.largeLoadStat(file, `largeload|laws|status|${s}`) === n && n === (file.counts.laws[s] ?? 0) - (s === "in effect" ? 1 : 0), `the count of laws ${s} is the laws' in scope (${n})`); }
ok(L.largeLoadStat(file, "largeload|rules|all") === 122 && L.largeLoadStat(file, "largeload|rules|public") === 100 && L.largeLoadStat(file, "largeload|rules|held") === 22, "the rule counts: all, public, held");
ok(L.largeLoadStat(file, "largeload|changes|public") === 94 && L.largeLoadStat(file, "largeload|changes|held") === 4 && L.largeLoadStat(file, "largeload|laws|public") === 26 && L.largeLoadStat(file, "largeload|laws|held") === 1, "the change and law counts");
ok(L.CHANGE_GROUPS.reduce((s, [k]) => s + L.largeLoadStat(file, `largeload|changes|group|${k}`), 0) === 94, "the changes by region sum to 94");
ok(L.largeLoadStat(file, "largeload|rules|state|TX") === all.filter((r) => /\bTX\b/.test(r.state)).length && L.largeLoadStat(file, "largeload|rules|state|TX") >= 8, "the rules of a state count public and held");
ok(L.largeLoadStat(file, "allgrids|x") === undefined && L.largeLoadStat(file, "largeload|rules|nothing") === undefined, "a key that is not the section's is no figure");

// what a cell draws
const kinds = {};
let blank = 0;
for (const r of file.rules) for (const f of L.FIELDS) {
  const c = r.fields[f], d = L.drawn(c, f);
  kinds[d.kind] = (kinds[d.kind] ?? 0) + 1;
  if (d.kind === "withheld" || d.kind === "held") { blank++; if (d.words !== "" || d.whole !== L.LICENSE_NEEDED || !d.tip.startsWith(L.LICENSE_NEEDED) || /\bcite\b/.test(JSON.stringify(c))) { failed++; console.log(`FAIL a withheld field prints something: ${r.id} ${f}`); } }
  if (d.kind === "value" && (!d.tip.includes(c.v) || !d.tip.includes(c.cite) || d.words.length > 115)) { failed++; console.log(`FAIL a value's hover lacks its words or its cite, or its cell is long: ${r.id} ${f}`); }
  if (d.kind === "not published" && d.words !== "not published") { failed++; console.log(`FAIL ${r.id} ${f}`); }
}
n++;
console.log(`ok   every field of every public rule draws by its kind: ${JSON.stringify(kinds)}`);
const withheldFields = file.rules.reduce((s, r) => s + r.withheld.length, 0);
const byRegistry = file.rules.reduce((s, r) => s + L.FIELDS.filter((f) => r.fields[f].kind === "withheld" && r.fields[f].registry).length, 0);
ok(blank === 8 && kinds.withheld === 7 && kinds.held === 1 && withheldFields === 4 && byRegistry === 3, "8 fields of public rules are drawn blank with license needed: 4 the table withholds, 3 a held registry file holds, 1 that points to a held row");
ok(kinds.value > 380 && kinds["not published"] > 350 && kinds.see === 27 && kinds.registry === 2, "the values, the fields not published, the pointers and the registry's");
ok(L.drawn(undefined, "collateral").kind === "empty" && L.drawn({ kind: "empty" }, "collateral").words === "", "an empty field draws nothing");
const v = L.drawn({ kind: "value", v: "25 MW", cite: "p. 1: \"25 MW\"" }, "threshold_mw");
ok(v.words === "25 MW" && v.tip.includes("As the document prints it: p. 1"), "a short value is whole, its cite in the hover");
ok(file.rules.every((r) => L.FIELDS.every((f) => r.fields[f].kind !== "see" || r.fields[f].held || all.some((x) => x.id === r.fields[f].row && !x.held))), "a pointer to the utility's other row names a public row of the file, or is held");

// the filters and the sort
ok(L.filterLines(all, L.NO_RULE_FILTERS).length === 122, "no filter holds every rule");
const tx = L.filterLines(all, { ...L.NO_RULE_FILTERS, states: ["TX"] });
ok(tx.length === L.largeLoadStat(file, "largeload|rules|state|TX") && tx.every((r) => L.statesOf(r.state).includes("TX")), `by state: ${tx.length} in Texas`);
ok(L.filterLines(all, { ...L.NO_RULE_FILTERS, grids: ["pjm"] }).length === L.largeLoadStat(file, "largeload|rules|grid|pjm"), "by grid");
ok(L.filterLines(all, { ...L.NO_RULE_FILTERS, statuses: ["proposed"] }).length === file.counts.rules.proposed, "by status");
ok(L.filterLines(all, { ...L.NO_RULE_FILTERS, statuses: [L.HELD_STATUS] }).length === 22 && L.filterLines(all, { ...L.NO_RULE_FILTERS, statuses: [L.HELD_STATUS] }).every((r) => r.held && !r.rule), "by status, the held rows: their status is not read");
ok(L.filterLines(all, { ...L.NO_RULE_FILTERS, find: "dominion" }).length >= 1 && L.filterLines(all, { ...L.NO_RULE_FILTERS, find: "DOMINION" }).every((r) => `${r.utility} ${r.rule?.name ?? ""}`.toLowerCase().includes("dominion")), "by a utility's or a rule's name");
ok(L.filterLines(all, { states: ["VA"], grids: ["pjm"], statuses: ["in effect"], find: "" }).every((r) => r.grid === "pjm" && r.rule.status === "in effect"), "the filters together");
for (const k of L.RULE_SORTS) {
  const up = L.sortLines(all, k, "asc"), down = L.sortLines(all, k, "desc");
  const empty = (r) => (k === "utility" || k === "grid" ? false : k === "state" ? !r.state : r.held || (k === "status" ? false : k === "date" ? !/^\d{4}/.test(r.rule.status_date) : r.rule.fields[k].kind !== "value"));
  const lastOk = (rows) => { const i = rows.findIndex(empty); return i === -1 || rows.slice(i).every(empty); };
  ok(up.length === 122 && down.length === 122 && lastOk(up) && lastOk(down), `sorts on ${k}, a row with nothing printed last either way`);
}
ok(L.sortLines(all, "date", "desc")[0].rule.status_date >= L.sortLines(all, "date", "desc")[5].rule.status_date, "by date, latest first");
const o = L.ruleOptions(all);
ok(o.statuses.reduce((s, x) => s + x.n, 0) === 122 && o.grids.reduce((s, x) => s + x.n, 0) === 122 && o.states.find((x) => x.key === "TX").n === tx.length, "the filters' choices count the rules they hold");

// a row of the tab
const oncor = L.rowRules(file, [{ number: "19327", name: "TXU Energy Retail Co, LLC" }, { number: "44372", name: "Oncor Electric Delivery Company LLC" }], "TX", "ercot");
ok(oncor.own.join() === "texas-02" && oncor.statewide.join() === "texas-01" && oncor.unread.length === 1 && oncor.none.length === 0 && oncor.inState === tx.length, "a Texas row in ERCOT: Oncor's rule, the Commission's rule for every utility, and a retailer not read");
const ms = L.rowRules(file, [{ number: "12685", name: "Entergy Mississippi LLC" }], "MS", "miso");
ok(ms.own.length === 0 && ms.none.length === 1 && ms.none[0].words.startsWith("No large-load rule found.") && ms.none[0].note.endsWith("entergy_mississippi.md"), "a utility read with no rule found says so, with the note");
const la = L.rowRules(file, [{ number: "11241", name: "Entergy Louisiana LLC" }], "LA", "miso");
ok(la.own.length === 2 && la.statewide.length === 2 && !la.statewide.some((id) => la.own.includes(id)), "Louisiana: the utility's two rules and the Commission's two for every utility");
ok(L.rowRules(file, [{ number: "8901", name: "CenterPoint Energy" }], "TX", "ercot").own.every((id) => L.lineOf(file, id).held), "a utility whose rule is held reaches the held row");
ok(L.rowRules(file, [], null, "pjm").inState === 0 && L.rowRules(file, [{ number: "1", name: "x" }, { number: "1", name: "x" }], "TX", "spp").unread.length === 1, "no state, no count; a utility named twice is read once");
ok(Object.keys(file.eia).every((k) => file.eia[k].rules.length || (file.eia[k].none ?? "").startsWith("No large-load rule found.")), "every utility number of the file has a rule or the note's line");
ok(Object.keys(file.statewide).every((id) => all.some((r) => r.id === id)) && Object.values(file.eia).every((e) => e.rules.every((id) => all.some((r) => r.id === id))), "every rule a row can open is a line of the table");

// the changes
const aff = {};
for (const c of file.changes) { const a = L.affectsOf(file, c); aff[a.kind] = (aff[a.kind] ?? 0) + 1; }
ok(aff.rule > 40 && aff.registry >= 5 && aff.new >= 1 && !aff.none, `every change names a rule, a registry file or a new rule: ${JSON.stringify(aff)}`);
ok(file.changes.every((c, i) => i === 0 || file.changes[i - 1].date >= c.date), "the changes are newest first");
ok(L.filterChanges(file.changes, ["south_changes"]).length === L.largeLoadStat(file, "largeload|changes|group|south_changes") && L.filterChanges(file.changes, []).length === 94, "the changes by region");
ok(L.filterChanges(file.changes, [], ["TX"]).every((c) => L.statesOf(c.state).includes("TX")), "the changes of a state");
ok(file.held_changes.every((h) => L.CHANGE_GROUPS.some(([k]) => h.id.startsWith(`${k}-`))), "a held change's region is read from its id");

// the laws
const parts = file.laws.flatMap((l) => L.requirementsOf(l));
ok(parts.length > 90 && parts.every((p) => p.topic && p.words && p.cite), `every requirement of every law parses to a topic, its words and its cite (${parts.length})`);
ok(file.laws.every((l) => L.requirementsOf(l).map((p) => `${p.topic}: ${p.words} [${p.cite}]`).join(" || ") === l.requirements), "the parts put together are the table's own cell");
ok(L.lawsOf(file, ["MD"]).laws.length === 2 && L.lawsOf(file, ["IN"]).held.length === 1 && L.lawsOf(file, []).laws.length === 27, "the laws of a state; Indiana's is held");
ok(L.lawStates(file).includes("IN") && L.lawStates(file).length === 25 && L.lawsHref("TX") === "/policy?view=monitor&state=TX#large-load-laws", "25 states have a law or a bill (Michigan out of scope, session 7626); the tab's link to one");
ok(L.largeLoadStat(file, "largeload|laws|state|MD") === 2 && L.largeLoadStat(file, "largeload|laws|state|IN") === 1, "the laws of a state count the held one");

// a state with no law in the table (session 7204): what the research records, never "no law"
const have = new Set([...file.laws, ...file.held_laws].map((l) => l.state)), searches = file.law_searches;
ok(searches.length === 22 && searches.every((x) => !have.has(x.state)) && new Set(searches.map((x) => x.state)).size === 22, "22 states with no row in the laws table have a record of what the research searched, none of them a state with a law");
ok(have.size + searches.length === 48 && ["AK", "HI"].every((s) => !have.has(s) && !searches.some((x) => x.state === s)), "26 states with a row and 22 with a record: every state but Alaska and Hawaii");
ok(searches.every((x) => ["none found", "not read", "withheld"].includes(x.kind)) && searches.filter((x) => x.kind === "withheld").map((x) => `${x.state} ${x.bill}`).join() === "TX S.B. 6", "each is none found, not read or withheld; the one withheld bill is Texas S.B. 6");
ok(searches.every((x) => !/\bnews\b|\blead\b|unconfirmed|described in/i.test(x.words)) && searches.filter((x) => !x.words).length === 5 && searches.every((x) => x.source.startsWith("docs/research/large_load/legislation/")), "no lead from the news is carried: five states' words stay in the research file, which is named");
const txS = L.lawSearchOf(searches, "TX"), ga = L.lawSearchOf(searches, "GA"), azS = L.lawSearchOf(searches, "AZ"), hi = L.lawSearchOf(searches, "HI");
ok(txS.kind === "withheld" && txS.bill === "S.B. 6" && txS.words === "read and not shown" && txS.tip.startsWith("not shown: the ERW read TX S.B. 6") && txS.tip.includes("robots file"), "Texas: S.B. 6 was read and is not shown, the reason in the hover");
ok(ga.kind === "not read" && ga.tip.includes("is not ruled out") && ga.tip.includes("docs/research/large_load/legislation/south_west.json"), "Georgia: not read, not ruled out, the research file named");
ok(azS.kind === "none found" && azS.words === "none found where searched" && azS.tip.includes("It is not proof that none exists.") && azS.tip.includes("What was searched: ARS Title 40"), "Arizona: none found where searched, with what was searched");
ok(hi.kind === "not searched" && hi.tip.includes("did not search HI"), "a state the research did not search says so");
ok(L.rulesHref("VA") === "/cost-of-power?view=allgrids&rstate=VA#large-load-rules" && L.rulesHref() === "/cost-of-power?view=allgrids#large-load-rules", "the link from a state's laws to its utilities' rules");

// the downloads
const parse = (text) => { const rows = []; let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) { const ch = text[i];
    if (q) { if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (ch === '"') q = false; else cell += ch; }
    else if (ch === '"') q = true; else if (ch === ",") { row.push(cell); cell = ""; } else if (ch === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; } else cell += ch; }
  return rows; };
const csv = L.rulesCsv(all, file, "/cost-of-power?view=allgrids");
const body = csv.slice(csv.indexOf("\n") + 1), rows = parse(body);
ok(csv.startsWith("# Energy Research Warehouse (ERW)") && rows[0].join() === L.RULE_CSV_COLS.join() && rows.length === 123 && rows.every((r) => r.length === L.RULE_CSV_COLS.length), "the rules' CSV: a provenance line, the columns, 122 rows of equal width");
const col = (name) => L.RULE_CSV_COLS.indexOf(name);
let same = 0;
for (const r of file.rules) { const line = rows.find((x) => x[0] === r.id);
  for (const f of L.FIELDS) { const c = r.fields[f];
    if (c.kind === "value" && line[col(f)] === c.v && line[col(`${f}_cite`)] === c.cite) same++;
    if (c.kind === "withheld" && (line[col(f)] !== L.LICENSE_NEEDED || line[col(`${f}_cite`)] !== "")) { failed++; console.log(`FAIL the CSV prints a withheld field: ${r.id} ${f}`); } } }
ok(same === kinds.value, `every value and its cite is in the CSV as the file has it (${same})`);
const heldLines = rows.filter((x) => x[col("license")] === "internal");
ok(heldLines.length === 22 && heldLines.every((x) => L.FIELDS.every((f) => x[col(f)] === L.LICENSE_NEEDED && x[col(`${f}_cite`)] === "") && x[col("source_url")] === "" && x[col("notes")] === "" && x[col("rule")] === L.LICENSE_NEEDED), "a held row's CSV line is its id, utility and place; every other cell license needed or empty");
ok(L.rulesCsv(tx, file, "x").split("\n").length === tx.length + 3, "the CSV holds the rows shown");
const ccsv = parse(L.changesCsv(file.changes, file, "x").replace(/^[^\n]*\n/, ""));
ok(ccsv[0].join() === L.CHANGE_CSV_COLS.join() && ccsv.length === 95 && ccsv.every((r) => r.length === L.CHANGE_CSV_COLS.length) && ccsv[1][L.CHANGE_CSV_COLS.indexOf("what")] === file.changes[0].what, "the changes' CSV");
const lcsv = parse(L.lawsCsv(file.laws, file.held_laws, file, "x").replace(/^[^\n]*\n/, ""));
ok(lcsv[0].join() === L.LAW_CSV_COLS.join() && lcsv.length === 29 && lcsv.every((r) => r.length === L.LAW_CSV_COLS.length) && lcsv[28][L.LAW_CSV_COLS.indexOf("requirements")] === L.LICENSE_NEEDED, "the laws' CSV, the held law license needed");
ok(L.pythonReader("x.csv", L.RULE_CSV_COLS, "w").includes('pd.read_csv("x.csv", comment="#"') && L.stataReader("x.csv", L.RULE_CSV_COLS, "w").includes("varnames(2) rowrange(3)") && L.pythonReader("x.csv", L.RULE_CSV_COLS, "w").includes("collateral_cite"), "the readers skip the provenance line and name the columns");

// no held value anywhere a page can print: a held line carries five keys
ok(file.held_rules.every((r) => Object.keys(r).sort().join() === "grid,id,region,state,utility") && file.held_changes.every((r) => Object.keys(r).sort().join() === "id,utility") && file.held_laws.every((r) => Object.keys(r).sort().join() === "bill,id,state"), "a held row of the file is its name and place only");
const text = [L.FIELD_HEAD, L.FIELD_TIP, L.STATUS_TIP, L.LAW_STATUS_TIP, L.GRID_WORDS, L.CHANGE_KIND_WORDS].map((x) => JSON.stringify(x)).join(" ") + L.UPGRADES_TIP;
ok(!text.includes(String.fromCharCode(0x2014)) && !text.includes(String.fromCharCode(0x2013)), "no em or en dash in the page's own words");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
