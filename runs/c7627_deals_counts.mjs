// Session 7627: counts only (never a deal's parties or figures) of the deal tracker's rows on this machine's copy of
// energy_deals (held: license needed), read through the page's own functions (site/lib/deals2.ts) of the worktree named.
//   node runs/c7627_deals_counts.mjs <worktree site folder> <energy_deals.csv>
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [site, csvPath] = process.argv.slice(2);
const D = await import(pathToFileURL(path.join(site, "lib", "deals2.ts")).href);
const pairs = JSON.parse(fs.readFileSync(path.join(site, "data", "deal_duplicates.json"), "utf-8")).pairs;

function parseCsv(text) {
  const rows = []; let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true;
    else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; }
    else if (c !== "\r") cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows;
}
const lines = fs.readFileSync(csvPath, "utf-8").split("\n").filter((l) => !l.startsWith("#")).join("\n");
const [head, ...body] = parseCsv(lines);
const TOP = ["event_id", "event_date", "status", "mw", "price", "currency", "parties", "source", "source_url"];
const rows = body.filter((r) => r.length === head.length).map((r) => {
  const o = Object.fromEntries(head.map((h, i) => [h, r[i]]));
  const extra = Object.fromEntries(head.filter((h) => !TOP.includes(h)).map((h) => [h, o[h]]));
  return { ...Object.fromEntries(TOP.map((h) => [h, o[h] === "" ? null : o[h]])), extra };
});
const all = D.fold(rows.map(D.toDeal), pairs);
const mw = all.filter((d) => d.mw !== null);
const out = { rows: rows.length, deals: all.length, mw_sum: Math.round(mw.reduce((a, d) => a + d.mw, 0)), with_mw: mw.length,
  ai: all.filter((d) => d.ai).length, grid_none: all.filter((d) => !d.grid).length, pjm: all.filter((d) => d.grid === "PJM" || d.grid === "pjm").length };
console.log(JSON.stringify(out));
