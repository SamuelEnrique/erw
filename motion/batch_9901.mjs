// Energy Research Warehouse (ERW), session 9901 (25 November 2026): stills and videos of the batch-2 posts in three
// shapes. Nothing is posted anywhere.
// Shapes: x = 1080 x 1080, linkedin = 1080 x 1350, ig = the 1080 x 1350 layout on a 1080 x 1920 fog canvas, 200 px down.
// Usage:
//   node batch_9901.mjs stills <out_dir> <frames: 0,112,last> <shapes: x,linkedin,ig> <spec.json> [<spec.json> ...]
//   node batch_9901.mjs video  <out_root> <shapes> <spec.json> [...]
//     writes <out_root>/<post>/<post>_<option>_<shape>.mp4 and _thumb.png (the last frame), all at scale 2.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const [mode, outArg, ...rest] = process.argv.slice(2);
const out = path.resolve(outArg);
let framesArg = null;
if (mode === "stills") framesArg = rest.shift();
const shapes = rest.shift().split(",");
const files = rest;
const SHAPE = { x: { height: 1080 }, linkedin: { height: 1350 }, ig: { height: 1350, canvasHeight: 1920, canvasTop: 200 } };
const serveUrl = await bundle({ entryPoint: path.join(HERE, "src", "index.ts") });
for (const file of files) {
  const base = JSON.parse(fs.readFileSync(path.resolve(file), "utf-8"));
  for (const sh of shapes) {
    const spec = { ...base, ...SHAPE[sh] };
    if (!SHAPE[sh].canvasHeight) { delete spec.canvasHeight; delete spec.canvasTop; }
    const inputProps = { spec };
    const composition = await selectComposition({ serveUrl, id: "Motion", inputProps });
    const last = composition.durationInFrames - 1;
    if (mode === "stills") {
      fs.mkdirSync(out, { recursive: true });
      const frames = framesArg.split(",").map((x) => (x === "last" ? last : +x));
      for (const fr of frames) {
        const o = path.join(out, `${base.id}_${sh}_f${String(fr).padStart(3, "0")}.png`);
        await renderStill({ composition, serveUrl, output: o, inputProps, frame: fr, scale: 2 });
        console.log(o);
      }
    } else {
      const dir = path.join(out, base.post);
      fs.mkdirSync(dir, { recursive: true });
      const name = `${base.post}_${base.option}_${sh}`;
      await renderMedia({ composition, serveUrl, codec: "h264", muted: true, outputLocation: path.join(dir, `${name}.mp4`), inputProps, scale: 2, crf: 12, x264Preset: "medium", concurrency: 6 });
      await renderStill({ composition, serveUrl, output: path.join(dir, `${name}_thumb.png`), inputProps, frame: last, scale: 2 });
      console.log(path.join(dir, name));
    }
  }
}
