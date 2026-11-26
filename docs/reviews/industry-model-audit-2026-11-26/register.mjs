// Session 10224: the site's own loaders (site/scripts/alias-loader.mjs, tsx-loader.mjs) and the two stand-ins that
// site/scripts/test-reader-pages-render.mjs uses (next/font/google and next/navigation exist only inside a build).
// Copied from session 10221's register.mjs.
//   node --import ../runs/c10224/register.mjs ../runs/c10224/draw_industry.mjs ...   (run from site/)
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register("./stubs.mjs", import.meta.url);
