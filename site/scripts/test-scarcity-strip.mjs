// Energy Research Warehouse (ERW) site, session 1154 (chain 077): lib/scarcityStrip.ts, the Grid tool's scarcity hours
// (grid_scarcity_<grid>), on a committed fixture of real rows (scripts/fixtures/scarcity_strip.json: scarcity_hours_by_grid,
// iso_rtm_hub_prices and ercot_hub_prices_daily, a few days each, read once with the anon key on 23 October 2026). Every
// key the panel writes is recomputed here as scripts/check-values.mjs recomputes it (series_sum, the new series_n,
// series_max) from the fixture's rows, to the panel's own value. Needs no build, no network and no node_modules.
//
//   node scripts/test-scarcity-strip.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as S from "../lib/scarcityStrip.ts";
import * as A from "../lib/datacenter/answers.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fx = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "scarcity_strip.json"), "utf-8"));
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const E = S.SCARCITY_GRIDS.ercot, C = S.SCARCITY_GRIDS.caiso;

/** A key recomputed from rows, as check-values reads it: rows of the key's table, variable and entity in [start, end). */
function recompute(check, tables) {
  const p = check.split("|");
  const [kind, table, variable, start, end, entity] = p;
  const rows = (tables[`${table}|${entity}`] ?? []).filter((r) => (r.variable === undefined || r.variable === variable)
    && Date.parse(r.ts_utc) >= Date.parse(start) && Date.parse(r.ts_utc) < Date.parse(end));
  if (kind === "series_n") return S.heldHours(rows);
  if (!rows.length) return undefined;
  if (kind === "series_sum") return rows.reduce((a, r) => a + r.value, 0);
  if (kind === "series_max") return Math.max(...rows.map((r) => r.value));
  throw new Error(`unknown kind ${kind}`);
}
const figs = (s) => [s.rt?.hours, s.rt?.held, s.rt?.intervals, s.da?.hours, s.da?.held, s.own?.hours, s.own?.held, s.rtMax, s.dayMax].filter(Boolean);

test("the level, the table and the hubs are lib/datacenter/answers.ts's", () => {
  assert.equal(S.SCARCITY_TABLE, A.SBG_TABLE);
  assert.equal(S.SCARCITY_LEVEL, A.SBG_LEVEL);
  assert.equal(E.hub, A.SBG_HUBS.ercot);
  assert.equal(C.hub, A.SBG_HUBS.caiso);
});

test("the window: the 30 standard-time days that end with the newest hour's day (1 to 30 September 2026)", () => {
  assert.equal(fx.ercot.newest.slice(0, 19), "2026-10-01T05:00:00");
  const we = S.windowOf(fx.ercot.newest, E.behind), wc = S.windowOf(fx.caiso.newest, C.behind);
  assert.equal(we.start, "2026-09-01T06:00:00Z");
  assert.equal(we.end, "2026-10-01T06:00:00Z");
  assert.equal(wc.start, "2026-09-01T08:00:00Z");
  assert.equal(wc.end, "2026-10-01T08:00:00Z");
  assert.equal(we.days.length, 30);
  assert.equal(we.days[0], "2026-09-01");
  assert.equal(we.days[29], "2026-09-30");
});

const ercot = S.scarcityStrip(E, { rows: fx.ercot.rows, prices: fx.ercot.prices, daily: fx.ercot.daily, newest: fx.ercot.newest });
const caiso = S.scarcityStrip(C, { rows: fx.caiso.rows, prices: fx.caiso.prices, daily: [], newest: fx.caiso.newest });

test("ERCOT: a cell for each held hour, none before the fixture's days (not held is null, not a zero)", () => {
  assert.equal(ercot.rows.length, 24);
  assert.equal(ercot.cols.length, 30);
  const held = ercot.cells.flat().filter((v) => v !== null).length;
  assert.equal(held, 72);                                        // 28 to 30 September, 24 hours each
  for (let j = 0; j < 27; j++) for (let h = 0; h < 24; h++) assert.equal(ercot.cells[h][j], null);
  assert.equal(ercot.high, 0);                                   // no hour of those days reached USD 1,000
  assert.equal(ercot.marks.length, 0);
  assert.equal(ercot.own, null);                                 // the adder is held to 4 December 2025 only
});

test("ERCOT: the hover names the hour in CST and UTC, the variables at 1, the intervals, the hour's highest price and the level's source", () => {
  const h = 17, j = 29;                                           // 30 September, 17:00 CST, 23:00 UTC
  const t = ercot.tips[h][j];
  assert.ok(t.startsWith("2026-09-30 17:00 CST (2026-09-30 23:00 UTC)."), t);
  assert.ok(t.includes("Variables at 1: none."), t);
  assert.ok(t.includes("Real-time intervals at or above USD 1,000 per MWh: 0 of 4."), t);
  assert.ok(t.includes("own_signal: not held (ERCOT published its reserve adder to 4 December 2025"), t);
  const ms = Date.parse("2026-09-30T23:00:00Z");
  const want = Math.max(...fx.ercot.prices.filter((p) => Date.parse(p.ts_utc) >= ms && Date.parse(p.ts_utc) < ms + 3_600_000).map((p) => p.value));
  assert.ok(t.includes(`Highest 15-minute real-time price at HB_HUBAVG: USD ${want.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} per MWh (4 of 4 intervals held, iso_rtm_hub_prices).`), t);
  assert.ok(t.endsWith("Level: USD 1,000 per MWh, docs/methods/scarcity_hours_by_grid.md; prices: ERCOT."), t);
  assert.ok(ercot.tips[0][0].includes("Not held in scarcity_hours_by_grid"), ercot.tips[0][0]);
});

