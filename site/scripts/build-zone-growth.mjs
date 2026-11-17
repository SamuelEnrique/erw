// Energy Research Warehouse (ERW) site, ruling alternative 3 of /demand (session 7728, 17 November 2026; branch
// wip/alt-demand-3, not a default on main): each load zone's own growth, the file /demand reads (site/data/zone_growth.json).
//
//   node scripts/build-zone-growth.mjs <warehouse/output directory> [out.json]
//
// From ercot_zone_load_hourly (ERCOT's Hourly Load Data Archives, public): each zone's and ERCOT's mean hourly load in the
// base year and the newest whole year, both counted only when every hour of the year is held. Only ERCOT's zones: the
// held grids' zones (Dominion's in PJM's file is not in this table; NYISO's and ISO-NE's are held) are not read. Reads
// only; writes the one file.
import fs from "node:fs";
import path from "node:path";

const [dir, outArg] = process.argv.slice(2);
const TABLE = "ercot_zone_load_hourly", BASE = "2019";
const file = path.join(dir, `${TABLE}.csv`);
const text = fs.readFileSync(file, "utf-8");
const header = text.split(/\r?\n/).filter((l) => l.startsWith("#"));
const retrieved = (header.find((l) => /Retrieved: /.test(l)) ?? "").replace(/^#\s*/, "");
const acc = {};
for (const line of text.split(/\r?\n/)) {
  if (!line.startsWith("ercot:")) continue;
  const c = line.split(",");
  if (c[1] !== "load" || c[3] === "") continue;
  const y = c[2].slice(0, 4);
  const a = ((acc[c[0]] ??= {})[y] ??= { sum: 0, n: 0 });
  a.sum += Number(c[3]); a.n += 1;
}
const hours = (y) => ((Number(y) % 4 === 0 && Number(y) % 100 !== 0) || Number(y) % 400 === 0 ? 8784 : 8760);
const years = [...new Set(Object.values(acc).flatMap((z) => Object.keys(z)))].sort();
const last = years.filter((y) => y > BASE && Object.values(acc).every((z) => z[y]?.n === hours(y))).at(-1) ?? null;
const zones = Object.entries(acc).map(([entity, z]) => {
  const b = z[BASE], l = last ? z[last] : null;
  if (!b || b.n !== hours(BASE) || !l) return { entity, base_mw: null, last_mw: null };
  const bm = b.sum / b.n, lm = l.sum / l.n;
  return { entity, base_mw: Math.round(bm * 1000) / 1000, last_mw: Math.round(lm * 1000) / 1000, change_mw: Math.round((lm - bm) * 1000) / 1000, change_pct: Math.round((lm / bm - 1) * 100000) / 1000 };
}).sort((a, b) => (b.change_pct ?? -Infinity) - (a.change_pct ?? -Infinity));
const out = { built_by: "site/scripts/build-zone-growth.mjs (wip/alt-demand-3)", table: TABLE, source: "ERCOT, Hourly Load Data Archives, through the ERW table ercot_zone_load_hourly",
  retrieved, base: BASE, last, zones };
const target = outArg ?? new URL("../data/zone_growth.json", import.meta.url);
fs.writeFileSync(target, JSON.stringify(out, null, 1) + "\n");
process.stdout.write(`zone_growth: ${zones.length} rows, ${BASE} against ${last}\n`);
