// Energy Research Warehouse (ERW) site, session 1116: the board's held rows and stale closes, on the site's own file
// (data/board.json). No request, no build.
//
//   node --import ./scripts/alias-register.mjs scripts/test-board-1116.mjs
//
// What is held here: holdRows makes every row of a grid held for a license on the day "license needed" in place (its
// name, label, group and tags kept, every figure dropped), leaves those grids' week rows and spikes out, and changes no
// other row; MISO's rows stay "paused" and PJM's "licensed source needed"; with no grid held the file is unchanged.
// closeAge counts a close's age in whole UTC days from its date to the build's day and marks it stale past 10 days
// (daily), 17 (weekly) or 132 (monthly); the twelve numbers at the top are none of them stale.
import assert from "node:assert/strict";
import fs from "node:fs";

const b = await import("../lib/board.ts");
const lic = await import("../lib/license.ts");
const file = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf8"));
const HELD = lic.licenseHeldGrids().map(lic.gridName);

let n = 0, failed = 0;
const test = (name, f) => {
  n += 1;
  try { f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};

test("the grids held on the day are the status file's: ISO-NE, MISO and NYISO", () => {
  assert.deepEqual([...HELD].sort(), ["ISO-NE", "MISO", "NYISO"]);
});

test("every row of ISO-NE and NYISO is license needed in place, with no figure", () => {
  const held = b.holdRows(file, HELD);
  assert.deepEqual(held.held, ["ISO-NE", "NYISO"]);
  const before = new Map(file.rows.map((r) => [r.id, r]));
  let made = 0;
  for (const r of held.rows) {
    const g = b.gridOfRow(r), was = before.get(r.id);
    if (g === "ISO-NE" || g === "NYISO") {
      if (was.status === "not_held") { assert.deepEqual(r, was, r.id); continue; }
      assert.equal(r.status, "license", r.id);
      assert.equal(b.PLACEHOLDER[r.status], "license needed");
      assert.match(r.note, /license needed/);
      for (const k of ["last", "moves", "range", "avg7", "avg30", "lo30", "hi30", "spark", "hourly"]) assert.equal(r[k], undefined, `${r.id} ${k}`);
      for (const k of ["id", "group", "label", "at", "code", "unit", "tags"]) assert.deepEqual(r[k], was[k], `${r.id} ${k}`);
      if (was.status === "ok") made += 1;
    } else assert.equal(r, was, r.id);               // every other row is the same object, untouched
  }
  assert.equal(made, file.rows.filter((r) => ["ISO-NE", "NYISO"].includes(b.gridOfRow(r)) && r.status === "ok").length);
  assert.ok(made >= 90, `${made} rows that carried figures`);   // 94 on the file of 23 October 2026
  assert.ok(!held.week.some((w) => w.grid === "ISO-NE" || w.grid === "NYISO") && !held.spikes.some((s) => s.grid === "ISO-NE" || s.grid === "NYISO"));
  assert.ok(held.week.length > 0 && held.week.length === file.week.filter((w) => !["ISO-NE", "NYISO"].includes(w.grid)).length);
});

test("MISO stays paused and PJM licensed; no grid held leaves the file as it is", () => {
  const held = b.holdRows(file, HELD);
  assert.ok(held.rows.filter((r) => b.gridOfRow(r) === "MISO").every((r) => r.status === "paused"));
  assert.ok(held.rows.filter((r) => b.gridOfRow(r) === "PJM").every((r) => r.status === "licensed"));
  const none = b.holdRows(file, []);
  assert.equal(none.rows, file.rows);
  assert.deepEqual(none.held, []);
});

test("a close's age and the stale thresholds", () => {
  const row = (t, freq) => ({ id: "x", freq, last: { t, v: 1 } });
  const built = "2026-10-23T15:07:43Z";
  assert.equal(b.ageDays("2026-10-13", built), 10);
  assert.equal(b.closeAge(row("2026-10-13", "D"), built).stale, false);
  assert.equal(b.closeAge(row("2026-10-12", "D"), built).stale, true);
  assert.equal(b.closeAge(row("2026-10-06", "W"), built).stale, false);
  assert.equal(b.closeAge(row("2026-10-05", "W"), built).stale, true);
  assert.equal(b.closeAge(row("2026-06-13", "M"), built).stale, false);
  assert.equal(b.closeAge(row("2026-06-12", "M"), built).stale, true);
  assert.match(b.closeAge(row("2026-10-20", "D"), built).words, /^3 days before the board was built on 23 Oct 2026$/);
  assert.match(b.closeAge(row("2026-10-24", "D"), built).words, /^1 day after the board was built/);
  assert.match(b.closeAge(row("2026-10-03", "D"), built).words, /Stale: a daily series is marked stale past 10 days/);
  assert.equal(b.closeAge({ id: "x", freq: "" }, built), null);
});

test("on the file: SPP's ancillary prices of 3 October and CARB's weekly credits are stale; none of the top twelve is", () => {
  const held = b.holdRows(file, HELD);
  const stale = held.rows.filter((r) => r.status === "ok" && b.closeAge(r, held.built)?.stale).map((r) => r.id);
  if (file.built.startsWith("2026-10-23")) {
    assert.ok(stale.includes("spp-spp-as-price-dam-regup") && stale.includes("carb-lcfs-avg"), stale.slice(0, 8).join(", "));
  }
  for (const r of b.topRows(held)) assert.equal(b.closeAge(r, held.built).stale, false, r.id);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
