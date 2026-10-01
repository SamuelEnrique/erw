// Energy Research Warehouse (ERW) site: full-page screenshots of every page, in a headless browser.
//
//   npm run build && npm start            (in another terminal: the site on http://localhost:3000)
//   node scripts/screenshots.mjs [base-url] [--only name,name] [--ask "question"]
//
// Starts headless Chrome (CHROME_PATH, or the usual Windows, macOS and Linux locations) with the
// DevTools protocol, loads each page at desktop width (1280) and phone width (390), waits for the
// charts to draw, and writes screenshots/<name>-desktop.png and screenshots/<name>-mobile.png.
// --only captures the named pages. --ask also types the question into /ask, submits it (one
// real model call, on the server), waits for the answer and captures ask-answer-desktop.png.
// Uses Node's built-in WebSocket (Node 22 or later); no other dependency.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const flag = (f) => (argv.includes(f) ? argv[argv.indexOf(f) + 1] : undefined);
const base = argv[0] && !argv[0].startsWith("--") ? argv[0] : "http://localhost:3000";
const only = flag("--only")?.split(",");
const askQuestion = flag("--ask");
const outDir = path.join(here, "..", "screenshots");
const PORT = 9333;
const MAX_HEIGHT = 12000; // CSS px; taller pages (the data standard) are cut at this height, and the list says so

const PAGES = [
  ["home", "/"],
  ["play-battery", "/play/battery"],  // session 56: the levels grouped by grid
  ["board", "/board"],
  ["emissions", "/emissions"],
  ["storage", "/storage"],
  ["prices", "/prices"],
  ["prices-entity", "/prices/ercot%3AHB_HUBAVG"],
  ["digest", "/digest"],
  ["digest-date", "/digest/2026-09-25"],
  ["data", "/data"],
  ["data-standard", "/data/standard"],
  ["data-method", "/data/methods/ercot_peak_premium"],
  ["explorer-ercot-peak-premium", "/explorer/ercot-peak-premium"],
  ["about", "/about"],
  ["ask", "/ask"],
  ["deals", "/deals"],
  ["grid", "/grid"],
  ["map", "/map"],
  ["datacenters", "/datacenters"],
  ["roundup", "/roundup"],
  // session 18
  ["mix", "/mix?ba=erco&state=TX"],
  ["curtailment", "/curtailment"],
  ["consumption", "/consumption"],
  // session 19
  ["markets", "/markets"],
  ["subscribe", "/subscribe"],
  // session 21
  ["terms", "/terms"],
  // session 23
  ["roundup-week", "/roundup/2026-W39"],
  ["digest-weekend", "/digest/2026-10-03"],
  ["analysis", "/analysis"],
  ["analysis-week", "/analysis/2026-W39"],
  // session 24
  ["policy", "/policy"],
  // session 26
  // the row first: loading /companies#... right after /companies is a same-document jump, with no load event
  ["companies-row", "/companies#co-fervo-energy"],
  ["companies", "/companies"],
];
const WIDTHS = [
  ["desktop", 1280, 1],
  ["mobile", 390, 1],
];

function chromePath() {
  const c = [
    process.env.CHROME_PATH,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
  ].filter(Boolean);
  const p = c.find((x) => fs.existsSync(x));
  if (!p) throw new Error("no Chrome or Edge found; set CHROME_PATH");
  return p;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const withTimeout = (ms, p, what) =>
  Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(`timed out: ${what}`)), ms))]);

