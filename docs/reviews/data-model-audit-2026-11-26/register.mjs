// Session 10228: the site's own loaders (site/scripts/alias-loader.mjs, tsx-loader.mjs) and one stand-in for
// components/Brand.tsx (brand-stub.mjs), for drawing the company pages to HTML. Run from site/:
//   node --import ../runs/c10228/register.mjs ../runs/c10228/draw_companies.mjs <out prefix> [needle ...]
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register("./brand-stub.mjs", import.meta.url);
