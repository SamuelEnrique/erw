// Energy Research Warehouse (ERW) site, session 38: the battery game's optimum against brute force.
//
//   node scripts/test-battery.mjs        (Node 23.6 or later runs lib/battery.ts as it is; tests/test_session38.py runs this)
//
// On 12-interval toy days, every one of the 3^12 action sequences is simulated with the game's own rules, and the best
// score must equal the dynamic programme's optimum, whose actions must reproduce it. Prints one line per day; exits 1
// on any mismatch.
import {
  ADDONS, DEFAULT_PRESET, DEFAULT_SETTINGS, EMERGENCY, emergencyOf, eventPageFor, explain, FLEET_MW, FLEET_MWH, isPerfect, LIGHTS_OUT, optimum, outageDraw, parsePreset, perfectShare,
  presetLabel, presetOf, RULES_VERSION, rulesOf, SETTINGS, shownPrices, simulate, SOLAR, solarKwh, SPIKE_LABEL, START_MONEY, validAddons, validSettings, validSolar, vppHour, worstHour,
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
// session 70: a second toy shape, with sun in the first intervals (where the toy day "negative" has its negative
// prices), so the curtailment rule is in play under brute force. A test shape, used on the toy days only.
const EARLY_SUN = [0.5, 0.6, 0.4, 0.2, 0.1, 0, 0, 0, 0, 0, 0, 0];
const presets = [
  ["hard, default battery", DEFAULT_SETTINGS, "hard"],
  ["hard, 5 kWh, 2.5 kW, 85 percent, reserve 30, wear 0.20", { kwh: 5, kw: 2.5, rte: 0.85, reserve: 0.3, deg: 0.2 }, "hard"],
  ["easy, 20 kWh, 10 kW, 92 percent", { kwh: 20, kw: 10, rte: 0.92, reserve: 0.2, deg: 0.11 }, "easy"],
  ["normal, default battery", DEFAULT_SETTINGS, "normal"],
  // session 66: Hard with the rooftop solar add-on, the outage and the lights-out penalty in play
  ["hard, default battery, rooftop solar", DEFAULT_SETTINGS, "hard", ["solar"]],
  ["hard, 5 kWh, 2.5 kW, 85 percent, reserve 30, wear 0.20, rooftop solar", { kwh: 5, kw: 2.5, rte: 0.85, reserve: 0.3, deg: 0.2 }, "hard", ["solar"]],
  // session 70: the roof with sun at the negative prices (curtailment), and the largest inverter (the whole-outage charge)
  ["hard, default battery, rooftop solar, early sun", DEFAULT_SETTINGS, "hard", ["solar"], EARLY_SUN],
  ["hard, 13.5 kWh, 11.5 kW, no reserve", { ...DEFAULT_SETTINGS, kw: 11.5, reserve: 0 }, "hard"],
];
// session 66: a toy solar shape (output per MW installed, one per interval): dark, a morning climb, a midday peak, dusk.
// With the 5 kW roof it makes less than the house needs in some outage intervals, exactly its need in one (0.3) and more
// in others, so the outage's three cases all occur. A test shape, used on the toy days only.
const TOY_SUN = [0, 0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.5, 0.2, 0.05];
// session 66, Part A: per Hard preset and toy day, whether some play keeps the lights on all day (from brute force)
const toyFeasible = [];
for (const [label, s, d, addons, shape] of presets) {
  const r = rulesOf(s, d, addons ?? []);
  const sun = r.solarKw > 0 ? (shape ?? TOY_SUN) : undefined;
  for (const [name, prices] of Object.entries(days)) {
    // session 63: on Hard the outage may draw the battery below its reserve (the reserve is for it): the reserve binds
    // before the outage
    const o = emergencyOf(prices, r).outage;
    const upto = (soc) => (o ? soc.slice(0, o.first + 1) : soc);
    let best = -Infinity;
    const seq = new Array(12).fill(0);
    const acts = [1, 0, -1];
    let lowest = Infinity;
    let lit = false, dark = 0, sums = true;
    for (let code = 0; code < 3 ** 12; code++) {
      let c = code;
      for (let i = 0; i < 12; i++) { seq[i] = acts[c % 3]; c = Math.floor(c / 3); }
      const x = simulate(prices, seq, r, sun);
      if (x.score > best) best = x.score;
      if (x.why === "") lit = true;
      if (x.why === "lights_out") dark++;
      if (code % 997 === 0) {
        lowest = Math.min(lowest, ...upto(x.soc));
        // session 66: the per-interval earnings sum to the score (the end screen's hour is read from them)
        if (Math.abs(x.gain.reduce((a, b) => a + b, 0) - x.score) > 1e-9) sums = false;
      }
    }
    const dp = optimum(prices, r, sun);
    const replay = simulate(prices, dp.actions, r, sun);
    // session 66, Part A: where some play keeps the lights on all day, the perfect battery does not end in lights out
    const keeps = !(lit && replay.why === "lights_out");
    if (o) toyFeasible.push({ label, name, s, d, addons: addons ?? [], prices, sun, lit });
    const ok = Math.abs(dp.score - best) < 1e-9 && Math.abs(replay.score - dp.score) < 1e-9 && lowest >= r.reserveKwh - 1e-9 && Math.min(...upto(replay.soc)) >= r.reserveKwh - 1e-9 && keeps && sums;
    if (!ok) bad++;
    console.log(`${ok ? "ok  " : "FAIL"} ${label}, ${name}: brute force ${best.toFixed(6)}, DP ${dp.score.toFixed(6)}, replayed ${replay.score.toFixed(6)} (wear ${replay.wear.toFixed(4)}), lowest charge before any outage ${Math.min(lowest, ...upto(replay.soc)).toFixed(3)} of reserve ${r.reserveKwh.toFixed(3)} kWh${o ? `; outage ${o.first} to ${o.last}: ${dark} of ${3 ** 12} plays go dark, keeping the lights on is ${lit ? "possible" : "not possible"}, the perfect battery ends ${replay.why || "with a whole day"}` : ""}`);
  }
}
// on Normal with the default battery the defaults are the rules: the same score for the same actions; session 63: the
// preset carries the rules' version
{
  const a = optimum(days.shape).actions;
  const ok = Math.abs(simulate(days.shape, a).score - simulate(days.shape, a, rulesOf(DEFAULT_SETTINGS, "normal")).score) < 1e-12 && presetOf(DEFAULT_SETTINGS, "normal") === DEFAULT_PRESET && DEFAULT_PRESET === "normal:13.5-5-90-v4";
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} Normal with the default battery: its preset is ${DEFAULT_PRESET}`);
}
const v2 = [
  ["validSettings(defaults)", validSettings(DEFAULT_SETTINGS), true],
  ["validSettings: kwh 31 is out of range", validSettings({ ...DEFAULT_SETTINGS, kwh: 31 }), false],
  ["validSettings: kw 5.25 is off its 0.5 step", validSettings({ ...DEFAULT_SETTINGS, kw: 5.25 }), false],
  ["validSettings: an extra key", validSettings({ ...DEFAULT_SETTINGS, x: 1 }), false],
  ["validSettings: a string", validSettings({ ...DEFAULT_SETTINGS, deg: "0.11" }), false],
  // session 66: the presets carry v4 and the add-ons; v2 and v3 boards stay readable and say which rules they are
  ["RULES_VERSION", RULES_VERSION, "v4"],
  ["presetOf(hard)", presetOf(DEFAULT_SETTINGS, "hard"), "hard:13.5-5-90-r20-d0.11-v4"],
  ["presetOf(hard, rooftop solar)", presetOf(DEFAULT_SETTINGS, "hard", ["solar"]), "hard:13.5-5-90-r20-d0.11-solar-v4"],
  ["presetOf(normal) ignores an add-on: Normal has none", presetOf(DEFAULT_SETTINGS, "normal", ["solar"]), "normal:13.5-5-90-v4"],
  ["presetLabel(default normal, v4)", presetLabel("normal:13.5-5-90-v4"), "Normal, the default battery"],
  ["presetLabel(default normal, a v3 board)", presetLabel("normal:13.5-5-90-v3"), "Normal, the default battery (v3 rules)"],
  ["presetLabel(default normal, a v2 board)", presetLabel("normal:13.5-5-90"), "Normal, the default battery (v2 rules)"],
  ["presetLabel(custom hard)", presetLabel("hard:5-2.5-85-r30-d0.2-v4"), "Hard, 5 kWh, 2.5 kW, 85 percent round trip, reserve 30 percent, wear $0.2 per kWh"],
  ["presetLabel(custom hard, a v3 board)", presetLabel("hard:5-2.5-85-r30-d0.2-v3"), "Hard, 5 kWh, 2.5 kW, 85 percent round trip, reserve 30 percent, wear $0.2 per kWh (v3 rules)"],
  ["presetLabel(default hard, rooftop solar)", presetLabel("hard:13.5-5-90-r20-d0.11-solar-v4"), "Hard, the default battery, with rooftop solar"],
  ["presetLabel(custom hard, rooftop solar)", presetLabel("hard:5-2.5-85-r30-d0.2-solar-v4"), "Hard, 5 kWh, 2.5 kW, 85 percent round trip, reserve 30 percent, wear $0.2 per kWh, with rooftop solar"],
  ["parsePreset(v4) round trip", JSON.stringify(parsePreset("hard:13.5-5-90-r20-d0.11-v4")), JSON.stringify({ settings: DEFAULT_SETTINGS, difficulty: "hard", addons: [], version: "v4" })],
  ["parsePreset(v4, rooftop solar) round trip", JSON.stringify(parsePreset("hard:13.5-5-90-r20-d0.11-solar-v4")), JSON.stringify({ settings: DEFAULT_SETTINGS, difficulty: "hard", addons: ["solar"], version: "v4" })],
  ["parsePreset(a v3 board) is readable", parsePreset("hard:13.5-5-90-r20-d0.11-v3")?.version, "v3"],
  ["parsePreset(a v2 board) is readable", parsePreset("normal:13.5-5-90")?.version, "v2"],
  ["parsePreset(a v2 Hard board) is readable", parsePreset("hard:13.5-5-90-r20-d0.11")?.version, "v2"],
  ["parsePreset: v3 twice is refused", parsePreset("normal:13.5-5-90-v3-v3"), null],
  ["parsePreset: v4 twice is refused", parsePreset("normal:13.5-5-90-v4-v4"), null],
  ["parsePreset: an add-on on a v3 board is refused (v3 had none)", parsePreset("hard:13.5-5-90-r20-d0.11-solar-v3"), null],
  ["parsePreset: an add-on without a version is refused", parsePreset("hard:13.5-5-90-r20-d0.11-solar"), null],
  ["parsePreset: an add-on on Normal is refused", parsePreset("normal:13.5-5-90-solar-v4"), null],
  ["parsePreset: an unknown add-on is refused", parsePreset("hard:13.5-5-90-r20-d0.11-wind-v4"), null],
  ["parsePreset: an add-on twice is refused", parsePreset("hard:13.5-5-90-r20-d0.11-solar-solar-v4"), null],
  ["every preset the game writes round trips", [["easy", []], ["normal", []], ["hard", []], ["hard", ["solar"]]].every(([d, a]) => {
    const p = parsePreset(presetOf(DEFAULT_SETTINGS, d, a));
    return p !== null && presetOf(p.settings, p.difficulty, p.addons) === presetOf(DEFAULT_SETTINGS, d, a) && p.version === "v4";
  }), true],
  ["validAddons: none, anywhere", validAddons([], "easy"), true],
  ["validAddons: rooftop solar on Hard", validAddons(["solar"], "hard"), true],
  ["validAddons: rooftop solar on Normal", validAddons(["solar"], "normal"), false],
  ["validAddons: an unknown add-on", validAddons(["wind"], "hard"), false],
  ["validAddons: not a list", validAddons("solar", "hard"), false],
  ["the add-ons shipped", Object.keys(ADDONS).join(","), "solar"],
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
// session 66: game v4.
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const HARD = rulesOf(DEFAULT_SETTINGS, "hard");
const need = (EMERGENCY.houseKw * 15) / 60;  // the house's need in one interval, kWh at the meter
// Part A (session 70): lights out costs money, priced at Texas's value of lost load, for the whole outage. Selling
// everything into the spike with the 5 kWh test battery: lights out at the outage's first interval; the house is
// charged 1.5 kW for every interval of the outage at USD 35,000/MWh; the score carries it, and the earnings per
// interval sum to the score
{
  const r = rulesOf({ ...DEFAULT_SETTINGS, kwh: 5, kw: 5, reserve: 0 }, "hard");
  const day = days.spike, em = emergencyOf(day, r), v = vppHour(day);
  const x = simulate(day, day.map((_, i) => (i >= v.first && i <= v.last ? -1 : 0)), r);
  const all = em.outage.last - em.outage.first + 1;
  const want = (all * need * LIGHTS_OUT.usdPerMwh) / 1000;
  check(LIGHTS_OUT.usdPerMwh === 35000 && LIGHTS_OUT.study === 35685 && LIGHTS_OUT.residential === 3964 && r.voll === 35000 && HARD.voll === 35000,
    `the lights-out charge is priced at USD ${LIGHTS_OUT.usdPerMwh}/MWh (the study's ${LIGHTS_OUT.study}, rounded by the Commission; residential alone ${LIGHTS_OUT.residential})`);
  check(x.why === "lights_out" && Math.abs(x.penalty - want) < 1e-9 && Math.abs(x.unservedKwh - all * need) < 1e-12 && Math.abs(x.score - (x.cash - x.wear + x.bonus - x.penalty)) < 1e-9
    && Math.abs(x.gain.reduce((a, b) => a + b, 0) - x.score) < 1e-9 && Math.abs(x.gain[x.end] + want) < 1e-9,
  `lights out costs money: ${all} intervals x ${need} kWh at USD ${LIGHTS_OUT.usdPerMwh}/MWh = USD ${x.penalty.toFixed(4)}; the score ${x.score.toFixed(4)}`);
  // sold at the day's cheap start instead: little earned, the same penalty: the money ends below $0, and the round
  // ended at lights out (the out-of-money rule has nothing left to end)
  const y = simulate(day, day.map((_, i) => (i < 4 ? -1 : 0)), r);
  check(y.why === "lights_out" && y.end === em.outage.first && y.money < 0 && Math.abs(y.money - (START_MONEY + y.score)) < 1e-12, `the penalty can take the money below $0: money ${y.money.toFixed(4)} after lights out at interval ${y.end}`);
  // Fix 2: lights out later in the outage costs the whole outage all the same, not only what is left of it: the same
  // charge as going dark at the outage's first interval
  const z = simulate(days.flat, days.flat.map(() => 0), r), z0 = simulate(days.flat, days.flat.map((_, i) => (i < 4 ? -1 : 0)), r);
  const o = emergencyOf(days.flat, r).outage, whole8 = o.last - o.first + 1;
  check(z.why === "lights_out" && z.end > o.first && z0.why === "lights_out" && z0.end === o.first && Math.abs(z.unservedKwh - whole8 * need) < 1e-12 && Math.abs(z.penalty - (whole8 * need * 35000) / 1000) < 1e-9 && z.penalty === z0.penalty,
    `lights out at interval ${z.end} of an outage ${o.first} to ${o.last} is charged for all ${whole8} intervals, USD ${z.penalty.toFixed(4)}, as lights out at interval ${z0.end} is`);
  check(Math.abs((8 * need * LIGHTS_OUT.usdPerMwh) / 1000 - 105) < 1e-9 && Math.abs((need * LIGHTS_OUT.usdPerMwh) / 1000 - 13.125) < 1e-9, "a whole two-hour outage in the dark costs USD 105.00 (USD 13.125 for each fifteen minutes)");
  // mid-game the page scores only the intervals played: before the outage nothing of it shows, even where idling
  // through the rest of the day would end in lights out
  const whole = simulate(day, [-1, -1, -1, -1], r), part = simulate(day, [-1, -1, -1, -1], r, undefined, 4);
  check(whole.why === "lights_out" && part.why === "" && part.end === null && part.penalty === 0 && part.soc.length === 5 && part.soc[4] === 0 && Math.abs(part.score - part.gain.reduce((a, b) => a + b, 0)) < 1e-12
    && simulate(day, optimum(day, r).actions, r, undefined, 12).score === simulate(day, optimum(day, r).actions, r).score,
  `the state after 4 intervals holds nothing of the outage to come (charge ${part.soc[4].toFixed(2)} kWh, money ${part.money.toFixed(2)}); the whole day ends ${whole.why}`);
  check(simulate(days.shape, optimum(days.shape).actions).penalty === 0 && simulate(days.shape, days.shape.map(() => -1)).penalty === 0, "Normal has no outage and no penalty");
}
// Part A's required result (session 70: at the fixed price; nothing is searched or tuned). The cases: each famous day on
// Hard with the default battery (and with rooftop solar where the level holds a solar shape); each toy day with an
// outage under every Hard preset of the brute force above; and the larger-inverter batteries session 66 named as able
// to choose the dark (BIG: the largest inverter, 11.5 kW, on the default, the largest and the smallest battery, with and
// without the reserve and the wear cost), on every famous day and every toy day with an outage. Where keeping the lights
// on is possible (the optimum under a prohibitive price stays lit; for the brute-forced toy cases, some play does), the
// perfect battery must not end in lights out. A case that fails is printed exactly; the price is not changed for it.
{
  const BIG = [
    ["13.5 kWh, 11.5 kW", { ...DEFAULT_SETTINGS, kw: 11.5 }],
    ["13.5 kWh, 11.5 kW, no reserve, no wear", { ...DEFAULT_SETTINGS, kw: 11.5, reserve: 0, deg: 0 }],
    ["30 kWh, 11.5 kW", { ...DEFAULT_SETTINGS, kwh: 30, kw: 11.5 }],
    ["30 kWh, 11.5 kW, no reserve, no wear, 95 percent round trip", { kwh: 30, kw: 11.5, rte: 0.95, reserve: 0, deg: 0 }],
    ["5 kWh, 11.5 kW", { ...DEFAULT_SETTINGS, kwh: 5, kw: 11.5 }],
    ["5 kWh, 11.5 kW, no reserve, no wear", { ...DEFAULT_SETTINGS, kwh: 5, kw: 11.5, reserve: 0, deg: 0 }],
  ];
  const toyOutage = Object.entries(days).filter(([, p]) => emergencyOf(p, HARD).outage);
  const cases = [
    ...levels.map((l) => ({ what: `${l.date} (${l.slug}), Hard, default battery`, prices: l.price, s: DEFAULT_SETTINGS, addons: [], sun: undefined })),
    ...levels.filter((l) => validSolar(l.solar, l.price.length)).map((l) => ({ what: `${l.date} (${l.slug}), Hard, default battery, rooftop solar`, prices: l.price, s: DEFAULT_SETTINGS, addons: ["solar"], sun: l.solar })),
    ...toyFeasible.map((c) => ({ what: `toy day ${c.name}: ${c.label}`, prices: c.prices, s: c.s, addons: c.addons, sun: c.sun, lit: c.lit })),
    ...BIG.flatMap(([name, s]) => [
      ...levels.map((l) => ({ what: `${l.date} (${l.slug}), Hard, ${name}`, prices: l.price, s, addons: [], sun: undefined, big: true })),
      ...toyOutage.map(([day, p]) => ({ what: `toy day ${day}, Hard, ${name}`, prices: p, s, addons: [], sun: undefined, big: true })),
    ]),
  ];
  const play = (c, voll) => {
    const r = { ...rulesOf(c.s, "hard", c.addons), voll };
    return simulate(c.prices, optimum(c.prices, r, c.sun).actions, r, c.sun);
  };
  for (const c of cases) if (c.lit === undefined) c.lit = play(c, 1e12).why !== "lights_out";
  const can = cases.filter((c) => c.lit);
  const dark = can.filter((c) => play(c, LIGHTS_OUT.usdPerMwh).why === "lights_out");
  console.log(`  Part A: ${cases.length} cases (${cases.filter((c) => c.big).length} with the 11.5 kW inverter), ${can.length} where the lights can be kept on (not possible: ${cases.filter((c) => !c.lit).map((c) => c.what).join("; ") || "none"})`);
  for (const c of dark) {
    const x = play(c, LIGHTS_OUT.usdPerMwh), lit = play(c, 1e12);
    console.log(`  Part A FAILS: ${c.what}: the perfect battery ends in lights out at interval ${x.end} with USD ${x.score.toFixed(4)} after a charge of USD ${x.penalty.toFixed(4)} (${x.outageStartKwh.toFixed(3)} kWh at the outage's start, need ${x.outageNeedKwh.toFixed(3)}); keeping the lights on earns USD ${lit.score.toFixed(4)}`);
  }
  check(dark.length === 0, `Part A: at USD ${LIGHTS_OUT.usdPerMwh}/MWh for the whole outage the perfect battery never ends in lights out where the lights can be kept on (${can.length} cases)${dark.length ? `; ${dark.length} FAIL` : ""}`);
  // the closest case: what going dark would have had to save to be worth it
  let tight = null;
  for (const c of can) {
    const free = play(c, 0), lit = play(c, 1e12);  // the best play if the dark were free, and the best play that stays lit
    if (free.why !== "lights_out") continue;
    const gainDark = free.score - lit.score, charge = (free.unservedKwh * LIGHTS_OUT.usdPerMwh) / 1000;
    if (!tight || charge - gainDark < tight.room) tight = { what: c.what, gainDark, charge, room: charge - gainDark };
  }
  if (tight) console.log(`  Part A: the closest case is ${tight.what}: with no charge at all, going dark would earn USD ${tight.gainDark.toFixed(2)} more than staying lit; the charge is USD ${tight.charge.toFixed(2)}`);
  // the table of the report: the perfect battery on the famous days under v4
  for (const l of levels) {
    const row = [["Hard", HARD, undefined], ...(validSolar(l.solar, l.price.length) ? [["Hard with rooftop solar", rulesOf(DEFAULT_SETTINGS, "hard", ["solar"]), l.solar]] : []), ["Normal", rulesOf(DEFAULT_SETTINGS, "normal"), undefined]]
      .map(([name, r, sun]) => {
        const x = simulate(l.price, optimum(l.price, r, sun).actions, r, sun);
        return `${name} ${x.score.toFixed(2)} USD, ends ${x.why || "with a whole day"}${x.outageStartKwh !== null ? `, ${x.outageStartKwh.toFixed(2)} kWh at the outage's start (need ${x.outageNeedKwh.toFixed(2)})` : ""}`;
      });
    console.log(`  v4, ${l.date} (${l.slug}): ${row.join("; ")}${validSolar(l.solar, l.price.length) ? "" : "; no solar shape held for this day: the rooftop add-on is unavailable"}`);
  }
}
// Part B: a spiked price never shows without its label. Every interval whose played price is not the real one carries
// SPIKE_LABEL and the real price in its text; every other shows the real price plain; off Hard nothing is labeled
{
  const fmt = (v) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
  let spiked = 0, plain = 0, wrong = 0;
  for (const prices of [...levels.map((l) => l.price), ...Object.values(days)]) {
    const em = emergencyOf(prices, HARD), shown = shownPrices(prices, HARD);
    shown.forEach((s, i) => {
      const changed = em.prices[i] !== prices[i];
      const inSpike = i >= em.spike.first && i <= em.spike.last;
      if (changed) spiked++; else plain++;
      const good = changed
        ? s.spike && inSpike && s.text === `${fmt(em.prices[i])} USD/MWh (${SPIKE_LABEL}; the real price was ${fmt(prices[i])} USD/MWh)` && s.value === em.prices[i] && s.real === prices[i]
        : !s.spike && !s.text.includes(SPIKE_LABEL) && s.text === `${fmt(prices[i])} USD/MWh` && s.value === prices[i];
      if (!good || shown.length !== prices.length) wrong++;
    });
    if (shownPrices(prices, rulesOf(DEFAULT_SETTINGS, "normal")).some((s) => s.spike || s.text.includes(SPIKE_LABEL))) wrong++;
  }
  check(wrong === 0 && spiked > 0 && SPIKE_LABEL === "game rule, not a real price", `Part B: ${spiked} spiked prices, each with "${SPIKE_LABEL}" and its real price on the number; ${plain} real prices plain; none labeled off Hard`);
  // Uri's dearest hour already sits above the cap: the game leaves those prices as they are, so they are real and plain
  const uri = levels.find((l) => l.slug === "uri");
  const u = emergencyOf(uri.price, HARD), us = shownPrices(uri.price, HARD);
  check(us.slice(u.spike.first, u.spike.last + 1).every((s, k) => s.spike === (uri.price[u.spike.first + k] < EMERGENCY.cap)), `Part B: Uri's dearest hour: ${us.slice(u.spike.first, u.spike.last + 1).map((s) => s.text).join(" | ")}`);
  // the page: Game.tsx shows a played price only through shownPrices' text or worstHour's (lib/battery.ts). It never
  // formats the played prices itself: the array is used for the chart's geometry alone, and each line that prints USD/MWh
  // either prints a text from the library or a real price of the level
  const game = fs.readFileSync(new URL("../app/play/battery/Game.tsx", import.meta.url), "utf-8").split(/\r?\n/);
  const offenders = game.filter((line) => {
    if (/^\s*(\/\/|\{\/\*|\*)/.test(line)) return false;
    const formatsPlayed = /\bP\[[^\]]*\]\s*\.\s*(toLocaleString|toFixed)|em\.prices\[[^\]]*\]\s*\.\s*(toLocaleString|toFixed)|\$\{\s*P\[|\{\s*P\[/.test(line);
    const unit = line.includes("USD/MWh") && !/\.text\b|level\.price\[|GRIDS|EMERGENCY\.cap|const STEPS|^\s*"/.test(line);
    return formatsPlayed || unit;
  });
  check(offenders.length === 0 && game.some((l) => l.includes("shownPrices(")) && game.some((l) => l.includes("SPIKE_LABEL")), `Part B: Game.tsx prints no played price outside the library's labeled text${offenders.length ? `: ${offenders.map((l) => l.trim().slice(0, 90)).join(" || ")}` : ""}`);
}
// Part C: the end screen's hour, from simulate()'s own per-interval earnings
{
  const r = rulesOf(DEFAULT_SETTINGS, "normal");
  const best = optimum(days.shape, r);
  const perfect = simulate(days.shape, best.actions, r), idle = simulate(days.shape, days.shape.map(() => 0), r);
  const w = worstHour(days.shape, idle, perfect, r);
  const hours = [0, 4, 8].map((f) => perfect.gain.slice(f, f + 4).reduce((a, b) => a + b, 0) - idle.gain.slice(f, f + 4).reduce((a, b) => a + b, 0));
  const top = hours.indexOf(Math.max(...hours));
  check(w !== null && w.first === top * 4 && w.last === top * 4 + 3 && Math.abs(w.lost - hours[top]) < 1e-12 && Math.abs(w.lost - (w.perfect - w.mine)) < 1e-12 && [-1, 0, 1].includes(w.did) && !w.price.spike,
    `Part C: against a play that never moves, the hour lost most is intervals ${w?.first} to ${w?.last}: the perfect battery ${w?.did === -1 ? "sold" : w?.did === 1 ? "charged" : "held"} at ${w?.price.text} and earned ${w?.perfect.toFixed(4)}; the play ${w?.mine.toFixed(4)}`);
  check(worstHour(days.shape, perfect, perfect, r) === null, "Part C: a play that matches the perfect battery has no hour lost");
  // on Hard, a play that sits out the spike loses most in the spike hour, and the price it is told carries the label
  const h = rulesOf(DEFAULT_SETTINGS, "hard");
  const hp = simulate(days.spike, optimum(days.spike, h).actions, h), hi = simulate(days.spike, days.spike.map(() => 0), h);
  const hw = worstHour(days.spike, hi, hp, h), em = emergencyOf(days.spike, h);
  check(hw !== null && hw.first === em.spike.first && hw.did === -1 && hw.price.spike && hw.price.text.includes(SPIKE_LABEL) && hw.price.text.includes("the real price was"),
    `Part C on Hard: the hour lost most is the spike hour; its price reads "${hw?.price.text}"`);
  // lights out: the hour lost most is the outage's, where the perfect battery could only hold
  const dark = simulate(days.spike, days.spike.map((_, i) => (i < 8 ? -1 : 0)), rulesOf({ ...DEFAULT_SETTINGS, reserve: 0 }, "hard"));
  check(dark.why === "lights_out", `a play that sells everything before the outage goes dark (penalty USD ${dark.penalty.toFixed(2)})`);
}
// Part D: the rooftop solar add-on
{
  const solar = rulesOf(DEFAULT_SETTINGS, "hard", ["solar"]);
  check(solar.solarKw === SOLAR.kw && SOLAR.kw === 5 && HARD.solarKw === 0 && rulesOf(DEFAULT_SETTINGS, "normal", ["solar"]).solarKw === 0, "the roof is 5 kW, off by default, and only on Hard");
  let threw = 0;
  for (const shape of [undefined, null, TOY_SUN.slice(1), TOY_SUN.map((v, i) => (i === 3 ? NaN : v)), TOY_SUN.map((v, i) => (i === 3 ? null : v))]) {
    try { simulate(days.shape, days.shape.map(() => 0), solar, shape); } catch { threw++; }
    try { optimum(days.shape, solar, shape); } catch { threw++; }
  }
  check(threw === 10, "the roof without a whole solar shape of the day's length is refused, never filled (missing, short, or with a gap)");
  check(simulate(days.shape, optimum(days.shape, HARD).actions, HARD, TOY_SUN).score === simulate(days.shape, optimum(days.shape, HARD).actions, HARD).score, "without the add-on a level's solar shape changes nothing");
  // the fleet's output per MW installed is kept between 0 and 1: station use at night is not a roof drawing power
  const kwh = solarKwh([1, 1, 1, 1], solar, [-0.02, 0.5, 1.4, 1]);
  check(kwh[0] === 0 && kwh[1] === 5 * 0.5 * 0.25 && kwh[2] === 5 * 0.25 && kwh[3] === 5 * 0.25, `the roof's output: ${kwh.join(", ")} kWh for a fleet at -0.02, 0.5, 1.4 and 1 of its nameplate`);
  // a day without an outage (the toy day "negative": its dearest hour is the last): the roof's power is sold at each
  // interval's price, whatever the battery does, so the same actions earn exactly that much more
  const em = emergencyOf(days.negative, solar);
  const acts = optimum(days.negative, solar, TOY_SUN).actions;
  const a = simulate(days.negative, acts, solar, TOY_SUN), b = simulate(days.negative, acts, HARD);
  const sold = TOY_SUN.reduce((x, v, i) => x + (5 * v * 0.25 * em.prices[i]) / 1000, 0);
  check(em.outage === null && a.why === "" && Math.abs(a.solar - sold) < 1e-12 && Math.abs(a.score - b.score - sold) < 1e-9 && Math.abs(a.solarKwh - TOY_SUN.reduce((x, v) => x + 5 * v * 0.25, 0)) < 1e-12,
    `the roof's power is sold at each interval's price: USD ${a.solar.toFixed(4)} for ${a.solarKwh.toFixed(3)} kWh on the toy day "negative"`);
  // session 70, Fix 3: below zero the roof does not pay to export. With the battery idle or selling the roof is curtailed
  // and earns nothing; while the battery charges, the roof's power goes into it first (in place of grid power the
  // battery would have been paid to take) and only the rest is curtailed. The toy day "negative" opens with four
  // negative prices, and EARLY_SUN shines in them
  {
    const neg = days.negative, kwhOf = (i) => 5 * EARLY_SUN[i] * 0.25;
    const still = simulate(neg, neg.map(() => 0), solar, EARLY_SUN);
    const paid = neg.reduce((x, p, i) => x + (p >= 0 ? (kwhOf(i) * p) / 1000 : 0), 0), off = neg.reduce((x, p, i) => x + (p < 0 ? kwhOf(i) : 0), 0);
    check(off > 0 && Math.abs(still.solar - paid) < 1e-12 && Math.abs(still.curtailedKwh - off) < 1e-12 && [0, 1, 2, 3].every((i) => still.gain[i] === 0) && Math.abs(still.score - paid) < 1e-12,
      `below zero an idle battery's roof is curtailed: ${still.curtailedKwh.toFixed(3)} kWh switched off, nothing paid to export; the roof earns USD ${still.solar.toFixed(4)} at the prices of zero or more`);
    const sell = simulate(neg, [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], solar, EARLY_SUN), sellPlain = simulate(neg, [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], HARD);
    check(Math.abs(sell.gain[0] - sellPlain.gain[0]) < 1e-12 && sell.gain[0] < 0, `below zero a selling battery's roof is curtailed too: the interval's money is the battery's alone (USD ${sell.gain[0].toFixed(4)})`);
    // charging at -20 USD/MWh: the battery takes 1.25 kWh at the meter, 0.625 of it from the roof, so the grid pays for 0.625
    const chg = simulate(neg, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], solar, EARLY_SUN), chgPlain = simulate(neg, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], HARD);
    check(Math.abs(chg.gain[0] - ((1.25 - kwhOf(0)) * 20) / 1000) < 1e-12 && Math.abs(chgPlain.gain[0] - (1.25 * 20) / 1000) < 1e-12 && Math.abs(chg.curtailedKwh - (off - kwhOf(0))) < 1e-12,
      `below zero a charging battery takes the roof's power first: the grid pays for ${(1.25 - kwhOf(0)).toFixed(3)} kWh, not 1.25 (USD ${chg.gain[0].toFixed(4)} against ${chgPlain.gain[0].toFixed(4)} without the roof)`);
    // a 1 kW battery takes 0.25 kWh, less than the roof's 0.625: the rest is curtailed, and nothing is bought or sold
    const slow = rulesOf({ ...DEFAULT_SETTINGS, kw: 1 }, "hard", ["solar"]);
    const s1 = simulate(neg, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], slow, EARLY_SUN);
    check(Math.abs(s1.gain[0]) < 1e-12 && Math.abs(s1.curtailedKwh - (off - 0.25)) < 1e-12 && s1.soc[1] > s1.soc[0], `a roof larger than the charge: the battery charges for free and the rest is curtailed (${(kwhOf(0) - 0.25).toFixed(3)} kWh in the interval)`);
    // a full battery told to charge is not charging: the whole roof is curtailed
    const full = { ...solar, start: solar.kwh };
    const s2 = simulate(neg, [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], full, EARLY_SUN);
    check([0, 1, 2, 3].every((i) => s2.gain[i] === 0) && Math.abs(s2.curtailedKwh - off) < 1e-12, "a full battery told to charge takes nothing: below zero its roof is curtailed");
    // only a price below zero curtails: at exactly zero the roof is on and earns nothing (three intervals at 0, too
    // short a day for an emergency)
    const zero = simulate([0, 0, 0], [0, 0, 0], solar, [0.5, 0.5, 0.5]);
    check(zero.curtailedKwh === 0 && zero.solar === 0 && zero.solarKwh > 0 && simulate(days.shape, days.shape.map(() => 0), solar, TOY_SUN).curtailedKwh === 0, "at a price of zero or more nothing is curtailed");
    // the perfect battery with the roof never earns less than without it on this day's actions, and the DP knows the rule
    const o = optimum(neg, solar, EARLY_SUN);
    check(Math.abs(simulate(neg, o.actions, solar, EARLY_SUN).score - o.score) < 1e-9, `the DP plays by the curtailment rule (optimum USD ${o.score.toFixed(4)} on the toy day "negative" with early sun)`);
  }
  // in the outage (the toy day "flat": intervals 4 to 11) the roof carries the house first: below the house's need the
  // battery supplies the rest; at exactly the need the battery rests; above it the surplus charges the battery
  const idle = simulate(days.flat, days.flat.map(() => 0), solar, TOY_SUN);
  const eta = solar.eta, d = (i) => idle.soc[i + 1] - idle.soc[i];
  check(idle.why === "" && Math.abs(d(4) + (need - 5 * 0.1 * 0.25) / eta) < 1e-12 && Math.abs(d(6)) < 1e-12 && Math.abs(d(7) - (5 * 0.4 * 0.25 - need) * eta) < 1e-12 && Math.abs(d(8) - (5 * 0.6 * 0.25 - need) * eta) < 1e-12,
    `in the outage the roof runs the house first: the battery's charge moves ${[4, 6, 7, 8].map((i) => d(i).toFixed(4)).join(", ")} kWh in intervals 4, 6, 7 and 8`);
  check(Math.abs(idle.outageNeedKwh - TOY_SUN.slice(4).reduce((x, v) => x + Math.max(0, need - 5 * v * 0.25) / eta, 0)) < 1e-12 && idle.outageNeedKwh < simulate(days.flat, days.flat.map(() => 0), HARD).outageNeedKwh, `with the roof the outage needs ${idle.outageNeedKwh.toFixed(3)} kWh from the battery, less than without it`);
  // lights out with the roof: the unserved energy is the house's need less what the roof makes, to the outage's end
  const small = rulesOf({ ...DEFAULT_SETTINGS, kwh: 5, kw: 5, reserve: 0 }, "hard", ["solar"]);
  const night = TOY_SUN.map((v, i) => (i >= 4 && i <= 9 ? 0 : v));  // dark until interval 10
  const x = simulate(days.flat, days.flat.map((_, i) => (i < 4 ? -1 : 0)), small, night);
  const want = [4, 5, 6, 7, 8, 9, 10, 11].reduce((s, i) => s + Math.max(0, need - 5 * night[i] * 0.25), 0);
  check(x.why === "lights_out" && x.end === 4 && Math.abs(x.unservedKwh - want) < 1e-12 && Math.abs(x.penalty - (want * LIGHTS_OUT.usdPerMwh) / 1000) < 1e-9, `lights out with the roof: ${x.unservedKwh.toFixed(3)} kWh unserved (the need less the roof's output), USD ${x.penalty.toFixed(2)}`);
  // the famous days: with a shape held, the DP stays quick and its actions replay to its score
  for (const l of levels.filter((v) => validSolar(v.solar, v.price.length))) {
    const t0 = performance.now();
    const o = optimum(l.price, solar, l.solar);
    const ms = performance.now() - t0;
    check(ms < 2000 && Math.abs(simulate(l.price, o.actions, solar, l.solar).score - o.score) < 1e-9, `${l.date} on Hard with rooftop solar: the optimum ${o.score.toFixed(4)} USD in ${ms.toFixed(0)} ms`);
  }
  console.log(`  famous days with a solar shape held: ${levels.filter((v) => validSolar(v.solar, v.price.length)).map((v) => v.date).join(", ") || "none yet (warehouse/derived/battery_solar.py writes them; the add-on is unavailable until then)"}`);
}
console.log(bad ? `${bad} FAILED` : "every toy day: the DP optimum equals brute force");
process.exit(bad ? 1 : 0);
