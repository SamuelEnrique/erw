// Energy Research Warehouse (ERW) site, ruling alternatives of /contracts (session 7701, 17 November 2026; wip/alt-contracts-*
// branches, not a default on main). The page's own library run on rows a Python test hands it in a JSON file (the rows of
// the internal table, which are never written to the repository), so that the figure under the other choice is pinned
// with the site's code. Prints, for each product group, the counts the first view's sentence and headline cells state.
// On wip/alt-contracts-2 a rate filed as the number 0 is not counted as a price, as the page counts it there.
//   node --import ./scripts/tsx-register.mjs scripts/alt-contracts-figures.mjs <rows.json>
import fs from "node:fs";

const C = await import("../lib/contracts.ts");
const rows = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = {};
for (const p of C.PRODUCTS) {
  const kept = C.filter(rows, p, null);
  const c = C.counts(kept), zero = C.zeroPriced(kept);   // priced: the page's own function on this branch
  out[p.slug] = { rows: c.rows, priced: C.pricedNotZero(kept), priced_as_main: c.priced, zero, agreements: c.agreements, sellers: c.sellers, buyers: c.buyers };
}
process.stdout.write(JSON.stringify(out));
