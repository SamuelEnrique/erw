// Energy Research Warehouse (ERW) site, ruling alternative 1 of /storage (session 7727, 17 November 2026; branch
// wip/alt-storage-1, not a default on main). The page's own function (lib/storagemonth.ts monthTotal) on
// storage_daily_cycle as the warehouse wrote it: each panel grid's newest whole month of discharge.
//   node --import ./scripts/tsx-register.mjs scripts/alt-storage-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const S = await import("../lib/storagemonth.ts");
const rows = [];
for (const line of fs.readFileSync(path.join(process.argv[2], "storage_daily_cycle.csv"), "utf-8").split(/\r?\n/)) {
  if (!line || line.startsWith("#") || line.startsWith("entity,")) continue;
  const c = line.split(",");
  if (c[1] === "mwh_discharged" && c[3] !== "") rows.push({ entity: c[0], variable: c[1], ts_utc: c[2], value: Number(c[3]) });
}
const out = {};
for (const e of ["caiso:ISO", "eia930:ERCO", "eia930:SWPP"]) out[e] = S.monthTotal(rows, e);
// the month before the newest whole one, the impact file's second month
out.august = Object.fromEntries(["caiso:ISO", "eia930:ERCO", "eia930:SWPP"].map((e) => [e, S.monthTotal(rows.filter((r) => r.ts_utc < "2026-09-01"), e)]));
process.stdout.write(JSON.stringify(out));
