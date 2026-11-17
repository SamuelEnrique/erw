// Energy Research Warehouse (ERW) site, session 7544 (chain 304, part C): the site rows of the read of /curtailment as a
// solar or battery developer in CAISO or ERCOT reads it (docs/reviews/curtailment-read-2026-11-16.md, rows 1 to 8). The
// whole page is drawn to HTML with the site's own code on the site's own files (site/data/curtailment/ and
// site/data/curtailment_profile.json, public CAISO and ERCOT figures); its two reads of the live set are answered with no
// rows. No server, no network, nothing written.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-curtailment-read.mjs
import fs from "node:fs";
import { drawPage, pageText } from "./curtailment-page.mjs";
import { An, HUB_WORDS, an, curtailedOf, ercotWholeMonths } from "../app/curtailment/Sections.tsx";

let failed = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { failed += 1; console.log(`FAIL ${what}`); } };
const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf-8");
const json = (p) => JSON.parse(read(p));
const whole = (v) => Math.round(v).toLocaleString("en-US");
const profile = json("../data/curtailment_profile.json");
const worth = json("../data/curtailment/worth.json");
const ercot = json("../data/curtailment/ercot.json");
const shares = json("../data/curtailment/shares.json");
const none = () => [];
const draw = async (q) => pageText((await drawPage(none, q)).html);

// the helpers
check(an(8) === "an" && an("8") === "an" && an(2) === "a" && an(4) === "a" && An(8) === "An" && An(4) === "A", "an 8-hour, a 4-hour");
check(curtailedOf({ months: { "2026-01": { curtailed_mwh: 1 }, "2026-02": { curtailed_mwh: 2.5 } } }, "2026") === 3.5, "a year's curtailed MWh from its months");
check(curtailedOf({ months: { "2026-01": { curtailed_mwh: 1 }, "2026-02": {} } }, "2026") === null, "a month without the figure: no year");
check(curtailedOf({ months: { "2026-01": { curtailed_mwh: 7 } } }, "2026-01") === 7 && curtailedOf(undefined, "2026") === null, "a month's own");
check(JSON.stringify(ercotWholeMonths({ months: { "2026-11": { hours_held: 1 }, "2026-10": { both: { share_pct: 6 } }, "2026-09": { both: { share_pct: null } } } })) === '["2026-10"]', "the whole months of Texas's file");
check(HUB_WORDS.HB_HUBAVG.includes("four trading hubs"), "the hub average said in words");

// the page drawn, the default address (CAISO, the newest year) and the cases' addresses
const year = await draw({});
const oct = profile.months["2026-10"];
const months = Object.keys(profile.months).sort();
// row 1: the batteries' share is the month's, said as the month's
check(/percent of that month's curtailment fell in hours in which the batteries were already charging/.test(year), "row 1: the month named in the summary");
check(!/percent of it fell in hours in which the batteries/.test(year), "row 1: no 'of it' after a year");
// row 2: the batteries' count against the storage page's
check(year.includes("each five-minute value below zero, added up. The storage page 's daily charging nets each hour first, so it is never higher."), "row 2: the two counts of charging");
// row 3: a share over fewer days than the month says so, with the month whole
const sm = Object.entries(shares.grids.caiso.months).filter(([m, r]) => r.days_held < r.days_in_month && profile.months[m]);
for (const [m, r] of sm) {
  const p = profile.months[m];
  check(year.includes(`[title: Over the ${r.days_held} of ${r.days_in_month} days for which CAISO's wind and solar output is held; a day without it is left out of both sides of the share. Every day held of the month, from CAISO's record by the hour: ${whole(p.curtailed_solar_mwh + p.curtailed_wind_mwh)} MWh over ${p.days_held} of ${p.days_in_month} days] ${whole(r.curtailed_mwh)}`), `row 3: ${m}'s share names its days`);
}
check(sm.length >= 1, "row 3: at least one month of the file is over fewer days than the month");
// row 4: the worth of a period says what had no price
const rt = worth.grids.caiso.hubs[worth.grids.caiso.main_hub].rt;
const unpriced = Object.entries(rt.months).filter(([, v]) => v.curtailed_mwh !== undefined && v.curtailed_mwh - v.curtailed_mwh_priced >= 0.5);
for (const [m, v] of unpriced) {
  const t = await draw({ period: m });
  check(t.includes(`fell in hours with no real-time price held and are left out.`) && t.includes(`Of the ${whole(v.curtailed_mwh)} MWh curtailed in`) && t.includes(`, ${whole(v.curtailed_mwh - v.curtailed_mwh_priced)} fell`), `row 4: ${m}'s unpriced MWh`);
}
const full = Object.keys(rt.months).find((m) => rt.months[m].curtailed_mwh !== undefined && Math.abs(rt.months[m].curtailed_mwh - rt.months[m].curtailed_mwh_priced) < 0.5 && profile.months[m]);
if (full) check(!(await draw({ period: full })).includes("no real-time price held"), `row 4: ${full}, every MWh priced, no such sentence`);
// row 5: the hub table's hover says what its hours are
check(/\[title: [\d,]+ of the [\d,]+ hours with a price had any curtailment\] SP15, real time/.test(year), "row 5: CAISO's hours with a price and with curtailment");
// row 6: an 8-hour battery
const eight = await draw({ period: months.at(-1), dur: "8" });
check(eight.includes("An 8-hour battery could have taken in") && eight.includes("What an 8-hour fleet could have absorbed") && !/\bA 8-hour|\ba 8-hour/.test(eight), "row 6: an 8-hour");
check((await draw({ dur: "2" })).includes("A 2-hour battery could have taken in"), "row 6: a 2-hour");
// rows 7 and 8: Texas's whole month in the head, and the hub average in words
const tx = await draw({ grid: "ercot" });
const wm = ercotWholeMonths(ercot).at(-1);
if (wm) {
  const r = ercot.months[wm];
  check(tx.includes(`A whole month, ${["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][Number(wm.slice(5)) - 1]} ${wm.slice(0, 4)} ${r.both.share_pct.toFixed(2)} percent`), "row 7: the newest whole month in the head");
  check(!tx.includes("ERCOT, a whole month: [title"), "row 7: no 'a whole month: not held yet' above the month held");
}
check(tx.includes(`[title: ${HUB_WORDS.HB_HUBAVG}. `) && tx.includes(`hours with a real-time price, at [title: ${HUB_WORDS.HB_HUBAVG}] HB HUBAVG`), "row 8: HB HUBAVG said in words, the table and the head");
check(/\[title: [\d,]+ of the [\d,]+ hours with a price had output below the limit\]/.test(tx), "row 5: Texas's hours say output below the limit");

// nothing of a license-held table in what this session commits: the read file and this test name no held grid's figure
const readFile = fs.readFileSync(new URL("../../docs/reviews/curtailment-read-2026-11-16.md", import.meta.url), "utf-8");
check(!/(nyiso|isone|miso|pjm):/i.test(readFile), "the read file names no entity of a held grid");
check(!/(NYISO|ISO-NE|MISO|PJM)[^|\n]{0,40}\d{2,}/.test(readFile.replace(/rows? \d+|\d+ rows|session \d+|sessions? \d+/g, "")), "the read file gives no figure of a held grid");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
