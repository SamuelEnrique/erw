// Session 583: AccessLint's automated scan of every address of check-values' list (its `--list`, pages and internal),
// at each width, through the same command the plugin's `audit_live` runs (`accesslint scan <url> --format json --port P`:
// a new tab in the given Chrome, the load event, the @accesslint/core engine, WCAG 2.2 A and AA, the tab closed).
// Each Chrome is started by chrome-583.mjs at its width with the internal view open. Writes one JSON file (no file of
// the tool's own: no --snapshot).
//   node docs/brand/review-583/scan-583.mjs <site-dir> <base> <out.json> <cli.js> <width>:<port> [<width>:<port> ...]
import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
const [siteDir, base, out, cli, ...pairs] = process.argv.slice(2);
const list = await new Promise((res, rej) => execFile(process.execPath, [path.join(siteDir, "scripts", "check-values.mjs"), "--list"],
  { cwd: siteDir }, (e, so) => (e ? rej(e) : res(JSON.parse(so)))));
const addrs = [...list.pages, ...list.internal];
const widths = pairs.map((p) => { const [w, port] = p.split(":"); return { w: Number(w), port }; });
const scan = (url, port) => new Promise((res) => execFile(process.execPath, [cli, "scan", url, "--format", "json", "--port", port],
  { maxBuffer: 64 * 1024 * 1024, timeout: 120000 }, (e, so, se) => {
    const code = e ? (typeof e.code === "number" ? e.code : null) : 0;
    try { res({ code, result: JSON.parse(String(so).trim()) }); } catch { res({ code, error: String(se || so || e).trim().slice(0, 400) }); }
  }));
const results = [];
async function worker(w, queue) {
  for (;;) {
    const a = queue.shift();
    if (a === undefined) return;
    const url = base + a;
    let r = await scan(url, w.port);
    if (r.error) r = await scan(url, w.port);  // once more on a tool error (a slow page's 15 s load limit)
    const v = r.result?.violations ?? [];
    results.push({ addr: a, width: w.w, code: r.code, error: r.error ?? null, count: v.length,
      violations: v.map((x) => ({ ruleId: x.ruleId, impact: x.impact, selector: x.selector, message: x.message, html: (x.html ?? "").slice(0, 300) })) });
    console.log(`${w.w} ${a} ${r.error ? "ERROR " + r.error.split("\n")[0] : v.length}`);
  }
}
const jobs = [];
for (const w of widths) { const q = [...addrs]; jobs.push(worker(w, q), worker(w, q)); }
await Promise.all(jobs);
results.sort((x, y) => addrs.indexOf(x.addr) - addrs.indexOf(y.addr) || x.width - y.width);
fs.writeFileSync(out, JSON.stringify({ base, when: new Date().toISOString(), addresses: addrs.length, results }, null, 1));
const errors = results.filter((r) => r.error).length;
console.log(`done: ${results.length} scans, ${results.reduce((s, r) => s + r.count, 0)} findings, ${errors} errors`);
process.exit(errors ? 1 : 0);
