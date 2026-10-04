// Energy Research Warehouse (ERW) site: the proof that /battery/customer sends nothing (session 88).
//
//   npm run build && npm start                         (the site on http://localhost:3000)
//   node scripts/check-no-request.mjs [base-url]
//
// The page says: "Nothing you type is sent or stored." This drives a real browser (Chrome or Edge, headless, through
// its DevTools protocol; no package is installed for it) to the page, waits until the page has finished loading and
// gone quiet, then types a number into every field as a person would, and counts what the browser did while and
// after it typed:
//   1. network requests of any kind (fetch, XHR, beacon, image, prefetch, navigation), and WebSockets: there must be none;
//   2. the address: it must not change (nothing typed is put in it);
//   3. cookies, localStorage and sessionStorage: they must be as they were;
//   4. the result on the page: it must be the one lib/customerbattery.ts computes for the numbers typed, so the
//      arithmetic did run, in the browser, with no request.
// Exits 1 if any of the four fails. If no browser is found on the machine it says so and exits 0: nothing was proven,
// and the line says that plainly. On the workflow's runner (GITHUB_ACTIONS) a missing browser exits 1 instead, so a
// green step there always means the proof was made. The page is in review, so the browser first opens the internal view with
// INTERNAL_COSTS_TOKEN (from the environment, site/.env.local or ../.env), as scripts/check-routes.mjs does.
import { execFileSync, spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
function env(name) {
  if (process.env[name]) return process.env[name];
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z_]+)=(.*)$/);
      if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
    }
  }
  return undefined;
}
const { FIELDS, readAll, saving, usd } = await import("../lib/customerbattery.ts");
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const PAGE = "/battery/customer";
// what a person might type: a 500 kW peak, a 200 kW battery of four hours
const TYPED = { peakKw: "500", demandCharge: "18", peakRate: "0.22", offPeakRate: "0.09", batteryKw: "200", batteryKwh: "800", peakHours: "4", days: "22", roundTrip: "85" };

function browser() {
  const named = process.env.BROWSER_PATH || process.env.CHROME_PATH;
  if (named && fs.existsSync(named)) return named;
  const pf = [process.env["PROGRAMFILES(X86)"], process.env.PROGRAMFILES, process.env.LOCALAPPDATA].filter(Boolean);
  const fixed = [
    ...pf.flatMap((p) => [path.join(p, "Google", "Chrome", "Application", "chrome.exe"), path.join(p, "Microsoft", "Edge", "Application", "msedge.exe")]),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  ];
  for (const f of fixed) if (fs.existsSync(f)) return f;
  if (process.platform !== "win32") {
    for (const n of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"]) {
      try { return execFileSync("which", [n], { encoding: "utf-8" }).trim(); } catch { /* not this one */ }
    }
  }
  return null;
}

const exe = browser();
if (!exe) {
  // on the workflow's runner a missing browser is a failure: a green step there must mean the proof was made
  const ci = process.env.GITHUB_ACTIONS === "true";
  console.log(`check-no-request: ${ci ? "FAILED" : "NOT PROVEN on this machine"}: no Chrome or Edge was found (set BROWSER_PATH). ${PAGE} was not checked.`);
  process.exit(ci ? 1 : 0);
}
const token = env("INTERNAL_COSTS_TOKEN");
if (!token) {
  console.error(`check-no-request: FAILED: INTERNAL_COSTS_TOKEN is not set, so the page in review cannot be opened at ${base}`);
  process.exit(1);
}

const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-no-request-"));
const args = ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check",
  "--disable-background-networking", "--disable-component-update", "--disable-sync", "--disable-extensions", "--disable-gpu", "about:blank"];
if (process.platform === "linux") args.unshift("--no-sandbox");
const child = spawn(exe, args, { stdio: ["ignore", "ignore", "pipe"] });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let failed = [];
const done = async (code) => {
  try { child.kill(); } catch { /* already gone */ }
  await sleep(500);
  try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch { /* the browser still holds a file: the temp directory is left */ }
  process.exit(code);
};

