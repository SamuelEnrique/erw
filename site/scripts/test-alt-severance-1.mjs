// Energy Research Warehouse (ERW) site, ruling alternative 1 of /severance (session 7702, 17 November 2026; branch
// wip/alt-severance-1, not a default on main): the calculator's price box takes the chosen report period's own mean.
// The figure pinned on the warehouse's EIA daily spot prices (eia_fuel_spot_prices, public), read from the folder
// ERW_TABLES_DIR names or warehouse/output; skipped when the table is not on the machine. The page's own functions
// (lib/severance.ts periodMeans, periodPrice, compute) on the rows the page reads (since 1 January 2025).
//   node --import ./scripts/tsx-register.mjs scripts/test-alt-severance-1.mjs
import fs from "node:fs";
import path from "node:path";

const S = await import("../lib/severance.ts");
const rules = JSON.parse(fs.readFileSync(new URL("../data/severance_rules.json", import.meta.url), "utf-8"));
const dir = process.env.ERW_TABLES_DIR || path.join(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..", "..", "warehouse", "output");
const file = path.join(dir, "eia_fuel_spot_prices.csv");
let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
if (!fs.existsSync(file)) {
  console.log(`skip: ${file} is not on this machine`);
} else {
  const rows = { "eia:wti_cushing": [], "eia:henry_hub": [] };
  for (const line of fs.readFileSync(file, "utf-8").split(/\r?\n/)) {
    if (!line || line.startsWith("#")) continue;
    const [entity, variable, ts_utc, value] = line.split(",");
    if (rows[entity] && variable === "spot_price" && ts_utc >= "2025-01-01T00:00:00Z" && value !== "") rows[entity].push({ ts_utc, value: Number(value) });
  }
  const oil = S.periodMeans(rows["eia:wti_cushing"]), gas = S.periodMeans(rows["eia:henry_hub"]);
  const tax = (state, product, volume, price) => Math.round(S.compute(rules, { state, product, volume, price }).baseTotal * 100) / 100;
  const main = tax("TX", "gas", 1860, gas["2026-10"].value);
  ok(gas["2026-10"].value === 2.99 && oil["2026-10"].value === 102.07, "the default month, October 2026: Henry Hub $2.99, WTI Cushing $102.07");
  ok(S.periodPrice(gas, "2026-08") === 2.79 && main === 417.11 && tax("TX", "gas", 1860, S.periodPrice(gas, "2026-08")) === 389.21,
    "the read's case, 1,860 Mcf of Texas gas for August 2026: $417.11 under main's rule, $389.21 at August's own $2.79 (-27.90, -6.7 percent)");
  ok(S.periodPrice(oil, "2026-08") === 83.9 && tax("TX", "oil", 1000, oil["2026-10"].value) === 4695.22 && tax("TX", "oil", 1000, S.periodPrice(oil, "2026-08")) === 3859.4,
    "1,000 bbl of Texas oil for August 2026: $4,695.22 under main's rule, $3,859.40 at August's own $83.90 (-17.8 percent)");
  const cert = rules.states.TX.products.gas.options.find((o) => o.id === "tx_lp_gas").certified.prices.map((p) => p.period);
  const moves = cert.map((p) => (tax("TX", "gas", 1860, S.periodPrice(gas, p)) - main) / main * 100);
  ok(cert.length === 20 && cert.every((p) => S.periodPrice(gas, p) !== null) && Math.min(...moves).toFixed(2) === "-7.36" && Math.max(...moves).toFixed(2) === "158.19",
    "the 20 certified periods of the gas credit are all held; the tax at the base rate moves from -7.36 to +158.19 percent (January 2026)");
}
console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
