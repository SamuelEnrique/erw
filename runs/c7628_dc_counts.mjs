// Session 7628: counts only (no facility's name, operator or own figure) of the datacenter tracker's "operator not
// stated" line, read through the page's own rollup (site/lib/dcrollups.ts) of the worktree named, on this machine's
// copy of datacenter_facilities (held: license needed).
//   node runs/c7628_dc_counts.mjs <worktree site folder> <datacenter_facilities.csv>
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [site, csvPath] = process.argv.slice(2);
const R = await import(pathToFileURL(path.join(site, "lib", "dcrollups.ts")).href);
function parseCsv(text) {
  const rows = []; let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true; else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; } else if (c !== "\r") cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows;
}
const text = fs.readFileSync(csvPath, "utf-8").split("\n").filter((l) => !l.startsWith("#")).join("\n");
const [head, ...body] = parseCsv(text);
const TOP = ["entity_id", "capacity_mw", "status", "operator"];
const rows = body.filter((r) => r.length === head.length).map((r) => {
  const o = Object.fromEntries(head.map((h, i) => [h, r[i]]));
  return { ...Object.fromEntries(TOP.map((h) => [h, o[h] === "" ? null : o[h]])), extra: Object.fromEntries(head.filter((h) => !TOP.includes(h)).map((h) => [h, o[h]])) };
});
const ro = R.rollups(rows, "operator");
const none = ro.find((x) => !x.value);
const counted = ro.reduce((a, x) => a + x.counted, 0), mw = ro.reduce((a, x) => a + (x.mw ?? 0), 0);
console.log(JSON.stringify({ rows: rows.length, counted, mw: Math.round(mw * 10) / 10, lines: ro.length,
  none: none ? { facilities: none.facilities, withMw: none.withMw, counted: none.counted, mw: none.mw === null ? null : Math.round(none.mw * 10) / 10 } : null }));
