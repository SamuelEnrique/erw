// Energy Research Warehouse (ERW) site, session 2241 (chain 156): the deals pages as a reviewer sees them, headless.
//
//   npm run build && npx next start -p 3230          (the site on http://localhost:3230)
//   node scripts/shots-2241.mjs [base-url] [--out <dir>]
//
// Opens the internal view through the form at /internal/open (browser.mjs's unlockForm; the token read from the
// environment or site/.env.local, never printed, never in an address: test 301), then captures the deals table
// (/deals), the comparables (/deals?view=comparables), the AI-power view (/deals?view=ai) and the charts
// (/deals?view=charts) at 390 and 1280 CSS px wide, full page, to <out>/<name>-<width>.png (default runs/s2241/shots/).
// An SVG title is the browser's own hover tip and is not drawn in an image, so for each chart the title of its first
// mark is read and listed in shots.txt beside the images. Adapted from session 2226's shots-2226.mjs.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import { unlockForm } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const argv = process.argv.slice(2);
const base = (argv.find((a) => a.startsWith("http")) || "http://localhost:3230").replace(/\/$/, "");
const opt = (name) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : undefined; };
const outDir = opt("--out") || path.join(root, "runs", "s2241", "shots");
const PORT = 9241;
const MAX_HEIGHT = 5000;
const WIDTHS = [390, 1280];

function token() {
  if (process.env.INTERNAL_COSTS_TOKEN) return process.env.INTERNAL_COSTS_TOKEN.trim();
  for (const p of [path.join(here, "..", ".env.local"), path.join(root, "..", "erw", "site", ".env.local")]) {
    if (!fs.existsSync(p)) continue;
    const m = fs.readFileSync(p, "utf8").match(/^INTERNAL_COSTS_TOKEN=(.+)$/m);
    if (m) return m[1].trim().replace(/^"|"$/g, "");
  }
  throw new Error("INTERNAL_COSTS_TOKEN is not in the environment or site/.env.local");
}

function pages() {
  return [["deals-table", "/deals"], ["deals-comparables", "/deals?view=comparables"], ["deals-ai", "/deals?view=ai"], ["deals-charts", "/deals?view=charts"]];
}

function chromePath() {
  const c = [process.env.CHROME_PATH, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"].filter(Boolean);
  const p = c.find((x) => fs.existsSync(x));
  if (!p) throw new Error("no Chrome or Edge found; set CHROME_PATH");
  return p;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const withTimeout = (ms, p, what) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(`timed out: ${what}`)), ms))]);

async function cdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0;
  const pending = new Map();
  const listeners = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const { res, rej } = pending.get(m.id); pending.delete(m.id); m.error ? rej(new Error(m.error.message)) : res(m.result); }
    else if (m.method) listeners.forEach((f) => f(m));
  };
  return {
    send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }),
    once: (method) => new Promise((res) => listeners.push((m) => m.method === method && res(m.params))),
    close: () => ws.close(),
  };
}

async function goto(page, url, what) {
  const loaded = page.once("Page.loadEventFired");
  const nav = await page.send("Page.navigate", { url });
  if (nav.errorText) throw new Error(`${what}: ${nav.errorText}`);
  await withTimeout(45000, loaded, `load ${what}`);
}

async function viewport(page, width, height = 900) {
  await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 700 });
}

async function capture(page, width, file, written, note) {
  const { cssContentSize } = await page.send("Page.getLayoutMetrics");
  const full = Math.ceil(cssContentSize.height);
  const height = Math.min(Math.max(full, 600), MAX_HEIGHT);
  await viewport(page, width, height);
  await sleep(700);
  const shot = await withTimeout(45000, page.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false, clip: { x: 0, y: 0, width, height, scale: 1 } }), `capture ${file}`);
  fs.writeFileSync(file, Buffer.from(shot.data, "base64"));
  written.push(`${path.basename(file)} (${width} x ${height} CSS px${full > height ? `, page is ${full} px, cut` : ""}) ${note}`);
}

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  const profile = path.join(outDir, "..", ".profile");
  const chrome = spawn(chromePath(), ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--hide-scrollbars", "--disable-gpu", "about:blank"]);
  let version;
  for (let i = 0; i < 50 && !version; i++) {
    await sleep(200);
    version = await fetch(`http://127.0.0.1:${PORT}/json/version`).then((r) => r.json()).catch(() => undefined);
  }
  if (!version) throw new Error("headless browser did not start");
  const target = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" }).then((r) => r.json());
  const page = await cdp(target.webSocketDebuggerUrl);
  await page.send("Page.enable");
  const written = [];
  try {
    await viewport(page, 1280);
    // session 2947 (chain 157): the form, not a GET with the token in its address (test 301)
    const evaluate = async (expression) => (await page.send("Runtime.evaluate", { expression, returnByValue: true })).result.value;
    await unlockForm({ go: (url) => goto(page, url, url.replace(base, "")), evaluate, sleep }, base, token());
    const cookies = await page.send("Network.getCookies", { urls: [base] });
    if (!cookies.cookies.some((c) => c.name === "erw_internal")) throw new Error("the internal cookie was not set: is INTERNAL_COSTS_TOKEN the server's?");
    written.push("internal view opened (erw_internal and erw_view set for this browser)");
    for (const [name, route] of pages()) {
      for (const width of WIDTHS) {
        await viewport(page, width);
        await goto(page, base + route, route);
        await sleep(1500);
        await capture(page, width, path.join(outDir, `${name}-${width}.png`), written, route);
      }
    }
    // each chart's first mark: its hover title and its key, as the page gives them
    await viewport(page, 1280);
    await goto(page, base + "/deals?view=charts", "/deals?view=charts");
    await sleep(1500);
    const marks = await page.send("Runtime.evaluate", { expression: "JSON.stringify([...document.querySelectorAll('svg[data-chart]')].map((s) => { const m = s.querySelector('[data-check]'); return { chart: s.dataset.chart, key: m ? m.dataset.check : '', value: m ? m.dataset.value : '', title: m && m.querySelector('title') ? m.querySelector('title').textContent : '' }; }))", returnByValue: true });
    for (const m of JSON.parse(marks.result.value)) written.push(`hover of chart ${m.chart}: ${m.title || "no mark (the chart is empty)"} [${m.key} = ${m.value}]`);
  } finally {
    page.close();
    chrome.kill();
  }
  fs.writeFileSync(path.join(outDir, "shots.txt"), written.join("\n") + "\n");
  console.log(written.join("\n"));
}

main().catch((e) => { console.error(`shots-2241 FAILED: ${e.message}`); process.exit(1); });
