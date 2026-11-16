// Chain 304, part B (sessions 7521 and 7524, 16 November 2026): "What a datacenter pays" (/cost-of-power, the view
// "Your load") read as the energy lead of an AI lab sizing a 300 MW site, for five cases
// (docs/reviews/datacenter-cost-read-2026-11-16.md). Each site fault the read found is held here as fixed: the row
// numbers are the review's. The page is drawn whole, without a build, by scripts/cost-of-power-read.mjs's drawer, its
// reads of the live set answered from the warehouse's table files on this machine (read only); where the files are not
// on the machine the drawn checks are skipped and said so. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-cost-of-power-read.mjs [tables dir]
import fs from "node:fs";
import path from "node:path";

const A = await import("../lib/datacenter/answers.ts");
const LA = await import("../app/cost-of-power/LoadAnswers.tsx");
const LL = await import("../lib/largeloadrules.ts");
const { LARGE_LOAD } = await import("../lib/sitingdata.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"));
const read = (...p) => fs.readFileSync(path.join(here, "..", ...p), "utf-8");

// ---- row 6, the arithmetic: the months of the twelve with no intensity are named, and the rate is unchanged
const l12 = ["2025-11", "2025-12", "2026-01"];
const energy = (m) => ({ m, energy: 744 });
const months = { flat: l12.map(energy), flex: l12.map(energy), shift: l12.map(energy) };
const c = A.l12Carbon([{ ts_utc: "2025-12-01T00:00:00Z", value: 200 }], months, l12);
ok(c.flat.kgPerMwh === 200 && c.flat.months === 1 && c.flat.of === 3 && JSON.stringify(c.flat.left) === JSON.stringify(["2025-11", "2026-01"]), "row 6: l12Carbon names the two months it leaves out and keeps the rate of the month held");
ok(LA.monthList(["2025-11", "2026-01", "2026-10"]) === "November 2025, January 2026 and October 2026" && LA.monthList(["2025-12"]) === "December 2025", "row 6: the months are written by name");

// ---- the page's source holds each fix where it is drawn
const page = read("app", "cost-of-power", "page.tsx"), answers = read("app", "cost-of-power", "LoadAnswers.tsx");
ok(page.includes("<BlankGrid asked={q.grid}") && page.includes("#${RULES_ANCHOR}`} data-blank-grid-rules={id}"), "row 12: the line for a grid the page prices nowhere is drawn under the box and links the All grids tab's rules");
ok(page.includes('data-saved-split="1"') && page.includes("is the lower price on the") && page.includes("MWh not bought, at the flat load's"), "row 3: the dollars the flexibility saves are split on hover");
ok(page.includes('data-cp-local="1"'), "row 11: each four-peak interval gives the grid's standard time beside UTC");
ok(answers.includes("data-carbon-left=") && answers.includes('data-carbon-grid-mean="1">against <N pre={f.pre} stat="co2:window:grid"'), "rows 6 and 7: the carbon card names the months left out, and the grid's mean is the sentence's key");
ok(answers.includes('data-answer-b-same-grid="1"'), "row 9: B at another site of the same grid is told the section is the grid's");

