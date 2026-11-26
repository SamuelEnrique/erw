// Session 10218: /prices/compare drawn to HTML with the site's own page function on the site's own file, no build.
// Run from site/:  node --import ./scripts/tsx-register.mjs ../runs/c10218/draw_compare.mjs <out json>
// Four views: the default; the default with A = ERCOT West hub and B = ERCOT West load zone; the month; real time.
import fs from "node:fs";
import path from "node:path";
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
register(pathToFileURL(path.join(site, "scripts", "font-stub-loader.mjs")).href, pathToFileURL(path.join(site, "scripts", "x.mjs")).href);
const { default: Compare } = await import(pathToFileURL(path.join(site, "app", "prices", "compare", "page.tsx")).href);
const unesc = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const text = (html) => unesc(html.replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
const VIEWS = { default: {}, ab: { a: "ercot:HB_WEST", b: "ercot:LZ_WEST" }, month: { period: "month" }, rtm: { market: "rtm" } };
const out = {};
for (const [k, q] of Object.entries(VIEWS)) {
  const html = renderToStaticMarkup(await Compare({ searchParams: Promise.resolve(q) }));
  const marked = Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [unesc(x[1]), x[2]]));
  const bars = [...html.matchAll(/<g data-bar="([^"]+)"/g)].map((x) => unesc(x[1]));
  const titles = [...new Set([...html.matchAll(/title="([^"]*)"/g)].map((x) => unesc(x[1])))];
  out[k] = { q, marked, bars, titles, text: text(html), emDashes: html.split(String.fromCharCode(0x2014)).length - 1 };
}
fs.writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
console.log(`written ${process.argv[2]}: ${Object.entries(out).map(([k, v]) => `${k} ${Object.keys(v.marked).length} marked`).join("; ")}`);
