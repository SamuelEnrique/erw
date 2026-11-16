// Energy Research Warehouse (ERW) site, chain 302 (session 7201): a Node module hook that lets a script import the
// site's components (.tsx) as they are and draw them to HTML with react-dom/server, without building the site. The old
// laptop's memory does not always hold a build; a component that throws while it draws, a held value in the HTML, or a
// tip with no target is found here in seconds. It turns a .tsx file into JavaScript with the TypeScript compiler the
// site already has (transpile only: no type check, which `tsc` does), and stands in for the imports that exist only
// inside Next: the site's link (components/SiteLink.tsx: next/link, the address's hooks and the release gate), drawn as
// a plain link with its attributes; and for next/link and next/navigation themselves, where a component names them. It is registered in front of scripts/alias-loader.mjs, which resolves "@/..." and
// reads .json (scripts/tsx-register.mjs). It draws what the server would draw first; it runs no effect and no click.
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const HERE = pathToFileURL(path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "package.json")).href;
const STUBS = {
  "@/components/SiteLink": `import { createElement } from "react";
export function SiteLink({ href, children, gate, prefetch, scroll, ...rest }) { return createElement("a", { href: typeof href === "string" ? href : href?.pathname, "data-site-link": "1", ...rest }, children); }
export const NO_PREFETCH = []; export const noPrefetch = () => false;`,
  // the address's hooks, for a client component drawn outside Next: no address, and a router that goes nowhere
  "next/navigation": `export const useRouter = () => ({ push() {}, replace() {}, refresh() {}, prefetch() {} });
export const usePathname = () => "/"; export const useSearchParams = () => new URLSearchParams();`,
  "next/link": `import { createElement } from "react";
export default function Link({ href, children, prefetch, scroll, replace, ...rest }) { return createElement("a", { href: typeof href === "string" ? href : href?.pathname, ...rest }, children); }`,
};

export async function resolve(specifier, context, next) {
  if (specifier in STUBS) return { url: `erw-tsx-stub:${specifier}`, shortCircuit: true };
  // a stand-in's own imports ("react") are found from the site's folder, as a component's are
  if (context.parentURL?.startsWith("erw-tsx-stub:")) return next(specifier, { ...context, parentURL: HERE });
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url.startsWith("erw-tsx-stub:")) return { format: "module", source: STUBS[url.slice("erw-tsx-stub:".length)], shortCircuit: true };
  if (url.startsWith("file:") && url.endsWith(".tsx")) {
    const ts = require("typescript");
    const out = ts.transpileModule(fs.readFileSync(fileURLToPath(url), "utf-8"), {
      fileName: fileURLToPath(url),
      compilerOptions: { jsx: ts.JsxEmit.ReactJSX, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022, verbatimModuleSyntax: false, isolatedModules: true },
    });
    return { format: "module", source: out.outputText, shortCircuit: true };
  }
  return next(url, context);
}
