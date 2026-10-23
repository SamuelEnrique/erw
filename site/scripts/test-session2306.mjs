// Energy Research Warehouse (ERW) site, session 2306: the All grids tab's disclosure words, on fixtures. No request, no
// browser, no build.
//
//   node --import ./scripts/alias-register.mjs scripts/test-session2306.mjs
//
//   1. peakWords: the sentence on ERCOT's four summer peak intervals follows the count the model made (ProfileTwelve.peaks),
//      where the tab printed "none of those held falls in these months" whatever the count was.
//   2. (session 2306, fix 3) foreseenWords and columnHead: a flexible or electrolyzer profile's figures that are chosen
//      knowing the year's prices are labelled "if perfectly foreseen" in the tip and in the column head, as "Your load"
//      labels its own hindsight figure; the datacenter profile's are not.
// Exit 1 on a failure.
import { peakWords } from "../lib/siting.ts";

let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };

// 1. the peak intervals' sentence
const note = "the intervals are ERCOT's own, from its 4CP report";
check(peakWords(0, 2025, note) === `none of those held falls in these months (ercot_4cp_intervals holds summers to 2025; ${note})`, "0 peak hours in the window: the old sentence, with the newest summer and the note");
check(peakWords(1, 2026, note) === `1 of their hours held falls in these months and the load is off in it (ercot_4cp_intervals holds summers to 2026; ${note})`, "1 peak hour in the window: singular");
check(peakWords(4, 2026, note) === `4 of their hours held fall in these months and the load is off in them (ercot_4cp_intervals holds summers to 2026; ${note})`, "4 peak hours in the window: plural, and the load is off in them");
check(peakWords(0, undefined, note).includes("holds summers to none"), "no summer held: \"none\"");
check(!/—/.test(peakWords(3, 2026, note)), "no em dash");

export { check, bad, n };
if (!process.env.SESSION2306_MORE) {
  console.log(`${n - bad} of ${n} passed`);
  process.exit(bad ? 1 : 0);
}
