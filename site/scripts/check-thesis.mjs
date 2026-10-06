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
// Exit 1 on a failure.
import { env, withBrowser } from "./browser.mjs";
import { EMPTY_TAB, PB_PENDING, PB_PENDING_WHY, TABS } from "../lib/thesis/view.ts";
import { DONE, FAILED, KEY, QUEUED, fixtureAnswer } from "./thesis-stub.mjs";

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
    await go(`${base}/thesis?run=${DONE}&tab=pipeline`);
    check(await evaluate(`!!document.querySelector('[data-company="Example Storage Inc."] [data-pb-block]') && [...document.querySelectorAll('[data-pb-figure]')].every((e) => !!e.querySelector('[data-pb-tag]')) && !!document.querySelector('[data-company="Sample Grid Co"] [data-missing="pitchbook_absent"]')`),
      "in the Pipeline map too; a cell PitchBook's answer holds nothing for says so");

    // a run asked for on the form: queued, then re-read every 15 seconds until it ends
    await go(`${base}/thesis`);
    await evaluate(`(() => { const el = document.querySelector('input[name="niche"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, 'fixture: a niche typed by the check'); el.dispatchEvent(new Event('input', { bubbles: true })); document.querySelector('[data-thesis-run="1"]').click(); return true; })()`);
    await wait(`location.search.includes('run=fixture-new-1') && !!document.querySelector('[data-thesis-watch]')`, 20000, "the queued run");
    check(true, "Run queues a run, the address becomes /thesis?run=<its id>, and the page says it waits");
    await wait(`!!document.querySelector('[data-thesis-failed="1"]')`, 90000, "the run's end, read by the page itself");
    check((await evaluate(`document.querySelector('[data-thesis-failed="1"]').innerText`)).includes("Fixture: a run queued on the stub stops here."), "the page re-reads a waiting run by itself and shows how it ended, with the failed run's note");
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
