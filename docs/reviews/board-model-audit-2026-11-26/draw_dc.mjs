// Session 10206: /cost-of-power drawn to HTML with the site's own page and drawer (site/scripts/cost-of-power-read.mjs),
// for the default view, the All grids tab and a 1,000 MW case, so a words branch can be read against origin/main.
//   cd site && node --import ./scripts/tsx-register.mjs ../runs/c10206/draw_dc.mjs <tables dir> <out dir>
import fs from "node:fs";
import path from "node:path";

const [dir, outDir] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const { drawer } = await import("../../site/scripts/cost-of-power-read.mjs");
const { draw, textOf, log } = await drawer(dir);
const CASES = {
  default: {},
  gw: { grid: "ercot", region: "LZ_NORTH", mw: "1000", run: "flat", buy: "rt" },
  allgrids: { view: "allgrids" },
  allgrids_gw: { view: "allgrids", mw: "1000" },
};
for (const [id, q] of Object.entries(CASES)) {
  const html = await draw(q);
  fs.writeFileSync(path.join(outDir, `${id}.html`), html);
  fs.writeFileSync(path.join(outDir, `${id}.txt`), textOf(html));
  console.log(`${id}: ${html.length} bytes`);
}
fs.writeFileSync(path.join(outDir, "reads.log"), log.join("\n"));
console.log(`${log.filter((l) => l.startsWith("NOT")).length} reads not answered`);
process.exitCode = 0;
