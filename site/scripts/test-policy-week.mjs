// Energy Research Warehouse (ERW) site, session 157: the pure functions of "What changed this week", the second view of
// the policy monitor (/policy?view=week; lib/policyweek.ts). No request, no browser, no model.
//
//   node --import ./scripts/alias-register.mjs scripts/test-policy-week.mjs
//   node --import ./scripts/alias-register.mjs scripts/test-policy-week.mjs --cases <file> [<rule file>]   (the tag rule only)
//
// THE ROWS BELOW ARE MADE UP FOR THIS TEST: no agency's action, regulator, docket, date, sentence or read in this file
// is real, and none of it is in any file the site ships (the page reads the live set and data/policy/*.json and nothing
// else). They are shaped as the contract between the warehouse's builder and the page states
// (runs/session157/CONTRACT.md). The tag rule itself is the real one where data/policy/tag_rules.json is on the machine.
//
//   1. the two views and the address: anything but view=week is the page as it was; a choice the view does not know is
//      no choice; the address of a choice restores it;
//   2. the windows: seven and thirty days counted back from today, both ends stated;
//   3. the tag rule: whole words in order, the stripped names, the exclusions, the listed dockets, the municipal rule;
//      the rule's own answers on the warehouse's cases (tests/fixtures/session157/policy_tag_cases.json) and, where it
//      is on the machine, on every action of the table held (runs/session157/policy_tag_cases_full.json);
//   4. the page's tags are the rule's on the row read, united with the file's;
//   5. the grid an action is under: a named operator, a listed docket's, or every grid when it names none;
//   6. the agency filter: the regulators and agencies in order, a refusing regulator's mark with the file's reason word
//      for word, nothing outside federal and state;
//   7. a row: the status as the source words it or its type, the link's words and hover, the read marked as a model's
//      with the recheck's words, "no read yet"; a docket row's sentence or the phrase in its place; what is not shown;
//   8. the filters: agency, topic, grid and large loads; MISO shows no row; a row under MISO alone is under no grid;
//   9. the chart's counts and the words a count answers the mouse with;
//  10. where the site's files are on the machine: what the view makes of them.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const W = await import("../lib/policyweek.ts");

