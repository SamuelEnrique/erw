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
export function files() {
  if (!cached) cached = { index: read("datacenter", "index.json"), nodes: read("siting", "nodes.json") };
  return cached;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url) && process.argv[2] === "rows") {
  const S = await import("../lib/siting.ts");
  const f = files();
  process.stdout.write(JSON.stringify({ hubs: S.hubRows(f.index), nodes: S.nodeRows(f.nodes), stat: { hubs: S.sitingStat(f, "allgrids|rows|hubs"), nodes: S.sitingStat(f, "allgrids|rows|nodes") } }));
}
