// Energy Research Warehouse (ERW) site, ruling alternatives of /battery/customer (session 7704, 17 November 2026;
// wip/alt-battery-customer-* branches, not a default on main). The page's own arithmetic (lib/customerbattery.ts) run on
// the published cases of the replication (replication/battery_customer/cases.json), so that the figures under the other
// choice are pinned with the site's code. On wip/alt-battery-customer-3: each case's "From shaving the peak" a month and
// "Saved a year", with 85 percent of the kW the battery could take reaching the bill.
//   node --import ./scripts/tsx-register.mjs scripts/alt-battery-customer-figures.mjs
import fs from "node:fs";

const C = await import("../lib/customerbattery.ts");
const cases = JSON.parse(fs.readFileSync(new URL("../../replication/battery_customer/cases.json", import.meta.url), "utf8")).cases;
const out = { share: C.SHAVE_SHARE };
for (const c of cases) {
  const r = C.readAll(c.typed);
  if (r.ok) { const s = C.saving(r.x); out[c.id] = { demand: s.demandSaved, year: s.yearSaved, shaved: s.shavedKw }; }
}
process.stdout.write(JSON.stringify(out));
