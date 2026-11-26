// Energy Research Warehouse (ERW) site, session 10218 (docs/reviews/prices-model-audit-2026-11-26.md, finding 6): a
// hub's page (/prices/<hub>) drawn by its own function (scripts/prices-read-page.mjs, session 7539's stand-in for the
// live set) on stand-in rows made for the test (every price 0): real time to the render time, day-ahead to the end of
// the next day, as the live set holds them once the next day's day-ahead is published. Prints one line of JSON: the
// page's words (tags removed, hovers kept as "[title: ...]"). No table is read and nothing is written.
//   node --import ./scripts/prices-read-register.mjs scripts/audit-prices-6-draw.mjs
import { draw } from "./prices-read-page.mjs";
import { pageText } from "./battery-awards-page.mjs";

const now = Date.parse("2026-11-12T18:00:00Z");
const iso = (t) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const rt = [], da = [];
for (let t = now - 2 * 86_400_000; t <= now; t += 900_000) rt.push({ entity: "ercot:HB_HUBAVG", variable: "spp_rtm", ts_utc: iso(t), value: "0" });
for (let t = now - 2 * 86_400_000; t < Date.parse("2026-11-14T06:00:00Z"); t += 3_600_000) da.push({ entity: "ercot:HB_HUBAVG", variable: "spp_dam", ts_utc: iso(t), value: "0" });
const rowsOf = (t) => (t === "iso_rtm_hub_prices" ? rt : t === "iso_dam_hub_prices" ? da : t === "latest_prices" ? [] : []);
const { html } = await draw(rowsOf, now, "ercot:HB_HUBAVG");
console.log(JSON.stringify({ text: pageText(html).replace(/\s+/g, " "), emDashes: html.split(String.fromCharCode(0x2014)).length - 1 }));
