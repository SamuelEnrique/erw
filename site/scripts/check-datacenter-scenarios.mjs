// Energy Research Warehouse (ERW) site, session 194: the scenarios of /cost-of-power ("What a datacenter pays") in the
// internal view, in a headless browser, at desktop width (1280) and phone width (390). The twin of
// scripts/check-seller-scenarios.mjs and scripts/check-battery-scenarios.mjs, on the shared browser (browser.mjs).
//
//   npm run build && npx next start -p 3194
//   node scripts/check-datacenter-scenarios.mjs [base-url] [output-dir]
//   TEXT_ONLY=name node scripts/check-datacenter-scenarios.mjs [base-url] [output-dir]
//       writes only <output-dir>/<name>.txt, the visible text of the page at its bare address (for the comparison of the
//       page before and after a change), and exits
//
// The page is in review: this unlocks the internal view first (INTERNAL_COSTS_TOKEN from the environment,
// site/.env.local or the root .env; the token is never printed). It asserts:
//   1. the panel: eight assumptions in order, each with its default, its source and a Reset; one Reset for all; "Copy A
//      to B"; at the bare address nothing is written into the address;
//   2. the table: two columns, eight rows in order, then the row in words and B against A; at the defaults the price,
//      the year's cost, the GPU-hour and the bad month are the page's own numbers elsewhere on it, and every figure is
//      lib/datacenter/finance.ts's on the page's own files (scripts/datacenter-ways.mjs);
//   3. a change computes in the browser: no request at all, the address gains the parameter, the header of each column
//      shows only what differs, the row says it in words and B is set against A in numbers;
//   4. the address round trip: opening the address again gives the same inputs and the same numbers;
//   5. "Copy A to B", a Reset and the Reset for all;
//   6. the sensitivity chart: eight bars sorted by size, a legend, and a hover that states the two values and the step;
//   7. no word of recommendation in the block;
//   8. the page's own parameters still work: a flexible load is the default of both scenarios and its figures are that
//      page's; Show and the choice of a grid carry the scenarios;
//   9. the contract panel's promise, with the scenarios beside it: typing the terms sends no request, leaves the address
//      unchanged and stores nothing; a scenario change after it puts no contract term in the address;
//  10. the other grids, a region with no twelve months (nothing is filled) and a region whose flexible way is not held;
//  11. at 390 px the page does not scroll sideways.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { env, withBrowser } from "./browser.mjs";
import * as L from "../lib/datacenter.ts";
import * as F from "../lib/datacenter/finance.ts";
import * as W from "./datacenter-ways.mjs";

const base = (process.argv[2] ?? "http://localhost:3194").replace(/\/$/, "");
const outDir = process.argv[3];
let failed = 0, count = 0;
function check(ok, what, detail = "") {
  count++;
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}
const near = (a, b, tol = 1e-9) => Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));
const num = (s) => (s === null || s === undefined ? null : Number(String(s).replace(/,/g, "")));
const SOURCE = /^Default [\w.,-]+\. .{12,}\.$/;

const STATE = `(() => {
  const root = document.querySelector("[data-scenarios]");
  const t = (sel) => document.querySelector(sel)?.textContent ?? null;
  const main = document.querySelector("main") ?? document.body;
  if (!root) return { none: true, text: main.innerText, search: location.search, bad: /undefined|NaN/.test(main.innerText) };
  const head = (p) => { const h = root.querySelector('[data-head="' + p + '"]'); return [...h.querySelectorAll("[data-differs]")].map((e) => e.textContent); };
  return {
    view: root.querySelector("[data-assumptions]").getAttribute("data-assumptions"),
    fields: [...root.querySelectorAll("[data-field]")].map((f) => ({
      key: f.getAttribute("data-field"), value: f.querySelector("[data-assumption]").value, reset: !!f.querySelector("button[data-reset]"), resetOff: f.querySelector("button[data-reset]")?.disabled ?? null,
      def: f.querySelector("[data-default]")?.getAttribute("data-default") ?? null, source: f.querySelector("[data-default]")?.textContent ?? "",
      options: [...f.querySelectorAll("option")].map((o) => ({ value: o.value, text: o.textContent, off: o.disabled })) })),
    resetAll: root.querySelector("[data-reset-all]")?.textContent ?? null, copy: root.querySelector("[data-copy]")?.textContent ?? null,
    rows: [...root.querySelectorAll("[data-scenario-table] tbody tr")].map((r) => r.getAttribute("data-row")),
    labels: Object.fromEntries([...root.querySelectorAll("[data-scenario-table] tbody tr")].map((r) => [r.getAttribute("data-row"), r.querySelector("th").textContent])),
    cells: Object.fromEntries([...root.querySelectorAll("[data-cell]")].map((c) => [c.getAttribute("data-cell"), { raw: c.getAttribute("data-raw") === "" ? null : Number(c.getAttribute("data-raw")), text: c.textContent, missing: c.querySelector("[data-missing]")?.getAttribute("title") ?? null }])),
    headA: head("a"), headB: head("b"), headFor: root.querySelector("[data-scenario-table] thead th").textContent, words: root.querySelector("[data-differs-words]").textContent,
    against: root.querySelector("[data-against-words]").textContent, rate: root.querySelector("[data-against-words]").getAttribute("data-rate"), even: root.querySelector("[data-against-words]").getAttribute("data-even"),
    sentence: root.querySelector("[data-pv-sentence]")?.textContent ?? null,
    // session 213: the chart is the page's third section, outside the block
    bars: [...document.querySelectorAll("[data-bar]")].map((b) => ({ key: b.getAttribute("data-bar"), size: Number(b.getAttribute("data-size")), title: b.getAttribute("title") })),
    chartView: document.querySelector("[data-sensitivity]")?.getAttribute("data-sensitivity") ?? null,
    legend: document.querySelector("[data-sensitivity] figcaption")?.textContent ?? "", readout: document.querySelector("[data-sensitivity-readout]")?.textContent ?? "",
    howToRead: document.querySelector("[data-how-to-read]")?.textContent ?? "",
    text: root.innerText, search: location.search, href: location.href,
    per: t('[data-stat="l12_per"]'), cost: t('[data-stat="l12_cost"]'), gpu: t('[data-stat="gpu_hour"]'), saved: t('[data-stat="l12_saved"]'),
    heads: [...document.querySelectorAll("h2")].map((h) => h.textContent),
    summary: document.querySelector("[data-summary]")?.textContent ?? "", page: main.innerText, bad: /undefined|NaN/.test(main.innerText),
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
  };
})()`;

