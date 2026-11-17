// Energy Research Warehouse (ERW) site, ruling alternatives of /prices (session 7723, 17 November 2026; wip/alt-prices-*
// branches, not a default on main). The hub page's own library (lib/pricehub.ts) and market file (data/markets.json) run on
// the public tables as the warehouse wrote them, over the impact file's rolling 30 days (to the newest real-time hour).
// On wip/alt-prices-4: SPP's hubs read through the real-time table the market file now names: real time less day-ahead
// over the hours both hold (realLessDayAhead), and the hours of real-time history the hub pages gain.
//   node --import ./scripts/tsx-register.mjs scripts/alt-prices-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const H = await import("../lib/pricehub.ts");
const markets = JSON.parse(fs.readFileSync(new URL("../data/markets.json", import.meta.url), "utf8")).isos;
const spp = markets.find((m) => m.iso === "SPP");
const dir = process.argv[2];
function rows(table, variable, entity) {
  const out = [];
  for (const line of fs.readFileSync(path.join(dir, `${table}.csv`), "utf-8").split(/\r?\n/)) {
    if (!line.startsWith(`${entity},${variable},`)) continue;
    const c = line.split(",");
    if (c[3] !== "") out.push({ entity, variable, ts_utc: c[2], value: Number(c[3]) });
  }
  return out;
}
const out = { rt: spp.rt };
let newest = "";
for (const e of ["spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"]) for (const r of rows(spp.rt.table, spp.rt.variable, e)) if (r.ts_utc > newest) newest = r.ts_utc;
const end = Date.parse(newest.slice(0, 13) + ":00:00Z"), start = end - 30 * 86400e3;
const inWin = (r) => { const t = Math.floor(Date.parse(r.ts_utc) / 3600e3) * 3600e3; return t > start && t <= end; };
for (const e of ["spp:SPPNORTH_HUB", "spp:SPPSOUTH_HUB"]) {
  const rtAll = rows(spp.rt.table, spp.rt.variable, e), rt = rtAll.filter(inWin);
  const da = rows(spp.da.table, spp.da.variable, e).filter(inWin);
  const d = H.realLessDayAhead(rt, da, spp.rt.freq);
  const hours = new Set(rtAll.map((r) => r.ts_utc.slice(0, 13)));
  out[e] = { both: d?.n ?? null, mean_rt_less_da: d?.mean ?? null, min: d?.min ?? null, max: d?.max ?? null, rt_hours_held: hours.size, first: rtAll[0]?.ts_utc ?? null };
}
process.stdout.write(JSON.stringify(out));
