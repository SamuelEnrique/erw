// Energy Research Warehouse (ERW) site, ruling alternative 1 of /play/ev (session 7720, 17 November 2026; branch
// wip/alt-ev-game-1, not a default on main). The game's own arithmetic (lib/ev.ts verdict, at its defaults) on California
// as the committed price file holds it (data/ev_prices.json), with home electricity at the state's average (main) and at
// PG&E's E-TOU-C winter off-peak (the branch), and the same at the summer off-peak; the rate as bill_rules.json holds it.
//   node --import ./scripts/tsx-register.mjs scripts/alt-ev-game-figures.mjs
import fs from "node:fs";

const E = await import("../lib/ev.ts");
const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf8"));
const prices = read("../data/ev_prices.json"), bills = read("../data/bill_rules.json");
const ca = (prices.states ?? prices.places ?? []).find((s) => s.code === "CA");
const D = Object.fromEntries(Object.entries(E.DEFAULTS).map(([k, v]) => [k, v.value]));
const run = (power) => { const r = E.verdict({ ...D, gasUsdPerGal: ca.gas.value, powerUsdPerMwh: power, credit: 0 }); return { power_cents: power / 10, saved: r.saveYear, payback: r.payback, npv: r.npv }; };
const off = bills.bills.CA.seasons;
process.stdout.write(JSON.stringify({
  file_built: prices.built_at, ca_power: ca.power.value, ca_power_month: ca.power.ts, ca_gas: ca.gas.value,
  tou: E.TOU_DEFAULT.CA.value, bill_winter: off.winter.offpeak, bill_summer: off.summer.offpeak,
  main: run(ca.power.value), branch: run(E.TOU_DEFAULT.CA.value), summer: run(off.summer.offpeak * 1000),
}));