const code = await withBrowser(async ({ go, evaluate, unlock, send, requests, sleep }) => {
  const size = (width) => send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
  /** Session 213: the page's two CSV downloads, fetched by the browser (so with the internal view's cookie) for the
   * address in view, parsed: the tables the long-form file holds, and the newest twelve complete months' flat price. */
  const parseCsv = (txt) => {
    const rows = [];
    let row = [], cellText = "", quoted = false;
    for (let i = 0; i < txt.length; i++) {
      const ch = txt[i];
      if (quoted) {
        if (ch === '"' && txt[i + 1] === '"') { cellText += '"'; i++; } else if (ch === '"') quoted = false; else cellText += ch;
      } else if (ch === '"') quoted = true;
      else if (ch === ",") { row.push(cellText); cellText = ""; }
      else if (ch === "\n") { row.push(cellText); rows.push(row); row = []; cellText = ""; }
      else if (ch !== "\r") cellText += ch;
    }
    if (cellText !== "" || row.length) { row.push(cellText); rows.push(row); }
    return rows.filter((r) => r.length && !r[0].startsWith("#"));
  };
  const fetchText = (route) => evaluate(`fetch(${JSON.stringify(route)}).then(async (r) => r.status + "\\n" + await r.text())`);
  const downloads = async (search) => {
    const [ms, ts] = await Promise.all([fetchText(`/cost-of-power/months.csv${search}`), fetchText(`/cost-of-power/tables.csv${search}`)]);
    const status = (t) => Number(t.split("\n")[0]);
    const body = (t) => t.slice(t.indexOf("\n") + 1);
    const mRows = parseCsv(body(ms)), tRows = parseCsv(body(ts));
    const mh = mRows[0] ?? [];
    const col = (name) => mh.indexOf(name);
    const months = mRows.slice(1).filter((r) => r[col("kind")] === "month" && r[col("complete")] === "yes");
    // a flat 100 MW load: the newest twelve complete months' cost over their hours (the file rounds each month to a dollar)
    const twelve = months.slice(0, 12);
    const flatPrice = twelve.length === 12 ? twelve.reduce((a, r) => a + Number(r[col("usd")]), 0) / (100 * twelve.reduce((a, r) => a + Number(r[col("held")].split(" ")[0]), 0)) : null;
    return { status: [status(ms), status(ts)], months: mRows.length - 1, tables: tRows.length - 1, yearRows: mRows.slice(1).filter((r) => r[col("kind")] === "year").length,
      tablesOf: [...new Set(tRows.slice(1).map((r) => r[0]))], flatPrice, heads: `${body(ms).split("\n")[0]} | ${body(ts).split("\n")[0]}` };
  };
  const open = async (route, width = 1280) => { await size(width); await go(route.startsWith("http") ? route : base + route); await sleep(1500); return evaluate(STATE); };
  const shot = async (name, width) => {
    if (!outDir) return;
    fs.mkdirSync(outDir, { recursive: true });
    const { cssContentSize } = await send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 14000);
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(500);
    const s = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(outDir, `${name}.png`), Buffer.from(s.data, "base64"));
    await size(width);
  };
  /** Type a value into an assumption's field as a reader would: focus, select all, type. */
  const type = async (k, text) => {
    await evaluate(`(() => { const e = document.querySelector('input[data-assumption="${k}"]'); e.scrollIntoView({ block: "center" }); e.focus(); e.select(); })()`);
    await send("Input.insertText", { text });
    await sleep(350);
    await evaluate(`document.activeElement && document.activeElement.blur()`);
    await sleep(150);
  };
  /** Choose how the load runs, as a reader would: the list's value, then its change event. */
  const choose = async (v) => {
    await evaluate(`(() => { const e = document.querySelector('select[data-assumption="run"]'); const set = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set; set.call(e, "${v}"); e.dispatchEvent(new Event("change", { bubbles: true })); })()`);
    await sleep(350);
  };
  const click = async (sel) => { await evaluate(`document.querySelector(${JSON.stringify(sel)}).click()`); await sleep(350); };
  // every change in the block is held to no request at all: the page's contract box says nothing typed there is sent,
  // so no usage count follows an input on this page (components/Usage.tsx), and the block sends none of its own
  const noRequest = async (what, act) => {
    const mark = requests.length;
    await act();
    await sleep(700);
    const sent = requests.slice(mark).filter((r) => !r.url.startsWith("data:"));
    check(sent.length === 0, `${what}: no request is sent`, sent.slice(0, 3).map((r) => r.url).join(" "));
  };

  await unlock(base);
  if (process.env.TEXT_ONLY) {
    await size(1280);
    await go(`${base}/cost-of-power`);
    await sleep(1500);
    const text = await evaluate(`document.querySelector("main")?.innerText ?? document.body.innerText`);
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, `${process.env.TEXT_ONLY}.txt`), text.replace(/\r\n/g, "\n"));
    console.log(`${process.env.TEXT_ONLY}.txt: ${text.split("\n").length} lines of ${base}/cost-of-power`);
    return 0;
  }

  // 1 and 2: the bare address (ERCOT, LZ_NORTH, a flat 100 MW, real time)
  const P = W.pageOf({});
  const d = F.defaultsOf(P.load), [flat, flex] = P.ways;
  let s = await open("/cost-of-power");
  check(!s.none && !s.bad, "the bare address: the block is on the page");
  check(s.search === "", "the bare address stays bare: nothing is written into it", s.search);
  check(JSON.stringify(s.fields.map((f) => f.key)) === JSON.stringify(F.KEYS), "ten assumptions, in the page's order (session 213: the contract's share and price last)", s.fields.map((f) => f.key).join(", "));
  check(s.fields.every((f) => Number(f.value) === d[f.key] && Number(f.def) === d[f.key]), "each field holds its default", s.fields.map((f) => `${f.key} ${f.value}`).join(", "));
  check(s.fields.every((f) => f.reset && f.resetOff === true), "each has a Reset, idle at the default");
  check(s.fields.every((f) => SOURCE.test(f.source)), "each states its default and where the default comes from", s.fields.find((f) => !SOURCE.test(f.source))?.source ?? "");
  check(/NVIDIA DGX H100/.test(s.fields[1].source) && /Uptime Institute, Global Data Center Survey 2024/.test(s.fields[2].source), "the power per GPU and the overhead ratio cite the page's two sources");
  check(s.fields.filter((f) => /No cited/.test(f.source)).map((f) => f.key).join() === "growth,upfront,life", "the three defaults with no source say so", s.fields.filter((f) => /No cited/.test(f.source)).map((f) => f.key).join());
  check(/Lazard, Levelized Cost of Energy\+, June 2025: "60% debt at an 8% interest rate and 40% equity at a 12% cost"\. The default is that weighted cost, 0\.6 x 8 \+ 0\.4 x 12 = 9\.6 percent/.test(s.fields[7].source) && Number(s.fields[7].value) === 9.6, "the hurdle rate is Lazard's weighted cost, with the sentence it comes from (session 196)", s.fields[7].source);
  check(s.fields[0].options.length === 2 && /^Flat: the same in every hour$/.test(s.fields[0].options[0].text) && /^Flexible: off in the 100 most expensive hours of each year$/.test(s.fields[0].options[1].text) && s.fields[0].options.every((o) => !o.off),
    "how the load runs offers the two ways the page computed", s.fields[0].options.map((o) => o.text).join(" | "));
  check(s.resetAll === "Reset all of A" && s.copy === "Copy A to B", "one Reset for all, and Copy A to B", `${s.resetAll}; ${s.copy}`);
  check(JSON.stringify(s.rows) === JSON.stringify(["price", "bill", "gpu", "bad", "off", "pv", "level", "allin", "differs", "against"]), "eight rows in order, then the row in words and B against A", s.rows.join(", "));
  check(s.headA.length === 0 && s.headB.length === 0 && s.words === "A and B hold the same assumptions." && s.against === "No difference.", "equal scenarios: nothing in the headers", `${s.words} ${s.against}`);
  check(s.cells["a|price"].raw.toFixed(2) === num(s.per).toFixed(2) && s.cells["b|price"].raw === s.cells["a|price"].raw, "the price is the page's last twelve months per MWh", `${s.cells["a|price"].text} against the headline ${s.per}`);
  check(s.cells["a|bill"].text.startsWith(`USD ${s.cost}`) && s.cells["a|gpu"].raw.toFixed(4) === s.gpu, "the year's cost and the GPU-hour are the page's own", `${s.cells["a|bill"].text} | ${s.cells["a|gpu"].text} against ${s.cost} and ${s.gpu}`);
  check(s.page.includes(`USD ${L.two(s.cells["a|bad"].raw)}`) && s.cells["a|bad"].text.includes(L.monthName(P.bad.m)), "the bad month is the page's own headline", s.cells["a|bad"].text);
  const r0 = F.resultOf(d, flat);
  check(s.cells["a|price"].raw === r0.price && near(s.cells["a|bill"].raw, r0.bill) && near(s.cells["a|gpu"].raw, r0.gpuHour) && s.cells["a|bad"].raw === flat.bad.per, "the same four are the library's on the page's own files", `USD ${L.two(r0.price)}`);
  check(near(s.cells["a|pv"].raw, r0.pv) && near(s.cells["a|level"].raw, r0.level) && near(s.cells["a|allin"].raw, r0.allIn) && s.cells["a|off"].raw === null && /^none/.test(s.cells["a|off"].text),
    "the present value, the fixed price and the all-in figure are the library's; a flat load has no hours off", `${s.cells["a|pv"].text} | ${s.cells["a|level"].text} | ${s.cells["a|allin"].text}`);
  check(near(s.cells["a|level"].raw, s.cells["a|price"].raw, 1e-12) && near(s.cells["a|allin"].raw, s.cells["a|gpu"].raw, 1e-12), "at the defaults the fixed price is the price and the all-in figure is the GPU-hour");
  check(/^Scenario A, 100 MW at LZ_NORTH in ERCOT, real time: at a hurdle rate of 9.6 percent, 20 years of power cost USD [\d,.]+( million| billion)? today, USD 0\.\d{4} per GPU-hour\.$/.test(s.sentence ?? ""), "the sentence states the numbers", s.sentence ?? "");
  check(JSON.stringify(s.heads) === JSON.stringify(["Your load", "What will it pay?", "Will the power be there?", "How clean?", "How soon?", "Which option is better?", "What matters most"]), "the page asks its four questions, then the two of the decisions, after the panel (session 228)", s.heads.join(" | "));
  check(/^Each row moves one assumption of scenario A down and up by the step named, holds the other nine/.test(s.howToRead), "one line says how to read the chart", s.howToRead);
  const dl = await downloads("");
  check(dl.status[0] === 200 && dl.status[1] === 200 && dl.months > 24 && dl.tables > 40 && /^# Energy Research Warehouse/.test(dl.heads), "the two CSV downloads answer the internal view with their provenance lines", `${dl.status}; ${dl.months} rows, ${dl.tables} cells`);
  check(dl.tablesOf.every((t) => ["scarce_hours", "carbon", "large_load", "power_there", "how_clean", "how_soon", "waits", "waits_stated", "rules", "regions", "matrix", "ny_load"].includes(t)) && ["scarce_hours", "carbon", "large_load", "power_there", "how_clean", "how_soon", "waits", "rules", "regions", "matrix"].every((t) => dl.tablesOf.includes(t)), "the download holds the three answers (session 228), the grid's three questions, the waits, the rules, every region and the matrix", dl.tablesOf.join(", "));
  check(near(dl.flatPrice, flat.per, 1e-4) && dl.yearRows > 0, "the months download's newest twelve complete months give the page's flat price (to the dollar a month)", `${dl.flatPrice} against ${flat.per}`);
  await shot("datacenter-scenarios-default-desktop", 1280);

  // 3: a change computes in the browser
  await noRequest("typing an overhead ratio into A", () => type("pue", "1.2"));
  s = await evaluate(STATE);
  const a1 = { ...d, pue: 1.2 };
  check(s.search === "?ap=1.2", "the address gains the one parameter", s.search);
  check(near(s.cells["a|gpu"].raw, F.gpuHour(a1, flat)) && near(s.cells["a|allin"].raw, F.levelGpuHour(a1, flat)) && near(s.cells["b|gpu"].raw, r0.gpuHour) && near(s.cells["a|bill"].raw, r0.bill), "A is recomputed and B is not moved; the overhead ratio moves the GPU-hour and not the year's cost", `${s.cells["a|gpu"].text} against ${s.cells["b|gpu"].text}`);
  check(JSON.stringify(s.headA) === JSON.stringify(["overhead ratio 1.2"]) && JSON.stringify(s.headB) === JSON.stringify(["overhead ratio 1.56"]), "each header shows only what differs", `${s.headA} | ${s.headB}`);
  check(s.words === "B: overhead ratio 1.56 against 1.2.", "the row says it in words", s.words);
  check(s.fields.find((f) => f.key === "pue").resetOff === false && s.fields.filter((f) => f.resetOff === false).length === 1, "only the changed field's Reset is live");
  await noRequest("putting B in view", () => click('[data-view="b"]'));
  await noRequest("choosing how B runs", () => choose("1"));
  await noRequest("typing an upfront cost into B", () => type("upfront", "50"));
  await noRequest("typing a hurdle rate into B", () => type("hurdle", "10"));
  s = await evaluate(STATE);
  const b1 = { ...d, run: 1, upfront: 50, hurdle: 10 };
  check(s.search === "?ap=1.2&bw=1&bu=50&bh=10&v=b", "the address keeps both scenarios and the one in view", s.search);
  const rb = F.resultOf(b1, flex);
  check(s.cells["b|price"].raw === flex.per && near(s.cells["b|bill"].raw, rb.bill) && near(s.cells["b|pv"].raw, rb.pv) && near(s.cells["b|allin"].raw, rb.allIn) && near(s.cells["b|off"].raw, rb.off.perGpuHour) && s.cells["b|bad"].raw === flex.bad.per,
    "B's price, year's cost, bad month, hours off, present value and all-in figure follow the flexible way", `${s.cells["b|price"].text} | ${s.cells["b|off"].text} | ${s.cells["b|pv"].text}`);
  check(new RegExp(`off in ${L.whole(flex.down)} hours; USD ${L.two(rb.off.perMwh).replace(".", "\\.")} per MWh not bought`).test(s.cells["b|off"].text), "the hours off and what the power not bought would have cost are stated", s.cells["b|off"].text);
  check(s.headA.length === 4 && s.headB.length === 4 && s.words === "B: runs flexible against flat; overhead ratio 1.56 against 1.2; upfront cost USD 50 per kW against 0; hurdle rate 10 percent against 9.6.", "four differences, in the headers and in words", s.words);
  const g1 = F.against(a1, flat, b1, flex);
  check(near(Number(s.rate), g1.rate) && near(Number(s.even), g1.evenUpfront) && s.against.includes(`which returns ${g1.rate.toFixed(1)} percent a year in lower yearly cost; B's hurdle rate is 10 percent.`) && /each over its own years and at its own hurdle rate/.test(s.against) && /B runs [\d,]+ fewer GPU-hours a year/.test(s.against),
    "B against A: the year's cost, the GPU-hours, the present value, the upfront cost at which they are equal, and the rate the extra upfront cost returns beside B's hurdle rate", s.against);
  check(s.chartView === "b" && /scenario B/.test(s.legend), "the chart follows the scenario in view");
  check(/^Scenario A, 100 MW at LZ_NORTH in ERCOT, real time: at a hurdle rate of 9.6 percent, 20 years of power cost USD /.test(s.sentence ?? "") && (s.sentence ?? "").endsWith(`USD ${s.cells["a|allin"].raw.toFixed(4)} per GPU-hour.`),
    "the sentence under the table states scenario A, the headline's scenario, with B in view (session 195)", s.sentence ?? "");

  // 6: the sensitivity chart
  check(s.bars.length === 8 && s.bars.every((b, i) => i === 0 || s.bars[i - 1].size >= b.size) && !s.bars.some((b) => b.key === "cshare" || b.key === "cprice"), "eight bars at the default, sorted by size, no contract row (session 213)", s.bars.map((b) => b.key).join(", "));
  const lib = F.sensitivity(b1, P.ways);
  check(JSON.stringify(s.bars.map((b) => b.key)) === JSON.stringify(lib.map((b) => b.key)) && s.bars.every((b, i) => near(b.size, lib[i].size, 1e-9)), "each bar is the library's");
  check(/Lowered by the step/.test(s.legend) && /Raised by the step/.test(s.legend), "a legend names the two directions");
  const first = s.bars.find((b) => b.key === "pue");   // an assumption with a step on both sides
  const box = await evaluate(`(() => { const e = document.querySelector('[data-bar="${first.key}"]'); e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(); return { x: r.x + r.width * 0.75, y: r.y + r.height / 2 }; })()`);
  await noRequest("pointing at a bar", () => send("Input.dispatchMouseEvent", { type: "mouseMoved", x: box.x, y: box.y }));
  const hover = await evaluate(STATE);
  check(/moved by .+: all-in power per GPU-hour is USD [\d.]+ at [\d,.-]+ and USD [\d.]+ at [\d,.-]+; USD [\d.]+ at /.test(hover.readout) && hover.readout === first.title, "pointing at a bar states the two values and the step", hover.readout);
  check(/^How the load runs, the other way \(the same in every hour\): USD [\d.]+ per GPU-hour; USD [\d.]+ as it is \(off in the 100 most expensive hours of each year\)\.$/.test(s.bars.find((b) => b.key === "run").title), "the way of running has one step, the other way, stated with both figures", s.bars.find((b) => b.key === "run").title);
  await shot("datacenter-scenarios-compared-desktop", 1280);

  // 7: no word of recommendation. "A bad month" is the page's own headline: the top tenth of 36 months, a rank.
  const judged = (s.text + " " + hover.readout).toLowerCase().match(/\b(better|worse|attractive|should|recommend\w*|best|worst|good|poor|prefer\w*|favou?r\w*)\b/g);
  check(!judged?.length, "no word of recommendation in the block", (judged ?? []).join(", "));

  // 4: the address round trip
  const shared = s.href;
  const again = await open(shared);
  check(again.search === s.search && again.view === "b", "the shared address opens with B in view", again.search);
  check(JSON.stringify(again.cells) === JSON.stringify(s.cells) && again.against === s.against, "the same numbers in every cell, and the same sentences");
  check(JSON.stringify(again.fields.map((f) => f.value)) === JSON.stringify(s.fields.map((f) => f.value)) && again.words === s.words, "the same inputs and the same words");
  await click('[data-view="a"]');
  const againA = await evaluate(STATE);
  check(Number(againA.fields.find((f) => f.key === "pue").value) === 1.2 && !/v=b/.test(againA.search), "A is as it was set", againA.search);
  if (outDir) { fs.mkdirSync(outDir, { recursive: true }); fs.writeFileSync(path.join(outDir, "shared_link.txt"), shared.replace(base, "https://erw-flame.vercel.app") + "\n"); }

  // 5: copy and reset
  await noRequest("Copy A to B", () => click("[data-copy]"));
  s = await evaluate(STATE);
  check(s.search === "?ap=1.2&bp=1.2" && s.headA.length === 0 && s.words === "A and B hold the same assumptions." && s.against === "No difference." && JSON.stringify(s.cells["a|pv"]) === JSON.stringify(s.cells["b|pv"]), "Copy A to B: B is A, and nothing differs", s.search);
  await noRequest("one Reset", () => click('button[data-reset="pue"]'));
  s = await evaluate(STATE);
  check(s.search === "?bp=1.2" && Number(s.fields.find((f) => f.key === "pue").value) === 1.56, "a Reset returns one assumption of the scenario in view to its default", s.search);
  await click('[data-view="b"]');
  await type("growth", "2");
  s = await evaluate(STATE);
  check(near(s.cells["b|level"].raw, F.levelPrice({ ...d, pue: 1.2, growth: 2 }, flat)) && s.cells["b|level"].raw > s.cells["b|price"].raw && /rising 2 percent a year for 20 years/.test(s.cells["b|level"].text), "with prices rising, the fixed price with the same present value stands above the last twelve months' price", s.cells["b|level"].text);
  await noRequest("the Reset for all", () => click("[data-reset-all]"));
  s = await evaluate(STATE);
  check(s.search === "?v=b" && s.fields.every((f) => Number(f.value) === d[f.key]), "Reset all of B returns every assumption of B to its default", s.search);

  // 8: the page's own parameters: a flexible load, Show and the grid
  const PF = W.pageOf({ run: "hours", n: "100" });
  s = await open("/cost-of-power?grid=ercot&region=LZ_NORTH&mw=50&run=hours&n=100&buy=rt&au=50&bh=9");
  const df = F.defaultsOf(PF.load);
  check(df.run === 1 && Number(s.fields[0].value) === 1 && /^Default flexible\./.test(s.fields[0].source) && s.cells["a|price"].raw.toFixed(2) === num(s.per).toFixed(2) && s.cells["a|price"].raw === PF.s12.per,
    "on a flexible load's page both scenarios default to flexible, and the price is that page's headline", `${s.cells["a|price"].text} against ${s.per}`);
  check(/^For 50 MW at LZ_NORTH in ERCOT, real time$/.test(s.headFor) && s.headA.length === 2 && near(s.cells["a|pv"].raw, F.presentValue({ ...df, upfront: 50 }, PF.ways[1])) && near(s.cells["b|pv"].raw, F.presentValue({ ...df, hurdle: 9 }, PF.ways[1])), "both scenarios are read from the address beside the page's own parameters, for the reader's size", s.headFor);
  await choose("0");
  s = await evaluate(STATE);
  check(s.cells["a|price"].raw === flat.per && /aw=0/.test(s.search) && s.cells["a|off"].raw === null, "set to flat, a scenario there reads the flat load's own twelve months", `${s.cells["a|price"].text}; ${s.search}`);
  await evaluate(`(() => { const e = document.querySelector('form[data-load-form] input[name="mw"]'); e.focus(); e.select(); })()`);
  await send("Input.insertText", { text: "200" });
  await evaluate(`document.querySelector('form[data-load-form] button[type="submit"]').click()`);
  await sleep(4000);
  s = await evaluate(STATE);
  check(/mw=200/.test(s.search) && /aw=0/.test(s.search) && /au=50/.test(s.search) && /bh=9/.test(s.search) && /^For 200 MW at /.test(s.headFor) && s.headA.length === 3, "Show keeps the scenarios", s.search);
  await evaluate(`document.querySelector('[data-grid="caiso"] input').click()`);
  await sleep(5000);
  s = await evaluate(STATE);
  check(/grid=caiso/.test(s.search) && /au=50/.test(s.search) && /bh=9/.test(s.search) && !s.none && !s.bad && / in CAISO, /.test(s.headFor), "another grid keeps the scenarios", s.search);

  // 8b (session 195): scenario A sets the headline; "Your load" holds no power per GPU and no overhead ratio; an older
  // link's `gpu` and `pue` are read as the scenarios'
  {
    const HEAD = `(() => {
      const sum = document.querySelector("[data-summary]");
      return { row: sum?.nextElementSibling?.innerText ?? "", gpu: document.querySelector('[data-stat="gpu_hour"]')?.textContent ?? "",
        fields: [...document.querySelectorAll("form[data-load-form] input[name]")].map((e) => e.name), where: document.querySelector("[data-costs-in-a]")?.textContent ?? "",
        runNote: document.querySelector("[data-scenario-a-run]")?.textContent ?? "", adderNote: document.querySelector("[data-scenario-a-adder]")?.textContent ?? "" };
    })()`;
    s = await open("/cost-of-power");
    let h = await evaluate(HEAD);
    check(!h.fields.includes("gpu") && !h.fields.includes("pue") && /scenario A gives the headline/.test(h.where), "\"Your load\" holds no power per GPU and no overhead ratio, and says scenario A gives the headline", [...new Set(h.fields)].join(", "));
    check(h.row.includes(`USD ${s.cells["a|gpu"].raw.toFixed(4)}`) && h.row.includes(`USD ${s.cells["a|price"].raw.toFixed(2)}`) && h.row.includes(`USD ${s.cells["a|bad"].raw.toFixed(2)}`) && h.gpu === s.cells["a|gpu"].raw.toFixed(4) && /At 1\.3 kW per GPU and an overhead ratio of 1\.56/.test(h.row),
      "at the defaults the three headline numbers are scenario A's rows, and the page's own of before this session", h.row.replace(/\s+/g, " ").slice(0, 160));
    await noRequest("typing an overhead ratio into A, for the headline", () => type("pue", "1.2"));
    h = await evaluate(HEAD); s = await evaluate(STATE);
    check(h.row.includes(`USD ${s.cells["a|gpu"].raw.toFixed(4)}`) && h.gpu === s.cells["a|gpu"].raw.toFixed(4) && /overhead ratio of 1\.2:/.test(h.row) && near(s.cells["a|gpu"].raw, F.gpuHour({ ...d, pue: 1.2 }, flat)),
      "a change of A's overhead ratio moves the headline's power per GPU-hour, its GPUs, and the summary sentence's figure", h.row.replace(/\s+/g, " ").slice(-120));
    await choose("1");
    h = await evaluate(HEAD); s = await evaluate(STATE);
    check(h.row.includes(`USD ${s.cells["a|price"].raw.toFixed(2)}`) && s.cells["a|price"].raw < flat.per && /Scenario A runs flexible/.test(h.runNote) && /Your load/.test(h.runNote),
      "A set to flexible moves the headline's market energy, and the headline says the sections below are the load as \"Your load\" describes it", h.runNote);
    await evaluate(`document.querySelector('[data-view="b"]').click()`);
    await sleep(350);
    await noRequest("typing an overhead ratio into B", () => type("pue", "1.9"));
    const hb = await evaluate(HEAD); s = await evaluate(STATE);
    check(hb.row === h.row && hb.gpu === h.gpu && /^Scenario A/.test(s.sentence ?? ""), "a change of B moves neither the headline nor the sentence under the table");
    s = await open("/cost-of-power?gpu=1&pue=1.2");
    h = await evaluate(HEAD);
    check(Number(s.fields.find((f) => f.key === "gpu").value) === 1 && near(s.cells["a|gpu"].raw, F.gpuHour({ ...d, gpu: 1, pue: 1.2 }, flat)) && near(s.cells["b|gpu"].raw, s.cells["a|gpu"].raw) && h.gpu === s.cells["a|gpu"].raw.toFixed(4)
      && /ag=1(&|$)/.test(s.search) && /bg=1(&|$)/.test(s.search) && /ap=1\.2/.test(s.search) && /bp=1\.2/.test(s.search) && !/[?&](gpu|pue)=/.test(s.search),
      "an older link's gpu and pue open the same numbers in the headline and in both scenarios, and leave the address", s.search);
  }

  // 9 (session 213): the contract as two scenario assumptions of A. Typed into the block it goes into the address and
  // nowhere else; A's price, its year's cost and the headline read it; the chart gains its two rows; a Reset returns
  // the market's figure. The fixed price with the same present value does not read it.
  await open("/cost-of-power");
  const stored = `JSON.stringify([localStorage.length, sessionStorage.length, document.cookie])`;
  const storedBefore = await evaluate(stored);
  const CONTRACT = `(() => { const c = document.querySelector('[data-headline-contract="2"]'); const v = document.querySelector('[data-headline-contract="1"]'); return { words: c?.textContent ?? "", value: v?.textContent ?? "" }; })()`;
  check((await evaluate(CONTRACT)).words === "" && s.cells["a|price"].raw === flat.per, "at the defaults no contract is named and the headline's energy is the market's");
  const r00 = F.resultOf(d, flat);
  await noRequest("typing a contract price into A, with no share", () => type("cprice", "30"));
  s = await evaluate(STATE);
  check(/[?&]ac=30$/.test(s.search) && !/an=/.test(s.search) && s.cells["a|price"].raw === flat.per && near(s.cells["a|bill"].raw, r00.bill) && near(s.cells["a|pv"].raw, r00.pv) && (await evaluate(CONTRACT)).words === "" && s.bars.length === 8, "a price with no share goes into the address and moves nothing; no contract row in the chart", s.search);
  await noRequest("typing a contract share into A", () => type("cshare", "50"));
  s = await evaluate(STATE);
  const ac = { ...d, cshare: 50, cprice: 30 }, rc = F.resultOf(ac, flat), con = await evaluate(CONTRACT);
  check(/[?&]an=50&ac=30$/.test(s.search) && near(s.cells["a|price"].raw, rc.price) && near(s.cells["a|bill"].raw, rc.bill) && near(s.cells["a|pv"].raw, rc.pv) && near(s.cells["a|gpu"].raw, rc.gpuHour) && rc.bill !== r00.bill, "the share goes into the address; A's price, year's cost, GPU-hour and present value read the contract", `${s.search}: ${s.cells["a|price"].text}`);
  check(near(s.cells["a|price"].raw, 0.5 * flat.per + 0.5 * 30) && near(s.cells["a|level"].raw, r00.level, 1e-12), "the price is half the market's and half the contract's; the fixed price with the same present value stays the market's", s.cells["a|level"].text);
  check(s.bars.length === 10 && s.bars.some((b) => b.key === "cshare") && s.bars.some((b) => b.key === "cprice"), "with a contract in A the chart draws its share and price as two more rows", s.bars.map((b) => b.key).join(", "));
  check(/50 percent of the energy at USD 30 per MWh/.test(con.words) && con.value === `USD ${L.two(rc.price)}`, "the headline names the contract and shows the price of the energy with it", `${con.words.trim()} ${con.value}`);
  check(JSON.stringify(s.headA) === JSON.stringify(["contract 50%", "contract USD 30/MWh"]) && s.words === "B: contract share 0 percent against 50; contract price USD 0 per MWh against 30.", "the headers and the row in words name the contract", s.words);
  check(/50 percent of the energy contracted at USD 30 per MWh/.test(s.cells["a|bill"].text), "the year's cost says what the contract is", s.cells["a|bill"].text);
  check((await evaluate(stored)) === storedBefore, "the contract writes nothing to storage or cookies");
  s = await open("/cost-of-power?an=50&ac=30");
  check(near(s.cells["a|price"].raw, rc.price) && Number(s.fields.find((f) => f.key === "cshare").value) === 50, "the address with the contract opens with it");
  await evaluate(`document.querySelector('[data-reset="cshare"]').click()`);
  await sleep(400);
  s = await evaluate(STATE);
  check(s.search === "?ac=30" && s.cells["a|price"].raw === flat.per && (await evaluate(CONTRACT)).words === "" && s.bars.length === 8, "a Reset of the share returns the headline to the market's figure and the chart to eight rows", s.search);
  const visitor = await fetch(`${base}/cost-of-power/months.csv`).then((r) => r.status).catch(() => 0);
  check(visitor === 404, "a visitor (no internal cookie) is answered 404 for the download while the page is in review", String(visitor));

  // 10: the other grids, a region with no twelve months, a region whose flexible way is not held
  for (const grid of Object.keys(W.INDEX.grids).filter((g) => g !== "ercot")) {
    const p = W.pageOf({ grid });
    s = await open(`/cost-of-power?grid=${grid}`);
    const dg = F.defaultsOf(p.load);
    if (!p.ways[0]) { check(!s.none && s.cells["a|price"].raw === null, `${grid}: no twelve months at its main region, and nothing is filled`); continue; }
    const rg = F.resultOf(dg, p.ways[0]);
    check(!s.bad && s.cells["a|price"].raw === rg.price && s.cells["a|price"].raw.toFixed(2) === num(s.per).toFixed(2) && near(s.cells["a|pv"].raw, rg.pv) && s.bars.length === 8 && s.cells["a|price"].text.includes(`${L.shortMonth(p.l12[0].m)} to ${L.shortMonth(p.l12[11].m)}`),
      `${grid}, ${p.x.region}, ${L.BUYS[p.x.buy].toLowerCase()}: the scenarios read that page's own twelve months and name them`, s.cells["a|price"].text);
  }
  let empty = null, half = null;
  for (const [grid, g] of Object.entries(W.INDEX.grids)) for (const r of g.regions) {
    if (empty && half) break;
    const p = W.pageOf({ grid, region: r.id });
    if (!empty && !p.ways[0] && !p.ways[1] && r[p.x.buy]) empty = { grid, region: r.id };
    if (!half && p.ways[0] && !p.ways[1]) half = { grid, region: r.id };
  }
  if (empty) {
    s = await open(`/cost-of-power?grid=${empty.grid}&region=${encodeURIComponent(empty.region)}`);
    check(!s.none && !s.bad && s.cells["a|price"].raw === null && s.cells["a|pv"].raw === null && (s.cells["a|price"].missing ?? "").length > 20 && s.bars.length === 0 && s.sentence === null && s.fields.length === 10 && s.against === "Not held for both scenarios.",
      `${empty.region} in ${empty.grid}, no twelve months: the rows say not held with the reason on hover, with no chart and no sentence (nothing is filled)`, s.none ? "no block" : s.cells["a|price"].missing ?? "");
  } else console.log("note every region with a price holds twelve months: the empty case is not on this build's files");
  if (half) {
    s = await open(`/cost-of-power?grid=${half.grid}&region=${encodeURIComponent(half.region)}`);
    check(!s.none && !s.bad && s.fields[0].options[1].off === true && /not held here/.test(s.fields[0].options[1].text) && /day-ahead|Twelve complete months/.test(s.fields[0].source) && s.cells["a|price"].raw !== null && s.bars.find((b) => b.key === "run").size === 0,
      `${half.region} in ${half.grid}: the flexible way is not held, the list says so with its reason, and the flat scenario is computed`, s.none ? "no block" : s.fields[0].source);
    const forced = await open(`/cost-of-power?grid=${half.grid}&region=${encodeURIComponent(half.region)}&aw=1`);
    check(Number(forced.fields[0].value) === 0 && forced.cells["a|price"].raw !== null, "an address that asks for the way not held gets the default");
  } else console.log("note every region with twelve months holds both ways: the half case is not on this build's files");

  // 11: phone width
  for (const q of ["", "?ap=1.2&bw=1&bu=50&bh=10&v=b"]) {
    s = await open(`/cost-of-power${q}`, 390);
    check(s.clientW === 390 && s.scrollW <= s.clientW + 1, `390 px${q ? ", two scenarios" : ""}: the page does not scroll sideways`, `scroll width ${s.scrollW}, width ${s.clientW}`);
    check(s.bars.length === 8 && s.rows.length === 10, `390 px${q ? ", two scenarios" : ""}: the table and the chart are drawn`);
    await shot(q ? "datacenter-scenarios-compared-phone" : "datacenter-scenarios-default-phone", 390);
  }
  return 0;
}, { width: 1280, height: 900 }).catch((e) => { failed++; console.log(`FAIL the browser run stopped: ${e.message}`); return 1; });

if (code === null) { console.log("check-datacenter-scenarios: no Chrome or Edge on this machine; nothing was checked"); process.exit(env("GITHUB_ACTIONS") === "true" ? 1 : 0); }
if (!process.env.TEXT_ONLY) console.log(failed ? `\ncheck-datacenter-scenarios FAILED: ${failed} of ${count}` : `\ncheck-datacenter-scenarios: all ${count} passed`);
process.exit(failed ? 1 : 0);
