// Energy Research Warehouse (ERW) site, ruling alternatives of /contracts (session 7701, 17 November 2026; wip/alt-contracts-*
// branches, not a default on main). The page's own library run on rows a Python test hands it in a JSON file (the rows of
// the internal table, which are never written to the repository), so that the figure under the other choice is pinned
// with the site's code. Prints, for each product group, the counts the first view's sentence and headline cells state.
//   node --import ./scripts/tsx-register.mjs scripts/alt-contracts-figures.mjs <rows.json>
import fs from "node:fs";

const C = await import("../lib/contracts.ts");
const rows = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = {};
for (const p of C.PRODUCTS) {
  const asFiled = C.filter(rows, p, null);
  const kept = C.withoutOperators ? C.withoutOperators(asFiled) : asFiled;
  const c = C.counts(kept);
  out[p.slug] = { rows: c.rows, priced: c.priced, agreements: c.agreements, sellers: c.sellers, buyers: c.buyers, zero: C.zeroPriced(kept), left_out: asFiled.length - kept.length };
}
process.stdout.write(JSON.stringify(out));
