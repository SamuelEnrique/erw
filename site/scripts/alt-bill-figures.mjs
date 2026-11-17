// Energy Research Warehouse (ERW) site, ruling alternatives of /learn/bill (session 7715, 17 November 2026;
// wip/alt-bill-* branches, not a default on main). The page's own library (lib/bill.ts) run on the rows of
// cost_of_power_monthly committed beside the replication (replication/bill/source_rows.csv, the live set of 16 November
// 2026), so that the figures under the other choice are pinned with the site's code. On wip/alt-bill-1: the month and
// price the wholesale bar reads for each price point as of each month's end (the rows cut at that month), and today.
//   node --import ./scripts/tsx-register.mjs scripts/alt-bill-figures.mjs
import fs from "node:fs";

const B = await import("../lib/bill.ts");
const rows = [];
let head = null;
for (const line of fs.readFileSync(new URL("../../replication/bill/source_rows.csv", import.meta.url), "utf8").split(/\r?\n/)) {
  if (!line || line.startsWith("#")) continue;
  if (!head) { head = line.split(","); continue; }
  const c = line.split(",");
  rows.push({ entity: c[0], variable: c[1], ts_utc: c[2], value: Number(c[3]), unit: c[4] });
}
const at = (entity, upTo) => {
  const w = B.wholesaleMonth(rows.filter((r) => r.entity === entity && (!upTo || r.ts_utc.slice(0, 7) <= upTo)));
  return w ? { month: w.row.ts_utc.slice(0, 7), price: w.row.value, partial: w.partial } : null;
};
const out = { missing: B.MISSING_HOURS_WHOLE };
for (const e of ["caiso:TH_NP15_GEN-APND", "caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG"]) {
  out[e] = { today: at(e), "2024-10": at(e, "2024-10"), "2025-10": at(e, "2025-10"), "2025-12": at(e, "2025-12") };
}
process.stdout.write(JSON.stringify(out));
