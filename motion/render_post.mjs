// Energy Research Warehouse (ERW): render a LinkedIn post (specs/posts/*.json, type "post", src/Post.tsx) as a
// silent 2160 x 2160 master (scale 2 of the 1080 layout) plus a still of its last frame, into docs/research/motion/posts/.
// Nothing is posted anywhere.  Usage: node render_post.mjs specs/posts/<id>.json [--height 1350]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(HERE, "..", "docs", "research", "motion", "posts");
const args = process.argv.slice(2);
const file = path.resolve(args[0]);
const hi = args.indexOf("--height");
const spec = JSON.parse(fs.readFileSync(file, "utf-8"));
if (hi >= 0) spec.height = +args[hi + 1];
fs.mkdirSync(OUT, { recursive: true });
const name = `${spec.id}_${spec.width * 2}x${spec.height * 2}`;
const serveUrl = await bundle({ entryPoint: path.join(HERE, "src", "index.ts") });
const inputProps = { spec };
const composition = await selectComposition({ serveUrl, id: "Motion", inputProps });
await renderMedia({ composition, serveUrl, codec: "h264", muted: true, outputLocation: path.join(OUT, `${name}.mp4`), inputProps, scale: 2, crf: 12, x264Preset: "medium", concurrency: 2 });
await renderStill({ composition, serveUrl, output: path.join(OUT, `${name}_last.png`), inputProps, frame: composition.durationInFrames - 1, scale: 2 });
console.log(`${name}.mp4 written to docs/research/motion/posts/`);
