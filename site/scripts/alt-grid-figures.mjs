// Energy Research Warehouse (ERW) site, ruling alternative 2 of /grid (session 7725, 17 November 2026; branch wip/alt-grid-2,
// not a default on main). The Mix tab's own choice of demand (lib/griddemand.ts pickDemand) on the committed hourly snapshot
// (data/grid_network.json) and the local daily demand table (eia930_all_demand): for each public grid, the table's newest
// hour and value (main), the snapshot's, and which the branch draws.
//   node --import ./scripts/tsx-register.mjs scripts/alt-grid-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const G = await import("../lib/griddemand.ts");
const snap = JSON.parse(fs.readFileSync(new URL("../data/grid_network.json", import.meta.url), "utf8"));
const newest = {};
for (const line of fs.readFileSync(path.join(process.argv[2], "eia930_all_demand.csv"), "utf-8").split(/\r?\n/)) {
  const c = line.split(",");
  if (c[1] !== "demand_mw" || c[3] === "" || !c[0].startsWith("eia930:")) continue;
  if (!newest[c[0]] || c[2] > newest[c[0]].ts_utc) newest[c[0]] = { entity: c[0], variable: c[1], ts_utc: c[2], value: Number(c[3]) };
}
const out = { snapshot_built: snap.built };
for (const ba of ["ERCO", "CISO", "SWPP", "PJM"]) {
  const e = `eia930:${ba}`, node = snap.nodes.find((n) => n.id === ba);
  const p = G.pickDemand(newest[e], node, e);
  out[ba] = { table: newest[e] ? [newest[e].ts_utc, newest[e].value] : null, snapshot: node ? [node.demand_ts, node.demand_mw] : null, drawn: p.d ? [p.d.ts_utc, p.d.value] : null, fromSnap: p.fromSnap };
}
process.stdout.write(JSON.stringify(out));
