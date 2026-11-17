// Energy Research Warehouse (ERW) site, session 7565: the loaders of scripts/battery-awards-page-register.mjs and, in
// front of them, the stand-in for next/dynamic (scripts/grid-read-loader.mjs), so /grid can be drawn without a build.
//   node --import ./scripts/grid-read-register.mjs scripts/grid-read-page.mjs <grid> <view> <out.txt>
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
register("./tsx-loader.mjs", import.meta.url);
register("./battery-awards-page-loader.mjs", import.meta.url);
register("./grid-read-loader.mjs", import.meta.url);
