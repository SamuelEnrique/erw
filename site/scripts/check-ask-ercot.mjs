// Energy Research Warehouse (ERW) site, session 92: Ask ERCOT's link and context, in a real browser.
//
//   npm run build && npx next start -p 3092
//   node scripts/check-ask-ercot.mjs [base-url]      (default http://localhost:3092)
//
// The link "Ask ERCOT about this view" is drawn by the browser, not the server (it shows only in the internal view while
// /ask/ercot is in review), so a plain request cannot see it. In a real browser:
//   as a visitor   the battery page (a live page) holds no such link, and no text of it
//   internal view  each ERCOT view holds the link, its address carries the view and its settings, a view of another
//                  grid holds none, and following the link opens /ask/ercot with the view named above the question box
// It never asks a question: no model call is made. Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3092").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const LINK = `(() => { const p = document.querySelector('[data-ask-ercot]'); return p ? { view: p.getAttribute('data-ask-ercot'), href: p.querySelector('a')?.getAttribute('href') ?? null } : null; })()`;
const settled = `document.readyState === 'complete'`;

const VIEWS = [
  ["/cost-of-power/battery?grid=ercot&dur=8&strat=dayahead", "/cost-of-power/battery", { grid: "ERCOT", duration: "8 hours" }],
  ["/cost-of-power/seller?iso=ercot&asset=wind", "/cost-of-power/seller", { grid: "ERCOT" }],
  ["/shoulder?grid=ercot&month=2025-01", "/shoulder", { grid: "ERCOT", month: "2025-01" }],
  ["/storage/buildout?grid=ercot&measure=mwh", "/storage/buildout", { grid: "ERCOT" }],
  ["/storage/owners?grid=ercot", "/storage/owners", { grid: "ERCOT" }],
  ["/grid/ercot", "/grid/ercot", { grid: "ERCOT" }],
  ["/explorer/ercot-peak-premium", "/explorer/ercot-peak-premium", { grid: "ERCOT" }],
  ["/events/uri-2021", "/events/uri-2021", { event: "uri_2021" }],
];
const OTHERS = ["/cost-of-power/battery?grid=caiso", "/shoulder?grid=caiso", "/storage/buildout?grid=caiso", "/grid/caiso", "/cost-of-power/seller?iso=caiso&asset=solar"];

