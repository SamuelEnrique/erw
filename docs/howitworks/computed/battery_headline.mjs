// Session 249: the numbers marked [c] in docs/howitworks/battery.md, computed with the page's own libraries
// (site/lib/batterystack.ts, site/lib/battery/finance.ts) from the table on this machine. Reads only; writes nothing.
//   node docs/howitworks/computed/battery_headline.mjs > docs/howitworks/computed/battery_headline.txt
// It needs warehouse/output/battery_stack_monthly.csv (the data machine holds it) and a node that reads TypeScript (22.18 or later).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..", "..", "..");
const B = await import(pathToFileURL(path.join(root, "site", "lib", "batterystack.ts")).href);
const F = await import(pathToFileURL(path.join(root, "site", "lib", "battery", "finance.ts")).href);

function read(name, withEvent) {
  const text = fs.readFileSync(path.join(root, "warehouse", "output", name), "utf-8");
  const lines = text.split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const ie = head.indexOf("event");
  return lines.slice(1).map((l) => {
    const p = l.split(",");
    return { entity: p[0], variable: p[1], ts_utc: p[2], value: Number(p[3]), event: withEvent ? p[ie] : undefined };
  });
}
const monthly = read("battery_stack_monthly.csv", false);
const header = fs.readFileSync(path.join(root, "warehouse", "output", "battery_stack_monthly.csv"), "utf-8").split(/\r?\n/).filter((l) => l.startsWith("# Retrieved"))[0];
console.log(header);

const two = (v) => (v === null ? "null" : v.toFixed(2));
for (const grid of ["ercot", "caiso"]) for (const dur of [2, 4, 8]) for (const strat of ["foresight", "dayahead"]) {
  const g = B.gridOf(grid);
  const rows = monthly.filter((r) => r.entity === g.entity && r.variable.startsWith(`${strat}_${dur}h_`));
  const d = F.defaultsOf(B.COSTS[dur]);
  const x = { ...B.inputsOf({ grid, dur: String(dur), strat }), fom: d.fom, ds: F.debtUsd(d, 100) };
  const st = (s) => B.stat(rows, [], x, s);
  const ms = B.monthsOf(rows, strat, dur);
  const l12 = B.lastTwelve(ms), w = B.last36(ms), bad = B.badMonth(w?.months ?? []);
  const kw = st("l12_kw:total");
  const r = kw === null ? null : F.resultOf(d, kw);
  console.log([
    `${grid} ${dur}h ${strat}`,
    `l12 ${l12 ? l12[0].m + ".." + l12[11].m : "none"}`,
    `kw ${two(kw)}`, `share_anc ${st("l12_share:ancillary")}`, `usd ${st("l12:total")}`,
    `bad ${st("p10_36")} ${bad ? bad.m : ""} n36 ${st("n36")}`,
    `ds ${x.ds}`, `cover ${two(st("cover"))}`,
    `y3 ${two(st("y3_kw:total"))}`, `avg ${two(st("avg_kw:total"))}`, `without ${two(st("avg_without_kw:total"))}`, `top ${st("top_share")}`,
    `out ${st("out")}`,
    r ? `npv/kW ${two(r.npv)} irr ${r.irr === null ? "none" : r.irr.toFixed(1)} toll ${two(r.toll)}` : "",
  ].join(" | "));
  if (dur === 4) {
    const ys = B.years(ms).map((y) => `${y.y}${y.complete ? "" : "(" + y.months + "m)"}:${Math.round((y.energy + y.ancillary) / 1000)}=${two(y.energy / 1000)}+${two(y.ancillary / 1000)}`);
    console.log("   years " + ys.join(" "));
    if (l12) console.log("   l12 streams " + ["energy", "ancillary", ...B.PRODUCTS[grid].map((p) => p.key)].map((s) => `${s} ${st("l12:" + s)}`).join(" "));
  }
}

// the default case's sensitivity, from the file of steps
const steps = JSON.parse(fs.readFileSync(path.join(root, "site", "data", "battery_scenario_steps.json"), "utf-8"));
const c = steps.cases["ercot|foresight|4"];
const d4 = F.defaultsOf(B.COSTS[4]);
const revOf = (rte, cycles) => { const v = c.cells[`${rte}|${cycles}`]; return v ? v.slice(-12).reduce((a, b) => a + b, 0) / 1000 : null; };
const bars = F.sensitivity(d4, revOf, { rte: steps.rte_steps, cycles: steps.cycle_steps });
console.log("sensitivity, ERCOT 4h foresight, 100 MW, USD million:");
for (const b of bars) console.log(`   ${b.label} (${b.step}): size ${(b.size * 100000 / 1e6).toFixed(2)} down ${b.down ? (b.down.npv * 100000 / 1e6).toFixed(2) + "@" + b.down.value : "none"} up ${b.up ? (b.up.npv * 100000 / 1e6).toFixed(2) + "@" + b.up.value : "none"} base ${(b.base * 100000 / 1e6).toFixed(2)}`);

// the demo's cases
const show = (label, a, rev) => { const r = F.resultOf(a, rev); console.log(`   ${label}: debt ${F.debtUsd(a, 100)} cover ${two(r.coverage)} npv ${(r.npv * 100000 / 1e6).toFixed(2)}m (${two(r.npv)}/kW) irr ${r.irr === null ? "none" : r.irr.toFixed(1)} toll ${two(r.toll)} tail ${(r.tail.pv * 100000 / 1e6).toFixed(2)}m years ${r.tail.years}`); };
const rev0 = revOf(86, 1);
console.log(`demo, revenue ${rev0}`);
show("defaults", d4, rev0);
show("capex 620", { ...d4, capex: 620 }, rev0);
show("contract 50% at 10", { ...d4, cshare: 50, cprice: 10 }, rev0);
show("B: rte 92, cycles 2", { ...d4, rte: 92, cycles: 2 }, revOf(92, 2));
show("B: capex 1300", { ...d4, capex: 1300 }, rev0);
show("old defaults 60/9.6", { ...d4, share: 60, hurdle: 9.6 }, rev0);
show("term 10", { ...d4, term: 10 }, rev0);
console.log(`   revenue at 92|2 ${revOf(92, 2)}; 89|1 ${revOf(89, 1)}; 86|0.5 ${revOf(86, 0.5)}; 86|1.5 ${revOf(86, 1.5)}`);
