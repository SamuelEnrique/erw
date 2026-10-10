// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis) and its two API routes, on the built site.
//
//   npm run build && npx next start -p 3135
//   node --import ./scripts/alias-register.mjs scripts/check-thesis.mjs [base-url]      (default http://localhost:3135)
//
// Against any database (the check never queues a run and never stores an answer there):
//   visitor     /thesis is the in-review page, not indexed, with nothing of the tool on it
//   routes      POST /api/thesis/run and GET /api/thesis/run?id= answer 404 with an empty body without the internal
//               cookie, and with a wrong one; POST /api/thesis/pitchbook never answers 200 to a bad payload (400), a
//               body over 400 KB (413) or a wrong key (403)
//   internal    with the internal cookie /thesis answers 200, is never cached or indexed, and holds the form, its
//               Method note and either the runs or "Runs could not be read." (when migration 024 is not applied, or
//               the server's token is not the database's): no stack trace, no "undefined", no export or download
//   form        a niche too short to be one is refused in plain words before the database is asked
// Against the stand-in (scripts/thesis-stub.mjs, its fixture runs): every tab of a report, the placeholders with their
// hovers, the sources as links, the confidence score with its line, a failed run's note, a queued run's state; then in
// a real browser: each chart answers the mouse with the series, the category and the value with its unit, the report's
// words are never read as markup, a tab is kept in the address, the PitchBook answer is submitted once and every figure
// of it carries its tag, a run asked for on the form is queued and re-read until it ends, and a phone's width does not
// scroll sideways. Against a real database those are "not proven here".
//
// Session 150, the data providers: POST /api/thesis/provider answers 404 with an empty body without the internal
// cookie and never 200 to a bad request; against the stand-in the panel offers PitchBook, Harmonic and Crunchbase with
// PitchBook chosen, the request text changes with the choice, an answer in another provider's format is refused in
// plain words and stores nothing, an answer of Harmonic and one of Crunchbase are accepted once each, every figure
// stands with its provider's label (whose hover holds the terms line and the hash of the pasted text), a fact two
// providers give differently is marked on each line with every value kept, and what a provider returned that the page
// does not use is counted as not mapped. The answers are the made-up ones of scripts/thesis-providers-fixtures.mjs.
//
// Session 158: Crunchbase answers are not kept until its terms are ruled on. POST /api/thesis/provider refuses one
// with those plain words whatever is pasted, and nothing of it is stored; an answer in Crunchbase's format under
// another provider is refused with the same words; the choice shows Crunchbase with its button off and the short mark
// "not yet available", the words on hover; its request text is never in the box. A run that already holds the three
// providers' answers (the stand-in's "fixture-three", there when the stand-in is started with the alias loader) is
// still drawn with every figure and label. And a "Why it is here" sentence from a data vendor's public page carries
// the short mark "vendor page" with its reason on hover.
//
// Session 160: a "Why it is here" sentence read from a page's kept text carries the day that text was retrieved as a
// short mark with its reason on hover, and a company written under several names shows the others under its name.
//
// Session 169, the gate on the niche (lib/thesis/niche.ts): the form holds the owner's label, placeholder, help line
// and three example chips; POST /api/thesis/run refuses a sector or a market topic with 422, the refusal's sentence
// and the curated table's chips, before the database or a model is asked (against any server: "oil & gas demand" and
// "geothermal", the table's own inputs, cost nothing). Against the stand-in, in a browser: the refusal is shown with
// its chips at once, a chip fills the box, "Run anyway" queues the run through thesis_submit_forced with its gate, and
// a forced run's report carries the mark "run anyway" with its reason on hover. Start the server for this check with
// THESIS_GATE_MODEL=0, so that no input of the check can reach the model.
// Exit 1 on a failure.
import { env, withBrowser } from "./browser.mjs";
import { EMPTY_TAB, PB_PENDING, PB_PENDING_WHY, TABS } from "../lib/thesis/view.ts";
import { ALSO, DONE, FAILED, FORCED, KEPT_MARK, KEPT_NOTE, KEY, MARKET, MARKET_PB, QUEUED, THREE, VENDOR_NOTE, fixtureAnswer } from "./thesis-stub.mjs";
import { CONNECTOR_NOTE } from "../lib/thesis/view.ts";
import * as niche from "../lib/thesis/niche.ts";
import { crunchbaseAnswer, harmonicAnswer } from "./thesis-providers-fixtures.mjs";
import { NOT_KEPT, PROVIDERS, TERMS } from "../lib/thesis/providers.ts";

const NOT_KEPT_WORDS = `${NOT_KEPT.crunchbase}.`;      // "Crunchbase answers are not kept until its terms are ruled on."

const base = (process.argv[2] ?? "http://localhost:3135").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const ask = async (path, { withCookie = true, method = "GET", body, wrong = false } = {}) => {
  const headers = {};
  if (wrong) headers.Cookie = `erw_internal=${"0".repeat(64)}; erw_view=internal`;
  else if (withCookie) headers.Cookie = cookie;
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const r = await fetch(base + path, { method, headers, body: body === undefined ? undefined : typeof body === "string" ? body : JSON.stringify(body), redirect: "manual" });
  const text = await r.text();
  let json = null;
  try { json = JSON.parse(text); } catch { /* not JSON */ }
  return { status: r.status, html: text, json, cache: r.headers.get("cache-control") ?? "", robots: r.headers.get("x-robots-tag") ?? "" };
};
const plain = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/\s+/g, " ");
/** The page's own part of the HTML: from its first element on. */
const face = (html) => { const i = html.indexOf('data-thesis="1"'); return i < 0 ? "" : html.slice(i); };
const clean = (text) => !/\bundefined\b|\bNaN\b|\[object Object\]/.test(text) && !/\bat [\w.<>$]+ \(|node_modules|Error:|HTTP \d{3}/.test(text);

// ---- as a visitor
{
  const v = await ask("/thesis", { withCookie: false });
  check(v.status === 200 && v.html.includes('data-in-review="1"') && plain(v.html).includes("This tool is in review and will open when it is approved") && !v.html.includes('data-thesis="1"') && !v.html.includes("data-thesis-form")
    && (/noindex/.test(v.robots) || /<meta name="robots" content="[^"]*noindex/.test(v.html)), "as a visitor /thesis is the in-review page, not indexed, with nothing of the tool on it");
  const w = await ask("/thesis", { wrong: true });
  check(w.status === 200 && w.html.includes('data-in-review="1"') && !w.html.includes("data-thesis-form"), "a wrong internal cookie is a visitor");
  const post = await ask("/api/thesis/run", { withCookie: false, method: "POST", body: { niche: "a niche long enough to be read as one" } });
  const get = await ask("/api/thesis/run?id=x", { withCookie: false });
  check(post.status === 404 && post.html === "" && get.status === 404 && get.html === "", `without the cookie POST /api/thesis/run answers ${post.status} and GET /api/thesis/run?id=x answers ${get.status}, each with an empty body`);
  check(/no-store/.test(post.cache) && /no-store/.test(get.cache), "and neither answer may be stored");
  const post2 = await ask("/api/thesis/run", { wrong: true, method: "POST", body: { niche: "a niche long enough to be read as one" } });
  const get2 = await ask("/api/thesis/run?id=x", { wrong: true });
  check(post2.status === 404 && post2.html === "" && get2.status === 404 && get2.html === "", "nor with a wrong cookie");
}

