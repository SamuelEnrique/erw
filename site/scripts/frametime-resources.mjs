// Energy Research Warehouse (ERW) site, session 146: the frame time of "Where the resources are" while its map is
// panned and zoomed, in a visible browser window (frames only run in a visible window; scripts/frametime-battery.mjs
// is the pattern).
//
//   npm run build && npx next start -p 3146
//   node scripts/frametime-resources.mjs [base-url] [--only id,id;id] [--headless]
//
// --only: scenarios apart by ";", the layers of one apart by ","; "nothing" is the map with no layer on (the states
// alone), the measure of what the browser and the machine do by themselves. --idle: the mouse is still between the
// zooms (the first run of the session did this, and met a slow first frame after each idle spell, layer or no layer). --headless: no window (a machine whose screen is
// locked draws no frames in a window; headless Chrome draws them at its own 60 a second).
//
// For each grid layer of the manifest, alone, then for every grid with the plants, the queue and the datacenters over
// it: opens the page in the internal view, and with the real mouse path (DevTools input events) drags the map and
// turns the wheel at three zooms, waiting between them for the finer level to arrive, so each level of the pyramid is
// on the screen while it is measured. Every requestAnimationFrame interval during the dragging and zooming is kept.
// Prints, a scenario: the levels that were drawn, the frame count, the median, the 95th percentile and the longest
// frame, and how many frames ran over 33.4 ms and over 100 ms. "Smooth" here: a median of 33.4 ms or less (30 frames a
// second) and no frame over 100 ms. Exit 1 when a scenario is not smooth, or the window was not visible.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { browserPath, env, sleep } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const flag = (f, d) => (argv.includes(f) ? argv[argv.indexOf(f) + 1] : d);
const base = (argv[0] && !argv[0].startsWith("--") ? argv[0] : "http://localhost:3146").replace(/\/$/, "");
const HEADLESS = argv.includes("--headless");
const IDLE = argv.includes("--idle");
const REST = Number(flag("--rest", "2500"));   // ms waited at each zoom for a finer level to arrive, not recorded
const PORT = Number(flag("--port", "9346"));
// session 159: --size WIDTHxHEIGHT is the browser window's size (the default is the first session's 1400 by 1000; a
// laptop's is 1366x768); --all adds one scenario with EVERY layer of the manifest and every overlay on at once; "all" in
// --only stands for that scenario ("--only nothing;all" measures the bare map, then everything).
const SIZE = /^\d+x\d+$/.test(flag("--size", "")) ? flag("--size", "").split("x").map(Number) : [1400, 1000];
const manifest = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "resources", "manifest.json"), "utf-8"));
const grids = (manifest.layers ?? []).filter((l) => l.kind === "grid").map((l) => l.id);
const OVERLAY_IDS = ["plants_operating", "plants_planned", "queue", "datacenters"];
const EVERYTHING = [...(manifest.layers ?? []).map((l) => l.id), ...OVERLAY_IDS];
const only = flag("--only", "");
const scenarios = only ? only.split(";").map((s) => (s === "nothing" ? [] : s === "all" ? EVERYTHING : s.split(",")))
  : [...grids.map((g) => [g]), [...grids.slice(0, 2), ...OVERLAY_IDS], ...(argv.includes("--all") ? [EVERYTHING] : [])];

const exe = browserPath();
if (!exe) { console.log("no Chrome or Edge on this machine: the frame time was not measured"); process.exit(1); }
const token = env("INTERNAL_COSTS_TOKEN");
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "erw-frametime-"));
const chrome = spawn(exe, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check", "--new-window", `--window-size=${SIZE[0]},${SIZE[1]}`, "--window-position=0,0",
  ...(HEADLESS ? ["--headless=new"] : []), "about:blank"], { stdio: "ignore" });
