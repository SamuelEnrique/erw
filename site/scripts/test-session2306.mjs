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

// 2. the carbon column names its measure by profile (fix 2)
{
  const { columnHead, COLUMNS, foreseen, foreseenWords } = await import("../lib/siting.ts");
  const dc = { profile: "datacenter", strike: null }, flex = { profile: "flexible", strike: 150 }, ely = { profile: "electrolyzer", strike: null }, elyTyped = { profile: "electrolyzer", strike: 40 }, ind = { profile: "industry", strike: null };
  const carbon = COLUMNS.find((c) => c.id === "carbon");
  check(columnHead(carbon, dc) === "Carbon (eGRID 2023, generated)", "datacenter: eGRID's generation-based annual rate");
  check(columnHead(carbon, flex) === "Carbon (EIA-930 hourly, consumed, where held)" && columnHead(carbon, ely) === "Carbon (EIA-930 hourly, consumed, where held)", "flexible and electrolyzer: EIA-930's hourly consumption-based intensity");
  check(/eGRID 2023/.test(carbon.tip) && /intensity_demand/.test(carbon.tip) && /16 December 2025/.test(carbon.tip) && /eia930_caiso_break/.test(carbon.tip), "the head's tip states both measures and names the CAISO reporting break");
  const other = COLUMNS.find((c) => c.id === "capacity");
  check(columnHead(other, flex) === other.head, "another column's head is unchanged");

  // 3. the hindsight figures are labelled "if perfectly foreseen" (fix 3)
  const energy = COLUMNS.find((c) => c.id === "energy"), tx = COLUMNS.find((c) => c.id === "transmission");
  check(foreseen(flex) && foreseen(ely) && !foreseen(elyTyped) && !foreseen(dc) && !foreseen(ind), "foreseen: the flexible profile and the electrolyzer at its own percentile; not a typed strike, the flat load or industry");
  check(columnHead(energy, flex) === "Energy (if perfectly foreseen)" && columnHead(energy, ely) === "Energy (if perfectly foreseen)", "the energy head is labelled for the two hindsight profiles");
  check(columnHead(energy, dc) === "Energy" && columnHead(energy, elyTyped) === "Energy" && columnHead(energy, ind) === "Energy", "the energy head is plain for the others");
  check(columnHead(tx, flex) === "Transmission and 4CP (own and off: if perfectly foreseen)" && columnHead(tx, dc) === "Transmission and 4CP", "the transmission head is labelled for the flexible profile alone");
  check(foreseenWords("its strike").startsWith("If perfectly foreseen: its strike is chosen knowing the whole year's prices") && /Your load/.test(foreseenWords("x")), "the tip's words, in the single-region tab's own phrase");
  const view = (await import("node:fs")).readFileSync(new URL("../app/cost-of-power/AllGridsView.tsx", import.meta.url), "utf-8");
  check(/foreseen\(x\) \? "" : ` \$\{foreseenWords\(/.test(view) && /curtTip = `Curtailing:[^\n]*\$\{hind\}/.test(view) && /columnHead\(c, x\)/.test(view), "the tab draws the words in the profile's tip, the four-peak tips and the heads");
  check(!/—/.test(view) && !/—/.test(foreseenWords("x")), "no em dash");
}

console.log(`${n - bad} of ${n} passed`);
process.exit(bad ? 1 : 0);
