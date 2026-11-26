// Session 10207 (copied by session 10211): a module hook that answers "@/components/Brand" with a plain wrapper (see register.mjs).
import path from "node:path";
import { pathToFileURL } from "node:url";

const SITE = pathToFileURL(path.join(process.cwd(), "package.json")).href;
const SRC = `import { createElement } from "react";
export function Brand({ children, noUsage }) { return createElement("div", { "data-brand-stub": "1", "data-no-usage": noUsage ? "1" : undefined }, children); }`;

export async function resolve(specifier, context, next) {
  if (specifier === "@/components/Brand") return { url: "erw-brand-stub:Brand", shortCircuit: true };
  if (context.parentURL?.startsWith("erw-brand-stub:")) return next(specifier, { ...context, parentURL: SITE });
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === "erw-brand-stub:Brand") return { format: "module", source: SRC, shortCircuit: true };
  return next(url, context);
}
