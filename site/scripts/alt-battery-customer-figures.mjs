// Energy Research Warehouse (ERW) site, ruling alternatives of /battery/customer (session 7704, 17 November 2026;
// wip/alt-battery-customer-* branches, not a default on main). The page's own arithmetic (lib/customerbattery.ts) run on
// the published cases of the replication (replication/battery_customer/cases.json), so that the figures under the other
// choice are pinned with the site's code. On wip/alt-battery-customer-4: each case's "From shifting energy" and year with
// the energy moved capped at the peak kW times the peak hours, and the faults file's oversized case (the browser proof's
// rates with a 50 kW peak: docs/reviews/battery-customer-faults-2026-11-16.md).
//   node --import ./scripts/tsx-register.mjs scripts/alt-battery-customer-figures.mjs
import fs from "node:fs";

const C = await import("../lib/customerbattery.ts");
const cases = JSON.parse(fs.readFileSync(new URL("../../replication/battery_customer/cases.json", import.meta.url), "utf8")).cases;
const out = {};
const one = (typed) => { const r = C.readAll(typed); if (!r.ok) return null; const s = C.saving(r.x); return { energy: s.energySaved, year: s.yearSaved, capped: s.capped, cap: s.capKwh }; };
for (const c of cases) out[c.id] = one(c.typed);
out.oversized = one({ ...cases.find((c) => c.id === "browser-proof").typed, peakKw: "50" });
process.stdout.write(JSON.stringify(out));