// ---- the page drawn, on the warehouse's table files
const dir = process.argv[2] ?? process.env.ERW_TABLES ?? path.join(here, "..", "..", "..", "erw", "warehouse", "output");
const need = ["carbon_intensity_monthly", "carbon_intensity_hourly", "scarcity_hours_by_grid", "ercot_4cp_intervals"];
if (!need.every((t) => fs.existsSync(path.join(dir, `${t}.csv`)))) console.log(`skip the drawn cases: the table files are not in ${dir}`);
else {
  const { drawer } = await import("./cost-of-power-read.mjs");
  const { draw } = await drawer(dir);
  const attr = (html, name) => (html.match(new RegExp(`<[^>]*${name}[^>]*>([\\s\\S]*?)</`)) ?? ["", ""])[1];
  const stat = (html, s) => ent((html.match(new RegExp(`data-stat="${s}"[^>]*>([^<]*)<`)) ?? ["", ""])[1]);

  // case 1: Abilene, the West load zone, 300 MW flat in real time: the headline is what it was
  const c1 = await draw({ grid: "ercot", region: "LZ_WEST", mw: "300", run: "flat", buy: "rt" });
  ok(stat(c1, "l12_per") === "35.35", `case 1: the flat load's last twelve months at LZ_WEST, real time, is USD ${stat(c1, "l12_per")} per MWh (35.35 before the read)`);
  ok(!c1.includes("data-blank-grid=") && !c1.includes('data-saved-split="1"'), "case 1: a flat load in ERCOT draws neither the blank grid's line nor the split");

  // row 3: off in its dearest 15 percent of hours
  const c1f = await draw({ grid: "ercot", region: "LZ_WEST", mw: "300", run: "share", pct: "15", buy: "rt" });
  const split = ent((c1f.match(/data-saved-split="1"[\s\S]*?title="([^"]*)"/) ?? ["", ""])[1]);
  ok(split.includes("is the lower price on the 2,226,900 MWh bought (USD 9.61 per MWh)") && split.includes("is the 401,100 MWh not bought, at the flat load's USD 35.35 per MWh"), `row 3: the split names the MWh bought and not bought: "${split.slice(0, 160)}..."`);

  // row 11: case 2, the four peaks' intervals in Central standard time
  const c2 = (await draw({ grid: "ercot", region: "LZ_WEST", mw: "300", run: "hours", n: "50", buy: "rt", cp: "1" })).replace(/<!-- -->/g, "");
  ok(c2.includes('06-19 21:45 UTC (<span data-cp-local="1">15:45 US Central standard time</span>)'), "row 11: summer 2025's June interval reads 21:45 UTC (15:45 US Central standard time)");

  // row 9: case 3, North against West: B's line under "How soon?"
  const c3 = (await draw({ grid: "ercot", region: "LZ_NORTH", mw: "300", run: "flat", buy: "rt", bsite: "ercot:LZ_WEST" })).replace(/<!-- -->/g, "");
  ok(c3.includes('data-answer-b-same-grid="1"') && ent(attr(c3, 'data-answer-b-same-grid="1"')).includes("is in the same grid: every figure here is ERCOT"), "row 9: case 3 says B's site is in the same grid and the section is ERCOT's");

  // rows 6 and 7: case 4, California: the months the twelve-month carbon leaves out are named
  const c4 = await draw({ grid: "caiso", region: "TH_SP15_GEN-APND", mw: "300", run: "flat", buy: "rt", bsite: "caiso:TH_NP15_GEN-APND" });
  const left = (c4.match(/data-carbon-left="(\d+)"[^>]*>([^<]*)</) ?? []);
  ok(left.length === 3 && Number(left[1]) >= 1 && /left out: [A-Z][a-z]+ 20\d\d/.test(ent(left[2])), `row 6: case 4 names the ${left[1]} months left out: "${ent(left[2] ?? "").slice(0, 200)}"`);
  const means = [...c4.matchAll(/data-check="dc\|[^"]*\|co2:window:grid" data-raw="([^"]+)"/g)].map((m) => m[1]);
  ok(means.length >= 2 && new Set(means).size === 1, `row 7: the grid's hourly mean is one key, drawn ${means.length} times with one value`);
  ok(!/against 1\d\d<\/span>/.test(c4), "row 7: the card no longer writes the grid's mean as a whole number");

  // row 12: case 5, Loudoun County: an address naming PJM
  const c5 = await draw({ grid: "pjm", region: "DOM", mw: "300" });
  const k = LL.lines(LARGE_LOAD).filter((l) => l.grid === "pjm").length;
  const blank = ent((c5.match(/<p[^>]*data-blank-grid="pjm"[^>]*>([\s\S]*?)<\/p>/) ?? ["", ""])[1].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).replace(/\s+/g, " ");
  ok(blank.includes("PJM's prices are not shown on this page: licensed source needed.") && blank.includes("The rules in motion under \"How soon?\" are PJM's; every other figure is ERCOT's."), `row 12: case 5 says why PJM is not priced and whose figures are drawn: "${blank.slice(0, 160)}"`);
  ok(k > 0 && c5.includes(`href="/cost-of-power?view=allgrids&amp;rgrid=pjm#large-load-rules"`) && blank.includes(`${k} rules read in PJM`), `row 12: and links the ${k} rules read in PJM on the All grids tab`);
}

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
