// Energy Research Warehouse (ERW) site, session 179: the scenarios of /cost-of-power/battery in the internal view, in a
// headless browser, at desktop width (1280) and phone width (390).
//
//   npm run build && npm start
//   node scripts/check-battery-scenarios.mjs [base-url] [output-dir]
//   TEXT_ONLY=name node scripts/check-battery-scenarios.mjs [base-url] [output-dir]
//       writes only <output-dir>/<name>.txt, the visible text of the page at its bare address (for the comparison of the
//       page before and after a change), and exits
//
// The page is in review: this script unlocks the internal view first (/internal/unlock with INTERNAL_COSTS_TOKEN from
// the environment or site/.env.local; the token is never printed). It asserts:
//   1. the panel: ten assumptions in order, each with its default, its source and a Reset; one Reset for all; "Copy A
//      to B"; at the bare address nothing is written into the address;
//   2. the table: two columns, seven rows in order and the last row in words; at the defaults A's revenue, 10th-percentile
//      month and coverage are the page's own headline numbers, and every other number is lib/battery/finance.ts's;
//   3. a change computes in the browser: no request, the address gains the parameter, the header of each column shows
//      only what differs and the last row says it in words. The one request allowed after a scenario change is
//      session 177's usage count (POST /api/usage, the event and the path, no value), at most once a page view, sent
//      only once the call marked in Scenarios.tsx is added; typing the contract terms is held to no request at all;
//   4. a step of efficiency is the model's own run in data/battery_scenario_steps.json;
//   5. the address round trip: opening the address again gives the same inputs and the same numbers;
//   6. "Copy A to B", a Reset and the Reset for all;
//   7. the sensitivity chart: ten bars sorted by size (twelve with a contract, session 211), a legend, and a hover that states the two values and the step;
//   8. no word of recommendation in the block;
//   9. the page's own six parameters still work, and its links and its Show carry the scenarios;
//  10. at 390 px the page does not scroll sideways;
//  12. (session 195) scenario A sets the headline: "Your battery" holds no fixed O&M and no debt payments; at the
//      defaults the headline is the page's own of before; a change of A moves the headline's coverage, its debt
//      payments, its check key and the summary sentence, and a change of B moves none of them; the sentence under the
//      table states scenario A; A's efficiency step moves the headline's revenue and the page says so; an older link's
//      `fom` and `ds` open the same headline and leave the address. Since the owner's ruling of 11 October 2026 no usage
//      count is allowed at all: every change is held to no request (item 3's allowance is closed);
//  11. the contract panel's promise, with the scenarios beside it: typing the terms sends no request, leaves the
//      address unchanged and stores nothing; a scenario change after it sends no request and puts no contract term in
//      the address; a change of duration keeps the terms and no request of it carries them.
// The contract of scripts/test-battery-stack.mjs (written when the page was open to visitors) that an input change
// sends no request is held here for the scenarios, in the internal view. Prints one line per assertion; exits 1 if any fails.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const outDir = process.argv[3];
const PORT = 9379;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const F = await import("../lib/battery/finance.ts");
const B = await import("../lib/batterystack.ts");
const STEPS = process.env.TEXT_ONLY ? null : JSON.parse(fs.readFileSync(path.join(here, "..", "data", "battery_scenario_steps.json"), "utf-8"));

