// Session 11402: /forecast drawn to HTML with the site's own code from main's real page files (read only), Texas demand
// and price; prints the "behind" line if drawn, and writes the visible text. Run from site/:
//   node --import ./scripts/events-page-register.mjs ../runs/c770/s11402/draw2.mjs
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const SITE = process.cwd();
const req = createRequire(path.join(SITE, "package.json"));
const { createElement: h } = await import(pathToFileURL(req.resolve("react")).href);
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
process.env.ERW_PREDICT_DIR = path.join(SITE, "data", "predict");
const { ForecastView } = await import(pathToFileURL(path.join(SITE, "app", "forecast", "view.tsx")).href);
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ");
const out = path.resolve(SITE, "..", "runs", "c770", "s11402", "out");
fs.mkdirSync(out, { recursive: true });
for (const [name, query] of [["tex_demand", {}], ["tex_price", { s: "price" }], ["aeci_demand", { a: "ba-aeci" }]]) {
  const html = renderToStaticMarkup(h(ForecastView, { query }));
  fs.writeFileSync(path.join(out, `draw2_${name}.txt`), text(html));
  const i = html.indexOf('data-fc-behind="a"');
  const line = i < 0 ? "none" : text(html.slice(html.indexOf(">", i) + 1, html.indexOf("</p>", i))).trim();
  console.log(name, "| behind line:", line, "| bytes", html.length);
}
process.exitCode = 0;
