// Session 10216: draw ProjectMap on the page's file with its queue vintage set to another day (finding 1's words for a
// copy pulled after ERCOT's milestones). Run from site/:
//   node --import ./scripts/tsx-register.mjs ../runs/c10216/draw_vintage.mjs 2026-11-23 "?kind=queue&grid=ercot&at=32.4487,-99.7331&within=30" ../runs/c10216/out/b1_later
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"));
const site = path.resolve(here, "..", "..", "site");
const req = createRequire(path.join(site, "package.json"));
const { createElement } = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const { feature } = req("topojson-client");
const url = (...p) => new URL("file:///" + path.join(site, ...p).replace(/\\/g, "/")).href;
const { ProjectMap } = await import(url("app", "map", "ProjectMap.tsx"));
const { faceOf } = await import(url("lib", "projectmap.ts"));
const { textOf } = await import(url("scripts", "map-read-page.mjs"));
const [vintage, search, out] = process.argv.slice(2);
const file = JSON.parse(fs.readFileSync(path.join(site, "data", "map.json"), "utf-8"));
file.vintages = { ...file.vintages, queue: vintage };
const topo = JSON.parse(fs.readFileSync(path.join(site, "node_modules", "us-atlas", "states-albers-10m.json"), "utf-8"));
const html = renderToStaticMarkup(createElement(ProjectMap, { file: faceOf(file), statesGeo: feature(topo, topo.objects.states), serverSearch: search }));
fs.writeFileSync(out + ".txt", textOf(html) + "\n", "utf-8");
console.log(`drawn with the queue vintage ${vintage}: ${out}.txt`);
