// Energy Research Warehouse (ERW) site, chain 302 (session 7201): registers scripts/alias-loader.mjs and, in front of it,
// scripts/tsx-loader.mjs, so a script can draw the site's own components to HTML without building the site.
//   node --import ./scripts/tsx-register.mjs scripts/test-large-load-render.mjs
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
register("./tsx-loader.mjs", import.meta.url);
