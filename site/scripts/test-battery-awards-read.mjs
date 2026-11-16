// Energy Research Warehouse (ERW) site, session 7514 (chain 304, part B): /cost-of-power/battery/awards read as a
// lender's analyst reads it, for five cases (docs/reviews/battery-awards-read-2026-11-16.md). The whole page is drawn
// to HTML by its own function (scripts/battery-awards-page.mjs), its reads answered from the public rows committed
// beside the replication (replication/battery_awards/monthly_rows.csv, and inventory_rows.csv for the EIA's count), and
// each site fault the read found is held here as fixed: the row numbers are the review's. It also holds the page to
// the battery page's own file on the one figure the two share. Real rows; no server, no network, no click.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-battery-awards-read.mjs
import fs from "node:fs";
import { drawPage, pageText } from "./battery-awards-page.mjs";

const A = await import("../lib/storageawards.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const file = (...p) => fs.readFileSync(new URL(["..", ...p].join("/"), import.meta.url), "utf-8");
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");

// the committed public rows, by table
const held = new Map();
for (const name of ["monthly_rows.csv", "inventory_rows.csv"]) {
  const lines = file("..", "replication", "battery_awards", name).split(/\r?\n/).filter(Boolean);
  for (const line of lines.slice(1)) {
    const c = line.split(",");
    if (!held.has(c[0])) held.set(c[0], []);
    held.get(c[0]).push({ entity: c[1], variable: c[2], ts_utc: c[3], value: c[4] });
  }
}
const rowsOf = (table) => held.get(table) ?? null;
const { html, asked } = await drawPage(rowsOf);
const text = pageText(html);
const lines = text.split("\n");

ok(asked.length === 7 && asked.every((a) => !a.endsWith(": 0 rows") && !a.endsWith("not answered")), `the page makes its seven reads and each is answered from the committed rows (${asked.length})`);
ok(text.includes("In July 2026, ERCOT's disclosure lists 332 storage resources with 21,365 MW between them; their day-ahead awards came to USD 0.68 per kW for the month, 0.53 from energy net of charging and 0.15 from ancillary services."),
  "case 1: the page's sentence for July 2026, as it was");

// ---- row 1 (case 1): a month's ancillary award by service, on the hover of the month's ancillary cell
const fleet = held.get(A.TABLE).filter((r) => r.entity === A.ENTITY), model = held.get(A.MODEL_TABLE).filter((r) => r.entity === A.MODEL_ENTITY);
const ms = A.monthsOf(fleet, model);
const tipOf = (m) => ent((html.match(new RegExp(`data-awards-services="${m}" title="([^"]*)"`)) ?? ["", ""])[1]);
ok(ms.length === 9 && ms.every((r) => tipOf(r.m) !== "" && tipOf(r.m) === A.servicesOf(r)), `row 1: each of the ${ms.length} months' ancillary cells carries its five services on hover`);
ok(tipOf("2026-07").startsWith("July 2026, USD per kW awarded day-ahead: Regulation Up 0.01, Regulation Down 0.01, Responsive Reserve 0.02, ECRS (ERCOT Contingency Reserve Service) 0.02, Non-Spin 0.09; ancillary services are 22 percent of the month's 0.68.")
  && tipOf("2026-07").includes("ERCOT, 60-Day DAM Disclosure, NP3-966-ER"), "row 1: July 2026 by service, with the ancillary share of the month and the source document");
ok(ms.every((r) => Math.abs(A.PRODUCTS.reduce((a, p) => a + r.products[p.key], 0) - r.ancillary) < 0.01), "row 1: in every month the five services add up to the month's ancillary figure (inside a cent per MW)");
const noService = A.monthsOf(fleet.filter((r) => r.variable !== "revenue_nspin_usd_per_mw"), model);
ok(noService.every((r) => A.servicesOf(r) === null), "row 1: a month that lacks one of the five has no hover, and no service is filled in");

// ---- row 2 (cases 1 and 2): the five services together, and the battery page's line for the same months
const beside = JSON.parse(file("data", "battery_awards_beside.json")).cases.dayahead_2h;
const rawOf = (attr, key) => Number((html.match(new RegExp(`${attr}="${key}" data-offers-raw="([^"]+)"`)) ?? ["", "NaN"])[1]);
const fiveAwards = rawOf("data-offers-five", "awards"), fiveModel = rawOf("data-offers-five", "model");
const perMonthAwards = rawOf("data-offers-five-per-month", "awards"), perMonthModel = rawOf("data-offers-five-per-month", "model");
const offersMonths = (html.match(/data-offers-months="([^"]+)"/) ?? ["", ""])[1].split(",");
ok(lines.some((l) => l.startsWith("The five together | | | | | 2.78 | 15.66 | 12.88 |")), "row 2: the services table ends with the five together: awards, the model's and the gap, the shares left empty");
ok(offersMonths.length === beside.months && offersMonths[0] === beside.first && offersMonths.at(-1) === beside.last, `row 2: the months are the battery page's (${beside.first} to ${beside.last}, ${beside.months})`);
ok(Math.abs(perMonthAwards - beside.fleet) < 0.0005 && Math.abs(perMonthModel - beside.model) < 0.0005 && Math.abs(fiveModel / fiveAwards - beside.ratio) < 0.005,
  `row 2: per kW a month the two pages agree: awards ${perMonthAwards.toFixed(4)} and ${beside.fleet}, the model's ${perMonthModel.toFixed(4)} and ${beside.model}, the ratio ${(fiveModel / fiveAwards).toFixed(2)} and ${beside.ratio}`);
ok(text.includes("Per kW a month that is USD 0.40 against USD 2.24 , the model's 5.64 times the awards.") && text.includes("this line is ancillary services alone"), "row 2: the sentence gives the two per kW a month and says it is ancillary services alone");
ok(html.includes('href="/cost-of-power/battery?dur=2&amp;strat=dayahead"'), "row 2: the link opens the battery page on the case this page sets beside the awards (2 hours, the day-ahead schedule)");

// ---- row 3: a service named by its initials says its name on hover, in both tables
ok((html.match(/<abbr title="ERCOT Contingency Reserve Service">ECRS<\/abbr>/g) ?? []).length === 2 && /data-offers-service="ecrs"><abbr/.test(html) && /data-rt-service="ecrs"><abbr/.test(html),
  "row 3: ECRS carries its full name on hover in the offers table and in the real-time table");

// ---- row 4 (case 3): where the page stops for a reader with two nodes in hand, and where the site goes on
const further = ent((html.match(/<p data-rt-nodes-further="1">([\s\S]*?)<\/p>/) ?? ["", ""])[1]);
ok(further.includes("No settlement point is named on this page") && further.includes("the 293 points") && further.includes("21 days measured here") && further.includes("ercot_storage_node_basis"),
  "row 4: the node part says it names no point, and names the table that holds each point's own 21 days");
ok(further.includes('href="/cost-of-power?view=allgrids&rows=nodes"') && further.includes('href="/cost-of-power/battery"'), "row 4: it links the ERCOT node list of the All grids tab and the battery page");
const nodes = JSON.parse(file("data", "siting", "nodes.json"));
const names = JSON.stringify(nodes);
ok(names.includes('"AZURE_RN"') && names.includes('"KNAPP_RN"'), "row 4: the node list it links holds the case's two points by ERCOT's names (AZURE_RN, KNAPP_RN)");
ok(text.includes("It is 21 days of one autumn.") && text.includes("it is not applied to any figure above"), "row 4: the part's own caution is kept");

// ---- row 5: the fleet's size here and on the storage page, side by side on the MW line's hover
const tip = lines.find((l) => l.startsWith("[tip] The storage page")) ?? "";
ok(tip.includes("For ERCOT in July 2026 it lists 18,070 MW in 257 generators, holding 1.65 MWh per MW.") && tip.includes("ERCOT's file lists 21,365 MW in 332 resources, 3,296 MW more")
  && tip.includes("each per kW figure of July 2026 would be 18 percent higher"), "row 5: the hover sets the EIA's 18,070 MW beside the 21,365 MW here, for the month of the page's sentence");
ok(tip.includes("EIA, Form EIA-860M, as the table storage_buildout_monthly holds it") && tip.includes("ERCOT, 60-Day DAM Disclosure (NP3-966-ER), the column HSL"), "row 5: each count carries its source document");
const eia = A.inventoryOf(held.get(A.INVENTORY_TABLE), "2026-07"), july = ms.find((r) => r.m === "2026-07");
ok(eia && Math.abs(eia.mw - 18069.6) < 1e-6 && eia.units === 257 && Math.abs(july.mw - eia.mw - Number((html.match(/data-awards-inventory-diff="([^"]+)"/) ?? ["", "NaN"])[1])) < 1e-6, "row 5: the difference drawn is the two tables' rows, as held");
ok(html.includes('aria-describedby="tip-awards-mw"') && (html.match(/ id="tip-awards-mw"/g) ?? []).length === 1, "row 5: the tip has its one target");
// the EIA's table not readable: the hover says so, and every other line of the page is as it is with it
const without = await drawPage((t) => (t === A.INVENTORY_TABLE ? null : rowsOf(t)));
const linesWithout = pageText(without.html).split("\n");
const tipWithout = linesWithout.find((l) => l.startsWith("[tip] The storage page")) ?? "";
ok(tipWithout.includes("Its figure could not be read here") && !/\d{2},\d{3} MW/.test(tipWithout), "row 5: when the EIA's table cannot be read the hover says so and draws no figure of it");
ok(linesWithout.length === lines.length && lines.every((l, i) => l === linesWithout[i] || l.startsWith("[tip] The storage page")), "row 5: and every other line of the page is unchanged");
ok(A.inventoryOf(held.get(A.INVENTORY_TABLE), "2027-01") === null, "row 5: a month the EIA's table does not hold gives no figure");

// ---- the page drops nothing it had: every figure session 7505's replication found on the page is on it still
const fig = JSON.parse(file("..", "replication", "battery_awards", "page_figures.json"));
const plain = text.replace(/\[title: [^\]]*\]/g, "");
const lost = Object.entries(fig.figures).filter(([, shown]) => !plain.includes(String(shown)));
ok(Object.keys(fig.figures).length >= 300 && lost.length === 0, `every one of the ${Object.keys(fig.figures).length} figures of page_figures.json is on the drawn page${lost.length ? `; lost: ${lost.slice(0, 5).map(([k]) => k).join(", ")}` : ""}`);
for (const kept of ["What this is not.", "What is counted", "By month", "By year", "Why the two differ", "Where the gap comes from: what was offered day-ahead", "The real-time side: what the fleet did after the day-ahead market closed",
  "Do not add the last column up.", "It is not a forecast.", "What the offers still cannot show", "Decisions on this page (15)"]) ok(text.includes(kept), `the page keeps what it had: ${kept}`);

// ---- the page standard
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
ok(!dash.some((c) => html.includes(c)), "no em dash and no en dash on the drawn page");
const added = [tip, further, tipOf("2026-07"), lines.find((l) => l.startsWith("The five together, over")) ?? ""].join(" ");
ok(!/\b(should|recommend|we advise|best choice|better node|prefer)\b/i.test(added), "what this session added states facts and takes no view");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
