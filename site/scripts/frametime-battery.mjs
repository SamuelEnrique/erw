// Energy Research Warehouse (ERW) site, session 50: the battery game's frame time, in a visible browser window.
//
//   npm run build && npm start                      (the site on http://localhost:3000)
//   node scripts/frametime-battery.mjs [base-url] [--width 1280] [--seconds 20] [--headless --shot file.png]
//
// Starts Chrome with a visible window (not headless; its own profile in a temporary folder) and the DevTools protocol,
// opens /play/battery, skips the tutorial, picks Easy (the busiest drawing: the forecast band), starts today's level,
// holds Charge for a few seconds, and records every requestAnimationFrame interval for --seconds while the game runs.
// Prints the window's visibility (frames only run in a visible window), the frame count and the mean, median, 95th
// and 99th percentile and the longest frame, in ms; with --width 380 it also checks that nothing on the page is wider
// than the window. Uses Node's built-in WebSocket; no other dependency. Exits 1 if the window was not visible.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const argv = process.argv.slice(2);
const flag = (f, d) => (argv.includes(f) ? argv[argv.indexOf(f) + 1] : d);
const base = (argv[0] && !argv[0].startsWith("--") ? argv[0] : "http://localhost:3000").replace(/\/$/, "");
const WIDTH = Number(flag("--width", "1280"));
const SECONDS = Number(flag("--seconds", "20"));
const SHOT = flag("--shot");  // a PNG of the page mid-game (with --headless, for the layout at a phone width)
const HEADLESS = argv.includes("--headless");
const PORT = 9334;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const errors = [];  // the page's exceptions and console errors

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
  const pending = new Map();
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails?.exception?.description?.split(String.fromCharCode(10))[0] ?? m.params.exceptionDetails?.text);
    if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") errors.push(m.params.args.map((a) => a.value ?? a.description).join(" ").slice(0, 200));
    if (m.id && pending.has(m.id)) {
      const { res, rej } = pending.get(m.id);
      pending.delete(m.id);
      m.error ? rej(new Error(m.error.message)) : res(m.result);
    }
  };
  return {
    send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }),
    close: () => ws.close(),
  };
}

const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-frametime-"));
const chrome = spawn(chromePath(), [
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check", "--new-window",
  `--window-size=${Math.max(WIDTH, 500)},900`, "--window-position=0,0", ...(HEADLESS ? ["--headless=new"] : []), "about:blank",
], { stdio: "ignore" });
let code = 0;
try {
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    await sleep(200);
    try { target = (await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()).find((t) => t.type === "page"); } catch { /* not up yet */ }
  }
  if (!target) throw new Error("Chrome did not start");
  const c = await cdp(target.webSocketDebuggerUrl);
  await c.send("Page.enable");
  await c.send("Runtime.enable");
  await c.send("Page.bringToFront");
  if (WIDTH < 500) await c.send("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: 800, deviceScaleFactor: 2, mobile: true });
  // every frame from the page's load: [time, interval]
  await c.send("Page.addScriptToEvaluateOnNewDocument", { source: "window.__ft = []; (() => { let last = performance.now(); const f = (now) => { window.__ft.push([now, now - last]); last = now; requestAnimationFrame(f); }; requestAnimationFrame(f); })();" });
  await c.send("Page.navigate", { url: `${base}/play/battery` });
  await sleep(6000);
  const run = async (expr) => (await c.send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result.value;
  const vis = await run("document.visibilityState");
  const probe = await run("Promise.race([new Promise((r) => requestAnimationFrame(() => r('raf ok'))), new Promise((r) => setTimeout(() => r('raf did not fire in 2 s'), 2000))])");
  console.log(`animation-frame probe: ${probe}`);
  const overflow = await run(`(() => { const w = document.documentElement.clientWidth; const wide = [...document.querySelectorAll("body *")].filter((e) => e.getBoundingClientRect().right > w + 1 && getComputedStyle(e).position !== "fixed").map((e) => e.tagName + "." + (e.className && e.className.baseVal === undefined ? String(e.className).split(" ")[0] : "")); return { clientWidth: w, scrollWidth: document.documentElement.scrollWidth, wider: wide.slice(0, 8) }; })()`);
  const click = (t) => run(`(() => { const b = [...document.querySelectorAll("button")].find((x) => x.textContent.trim().startsWith(${JSON.stringify(t)})); if (b) b.click(); return !!b; })()`);
  await click("Skip");
  await sleep(300);
  await click("Easy");
  await sleep(500);
  let started = false;
  for (let i = 0; i < 20 && !started; i++) {
    await click("Play 20");
    await sleep(500);
    started = await run(`!![...document.querySelectorAll("button")].find((x) => x.textContent.includes("Hold to charge"))`);
  }
  if (!started) throw new Error("the game did not start");
  const t0 = await run("performance.now()");
  // hold Charge for three seconds, by the keyboard (the game listens for C)
  await c.send("Input.dispatchKeyEvent", { type: "keyDown", code: "KeyC", key: "c" });
  await sleep(3000);
  await c.send("Input.dispatchKeyEvent", { type: "keyUp", code: "KeyC", key: "c" });
  await sleep(SECONDS * 1000 - 3000);
  if (SHOT) {
    const png = await c.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    fs.writeFileSync(SHOT, Buffer.from(png.data, "base64"));
    console.log(`screenshot: ${SHOT}`);
  }
  const r = await run(`(() => { const d = window.__ft.filter(([t]) => t > ${t0}).map(([, x]) => x).sort((a, b) => a - b); const q = (p) => d[Math.min(d.length - 1, Math.floor(p * d.length))]; const clock = [...document.querySelectorAll("span[aria-live=polite]")].map((s) => s.textContent).join(" "); const replay = document.body.innerText.includes("Replay: the perfect battery") ? (document.body.innerText.match(/Every switch of the perfect plan [(]([0-9]+)[)]/) || [])[1] + " switches" : "none"; return d.length ? { replay, frames: d.length, mean: d.reduce((a, b) => a + b, 0) / d.length, p50: q(0.5), p95: q(0.95), p99: q(0.99), max: d.at(-1), over33: d.filter((x) => x > 33.4).length, over50: d.filter((x) => x > 50).length, clock } : { frames: 0, clock }; })()`);
  const f = (v) => (typeof v === "number" ? v.toFixed(2) : v);
  console.log(`window ${WIDTH} px, visibility ${vis}; ${r.frames} frames in ${SECONDS} s: mean ${f(r.mean)} ms, median ${f(r.p50)}, p95 ${f(r.p95)}, p99 ${f(r.p99)}, longest ${f(r.max)}, over 33.4 ms ${r.over33}, over 50 ms ${r.over50}; the game's clock after ${SECONDS} s: ${r.clock}; the replay after the game: ${r.replay}`);
  console.log(`layout at ${overflow.clientWidth} px: scrollWidth ${overflow.scrollWidth}${overflow.wider.length ? `; wider than the window: ${overflow.wider.join(", ")}` : "; nothing wider than the window"}`);
  console.log(`page errors: ${errors.length ? errors.join(" | ") : "none"}`);
  if (errors.length) code = 1;
  if (!HEADLESS && (vis !== "visible" || !r.frames)) code = 1;
  c.close();
} catch (e) {
  console.error(`frametime FAILED: ${e.message}`);
  code = 1;
} finally {
  chrome.kill();
  await sleep(500);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* Chrome may still hold a file */ }
}
process.exit(code);
