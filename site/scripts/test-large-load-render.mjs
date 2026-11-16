// Chain 302 (session 7201): the large-load rules' components, drawn to HTML as the server draws them first, without
// building the site (scripts/tsx-loader.mjs): the table under the All grids tab with its filters, A and B and the
// changes; the section with its counts and the panel a row of the tab opens; the line each hub row's Utility and Time
// to connect cell draws; and the states' laws in the policy monitor. It holds what a build would otherwise have to
// show: every component draws without an error; a held row and a withheld field are blank cells that say "license
// needed" and are counted; no value of a held row is anywhere in the HTML; every tip has its target and every button a
// name; every count is the file's; and the section's weight stays small. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-large-load-render.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const L = await import("../lib/largeloadrules.ts");
const S = await import("../lib/siting.ts");
const { SITING_FILES } = await import("../lib/sitingdata.ts");
const { LargeLoadRules } = await import("../app/cost-of-power/LargeLoadRules.tsx");
const { LargeLoadSection, RuleLine, rulesOfRow } = await import("../app/cost-of-power/LargeLoadSection.tsx");
const { StateLaws } = await import("../app/policy/StateLaws.tsx");
const { RuleCard, HeldCard } = await import("../components/largeload/parts.tsx");
const file = JSON.parse(fs.readFileSync(new URL("../data/siting/large_load_rules.json", import.meta.url), "utf-8"));

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const count = (html, re) => (html.match(re) ?? []).length;
const NONE = { state: "", grid: "", status: "", find: "", sort: "", dir: "", a: "", b: "", rule: "", region: "" };
const table = (opened = {}) => renderToStaticMarkup(h(LargeLoadRules, { opened: { ...NONE, ...opened }, address: "/cost-of-power?view=allgrids" }));
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ");
/** What a page must hold whatever it draws: each tip's target is there once, each button has a name, no nest that a
 * browser would break. */
function sound(html, what) {
  const ids = [...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]);
  const twice = ids.filter((id, i) => ids.indexOf(id) !== i);
  const asked = [...html.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]);
  const lost = asked.filter((id) => !ids.includes(id));
  const buttons = [...html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)];
  const nameless = buttons.filter((b) => !/aria-label="[^"]+"/.test(b[1]) && !text(b[2]).trim());
  const nested = buttons.filter((b) => /<button\b|<a\b/.test(b[2]));
  ok(!twice.length && !lost.length && !nameless.length && !nested.length && asked.length > 0,
    `${what}: ${asked.length} tips each with its one target, ${buttons.length} buttons each with a name, none nested${twice.length ? `; an id twice: ${twice[0]}` : ""}${lost.length ? `; a tip with no target: ${lost[0]}` : ""}${nameless.length ? "; a button with no name" : ""}`);
  ok(!html.includes(String.fromCharCode(0x2014)) || text(html).includes(String.fromCharCode(0x2014)), `${what}: no em dash of the page's own (a document's own words may hold one)`);
}

