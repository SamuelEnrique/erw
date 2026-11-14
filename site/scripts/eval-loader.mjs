// Energy Research Warehouse (ERW) site, session 5202 (chain 235): scripts/alias-loader.mjs, and one thing more for a
// git worktree that has no node_modules of its own: a package the site imports by name ("@anthropic-ai/sdk") that is
// not found from the worktree is resolved from another checkout's site/node_modules, read where it stands. Nothing is
// installed, linked or copied, and nothing is built. The other checkout is ERW_NODE_MODULES_SITE when set, else the
// main checkout beside the worktree (../../erw/site, as warehouse/chat/eval/eval_loop.py finds the .env).
//
// Used by scripts/eval-ask-site-loop.mjs through scripts/eval-register.mjs.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import * as alias from "./alias-loader.mjs";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const other = process.env.ERW_NODE_MODULES_SITE || path.join(site, "..", "..", "erw", "site");

/** Whether a specifier names a package (not a path, not a URL, not a node: builtin). */
export function bare(specifier) {
  return !/^(\.{0,2}\/|[A-Za-z]:[\\/]|file:|node:|data:|erw-stub:|@\/)/.test(specifier);
}

export async function resolve(specifier, context, next) {
  try {
    return await alias.resolve(specifier, context, next);
  } catch (e) {
    const here = fs.existsSync(path.join(site, "node_modules"));
    if (here || !bare(specifier) || e?.code !== "ERR_MODULE_NOT_FOUND" || !fs.existsSync(path.join(other, "node_modules"))) throw e;
    return next(specifier, { ...context, parentURL: pathToFileURL(path.join(other, "package.json")).href });
  }
}

export const load = alias.load;
