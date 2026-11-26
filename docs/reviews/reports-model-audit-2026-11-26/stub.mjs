// Session 10232 (reports audit): module stand-ins for drawing the two draft reports outside Next. Brand (next/font),
// next/headers (no request: no cookie, no header), next/navigation (notFound throws, as Next's does), lib/guard's
// pageTokenTriesLeft (a try is always left) and lib/thesis/server's internalOk (no internal cookie). None of them
// carries a figure or a word of the report; they only open the token gate with a stand-in token.
import path from "node:path";
import { pathToFileURL } from "node:url";

const SITE = pathToFileURL(path.join(process.cwd(), "package.json")).href;
const SRC = {
  "@/components/Brand": `import { createElement } from "react";
export function Brand({ children }) { return createElement("div", { "data-brand-stub": "1" }, children); }`,
  "next/headers": `export async function cookies() { return { get: () => undefined }; }
export async function headers() { return new Headers(); }`,
  "next/navigation": `export function notFound() { throw new Error("NOT_FOUND"); }
export const useRouter = () => ({ push() {}, replace() {}, refresh() {}, prefetch() {} });
export const usePathname = () => "/"; export const useSearchParams = () => new URLSearchParams();`,
  "@/lib/guard": `export async function pageTokenTriesLeft() { return true; }`,
  "@/lib/thesis/server": `export async function internalOk() { return false; }`,
};

export async function resolve(specifier, context, next) {
  if (specifier in SRC) return { url: `erw-c10232-stub:${specifier}`, shortCircuit: true };
  if (context.parentURL?.startsWith("erw-c10232-stub:")) return next(specifier, { ...context, parentURL: SITE });
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url.startsWith("erw-c10232-stub:")) return { format: "module", source: SRC[url.slice("erw-c10232-stub:".length)], shortCircuit: true };
  return next(url, context);
}
