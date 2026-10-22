// Session 583: AccessLint's automated scan of every address of check-values' list (its `--list`, pages and internal),
// at each width, through the same command the plugin's `audit_live` runs (`accesslint scan <url> --format json --port P`:
// the @accesslint/core engine, WCAG 2.2 A and AA, in the live page). Headless Chrome cannot make a window narrower
// than about 500 px, so this script opens each tab itself, sets the width by Emulation.setDeviceMetricsOverride (390
// by 844 as a phone, 1280 by 900 as a desktop), loads the page and lets it settle 1.5 s, then has the scan attach to
// that tab (`--attach`), and closes it. The Chrome is started by chrome-583.mjs with the internal view open.
// Writes one JSON file (no file of the tool's own: no --snapshot).
//   node docs/brand/review-583/scan-583.mjs <site-dir> <base> <out.json> <cli.js> <port> [<width> ...]
import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
const [siteDir, base, out, cli, port, ...ws] = process.argv.slice(2);
const widths = (ws.length ? ws : ["1280", "390"]).map(Number);
const dev = `http://127.0.0.1:${port}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const list = await new Promise((res, rej) => execFile(process.execPath, [path.resolve(siteDir, "scripts", "check-values.mjs"), "--list"],
  { cwd: siteDir }, (e, so) => (e ? rej(e) : res(JSON.parse(so)))));
const addrs = [...list.pages, ...list.internal];
const only = process.env.SCAN_ONLY ? process.env.SCAN_ONLY.split(",") : null;  // a few addresses, for a check
const todo = [];
let seq = 0;
for (const a of only ?? addrs) for (const w of widths) todo.push({ a, w });

const scan = (url) => new Promise((res) => execFile(process.execPath, [cli, "scan", url, "--attach", "--format", "json", "--port", port],
  { maxBuffer: 64 * 1024 * 1024, timeout: 120000 }, (e, so, se) => {
    const code = e ? (typeof e.code === "number" ? e.code : null) : 0;
    try { res({ code, result: JSON.parse(String(so).trim()) }); } catch { res({ code, error: String(se || so || e).trim().slice(0, 400) }); }
  }));

async function auditOne(addr, w) {
  const t = await (await fetch(`${dev}/json/new?about:blank`, { method: "PUT" })).json();
  const sock = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((r, j) => { sock.onopen = r; sock.onerror = j; });
  let id = 0, loads = 0; const wait = new Map();
  sock.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)) { wait.get(d.id)(d.result); wait.delete(d.id); } if (d.method === "Page.loadEventFired") loads += 1; };
  const send = (method, params = {}) => new Promise((r) => { id += 1; wait.set(id, r); sock.send(JSON.stringify({ id, method, params })); });
  try {
    await send("Page.enable"); await send("Runtime.enable");
    const phone = w < 600;
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: phone ? 844 : 900, deviceScaleFactor: 1, mobile: phone });
    const b = loads;
    // a fragment of its own: the scan attaches to the tab whose address is this one, never to the same page open at
    // the other width in another tab (the first run's findings at 1280 were in part the 390 tab's)
    seq += 1;
    await send("Page.navigate", { url: `${base}${addr}#a11y-scan-${seq}` });
    for (let i = 0; i < 600 && loads === b; i += 1) await sleep(100);
    await sleep(Number(process.env.SCAN_SETTLE_MS ?? 1500));
    const info = (await send("Runtime.evaluate", { expression: "JSON.stringify({u: location.href, w: innerWidth, h1: (document.querySelector('h1')?.textContent ?? '').trim().slice(0, 80)})", returnByValue: true }))?.result?.value;
    const page = JSON.parse(info ?? "{}");
    const r = await scan(page.u);
    return { ...r, innerWidth: page.w, finalUrl: page.u, h1: page.h1 };
  } finally {
    sock.close();
    await fetch(`${dev}/json/close/${t.id}`).catch(() => {});
  }
}

const results = [];
async function worker() {
  for (;;) {
    const job = todo.shift();
    if (!job) return;
    let r = await auditOne(job.a, job.w);
    if (r.error) r = await auditOne(job.a, job.w);  // once more on a tool error
    const v = r.result?.violations ?? [];
    results.push({ addr: job.a, width: job.w, innerWidth: r.innerWidth, finalUrl: r.finalUrl, h1: r.h1, code: r.code, error: r.error ?? null, count: v.length,
      violations: v.map((x) => ({ ruleId: x.ruleId, impact: x.impact, selector: x.selector, message: x.message, html: (x.html ?? "").slice(0, 300) })) });
    console.log(`${job.w} ${job.a} ${r.error ? "ERROR " + r.error.split("\n")[0] : v.length}`);
  }
}
await Promise.all([worker(), worker(), worker()]);
const order = only ?? addrs;
results.sort((x, y) => order.indexOf(x.addr) - order.indexOf(y.addr) || y.width - x.width);
fs.writeFileSync(out, JSON.stringify({ base, when: new Date().toISOString(), addresses: order.length, widths, results }, null, 1));
const errors = results.filter((r) => r.error).length;
const wrong = results.filter((r) => r.innerWidth !== r.width).length;
console.log(`done: ${results.length} scans, ${results.reduce((s, r) => s + r.count, 0)} findings, ${errors} errors, ${wrong} at the wrong width`);
process.exit(errors || wrong ? 1 : 0);
