// Energy Research Warehouse (ERW) site: the browser test of /network (session 68).
//
//   npm run build && npm start
//   node scripts/test-network.mjs [base-url] [screenshot-dir]
//
// Drives a headless Chrome or Edge over the DevTools protocol (software WebGL), in a fresh profile. Asserts: the
// network draws and fills its frame; each of the four Watch buttons sets its view, opens the grid it is about (the
// stories and California's evening) and plays; clicking a grid (here, choosing it) opens the panel beside the network
// with its figures, and Escape and the close button close it; the Batteries switch is a real switch, off by default, and
// California's evening turns it on; the Watch buttons, Play, the switch and the close button are real buttons. Prints one
// line per assertion; exits 1 if any fails.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const shots = process.argv[3];
const PORT = 9348;
function chromePath() {
  const c = [process.env.CHROME_PATH, "C:/Program Files/Google/Chrome/Application/chrome.exe", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium"].filter(Boolean);
  const p = c.find((x) => fs.existsSync(x));
  if (!p) throw new Error("no Chrome or Edge found; set CHROME_PATH");
  return p;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
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
  return { send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }),
    on: (f) => listeners.push(f), close: () => ws.close() };
}
let failed = 0;
const check = (ok, what, detail = "") => { if (!ok) failed++; console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };

