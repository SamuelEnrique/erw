// Energy Research Warehouse (ERW) site, session 132: the price board's pure functions (lib/board.ts), on the site's own
// files: the board (data/board.json) and real series the workbench reads (public/board/s, public/board/h).
//
//   node --import ./scripts/alias-loader.mjs scripts/test-board.mjs
//
// Exit 1 on a failure. Where a test removes a real value it says so; nothing is written.
import assert from "node:assert/strict";
import fs from "node:fs";
import * as b from "../lib/board.ts";

const read = (p) => JSON.parse(fs.readFileSync(new URL(`../${p}`, import.meta.url), "utf-8"));
const file = read("data/board.json");
const hh = read("public/board/s/eia-henry-hub-spot.json");
const wti = read("public/board/s/eia-wti-cushing-spot.json");
const brent = read("public/board/s/eia-brent-spot.json");
const gap = read("public/board/s/erw-brent-minus-wti.json");
const hub = read("public/board/h/ercot-hb-hubavg.json");
let n = 0;
const test = (name, fn) => { fn(); n += 1; console.log(`ok   ${name}`); };

test("a series file opens as points, the last one the board's latest value", () => {
  const p = b.pointsOf(hh), row = file.rows.find((r) => r.id === "eia-henry-hub-spot");
  assert.equal(p.length, hh.v.length);
  assert.equal(b.isoDay(p[p.length - 1].t), row.last.t);
  assert.equal(p[p.length - 1].v, row.last.v);
  assert.deepEqual(b.sparkOf(row).at(-1), { t: row.last.t, v: row.last.v });
});
test("a window counts back from the newest point, and dates given are inclusive", () => {
  const p = b.pointsOf(hh), last = p[p.length - 1].t;
  const week = b.windowed(p, "1w");
  assert.ok(week.length >= 3 && week.length <= 7 && week.every((x) => x.t > last - 7 * b.DAY));
  assert.equal(b.windowed(p, "all").length, p.length);
  const jan = b.windowed(p, "1y", "2024-01-01", "2024-01-31");
  assert.ok(jan.length > 15 && jan.every((x) => b.isoDay(x.t).startsWith("2024-01")));
});
test("the spread of two series is their difference on the days both hold: Brent less WTI is the board's own row", () => {
  const j = b.joined(b.pointsOf(brent), b.pointsOf(wti)), g = b.pointsOf(gap);
  assert.equal(j.length, g.length);
  const last = j[j.length - 1];
  assert.ok(Math.abs(last.spread - g[g.length - 1].v) < 1e-6);
  assert.ok(Math.abs(last.ratio - last.a / last.b) < 1e-12);
  const fewer = b.joined(b.pointsOf(brent), b.pointsOf(wti).slice(0, -5));          // WTI's last five days removed: no value stands in for them
  assert.equal(fewer.length, j.length - 5);
});
test("an hourly file keeps its gaps and its peak hours", () => {
  const da = b.hourlyOf(hub, "da"), rt = b.hourlyOf(hub, "rt");
  assert.equal(da.length, hub.da.filter((v) => v !== null).length);
  assert.ok(rt.length > 60000 && rt.length <= hub.n);
  const week = b.windowed(rt, "1w");
  const d = b.distribution(week, 100, hub);
  assert.equal(d.n, week.length);
  assert.equal(d.peakN + d.offN, week.length);
  assert.equal(d.top.length, 10);
  assert.ok(d.top[0].v >= d.top[9].v && d.top[0].v === Math.max(...week.map((x) => x.v)));
  assert.equal(d.above, week.filter((x) => x.v > 100).length);
  assert.equal(d.negative, week.filter((x) => x.v < 0).length);
  const peak = week.filter((x) => b.isPeak(hub, x.t));
  assert.ok(Math.abs(d.peakMean - peak.reduce((a, x) => a + x.v, 0) / peak.length) < 1e-9);
});
test("this year against prior years: one line a year, and a band of the five years before the newest", () => {
  const s = b.seasonal(b.pointsOf(hh), "D");
  const newest = s.years.at(-1);
  assert.deepEqual(s.bandYears, [newest - 5, newest - 4, newest - 3, newest - 2, newest - 1]);
  const slot = b.slotOf(Date.UTC(newest - 1, 5, 15), "D");
  const vals = s.bandYears.map((y) => s.lines[y][slot]).filter((v) => v !== null);
  assert.equal(s.lo[slot], Math.min(...vals));
  assert.equal(s.hi[slot], Math.max(...vals));
  assert.equal(b.slotOf(Date.UTC(2024, 2, 1), "D"), b.slotOf(Date.UTC(2023, 2, 1), "D"));      // 1 March lines up in a leap year
  assert.equal(b.slotLabel(0, "M"), "Jan");
  assert.equal(s.lines[newest].filter((v) => v !== null).length, b.pointsOf(hh).filter((x) => new Date(x.t).getUTCFullYear() === newest).length);
});
test("volatility is the standard deviation of the last 30 changes, and needs 31 points", () => {
  const p = b.pointsOf(hh);
  assert.equal(b.volatility(p.slice(-30), 30), null);
  const tail = p.slice(-31), ch = tail.slice(1).map((x, i) => x.v - tail[i].v), m = ch.reduce((a, x) => a + x, 0) / 30;
  assert.ok(Math.abs(b.volatility(p, 30) - Math.sqrt(ch.reduce((a, x) => a + (x - m) ** 2, 0) / 29)) < 1e-12);
});
test("the filters of a group choose its rows; MISO and PJM stay listed", () => {
  const power = file.groups.find((g) => g.id === "power");
  const main = b.rowsOf(file, power, {});
  assert.equal(main.length, 14);                    // five grids in two markets, and MISO's and PJM's main hubs, blank
  assert.ok(main.some((r) => r.status === "paused") && main.some((r) => r.status === "licensed"));
  const all = b.rowsOf(file, power, { scope: "all" });
  assert.ok(all.length > 80);
  const ercot = b.rowsOf(file, power, { scope: "all", grid: "ERCOT", market: "da" });
  assert.equal(ercot.length, 6);
  const spreads = file.groups.find((g) => g.id === "oilspreads");
  assert.ok(b.rowsOf(file, spreads, {}).some((r) => r.id === "erw-brent-minus-wti"));        // the gap is a row of crude and of the oil spreads
});
test("the workbench's state is the address: a power hub opens on seven days by the hour against its other market", () => {
  const q = new URLSearchParams("s=ercot-hb-hubavg-rt");
  const s = b.benchOf(q, file);
  assert.deepEqual([s.s, s.o, s.w, s.r, s.m, s.v], ["ercot-hb-hubavg-rt", "ercot-hb-hubavg-da", "1w", "h", "spread", "price"]);
  assert.equal(b.benchQuery(s, file), "s=ercot-hb-hubavg-rt");
  const t = { ...s, o: "eia-henry-hub-spot", m: "ratio", w: "1y", r: "d", x: true };
  const back = b.benchOf(new URLSearchParams(b.benchQuery(t, file)), file);
  assert.deepEqual(back, t);
  const fuel = b.benchOf(new URLSearchParams("s=eia-henry-hub-spot"), file);
  assert.deepEqual([fuel.o, fuel.w, fuel.r], [null, "1y", "d"]);
  assert.equal(b.benchOf(new URLSearchParams("s=miso-indiana-hub-da"), file).s, null);      // a blank row opens nothing
  assert.equal(b.benchOf(new URLSearchParams("s=no-such-row"), file).s, null);
  assert.equal(b.benchQuery({ ...fuel, s: null }, file, new URLSearchParams("power.grid=ERCOT&s=x")), "power.grid=ERCOT");
});
test("numbers as written, and a CSV of rows", () => {
  assert.equal(b.fmt(3.18, "USD/MMBtu"), "3.18");
  assert.equal(b.fmt(4.4785, "USD/gal"), "4.479");
  assert.equal(b.fmt(148620.0008, "USD/t"), "148,620");
  assert.equal(b.signed(-6.12, "USD/MWh"), "−6.12");
  assert.equal(b.signed(0.28, "USD/MMBtu"), "+0.28");
  assert.equal(b.dateWords("2026-09-29"), "29 Sep 2026");
  assert.equal(b.dateWords("2026-08-01", "M"), "Aug 2026");
  assert.equal(b.csv(["date", "a, b"], [["2026-01-01", 1.5], ["2026-01-02", null]]), 'date,"a, b"\n2026-01-01,1.5\n2026-01-02,\n');
  assert.ok(b.noMove("M", "w") && b.noMove("W", "d") && !b.noMove("W", "w") && !b.noMove("D", "d"));
});
test("the headline: lowest and highest grid on the day every priced main hub holds", () => {
  const ex = b.gridExtremes(file, "da");
  assert.ok(ex && ex.grids === 5 && ex.low.v <= ex.high.v);
  const rx = b.rangeExtremes(file);
  assert.ok(rx.top.range.pos >= rx.bottom.range.pos);
  assert.ok(!["plantfuel", "as", "retailpower"].includes(rx.top.group) && !["plantfuel", "as", "retailpower"].includes(rx.bottom.group));
});
console.log(`${n} tests pass`);
