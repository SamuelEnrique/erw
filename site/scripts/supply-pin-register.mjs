// Energy Research Warehouse (ERW) site, session 8430 (chain 503, part D): the site's two loaders, as
// scripts/tsx-register.mjs registers them, and in front of them the loader of the pin of /supply
// (scripts/supply-pin-loader.mjs: the copy of the page's two input files kept with the pin, and the stand-in for
// next/font/google), so the whole page can be drawn without a build on the inputs the pin was written from.
//   node --import ./scripts/supply-pin-register.mjs scripts/test-supply-pin.mjs
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
register("./tsx-loader.mjs", import.meta.url);
register("./supply-pin-loader.mjs", import.meta.url);
