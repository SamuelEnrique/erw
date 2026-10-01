// Energy Research Warehouse (ERW) site, session 45: the severance lease tool against hand-computed leases.
//
//   node scripts/test-lease.mjs      (tests/test_session45.py runs this)
//
// 1. A three-well, two-month lease for each state (Texas, Louisiana, New Mexico), prices given in the file, each
//    well-month worked by hand from the cited rules (data/severance_rules.json); lib/lease.ts must match to a
//    hundredth of a cent: base, with the ticked rules, the potential savings and the flags.
// 2. The flag logic at each threshold: one side flags, the other does not.
// 3. No network: fetch, XMLHttpRequest, WebSocket, EventSource and sendBeacon are replaced by traps while the sample
//    and the test leases are parsed, analysed and written to CSV; not one is called. The page's own sources name none.
// Exits 1 on any failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { compute, creditPct } from "../lib/severance.ts";
import { analyzeLease, bestTicks, parseLease, SAMPLE_CSV, ticksFromFile, toCsv, TEMPLATE_CSV, COLUMNS } from "../lib/lease.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const rules = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "severance_rules.json"), "utf-8"));
const engine = { compute, creditPct };
const NO_PRICES = { oil: {}, gas: {} };
let bad = 0, n = 0;
const near = (a, b) => Math.abs(a - b) < 1e-4;
function check(ok, name, detail = "") {
  n++;
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} ${name}${detail ? ` | ${detail}` : ""}`);
}
const H = COLUMNS.join(",");
/** A CSV row from a partial record, in the template's column order. */
const row = (o) => COLUMNS.map((c) => { const v = String(o[c] ?? ""); return v.includes(",") ? `"${v}"` : v; }).join(",");
function run(rows, ticks, prices = NO_PRICES) {
  const p = parseLease([H, ...rows.map(row)].join("\n"), rules);
  if (p.errors.length) console.log("  parse errors:", JSON.stringify(p.errors));
  const t = ticksFromFile(rules, p.rows);
  return { p, a: analyzeLease(rules, engine, p.rows, { prices, ticks: ticks ?? t.ticks }) };
}
const line = (a, well, month, product) => a.lines.find((l) => l.well === well && l.month === month && l.product === product);
const flagIds = (l) => (l ? l.flags.filter((f) => !f.info).map((f) => f.id).sort().join(",") : "no line");

// --- 1. the hand-computed leases --------------------------------------------------------------------------------

function lease(name, rows, want) {
  const { p, a } = run(rows);
  check(p.errors.length === 0, `${name}: the file parses without an error`);
  for (const [well, month, product, base, withT, flags] of want.lines) {
    const l = line(a, well, month, product);
    check(!!l && near(l.base, base) && near(l.withTicked, withT) && flagIds(l) === flags,
      `${name} ${well} ${month} ${product}: base ${base}, with ticks ${withT}, flags [${flags}]`,
      l ? `tool: base ${l.base?.toFixed(4)}, with ${l.withTicked?.toFixed(4)}, flags [${flagIds(l)}]` : "no line");
  }
  check(near(a.lease.base, want.base), `${name}: lease base ${want.base}`, `tool ${a.lease.base.toFixed(4)}`);
  check(near(a.lease.withTicked, want.with), `${name}: lease with ticks ${want.with}`, `tool ${a.lease.withTicked.toFixed(4)}`);
  check(near(a.lease.potential, want.potential), `${name}: lease potential savings ${want.potential}`, `tool ${a.lease.potential.toFixed(4)}`);
  if (want.fees !== undefined) check(near(a.lease.fees, want.fees), `${name}: lease regulatory fees ${want.fees}`, `tool ${a.lease.fees.toFixed(4)}`);
  if (want.first) check(a.opportunities[0]?.id === want.first[0] && a.opportunities[0]?.well === want.first[1] && near(a.opportunities[0].savings, want.first[2]),
    `${name}: the largest potential saving first, ${want.first.join(" ")}`, JSON.stringify(a.opportunities[0]));
  return a;
}

// Texas. Oil 4.6% of value (or 4.6 cents a barrel, if more); gas 7.5% of value (Comptroller; Secs. 202.052, 201.052).
// TX-A, an oil well, ticks EOR (2.3%): 07 oil 600 x $70 = $42,000 x 4.6% = $1,932.00, EOR $966.00; gas 900 x $3 =
//   $2,700 x 7.5% = $202.50 (casinghead: well_type oil, no low-producing gas flag). 08 oil 580 x $65 = $37,700 x 4.6%
//   = $1,734.20, EOR $867.10; gas 880 x $3 = $2,640 x 7.5% = $198.00. Lease oil test: 600 / 31 = 19.35 bbl per well
//   per day in 07, (600 + 580) / 62 = 19.03 over 07 and 08, not under 15: no low-producing lease flag.
// TX-B, a gas well, ticks the low-producing gas credit: 07 2,500 Mcf x $3 = $7,500 x 7.5% = $562.50; no month before
//   in the file, so 07 itself: 2,500 / 31 = 80.65 Mcf a day, 90 or less; certified 2026-07 $1.31, $2.50 or less: 100%
//   credit, $0.00. 08 2,400 x $2.80 = $6,720 x 7.5% = $504.00; the months before held: 07, 80.65, flag; 2026-08
//   certified $1.36: $0.00.
// TX-C, a high-cost gas well, costs 0.5 times the median, completed 2024-01-01, ticks high-cost gas: rate 7.5% - 7.5%
//   x 0.5 / 2 = 5.625%. 07 40,000 x $3 = $120,000: base $9,000.00, with $6,750.00. 08 38,000 x $2.80 = $106,400:
//   base $7,980.00, with $5,985.00. 40,000 / 31 = 1,290 Mcf a day: no low-producing flag.
// Lease: base 1,932 + 202.50 + 1,734.20 + 198 + 562.50 + 504 + 9,000 + 7,980 = $22,113.20; with ticks 966 + 202.50
//   + 867.10 + 198 + 0 + 0 + 6,750 + 5,985 = $14,968.60; potential (the flagged rules only) 562.50 + 504 + 2,250 +
//   1,995 = $5,311.50. Fees: oil $0.00625 x 1,180 = $7.375; gas $0.000667 x 84,680 = $56.48156; $63.85656.
lease("TX lease", [
  { state: "TX", well_id: "TX-A", month: "2026-07", oil_bbl: 600, gas_mcf: 900, oil_price: 70, gas_price: 3, well_type: "oil", exemptions: "tx_eor" },
  { state: "TX", well_id: "TX-A", month: "2026-08", oil_bbl: 580, gas_mcf: 880, oil_price: 65, gas_price: 3, well_type: "oil" },
  { state: "TX", well_id: "TX-B", month: "2026-07", gas_mcf: 2500, gas_price: 3, well_type: "gas", exemptions: "tx_lp_gas" },
  { state: "TX", well_id: "TX-B", month: "2026-08", gas_mcf: 2400, gas_price: 2.8, well_type: "gas" },
  { state: "TX", well_id: "TX-C", month: "2026-07", gas_mcf: 40000, gas_price: 3, well_type: "gas", hcg_cost_ratio: 0.5, completion_date: "2024-01-01", exemptions: "tx_hcg" },
  { state: "TX", well_id: "TX-C", month: "2026-08", gas_mcf: 38000, gas_price: 2.8, well_type: "gas", hcg_cost_ratio: 0.5, completion_date: "2024-01-01" },
], {
  lines: [
    ["TX-A", "2026-07", "oil", 1932, 966, ""], ["TX-A", "2026-07", "gas", 202.5, 202.5, ""],
    ["TX-A", "2026-08", "oil", 1734.2, 867.1, ""], ["TX-A", "2026-08", "gas", 198, 198, ""],
    ["TX-B", "2026-07", "gas", 562.5, 0, "tx_lp_gas"], ["TX-B", "2026-08", "gas", 504, 0, "tx_lp_gas"],
    ["TX-C", "2026-07", "gas", 9000, 6750, "tx_hcg"], ["TX-C", "2026-08", "gas", 7980, 5985, "tx_hcg"],
  ],
  base: 22113.2, with: 14968.6, potential: 5311.5, fees: 63.85656, first: ["tx_hcg", "TX-C", 4245],
});

// Louisiana. Oil 12.5% of value (completed before July 1, 2025) or 6.5%, value less trucking, barging and pipeline
// fees; gas 15.14 cents per Mcf (July 2026 to June 2027) (La. R.S. 47:633; RIB 26-013, 26-014).
// LA-A, an oil well completed 2010-05-01, $2 a barrel transport, 70% water, ticks stripper: 07 250 bbl in 28 producing
//   days = 8.93 a day (10 or less: stripper; 25 or less with 50% water or more: incapable); ($70 - $2) x 250 =
//   $17,000 x 12.5% = $2,125.00; stripper 3.125% = $531.25 (saves $1,593.75), incapable 6.25% = $1,062.50. 08 270 bbl
//   in 30 days = 9.0 a day; ($65 - $2) x 270 = $17,010 x 12.5% = $2,126.25; stripper $531.5625 (saves $1,594.6875).
// LA-B, a horizontal gas well completed 2025-10-01 (on or after July 1, 2025: 18 months), 12,000 ft, ticks
//   horizontal: 07 7,000 Mcf x $0.1514 = $1,059.80; 7,000 / 31 = 225.8 Mcf a day, under 250: incapable, 1.3 cents,
//   $91.00; horizontal, month 10 of 18: 100% exempt, $0.00. 08 6,500 x $0.1514 = $984.10; 209.7 a day: incapable
//   $84.50; horizontal $0.00.
// LA-C, an oil well completed 2025-08-01: 6.5%. 07 3,000 bbl: ($70 - $2) x 3,000 = $204,000 x 6.5% = $13,260.00; 08
//   2,900 bbl: ($65 - $2) x 2,900 = $182,700 x 6.5% = $11,875.50. 96.8 bbl a day: no flag.
// Lease: base 2,125 + 2,126.25 + 1,059.80 + 984.10 + 13,260 + 11,875.50 = $31,430.65; with ticks 531.25 + 531.5625 +
//   0 + 0 + 13,260 + 11,875.50 = $26,198.3125; potential 1,593.75 + 1,594.6875 + 1,059.80 + 984.10 = $5,232.3375.
lease("LA lease", [
  { state: "LA", well_id: "LA-A", month: "2026-07", oil_bbl: 250, oil_price: 70, days_produced: 28, water_cut_pct: 70, completion_date: "2010-05-01", transport_per_bbl: 2, well_type: "oil", exemptions: "la_stripper" },
  { state: "LA", well_id: "LA-A", month: "2026-08", oil_bbl: 270, oil_price: 65, days_produced: 30, water_cut_pct: 70 },
  { state: "LA", well_id: "LA-B", month: "2026-07", gas_mcf: 7000, gas_price: 3, horizontal: "yes", completion_date: "2025-10-01", depth_ft: 12000, well_type: "gas", exemptions: "la_gas_horizontal" },
  { state: "LA", well_id: "LA-B", month: "2026-08", gas_mcf: 6500, gas_price: 3 },
  { state: "LA", well_id: "LA-C", month: "2026-07", oil_bbl: 3000, oil_price: 70, completion_date: "2025-08-01", transport_per_bbl: 2, water_cut_pct: 20 },
  { state: "LA", well_id: "LA-C", month: "2026-08", oil_bbl: 2900, oil_price: 65, water_cut_pct: 20 },
], {
  lines: [
    ["LA-A", "2026-07", "oil", 2125, 531.25, "la_incapable,la_stripper"], ["LA-A", "2026-08", "oil", 2126.25, 531.5625, "la_incapable,la_stripper"],
    ["LA-B", "2026-07", "gas", 1059.8, 0, "la_gas_horizontal,la_gas_incapable"], ["LA-B", "2026-08", "gas", 984.1, 0, "la_gas_horizontal,la_gas_incapable"],
    ["LA-C", "2026-07", "oil", 13260, 13260, ""], ["LA-C", "2026-08", "oil", 11875.5, 11875.5, ""],
  ],
  base: 31430.65, with: 26198.3125, potential: 5232.3375, first: ["la_stripper", "LA-A", 3188.4375],
});

// New Mexico. Severance 3.75%, emergency school 3.15% (oil) or 4% (gas), conservation 0.24% (oil) or 0.19% (gas), and
// the district's ad valorem production rate (TRD's 2026 table), on value less royalties and trucking (TRD).
// NM-A, LEA 01 suffix 2510 (1.6342%), 12.5% royalty, $1 trucking: oil rate 8.7742%, gas 9.5742%.
//   07 oil 1,000 x $70 = $70,000 - $8,750 - $1,000 = $60,250 x 8.7742% = $5,286.4555; gas 3,000 x $3 = $9,000 -
//   $1,125 - $3,000 = $4,875 x 9.5742% = $466.74225. 08 oil 900 x $65 = $58,500 - $7,312.50 - $900 = $50,287.50 x
//   8.7742% = $4,412.325825; gas 2,800 x $2.80 = $7,840 - $980 - $2,800 = $4,060 x 9.5742% = $388.71252.
// NM-B, SAN JUAN 02 suffix 4510 (1.3737%), 12.5% royalty: gas 9.3137%. 07 20,000 x $3 = $60,000 - $7,500 = $52,500 x
//   9.3137% = $4,889.6925; 08 19,000 x $2.80 = $53,200 - $6,650 = $46,550 x 9.3137% = $4,335.52735.
// NM-C, no district (ad valorem left out, flagged): oil 7.14%. 07 100 x $70 = $7,000 x 7.14% = $499.80; 08 100 x $65 =
//   $6,500 x 7.14% = $464.10.
// Lease: $20,743.355945; no reduced New Mexico rate in the rules file, so with ticks the same and no savings.
const nm = lease("NM lease", [
  { state: "NM", well_id: "NM-A", month: "2026-07", oil_bbl: 1000, gas_mcf: 3000, oil_price: 70, gas_price: 3, nm_district: "2510", royalty_pct: 12.5, trucking_per_unit: 1 },
  { state: "NM", well_id: "NM-A", month: "2026-08", oil_bbl: 900, gas_mcf: 2800, oil_price: 65, gas_price: 2.8 },
  { state: "NM", well_id: "NM-B", month: "2026-07", gas_mcf: 20000, gas_price: 3, nm_district: "SAN JUAN, district 02, suffix 4510", royalty_pct: 12.5 },
  { state: "NM", well_id: "NM-B", month: "2026-08", gas_mcf: 19000, gas_price: 2.8 },
  { state: "NM", well_id: "NM-C", month: "2026-07", oil_bbl: 100, oil_price: 70 },
  { state: "NM", well_id: "NM-C", month: "2026-08", oil_bbl: 100, oil_price: 65 },
], {
  lines: [
    ["NM-A", "2026-07", "oil", 5286.4555, 5286.4555, ""], ["NM-A", "2026-07", "gas", 466.74225, 466.74225, ""],
    ["NM-A", "2026-08", "oil", 4412.325825, 4412.325825, ""], ["NM-A", "2026-08", "gas", 388.71252, 388.71252, ""],
    ["NM-B", "2026-07", "gas", 4889.6925, 4889.6925, ""], ["NM-B", "2026-08", "gas", 4335.52735, 4335.52735, ""],
    ["NM-C", "2026-07", "oil", 499.8, 499.8, ""], ["NM-C", "2026-08", "oil", 464.1, 464.1, ""],
  ],
  base: 20743.355945, with: 20743.355945, potential: 0,
});
{
  const a = line(nm, "NM-A", "2026-07", "oil").flags.find((f) => f.id === "nm_district");
  const c = line(nm, "NM-C", "2026-07", "oil").flags.find((f) => f.id === "nm_district");
  check(a?.info && a.test.includes("LEA, district 01, suffix 2510") && a.test.includes("1.6342%"), "NM district flag names the district and its rate", a?.test);
  check(c?.info && c.test.includes("left out") && c.test.includes("0.7105%") && c.test.includes("1.7249%"), "NM without a district: ad valorem left out, the range stated", c?.test);
}

// --- 2. the flags at each threshold ---------------------------------------------------------------------------------

function flags(rows, well, month, product) {
  const { a } = run(rows);
  return flagIds(line(a, well, month, product)).split(",").filter(Boolean);
}
const has = (ids, id) => ids.includes(id);
const J = "2026-07";  // 31 days
// TX low-producing oil lease: less than 15 bbl per well per day (two wells: 464 / 31 = 14.97; 465 / 31 = 15.00)
check(has(flags([{ state: "TX", well_id: "a", month: J, oil_bbl: 464, oil_price: 70 }, { state: "TX", well_id: "b", month: J, oil_bbl: 464, oil_price: 70 }], "a", J, "oil"), "tx_lp_oil"), "TX lease oil 14.97 bbl/well/day: flags tx_lp_oil");
check(!has(flags([{ state: "TX", well_id: "a", month: J, oil_bbl: 465, oil_price: 70 }, { state: "TX", well_id: "b", month: J, oil_bbl: 465, oil_price: 70 }], "a", J, "oil"), "tx_lp_oil"), "TX lease oil 15.00 bbl/well/day: no flag (less than 15)");
// or less than 5% oil per barrel of water: 95.3% water gives 4.7 / 95.3 = 4.93%; 95.2% gives 5.04%
check(has(flags([{ state: "TX", well_id: "a", month: J, oil_bbl: 3000, oil_price: 70, water_cut_pct: 95.3 }], "a", J, "oil"), "tx_lp_oil"), "TX lease oil 4.93% oil per barrel of water: flags tx_lp_oil");
check(!has(flags([{ state: "TX", well_id: "a", month: J, oil_bbl: 3000, oil_price: 70, water_cut_pct: 95.2 }], "a", J, "oil"), "tx_lp_oil"), "TX lease oil 5.04% oil per barrel of water: no flag");
// TX low-producing gas: no more than 90 Mcf a day (2,790 / 31 = 90.0; 2,791 = 90.03); never casinghead gas
check(has(flags([{ state: "TX", well_id: "g", month: J, gas_mcf: 2790, gas_price: 3 }], "g", J, "gas"), "tx_lp_gas"), "TX gas 90.0 Mcf/day: flags tx_lp_gas");
check(!has(flags([{ state: "TX", well_id: "g", month: J, gas_mcf: 2791, gas_price: 3 }], "g", J, "gas"), "tx_lp_gas"), "TX gas 90.03 Mcf/day: no flag");
check(!has(flags([{ state: "TX", well_id: "g", month: J, gas_mcf: 1000, gas_price: 3, well_type: "oil" }], "g", J, "gas"), "tx_lp_gas"), "TX casinghead gas (an oil well): no low-producing gas flag");
// the three months before, when the file holds them: 3,000 a month in April to June (98 a day) flags nothing in July
check(!has(flags(["04", "05", "06"].map((m) => ({ state: "TX", well_id: "g", month: `2026-${m}`, gas_mcf: 3000, gas_price: 3 })).concat([{ state: "TX", well_id: "g", month: J, gas_mcf: 100, gas_price: 3 }]), "g", J, "gas"), "tx_lp_gas"), "TX gas: July judged on April to June (about 98 a day), not on July's 100 Mcf: no flag");
// TX high-cost gas: within 120 months of completion
check(has(flags([{ state: "TX", well_id: "h", month: J, gas_mcf: 30000, gas_price: 3, hcg_cost_ratio: 1, completion_date: "2016-08-01" }], "h", J, "gas"), "tx_hcg"), "TX high-cost gas, month 120 of 120: flags tx_hcg");
check(!has(flags([{ state: "TX", well_id: "h", month: J, gas_mcf: 30000, gas_price: 3, hcg_cost_ratio: 1, completion_date: "2016-07-01" }], "h", J, "gas"), "tx_hcg"), "TX high-cost gas, 120 months after completion: no flag");
// two-year inactive: 24 months or more (the reader's inactive_months, or 24 zero months in the file)
check(has(flags([{ state: "TX", well_id: "i", month: J, oil_bbl: 900, oil_price: 70, inactive_months: 24 }], "i", J, "oil"), "tx_oil_inactive"), "TX inactive 24 months: flags tx_oil_inactive");
check(!has(flags([{ state: "TX", well_id: "i", month: J, oil_bbl: 900, oil_price: 70, inactive_months: 23 }], "i", J, "oil"), "tx_oil_inactive"), "TX inactive 23 months: no flag");
{
  const zeros = Array.from({ length: 24 }, (_, k) => ({ state: "LA", well_id: "z", month: new Date(Date.UTC(2024, 6 + k, 1)).toISOString().slice(0, 7), oil_bbl: 0, gas_mcf: 0 }));
  check(has(flags([...zeros, { state: "LA", well_id: "z", month: J, oil_bbl: 900, oil_price: 70 }], "z", J, "oil"), "la_oil_inactive"), "LA: 24 zero months in the file before July 2026: flags la_oil_inactive");
  check(!has(flags([...zeros.slice(1), { state: "LA", well_id: "z", month: J, oil_bbl: 900, oil_price: 70 }], "z", J, "oil"), "la_oil_inactive"), "LA: 23 zero months: no flag");
}
// LA stripper: 10 bbl or less per producing day (300 / 30 = 10.0; 301 / 30 = 10.03); calendar days when not given
check(has(flags([{ state: "LA", well_id: "s", month: J, oil_bbl: 300, oil_price: 70, days_produced: 30 }], "s", J, "oil"), "la_stripper"), "LA 10.0 bbl per producing day: flags la_stripper");
check(!has(flags([{ state: "LA", well_id: "s", month: J, oil_bbl: 301, oil_price: 70, days_produced: 30 }], "s", J, "oil"), "la_stripper"), "LA 10.03 bbl per producing day: no flag");
check(has(flags([{ state: "LA", well_id: "s", month: J, oil_bbl: 310, oil_price: 70 }], "s", J, "oil"), "la_stripper"), "LA 310 bbl over July's 31 calendar days (days_produced blank): flags la_stripper");
// LA incapable oil: 25 or less per producing day with 50% salt water or more
check(has(flags([{ state: "LA", well_id: "c", month: J, oil_bbl: 750, oil_price: 70, days_produced: 30, water_cut_pct: 50 }], "c", J, "oil"), "la_incapable"), "LA 25.0 bbl/day, 50% water: flags la_incapable");
check(!has(flags([{ state: "LA", well_id: "c", month: J, oil_bbl: 750, oil_price: 70, days_produced: 30, water_cut_pct: 49.9 }], "c", J, "oil"), "la_incapable"), "LA 25.0 bbl/day, 49.9% water: no flag");
check(!has(flags([{ state: "LA", well_id: "c", month: J, oil_bbl: 751, oil_price: 70, days_produced: 30, water_cut_pct: 80 }], "c", J, "oil"), "la_incapable"), "LA 25.03 bbl/day: no flag");
// LA incapable gas well: under 250 Mcf a day over the month (7,750 / 31 = 250.0)
check(has(flags([{ state: "LA", well_id: "q", month: J, gas_mcf: 7749, gas_price: 3, well_type: "gas" }], "q", J, "gas"), "la_gas_incapable"), "LA gas 249.97 Mcf/day: flags la_gas_incapable");
check(!has(flags([{ state: "LA", well_id: "q", month: J, gas_mcf: 7750, gas_price: 3, well_type: "gas" }], "q", J, "gas"), "la_gas_incapable"), "LA gas 250.0 Mcf/day: no flag");
check(!has(flags([{ state: "LA", well_id: "q", month: J, gas_mcf: 1000, gas_price: 3, well_type: "oil" }], "q", J, "gas"), "la_gas_incapable"), "LA gas from a well designated an oil well: no flag");
// LA deep: more than 15,000 ft, production after July 31, 1994, 24 months
check(!has(flags([{ state: "LA", well_id: "d", month: J, gas_mcf: 9000, gas_price: 3, depth_ft: 15000 }], "d", J, "gas"), "la_gas_deep"), "LA 15,000 ft: no deep flag");
check(has(flags([{ state: "LA", well_id: "d", month: J, gas_mcf: 9000, gas_price: 3, depth_ft: 15001 }], "d", J, "gas"), "la_gas_deep"), "LA 15,001 ft: flags la_gas_deep");
check(!has(flags([{ state: "LA", well_id: "d", month: J, gas_mcf: 9000, gas_price: 3, depth_ft: 16000, completion_date: "1994-07-31" }], "d", J, "gas"), "la_gas_deep"), "LA deep well completed July 31, 1994: no flag");
check(has(flags([{ state: "LA", well_id: "d", month: J, oil_bbl: 900, oil_price: 70, depth_ft: 16000, completion_date: "2024-08-01" }], "d", J, "oil"), "la_oil_deep"), "LA deep oil well, month 24 of 24: flags la_oil_deep");
check(!has(flags([{ state: "LA", well_id: "d", month: J, oil_bbl: 900, oil_price: 70, depth_ft: 16000, completion_date: "2024-07-01" }], "d", J, "oil"), "la_oil_deep"), "LA deep oil well, 24 months after completion: no flag");
// LA horizontal: gas completed on or after July 1, 2025, 18 months; oil 24 months
check(has(flags([{ state: "LA", well_id: "z", month: "2026-12", gas_mcf: 9000, gas_price: 3, horizontal: "yes", completion_date: "2025-07-01" }], "z", "2026-12", "gas"), "la_gas_horizontal"), "LA horizontal gas, month 18 of 18: flags la_gas_horizontal");
check(!has(flags([{ state: "LA", well_id: "z", month: "2027-01", gas_mcf: 9000, gas_price: 3, horizontal: "yes", completion_date: "2025-07-01" }], "z", "2027-01", "gas"), "la_gas_horizontal"), "LA horizontal gas, 18 months after completion: no flag");
check(has(flags([{ state: "LA", well_id: "z", month: "2027-01", oil_bbl: 900, oil_price: 70, horizontal: "yes", completion_date: "2025-07-01" }], "z", "2027-01", "oil"), "la_oil_horizontal"), "LA horizontal oil, month 19 of 24: flags la_oil_horizontal");
// the Texas credit follows the certified price of the production month; a month not published gives none
{
  const { a } = run([{ state: "TX", well_id: "g", month: "2026-09", gas_mcf: 1000, gas_price: 3 }]);
  const f = line(a, "g", "2026-09", "gas").flags.find((x) => x.id === "tx_lp_gas");
  check(f && f.savings === 0 && f.notes.some((s) => s.includes("no certified price")), "TX gas in 2026-09, no certified price published: flagged, no credit computed");
}
// Louisiana's oil rate follows the completion date (July 1, 2025)
{
  const { a } = run([{ state: "LA", well_id: "r", month: J, oil_bbl: 1000, oil_price: 70, completion_date: "2025-07-01" }, { state: "LA", well_id: "s", month: J, oil_bbl: 1000, oil_price: 70, completion_date: "2025-06-30" }]);
  check(near(line(a, "r", J, "oil").base, 4550) && near(line(a, "s", J, "oil").base, 8750), "LA oil: completed 2025-07-01 6.5% ($4,550), 2025-06-30 12.5% ($8,750)");
}
// the default price: the month's warehouse mean, labeled, when the file has none; none held means no tax computed
{
  const book = { oil: { [J]: { value: 70, n: 22, label: "WTI Cushing, test label" } }, gas: {} };
  const { a } = run([{ state: "TX", well_id: "p", month: J, oil_bbl: 1000, gas_mcf: 100 }], undefined, book);
  const o = line(a, "p", J, "oil"), g = line(a, "p", J, "gas");
  check(o.price === 70 && o.priceSource === "WTI Cushing, test label" && near(o.base, 3220), "blank oil price: the month's WTI mean, labeled");
  check(g.price === null && g.base === null && a.issues.length === 1, "blank gas price and no Henry Hub mean held: not computed, reported");
}
// the parser: errors are named with their line; aliases, tabs, quotes and districts by suffix
{
  const p = parseLease("state,well,month,oil\nTX,a,2026-13,1\nZZ,b,2026-07,1\nTX,c,2026-07,-4\nTX,d,2026-07,5\nTX,d,2026-07,6\n", rules);
  check(p.errors.length === 4 && p.rows.length === 2, "parser: a bad month, an unknown state and a duplicate are skipped; a negative volume is reported", JSON.stringify(p.errors));
  const t = parseLease('state\twell_id\tmonth\tnm_district\n"NM"\t"x, y"\t2026-07\t510\n', rules);
  check(t.rows[0]?.well === "x, y" && t.rows[0].facts.district?.label === "CHAVES, district 01, suffix 0510", "parser: tab-separated, quoted, suffix 510 finds CHAVES 01/0510");
}

// --- 3. no network ---------------------------------------------------------------------------------------------

{
  let calls = 0;
  const trap = () => { calls++; throw new Error("network call"); };
  const saved = { fetch: globalThis.fetch, XMLHttpRequest: globalThis.XMLHttpRequest, WebSocket: globalThis.WebSocket, EventSource: globalThis.EventSource };
  globalThis.fetch = trap;
  globalThis.XMLHttpRequest = function () { trap(); };
  globalThis.WebSocket = function () { trap(); };
  globalThis.EventSource = function () { trap(); };
  const nav = Object.getOwnPropertyDescriptor(globalThis, "navigator");
  Object.defineProperty(globalThis, "navigator", { value: { sendBeacon: trap }, configurable: true });
  try {
    const p = parseLease(SAMPLE_CSV, rules);
    const a = analyzeLease(rules, engine, p.rows, { prices: NO_PRICES, ticks: ticksFromFile(rules, p.rows).ticks });
    const b = analyzeLease(rules, engine, p.rows, { prices: NO_PRICES, ticks: bestTicks(a, rules) });
    toCsv(b, rules.version);
    parseLease(TEMPLATE_CSV, rules);
  } finally {
    Object.assign(globalThis, saved);
    if (nav) Object.defineProperty(globalThis, "navigator", nav);
  }
  check(calls === 0, "no network: parsing, analysing and writing the sample calls no fetch, XMLHttpRequest, WebSocket, EventSource or sendBeacon", `${calls} calls`);
  const banned = /\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|"use server"|<form|\baction=|\bimport\s*\(/;
  for (const f of ["app/severance/lease/LeaseTool.tsx", "lib/lease.ts"]) {
    const src = fs.readFileSync(path.join(here, "..", f), "utf-8");
    const m = src.match(banned);
    check(!m, `no network in ${f}: no fetch, XMLHttpRequest, beacon, socket, server action, form or dynamic import`, m ? m[0] : "");
  }
  // the page's server part reads only the warehouse prices; it passes nothing of the reader's back
  const page = fs.readFileSync(path.join(here, "..", "app/severance/lease/page.tsx"), "utf-8");
  check(!/"use server"|searchParams|cookies\(|headers\(/.test(page), "the server page takes no request data (no server action, search parameters, cookies or headers)");
  // session 46: no prefetch on this page: its own links say prefetch={false}; the shared ones (header, nav, footer,
  // citations) are components/SiteLink, which turns prefetch off on /severance/lease
  const links = page.match(/<Link\s[^>]*>/g) ?? [];
  check(links.length > 0 && links.every((l) => l.includes("prefetch={false}")), `every link on the lease page is prefetch={false} (${links.length})`);
  const site = fs.readFileSync(path.join(here, "..", "components/SiteLink.tsx"), "utf-8");
  check(/NO_PREFETCH = \[[^\]]*"\/severance\/lease"/.test(site) && site.includes("prefetch={noPrefetch(path) ? false"), "SiteLink turns prefetch off on /severance/lease");
  for (const f of ["app/layout.tsx", "components/Nav.tsx", "components/Cite.tsx"]) {
    const src = fs.readFileSync(path.join(here, "..", f), "utf-8");
    check(src.includes('SiteLink as Link } from "@/components/SiteLink"') && !src.includes('from "next/link"'), `${f} links through SiteLink`);
  }
}

// --- the sample -------------------------------------------------------------------------------------------------

{
  const p = parseLease(SAMPLE_CSV, rules);
  check(p.errors.length === 0 && p.rows.length === 19 && p.rows.every((r) => r.well.startsWith("FICTIONAL-")), "the sample: 19 well-months, every well labeled FICTIONAL, no error");
  check(SAMPLE_CSV.startsWith("# SAMPLE: FICTIONAL WELLS"), "the sample's first line says its wells are fictional");
  const prices = { oil: {}, gas: {} };
  for (const m of ["2026-06", "2026-07", "2026-08"]) { prices.oil[m] = { value: 70, n: 1, label: "test" }; prices.gas[m] = { value: 3, n: 1, label: "test" }; }
  const a = analyzeLease(rules, engine, p.rows, { prices, ticks: {} });
  const fired = [...new Set(a.lines.flatMap((l) => l.flags.filter((f) => !f.info).map((f) => `${l.well}:${f.id}`)))].sort();
  console.log(`  flags on the sample: ${fired.join(" ")}`);
  const want = ["FICTIONAL-LA-1:la_incapable", "FICTIONAL-LA-1:la_stripper", "FICTIONAL-LA-2:la_cond_deep", "FICTIONAL-LA-2:la_gas_deep",
    "FICTIONAL-LA-2:la_gas_horizontal", "FICTIONAL-LA-2:la_gas_incapable", "FICTIONAL-TX-1:tx_lp_oil", "FICTIONAL-TX-2:tx_lp_gas", "FICTIONAL-TX-3:tx_hcg"];
  check(JSON.stringify(fired) === JSON.stringify(want), "the sample fires the flags it was written to show");
}

// session 49: "Load a real lease": the RRC table's rows become the tool's file (lib/rrclease.ts). The fixture is made up
// (FICTIONAL lease names, the table's columns), not RRC data, which is internal and not in git.
{
  const { parseRrc, leaseCsv, splitCsv } = await import("../lib/rrclease.ts");
  const fx = [
    "# a made-up fixture in the shape of rrc_lease_production_monthly",
    "entity,variable,ts_utc,value,unit,freq,geo,market,node,source,source_url,retrieved_at,vintage,x_county,x_district,x_oil_gas_code,x_lease_no,x_lease_name,x_operator_no,x_operator_name,x_field_no,x_field_name,x_gas_well_no,x_wells",
    'rrc:O-10-99999,oil_bbl,2026-06-01T00:00:00Z,300,bbl,P1M,US-TX,,,rrc:pdq_dump,u,r,v,MARTIN,08,O,99999,"FICTIONAL ""A"", UNIT",1,FICTIONAL OPERATING,2,FIELD X,,1',
    'rrc:O-10-99999,casinghead_gas_mcf,2026-06-01T00:00:00Z,900,Mcf,P1M,US-TX,,,rrc:pdq_dump,u,r,v,MARTIN,08,O,99999,"FICTIONAL ""A"", UNIT",1,FICTIONAL OPERATING,2,FIELD X,,1',
    'rrc:O-10-99999,oil_bbl,2026-05-01T00:00:00Z,310,bbl,P1M,US-TX,,,rrc:pdq_dump,u,r,v,MARTIN,08,O,99999,"FICTIONAL ""A"", UNIT",1,FICTIONAL OPERATING,2,FIELD X,,1',
    'rrc:G-10-88888,gas_mcf,2026-06-01T00:00:00Z,5000,Mcf,P1M,US-TX,,,rrc:pdq_dump,u,r,v,MARTIN,08,G,88888,FICTIONAL GAS,1,FICTIONAL OPERATING,3,FIELD Y,1,1',
    'rrc:G-10-88888,condensate_bbl,2026-06-01T00:00:00Z,12,bbl,P1M,US-TX,,,rrc:pdq_dump,u,r,v,MARTIN,08,G,88888,FICTIONAL GAS,1,FICTIONAL OPERATING,3,FIELD Y,1,1',
  ].join("\n");
  check(JSON.stringify(splitCsv('a,"b ""c"", d",e')) === JSON.stringify(["a", 'b "c", d', "e"]), "rrclease: CSV quoting (a doubled quote, a comma inside quotes)");
  const t = parseRrc(fx);
  const o = t.leases.get("rrc:O-10-99999"), g = t.leases.get("rrc:G-10-88888");
  check(t.leases.size === 2 && o.name === 'FICTIONAL "A", UNIT' && o.wells === 1 && Object.keys(o.months).length === 2, "rrclease: two leases parsed, the quoted name and the months");
  const po = parseLease(leaseCsv(o, COLUMNS), rules), pg = parseLease(leaseCsv(g, COLUMNS), rules);
  check(po.errors.length === 0 && po.rows.length === 2 && pg.errors.length === 0 && pg.rows.length === 1, "rrclease: the made file parses in the lease tool without error", JSON.stringify([po.errors, pg.errors]));
  const jun = po.rows.find((r) => r.month === "2026-06"), may = po.rows.find((r) => r.month === "2026-05");
  check(jun.vol.oil === 300 && jun.vol.gas === 900 && may.vol.oil === 310 && !may.vol.gas && pg.rows[0].vol.gas === 5000 && pg.rows[0].vol.condensate === 12,
    "rrclease: oil, casinghead gas as gas, gas and condensate land in their columns", JSON.stringify([jun.vol, may.vol, pg.rows[0].vol]));
  const banned = /\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|"use server"|\bimport\s*\(/;
  check(!banned.test(fs.readFileSync(path.join(here, "..", "lib", "rrclease.ts"), "utf8")), "rrclease: no network in lib/rrclease.ts");
}

console.log(bad ? `${bad} of ${n} FAILED` : `every check passes (${n}): the lease tool matches the hand-computed leases and thresholds, and makes no network call`);
process.exit(bad ? 1 : 0);
