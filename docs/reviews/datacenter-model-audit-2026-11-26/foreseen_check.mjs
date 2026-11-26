// Session 10203: is "if perfectly foreseen" ever below the rule's figure ("the most it could have saved")? Every grid,
// region and market the page holds, several settings of each flexible way, over the last twelve months (the summary,
// the table, the headline) and each calendar year of the chart. The page's own library (checked equal to restate.py).
//   node runs/c10203/foreseen_check.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as L from "../../site/lib/datacenter.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(here, "..", "..", "site", "data", "datacenter");
const INDEX = JSON.parse(fs.readFileSync(path.join(dir, "index.json"), "utf-8"));
const SETS = [["hours", { n: 50 }], ["hours", { n: 100 }], ["hours", { n: 300 }], ["hours", { n: 1000 }], ["share", { pct: 5 }], ["share", { pct: 15 }], ["shift", { shift: 20 }]];
let cases = 0, l12Worse = [], yearWorse = 0, years = 0, keptOver = 0;
for (const [grid, g] of Object.entries(INDEX.grids)) {
  const files = g.years.map((y) => JSON.parse(fs.readFileSync(path.join(dir, `${grid}_${y}.json`), "utf-8")));
  for (const r of g.regions) for (const buy of ["rt", "da"]) {
    if (!r[buy] || !r.da) continue;
    for (const [run, kw] of SETS) {
      const x = { run, n: 100, pct: 5, shift: 20, ...kw };
      const fore = L.monthsRuled(files, r.id, buy, x, "forecast"), hind = L.monthsRuled(files, r.id, buy, x, "hindsight");
      const l = L.lastTwelve(fore.months), h = L.lastTwelve(hind.months);
      if (!l || !h) continue;
      cases++;
      const sl = L.span(l), sh = L.span(h);
      const saved = sl.flat - sl.per, savedH = sh.flat - sh.per;
      if (savedH < saved - 1e-9) { l12Worse.push({ grid, region: r.id, buy, run, ...kw, rule: +sl.per.toFixed(4), foreseen: +sh.per.toFixed(4), kept_pct: Math.round((100 * saved) / savedH), downRule: sl.down, downFore: sh.down, months: `${l[0].m} to ${l[11].m}` }); }
      if (savedH > 0 && saved / savedH > 1) keptOver++;
      const yh = new Map(L.years(hind.months).map((y) => [y.y, y]));
      for (const y of L.years(fore.months)) {
        const z = yh.get(y.y);
        if (!z || y.per === null || z.per === null) continue;
        years++;
        if (z.per > y.per + 1e-9) yearWorse++;
      }
    }
  }
}
console.log(JSON.stringify({ cases, l12_foreseen_worse: l12Worse.length, kept_over_100: keptOver, year_rows: years, year_rows_foreseen_worse: yearWorse, examples: l12Worse.slice(0, 25) }, null, 1));