async function cdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => {
    ws.onopen = res;
    ws.onerror = rej;
  });
  let id = 0;
  const pending = new Map();
  const listeners = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { res, rej } = pending.get(m.id);
      pending.delete(m.id);
      m.error ? rej(new Error(m.error.message)) : res(m.result);
    } else if (m.method) listeners.forEach((f) => f(m));
  };
  return {
    send: (method, params = {}) =>
      new Promise((res, rej) => {
        const i = ++id;
        pending.set(i, { res, rej });
        ws.send(JSON.stringify({ id: i, method, params }));
      }),
    once: (method) => new Promise((res) => listeners.push((m) => m.method === method && res(m.params))),
    close: () => ws.close(),
  };
}

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  const profile = path.join(here, "..", ".screenshot-profile");
  const chrome = spawn(chromePath(), [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${profile}`,
    "--no-first-run",
    "--hide-scrollbars",
    "--disable-gpu", // session 21: without it the capture hung on this machine (every page timed out)
    "about:blank",
  ]);
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
    for (const [name, route] of PAGES.filter(([n]) => !only || only.includes(n))) {
      for (const [label, width, scale] of WIDTHS) {
        await page.send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: scale, mobile: label === "mobile" });
        if (route.includes("#")) {
          // session 26: loading a URL with a fragment over the same page (desktop, then mobile) is a same-document jump
          // that fires no load event; start from a blank page so the fragment's page loads fully
          const blank = page.once("Page.loadEventFired");
          await page.send("Page.navigate", { url: "about:blank" });
          await withTimeout(30000, blank, "load about:blank");
        }
        const loaded = page.once("Page.loadEventFired");
        const nav = await page.send("Page.navigate", { url: base + route });
        if (nav.errorText) throw new Error(`${route}: ${nav.errorText}`);
        await withTimeout(30000, loaded, `load ${route}`);
        await sleep(1500); // client charts draw after hydration
        const { cssContentSize } = await page.send("Page.getLayoutMetrics");
        const full = Math.ceil(cssContentSize.height);
        const height = Math.min(full, MAX_HEIGHT);
        // Session 16: make the viewport as tall as the capture first. captureBeyondViewport
        // re-lays the page out during the capture, which drew the /map canvas squashed.
        await page.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: scale, mobile: label === "mobile" });
        await sleep(800);
        const shot = await withTimeout(30000, page.send("Page.captureScreenshot", {
          format: "png",
          captureBeyondViewport: false,
          clip: { x: 0, y: 0, width, height, scale: 1 },
        }), `${route} at ${width}px`);
        const file = path.join(outDir, `${name}-${label}.png`);
        fs.writeFileSync(file, Buffer.from(shot.data, "base64"));
        written.push(`${path.basename(file)} (${width} x ${height} CSS px${full > height ? `, page is ${full} px, cut` : ""}) ${route}`);
      }
    }
    if (askQuestion) {
      await page.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
      const loaded = page.once("Page.loadEventFired");
      await page.send("Page.navigate", { url: base + "/ask" });
      await withTimeout(30000, loaded, "load /ask");
      await sleep(1000);
      // set the input the way React sees it, then submit the form
      await page.send("Runtime.evaluate", { expression: `(() => { const i = document.getElementById("q"); const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set; set.call(i, ${JSON.stringify(askQuestion)}); i.dispatchEvent(new Event("input", { bubbles: true })); setTimeout(() => i.form.requestSubmit(), 100); })()` });
      let done = false;
      for (let i = 0; i < 180 && !done; i++) {
        await sleep(1000);
        const r = await page.send("Runtime.evaluate", { expression: "!!document.querySelector('section[aria-live]') || !!document.querySelector('[role=status]')", returnByValue: true });
        done = r.result.value === true;
      }
      if (!done) throw new Error("no answer on /ask within 180 s");
      await sleep(500);
      const { cssContentSize } = await page.send("Page.getLayoutMetrics");
      const height = Math.min(Math.ceil(cssContentSize.height), MAX_HEIGHT);
      const shot = await withTimeout(30000, page.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: 1280, height, scale: 1 } }), "ask answer");
      fs.writeFileSync(path.join(outDir, "ask-answer-desktop.png"), Buffer.from(shot.data, "base64"));
      written.push(`ask-answer-desktop.png (1280 x ${height} CSS px) /ask, after asking: ${askQuestion}`);
    }
  } finally {
    page.close();
    chrome.kill();
  }
  console.log(written.join("\n"));
}

main().catch((e) => {
  console.error(`screenshots FAILED: ${e.message}`);
  process.exit(1);
});
