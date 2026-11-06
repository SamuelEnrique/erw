// Energy Research Warehouse (ERW) site, session 294: the EV game against hand-computed figures.
//
//   node scripts/test-ev.mjs        (tests/test_session294.py runs this)
//
// Works the method note's example by hand (docs/methods/ev_game.md: the defaults in California) and checks
// lib/ev.ts to a hundredth of a cent, then the edge cases (an EV that costs no more, one that saves nothing), and that
// data/ev_prices.json holds every state with a dated, sourced power price and gasoline price. Exits 1 on any failure.
import fs from "node:fs";
import { chargePrice, cumulative, DEFAULTS, evPer100, gasPer100, keyed, NO_CREDIT_LINE, verdict } from "../lib/ev.ts";

let bad = 0;
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const near = (a, b, e = 1e-6) => Math.abs(a - b) < e;
const d = JSON.parse(fs.readFileSync(new URL("../data/ev_prices.json", import.meta.url), "utf-8"));
const ca = d.states.find((s) => s.code === "CA");
const D = Object.fromEntries(Object.entries(DEFAULTS).map(([k, v]) => [k, v.value]));

// by hand, California at the defaults
const g100 = (100 / 27) * 6.227, e100 = 100 * 0.31 * (336.1 / 1000);
const gy = g100 * 150, ey = e100 * 150, save = gy - ey, extra = 33600 - 28600;
let pv = 0; for (let t = 1; t <= 8; t++) pv += save / 1.05 ** t;
check(ca.power.value === 336.1 && ca.gas.value === 6.227 && ca.gas.where === "state", `California: ${ca.power.value} USD/MWh (${ca.power.ts}), ${ca.gas.value} USD/gal (${ca.gas.ts}), its own gasoline series`);
const v = verdict({ ...D, gasUsdPerGal: ca.gas.value, powerUsdPerMwh: ca.power.value, credit: 0 });
check(near(v.gasPer100, g100) && near(gasPer100(27, 6.227), 23.062963, 1e-6), `100 miles on gasoline: 100 / 27 x $6.227 = $${g100.toFixed(4)} | ${v.gasPer100.toFixed(4)}`);
check(near(v.evPer100, e100) && near(evPer100(0.31, 336.1), 10.4191, 1e-9), `100 miles on electricity: 100 x 0.31 x $0.3361 = $${e100.toFixed(4)} | ${v.evPer100.toFixed(4)}`);
check(near(v.saveYear, save) && Math.round(v.saveYear) === 1897, `a year, 15,000 miles: $${gy.toFixed(2)} - $${ey.toFixed(2)} = $${save.toFixed(2)} saved | ${v.saveYear.toFixed(2)}`);
check(near(v.payback, extra / save) && v.payback.toFixed(1) === "2.6", `payback: $5,000 / $${save.toFixed(2)} = ${(extra / save).toFixed(3)} years | ${v.payback.toFixed(3)}`);
check(near(v.npv, pv - extra) && Math.round(v.npv) === 7258, `NPV, 8 years at 5 percent: $${(pv - extra).toFixed(2)} | ${v.npv.toFixed(2)}`);
// edges
check(verdict({ ...D, gasUsdPerGal: 4, powerUsdPerMwh: 150, evCar: 28000, credit: 0 }).payback === 0, "an EV that costs no more pays back at once");
check(verdict({ ...D, gasUsdPerGal: 2, powerUsdPerMwh: 600, credit: 0 }).payback === null, "an EV that saves nothing never pays back");
check(near(verdict({ ...D, gasUsdPerGal: 4, powerUsdPerMwh: 150, credit: 5000 }).extra, 0), "a $5,000 credit takes the $5,000 gap to nothing");
check(near(verdict({ ...D, gasUsdPerGal: 4, powerUsdPerMwh: 150, rate: 0, years: 1, credit: 0 }).npv, verdict({ ...D, gasUsdPerGal: 4, powerUsdPerMwh: 150, rate: 0, years: 1, credit: 0 }).saveYear - 5000), "at 0 percent over 1 year the NPV is one year's saving less the extra");
// Session 3276: three households worked by hand (docs/methods/ev_game.md, "One screen"), the prices from data/ev_prices.json
// (built 15 October 2026). Each figure below was computed on paper first; the test holds lib/ev.ts to it.
//
// Household 1, the United States as a whole at the defaults, credit off (the page's opening figures):
//   power 183.1 USD/MWh = $0.1831 a kWh; gasoline $4.354 a gallon (eia:EMM_EPMR_PTE_NUS_DPG)
//   100 miles: gasoline 100 / 27 x 4.354 = $16.1259; electricity 100 x 0.31 x 0.1831 = $5.6761
//   a year, 15,000 miles: 16.1259 x 150 = $2,418.89; 5.6761 x 150 = $851.42; saved $1,567.47
//   extra to buy: 33,600 - 28,600 = $5,000; payback 5,000 / 1,567.47 = 3.19 years (shown 3.2)
//   8 years at 5 percent: (1 - 1.05^-8) / 0.05 = (1 - 0.676839) / 0.05 = 6.463213; 1,567.47 x 6.463213 = $10,130.92;
//   NPV 10,130.92 - 5,000 = $5,130.92 (shown $5,131)
// Household 2, Texas: 12,000 miles, 30 mpg, 0.28 kWh a mile, $25,000 and $35,000, 10 years, 5 percent, the credit on
//   at $7,500, 80 percent charged at home and the rest at a public charger the family says asks 45 cents a kWh:
//   gasoline 100 / 30 x 3.874 = $12.9133 per 100 miles; a year x 120 = $1,549.60
//   charging 0.8 x 158.8 + 0.2 x 450 = 127.04 + 90 = 217.04 USD/MWh; 100 x 0.28 x 0.21704 = $6.0771; a year $729.25
//   saved 1,549.60 - 729.25 = $820.35; extra 35,000 - 25,000 - 7,500 = $2,500; payback 2,500 / 820.35 = 3.05 years
//   10 years at 5 percent: (1 - 0.613913) / 0.05 = 7.721735; 820.35 x 7.721735 = $6,334.49; NPV $3,834.49
// Household 3, Ohio: 8,000 miles, 40 mpg, 0.35 kWh a mile, $30,000 gasoline and $29,000 EV, 5 years, 3 percent, credit off:
//   gasoline 100 / 40 x 3.829 = $9.5725 per 100; a year x 80 = $765.80; electricity 100 x 0.35 x 0.1945 = $6.8075; $544.60
//   saved $221.20; the EV costs $1,000 less, so payback is at once (0)
//   5 years at 3 percent: (1 - 1.03^-5) / 0.03 = (1 - 0.862609) / 0.03 = 4.579707; 221.20 x 4.579707 = $1,013.03; NPV
//   1,013.03 + 1,000 = $2,013.03
{
  const st = (c) => (c === "US" ? d.us : d.states.find((s) => s.code === c));
  const [us, tx, oh] = ["US", "TX", "OH"].map(st);
  check(us.power.value === 183.1 && us.gas.value === 4.354 && tx.power.value === 158.8 && tx.gas.value === 3.874 && oh.power.value === 194.5 && oh.gas.value === 3.829, "the three households' prices as the file holds them (US, Texas, Ohio)");
  const h1 = verdict({ ...D, gasUsdPerGal: us.gas.value, powerUsdPerMwh: us.power.value, credit: 0 });
  check(near(h1.gasYear, 2418.89, 0.005) && near(h1.evYear, 851.42, 0.006) && near(h1.saveYear, 1567.47, 0.006) && h1.payback.toFixed(1) === "3.2" && near(h1.npv, 5130.92, 0.01), `household 1 (US, defaults): saved $${h1.saveYear.toFixed(2)} a year, payback ${h1.payback.toFixed(2)} years, NPV $${h1.npv.toFixed(2)} (by hand 1,567.47, 3.19, 5,130.92)`);
  const k = keyed(us.power.value, us.gas.value);
  check(k.power_cents === 18.31 && k.gas === 4.354 && k.payback === 3.2 && k.npv === 5131, `the page's keyed figures for the US: ${JSON.stringify(k)}`);
  const x2 = { ...D, miles: 12000, mpg: 30, kwhPerMile: 0.28, gasCar: 25000, evCar: 35000, years: 10, rate: 5, credit: 7500, homeShare: 80, publicUsdPerMwh: 450, gasUsdPerGal: tx.gas.value, powerUsdPerMwh: tx.power.value };
  const h2 = verdict(x2);
  check(near(chargePrice(x2), 217.04, 1e-9) && near(h2.gasYear, 1549.6, 1e-6) && near(h2.evYear, 729.25, 0.006) && near(h2.saveYear, 820.35, 0.006) && near(h2.payback, 3.05, 0.005) && near(h2.npv, 3834.49, 0.01), `household 2 (Texas, 80 percent at home, credit on): charging ${chargePrice(x2).toFixed(2)} USD/MWh, saved $${h2.saveYear.toFixed(2)}, payback ${h2.payback.toFixed(2)}, NPV $${h2.npv.toFixed(2)} (by hand 217.04, 820.35, 3.05, 3,834.49)`);
  const h3 = verdict({ ...D, miles: 8000, mpg: 40, kwhPerMile: 0.35, gasCar: 30000, evCar: 29000, years: 5, rate: 3, credit: 0, gasUsdPerGal: oh.gas.value, powerUsdPerMwh: oh.power.value });
  check(near(h3.gasYear, 765.8, 1e-6) && near(h3.evYear, 544.6, 1e-6) && near(h3.saveYear, 221.2, 1e-6) && h3.payback === 0 && near(h3.npv, 2013.03, 0.01), `household 3 (Ohio, the EV cheaper to buy): saved $${h3.saveYear.toFixed(2)}, payback at once, NPV $${h3.npv.toFixed(2)} (by hand 221.20, 0, 2,013.03)`);
  // the chart's lines cross at the payback year, inside the years kept; not at all when the EV costs less to buy
  const c1 = cumulative({ ...D, gasUsdPerGal: us.gas.value, powerUsdPerMwh: us.power.value, credit: 0 });
  check(c1.rows.length === 9 && c1.rows[0].gas === 28600 && c1.rows[0].ev === 33600 && near(c1.rows[8].gas, 28600 + 8 * h1.gasYear, 1e-6) && near(c1.cross, h1.payback, 1e-12), `the cumulative cost: 9 points (years 0 to 8), from each price, crossing at ${c1.cross.toFixed(2)} years`);
  check(cumulative({ ...D, miles: 8000, mpg: 40, kwhPerMile: 0.35, gasCar: 30000, evCar: 29000, years: 5, rate: 3, credit: 0, gasUsdPerGal: oh.gas.value, powerUsdPerMwh: oh.power.value }).cross === null, "no crossing to mark when the EV costs less from the start");
  // nothing guessed: some charging away from home without a public price gives no result
  check(chargePrice({ powerUsdPerMwh: 150, homeShare: 70, publicUsdPerMwh: null }) === null && chargePrice({ powerUsdPerMwh: 150 }) === 150, "no public charger price, no blended price (the game guesses none); 100 percent at home is the home price");
  check(DEFAULTS.homeShare.value === 100 && DEFAULTS.rate.value === 5 && DEFAULTS.rate.source.includes("A-94"), "the defaults: all charging at home, 5 percent with OMB's 2026 rates beside it");
}
// the file: every state, sourced and dated; the credit line as the IRS says
check(d.states.length === 51 && d.states.every((s) => s.power && s.gas && /^\d{4}-\d{2}-\d{2}$/.test(s.power.ts) && /^\d{4}-\d{2}-\d{2}$/.test(s.gas.ts) && s.power.table === "eia_retail_electricity_prices" && s.gas.table === "eia_regional_retail_fuel_prices"), "51 states and DC, each with a dated power price and gasoline price from the two tables");
check(d.states.filter((s) => s.gas.where === "state").map((s) => s.code).sort().join(",") === "CA,CO,FL,MA,MN,NY,OH,TX,WA", "gasoline of their own: the nine states EIA publishes");
check(d.states.every((s) => s.gas.where === "state" || (s.gas.where === "region" && s.gas.region)), "every other state names its region");
check(NO_CREDIT_LINE === "No federal credit for cars bought after 30 September 2025." && DEFAULTS.mpg.source.includes("48061") && DEFAULTS.kwhPerMile.source.includes("48697"), "the credit line, and the defaults' fueleconomy.gov vehicles");
console.log(bad ? `${bad} FAILED` : "the EV game: lib/ev.ts matches the hand-computed figures");
process.exit(bad ? 1 : 0);
