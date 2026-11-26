// Energy Research Warehouse (ERW) site, session 10218 (docs/reviews/prices-model-audit-2026-11-26.md, finding 5): the
// Grid map's price controls (components/grid/MapPrice.tsx, PriceControls) drawn to HTML with the site's own component on
// the site's own file (data/regions/prices_map.json), for each measure, no build, no network. Prints one line of JSON
// per measure: the legend's words and the hover line of each shown area.
//   node --import ./scripts/tsx-register.mjs scripts/audit-prices-5-draw.mjs [prices_map.json]
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const M = await import("../components/grid/MapPrice.tsx");
const file = JSON.parse(fs.readFileSync(process.argv[2] ?? new URL("../data/regions/prices_map.json", import.meta.url), "utf-8"));
const unesc = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
for (const [k] of M.PRICE_MEASURES) {
  const html = renderToStaticMarkup(h(M.PriceControls, { on: true, setOn: () => {}, measure: k, setMeasure: () => {}, m: file }));
  const legend = unesc((html.match(/data-map-price-range="[^"]*">([\s\S]*?)<\/span><details/) ?? [, ""])[1].replace(/<[^>]+>/g, "")).replace(/\s+/g, " ").trim();
  const hovers = Object.fromEntries(Object.keys(file.bas).map((id) => [id, M.priceLine(file, id, k)]));
  console.log(JSON.stringify({ measure: k, legend, hovers, emDashes: html.split(String.fromCharCode(0x2014)).length - 1 }));
}
