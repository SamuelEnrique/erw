// Energy Research Warehouse (ERW) site, session 40: the severance calculator against hand-computed cases.
//
//   node scripts/test-severance.mjs      (tests/test_session40.py runs this)
//
// Each case states its arithmetic from the cited rule (data/severance_rules.json) and the figure worked by hand; the
// calculator (lib/severance.ts) must match to a hundredth of a cent. Exits 1 on any mismatch.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { compute } from "../lib/severance.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const rules = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "severance_rules.json"), "utf-8"));

const cases = [
  // Texas: oil 4.6 percent of market value (Comptroller); fee $0.00625 per barrel
  { name: "TX oil, base: 1,000 bbl x $70 = $70,000 x 4.6% = $3,220.00; fee 1,000 x $0.00625 = $6.25",
    x: { state: "TX", product: "oil", volume: 1000, price: 70 }, base: 3220, with: 3220, fee: 6.25 },
  { name: "TX oil, EOR 2.3%: $70,000 x 2.3% = $1,610.00",
    x: { state: "TX", product: "oil", volume: 1000, price: 70, option: { id: "tx_eor" } }, base: 3220, with: 1610 },
  { name: "TX oil, EOR with anthropogenic CO2 at the full 50% more: 2.3% x 0.5 = 1.15%; $70,000 x 1.15% = $805.00; with a 50% low-producing lease credit $402.50",
    x: { state: "TX", product: "oil", volume: 1000, price: 70, option: { id: "tx_eor_co2", param: 50 }, credit: { id: "tx_lp_oil", tierPct: 50 } }, base: 3220, with: 402.5 },
  { name: "TX gas, base: 10,000 Mcf x $3 = $30,000 x 7.5% = $2,250.00; fee 10,000 x $0.000667 = $6.67",
    x: { state: "TX", product: "gas", volume: 10000, price: 3 }, base: 2250, with: 2250, fee: 6.67 },
  { name: "TX gas, high-cost gas at a certified 2.5%: $30,000 x 2.5% = $750.00",
    x: { state: "TX", product: "gas", volume: 10000, price: 3, option: { id: "tx_hcg", param: 2.5 } }, base: 2250, with: 750 },
  { name: "TX gas, low-producing well at a 100% credit: $0.00",
    x: { state: "TX", product: "gas", volume: 10000, price: 3, option: { id: "tx_lp_gas", tierPct: 100 } }, base: 2250, with: 0 },
  { name: "TX condensate: 500 bbl x $60 = $30,000 x 4.6% = $1,380.00",
    x: { state: "TX", product: "condensate", volume: 500, price: 60 }, base: 1380, with: 1380 },
  // Louisiana: oil 12.5% (completed before July 1, 2025) or 6.5%; value less trucking, barging and pipeline fees
  { name: "LA oil, pre-2025 well, $2/bbl transport: 1,000 x ($70 - $2) = $68,000 x 12.5% = $8,500.00",
    x: { state: "LA", product: "oil", volume: 1000, price: 70, transport: 2, variant: "la_oil_pre2025" }, base: 8500, with: 8500 },
  { name: "LA oil, well completed after July 1, 2025: $68,000 x 6.5% = $4,420.00",
    x: { state: "LA", product: "oil", volume: 1000, price: 70, transport: 2, variant: "la_oil_post2025" }, base: 4420, with: 4420 },
  { name: "LA oil, stripper: $68,000 x 3.125% = $2,125.00",
    x: { state: "LA", product: "oil", volume: 1000, price: 70, transport: 2, variant: "la_oil_pre2025", option: { id: "la_stripper" } }, base: 8500, with: 2125 },
  { name: "LA oil, stripper at $19/bbl: value under $20, exempt: base 1,000 x $19 x 12.5% = $2,375.00, with $0.00",
    x: { state: "LA", product: "oil", volume: 1000, price: 19, variant: "la_oil_pre2025", option: { id: "la_stripper" } }, base: 2375, with: 0 },
  { name: "LA oil, horizontal well, FY 2027 80% exempt: $8,500 x 20% = $1,700.00",
    x: { state: "LA", product: "oil", volume: 1000, price: 70, transport: 2, variant: "la_oil_pre2025", option: { id: "la_oil_horizontal" } }, base: 8500, with: 1700 },
  { name: "LA oil, orphan well returned: $68,000 x 1.565% = $1,064.20",
    x: { state: "LA", product: "oil", volume: 1000, price: 70, transport: 2, variant: "la_oil_pre2025", option: { id: "la_oil_orphan" } }, base: 8500, with: 1064.2 },
  { name: "LA gas, 15.14 cents per Mcf (July 2026 to June 2027): 10,000 x $0.1514 = $1,514.00",
    x: { state: "LA", product: "gas", volume: 10000, price: 3 }, base: 1514, with: 1514 },
  { name: "LA gas, incapable gas well, 1.3 cents: 10,000 x $0.013 = $130.00",
    x: { state: "LA", product: "gas", volume: 10000, price: 3, option: { id: "la_gas_incapable" } }, base: 1514, with: 130 },
  { name: "LA gas, inactive well returned, 3.785 cents: 10,000 x $0.03785 = $378.50",
    x: { state: "LA", product: "gas", volume: 10000, price: 3, option: { id: "la_gas_inactive" } }, base: 1514, with: 378.5 },
  { name: "LA condensate: 500 x $60 = $30,000 x 12.5% = $3,750.00; deep well: $0.00",
    x: { state: "LA", product: "condensate", volume: 500, price: 60, option: { id: "la_cond_deep" } }, base: 3750, with: 0 },
  // New Mexico: severance 3.75%, emergency school 3.15% (oil) or 4% (gas), conservation, ad valorem production (the
  // unit's rate); taxable value = price less royalties to the US, state or a tribe, less trucking
  { name: "NM oil: 1,000 x $70 = $70,000 less 12.5% royalty ($8,750) less $1/bbl trucking ($1,000) = $60,250; 3.75% $2,259.375 + 3.15% $1,897.875 + 0.24% $144.60 + 1.0% $602.50 = $4,904.35",
    x: { state: "NM", product: "oil", volume: 1000, price: 70, royaltyPct: 12.5, trucking: 1, choice: 0.0024, adval: 1.0 }, base: 4904.35, with: 4904.35 },
  { name: "NM gas: 10,000 x $3 = $30,000; 3.75% $1,125 + 4% $1,200 + 0.19% $57 + ad valorem 0 = $2,382.00",
    x: { state: "NM", product: "gas", volume: 10000, price: 3 }, base: 2382, with: 2382 },
];

