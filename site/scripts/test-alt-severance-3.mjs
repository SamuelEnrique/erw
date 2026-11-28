// Energy Research Warehouse (ERW) site, ruling alternative 3 of /severance (session 7702, finished by session 7900,
// 17 November 2026; branch wip/alt-severance-3, not a default on main): gas is priced per MMBtu and each Mcf is taken as
// 1.034 MMBtu (EIA's heat content of natural gas, 1,034 Btu a cubic foot, site/data/forecast/gas.json), the rule /impact
// uses, where main prices one Mcf as one MMBtu. The figure pinned is the read's case of
// docs/reviews/ruling-impact-severance-2026-11-17.md, line 3: one well's 46,500 Mcf at Henry Hub's October 2026 mean,
// USD 2.99 per MMBtu. The page's own function (lib/severance.ts compute) on the page's own rules file.
//   node --import ./scripts/tsx-register.mjs scripts/test-alt-severance-3.mjs
import fs from "node:fs";

const S = await import("../lib/severance.ts");
const rules = JSON.parse(fs.readFileSync(new URL("../data/severance_rules.json", import.meta.url), "utf-8"));
const gas = JSON.parse(fs.readFileSync(new URL("../data/forecast/gas.json", import.meta.url), "utf-8"));
const calc = fs.readFileSync(new URL("../app/severance/Calculator.tsx", import.meta.url), "utf-8");
const K = gas.btu_per_cf / 1000;
let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
// the page prints a tax to the cent, half a cent up (toLocaleString): 10,427.625 is printed 10,427.63
const cents = (v) => Math.round(Math.round(v * 1e6) / 1e4) / 100;
const base = (state, product, volume, price, mmbtuPerMcf) => cents(S.compute(rules, { state, product, volume, price, mmbtuPerMcf }).baseTotal);

ok(gas.btu_per_cf === 1034 && K === 1.034, "the heat content is EIA's 1,034 Btu a cubic foot: one Mcf is 1.034 MMBtu");
const main = base("TX", "gas", 46500, 2.99), alt = base("TX", "gas", 46500, 2.99, K);
console.log(`     Texas gas, 46,500 Mcf at $2.99: main ${main}, the other choice ${alt}`);
ok(main === 10427.63, "main's rule, one Mcf as one MMBtu: Texas gas tax at the base rate $10,427.63");
ok(alt === 10782.16, "the other choice, 1.034 MMBtu an Mcf: $10,782.16 (+354.53 on the printed cents, +3.40 percent)");
ok(((alt - main) / main * 100).toFixed(2) === "3.40", "the change is +3.40 percent");
const laMain = base("LA", "gas", 46500, 2.99), laAlt = base("LA", "gas", 46500, 2.99, K);
console.log(`     Louisiana gas, 46,500 Mcf: main ${laMain}, the other choice ${laAlt}`);
ok(laMain === 7040.1 && laAlt === 7040.1, "Louisiana's gas tax is per Mcf and does not move: $7,040.10 under both");
const nmMain = S.compute(rules, { state: "NM", product: "gas", volume: 46500, price: 2.99 }).baseTotal;
const nmAlt = S.compute(rules, { state: "NM", product: "gas", volume: 46500, price: 2.99, mmbtuPerMcf: K }).baseTotal;
console.log(`     New Mexico gas, 46,500 Mcf at $2.99: main ${cents(nmMain)}, the other choice ${cents(nmAlt)}`);
ok(Math.abs(nmAlt / nmMain - K) < 1e-9, "New Mexico's taxes are a percent of value and move by the same 3.40 percent");
const oilMain = base("TX", "oil", 1000, 102.07), oilAlt = base("TX", "oil", 1000, 102.07, K);
ok(oilMain === oilAlt && oilMain === 4695.22, "oil does not move: 1,000 bbl of Texas oil at $102.07 is $4,695.22 under both");
ok(/mmbtuPerMcf: MMBTU_PER_MCF/.test(calc) && /Price, USD per MMBtu/.test(calc) && /Default on the site: one Mcf priced as one MMBtu/.test(calc),
  "the calculator hands the factor to compute, labels the gas price per MMBtu and its tip names the site's default and EIA's source");
console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
