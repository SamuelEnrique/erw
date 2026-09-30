// Energy Research Warehouse (ERW) site, session 43: the bill explainer against hand-computed bills.
//
//   node scripts/test-bill.mjs      (tests/test_session43.py runs this)
//
// Each case works the bill by hand from the cited tariff rates (data/bill_rules.json); lib/bill.ts must match to a
// hundredth of a cent, and for California its unbundled lines must add up to the tariff's total rates. Exits 1 on any
// mismatch.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { billCA, billTX, defaultsCA, defaultsTX, totalCA } from "../lib/bill.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const rules = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "bill_rules.json"), "utf-8"));
const near = (a, b) => Math.abs(a - b) < 1e-4;
let bad = 0;
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

const ca = defaultsCA(rules);
// California, summer, territory T (6.5 kWh a day x 30 = 195 kWh baseline), 20% peak, Income Tier 3, 30 days
// 600 kWh: 120 x $0.52240 + 480 x $0.39940 = $254.40; baseline credit 195 x $0.08140 = $15.873; base services 30 x $0.79343 = $23.8029
const ca600 = billCA(rules, { ...ca, kwh: 600 });
check(near(ca600.total, 254.40 - 15.873 + 23.8029), `CA 600 kWh: $254.40 - $15.873 + $23.8029 = $262.3299 | calculator ${ca600.total.toFixed(4)}`);
check(near(totalCA(rules, { ...ca, kwh: 600 }), ca600.total), "CA 600 kWh: the unbundled lines equal the total rates of Sheet 2");
// 1,000 kWh: 200 x $0.52240 + 800 x $0.39940 = $424.00; the same credit and charge
const ca1000 = billCA(rules, { ...ca, kwh: 1000 });
check(near(ca1000.total, 424.00 - 15.873 + 23.8029), `CA 1,000 kWh: $424.00 - $15.873 + $23.8029 = $431.9299 | calculator ${ca1000.total.toFixed(4)}`);
check(near(totalCA(rules, { ...ca, kwh: 1000 }), ca1000.total), "CA 1,000 kWh: the unbundled lines equal the total rates");
// winter, same territory (7.5 x 30 = 225 kWh baseline), 600 kWh: 120 x $0.39757 + 480 x $0.36757 = $47.7084 + $176.4336 = $224.142
const caw = billCA(rules, { ...ca, kwh: 600, season: "winter" });
check(near(caw.total, 224.142 - 225 * 0.0814 + 23.8029), `CA winter 600 kWh: $224.142 - $18.315 + $23.8029 = $229.6299 | calculator ${caw.total.toFixed(4)}`);
check(near(totalCA(rules, { ...ca, kwh: 600, season: "winter" }), caw.total), "CA winter: the unbundled lines equal the total rates");
// Texas, Oncor: default energy $0.0907; per kWh 0.036043 + 0.019046 + 0.001487 + 0 + 0 + 0.000086 + 0.001027 + 0.003633 = $0.061322; fixed $1.48 + $2.58 = $4.06
const tx = defaultsTX(rules);
check(near(tx.energyRate, 0.0907), `TX default energy charge $0.0907 | ${tx.energyRate}`);
const tx600 = billTX(rules, { ...tx, kwh: 600 });
check(near(tx600.total, 600 * 0.0907 + 600 * 0.061322 + 4.06), `TX 600 kWh: $54.42 + $36.7932 + $4.06 = $95.2732 | calculator ${tx600.total.toFixed(4)}`);
const tx1000 = billTX(rules, { ...tx, kwh: 1000 });
check(near(tx1000.total, 90.70 + 61.322 + 4.06), `TX 1,000 kWh: $90.70 + $61.322 + $4.06 = $156.082 | calculator ${tx1000.total.toFixed(4)}`);
// every line cites a source with a quote, a date and an https URL
for (const b of [ca600, tx600]) for (const l of b.lines) {
  const s = rules.sources[l.cite];
  check(Boolean(s && s.url.startsWith("https://") && l.quote && l.effective), `line ${l.id}: cited (${l.cite}), quoted, dated`);
}
console.log(bad ? `${bad} FAILED` : "every bill: the calculator matches the hand-computed figures");
process.exit(bad ? 1 : 0);
