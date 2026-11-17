// Energy Research Warehouse (ERW) site, ruling alternative 1 of /grid (session 7725, 17 November 2026; branch wip/alt-grid-1,
// not a default on main). The Mix tab's own helpers (lib/gridalign.ts alignHour, lib/network.ts tiesAt, lib/networkV3.ts
// completeHour) on the committed hourly snapshot (data/grid_network.json) and the local tables (eia930_all_demand,
// carbon_intensity_hourly): for each public grid, the three figures at their own newest hours (main) and at the hour all
// three hold (the branch).
//   node --import ./scripts/tsx-register.mjs scripts/alt-grid-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const A = await import("../lib/gridalign.ts");
const N = await import("../lib/network.ts");
const V = await import("../lib/networkV3.ts");
const snap = JSON.parse(fs.readFileSync(new URL("../data/grid_network.json", import.meta.url), "utf8"));
const read = (table, variable) => {
  const by = {};
  for (const line of fs.readFileSync(path.join(process.argv[2], `${table}.csv`), "utf-8").split(/\r?\n/)) {
    const c = line.split(",");
    if (c[1] !== variable || c[3] === "" || !c[0].startsWith("eia930:")) continue;
    (by[c[0]] ??= []).push({ ts_utc: c[2], value: Number(c[3]) });
  }
  for (const k in by) by[k].sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  return by;
};
const dem = read("eia930_all_demand", "demand_mw"), car = read("carbon_intensity_hourly", "intensity_generation");
const complete = V.completeHour(snap.hours, snap.links);
const xLatest = complete.hour ?? snap.hours.at(-1);
const net = (ba, h) => N.tiesAt(snap, ba, h).reduce((a, t) => a + t.mw, 0);
const out = { snapshot_built: snap.built, xLatest };
for (const ba of ["ERCO", "CISO", "SWPP", "PJM"]) {
  const e = `eia930:${ba}`, d = dem[e] ?? [], c = car[e] ?? [];
  const hour = A.alignHour([d.at(-1)?.ts_utc, c.at(-1)?.ts_utc, xLatest], snap.hours);
  const at = (rows) => rows.find((r) => hour && Date.parse(r.ts_utc) === Date.parse(hour));
  out[ba] = { main: { demand: d.at(-1), carbon: c.at(-1), net: net(ba, xLatest) }, hour, branch: hour ? { demand: at(d) ?? null, carbon: at(c) ?? null, net: net(ba, hour) } : null };
}
process.stdout.write(JSON.stringify(out));
