// Session 10203: the same figures as restate.py, by the page's own library (site/lib/datacenter.ts and
// site/lib/datacenter/finance.ts) on the page's own files, the way app/cost-of-power/model.ts calls it.
//   node runs/c10203/lib_figures.mjs [grid] [region] [buy]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as L from "../../site/lib/datacenter.ts";
import * as F from "../../site/lib/datacenter/finance.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(here, "..", "..", "site", "data", "datacenter");
const INDEX = JSON.parse(fs.readFileSync(path.join(dir, "index.json"), "utf-8"));
const grid = process.argv[2] ?? "ercot", g = INDEX.grids[grid];
const region = process.argv[3] ?? g.main, buy = process.argv[4] ?? "rt";
const files = g.years.map((y) => JSON.parse(fs.readFileSync(path.join(dir, `${grid}_${y}.json`), "utf-8")));
const FLAT = { run: "flat", n: 0, pct: 0, shift: 0 };
function wayOf(ms) {
  const l = L.lastTwelve(ms), s = L.span(l), w = L.last36(ms), b = L.badMonth(w?.months ?? []);
  return { per: s.per, cost: s.cost, energy: s.energy, held: s.held, flatCost: s.flatCost, down: s.down, flat: s.flat, bad: b ? { m: b.m, per: b.cost / b.energy, cost: b.cost } : null, of: w?.months.length ?? 0, first: l[0].m, last: l[11].m };
}
const res = { grid, region, buy };
const ms = L.monthsRuled(files, region, buy, FLAT, "forecast").months;
const flat = wayOf(ms);
res.flat = flat;
const d = F.defaultsOf({ run: F.FLAT, gpu: L.DEFAULTS.gpu, pue: L.DEFAULTS.pue });
res.flat_finance = F.resultOf(d, flat);
res.gpus_100mw = 100 * F.gpusPerMw(d);
res.by_year = Object.fromEntries(L.years(ms).map((y) => [y.y, { flat: y.flat, per: y.per, months: y.months }]));
const r = g.regions.find((k) => k.id === region);
if (r.ref) {
  const hm = L.monthsOf(files, r.ref, buy, FLAT).filter((m) => m.m >= flat.first && m.m <= flat.last && m.complete);
  if (hm.length === 12) { const s = L.span(hm); res.hub = { id: r.ref, flat: s.flat, diff: flat.flat - s.flat }; }
}
if (buy === "rt" && r.da) res.da_l12 = L.span(L.lastTwelve(L.monthsRuled(files, region, "da", FLAT, "forecast").months)).per;
for (const [run, kw] of [["hours", { n: 100 }], ["share", { pct: 5 }], ["shift", { shift: 20 }]]) {
  const x = { run, n: 100, pct: 5, shift: 20, ...kw };
  const wr = wayOf(L.monthsRuled(files, region, buy, x, "forecast").months);
  const wf = wayOf(L.monthsRuled(files, region, buy, x, "hindsight").months);
  const saved = flat.flat - wr.per, savedF = flat.flat - wf.per;
  res[`rule_${run}`] = { way: wr, finance: F.resultOf({ ...d, run: F.FLEX }, wr), saved, foreseen_per: wf.per, foreseen_saved: savedF, kept_pct: (100 * saved) / savedF, foreseen_down: wf.down };
}
console.log(JSON.stringify(res, null, 1));
