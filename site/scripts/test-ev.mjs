// Energy Research Warehouse (ERW) site, session 294: the EV game against hand-computed figures.
//
//   node scripts/test-ev.mjs        (tests/test_session294.py runs this)
//
// Works the method note's example by hand (docs/methods/ev_game.md: the defaults in California) and checks
// lib/ev.ts to a hundredth of a cent, then the edge cases (an EV that costs no more, one that saves nothing), and that
// data/ev_prices.json holds every state with a dated, sourced power price and gasoline price. Exits 1 on any failure.
import fs from "node:fs";
import { DEFAULTS, evPer100, gasPer100, NO_CREDIT_LINE, verdict } from "../lib/ev.ts";

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
// the file: every state, sourced and dated; the credit line as the IRS says
check(d.states.length === 51 && d.states.every((s) => s.power && s.gas && /^\d{4}-\d{2}-\d{2}$/.test(s.power.ts) && /^\d{4}-\d{2}-\d{2}$/.test(s.gas.ts) && s.power.table === "eia_retail_electricity_prices" && s.gas.table === "eia_regional_retail_fuel_prices"), "51 states and DC, each with a dated power price and gasoline price from the two tables");
check(d.states.filter((s) => s.gas.where === "state").map((s) => s.code).sort().join(",") === "CA,CO,FL,MA,MN,NY,OH,TX,WA", "gasoline of their own: the nine states EIA publishes");
check(d.states.every((s) => s.gas.where === "state" || (s.gas.where === "region" && s.gas.region)), "every other state names its region");
check(NO_CREDIT_LINE === "No federal credit for cars bought after 30 September 2025." && DEFAULTS.mpg.source.includes("48061") && DEFAULTS.kwhPerMile.source.includes("48697"), "the credit line, and the defaults' fueleconomy.gov vehicles");
console.log(bad ? `${bad} FAILED` : "the EV game: lib/ev.ts matches the hand-computed figures");
process.exit(bad ? 1 : 0);
