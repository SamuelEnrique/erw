// Energy Research Warehouse (ERW) site, session 7531 (chain 304): the site's two loaders, as scripts/tsx-register.mjs
// registers them, and in front of them the stand-in for next/font/google (scripts/events-page-loader.mjs), so a whole
// /events page that wraps itself in <Brand> can be drawn without a build.
//   node --import ./scripts/events-page-register.mjs scripts/events-pages.mjs <tables dir> <out dir>
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
register("./tsx-loader.mjs", import.meta.url);
register("./events-page-loader.mjs", import.meta.url);
