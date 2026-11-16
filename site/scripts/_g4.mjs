// scratch (goal 4): draw the tab for an address's inputs and print rows' cells with their hovers
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
const { AllGridsView } = await import("../app/cost-of-power/AllGridsView.tsx");
const [query, out, want, tips] = process.argv.slice(2);
const html = renderToStaticMarkup(h(AllGridsView, { q: Object.fromEntries(new URLSearchParams(query)) }));
fs.writeFileSync(out, html);
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const strip = (s) => ent(s.replace(/<span role="tooltip"[\s\S]*?<\/span>(?=<\/span>)/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const tipsOf = (s) => [...s.matchAll(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span><\/span>/g)].map((m) => ent(m[1].replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim());
const head = html.match(/<p[^>]*data-allgrids-headline[^>]*>[\s\S]*?<\/p>/);
if (head) console.log("HEADLINE:", strip(head[0]));
const count = html.match(/<p[^>]*data-allgrids-count[^>]*>[\s\S]*?<\/p>/);
if (count) console.log("COUNT:", strip(count[0]));
for (const m of html.matchAll(/<tr[^>]*data-allgrids-row="([^"]+)"[^>]*>([\s\S]*?)<\/tr>/g)) {
  if (!want.split(",").some((w) => m[1] === w)) continue;
  console.log("ROW", m[1], "|", strip((m[2].match(/<th[\s\S]*?<\/th>/) || [""])[0]));
  for (const [, id, inner] of m[2].matchAll(/<td[^>]*data-cell="([^"]+)"[^>]*>([\s\S]*?)<\/td>/g)) {
    console.log("  ", id.padEnd(12), "|", strip(inner).slice(0, 300));
    if (tips) for (const t of tipsOf(inner)) console.log("        tip:", t.slice(0, Number(tips)));
  }
}
const ab = html.match(/<section[^>]*data-allgrids-abpanel[\s\S]*?<\/section>/);
if (ab) console.log("AB:", strip(ab[0]).slice(0, 1500));
