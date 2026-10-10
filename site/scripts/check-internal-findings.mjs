// Energy Research Warehouse (ERW) site, session 181: /internal/findings, the scanner's review list, on the built site
// against the local stand-in for migration 029's functions (scripts/findings-stub.mjs, started here).
//
//   npm run build
//   SUPABASE_URL=http://localhost:54381 SUPABASE_ANON_KEY=local npx next start -p 3181      (the stand-in's address)
//   node scripts/check-internal-findings.mjs [base-url] [stub-port]                         (default http://localhost:3181, 54381)
//
//   hidden     without the internal cookie the page, the approved list and the state route answer 404; a token in the
//              address opens nothing
//   list       with the cookie the page lists every draft of the fixture, strongest first, each with its card (title,
//              subtitle, the callouts' numbers as the card's JSON holds them, the footnote), marked as a draft, with no
//              paragraph, and three buttons; the page is noindex and no-store
//   rulings    Approve, Dismiss and Ask for a full card are POSTs that change the state, each kept with its time; a bad
//              id, a bad state, a body that is not JSON and a request from another origin are refused
//   /analysis  the approved draft is in the scanner's group, marked "Found by the scanner" with its date; the
//              dismissed one and the ones not ruled on are not (the list the page reads, and the page in a real browser)
//   a request  a done request's card is read from its queue row (GET /api/analysis?id=): drawn under the list in a
//              browser, with its numbers, its second chart and three downloads; the CSV the page makes holds the rows
//              of the committed CSV; a visitor is answered 404
//   phone      /internal/findings and the impact study's form at 390 px do not scroll sideways
// Exit 1 on a failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, withBrowser } from "./browser.mjs";
import { BACKTEST, DONE_ID, fixtureRows, startStub } from "./findings-stub.mjs";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");

