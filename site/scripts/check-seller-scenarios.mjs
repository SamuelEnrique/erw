// Energy Research Warehouse (ERW) site, session 186: the scenarios of /cost-of-power/seller in the internal view, in a
// headless browser, at desktop width (1280) and phone width (390). The twin of scripts/check-battery-scenarios.mjs.
//
//   npm run build && npm start
//   node scripts/check-seller-scenarios.mjs [base-url] [output-dir]
//   TEXT_ONLY=name node scripts/check-seller-scenarios.mjs [base-url] [output-dir]
//       writes only <output-dir>/<name>.txt, the visible text of the page at its bare address (for the comparison of the
//       page before and after a change), and exits
//
// The page is in review: this script unlocks the internal view first (/internal/unlock with INTERNAL_COSTS_TOKEN from
// the environment, site/.env.local or the root .env; the token is never printed). It asserts:
//   1. the panel: eight assumptions in order, each with its default, its source and a Reset; one Reset for all; "Copy A
//      to B"; at the bare address nothing is written into the address;
//   2. the table: two columns, eight rows in order and the last row in words; at the defaults revenue, the capture
//      price, the worst month, coverage and the pair with a battery are the page's own numbers elsewhere on it, and NPV,
//      IRR and the contract price are lib/seller/finance.ts's on the page's revenue and the model's energy;
//   3. a change computes in the browser: no request at all, the address gains the parameter, the header of each column
//      shows only what differs and the last row says it in words;
//   4. the address round trip: opening the address again gives the same inputs and the same numbers;
//   5. "Copy A to B", a Reset and the Reset for all;
//   6. the sensitivity chart (session 212: in the page's third section, "What matters most"): eight bars sorted by
//      size at the default, a legend, and a hover that states the two values and the step;
//   7. no word of recommendation in the block;
//   8. the page's own parameters still work (another hub prices the scenarios too), and Show, the asset choice and
//      "Reset the costs" carry the scenarios;
//   9. (session 212) the contract as two assumptions of a scenario: typed into the block it goes into the address and
//      nowhere else; A's coverage, NPV and the headline read it; the chart gains its two rows; a Reset returns the
//      market's figure with its check key;
//  10. the other assets and grids: wind, a battery and a peaker (a toll, and no pair), CAISO, New York (no pair), and a
//      zone with no twelve months (nothing is filled); the pair and the worst month are read from the page's two CSV
//      downloads (session 212: the tables beside the page), which a visitor is answered 404 for while the page is in
//      review;
//  11. at 390 px the page does not scroll sideways.
//  Session 212: the page asks three questions (the battery page's layout); the chart, the worst month's source and the
//  pair's source moved with it, and the contract panel of session 145 is gone.
// Prints one line per assertion; exits 1 if any fails.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const outDir = process.argv[3];
const PORT = 9386;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const F = await import("../lib/seller/finance.ts");
const M = await import("../lib/merchant.ts");
const SNAP = process.env.TEXT_ONLY ? null : JSON.parse(fs.readFileSync(path.join(here, "..", "data", "merchant_snapshot.json"), "utf-8"));

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
const num = (s) => (s === null || s === undefined ? null : Number(String(s).replace(/,/g, "")));

/** The model's last twelve months per MW at the main hub, from the snapshot the page reads: the newest held month whose
 * eleven months before it are all held. Revenue in USD per kW and energy in MWh per kW. */
function twelveOf(iso, asset) {
  const ms = M.months(SNAP, { iso, asset, mw: 1, mwh: asset === "battery" ? 4 : 0, ds: 0, hr: M.HEAT_RATE, vom: M.VOM, fom: 0 });
  const by = new Map(ms.map((r) => [r.m, r]));
  const prev = (m, k) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1)).toISOString().slice(0, 7);
  for (const r of [...ms].reverse()) {
    if (!r.held) continue;
    const t = Array.from({ length: 12 }, (_, k) => by.get(prev(r.m, k)));
    if (t.every((x) => x && x.held)) return { revenueKw: t.reduce((a, x) => a + x.revenue, 0) / 1000, energyKw: t.reduce((a, x) => a + x.energy, 0) / 1000 };
  }
  return null;
}