const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-network-test-"));
const chrome = spawn(chromePath(), ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--hide-scrollbars",
  "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "about:blank"]);
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
  const shot = async (name, width = 1280) => {
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    const s = await page.send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width, height: 1100, scale: 1 } });
    fs.writeFileSync(path.join(shots, `${name}.png`), Buffer.from(s.data, "base64"));
  };
  await page.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 1100, deviceScaleFactor: 1, mobile: false });
  const loaded = new Promise((res) => page.on((m) => m.method === "Page.loadEventFired" && res()));
  await page.send("Page.navigate", { url: `${base}/network` });
  await Promise.race([loaded, sleep(30000)]);
  await sleep(6000);
  const first = await ev(`(() => { const b = document.querySelector('[aria-label^="A 3D network"]'); const c = b ? b.querySelector("canvas") : null; return { canvas: !!c, w: c ? c.width : 0, h: c ? c.height : 0, bw: b ? b.clientWidth : 0, bh: b ? b.clientHeight : 0, view: document.querySelector("[data-network-view]")?.getAttribute("data-network-view"), noGl: /cannot draw 3D/.test(document.body.textContent) }; })()`);
  check(first.canvas && !first.noGl, "the network draws (WebGL)", JSON.stringify(first));
  check(first.bh >= 420 && first.bw > 600, "its frame is large: the network and its controls come first", `${first.bw} x ${first.bh}`);
  check(first.view === "live", "it opens on the live week");
  await shot("network-open");
  const buttons = await ev(`[...document.querySelectorAll('[role="group"][aria-label="Watch"] button')].map((b) => b.textContent.trim())`);
  // session 168: version 3 is the network page; its "Play the year" stands in the same group, after the four Watch buttons
  check(buttons.join("|") === "Live now|California's evening|Texas during Uri|The June 2025 heat|Play the year", "four Watch buttons, real buttons, and version 3's Play the year", buttons.join(", "));
  check(await ev(`!!document.querySelector('button[role="switch"][aria-checked="false"]')`), "the Batteries switch is a real switch, off by default");
  const click = (label) => ev(`[...document.querySelectorAll('[role="group"][aria-label="Watch"] button')].find((b) => b.textContent.trim().startsWith(${JSON.stringify(label)})).click()`);
  const state = () => ev(`({ view: document.querySelector("[data-network-view]")?.getAttribute("data-network-view"), text: document.querySelector("[data-network-view]")?.textContent ?? "",
    hour: [...document.querySelectorAll("span.tabular-nums")].map((s) => s.textContent).find((t) => /UTC/.test(t)) ?? "", panel: document.querySelector("[data-panel]")?.getAttribute("data-panel") ?? null,
    panelText: document.querySelector("[data-panel]")?.textContent ?? "", playing: [...document.querySelectorAll("button")].some((b) => b.textContent.trim() === "Pause"),
    batteries: document.querySelector('button[role="switch"]')?.getAttribute("aria-checked") })`);
  for (const [label, key, focus] of [["Texas during Uri", "uri_2021", "ERCO"], ["The June 2025 heat", "east_heat_2025", "PJM"], ["California's evening", "evening", "CISO"], ["Live now", "live", null]]) {
    await click(label);
    let s = await state();
    for (let i = 0; i < 40 && s.view !== key; i++) { await sleep(500); s = await state(); }
    const h0 = s.hour;
    await sleep(3000);
    const s2 = await state();
    check(s.view === key, `${label}: the view changes`, s.text.replace(/\s+/g, " ").slice(0, 200));
    check(s2.playing && s2.hour !== h0, `${label}: it plays`, `${h0} then ${s2.hour}`);
    if (focus) check(s2.panel === focus, `${label}: the camera and the panel go to ${focus}`, s2.panelText.replace(/\s+/g, " ").slice(0, 240));
    if (key === "evening") check(s2.batteries === "true" && /Its batteries/.test(s2.panelText), "California's evening turns the Batteries switch on and the panel gains its batteries line", s2.panelText.match(/Its batteries[^.]*/)?.[0] ?? "");
    if (key === "uri_2021") check(/Texas during Uri, 2021-02-07 to 2021-02-24/.test(s2.text), "Uri's window is stated, with what is missing", s2.text.replace(/\s+/g, " ").slice(0, 300));
    await shot(`network-${key}`);
  }
  // pause, choose a grid, read the panel, close it with Escape and with its button
  await ev(`[...document.querySelectorAll("button")].find((b) => b.textContent.trim() === "Pause")?.click()`);
  for (const id of ["CISO", "ERCO", "PJM"]) {
    await ev(`(() => { const s = [...document.querySelectorAll("select")].find((x) => [...x.options].some((o) => o.value === "${id}")); const set = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set; set.call(s, "${id}"); s.dispatchEvent(new Event("change", { bubbles: true })); })()`);
    await sleep(800);
    const s = await state();
    check(s.panel === id && /Who is supplying it/.test(s.panelText) && /Over the last twelve months/.test(s.panelText), `the panel opens for ${id}, beside the network`, s.panelText.replace(/\s+/g, " ").slice(0, 300));
    if (id === "PJM") check(/PJM's prices are licensed/.test(s.panelText), "PJM's panel shows no price");
    if (id !== "PJM") check(/What a battery earns here/.test(s.panelText), `${id}'s panel links to what a battery earns there`);
    if (id === "CISO") await shot("network-panel-caiso");
  }
  await page.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
  await page.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
  await sleep(400);
  check((await state()).panel === null, "Escape closes the panel");
  await ev(`(() => { const s = [...document.querySelectorAll("select")].find((x) => [...x.options].some((o) => o.value === "ERCO")); const set = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set; set.call(s, "ERCO"); s.dispatchEvent(new Event("change", { bubbles: true })); })()`);
  await sleep(500);
  await ev(`document.querySelector('[data-panel] button[aria-label="Close the panel"]').click()`);
  await sleep(400);
  check((await state()).panel === null, "the close button closes the panel");
  const was = (await state()).batteries;
  await ev(`document.querySelector('button[role="switch"]').click()`);
  await sleep(300);
  const now = (await state()).batteries;
  check(now !== was, "the switch turns the batteries over", `${was} to ${now}`);
  await ev(`document.querySelector('button[role="switch"]').click()`);
  await sleep(300);
  check((await state()).batteries === was, "and back again");
  // the phone: the panel stacks under the network
  await page.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 900, deviceScaleFactor: 1, mobile: true });
  await sleep(800);
  await ev(`(() => { const s = [...document.querySelectorAll("select")].find((x) => [...x.options].some((o) => o.value === "CISO")); const set = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value").set; set.call(s, "CISO"); s.dispatchEvent(new Event("change", { bubbles: true })); })()`);
  await sleep(800);
  const phone = await ev(`(() => { const n = document.querySelector('[aria-label^="A 3D network"]').getBoundingClientRect(), p = document.querySelector("[data-panel]").getBoundingClientRect(); return { stacked: p.top >= n.bottom - 1, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }; })()`);
  check(phone.stacked, "on a phone the panel stacks under the network");
  check(phone.sw <= phone.cw + 1, "on a phone the page is no wider than the screen", `${phone.sw} in ${phone.cw}`);
  page.close();
} finally {
  chrome.kill();
  await sleep(500);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* temp */ }
}
console.log(failed ? `network browser test: ${failed} assertion(s) FAILED` : "network browser test: all assertions pass");
process.exit(failed ? 1 : 0);
