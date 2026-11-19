// Energy Research Warehouse (ERW) site, session 8430 (chain 503, part D): the loader of the pin of /supply
// (scripts/test-supply-pin.mjs). The page's every figure is in the site's own file (data/supply.json), which the data
// machine rebuilds each week, and its holds are in data/license_status.json, which changes when a license does. A pin
// that hashes the drawn page would break at each rebuild though no code moved, so the pin keeps a copy of the two files
// as they stood when it was written (scripts/pins/supply-page-8430-input.json, both public files of this repository,
// copied whole) and this loader serves the copy in their place. It also stands in for next/font/google, which exists
// only inside a Next build (as scripts/battery-awards-page-loader.mjs does). While the copy does not exist yet the two
// files are served as they are. Nothing else is replaced, and only a script that registers this loader sees the copy.
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const FONT = "const f = () => ({ variable: '', className: '', style: { fontFamily: 'sans-serif' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
const INPUT = new URL("./pins/supply-page-8430-input.json", import.meta.url);
const KEYS = { "/data/supply.json": "supply", "/data/license_status.json": "license_status" };

export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stand-in:google", shortCircuit: true };
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === "erw-font-stand-in:google") return { format: "module", source: FONT, shortCircuit: true };
  if (url.startsWith("file:")) {
    const at = url.replace(/\\/g, "/");
    const key = Object.keys(KEYS).find((k) => at.endsWith(`/site${k}`));
    if (key && fs.existsSync(INPUT)) {
      const copy = JSON.parse(fs.readFileSync(fileURLToPath(INPUT), "utf-8"))[KEYS[key]];
      if (copy === undefined) throw new Error(`supply-pin-loader: the pin's input holds no ${KEYS[key]}`);
      return { format: "module", source: `export default ${JSON.stringify(copy)};`, shortCircuit: true };
    }
  }
  return next(url, context);
}
