// Energy Research Warehouse (ERW) site, session 66: a Node module hook so a script can import the server's own modules
// (lib/game.ts and what it imports) as they are, without building the site. It resolves the site's "@/..." paths to
// files (adding .ts where the import names none), reads a .json import as a module, and stands in for the two imports
// that only exist inside Next ("server-only", a marker, and "next/server", of which lib/game.ts uses NextResponse.json).
// Used by scripts/check-scorer.mjs:  node --import ./scripts/alias-register.mjs scripts/check-scorer.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const site = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const STUBS = {
  "server-only": "export {};",
  "next/server": "export const NextResponse = { json: (body, init) => ({ body, status: init?.status ?? 200 }) };",
};

export async function resolve(specifier, context, next) {
  if (specifier in STUBS) return { url: `erw-stub:${specifier}`, shortCircuit: true };
  if (specifier.startsWith("@/")) {
    const base = path.join(site, specifier.slice(2));
    const file = [base, `${base}.ts`, `${base}.tsx`, path.join(base, "index.ts")].find((p) => fs.existsSync(p) && fs.statSync(p).isFile());
    if (!file) throw new Error(`alias-loader: nothing at ${specifier}`);
    return { url: pathToFileURL(file).href, shortCircuit: true };
  }
  // session 92: a relative import that names no extension ("./ask" in lib/chat), as the site's own modules write them
  if (/^\.\.?\//.test(specifier) && !path.extname(specifier) && context.parentURL?.startsWith("file:")) {
    const base = path.resolve(path.dirname(fileURLToPath(context.parentURL)), specifier);
    const file = [`${base}.ts`, `${base}.tsx`, path.join(base, "index.ts")].find((p) => fs.existsSync(p) && fs.statSync(p).isFile());
    if (file) return { url: pathToFileURL(file).href, shortCircuit: true };
  }
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url.startsWith("erw-stub:")) return { format: "module", source: STUBS[url.slice("erw-stub:".length)], shortCircuit: true };
  if (url.endsWith(".json")) return { format: "module", source: `export default ${fs.readFileSync(fileURLToPath(url), "utf-8")};`, shortCircuit: true };
  return next(url, context);
}
