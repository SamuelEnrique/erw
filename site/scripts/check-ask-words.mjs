// Energy Research Warehouse (ERW) site, session 143: the answer's words before its chart, in a real browser, WITHOUT a
// model call: the route's replies are made here, as lines sent one after another with a pause between them.
//
//   npm run build && npx next start -p 3143
//   node --import ./scripts/alias-register.mjs scripts/check-ask-words.mjs [base-url]      (default http://localhost:3143)
//
// The whole answer is tests/fixtures/session92/site_answer.json (a real answer of Ask ERCOT saved in session 92), sent
// as form "chart". Checked: while the answer is on its way the page shows its words, and no source, chart or follow-up
// question yet; when the whole answer arrives it takes the place of the words (one answer, with its chart, its rows and
// its sources); words that are taken back disappear, and the answer that follows is the one shown; nothing of how long
// a stage took is on the page. Exit 1 on a failure.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3143").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const chart = JSON.parse(fs.readFileSync(new URL("../../tests/fixtures/session92/site_answer.json", import.meta.url), "utf-8"));
const whole = { type: "result", ...chart, form: "chart", stages_ms: { planning: 2700, fetching: 160, drawing: 1, writing: 3600, other: 150, total: 6611 }, seconds_words: 5.5, steps: [] };
const words = { type: "words", answer: chart.answer, form: "chart", not_in_warehouse: false, premise: "" };
// each script: the lines of one reply and the milliseconds to wait before each
const scripts = [
  [[0, { type: "started" }], [50, { type: "reading", tool: "query", table: "storage_buildout_monthly" }], [300, words], [2500, whole]],
  [[0, { type: "started" }], [200, { ...words, answer: "These words will be taken back." }], [1200, { type: "withdrawn" }], [1500, whole]],
];

const code = await withBrowser(async ({ go, evaluate, wait, unlock, errors, sleep }) => {
  await unlock(base);
  await go(`${base}/grid/ercot`);
  await wait(`!!document.querySelector('[data-ask-panel="ercot"] #ask-grid')`, 30000, "the panel on /grid/ercot");
  await evaluate(`(() => { window.__n = 0; window.__scripts = ${JSON.stringify(scripts)}; const real = window.fetch; const enc = new TextEncoder();
    window.fetch = async (u, o) => { if (!String(u).includes('/api/ask')) return real(u, o); const lines = window.__scripts[window.__n++];
      const body = new ReadableStream({ async start(c) { for (const [ms, line] of lines) { await new Promise((r) => setTimeout(r, ms)); c.enqueue(enc.encode(JSON.stringify(line) + "\\n")); } c.close(); } });
      return new Response(body, { status: 200, headers: { 'Content-Type': 'application/x-ndjson' } }); }; return true; })()`);
  const askIt = async (text) => {
    await evaluate(`(() => { const q = document.querySelector('#ask-grid'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(q, ${JSON.stringify(text)}); q.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
    await wait(`!document.querySelector('[data-ask-panel] form button[type=submit]').disabled`);
    await evaluate(`document.querySelector('[data-ask-panel] form button[type=submit]').click()`);
  };
  const early = () => evaluate(`(() => { const e = document.querySelector('[data-early="1"]'); if (!e) return null; const pos = (el) => el.getBoundingClientRect().top + window.scrollY;
    return { answer: e.querySelector('[data-answer]')?.innerText ?? '', series: e.querySelectorAll('[data-series]').length, sources: e.querySelectorAll('[data-sources] li').length, followups: e.querySelectorAll('[data-followups] button').length,
      below: pos(e) > pos(document.querySelector('[data-ask-panel] form')), busy: document.querySelector('[data-ask-panel] form button[type=submit]').innerText }; })()`);

  await askIt("How has the fleet grown?");
  await wait(`!!document.querySelector('[data-early="1"] [data-answer]')`, 10000, "the words before the whole answer");
  const e1 = await early();
  check(e1.answer === chart.answer && e1.below, "the answer's words are shown right below the box while the rest is on its way");
  check(e1.series === 0 && e1.sources === 0 && e1.followups === 0 && e1.busy === "Answering", `with them: no chart, no source and no question to ask next yet (${e1.series}, ${e1.sources}, ${e1.followups})`);
  check((await evaluate(`document.querySelectorAll('[data-turn]').length`)) === 1, "one answer on the page, not two");
  await wait(`!document.querySelector('[data-early="1"]') && !!document.querySelector('[data-turn="1"] [data-series] canvas, [data-turn="1"] [data-series] svg')`, 20000, "the whole answer with its chart");
  const t1 = await evaluate(`(() => { const s = document.querySelector('[data-turn="1"]'); return { n: document.querySelectorAll('[data-turn]').length, answer: s.querySelector('[data-answer]').innerText, series: s.querySelectorAll('[data-series]').length,
    rows: s.querySelectorAll('[data-series] tbody tr').length, sources: s.querySelectorAll('[data-sources] li').length, followups: s.querySelectorAll('[data-followups] button').length }; })()`);
  check(t1.n === 1 && t1.answer === chart.answer && t1.series === chart.series.length && t1.rows === chart.series[0].rows.length && t1.sources === chart.citations.length && t1.followups === chart.followups.length,
    `the whole answer takes the place of the words: the same words, now with the chart, its ${t1.rows} rows, ${t1.sources} source and ${t1.followups} questions to ask next`);

  await askIt("And the year before?");
  await wait(`!!document.querySelector('[data-early="1"] [data-answer]')`, 10000, "words that will be taken back");
  check((await early()).answer === "These words will be taken back.", "a second question shows its words too");
  await wait(`!document.querySelector('[data-early="1"]')`, 10000, "the words taken back");
  const gone = await evaluate(`({ text: document.querySelector('[data-ask-panel]').innerText.includes('These words will be taken back.'), turns: document.querySelectorAll('[data-turn]').length, busy: document.querySelector('[data-ask-panel] form button[type=submit]').innerText })`);
  check(!gone.text && gone.turns === 1 && gone.busy === "Answering", "words that are taken back disappear, and the page goes on waiting for the answer");
  await wait(`document.querySelectorAll('[data-turn]').length === 2`, 15000, "the answer after the words were taken back");
  await sleep(300);
  const after = await evaluate(`({ text: document.querySelector('[data-ask-panel]').innerText, answer: document.querySelector('[data-turn="2"] [data-answer]').innerText, early: !!document.querySelector('[data-early="1"]') })`);
  check(after.answer === chart.answer && !after.text.includes("These words will be taken back.") && !after.early, "the answer that follows is the one shown, and the words taken back are nowhere");
  check(!/planning|fetching|stages_ms|6611|5\.5 s/i.test(after.text), "nothing of how long a stage took is on the page");
  check(errors.length === 0, `no script error on the page${errors.length ? ": " + errors[0].slice(0, 160) : ""}`);
  return bad ? 1 : 0;
});
if (code === null) { console.log("check-ask-words: NOT PROVEN on this machine: no Chrome or Edge was found (set BROWSER_PATH)"); process.exit(0); }
console.log(`${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