// ---- the internal view
const page = await ask("/thesis");
const html = face(page.html);
const text = plain(html);
const unread = html.includes('data-thesis-unread="1"');
{
  check(page.status === 200 && !!html && text.includes("Thesis Builder"), "with the internal cookie /thesis answers 200 and is the tool");
  check(html.includes('data-thesis-form="1"') && /<input[^>]*name="niche"/.test(html) && /<input[^>]*name="stage"/.test(html) && /<input[^>]*name="geography"/.test(html) && /<button[^>]*data-thesis-run="1"[^>]*>Run<\/button>/.test(html),
    "it holds the form: the niche, the optional stage and geography, and Run");
  // session 169: the owner's words on the form, word for word (React writes a quotation mark in an attribute as &quot;)
  const attr = (s) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;");
  check(text.includes(niche.NICHE_LABEL) && html.includes(`placeholder="${attr(niche.NICHE_PLACEHOLDER)}"`) && text.includes(niche.NICHE_HELP)
    && niche.NICHE_EXAMPLES.every((x) => html.includes(`data-thesis-example="${x}"`)), "the form holds the owner's label, placeholder, help line and three example chips");
  check(/no-store/.test(page.cache) && /<meta name="robots" content="[^"]*noindex/.test(page.html), `the page is never stored (Cache-Control: ${page.cache}) and never indexed`);
  check(unread ? text.includes("Runs could not be read.") : /data-thesis-runs="\d+"/.test(html), unread ? 'the runs could not be read here, and the page says "Runs could not be read."' : "the runs are listed");
  check(clean(text), `no "undefined", no NaN and no trace of an error on the page${clean(text) ? "" : ` ("${(/.{0,40}(undefined|NaN|Error:|HTTP \d{3}|node_modules).{0,40}/.exec(text) ?? [""])[0]}")`}`);
  check(page.html.includes("/data/methods/thesis") && text.includes("Method note"), "the page names its Method note, /data/methods/thesis");
  const words = /\b(methodology|limitations?)\b/i.exec(text);
  check(!words && !/\bdownload=|>\s*(Export|Download|Copy all)\b/i.test(html), `no method prose on the face, and no export or download${words ? ` (found "${words[0]}")` : ""}`);
  const none = await ask("/thesis?run=no-such-run&tab=funnel");
  const t = plain(face(none.html));
  check(none.status === 200 && (t.includes("No run is held under this address.") || t.includes("This run could not be read.")) && clean(t) && none.html.includes('data-thesis-form="1"'), "an address naming a run that is not held says so and keeps the form");
}
{
  const short = await ask("/api/thesis/run", { method: "POST", body: { niche: "short" } });
  check(short.status === 400 && short.json?.ok === false && short.json.reason === "Describe the niche in a sentence." && /no-store/.test(short.cache), `a niche too short is refused in plain words (${short.status}: ${short.json?.reason})`);
  // session 169: a sector or a market topic is refused with the table's chips; the table answers, so no model and no
  // database is asked (test run 3 of the session: "oil & gas demand", at no run cost)
  for (const [x, id] of [["oil & gas demand", "oil_gas"], ["geothermal", "geothermal"]]) {
    const r = await ask("/api/thesis/run", { method: "POST", body: { niche: x, stage: "", geography: "" } });
    const want = niche.TABLE.find((t) => t.id === id).suggestions;
    check(r.status === 422 && r.json?.ok === false && r.json.refused === true && r.json.reason === niche.refusalWords(x) && JSON.stringify(r.json.suggestions) === JSON.stringify(want) && !r.json.run_id && /no-store/.test(r.cache),
      `"${x}" is refused with the refusal's sentence and its ${want.length} chips, and nothing is queued (${r.status})`);
  }
  const junk = await ask("/api/thesis/run", { method: "POST", body: "not json" });
  check(junk.status === 400 && junk.json?.ok === false, "and so is a body that is not JSON");
  const st = await ask("/api/thesis/run?id=no-such-run");
  check((st.status === 404 || st.status === 502) && st.json && Object.keys(st.json).sort().join() === "note,status" && /no-store/.test(st.cache), `GET /api/thesis/run?id= of a run not held answers ${st.status} with status and note only`);
  const odd = await ask("/api/thesis/run?id=..%2Fx");
  check(odd.status === 404, "an id that cannot be a run's is not asked of the database");
}

// ---- the PitchBook route: the key is the credential, and nothing but a good payload under the right key is 200
{
  const good = fixtureAnswer("no-such-run");
  const post = (body) => ask("/api/thesis/pitchbook", { withCookie: false, method: "POST", body });
  const a = await post("{not json");
  const b = await post({ run_id: "no-such-run", key: "k".repeat(43), payload: { ...good, format: "something-else" } });
  const c = await post({ run_id: "no-such-run", key: "k".repeat(43), payload: { ...good, extra: 1 } });
  const d = await post({ run_id: "no-such-run", key: "k".repeat(43), payload: { ...good, companies: [{ name: "Example Storage Inc.", found: true, total_raised_usd_m: -1 }] } });
  const e = await post({ run_id: "another-run", key: "k".repeat(43), payload: good });
  const f = await post({ run_id: "no-such-run", payload: good });
  check([a, b, c, d, e, f].every((r) => r.status === 400 && r.json?.ok === false && typeof r.json.reason === "string" && r.json.reason.length > 8 && /no-store/.test(r.cache)),
    `a payload that is not JSON, of another format, with an unknown key, with a negative figure, for another run, or with no key is 400 with its reason (${[a, b, c, d, e, f].map((r) => r.status).join(", ")}; "${d.json?.reason}")`);
  const short = await post({ run_id: "no-such-run", key: "too-short", payload: good });
  check(short.status === 403 && short.json?.ok === false, `a good payload under a key too short to be one is ${short.status}`);
  const wrong = await post({ run_id: "no-such-run", key: "k".repeat(43), payload: good });
  if (wrong.status === 502 && unread) console.log("not proven here: a good payload under a wrong key of full length (the database functions are not applied, so the route answered 502, not 200)");
  else check(wrong.status === 403 && wrong.json?.ok === false, `a good payload under a wrong key is ${wrong.status}`);
  const whole = await post({ ...good, key: "k".repeat(43) });
  check(whole.status === 403 || (whole.status === 502 && unread), `the payload itself carrying its key is read the same way (${whole.status})`);
  const big = await post({ run_id: "no-such-run", key: "k".repeat(43), payload: { ...good, companies: Array.from({ length: 300 }, (_, i) => ({ name: `Company ${i}`, found: true, description: "x".repeat(400), investors: Array.from({ length: 40 }, (_, j) => `Fund ${j} ${"y".repeat(100)}`) })) } });
  check(big.status === 413, `a body over 400 KB is ${big.status}`);
  check([a, b, c, d, e, f, short, wrong, whole, big].every((r) => r.status !== 200), "none of them is 200");
}

// ---- session 150, the providers' route: the internal cookie is the credential, and nothing but a good answer is 200
{
  const post = (body, o = {}) => ask("/api/thesis/provider", { method: "POST", body, ...o });
  const good = { run_id: "no-such-run", provider: "harmonic", pasted: JSON.stringify(harmonicAnswer("no-such-run")) };
  const out = await post(good, { withCookie: false });
  const wrong = await post(good, { wrong: true });
  check(out.status === 404 && out.html === "" && wrong.status === 404 && wrong.html === "" && /no-store/.test(out.cache), `without the internal cookie, or with a wrong one, POST /api/thesis/provider answers ${out.status} and ${wrong.status} with an empty body`);
  const a = await post("{not json");
  const b = await post({ ...good, provider: "another" });
  const c = await post({ ...good, extra: 1 });
  const d = await post({ ...good, pasted: "no json here" });
  const e = await post({ ...good, pasted: JSON.stringify(crunchbaseAnswer("no-such-run")) });
  const f = await post({ ...good, run_id: "another-run" });
  const g = await post({ ...good, run_id: "../x" });
  check([a, b, c, d, e, f, g].every((r) => r.status === 400 && r.json?.ok === false && typeof r.json.reason === "string" && r.json.reason.length > 8 && /no-store/.test(r.cache)),
    `a body that is not JSON, an unknown provider, an unknown key, a text with no JSON, another provider's format, another run and an id that cannot be a run's are 400 with a reason (${[a, b, c, d, e, f, g].map((r) => r.status).join(", ")})`);
  // session 158: Crunchbase's format under another provider is refused with the plain words (it read "Choose Crunchbase above" until then)
  check(e.json?.reason === NOT_KEPT_WORDS, `an answer in Crunchbase's format under another provider is refused in the plain words ("${e.json?.reason}")`);
  const e2 = await post({ ...good, provider: "pitchbook", pasted: JSON.stringify(harmonicAnswer("no-such-run")) });
  check(e2.status === 400 && e2.json?.reason === `This answer is in the format "erw-harmonic-1", Harmonic's. The provider chosen is PitchBook, which takes "erw-pitchbook-1". Choose Harmonic above, or paste PitchBook's answer.`, `another provider's format is named plainly ("${e2.json?.reason}")`);
  // session 158: with Crunchbase chosen the answer is the same whatever is pasted, so nothing of the text was read
  const cb = [JSON.stringify(crunchbaseAnswer("no-such-run")), "no json here", JSON.stringify(harmonicAnswer("no-such-run")), "x".repeat(2000)];
  const refused = [];
  for (const pasted of cb) refused.push(await post({ run_id: "no-such-run", provider: "crunchbase", pasted }));
  check(refused.every((r) => r.status === 400 && r.json?.ok === false && r.json.reason === NOT_KEPT_WORDS && Object.keys(r.json).sort().join() === "ok,reason" && /no-store/.test(r.cache)),
    `a Crunchbase answer is refused whatever is pasted (a good answer, no JSON, another format, filler): ${refused.map((r) => r.status).join(", ")}, "${refused[0].json?.reason}"`);
  const none = await post(good);
  check(none.status === 404 || none.status === 502, `a good answer for a run that is not held is ${none.status}${none.status === 502 ? " (this database does not hold the providers' store: migration 025 is not applied)" : ""}, never 200`);
  const big = await post({ ...good, pasted: JSON.stringify({ ...harmonicAnswer("no-such-run"), filler: "x".repeat(420_000) }) });
  check(big.status === 413, `an answer over 400 KB is ${big.status}`);
  check([out, wrong, a, b, c, d, e, e2, f, g, none, big, ...refused].every((r) => r.status !== 200), "none of them is 200");
}