let bad = 0;
const near = (a, b) => Math.abs(a - b) < 1e-4;
for (const c of cases) {
  const r = compute(rules, c.x);
  const fee = r.fees.reduce((a, f) => a + f.amount, 0);
  const ok = near(r.baseTotal, c.base) && near(r.withTotal, c.with) && near(r.savings, c.base - c.with) && (c.fee === undefined || near(fee, c.fee));
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} ${c.name} | calculator: base ${r.baseTotal.toFixed(4)}, with ${r.withTotal.toFixed(4)}, fee ${fee.toFixed(4)}`);
}
// every option in the rules computes, and cites a source the file names
for (const [s, st] of Object.entries(rules.states)) {
  for (const [p, pr] of Object.entries(st.products)) {
    for (const o of pr.options) {
      const x = { state: s, product: p, volume: 100, price: 50 };
      if (o.group === "rate") x.option = { id: o.id, tierPct: 50 }; else x.credit = { id: o.id, tierPct: 50 };
      const r = compute(rules, x);
      const ok = Number.isFinite(r.withTotal) && r.withTotal <= r.baseTotal + 1e-9 && rules.sources[o.cite] !== undefined;
      if (!ok) { bad++; console.log(`FAIL option ${s} ${p} ${o.id}`); }
    }
    for (const b of pr.base) if (!rules.sources[b.cite]) { bad++; console.log(`FAIL cite ${b.id}`); }
  }
}
console.log(bad ? `${bad} FAILED` : `every case: the calculator matches the hand-computed figures (${cases.length} cases)`);
process.exit(bad ? 1 : 0);
