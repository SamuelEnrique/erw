// Energy Research Warehouse (ERW) site, session 5202 (chain 235): registers scripts/eval-loader.mjs (see it).
import { register } from "node:module";

register("./eval-loader.mjs", import.meta.url);
