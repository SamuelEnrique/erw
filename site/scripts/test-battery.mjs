// Energy Research Warehouse (ERW) site, session 38: the battery game's optimum against brute force.
//
//   node scripts/test-battery.mjs        (Node 23.6 or later runs lib/battery.ts as it is; tests/test_session38.py runs this)
//
// On 12-interval toy days, every one of the 3^12 action sequences is simulated with the game's own rules, and the best
// score must equal the dynamic programme's optimum, whose actions must reproduce it. Prints one line per day; exits 1
// on any mismatch.
import {
  DEFAULT_PRESET, DEFAULT_SETTINGS, eventPageFor, explain, FLEET_MW, FLEET_MWH, isPerfect, optimum, perfectShare, presetLabel, presetOf, rulesOf, SETTINGS, simulate,
  validSettings, vppHour,
} from "../lib/battery.ts";
import fs from "node:fs";

const days = {
  // a morning trough and an evening peak
  shape: [30, 25, 20, 18, 22, 35, 60, 90, 120, 80, 40, 28],
  // negative prices: paid to charge
  negative: [-20, -30, -15, -5, 5, 10, 25, 40, 55, 30, 12, 8],
  // a flat day: nothing to gain but the starting charge
  flat: [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40],
  // a spike in the middle hour, after the VPP hour's run-up
  spike: [15, 12, 10, 14, 300, 900, 450, 200, 30, 25, 20, 18],
};

