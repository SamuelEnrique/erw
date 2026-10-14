// Energy Research Warehouse (ERW) site, session 263: the figures of the battery tool's review pack
// (docs/reviews/packs/battery.md) and of docs/methods/battery_earns_algorithm.md, section 11.3, that no check key on
// the page carries: recomputed with the page's own libraries (lib/batterystack.ts, lib/battery/finance.ts) from this
// script's own read of battery_stack_monthly in Supabase (the anon key, as scripts/check-values.mjs reads it) and from
// data/battery_scenario_steps.json, as the page reads them. Until session 263 these were the figures marked [c] in
// the old how-it-works note, computed once by docs/howitworks/computed/battery_headline.mjs from a table on the data
// machine; this script replaces that one-off run with a check any machine can make.
//
//   node scripts/check-battery-figures.mjs
//
// Each figure is compared with the value the pack prints, at the precision it prints. Prints one line a figure and
// exits 1 on any difference (or when the table cannot be read, or the file of steps no longer describes the table).
// The figures are those of the table as it stood on 2026-10-14 (the last twelve months October 2025 to September
// 2026). When the newest complete month moves (October 2026, about the first days of November) every figure moves:
// update EXPECTED, the pack and the methods note together, in the same commit. Reads only; writes nothing.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const B = await import("../lib/batterystack.ts");
const F = await import("../lib/battery/finance.ts");
const STEPS = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "battery_scenario_steps.json"), "utf-8"));

/** The pack's figures: name, the value printed, and the decimals it is printed to. */
export const EXPECTED = [
  // the headline of each case the pack quotes (scenario A at the defaults)
  ["ercot 4h foresight: last twelve months, USD per kW", 81.40, 2],
  ["ercot 4h foresight: last twelve months, USD for 100 MW", 8140219, 0],
  ["ercot 4h foresight: share from ancillary services, percent", 33, 0],
  ["ercot 4h foresight: a bad month, USD for 100 MW", 475477, 0],
  ["ercot 4h foresight: debt payments, USD a year for 100 MW", 2261119, 0],
  ["ercot 4h foresight: debt coverage, times", 2.63, 2],
  ["ercot 4h foresight: 2023 to 2025, a year, USD per kW", 255.08, 2],
  ["ercot 4h foresight: every year held, a year, USD per kW", 614.58, 2],
  ["ercot 4h foresight: without February 2021, a year, USD per kW", 269.68, 2],
  ["ercot 4h foresight: the one month's share of everything held, percent", 57, 0],
  ["ercot 4h foresight: NPV at the hurdle rate, USD million for 100 MW", -69.78, 2],
  ["ercot 4h foresight: IRR, percent a year", -8.8, 1],
  ["ercot 4h foresight: breakeven toll, USD per kW-month", 4.19, 2],
  ["ercot 4h dayahead: last twelve months, USD per kW", 73.00, 2],
  ["ercot 4h dayahead: share from ancillary services, percent", 35, 0],
  ["ercot 4h dayahead: debt coverage, times", 2.26, 2],
  ["caiso 4h foresight: last twelve months, USD per kW", 79.05, 2],
  ["caiso 4h dayahead: last twelve months, USD per kW", 64.96, 2],
  ["caiso 4h dayahead: share from ancillary services, percent", 51, 0],
  ["caiso 4h dayahead: debt coverage, times", 1.90, 2],
  // scenario A moved, the default case's revenue held
  ["contract 50 percent at USD 10: debt coverage, times", 3.48, 2],
  ["contract 50 percent at USD 10: NPV, USD million for 100 MW", -51.13, 2],
  ["capital cost 620: NPV, USD million for 100 MW", -23.12, 2],
  ["capital cost 620: IRR, percent a year", 2.1, 1],
  // the sensitivity chart at the defaults (data/battery_scenario_steps.json for efficiency and cycles)
  ["sensitivity: first row", "Cycles a day, at most", null],
  ["sensitivity: second row", "Capital cost", null],
  ["sensitivity: cycles, the move down to 0.5, USD million", 11.14, 2],
  ["sensitivity: cycles, the move up to 1.5, USD million", 1.40, 2],
  ["sensitivity: capital cost, the larger move, USD million", 9.52, 2],
  ["sensitivity: degradation, the larger move, USD million", 3.02, 2],
  ["scenario B at 92 percent and 2 cycles: last twelve months, USD per kW", 88.24, 2],
  ["1.5 cycles: last twelve months, USD per kW", 83.57, 2],
];

