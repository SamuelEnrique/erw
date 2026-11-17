// Energy Research Warehouse (ERW) site, ruling alternatives of /contracts (session 7701, 17 November 2026; wip/alt-contracts-*
// branches, not a default on main). The page's own library run on rows a Python test hands it in a JSON file (the rows of
// the internal table, which are never written to the repository), so that the figure under the other choice is pinned
// with the site's code. On wip/alt-contracts-5: the figures in USD per kW-month the capacity list draws (its first 400
// rows, as the page draws them), counted, with their median, least and most.
//   node --import ./scripts/tsx-register.mjs scripts/alt-contracts-figures.mjs <rows.json>
import fs from "node:fs";

const C = await import("../lib/contracts.ts");
const rows = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const capacity = C.PRODUCTS.find((p) => p.slug === "capacity");
const drawn = C.filter(rows, capacity, null).slice(0, 400);
const v = drawn.map((r) => C.kwMonth(r)).filter((x) => x !== null).sort((a, b) => a - b);
const median = v.length ? (v.length % 2 ? v[(v.length - 1) / 2] : (v[v.length / 2 - 1] + v[v.length / 2]) / 2) : null;
process.stdout.write(JSON.stringify({ drawn: drawn.length, converted: v.length, median, least: v[0] ?? null, most: v.at(-1) ?? null }));
