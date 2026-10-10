// Energy Research Warehouse (ERW) site, session 178: the face of /cost-of-power/battery in the internal view, in a
// headless browser, at desktop width (1280) and phone width (390).
//
//   npm run build && npm start
//   node scripts/check-battery-face.mjs [base-url] [screenshot-dir]
//
// The page is in review, so scripts/test-battery-stack.mjs (a visitor, written when the page was live) no longer reaches
// it. This script unlocks the internal view first (/internal/unlock with INTERNAL_COSTS_TOKEN from the environment or
// site/.env.local; the token is never printed) and asserts:
//   1. the summary, the three headline numbers, the chart and the income table are drawn;
//   2. session 178's one line beside ERCOT's real awards: present on ERCOT with three checked numbers that follow the
//      duration and the strategy, absent on CAISO;
//   3. the link to the step-by-step note beside the Method link, and the three downloads, each answering 200;
//   4. at 390 px the page does not scroll sideways, on ERCOT and on CAISO.
// Prints one line per assertion; exits 1 if any fails.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const shots = process.argv[3];
const PORT = 9378;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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

const tok = token();
if (!tok) { console.log("check-battery-face FAILED: INTERNAL_COSTS_TOKEN is not set here, so the page in review cannot be opened"); process.exit(1); }
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-battery-face-"));
const chrome = spawn(chromePath(), ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--hide-scrollbars", "--disable-gpu", "about:blank"]);
try {
  let version;
  for (let i = 0; i < 50 && !version; i++) { await sleep(200); version = await fetch(`http://127.0.0.1:${PORT}/json/version`).then((r) => r.json()).catch(() => undefined); }
  if (!version) throw new Error("headless browser did not start");
  const target = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" }).then((r) => r.json());
  const page = await cdp(target.webSocketDebuggerUrl);
  await page.send("Page.enable");
  const ev = async (expression) => {
    const r = await page.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(`${r.exceptionDetails.text}: ${expression.slice(0, 80)}`);
    return r.result.value;
  };
  const go = async (route, width = 1280) => {
    await page.send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
    const loaded = new Promise((res) => page.on((m) => m.method === "Page.loadEventFired" && res()));
    const nav = await page.send("Page.navigate", { url: base + route });
    if (nav.errorText) throw new Error(`${route.split("?")[0]}: ${nav.errorText}`);
    await Promise.race([loaded, sleep(30000)]);
    await sleep(1500);
  };
  const shot = async (name, width) => {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    const { cssContentSize } = await page.send("Page.getLayoutMetrics");
    const height = Math.min(Math.ceil(cssContentSize.height), 9000);
    await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 600 });
    await sleep(500);
    const s = await page.send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height, scale: 1 } });
    fs.writeFileSync(path.join(shots, `${name}.png`), Buffer.from(s.data, "base64"));
  };
  const STATE = `(() => {
    const line = document.querySelector("[data-awards-beside]");
    const nums = line ? [...line.querySelectorAll("[data-check]")].map((e) => ({ check: e.getAttribute("data-check"), raw: Number(e.getAttribute("data-raw")), text: e.textContent })) : [];
    return {
      inReview: !!document.querySelector("[data-in-review]"),
      summary: document.querySelector("[data-summary]")?.textContent ?? "",
      tables: document.querySelectorAll("table").length, chart: document.querySelector('svg[role="img"]')?.outerHTML.length ?? 0,
      line: line ? line.textContent.replace(/\\s+/g, " ").trim() : null, lineCase: line?.getAttribute("data-awards-beside") ?? null, nums,
      links: [...document.querySelectorAll("a")].map((a) => ({ href: a.getAttribute("href"), text: a.textContent, download: a.hasAttribute("download") })),
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    };
  })()`;

  await go(`/internal/unlock?token=${encodeURIComponent(tok)}`);
  for (const [q, want] of [["grid=ercot&dur=4&strat=foresight", "foresight_4h"], ["grid=ercot&dur=8&strat=dayahead", "dayahead_8h"]]) {
    await go(`/cost-of-power/battery?${q}`);
    const s = await ev(STATE);
    check(!s.inReview && s.summary.includes("battery in ERCOT") && s.tables >= 1 && s.chart > 500, `${q}: the page opens in the internal view with its summary, chart and income table`);
    check(s.lineCase === want && s.nums.length === 3, `${q}: one line beside ERCOT's real awards, three checked numbers`, s.line ?? "no line");
    const [m, f, r] = s.nums;
    check(s.nums.length === 3 && m.check === `bsa|${want}|model` && f.check === `bsa|${want}|fleet` && r.check === `bsa|${want}|ratio`, `${q}: the keys are bsa|${want}|model, fleet and ratio`);
    check(s.nums.length === 3 && m.raw > 0 && f.raw > 0 && Math.abs(r.raw - m.raw / f.raw) < 0.02, `${q}: the ratio is the model over the fleet`, s.nums.map((n) => n.text).join(", "));
    check(s.nums.every((n) => /^\d+\.\d\d$/.test(n.text)),`${q}: each number is written with two decimals`);
    if (want === "foresight_4h") {
      const note = s.links.find((a) => a.text === "Every number, step by step");
      check(note && (note.href === "/data/methods/battery_earns_algorithm"), "the lead links the step-by-step note beside the Method link");
      const files = s.links.filter((a) => a.download).map((a) => a.href);
      check(files.length === 3 && files.every((h) => h.startsWith("/battery/erw_2026_battery_")), "the source line offers three downloads", files.join(", "));
      for (const h of [...files, "/data/methods/battery_earns_algorithm"]) {
        const res = await fetch(base + h, { headers: { Cookie: await ev("document.cookie") } }).catch(() => null);
        check(res && res.status === 200, `${h} answers 200`, res ? `${res.status}, ${(await res.arrayBuffer()).byteLength.toLocaleString("en-US")} bytes` : "no answer");
      }
      await shot("battery-ercot-4h-desktop", 1280);
    }
  }
  await go("/cost-of-power/battery?grid=caiso&dur=4&strat=foresight");
  const c = await ev(STATE);
  check(!c.inReview && c.summary.includes("battery in CAISO") && c.line === null, "CAISO: the page opens and carries no line beside ERCOT's awards");
  for (const [q, name] of [["grid=ercot&dur=4&strat=foresight", "battery-ercot-4h-phone"], ["grid=caiso&dur=4&strat=foresight", "battery-caiso-4h-phone"]]) {
    await go(`/cost-of-power/battery?${q}`, 390);
    const s = await ev(STATE);
    check(s.clientW === 390 && s.scrollW <= s.clientW + 1, `${q} at 390 px: the page does not scroll sideways`, `scroll width ${s.scrollW}, width ${s.clientW}`);
    if (q.startsWith("grid=ercot")) check(s.line !== null, `${q} at 390 px: the line is on the page`, s.line ?? "");
    await shot(name, 390);
  }
} finally {
  chrome.kill();
  await sleep(300);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the profile is in the temp directory */ }
}
console.log(failed ? `\n${failed} FAILED` : "\nall passed");
process.exit(failed ? 1 : 0);