test("ERCOT: an hour without its 15-minute prices gives its local day's highest, said as the day's", () => {
  const prices = fx.ercot.prices.filter((p) => Date.parse(p.ts_utc) >= Date.parse("2026-09-29T00:00:00Z"));
  const s = S.scarcityStrip(E, { rows: fx.ercot.rows, prices, daily: fx.ercot.daily, newest: fx.ercot.newest });
  const t = s.tips[0][27];                                        // 28 September, 00:00 CST: 06:00 UTC, 01:00 CDT
  const day = fx.ercot.daily.find((d) => d.ts_utc.startsWith("2026-09-28")).value;
  assert.ok(t.includes(`the highest real-time price of ERCOT's local day 2026-09-28 at HB_HUBAVG: USD ${day.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} per MWh (ercot_hub_prices_daily).`), t);
  const none = S.scarcityStrip(E, { rows: fx.ercot.rows, prices: [], daily: [], newest: fx.ercot.newest });
  assert.ok(none.tips[0][27].includes("No price of this hour is in the live set"), none.tips[0][27]);
  assert.equal(none.rtMax, null);
  assert.equal(none.dayMax, null);
});

const tables = {
  [`scarcity_hours_by_grid|iso:ercot`]: fx.ercot.rows, [`scarcity_hours_by_grid|iso:caiso`]: fx.caiso.rows,
  [`iso_rtm_hub_prices|ercot:HB_HUBAVG`]: fx.ercot.prices, [`iso_rtm_hub_prices|caiso:TH_SP15_GEN-APND`]: fx.caiso.prices,
  [`ercot_hub_prices_daily|ercot:HB_HUBAVG`]: fx.ercot.daily,
};

test("every key of both grids recomputes to the panel's value, as check-values reads it", () => {
  let keys = 0;
  for (const s of [ercot, caiso]) {
    for (const f of figs(s)) {
      assert.equal(recompute(f.check, tables), f.raw, f.check);
      assert.ok(f.tip.length > 20, f.check);
      keys += 1;
    }
  }
  assert.equal(keys, 7 + 8);                                      // ERCOT: rt 3, da 2, two prices; CAISO: rt 3, da 2, own 2, one price
  assert.equal(ercot.rt.held.raw, 72);
  assert.equal(caiso.own.held.raw, 48);
  assert.equal(caiso.dayMax, null);
  assert.ok(ercot.rt.hours.check === "series_sum|scarcity_hours_by_grid|rt_hour_ge_1000|2026-09-01T06:00:00Z|2026-10-01T06:00:00Z|iso:ercot", ercot.rt.hours.check);
  assert.ok(ercot.dayMax.check === "series_max|ercot_hub_prices_daily|rt_max|2026-09-01T00:00:00Z|2026-10-01T00:00:00Z|ercot:HB_HUBAVG", ercot.dayMax.check);
});

test("heldHours counts an hour written twice once (the series_n recomputation)", () => {
  const r = fx.caiso.rows.filter((x) => x.variable === "own_signal");
  assert.equal(S.heldHours(r), 48);
  assert.equal(S.heldHours([...r, ...r]), 48);
  assert.equal(S.heldHours([]), 0);
});

test("CAISO, 26 and 27 August 2026: the hour at or above USD 1,000 is filled, its tip names rt_hour_ge_1000", () => {
  const s = S.scarcityStrip(C, { rows: fx.caiso_aug.rows, prices: [], daily: [], newest: "2026-08-28T07:00:00Z" });
  assert.equal(s.window.days[29], "2026-08-27");
  assert.equal(s.high, 1);
  assert.equal(s.rt.hours.raw, 1);
  assert.equal(s.rt.intervals.raw, 6);                            // 2 intervals at 20:00 PST and 4 at 21:00 PST, 26 August
  const h = 21, j = 28;                                           // 26 August, 21:00 PST, 27 August 05:00 UTC
  assert.equal(s.cells[h][j], 1);
  assert.equal(s.cells[20][j], 0);                                // two intervals at or above, the hour's mean below
  assert.ok(s.tips[h][j].includes("Variables at 1: rt_hour_ge_1000."), s.tips[h][j]);
  assert.ok(s.tips[h][j].includes("4 of 4."), s.tips[h][j]);
  assert.ok(s.tips[h][j].includes("No price of this hour is in the live set"), s.tips[h][j]);
});

test("CAISO, the EEA Watch of 24 July 2024: seven hours of own_signal, marked on blank cells (no price held then)", () => {
  const s = S.scarcityStrip(C, { rows: fx.caiso_eea.rows, prices: [], daily: [], newest: "2024-07-26T07:00:00Z" });
  assert.equal(s.marks.length, 7);
  assert.equal(s.signal, 7);
  assert.equal(s.own.hours.raw, 7);
  assert.equal(s.rt, null);                                       // CAISO's prices are held from 1 September 2024
  for (const [h, j] of s.marks) assert.equal(s.cells[h][j], null);   // no price row: the cell is not held, the mark stands
  assert.deepEqual(s.marks.map(([h]) => h).sort((a, b) => a - b), [16, 17, 18, 19, 20, 21, 22]);   // 17:25 to 23:59 PDT, 16:00 to 22:00 PST
});

test("no em dash in this session's files", () => {
  for (const f of ["../lib/scarcityStrip.ts", "../components/grid/ScarcityPanel.tsx", "test-scarcity-strip.mjs"]) {
    assert.ok(!fs.readFileSync(path.join(here, f), "utf-8").includes(String.fromCharCode(0x2014)), f);
  }
});

console.log(`${n} of ${n} passed`);
