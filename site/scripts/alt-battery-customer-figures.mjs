// Energy Research Warehouse (ERW) site, ruling alternatives of /battery/customer (session 7704, 17 November 2026;
// wip/alt-battery-customer-* branches, not a default on main). The page's own arithmetic (lib/customerbattery.ts) run on
// the published cases of the replication (replication/battery_customer/cases.json), so that the figures under the other
// choice are pinned with the site's code. For each case: the year as the case types it, and the year when "How long
// your peak lasts" is left at the field's starting value (a reader who does not change it).
//   node --import ./scripts/tsx-register.mjs scripts/alt-battery-customer-figures.mjs
import fs from "node:fs";

const C = await import("../lib/customerbattery.ts");
const cases = JSON.parse(fs.readFileSync(new URL("../../replication/battery_customer/cases.json", import.meta.url), "utf8")).cases;
const start = C.FIELDS.find((f) => f.key === "peakHours").start;
const year = (typed) => { const r = C.readAll(typed); return r.ok ? C.saving(r.x).yearSaved : null; };
const out = { start };
for (const c of cases) out[c.id] = { typed: year(c.typed), at_start: year({ ...c.typed, peakHours: start }) };
process.stdout.write(JSON.stringify(out));
