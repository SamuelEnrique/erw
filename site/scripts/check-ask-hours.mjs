// Energy Research Warehouse (ERW) site, session 161: the average day by hour as one line on /ask/ercot, in a real
// browser, WITHOUT a model call: the route's replies are made here from recorded rows.
//
//   npm run build && npx next start -p 3161
//   node --import ./scripts/alias-register.mjs scripts/check-ask-hours.mjs [base-url]      (default http://localhost:3161)
//
// The first reply is the 24 rows the query tool returned for ERCOT's batteries by hour of the day on 8 October 2026
// (tests/fixtures/session156/form_reads.json, the call h13_family_newest), made into a series by the panel's own
// code (lib/chat/ercot.ts, finish). The second is tests/fixtures/session92/site_answer.json, a series over time.
// Checked: the 24 hours are one line on an axis of hours, 00:00 to 23:00, each point the row fetched; the line answers
// the mouse with the hour and the value; the 24 rows are still on the page, folded under the line; and a series over
// time is drawn on a time axis with its range slider, as before. Exit 1 on a failure.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3161").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf-8"));
const FIX = read("../../tests/fixtures/session156/form_reads.json");
const overTime = read("../../tests/fixtures/session92/site_answer.json");

// the recorded reads stand in for the database while the series is made; the browser's requests are the page's own
const real = globalThis.fetch, env = { url: process.env.SUPABASE_URL, key: process.env.SUPABASE_ANON_KEY };
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
globalThis.fetch = async (url) => {
  const body = FIX.reads[String(url)];
  if (body === undefined) throw new Error(`a read that was not recorded: ${decodeURIComponent(String(url)).slice(0, 300)}`);
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
const { runTool } = await import("../lib/chat/tools.ts");
const { ercotProfile } = await import("../lib/chat/ercot.ts");
const profile = ercotProfile();
const call = FIX.calls.find((c) => c.id === "h13_family_newest");
const r = await runTool("query", call.input, profile.scope);
const records = [{ tool: "query", input: call.input, out: profile.tag("query", call.input, r.out, 1), isError: false }];
const draft = { answer: "ERCOT's batteries by the hour of the day, from the rows recorded on 8 October 2026 (shoulder_hours_monthly).", citations: [{ table: r.out.table, source_report: "", data_version: "", tier: "" }],
  not_in_warehouse: false, form: "chart", series: ["r1"], followups: [], premise: "" };
const done = profile.finish("answered", draft, records);
globalThis.fetch = real;
if (env.url === undefined) delete process.env.SUPABASE_URL; else process.env.SUPABASE_URL = env.url;
if (env.key === undefined) delete process.env.SUPABASE_ANON_KEY; else process.env.SUPABASE_ANON_KEY = env.key;
const rows = done.series[0].rows;
check(done.series.length === 1 && rows.length === 24 && done.series[0].kind === "line" && done.series[0].check.points === 24, `the recorded call gives one series of 24 rows, a line (${done.series[0].check.points} points)`);
const HOURS = { type: "result", status: "answered", form: "chart", answer: draft.answer, model: "recorded", tool_calls: 1, retried: false, cost_usd: null, calls: [], nearest: [], premise: "", followups: [],
  citations: [{ table: r.out.table, source_report: "recorded", data_version: "recorded", tier: "derived" }], series: done.series };
const replies = [HOURS, { type: "result", ...overTime, form: "chart" }];

const code = await withBrowser(async ({ go, evaluate, wait, unlock, errors }) => {
  await unlock(base);
  await go(`${base}/ask/ercot`);
  await wait(`!!document.querySelector('[data-ask-panel="ercot"] input')`, 30000, "the panel on /ask/ercot");
  await evaluate(`(() => { window.__asked = []; window.__replies = ${JSON.stringify(replies)}; const real = window.fetch;
    window.fetch = async (u, o) => String(u).includes('/api/ask') ? (window.__asked.push(JSON.parse(o.body)), new Response(JSON.stringify(window.__replies[window.__asked.length - 1]) + "\\n", { status: 200, headers: { 'Content-Type': 'application/x-ndjson' } })) : real(u, o); return true; })()`);
  const askIt = async (text, turn) => {
    await evaluate(`(() => { const q = document.querySelector('[data-ask-panel] input'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(q, ${JSON.stringify(text)}); q.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
    await wait(`!document.querySelector('[data-ask-panel] form button[type=submit]').disabled`);
    await evaluate(`document.querySelector('[data-ask-panel] form button[type=submit]').click()`);
    await wait(`!!document.querySelector('[data-turn="${turn}"] [data-series] [_echarts_instance_] canvas')`, 25000, `the chart of answer ${turn}`);
  };
  const chartOf = (turn) => evaluate(`(() => { const s = document.querySelector('[data-turn="${turn}"] [data-series]'); const el = s.querySelector('[_echarts_instance_]'); const o = window.echarts.getInstanceByDom(el).getOption();
    return { x: { type: o.xAxis[0].type, min: o.xAxis[0].min ?? null, max: o.xAxis[0].max ?? null }, zoom: (o.dataZoom ?? []).map((z) => z.type), lines: o.series.length, kind: o.series[0].type, points: o.series[0].data,
      mark: s.querySelector('[data-chart-check]').getAttribute('data-chart-check'), said: s.querySelector('[data-chart-check]').innerText, open: s.querySelector('details').open, tableRows: s.querySelectorAll('tbody tr').length,
      shown: s.getAttribute('data-form') }; })()`);
  const tipOf = (turn, i) => evaluate(`(() => { const el = document.querySelector('[data-turn="${turn}"] [data-series] [_echarts_instance_]'); const c = window.echarts.getInstanceByDom(el);
    c.dispatchAction({ type: 'showTip', seriesIndex: 0, dataIndex: ${i} }); return new Promise((ok) => setTimeout(() => ok([...el.querySelectorAll('div')].map((d) => d.innerText || '').filter((t) => /\\d/.test(t)).sort((a, b) => b.length - a.length)[0] ?? ''), 500)); })()`);

  await askIt("Show how ERCOT's batteries charge and discharge across the hours of a day.", 1);
  const h = await chartOf(1);
  check(h.shown === "chart" && h.lines === 1 && h.kind === "line", `the 24 hours are drawn as one line (${h.lines} line, shown as ${h.shown})`);
  check(h.x.type === "value" && h.x.min === 0 && h.x.max === 23 && h.zoom.length === 0, `on an axis of the hours of a day, 0 to 23, with no range slider (${JSON.stringify(h.x)})`);
  check(JSON.stringify(h.points) === JSON.stringify(rows.map((x, i) => [i, x.value])), "each point is the row fetched: hour by hour, the value as the tool returned it");
  check(h.mark === "24/24" && /24 rows, one for each local hour of the day/.test(h.said), `the chart says it draws every row (${h.mark}: "${h.said}")`);
  check(h.tableRows === 24 && h.open === false, `the 24 rows are still on the page, folded under the line (${h.tableRows} rows, open ${h.open})`);
  const tip = String(await tipOf(1, 7)).replace(/\s+/g, " ");
  check(tip.startsWith("07:00") && /\d/.test(tip.slice(5)), `the line answers the mouse with the hour and the value ("${tip.slice(0, 90)}")`);

  await askIt("How has the fleet grown?", 2);
  const t = await chartOf(2);
  check(t.x.type === "time" && t.x.min === null && t.zoom.join(",") === "inside,slider", `a series over time is on a time axis with its range slider, as before (${t.x.type}; ${t.zoom.join(", ")})`);
  check(t.points.length === overTime.series[0].rows.filter((x) => x.value !== null).length && t.points.every((p) => p[0] > 1e11), `its points are times (${t.points.length})`);
  check(errors.length === 0, `no script error on the page${errors.length ? ": " + errors[0].slice(0, 160) : ""}`);
  return bad ? 1 : 0;
});
if (code === null) { console.log("no browser on this machine: not proven here"); process.exit(0); }
console.log(bad ? `${bad} of ${n} checks FAILED` : `${n} checks pass`);
process.exit(bad ? 1 : 0);
