// Energy Research Warehouse (ERW) site, session 38: the battery game's optimum against brute force.
//
//   node scripts/test-battery.mjs        (Node 23.6 or later runs lib/battery.ts as it is; tests/test_session38.py runs this)
//
// On 12-interval toy days, every one of the 3^12 action sequences is simulated with the game's own rules, and the best
// score must equal the dynamic programme's optimum, whose actions must reproduce it. Prints one line per day; exits 1
// on any mismatch.
import {
  DEFAULT_PRESET, DEFAULT_SETTINGS, EMERGENCY, emergencyOf, eventPageFor, explain, FLEET_MW, FLEET_MWH, isPerfect, optimum, outageDraw, parsePreset, perfectShare,
  presetLabel, presetOf, rulesOf, SETTINGS, simulate, START_MONEY, validSettings, vppHour,
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
    // session 63: on Hard the outage may draw the battery below its reserve (the reserve is for it): the reserve binds
    // before the outage
    const o = emergencyOf(prices, r).outage;
    const upto = (soc) => (o ? soc.slice(0, o.first + 1) : soc);
    let best = -Infinity;
    const seq = new Array(12).fill(0);
    const acts = [1, 0, -1];
    let lowest = Infinity;
    for (let code = 0; code < 3 ** 12; code++) {
      let c = code;
      for (let i = 0; i < 12; i++) { seq[i] = acts[c % 3]; c = Math.floor(c / 3); }
      const x = simulate(prices, seq, r);
      if (x.score > best) best = x.score;
      if (code % 997 === 0) lowest = Math.min(lowest, ...upto(x.soc));
    }
    const dp = optimum(prices, r);
    const replay = simulate(prices, dp.actions, r);
    const ok = Math.abs(dp.score - best) < 1e-9 && Math.abs(replay.score - dp.score) < 1e-9 && lowest >= r.reserveKwh - 1e-9 && Math.min(...upto(replay.soc)) >= r.reserveKwh - 1e-9;
    if (!ok) bad++;
    console.log(`${ok ? "ok  " : "FAIL"} ${label}, ${name}: brute force ${best.toFixed(6)}, DP ${dp.score.toFixed(6)}, replayed ${replay.score.toFixed(6)} (wear ${replay.wear.toFixed(4)}), lowest charge before any outage ${Math.min(lowest, ...upto(replay.soc)).toFixed(3)} of reserve ${r.reserveKwh.toFixed(3)} kWh${o ? `; outage ${o.first} to ${o.last}${replay.why ? `, ${replay.why}` : ""}` : ""}`);
  }
}
// on Normal with the default battery the defaults are the rules: the same score for the same actions; session 63: the
// preset carries the rules' version
{
  const a = optimum(days.shape).actions;
  const ok = Math.abs(simulate(days.shape, a).score - simulate(days.shape, a, rulesOf(DEFAULT_SETTINGS, "normal")).score) < 1e-12 && presetOf(DEFAULT_SETTINGS, "normal") === DEFAULT_PRESET && DEFAULT_PRESET === "normal:13.5-5-90-v3";
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} Normal with the default battery: its preset is ${DEFAULT_PRESET}`);
}
const v2 = [
  ["validSettings(defaults)", validSettings(DEFAULT_SETTINGS), true],
  ["validSettings: kwh 31 is out of range", validSettings({ ...DEFAULT_SETTINGS, kwh: 31 }), false],
  ["validSettings: kw 5.25 is off its 0.5 step", validSettings({ ...DEFAULT_SETTINGS, kw: 5.25 }), false],
  ["validSettings: an extra key", validSettings({ ...DEFAULT_SETTINGS, x: 1 }), false],
  ["validSettings: a string", validSettings({ ...DEFAULT_SETTINGS, deg: "0.11" }), false],
  ["presetOf(hard)", presetOf(DEFAULT_SETTINGS, "hard"), "hard:13.5-5-90-r20-d0.11-v3"],
  ["presetLabel(default normal, v3)", presetLabel("normal:13.5-5-90-v3"), "Normal, the default battery"],
  ["presetLabel(default normal, a v2 board)", presetLabel("normal:13.5-5-90"), "Normal, the default battery (v2 rules)"],
  ["presetLabel(custom hard)", presetLabel("hard:5-2.5-85-r30-d0.2-v3"), "Hard, 5 kWh, 2.5 kW, 85 percent round trip, reserve 30 percent, wear $0.2 per kWh"],
  ["parsePreset(v3) round trip", JSON.stringify(parsePreset("hard:13.5-5-90-r20-d0.11-v3")?.v3), "true"],
  ["parsePreset(a v2 board) is readable", JSON.stringify(parsePreset("normal:13.5-5-90")?.v3), "false"],
  ["parsePreset: v3 twice is refused", parsePreset("normal:13.5-5-90-v3-v3"), null],
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
// session 63: game v3. Money: a play starts with $5 and ends in the interval it falls below $0. On Hard, the emergency
// spikes the day's dearest hour toward the cap and then cuts the grid for up to two hours; the house draws on the battery
// and the lights go out when it cannot. The brute force above already ran every sequence under these rules on Hard.
{
  const dear = new Array(12).fill(2000);
  const all = new Array(12).fill(1);
  const x = simulate(dear, all);
  // each interval buys 1.25 kWh at USD 2/kWh, USD 2.50: $5 is $0 after two intervals and below it in the third
  const ok = START_MONEY === 5 && x.why === "bankrupt" && x.end === 2 && Math.abs(x.money + 2.5) < 1e-9;
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} charging at USD 2,000/MWh runs out of money in interval ${x.end} (money ${x.money.toFixed(2)}, ${x.why})`);
  const o = optimum(dear);
  const ok2 = o.score >= 0 && simulate(dear, o.actions).why !== "bankrupt";
  if (!ok2) bad++;
  console.log(`${ok2 ? "ok  " : "FAIL"} the optimum never goes bankrupt (score ${o.score.toFixed(4)})`);
}
{
  const r = rulesOf({ ...DEFAULT_SETTINGS, kwh: 5, kw: 5, reserve: 0 }, "hard");
  const day = days.spike;  // its dearest hour is intervals 4 to 7, so the outage has room after it
  const em = emergencyOf(day, r);
  const v = vppHour(day);
  const spiked = em.prices.slice(v.first, v.last + 1).map((p, k) => Math.abs(p - (day[v.first + k] + (EMERGENCY.cap - day[v.first + k]) * EMERGENCY.ramp[k])) < 1e-9);
  const okSpike = spiked.every(Boolean) && em.outage.first === v.last + 1 && em.outage.last === 11;
  if (!okSpike) bad++;
  console.log(`${okSpike ? "ok  " : "FAIL"} Hard's spike: the dearest hour (${v.first} to ${v.last}) climbs toward ${EMERGENCY.cap}; the outage runs ${em.outage.first} to ${em.outage.last}`);
  const sellAll = day.map((_, i) => (i >= v.first && i <= v.last ? -1 : 0));
  const x = simulate(day, sellAll, r);
  const ok = x.why === "lights_out" && x.end === em.outage.first && Math.abs(x.outageNeedKwh - (em.outage.last - em.outage.first + 1) * outageDraw(r)) < 1e-12;
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} selling everything into the spike: lights out at interval ${x.end}; the outage needed ${x.outageNeedKwh.toFixed(3)} kWh, the battery held ${x.outageStartKwh?.toFixed(3)}`);
  const ignored = simulate(day, day.map((_, i) => (i > v.last ? 1 : 0)), rulesOf(DEFAULT_SETTINGS, "hard"));
  const ok3 = ignored.cash === simulate(day, day.map(() => 0), rulesOf(DEFAULT_SETTINGS, "hard")).cash;
  if (!ok3) bad++;
  console.log(`${ok3 ? "ok  " : "FAIL"} in the outage the grid is down: charge actions buy nothing`);
}
console.log(bad ? `${bad} FAILED` : "every toy day: the DP optimum equals brute force");
process.exit(bad ? 1 : 0);
