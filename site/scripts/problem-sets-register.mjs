// Energy Research Warehouse (ERW) site, session 7534 (chain 304): the site's two loaders, as scripts/tsx-register.mjs
// registers them, and in front of them the stand-in for next/font/google (scripts/problem-sets-loader.mjs), so the
// problem sets' pages, which wrap themselves in <Brand>, can be drawn without a build.
//   node --import ./scripts/problem-sets-register.mjs scripts/problem-sets-figures.mjs replay ../replication/problem_sets
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
register("./tsx-loader.mjs", import.meta.url);
register("./problem-sets-loader.mjs", import.meta.url);
