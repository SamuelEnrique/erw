// Energy Research Warehouse (ERW) site, session 1174 (chain 078): lib/ercotNotices.ts, ERCOT's grid notices tied into
// the Grid tool as CAISO's alerts are (the state line grid_ercotnotice_ercot, the notice days on ERCOT's scarcity strip
// and on its monthly mix), on a committed fixture of real rows (scripts/fixtures/ercot_notices.json: every row of
// ercot_grid_notices, read once with the anon key on 24 October 2026). Every key the pages write is recomputed here as
// scripts/check-values.mjs recomputes it (ercotnValue on the rows as its read returns them), to the page's own value;
// and each is checked to be named by the method note, by check-methods' own rules. Needs no build, no network and no
// node_modules.
//
//   node scripts/test-ercot-notices.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as E from "../lib/ercotNotices.ts";
import * as S from "../lib/scarcityStrip.ts";
import { figures, named, noteWords } from "./check-methods.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const fx = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "ercot_notices.json"), "utf-8"));
const rows = fx.rows;
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
// check-values reads event_date as PostgREST writes it (a timestamp) and the three fields of extra by name
const asRead = rows.map((r) => ({ event_date: `${r.event_date}T00:00:00+00:00`, event_type: r.event_type,
  extra: { x_counts: r.extra.x_counts ?? "", x_region: r.extra.x_region ?? "", retrieved_at: r.extra.retrieved_at ?? "" } }));
const recompute = (check) => E.ercotnValue(asRead, check);
const figsOf = (s) => [s.newest, s.read, s.lastCall?.fig, ...s.kinds.map((k) => k.last?.fig), s.lastOther?.fig, s.callDays, s.otherDays].filter(Boolean);

// 24 October 2026, 01:15 UTC: 20:15 on 23 October in Texas, when this session ran
const NOW = Date.parse("2026-10-24T01:15:00Z");
const s = E.noticeState(rows, NOW);

test("the fixture is the real table's rows: 178 notices, 2011-02-02 to 2026-10-15, read from ERCOT on 2026-10-19", () => {
  assert.equal(fx.table, E.NOTICE_TABLE);
  assert.equal(rows.length, 178);
  assert.equal(rows[0].event_date, "2011-02-02");
  assert.equal(rows.at(-1).event_date, "2026-10-15");
  assert.equal(rows.filter((r) => r.extra.x_counts === "yes").length, 120);
  assert.equal(new Set(rows.filter((r) => r.extra.x_counts === "yes").map((r) => r.event_date)).size, 100);   // the method note: 120 count, on 100 days
  for (const r of rows) assert.ok(!("x_text" in r.extra));   // ERCOT's words are not copied into the fixture
});

test("the groups: a call is a counted row; each kind a set of counted types; other the rows that do not count", () => {
  const row = (t, c, g = "ERCOT") => ({ event_date: "2026-01-01", event_type: t, extra: { x_counts: c, x_region: g } });
  assert.ok(E.inGroup(row("eea2", "yes"), "eea"));
  assert.ok(E.inGroup(row("rotating_outages", "yes"), "eea"));
  assert.ok(!E.inGroup(row("rotating_outages", "no", "Rio Grande Valley"), "eea"));   // the Valley's outages are not a system-wide call
  assert.ok(E.inGroup(row("rotating_outages", "no", "Rio Grande Valley"), "other"));
  assert.ok(E.inGroup(row("voluntary_conservation", "yes"), "conservation"));
  assert.ok(E.inGroup(row("power_watch", "yes"), "watch"));
  assert.ok(!E.inGroup(row("watch", "no"), "watch"));   // the control room's Watch on its own tools
  assert.ok(E.inGroup(row("update", "yes"), "call"));
  assert.ok(!E.inGroup(row("update", "yes"), "eea"));
  assert.ok(E.inGroup(row("advisory", "no"), "any"));
  assert.ok(!E.inGroup(row("eea1", "yes"), "nothing"));
  assert.deepEqual(E.GROUPS, ["any", "call", "eea", "conservation", "watch", "ocn", "other"]);
});

