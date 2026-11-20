// Energy Research Warehouse (ERW) site, ruling alternatives of /explore/interconnection (session 7710, 17 November 2026;
// wip/alt-interconnection-* branches, not a default on main). The page's own library run on the rows of
// iso_queue_statistics as the warehouse wrote them, so that the figures under the other choice are pinned with the
// site's code. On wip/alt-interconnection-2: the year each public queue opens on, and the figures of its headlines then.
//   node --import ./scripts/tsx-register.mjs scripts/alt-interconnection-figures.mjs <iso_queue_statistics.csv> <retrieved day>
import fs from "node:fs";

const L = await import("../lib/explore/interconnection.ts");
const [file, retrieved] = process.argv.slice(2);
const rows = [];
let head = null;
for (const line of fs.readFileSync(file, "utf-8").split(/\r?\n/)) {
  if (!line || line.startsWith("#")) continue;
  if (!head) { head = line.split(","); continue; }
  const c = line.split(",");
  rows.push({ entity: c[0], variable: c[1], ts_utc: c[2], value: c[3] });
}
const out = {};
for (const iso of ["caiso", "ercot", "spp"]) {
  const mine = rows.filter((r) => r.entity.startsWith(`${iso}:queue_`));
  const years = [...new Set(mine.map((r) => L.yearOf(r.entity)).filter((y) => y !== null))].sort((a, b) => a - b);
  const complete = years.filter((y) => !L.partialYear(y, retrieved, new Date("2026-11-17T00:00:00Z")));
  const y = L.openingYear(mine, iso, complete), main = complete.at(-1);
  const v = (yy, k) => L.valueOf(mine, iso, yy, k) ?? null;
  const fig = (yy) => ({ year: yy, entered: v(yy, "positions_entered"), mw: v(yy, "mw_entered"), operating: v(yy, "positions_operating"), withdrawn_share: v(yy, "withdrawal_rate"), waiting: v(yy, "positions_waiting") });
  out[iso] = { opens: fig(y), main: fig(main) };
}
process.stdout.write(JSON.stringify(out));
