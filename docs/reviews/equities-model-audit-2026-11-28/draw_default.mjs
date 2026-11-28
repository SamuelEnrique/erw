// Audit of /equities, session 11403: the page as it opens (no address), drawn by the site's own code from the site's own
// files, without a build. Prints every number the page marks (data-n) and the text of a few places, so that the
// restatement (restate.py) can be set beside what the page prints. Run from site/:
//   node --import ./scripts/tsx-register.mjs ../runs/c770/s11403/draw_default.mjs
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { EquitiesView } = await import("../../../site/app/equities/view.tsx");
const html = renderToStaticMarkup(h(EquitiesView, { query: {} }));
const text = (s) => s.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
const out = [];
for (const m of html.matchAll(/data-n="([^"]+)"[^>]*>(.*?)<\/span>/g)) out.push(`${m[1]} = ${text(m[2])}`);
console.log(`html ${html.length} characters; numbers marked: ${out.length}`);
for (const x of out) console.log(`  ${x}`);
const count = /data-eq-count="([^"]+)"/.exec(html);
console.log(`companies counted: ${count ? count[1] : "none"}`);
const heads = [...html.matchAll(/data-eq-newest="([^"]+)"/g)].map((m) => m[1]);
console.log(`newest columns: ${heads.join(", ")}`);
// the prices table: each row's latest and moves, as text
const prices = /data-eq-prices="\d+"[\s\S]*?<\/table>/.exec(html);
if (prices) for (const row of prices[0].split("<tr").slice(2)) console.log(`  price row: ${text("<tr" + row).slice(0, 160)}`);
// the newest-period table and the default figure's headline
const filed = /data-eq-filed="\d+"[\s\S]*?<\/table>/.exec(html);
if (filed) for (const row of filed[0].split("<tr").slice(1)) console.log(`  filed row: ${text("<tr" + row).slice(0, 200)}`);
const firstRows = /data-eq-count[\s\S]*?<tbody>([\s\S]*?)<\/tbody>/.exec(html);
if (firstRows) for (const row of firstRows[1].split("<tr").slice(1, 4)) console.log(`  company row: ${text("<tr" + row).slice(0, 200)}`);
process.exitCode = 0;
