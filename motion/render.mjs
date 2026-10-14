// Energy Research Warehouse (ERW), session 274: render each spec (specs/*.json) as a silent video at 1080x1350 and
// 1080x1080, with a still of its last frame, into docs/research/motion/. Nothing is posted anywhere.
//
//   node specs.mjs && node render.mjs            every spec
//   node render.mjs specs/<id>.json ...          those specs only
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(HERE, "..", "docs", "research", "motion");
const SIZES = [[1080, 1350], [1080, 1080]];

const args = process.argv.slice(2);
const files = args.length ? args.map((a) => path.resolve(a)) : fs.readdirSync(path.join(HERE, "specs")).filter((f) => f.endsWith(".json")).sort().map((f) => path.join(HERE, "specs", f));
fs.mkdirSync(OUT, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(HERE, "src", "index.ts") });
for (const f of files) {
  const base = JSON.parse(fs.readFileSync(f, "utf-8"));
  for (const [width, height] of SIZES) {
    const spec = { ...base, width, height };
    const name = `${base.id}_${width}x${height}`;
    const inputProps = { spec };
    const composition = await selectComposition({ serveUrl, id: "Motion", inputProps });
    const t0 = Date.now();
    await renderMedia({ composition, serveUrl, codec: "h264", muted: true, outputLocation: path.join(OUT, `${name}.mp4`), inputProps, concurrency: 2, crf: 20 });
    await renderStill({ composition, serveUrl, output: path.join(OUT, `${name}_last.png`), inputProps, frame: composition.durationInFrames - 1 });
    const mb = fs.statSync(path.join(OUT, `${name}.mp4`)).size / 1e6;
    console.log(`${name}.mp4: ${composition.durationInFrames / composition.fps} s, ${mb.toFixed(2)} MB, ${((Date.now() - t0) / 1000).toFixed(0)} s to render`);
  }
}
