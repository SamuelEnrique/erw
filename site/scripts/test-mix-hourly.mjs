// Energy Research Warehouse (ERW) site, session 1152 (chain 077): lib/mixHourly.ts, the figures of the Grid tool's energy
// mix panel (grid_mix_<grid>). On a committed fixture of real rows (tests/fixtures/session1152/mix_hourly_erco.json:
// ERCOT's eia930_all_generation and demand_mw from 2026-10-20, and iso:ercot's months of generation_mix_hourly_profile
// from 2025-09, read with the anon key): every key the panel writes is recomputed here the way scripts/check-values.mjs
// recomputes it (series, series_sum with one or several variables, series_max, series_esum, calc|pct) to the panel's
// own value. Needs no build, no network and no node_modules.
//
//   node scripts/test-mix-hourly.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as M from "../lib/mixHourly.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const FIX = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "session1152", "mix_hourly_erco.json"), "utf-8"));
const TABLES = { eia930_all_generation: FIX.generation, eia930_all_demand: FIX.demand, generation_mix_hourly_profile: FIX.monthly };
// the hourly chart's groups, as components/mix/Now.tsx HOURLY_FUELS writes them (checked against its text below)
const GROUPS = [
  { key: "gas", label: "Natural gas", vars: ["natural_gas"] },
  { key: "coal", label: "Coal", vars: ["coal"] },
  { key: "nuclear", label: "Nuclear", vars: ["nuclear"] },
  { key: "wind", label: "Wind", vars: ["wind", "wind_with_battery"] },
  { key: "solar", label: "Solar", vars: ["solar", "solar_with_battery"] },
  { key: "hydro", label: "Hydro", vars: ["hydro"] },
  { key: "storage", label: "Storage", vars: ["battery", "pumped_storage", "other_storage", "unknown_storage"] },
  { key: "other", label: "Other", vars: [] },
];
const MONTH_FUELS = [
  { key: "gas", label: "Natural gas", stem: "natural_gas" }, { key: "coal", label: "Coal", stem: "coal" }, { key: "nuclear", label: "Nuclear", stem: "nuclear" },
  { key: "wind", label: "Wind", stem: "wind" }, { key: "solar", label: "Solar", stem: "solar" }, { key: "hydro", label: "Hydro", stem: "hydro" },
  { key: "storage", label: "Storage", stem: "storage" }, { key: "other", label: "Other", stem: "other" },
];

/** A key recomputed as scripts/check-values.mjs truth() does, on the fixture's rows in place of Supabase. */
function truth(check) {
  const p = check.split("|");
  const t = (s) => Date.parse(s);
  if (p[0] === "series") {
    const [, table, entity, variable, at] = p;
    return TABLES[table].find((r) => r.entity === entity && r.variable === variable && t(r.ts_utc) === t(at))?.value;
  }
  if (p[0] === "series_sum" || p[0] === "series_max") {
    const [, table, variable, start, end, entity] = p;
    const vars = variable.includes(",") ? variable.split(",") : [variable];   // check-values: in.(...) for a list
    const rows = TABLES[table].filter((r) => vars.includes(r.variable) && t(r.ts_utc) >= t(start) && t(r.ts_utc) < t(end) && (!entity || r.entity === entity));
    if (!rows.length) return undefined;
    return p[0] === "series_max" ? Math.max(...rows.map((r) => r.value)) : rows.reduce((a, r) => a + r.value, 0);
  }
  if (p[0] === "series_esum") {
    const [, table, entity, variable, start, end] = p;
    const rows = TABLES[table].filter((r) => r.entity === entity && r.variable === variable && t(r.ts_utc) >= t(start) && t(r.ts_utc) < t(end));
    return rows.length ? rows.reduce((a, r) => a + r.value, 0) : undefined;
  }
  if (p[0] === "calc") {
    const [, op, a, b] = p;
    const x = Number(truth(a.replaceAll("~", "|"))), y = Number(truth(b.replaceAll("~", "|")));
    return op === "pct" ? (x / y) * 100 : undefined;
  }
  throw new Error(`a key kind this test does not know: ${check}`);
}
const same = (a, b) => Math.abs(Number(a) - Number(b)) < 1e-9 * Math.max(1, Math.abs(Number(a)));
const checkFig = (f) => { const v = truth(f.check); assert.ok(v !== undefined && same(v, f.raw), `${f.check}: recomputed ${v}, the panel ${f.raw}`); assert.ok(f.tip.length > 20, f.check); };

let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const H = 3_600_000;

test("the groups are components/mix/Now.tsx's HOURLY_FUELS", () => {
  const now = fs.readFileSync(path.join(here, "..", "components", "mix", "Now.tsx"), "utf-8");
  for (const g of GROUPS) assert.ok(now.includes(`{ key: "${g.key}", label: "${g.label}", vars: ${JSON.stringify(g.vars).replaceAll(",", ", ")} }`), g.key);
});

const m = M.mixHourly(FIX.generation, FIX.demand, GROUPS);
test("the headline is the 24 hours that end with the newest hour held", () => {
  assert.equal(M.isoZ(m.newest.t), "2026-10-22T23:00:00Z");
  assert.equal(M.isoZ(m.start), "2026-10-22T00:00:00Z");
  assert.equal(M.isoZ(m.end), "2026-10-23T00:00:00Z");
  assert.equal(m.hours, 24);
  assert.equal(m.entity, "eia930:ERCO");
});