let failed = 0, n = 0;
const ok = (cond, what) => { n += 1; console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed += 1; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const json = (...parts) => { const p = path.join(here, ...parts); return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : null; };

// --cases <file> [<rule file>]: only the tag rule, on a file of cases of the contract's shape ({ cases: [{ ..., expect }] });
// prints one JSON line (tests/test_session157_page.py gives it the Python rule's answers on every action of the table held)
if (process.argv[2] === "--cases") {
  const rules = JSON.parse(fs.readFileSync(process.argv[4] ?? path.join(here, "..", "data", "policy", "tag_rules.json"), "utf8"));
  const file = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
  const wrong = file.cases.filter((c) => !same(W.tagAction(c, rules), c.expect));
  console.log(JSON.stringify({ cases: file.cases.length, tagged: file.cases.filter((c) => W.tagAction(c, rules).length).length, differ: wrong.length, first: wrong.slice(0, 5).map((c) => c.event_id), version: rules.version }));
  process.exit(wrong.length ? 1 : 0);
}

// MADE UP: a small rule of the real file's shape, for the tests that must not depend on the real terms
const RULE = {
  version: "0", fields_matched: ["title", "abstract", "first_paragraph"], strip: ["made-up interconnection, l.l.c."],
  agencies_in_scope: { federal: ["MUA", "MUB"], state: ["MUS"] }, action_types_in_scope: ["rule", "notice"],
  municipal: { terms: ["zoning", "city council", "building permit"] },
  tags: {
    large_load: { what: "Made-up meaning.", terms: [{ term: "large load" }, { term: "data centers" }], exclude_any: ["large electric generating unit"], exclude_docket_prefix: [] },
    interconnection: { what: "Made-up meaning.", terms: [{ term: "interconnection" }], exclude_any: ["pipeline"], exclude_docket_prefix: ["CP"], exclude_docket_contains: ["-LNG"] },
    transmission_cost: { what: "Made-up meaning.", terms: [{ term: "formula rate", needs_any: ["transmission service"] }], exclude_any: [], exclude_docket_prefix: [] },
  },
  dockets: { max_dockets_in_a_notice: 3, list: [{ docket: "ZZ26-67", tags: ["large_load", "interconnection"], grids: ["PJM"] }, { docket: "ZZ26-4", tags: ["large_load"], grids: [] }] },
};
// MADE UP: an action of policy_actions' shape
const action = (id, date, more = {}) => ({
  event_id: id, event_date: date, status: "Made-up notice.", source_url: `https://example.invalid/fr/${id}`, agency: "MUA", action_type: "notice", title: `Made-up title ${id}`, abstract: null,
  docket: "", fr_document_number: "", why: null, model_id: null, ...more,
});
// MADE UP: a docket row of state_rules.json's shape
const docket = (id, date, more = {}) => ({
  id, date, regulator: "Made-up Commission", regulator_key: "mucc", jurisdiction: "state", state: "ZZ", docket: `MU-${id}`, title: "", row_kind: "order", topics: ["large-load tariff"], large_load: true,
  status_as_worded: null, status_class: "decided", url: `https://example.invalid/doc/${id}.pdf`, page: 2, sentence: null, sentence_withheld: "The Made-up Commission's terms ask permission to copy its text; open the document",
  sentence_from: "order text", sentence_kind: "document", flags: [], terms_class: "restricted", read: null, read_by: null, read_model: null, read_from: null, grids: ["ercot"], all_grids: false, why_here: "made-up mapping", in_motion: true, ...more,
});
const GRIDS = { grids: [
  { key: "ercot", name: "ERCOT", words: ["ERCOT", "Electric Reliability Council of Texas"] }, { key: "pjm", name: "PJM", words: ["PJM"] }, { key: "miso", name: "MISO", words: ["MISO", "Midcontinent Independent System Operator"] },
  { key: "caiso", name: "CAISO", words: ["CAISO"] }, { key: "nyiso", name: "NYISO", words: ["NYISO"] }, { key: "isone", name: "ISO-NE", words: ["ISO-NE", "ISO New England"] }, { key: "spp", name: "SPP", words: ["SPP", "Southwest Power Pool"] },
] };
const REFRESH = {
  regulators: [
    { key: "mufed", regulator: "Made-up Federal Commission", short: "MUA", agency: "MUA", jurisdiction: "federal", refreshed: true, list_name: "a made-up list", reason: null, refused: [{ host: "example.invalid", what: "a browser check" }] },
    { key: "mucc", regulator: "Made-up Commission", short: "Made-up CC", agency: "MUS", jurisdiction: "state", refreshed: true, list_name: "a made-up docket list", reason: null, refused: [] },
    { key: "muno", regulator: "Made-up Refusing Commission", short: "Refusing CC", agency: null, jurisdiction: "state", refreshed: false, list_name: "a made-up docket system", reason: "Not refreshed: its made-up docket system answers with a CAPTCHA.", refused: [{ host: "example.invalid", what: "a CAPTCHA" }] },
    { key: "mucity", regulator: "Made-up City Board", short: "City", agency: null, jurisdiction: "municipal", refreshed: true, reason: null, refused: [] },
  ],
  federal_feeds: [{ agency: "MUA", name: "Made-up Federal Commission", list_name: "a made-up feed", refreshed: true, reason: null }, { agency: "MUB", name: "Made-up Department", list_name: "a made-up feed", refreshed: true, reason: null },
    { agency: "MUB", name: "Made-up Department", list_name: "its own made-up pages", refreshed: false, reason: "Not refreshed: its own made-up pages answer with a browser check" }],
};
const TODAY = "2026-10-08";

// 1. the two views and the address
ok(W.viewOf({}) === "all" && W.viewOf({ view: "week" }) === "week" && W.viewOf({ view: "WEEK" }) === "all" && W.viewOf({ view: "anything" }) === "all", "anything but view=week is the page as it was");
ok(W.viewHref("all") === "/policy" && W.viewHref("week") === "/policy?view=week" && same(W.VIEWS.map((v) => v[0]), ["all", "week"]), "two views, each with its address");
{
  const known = { bodies: ["mufed", "mucc"], topics: ["large_load", "large-load-tariff"], grids: ["ercot", "pjm", "miso"] };
  ok(same(W.chosenOf({}, known), { days: 7, agency: "", topic: "", grid: "", large: false }), "an address with no choice: seven days and no filter");
  const c = W.chosenOf({ view: "week", days: "30", agency: "MUCC", topic: "large_load", grid: "miso", large: "1" }, known);
  ok(same(c, { days: 30, agency: "mucc", topic: "large_load", grid: "miso", large: true }), "an address's choices are read, in any case");
  ok(W.weekHref(c) === "/policy?view=week&days=30&agency=mucc&topic=large_load&grid=miso&large=1", "the address of a choice, in one fixed order");
  const back = Object.fromEntries(new URL(`https://example.invalid${W.weekHref(c)}`).searchParams);
  ok(same(W.chosenOf(back, known), c), "the address restores the choice");
  ok(same(W.chosenOf({ days: "365", agency: "nobody", topic: "zoning", grid: "mars", large: "yes" }, known), W.NOTHING), "a choice the view does not know is no choice");
  ok(W.weekHref(W.NOTHING) === "/policy?view=week", "no choice: the view's plain address");
}

// 2. the windows
ok(same([...W.WINDOWS], [7, 30]) && W.sinceDay(TODAY, 7) === "2026-10-01" && W.sinceDay(TODAY, 30) === "2026-09-08" && W.sinceDay("2026-03-05", 7) === "2026-02-26", "seven and thirty days counted back from today, across a month's end");
ok(W.inWindow("2026-10-01", TODAY, 7) && !W.inWindow("2026-09-30", TODAY, 7) && W.inWindow("2026-09-30", TODAY, 30) && !W.inWindow("2026-09-07", TODAY, 30) && W.inWindow("2026-10-09", TODAY, 7) && !W.inWindow("", TODAY, 30) && !W.inWindow("soon", TODAY, 30),
  "a row is of a window from its first day on; a row with no day is of none");
ok(W.windowWhy(TODAY, 7).includes("1 Oct 2026") && W.windowWhy(TODAY, 7).includes("8 Oct 2026") && W.windowWhy(TODAY, 30).includes("8 Sep 2026"), "the window's hover states both of its ends");
ok(W.dayOf(Date.UTC(2026, 9, 8, 23, 59)) === "2026-10-08", "today is a UTC day");

// 3. the tag rule
{
  const t = (more) => W.tagAction({ agency: "MUA", action_type: "notice", title: "", abstract: "", docket: "", ...more }, RULE);
  ok(same(t({ title: "Made-up notice on Large-Load service" }), [{ tag: "large_load", matched_term: "large load", matched_field: "title" }]), "a term matches as whole words in order, a hyphen read as a space, in any case");
  ok(same(t({ title: "Enlarge loads" }), []) && same(t({ title: "large loader" }), []), "a term does not match inside a longer word");
  ok(same(t({ title: "Made-up Interconnection, L.L.C.; notice" }), []) && t({ title: "Made-up Interconnection, L.L.C.; interconnection queue" }).length === 1, "a company's name is taken out before the terms are read");
  ok(same(t({ title: "Interconnection of a pipeline" }), []) && same(t({ title: "Interconnection", docket: "Docket No. CP26-1-000" }), []) && same(t({ title: "Interconnection", docket: "25-12-LNG" }), []), "a tag's exclusions: a phrase, a docket prefix, a docket's letters");
  ok(same(t({ abstract: "A formula rate." }), []) && same(t({ abstract: "A formula rate.", first_paragraph: "For transmission service." }).map((h) => [h.tag, h.matched_field]), [["transmission_cost", "abstract"]]), "a term that needs another beside it reads the other in any field");
  ok(same(t({ first_paragraph: "Service to data centers." }), [{ tag: "large_load", matched_term: "data centers", matched_field: "first_paragraph" }]), "the first paragraph of the printed text is read, after the title and the summary");
  ok(same(t({ title: "Large load", abstract: "Heard by the city council." }), []) && same(t({ title: "Large load rezoning" }), [{ tag: "large_load", matched_term: "large load", matched_field: "title" }]), "an action with a municipal phrase is never tagged (whole words, as the rule reads them)");
  ok(same(t({ title: "Large load", agency: "MUX" }), []) && same(t({ title: "Large load", action_type: "press_release" }), []), "an agency or a type outside the rule's scope is not tagged");
  ok(same(t({ title: "Parties' names only", docket: "Docket No. ZZ26-67-000" }).map((h) => [h.tag, h.matched_term, h.matched_field]), [["large_load", "ZZ26-67", "docket"], ["interconnection", "ZZ26-67", "docket"]]), "a listed docket gives its tags to a notice no term matches");
  ok(same(t({ title: "Names", docket: "Docket No. ZZ26-670-000" }), []) && same(t({ title: "Names", docket: "ZZ26-67-000;AA1-1;AA1-2;AA1-3" }), []), "a longer docket number is not the listed one; a notice of more than three dockets takes none");
  ok(same(W.docketPrefixes("Docket No. CP13-499-006;Docket No. EL26-67-000, Project No. 2731-046"), ["CP", "EL"]) && W.docketHolds("Docket No. EL26-67-000", "EL26-67") && !W.docketHolds("XEL26-67", "EL26-67"), "docket prefixes and whole docket numbers");
  ok(W.norm(`  Large${String.fromCharCode(0x2011)}Load ${String.fromCharCode(0x2014)} Tariff${String.fromCharCode(0xa0)}${String.fromCharCode(10)} Rules `) === "large load tariff rules", "every hyphen and dash is a space and white space is collapsed");
}
const REAL = json("..", "data", "policy", "tag_rules.json");
for (const [name, file, must] of [["the warehouse's cases", json("..", "..", "tests", "fixtures", "session157", "policy_tag_cases.json"), false], ["every action of the table held", json("..", "..", "..", "erw", "runs", "session157", "policy_tag_cases_full.json"), false]]) {
  if (!REAL || !file) { console.log(`skip ${name}: ${REAL ? "the cases are" : "data/policy/tag_rules.json is"} not on this machine${must ? " (FAIL)" : ""}`); continue; }
  const wrong = file.cases.filter((c) => !same(W.tagAction(c, REAL), c.expect));
  ok(String(file.rule_version) === String(REAL.version), `${name}: made with the rule's version ${REAL.version}`);
  ok(wrong.length === 0, `${name}: the page's rule gives the Python rule's tags on ${file.cases.length} actions (${file.cases.filter((c) => c.expect.length).length} tagged)${wrong.length ? `: ${wrong.slice(0, 3).map((c) => c.event_id).join(", ")}` : ""}`);
}

// 4. the page's tags
{
  const mine = [{ tag: "interconnection", matched_term: "interconnection", matched_field: "title" }, { tag: "large_load", matched_term: "large load", matched_field: "title" }];
  const file = [{ tag: "large_load", matched_term: "data centers", matched_field: "first_paragraph" }, { tag: "transmission_cost", matched_term: "formula rate", matched_field: "first_paragraph" }, { tag: "not_a_tag", matched_term: "x", matched_field: "title" }];
  const u = W.uniteTags(mine, file, RULE);
  ok(same(u.map((h) => h.tag), ["large_load", "interconnection", "transmission_cost"]) && u[0].matched_field === "first_paragraph", "the rule's tags on the row read, united with the file's, in the rule's order; the file's term is kept where both hold a tag");
  ok(same(W.uniteTags(mine, undefined, RULE).map((h) => h.tag), ["large_load", "interconnection"]) && same(W.uniteTags([], file, RULE).map((h) => h.tag), ["large_load", "transmission_cost"]), "a new action is tagged with no file; an older one keeps the file's tags");
}

// 5. the grid an action is under
{
  const g = (title, hits = [], more = {}) => W.gridsOfAction({ title, abstract: "", ...more }, hits, GRIDS, RULE);
  ok(same(g("Made-up notice of PJM Interconnection"), { grids: ["pjm"], all: false }) && same(g("Made-up order on ERCOT and the Southwest power pool"), { grids: ["ercot", "spp"], all: false }), "an action is under the operators its text names; a name of several words in any case");
  ok(g("Made-up notice on spp. and Pjm").all && g("XPJM and PJM2").all && g("Made-up notice on ISO-NE.").grids[0] === "isone", "a single word in its own case, standing on its own");
  ok(same(g("Parties' names", [{ tag: "large_load", matched_term: "ZZ26-67", matched_field: "docket" }]), { grids: ["pjm"], all: false }) && g("Parties' names", [{ tag: "large_load", matched_term: "ZZ26-4", matched_field: "docket" }]).all, "a listed docket that tagged it gives its grid; one that lists none gives none");
  ok(same(g("Made-up rule on reactors"), { grids: [], all: true }) && same(g("Made-up", [], { first_paragraph: "Filed by CAISO." }).grids, ["caiso"]), "an action that names no operator is under every grid; the first paragraph is read too");
}

// 6. the agency filter
const BODIES = W.bodiesOf(REFRESH, ["MUA", "MUS", "MUC"]);
{
  ok(same(BODIES.map((b) => b.key), ["mufed", "mub", "muc", "mucc", "muno"]), "federal first (the regulator, the feeds' agencies, an agency only the rows hold), then the state commissions; one choice a body");
  ok(!BODIES.some((b) => b.key === "mucity") && BODIES.every((b) => ["federal", "state"].includes(b.jurisdiction)), "nothing outside federal and state is ever a choice");
  const no = BODIES.find((b) => b.key === "muno"), fed = BODIES.find((b) => b.key === "mufed"), mub = BODIES.find((b) => b.key === "mub"), cc = BODIES.find((b) => b.key === "mucc"), muc = BODIES.find((b) => b.key === "muc");
  ok(no.mark.words === "not refreshed" && no.mark.why === REFRESH.regulators[2].reason, "a regulator whose list refuses a plain request keeps its place, marked, its hover the file's reason word for word");
  ok(fed.mark.words === "in part" && fed.mark.why === "example.invalid: a browser check." && fed.agency === "MUA", "a refreshed regulator with a host it never asks is marked in part, with what the host answered");
  ok(mub.mark.kind === "in part" && mub.mark.why.includes("browser check") && cc.mark === null && muc.mark === null && cc.agency === "MUS", "a federal agency with one feed of two not refreshed is marked in part; a body with nothing refused has no mark");
  ok(cc.why.includes("a made-up docket list") && !no.why.includes("Refreshed from"), "a body's hover names the list it is refreshed from, and none where it is not");
  ok(same(W.bodiesOf(null, ["MUA"]).map((b) => [b.key, b.mark]), [["mua", null]]), "with no refresh file the choices are the agencies of the rows");
}

// 7. a row
const TOPICS = W.topicsOf(RULE, ["large-load interconnection", "large-load tariff", "transmission cost allocation", "interconnection reform"]);
{
  ok(same(TOPICS.map((t) => t.key), ["large_load", "interconnection", "transmission_cost", "large-load-interconnection", "large-load-tariff", "transmission-cost-allocation", "interconnection-reform"]) && TOPICS[0].kind === "tag" && TOPICS[3].kind === "topic" && TOPICS[0].label === "Large loads",
    "the topics: the rule's tags, then the docket rows' topics, each with its own key");
  const mk = (a, read, hits = []) => W.actionRow(a, read, hits, { grids: [], all: true }, BODIES, TOPICS, RULE);
  const a1 = mk(action("a1", "2026-10-05T00:00:00+00:00", { abstract: "A made-up summary.", docket: "Docket No. ZZ26-1-000;MU-2026-1", fr_document_number: "2026-00001", why: "A made-up scorer line.", model_id: "made-up-scorer" }), null, [{ tag: "large_load", matched_term: "large load", matched_field: "abstract" }]).row;
  ok(a1.date === "2026-10-05" && a1.body === "mufed" && a1.kind === "action" && a1.status.words === "Made-up notice." && a1.status.stated, "an action: its day, its body, its status in the source's words");
  ok(a1.link.words === "MUA, Docket No. ZZ26-1-000" && a1.link.href === "https://example.invalid/fr/a1" && a1.link.hover === "abstract" && a1.link.tip.startsWith('"A made-up summary." The Federal Register\'s summary.') && a1.link.tip.includes("MU-2026-1") && a1.link.tip.includes("2026-00001"),
    "its link: the agency and the docket; the summary on hover, with the other numbers");
  ok(a1.read.line === "A made-up scorer line." && a1.read.why.startsWith("A model's read, by made-up-scorer") && a1.read.why.includes("Not the agency's words."), "with no impact read, the scorer's one line, marked as a model's with the model named");
  ok(same(a1.topics.map((t) => t.key), ["large_load"]) && a1.topics[0].why.includes('"large load" in the summary') && a1.largeLoad && a1.allGrids, "its tags with the term and the field each rests on; large-load relevance is the tag");
  const a2 = mk(action("a2", "2026-10-04", { status: "", action_type: "rule", fr_document_number: "2026-00002", model_recheck: "not rechecked" }), { action_event_id: "a2", plain_read: "A made-up impact line.", model_id: "made-up-reader", recheck: "rechecked", rechecked_at: "2026-10-08T10:00:00Z" }).row;
  ok(a2.status.words === "Final rule" && !a2.status.stated && a2.link.words === "MUA, FR Doc. 2026-00002" && a2.link.hover === "title" && a2.link.tip.includes("No summary of this document is held."), "no worded status: the document's type, as a placeholder; no summary: the title, said to be the title");
  ok(a2.read.line === "A made-up impact line." && a2.read.why.includes("by made-up-reader") && a2.read.why.endsWith("Rechecked against the source text on 8 Oct 2026."), "the impact read comes first, with the recheck's words on its hover");
  ok(W.recheckWords("not rechecked", "") === "Not rechecked against the source text." && W.recheckWords("source not reachable", null) === "Source not reachable when rechecked." && W.recheckWords(undefined, undefined) === "" && W.recheckWords("anything else", "") === "", "the recheck's three sayings, and nothing where the row holds none");
  const a3 = mk(action("a3", "2026-10-03", { first_paragraph: "A made-up first paragraph." })).row;
  ok(a3.read.line === null && a3.read.why.length > 0 && a3.link.hover === "first paragraph" && a3.topics.length === 0 && !a3.largeLoad, "no read: the placeholder's reason; no summary: the first paragraph of the printed text, named");
  ok(mk(action("a4", "2026-10-03", { source_url: "javascript:alert(1)" })).dropped.why === "no address of a source document" && mk(action("a5", "", {})).dropped.why === "no day" && mk(action("a6", "2026-10-03", { agency: "MUNICIPAL" })).dropped.why.includes("scope"),
    "an action with no address, no day or an agency that is no choice is not shown, with why");
  ok(mk(action("a7", "2026-10-03", { title: "Made-up rezoning hearing" })).row === null && mk(action("a8", "2026-10-03", { why: "Goes to the City Council next." })).dropped.why.includes("outside this page's scope") && mk(action("a9", "2026-10-03", { title: "Construction permit" })).row !== null,
    "a row with a municipal phrase on its face or on hover is not shown; a federal construction permit is");
  ok(W.municipalPhrase("County Board of made-up", { municipal: { terms: [] } }) === "county board" && W.municipalPhrase("a federal permit", RULE) === null && same([...W.MUNICIPAL], ["zoning", "city council", "county board"]), "three phrases are out of scope with or without the rule file");
  const d1 = W.docketRow(docket("d1", "2026-10-02"), BODIES, TOPICS, RULE).row;
  ok(d1.kind === "docket" && d1.body === "mucc" && d1.status.words === "decided" && d1.link.words === "Made-up Commission, MU-d1" && d1.link.hover === "withheld" && d1.link.tip.startsWith("The Made-up Commission's terms ask permission") && !d1.link.tip.includes('"'),
    "a docket row of a restricted regulator: its class as status, the file's phrase in place of the sentence, no sentence made");
  ok(d1.read.line === null && same(d1.topics.map((t) => t.key), ["large-load-tariff"]) && d1.largeLoad && same(d1.grids, ["ercot"]) && !d1.allGrids && d1.titleWhy === "made-up mapping", "its topics, its grid and its placeholder read");
  const d2 = W.docketRow(docket("d2", "2026-10-01", { sentence: "Made-up sentence of the order.", sentence_withheld: null, status_as_worded: "Made-up status", read: "Made-up line.", read_by: "model", read_model: "made-up-model", read_from: "the sentence" }), BODIES, TOPICS, RULE).row;
  ok(d2.link.hover === "sentence" && d2.link.tip.startsWith('"Made-up sentence of the order."') && d2.status.words === "Made-up status" && d2.read.line === "Made-up line." && d2.read.why.includes("made-up-model"), "a docket row whose text may be copied: its sentence, its worded status, its read marked as a model's");
  ok(W.docketRow(docket("d3", "2026-10-01", { read: "Made-up line.", read_by: "person" }), BODIES, TOPICS, RULE).row.read.line === null, "a line the file does not mark as a model's is not shown");
  ok(W.docketRow(docket("d4", "2026-10-01", { sentence_withheld: null }), BODIES, TOPICS, RULE).dropped.why.startsWith("neither a sentence") && W.docketRow(docket("d5", "2026-10-01", { regulator_key: "nobody" }), BODIES, TOPICS, RULE).row === null
    && W.docketRow(docket("d6", "2026-10-01", { jurisdiction: "municipal" }), BODIES, TOPICS, RULE).dropped.why.includes("scope") && W.docketRow(docket("d7", "2026-10-01", { url: "" }), BODIES, TOPICS, RULE).row === null,
    "a docket row with neither sentence nor phrase, an unlisted regulator, a body outside the scope or no address is not shown");
  ok(W.droppedTip([{ id: "x1", why: "no day" }, { id: "the zoning row", why: "a phrase of it is outside this page's scope" }], RULE) === "Not shown: x1 (no day); a row (a phrase of it is outside this page's scope).", "the count of rows not shown says each with why, and never a municipal phrase");
}

// 8. the filters
const mkA = (id, date, more = {}, hits = [], under = { grids: [], all: true }) => W.actionRow(action(id, date, more), null, hits, under, BODIES, TOPICS, RULE).row;
const ROWS = [
  mkA("f1", "2026-10-07", {}, [{ tag: "large_load", matched_term: "large load", matched_field: "title" }]),
  mkA("f2", "2026-10-02", { agency: "MUB" }, [{ tag: "interconnection", matched_term: "interconnection", matched_field: "title" }], { grids: ["pjm"], all: false }),
  mkA("f3", "2026-09-20", {}, [], { grids: ["miso"], all: false }),
  mkA("f4", "2026-09-10", { agency: "MUB" }, [{ tag: "large_load", matched_term: "large load", matched_field: "title" }, { tag: "interconnection", matched_term: "interconnection", matched_field: "title" }], { grids: ["pjm", "miso"], all: false }),
  W.docketRow(docket("s1", "2026-10-03"), BODIES, TOPICS, RULE).row,
  W.docketRow(docket("s2", "2026-09-15", { grids: [], topics: ["interconnection reform", "large-load tariff"] }), BODIES, TOPICS, RULE).row,
  mkA("f5", "2026-08-01"),
];
{
  const ids = (c) => W.shownRows(ROWS, { ...W.NOTHING, ...c }, TODAY).map((r) => r.id);
  ok(same(ids({}), ["f1", "s1", "f2"]) && same(ids({ days: 30 }), ["f1", "s1", "f2", "f3", "s2", "f4"]), "the rows of seven days and of thirty, newest first; an older row is in neither");
  ok(same(ids({ days: 30, agency: "mub" }), ["f2", "f4"]) && same(ids({ days: 30, agency: "mucc" }), ["s1", "s2"]) && same(ids({ days: 30, agency: "muno" }), []), "the agency filter");
  ok(same(ids({ days: 30, topic: "interconnection" }), ["f2", "f4"]) && same(ids({ days: 30, topic: "large-load-tariff" }), ["s1", "s2"]) && same(ids({ days: 30, topic: "interconnection-reform" }), ["s2"]), "the topic filter: a tag, and a docket row's topic");
  ok(same(ids({ days: 30, grid: "pjm" }), ["f1", "f2", "f4"]) && same(ids({ days: 30, grid: "ercot" }), ["f1", "s1"]), "the grid filter: the rows that name the grid, and the actions that name no operator");
  ok(same(ids({ days: 30, grid: "miso" }), []) && W.paused("miso") && !W.paused("pjm") && W.PAUSED_WORDS === "paused while terms are reviewed" && W.PAUSE_WHY.startsWith("MISO's terms forbid automated access"), "MISO shows the fixed words and no row");
  ok(["ercot", "pjm", "caiso", "nyiso", "isone", "spp", "miso"].every((g) => !ids({ days: 30, grid: g }).includes("f3")) && ids({ days: 30 }).includes("f3") && ["ercot", "pjm", "caiso"].every((g) => !ids({ days: 30, grid: g }).includes("s2")),
    "a row under MISO alone is under no grid's filter and is listed with no grid chosen; a docket row on no grid likewise");
  ok(same(ids({ days: 30, large: true }), ["f1", "s1", "s2", "f4"]), "large loads only: the actions tagged large loads and the docket rows of the large-load tables");
  ok(same(ids({ days: 30, agency: "mub", topic: "large_load", grid: "pjm", large: true }), ["f4"]) && same(ids({ agency: "mub", topic: "large_load" }), []), "the filters hold together; a choice that leaves nothing leaves nothing");
  const groups = W.groupsOf(W.shownRows(ROWS, { ...W.NOTHING, days: 30 }, TODAY), BODIES);
  ok(same(groups.map((g) => [g.body.key, g.rows.map((r) => r.id)]), [["mufed", ["f1", "f3"]], ["mub", ["f2", "f4"]], ["mucc", ["s1", "s2"]]]), "the list in groups by agency, in the filter's order, no row lost and none twice");
  ok(W.emptyWhy({ days: 7, agency: "mub", topic: "large_load", grid: "pjm", large: true }, TODAY, BODIES, TOPICS, { pjm: "PJM" }) === "No action of MUB on large loads under PJM that touches large loads is held that is dated 1 Oct 2026 or later.", "the placeholder of a choice that leaves nothing says what was chosen and since when");
}

// 9. the chart
{
  const c30 = W.countsOf(ROWS, { ...W.NOTHING, days: 30, agency: "mub", topic: "interconnection" }, TODAY, BODIES, TOPICS);
  const line = (k) => c30.lines.find((l) => l.body.key === k);
  const at = (k, t) => line(k).byTopic[TOPICS.findIndex((x) => x.key === t)];
  ok(same(c30.lines.map((l) => [l.body.key, l.total, l.none]), [["mufed", 2, 1], ["mub", 2, 0], ["mucc", 2, 0]]) && c30.total === 6, "one line an agency that holds a row, whatever agency and topic are chosen");
  ok(at("mub", "interconnection") === 2 && at("mub", "large_load") === 1 && at("mufed", "large_load") === 1 && at("mucc", "large-load-tariff") === 2 && at("mucc", "interconnection-reform") === 1 && c30.max === 2, "a count a topic; an action with two topics counts under each");
  const pjm = W.countsOf(ROWS, { ...W.NOTHING, days: 30, grid: "pjm" }, TODAY, BODIES, TOPICS);
  ok(same(pjm.lines.map((l) => [l.body.key, l.total]), [["mufed", 1], ["mub", 2]]) && W.countsOf(ROWS, { ...W.NOTHING, days: 30, grid: "miso" }, TODAY, BODIES, TOPICS).lines.length === 0 && W.countsOf(ROWS, { ...W.NOTHING, large: true }, TODAY, BODIES, TOPICS).total === 2, "the counts follow the window, the grid and the large-load choice; MISO counts nothing");
  ok(W.cellTip(line("mub"), TOPICS[1], 2, 30) === "MUB: 2 actions tagged interconnection in the last 30 days" && W.cellTip(line("mucc"), TOPICS[4], 1, 7) === "Made-up CC: 1 action on large-load tariff in the last 7 days" && W.cellTip(line("mufed"), null, 2, 30) === "MUA: 2 actions in all in the last 30 days", "a count answers the mouse with the agency, the number, the topic and the window");
}

// 10. the site's files, where they are on the machine
{
  const refresh = json("..", "data", "policy", "refresh.json"), state = json("..", "data", "policy", "state_rules.json"), grids = json("..", "data", "policy", "grids.json"), tags = json("..", "data", "policy", "action_tags.json");
  if (!REAL) console.log("skip the site's files: data/policy/tag_rules.json is not on this machine");
  else {
    ok(same(Object.keys(REAL.tags), ["large_load", "interconnection", "transmission_cost", "tax_credit"]) && REAL.fields_matched.includes("title") && REAL.fields_matched.includes("abstract"), `the rule file: four tags, read in ${REAL.fields_matched.join(", ")} (version ${REAL.version})`);
    if (grids) ok(same(grids.grids.map((g) => g.key), ["ercot", "pjm", "miso", "caiso", "nyiso", "isone", "spp"]) && same(grids.grids.map((g) => g.name), ["ERCOT", "PJM", "MISO", "CAISO", "NYISO", "ISO-NE", "SPP"]), "grids.json: the seven grids, in the contract's order");
    else console.log("skip grids.json: not on this machine");
    if (refresh) {
      const bodies = W.bodiesOf(refresh, []);
      const off = refresh.regulators.filter((r) => r.refreshed === false);
      ok(refresh.regulators.length === 11 && refresh.regulators.every((r) => bodies.some((b) => b.key === r.key)) && bodies.every((b) => ["federal", "state"].includes(b.jurisdiction)), `refresh.json: the eleven regulators are all choices of the agency filter (${bodies.length} choices: ${bodies.map((b) => b.label).join(", ")})`);
      ok(off.length > 0 && off.every((r) => { const b = bodies.find((x) => x.key === r.key); return b.mark?.words === "not refreshed" && b.mark.why === r.reason && r.reason.length > 20; }), `refresh.json: ${off.length} regulators refuse a plain request (${off.map((r) => r.short).join(", ")}); each is marked, its hover the file's reason word for word`);
      ok(bodies.every((b) => !W.municipalPhrase(`${b.label} ${b.name} ${b.why} ${b.mark?.why ?? ""}`, REAL)), "refresh.json: no municipal phrase in a choice or its hover");
      if (state) {
        const topics = W.topicsOf(REAL, state.topics);
        const made = state.rows.map((s) => W.docketRow(s, bodies, topics, REAL));
        const rows = made.filter((m) => m.row).map((m) => m.row), dropped = made.filter((m) => m.dropped).map((m) => m.dropped);
        ok(topics.length === 8 && rows.length + dropped.length === state.rows.length, `state_rules.json: ${state.rows.length} rows, ${rows.length} the view can show, ${dropped.length} not (${[...new Set(dropped.map((d) => d.why))].join("; ") || "none"})`);
        ok(rows.every((r) => /^\d{4}-\d{2}-\d{2}$/.test(r.date) && /^https?:\/\//.test(r.link.href) && r.status.words && r.link.tip && (r.read.line === null || r.read.why.startsWith("A model's read"))), "state_rules.json: every row shown has a day, a status, an address and a read that is a model's or the placeholder");
        ok(rows.every((r) => !W.municipalPhrase(W.wordsOf(r), REAL)) && state.rows.every((s) => s.sentence || s.sentence_withheld ? true : !made[state.rows.indexOf(s)].row), "state_rules.json: no municipal phrase in a row shown; no row without a sentence or the phrase in its place");
        ok(!/made[- ]up|example\.invalid|lorem ipsum/i.test(JSON.stringify(state)), "state_rules.json: no made-up row");
      } else console.log("skip state_rules.json: not on this machine");
    } else console.log("skip refresh.json: not on this machine");
    if (tags) ok(Object.values(tags.tags).every((hits) => hits.every((h) => h.tag in REAL.tags)) && String(tags.rule_version) === String(REAL.version), `action_tags.json: ${Object.keys(tags.tags).length} actions tagged by rule version ${tags.rule_version}`);
    else console.log("skip action_tags.json: not on this machine");
  }
}

console.log(failed ? `${failed} of ${n} FAILED` : `all ${n} passed`);
process.exit(failed ? 1 : 0);
