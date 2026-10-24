// Energy Research Warehouse (ERW) site, session 1185 (chain 091): lib/lower48.ts, the Lower 48's view by month of the
// Grid tool's energy mix panel (grid_mix_us48, mixp=month): the sum of the 48 contiguous states and DC in
// state_generation_mix_monthly (EIA-923). On a committed fixture of real rows (fixtures/lower48_mix.json: every row of
// the 49 locations from 2025-08 to 2026-08, read once with the anon key on 24 October 2026), every key the view writes is
// recomputed here as scripts/check-values.mjs recomputes it (states_sum through lib/lower48.ts statesSum on the rows of
// its range, calc|pct) to the view's own value; a state month taken out of the rows inside one test (said there) is not
// drawn, not summed, and named. Needs no build, no network and no node_modules.
//
//   node scripts/test-lower48.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as L from "../lib/lower48.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const FIX = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "lower48_mix.json"), "utf-8"));
/** The fixture's rows as the table's: one row a location, group and month with a value (none where the value is null). */
const ROWS = Object.entries(FIX.months).flatMap(([m, states]) => Object.entries(states).flatMap(([st, vals]) =>
  vals.map((v, i) => (v === null ? null : { entity: `eia:${st}`, variable: L.varOf(FIX.stems[i]), ts_utc: `${m}-01T00:00:00+00:00`, value: v })).filter(Boolean)));

/** A key recomputed as scripts/check-values.mjs truth() does, on the given rows in place of Supabase. */
function truth(check, rows) {
  const p = check.split("|");
  if (p[0] === "states_sum") {
    const [, table, variable, start, end, group] = p;
    assert.equal(table, L.STATE_MIX);
    const entities = L.groupEntities(group);
    // check-values reads the group's rows of every variable from start to end (entity in the group, ts_utc in the range)
    const read = rows.filter((r) => entities.includes(r.entity) && Date.parse(r.ts_utc) >= Date.parse(start) && Date.parse(r.ts_utc) < Date.parse(end));
    return L.statesSum(read, entities, variable.split(","), start, end);
  }
  if (p[0] === "calc") {
    const [, op, a, b] = p;
    const x = Number(truth(a.replaceAll("~", "|"), rows)), y = Number(truth(b.replaceAll("~", "|"), rows));
    return op === "pct" ? (x / y) * 100 : undefined;
  }
  throw new Error(`a key kind this test does not know: ${check}`);
}
const same = (a, b) => Math.abs(Number(a) - Number(b)) < 1e-9 * Math.max(1, Math.abs(Number(a)));
const checkFig = (f, rows) => { const v = truth(f.check, rows); assert.ok(v !== undefined && same(v, f.raw), `${f.check}: recomputed ${v}, the view ${f.raw}`); assert.ok(f.tip.length > 20, f.check); };
const figsOf = (m) => [m.total, m.totalYear, ...m.fuels.flatMap((f) => [f.mwh, f.share, f.year])].filter(Boolean);

let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };

test("the group is the 48 contiguous states and DC: not Alaska, Hawaii, Puerto Rico or the United States", () => {
  assert.equal(L.LOWER48_STATES.length, 49);
  assert.equal(new Set(L.LOWER48_STATES).size, 49);
  assert.ok(L.LOWER48_STATES.includes("DC"));
  for (const x of ["AK", "HI", "PR", "US"]) assert.ok(!L.LOWER48_STATES.includes(x), x);
  assert.deepEqual(L.groupEntities("lower48"), L.LOWER48_STATES.map((s) => `eia:${s}`));
  assert.throws(() => L.groupEntities("us"), /no group named us/);
  assert.deepEqual(Object.keys(FIX.months["2026-08"]).sort(), [...L.LOWER48_STATES].sort(), "the fixture holds the 49");
});

test("the groups are components/mix/Now.tsx's MONTHLY_FUELS, the method note's nine", () => {
  const now = fs.readFileSync(path.join(SITE, "components", "mix", "Now.tsx"), "utf-8");
  for (const f of L.LOWER48_FUELS) assert.ok(now.includes(`{ key: "${f.key}", label: "${f.label}", color: "${f.color}" }`), f.key);
  assert.deepEqual(FIX.stems, L.LOWER48_FUELS.map((f) => f.key));
  const note = fs.readFileSync(path.join(SITE, "..", "docs", "methods", "generation_mix.md"), "utf-8");
  assert.ok(note.includes("`net_generation_<natural_gas, coal, nuclear, wind, solar, hydro, other_renewables, oil_and_other, not_itemized>_mwh`"));
});

const m = L.lower48Monthly(ROWS);
test("the months: every month the 49 hold, the newest the table's (2026-08), the twelve to it", () => {
  assert.equal(m.newest, "2026-08-01");
  assert.equal(m.months.length, 13);
  assert.equal(m.months[0], "2025-08-01");
  assert.equal(m.from, "2025-09-01T00:00:00Z");
  assert.equal(m.to, "2026-09-01T00:00:00Z");
  assert.deepEqual(m.notHeld, []);
  assert.equal(L.lower48Monthly(ROWS, 5).months.length, 5);
});

test("every figure's key recomputes to the view's value (states_sum, calc|pct), as check-values recomputes it", () => {
  const figs = figsOf(m);
  assert.equal(figs.length, 2 + 9 * 3);
  for (const f of figs) checkFig(f, ROWS);
  assert.equal(m.total.check, `states_sum|state_generation_mix_monthly|${L.LOWER48_VARIABLES.join(",")}|2026-08-01T00:00:00Z|2026-09-01T00:00:00Z|lower48`);
  assert.equal(m.fuels.find((f) => f.key === "coal").year.check, "states_sum|state_generation_mix_monthly|net_generation_coal_mwh|2025-09-01T00:00:00Z|2026-09-01T00:00:00Z|lower48");
  const p = L.parseStatesSum(m.total.check);
  assert.deepEqual([p.table, p.variables.length, p.start, p.end, p.group], [L.STATE_MIX, 9, "2026-08-01T00:00:00Z", "2026-09-01T00:00:00Z", "lower48"]);
});

