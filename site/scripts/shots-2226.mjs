// Energy Research Warehouse (ERW) site, session 2226 (chain 152): the chats as a reviewer sees them, in a headless browser.
//
//   npm run build && npx next start -p 3226          (the site on http://localhost:3226)
//   node scripts/shots-2226.mjs [base-url] [--out <dir>] [--ask "question"] [--board "question"]
//
// Opens the internal view through the form at /internal/open (browser.mjs's unlockForm; the token read from the
// environment or site/.env.local, never printed, never in an address: session 2947, test 301), then captures /ask, each grid's chat (/ask?grid=<slug>, docs/grids/grids.json) and the
// board (/board, "Ask the board") at 390 and 1280 CSS px wide, full page, to <out>/<name>-<width>.png (default
// runs/s2226/shots/ in the repository). With --ask, types the question into /ask at each width, submits it (one model call
// on the server a width), waits for the answer, moves the pointer onto the chart under it and captures the answer with
// the hover's values (<out>/ask-chart-hover-<width>.png). With --board, the same on the board's Ask at 1280
// (<out>/board-ask-answer-1280.png). Built on scripts/screenshots.mjs (its Chrome, its DevTools protocol, no other
// dependency); nothing is written but the images and nothing leaves the machine but the requests to the local site.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import { unlockForm } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const argv = process.argv.slice(2);
const base = (argv.find((a) => a.startsWith("http")) || "http://localhost:3226").replace(/\/$/, "");
const opt = (name) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : undefined; };
const outDir = opt("--out") || path.join(root, "runs", "s2226", "shots");
const askQuestion = opt("--ask");
const boardQuestion = opt("--board");
const PORT = 9226;
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
  const grids = JSON.parse(fs.readFileSync(path.join(root, "docs", "grids", "grids.json"), "utf8")).grids.map((g) => g.slug);
  return [["ask", "/ask"], ...grids.map((s) => [`ask-${s}`, `/ask?grid=${s}`]), ["board", "/board"]];
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

async function askAndHover(page, width, question, written, route = "/ask", name = "ask-chart-hover") {
  await viewport(page, width);
  await goto(page, base + route, route);
  await sleep(1200);
  await page.send("Runtime.evaluate", { expression: `(() => { const i = document.getElementById("q") || document.querySelector("input[type=text], textarea"); const set = Object.getOwnPropertyDescriptor(i instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, "value").set; set.call(i, ${JSON.stringify(question)}); i.dispatchEvent(new Event("input", { bubbles: true })); setTimeout(() => i.form.requestSubmit(), 100); })()` });
  let done = false;
  for (let i = 0; i < 180 && !done; i++) {
    await sleep(1000);
    const r = await page.send("Runtime.evaluate", { expression: "(() => { const s = document.querySelector('section[aria-live]'); return !!s && s.textContent.trim().length > 40 && !document.querySelector('[data-progress]'); })()", returnByValue: true });
    done = r.result.value === true;
  }
  if (!done) throw new Error(`no answer on ${route} within 180 s`);
  await sleep(1500);
  // the chart under the answer: the pointer onto its middle, so the hover's values draw
  const box = await page.send("Runtime.evaluate", { expression: "(() => { const s = document.querySelector('section[aria-live]'); const svg = s && s.querySelector('svg'); if (!svg) return null; const r = svg.getBoundingClientRect(); return { x: r.left + r.width * 0.6, y: r.top + r.height * 0.5, w: r.width, h: r.height, top: r.top + window.scrollY }; })()", returnByValue: true });
  const b = box.result.value;
  let hovered = "no chart under the answer";
  if (b) {
    await page.send("Runtime.evaluate", { expression: `window.scrollTo(0, ${Math.max(0, Math.round(b.top - 200))})` });
    await sleep(300);
    const again = await page.send("Runtime.evaluate", { expression: "(() => { const svg = document.querySelector('section[aria-live] svg'); const r = svg.getBoundingClientRect(); return { x: r.left + r.width * 0.6, y: r.top + r.height * 0.5 }; })()", returnByValue: true });
    const { x, y } = again.result.value;
    await page.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: Math.round(x), y: Math.round(y) });
    await sleep(400);
    await page.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: Math.round(x) + 2, y: Math.round(y) });
    await sleep(600);
    const tip = await page.send("Runtime.evaluate", { expression: "(() => { const s = document.querySelector('section[aria-live]'); const t = s.querySelector('[role=tooltip], .recharts-tooltip-wrapper, [data-tooltip], title'); return t ? t.textContent.trim().slice(0, 120) : ''; })()", returnByValue: true });
    hovered = `chart ${Math.round(b.w)} x ${Math.round(b.h)} px, hovered at 60 percent of its width${tip.result.value ? `; tooltip: ${tip.result.value}` : ""}`;
  }
  // the viewport as it stands (the hover is a state of the pointer: a full-page relayout would lose it)
  const shot = await withTimeout(45000, page.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false }), "hover capture");
  const file = path.join(outDir, `${name}-${width}.png`);
  fs.writeFileSync(file, Buffer.from(shot.data, "base64"));
  written.push(`${path.basename(file)} (${width} px wide, the viewport) ${route}, asked: ${question}; ${hovered}`);
  const answer = await page.send("Runtime.evaluate", { expression: "(() => { const s = document.querySelector('section[aria-live]'); return s ? s.innerText.slice(0, 600) : ''; })()", returnByValue: true });
  written.push(`   answer: ${answer.result.value.replace(/\s+/g, " ").slice(0, 500)}`);
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
    if (askQuestion) for (const width of WIDTHS) await askAndHover(page, width, askQuestion, written);
    if (boardQuestion) await askAndHover(page, 1280, boardQuestion, written, "/board", "board-ask-answer");
  } finally {
    page.close();
    chrome.kill();
  }
  fs.writeFileSync(path.join(outDir, "shots.txt"), written.join("\n") + "\n");
  console.log(written.join("\n"));
}

main().catch((e) => { console.error(`shots-2226 FAILED: ${e.message}`); process.exit(1); });
