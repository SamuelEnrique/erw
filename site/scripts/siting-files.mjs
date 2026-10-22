// Energy Research Warehouse (ERW) site, session 700: the files the All grids tab of /cost-of-power reads, read a second
// time outside the page, for scripts/check-values.mjs (allgrids| keys) and tests/test_session700.py. The tab reads the
// same files through lib/sitingdata.ts. No server, no network.
//
//   node scripts/siting-files.mjs rows      the hub and zone rows and the node rows as JSON (the test's list)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const data = path.join(here, "..", "data");
const read = (...p) => JSON.parse(fs.readFileSync(path.join(data, ...p), "utf-8"));
let cached = null;
const years = new Map();
/** The files as lib/sitingdata.ts hands them to lib/siting.ts; a grid's years of hourly prices read when first asked. */
export function files() {
  if (!cached) {
    const index = read("datacenter", "index.json");
    const yearsOf = (grid) => {
      if (!years.has(grid)) years.set(grid, (index.grids[grid]?.years ?? []).map((y) => read("datacenter", `${grid}_${y}.json`)));
      return years.get(grid);
    };
    cached = { index, nodes: read("siting", "nodes.json"), years: yearsOf };
  }
  return cached;
}
/** lib/datacenter.ts's functions, as lib/sitingdata.ts hands them (session 701). */
export async function dc() {
  const L = await import("../lib/datacenter.ts");
  return { monthsRuled: L.monthsRuled, lastTwelve: L.lastTwelve, span: L.span, years: L.years };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url) && process.argv[2] === "rows") {
  const S = await import("../lib/siting.ts");
  const f = files();
  process.stdout.write(JSON.stringify({ hubs: S.hubRows(f.index), nodes: S.nodeRows(f.nodes), stat: { hubs: S.sitingStat(f, "allgrids|rows|hubs"), nodes: S.sitingStat(f, "allgrids|rows|nodes") } }));
}
// session 701: node scripts/siting-files.mjs energy    every row's energy keys and figures, and "Your load"'s own figure
// for each grid's main region bought day-ahead (scripts/datacenter-ways.mjs, pageOf), as JSON
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url) && process.argv[2] === "energy") {
  const S = await import("../lib/siting.ts");
  const W = await import("./datacenter-ways.mjs");
  const f = files(), d = await dc();
  const out = { rows: {}, page: {} };
  for (const r of [...S.hubRows(f.index), ...S.nodeRows(f.nodes)]) out.rows[r.id] = { da: S.sitingStat(f, `allgrids|energy|${r.id}|da`, d) ?? null, rt: S.sitingStat(f, `allgrids|energy|${r.id}|rt`, d) ?? null };
  for (const [g, gi] of Object.entries(f.index.grids)) out.page[`${g}:${gi.main}`] = W.pageOf({ grid: g, region: gi.main, buy: "da" }).s12?.per ?? null;
  process.stdout.write(JSON.stringify(out));
}
