// Session 10215 (after session 10211's): the site's own loaders (site/scripts/tsx-register.mjs) plus two stand-ins, for
// drawing app/deals/page.tsx whole: components/Brand.tsx imports next/font/google, which only a Next build resolves, so
// Brand is drawn as a plain wrapper of its children (brand-stub.mjs, no word of the tool); and the license file without
// the deals' row when ERW_DRAW_UNHELD=1 (unhold-stub.mjs).
//   node --import ../runs/c10215/register.mjs ../runs/c10215/draw_deals.mjs ...   (run from site/)
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register("./brand-stub.mjs", import.meta.url);
register("./unhold-stub.mjs", import.meta.url);
register("./table-stub.mjs", import.meta.url);
