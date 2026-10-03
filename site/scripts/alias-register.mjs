// Energy Research Warehouse (ERW) site, session 66: registers scripts/alias-loader.mjs (see it).
import { register } from "node:module";

register("./alias-loader.mjs", import.meta.url);
