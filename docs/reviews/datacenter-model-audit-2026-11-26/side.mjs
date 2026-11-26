// Session 10203: the default page's side figures by the page's own code: Texas delivery at 100 MW (lib/datacenter/
// delivery.ts on data/datacenter/texas_delivery.json), the four-peak saving (model.ts's arithmetic on the main copy's
// ercot_4cp_intervals.csv, read only), and the hours the default flexible way is off by month.
//   node runs/c10203/side.mjs <main copy warehouse/output>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as L from "../../site/lib/datacenter.ts";
import * as Dl from "../../site/lib/datacenter/delivery.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..", "..", "site");
const out = process.argv[2];
const DEL = JSON.parse(fs.readFileSync(path.join(site, "data", "datacenter", "texas_delivery.json"), "utf-8"));
const res = { delivery_100mw: {} };
for (const u of Dl.utilitiesOf(DEL.rows)) {
  const d = Dl.deliveryOf(DEL.rows, u, 100);
  res.delivery_100mw[u] = { total: d.total, parts: Object.fromEntries(d.components.map((c) => [c.kind, c.perMwh])), held: Dl.deliveryStat(DEL.rows, 100, `${Dl.slugOf(u)}:held`) ?? null, assumed: d.assumed };
}
const rates = (DEL.matrix ?? []).filter((r) => r.quantity === "postage_stamp_rate" && r.status === "approved" && r.matrix !== "B").sort((a, b) => a.year.localeCompare(b.year));
res.rate = rates.at(-1) ? { year: rates.at(-1).year, value: rates.at(-1).value, per_mwh_flat: (rates.at(-1).value * 1000) / 8760 } : null;
// four peaks, the default flexible way beside a flat load: off in 100 hours a year, the rule
const INDEX = JSON.parse(fs.readFileSync(path.join(site, "data", "datacenter", "index.json"), "utf-8"));
const g = INDEX.grids.ercot;
const files = g.years.map((y) => JSON.parse(fs.readFileSync(path.join(site, "data", "datacenter", `ercot_${y}.json`), "utf-8")));
const ruled = L.monthsRuled(files, "LZ_NORTH", "rt", { run: "hours", n: 100, pct: 0, shift: 0 }, "forecast");
const lines = fs.readFileSync(path.join(out, "ercot_4cp_intervals.csv"), "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const head = lines[0].split(",");
const iv = lines.slice(1).map((l) => l.split(",")).filter((c) => c[head.indexOf("variable")] === "cp4_load_mw").map((c) => ({ ts: c[head.indexOf("ts_utc")], mw: Number(c[head.indexOf("value")]) }));
const by = {};
for (const r of iv) {
  const t = Date.parse(r.ts) - 6 * 3600000, y = new Date(t).getUTCFullYear(), i = Math.floor((t - Date.UTC(y, 0, 1)) / 3600000);
  const w = ruled.weights.get(y)?.[i];
  (by[y] ??= []).push({ ts: r.ts, w: w ?? null });
}
res.four_peaks = Object.fromEntries(Object.entries(by).map(([y, v]) => [y, { intervals: v.length, avoided: v.length === 4 && v.every((k) => k.w !== null) ? 1 - v.reduce((a, k) => a + k.w, 0) / 4 : null }]));
// the month each year's budget ran out, for the default flexible way
const off = {};
for (const m of ruled.months) if (m.down) off[m.m] = m.down;
res.flex_hours_off_by_month = off;
console.log(JSON.stringify(res, null, 1));
