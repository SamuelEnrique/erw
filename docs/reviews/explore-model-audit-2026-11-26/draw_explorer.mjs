// Session 10231 (the explorers' audit): the ERCOT tab of /prices (where /explorer/ercot-peak-premium redirects) drawn
// to HTML with the site's own client component (app/explorer/ercot-peak-premium/Explorer.tsx) in its first state (no
// click), from the main copy's two tables. No build, no server, no request. Prints every checked figure (key, text)
// and the visible text, so the tab can be set beside /explore/ercot-peak-premium's default view.
// node --import ./scripts/tsx-register.mjs ../runs/c10231/draw_explorer.mjs <annual.csv> <monthly.csv> <out prefix>   (run from site/)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const React = await import(pathToFileURL(req.resolve("react")).href);
globalThis.fetch = async (url) => { throw new Error(`refused: ${url}`); };

function read(file) {
  const lines = fs.readFileSync(file, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const cols = lines[0].split(",");
  const ix = Object.fromEntries(cols.map((k, i) => [k, i]));
  return lines.slice(1).map((l) => { const c = l.split(","); return { e: c[ix.entity], v: c[ix.variable], t: c[ix.ts_utc].slice(0, 7), x: Number(c[ix.value]) }; });
}
const [annualFile, monthlyFile, out] = process.argv.slice(2);
const annual = read(annualFile);
const monthly = read(monthlyFile).filter((r) => ["peak_median", "midday_median", "overnight_median", "peak_iqr"].includes(r.v));
const { Explorer } = await import(pathToFileURL(path.join(site, "app", "explorer", "ercot-peak-premium", "Explorer.tsx")).href);
const html = renderToStaticMarkup(React.createElement(Explorer, { annual, monthly, monthlyError: null, citeAnnual: null, citeMonthly: null }));
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const text = (h) => unq(h.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const figs = [...html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)].map((m) => ({ key: unq(m[1]), raw: Number(m[2]), text: text(m[3]) }));
fs.writeFileSync(`${out}.html`, html);
fs.writeFileSync(`${out}.json`, JSON.stringify({ figures: figs, text: text(html) }, null, 1));
console.log(`${figs.length} checked figures; selected: ${(html.match(/<option[^>]*selected[^>]*>[^<]*/g) || []).join(" | ")}`);
