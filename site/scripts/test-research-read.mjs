// Energy Research Warehouse (ERW) site, session 7564: the Research page read as a fund analyst would read it
// (docs/reviews/research-read-2026-11-16.md, row 1). The finding cards as the site reads them (lib/findings.ts, on the
// site's own files in data/findings/) hold NYISO's and ISO-NE's figures in the why, the footnote and the charts, as
// their callouts already were; a card drawn to HTML by its own component carries none of them.
//   cd site && node --import ./scripts/tsx-register.mjs scripts/test-research-read.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const F = await import("../lib/findings.ts");
const H = await import("../lib/cardhold.ts");
const { FindingCard } = await import("../components/analysis/FindingCard.tsx");

let failed = 0;
const check = (ok, what) => { console.log(`${ok ? "ok  " : "FAIL"} ${what}`); if (!ok) failed++; };
const raw = (id) => JSON.parse(fs.readFileSync(new URL(`../data/findings/${id}.json`, import.meta.url), "utf-8"));

const held = H.heldGrids();
check(held.includes("nyiso") && held.includes("isone"), `NYISO and ISO-NE are held today (${held.join(", ")})`);

const peakRaw = raw("peak_hour_grids");
const peak = F.loadCard("peak_hour_grids");
check(peakRaw.why.includes("62.5") && !peak.why.includes("62.5") && !peak.why.includes("55.0 percent"), "peak hour: the why's NYISO and ISO-NE figures are out (62.5, 55.0 in the file)");
check(/sentences? with figures of (NYISO and ISO-NE|ISO-NE and NYISO) (is|are) held/.test(peak.why), `the why says what was held: ...${peak.why.slice(-120)}`);
check(peak.why.includes("In Texas it did") && peak.why.includes("24.9 to 71.0 percent"), "Texas's sentence and figures stay (24.9 to 71.0 percent)");
check(!peak.chart.panels.some((p) => p.grid === "nyiso" || p.grid === "isone") && peak.chart.panels.some((p) => p.grid === "ercot"), "the chart keeps ERCOT's panel and drops NYISO's and ISO-NE's");
check(["nyiso", "isone"].every((g) => peak.chart.placeholders.some((p) => p.grid === g && p.text.startsWith("license needed"))), "the chart names both in its placeholders, 'license needed'");

const gas = F.loadCard("gas_sets_price");
check(!gas.why.includes("18.6 to 5.5") && !gas.chart.series.some((s) => /NYISO|ISO-NE/.test(s.name)), "gas sets the price: ISO-NE's 18.6 to 5.5 and the held grids' bars are out");
check(gas.why.includes("Algonquin"), "a sentence naming ISO-NE with no figure stays (Algonquin)");

const lunch = F.loadCard("batteries_lunch_grids");
check(!lunch.why.includes("20.9x") && !lunch.why.includes("25.73"), "batteries' lunch: NYISO's 20.9x and its 25.73 per GW are out");

const rescue = F.loadCard("who_rescues_whom");
check(JSON.stringify(rescue) === JSON.stringify(raw("who_rescues_whom")), "a card with no held grid is unchanged (who rescues whom)");
check(F.loadCards().length === fs.readdirSync(new URL("../data/findings/", import.meta.url)).filter((f) => f.endsWith(".json") && f !== "catalogue.json").length, "every card still loads");

const html = renderToStaticMarkup(h(FindingCard, { card: peak, fold: true }));
check(!html.includes("62.5") && !html.includes("43.3"), "the card drawn to HTML prints neither of NYISO's two shares");
check(html.includes('data-placeholder="nyiso"') && html.includes('data-placeholder="isone"'), "it names NYISO and ISO-NE as held, beside MISO and PJM");

// row 3: the weekly chart's heading names an old week for what it is
const R = await import("../lib/research.ts");
check(R.isoWeekOf(new Date("2026-11-17T05:00:00Z")) === "2026-W47" && R.isoWeekOf(new Date("2026-11-08T23:00:00Z")) === "2026-W45" && R.isoWeekOf(new Date("2027-01-01T00:00:00Z")) === "2026-W53", "ISO weeks: 17 November 2026 is W47, 8 November W45, 1 January 2027 W53 of 2026");
check(R.weekChartTitle("2026-W45", new Date("2026-11-17T05:00:00Z")) === "The newest weekly chart, 2026-W45: none since", "on 17 November the W45 chart is 'the newest weekly chart', not this week's");
check(R.weekChartTitle("2026-W45", new Date("2026-11-10T12:00:00Z")) === "This week's chart, 2026-W45", "on the Tuesday after its Sunday it is this week's chart");
check(R.weekChartTitle(null) === "This week's chart", "no week: the plain heading");

console.log(failed ? `${failed} failed` : "all passed");
process.exitCode = failed ? 1 : 0;
