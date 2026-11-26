// Session 10231 (the explorers' audit): the components a words branch changes, drawn to HTML with the site's own code
// (no build, no server, no request), and their visible text written out, so the new words can be read as a visitor
// meets them: the peak premium's decisions block, the demand growth explorer's decisions block, and the source words of
// one figure of each explorer (lib/explore/source.ts, the hover every figure carries).
// node --import ./scripts/tsx-register.mjs ../runs/c10231/draw_words.mjs <out prefix>   (run from site/)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const React = await import(pathToFileURL(req.resolve("react")).href);
globalThis.fetch = async (url) => { throw new Error(`refused: ${url}`); };
const out = process.argv[2];
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const text = (h) => unq(h.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const peak = await import(pathToFileURL(path.join(site, "app", "explore", "ercot-peak-premium", "Decisions.tsx")).href);
const demand = await import(pathToFileURL(path.join(site, "app", "explore", "demand-growth", "Decisions.tsx")).href);
const source = await import(pathToFileURL(path.join(site, "lib", "explore", "source.ts")).href);
const parts = [];
for (const [name, C] of [["peak premium decisions", peak.PeakPremiumDecisions], ["demand growth decisions", demand.DemandGrowthDecisions]]) {
  const html = renderToStaticMarkup(React.createElement(C));
  fs.writeFileSync(`${out}_${name.replace(/ /g, "_")}.html`, html);
  parts.push(`== ${name}\n${text(html)}`);
}
parts.push("== source words of one figure of each explorer");
for (const k of ["series|ercot_peak_premium_annual|ercot:HB_HUBAVG|peak_iqr|2025-01-01T00:00:00Z", "series|eia930_demand_growth|eia930:ERCO|avg_demand_mw|2025-01-01T00:00:00Z", "series|iso_queue_statistics|caiso:queue_2023|positions_entered|2023-01-01T00:00:00Z"]) parts.push(source.sourceOf(k));
const all = parts.join("\n");
fs.writeFileSync(`${out}.txt`, all);
console.log(`drawn; ${all.length} characters; em dash: ${all.includes(String.fromCharCode(0x2014))}`);
