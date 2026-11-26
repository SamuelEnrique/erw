// Energy Research Warehouse (ERW) site, session 10218 (docs/reviews/prices-model-audit-2026-11-26.md, finding 4):
// /prices (its first tab) and /prices/<hub> of the held grids drawn by the pages' own functions (scripts/prices-read-page.mjs,
// session 7539's stand-in for the live set), with latest_prices holding a row of each held grid, as the connector writes
// it (warehouse/connectors/latest_prices.py: NYISO and ISO-NE every 15 minutes with license "public"; MISO's last row of
// 4 October 2026 stays). Every price here is a stand-in, 0, made for the test; no table is read and nothing is written.
// Prints one line of JSON per page: its words (tags removed, hovers kept as "[title: ...]").
//   node --import ./scripts/prices-read-register.mjs scripts/audit-prices-4-draw.mjs
import { draw } from "./prices-read-page.mjs";
import { pageText } from "./battery-awards-page.mjs";

const now = Date.parse("2026-11-12T18:00:00Z");
const row = (entity, ts) => ({ entity, variable: "lmp_rtm_5min", ts_utc: ts, value: "0", unit: "USD/MWh", license: "public" });
const latest = [row("nyiso:N.Y.C.", "2026-11-12T17:45:00Z"), row("nyiso:WEST", "2026-11-12T17:45:00Z"), row("isone:.H.INTERNAL_HUB", "2026-11-12T17:45:00Z"),
  row("miso:INDIANA.HUB", "2026-10-04T03:55:00Z")];
const rowsOf = (t) => (t === "latest_prices" ? latest : []);
for (const e of [null, "nyiso:N.Y.C.", "miso:INDIANA.HUB"]) {
  const { html } = await draw(rowsOf, now, e);
  console.log(JSON.stringify({ page: e ?? "/prices", text: pageText(html).replace(/\s+/g, " "), heldGrids: [...html.matchAll(/data-held-grid="([^"]+)"/g)].map((m) => m[1]),
    heldMarkets: [...html.matchAll(/data-held-market="([^"]+)"/g)].map((m) => m[1]), emDashes: html.split(String.fromCharCode(0x2014)).length - 1 }));
}
