// Energy Research Warehouse (ERW): render stills of a LinkedIn post (type "post") at chosen frames, for checks and
// review pages. Nothing is posted anywhere.  Session 9900 (24 November 2026).
// Usage: node stills_post.mjs specs/posts/<id>.json <out_dir> <frame,frame,...|peaks> [--height 1350] [--scale 2]
// "peaks" renders each row's highlight peak (64 + 40 i + 16), the settled frame and the last frame.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(path.resolve(args[0]), "utf-8"));
const out = path.resolve(args[1]);
const hi = args.indexOf("--height");
if (hi >= 0) spec.height = +args[hi + 1];
const si = args.indexOf("--scale");
const scale = si >= 0 ? +args[si + 1] : 2;
const n = spec.rows.length;
let frames;
if (args[2] === "peaks") {
  frames = spec.rows.map((_, i) => 64 + 40 * i + 16);
  frames.push(64 + (n - 1) * 40 + 16 + 36 + 20, spec.frames - 1);
} else frames = args[2].split(",").map(Number);
fs.mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(HERE, "src", "index.ts") });
const inputProps = { spec };
const composition = await selectComposition({ serveUrl, id: "Motion", inputProps });
for (const fr of frames) {
  const file = path.join(out, `${spec.id}_${spec.width * scale}x${spec.height * scale}_f${String(fr).padStart(3, "0")}.png`);
  await renderStill({ composition, serveUrl, output: file, inputProps, frame: fr, scale });
  console.log(file);
}
