// Energy Research Warehouse (ERW) site, ruling alternative 3 of /learn/bill (session 7715, finished by session 7900,
// 17 November 2026; branch wip/alt-bill-3, not a default on main). The page's own library (lib/bill.ts monthPrices and
// spanPrice) run on the rows of cost_of_power_monthly committed beside the replication
// (replication/bill/source_rows.csv, the live set of 16 November 2026): for each price point, the month the bar reads on
// main and the price of a meter-read span, each month weighted by the days of the span inside it.
//   node --import ./scripts/tsx-register.mjs scripts/alt-bill-3-figures.mjs
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
const out = {};
for (const e of ["caiso:TH_NP15_GEN-APND", "caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG"]) {
  const months = B.monthPrices(rows.filter((r) => r.entity === e));
  const whole = months.filter((m) => !m.partial).at(-1) ?? months.at(-1);
  out[e] = {
    main: whole,
    span: B.spanPrice(months, "2026-09-16", "2026-10-15"),
    one_month: B.spanPrice(months, "2026-09-01", "2026-09-30"),
    not_held: B.spanPrice(months, "2026-10-16", "2026-12-15"),
    out_of_order: B.spanPrice(months, "2026-10-15", "2026-09-16"),
  };
}
process.stdout.write(JSON.stringify(out));
