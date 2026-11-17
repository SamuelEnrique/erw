// Energy Research Warehouse (ERW) site, session 7539 (chain 304, part C): the loaders of
// scripts/battery-awards-page-register.mjs (the site's two, and the stand-in for next/font/google), and in front of
// them scripts/prices-read-loader.mjs (next/navigation with notFound), so /prices and /prices/<hub> can be drawn whole.
//   node --import ./scripts/prices-read-register.mjs scripts/prices-read-page.mjs <tables dir> <render time ISO> <out dir> [entity ...]
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
register("./tsx-loader.mjs", import.meta.url);
register("./battery-awards-page-loader.mjs", import.meta.url);
register("./prices-read-loader.mjs", import.meta.url);