test("every key of the hourly view recomputes to the panel's value", () => {
  for (const f of [m.total, m.newest.fig, m.peak.fig, ...m.fuels.flatMap((x) => [x.mwh, x.share])]) checkFig(f);
  assert.ok(m.total.check.startsWith("series_sum|eia930_all_generation|net_generation_mw|2026-10-22T00:00:00Z|2026-10-23T00:00:00Z|eia930:ERCO"));
});

test("the battery is storage, and the shares add up to about the whole", () => {
  const st = m.fuels.find((f) => f.key === "storage");
  assert.deepEqual(st.variables, ["net_generation_battery_mw"]);
  assert.ok(st.mwh.check.includes("|net_generation_battery_mw|"));
  const sum = m.fuels.reduce((a, f) => a + f.share.raw, 0);
  assert.ok(Math.abs(sum - 100) < 5, `the shares add to ${sum}`);
  assert.deepEqual(m.fuels.map((f) => f.key), ["gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"]);
});

test("the peak is the hour of highest demand in the 24 hours, inside them", () => {
  const inside = FIX.demand.filter((r) => Date.parse(r.ts_utc) >= m.start && Date.parse(r.ts_utc) < m.end);
  const top = Math.max(...inside.map((r) => r.value));
  assert.equal(m.peak.fig.raw, top);
  assert.ok(m.peak.t >= m.start && m.peak.t < m.end);
  assert.equal(inside.find((r) => Date.parse(r.ts_utc) === m.peak.t).value, top);
  assert.ok(m.peak.fig.check.startsWith("series_max|eia930_all_demand|demand_mw|"));
});

test("a day not complete: the 24 hours move back with the newest hour; a fuel group of several variables is one key", () => {
  const cut = Date.parse("2026-10-22T19:00:00Z");
  const gen = FIX.generation.filter((r) => Date.parse(r.ts_utc) < cut);
  // a second wind variable, added to the cut rows (a test row: the same hour's wind written as wind_with_battery, 0)
  const extra = gen.filter((r) => r.variable === "net_generation_wind_mw").map((r) => ({ ...r, variable: "net_generation_wind_with_battery_mw", value: 0 }));
  const p = M.mixHourly([...gen, ...extra], FIX.demand, GROUPS);
  assert.equal(M.isoZ(p.newest.t), "2026-10-22T18:00:00Z");
  assert.equal(M.isoZ(p.start), "2026-10-21T19:00:00Z");
  const wind = p.fuels.find((f) => f.key === "wind");
  assert.deepEqual(wind.variables, ["net_generation_wind_mw", "net_generation_wind_with_battery_mw"]);
  assert.ok(wind.mwh.check.includes("|net_generation_wind_mw,net_generation_wind_with_battery_mw|"));
  TABLES.eia930_all_generation = [...gen, ...extra];
  try { for (const f of [p.total, p.newest.fig, p.peak.fig, ...p.fuels.flatMap((x) => [x.mwh, x.share])]) checkFig(f); }
  finally { TABLES.eia930_all_generation = FIX.generation; }
});

test("no demand held: no peak; no generation: no panel", () => {
  assert.equal(M.mixHourly(FIX.generation, [], GROUPS).peak, null);
  assert.equal(M.mixHourly([], FIX.demand, GROUPS), null);
});

test("the age is whole hours from the hour's end", () => {
  const t = Date.parse("2026-10-22T23:00:00Z");
  assert.equal(M.hourAge(t, t + H), 0);
  assert.equal(M.hourAge(t, t + H + 59 * 60_000), 0);
  assert.equal(M.hourAge(t, t + 16 * H + 5 * 60_000), 15);
  assert.equal(M.hourAge(t, t), 0);
});

test("the monthly view: the months held, and every key recomputes", () => {
  const mm = M.mixMonthly(FIX.monthly, MONTH_FUELS);
  assert.equal(mm.months.length, 12);   // 2025-09 to 2026-09 without 2025-12, which the build did not write for ERCOT
  assert.equal(mm.newest, "2026-09-01");
  assert.equal(mm.from, "2025-10-01T00:00:00Z");
  assert.deepEqual(mm.notBuilt, ["2025-12"]);
  assert.equal(mm.to, "2026-10-01T00:00:00Z");
  assert.equal(mm.entity, "iso:ercot");
  for (const f of mm.fuels) for (const x of [f.mwh, f.share, f.year]) checkFig(x);
  checkFig(mm.days); checkFig(mm.daysInMonth);
  assert.equal(mm.fuels.find((f) => f.key === "gas").mwh.raw, 23813090);
  assert.equal(mm.fuels.find((f) => f.key === "gas").values.length, 12);
  // the twelve months' sum leaves out 2025-09, the thirteenth month back
  const gas = FIX.monthly.filter((r) => r.variable === "natural_gas_mwh" && r.ts_utc >= "2025-10");
  assert.equal(mm.fuels.find((f) => f.key === "gas").year.raw, gas.reduce((a, r) => a + r.value, 0));
  assert.equal(M.mixMonthly(FIX.monthly, MONTH_FUELS, 6).months.length, 6);
  assert.equal(M.mixMonthly([], MONTH_FUELS), null);
});

test("check-values sums a list of variables and reads the two monthly addresses", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('variable: variable.includes(",") ? `in.(${variable})` : `eq.${variable}`'));
  assert.ok(cv.includes('"/grid?grid=ercot&mixp=month", "/grid?grid=caiso&mixp=month"'));
});

console.log(`\n${n} tests passed`);