let bad = 0;
for (const [name, prices] of Object.entries(days)) {
  let best = -Infinity;
  const seq = new Array(12).fill(0);
  const acts = [1, 0, -1];
  for (let code = 0; code < 3 ** 12; code++) {
    let c = code;
    for (let i = 0; i < 12; i++) { seq[i] = acts[c % 3]; c = Math.floor(c / 3); }
    const s = simulate(prices, seq).score;
    if (s > best) best = s;
  }
  const dp = optimum(prices);
  const replay = simulate(prices, dp.actions).score;
  const ok = Math.abs(dp.score - best) < 1e-9 && Math.abs(replay - dp.score) < 1e-9;
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} ${name}: brute force ${best.toFixed(6)}, DP ${dp.score.toFixed(6)}, DP actions replayed ${replay.toFixed(6)}, VPP hour from interval ${vppHour(prices).first}`);
}
// session 46: game v1.1. The flag at 100 percent of perfect as shown (99.5 rounds to 100), the fleet constants, and
// the famous days that fall inside an /events window
const v11 = [
  ["isPerfect(10, 10)", isPerfect(10, 10), true],
  ["isPerfect(9.96, 10): 99.6 percent shows as 100", isPerfect(9.96, 10), true],
  ["isPerfect(9.94, 10): 99.4 percent shows as 99", isPerfect(9.94, 10), false],
  ["isPerfect(5, 0): perfect foresight earns nothing, no flag", isPerfect(5, 0), false],
  ["perfectShare(3, 4) = 75", perfectShare(3, 4), 75],
  ["FLEET_MW = 10,000 x 5 kW = 50", FLEET_MW, 50],
  ["FLEET_MWH = 10,000 x 13.5 kWh = 135", FLEET_MWH, 135],
  ["Uri, 2021-02-15: /events/uri-2021", eventPageFor("2021-02-15")?.href, "/events/uri-2021"],
  ["2023-08-10: /events/ercot-heat-2023", eventPageFor("2023-08-10")?.href, "/events/ercot-heat-2023"],
  ["2023-09-11, a day after the window: none", eventPageFor("2023-09-11"), null],
  ["2026-04-26, the calm day: none", eventPageFor("2026-04-26"), null],
];
for (const [name, got, want] of v11) {
  const ok = got === want;
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} ${name} (got ${JSON.stringify(got)})`);
}
// every famous level links where its date is inside a window, and the windows match warehouse/derived/event_window.py
const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels;
console.log(`  famous days linked: ${levels.map((l) => `${l.slug} ${eventPageFor(l.date)?.href ?? "none"}`).join("; ")}`);
const py = fs.readFileSync(new URL("../../warehouse/derived/event_window.py", import.meta.url), "utf-8");
for (const [ev, start, end] of [["uri_2021", "2021-02-07", "2021-02-24"], ["covid_2020", "2020-03-01", "2020-05-31"], ["elliott_2022", "2022-12-19", "2022-12-29"], ["ercot_heat_2023", "2023-08-01", "2023-09-10"]]) {
  const at = py.indexOf(`event="${ev}"`);
  const ok = at >= 0 && py.slice(at, at + 300).includes(`start="${start}", end="${end}"`);
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} ${ev}'s window in event_window.py is ${start} to ${end}`);
}
// session 50: game v2. The DP against brute force under the rules each difficulty enforces (Hard: the reserve and the
// degradation cost), for the default battery and a small one where the reserve binds early; replaying the DP's actions
// scores the same; the reserve is never crossed; the presets and the settings check; the replay's reasons
const presets = [
  ["hard, default battery", DEFAULT_SETTINGS, "hard"],
  ["hard, 5 kWh, 2.5 kW, 85 percent, reserve 30, wear 0.20", { kwh: 5, kw: 2.5, rte: 0.85, reserve: 0.3, deg: 0.2 }, "hard"],
  ["easy, 20 kWh, 10 kW, 92 percent", { kwh: 20, kw: 10, rte: 0.92, reserve: 0.2, deg: 0.11 }, "easy"],
  ["normal, default battery", DEFAULT_SETTINGS, "normal"],
];
for (const [label, s, d] of presets) {
  const r = rulesOf(s, d);
  for (const [name, prices] of Object.entries(days)) {
    let best = -Infinity;
    const seq = new Array(12).fill(0);
    const acts = [1, 0, -1];
    let lowest = Infinity;
    for (let code = 0; code < 3 ** 12; code++) {
      let c = code;
      for (let i = 0; i < 12; i++) { seq[i] = acts[c % 3]; c = Math.floor(c / 3); }
      const x = simulate(prices, seq, r);
      if (x.score > best) best = x.score;
      if (code % 997 === 0) lowest = Math.min(lowest, ...x.soc);
    }
    const dp = optimum(prices, r);
    const replay = simulate(prices, dp.actions, r);
    const ok = Math.abs(dp.score - best) < 1e-9 && Math.abs(replay.score - dp.score) < 1e-9 && lowest >= r.reserveKwh - 1e-9 && Math.min(...replay.soc) >= r.reserveKwh - 1e-9;
    if (!ok) bad++;
    console.log(`${ok ? "ok  " : "FAIL"} ${label}, ${name}: brute force ${best.toFixed(6)}, DP ${dp.score.toFixed(6)}, replayed ${replay.score.toFixed(6)} (wear ${replay.wear.toFixed(4)}), lowest charge ${Math.min(lowest, ...replay.soc).toFixed(3)} of reserve ${r.reserveKwh.toFixed(3)} kWh`);
  }
}
// on Normal with the default battery, v2's rules are v1's: the same score for the same actions
{
  const a = optimum(days.shape).actions;
  const ok = Math.abs(simulate(days.shape, a).score - simulate(days.shape, a, rulesOf(DEFAULT_SETTINGS, "normal")).score) < 1e-12 && presetOf(DEFAULT_SETTINGS, "normal") === DEFAULT_PRESET && DEFAULT_PRESET === "normal:13.5-5-90";
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} Normal with the default battery scores as v1; its preset is ${DEFAULT_PRESET}`);
}
const v2 = [
  ["validSettings(defaults)", validSettings(DEFAULT_SETTINGS), true],
  ["validSettings: kwh 31 is out of range", validSettings({ ...DEFAULT_SETTINGS, kwh: 31 }), false],
  ["validSettings: kw 5.25 is off its 0.5 step", validSettings({ ...DEFAULT_SETTINGS, kw: 5.25 }), false],
  ["validSettings: an extra key", validSettings({ ...DEFAULT_SETTINGS, x: 1 }), false],
  ["validSettings: a string", validSettings({ ...DEFAULT_SETTINGS, deg: "0.11" }), false],
  ["presetOf(hard)", presetOf(DEFAULT_SETTINGS, "hard"), "hard:13.5-5-90-r20-d0.11"],
  ["presetLabel(default normal)", presetLabel("normal:13.5-5-90"), "Normal, the default battery"],
  ["presetLabel(custom hard)", presetLabel("hard:5-2.5-85-r30-d0.2"), "Hard, 5 kWh, 2.5 kW, 85 percent round trip, reserve 30 percent, wear $0.2 per kWh"],
  ["the degradation default: 721 x 25 / 158,000 rounds to 0.11", Math.round((721 * 25) / 158000 * 100) / 100, SETTINGS.deg.def],
];
for (const [name, got, want] of v2) {
  const ok = got === want;
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} ${name} (got ${JSON.stringify(got)})`);
}
// the reasons: a toy day whose hours run 0 to 11 (night then morning), on Hard with the default battery
{
  const hours = days.shape.map((_, i) => i);
  const r = rulesOf(DEFAULT_SETTINGS, "hard");
  const segs = explain(days.shape, hours, optimum(days.shape, r).actions, r, (i) => `${String(i).padStart(2, "0")}:00`);
  console.log(`  reasons, shape day on Hard: ${segs.map((s) => `[${s.from}-${s.to}] ${s.text}`).join(" | ")}`);
  const covers = segs[0].from === 0 && segs.at(-1).to === 11 && segs.every((s, i) => i === 0 || s.from === segs[i - 1].to + 1);
  const read = segs.every((s) => /^(charged|sold|held): /.test(s.text));
  const ok = covers && read && segs.some((s) => s.text.startsWith("sold"));
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} the reasons cover the day without a gap, one line per run`);
  const held = explain([10, 10, 10, 10], [0, 0, 0, 0], [-1, -1, -1, 0], rulesOf({ ...DEFAULT_SETTINGS, kwh: 5, kw: 5 }, "hard"));
  const ok2 = held.at(-1).text === "held: reserve";
  if (!ok2) bad++;
  console.log(`${ok2 ? "ok  " : "FAIL"} a battery drained to its reserve reads "held: reserve" (got ${JSON.stringify(held.at(-1).text)})`);
}
// the DP on the real famous days under each difficulty: its time, so the page can compute it in the browser
for (const l of levels) {
  for (const d of ["normal", "hard"]) {
    const t0 = performance.now();
    const o = optimum(l.price, rulesOf(DEFAULT_SETTINGS, d));
    const ms = performance.now() - t0;
    const ok = ms < 2000 && Number.isFinite(o.score) && o.actions.length === l.price.length;
    if (!ok) bad++;
    console.log(`${ok ? "ok  " : "FAIL"} ${l.date} on ${d}: the optimum ${o.score.toFixed(4)} USD in ${ms.toFixed(0)} ms`);
  }
}
console.log(bad ? `${bad} FAILED` : "every toy day: the DP optimum equals brute force");
process.exit(bad ? 1 : 0);
