// Energy Research Warehouse (ERW) site, ruling alternative 4 of /learn/bill (session 7715, finished by session 7900,
// 17 November 2026; branch wip/alt-bill-4, not a default on main). The page's own library (lib/bill.ts defaultBill,
// wholesaleUsdOf, LOSS_FACTOR) on the page's rules file and the rows of cost_of_power_monthly committed beside the
// replication (replication/bill/source_rows.csv, the live set of 16 November 2026): for each of the five default
// bills, the wholesale dollars and share on the metered kWh (main) and with the wires' losses (this branch), at the
// price of the newest whole month (September 2026).
//   node --import ./scripts/tsx-register.mjs scripts/alt-bill-4-figures.mjs
import fs from "node:fs";

const B = await import("../lib/bill.ts");
const rules = JSON.parse(fs.readFileSync(new URL("../data/bill_rules.json", import.meta.url), "utf8"));
const by = new Map();
let head = null;
for (const line of fs.readFileSync(new URL("../../replication/bill/source_rows.csv", import.meta.url), "utf8").split(/\r?\n/)) {
  if (!line || line.startsWith("#")) continue;
  if (!head) { head = line.split(","); continue; }
  const c = line.split(","), k = `${c[0]}|${c[2].slice(0, 7)}`;
  (by.get(k) ?? by.set(k, {}).get(k))[c[1]] = Number(c[3]);
}
// the page's rule on main: the newest month whose real-time hours equal its hours
const whole = (entity) => [...by.keys()].filter((k) => k.startsWith(`${entity}|`) && by.get(k).rt_load_weighted !== undefined && by.get(k).rt_hours === by.get(k).hours_in_month).sort().at(-1);
const out = { loss_factor: B.LOSS_FACTOR, bills: {} };
for (const key of B.BILL_KEYS) {
  const bill = B.defaultBill(rules, key), k = whole(rules.bills[key].wholesale_entity), price = by.get(k).rt_load_weighted;
  const main = (bill.kwh * price) / 1000, alt = B.wholesaleUsdOf(bill.kwh, price);
  out.bills[key] = { month: k.split("|")[1], price, kwh: bill.kwh, total: bill.total, main_usd: main, alt_usd: alt, main_share: (main / bill.total) * 100, alt_share: (alt / bill.total) * 100 };
}
process.stdout.write(JSON.stringify(out));