test("the sums are the rows': the month's total is every row of the 49 that month, and the shares add to 100", () => {
  const rowsOf = (mo) => ROWS.filter((r) => r.ts_utc.startsWith(mo));
  assert.ok(same(m.total.raw, rowsOf("2026-08").reduce((a, r) => a + r.value, 0)));
  assert.ok(same(m.totalYear.raw, ROWS.filter((r) => r.ts_utc >= "2025-09").reduce((a, r) => a + r.value, 0)));
  const coal = ROWS.filter((r) => r.ts_utc.startsWith("2026-08") && r.variable === "net_generation_coal_mwh").reduce((a, r) => a + r.value, 0);
  assert.ok(same(m.fuels.find((f) => f.key === "coal").mwh.raw, coal));
  assert.ok(Math.abs(m.fuels.reduce((a, f) => a + (f.share?.raw ?? 0), 0) - 100) < 1e-9);
  // the chart's values: the group's sum each month drawn
  const gas = m.fuels.find((f) => f.key === "natural_gas");
  assert.ok(same(gas.values[0], ROWS.filter((r) => r.ts_utc.startsWith("2025-08") && r.variable === "net_generation_natural_gas_mwh").reduce((a, r) => a + r.value, 0)));
});

test("a month one location does not hold is not drawn, not summed, and named (DC's 2026-06 taken out of the rows here)", () => {
  // made up inside this test only: the real table holds DC in 2026-06
  const rows = ROWS.filter((r) => !(r.entity === "eia:DC" && r.ts_utc.startsWith("2026-06")));
  const x = L.lower48Monthly(rows);
  assert.ok(!x.months.includes("2026-06-01"));
  assert.equal(x.months.length, 12);
  assert.deepEqual(x.notHeld, [{ month: "2026-06", missing: ["DC"] }]);
  const june = ROWS.filter((r) => r.ts_utc.startsWith("2026-06") && r.entity !== "eia:DC").reduce((a, r) => a + r.value, 0);
  assert.ok(same(x.totalYear.raw, m.totalYear.raw - june - ROWS.filter((r) => r.ts_utc.startsWith("2026-06") && r.entity === "eia:DC").reduce((a, r) => a + r.value, 0)));
  for (const f of figsOf(x)) checkFig(f, rows);
  assert.ok(x.totalYear.tip.includes("not drawn: 2026-06"));
  // a range of one month a location misses recomputes to nothing: the month is never a figure
  assert.equal(L.statesSum(rows, L.LOWER48_ENTITIES, L.LOWER48_VARIABLES, "2026-06-01T00:00:00Z", "2026-07-01T00:00:00Z"), undefined);
  // and a month absent from every location is named "all"
  const y = L.lower48Monthly(ROWS.filter((r) => !r.ts_utc.startsWith("2026-03")));
  assert.deepEqual(y.notHeld, [{ month: "2026-03", missing: ["all"] }]);
  assert.equal(L.lower48Monthly([]), null);
});

test("a group no location has in the newest month draws no figure for it; a location's absent group adds nothing", () => {
  const rows = ROWS.filter((r) => !(r.variable === "net_generation_not_itemized_mwh" && r.ts_utc.startsWith("2026-08")));
  const x = L.lower48Monthly(rows);
  const ni = x.fuels.find((f) => f.key === "not_itemized");
  assert.equal(ni.mwh, null);
  assert.equal(ni.share, null);
  assert.ok(ni.year, "the twelve months still hold it");
  for (const f of figsOf(x)) checkFig(f, rows);
});

test("check-values, check-methods and the license gate know the kind; the panel's address is read", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('if (p[0] === "states_sum") {'));
  assert.ok(cv.includes("return L.statesSum(statesRows.get(k), entities, variable.split(\",\"), start, end);"));
  assert.ok(cv.includes('"/grid?grid=us48&mixp=month",'));
  assert.ok(fs.readFileSync(path.join(here, "check-methods.mjs"), "utf-8").includes("states_sum: [1, 2],"));
  assert.ok(fs.readFileSync(path.join(SITE, "components", "Num.tsx"), "utf-8").includes('else if (head === "states_sum") table = p[1] ?? "";'));
  assert.ok(fs.readFileSync(path.join(here, "grid-files.mjs"), "utf-8").includes('["/grid?grid=us48&mixp=month", ["grid_mix_us48_monthly"]]'));
});

test("the view says it is the sum of the states from EIA-923, not EIA-930's US48, and links its method", () => {
  const v = fs.readFileSync(path.join(SITE, "components", "grid", "Lower48Mix.tsx"), "utf-8");
  assert.ok(v.includes("not EIA-930&apos;s US48 total"));
  assert.ok(v.includes("<SiteLink href={METHOD_MIX_US48}>Method: the Lower 48 by month, the sum of the states</SiteLink>"));
  const mv = fs.readFileSync(path.join(SITE, "components", "grid", "MixView.tsx"), "utf-8");
  assert.ok(!mv.includes('words="not built for the Lower 48"'));
  assert.ok(mv.includes("series(STATE_MIX, { entities: LOWER48_ENTITIES"));
});

console.log(`${n} tests passed`);
