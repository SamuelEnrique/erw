// Energy Research Warehouse (ERW) site, ruling alternatives of /battery/customer (session 7704, 17 November 2026;
// wip/alt-battery-customer-* branches, not a default on main). The page's own arithmetic (lib/customerbattery.ts) run on
// the published cases of the replication (replication/battery_customer/cases.json), so that the figures under the other
// choice are pinned with the site's code. On wip/alt-battery-customer-2: Salt River Project E-32's year by its own
// seasons, each case typed in the fields as the main season and the other two typed as the page's two other seasons.
//   node --import ./scripts/tsx-register.mjs scripts/alt-battery-customer-figures.mjs
import fs from "node:fs";

const C = await import("../lib/customerbattery.ts");
const cases = Object.fromEntries(JSON.parse(fs.readFileSync(new URL("../../replication/battery_customer/cases.json", import.meta.url), "utf8")).cases.map((c) => [c.id, c]));
const MONTHS = { "srp-e32-summer-peak": 2, "srp-e32-summer": 4, "srp-e32-winter": 6 };   // the plan's seasons (docs/methods/battery_customer.md, section 6)
const out = {};
for (const main of Object.keys(MONTHS)) {
  const r = C.readAll(cases[main].typed);
  const others = Object.keys(MONTHS).filter((k) => k !== main).map((k) => {
    const t = cases[k].typed;
    return C.readSeason([String(MONTHS[k]), t.demandCharge, t.peakRate, t.offPeakRate]);
  });
  const by = C.yearBySeasons(r.x, others);
  out[main] = { twelve: C.saving(r.x).yearSaved, by_seasons: by.year, first_months: by.firstMonths };
}
out.empty = C.readSeason(["", "", "", ""]);
out.partly = C.readSeason(["4", "", "0.1", "0.05"]);
out.too_many = C.yearBySeasons(C.readAll(cases["srp-e32-summer"].typed).x, [{ months: 6, demandCharge: 1, peakRate: 0.1, offPeakRate: 0.05 }, { months: 6, demandCharge: 1, peakRate: 0.1, offPeakRate: 0.05 }]);
process.stdout.write(JSON.stringify(out));
