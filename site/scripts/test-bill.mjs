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
import { BILL_KEYS, billCA, billTDSP, billTOU, billTX, defaultBill, defaultsCA, defaultsTDSP, defaultsTOU, defaultsTX, totalCA } from "../lib/bill.ts";

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
// session 52: SCE TOU-D-4-9PM, SDG&E TOU-DR1 and CenterPoint, by hand from the cited rates
// SCE, winter, Region 9 (12.0 kWh a day x 30 = 360 kWh baseline), 20% 4-9 p.m. (mid-peak), 33.33% 8 a.m.-4 p.m. (super
// off-peak), the rest off-peak; delivery + generation per period, the Fixed Recovery Charge, the baseline credit, the
// Base Services Charge 30 x $0.794 = $23.82
const sceD = defaultsTOU(rules, "SCE");
const sceHand = (k) => {
  const mid = 0.2 * k, sup = 0.3333 * k, off = (1 - 0.2 - 0.3333) * k;
  const delivery = mid * 0.33156 + sup * 0.25153 + off * 0.27270, generation = mid * 0.17956 + sup * 0.08452 + off * 0.10245;
  return delivery + generation + k * 0.00619 + Math.min(k, 360) * -0.10099 + 30 * 0.794;
};
const sce600 = billTOU(rules, "SCE", { ...sceD, kwh: 600 }), sce1000 = billTOU(rules, "SCE", { ...sceD, kwh: 1000 });
check(near(sce600.total, sceHand(600)), `SCE winter 600 kWh: 120 x ($0.33156 + $0.17956) + 199.98 x ($0.25153 + $0.08452) + 280.02 x ($0.27270 + $0.10245) + 600 x $0.00619 - 360 x $0.10099 + $23.82 = $${sceHand(600).toFixed(4)} | calculator ${sce600.total.toFixed(4)}`);
check(near(sce1000.total, sceHand(1000)), `SCE winter 1,000 kWh: $${sceHand(1000).toFixed(4)} | calculator ${sce1000.total.toFixed(4)}`);
// SCE summer, 600 kWh: 4-9 p.m. on weekdays (5/7 of it) on-peak, weekends mid-peak; Region 9 summer 16.9 x 30 = 507 kWh
{
  const k = 600, on = 0.2 * 0.7143 * k, mid = 0.2 * (1 - 0.7143) * k, off = 0.8 * k;
  const hand = on * (0.33156 + 0.25321) + mid * (0.33156 + 0.13326) + off * (0.27270 + 0.07396) + k * 0.00619 + 507 * -0.10099 + 30 * 0.794;
  const c = billTOU(rules, "SCE", { ...sceD, kwh: k, season: "summer" });
  check(near(c.total, hand), `SCE summer 600 kWh: on ${on.toFixed(2)}, mid ${mid.toFixed(2)}, off ${off} kWh; baseline 507 kWh: $${hand.toFixed(4)} | calculator ${c.total.toFixed(4)}`);
}
// SDG&E, summer, 20% on-peak, 34.52% super off-peak, total rates; no baseline allowance entered; 30 x $0.79343 = $23.8029
const sdgeD = defaultsTOU(rules, "SDGE");
const sdgeHand = (k, allowance = 0) => 0.2 * k * 0.69135 + 0.3452 * k * 0.37433 + (1 - 0.2 - 0.3452) * k * 0.46421 + Math.min(k, allowance * 1.3) * -0.10702 + 30 * 0.79343;
const sdge600 = billTOU(rules, "SDGE", { ...sdgeD, kwh: 600 }), sdge1000 = billTOU(rules, "SDGE", { ...sdgeD, kwh: 1000 });
check(near(sdge600.total, sdgeHand(600)), `SDG&E summer 600 kWh: 120 x $0.69135 + 207.12 x $0.37433 + 272.88 x $0.46421 + $23.8029 = $${sdgeHand(600).toFixed(4)} | calculator ${sdge600.total.toFixed(4)}`);
check(near(sdge1000.total, sdgeHand(1000)), `SDG&E summer 1,000 kWh: $${sdgeHand(1000).toFixed(4)} | calculator ${sdge1000.total.toFixed(4)}`);
{
  const c = billTOU(rules, "SDGE", { ...sdgeD, kwh: 600, baselineKwh: 300 });
  check(near(c.total, sdgeHand(600, 300)), `SDG&E summer 600 kWh with a 300 kWh allowance: the credit on 390 kWh (130%) at $0.10702 = -$41.7378 | calculator ${c.total.toFixed(4)}`);
}
// CenterPoint: the default energy charge, derived as Oncor's was: $0.1588 - $0.065333 - $4.90 / 600 = $0.085300, rounded $0.0853
const cnpPer = 0.023240 + 0.030812 + 0.006137 + 0.001576 + 0.000013 + 0.000742 + 0.000048 + 0 + 0.000636 - 0.000023 + 0.002848 - 0.000418 - 0.000278;
const cnp = defaultsTDSP(rules, "TXC");
check(near(cnp.energyRate, 0.0853) && near(cnpPer, 0.065333), `CenterPoint per kWh $${cnpPer.toFixed(6)}; default energy charge $0.0853 | ${cnp.energyRate}`);
const cnp600 = billTDSP(rules, "TXC", { ...cnp, kwh: 600 }), cnp1000 = billTDSP(rules, "TXC", { ...cnp, kwh: 1000 });
check(near(cnp600.total, 600 * 0.0853 + 600 * cnpPer + 4.90), `CenterPoint 600 kWh: $51.18 + $39.1998 + $4.90 = $95.2798 | calculator ${cnp600.total.toFixed(4)}`);
check(near(cnp1000.total, 1000 * 0.0853 + 1000 * cnpPer + 4.90), `CenterPoint 1,000 kWh: $85.30 + $65.333 + $4.90 = $155.533 | calculator ${cnp1000.total.toFixed(4)}`);
// the five defaults, as the page draws them
for (const k of BILL_KEYS) check(defaultBill(rules, k).total > 0, `default bill ${k}: ${defaultBill(rules, k).total.toFixed(4)}`);
// every line cites a source with a quote, a date and an https URL
for (const b of [ca600, tx600, sce600, sdge600, cnp600]) for (const l of b.lines) {
  const s = rules.sources[l.cite];
  check(Boolean(s && s.url.startsWith("https://") && l.quote && l.effective), `line ${l.id}: cited (${l.cite}), quoted, dated`);
}
console.log(bad ? `${bad} FAILED` : "every bill: the calculator matches the hand-computed figures");
process.exit(bad ? 1 : 0);
