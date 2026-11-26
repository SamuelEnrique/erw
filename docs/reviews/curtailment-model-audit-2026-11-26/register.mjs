// Session 10207: the site's own loaders (site/scripts/tsx-register.mjs) plus one stand-in, for drawing app/severance/page.tsx
// whole: components/Brand.tsx imports next/font/google, which only a Next build resolves, so Brand is drawn as a plain
// wrapper of its children (it carries the page's fonts and its data-no-usage mark, no figure or word of the tool).
//   node --import ../runs/c10207/register.mjs ../runs/c10207/lib_figures.mjs ...   (run from site/)
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import path from "node:path";

const site = pathToFileURL(path.join(process.cwd(), "scripts") + path.sep).href;
register("./alias-loader.mjs", site);
register("./tsx-loader.mjs", site);
register("./brand-stub.mjs", import.meta.url);
