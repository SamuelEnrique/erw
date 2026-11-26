// Session 10219: the site's own loaders (site/scripts/tsx-register.mjs) plus the Brand stand-in of session 10207 (Brand
// imports next/font/google, which only a Next build resolves; it carries fonts and a usage mark, no figure or word).
//   node --import ../runs/c10219/register.mjs ../runs/c10219/draw.mjs <out dir> <tag>   (run from site/)
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register("./brand-stub.mjs", import.meta.url);
