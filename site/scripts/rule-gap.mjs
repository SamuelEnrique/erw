// Energy Research Warehouse (ERW) site, session 140: the gap between a flexible load judged on a forecast and the same
// load with perfect foresight, by grid and year (/cost-of-power; lib/datacenter.ts ruleWeights and weights).
//
//   node scripts/rule-gap.mjs [dir] [--json]
//
// Reads the page's own files (data/datacenter by default, or dir) and prints, for each grid's default region and each
// whole year held, in the market named: what a flat load paid, what the load paid under the rule an operator could
// follow, and what it would have paid with its hours chosen knowing the year's prices; the saving under each and the
// share of the foreseen saving the rule kept. Two loads: off in 100 hours a year, and 20 percent of each day's energy
// shifted. No request. The figures in the session report and the Method note are this script's output.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const L = await import("../lib/datacenter.ts");
const args = process.argv.slice(2);
const asJson = args.includes("--json");
const dir = args.find((a) => !a.startsWith("--")) ?? path.join(here, "..", "data", "datacenter");
const index = JSON.parse(fs.readFileSync(path.join(dir, "index.json"), "utf8"));
const LOADS = [{ name: "off in 100 hours a year", x: { run: "hours", n: 100, pct: 0, shift: 0 } }, { name: "20 percent of each day shifted", x: { run: "shift", n: 0, pct: 0, shift: 20 } }];
const out = [];
for (const grid of L.ORDER) {
  const g = index.grids[grid];
  if (!g) continue;
  const files = g.years.map((y) => JSON.parse(fs.readFileSync(path.join(dir, `${grid}_${y}.json`), "utf8")));
  const region = g.regions.find((r) => r.id === g.main) ?? g.regions[0];
  for (const buy of ["rt", "da"]) {
    if (!region[buy] || !region.da) continue;
    for (const load of LOADS) {
      const f = L.years(L.monthsRuled(files, region.id, buy, load.x, "forecast").months);
      const h = new Map(L.years(L.monthsRuled(files, region.id, buy, load.x, "hindsight").months).map((r) => [r.y, r]));
      // the threshold alone, with no budget of hours (the load may be off in more hours than named)
      const ys = [...files].sort((a, b) => a.year - b.year);
      const pay = ys.map((file) => L.expand(file, region.id, buy)), da = buy === "da" ? pay : ys.map((file) => L.expand(file, region.id, "da"));
      const consecutive = ys.every((file, i) => i === 0 || file.year === ys[i - 1].year + 1);
      const free = consecutive && load.x.run !== "shift" ? L.ruleWeights(pay, da, load.x, false).w : null;
      const u = new Map(free ? L.years(ys.flatMap((file, i) => L.monthsOfYear(file.year, pay[i], free[i], file.tight))).map((r) => [r.y, r]) : []);
      for (const r of f) {
        const k = h.get(r.y);
        if (!r.complete || !k || !k.complete || r.flat === null || r.per === null || k.per === null) continue;
        const saved = r.flat - r.per, foreseen = k.flat - k.per;
        out.push({ grid, region: region.id, buy, load: load.name, year: r.y, flat: r.flat, rule: r.per, foreseen: k.per, saved, saved_foreseen: foreseen,
          kept_pct: foreseen > 0 ? (100 * saved) / foreseen : null, hours_off_rule: r.down, hours_off_foreseen: k.down,
          no_budget: u.get(r.y)?.per ?? null, no_budget_hours_off: u.get(r.y)?.down ?? null });
      }
    }
  }
}
if (asJson) console.log(JSON.stringify(out));
else {
  const f = (v) => (v === null ? "" : v.toFixed(2));
  console.log("grid | region | market | load | year | flat | rule | if foreseen | saved by rule | saved if foreseen | rule kept % | hours off (rule / foreseen) | threshold alone, no budget | its hours off");
  for (const r of out) console.log([r.grid, r.region, r.buy, r.load, r.year, f(r.flat), f(r.rule), f(r.foreseen), f(r.saved), f(r.saved_foreseen), r.kept_pct === null ? "" : r.kept_pct.toFixed(0), `${r.hours_off_rule} / ${r.hours_off_foreseen}`, f(r.no_budget), r.no_budget_hours_off ?? ""].join(" | "));
}