// ---- the table as it opens
const first = table();
ok(count(first, /data-llr-row="/g) === 12 && first.includes(">122 rules shown") === false && /12[^<]*of[^<]*122|122/.test(text(first)), "the table opens on its first 12 rules of 122");
ok(text(first).includes("122 of 122 rules shown") && text(first).includes("Next 12 (12 of 122 drawn"), "the line says 122 of 122 shown, and the next 12 are a button away");
ok(count(first, /data-llr-head="/g) === 13 && L.FIELDS.every((f) => first.includes(`data-llr-head="${f}"`)), "thirteen headings sort: the utility, the state, the grid, the status, the date and the eight fields");
ok(["state", "grid", "status", "find"].every((k) => first.includes(`data-llr-filter="${k}"`)) && first.includes('data-llr-csv="rules"') && count(first, /data-download="python"/g) === 2 && count(first, /data-download="stata"/g) === 2, "the filters by state, grid, status and name, and the CSV, Python and Stata of the rules and of the changes");
ok(!/href="data:/.test(first) && first.length < 190_000, `no file is held in the page as a link's address, and the table and the changes weigh ${Math.round(first.length / 1000)} thousand characters as they open`);
sound(first, "the table as it opens");

// ---- every rule drawn (the last rule of the order is opened, so every row before it is drawn)
const order = L.sortLines(L.lines(file), "utility", "asc"), last = order.at(-1);
const all = table({ rule: last.id });
const rowsHtml = all.slice(all.indexOf("<tbody>"), all.indexOf('id="large-load-changes"'));
ok(count(all, /data-llr-row="/g) === 122 && count(all, /data-llr-held="1"/g) >= 22, "with the last rule open, all 122 rules are drawn");
const cardBlanks = last.held ? 10 : L.FIELDS.filter((f) => ["withheld", "held"].includes(L.drawn(last.rule.fields[f], f).kind)).length;
const blanks = count(rowsHtml, /data-license-held="utility_large_load_rules"/g);
ok(blanks === 22 * 10 + 8 + cardBlanks, `the rules table draws ${blanks} blank cells that say license needed: 220 of the 22 held rows, 8 fields of public rows${cardBlanks ? `, ${cardBlanks} in the open rule` : ""}`);
ok(count(rowsHtml, /aria-label="[^"]*: license needed"/g) === blanks, "each blank cell names what it is and says license needed to a screen reader");
const heldRows = [...rowsHtml.matchAll(/<tr id="llr-row-[^"]+"[^>]*data-llr-held="1"[^>]*>([\s\S]*?)<\/tr>/g)].map((m) => m[1]);
ok(heldRows.length === 22 && heldRows.every((r) => count(r, /data-license-held=/g) === 10 && !/<a\b/.test(r) && !/data-llr-field=/.test(r)), "a held row is its utility, its state and its grid, and ten blank cells: no document, no value");
ok(count(all, /data-llr-opened="/g) === 1 && count(all, /data-rule-card="/g) === 1, "the open rule is drawn in full under its row");
sound(all, "the table with every rule drawn");

// ---- no value of a held research row is in anything the pages draw
const csvRows = (() => { const t = fs.readFileSync(new URL("../../docs/research/large_load/utilities_2026-11-13.csv", import.meta.url), "utf-8").split("\n").filter((l) => !l.startsWith("#")).join("\n");
  const out = []; let row = [], cell = "", q = false;
  for (let i = 0; i < t.length; i++) { const ch = t[i];
    if (q) { if (ch === '"' && t[i + 1] === '"') { cell += '"'; i++; } else if (ch === '"') q = false; else cell += ch; }
    else if (ch === '"') q = true; else if (ch === ",") { row.push(cell); cell = ""; } else if (ch === "\n") { row.push(cell); out.push(row); row = []; cell = ""; } else if (ch !== "\r") cell += ch; }
  const head = out[0]; return out.slice(1).filter((r) => r.length === head.length).map((r) => Object.fromEntries(head.map((k, i) => [k, r[i]]))); })();
const publicText = JSON.stringify(file.rules);
const drawnText = text(all) + text(table({ status: "held" }));
let searched = 0, leaked = [];
for (const r of csvRows) {
  const internal = r.license === "internal";
  const cols = internal ? [...L.FIELDS.flatMap((f) => [f, `${f}_cite`]), "rule_name", "quoted_clause", "notes"] : (r.internal_fields ?? "").split(";").filter(Boolean).flatMap((f) => [f, `${f}_cite`]);
  for (const c of cols) {
    const v = (r[c] ?? "").trim();
    if (v.length < 40 || /^(not published|held:|see row:|searched:)/.test(v) || publicText.includes(JSON.stringify(v).slice(1, -1))) continue;
    searched++;
    if (drawnText.includes(v.replace(/\s+/g, " "))) leaked.push(`${r.row_id} ${c}`);
  }
}
ok(csvRows.length === 122 && searched > 100 && !leaked.length, `${searched} values and cites of held rows and withheld fields, searched for in the drawn pages: none found${leaked.length ? ` (found: ${leaked.slice(0, 3).join(", ")})` : ""}`);

// ---- the filters, as the address sets them
const tx = table({ state: "TX" });
// session 7204: the State filter chooses the changes too
const txChanges = L.filterChanges(file.changes, [], ["TX"]).length;
ok(txChanges > 0 && text(tx).includes(`${txChanges} of 94 changes, TX (the State filter above;`) && count(tx.slice(tx.indexOf('id="large-load-changes"')), /data-llr-change="[^"]+" data-llr-held="1"/g) === 0, `the rules' State filter chooses the changes too: ${txChanges} of Texas, and no held change's row (its state is not known) is drawn`);
ok(count(tx, /data-llr-row="/g) === L.largeLoadStat(file, "largeload|rules|state|TX") && text(tx).includes(`${L.largeLoadStat(file, "largeload|rules|state|TX")} of 122 rules shown (TX)`), "the address's state sets the filter: the rules of Texas, public and held");
const held = table({ status: "held" });
ok(count(held, /data-llr-row="/g) === 12 && text(held).includes("22 of 122 rules shown (license needed)"), "the status filter's held choice shows the 22 rows held for a license");
const dom = table({ find: "dominion" });
ok(count(dom, /data-llr-row="/g) >= 1 && [...dom.matchAll(/data-llr-open="[^"]+"[^>]*>([^<]+)</g)].length >= 1, "a utility is found by name");
const byDate = table({ sort: "date", dir: "desc" });
const dates = [...byDate.slice(0, byDate.indexOf('id="large-load-changes"')).matchAll(/<td class="whitespace-nowrap[^"]*">(\d{4}-\d{2}(?:-\d{2})?)<\/td>/g)].map((m) => m[1]);
ok(dates.length >= 10 && dates.every((d, i) => i === 0 || dates[i - 1] >= d) && byDate.includes('aria-sort="descending"'), "sorted by date, latest first, and the heading says so");

// ---- A and B
const pub = file.rules.find((r) => r.id === "dominion-01") ?? file.rules[0], heldRule = file.held_rules[0];
const ab = table({ a: pub.id, b: heldRule.id });
const abHtml = ab.slice(ab.indexOf('data-llr-ab="1"'), ab.indexOf('data-llr-filters="1"'));
ok(ab.includes('data-llr-ab="1"') && abHtml.includes(`A: ${pub.utility}`.replace(/&/g, "&amp;")) && count(abHtml, /data-license-held=/g) === 10, "A and B side by side: a public rule whole beside a held one, whose ten cells are blank");
const long = L.FIELDS.map((f) => pub.fields[f]).find((c) => c.kind === "value" && c.v.length > 140);
ok(!long || text(abHtml).includes(long.v.replace(/\s+/g, " ")), "in A and B a field is the document's words whole, not cut");
ok(count(table({ a: pub.id }), /data-llr-ab-head="B">B: none chosen/g) === 1, "one rule chosen: B says none chosen");
sound(ab, "A and B");

// ---- the changes
const changesHtml = first.slice(first.indexOf('id="large-load-changes"'));
ok(count(changesHtml, /data-llr-change="/g) === 12 + 4 && count(changesHtml, /data-license-held="utility_large_load_rule_changes"/g) === 16 && text(changesHtml).includes("94 of 94 changes"), "the changes open on the newest 12 of 94, and the 4 held are drawn blank (16 cells)");
ok(count(changesHtml, /data-llr-region="/g) === 6 && L.CHANGE_GROUPS.every(([k, w]) => text(changesHtml).includes(`${w} (${L.largeLoadStat(file, `largeload|changes|group|${k}`)})`)), "the regions, each with its count");
const south = table({ region: "south_changes" });
ok(text(south).includes(`${L.largeLoadStat(file, "largeload|changes|group|south_changes")} of 94 changes, South`), "the address's region sets the changes' filter");
const firstChange = file.changes[0];
ok(changesHtml.includes(`data-llr-change="${firstChange.id}"`) && text(changesHtml).includes(firstChange.what.replace(/\s+/g, " ")) && changesHtml.includes(`href="${firstChange.url.replace(/&/g, "&amp;")}"`), "the newest change is first, with what happened in the document's words and its document linked");
ok(count(first, /data-llr-affects="/g) >= 5, "a change names the rule it changed as a button that opens it");

// ---- a rule in full, and a held one
const card = renderToStaticMarkup(h(RuleCard, { rule: pub }));
ok(L.FIELDS.every((f) => { const c = pub.fields[f]; return c.kind !== "value" || (text(card).includes(c.v.replace(/\s+/g, " ")) && text(card).includes(c.cite.replace(/\s+/g, " ").slice(0, 60))); }) && card.includes(`href="${pub.url.replace(/&/g, "&amp;")}"`), "a rule in full: every field whole, its cite in its hover, its document linked");
ok(text(card).includes("Upgrades") && text(card).includes("no column") && card.includes('data-llr-notes="1"') === !!pub.notes, "who pays for the upgrades is written as no column; the ERW's notes are a hover");
const heldCard = renderToStaticMarkup(h(HeldCard, { rule: heldRule }));
ok(count(heldCard, /data-license-held=/g) === 10 && !/<a\b/.test(heldCard), "a held rule in full: ten blank cells");
sound(card + heldCard, "a rule's card");

// ---- the section: its counts, and the panel a row of the tab opens
const x = S.sitingInputs({});
const section = renderToStaticMarkup(h(LargeLoadSection, { q: { llrow: "ercot:LZ_AEN" }, x }));
const keys = [...section.matchAll(/data-check="(largeload\|[^"]+)" data-raw="([^"]+)"/g)];
ok(keys.length >= 9 && keys.every(([, k, raw]) => Number(raw) === L.largeLoadStat(file, k)), `the section's ${keys.length} counts are each the file's (${keys.slice(0, 3).map(([, k, r]) => `${k}=${r}`).join(", ")}, ...)`);
ok(section.includes('id="large-load-rules"') && section.includes('id="large-load-rule"') && section.includes('data-llr-row-panel="ercot:LZ_AEN"'), "the section and the row's panel carry the anchors the tab's cells link to");
const panel = section.slice(section.indexOf('data-llr-row-panel='), section.indexOf('data-llr-table="1"'));
ok(["texas-06", "texas-02", "texas-01"].every((id) => panel.includes(`data-rule-card="${id}"`)) && panel.includes('data-llr-none="14626"') && /data-llr-unread="\d+"/.test(panel), "ERCOT's Austin zone opens Austin Energy's and Oncor's rules, the Commission's rule for every utility, Pedernales with no rule found, and the cooperative not read");
ok(panel.includes(`data-check="largeload|rules|state|TX"`) && text(panel).includes("Every rule read in TX"), "the panel counts the rules read in the state and links to them");
ok(section.length < 420_000, `the section with a row's panel open weighs ${Math.round(section.length / 1000)} thousand characters`);
sound(section, "the section with a row's panel");
const plain = renderToStaticMarkup(h(LargeLoadSection, { q: {}, x }));
ok(!plain.includes("data-llr-row-panel") && plain.length < 260_000, `with no row opened the section draws no panel and weighs ${Math.round(plain.length / 1000)} thousand characters`);

// ---- the line each hub row's two cells draw
const hubs = S.hubRows(SITING_FILES.index);
const tally = { opens: 0, state: 0, found: 0, read: 0, grid: 0 };
let bad = [];
for (const r of hubs) {
  const rr = rulesOfRow(r);
  const u = renderToStaticMarkup(h(RuleLine, { r, x, cell: "utility" })), c = renderToStaticMarkup(h(RuleLine, { r, x, cell: "connect" }));
  // session 7203: a grid's one row (PJM) opens the rules read across the grid, not one county's utility's
  if (r.kind === "grid") { tally.grid++; if (![u, c].every((s) => s.includes(`llrow=${encodeURIComponent(r.id)}#large-load-rule`) && /\d+ large-load rules in PJM/.test(s))) bad.push(r.id); continue; }
  const has = rr.own.length + rr.statewide.length > 0;
  if (rr.own.length) tally.opens++; else if (rr.statewide.length) tally.state++; else if (rr.none.length) tally.found++; else tally.read++;
  const linkOk = has ? [u, c].every((s) => s.includes(`llrow=${encodeURIComponent(r.id)}#large-load-rule`)) : [u, c].every((s) => /no large-load rule (found|read)/.test(s) && !s.includes("llrow="));
  // the connect cell says whose rule it opens: a utility's, or the state's where only a rule for every utility was read
  const whose = has && !rr.own.length ? "state" : "utility";
  if (!linkOk || !u.includes('data-llr="cell"') || !text(c).trim().startsWith(`${whose}: `)) bad.push(r.id);
}
ok(hubs.length === 48 && !bad.length, `each of the ${hubs.length} hub and zone rows draws its rule line in both cells: ${tally.opens} open a utility's rule, ${tally.state} the state's rule alone, ${tally.found} say no rule found, ${tally.read} no rule read, ${tally.grid} is a grid's one row and opens the grid's rules${bad.length ? `; wrong: ${bad.join(", ")}` : ""}`);
ok(tally.opens >= 15 && tally.grid === 1 && tally.opens + tally.state + tally.found + tally.read + tally.grid === 48, "the tally sums to the rows");

// ---- the states' laws in the monitor
const byState = (rows) => { const o = {}; for (const r of rows) for (const s of L.statesOf(r.state)) o[s] = (o[s] ?? 0) + 1; return o; };
const lawsProp = { laws: file.laws, held: file.held_laws, built: file.built, retrieved: file.retrieved, searches: file.law_searches,
  rules: byState([...file.rules, ...file.held_rules]), changes: byState(file.changes) };
const laws = renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: [], clearStates: () => {} }));
ok(laws.includes('id="large-load-laws"') && count(laws, /data-law="/g) === 28 && count(laws, /data-law-held="1"/g) === 1 && count(laws, /data-license-held="state_large_load_laws"/g) === 4, "the 27 laws and bills and the 1 held, whose four cells are blank");
const lawKeys = [...laws.matchAll(/data-check="(largeload\|[^"]+)" data-raw="([^"]+)"/g)];
ok(lawKeys.length >= 8 && lawKeys.every(([, k, raw]) => Number(raw) === L.largeLoadStat(file, k)), `the laws' ${lawKeys.length} counts are each the file's`);
ok(file.laws.every((l) => laws.includes(`href="${l.url.replace(/&/g, "&amp;")}"`) && L.requirementsOf(l).every((p) => laws.includes(`data-law-topic="${p.topic}"`))), "every law links its own text, and each requirement is a topic with its words and cite on hover");
const md = renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: ["MD"], clearStates: () => {} }));
ok(count(md, /data-law="/g) === 2 && text(md).includes("2 of 28 shown (the State filter: MD;"), "the monitor's State filter chooses the laws: Maryland's two");
// session 7204 (the read of /policy): a state with no row is never "no law": what the research found, or did not reach
const txLaws = renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: ["TX"], clearStates: () => {} }));
ok(text(txLaws).includes("TX: S.B. 6, read and not shown") && txLaws.includes('data-law-withheld="TX"') && count(txLaws, /data-not-shown="state_large_load_laws"/g) === 4 && count(txLaws, /aria-label="[^"]*: not shown"/g) === 4 && !/was read for/.test(text(txLaws)),
  "Texas: S.B. 6 is a row, the bill named and its four cells blank, not shown; the page does not say no law was read");
ok(!txLaws.includes("data-license-held"), "a bill withheld for a robots file is not called license needed");
const gaAz = renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: ["GA", "AZ", "HI"], clearStates: () => {} }));
const said = [...gaAz.matchAll(/data-law-search="([^"]+)" data-law-search-state="([A-Z]{2})"/g)].map((m) => `${m[2]} ${m[1]}`).join("; ");
ok(said === "GA not read; AZ none found; HI not searched" && ["GA: ", "AZ: ", "HI: "].every((w) => text(gaAz).includes(w)) && !gaAz.includes("<table"), "Georgia not read, Arizona none found where searched, Hawaii not searched: each in place, with no table drawn");
ok(text(txLaws).includes(`The utilities' own large-load rules: ${L.largeLoadStat(file, "largeload|rules|state|TX")} in TX`) && txLaws.includes('href="/cost-of-power?view=allgrids&amp;rstate=TX#large-load-rules"') && /\(\d+ changes? in the last 90 days\)/.test(text(txLaws)), "a chosen state links its utilities' own rules on the All grids tab, with their count and the changes'");
ok(count(laws, /data-law-withheld="TX"/g) === 1 && laws.includes('data-laws-searched="22"') && count(laws, /data-law-search-state="/g) === 22 && laws.includes('data-laws-rules="all"'), "with no state chosen: Texas's withheld bill is a row, and one line names the 22 states with no row and what the read found in each");
ok(!/href="data:/.test(laws) && laws.length < 220_000, `the laws weigh ${Math.round(laws.length / 1000)} thousand characters`);
sound(laws, "the laws");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
