// Energy Research Warehouse (ERW) site, session 1155 (chain 077): lib/caisoAlerts.ts, CAISO's alerts tied into the Grid
// tool (the state line grid_caisoalert_caiso, the alert days on the scarcity strip and on CAISO's monthly mix), on a
// committed fixture of real rows (scripts/fixtures/caiso_alerts.json: every notice of caiso_grid_emergencies from
// 2022-01-01, read once with the anon key on 23 October 2026). Every key the pages write is recomputed here as
// scripts/check-values.mjs recomputes it (aweValue on the table's rows), to the page's own value. Needs no build, no
// network and no node_modules.
//
//   node scripts/test-caiso-alerts.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as A from "../lib/caisoAlerts.ts";
import * as S from "../lib/scarcityStrip.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fx = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "caiso_alerts.json"), "utf-8"));
const rows = fx.rows;
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
// check-values reads event_date as PostgREST writes it (a timestamp) and event_type only
const asRead = rows.map((r) => ({ event_date: `${r.event_date}T00:00:00+00:00`, event_type: r.event_type }));
const recompute = (check) => A.aweValue(asRead, check);
const figsOf = (s) => [s.newest, s.lastSignal?.fig, s.lastFlex?.fig, s.lastEea?.fig, s.lastRmo?.fig, s.lastTx?.fig, s.signalDays, s.rmoDays].filter(Boolean);

// 23 October 2026, 19:00 UTC: noon in California, the day this session ran
const NOW = Date.parse("2026-10-23T19:00:00Z");
const s = A.alertState(rows, NOW);

test("the fixture is the real table's rows: 123 notices, 2022-06-10 to 2026-10-08", () => {
  assert.equal(fx.table, A.ALERT_TABLE);
  assert.equal(rows.length, 123);
  assert.equal(rows[0].event_date, "2022-06-10");
  assert.equal(rows.at(-1).event_date, "2026-10-08");
});

test("the alert set is the scarcity table's own signal: EEA and alerts, not rmo or transmission emergencies", () => {
  for (const t of ["eea_watch", "eea1", "eea2", "eea3", "flex_alert", "alert", "warning", "stage1", "stage2", "stage3"]) assert.ok(A.inGroup(t, "signal"), t);
  for (const t of ["rmo", "transmission_emergency", "vlrp", "load_interruption"]) assert.ok(!A.inGroup(t, "signal"), t);
  assert.ok(A.inGroup("rmo", "any"));
  assert.ok(!A.inGroup("rmo", "nothing"));
  assert.match(S.SCARCITY_GRIDS.caiso.own, /Energy Emergency Alert or a Flex Alert/);
});

test("today is the Pacific day: 23 October 2026, and 22 October before 07:00 UTC", () => {
  assert.equal(s.today, "2026-10-23");
  assert.equal(A.pacificDay(Date.parse("2026-10-23T06:59:00Z")), "2026-10-22");
  assert.equal(A.pacificDay(Date.parse("2026-01-15T08:00:00Z")), "2026-01-15");
});

test("the state on 23 October 2026: not held (the table ends 2026-10-08); the last alert the EEA Watch of 2024-07-24", () => {
  assert.equal(s.covered, false);
  assert.deepEqual(s.todayAlerts, []);
  assert.equal(s.newest.raw, "2026-10-08");
  assert.equal(s.newest.check, "awe|last|any|2026-10-23");
  assert.equal(s.lastSignal.day, "2024-07-24");
  assert.deepEqual(s.lastSignal.types, ["eea_watch"]);
  assert.deepEqual(s.lastSignal.regions, ["CAISO Grid"]);
  assert.equal(s.lastSignal.fig.check, "awe|last|signal|2026-10-23");
  assert.equal(s.lastEea.day, "2024-07-24");
  assert.equal(s.lastFlex.day, "2022-09-09");
  assert.equal(s.signalDays.raw, 0);
  assert.equal(s.signalDays.check, "awe|ndays|signal|2026-01-01|2026-10-23");
});

test("not alerts, named apart: restricted maintenance last 2026-10-08 on 6 days of 2026; a transmission emergency last 2025-04-30", () => {
  assert.equal(s.lastRmo.day, "2026-10-08");
  assert.deepEqual(s.lastRmo.types, ["rmo"]);
  assert.equal(s.rmoDays.raw, 6);
  assert.equal(s.lastTx.day, "2025-04-30");
  assert.deepEqual(s.lastTx.regions, ["Northern CA Region"]);
});

