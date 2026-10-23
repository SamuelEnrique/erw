// Chain 072, session 1049: one frame of the node map's design (docs/reviews/siting-map-design.md), not wired.
// Texas's counties (us-atlas counties-10m, the site's own dependency) shaded by the count of ERCOT nodes
// ercot_node_places places in each (site/data/siting/nodes.json), at the county's resolution only: no node is drawn as
// a point. Writes an SVG and, through the site's headless browser helper, PNGs at 1280 and 390 wide.
//   node frame1049.mjs <site-dir> <out-dir>
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const [siteDir, outDir] = process.argv.slice(2).map((p) => path.resolve(p));
fs.mkdirSync(outDir, { recursive: true });
const req = createRequire(path.join(siteDir, "package.json"));
const { geoAlbers, geoPath } = await import(pathToFileURL(req.resolve("d3-geo")).href);
const topo = await import(pathToFileURL(req.resolve("topojson-client")).href);
const us = JSON.parse(fs.readFileSync(req.resolve("us-atlas/counties-10m.json"), "utf-8"));
const nodes = JSON.parse(fs.readFileSync(path.join(siteDir, "data", "siting", "nodes.json"), "utf-8"));

const key = (s) => s.toUpperCase().replace(/[^A-Z]/g, "");
const count = {}, zoneOf = {};
for (const n of nodes.nodes) if (n.county) { count[key(n.county)] = (count[key(n.county)] ?? 0) + 1; zoneOf[key(n.county)] = n.zone; }
const all = topo.feature(us, us.objects.counties).features.filter((f) => String(f.id).startsWith("48"));
const tx = { type: "FeatureCollection", features: all };
const W = 960, H = 920;
const proj = geoAlbers().rotate([99.5, 0]).fitExtent([[20, 104], [W - 20, H - 84]], tx);
const gp = geoPath(proj);
const max = Math.max(...Object.values(count));
const steps = [0, 1, 3, 6, 11, 21];   // bins: none, 1 to 2, 3 to 5, 6 to 10, 11 to 20, 21 and more
const fills = ["#f3f4f6", "#dbe7f3", "#b3cde6", "#7fa9d4", "#4a80bd", "#1f4f8f"];
const bin = (c) => steps.reduce((b, s, i) => (c >= s ? i : b), 0);
const matched = new Set();
const paths = all.map((f) => {
  const k = key(f.properties.name), c = count[k] ?? 0;
  if (c) matched.add(k);
  return `<path d="${gp(f)}" fill="${fills[bin(c)]}" stroke="#ffffff" stroke-width="0.6"><title>${f.properties.name} County: ${c} node${c === 1 ? "" : "s"} placed</title></path>`;
}).join("");
const unmatched = Object.keys(count).filter((k) => !matched.has(k));
const legend = steps.map((s, i) => {
  const label = i === 0 ? "none placed" : i === steps.length - 1 ? `${s} or more` : `${s} to ${steps[i + 1] - 1}`;
  return `<rect x="${24 + i * 150}" y="${H - 66}" width="18" height="18" fill="${fills[i]}" stroke="#9ca3af" stroke-width="0.5"/><text x="${48 + i * 150}" y="${H - 52}" font-size="15">${label}</text>`;
}).join("");
const placed = nodes.places.matched, of = nodes.places.of;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="IBM Plex Sans, Arial, sans-serif" fill="#111827">
<rect width="${W}" height="${H}" fill="#ffffff"/>
<text x="24" y="40" font-size="26" font-family="Source Serif 4, Georgia, serif">ERCOT nodes placed by county</text>
<text x="24" y="66" font-size="15">${placed} of ${of} resource nodes, by the county ERCOT's CDR gives the units at their station (ercot_node_places).</text>
<text x="24" y="86" font-size="15">${of - placed} are not placed and not drawn. Counties outside ERCOT are drawn too, unshaded.</text>
${paths}
${legend}
<text x="24" y="${H - 14}" font-size="12">Design frame, session 1049, not on the site. Counties: us-atlas (Census cartographic boundaries). Most nodes in one county: ${max}.</text>
<text x="24" y="${H - 2}" font-size="12">A county's shade is a count of nodes, not a node's location.</text>
</svg>`;
fs.writeFileSync(path.join(outDir, "frame_counties.svg"), svg);
console.log(`counties shaded ${matched.size} of ${Object.keys(count).length}; not matched to a county shape: ${unmatched.join(", ") || "none"}; max ${max}`);

const B = await import(pathToFileURL(path.join(siteDir, "scripts", "browser.mjs")).href);
const html = path.join(outDir, "frame_counties.html");
fs.writeFileSync(html, `<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff}svg{width:100%;height:auto;display:block}</style>${svg}`);
await B.withBrowser(async ({ go, send, sleep }) => {
  for (const w of [1280, 390]) {
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: Math.round((w * H) / W), deviceScaleFactor: 1, mobile: w < 600 });
    await go(pathToFileURL(html).href);
    await sleep(500);
    const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    fs.writeFileSync(path.join(outDir, `frame_counties_${w}.png`), Buffer.from(shot.data, "base64"));
    console.log(`wrote frame_counties_${w}.png`);
  }
});
fs.rmSync(html);
