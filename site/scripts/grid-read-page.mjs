// Energy Research Warehouse (ERW) site, session 7565 (docs/reviews/grid-read-2026-11-16.md): draw /grid for a grid and a tab to text, by the page's own function, on the live set's public reads
// (the anon key only; no service key in the environment). Run from site/:
//   node --import ./scripts/grid-read-register.mjs scripts/grid-read-page.mjs <grid> <view> <out.txt>
import fs from "node:fs";
import { renderToReadableStream } from "react-dom/server.edge";

const [grid, view, out] = process.argv.slice(2);
const { default: GridPage } = await import("../app/grid/page.tsx");
const el = await GridPage({ searchParams: Promise.resolve({ grid, view }) });
const stream = await renderToReadableStream(el);
await stream.allReady;
const html = await new Response(stream).text();
const text = html
  .replace(/<script[\s\S]*?<\/script>/g, " ")
  .replace(/<(br|p|div|li|tr|h[1-6]|section|table|figcaption)[^>]*>/g, "\n")
  .replace(/<td[^>]*>/g, " | ")
  .replace(/title="([^"]*)"/g, (m, t) => ` [tip: ${t}] `)
  .replace(/<[^>]+>/g, " ")
  .replace(/&amp;/g, "&").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">")
  .replace(/[ \t]+/g, " ").replace(/\n\s*\n+/g, "\n");
fs.writeFileSync(out, text);
fs.writeFileSync(out.replace(/\.txt$/, ".html"), html);
console.log(`${grid} ${view}: ${html.length} characters of HTML, ${text.split("\n").length} lines of text`);
