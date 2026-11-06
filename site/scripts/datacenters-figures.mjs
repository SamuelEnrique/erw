// Energy Research Warehouse (ERW) site, session 2246 (chain 156): the datacenter tracker's chart figures, as the page
// computes them (lib/dcrollups.ts dcFigures).
//
//   node scripts/datacenters-figures.mjs <rows.json>
//
// rows.json: datacenter_facilities as the live set serves it (entity_id, capacity_mw, status, operator, extra). Prints one
// JSON object, {key: value}; scripts/check_datacenters.py compares it with its own sums.
import fs from "node:fs";

const R = await import("../lib/dcrollups.ts");
console.log(JSON.stringify(R.dcFigures(JSON.parse(fs.readFileSync(process.argv[2], "utf-8")))));
