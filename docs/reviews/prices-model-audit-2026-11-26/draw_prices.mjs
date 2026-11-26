// Session 10218: /prices (first tab) and /prices/<hub> drawn by the pages' own functions (site/scripts/prices-read-page.mjs,
// session 7539's stand-in for the live set) on this machine's warehouse tables, at a fixed render time. No network.
// Run from site/:
//   node --import ./scripts/prices-read-register.mjs ../runs/c10218/draw_prices.mjs <tables dir> <render ISO> <out dir>
// latest_prices is not a warehouse table: it is made here as the newest real-time interval at or before the render time
// of each public hub (the variable of the table it came from). For the held grids (NYISO, ISO-NE, MISO), whose rows the
// connector writes to latest_prices with license "public" (warehouse/connectors/latest_prices.py rows_for), one stand-in
// row each, value 0, marked as a stand-in: what the page draws for a held grid that latest_prices holds. No held grid's
// price is read from any table.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const site = process.cwd();
const { draw } = await import(pathToFileURL(path.join(site, "scripts", "prices-read-page.mjs")).href);
const { tableRows, pageText } = await import(pathToFileURL(path.join(site, "scripts", "battery-awards-page.mjs")).href);
const [dir, at, out] = process.argv.slice(2);
const now = Date.parse(at);
const PUBLIC = ["ercot:", "caiso:", "spp:"];
const pub = (r) => PUBLIC.some((p) => r.entity.startsWith(p));
const rt = tableRows(path.join(dir, "iso_rtm_hub_prices.csv")).filter((r) => pub(r) && Date.parse(r.ts_utc) <= now);
const da = tableRows(path.join(dir, "iso_dam_hub_prices.csv")).filter((r) => pub(r) && Date.parse(r.ts_utc) <= now + 86_400_000);
const newest = new Map();
for (const r of rt) { const o = newest.get(r.entity); if (!o || r.ts_utc > o.ts_utc) newest.set(r.entity, r); }
const stand = (e, ts, v) => ({ entity: e, variable: "lmp_rtm_5min", ts_utc: ts, value: "0", unit: "USD/MWh", license: "public", source: "stand-in" });
const latest = [...newest.values()].map((r) => ({ ...r, unit: "USD/MWh", license: "public" }))
  .concat([stand("nyiso:N.Y.C.", new Date(now - 900_000).toISOString().replace(/\.\d{3}Z$/, "Z")), stand("isone:.H.INTERNAL_HUB", new Date(now - 900_000).toISOString().replace(/\.\d{3}Z$/, "Z")),
    stand("miso:INDIANA.HUB", "2026-10-04T03:55:00Z")]);
const rowsOf = (t) => (t === "iso_rtm_hub_prices" ? rt : t === "iso_dam_hub_prices" ? da : t === "latest_prices" ? latest : []);
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, "latest_made.json"), JSON.stringify(latest.filter((r) => r.source !== "stand-in")));
for (const e of [null, "ercot:HB_HUBAVG", "ercot:HB_WEST", "caiso:TH_SP15_GEN-APND", "spp:SPPNORTH_HUB", "nyiso:N.Y.C.", "miso:INDIANA.HUB"]) {
  const { html, asked } = await draw(rowsOf, now, e);
  const name = e ? e.replace(/[^\w.-]+/g, "_") : "prices";
  fs.writeFileSync(path.join(out, `${name}.html`), html);
  fs.writeFileSync(path.join(out, `${name}.txt`), pageText(html) + "\n\n[reads]\n" + asked.join("\n") + "\n");
  console.log(`${name}: ${html.length} bytes, ${asked.length} reads, em dashes ${html.split(String.fromCharCode(0x2014)).length - 1}`);
}
