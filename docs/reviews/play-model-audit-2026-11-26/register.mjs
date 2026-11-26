// Session 10227 (play audit): the site's own loaders (site/scripts/tsx-register.mjs), the Brand stand-in of session 10207
// (docs/reviews/conditions-model-audit-2026-11-26/brand-stub.mjs: Brand imports next/font/google, which only a Next build
// resolves; it carries fonts and a usage mark, no figure or word), and one hook of this audit's own: it adds
// "export { EndTable }" to the end of Game.tsx as loaded here, so the end table (drawn by the game only after a play) can
// be drawn too. Nothing in the repository is changed.
//   node --import ../runs/c10227/register.mjs ../runs/c10227/draw.mjs <out dir> <tag>   (run from site/)
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register(pathToFileURL(path.join(process.cwd(), "..", "docs", "reviews", "conditions-model-audit-2026-11-26", "brand-stub.mjs")).href);
register("./export-endtable.mjs", import.meta.url);