const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep }) => {
  // a visitor: nothing of the link on a live page
  await go(`${base}/cost-of-power/battery`);
  await wait(settled);
  await sleep(1500);
  check((await evaluate(LINK)) === null && !(await evaluate(`document.body.innerText.includes('Ask ERCOT')`)), "a visitor's battery page holds no link to Ask ERCOT and no text of one");
  await go(`${base}/ask/ercot`);
  check(await evaluate(`document.body.innerText.toLowerCase().includes('in review')`), "a visitor asking for /ask/ercot gets the in-review page");

  await unlock(base);
  for (const [page, view, settings] of VIEWS) {
    await go(base + page);
    let link = null;
    try { link = await wait(LINK, 10000, `the link on ${page}`); } catch { /* reported below */ }
    const params = link?.href ? Object.fromEntries(new URL(link.href, base).searchParams) : {};
    check(!!link && link.view === view && link.href.startsWith("/ask/ercot?") && params.from === view
      && Object.entries(settings).every(([k, v]) => params[`s_${k}`] === v), `${page}: the link carries the view ${view} and ${JSON.stringify(settings)} (${link?.href ?? "no link"})`);
  }
  for (const page of OTHERS) {
    await go(base + page);
    await wait(settled);
    await sleep(1200);
    check((await evaluate(LINK)) === null, `${page}: another grid's view holds no link to Ask ERCOT`);
  }
  // following the link: the chat names the view and its settings, and has asked nothing yet
  await go(`${base}/shoulder?grid=ercot&month=2025-01`);
  const link = await wait(LINK, 10000, "the link on /shoulder");
  await go(base + link.href);
  const ctx = await wait(`(() => { const p = document.querySelector('[data-context]'); return p ? { view: p.getAttribute('data-context'), text: p.innerText } : null; })()`, 10000, "the context above the question box");
  check(ctx.view === "/shoulder" && ctx.text.includes("The shoulder hours") && ctx.text.includes("month 2025-01") && ctx.text.includes("grid ERCOT"), `the chat opens with the view named: ${ctx.text.slice(0, 120)}`);
  check(await evaluate(`document.querySelector('h1')?.innerText === 'Ask ERCOT' && !!document.querySelector('#q') && !document.querySelector('[data-answer]')`), "the page is Ask ERCOT, with its question box and no answer yet");
  // a question carried in the address fills the box and is not asked by itself
  await go(`${base}/ask/ercot?from=%2Fcost-of-power%2Fbattery&s_duration=8+hours&q=What+did+this+battery+earn%3F`);
  await wait(`!!document.querySelector('#q')`);
  check((await evaluate(`document.querySelector('#q').value`)) === "What did this battery earn?" && !(await evaluate(`!!document.querySelector('[data-answer]')`)), "a question in the address fills the box and waits for the reader");
  // an answer, drawn: the route's reply is a recorded one (tests/fixtures/session92/site_answer.json, a real answer of
  // this page saved in session 92), so no model is called. The chart, the rows with their source and the follow-ups
  // must be there, and a follow-up asks itself with the same context.
  const fixture = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session92/site_answer.json", import.meta.url), "utf-8"));
  await go(`${base}/ask/ercot?from=%2Fstorage%2Fbuildout&s_grid=ERCOT`);
  await wait(`!!document.querySelector('#q')`);
  await evaluate(`(() => { window.__asked = []; const real = window.fetch;
    window.fetch = async (u, o) => String(u).includes('/api/ask') ? (window.__asked.push(JSON.parse(o.body)), new Response(${JSON.stringify(JSON.stringify(fixture))}, { status: 200, headers: { 'Content-Type': 'application/json' } })) : real(u, o);
    const q = document.querySelector('#q'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(q, 'How has the fleet grown?'); q.dispatchEvent(new Event('input', { bubbles: true }));
    return true; })()`);
  await wait(`!document.querySelector('form button[type=submit]').disabled`);
  await evaluate(`document.querySelector('form button[type=submit]').click()`);
  await wait(`!!document.querySelector('[data-series]')`, 15000, "the series under the answer");
  const s0 = fixture.series[0];
  const drawn = await wait(`(() => { const b = document.querySelector('[data-series]'); const c = b.querySelector('canvas, svg'); return c && c.getBoundingClientRect().width > 100 ? { rows: b.querySelectorAll('tbody tr').length,
    text: b.innerText, first: b.querySelector('tbody tr')?.innerText ?? '' } : null; })()`, 15000, "the chart of the series");
  check(drawn.rows === s0.rows.length && drawn.first.includes(s0.rows[0].key) && drawn.first.includes(s0.table), `the series is drawn as a chart with its ${s0.rows.length} rows, each naming ${s0.table} (${drawn.first.replace(/\s+/g, " ")})`);
  check(drawn.text.includes("Source: ERW table") && drawn.text.includes(s0.source_report), "the series states its table and source report");
  check((await evaluate(`document.querySelector('[data-answer]').innerText`)) === fixture.answer, "the answer shown is the route's answer, character for character");
  const ups = await evaluate(`[...document.querySelectorAll('[data-followups] button')].map((b) => b.innerText)`);
  check(JSON.stringify(ups) === JSON.stringify(fixture.followups) && ups.length >= 2 && ups.length <= 3, `${ups.length} follow-up questions are offered`);
  await evaluate(`document.querySelector('[data-followups] button').click()`);
  await wait(`window.__asked.length === 2`, 10000, "the follow-up to be asked");
  const asked = await evaluate(`window.__asked`);
  check(asked[0].profile === "ercot" && asked[0].question === "How has the fleet grown?" && asked[0].context?.view === "/storage/buildout"
    && asked[1].question === fixture.followups[0] && asked[1].profile === "ercot" && asked[1].context?.view === "/storage/buildout", "a follow-up asks itself, with the profile and the view it came from");
  return bad ? 1 : 0;
});
if (code === null) { console.log("check-ask-ercot: NOT PROVEN on this machine: no Chrome or Edge was found (set BROWSER_PATH)"); process.exit(0); }
console.log(bad ? `${bad} of ${n} checks FAILED` : `Ask ERCOT in a browser: ${n} checks pass`);
process.exit(code);
