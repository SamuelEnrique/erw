// Energy Research Warehouse (ERW) site, session 38: the battery game's optimum against brute force.
//
//   node scripts/test-battery.mjs        (Node 23.6 or later runs lib/battery.ts as it is; tests/test_session38.py runs this)
//
// On 12-interval toy days, every one of the 3^12 action sequences is simulated with the game's own rules, and the best
// score must equal the dynamic programme's optimum, whose actions must reproduce it. Prints one line per day; exits 1
// on any mismatch.
import { eventPageFor, FLEET_MW, FLEET_MWH, isPerfect, optimum, perfectShare, simulate, vppHour } from "../lib/battery.ts";
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
console.log(bad ? `${bad} FAILED` : "every toy day: the DP optimum equals brute force");
process.exit(bad ? 1 : 0);
