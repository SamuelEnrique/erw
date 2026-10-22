// Session 583: a headless Chrome on a DevTools port at a given window size, with the internal view open (the token
// posted by the form, never in an address), for AccessLint's scan (the engine audit_live runs), which opens each page
// in a new tab of this browser. The browser is left running (detached); its pid is printed so the session stops it.
//   node docs/brand/review-583/chrome-583.mjs <site-dir> <base> <port> <width> <height> <profile-dir>
import { spawn } from "node:child_process";
import { pathToFileURL } from "node:url";
import path from "node:path";
const [siteDir, base, port, width, height, profile] = process.argv.slice(2);
const B = await import(pathToFileURL(path.join(path.resolve(siteDir), "scripts", "browser.mjs")).href);
const child = spawn(B.browserPath(), ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
  `--window-size=${width},${height}`, "--no-first-run", "--no-default-browser-check", "--disable-background-networking",
  "--disable-component-update", "--disable-sync", "--disable-extensions", "about:blank"], { detached: true, stdio: "ignore" });
child.unref();
console.log(`chrome pid ${child.pid}`);
const dev = `http://127.0.0.1:${port}`;
let ver = null;
for (let i = 0; i < 60 && !ver; i += 1) { await B.sleep(500); try { ver = await (await fetch(`${dev}/json/version`)).json(); } catch { /* not yet */ } }
if (!ver) { console.log(`FAIL: no DevTools on ${port}`); process.exit(1); }
const target = await (await fetch(`${dev}/json/new?about:blank`, { method: "PUT" })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let id = 0, loads = 0; const wait = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)) { wait.get(d.id)(d.result); wait.delete(d.id); } if (d.method === "Page.loadEventFired") loads += 1; };
const send = (method, params = {}) => new Promise((r) => { id += 1; wait.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const evaluate = async (expression) => (await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true }))?.result?.value;
const go = async (url) => { const b = loads; await send("Page.navigate", { url }); for (let i = 0; i < 600 && loads === b; i += 1) await B.sleep(100); };
await send("Page.enable"); await send("Runtime.enable");
await B.unlockForm({ go, evaluate, sleep: B.sleep }, base, B.env("INTERNAL_COSTS_TOKEN"));
console.log(`internal view open on ${port}: ${await evaluate("document.cookie.includes('erw_view=internal')")}; window ${await evaluate("innerWidth")} px`);
ws.close();
process.exit(0);