try {
  const port = await new Promise((resolve, reject) => {
    let buf = "";
    const t = setTimeout(() => reject(new Error(`the browser did not open its DevTools port: ${buf.slice(-300)}`)), 30000);
    child.stderr.on("data", (d) => {
      buf += d.toString();
      const m = buf.match(/DevTools listening on ws:\/\/[^:]+:(\d+)\//);
      if (m) { clearTimeout(t); resolve(Number(m[1])); }
    });
    child.on("exit", (c) => { clearTimeout(t); reject(new Error(`the browser exited (${c}): ${buf.slice(-300)}`)); });
  });
  const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json();
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = () => reject(new Error("the DevTools socket did not open")); });
  let id = 0;
  const waiting = new Map();
  const events = [];
  let loads = 0;
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && waiting.has(d.id)) { const { resolve, reject } = waiting.get(d.id); waiting.delete(d.id); d.error ? reject(new Error(d.error.message)) : resolve(d.result); return; }
    if (d.method === "Page.loadEventFired") loads += 1;
    if (d.method === "Network.requestWillBeSent") events.push({ at: Date.now(), kind: d.params.type ?? "request", url: d.params.request.url });
    if (d.method === "Network.webSocketCreated") events.push({ at: Date.now(), kind: "WebSocket", url: d.params.url });
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => { id += 1; waiting.set(id, { resolve, reject }); ws.send(JSON.stringify({ id, method, params })); });
  const evaluate = async (expression) => {
    const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(`in the page: ${r.exceptionDetails.exception?.description ?? r.exceptionDetails.text}`);
    return r.result.value;
  };
  const go = async (url) => {
    const before = loads;
    await send("Page.navigate", { url });
    for (let i = 0; i < 300 && loads === before; i += 1) await sleep(100);
    if (loads === before) throw new Error(`${url} did not finish loading in 30 s`);
  };
  /** Wait until the browser has made no request for `ms`. */
  const quiet = async (ms, cap = 30000) => {
    const t0 = Date.now();
    for (;;) {
      const last = events.length ? events[events.length - 1].at : t0;
      if (Date.now() - Math.max(last, t0) >= ms) return;
      if (Date.now() - t0 > cap) throw new Error(`the page was still making requests after ${cap / 1000} s`);
      await sleep(100);
    }
  };
  await send("Network.enable");
  await send("Page.enable");
  await send("Runtime.enable");

  await go(`${base}/internal/unlock?token=${encodeURIComponent(token)}`);
  await go(`${base}${PAGE}`);
  await quiet(3000);
  const fields = await evaluate(`[...document.querySelectorAll('input[data-field]')].map((e) => e.dataset.field)`);
  const own = await evaluate(`!!document.querySelector('[data-own-numbers]')`);
  if (!own || JSON.stringify(fields) !== JSON.stringify(FIELDS.map((f) => f.key))) {
    throw new Error(`${PAGE} did not open as the calculator (fields ${JSON.stringify(fields)}): is the internal token this server's?`);
  }
  const state = `JSON.stringify({ href: location.href, cookie: document.cookie, local: Object.keys(localStorage).sort(), session: Object.keys(sessionStorage).sort() })`;
  const before = await evaluate(state);
  const waitingText = await evaluate(`document.querySelector('[data-result]')?.dataset.result ?? null`);
  const mark = events.length;
  const t0 = Date.now();

  for (const f of FIELDS) {
    await evaluate(`(() => { const e = document.querySelector('input[data-field="${f.key}"]'); e.focus(); e.select(); })()`);
    await send("Input.insertText", { text: TYPED[f.key] });  // the browser's own text input, as typing or pasting is
    await sleep(120);
  }
  await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
  await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
  await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await sleep(5000);  // long enough for a debounced or deferred send to show itself

  const sent = events.slice(mark);
  const after = await evaluate(state);
  const typed = await evaluate(`JSON.stringify(Object.fromEntries([...document.querySelectorAll('input[data-field]')].map((e) => [e.dataset.field, e.value])))`);
  const shown = await evaluate(`JSON.stringify(Object.fromEntries([...document.querySelectorAll('[data-result="summary"] [data-n]')].map((e) => [e.dataset.n, e.textContent])))`);
  const r = readAll(TYPED);
  const s = saving(r.x);
  const want = { month: usd(s.monthSaved), year: usd(s.yearSaved), demand: usd(s.demandSaved), energy: usd(s.energySaved) };

  console.log(`check-no-request: ${path.basename(exe)}, ${base}${PAGE}`);
  console.log(`  before typing: the result block read "${waitingText}"; ${mark} requests had loaded the page`);
  console.log(`  typed: ${typed}`);
  console.log(`  shown: ${shown}`);
  console.log(`  requests while typing and for ${((Date.now() - t0) / 1000).toFixed(1)} s after: ${sent.length}`);
  for (const e of sent) console.log(`    ${e.kind} ${e.url}`);
  if (sent.length) failed.push(`${sent.length} request(s) were made after typing began`);
  if (typed !== JSON.stringify(TYPED)) failed.push("the fields do not hold what was typed");
  if (shown !== JSON.stringify(want)) failed.push(`the page shows ${shown}, lib/customerbattery.ts computes ${JSON.stringify(want)}`);
  if (after !== before) failed.push(`the address, the cookies or the stored keys changed: before ${before}, after ${after}`);
  else console.log(`  address, cookies and stored keys unchanged: ${JSON.parse(after).href}, ${JSON.parse(after).local.length} localStorage keys, ${JSON.parse(after).session.length} sessionStorage keys`);
  ws.close();
} catch (e) {
  failed.push(e.message);
}
if (failed.length) {
  for (const f of failed) console.error(`check-no-request: FAILED: ${f}`);
  await done(1);
}
console.log("check-no-request: passed: typing into the page made no request and stored nothing");
await done(0);
