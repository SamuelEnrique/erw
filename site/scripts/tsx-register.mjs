// Energy Research Warehouse (ERW) site, session 1160: registers scripts/tsx-loader.mjs (see it). Registered after
// scripts/alias-register.mjs, so its hooks run first and hand every other import to session 66's loader.
import { register } from "node:module";

register("./tsx-loader.mjs", import.meta.url);
