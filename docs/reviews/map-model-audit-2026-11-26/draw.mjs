// Session 10216: draw /map's Projects tab (ProjectMap) and the decisions block with the site's own code, on the
// page's own file, for an address. Run from site/:
//   node --import ./scripts/tsx-register.mjs ../runs/c10216/draw.mjs "" ../runs/c10216/out/default
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"));
const site = path.resolve(here, "..", "..", "site");
const req = createRequire(path.join(site, "package.json"));
const { createElement } = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const { drawView, textOf } = await import(new URL("file:///" + path.join(site, "scripts", "map-read-page.mjs").replace(/\\/g, "/")).href);
const { MapDecisions } = await import(new URL("file:///" + path.join(site, "app", "map", "Decisions.tsx").replace(/\\/g, "/")).href);

const search = process.argv[2] ?? "";
const out = process.argv[3] ?? path.join(here, "out", "default");
fs.mkdirSync(path.dirname(out), { recursive: true });
const html = drawView(search);
const dec = renderToStaticMarkup(createElement(MapDecisions));
fs.writeFileSync(out + ".html", html + "\n<!-- decisions -->\n" + dec, "utf-8");
fs.writeFileSync(out + ".txt", textOf(html) + "\n--- decisions ---\n" + textOf(dec) + "\n", "utf-8");
console.log(`drawn ${search || "(default)"}: ${html.length} + ${dec.length} characters -> ${out}.html, .txt`);