test("today is the Central day: 23 October 2026 at 01:15 UTC on the 24th; 15 January at 06:00 UTC", () => {
  assert.equal(s.today, "2026-10-23");
  assert.equal(E.centralDay(Date.parse("2026-10-24T05:00:00Z")), "2026-10-24");
  assert.equal(E.centralDay(Date.parse("2026-01-15T05:59:00Z")), "2026-01-14");
  assert.equal(E.centralDay(Date.parse("2026-01-15T06:00:00Z")), "2026-01-15");
});

test("the state on 23 October 2026: not held (the table ends 2026-10-15, read 2026-10-19); the last call the OCN of 2026-08-25", () => {
  assert.equal(s.covered, false);
  assert.deepEqual(s.todayCalls, []);
  assert.equal(s.newest.raw, "2026-10-15");
  assert.equal(s.newest.check, "ercotn|last|any|2026-10-23");
  assert.equal(s.read.raw, "2026-10-19");
  assert.equal(s.read.check, "ercotn|read");
  assert.equal(s.lastCall.day, "2026-08-25");
  assert.deepEqual(s.lastCall.types, ["ocn_weather"]);
  assert.equal(s.lastCall.fig.check, "ercotn|last|call|2026-10-23");
  assert.equal(s.callDays.raw, 10);   // 24 to 27 January (Weather Watch) and 20 to 25 August (OCN)
  assert.equal(s.callDays.check, "ercotn|ndays|call|2026-01-01|2026-10-23");
});

test("the last day of each kind: EEA 2023-09-06, conservation 2024-01-16, Weather Watch 2026-01-27, OCN 2026-08-25", () => {
  const by = Object.fromEntries(s.kinds.map((k) => [k.kind, k.last]));
  assert.deepEqual(s.kinds.map((k) => k.kind), ["eea", "conservation", "watch", "ocn"]);
  assert.equal(by.eea.day, "2023-09-06");
  assert.deepEqual(by.eea.types, ["eea2"]);
  assert.equal(by.conservation.day, "2024-01-16");
  assert.equal(by.watch.day, "2026-01-27");
  assert.deepEqual(by.watch.types, ["weather_watch"]);
  assert.equal(by.ocn.day, "2026-08-25");
  for (const k of s.kinds) assert.equal(k.last.fig.check, `ercotn|last|${k.kind}|2026-10-23`);
});

test("not calls, named apart: the Advisory of 2026-10-15 (and its cancellation), on 19 days of 2026", () => {
  assert.equal(s.lastOther.day, "2026-10-15");
  assert.deepEqual(s.lastOther.types, ["advisory", "update"]);
  assert.equal(s.otherDays.raw, 19);
  assert.equal(s.otherDays.check, "ercotn|ndays|other|2026-01-01|2026-10-23");
});

test("a day the table covers: in force on 2023-09-06 (the EEA 2 day) and 2021-02-15 (rotating outages); none on 2026-10-15", () => {
  const on = E.noticeState(rows, Date.parse("2023-09-06T20:00:00Z"));
  assert.equal(on.covered, true);
  assert.deepEqual(on.todayCalls, ["eea2", "conservation_appeal", "weather_watch", "update"]);   // the gravest first
  const uri = E.noticeState(rows, Date.parse("2021-02-15T20:00:00Z"));
  assert.equal(uri.todayCalls[0], "rotating_outages");
  const off = E.noticeState(rows, Date.parse("2026-10-15T20:00:00Z"));
  assert.equal(off.covered, true);
  assert.deepEqual(off.todayCalls, []);   // an Advisory that day, not a call
});

test("every key of the state line is recomputed as check-values does, to the page's value", () => {
  const figs = figsOf(s);
  assert.equal(figs.length, 10);
  for (const f of figs) assert.equal(recompute(f.check), f.raw, f.check);
  assert.equal(new Set(figs.map((f) => f.check)).size, figs.length);
  for (const f of figs) assert.match(f.tip, /^ercot_grid_notices /);
});

test("the scarcity strip's window (1 to 30 September 2026, CST): no call day; Advisories on 15, 28 and 29 September, not marked", () => {
  const w = S.windowOf("2026-10-01T05:00:00Z", S.SCARCITY_GRIDS.ercot.behind);
  assert.equal(w.days[0], "2026-09-01");
  assert.equal(w.days.at(-1), "2026-09-30");
  const c = E.callDays(rows, w.days);
  assert.deepEqual(c.cols, []);
  assert.deepEqual(c.other, ["2026-09-15", "2026-09-28", "2026-09-29"]);
  assert.equal(c.call.check, "ercotn|ndays|call|2026-09-01|2026-09-30");
  assert.equal(c.call.raw, 0);
  assert.equal(c.otherFig.raw, 3);
  for (const f of [c.call, c.otherFig]) assert.equal(recompute(f.check), f.raw, f.check);
});