const tok = token();
if (!tok) { console.log("check-seller-scenarios FAILED: INTERNAL_COSTS_TOKEN is not set here, so the page in review cannot be opened"); process.exit(1); }
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-seller-scenarios-"));
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
    const nav = await page.send("Page.navigate", { url: route.startsWith("http") ? route : base + route });
    if (nav.errorText) throw new Error(`${route.split("?")[0]}: ${nav.errorText}`);
    await Promise.race([loaded, sleep(30000)]);
    await sleep(1800);
  };
  const shot = async (name, width) => {
    if (!outDir) return;
    fs.mkdirSync(outDir, { recursive: true });
    const { cssContentSize } = await page.send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 14000);
    await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(500);
    const s = await page.send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(outDir, `${name}.png`), Buffer.from(s.data, "base64"));
    await page.send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
  };
  /** Type a value into an assumption's field as a reader would: focus, select all, type. */
  const type = async (k, text) => {
    await ev(`(() => { const e = document.querySelector('input[data-assumption="${k}"]'); e.scrollIntoView({ block: "center" }); e.focus(); e.select(); })()`);
    await page.send("Input.insertText", { text });
    await sleep(350);
    await ev(`document.activeElement && document.activeElement.blur()`);
    await sleep(150);
  };
  const click = async (sel) => { await ev(`document.querySelector(${JSON.stringify(sel)}).click()`); await sleep(350); };
  const STATE = `(() => {
    const root = document.querySelector("[data-scenarios]");
    if (!root) return null;
    const head = (p) => { const h = root.querySelector('[data-head="' + p + '"]'); return [...h.querySelectorAll("[data-differs]")].map((e) => e.textContent); };
    const raw = (sel) => { const e = document.querySelector(sel); return e ? Number(e.getAttribute("data-raw")) : null; };
    const t = (sel) => document.querySelector(sel)?.textContent ?? null;
    return {
      view: root.querySelector("[data-assumptions]").getAttribute("data-assumptions"),
      fields: [...root.querySelectorAll("[data-field]")].map((f) => ({
        key: f.getAttribute("data-field"), value: f.querySelector("[data-assumption]").value, reset: !!f.querySelector("button[data-reset]"), resetOff: f.querySelector("button[data-reset]")?.disabled ?? null,
        def: f.querySelector("[data-default]")?.getAttribute("data-default") ?? null, source: f.querySelector("[data-default]")?.textContent ?? "" })),
      resetAll: root.querySelector("[data-reset-all]")?.textContent ?? null, copy: root.querySelector("[data-copy]")?.textContent ?? null,
      rows: [...root.querySelectorAll("[data-scenario-table] tbody tr")].map((r) => r.getAttribute("data-row")),
      labels: Object.fromEntries([...root.querySelectorAll("[data-scenario-table] tbody tr")].map((r) => [r.getAttribute("data-row"), r.querySelector("th").textContent])),
      cells: Object.fromEntries([...root.querySelectorAll("[data-cell]")].map((c) => [c.getAttribute("data-cell"), { raw: c.getAttribute("data-raw") === "" ? null : Number(c.getAttribute("data-raw")), text: c.textContent, missing: c.querySelector("[data-missing]")?.getAttribute("title") ?? null }])),
      headA: head("a"), headB: head("b"), headFor: root.querySelector("[data-scenario-table] thead th").textContent, words: root.querySelector("[data-differs-words]").textContent,
      sentence: root.querySelector("[data-npv-sentence]")?.textContent ?? null,
      // session 212: the chart is the page's third section, outside the block
      bars: [...document.querySelectorAll("[data-bar]")].map((b) => ({ key: b.getAttribute("data-bar"), size: Number(b.getAttribute("data-size")), title: b.getAttribute("title") })),
      chartView: document.querySelector("[data-sensitivity]")?.getAttribute("data-sensitivity") ?? null,
      legend: document.querySelector("[data-sensitivity] figcaption")?.textContent ?? "", readout: document.querySelector("[data-sensitivity-readout]")?.textContent ?? "",
      howToRead: document.querySelector("[data-how-to-read]")?.textContent ?? "",
      text: root.innerText, search: location.search, href: location.href,
      l12: t('[data-stat="l12_kw"]'), pricedAt: t('[data-stat="priced_at"]'), cap: t('[data-stat="cap_price"]'), capFlat: t('[data-stat="cap_flat"]'),
      cover: raw('[data-stat="cover"] [data-check]'),
      before: (() => { const hs = [...document.querySelectorAll("main h2, main section h2, h2")].map((h) => h.textContent); return hs; })(),
      summary: document.querySelector("[data-summary]")?.textContent ?? "", bad: /undefined|NaN/.test(document.querySelector("main")?.innerText ?? document.body.innerText),
      resetCosts: document.querySelector("[data-reset-costs]")?.getAttribute("href") ?? null,
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    };
  })()`;
  /** Session 212: the page's two CSV downloads, fetched by the browser (so with the internal view's cookie) for the
   * address in view, parsed: the worst held month's revenue from months.csv, and the pair and the plant alone at
   * day-ahead prices from tables.csv. The figures the page drew in its own sections until this session. */
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
  const fetchText = (route) => ev(`fetch(${JSON.stringify(route)}).then(async (r) => r.status + "\\n" + await r.text())`);
  const downloads = async (search) => {
    const [ms, ts] = await Promise.all([fetchText(`/cost-of-power/seller/months.csv${search}`), fetchText(`/cost-of-power/seller/tables.csv${search}`)]);
    const status = (t) => Number(t.split("\n")[0]);
    const body = (t) => t.slice(t.indexOf("\n") + 1);
    const mRows = parseCsv(body(ms)), tRows = parseCsv(body(ts));
    const mh = mRows[0] ?? [], th = tRows[0] ?? [];
    const col = (h, name) => h.indexOf(name);
    const held = mRows.slice(1).filter((r) => r[col(mh, "held")] === "yes").map((r) => Number(r[col(mh, "revenue_usd")]));
    const tv = (table, row, column) => { const r = tRows.slice(1).find((x) => x[0] === table && x[1] === row && x[2] === column); return r && r[3] !== "" ? Number(r[3]) : null; };
    return { status: [status(ms), status(ts)], months: mRows.length - 1, tables: tRows.length - 1,
      worst: held.length ? Math.min(...held) : null, pair: tv("battery_beside", "energy_at_day_ahead_prices", "co_optimized_pair_usd"), plant: tv("battery_beside", "energy_at_day_ahead_prices", "plant_alone_usd"),
      heads: `${body(ms).split("\n")[0]} | ${body(ts).split("\n")[0]}` };
  };
  // every change in the block is held to no request at all: nothing typed on this page is sent, so no usage count
  // follows an input on it (components/Usage.tsx), and the block sends none of its own
  const noRequest = async (what, act) => {
    const mark = requests.length;
    await act();
    await sleep(700);
    const sent = requests.slice(mark);
    check(sent.length === 0, `${what}: no request is sent`, sent.slice(0, 3).map((r) => `${r.method} ${r.url}`).join(" "));
  };

  await go(`/internal/unlock?token=${encodeURIComponent(tok)}`);
  if (process.env.TEXT_ONLY) {
    await go("/cost-of-power/seller");
    const text = await ev(`document.querySelector("main")?.innerText ?? document.body.innerText`);
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, `${process.env.TEXT_ONLY}.txt`), text.replace(/\r\n/g, "\n"));
    console.log(`${process.env.TEXT_ONLY}.txt: ${text.split("\n").length} lines of ${base}/cost-of-power/seller`);
    chrome.kill();
    await sleep(300);
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the profile is in the temp directory */ }
    process.exit(0);
  }

  // 1 and 2: the bare address (ERCOT, solar, 100 MW, the hub average)
  await go("/cost-of-power/seller");
  let s = await ev(STATE);
  check(!!s && !s.bad, "the bare address: the block is on the page");
  const D = M.DEFAULTS.solar;
  const d = F.defaultsOf({ ...D, deg: F.SOLAR_DEG });   // session 298 (ruling 7a): solar's degradation default is the ATB's 0.7
  check(s.search === "", "the bare address stays bare: nothing is written into it", s.search);
  check(JSON.stringify(s.fields.map((f) => f.key)) === JSON.stringify(F.KEYS), "eleven assumptions, in the order asked (session 212: the contract's share and price; session 264: the PPA term last)", s.fields.map((f) => f.key).join(", "));
  check(/percent of the energy/.test(s.text) && /USD per MWh/.test(s.fields.find((f) => f.key === "cprice").source + s.text), "for solar the contract is a share of the energy at a price per MWh");
  let dl = await downloads("");
  check(dl.status[0] === 200 && dl.status[1] === 200 && dl.months > 12 && dl.tables > 100 && /^# Energy Research Warehouse/.test(dl.heads), "the two CSV downloads answer the internal view with their provenance lines", `${dl.status}; ${dl.months} months, ${dl.tables} cells`);
  check(s.fields.every((f) => Number(f.value) === d[f.key] && Number(f.def) === d[f.key]), "each field holds its default", s.fields.map((f) => `${f.key} ${f.value}`).join(", "));
  check(s.fields.every((f) => f.reset && f.resetOff === true), "each has a Reset, idle at the default");
  check(s.fields.every((f) => /^Default [\d,.]+\. .{12,}\.$/.test(f.source)), "each states its default and where the default comes from", s.fields.find((f) => !/^Default [\d,.]+\. .{12,}\.$/.test(f.source))?.source ?? "");
  check(s.fields.filter((f) => /Lazard, Levelized Cost of Energy\+, June 2025/.test(f.source)).length === 8, "eight defaults cite Lazard's June 2025 report (session 196: the hurdle rate among them; session 264: the PPA term, the asset's life)", s.fields.filter((f) => !/Lazard/.test(f.source)).map((f) => f.key).join(", "));
  check(/1,150 to 1,600 for solar/.test(s.fields[0].source) && /35 years for solar/.test(s.fields.find((f) => f.key === "life").source), "the capital cost and the life cite the asset's own range and life", s.fields[0].source);
  check(s.resetAll === "Reset all of A" && s.copy === "Copy A to B", "one Reset for all, and Copy A to B", `${s.resetAll}; ${s.copy}`);
  check(JSON.stringify(s.rows) === JSON.stringify(["revenue", "capture", "month", "coverage", "npv", "irr", "contract", "ppa", "battery", "differs"]), "nine rows in order (session 235: the breakeven PPA price), then the row in words", s.rows.join(", "));
  check(s.headA.length === 0 && s.headB.length === 0 && s.words === "A and B hold the same assumptions.", "equal scenarios: nothing in the headers", s.words);
  check(s.cells["a|revenue"].raw.toFixed(2) === num(s.l12).toFixed(2) && s.cells["b|revenue"].raw === s.cells["a|revenue"].raw, "revenue is the page's last twelve months per kW", `${s.cells["a|revenue"].text} against the headline ${s.l12}`);
  check(s.cells["a|capture"].raw.toFixed(2) === num(s.cap).toFixed(2) && s.cells["a|capture"].text.includes(`of USD ${s.capFlat}`), "the capture price is the page's price received, with its ratio to the flat average", s.cells["a|capture"].text);
  check(Math.round(s.cells["a|month"].raw) === dl.worst, "the worst month is the lowest held month of the page's months.csv (whole dollars there)", `${s.cells["a|month"].text} against ${dl.worst}`);
  check(near(s.cells["a|coverage"].raw, s.cover, 1e-6) && s.cells["a|coverage"].raw.toFixed(2) === s.cover.toFixed(2), "coverage is the page's headline coverage", s.cells["a|coverage"].text);
  check(s.cells["a|battery"].raw === dl.pair && s.cells["a|battery"].text.includes(" with") && s.cells["a|battery"].text.includes(" without") && dl.pair > dl.plant, "with and without the battery are the co-optimized pair and the plant alone of the page's tables.csv", `${s.cells["a|battery"].text} against ${dl.pair} and ${dl.plant}`);
  const tw = twelveOf("ercot", "solar");
  check(near(s.cells["a|revenue"].raw, tw.revenueKw), "revenue is the model's last twelve months in the snapshot", String(tw.revenueKw));
  const r0 = F.resultOf(d, tw.revenueKw);
  check(near(s.cells["a|npv"].raw, r0.npv) && (r0.irr === null ? s.cells["a|irr"].raw === null : near(s.cells["a|irr"].raw, r0.irr)) && near(s.cells["a|contract"].raw, F.contractPrice(d, tw.energyKw)),
    "NPV, IRR and the contract price are the library's on the page's revenue and energy", `${s.cells["a|npv"].text} | ${s.cells["a|irr"].text} | ${s.cells["a|contract"].text}`);
  check(near((s.cells["a|contract"].raw * tw.energyKw - d.fom) / F.debtService(d), 1.25, 1e-9), "at the contract price, coverage is 1.25", s.cells["a|contract"].text);
  check(/^Scenario A, 100 MW of solar: at a hurdle rate of 12 percent, NPV is USD -?[\d,.]+( million| billion)?\.$/.test(s.sentence ?? ""), "the sentence states the number (session 208: at a hurdle rate of 12)", s.sentence ?? "");
  check(JSON.stringify(s.before) === JSON.stringify(["Your plant", "What did it earn?", "Is it worth building?", "What matters most"]), "the page asks three questions, in the battery page's order, after the panel (session 212)", s.before.join(" | "));
  check(/^Each row moves one assumption of scenario A down and up by the step named, holds the others/.test(s.howToRead), "one line says how to read the chart", s.howToRead);
  await shot("seller-scenarios-default-desktop", 1280);

  // 3: a change computes in the browser
  await noRequest("typing a capital cost into A", () => type("capex", "1500"));
  s = await ev(STATE);
  const a1 = { ...d, capex: 1500 };
  check(s.search === "?ac=1500", "the address gains the one parameter", s.search);
  check(near(s.cells["a|npv"].raw, F.resultOf(a1, tw.revenueKw).npv) && near(s.cells["a|coverage"].raw, F.coverage(a1, tw.revenueKw)) && near(s.cells["b|npv"].raw, r0.npv), "A is recomputed and B is not moved", `${s.cells["a|npv"].text} against ${s.cells["b|npv"].text}`);
  check(JSON.stringify(s.headA) === JSON.stringify(["capex 1,500 USD/kW"]) && JSON.stringify(s.headB) === JSON.stringify(["capex 1,375 USD/kW"]), "each header shows only what differs", `${s.headA} | ${s.headB}`);
  check(s.words === "B: capex USD 1,375 per kW against 1,500.", "the last row says it in words", s.words);
  check(s.fields.find((f) => f.key === "capex").resetOff === false && s.fields.filter((f) => f.resetOff === false).length === 1, "only the changed field's Reset is live");
  check(s.cells["a|revenue"].raw === s.cells["b|revenue"].raw && s.cells["a|capture"].raw === s.cells["b|capture"].raw && s.cells["a|month"].raw === s.cells["b|month"].raw && s.cells["a|month"].text !== s.cells["b|month"].text,
    "revenue, the capture price and the worst month stay the page's own; the worst month's coverage follows each scenario", `${s.cells["a|month"].text} | ${s.cells["b|month"].text}`);
  await noRequest("putting B in view", () => click('[data-view="b"]'));
  await noRequest("typing a hurdle rate into B", () => type("hurdle", "10"));
  await noRequest("typing a term into B", () => type("term", "10"));
  await noRequest("typing a degradation rate into B", () => type("deg", "0.5"));
  s = await ev(STATE);
  const b1 = { ...d, hurdle: 10, term: 10, deg: 0.5 };
  check(s.search === "?ac=1500&bt=10&bd=0.5&bh=10&v=b", "the address keeps both scenarios and the one in view", s.search);
  const rb = F.resultOf(b1, tw.revenueKw);
  check(near(s.cells["b|npv"].raw, rb.npv) && near(s.cells["b|coverage"].raw, rb.coverage) && near(s.cells["b|contract"].raw, F.contractPrice(b1, tw.energyKw)) && (rb.irr === null ? s.cells["b|irr"].raw === null : near(s.cells["b|irr"].raw, rb.irr)),
    "B's coverage, NPV, IRR and contract price follow", `${s.cells["b|coverage"].text} | ${s.cells["b|npv"].text} | ${s.cells["b|irr"].text} | ${s.cells["b|contract"].text}`);
  check(s.headA.length === 4 && s.headB.length === 4 && s.words === "B: capex USD 1,375 per kW against 1,500; term 10 years against 35; degradation 0.5 percent a year against 0.7; hurdle rate 10 percent against 12.", "four differences, in the headers and in words", s.words);
  check(s.chartView === "b" && /scenario B/.test(s.legend), "the chart follows the scenario in view");
  check(/^Scenario A, 100 MW of solar: at a hurdle rate of 12 percent, NPV is USD /.test(s.sentence ?? "") && (s.sentence ?? "").endsWith(`NPV is ${s.cells["a|npv"].text.match(/^USD -?[\d.,]+( million| billion)?/)[0]}.`),
    "the sentence under the table states scenario A, the headline's scenario, with B in view (session 195)", s.sentence ?? "");

  // 6: the sensitivity chart
  check(s.bars.length === 8 && s.bars.every((b, i) => i === 0 || s.bars[i - 1].size >= b.size) && !s.bars.some((b) => b.key === "cshare" || b.key === "cprice"), "eight bars at the default, sorted by size, no contract row (session 212)", s.bars.map((b) => b.key).join(", "));
  const lib = F.sensitivity(b1, tw.revenueKw);
  check(JSON.stringify(s.bars.map((b) => b.key)) === JSON.stringify(lib.map((b) => b.key)) && s.bars.every((b, i) => near(b.size, lib[i].size * 100000, 1e-9)), "each bar is the library's, for 100 MW");
  check(/Lowered by the step/.test(s.legend) && /Raised by the step/.test(s.legend), "a legend names the two directions");
  const box = await ev(`(() => { const e = document.querySelector('[data-bar="${s.bars[0].key}"]'); e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(); return { x: r.x + r.width * 0.75, y: r.y + r.height / 2 }; })()`);
  await noRequest("pointing at a bar", () => page.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: box.x, y: box.y }));
  const hover = await ev(STATE);
  check(/moved by .+: NPV is USD -?[\d,.]+.* at [\d,.]+ and USD -?[\d,.]+.* at [\d,.]+; USD/.test(hover.readout) && hover.readout === s.bars[0].title, "pointing at a bar states the two NPVs and the step", hover.readout);
  await shot("seller-scenarios-compared-desktop", 1280);

  // 7: no word of recommendation. "The worst month" is the row the brief names, the lowest month: a rank, not a verdict.
  const judged = (s.text + " " + hover.readout).toLowerCase().replace(/the worst month/g, "").match(/\b(better|worse|attractive|should|recommend\w*|best|worst|good|poor|prefer\w*|favou?r\w*)\b/g);
  check(!judged, "no word of recommendation in the block", (judged ?? []).join(", "));

  // 4: the address round trip
  const shared = s.href;
  await go(shared);
  const again = await ev(STATE);
  check(again.search === s.search && again.view === "b", "the shared address opens with B in view", again.search);
  check(JSON.stringify(again.cells) === JSON.stringify(s.cells), "the same numbers in every cell");
  check(JSON.stringify(again.fields.map((f) => f.value)) === JSON.stringify(s.fields.map((f) => f.value)) && again.words === s.words, "the same inputs and the same words");
  await click('[data-view="a"]');
  const againA = await ev(STATE);
  check(Number(againA.fields.find((f) => f.key === "capex").value) === 1500 && !/v=b/.test(againA.search), "A is as it was set", againA.search);
  if (outDir) { fs.mkdirSync(outDir, { recursive: true }); fs.writeFileSync(path.join(outDir, "shared_link.txt"), shared.replace(base, "https://erw-flame.vercel.app") + "\n"); }

  // 5: copy and reset
  await noRequest("Copy A to B", () => click("[data-copy]"));
  s = await ev(STATE);
  check(s.search === "?ac=1500&bc=1500" && s.headA.length === 0 && s.words === "A and B hold the same assumptions." && JSON.stringify(s.cells["a|npv"]) === JSON.stringify(s.cells["b|npv"]), "Copy A to B: B is A, and nothing differs", s.search);
  await noRequest("one Reset", () => click('button[data-reset="capex"]'));
  s = await ev(STATE);
  check(s.search === "?bc=1500" && Number(s.fields.find((f) => f.key === "capex").value) === 1375, "a Reset returns one assumption of the scenario in view to its default", s.search);
  await click('[data-view="b"]');
  await type("deg", "2");
  await noRequest("the Reset for all", () => click("[data-reset-all]"));
  s = await ev(STATE);
  check(s.search === "?v=b" && s.fields.every((f) => Number(f.value) === d[f.key]), "Reset all of B returns every assumption of B to its default", s.search);

  // 8b (session 195): scenario A sets the headline; "Your plant" holds no debt payments and no fixed O&M; an older
  // link's `fom` and `ds` are read as scenario A's
  {
    const HEAD = `(() => {
      const raw = (sel) => { const e = document.querySelector(sel); return e ? Number(e.getAttribute("data-raw")) : null; };
      const all = (end) => [...document.querySelectorAll("[data-check]")].filter((x) => x.getAttribute("data-check").endsWith(end));
      return { cover: raw('[data-stat="cover"] [data-check]'), key: document.querySelector('[data-stat="cover"] [data-check]')?.getAttribute("data-check") ?? "",
        ds: all("|ds").map((e) => Number(e.getAttribute("data-raw"))), under1: all("|under1").map((e) => Number(e.getAttribute("data-raw")))[0] ?? null,
        fields: [...document.querySelectorAll("form[data-seller-form] input[name]")].map((e) => e.name), where: document.querySelector("[data-costs-in-a]")?.textContent ?? "",
        coverage: document.querySelector('[data-stat="cover"]')?.closest(".border-t-2")?.innerText ?? "" };
    })()`;
    await go("/cost-of-power/seller");
    s = await ev(STATE);
    let h = await ev(HEAD);
    const ds0 = Math.round(M.debtPerMw("solar") * 100), cover0 = h.cover;
    check(!h.fields.includes("fom") && !h.fields.includes("ds") && /scenario A gives the headline/.test(h.where), "\"Your plant\" holds no debt payments and no fixed O&M, and says scenario A gives the headline", [...new Set(h.fields)].join(", "));
    check(h.ds.length >= 1 && h.ds.every((v) => v === ds0) && F.debtUsd(d, 100) === ds0 && near(h.cover, s.cells["a|coverage"].raw, 1e-6) && h.key.includes(`&ds=${ds0}&`),
      "at the defaults the headline's coverage and its debt payments are the page's own of before this session", `USD ${ds0}, ${h.cover}`);
    await noRequest("typing a capital cost into A, for the headline", () => type("capex", "1500"));
    h = await ev(HEAD); s = await ev(STATE);
    const ds1 = F.debtUsd({ ...d, capex: 1500 }, 100);
    check(h.ds.every((v) => v === ds1) && near(h.cover, s.cells["a|coverage"].raw, 1e-6) && h.cover < cover0 && h.key.includes(`&ds=${ds1}&`) && /debt payments of/.test(h.coverage),
      "a change of A moves the headline's coverage, its check key and its debt payments", `${h.cover} on USD ${ds1}`);
    await noRequest("typing a fixed O&M into A, for the headline", () => type("fom", "20"));
    const h2 = await ev(HEAD); s = await ev(STATE);
    check(h2.cover < h.cover && near(h2.cover, s.cells["a|coverage"].raw, 1e-6) && h2.key.endsWith("&fom=20|ttm_last"), "and A's fixed O&M moves them too", String(h2.cover));
    await click('[data-view="b"]');
    await noRequest("typing a capital cost into B", () => type("capex", "900"));
    const h3 = await ev(HEAD); s = await ev(STATE);
    check(h3.cover === h2.cover && h3.ds[0] === h2.ds[0] && /^Scenario A/.test(s.sentence ?? ""), "a change of B moves neither the headline nor the sentence under the table");
    await go("/cost-of-power/seller?fom=20&ds=5000000");
    h = await ev(HEAD); s = await ev(STATE);
    check(h.ds.every((v) => v === 5000000) && Number(s.fields.find((f) => f.key === "fom").value) === 20 && /af=20/.test(s.search) && /ac=/.test(s.search) && !/[?&](fom|ds)=/.test(s.search) && near(h.cover, s.cells["a|coverage"].raw, 1e-6),
      "an older link's fom and ds open the same headline (A's fixed O&M; the capital cost at which A's debt payments are that amount) and leave the address", `${s.search}: ${h.cover}`);
    await go(`/cost-of-power/seller?ds=${ds0}&fom=${d.fom}`);
    s = await ev(STATE);
    check(s.search === "" && s.fields.every((f) => Number(f.value) === d[f.key]), "an older link that held the defaults opens the bare address", s.search);
  }

  // 8: the page's own parameters, another hub, and the links
  await go("/cost-of-power/seller?iso=ercot&asset=solar&hub=HB_WEST&mw=50&ac=1500&bh=9");
  s = await ev(STATE);
  check(/priced at the West hub \(real-time prices\)/.test(s.summary) && s.headA.length === 2 && s.cells["a|revenue"].raw.toFixed(2) === num(s.l12).toFixed(2) && !near(s.cells["a|revenue"].raw, tw.revenueKw, 1e-3),
    "at another hub the scenarios read that hub's revenue", `${s.cells["a|revenue"].text}`);
  dl = await downloads(s.search);
  check(/For 50 MW of solar/.test(s.headFor) && Math.round(s.cells["a|month"].raw) === dl.worst && /priced at the West hub/.test(s.cells["a|revenue"].text), "and the reader's size, the hub's worst month (months.csv at the hub), and where it is priced", `${s.headFor}; ${s.cells["a|month"].raw} against ${dl.worst}`);
  check(near(s.cells["a|npv"].raw, F.resultOf({ ...d, capex: 1500 }, s.cells["a|revenue"].raw).npv) && near(s.cells["b|npv"].raw, F.resultOf({ ...d, hurdle: 9 }, s.cells["b|revenue"].raw).npv), "both scenarios are read from the address beside the page's own parameters");
  check(/ac=1500/.test(s.resetCosts ?? "") && /bh=9/.test(s.resetCosts ?? "") && !/mw=/.test(s.resetCosts ?? ""), "\"Reset the costs\" keeps the scenarios", s.resetCosts ?? "");
  await ev(`(() => { const e = document.querySelector('form[data-seller-form] input[name="mw"]'); e.focus(); e.select(); })()`);
  await page.send("Input.insertText", { text: "200" });
  await ev(`document.querySelector('form[data-seller-form] button[type="submit"]').click()`);
  await sleep(4000);
  s = await ev(STATE);
  check(/mw=200/.test(s.search) && /hub=HB_WEST/.test(s.search) && /ac=1500/.test(s.search) && /bh=9/.test(s.search) && /For 200 MW of solar/.test(s.headFor) && s.headA.length === 2, "Show keeps the scenarios", s.search);
  await ev(`document.querySelector('[data-asset="wind"] input').click()`);
  await sleep(4000);
  s = await ev(STATE);
  check(/asset=wind/.test(s.search) && /bh=9/.test(s.search) && !/ac=/.test(s.search) && Number(s.fields.find((f) => f.key === "capex").value) === M.DEFAULTS.wind.capex && Number(s.fields.find((f) => f.key === "life").value) === 30,
    "another asset keeps the hurdle rate and drops a typed capital cost: the defaults are wind's", s.search);

  // 9 (session 212): the contract as two scenario assumptions of A. Typed into the block it goes into the address and
  // nowhere else; A's coverage, NPV and the headline read it; the chart gains its two rows; a Reset returns the
  // market's figure with its check key. The breakeven contract price row is for the whole of the energy and does not
  // read it.
  await go("/cost-of-power/seller?iso=ercot&asset=solar");
  s = await ev(STATE);
  const stored = `JSON.stringify([localStorage.length, sessionStorage.length, document.cookie])`;
  const storedBefore = await ev(stored);
  const CONTRACT = `(() => { const c = document.querySelector('[data-headline-contract="2"]'); const k = document.querySelector('[data-stat="cover"] [data-check]'); return { words: c?.textContent ?? "", keyed: !!k, cover: Number(document.querySelector('[data-stat="cover"]')?.textContent ?? NaN) }; })()`;
  check((await ev(CONTRACT)).words === "" && (await ev(CONTRACT)).keyed && s.cells["a|coverage"].raw !== null, "at the defaults no contract is named and the headline's coverage carries its check key");
  const en = { kind: "energy", energyKw: tw.energyKw };
  const r00 = F.resultOf(d, tw.revenueKw, en);
  await noRequest("typing a contract price into A, with no share", () => type("cprice", "40"));
  s = await ev(STATE);
  check(/[?&]ap=40$/.test(s.search) && !/an=/.test(s.search) && near(s.cells["a|coverage"].raw, r00.coverage) && near(s.cells["a|npv"].raw, r00.npv) && (await ev(CONTRACT)).words === "" && s.bars.length === 8, "a price with no share goes into the address and moves nothing; no contract row in the chart", s.search);
  await noRequest("typing a contract share into A", () => type("cshare", "50"));
  s = await ev(STATE);
  const rc = F.resultOf({ ...d, cshare: 50, cprice: 40 }, tw.revenueKw, en), con = await ev(CONTRACT);
  check(/[?&]an=50&ap=40$/.test(s.search) && near(s.cells["a|coverage"].raw, rc.coverage) && near(s.cells["a|npv"].raw, rc.npv) && rc.coverage !== r00.coverage, "the share goes into the address; A's coverage and NPV read the contract", `${s.search}: ${s.cells["a|coverage"].text}`);
  check(s.bars.length === 11 && s.bars.some((b) => b.key === "cshare") && s.bars.some((b) => b.key === "cprice") && s.bars.some((b) => b.key === "ppa"), "with a contract in A the chart draws its share, price and PPA term as three more rows (session 264)", s.bars.map((b) => b.key).join(", "));
  check(/50 percent of the energy at USD 40 per MWh/.test(con.words) && !con.keyed && near(con.cover, Number(rc.coverage.toFixed(2)), 1e-9), "the headline names the contract, reads its coverage and drops the key", `${con.words.trim()} ${con.cover}`);
  check(JSON.stringify(s.headA) === JSON.stringify(["contract 50%", "contract USD 40"]) && s.words === "B: contract share 0 percent against 50; contract price USD 0 against 40.", "the headers and the row in words name the contract", s.words);
  check(/contract 50 percent at USD 40 per MWh; debt payments/.test(s.cells["a|coverage"].text), "the coverage cell says what the contract is", s.cells["a|coverage"].text);
  check(near(s.cells["a|contract"].raw, F.contractPrice(d, tw.energyKw)), "the breakeven contract price row is for the whole of the energy and does not read the contract", s.cells["a|contract"].text);
  check((await ev(stored)) === storedBefore, "the contract writes nothing to storage or cookies");
  await go("/cost-of-power/seller?an=50&ap=40");
  s = await ev(STATE);
  check(near(s.cells["a|coverage"].raw, rc.coverage) && Number(s.fields.find((f) => f.key === "cshare").value) === 50, "the address with the contract opens with it");
  await click('[data-reset="cshare"]');
  s = await ev(STATE);
  check(s.search === "?ap=40" && near(s.cells["a|coverage"].raw, r00.coverage) && (await ev(CONTRACT)).keyed && s.bars.length === 8, "a Reset of the share returns the headline to the table's own figure, with its key, and the chart to eight rows", s.search);
  const visitor = await fetch(`${base}/cost-of-power/seller/months.csv`).then((r) => r.status).catch(() => 0);
  check(visitor === 404, "a visitor (no internal cookie) is answered 404 for the download while the page is in review", String(visitor));

  // 10: the other assets and grids
  await go("/cost-of-power/seller?iso=ercot&asset=wind");
  s = await ev(STATE);
  const dw = F.defaultsOf(M.DEFAULTS.wind), tww = twelveOf("ercot", "wind");
  dl = await downloads("?iso=ercot&asset=wind");
  check(!s.bad && s.fields.every((f) => Number(f.value) === dw[f.key]) && near(s.cells["a|revenue"].raw, tww.revenueKw) && near(s.cells["a|contract"].raw, F.contractPrice(dw, tww.energyKw)) && s.cells["a|battery"].raw === dl.pair && near(s.cells["a|coverage"].raw, s.cover, 1e-6),
    "wind: its own defaults (30 years), revenue, contract price, the pair with a battery, and the page's coverage", `${s.cells["a|revenue"].text} | ${s.cells["a|contract"].text}`);
  await go("/cost-of-power/seller?iso=ercot&asset=battery");
  s = await ev(STATE);
  const db = F.defaultsOf({ ...M.DEFAULTS.battery_4h, deg: F.BATTERY_DEG }), twb = twelveOf("ercot", "battery");
  check(!s.bad && s.fields.every((f) => Number(f.value) === db[f.key]) && near(s.cells["a|revenue"].raw, twb.revenueKw) && near(s.cells["a|contract"].raw, F.breakevenToll(db)) && /toll/.test(s.labels.contract) && /kW-month/.test(s.labels.contract),
    "a battery: the 4-hour defaults (session 196: with Lazard's degradation of 2.6 percent a year), and the contract row is a toll in USD per kW-month", `${s.cells["a|contract"].text}`);
  check(s.cells["a|battery"].raw === null && /solar or a wind plant/.test(s.cells["a|battery"].missing ?? "") && /Price while selling/.test(s.labels.capture) && s.cells["a|capture"].raw !== null && near(s.cells["a|coverage"].raw, s.cover, 1e-6) && /^Scenario A, a 100 MW \/ 400 MWh battery:/.test(s.sentence ?? ""),
    "a battery: no pair (its reason on hover), the price while selling, the page's coverage", `${s.cells["a|battery"].text} | ${s.sentence}`);
  await go("/cost-of-power/seller?iso=ercot&asset=battery&mwh=200");
  s = await ev(STATE);
  check(Number(s.fields[0].value) === M.DEFAULTS.battery_2h.capex && /a 2-hour battery/.test(s.fields[0].source), "a 2-hour battery: that duration's capital cost", s.fields[0].source);
  await go("/cost-of-power/seller?iso=ercot&asset=peaker");
  s = await ev(STATE);
  const dp = F.defaultsOf(M.DEFAULTS.peaker), twp = twelveOf("ercot", "peaker");
  check(!s.bad && s.fields.every((f) => Number(f.value) === dp[f.key]) && near(s.cells["a|revenue"].raw, twp.revenueKw) && /Margin over fuel/.test(s.labels.revenue) && /Price while running/.test(s.labels.capture) && near(s.cells["a|contract"].raw, F.breakevenToll(dp)) && near(s.cells["a|coverage"].raw, s.cover, 1e-6) && /^Scenario A, a 100 MW gas peaker:/.test(s.sentence ?? ""),
    "a gas peaker: its defaults, its margin over fuel, a toll, the page's coverage", `${s.cells["a|revenue"].text} | ${s.cells["a|contract"].text}`);
  await go("/cost-of-power/seller?iso=caiso&asset=solar");
  s = await ev(STATE);
  const twc = twelveOf("caiso", "solar");
  dl = await downloads("?iso=caiso&asset=solar");
  check(!s.bad && near(s.cells["a|revenue"].raw, twc.revenueKw) && s.cells["a|battery"].raw === dl.pair && dl.pair !== null && s.cells["a|capture"].raw.toFixed(2) === num(s.cap).toFixed(2) && near(s.cells["a|coverage"].raw, s.cover, 1e-6), "CAISO solar: revenue, the capture price, the pair (tables.csv) and coverage are the page's", `${s.cells["a|revenue"].text} | ${s.cells["a|battery"].text}`);
  await go("/cost-of-power/seller?iso=nyiso&asset=wind");
  s = await ev(STATE);
  check(!s.bad && s.cells["a|revenue"].raw !== null && s.cells["a|battery"].raw === null && (s.cells["a|battery"].missing ?? "").length > 20 && s.bars.length === 8, "New York wind: the scenarios are computed; no pair is modeled, with its reason on hover", s.cells["a|battery"].missing ?? "");
  await go("/cost-of-power/seller?iso=isone&asset=solar&hub=.Z.MAINE");
  s = await ev(STATE);
  check(!!s && !s.bad && s.cells["a|revenue"].raw === null && s.cells["a|npv"].raw === null && s.bars.length === 0 && s.sentence === null && s.fields.length === 11, "a zone with no twelve months: the rows say not held, with no chart and no sentence (nothing is filled)", s ? s.cells["a|revenue"].text : "no block");

  // 10b (session 235): the breakeven PPA price, "Make B a PPA", and the capture chart and table inside the first question
  await go("/cost-of-power/seller");
  s = await ev(STATE);
  {
    const d5 = F.defaultsOf({ ...M.DEFAULTS.solar, deg: F.SOLAR_DEG }), t5 = twelveOf("ercot", "solar"), c5 = { kind: "energy", energyKw: t5.energyKw };   // session 298
    const want = F.breakevenPpa(d5, t5.revenueKw, c5), b5 = F.asPpa(d5, t5.revenueKw, c5);
    check(near(s.cells["a|ppa"].raw, want, 1e-6) && near(s.cells["b|ppa"].raw, want, 1e-6) && /Breakeven PPA price/.test(s.labels.ppa) && /on 100 percent of the energy/.test(s.cells["a|ppa"].text)
      && Math.abs(F.npv(d5.hurdle, F.flows({ ...d5, cshare: 100, cprice: want }, t5.revenueKw, c5))) < 1e-6,
      "the breakeven PPA price is the contract price at which NPV is zero, for the whole of the energy when the scenario holds no contract", s.cells["a|ppa"].text);
    check(s.fields.every((f) => Number(f.value) === d5[f.key]) && s.search === "", "both scenarios still open as merchant, at the defaults");
    const npvA = s.cells["a|npv"].raw, covA = s.cells["a|coverage"].raw;
    const offer = await ev(`document.querySelector("[data-ppa]")?.textContent ?? ""`);
    check(/Make B a PPA/.test(offer) && /100 percent of the energy/.test(offer) && offer.includes(`USD ${b5.cprice.toFixed(2)} per MWh`) && /no published price is held/.test(offer), "the offer under the assumptions says what one click sets, and that the price is no published one", offer);
    await click("[data-make-ppa]");
    s = await ev(STATE);
    const val = (k) => Number(s.fields.find((f) => f.key === k).value);
    check(s.view === "b" && val("cshare") === 100 && val("cprice") === b5.cprice && s.search === `?bn=100&bp=${b5.cprice}&v=b`, "one click: B in view, its share 100 percent and its price the breakeven rounded up to the cent, kept in the address", s.search);
    check(s.cells["a|npv"].raw === npvA && s.cells["a|coverage"].raw === covA && s.cells["b|npv"].raw >= 0 && s.cells["b|npv"].raw < 1 && near(s.cells["b|ppa"].raw, want, 1e-6) && s.bars.length === 11,   // session 264: the PPA term is the eleventh row
      "A does not move; B's NPV is zero or just above (under USD 1 per kW); the breakeven row still reads the breakeven; the chart of B draws the contract's rows", `${s.cells["b|npv"].text} | ${s.cells["b|ppa"].text}`);
    await go("/cost-of-power/seller");
    const capT = await ev(`(() => {
      const root = document.querySelector("[data-capture]");
      if (!root) return null;
      const row = root.querySelector("[data-cap-chosen]")?.closest("tr");
      return { kind: root.getAttribute("data-capture"), inFirst: !!document.querySelector('[data-question="1"] [data-capture]'), charts: root.querySelectorAll('svg[data-bars="capture"]').length, tables: root.querySelectorAll("table").length,
        rows: root.querySelectorAll("tbody tr").length, keys: root.querySelectorAll('[data-check^="cap|"]').length, chosen: row?.querySelector("strong")?.textContent ?? null,
        l12: row?.querySelector('[data-check$="|l12|price"]')?.textContent ?? null, flat: row?.querySelector('[data-check$="|l12|flat"]')?.textContent ?? null,
        groups: [...root.querySelectorAll('svg[data-bars="capture"] [data-group]')].map((g) => g.getAttribute("data-group")), names: root.querySelector('svg[data-bars="capture"] [data-direct-labels]')?.textContent ?? "",
        cap: document.querySelector('[data-stat="cap_price"]')?.textContent ?? null, capFlat: document.querySelector('[data-stat="cap_flat"]')?.textContent ?? null,
        brand: !!document.querySelector('.brand-a[data-brand="a"][data-no-usage="1"] [data-capture]'), canvases: document.querySelectorAll("[data-chart] canvas").length };
    })()`);
    check(!!capT && capT.kind === "solar" && capT.inFirst && capT.charts === 1 && capT.tables === 1 && capT.rows === 14 && capT.keys >= 3 * 14,
      "the capture price is inside What did it earn?: one chart and one table, a row a hub or zone of ERCOT, its figures keyed", JSON.stringify(capT));
    check(!!capT && capT.chosen === "Hub average" && capT.l12 === capT.cap && capT.flat === capT.capFlat && capT.groups.at(-1) === "Last 12 months" && capT.groups.length >= 3 && /Capture price/.test(capT.names) && /Hub average/.test(capT.names),
      "the chosen hub's row reads the headline's capture price and hub average; the chart runs by year to the last twelve months, its two series named on it", JSON.stringify(capT));
    check(!!capT && capT.brand && capT.canvases === 0, "the page is on the brand (the wrapper, no usage count) and draws no chart of the chart library");
  }

  // 11: phone width
  for (const q of ["", "?ac=1500&bt=10&bd=0.5&bh=10&v=b"]) {
    await go(`/cost-of-power/seller${q}`, 390);
    s = await ev(STATE);
    check(s.clientW === 390 && s.scrollW <= s.clientW + 1, `390 px${q ? ", two scenarios" : ""}: the page does not scroll sideways`, `scroll width ${s.scrollW}, width ${s.clientW}`);
    check(s.bars.length === 8 && s.rows.length === 10, `390 px${q ? ", two scenarios" : ""}: the table and the chart are drawn`);
    await shot(q ? "seller-scenarios-compared-phone" : "seller-scenarios-default-phone", 390);
  }
} catch (e) {
  failed++;
  console.log(`FAIL the browser run stopped: ${e.message}`);
} finally {
  chrome.kill();
  await sleep(300);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the profile is in the temp directory */ }
}
console.log(failed ? `\n${failed} FAILED` : "\nall passed");
process.exit(failed ? 1 : 0);
