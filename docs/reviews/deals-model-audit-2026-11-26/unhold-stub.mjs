// Session 10215: a module hook for drawing the deal pages as they would be once the hold allows. When ERW_DRAW_UNHELD is
// "1", the site's license file (@/data/license_status.json) is answered without its energy_deals row, so the pages read
// the rows the drawing script serves; otherwise the file is the site's own and every deal view draws the hold.
// Registered by register.mjs after the site's loaders (so it is asked first).
import fs from "node:fs";
import path from "node:path";

const FILE = path.join(process.cwd(), "data", "license_status.json");

export async function resolve(specifier, context, next) {
  if (specifier === "@/data/license_status.json" && process.env.ERW_DRAW_UNHELD === "1") return { url: "erw-unhold:license_status", shortCircuit: true };
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === "erw-unhold:license_status") {
    const j = JSON.parse(fs.readFileSync(FILE, "utf-8"));
    delete j.tables.energy_deals;
    return { format: "module", source: `export default ${JSON.stringify(j)};`, shortCircuit: true };
  }
  return next(url, context);
}