const base = (process.argv[2] ?? "http://localhost:3181").replace(/\/$/, "");
const stubPort = Number(process.argv[3] ?? 54381);
let bad = 0, n = 0;
const check = (ok, what, shown = "") => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what} ${shown}`); } else console.log(`ok   ${what} ${shown}`); };
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/'/g, "&#x27;").replace(/"/g, "&quot;");
const text = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ")
  .replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&").replace(/\s+/g, " ");

// the first run's drafts, and one draft of a backtest (22 February 2021) on a series the impact study knows
const backtest = fixtureRows(BACKTEST);
const stub = await startStub(stubPort, { rows: [...fixtureRows(), ...backtest] });
let code = 1;
try {
  const token = env("INTERNAL_COSTS_TOKEN") ?? "";
  const drafts = [...stub.rows].sort((a, b) => b.strength - a.strength);
  const firstRun = drafts.filter((d) => !backtest.some((x) => x.id === d.id));
  check(firstRun.length >= 3 && backtest.length === 1, `${firstRun.length} drafts of the first run and ${backtest.length} of the backtest`);

  // hidden
  const noCookie = await fetch(`${base}/internal/findings`);
  check(noCookie.status === 404, "without the cookie /internal/findings is 404", `(${noCookie.status})`);
  const withToken = await fetch(`${base}/internal/findings?token=${encodeURIComponent(token)}`);
  check(withToken.status === 404, "a token in the address opens nothing", `(${withToken.status})`);
  const apNo = await fetch(`${base}/internal/findings/approved`);
  check(apNo.status === 404 && (await apNo.text()) === "", "without the cookie the approved list is 404 with an empty body", `(${apNo.status})`);
  const postNo = await fetch(`${base}/internal/findings/state`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: drafts[0].id, state: "approved" }) });
  check(postNo.status === 404 && stub.rows.every((r) => r.state === "draft"), "without the cookie a ruling is 404 and changes nothing", `(${postNo.status})`);

  const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(token)}`, { redirect: "manual" });
  const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
  if (!cookie) throw new Error(`${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`);
  const page = async () => { const r = await fetch(`${base}/internal/findings`, { headers: { Cookie: cookie } }); return { r, html: await r.text() }; };
  const rule = (body, headers = {}) => fetch(`${base}/internal/findings/state`, { method: "POST", headers: { "Content-Type": "application/json", Cookie: cookie, ...headers }, body: typeof body === "string" ? body : JSON.stringify(body) });

  // list
  const { r, html } = await page();
  const t = text(html);
  check(r.status === 200 && html.includes(`data-drafts="${drafts.length}"`), `with the cookie the page lists ${drafts.length} drafts`, `(${r.status})`);
  check(/no-store/.test(r.headers.get("cache-control") ?? ""), "the page is no-store", `(${r.headers.get("cache-control")})`);
  check(/noindex/.test(r.headers.get("x-robots-tag") ?? "") || /<meta name="robots" content="noindex/.test(html), "the page is noindex");
  check(!html.includes(token), "the token is nowhere in the page");
  const order = [...html.matchAll(/data-draft-id="([^"]+)"/g)].map((m) => m[1]);
  check(JSON.stringify(order) === JSON.stringify(drafts.map((d) => d.id)), "the drafts are strongest first", `(${order.length})`);
  for (const d of drafts) {
    const c = d.card, tag = `${d.id}:`;
    check(html.includes(`data-card="${d.id}"`) && html.includes(`data-draft-mark="${d.id}"`), `${tag} its card is drawn and marked as a draft`);
    check(t.includes(c.title) && t.includes(c.subtitle.replace(/\s+/g, " ")), `${tag} title and subtitle`);
    c.callouts.forEach((co, i) => check(html.includes(`>${esc(co.before.text)}<`) && html.includes(`>${esc(co.after.text)}<`), `${tag} callout ${i}: ${co.before.text} | ${co.after.text}`));
    check(t.includes(c.footnote.replace(/\s+/g, " ").slice(0, 120)), `${tag} footnote`);
    check(html.includes(`data-draft-review="${d.id}"`), `${tag} the review block`);
  }
  check(!html.includes('data-finding-why="1"'), "no draft has a paragraph");
  check(!html.includes("data-download="), "a draft offers no download and no render");
  for (const b of ["approved", "dismissed", "full_card_asked"]) {
    check((html.match(new RegExp(`data-draft-button="${b}"`, "g")) ?? []).length === drafts.length, `every draft has the ${b} button`);
  }
  check(html.includes('data-finding-chart="flag_line"'), "the charts are the interactive kind (flag_line)");

  // rulings
  const [a, b, c] = firstRun;
  const ra = await rule({ id: a.id, state: "approved" }); const ja = await ra.json();
  check(ra.status === 200 && ja.ok && ja.state === "approved" && /Z$/.test(ja.at ?? ""), "Approve is a POST that answers the state and its time", JSON.stringify(ja));
  const rb = await rule({ id: b.id, state: "dismissed" }); const jb = await rb.json();
  check(rb.status === 200 && jb.ok && jb.state === "dismissed", "Dismiss changes the state", JSON.stringify(jb));
  const rc = await rule({ id: c.id, state: "full_card_asked" }); const jc = await rc.json();
  const wantsRequest = Boolean(c.card.scanner?.full_card);
  check(rc.status === 200 && jc.ok && jc.state === "full_card_asked" && (wantsRequest ? stub.requests.length === 2 && jc.request_id === stub.requests[1].id : stub.requests.length === 1 && /session writes the card/.test(jc.note)),
    `Ask for a full card ${wantsRequest ? "queues the impact study and keeps the request id" : "marks the draft for a session (no analysis fits its series)"}`, JSON.stringify(jc));
  const withFull = drafts.find((d) => d.card.scanner?.full_card && ![a.id, b.id, c.id].includes(d.id));
  check(Boolean(withFull), "one draft names an analysis for its full card (the backtest's, on ERCOT North Hub real-time)");
  if (withFull) {
    const before = stub.requests.length;
    const rf = await rule({ id: withFull.id, state: "full_card_asked" }); const jf = await rf.json();
    const q = stub.requests[stub.requests.length - 1];
    check(rf.status === 200 && jf.ok && stub.requests.length === before + 1 && q.finding === "impact_study" && q.params.series === String(withFull.card.scanner.full_card.params.series) && jf.request_id === q.id,
      `${withFull.id}: a full card on a series the impact study knows queues it`, JSON.stringify(q?.params));
    const again = await rule({ id: withFull.id, state: "full_card_asked" }); const jg = await again.json();
    check(again.status === 200 && jg.ok && stub.requests.length === before + 1 && /already asked/.test(jg.note), "asking twice queues once", jg.note);
    check(q.params.event === "date" && q.params.window === "14" && q.params.control === String(withFull.card.scanner.full_card.params.control), "the queued request is the impact study around the flagged date, 14 days, its default control", JSON.stringify(q.params));
  }
  check(stub.rows.find((x) => x.id === a.id).state_history.length === 1 && stub.rows.find((x) => x.id === a.id).state_history[0].from === "draft", "the change is kept with its time and what it was before");
  for (const [what, res, want] of [
    ["an id that is not a flag's", await rule({ id: "x; drop table", state: "approved" }), 400],
    ["an unknown state", await rule({ id: a.id, state: "published" }), 400],
    ["a body that is not JSON", await rule("approve it"), 400],
    ["a form's content type", await rule(`id=${a.id}&state=approved`, { "Content-Type": "application/x-www-form-urlencoded" }), 415],
    ["a request from another site", await rule({ id: a.id, state: "dismissed" }, { Origin: "https://example.org" }), 404],
  ]) check(res.status === want, `${what} is refused`, `(${res.status}, ${want} expected)`);
  check(stub.rows.find((x) => x.id === a.id).state === "approved", "the refused requests changed nothing");
  const after = await page();
  check(new RegExp(`data-draft-review="${a.id}" data-draft-state="approved"`).test(after.html) && new RegExp(`data-draft-review="${b.id}" data-draft-state="dismissed"`).test(after.html)
    && new RegExp(`data-draft-review="${c.id}" data-draft-state="full_card_asked"`).test(after.html), "the page shows the three rulings");
  check(after.html.includes('data-n="approved">1<') && after.html.includes('data-n="dismissed">1<') && after.html.includes(`data-n="full_card_asked">${withFull ? 2 : 1}<`), "the counts by state follow");

  // /analysis
  const ap = await fetch(`${base}/internal/findings/approved`, { headers: { Cookie: cookie } });
  const apj = await ap.json();
  check(ap.status === 200 && apj.drafts.length === 1 && apj.drafts[0].id === a.id && apj.drafts[0].card.draft === true, "the approved list holds the approved draft alone", `(${apj.drafts.map((d) => d.id).join(", ")})`);
  check(/no-store/.test(ap.headers.get("cache-control") ?? ""), "the approved list is no-store");
  const an = await fetch(`${base}/analysis`, { headers: { Cookie: cookie } });
  const anHtml = await an.text();
  check(an.status === 200 && text(anHtml).includes("Found by the scanner") && anHtml.includes("data-scanner-cards="), "/analysis has the scanner's group");
  check(anHtml.includes('data-impact-form="1"') && anHtml.includes('data-impact-input="series"') && anHtml.includes('data-impact-input="control"') && anHtml.includes('data-impact-input="event"')
    && anHtml.includes('data-impact-input="window"') && anHtml.includes('data-impact-reset="1"'), "/analysis has the impact study's inputs with a Reset");
  check(!anHtml.includes(b.id), "the dismissed draft is nowhere in /analysis's HTML");
  const visitor = await fetch(`${base}/analysis`);
  check((await visitor.text()).includes('data-in-review="1"'), "a visitor still sees the in-review page");

  // a request's card, read from its queue row (the stand-in holds one done request: the committed impact card)
  const committed = JSON.parse(fs.readFileSync(path.join(site, "data", "findings", "impact_study.json"), "utf-8"));
  const one = await fetch(`${base}/api/analysis?id=${DONE_ID}`, { headers: { Cookie: cookie } });
  const oneJ = await one.json();
  check(one.status === 200 && oneJ.request?.status === "done" && oneJ.request.card?.card_id === "impact_study" && oneJ.request.card.numbers.reg_did === committed.numbers.reg_did,
    "GET /api/analysis?id= answers the done request with its card", `(${one.status})`);
  check((await fetch(`${base}/api/analysis?id=${DONE_ID}`)).status === 404, "a visitor is answered 404 for a request's card");
  const absent = await fetch(`${base}/api/analysis?id=nothing-here-0000`, { headers: { Cookie: cookie } });
  const notAnId = await fetch(`${base}/api/analysis?id=${encodeURIComponent("x'; drop")}`, { headers: { Cookie: cookie } });
  check(absent.status === 404 && notAnId.status === 400, "a request that is not there is 404, an id that is not one is 400", `(${absent.status}, ${notAnId.status})`);
  check(Array.isArray(committed.rows) && committed.rows.length > 40 && typeof committed.do_file === "string" && committed.csv_name === committed.downloads.csv, "the impact card carries its rows and its do-file");

  const seen = await withBrowser(async ({ go, wait, evaluate, unlock: open, send, errors }) => {
    await open(base);
    await go(`${base}/analysis`);
    await wait(`!!document.querySelector('[data-request-show="${DONE_ID}"]')`, 20000, "the done request in the list");
    await evaluate(`document.querySelector('[data-request-show="${DONE_ID}"]').click()`);
    await wait(`!!document.querySelector('[data-request-card="done"] [data-more-chart] canvas')`, 20000, "the request's card with its second chart");
    const rq = await evaluate(`(() => { const box = document.querySelector('[data-request-card="done"]'); return { text: box.innerText.replace(/\\s+/g, " "), table: !!box.querySelector('[data-effect-table]'),
      downloads: [...box.querySelectorAll('[data-request-downloads] [data-download]')].map((e) => e.dataset.download), files: box.querySelectorAll('a[href$=".csv"]').length,
      py: box.querySelector('[data-download="python"]').getAttribute("href") }; })()`);
    const nn = committed.numbers, f2 = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    check([nn.series_pre, nn.series_post, nn.control_pre, nn.control_post, nn.did_abs, nn.reg_did_se].every((v) => rq.text.includes(f2(v))) && rq.text.includes(committed.why.replace(/\s+/g, " ")),
      "the request's card shows the computed numbers and the sentence written by code");
    check(rq.table && JSON.stringify(rq.downloads) === JSON.stringify(["csv", "python", "stata"]) && rq.py === "/findings/impact_study.py" && rq.files === 0,
      "it has its table, its second chart and three downloads made from the card", JSON.stringify(rq.downloads));
    // the CSV the page makes from the card's rows, against the committed CSV: the same comment lines, columns and values
    const made = await evaluate(`(async () => { const blobs = []; const make = URL.createObjectURL.bind(URL); URL.createObjectURL = (b) => { blobs.push(b); return make(b); };
      document.querySelector('[data-request-card="done"] button[data-download="csv"]').click(); return blobs.length ? await blobs[0].text() : ""; })()`);
    const file = fs.readFileSync(path.join(site, "public", "findings", committed.downloads.csv), "utf-8");
    const NL = String.fromCharCode(10);
    const parse = (t) => t.split(NL).filter((l) => l && !l.startsWith("#")).map((l) => l.split(","));
    const [pa, pb] = [parse(made), parse(file)];
    const same = pa.length === pb.length && pa.every((r, i) => r.length === pb[i].length && r.every((v, j) => v === pb[i][j] || (v !== "" && pb[i][j] !== "" && Math.abs(Number(v) - Number(pb[i][j])) < 1e-9)));
    check(made.split(NL).slice(0, 4).join("|") === file.split(NL).slice(0, 4).join("|") && same && pa.length > 40, "the CSV the page makes holds the committed CSV's comment lines and rows", `(${pa.length - 1} rows)`);
    await wait(`document.querySelector('[data-scanner-cards]')?.dataset.scannerCards === "1"`, 20000, "the scanner's group with one card");
    const s = await evaluate(`({ found: [...document.querySelectorAll("[data-found-by-scanner]")].map((e) => e.dataset.foundByScanner + "|" + e.textContent),
      cards: [...document.querySelectorAll("[data-scanner-cards] [data-card]")].map((e) => e.dataset.card), chart: !!document.querySelector("[data-scanner-cards] [data-finding-chart] canvas"),
      draftMarks: document.querySelectorAll("[data-scanner-cards] [data-draft-mark]").length })`);
    check(s.cards.length === 1 && s.cards[0] === a.id, "in a browser, /analysis draws the approved draft and no other", `(${s.cards.join(", ")})`);
    check(s.found.length === 1 && s.found[0].startsWith(`${a.id}|Found by the scanner, flagged ${a.flag_date}`), "it is marked Found by the scanner with its date", `(${s.found[0]})`);
    check(s.chart, "its chart is drawn (a canvas that answers the mouse)");
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    for (const p of ["/internal/findings", "/analysis"]) {
      await go(`${base}${p}`);
      await wait(p === "/analysis" ? `!!document.querySelector('[data-impact-form]')` : `!!document.querySelector('[data-drafts]')`, 20000, `${p} at 390 px`);
      const w = await evaluate(`({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth,
        form: (() => { const f = document.querySelector('[data-impact-form]'); return f ? Math.round(f.getBoundingClientRect().right) : null; })() })`);
      check(w.client === 390 && w.scroll <= w.client + 1, `${p} at 390 px does not scroll sideways`, `(scroll width ${w.scroll}, width ${w.client}${w.form !== null ? `, the form ends at ${w.form}` : ""})`);
    }
    check(errors.length === 0, "no exception in the pages", errors.slice(0, 2).join(" | "));
    return 0;
  });
  if (seen === null) console.log("note no browser on this machine: the browser checks of /analysis and of 390 px are not proven here");
  code = bad ? 1 : 0;
} catch (e) {
  console.log(`FAILED: ${e.message}`);
  code = 1;
} finally {
  await stub.close();
}
console.log(`${n - bad} of ${n} checks passed`);
await new Promise((done) => process.stdout.write("", done));
process.exit(code);
