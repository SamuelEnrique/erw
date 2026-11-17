// Energy Research Warehouse (ERW) site, ruling alternatives of /supply (session 7726, 17 November 2026; wip/alt-supply-*
// branches, not a default on main). The page's own library (lib/supply.ts) run on the public table as the warehouse wrote
// it. On wip/alt-supply-3: each grid's net imports for the newest month (netImports) from ba_supply_monthly.
//   node --import ./scripts/tsx-register.mjs scripts/alt-supply-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const S = await import("../lib/supply.ts");
const BAS = ["ERCO", "CISO", "PJM", "MISO", "NYIS", "ISNE", "SWPP"];
const rows = [];
for (const line of fs.readFileSync(path.join(process.argv[2], `${S.NET_IMPORT_TABLE}.csv`), "utf-8").split(/\r?\n/)) {
  const c = line.split(",");
  if (BAS.some((b) => c[0] === `eia930:${b}`) && S.NET_IMPORT_VARS.includes(c[1])) rows.push({ entity: c[0], variable: c[1], ts_utc: c[2], value: Number(c[3]) });
}
process.stdout.write(JSON.stringify(S.netImports(rows, BAS)));
