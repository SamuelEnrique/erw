// Energy Research Warehouse (ERW) site, session 7537 (chain 304, part C): the Projects tab of /map drawn to HTML by its
// own component (app/map/ProjectMap.tsx) on the page's own file (data/map.json), for any address, without building the
// site. The tab computes in the reader's browser; with no window the component reads the address it is given
// (`serverSearch`), so the HTML is what the tab shows on that address before any click. The drawing itself (the chart)
// is a box with no marks here: a browser draws it. Used by scripts/test-map-read.mjs, and on its own:
//   node --import ./scripts/tsx-register.mjs scripts/map-read-page.mjs "?at=32.4487,-99.7331&within=30"
import fs from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { feature } from "topojson-client";

const { ProjectMap } = await import("../app/map/ProjectMap.tsx");
const { faceOf } = await import("../lib/projectmap.ts");
export const file = JSON.parse(fs.readFileSync(new URL("../data/map.json", import.meta.url), "utf-8"));
const topo = JSON.parse(fs.readFileSync(new URL("../node_modules/us-atlas/states-albers-10m.json", import.meta.url), "utf-8"));
const statesGeo = feature(topo, topo.objects.states);
const face = faceOf(file);

/** The tab's HTML on an address (the part after /map). */
export function drawView(search) {
  return renderToStaticMarkup(createElement(ProjectMap, { file: face, statesGeo, serverSearch: search }));
}
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
/** The visible words of the HTML, one block a line (a tip's words are kept: they are what a hover shows). */
export function textOf(html) {
  return ent(html.replace(/<(\/(p|div|li|tr|h2|h3|section|aside|summary|table|caption)|br\s*\/?)>/g, "\n").replace(/<\/t[dh]>/g, " | ").replace(/<[^>]+>/g, "")).replace(/[ \t]+/g, " ").split("\n").map((l) => l.trim()).filter(Boolean).join("\n");
}

if (process.argv[1] && process.argv[1].endsWith("map-read-page.mjs")) {
  console.log(textOf(drawView(process.argv[2] ?? "")));
}
