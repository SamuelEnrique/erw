// Energy Research Warehouse (ERW) site, session 7539 (chain 304, part C): /prices and /prices/<hub> read as a fund
// analyst or a merchant developer comparing hub prices, their peaks and their spread across grids and months
// (docs/reviews/prices-read-2026-11-16.md). Both pages are drawn to HTML by their own functions
// (scripts/prices-read-page.mjs), their reads answered from the public rows committed beside this test
// (scripts/prices-read-rows.csv: the live set as the pages read it at 23:20 UTC on 16 November 2026, ERCOT, CAISO and
// SPP only), at that render time. Each site row the read fixed is held here; the row numbers are the review's. It also
// holds that the upgrade drops no figure the pages drew and that nothing committed holds a license-held grid's row.
// Real rows; no server, no network, no click.
//   node --import ./scripts/prices-read-register.mjs scripts/test-prices-read.mjs
import fs from "node:fs";
import { draw } from "./prices-read-page.mjs";

const H = await import("../lib/pricehub.ts");
const { licenseHeldGrids } = await import("../lib/license.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const file = (...p) => fs.readFileSync(new URL(["..", ...p].join("/"), import.meta.url), "utf-8");
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (html) => ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const titles = (html) => [...html.matchAll(/title="([^"]*)"/g)].map((m) => ent(m[1]));

// the committed public rows, by table
const byTable = new Map();
const csvText = file("scripts", "prices-read-rows.csv");
for (const line of csvText.split(/\r?\n/).filter((l) => l && !l.startsWith("#")).slice(1)) {
  const [t, entity, variable, ts_utc, value] = line.split(",");
  if (!byTable.has(t)) byTable.set(t, []);
  byTable.get(t).push({ entity, variable, ts_utc, value });
}
const rowsOf = (t) => byTable.get(t) ?? null;
const NOW = Date.parse("2026-11-16T23:20:00Z");

// ---- nothing committed holds a held grid's row (the repository is public)
const heldPrefixes = licenseHeldGrids().map((g) => `${g}:`);
const allRows = [...byTable.values()].flat();
ok(heldPrefixes.length >= 3 && allRows.length === 7394 && allRows.every((r) => !heldPrefixes.some((p) => r.entity.startsWith(p))),
  `the committed rows (${allRows.length}) hold no row of a held grid (${heldPrefixes.join(" ")})`);

// ---- the first tab
const { html: page, asked } = await draw(rowsOf, NOW, null);
const pw = words(page);
ok(asked.filter((a) => a.startsWith("latest_prices") || a.startsWith("iso_dam_hub_prices")).length === 4, "the first tab reads latest_prices once and iso_dam_hub_prices for ERCOT, CAISO and SPP");
const checks = [...page.matchAll(/data-check="([^"]+)"/g)].map((m) => ent(m[1]));
ok(checks.length === 14 && checks.filter((c) => c.startsWith("latest_prices|")).length === 11 && checks.filter((c) => c.startsWith("series|iso_dam_hub_prices|")).length === 3,
  `nothing dropped: the 11 real-time figures and the 3 day-ahead figures of the hubs whose rows are given are drawn as checked numbers (${checks.length})`);
ok(pw.includes("ERCOT") && /HB_HUBAVG main 71\.34 .* 71\.41/.test(pw), "the ERCOT Hub Average's row as it was: 71.34 real time, 71.41 day-ahead this hour");

// row 1: a held grid is named with "license needed" in its price cells, and is not said to have no data
for (const iso of ["NYISO", "MISO", "ISO-NE"]) {
  const sec = (page.match(new RegExp(`<h2[^>]*>${iso}</h2>([\\s\\S]*?)</section>`)) ?? ["", ""])[1];
  ok(sec.includes(`data-held-grid="${iso}"`) && (sec.match(/>license needed</g) ?? []).length === 2 && !/no data/.test(words(sec)) && /the publisher&#x27;s own page asks for permission/.test(sec),
    `row 1: ${iso}'s section names its main hub or zone with two cells "license needed", the publisher's words on hover, and no "no data"`);
}
ok(page.includes('title="NYISO, New York City zone"') && page.includes('title="ISO-NE, Internal Hub"'), "row 1: the held grids' main zone and hub by name on hover");

// row 6: the interval column in words, the code on hover; the hubs' names on hover
ok(pw.includes("2026-11-16 22:45 (15-minute settlement point price)") && pw.includes("2026-11-16 23:15 (5-minute locational price)") && !/\((spp_rtm|lmp_rtm_5min)\)/.test(pw),
  "row 6: the interval column says each operator's interval in words, not the variable's code");
ok(titles(page).includes("spp_rtm: 15-minute settlement point price") && page.includes('title="ERCOT, West hub"') && page.includes('title="CAISO, SP15 hub (south)"'),
  "row 6: the code on hover; each hub's name on the hover of its link");

// row 8: the page for a month or twelve months of every hub
ok(/href="\/prices\/compare"[^>]*data-compare-link="1"/.test(page) && pw.includes("Each hub over the last whole month and the last twelve months, side by side: where power is cheap"),
  "row 8: the first tab links /prices/compare in its lead");

// row 9: the site's index line for /prices promises only what the page draws
const pagesTs = file("lib", "pages.ts");
const line = (pagesTs.match(/href: "\/prices", label: "Prices", line: "([^"]*)", tables: "([^"]*)"/) ?? ["", "", ""]);
ok(line[1] !== "" && !/Henry Hub|WTI|Brent/.test(line[1]) && !line[2].includes("eia_fuel_spot_prices") && line[1].includes("last 30 days"),
  "row 9: the index line names no Henry Hub, WTI or Brent and no eia_fuel_spot_prices: the page draws none");

// ---- a hub's page: ERCOT Hub Average
const hub = await draw(rowsOf, NOW, "ercot:HB_HUBAVG");
const hw = words(hub.html), ht = titles(hub.html);
const rt = byTable.get("iso_rtm_hub_prices").filter((r) => r.entity === "ercot:HB_HUBAVG").map((r) => ({ ...r, value: Number(r.value) }));
const da = byTable.get("iso_dam_hub_prices").filter((r) => r.entity === "ercot:HB_HUBAVG").map((r) => ({ ...r, value: Number(r.value) }));
ok(rt.length === 2428 && da.length === 679, `the rows of case 4: ${rt.length} real-time intervals and ${da.length} day-ahead hours`);
ok(/Real time iso_rtm_hub_prices 2,428 of 2,812 -11\.33 35\.84 565\.21/.test(hw) && /Day-ahead iso_dam_hub_prices 679 of 727 5\.92 35\.85 161\.48/.test(hw),
  "nothing dropped: the min, mean and max of each market as they were, with the count now of the intervals due");

// rows 2 and 3: when the high and the low fell
ok(ht.includes("The highest interval starts 2026-11-12 04:00 UTC (Nov 11, 2026, 22:00 CST)") && hub.html.includes('data-at="2026-11-12T04:00:00+00:00"'),
  "rows 2 and 3: the real-time high of 565.21 says on hover that it fell at 22:00 Central on 11 November 2026");
const hi = rt.reduce((a, r) => (r.value > a.value ? r : a));
ok(hi.value === 565.21 && hi.ts_utc.startsWith("2026-11-12T04:00"), "rows 2 and 3: the high's time recomputed from the rows here");
ok(ht.includes("The lowest interval starts 2026-10-18 15:00 UTC (Oct 18, 2026, 10:00 CDT)"), "rows 2 and 3: the day-ahead low's hour on hover");

// row 4: the intervals held of those due, and the days with no row
ok(ht.some((t) => t.startsWith("2,428 of the 2,812 intervals from 2026-10-17 23:00 UTC to 2026-11-16 05:45 UTC at the table's step (PT15M). UTC days with no row: 2026-11-06, 2026-11-07, 2026-11-08.")),
  "row 4: the real-time count says 2,428 of 2,812 and names the three UTC days with no row");
ok(H.heldOf(rt, "PT15M").due === 2812 && H.heldOf(da, "PT1H").due === 727 && H.heldOf([], "PT1H") === null && H.heldOf(rt, "P1D") === null, "row 4: the count due, and none for no rows or a step it does not know");
ok((await draw(rowsOf, NOW, "caiso:TH_SP15_GEN-APND")).html.includes('data-held="2820/2820"'), "row 4: a hub with every interval held reads its count alone (CAISO SP15, 2,820)");

// row 5: real time less day-ahead over the hours both hold, recomputed here without the page's library
const hours = new Map();
for (const r of rt) { const h = r.ts_utc.slice(0, 13); hours.set(h, [...(hours.get(h) ?? []), r.value]); }
const diffs = da.filter((d) => (hours.get(d.ts_utc.slice(0, 13)) ?? []).length === 4).map((d) => hours.get(d.ts_utc.slice(0, 13)).reduce((a, b) => a + b, 0) / 4 - d.value);
const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
const naive = rt.reduce((a, r) => a + r.value, 0) / rt.length - da.reduce((a, r) => a + r.value, 0) / da.length;
ok(diffs.length === 607 && Math.abs(mean - 0.549) < 0.001 && Math.abs(naive - -0.0106) < 0.001, `row 5: over the 607 hours both hold real time is ${mean.toFixed(3)} above day-ahead; the two means' difference reads ${naive.toFixed(4)}`);
ok(/Real time less day-ahead the hours both hold 607 hours -100\.24 0\.55 281\.92/.test(hw) && hub.html.includes('data-dart="ercot:HB_HUBAVG"'), "row 5: the page's row reads 607 hours, low -100.24, mean 0.55, high 281.92");
ok(ht.some((t) => t.startsWith("Each hour's real-time price (the mean of its intervals, taken only when every interval of the hour is held) less the same hour's day-ahead price.")), "row 5: the row says on hover what it is and why the two means' difference is not it");
ok(H.realLessDayAhead(rt, [], "PT15M") === null && H.realLessDayAhead(rt.filter((r) => !r.ts_utc.endsWith(":15:00+00:00")), da, "PT15M") === null, "row 5: no row with no day-ahead, and no hour taken with an interval missing");

// row 6: the hub's name and the legend in words
ok(hw.includes("ERCOT, Hub Average , entity ercot:HB_HUBAVG") && hw.includes("Day-ahead, hourly settlement point price") && hw.includes("Real time, 15-minute settlement point price") && !/\((spp_rtm|spp_dam)\)/.test(hw),
  "row 6: the hub by name under its code, and the chart's legend in words");

// row 7: SPP's real time is not said to be absent from the warehouse
const spp = words((await draw(rowsOf, NOW, "spp:SPPNORTH_HUB")).html);
ok(!spp.includes("the ERW has no SPP real-time series table") && !spp.includes("no real-time series table for this ISO") && spp.includes("site/data/markets.json names no real-time table for SPP"),
  "row 7: the SPP hub's page says that markets.json names no real-time table for SPP, not that the warehouse has none");

// ---- ruling alternative 3 (wip/alt-prices-3, not a default on main), session 8401, browser row 362: at 390 px the page
// was 504 px wide, the table of A less B standing in no frame. Drawn with a second hub (no row of it is committed, so
// each row reads "no hour held by both"), the table stands inside its own scrolling frame, as every table of the page
const withB = (await draw(rowsOf, NOW, "ercot:HB_HUBAVG", "ercot:HB_WEST")).html;
ok(/<div class="overflow-x-auto"><table[^>]*data-ab-table="ercot:HB_WEST"/.test(withB) && (withB.match(/data-ab-row=/g) ?? []).length === 2,
  "browser row 362: the table of A less B is drawn inside a frame that scrolls sideways, with its two rows");
ok((withB.match(/<table\b/g) ?? []).length === 2 && (withB.match(/overflow-x-auto"><table\b/g) ?? []).length === 2, "browser row 362: no table of a hub's page stands outside a scrolling frame");
ok(!/data-ab-table/.test((await draw(rowsOf, NOW, "ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND")).html) && !/data-ab-table/.test(hub.html), "a hub of another grid, or none, draws no table of A less B");

console.log(`\n${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
