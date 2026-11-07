// Energy Research Warehouse (ERW) site, session 2241 (chain 156): the deals charts' figures, as the page computes them.
//
//   node scripts/deals-figures.mjs <rows.json>
//
// rows.json: energy_deals as the live set serves it (event_id, event_date, status, mw, price, source, source_url,
// extra). Prints one JSON object, {key: value}, of every figure of /deals?view=charts (lib/dealsai.ts figures), with the
// register's folded pairs once (data/deal_duplicates.json). scripts/check_deals.py compares it with its own sums.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const D = await import("../lib/deals2.ts");
const A = await import("../lib/dealsai.ts");
const rows = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
const pairs = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "deal_duplicates.json"), "utf-8")).pairs;
console.log(JSON.stringify(A.figures(D.fold(rows.map(D.toDeal), pairs))));
