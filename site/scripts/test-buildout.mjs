// Energy Research Warehouse (ERW) site, session 69: the storage build-out page's model on its fixture.
//
//   node scripts/test-buildout.mjs
//
// Feeds lib/buildout.ts the fixture (tests/fixtures/session69/storage_buildout_monthly.csv: real values cut from the
// scratch table) and checks, for every grid and both measures: the months the page reads; that every value shown is a
// row of the table under its own key; that the duration buckets sum to the total in every year; that the United States
// is the seven grids plus the units outside them; the summary sentence. And that the page's production code holds no
// fixture: it reads Supabase and nothing else. Exits 1 on a failure. No request leaves the machine.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { BUCKETS, GRIDS, OUTSIDE, checkKey, choices, direction, index, monthName, monthsNeeded, shown, tsOf, view, yearBefore } from "../lib/buildout.ts";
import { fixtureRows } from "./buildout-stub.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
let bad = 0, n = 0;
const check = (ok, what) => { n++; if (!ok) { bad++; console.log(`FAIL ${what}`); } };
const near = (a, b) => Math.abs(a - b) < 1e-6 * Math.max(1, Math.abs(a), Math.abs(b));

const rows = fixtureRows();
const { get, newest } = index(rows);
check(newest === "2026-08", `the fixture's newest month is 2026-08 (${newest})`);

// the months the page reads are the fixture's months, so the fixture answers the page's query in full
const months = monthsNeeded(newest);
check(months.join() === [...new Set(rows.map((r) => r.ts_utc.slice(0, 7)))].sort().join(), `monthsNeeded(${newest}) is the fixture's months: ${months.join(" ")}`);
check(monthsNeeded("2025-12").join() === "2015-12,2016-12,2017-12,2018-12,2019-12,2020-12,2021-12,2022-12,2023-12,2024-12,2025-12", "a December newest month needs the Decembers only");
check(yearBefore("2026-08") === "2025-08" && tsOf("2026-08") === "2026-08-01T00:00:00Z" && monthName("2026-08") === "August 2026", "month helpers");
check(choices({}).grid.slug === "us" && choices({}).measure === "mw" && choices({ grid: "nope", measure: "x" }).grid.slug === "us"
  && choices({ grid: "ercot", measure: "mwh" }).grid.entity === "iso:ercot" && choices({ grid: "ercot", measure: "mwh" }).measure === "mwh", "choices: defaults, wrong values, a named grid");
check(shown(18204.5) === "18,204.50" && shown(1137) === "1,137" && shown(2.7609) === "2.76", "numbers are written whole or with 2 decimals");
check(direction(2, 1) === "up from" && direction(1, 2) === "down from" && direction(1, 1) === "unchanged from", "direction");
check(view([], GRIDS[0], "mw") === null, "no rows, no view");

