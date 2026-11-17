// Energy Research Warehouse (ERW) site, ruling alternatives of /battery/customer (session 7704, 17 November 2026;
// wip/alt-battery-customer-* branches, not a default on main). The page's own arithmetic (lib/customerbattery.ts) run on
// the published cases of the replication (replication/battery_customer/cases.json), so that the figures under the other
// choice are pinned with the site's code. On wip/alt-battery-customer-5: whether each case is read under the energy
// rates' limit of USD 1 per kWh, its year, and the read's store with its rates typed in cents and in dollars.
//   node --import ./scripts/tsx-register.mjs scripts/alt-battery-customer-figures.mjs
import fs from "node:fs";

const C = await import("../lib/customerbattery.ts");
const cases = JSON.parse(fs.readFileSync(new URL("../../replication/battery_customer/cases.json", import.meta.url), "utf8")).cases;
const one = (typed) => { const r = C.readAll(typed); return r.ok ? { year: C.saving(r.x).yearSaved } : { missing: r.missing }; };
const out = { limit: C.FIELDS.find((f) => f.key === "peakRate").max };
for (const c of cases) out[c.id] = one(c.typed);
// the read's store (docs/reviews/battery-customer-read-2026-11-16.md, row 4): 247 kW, 55 kW and 110 kWh, 4.9 and 2.5 for cents; the
// demand charge, 15.35 (Austin Energy's case), only completes the fields: the test checks that the rates are refused or read, not a year
const store = { peakKw: "247", demandCharge: "15.35", batteryKw: "55", batteryKwh: "110", peakHours: "2", days: "21", roundTrip: "86" };
out.store_cents = one({ ...store, peakRate: "4.9", offPeakRate: "2.5" });
out.store_dollars = one({ ...store, peakRate: "0.049", offPeakRate: "0.025" });
process.stdout.write(JSON.stringify(out));