test("a day the table covers: in force on 2022-09-06 (the EEA 3 day), none on 2022-09-10", () => {
  const on = A.alertState(rows, Date.parse("2022-09-06T20:00:00Z"));
  assert.equal(on.covered, true);
  assert.ok(on.todayAlerts.includes("eea3"), on.todayAlerts.join());
  assert.ok(on.todayAlerts.includes("flex_alert"));
  assert.equal(on.todayAlerts[0], "eea_watch");   // in the order of the signal: the EEAs, then the Flex Alert
  const off = A.alertState(rows, Date.parse("2022-09-10T20:00:00Z"));
  assert.equal(off.covered, true);
  assert.deepEqual(off.todayAlerts, []);
  assert.equal(off.lastSignal.day, "2022-09-09");
});

test("every key of the state line is recomputed as check-values does, to the page's value", () => {
  const figs = figsOf(s);
  assert.equal(figs.length, 8);
  for (const f of figs) assert.equal(recompute(f.check), f.raw, f.check);
  assert.equal(new Set(figs.map((f) => f.check)).size, figs.length);   // lastSignal and lastEea share a day (2024-07-24), not a key
  for (const f of figs) assert.match(f.tip, /^caiso_grid_emergencies /);
});

test("the scarcity strip's window (1 to 30 September 2026, PST): no alert day; restricted maintenance on 9 and 10 September", () => {
  const w = S.windowOf("2026-10-01T07:00:00Z", S.SCARCITY_GRIDS.caiso.behind);
  const a = A.alertDays(rows, w.days);
  assert.deepEqual(a.cols, []);
  assert.deepEqual(a.rmo, ["2026-09-09", "2026-09-10"]);
  assert.deepEqual(a.tx, []);
  assert.equal(a.signal.check, "awe|ndays|signal|2026-09-01|2026-09-30");
  assert.equal(a.signal.raw, 0);
  assert.equal(a.rmoFig.raw, 2);
  for (const f of [a.signal, a.rmoFig]) assert.equal(recompute(f.check), f.raw, f.check);
});

test("a window that holds alert days marks their columns: 1 to 30 September 2022", () => {
  const days = Array.from({ length: 30 }, (_, i) => `2022-09-${String(i + 1).padStart(2, "0")}`);
  const a = A.alertDays(rows, days);
  const marked = a.cols.map((j) => days[j]);
  assert.ok(marked.includes("2022-09-06") && marked.includes("2022-09-09"), marked.join());
  assert.equal(a.signal.raw, marked.length);
  assert.equal(recompute(a.signal.check), a.signal.raw);
  assert.ok(a.byDay.get("2022-09-06").includes("eea3"));
});

test("the monthly mix (2024-09 to 2026-09): no alert month, so nothing is marked; August and September 2022 are marked, October not", () => {
  const months = [];
  for (let y = 2024, m = 9; y < 2026 || m <= 9; m === 12 ? (y += 1, m = 1) : (m += 1)) if (!(y === 2025 && m === 12)) months.push(`${y}-${String(m).padStart(2, "0")}-01`);
  assert.equal(months.length, 24);
  const al = A.alertMonths(rows, months);
  assert.equal(al.from, "2024-09-01");
  assert.equal(al.to, "2026-09-30");
  assert.deepEqual(al.months, []);
  assert.equal(al.signal.raw, 0);
  assert.equal(recompute(al.signal.check), 0);
  const old = A.alertMonths(rows, ["2022-08-01", "2022-09-01", "2022-10-01"]);
  assert.deepEqual(old.months.map((x) => x.month), ["2022-08-01", "2022-09-01"]);   // the Flex Alerts of 17 and 18 August 2022, the heat wave of September
  assert.equal(old.signal.raw, old.months[0].days.length + old.months[1].days.length);
  assert.ok(old.months[0].days.includes("2022-08-17"));
  assert.equal(recompute(old.signal.check), old.signal.raw);
});

test("a key aweValue does not know is left to check-values' own branch (session 58's awe|days)", () => {
  assert.equal(A.aweValue(asRead, "awe|days|rmo|2026"), undefined);
  assert.equal(A.aweValue(asRead, "awe|last|nothing|2026-10-23"), undefined);
  assert.equal(A.aweValue(asRead, "awe|last|signal|2021-12-31"), null);   // nothing in the fixture before 2022
});

test("check-values recomputes the new keys with this file, on every row of the table", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('if (p[0] === "awe" && (p[1] === "last" || p[1] === "ndays")) {'));
  assert.ok(cv.includes('await import("../lib/caisoAlerts.ts")'));
  assert.ok(cv.includes("A.aweValue("));
  assert.ok(cv.indexOf('p[1] === "ndays"') < cv.indexOf('if (p[0] === "awe") {'));
});

console.log(`${n} of ${n} passed`);
