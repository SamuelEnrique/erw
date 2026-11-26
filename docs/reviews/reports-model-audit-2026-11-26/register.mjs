// Session 10232: the site's own loaders (site/scripts/alias-loader.mjs, tsx-loader.mjs) plus this session's stand-ins
// (stub.mjs), registered last so they answer first.
//   node --import ../runs/c10232/register.mjs ../runs/c10232/draw.mjs <csv dir> <out dir> <tag>   (run from site/)
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register("./stub.mjs", import.meta.url);
