// Energy Research Warehouse (ERW) site, ruling alternatives of /contracts (session 7701, 17 November 2026; wip/alt-contracts-*
// branches, not a default on main). The page's own library run on rows a Python test hands it in a JSON file (the rows of
// the internal table, which are never written to the repository), so that the figure under the other choice is pinned
// with the site's code. Prints, for each product group, the counts the first view's sentence states.
// On wip/alt-contracts-4 the list is counted by filer and contract identifier and by merged buyer name (contractCounts).
//   node --import ./scripts/tsx-register.mjs scripts/alt-contracts-figures.mjs <rows.json>
import fs from "node:fs";

const C = await import("../lib/contracts.ts");
const rows = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = {};
for (const p of C.PRODUCTS) {
  const kept = C.filter(rows, p, null);
  const c = C.counts(kept), k = C.contractCounts(kept);
  out[p.slug] = { rows: c.rows, agreements_as_main: c.agreements, sellers_as_main: c.sellers, buyers_as_main: c.buyers, contracts: k.agreements, sellers: k.sellers, buyers: k.buyers, by_contract: k.byContract };
}
process.stdout.write(JSON.stringify(out));
