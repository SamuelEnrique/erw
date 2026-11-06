// Energy Research Warehouse (ERW) site, session 2402: the figures docs/battery_game_demo.md quotes, recomputed with the
// game's own model (lib/battery.ts) from the frozen levels (data/battery_levels.json), so that the demo note never
// quotes a figure the page no longer shows.
//
//   node --import ./scripts/alias-register.mjs scripts/check-battery-demo.mjs
//
// For each day the note names, the perfect battery's earnings under each mode (the exact dynamic programme, optimum,
// replayed with simulate), the roof alone (noBattery with the solar add-on), and the day's lowest and highest price with
// their intervals. Prints one line a figure and exits 1 on any difference at the precision the note prints. When the
// game's rules change (RULES_VERSION), update the note and EXPECTED in the same commit. Reads only; writes nothing.
import fs from "node:fs";
import { DEFAULT_SETTINGS, noBattery, optimum, rulesOf, simulate, validSolar } from "../lib/battery.ts";

const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels;

/** The note's figures: the day, what, the value printed, its decimals. */
export const EXPECTED = [
  ["2023-08-10", "lowest price, USD per MWh", 24.90, 2],
  ["2023-08-10", "highest price, USD per MWh", 3842.89, 2],
  ["2023-08-10", "lowest price, Central clock", "08:45", null],
  ["2023-08-10", "highest price, Central clock", "15:30", null],
  ["2023-08-10", "perfect battery, Easy, USD", 60.97, 2],
  ["2023-08-10", "perfect battery, Normal, USD", 60.97, 2],
  ["2023-08-10", "perfect battery, Hard, USD", 48.36, 2],
  ["2023-08-10", "perfect battery, Hard with rooftop solar, USD", 88.34, 2],
  ["2023-08-10", "no battery, Hard with rooftop solar (the roof alone), USD", 34.32, 2],
  ["2026-04-26", "perfect battery, Normal, USD", 0.44, 2],
];

const clock = new Intl.DateTimeFormat("en-GB", { timeZone: "America/Chicago", hour: "2-digit", minute: "2-digit", hour12: false });
function computed(date, what) {
  const l = levels.find((x) => x.date === date);
  if (!l) return undefined;
  const lo = l.price.indexOf(Math.min(...l.price)), hi = l.price.indexOf(Math.max(...l.price));
  if (what.startsWith("lowest price, USD")) return l.price[lo];
  if (what.startsWith("highest price, USD")) return l.price[hi];
  if (what.startsWith("lowest price, Central")) return clock.format(new Date(l.ts_utc[lo]));
  if (what.startsWith("highest price, Central")) return clock.format(new Date(l.ts_utc[hi]));
  const mode = what.includes("Easy") ? "easy" : what.includes("Normal") ? "normal" : "hard";
  const sun = what.includes("rooftop") ? (validSolar(l.solar, l.price.length) ? l.solar : undefined) : null;
  if (sun === undefined) return undefined;
  const r = rulesOf(DEFAULT_SETTINGS, mode, sun ? ["solar"] : []);
  if (what.startsWith("no battery")) return noBattery(l.price, r, sun);
  return simulate(l.price, optimum(l.price, r, sun).actions, r, sun).score;
}

let bad = 0;
for (const [date, what, want, dec] of EXPECTED) {
  const got = computed(date, what);
  const ok = got !== undefined && (dec === null ? got === want : Number(got.toFixed(dec)) === want);
  if (!ok) bad++;
  console.log(`${ok ? "ok  " : "FAIL"} ${date}, ${what}: note ${want}, computed ${got === undefined ? "nothing (no such level or no solar shape)" : dec === null ? got : got.toFixed(dec)}`);
}
console.log(bad ? `${bad} of ${EXPECTED.length} FAIL: the demo note and the game disagree` : `all ${EXPECTED.length} demo figures match the game's model`);
process.exit(bad ? 1 : 0);
