// Session 412: open the internal view in the Chrome listening on 9412 (the form at /internal/open, the
// token posted, never in an address), so AccessLint's audit_live (port 9412) audits the pages, not the curtain.
import { env, unlockForm, sleep } from "../../../site/scripts/browser.mjs";
const base = process.argv[2] ?? "http://localhost:3412";
const list = await (await fetch("http://127.0.0.1:9412/json")).json();
const page = list.find((t) => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let id = 0, loads = 0; const waiting = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && waiting.has(d.id)) { waiting.get(d.id)(d); waiting.delete(d.id); } if (d.method === "Page.loadEventFired") loads += 1; };
const send = (method, params = {}) => new Promise((r) => { id += 1; waiting.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
await send("Page.enable");
const evaluate = async (expression) => { const d = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true }); if (d.result?.exceptionDetails) throw new Error("in the page"); return d.result?.result?.value; };
const go = async (url) => { const b = loads; await send("Page.navigate", { url }); for (let i = 0; i < 600 && loads === b; i += 1) await sleep(100); };
await unlockForm({ go, evaluate, sleep }, base, env("INTERNAL_COSTS_TOKEN"));
console.log("internal view open in the Chrome on 9412:", await evaluate("document.cookie.includes('erw_view=internal')"));
ws.close();
