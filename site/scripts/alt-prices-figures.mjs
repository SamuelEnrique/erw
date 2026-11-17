// Energy Research Warehouse (ERW) site, ruling alternatives of /prices (session 7723, 17 November 2026; wip/alt-prices-*
// branches, not a default on main). The hub page's own library (lib/pricehub.ts) run on the public tables as the warehouse
// wrote them. On wip/alt-prices-2: each hub's month line (monthLine) from hub_price_comparison's monthly rows.
//   node --import ./scripts/tsx-register.mjs scripts/alt-prices-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const H = await import("../lib/pricehub.ts");
const dir = process.argv[2];
const HUBS = ["spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB", "ercot:HB_NORTH", "caiso:TH_SP15_GEN-APND"];
const rows = {};
for (const line of fs.readFileSync(path.join(dir, `${H.MONTH_TABLE}.csv`), "utf-8").split(/\r?\n/)) {
  if (!line || line.startsWith("#") || line.startsWith("entity,")) continue;
  const c = line.split(",");
  if (HUBS.includes(c[0])) (rows[c[0]] ??= []).push({ entity: c[0], variable: c[1], ts_utc: c[2], value: Number(c[3]), unit: c[4], freq: c[5] });
}
process.stdout.write(JSON.stringify(Object.fromEntries(HUBS.map((e) => [e, H.monthLine(rows[e] ?? [])]))));