let code = 0;
try {
  let target;
  for (let i = 0; i < 60 && !target; i++) {
    await sleep(250);
    try { target = (await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()).find((t) => t.type === "page"); } catch { /* not up yet */ }
  }
  if (!target) throw new Error("the browser did not start");
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0;
  const pending = new Map(), errors = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails?.exception?.description?.split(String.fromCharCode(10))[0] ?? m.params.exceptionDetails?.text);
    if (m.id && pending.has(m.id)) { const { res, rej } = pending.get(m.id); pending.delete(m.id); if (m.error) rej(new Error(m.error.message)); else res(m.result); }
  };
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  const run = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result.value;
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Page.bringToFront");
  await send("Page.addScriptToEvaluateOnNewDocument", { source: "window.__ft = []; window.__at = []; window.__on = false; window.__step = ''; window.__long = []; try { new PerformanceObserver((l) => { for (const e of l.getEntries()) if (window.__on) window.__long.push(Math.round(e.duration)); }).observe({ entryTypes: ['longtask'] }); } catch (e) {} (() => { let last = performance.now(); const f = (now) => { if (window.__on) { window.__ft.push(now - last); window.__at.push([window.__step, Math.round(now - last)]); } last = now; requestAnimationFrame(f); }; requestAnimationFrame(f); })();" });
  await send("Page.navigate", { url: `${base}/internal/unlock?token=${encodeURIComponent(token ?? "")}` });
  await sleep(4000);
  // frames only run in a window that is being shown: a locked or sleeping screen, or a window behind another, gives none
  const probe = await run("Promise.race([new Promise((r) => requestAnimationFrame(() => r('frames run'))), new Promise((r) => setTimeout(() => r('no frame in 3 s'), 3000))])");
  console.log(`animation-frame probe: ${probe}; visibility ${await run("document.visibilityState")}${HEADLESS ? "; headless" : "; a window on the screen"}; between zooms the mouse ${IDLE ? "is still" : "keeps moving over the map"}`);
  // session 159: what the measurement ran on, in the browser's own words: the window, the screen, and the graphics it draws with
  console.log(`window asked ${SIZE[0]} by ${SIZE[1]}; ${await run("'viewport ' + innerWidth + ' by ' + innerHeight + ', outer ' + outerWidth + ' by ' + outerHeight + ', screen ' + screen.width + ' by ' + screen.height + ', pixel ratio ' + devicePixelRatio + ', focus ' + document.hasFocus()")}; graphics: ${await run("(() => { try { const gl = document.createElement('canvas').getContext('webgl'); const e = gl.getExtension('WEBGL_debug_renderer_info'); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'not named'; } catch (e) { return 'not named'; } })()")}`);
  if (probe !== "frames run") throw new Error("the window draws no frames (the screen is locked or the window is hidden); run again with the screen on, or with --headless");

  for (const ids of scenarios) {
    await send("Page.navigate", { url: `${base}/resources?on=${ids.join(",")}&z=1&c=-95.75,37.25` });
    let ok = false;
    for (let i = 0; i < 240 && !ok; i++) {
      await sleep(250);
      ok = await run(`${JSON.stringify(ids)}.every((id) => document.querySelector('[data-layer="' + id + '"]')?.dataset.state === 'ready')`).catch(() => false);
    }
    if (!ok) { console.log(`${ids.join(" + ") || "nothing on"}: NOT MEASURED, a layer was not read in 60 s`); code = 1; continue; }
    await sleep(800);
    const vis = await run("document.visibilityState");
    const box = await run(`(() => { const c = document.querySelector('[data-map] canvas'); c.scrollIntoView({ block: 'center' }); const r = c.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height }; })()`);
    const levelsNow = () => run(`[...document.querySelectorAll('[data-layer][data-kind="grid"]')].filter((e) => e.querySelector('input').checked).map((e) => e.dataset.level).join('/')`);
    const seen = new Set();
    let stretch = 0;
    const name = (what) => { stretch += 1; return run(`window.__step = ${JSON.stringify(`${stretch} ${what}`)}`); };
    const drag = async () => {
      await name("drag");
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x: box.x, y: box.y, button: "left", buttons: 1, clickCount: 1 });
      for (let i = 1; i <= 80; i++) {
        const a = (i / 80) * Math.PI * 2;
        await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: box.x + Math.sin(a) * box.w * 0.22, y: box.y + (1 - Math.cos(a)) * box.h * 0.16, button: "left", buttons: 1 });
        await sleep(12);
      }
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: box.x, y: box.y, button: "left", buttons: 0, clickCount: 1 });
    };
    const wheel = async (steps, dy) => { await name(dy < 0 ? "wheel in" : "wheel out"); for (let i = 0; i < steps; i++) { await send("Input.dispatchMouseEvent", { type: "mouseWheel", x: box.x + 40, y: box.y - 30, deltaX: 0, deltaY: dy }); await sleep(28); } };
    // between two zooms the finer level is given time to arrive, unrecorded. With --idle the mouse is still for that
    // time; otherwise it keeps moving over the map (no button), as a reader's does, so the next drag does not begin
    // from a browser that has gone idle (the first frame after an idle spell is slow here with no layer on at all).
    const rest = async () => {
      await run("window.__on = false");
      if (IDLE) await sleep(REST);
      else for (let t = 0, i = 0; t < REST; t += 16, i++) { await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: box.x + Math.cos(i / 9) * 60, y: box.y + Math.sin(i / 9) * 40 }); await sleep(14); }
      seen.add(await levelsNow());
      await run("window.__on = true");
    };
    seen.add(await levelsNow());
    if (!IDLE) for (let i = 0; i < 40; i++) { await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: box.x + Math.cos(i / 9) * 60, y: box.y + Math.sin(i / 9) * 40 }); await sleep(14); }
    await run("window.__ft = []; window.__at = []; window.__long = []; window.__on = true");
    await drag(); await wheel(14, -100);          // zoom 1, then in to about 8
    await rest(); await drag(); await wheel(12, -100);   // and in to about 50
    await rest(); await drag(); await wheel(26, 100);    // and out again
    await run("window.__on = false");
    seen.add(await levelsNow());
    const r = await run(`(() => { const d = window.__ft.slice().sort((a, b) => a - b); const q = (p) => d[Math.min(d.length - 1, Math.floor(p * d.length))]; return d.length ? { frames: d.length, p50: q(0.5), p95: q(0.95), max: d.at(-1), over33: d.filter((x) => x > 33.4).length, over100: d.filter((x) => x > 100).length } : { frames: 0 }; })()`);
    await sleep(600);
    const slow = await run(`JSON.parse(document.querySelector('[data-map]').dataset.slow || '{}')`);
    // where the slow frames fell: the stretch, and how far into it (its frame number)
    const where = await run(`(() => { const n = {}; const out = []; for (const [step, dt] of window.__at) { n[step] = (n[step] || 0) + 1; if (dt > 50) out.push(dt + ' ms at frame ' + n[step] + ' of "' + step + '"'); } return out.join('; '); })()`);
    const smooth = r.frames > 0 && r.p50 <= 33.4 && r.over100 === 0;
    const f = (v) => (typeof v === "number" ? v.toFixed(1) : v);
    console.log(`${ids.join(" + ") || "nothing on (the states alone)"}: ${smooth ? "smooth" : "NOT SMOOTH"}; window ${vis}, map ${Math.round(box.w)} by ${Math.round(box.h)} px; levels drawn (degrees) ${[...seen].filter(Boolean).join(", ")}; ${r.frames} frames while dragging and zooming: median ${f(r.p50)} ms, 95th percentile ${f(r.p95)} ms, longest ${f(r.max)} ms, over 33.4 ms ${r.over33}, over 100 ms ${r.over100}; the page's own longest work, ms: a frame while moving ${f(slow.moving)}, a frame at rest ${f(slow.rest)}, reading a file into a picture ${f(slow.decode)}; frames drawn from the picture kept at rest (a heavy map while it moves) ${slow.kept ?? 0}${where ? `; frames over 50 ms: ${where}` : ""}; tasks of the page's thread over 50 ms while recording: ${(await run("window.__long.join(', ')")) || "none"}`);
    if (!smooth || (!HEADLESS && vis !== "visible")) code = 1;
  }
  console.log(`page errors: ${errors.length ? errors.join(" | ") : "none"}`);
  if (errors.length) code = 1;
  ws.close();
} catch (e) {
  console.error(`frametime FAILED: ${e.message}`);
  code = 1;
} finally {
  chrome.kill();
  await sleep(500);
  try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* the browser may still hold a file */ }
}
process.exit(code);
