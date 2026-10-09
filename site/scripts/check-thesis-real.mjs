// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), a REAL run in a real browser.
//
//   node --import ./scripts/alias-register.mjs scripts/check-thesis-real.mjs <base-url> <run-id>
//
// check-thesis.mjs proves the charts on a stand-in's fixture runs. This reads one real run of the internal table, as
// the owner sees it: how many of its five trends draw a chart, what each chart says under the mouse, that the deal
// funnel's chart answers the mouse, and that no script error is raised. It asks for nothing and stores nothing.
// Session 169: a run since then (report version 2) says "no real series: not drawn" where a trend has no chart, and its
// deal funnel is a connector tab: the placeholder, or the rows of a pasted provider's answer.
// Exit 1 when a chart that is drawn does not answer the mouse, or the page raises an error.
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "").replace(/\/$/, "");
const run = process.argv[3] ?? "";
if (!base || !run) { console.log("usage: check-thesis-real.mjs <base-url> <run-id>"); process.exit(2); }
let bad = 0;
const check = (ok, what) => { if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

const code = await withBrowser(async ({ go, evaluate, wait, unlock, errors, sleep }) => {
  await unlock(base);
  await go(`${base}/thesis?run=${encodeURIComponent(run)}&tab=trends`);
  await sleep(4000);
  const n = await evaluate(`document.querySelectorAll('[data-chart="trend"] canvas').length`);
  const none = await evaluate(`[...document.querySelectorAll('main *')].filter((e) => e.children.length === 0 && e.textContent.trim() === 'no chart').length + document.querySelectorAll('[data-missing="no_series"]').length`);
  console.log(`trends tab: ${n} charts drawn, ${none} trends read "no chart"`);
  check(n + none >= 1, "at least one trend shows a chart or says why it has none");
  for (let k = 0; k < n; k++) {
    const tip = await evaluate(`(() => { const el = document.querySelectorAll('[data-chart="trend"]')[${k}]; const chart = window.echarts.getInstanceByDom(el);
      chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: 0 });
      return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /\\d/.test(t)).sort((x, y) => y.length - x.length)[0] ?? ''), 500)); })()`);
    const t = String(tip).replace(/\s+/g, " ").trim();
    check(/\d/.test(t) && t.length > 4, `chart ${k + 1} answers the mouse: "${t.slice(0, 110)}"`);
  }
  await go(`${base}/thesis?run=${encodeURIComponent(run)}&tab=funnel`);
  await sleep(3000);
  const f = await evaluate(`(() => { if (document.querySelector('[data-connector="funnel"], [data-connector-row="funnel"]')) return 'a connector tab: ' + (document.querySelectorAll('[data-connector-row="funnel"]').length || 0) + ' rows';
      const el = document.querySelector('[data-chart="funnel"]'); if (!el || !window.echarts) return 'no funnel chart'; const chart = window.echarts.getInstanceByDom(el);
      chart.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: 0 });
      return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /\\d/.test(t)).sort((x, y) => y.length - x.length)[0] ?? ''), 500)); })()`);
  check(/\d/.test(String(f)), `the deal funnel answers the mouse, or is a connector tab: "${String(f).replace(/\s+/g, " ").slice(0, 110)}"`);
  const errs = errors;
  check(errs.length === 0, `no script error on the page${errs.length ? ": " + errs.slice(0, 2).join(" | ").slice(0, 200) : ""}`);
});
process.exit(bad || code ? 1 : 0);