for (const grid of GRIDS) {
  for (const measure of ["mw", "mwh"]) {
    const v = view(rows, grid, measure);
    const tag = `${grid.slug} ${measure}`;
    check(v && v.newest === "2026-08" && v.before === "2025-08", `${tag}: newest and the month twelve before`);
    check(v.years.length === 12 && v.years[0].label === "2015" && v.years.at(-1).label === "2026 to August" && v.years.at(-2).month === "2025-12", `${tag}: twelve bars, 2015 to the year so far`);
    for (const y of v.years) {
      const parts = y.buckets.reduce((a, b) => a + (b.row?.value ?? NaN), 0) + (measure === "mw" ? y.notReported?.value ?? NaN : 0);
      check(y.total && near(parts, y.total.value), `${tag} ${y.month}: the buckets sum to the total (${parts} against ${y.total?.value})`);
      check(y.buckets.every((b) => b.row && b.row.variable === `battery_operating_${measure}_${b.key}` && b.row.ts_utc.startsWith(y.month)), `${tag} ${y.month}: each bucket is its own row`);
    }
    // every row the view carries is the table's row under the key the page writes
    const held = [v.mw, v.mwh, v.units, v.mwBefore, v.mwhBefore, v.addedMw, v.addedMwh, v.notReportedMw, ...v.years.flatMap((y) => [y.total, y.solar, y.notReported, ...y.buckets.map((b) => b.row)]),
      ...v.table.flatMap((g) => [g.mw, g.mwh, g.units, g.addedMw, g.addedMwh, g.planned, g.underConstruction, ...g.plannedByYear.map((p) => p.row)])];
    check(held.every((r) => r !== undefined), `${tag}: no sum the page shows is missing`);
    check(held.filter(Boolean).every((r) => get(r.entity, r.variable, r.ts_utc.slice(0, 7)) === r && checkKey(r) === `series|storage_buildout_monthly|${r.entity}|${r.variable}|${r.ts_utc}`), `${tag}: every value is a table row under its check key`);
    check(v.mw.entity === grid.entity && v.mwBefore.ts_utc.startsWith("2025-08") && v.addedMw.ts_utc.startsWith("2026-08"), `${tag}: the headline rows are the grid's`);
    check(near(v.addedMw.value, v.mw.value - v.mwBefore.value) && near(v.addedMwh.value, v.mwh.value - v.mwhBefore.value), `${tag}: added in twelve months is the newest month less the month twelve before`);
    if (v.hours) check(Math.abs(v.hours.value - v.mwh.value / (v.mw.value - v.notReportedMw.value)) < 0.00006, `${tag}: average hours is MWh over the MW that report energy`);
    // the table by grid: the seven, outside, then the United States; the US is the sum of the others
    check(v.table.map((g) => g.slug).join() === "caiso,ercot,isone,miso,nyiso,pjm,spp,outside,us", `${tag}: the table's rows`);
    const us = v.table.at(-1), parts = v.table.slice(0, -1);
    for (const k of ["mw", "mwh", "units", "addedMw", "addedMwh", "planned", "underConstruction"]) check(near(parts.reduce((a, g) => a + g[k].value, 0), us[k].value), `${tag}: the United States ${k} is the seven grids plus the units outside them`);
    check(v.plannedYears.join() === "2026,2027,2028,2029,2030,2031", `${tag}: planned years ${v.plannedYears.join()}`);
    for (const g of v.table) check(near(g.plannedByYear.reduce((a, p) => a + p.row.value, 0), g.planned.value), `${tag}: ${g.slug} planned by year sums to planned`);
    for (const [i, p] of us.plannedByYear.entries()) check(near(parts.reduce((a, g) => a + g.plannedByYear[i].row.value, 0), p.row.value), `${tag}: planned ${p.year} sums over grids`);
    // the summary sentence, as the page writes it
    const s = `${grid.name} has ${shown(v.mw.value)} MW of batteries holding ${shown(v.mwh.value)} MWh, an average of ${shown(v.hours.value)} hours, ${direction(v.mw.value, v.mwBefore.value)} ${shown(v.mwBefore.value)} MW a year ago.`;
    const words = s.split(/\s+/).length;
    check(words >= 20 && words <= 30, `${tag}: the summary sentence is about 25 words (${words})`);
    if (measure === "mw") console.log(`  ${s}`);
  }
}
check(OUTSIDE.entity === "us:outside_isos" && BUCKETS.map((b) => b.key).join() === "lt2h,2to4h,4to6h,ge6h", "the buckets run shortest first");

// the production code path holds no fixture: the page, its reader, its pieces and the model read no file and name no test path
for (const f of ["app/storage/buildout/page.tsx", "app/storage/buildout/read.ts", "app/storage/buildout/parts.tsx", "lib/buildout.ts"]) {
  const src = fs.readFileSync(path.join(here, "..", f), "utf-8");
  check(!/node:fs|from "fs"|readFileSync|fixtures\/|\.csv|buildout-stub|\.json/.test(src), `${f} reads no file and no fixture`);
  check(!src.includes("—"), `${f} has no em dash`);
}
const read = fs.readFileSync(path.join(here, "..", "app/storage/buildout/read.ts"), "utf-8");
check(read.includes('import "server-only"') && read.includes('from "@/lib/supabase"') && (read.match(/rest</g) ?? []).length === 2, "the reader is two reads through lib/supabase.ts");
const page = fs.readFileSync(path.join(here, "..", "app/storage/buildout/page.tsx"), "utf-8");
check(page.includes("attempt(buildoutRows)"), "the page reads through its reader");

console.log(bad ? `${bad} of ${n} checks FAILED` : `storage build-out model: ${n} checks pass`);
process.exit(bad ? 1 : 0);
