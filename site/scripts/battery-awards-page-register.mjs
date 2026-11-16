// Energy Research Warehouse (ERW) site, session 7514 (chain 304, part B): the site's two loaders, as
// scripts/tsx-register.mjs registers them, and in front of them the stand-in for next/font/google
// (scripts/battery-awards-page-loader.mjs), so a whole page that wraps itself in <Brand> can be drawn without a build.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/battery-awards-page.mjs <tables dir> <out.html> <out.txt>
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
register("./tsx-loader.mjs", import.meta.url);
register("./battery-awards-page-loader.mjs", import.meta.url);
