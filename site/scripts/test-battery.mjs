// Energy Research Warehouse (ERW) site, session 38: the battery game's optimum against brute force.
//
//   node scripts/test-battery.mjs        (Node 23.6 or later runs lib/battery.ts as it is; tests/test_session38.py runs this)
//
// On 12-interval toy days, every one of the 3^12 action sequences is simulated with the game's own rules, and the best
// score must equal the dynamic programme's optimum, whose actions must reproduce it. Prints one line per day; exits 1
// on any mismatch.
import { optimum, simulate, vppHour } from "../lib/battery.ts";

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
console.log(bad ? `${bad} FAILED` : "every toy day: the DP optimum equals brute force");
process.exit(bad ? 1 : 0);
