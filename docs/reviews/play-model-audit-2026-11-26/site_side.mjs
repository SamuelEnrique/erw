// Session 10227 (play audit): the same plays scored by the site's own code (site/lib/battery.ts, as the page and the
// server's scorer call it), to set beside restate.py's independent figures. Reads plays.json and extract.json; writes
// site_side.json. No network, no write route.
//   node runs/c10227/site_side.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const B = await import(pathToFileURL(path.join(root, "site", "lib", "battery.ts")).href);
const levels = JSON.parse(fs.readFileSync(path.join(root, "site", "data", "battery_levels.json"), "utf-8")).levels;
const ex = JSON.parse(fs.readFileSync(path.join(here, "extract.json"), "utf-8"));
const day = Object.keys(ex.recent_rt).sort().pop();
const r = ex.recent_rt[day]["ercot:HB_HUBAVG"].slice().sort((a, b) => (a[0] < b[0] ? -1 : 1));
const all = [{ slug: "today", date: day, ts_utc: r.map((x) => x[0]), price: r.map((x) => x[1]) }, ...levels];
const plays = JSON.parse(fs.readFileSync(path.join(here, "plays.json"), "utf-8"));
const out = {};
const c4 = (v) => Math.round(v * 10_000) / 10_000;  // the server's rounding (lib/game.ts scoreOn)
for (const L of all) {
  for (const mode of ["normal", "hard", "easy"]) {
    const rules = B.rulesOf(B.DEFAULT_SETTINGS, mode, []);
    const o = B.optimum(L.price, rules);
    const pl = plays[`${L.date}|${mode === "easy" ? "normal" : mode}`];
    const res = {};
    for (const [k, a] of Object.entries({ ...pl, site_best: o.actions })) {
      const s = B.simulate(L.price, a, rules);
      const t = B.tally(L.price, a, rules);
      res[k] = { score: s.score, server: c4(s.score), cash: s.cash, wear: s.wear, bonus: s.bonus, penalty: s.penalty, end: s.end, why: s.why,
        soc_end: s.soc[s.soc.length - 1], bought: t.boughtKwh, sold: t.soldKwh, buy_avg: t.buyPrice, sell_avg: t.sellPrice };
    }
    out[`${L.date}|${mode}`] = { optimum: o.score, server_optimal: c4(o.score), none: B.noBattery(L.price, rules), plays: res, preset: B.presetOf(B.DEFAULT_SETTINGS, mode) };
  }
}
// the roof: the levels with a solar shape, on Hard
for (const L of levels.filter((l) => l.solar)) {
  const rules = B.rulesOf(B.DEFAULT_SETTINGS, "hard", ["solar"]);
  const o = B.optimum(L.price, rules, L.solar);
  out[`${L.date}|hard-solar`] = { optimum: o.score, none: B.noBattery(L.price, rules, L.solar) };
}
fs.writeFileSync(path.join(here, "site_side.json"), JSON.stringify(out, null, 1));
for (const [k, v] of Object.entries(out)) console.log(k, "optimum", v.optimum.toFixed(6), v.plays ? `best ${v.plays.best.score.toFixed(6)} naive ${v.plays.naive.score.toFixed(4)} bad ${v.plays.bad.score.toFixed(4)} why_naive ${v.plays.naive.why || "-"}` : `none ${v.none.toFixed(4)}`);
