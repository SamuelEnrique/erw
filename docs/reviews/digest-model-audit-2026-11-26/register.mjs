// Session 10221: the site's own loaders (site/scripts/alias-loader.mjs, tsx-loader.mjs) and the two stand-ins that
// site/scripts/test-reader-pages-render.mjs uses (next/font/google and next/navigation exist only inside a build).
//   node --import ../runs/c10221/register.mjs ../runs/c10221/draw_ai.mjs ...   (run from site/)
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register("./stubs.mjs", import.meta.url);
