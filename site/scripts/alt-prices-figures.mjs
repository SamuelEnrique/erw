// Energy Research Warehouse (ERW) site, ruling alternatives of /prices (session 7723, 17 November 2026; wip/alt-prices-*
// branches, not a default on main). The hub page's own library (lib/pricehub.ts) and market file run on the public tables
// as the warehouse wrote them, over the impact file's rolling 30 days (to the newest real-time hour held). On
// wip/alt-prices-3: hub A less hub B (hubLessHub), ERCOT West less Houston, real time and day-ahead.
//   node --import ./scripts/tsx-register.mjs scripts/alt-prices-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const H = await import("../lib/pricehub.ts");
const ercot = JSON.parse(fs.readFileSync(new URL("../data/markets.json", import.meta.url), "utf8")).isos.find((m) => m.iso === "ERCOT");
const dir = process.argv[2];
const cache = {};
function rows(table, variable, entity) {
  cache[table] ??= fs.readFileSync(path.join(dir, `${table}.csv`), "utf-8").split(/\r?\n/);
  const out = [];
  for (const line of cache[table]) {
    if (!line.startsWith(`${entity},${variable},`)) continue;
    const c = line.split(",");
    if (c[3] !== "") out.push({ entity, variable, ts_utc: c[2], value: Number(c[3]) });
  }
  return out;
}
const A = "ercot:HB_WEST", B = "ercot:HB_HOUSTON";
let newest = "";
for (const t of ["iso_rtm_hub_prices"]) for (const line of fs.readFileSync(path.join(dir, `${t}.csv`), "utf-8").split(/\r?\n/)) { const c = line.split(","); if (/^[a-z]+:/.test(c[0]) && c[2] > newest) newest = c[2]; }
const end = Date.parse(newest.slice(0, 13) + ":00:00Z"), start = end - 30 * 86400e3;
const win = (r) => { const t = Math.floor(Date.parse(r.ts_utc) / 3600e3) * 3600e3; return t > start && t <= end; };
const pair = (src) => H.hubLessHub(rows(src.table, src.variable, A).filter(win), rows(src.table, src.variable, B).filter(win), src.freq);
process.stdout.write(JSON.stringify({ newest, rt: pair(ercot.rt), da: pair(ercot.da) }));
