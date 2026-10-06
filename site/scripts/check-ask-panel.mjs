// Energy Research Warehouse (ERW) site, session 137: the question box and its answer panel (components/ask/AskPanel.tsx)
// where it is placed on /grid/ercot, in a real browser, WITHOUT a model call: the route's replies are recorded ones.
//
//   npm run build && npx next start -p 3137
//   node --import ./scripts/alias-register.mjs scripts/check-ask-panel.mjs [base-url]      (default http://localhost:3137)
//
// The chart's reply is tests/fixtures/session92/site_answer.json (a real answer of Ask ERCOT saved in session 92), sent
// once as form "chart" and once, its series removed, as form "sentence"; the words' reply is the real answer the
// evaluation of 6 October 2026 got to "What is a hub?" (warehouse/chat/eval_ercot_panel_results.csv, c02).
// Checked: the panel is on the page in the place of the old box; the answer sits right below the box and the newest
// answer comes first; an answer in words or in a sentence shows no chart and no table; an answer of form "chart" shows
// a chart that answers the mouse and the rows it was drawn from; the question goes to the route as the ERCOT profile,
// streamed; a visitor's page is the in-review page. Exit 1 on a failure.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3137").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const chart = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session92/site_answer.json", import.meta.url), "utf-8"));
const WORDS = { type: "result", status: "answered", form: "words", series: [], followups: ["What is a locational marginal price?", "How does the day-ahead market differ from the real-time market?"],
  answer: "A hub is an average of the prices at many grid locations, used as one reference price that traders use.", model: "recorded", tool_calls: 0, retried: false, cost_usd: null, calls: [], nearest: [], premise: "",
  citations: [{ table: "docs/grids/ercot.md", source_report: "docs/grids/ercot.md: text written for the ERW's ERCOT page; each section names its ISO and EIA sources", data_version: "the site's build", tier: "written" }] };
const replies = [WORDS, { type: "result", ...chart, form: "sentence", series: [] }, { type: "result", ...chart, form: "chart" }];

const visitor = await fetch(`${base}/grid/ercot`);
check((await visitor.text()).includes("in review"), "a visitor asking for /grid/ercot gets the in-review page");

