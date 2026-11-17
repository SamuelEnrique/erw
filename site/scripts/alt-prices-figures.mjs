// Energy Research Warehouse (ERW) site, ruling alternatives of /prices (session 7723, 17 November 2026; wip/alt-prices-*
// branches, not a default on main). The hub page's own library (lib/pricehub.ts) run on the public tables as the warehouse
// wrote them, over the impact file's rolling 30 days (the 720 hours after the newest real-time hour less 30 days, to it).
// On wip/alt-prices-1: each hub's day-ahead mean on-peak and off-peak (splitPeak), and over every hour.
//   node --import ./scripts/tsx-register.mjs scripts/alt-prices-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";

const H = await import("../lib/pricehub.ts");
const dir = process.argv[2];
const HUBS = { "ercot:HB_HUBAVG": "ERCOT", "ercot:HB_HOUSTON": "ERCOT", "caiso:TH_SP15_GEN-APND": "CAISO", "spp:SPPNORTH_HUB": "SPP", "spp:SPPSOUTH_HUB": "SPP" };
function hourly(table, vars) {
  const acc = {};
  for (const line of fs.readFileSync(path.join(dir, `${table}.csv`), "utf-8").split(/\r?\n/)) {
    if (!line || line.startsWith("#") || line.startsWith("entity,")) continue;
    const c = line.split(",");
    if (!HUBS[c[0]] || !vars.includes(c[1]) || c[3] === "") continue;
    const h = c[2].slice(0, 13);
    ((acc[c[0]] ??= {})[h] ??= []).push(Number(c[3]));
  }
  return acc;
}
const rt = hourly("iso_rtm_hub_prices", ["spp_rtm", "lmp_rtm_15m_mean"]), da = hourly("iso_dam_hub_prices", ["spp_dam", "lmp_dam"]);
const last = Object.values(rt).flatMap((hs) => Object.keys(hs)).sort().at(-1);
const end = Date.parse(`${last}:00:00Z`), start = end - 30 * 86400e3;
const iso = (t) => new Date(t).toISOString().slice(0, 13);
const mean = (rows) => (rows.length ? rows.reduce((a, r) => a + r.value, 0) / rows.length : null);
const out = { newest_rt_hour: last };
for (const [e, grid] of Object.entries(HUBS)) {
  const rows = Object.entries(da[e] ?? {}).filter(([h]) => h > iso(start) && h <= iso(end)).map(([h, v]) => ({ ts_utc: `${h}:00:00Z`, value: v.reduce((a, b) => a + b, 0) / v.length }));
  const p = H.splitPeak(rows, grid);
  out[e] = { all: mean(rows), on: mean(p.on), off: mean(p.off), n: rows.length, on_n: p.on.length };
}
process.stdout.write(JSON.stringify(out));
