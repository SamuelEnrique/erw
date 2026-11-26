// Energy Research Warehouse (ERW) site, session 10218 (docs/reviews/prices-model-audit-2026-11-26.md, finding 1):
// /prices/compare drawn to HTML by its own page function on the site's own file, no build, no network; prints one line
// of JSON per view asked: the page's words (tags removed) and its marked figures (data-n). Used by
// tests/test_audit_prices_1.py.
//   node --import ./scripts/tsx-register.mjs scripts/audit-prices-1-draw.mjs [query JSON ...]
import { register } from "node:module";
import { renderToStaticMarkup } from "react-dom/server";

register("./font-stub-loader.mjs", import.meta.url);
const { default: Compare } = await import("../app/prices/compare/page.tsx");
const unesc = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const views = process.argv.slice(2).length ? process.argv.slice(2).map((q) => JSON.parse(q)) : [{}];
for (const q of views) {
  const html = renderToStaticMarkup(await Compare({ searchParams: Promise.resolve(q) }));
  const text = unesc(html.replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ");
  const marked = Object.fromEntries([...html.matchAll(/<span data-n="([^"]+)">([^<]*)<\/span>/g)].map((x) => [unesc(x[1]), x[2]]));
  const titles = [...html.matchAll(/title="([^"]*)"/g)].map((x) => unesc(x[1]));
  console.log(JSON.stringify({ q, text, marked, titles, emDashes: html.split(String.fromCharCode(0x2014)).length - 1 }));
}