const code = await withBrowser(async ({ go, evaluate, wait, unlock, errors }) => {
  await unlock(base);
  await go(`${base}/grid/ercot`);
  await wait(`!!document.querySelector('[data-ask-panel="ercot"] #ask-grid')`, 30000, "the panel on /grid/ercot");
  check(await evaluate(`document.querySelectorAll('[data-ask-panel]').length === 1 && !document.querySelector('form[action="/ask"]')`), "the page holds one panel, in the place of the box that opened /ask");
  check(await evaluate(`(() => { const p = document.querySelector('[data-ask-panel]'); const h = [...document.querySelectorAll('h2')].map((x) => x.innerText); const prev = h.find((t) => /Who runs this grid/.test(t)), next = h.find((t) => /Right now/.test(t));
    const pos = (el) => el.getBoundingClientRect().top + window.scrollY; const hs = [...document.querySelectorAll('h2')];
    return !!prev && !!next && pos(hs.find((x) => /Who runs this grid/.test(x.innerText))) < pos(p) && pos(p) < pos(hs.find((x) => /Right now/.test(x.innerText))); })()`), "it sits between \"Who runs this grid\" and \"Right now: demand\", where the box was");
  await evaluate(`(() => { window.__asked = []; window.__replies = ${JSON.stringify(replies)}; const real = window.fetch;
    window.fetch = async (u, o) => String(u).includes('/api/ask') ? (window.__asked.push(JSON.parse(o.body)), new Response(JSON.stringify(window.__replies[window.__asked.length - 1]) + "\\n", { status: 200, headers: { 'Content-Type': 'application/x-ndjson' } })) : real(u, o); return true; })()`);
  const askIt = async (text, turn) => {
    await evaluate(`(() => { const q = document.querySelector('#ask-grid'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(q, ${JSON.stringify(text)}); q.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
    await wait(`!document.querySelector('[data-ask-panel] form button[type=submit]').disabled`);
    await evaluate(`document.querySelector('[data-ask-panel] form button[type=submit]').click()`);
    await wait(`!!document.querySelector('[data-turn="${turn}"]')`, 15000, `answer ${turn}`);
  };
  const turn = (k) => evaluate(`(() => { const s = document.querySelector('[data-turn="${k}"]'); const pos = (el) => el.getBoundingClientRect().top + window.scrollY;
    return { form: s.getAttribute('data-form'), answer: s.querySelector('[data-answer]').innerText, series: s.querySelectorAll('[data-series]').length, charts: s.querySelectorAll('[data-series] canvas, [data-series] svg').length,
      tables: s.querySelectorAll('table').length, sources: s.querySelectorAll('[data-sources] li').length, below: pos(s) > pos(document.querySelector('[data-ask-panel] form')), top: pos(s) }; })()`);

  await askIt("What is a hub?", 1);
  const t1 = await turn(1);
  check(t1.form === "words" && t1.answer === WORDS.answer && t1.series === 0 && t1.charts === 0 && t1.tables === 0, `an answer in words shows no chart and no table (${t1.series} series, ${t1.tables} tables)`);
  check(t1.below && t1.sources === 1, "the answer sits right below the box, with its source (the ERCOT page's own text)");

  await askIt("How much battery storage is installed?", 2);
  const t2 = await turn(2);
  check(t2.form === "sentence" && t2.series === 0 && t2.charts === 0 && t2.tables === 0 && t2.answer === chart.answer, "an answer of one figure shows no chart and no table, though its query returned rows");

  await askIt("How has the fleet grown?", 3);
  await wait(`!!document.querySelector('[data-turn="3"] [data-series] canvas, [data-turn="3"] [data-series] svg')`, 20000, "the chart");
  const t3 = await turn(3), t2b = await turn(2), t1b = await turn(1);
  check(t3.form === "chart" && t3.series === chart.series.length && t3.charts >= 1 && t3.tables >= 1, `an answer of form "chart" shows the chart and the rows it was drawn from (${t3.series} series)`);
  check(t3.below && t3.top < t2b.top && t2b.top < t1b.top, "the newest answer comes first, right below the box; the earlier ones follow");
  const rows = await evaluate(`document.querySelectorAll('[data-turn="3"] [data-series] tbody tr').length`);
  const mark = await evaluate(`document.querySelector('[data-turn="3"] [data-chart-check]')?.getAttribute('data-chart-check') ?? ''`);
  check(rows === chart.series[0].rows.length && mark.endsWith(`/${chart.series[0].rows.length}`), `the table holds every row fetched (${rows}) and the chart says how many of them it draws (${mark})`);
  const tip = await evaluate(`(() => { const el = document.querySelector('[data-turn="3"] [data-series] [_echarts_instance_]'); if (!el || !window.echarts) return ''; const c = window.echarts.getInstanceByDom(el);
    c.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: 1 }); return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /\\d/.test(t)).sort((a, b) => b.length - a.length)[0] ?? ''), 500)); })()`);
  check(/\d/.test(String(tip)), `the chart answers the mouse ("${String(tip).replace(/\s+/g, " ").slice(0, 90)}")`);
  const asked = await evaluate(`window.__asked`);
  check(asked.length === 3 && asked.every((a) => a.profile === "ercot" && a.stream === true && a.context?.view === "/grid/ercot") && asked[1].history?.length === 1 && asked[2].history?.length === 2,
    "each question goes to the route as the ERCOT profile, streamed, with the answers before it");
  check(!(await evaluate(`document.querySelector('[data-ask-panel]').innerText`)).includes("Opened from"), "on the page it describes, the panel does not say where it was opened from");
  check(errors.length === 0, `no script error on the page${errors.length ? ": " + errors[0].slice(0, 160) : ""}`);
  return bad ? 1 : 0;
});
if (code === null) { console.log("check-ask-panel: NOT PROVEN on this machine: no Chrome or Edge was found (set BROWSER_PATH)"); process.exit(0); }
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
