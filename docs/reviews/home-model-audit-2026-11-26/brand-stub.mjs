// Session 10228 (copied from session 10215's): a module hook that answers "@/components/Brand" with a plain wrapper
// (components/Brand.tsx imports next/font/google, which only a Next build resolves). No word of the tool is drawn by it.
import path from "node:path";
import { pathToFileURL } from "node:url";

const SITE = pathToFileURL(path.join(process.cwd(), "package.json")).href;
const SRC = `import { createElement } from "react";
export function Brand({ children, noUsage }) { return createElement("div", { "data-brand-stub": "1", "data-no-usage": noUsage ? "1" : undefined }, children); }`;

// and "next/navigation" (the company page calls notFound for an id no listed company has): a stand-in that throws
const NAV = `export function notFound() { throw new Error("notFound"); }
export function redirect(u) { throw new Error("redirect " + u); }
export function usePathname() { return "/"; }
export function useSearchParams() { return new URLSearchParams(); }
export function useRouter() { return { push() {}, replace() {} }; }`;

export async function resolve(specifier, context, next) {
  if (specifier === "@/components/Brand") return { url: "erw-brand-stub:Brand", shortCircuit: true };
  if (specifier === "next/navigation") return { url: "erw-brand-stub:nav", shortCircuit: true };
  if (context.parentURL?.startsWith("erw-brand-stub:")) return next(specifier, { ...context, parentURL: SITE });
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === "erw-brand-stub:Brand") return { format: "module", source: SRC, shortCircuit: true };
  if (url === "erw-brand-stub:nav") return { format: "module", source: NAV, shortCircuit: true };
  return next(url, context);
}