// ---- the fixture runs of the stand-in
const fixture = html.includes(`data-run="${DONE}"`);
if (!fixture) {
  console.log("not proven here: a report's tabs, charts, sources, placeholders and the PitchBook answer (this server reads a real database; run it against scripts/thesis-stub.mjs)");
} else {
  const tab = async (id, run = DONE) => { const r = await ask(`/thesis?run=${run}&tab=${id}`); const h = face(r.html); return { status: r.status, html: h, text: plain(h) }; };
  const tabs = Object.fromEntries(await Promise.all(TABS.map(async (t) => [t.id, await tab(t.id)])));
  check(TABS.every((t) => tabs[t.id].status === 200 && tabs[t.id].html.includes(`data-thesis-tab="${t.id}"`) && clean(tabs[t.id].text) && TABS.every((x) => tabs[t.id].html.includes(`data-tab="${x.id}"`))),
    `all ${TABS.length} tabs open, each naming the others, with no "undefined" and no NaN`);
  check(tabs.scope.text.includes("Fixture definition of the niche.") && tabs.scope.text.includes("Fixture stage two.") && tabs.scope.text.includes("Fixture meaning.") && tabs.scope.text.includes("Fixture reason it is left out."), "Scope and definitions: the definition, the value chain, the definitions and what is excluded");
  {
    const h = tabs.scope.html;
    const s1 = /<a [^>]*href="https:\/\/example\.com\/one"[^>]*>S1<\/a>/.exec(h)?.[0] ?? "";
    check(/target="_blank"/.test(s1) && /rel="noopener noreferrer"/.test(s1) && /title="Fixture source one/.test(s1), "a web source is a small raised link that opens the source and shows its title on hover");
    check(/<span[^>]*title="ERW table fixture_table[^"]*"[^>]*data-source="E1"[^>]*>E1<\/span>/.test(h) && !/<a [^>]*data-source="E1"/.test(h), "an ERW source has no address: its title on hover only");
    const l = tabs.landscape.html;
    check(/<span[^>]*data-source="S3"/.test(l) && !/href="javascript:/i.test(l) && !/href="javascript:/i.test(h), "an address that is not a web address is never a link (a source's, a company's)");
  }
  {
    const h = tabs.trends.html, t = tabs.trends.text;
    check((h.match(/data-chart="trend"/g) ?? []).length === 2 && [1, 2, 3, 4].every((k) => h.includes(`id="trend-${k}"`)), "Trends: four trends, two of them with a chart of their own table");
    check(/title="No row of this trend&#x27;s table holds a number to draw\."[^>]*>no chart</.test(h), 'a trend whose table holds no number reads "no chart", with the reason on hover');
    check(/title="Fixture: not published for 2024\."[^>]*data-missing="not_held"[^>]*>not held</.test(h) && /title="Fixture: the planner does not disclose it\."[^>]*data-missing="not_disclosed"[^>]*>not disclosed</.test(h), "a missing cell is a short placeholder whose hover is the cell's own note");
    check(t.includes("<img src=x onerror=window.__thesis_probe=1>") && !/<img src=x/i.test(h), "the report's words are written as text, never as markup");
    check(/data-source="S9"/.test(h) && /this run does not list this source/.test(h), "a source id the run does not list is shown and says so on hover");
  }
  {
    const h = tabs.landscape.html, t = tabs.landscape.text;
    check(/<caption[^>]*>Fixture rule: a company is on this map when a fixture source ties it to a fixture trend\.<\/caption>/.test(h), "Company landscape: the rule is the table's caption");
    check(["Fixture reason one.", "Fixture reason two.", "Fixture reason three."].every((w) => t.includes(w)) && /href="\/thesis\?run=fixture-done&amp;tab=trends#trend-2"[^>]*>Trend (<!-- -->)?2</.test(h), "each company's reason is stated, with the trends it serves as chips that open the Trends tab");
    // session 158: a sentence from a data vendor's public page carries the short mark, its reason on hover
    const marks = [...h.matchAll(/<span[^>]*title="([^"]*)"[^>]*data-vendor-page="1"[^>]*>([^<]*)<\/span>/g)];
    const cellOf = (name) => (new RegExp(`data-company="${name}"[\\s\\S]*?<td[^>]*data-reason="1"[^>]*>([\\s\\S]*?)</td>`).exec(h) ?? ["", ""])[1];
    check(marks.length === 1 && marks[0][2] === "vendor page" && marks[0][1].replace(/&#x27;/g, "'") === VENDOR_NOTE && /Fixture reason two\.[\s\S]*data-vendor-page="1"/.test(cellOf("Sample Grid Co"))
      && !cellOf("Example Storage Inc.").includes("data-vendor-page") && !cellOf("Unasked Example LLC").includes("data-vendor-page") && !TABS.some((x) => x.id !== "landscape" && tabs[x.id].html.includes("data-vendor-page")),
      `a "Why it is here" sentence from a data vendor's page reads "${marks[0]?.[2]}" after it, with the reason on hover, and no other sentence does (${marks.length} mark)`);
    // session 160: a sentence from a page's kept text carries the day it was retrieved, its reason on hover; other names stand under the name
    const kept = [...h.matchAll(/<span[^>]*title="([^"]*)"[^>]*data-kept-text="1"[^>]*>([^<]*)<\/span>/g)];
    check(kept.length === 1 && kept[0][2] === KEPT_MARK && kept[0][1].replace(/&#x27;/g, "'") === KEPT_NOTE && /Fixture reason three\.[\s\S]*data-kept-text="1"/.test(cellOf("Unasked Example LLC"))
      && !cellOf("Example Storage Inc.").includes("data-kept-text") && !cellOf("Sample Grid Co").includes("data-kept-text") && !TABS.some((x) => x.id !== "landscape" && tabs[x.id].html.includes("data-kept-text")),
      `a "Why it is here" sentence from a page's kept text reads "${kept[0]?.[2]}" after it, with the reason on hover, and no other sentence does (${kept.length} mark)`);
    const also = [...h.matchAll(/<span[^>]*data-also="1"[^>]*>([\s\S]*?)<\/span>/g)].map((m) => m[1].replace(/<!-- -->/g, ""));
    check(also.length === 1 && also[0] === `also written: ${ALSO.join("; ")}` && new RegExp(`data-company="Unasked Example LLC"[\\s\\S]*?data-also="1"`).test(h),
      `a company written under several names shows the others under its name ("${also[0]}"), and no other company does (${also.length})`);
    check(/data-confidence="1"><span[^>]*>72<\/span><span[^>]*>Fixture note: two sources agree\.<\/span>/.test(h), "the confidence score is the number with its one line beside it");
    const pend = [...h.matchAll(/title="([^"]*)"[^>]*data-missing="pitchbook_pending"[^>]*>([^<]*)</g)];
    check(pend.length >= 4 && pend.every((m) => m[1] === PB_PENDING_WHY && m[2] === PB_PENDING), `the ${pend.length} cells the PitchBook stage will fill read "${PB_PENDING}", with the hover "${PB_PENDING_WHY}"`);
    check(/data-missing="pitchbook_not_asked"/.test(h) && !h.includes("data-pb-tag"), "a company not asked of PitchBook says so, and no PitchBook figure is shown before the answer");
    check(/title="Fixture: the company names no founder\."[^>]*>not disclosed</.test(h) && /title="Fixture: one source only\."[^>]*>not confirmed</.test(h) && /title="Fixture: no round is held\."[^>]*>not held</.test(h), "not disclosed, not confirmed and not held each carry their reason on hover");
  }
  {
    const h = tabs.funnel.html, t = tabs.funnel.text;
    check(h.includes('data-chart="funnel"') && ["Example Storage Inc.", "Sample Grid Co", "Dropped Example"].every((c) => h.includes(`data-company="${c}"`)) && t.includes("Fixture: no second source."), "Deal funnel: the chart of its stages, with every company under it");
    check(/title="This run holds no score for this company\."[^>]*>not scored</.test(h) && /data-score="1">72</.test(h), "a company with no score reads a placeholder, never zero");
    check(tabs.pipeline.text.includes("USD 4 billion") && /data-confidence="1"><span[^>]*>41<\/span><span[^>]*>Fixture note: one source\.<\/span>/.test(tabs.pipeline.html), "Pipeline map: each company with its confidence and the line that explains it");
    check(tabs.capital.text.includes("USD 12.5 million") && tabs.capital.text.includes("2025-03") && /data-missing="pitchbook_pending"/.test(tabs.capital.html), "Capital: the rounds, a cell that is text shown as it is, a pending amount");
    check(tabs.incumbents.text.includes(EMPTY_TAB) && tabs.incumbents.html.includes('data-thesis-empty="1"'), `a tab the run holds nothing for says "${EMPTY_TAB}"`);
    check(tabs.risks.text.includes("Fixture: what is not known.") && tabs.policy.text.includes("Fixture agency") && /<a [^>]*href="https:\/\/example\.com\/rule"[^>]*>Fixture rule<\/a>/.test(tabs.policy.html), "Risks and Policy: their rows, an action linked to its publisher");
  }
  {
    const main = await tab("scope");
    check(main.html.includes('data-thesis-pitchbook="pending"') && main.text.includes(PB_PENDING) && main.text.includes("Asked for 2 companies") && /data-thesis-asked="1"[\s\S]*?Example Storage Inc\.[\s\S]*?Sample Grid Co/.test(main.html)
      && /<textarea[^>]*readOnly=""[^>]*data-thesis-paste="1"[^>]*>FIXTURE REQUEST for run fixture-done/i.test(main.html) && />Copy<\/button>/.test(main.html) && main.text.includes("Paste Claude's answer here") && />Submit<\/button>/.test(main.html),
      "the PitchBook panel: pending, the companies asked for, the request in a read-only box with Copy, and the box for the answer with Submit");
    const radios = [...main.html.matchAll(/<input[^>]*data-thesis-provider-choice="([a-z]+)"[^>]*>/g)].map((m) => [m[1], /\schecked=""/.test(m[0]), /\sdisabled=""/.test(m[0])]);
    // session 158: Crunchbase is listed with its button off (it was open to choose until then)
    check(JSON.stringify(radios) === JSON.stringify([["pitchbook", true, false], ["harmonic", false, false], ["crunchbase", false, true]]) && main.text.includes("Data provider") && main.html.includes('data-thesis-provider="pitchbook"'),
      `the panel lists the three providers, PitchBook first and chosen, Crunchbase not to be chosen (${radios.map((r) => `${r[0]}${r[1] ? " chosen" : ""}${r[2] ? " off" : ""}`).join(", ")})`);
    const off = [...main.html.matchAll(/<span[^>]*title="([^"]*)"[^>]*data-thesis-provider-unavailable="([a-z]+)"[^>]*>([^<]*)<\/span>/g)].map((m) => [m[2], m[3], m[1]]);
    check(JSON.stringify(off) === JSON.stringify([["crunchbase", "not yet available", NOT_KEPT_WORDS]]) && !main.html.includes("You have a Crunchbase connector"),
      `Crunchbase reads "${off[0]?.[1]}" with the hover "${off[0]?.[2]}", and its request text is not on the page`);
    const cbDone = await ask("/api/thesis/provider", { method: "POST", body: { run_id: DONE, provider: "crunchbase", pasted: JSON.stringify(crunchbaseAnswer(DONE)) } });
    const afterCb = await tab("funnel");
    check(cbDone.status === 400 && cbDone.json?.reason === NOT_KEPT_WORDS && !afterCb.html.includes("data-thesis-provider-received") && !afterCb.html.includes('data-provider="crunchbase"') && afterCb.html.includes('data-thesis-pitchbook="pending"'),
      `a good Crunchbase answer for a finished run is ${cbDone.status} ("${cbDone.json?.reason}"), and the run holds nothing of it afterwards`);
    const queuedProvider = await ask("/api/thesis/provider", { method: "POST", body: { run_id: QUEUED, provider: "harmonic", pasted: JSON.stringify(harmonicAnswer(QUEUED)) } });
    check(queuedProvider.status === 404 && queuedProvider.json?.reason === "No finished run is held under this address.", `a provider's answer for a run that has not finished is ${queuedProvider.status}: "${queuedProvider.json?.reason}"`);
    const failed = await tab("scope", FAILED);
    check(failed.html.includes('data-thesis-failed="1"') && failed.text.includes("Fixture: the run stopped because the fixture says so.") && !failed.html.includes("data-thesis-pitchbook") && !failed.html.includes("data-thesis-report"), "a failed run shows its note, and no report or PitchBook panel");
    const queued = await tab("scope", QUEUED);
    check(queued.html.includes('data-thesis-watch="queued"') && queued.text.includes("Queued. The run is waiting to start.") && !queued.html.includes("data-thesis-report"), "a queued run says so in plain words");
    const st = await ask(`/api/thesis/run?id=${QUEUED}`);
    check(st.status === 200 && st.json?.status === "queued" && Object.keys(st.json).sort().join() === "note,status", "GET /api/thesis/run?id= answers a run's status and note, and nothing else of it");
    check(page.html.includes(`data-run="${FAILED}"`) && /data-run="fixture-done" data-status="done"/.test(html) && text.includes("pending") && text.includes("not yet"), "the list holds each run with its status, its companies and its PitchBook state");
  }

  const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, errors, sleep }) => {
    await open(base);
    await go(`${base}/thesis?run=${DONE}&tab=trends`);
    await wait(`document.querySelectorAll('[data-chart="trend"] canvas').length === 2`, 40000, "the two trend charts");
    const tip = (sel, k, i, re) => evaluate(`(() => { const el = document.querySelectorAll('${sel}')[${k}]; const chart = window.echarts.getInstanceByDom(el);
      chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: ${i} });
      return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => ${re}.test(t)).sort((x, y) => x.length - y.length)[0] ?? ''), 400)); })()`);
    const bar = (await tip('[data-chart="trend"]', 0, 0, "/Installed/")).replace(/\s+/g, " ");
    check(/2023/.test(bar) && /Installed: 10 GW/.test(bar) && /Planned: 4 GW/.test(bar), `a bar chart answers the mouse with the category, each series and the value with its unit ("${bar.slice(0, 80)}")`);
    const gapTip = (await tip('[data-chart="trend"]', 0, 1, "/Installed/")).replace(/\s+/g, " ");
    check(/2025/.test(gapTip) && /Installed: 18.5 GW/.test(gapTip) && !/Planned/.test(gapTip), `the row with no number (2024) is left out, and a cell with none is a gap, not a zero ("${gapTip.slice(0, 80)}")`);
    const probe = (await tip('[data-chart="trend"]', 0, 2, "/Installed/")).replace(/\s+/g, " ");
    check(probe.includes("<img src=x onerror=window.__thesis_probe=1>") && /Installed: 1,024 GW/.test(probe) && (await evaluate(`window.__thesis_probe === undefined && !document.querySelector('img[src="x"]')`)), "a category that would be markup is shown as text in the tooltip and runs nothing");
    const line = (await tip('[data-chart="trend"]', 1, 1, "/Price/")).replace(/\s+/g, " ");
    check(/Q2/.test(line) && /Price: 98.5 USD\/kWh/.test(line), `a line chart answers the mouse the same way ("${line.slice(0, 80)}")`);
    check(await evaluate(`!!document.querySelector('a[href="/data/methods/thesis"]') && ![...document.querySelectorAll('[data-thesis] *')].some((e) => e.hasAttribute('download'))`), "in the internal view the Method note is a link, and nothing on the page downloads");
    await evaluate(`document.querySelector('[data-tab="funnel"]').click()`);
    await wait(`location.search.includes('tab=funnel') && !!document.querySelector('[data-chart="funnel"] canvas')`, 20000, "the funnel tab");
    const fun = (await tip('[data-chart="funnel"]', 0, 1, "/Deal funnel/")).replace(/\s+/g, " ");
    check(/Deal funnel/.test(fun) && /Sourced: 9 companies/.test(fun), `a tab is kept in the address, and the funnel answers the mouse with the stage and its count ("${fun.slice(0, 80)}")`);

    // session 158: the request text changes with the provider chosen (until this session the check chose Crunchbase
    // for this; Crunchbase cannot be chosen now), and a click on Crunchbase changes nothing
    const pasteBox = () => evaluate(`document.querySelector('[data-thesis-paste="1"]').value`);
    const pitchbookText = await pasteBox();
    await evaluate(`document.querySelector('[data-thesis-provider-choice="harmonic"]').click()`);
    await wait(`document.querySelector('[data-thesis-paste="1"]').value.startsWith('You have a Harmonic connector.')`, 5000, "the request of Harmonic");
    const harmonicFirst = await pasteBox();
    check(pitchbookText.startsWith(`FIXTURE REQUEST for run ${DONE}`) && harmonicFirst.includes('"format": "erw-harmonic-1"') && harmonicFirst.includes("2. Sample Grid Co") && harmonicFirst !== pitchbookText
      && (await evaluate(`document.querySelector('[data-thesis-pitchbook]').dataset.thesisProvider`)) === "harmonic", "the request text changes with the provider chosen");
    await evaluate(`document.querySelector('[data-thesis-provider-choice="crunchbase"]').click()`);
    await sleep(400);
    const cbChoice = await evaluate(`(() => { const r = document.querySelector('[data-thesis-provider-choice="crunchbase"]'), m = document.querySelector('[data-thesis-provider-unavailable="crunchbase"]');
      return [r.disabled, r.checked, m ? m.innerText.trim() : '', m ? m.title : '', document.querySelector('[data-thesis-pitchbook]').dataset.thesisProvider, document.querySelector('[data-thesis-paste="1"]').value.includes('Crunchbase connector'), document.querySelector('label[for="thesis-paste"]').innerText]; })()`);
    check(cbChoice[0] === true && cbChoice[1] === false && cbChoice[2] === "not yet available" && cbChoice[3] === NOT_KEPT_WORDS && cbChoice[4] === "harmonic" && cbChoice[5] === false && cbChoice[6] === "Paste this into a Claude chat that has a Harmonic connector",
      `Crunchbase cannot be chosen: its button is off, it reads "${cbChoice[2]}" with the hover "${cbChoice[3]}", and a click leaves the provider and the request as they were`);
    await evaluate(`document.querySelector('[data-thesis-provider-choice="pitchbook"]').click()`);
    await wait(`document.querySelector('[data-thesis-paste="1"]').value.startsWith('FIXTURE REQUEST')`, 5000, "the request of PitchBook again");

    // the PitchBook answer: refused with its reason, then accepted once, then every figure tagged
    const type = (words) => evaluate(`(() => { const el = document.querySelector('[data-thesis-answer="1"]'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(el, ${JSON.stringify(words)}); el.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
    await type(JSON.stringify({ ...fixtureAnswer(), valuation: 1 }));
    await wait(`!document.querySelector('[data-thesis-submit="1"]').disabled`, 5000, "the Submit button");
    await evaluate(`document.querySelector('[data-thesis-submit="1"]').click()`);
    const said = await wait(`document.querySelector('[data-thesis-pitchbook] [data-thesis-said="1"]')?.innerText`, 15000, "the refusal");
    check(/holds a key the format does not have: "valuation"/.test(said) && (await evaluate(`!!document.querySelector('[data-thesis-pitchbook="pending"]')`)), `an answer the format refuses is said in the route's own words, and nothing is stored ("${said}")`);
    await type("Here is the answer:\n```json\n" + JSON.stringify(fixtureAnswer(), null, 1) + "\n```");
    await evaluate(`document.querySelector('[data-thesis-submit="1"]').click()`);
    await wait(`!!document.querySelector('[data-thesis-pitchbook="received"]')`, 20000, "PitchBook received");
    const got = await evaluate(`document.querySelector('[data-thesis-pitchbook="received"]').innerText`);
    check(/PitchBook received/.test(got) && /Pulled on 6 Oct 2026/.test(got), `the answer pasted from a chat is accepted: "${got.replace(/\s+/g, " ").slice(0, 110)}"`);
    const figures = await evaluate(`[...document.querySelectorAll('[data-pb-figure]')].map((e) => e.innerText.replace(/\\s+/g, ' ').trim())`);
    check(figures.length >= 8 && figures.every((f) => /PitchBook$/.test(f)) && figures.includes("Total raised: USD 18 million PitchBook") && figures.includes("Last round: Series A, Mar 2025, USD 12.5 million PitchBook"),
      `in the Deal funnel every PitchBook figure carries its tag (${figures.length} figures; "${figures[0]}")`);
    const more = await evaluate(`document.querySelector('[data-pb-additional="1"]')?.innerText.replace(/\\s+/g, ' ') ?? ''`);
    check(/Found by PitchBook/.test(more) && /Found Later LLC/.test(more) && /Total raised: USD 3.25 million PitchBook/.test(more) && (await evaluate(`!!document.querySelector('[data-company="Sample Grid Co"] [data-missing="pitchbook_not_found"]')`)),
      "the companies PitchBook found beyond those asked are listed as found by PitchBook, and one it did not find says so");
    const again = await evaluate(`fetch('/api/thesis/pitchbook', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: ${JSON.stringify(JSON.stringify({ run_id: DONE, key: KEY, payload: fixtureAnswer() }))} }).then((r) => r.status)`);
    check(again === 403, `the key opens one write: the same answer under it a second time is ${again}`);
    await go(`${base}/thesis?run=${DONE}&tab=landscape`);
    const cells = await evaluate(`[...document.querySelectorAll('[data-company="Example Storage Inc."] td > [data-pb-figure]')].map((e) => e.innerText.replace(/\\s+/g, ' ').trim())`);
    check(cells.includes("Founders: A. Fixture, C. Fixture PitchBook") && cells.includes("Total raised: USD 18 million PitchBook") && cells.includes("Headquarters: Austin, TX PitchBook")
      && (await evaluate(`!document.querySelector('[data-missing="pitchbook_pending"]') && [...document.querySelectorAll('[data-pb-figure]')].every((e) => !!e.querySelector('[data-pb-tag]'))`)),
      `in the Company landscape a cell PitchBook answers holds the figure with its tag, and none is left pending ("${cells[0]}")`);
    // session 158: the vendor page mark, in the browser
    const vm = await evaluate(`(() => { const m = document.querySelectorAll('[data-vendor-page="1"]'); return [m.length, m[0] ? m[0].innerText.trim() : '', m[0] ? m[0].title : '', m[0] ? m[0].closest('tr').dataset.company : '', m[0] ? getComputedStyle(m[0]).cursor : '', m[0] ? m[0].closest('td').dataset.reason : '']; })()`);
    check(vm[0] === 1 && vm[1] === "vendor page" && vm[2] === VENDOR_NOTE && vm[3] === "Sample Grid Co" && vm[4] === "help" && vm[5] === "1", `in the browser the mark "${vm[1]}" stands after the "Why it is here" sentence of ${vm[3]} and answers the mouse with its reason`);
    // session 160: the kept text's mark, in the browser
    const km = await evaluate(`(() => { const m = document.querySelectorAll('[data-kept-text="1"]'); return [m.length, m[0] ? m[0].innerText.trim() : '', m[0] ? m[0].title : '', m[0] ? m[0].closest('tr').dataset.company : '', m[0] ? getComputedStyle(m[0]).cursor : '', m[0] ? m[0].closest('td').dataset.reason : '']; })()`);
    check(km[0] === 1 && km[1] === KEPT_MARK && km[2] === KEPT_NOTE && km[3] === "Unasked Example LLC" && km[4] === "help" && km[5] === "1", `in the browser the mark "${km[1]}" stands after the "Why it is here" sentence of ${km[3]} and answers the mouse with its reason`);
    await go(`${base}/thesis?run=${DONE}&tab=pipeline`);
    check(await evaluate(`!!document.querySelector('[data-company="Example Storage Inc."] [data-pb-block]') && [...document.querySelectorAll('[data-pb-figure]')].every((e) => !!e.querySelector('[data-pb-tag]')) && !!document.querySelector('[data-company="Sample Grid Co"] [data-missing="pitchbook_absent"]')`),
      "in the Pipeline map too; a cell PitchBook's answer holds nothing for says so");

    // session 150: the other two providers, after PitchBook's answer is held
    await go(`${base}/thesis?run=${DONE}&tab=funnel`);
    await wait(`!!document.querySelector('[data-thesis-pitchbook="received"] [data-thesis-providers="1"]')`, 20000, "the panel after PitchBook");
    const state = () => evaluate(`[...document.querySelectorAll('[data-thesis-provider-choice]')].map((e) => [e.value, e.checked, e.disabled])`);
    check(JSON.stringify(await state()) === JSON.stringify([["pitchbook", false, true], ["harmonic", true, false], ["crunchbase", false, true]])
      && (await evaluate(`document.querySelector('[data-thesis-pitchbook]').innerText`)).includes("PitchBook received"),
      "once PitchBook's answer is held it reads received and cannot be chosen again; the next provider is chosen (Harmonic: Crunchbase stays off)");
    const harmonicText = await pasteBox();
    check(harmonicText.startsWith("You have a Harmonic connector.") && harmonicText.includes(`Run: ${DONE}`) && harmonicText.includes("1. Example Storage Inc. (https://www.example.com)") && harmonicText.includes('"format": "erw-harmonic-1"')
      && !harmonicText.includes(KEY) && (await evaluate(`document.querySelector('label[for="thesis-paste"]').innerText`)) === "Paste this into a Claude chat that has a Harmonic connector",
      "with Harmonic chosen the request is Harmonic's: the run, the companies asked for, the format erw-harmonic-1, and no key");
    // session 158: a Crunchbase answer pasted under Harmonic is refused in the plain words and goes nowhere (until
    // this session the refusal named the format and said to choose Crunchbase); PitchBook's format is still named
    await type(JSON.stringify(crunchbaseAnswer()));
    await wait(`!document.querySelector('[data-thesis-submit="1"]').disabled`, 5000, "the Submit button");
    await evaluate(`document.querySelector('[data-thesis-submit="1"]').click()`);
    const refusal = await wait(`document.querySelector('[data-thesis-pitchbook] [data-thesis-said="1"]')?.innerText`, 15000, "the refusal of a Crunchbase answer");
    check(refusal === NOT_KEPT_WORDS && !(await evaluate(`!!document.querySelector('[data-thesis-provider-received]')`)), `a Crunchbase answer pasted under another provider is refused in the plain words, and nothing is stored ("${refusal}")`);
    await type(JSON.stringify(fixtureAnswer()));
    await evaluate(`document.querySelector('[data-thesis-submit="1"]').click()`);
    const refusal2 = await wait(`(() => { const t = document.querySelector('[data-thesis-pitchbook] [data-thesis-said="1"]')?.innerText; return t && t.includes('erw-pitchbook-1') ? t : ''; })()`, 15000, "the refusal of another provider's format");
    check(refusal2 === `This answer is in the format "erw-pitchbook-1", PitchBook's. The provider chosen is Harmonic, which takes "erw-harmonic-1". Choose PitchBook above, or paste Harmonic's answer.`
      && !(await evaluate(`!!document.querySelector('[data-thesis-provider-received]')`)), `the answer box takes only the format of the provider chosen, and says which it was given ("${refusal2}")`);
    const harmonicPasted = "Here is the answer:\n```json\n" + JSON.stringify(harmonicAnswer(), null, 1) + "\n```";
    await type(harmonicPasted);
    await evaluate(`document.querySelector('[data-thesis-submit="1"]').click()`);
    await wait(`!!document.querySelector('[data-thesis-provider-received="harmonic"]')`, 20000, "Harmonic received");
    const gotH = (await evaluate(`document.querySelector('[data-thesis-provider-received="harmonic"]').innerText`)).replace(/\s+/g, " ");
    check(/Harmonic received/.test(gotH) && /Pulled on 7 Oct 2026/.test(gotH) && /2 of 2 companies found/.test(gotH) && /1 more found by Harmonic/.test(gotH) && /3 saved searches/.test(gotH) && /\d+ not mapped/.test(gotH),
      `Harmonic's answer pasted from a chat is accepted: "${gotH.slice(0, 150)}"`);
    const lines = () => evaluate(`[...document.querySelectorAll('[data-company="Example Storage Inc."] [data-provider-block] [data-provider-figure]')].map((e) => [e.dataset.provider, e.dataset.providerFigure, e.dataset.disagree ?? '', e.innerText.replace(/\\s+/g, ' ').trim()])`);
    let figs = await lines();
    const of = (id) => figs.filter((f) => f[1] === id).map((f) => f[3]);
    check(figs.length >= 20 && figs.every((f) => f[3].endsWith(PROVIDERS[f[0]].label)) && (await evaluate(`[...document.querySelectorAll('[data-provider-figure]')].every((e) => !!e.querySelector('[data-provider-tag]'))`))
      && (await evaluate(`document.querySelector('[data-tab="funnel"]') && [...document.querySelectorAll('th')].some((t) => t.innerText.trim().toUpperCase() === 'DATA PROVIDERS')`)),
      `in the Deal funnel the column is the providers', and every one of the ${figs.length} figures of the company stands with its provider's label ("${figs.find((f) => f[0] === "harmonic")?.[3]}")`);
    check(JSON.stringify(of("total_raised")) === JSON.stringify(["DIFFERS Total raised: USD 18 million PitchBook", "DIFFERS Total raised: 18,200,000 Harmonic"]) && JSON.stringify(of("founded_year")) === JSON.stringify(["Founded: 2019 PitchBook", "Founded: 2019 Harmonic"])
      && JSON.stringify(of("hq")) === JSON.stringify(["DIFFERS Headquarters: Austin, TX PitchBook", "DIFFERS Headquarters: Austin, Texas, United States Harmonic"]),
      `a fact two providers give differently is marked on each line and both values are kept; one they agree on is not marked ("${of("total_raised").join('" | "')}")`);
    const hover = await evaluate(`(() => { const li = [...document.querySelectorAll('[data-company="Example Storage Inc."] [data-provider="harmonic"]')][0]; return [li.querySelector('[data-provider-tag="harmonic"]').title, document.querySelector('[data-company="Example Storage Inc."] [data-disagree-mark]').title, document.querySelector('[data-company="Example Storage Inc."] [data-pb-tag]').title]; })()`);
    const digest = [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(harmonicPasted)))].map((x) => x.toString(16).padStart(2, "0")).join("");
    check(hover[0].includes(TERMS.harmonic) && hover[0].includes("Figures as returned from Harmonic through the user's own account; not checked by the ERW.") && hover[0].includes("Format erw-harmonic-1.") && /Pasted \d+ \w+ \d{4}, \d\d:\d\d UTC\./.test(hover[0])
      && hover[0].includes(`Hash of the pasted text: ${digest.slice(0, 12)}.`) && hover[1] === "The providers give this differently. Each value is shown as its provider gave it.",
      `the label's hover holds the terms line, the format, the time pasted and the hash of the pasted text (${digest.slice(0, 12)})`);
    check(hover[2].includes(TERMS.pitchbook) && /Hash of the pasted text: [0-9a-f]{12}\./.test(hover[2]) && hover[2].includes("Figures as returned from PitchBook through the user's own account; not checked by the ERW."),
      "PitchBook's label keeps its note and now holds its terms line and the hash of the text its answer was pasted as");
    const notMapped = await evaluate(`(() => { const e = document.querySelector('[data-company="Example Storage Inc."] [data-not-mapped]'); return e ? [e.dataset.notMapped, e.innerText.replace(/\\s+/g, ' ').trim(), e.querySelector('span').title] : null; })()`);
    check(notMapped && notMapped[0] === "6" && notMapped[1] === "6 fields not mapped Harmonic" && notMapped[2].includes("company.stage") && notMapped[2].includes("company.fixture_undocumented_field.nested") && notMapped[2].startsWith("Returned by Harmonic, kept as given and not used here:"),
      `what Harmonic returned that the page does not use is counted and named on hover ("${notMapped?.[1]}")`);
    const grid = await evaluate(`document.querySelector('[data-company="Sample Grid Co"] [data-provider-block]').innerText.replace(/\\s+/g, ' ').trim()`);
    check(/Headquarters: Reno, Nevada, United States Harmonic/.test(grid) && /Employees: 8 Harmonic/.test(grid) && /not found in PitchBook/.test(grid), `a company one provider found and another did not shows the one's figures and says so of the other ("${grid.slice(0, 120)}")`);
    const foundBy = await evaluate(`document.querySelector('[data-provider-additional="harmonic"]')?.innerText.replace(/\\s+/g, ' ') ?? ''`);
    check(/Found by Harmonic/.test(foundBy) && /Harmonic Fixture Later LLC/.test(foundBy) && /Fixture: matched the search words\./.test(foundBy) && /Harmonic saved search of investors: Fixture saved search of investors/.test(foundBy) && /Fixture Fund Three/.test(foundBy) && /investment_count: 31/.test(foundBy)
      && /Harmonic saved search of companies: Fixture saved search of companies/.test(foundBy) && /Saved Fixture Co/.test(foundBy) && (await evaluate(`!!document.querySelector('[data-pb-additional="1"]') && [...document.querySelectorAll('[data-provider-additional="harmonic"] li[data-provider-figure]')].every((e) => !!e.querySelector('[data-provider-tag="harmonic"]'))`)),
      "the companies Harmonic found beyond those asked, and the results of its saved searches of companies, investors and people, are listed with its label; PitchBook's own list stands as it did");
    const againH = await evaluate(`fetch('/api/thesis/provider', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: ${JSON.stringify(JSON.stringify({ run_id: DONE, provider: "harmonic", pasted: JSON.stringify(harmonicAnswer()) }))} }).then(async (r) => [r.status, (await r.json()).reason])`);
    check(againH[0] === 409 && againH[1] === "This run already holds Harmonic's answer.", `one answer a provider and run: a second is ${againH[0]} ("${againH[1]}")`);
    // session 158: with PitchBook's and Harmonic's answers held no provider is left to choose (Crunchbase's answers
    // are not kept), so the panel offers no request; a Crunchbase answer sent straight to the route is refused and
    // the run holds nothing of it. Until this session the check pasted a Crunchbase answer here and saw it received.
    check(!(await evaluate(`!!document.querySelector('[data-thesis-providers="1"]') || !!document.querySelector('[data-thesis-paste="1"]') || !!document.querySelector('[data-thesis-answer="1"]')`))
      && /PitchBook received[\s\S]*Harmonic received/.test(await evaluate(`document.querySelector('[data-thesis-pitchbook="received"]').innerText`)),
      "Harmonic now reads received; with PitchBook's and Harmonic's answers held the panel offers no request and no box (Crunchbase is not to be chosen)");
    const cbStraight = await evaluate(`fetch('/api/thesis/provider', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: ${JSON.stringify(JSON.stringify({ run_id: DONE, provider: "crunchbase", pasted: JSON.stringify(crunchbaseAnswer()) }))} }).then(async (r) => [r.status, (await r.json()).reason])`);
    await go(`${base}/thesis?run=${DONE}&tab=funnel`);
    await wait(`!!document.querySelector('[data-thesis-provider-received="harmonic"]')`, 20000, "the run after the refused Crunchbase answer");
    check(cbStraight[0] === 400 && cbStraight[1] === NOT_KEPT_WORDS && (await evaluate(`!document.querySelector('[data-thesis-provider-received="crunchbase"]') && !document.querySelector('[data-provider="crunchbase"]') && !document.querySelector('[data-provider-tag="crunchbase"]')`)),
      `a Crunchbase answer sent to the route for this run is ${cbStraight[0]} ("${cbStraight[1]}"), and the run shows nothing of it: no figure, no label, not received`);

    // a run that already holds the three providers' answers (the stand-in's own, read by the site's readers) is drawn as before
    if (!html.includes(`data-run="${THREE}"`)) {
      console.log(`not proven here: a run that already holds a Crunchbase answer is still drawn (the stand-in does not hold "${THREE}": start it with --import ./scripts/alias-register.mjs)`);
    } else {
      await go(`${base}/thesis?run=${THREE}&tab=funnel`);
      await wait(`!!document.querySelector('[data-thesis-provider-received="crunchbase"]')`, 20000, "the run that holds three providers' answers");
      check(!(await evaluate(`!!document.querySelector('[data-thesis-providers="1"]')`)) && /PitchBook received[\s\S]*Harmonic received[\s\S]*Crunchbase received/.test(await evaluate(`document.querySelector('[data-thesis-pitchbook="received"]').innerText`)), "with all three held the panel shows the three as received and offers no request");
      figs = await lines();
      check(JSON.stringify(of("founded_year")) === JSON.stringify(["DIFFERS Founded: 2019 PitchBook", "DIFFERS Founded: 2019 Harmonic", "DIFFERS Founded: 2018 Crunchbase"]) && JSON.stringify(of("employees")) === JSON.stringify(["Employees: 42 PitchBook", "Employees: 42 Harmonic", "Employees: 11 to 50 Crunchbase"])
        && JSON.stringify(of("total_raised")) === JSON.stringify(["DIFFERS Total raised: USD 18 million PitchBook", "DIFFERS Total raised: 18,200,000 Harmonic", "DIFFERS Total raised: USD 18 million Crunchbase"]),
        `with three providers each value of a fact they differ on is kept with its label, none averaged or dropped ("${of("founded_year").join('" | "')}"); a count inside another's range is not marked`);
      await go(`${base}/thesis?run=${THREE}&tab=landscape`);
      const cells3 = await evaluate(`[...document.querySelectorAll('[data-company="Example Storage Inc."] td > [data-provider-figure]')].map((e) => e.innerText.replace(/\\s+/g, ' ').trim())`);
      check(cells3.includes("Founders: A. Fixture, C. Fixture PitchBook") && cells3.includes("Founders: A. Fixture, C. Fixture Harmonic") && cells3.includes("Founders: A. Fixture, C. Fixture Crunchbase") && cells3.includes("DIFFERS Headquarters: Austin, Texas, United States Crunchbase")
        && (await evaluate(`[...document.querySelectorAll('[data-pb-figure]')].every((e) => !!e.querySelector('[data-pb-tag]')) && !!document.querySelector('[data-company="Unasked Example LLC"] td') && document.querySelector('[data-company="Unasked Example LLC"]').innerText.includes('USD 2 million') && !document.querySelector('[data-company="Unasked Example LLC"] td:nth-child(4) [data-provider-tag]')`)),
        "in the Company landscape a cell the providers answer holds each provider's figure with its label, and a figure with no provider keeps the label it had");
    }

    // a run asked for on the form: queued, then re-read every 15 seconds until it ends
    await go(`${base}/thesis`);
    await evaluate(`(() => { const el = document.querySelector('input[name="niche"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, 'fixture: monitoring software typed by the check'); el.dispatchEvent(new Event('input', { bubbles: true })); document.querySelector('[data-thesis-run="1"]').click(); return true; })()`);
    await wait(`location.search.includes('run=fixture-new-1') && !!document.querySelector('[data-thesis-watch]')`, 20000, "the queued run");
    check(true, "Run queues a run, the address becomes /thesis?run=<its id>, and the page says it waits");
    await wait(`!!document.querySelector('[data-thesis-failed="1"]')`, 90000, "the run's end, read by the page itself");
    check((await evaluate(`document.querySelector('[data-thesis-failed="1"]').innerText`)).includes("Fixture: a run queued on the stub stops here."), "the page re-reads a waiting run by itself and shows how it ended, with the failed run's note");
    // session 169: the gate on the form. A refusal the table answers is shown at once with its chips; a chip fills the box
    const typeIn = (v) => `(() => { const el = document.querySelector('input[name="niche"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, ${JSON.stringify(v)}); el.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`;
    const oilGas = niche.TABLE.find((t) => t.id === "oil_gas").suggestions;
    await go(`${base}/thesis`);
    await evaluate(typeIn("oil & gas demand"));
    await evaluate(`document.querySelector('[data-thesis-run="1"]').click()`);
    await wait(`!!document.querySelector('[data-thesis-refused="1"]')`, 10000, "the refusal");
    const shown = await evaluate(`[document.querySelector('[data-thesis-refused="1"] p').innerText, [...document.querySelectorAll('[data-thesis-suggestion]')].map((b) => b.innerText), location.search]`);
    check(shown[0] === niche.refusalWords("oil & gas demand") && JSON.stringify(shown[1]) === JSON.stringify(oilGas) && shown[2] === "",
      "on the form the input oil & gas demand is refused with the owner's sentence and his four oil and gas chips, and nothing is queued");
    await evaluate(`document.querySelector('[data-thesis-suggestion]').click()`);
    await wait(`document.querySelector('input[name="niche"]').value === ${JSON.stringify(oilGas[0])} && !document.querySelector('[data-thesis-refused="1"]')`, 5000, "the chip in the box");
    check(true, "a chip puts its niche in the box and the refusal goes");
    // Run anyway: ticked on the refused input, the run is queued through thesis_submit_forced with its gate
    await evaluate(typeIn("oil & gas demand"));
    await evaluate(`document.querySelector('[data-thesis-run="1"]').click()`);
    await wait(`!!document.querySelector('[data-thesis-anyway="1"]')`, 10000, "the Run anyway box");
    await evaluate(`document.querySelector('[data-thesis-anyway="1"]').click()`);
    await evaluate(`document.querySelector('[data-thesis-run="1"]').click()`);
    await wait(`location.search.includes('run=fixture-new-2')`, 20000, "the forced run queued");
    await go(`${base}/thesis?run=fixture-new-2`);      // read afresh: the page's own re-reading is proven above
    await wait(`!!document.querySelector('[data-thesis-failed="1"]')`, 90000, "the forced run's end");
    check((await evaluate(`document.querySelector('[data-thesis-failed="1"]').innerText`)).includes("Fixture: a run started with Run anyway (sector_only) and kept with its gate"),
      "Run anyway queues the refused niche through thesis_submit_forced, with what the gate read of it");
    await go(`${base}/thesis?run=${FORCED}`);
    await wait(`!!document.querySelector('[data-thesis-report]')`, 20000, "the forced run's report");
    const mark = await evaluate(`(() => { const m = document.querySelector('[data-thesis-forced="1"]'); return m ? [m.textContent, m.title] : null; })()`);
    check(!!mark && mark[0].trim() === niche.FORCED_MARK && mark[1] === niche.FORCED_NOTE, "a forced run's report carries the mark run anyway with its reason on hover");
    await go(`${base}/thesis?run=${DONE}`);
    await wait(`!!document.querySelector('[data-thesis-report]')`, 20000, "the done run's report");
    check(await evaluate(`!document.querySelector('[data-thesis-forced]')`), "a run that passed the gate carries no mark");
    // session 169: the market research's report (version 2), and the connector tabs
    await go(`${base}/thesis?run=${MARKET}&tab=trends`);
    await wait(`document.querySelectorAll('[data-trend]').length === 5`, 20000, "the market run's trends");
    const tr = await evaluate(`[...document.querySelectorAll('[data-trend]')].map((s) => [s.dataset.series, !!s.querySelector('[data-chart="trend"]'), (s.querySelector('[data-fact]')?.innerText ?? '').slice(0, 5), s.querySelector('[data-source-line]')?.innerText ?? '', s.querySelector('[data-missing="no_series"]')?.title ?? ''])`);
    check(tr.filter((t) => t[1]).length === 2 && tr[0][0] === "eia:fixture:1" && tr[0][3].startsWith("Source: U.S. Energy Information Administration") && tr.every((t) => t[2] === "Fact:")
      && tr[1][4] === "Fixture: no real series measures this trend, so it is not drawn." && !tr[1][1], "a market trend states its Fact; two draw their series with the publisher's source line; the others say they are not drawn, the reason on hover");
    const mtip = await evaluate(`(() => { const el = document.querySelector('[data-chart="trend"]'); const chart = window.echarts.getInstanceByDom(el); chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: 2 });
      return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /\\d/.test(t)).sort((x, y) => y.length - x.length)[0] ?? ''), 500)); })()`);
    check(/12\.5/.test(String(mtip)) && /2025/.test(String(mtip)), `a market trend's chart answers the mouse with the period and the value as published ("${String(mtip).replace(/\s+/g, " ").slice(0, 80)}")`);
    for (const tab of ["landscape", "funnel", "pipeline", "success", "investors"]) {
      await go(`${base}/thesis?run=${MARKET}&tab=${tab}`);
      await wait(`!!document.querySelector('[data-thesis-tab="${tab}"]')`, 20000, `the ${tab} tab`);
      const c = await evaluate(`(() => { const d = document.querySelector('[data-connector="${tab}"]'); return d ? [d.innerText.split('\\n')[0], d.querySelectorAll('th').length] : null; })()`);
      check(!!c && c[0].includes(CONNECTOR_NOTE) && c[1] >= 5, `the ${tab} tab of a market run is the greyed placeholder "${CONNECTOR_NOTE}" with its ${c ? c[1] : 0} columns`);
    }
    for (const [tab, want] of [["landscape", 2], ["pipeline", 1], ["success", 1], ["investors", 2], ["funnel", 2]]) {
      await go(`${base}/thesis?run=${MARKET_PB}&tab=${tab}`);
      await wait(`!!document.querySelector('[data-thesis-tab="${tab}"]')`, 20000, `the ${tab} tab with PitchBook`);
      const n = await evaluate(`[document.querySelectorAll('[data-connector-row="${tab}"]').length, [...document.querySelectorAll('[data-connector-row="${tab}"]')].every((r) => !!r.querySelector('[data-pb-tag]'))]`);
      check(n[0] === want && n[1], `with a PitchBook answer pasted the ${tab} tab holds ${n[0]} rows (${want} expected), each with the PitchBook tag`);
    }
    await go(`${base}/thesis?run=${MARKET}&tab=timing`);
    await wait(`!!document.querySelector('[data-timing]')`, 20000, "the timing tab");
    check((await evaluate(`document.querySelector('[data-timing]').innerText`)).toLowerCase().includes("being installed"), "the Timing tab says whether the market is being installed or deploying, with its evidence");
    await go(`${base}/thesis?run=${MARKET}&tab=references`);
    await wait(`!!document.querySelector('[data-references]')`, 20000, "the references tab");
    check(await evaluate(`document.querySelectorAll('[data-reference]').length === 2 && !!document.querySelector('[data-reference="S9"] a[href^="https://www.eia.gov/"]')`), "the References tab lists every source the report cites, each with its link");
    await go(`${base}/thesis?run=${DONE}&tab=landscape`);
    await wait(`!!document.querySelector('[data-thesis-tab="landscape"]')`, 20000, "an old run's landscape");
    check(await evaluate(`!document.querySelector('[data-connector="landscape"]') && document.querySelectorAll('[data-company]').length > 0`), "a run written before keeps its own company landscape as it was drawn");
    await go(`${base}/thesis?run=${DONE}&tab=timing`);
    await wait(`!!document.querySelector('[data-thesis-tab="timing"]')`, 20000, "an old run's timing tab");
    check((await evaluate(`document.querySelector('[data-thesis-tab="timing"]').innerText`)).includes("This run was written before the Timing tab existed."), "a run written before says it has no Timing tab");
    check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 160)}` : ""}`);
    await sleep(100);
    return 0;
  });
  if (code === null) console.log("not proven here: no browser on this machine (the HTML checks above stand)");
  else {
    await withBrowser(async ({ go, evaluate, wait, unlock: open, send }) => {
      await open(base);
      await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: false });
      for (const t of ["trends", "landscape"]) {
        await go(`${base}/thesis?run=${DONE}&tab=${t}`);
        await wait(`!!document.querySelector('[data-thesis-tab="${t}"]')`, 20000, `the ${t} tab on a phone`);
        const w = await evaluate(`[document.documentElement.scrollWidth, window.innerWidth]`);
        check(w[0] <= w[1] + 1, `at a phone's width the ${t} tab does not scroll sideways (${w[0]} in ${w[1]}); its tables scroll inside themselves`);
      }
      return 0;
    }, { width: 390, height: 844 });
  }
}
console.log(`${n - bad} of ${n} checks pass`);
process.exitCode = bad ? 1 : 0;