function token() {
  if (process.env.INTERNAL_COSTS_TOKEN) return process.env.INTERNAL_COSTS_TOKEN;
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    const m = fs.readFileSync(f, "utf-8").match(/^INTERNAL_COSTS_TOKEN=(.*)$/m);
    if (m) return m[1].trim().replace(/^["']|["']$/g, "");
  }
  return "";
}
function chromePath() {
  const c = [process.env.CHROME_PATH, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"].filter(Boolean);
  const p = c.find((x) => fs.existsSync(x));
  if (!p) throw new Error("no Chrome or Edge found; set CHROME_PATH");
  return p;
}
async function cdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0;
  const pending = new Map(), listeners = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const { res, rej } = pending.get(m.id); pending.delete(m.id); m.error ? rej(new Error(m.error.message)) : res(m.result); }
    else if (m.method) listeners.forEach((f) => f(m));
  };
  return {
    send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }),
    on: (f) => listeners.push(f),
  };
}
let failed = 0;
function check(ok, what, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`);
}
const near = (a, b, tol = 1e-9) => Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));

const tok = token();
if (!tok) { console.log("check-battery-scenarios FAILED: INTERNAL_COSTS_TOKEN is not set here, so the page in review cannot be opened"); process.exit(1); }
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-battery-scenarios-"));
const chrome = spawn(chromePath(), ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--hide-scrollbars", "--disable-gpu", "about:blank"]);
try {
  let version;
  for (let i = 0; i < 50 && !version; i++) { await sleep(200); version = await fetch(`http://127.0.0.1:${PORT}/json/version`).then((r) => r.json()).catch(() => undefined); }
  if (!version) throw new Error("headless browser did not start");
  const target = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" }).then((r) => r.json());
  const page = await cdp(target.webSocketDebuggerUrl);
  await page.send("Page.enable");
  await page.send("Network.enable");
  const requests = [];
  page.on((m) => { if (m.method === "Network.requestWillBeSent" && !m.params.request.url.startsWith("data:")) requests.push({ url: m.params.request.url, method: m.params.request.method, body: m.params.request.postData ?? "", headers: JSON.stringify(m.params.request.headers ?? {}) }); });
  const ev = async (expression) => {
    const r = await page.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(`${r.exceptionDetails.text}: ${expression.slice(0, 120)}`);
    return r.result.value;
  };
  const go = async (route, width = 1280) => {
    await page.send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
    const loaded = new Promise((res) => page.on((m) => m.method === "Page.loadEventFired" && res()));
    countsThisView = 0;
    const nav = await page.send("Page.navigate", { url: route.startsWith("http") ? route : base + route });
    if (nav.errorText) throw new Error(`${route.split("?")[0]}: ${nav.errorText}`);
    await Promise.race([loaded, sleep(30000)]);
    await sleep(1800);
  };
  const shot = async (name, width) => {
    if (!outDir) return;
    fs.mkdirSync(outDir, { recursive: true });
    const { cssContentSize } = await page.send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 12000);
    await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(500);
    const s = await page.send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(outDir, `${name}.png`), Buffer.from(s.data, "base64"));
  };
  /** Type a value into an assumption's field as a reader would: focus, select all, type. */
  // session 296: the twelve fields sit in the box's "Financing" section, closed by default: it is opened first, as a reader opens it
  const type = async (k, text) => {
    await ev(`(() => { const e = document.querySelector('input[data-assumption="${k}"]'); const f = e.closest("details"); if (f) f.open = true; e.scrollIntoView({ block: "center" }); e.focus(); e.select(); })()`);
    await page.send("Input.insertText", { text });
    await sleep(350);
    await ev(`document.activeElement && document.activeElement.blur()`);
    await sleep(150);
  };
  const choose = async (k, v) => {
    await ev(`(() => { const e = document.querySelector('select[data-assumption="${k}"]'); const f = e.closest("details"); if (f) f.open = true; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set.call(e, "${v}"); e.dispatchEvent(new Event("change", { bubbles: true })); })()`);
    await sleep(350);
  };
  const click = async (sel) => { await ev(`document.querySelector(${JSON.stringify(sel)}).click()`); await sleep(350); };
  const STATE = `(() => {
    const root = document.querySelector("[data-scenarios]");
    if (!root) return null;
    const head = (p) => { const h = root.querySelector('[data-head="' + p + '"]'); return [...h.querySelectorAll("[data-differs]")].map((e) => e.textContent); };
    const checked = (end) => { const e = [...document.querySelectorAll("[data-check]")].find((x) => x.getAttribute("data-check").endsWith(end)); return e ? Number(e.getAttribute("data-raw")) : null; };
    // session 296: the panel (the twelve fields, the two tabs, Copy and Reset all) is in the box on the left, under
    // "Financing", not inside the block: it is read from the page
    const panel = document.querySelector("[data-assumptions]");
    return {
      view: panel.getAttribute("data-assumptions"),
      fields: [...panel.querySelectorAll("[data-field]")].map((f) => ({
        key: f.getAttribute("data-field"), value: f.querySelector("[data-assumption]").value, tag: f.querySelector("[data-assumption]").tagName,
        options: [...f.querySelectorAll("option")].map((o) => o.value), reset: !!f.querySelector("button[data-reset]"), resetOff: f.querySelector("button[data-reset]")?.disabled ?? null,
        def: f.querySelector("[data-default]")?.getAttribute("data-default") ?? null, source: f.querySelector("[data-default]")?.textContent ?? "" })),
      resetAll: panel.querySelector("[data-reset-all]")?.textContent ?? null, copy: panel.querySelector("[data-copy]")?.textContent ?? null,
      steps: panel.querySelector("[data-steps]")?.getAttribute("data-steps") ?? null, stepsText: panel.querySelector("[data-steps]")?.textContent ?? "",
      folds: [...document.querySelectorAll("[data-settings-fold]")].map((f) => ({ id: f.getAttribute("data-settings-fold"), open: f.open, summary: f.querySelector("[data-fold-summary]")?.textContent ?? "" })),
      noRange: document.querySelector("[data-no-range]")?.getAttribute("data-no-range") ?? "",
      rows: [...root.querySelectorAll("[data-scenario-table] tbody tr")].map((r) => r.getAttribute("data-row")),
      cells: Object.fromEntries([...root.querySelectorAll("[data-cell]")].map((c) => [c.getAttribute("data-cell"), { raw: c.getAttribute("data-raw") === "" ? null : Number(c.getAttribute("data-raw")), text: c.textContent }])),
      headA: head("a"), headB: head("b"), words: root.querySelector("[data-differs-words]").textContent,
      sentence: root.querySelector("[data-npv-sentence]")?.textContent ?? null,
      bars: [...document.querySelectorAll("[data-bar]")].map((b) => ({ key: b.getAttribute("data-bar"), size: Number(b.getAttribute("data-size")), title: b.getAttribute("title") })),
      chartView: document.querySelector("[data-sensitivity]")?.getAttribute("data-sensitivity") ?? null,
      legend: document.querySelector("[data-sensitivity] figcaption")?.textContent ?? "", readout: document.querySelector("[data-sensitivity-readout]")?.textContent ?? "",
      howToRead: document.querySelector("[data-how-to-read]")?.textContent ?? "", questions: [...document.querySelectorAll("[data-question] > section > h2")].map((h) => h.textContent),
      contractHead: document.querySelector("[data-headline-contract]")?.textContent ?? "", otherGrids: document.querySelector("[data-other-grids]")?.textContent ?? "",
      text: root.innerText, search: location.search, href: location.href,
      l12kw: checked("|l12_kw:total"), p10: checked("|p10_36"), cover: checked("|cover"),
      summary: document.querySelector("[data-summary]")?.textContent ?? "",
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    };
  })()`;
  // Session 177's usage count (lib/usage.ts: POST /api/usage, the event and the path, no value) is the one request a
  // scenario change may cause, once a page view, when the call marked in Scenarios.tsx is added. Everything else is
  // held to none; `strict` holds the usage count to none as well (the contract box's promise).
  const isCount = (r) => r.method === "POST" && new URL(r.url).pathname === "/api/usage" && new URL(r.url).search === "";
  const counts = [];
  let countsThisView = 0;
  const noRequest = async (what, act, strict = true) => {
    const mark = requests.length;
    await act();
    await sleep(700);
    const sent = requests.slice(mark);
    const count = sent.filter(isCount), other = sent.filter((r) => !isCount(r));
    counts.push(...count);
    countsThisView += count.length;
    check(other.length === 0 && (!strict || count.length === 0), `${what}: no request is sent${count.length && !strict ? " but the usage count" : ""}`, sent.slice(0, 3).map((r) => `${r.method} ${r.url}`).join(" "));
    if (count.length) check(countsThisView <= 1, `${what}: at most one usage count a page view`, `${countsThisView} sent`);
  };

  await go(`/internal/unlock?token=${encodeURIComponent(tok)}`);
  if (process.env.TEXT_ONLY) {
    await go("/cost-of-power/battery");
    const text = await ev(`document.querySelector("main")?.innerText ?? document.body.innerText`);
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, `${process.env.TEXT_ONLY}.txt`), text.replace(/\r\n/g, "\n"));
    console.log(`${process.env.TEXT_ONLY}.txt: ${text.split("\n").length} lines of ${base}/cost-of-power/battery`);
    // leave as the full run does: the browser stopped and its profile removed (an exit here would skip the finally below)
    chrome.kill();
    await sleep(300);
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the profile is in the temp directory */ }
    process.exit(0);
  }

  // 1 and 2: the bare address
  await go("/cost-of-power/battery");
  let s = await ev(STATE);
  check(!!s, "the bare address: the block is on the page");
  check(JSON.stringify(s.questions) === JSON.stringify(["What did it earn?", "Is it worth building?", "What matters most"]), "the three questions, in order (session 208)", (s.questions ?? []).join(" | "));
  check(/^Each row moves one assumption of scenario A to its published low case and its published high case/.test(s.howToRead), "one line says how to read the chart (session 296: the sourced range by default)", s.howToRead);
  // session 296: the box on the left: five sections, two open, each with its summary line
  check(JSON.stringify(s.folds.map((f) => f.id)) === JSON.stringify(["battery", "heads", "charts", "financing", "sensitivity"]) && s.folds.filter((f) => f.open).map((f) => f.id).join(",") === "battery,heads",
    "the box has five sections, Assumptions and Headline figures open (session 296)", s.folds.map((f) => `${f.id}:${f.open}`).join(", "));
  check(/^Scenario A: 20% debt at 8%, 12% hurdle, no contract$/.test(s.folds.find((f) => f.id === "financing")?.summary ?? ""), "the financing section's one line says its settings", s.folds.find((f) => f.id === "financing")?.summary);
  check(/^Sourced range, NPV$/.test(s.folds.find((f) => f.id === "sensitivity")?.summary ?? "") && /^3 of 8: /.test(s.folds.find((f) => f.id === "heads")?.summary ?? "") && /^Revenue by stream; adjusted scale$/.test(s.folds.find((f) => f.id === "charts")?.summary ?? ""),
    "the sensitivity, headline and chart sections' lines say the defaults", s.folds.map((f) => f.summary).join(" | "));
  check(/The other five grids, in words only/.test(s.otherGrids) && /seller tab/.test(s.otherGrids), "one line under the grid picker stands for the other grids", s.otherGrids.slice(0, 80));
  const d = F.defaultsOf(B.COSTS[4]);
  check(s.search === "", "the bare address stays bare: nothing is written into it", s.search);
  check(JSON.stringify(s.fields.map((f) => f.key)) === JSON.stringify(F.KEYS), "twelve assumptions, in the order asked (session 208: the contract's share and price last)", s.fields.map((f) => f.key).join(", "));
  check(s.fields.every((f) => Number(f.value) === d[f.key] && Number(f.def) === d[f.key]), "each field holds its default", s.fields.map((f) => `${f.key} ${f.value}`).join(", "));
  check(s.fields.every((f) => f.reset && f.resetOff === true), "each has a Reset, idle at the default");
  check(s.fields.every((f) => /^Default [\d,.]+\. .{12,}\.$/.test(f.source)), "each states its default and where the default comes from", s.fields.find((f) => !/^Default [\d,.]+\. .{12,}\.$/.test(f.source))?.source ?? "");
  check(s.fields.filter((f) => /Lazard, Levelized Cost of Energy\+, June 2025/.test(f.source)).length === 9, "nine defaults cite Lazard's June 2025 report (session 196: the degradation and the hurdle rate among them)", s.fields.filter((f) => !/Lazard/.test(f.source)).map((f) => f.key).join(", "));
  check(s.resetAll === "Reset all of A" && s.copy === "Copy A to B", "one Reset for all, and Copy A to B", `${s.resetAll}; ${s.copy}`);
  check(JSON.stringify(s.rows) === JSON.stringify(["revenue", "p10", "coverage", "npv", "irr", "toll", "tail", "differs"]), "seven rows in order, then the row in words", s.rows.join(", "));
  check(s.headA.length === 0 && s.headB.length === 0 && s.words === "A and B hold the same assumptions.", "equal scenarios: nothing in the headers", s.words);
  check(s.cells["a|revenue"].raw === s.l12kw && s.cells["b|revenue"].raw === s.l12kw, "revenue is the page's last twelve months per kW", `${s.cells["a|revenue"].text}`);
  check(s.cells["a|p10"].raw === s.p10, "the 10th-percentile month is the page's bad month", s.cells["a|p10"].text);
  check(near(s.cells["a|coverage"].raw, s.cover, 1e-6) && s.cells["a|coverage"].raw.toFixed(2) === s.cover.toFixed(2), "coverage is the page's headline coverage", `${s.cells["a|coverage"].text}`);
  const r0 = F.resultOf(d, s.l12kw);
  check(near(s.cells["a|npv"].raw, r0.npv) && near(s.cells["a|toll"].raw, r0.toll) && near(s.cells["a|tail"].raw, r0.tail.pv) && (r0.irr === null ? s.cells["a|irr"].raw === null : near(s.cells["a|irr"].raw, r0.irr)),
    "NPV, IRR, the toll and the tail are the library's on the page's revenue", `${s.cells["a|npv"].text} | ${s.cells["a|irr"].text} | ${s.cells["a|toll"].text} | ${s.cells["a|tail"].text}`);
  check(/^Scenario A, 100 MW, 4-hour: at a hurdle rate of 12 percent, NPV is USD -?[\d,.]+( million| billion)?\.$/.test(s.sentence ?? ""), "the sentence states the number", s.sentence ?? "");
  check(s.steps === "held" && JSON.stringify(s.fields.find((f) => f.key === "rte").options) === JSON.stringify(STEPS.rte_steps.map(String)) && JSON.stringify(s.fields.find((f) => f.key === "cycles").options) === JSON.stringify(STEPS.cycle_steps.map(String)),
    "efficiency and cycles offer exactly the steps the model was run at", `${s.steps}: ${s.stepsText}`);
  await shot("scenarios-default-desktop", 1280);
  await page.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });

  // 3: a change computes in the browser
  await noRequest("typing a capital cost into A", () => type("capex", "1300"));
  s = await ev(STATE);
  const a1 = { ...d, capex: 1300 };
  check(s.search === "?ac=1300", "the address gains the one parameter", s.search);
  check(near(s.cells["a|npv"].raw, F.resultOf(a1, s.l12kw).npv) && near(s.cells["a|coverage"].raw, F.coverage(a1, s.l12kw)) && near(s.cells["b|npv"].raw, r0.npv), "A is recomputed and B is not moved", `${s.cells["a|npv"].text} against ${s.cells["b|npv"].text}`);
  check(JSON.stringify(s.headA) === JSON.stringify(["capex 1,300 USD/kW"]) && JSON.stringify(s.headB) === JSON.stringify(["capex 1,110 USD/kW"]), "each header shows only what differs", `${s.headA} | ${s.headB}`);
  check(s.words === "B: capex USD 1,110 per kW against 1,300.", "the last row says it in words", s.words);
  check(s.fields.find((f) => f.key === "capex").resetOff === false && s.fields.filter((f) => f.resetOff === false).length === 1, "only the changed field's Reset is live");
  await noRequest("putting B in view", () => click('[data-view="b"]'));
  await noRequest("typing a hurdle rate into B", () => type("hurdle", "10"));
  await noRequest("choosing an efficiency step for B", () => choose("rte", 92));
  await noRequest("choosing a cycle limit for B", () => choose("cycles", 2));
  await noRequest("typing a term into B", () => type("term", "10"));
  s = await ev(STATE);
  const b1 = { ...d, hurdle: 10, rte: 92, cycles: 2, term: 10 };
  check(s.search === "?ac=1300&bt=10&be=92&by=2&bh=10&v=b", "the address keeps both scenarios and the one in view", s.search);
  // 4: the step is the model's own run
  const cell = STEPS.cases["ercot|foresight|4"].cells["92|2"];
  const rev92 = cell.slice(-12).reduce((x, y) => x + y, 0) / 1000;
  check(near(s.cells["b|revenue"].raw, rev92, 1e-9) && s.cells["b|revenue"].raw > s.cells["a|revenue"].raw, "B's revenue at 92 percent and two cycles is the model's own run in the file of steps", `${s.cells["b|revenue"].text} against ${s.cells["a|revenue"].text}`);
  const rb = F.resultOf(b1, rev92);
  check(near(s.cells["b|npv"].raw, rb.npv) && near(s.cells["b|tail"].raw, rb.tail.pv) && /years 11 to 20/.test(s.cells["b|tail"].text) && near(s.cells["b|toll"].raw, rb.toll), "B's NPV, toll and tail follow (a ten-year term leaves years 11 to 20)", `${s.cells["b|npv"].text} | ${s.cells["b|toll"].text} | ${s.cells["b|tail"].text}`);
  check(s.headA.length === 5 && s.headB.length === 5 && s.words === "B: capex USD 1,110 per kW against 1,300; term 10 years against 20; round-trip efficiency 92 percent against 86; cycles a day 2 against 1; hurdle rate 10 percent against 12.", "five differences, in the headers and in words", s.words);
  check(s.chartView === "b" && /scenario B/.test(s.legend), "the chart follows the scenario in view");
  check(/^Scenario A, 100 MW, 4-hour: at a hurdle rate of 12 percent, NPV is USD /.test(s.sentence ?? "") && (s.sentence ?? "").endsWith(`NPV is ${s.cells["a|npv"].text.match(/^USD -?[\d.,]+( million| billion)?/)[0]}.`),
    "the sentence under the table states scenario A, the headline's scenario, with B in view (session 195)", s.sentence ?? "");

  // 7: the sensitivity chart
  // session 296: the sourced range by default: the six assumptions with a published low and high case, and a line naming the others
  check(s.bars.length === 6 && s.bars.every((b, i) => i === 0 || s.bars[i - 1].size >= b.size) && !s.bars.some((b) => b.key === "cshare" || b.key === "cprice") && ["capex", "fom", "share", "rte", "deg", "life"].every((k) => s.bars.some((b) => b.key === k)),
    "six bars at the default (the sourced range: capital cost, fixed O&M, debt share, efficiency, degradation, life), sorted by size, no contract row", s.bars.map((b) => b.key).join(", "));
  check(s.noRange === "rate+term+cycles+hurdle" || s.noRange.split("+").sort().join("+") === "cycles+hurdle+rate+term", "the line under the chart names the four without a published range", s.noRange);
  check(/Low case/.test(s.legend) && /High case/.test(s.legend), "a legend names the two cases");
  const box = await ev(`(() => { const e = document.querySelector('[data-bar="${s.bars[0].key}"]'); e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(); return { x: r.x + r.width * 0.75, y: r.y + r.height / 2 }; })()`);
  await noRequest("pointing at a bar", () => page.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: box.x, y: box.y }));
  const hover = await ev(STATE);
  check(/at its published low case: NPV is USD -?[\d,.]+.* at [\d,.]+; at its published high case: USD -?[\d,.]+.* at [\d,.]+; USD/.test(hover.readout) && hover.readout === s.bars[0].title && /Lazard|Annual Technology Baseline/.test(hover.readout),
    "pointing at a bar states the two NPVs, the two cases and their source (session 296)", hover.readout);
  await shot("scenarios-compared-desktop", 1280);
  await page.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });

  // 8: no word of recommendation
  const judged = (s.text + " " + hover.readout).toLowerCase().match(/\b(better|worse|attractive|should|recommend\w*|best|worst|good|poor|prefer\w*|favou?r\w*)\b/g);
  check(!judged, "no word of recommendation in the block", (judged ?? []).join(", "));

  // 5: the address round trip
  const shared = s.href;
  await go(shared);
  const again = await ev(STATE);
  check(again.search === s.search && again.view === "b", "the shared address opens with B in view", again.search);
  check(JSON.stringify(again.cells) === JSON.stringify(s.cells), "the same numbers in every cell");
  check(JSON.stringify(again.fields.map((f) => f.value)) === JSON.stringify(s.fields.map((f) => f.value)) && again.words === s.words, "the same inputs and the same words");
  await click('[data-view="a"]');
  const againA = await ev(STATE);
  check(Number(againA.fields.find((f) => f.key === "capex").value) === 1300 && !/v=b/.test(againA.search), "A is as it was set", againA.search);
  if (outDir) { fs.mkdirSync(outDir, { recursive: true }); fs.writeFileSync(path.join(outDir, "shared_link.txt"), shared.replace(base, "https://erw-flame.vercel.app") + "\n"); }

  // 6: copy and reset
  await noRequest("Copy A to B", () => click("[data-copy]"));
  s = await ev(STATE);
  check(s.search === "?ac=1300&bc=1300" && s.headA.length === 0 && s.words === "A and B hold the same assumptions." && JSON.stringify(s.cells["a|npv"]) === JSON.stringify(s.cells["b|npv"]), "Copy A to B: B is A, and nothing differs", s.search);
  await noRequest("one Reset", () => click('button[data-reset="capex"]'));
  s = await ev(STATE);
  check(s.search === "?bc=1300" && Number(s.fields.find((f) => f.key === "capex").value) === 1110, "a Reset returns one assumption of the scenario in view to its default", s.search);
  await click('[data-view="b"]');
  await type("deg", "2");
  await noRequest("the Reset for all", () => click("[data-reset-all]"));
  s = await ev(STATE);
  check(s.search === "?v=b" && s.fields.every((f) => Number(f.value) === d[f.key]), "Reset all of B returns every assumption of B to its default", s.search);

  // 9: the page's own parameters, and its links
  await go("/cost-of-power/battery?grid=ercot&dur=4&strat=dayahead&mw=50&fom=30&ds=4000000&ac=1300&bh=9");
  s = await ev(STATE);
  check(/50 MW, 4-hour battery in ERCOT/.test(s.summary) && /^grid=ercot&dur=4&strat=dayahead&mw=50&/.test(s.search.slice(1)), "the page's own four parameters are read as before", s.search);
  check(/ac=1300/.test(s.search) && /af=30/.test(s.search) && /bh=9/.test(s.search) && !/[?&](fom|ds)=/.test(s.search) && s.headA.length === 3,
    "and the scenarios beside them: the old fom is A's fixed O&M, A's own capital cost wins over the old ds, and the old names leave the address (session 195)", s.search);
  const links = await ev(`({ d8: document.querySelector('[data-duration="8"]').getAttribute("href"), d4: document.querySelector('[data-duration="4"]').getAttribute("href") })`);
  check(/dur=8/.test(links.d8) && /bh=9/.test(links.d8) && !/ac=/.test(links.d8) && /ac=1300/.test(links.d4), "a duration link carries the scenarios and drops a typed capital cost", links.d8);
  await ev(`(() => { const e = document.querySelector('input[name="mw"]'); e.focus(); e.select(); })()`);
  await page.send("Input.insertText", { text: "200" });
  await ev(`document.querySelector('form button[type="submit"]').click()`);
  await sleep(4000);
  s = await ev(STATE);
  check(/mw=200/.test(s.search) && /ac=1300/.test(s.search) && /bh=9/.test(s.search) && /200 MW, 4-hour battery/.test(s.summary), "Show keeps the scenarios", s.search);

  // 11 (session 208): the contract is scenario A's two assumptions, 0 by default. A share and a price typed into A go into
  // the address like every other assumption; the headline's coverage reads them and loses its check key (the table holds no
  // contract); the row's coverage is lib/battery/finance.ts's; a price with no share moves nothing; no request is sent.
  await go("/cost-of-power/battery?grid=ercot&dur=4&strat=foresight");
  s = await ev(STATE);
  const stored = `JSON.stringify([localStorage.length, sessionStorage.length, document.cookie])`;
  const storedBefore = await ev(stored);
  const CONTRACT = `(() => { const c = document.querySelector("[data-headline-contract]"); const k = [...document.querySelectorAll("[data-check]")].find((x) => x.getAttribute("data-check").endsWith("|cover")); const sum = document.querySelector("[data-summary]"); return { words: c?.textContent ?? "", keyed: !!k, cover: Number(sum.textContent.match(/covered its debt ([\\d.]+) times/)?.[1] ?? NaN) }; })()`;
  check((await ev(CONTRACT)).words === "" && (await ev(CONTRACT)).keyed && s.cells["a|coverage"].raw !== null, "at the defaults no contract is named and the headline's coverage carries its check key");
  const r00 = F.resultOf(d, s.l12kw);
  await noRequest("typing a contract price into A, with no share", () => type("cprice", "10"));
  s = await ev(STATE);
  check(/[?&]ap=10$/.test(s.search) && !/an=/.test(s.search) && near(s.cells["a|coverage"].raw, r00.coverage) && near(s.cells["a|npv"].raw, r00.npv) && (await ev(CONTRACT)).words === "", "a price with no share goes into the address and moves nothing", s.search);
  await noRequest("typing a contract share into A", () => type("cshare", "50"));
  s = await ev(STATE);
  const rc = F.resultOf({ ...d, cshare: 50, cprice: 10 }, s.l12kw), con = await ev(CONTRACT);
  check(/[?&]an=50&ap=10$/.test(s.search) && near(s.cells["a|coverage"].raw, rc.coverage) && near(s.cells["a|npv"].raw, rc.npv) && rc.coverage !== r00.coverage, "the share goes into the address; A's coverage and NPV read the contract", `${s.search}: ${s.cells["a|coverage"].text}`);
  // session 296: in the sourced range the contract's two have no published case, so they are named under the chart, not drawn
  // (session 211's two rows are drawn in the percent-step mode, checked below)
  check(s.bars.length === 6 && !s.bars.some((b) => b.key === "cshare") && /cshare/.test(s.noRange) && /cprice/.test(s.noRange), "with a contract in A the sourced range names the contract's share and price as having no published case", s.noRange);
  await noRequest("switching the sensitivity to a percent step", () => click('[data-seg="mode"] [data-seg-key="pct"]'));
  s = await ev(STATE);
  check(s.bars.length === 12 && s.bars.some((b) => b.key === "cshare") && s.bars.some((b) => b.key === "cprice") && /sm=pct/.test(s.search), "by a percent step, with a contract in A, the chart draws its share and price as two more rows (session 211), and the address says so", `${s.search}: ${s.bars.map((b) => b.key).join(", ")}`);
  check(/down and up by 10 percent of its value/.test(s.howToRead) && /Lowered by 10 percent/.test(s.legend), "the line and the legend say the percent", s.howToRead);
  await noRequest("switching the sensitivity back to the sourced range", () => click('[data-seg="mode"] [data-seg-key="range"]'));
  s = await ev(STATE);
  check(/50 percent of its power contracted at USD 10 per kW-month/.test(con.words) && !con.keyed && near(con.cover, Number(rc.coverage.toFixed(2)), 1e-9), "the headline names the contract, reads its coverage and drops the key", `${con.words.trim()} ${con.cover}`);
  check(JSON.stringify(s.headA) === JSON.stringify(["contract 50%", "contract USD 10/kW-month"]) && s.words === "B: contract share 0 percent against 50; contract price USD 0 per kW-month against 10.", "the headers and the row in words name the contract", s.words);
  check(/contract 50 percent at USD 10 per kW-month; debt payments/.test(s.cells["a|coverage"].text), "the coverage cell says what the contract is", s.cells["a|coverage"].text);
  check((await ev(stored)) === storedBefore, "the contract writes nothing to storage or cookies");
  await go("/cost-of-power/battery?an=50&ap=10");
  s = await ev(STATE);
  check(near(s.cells["a|coverage"].raw, rc.coverage) && Number(s.fields.find((f) => f.key === "cshare").value) === 50, "the address with the contract opens with it");
  await click('[data-reset="cshare"]');
  s = await ev(STATE);
  check(s.search === "?ap=10" && near(s.cells["a|coverage"].raw, r00.coverage) && (await ev(CONTRACT)).keyed, "a Reset of the share returns the headline to the table's own figure, with its key", s.search);

  // session 195: no usage count is sent from the block (the owner's ruling of 11 October 2026)
  check(counts.length === 0, "no usage count was sent by any change on the page", `${counts.length} sent`);

  // 12 (session 195): scenario A sets the headline
  const HEAD = `(() => {
    const sum = document.querySelector("[data-summary]");
    const checked = (end) => { const e = [...document.querySelectorAll("[data-check]")].find((x) => x.getAttribute("data-check").endsWith(end)); return e ? Number(e.getAttribute("data-raw")) : null; };
    return { row: sum?.nextElementSibling?.innerText ?? "", summary: sum?.textContent ?? "", ds: checked("|ds"), cover: checked("|cover"),
      key: [...document.querySelectorAll("[data-check]")].find((x) => x.getAttribute("data-check").endsWith("|cover"))?.getAttribute("data-check") ?? "",
      fields: [...document.querySelectorAll("aside form input[name]")].map((e) => e.name), where: document.querySelector("[data-costs-in-a]")?.textContent ?? "",
      stepsNote: document.querySelector("[data-scenario-a-steps]")?.textContent ?? "" };
  })()`;
  await go("/cost-of-power/battery");
  s = await ev(STATE);
  let h = await ev(HEAD);
  const l12 = s.l12kw, cover0 = h.cover;
  check(!h.fields.includes("fom") && !h.fields.includes("ds") && /scenario A gives the headline/.test(h.where), "\"Your battery\" holds no fixed O&M and no debt payments, and says scenario A gives the headline", h.fields.join(", "));
  check(h.ds === F.debtUsd(d, 100) && h.ds === Math.round(B.debtPerMw(4) * 100) && near(h.cover, (l12 * 100000 - d.fom * 100000) / h.ds, 1e-12) && near(h.cover, s.cells["a|coverage"].raw, 1e-6),
    "at the defaults the headline's debt payments and coverage are the page's own of before this session, and scenario A's row", `USD ${h.ds}, ${h.cover}`);
  await noRequest("typing a capital cost into A, for the headline", () => type("capex", "1300"));
  h = await ev(HEAD); s = await ev(STATE);
  check(h.ds === F.debtUsd({ ...d, capex: 1300 }, 100) && near(h.cover, (l12 * 100000 - d.fom * 100000) / h.ds, 1e-12) && near(h.cover, s.cells["a|coverage"].raw, 1e-6) && h.cover < cover0
    && h.summary.includes(`covered its debt ${h.cover.toFixed(2)} times`) && h.key.endsWith(`&ds=${h.ds}|cover`),
    "a change of A moves the headline's coverage, its debt payments, its check key and the summary sentence", `${h.cover} on USD ${h.ds}`);
  await noRequest("typing a fixed O&M into A, for the headline", () => type("fom", "30"));
  h = await ev(HEAD);
  check(near(h.cover, (l12 * 100000 - 30 * 100000) / h.ds, 1e-12) && h.key.includes("&fom=30&"), "and A's fixed O&M moves it too", String(h.cover));
  await click('[data-view="b"]');
  await noRequest("typing a capital cost into B", () => type("capex", "900"));
  let hb = await ev(HEAD); s = await ev(STATE);
  check(hb.cover === h.cover && hb.ds === h.ds && hb.row === h.row && /^Scenario A/.test(s.sentence ?? ""), "a change of B moves neither the headline nor the sentence under the table");
  await click('[data-view="a"]');
  await noRequest("choosing an efficiency step for A", () => choose("rte", 92));
  h = await ev(HEAD); s = await ev(STATE);
  check(h.row.includes(`USD ${s.cells["a|revenue"].raw.toFixed(2)}`) && s.cells["a|revenue"].raw > l12 && /Scenario A: round-trip efficiency 92 percent/.test(h.stepsNote) && /at a round-trip efficiency of 92 percent/.test(h.summary),
    "A's efficiency step moves the headline's revenue, and the headline names the step and says the sections below are the model's own run", h.stepsNote);
  await go("/cost-of-power/battery?fom=30&ds=4000000");
  h = await ev(HEAD); s = await ev(STATE);
  check(h.ds === 4000000 && near(h.cover, (l12 * 100000 - 3000000) / 4000000, 1e-12) && Number(s.fields.find((f) => f.key === "fom").value) === 30 && /af=30/.test(s.search) && /ac=/.test(s.search) && !/[?&](fom|ds)=/.test(s.search),
    "an older link's fom and ds open the same headline (A's fixed O&M; the capital cost at which A's debt payments are that amount) and leave the address", `${s.search}: ${h.cover} on USD ${h.ds}`);
  await go(`/cost-of-power/battery?fom=${d.fom}&ds=${Math.round(B.debtPerMw(4) * 100)}`);
  s = await ev(STATE);
  check(s.search === "" && s.fields.every((f) => Number(f.value) === d[f.key]), "an older link that held the defaults opens the bare address", s.search);

  // other grids
  await go("/cost-of-power/battery?grid=caiso&dur=2&strat=foresight");
  s = await ev(STATE);
  check(!!s && s.steps === "held" && Number(s.fields.find((f) => f.key === "capex").value) === 610 && s.cells["a|revenue"].raw === s.l12kw, "CAISO, 2 hours: the block opens at that duration's defaults, steps held", s ? s.cells["a|revenue"].text : "no block");
  await go("/cost-of-power/battery?grid=nyiso&dur=4&strat=foresight");
  s = await ev(STATE);
  if (s) check(s.steps === "none" && s.fields.find((f) => f.key === "rte").options.length === 1 && /only the model's own step is held for NYISO/.test(s.stepsText), "a grid in review offers the default step alone and says so", s.stepsText);
  else console.log("note NYISO: no block (no month held in the review snapshot)");

  // 10: phone width
  for (const q of ["", "?ac=1300&bt=10&be=92&by=2&bh=10&v=b"]) {
    await go(`/cost-of-power/battery${q}`, 390);
    s = await ev(STATE);
    check(s.clientW === 390 && s.scrollW <= s.clientW + 1, `390 px${q ? ", two scenarios" : ""}: the page does not scroll sideways`, `scroll width ${s.scrollW}, width ${s.clientW}`);
    check(s.bars.length === 6 && s.rows.length === 8, `390 px${q ? ", two scenarios" : ""}: the table and the chart are drawn (session 296: six rows in the sourced range)`);
    await shot(q ? "scenarios-compared-phone" : "scenarios-default-phone", 390);
  }
} finally {
  chrome.kill();
  await sleep(300);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the profile is in the temp directory */ }
}
console.log(failed ? `\n${failed} FAILED` : "\nall passed");
process.exit(failed ? 1 : 0);