function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(here, "..", ".env.local");
  if (fs.existsSync(f)) for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
    const m = line.match(/^([A-Z_]+)=(.*)$/);
    if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
  }
  throw new Error(`${name} is not set`);
}

async function rowsOf(entity, strat, dur) {
  const origin = new URL(env("SUPABASE_URL")).origin, key = env("SUPABASE_ANON_KEY");
  const out = [];
  for (let off = 0; ; off += 1000) {
    const params = new URLSearchParams({ select: "variable,ts_utc,value", table_name: `eq.${B.TABLE}`, entity: `eq.${entity}`, variable: `like.${strat}_${dur}h_*`,
      order: "variable,ts_utc", limit: "1000", offset: String(off) });
    let res;
    for (let attempt = 0; attempt < 3; attempt++) {
      res = await fetch(`${origin}/rest/v1/series?${params}`, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
      if (res.ok || res.status !== 500) break;
      await new Promise((r) => setTimeout(r, attempt ? 3000 : 1000));
    }
    if (!res.ok) throw new Error(`series: HTTP ${res.status}`);
    const b = await res.json();
    out.push(...b.map((r) => ({ ...r, value: Number(r.value) })));
    if (b.length < 1000) return out;
  }
}

/** One case as the page computes it: its months, its inputs at scenario A's defaults, the stat function, and the
 * revenue of a step of efficiency and cycles exactly as Scenarios.tsx builds it (the page's months with the step's
 * totals over the months of the 36-month window). */
async function caseOf(grid, dur, strat) {
  const rows = await rowsOf(B.gridOf(grid).entity, strat, dur);
  const ms = B.monthsOf(rows, strat, dur);
  const d = F.defaultsOf(B.COSTS[dur]);
  const x = { ...B.inputsOf({ grid, dur: String(dur), strat }), fom: d.fom, ds: F.debtUsd(d, 100) };
  const need = (B.last36(ms)?.months ?? []).map((r) => r.m);
  const c = STEPS.cases[`${grid}|${strat}|${dur}`] ?? null;
  const state = F.stepState(c, ms, need);
  const steps = F.stepsOffered(STEPS, state);
  const revenue = (rte, cycles) => {
    let months = ms;
    if (rte !== F.MODEL.rte || cycles !== F.MODEL.cycles) {
      const t = state.ok ? F.cellTotals(c, rte, cycles) : null;
      if (!t) return null;
      months = ms.map((r) => (need.includes(r.m) && t.has(r.m) ? { ...r, total: t.get(r.m) } : r));
    }
    const l12 = B.lastTwelve(months);
    return l12 ? B.sumOf(l12, "total") / 1000 : null;
  };
  return { st: (s) => B.stat(rows, [], x, s), d, state, steps, revenue, last: B.lastTwelve(ms)?.[11]?.m ?? null };
}

const million = (perKw) => (perKw * 1000 * 100) / 1e6;
const got = new Map();
const e4f = await caseOf("ercot", 4, "foresight");
{
  const { st, d, revenue, steps, state } = e4f;
  const r = F.resultOf(d, revenue(86, 1));
  got.set("ercot 4h foresight: last twelve months, USD per kW", st("l12_kw:total"));
  got.set("ercot 4h foresight: last twelve months, USD for 100 MW", st("l12:total"));
  got.set("ercot 4h foresight: share from ancillary services, percent", st("l12_share:ancillary"));
  got.set("ercot 4h foresight: a bad month, USD for 100 MW", st("p10_36"));
  got.set("ercot 4h foresight: debt payments, USD a year for 100 MW", st("ds"));
  got.set("ercot 4h foresight: debt coverage, times", st("cover"));
  got.set("ercot 4h foresight: 2023 to 2025, a year, USD per kW", st("y3_kw:total"));
  got.set("ercot 4h foresight: every year held, a year, USD per kW", st("avg_kw:total"));
  got.set("ercot 4h foresight: without February 2021, a year, USD per kW", st("avg_without_kw:total"));
  got.set("ercot 4h foresight: the one month's share of everything held, percent", st("top_share"));
  got.set("ercot 4h foresight: NPV at the hurdle rate, USD million for 100 MW", million(r.npv));
  got.set("ercot 4h foresight: IRR, percent a year", r.irr);
  got.set("ercot 4h foresight: breakeven toll, USD per kW-month", r.toll);
  const rev = revenue(86, 1);
  const contract = F.resultOf({ ...d, cshare: 50, cprice: 10 }, rev), cheap = F.resultOf({ ...d, capex: 620 }, rev);
  got.set("contract 50 percent at USD 10: debt coverage, times", contract.coverage);
  got.set("contract 50 percent at USD 10: NPV, USD million for 100 MW", million(contract.npv));
  got.set("capital cost 620: NPV, USD million for 100 MW", million(cheap.npv));
  got.set("capital cost 620: IRR, percent a year", cheap.irr);
  if (!state.ok) console.log(`NOTE the file of steps no longer describes the table (${state.why}): the page offers the default step alone, and the step figures below cannot be computed`);
  const bars = F.sensitivity(d, revenue, steps);
  const bar = (k) => bars.find((b) => b.key === k);
  got.set("sensitivity: first row", bars[0]?.label ?? null);
  got.set("sensitivity: second row", bars[1]?.label ?? null);
  const cyc = bar("cycles");
  got.set("sensitivity: cycles, the move down to 0.5, USD million", cyc?.down && cyc.down.value === 0.5 ? million(Math.abs(cyc.down.npv - cyc.base)) : null);
  got.set("sensitivity: cycles, the move up to 1.5, USD million", cyc?.up && cyc.up.value === 1.5 ? million(Math.abs(cyc.up.npv - cyc.base)) : null);
  got.set("sensitivity: capital cost, the larger move, USD million", bar("capex") ? million(bar("capex").size) : null);
  got.set("sensitivity: degradation, the larger move, USD million", bar("deg") ? million(bar("deg").size) : null);
  got.set("scenario B at 92 percent and 2 cycles: last twelve months, USD per kW", revenue(92, 2));
  got.set("1.5 cycles: last twelve months, USD per kW", revenue(86, 1.5));
}
const e4d = await caseOf("ercot", 4, "dayahead");
got.set("ercot 4h dayahead: last twelve months, USD per kW", e4d.st("l12_kw:total"));
got.set("ercot 4h dayahead: share from ancillary services, percent", e4d.st("l12_share:ancillary"));
got.set("ercot 4h dayahead: debt coverage, times", e4d.st("cover"));
const c4f = await caseOf("caiso", 4, "foresight");
got.set("caiso 4h foresight: last twelve months, USD per kW", c4f.st("l12_kw:total"));
const c4d = await caseOf("caiso", 4, "dayahead");
got.set("caiso 4h dayahead: last twelve months, USD per kW", c4d.st("l12_kw:total"));
got.set("caiso 4h dayahead: share from ancillary services, percent", c4d.st("l12_share:ancillary"));
got.set("caiso 4h dayahead: debt coverage, times", c4d.st("cover"));

let bad = 0;
console.log(`the last twelve months end ${e4f.last} (ERCOT) and ${c4f.last} (CAISO)`);
for (const [name, want, dp] of EXPECTED) {
  const v = got.get(name);
  const shown = v === null || v === undefined ? "none" : dp === null ? String(v) : Number(v).toFixed(dp);
  const wanted = dp === null ? String(want) : Number(want).toFixed(dp);
  const ok = shown === wanted;
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "DIFF"} ${name}: ${shown}${ok ? "" : ` (the pack prints ${wanted})`}`);
}
console.log(bad ? `${bad} of ${EXPECTED.length} figures differ from the pack` : `all ${EXPECTED.length} figures are the pack's`);
process.exit(bad ? 1 : 0);