test("a window that holds call days marks their columns: 1 to 30 August 2026, the OCN of 20 to 25 August", () => {
  const days = Array.from({ length: 30 }, (_, i) => `2026-08-${String(i + 1).padStart(2, "0")}`);
  const c = E.callDays(rows, days);
  assert.deepEqual(c.cols.map((j) => days[j]), ["2026-08-20", "2026-08-21", "2026-08-22", "2026-08-23", "2026-08-24", "2026-08-25"]);
  assert.equal(c.call.raw, 6);
  assert.equal(recompute(c.call.check), 6);
  assert.deepEqual(c.byDay.get("2026-08-25"), ["ocn_weather"]);
  assert.deepEqual(c.other, ["2026-08-25"]);   // the OCN's cancellation, not a call
});

test("the monthly mix (24 months, 2024-09 to 2026-09): four months marked, 22 call days", () => {
  const months = [];
  for (let y = 2024, m = 9; y < 2026 || m <= 9; m === 12 ? (y += 1, m = 1) : (m += 1)) if (!(y === 2025 && m === 12)) months.push(`${y}-${String(m).padStart(2, "0")}-01`);
  assert.equal(months.length, 24);
  const cm = E.callMonths(rows, months);
  assert.equal(cm.from, "2024-09-01");
  assert.equal(cm.to, "2026-09-30");
  assert.deepEqual(cm.months.map((x) => x.month), ["2025-01-01", "2025-02-01", "2026-01-01", "2026-08-01"]);
  assert.equal(cm.months[0].days.length, 9);   // the Weather Watches of 6 to 10 and 20 to 23 January 2025
  assert.equal(cm.call.raw, 22);
  assert.equal(cm.call.check, "ercotn|ndays|call|2024-09-01|2026-09-30");
  assert.equal(recompute(cm.call.check), 22);
});

test("a key ercotnValue does not know is undefined; a group with nothing before a day is null", () => {
  assert.equal(E.ercotnValue(asRead, "ercotn|last|nothing|2026-10-23"), undefined);
  assert.equal(E.ercotnValue(asRead, "ercotn|rows|any"), undefined);
  assert.equal(E.ercotnValue(asRead, "awe|last|signal|2026-10-23"), undefined);
  assert.equal(E.ercotnValue(asRead, "ercotn|last|eea|2011-01-31"), null);
  assert.equal(E.ercotnValue([], "ercotn|read"), null);
});

test("check-values recomputes the keys with this file, on every row of the table", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('if (p[0] === "ercotn") {'));
  assert.ok(cv.includes('await import("../lib/ercotNotices.ts")'));
  assert.ok(cv.includes("E.ercotnValue("));
  assert.ok(cv.includes("x_counts:extra->>x_counts,x_region:extra->>x_region,retrieved_at:extra->>retrieved_at"));
  const read = fs.readFileSync(path.join(here, "..", "lib", "gridErcotNotices.ts"), "utf-8");
  assert.ok(read.includes("x_counts:extra->>x_counts,x_region:extra->>x_region,retrieved_at:extra->>retrieved_at"));   // the page asks for the same fields
});

test("the method note names every key of the three panels, by check-methods' rules", () => {
  const note = noteWords(fs.readFileSync(path.join(here, "..", "..", "docs", "methods", "ercot_grid_notices.md"), "utf-8"));
  const w = S.windowOf("2026-10-01T05:00:00Z", S.SCARCITY_GRIDS.ercot.behind);
  const keys = [...figsOf(s).map((f) => f.check), E.callDays(rows, w.days).call.check, E.callDays(rows, w.days).otherFig.check,
    E.callMonths(rows, ["2024-09-01", "2026-09-01"]).call.check];
  for (const k of keys) for (const f of figures(k)) assert.ok(named(note, f), `${k}: ${f.id}`);
});

console.log(`${n} of ${n} passed`);
