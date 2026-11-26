// Session 10211: a module hook that answers app/datacenters/Body.tsx's "./DatacentersTable" with a plain stand-in, so the
// top block can be drawn without the list (the list's client component suspends under renderToStaticMarkup). The list
// carries the rows themselves, no sentence an audit branch changes. Registered by register.mjs after the site's loaders.
const SRC = `import { createElement } from "react";
export function DatacentersTable({ rows }) { return createElement("div", { "data-table-stub": String(rows.length) }); }`;

export async function resolve(specifier, context, next) {
  if (specifier === "./DatacentersTable" && (context.parentURL ?? "").includes("/app/datacenters/Body")) return { url: "erw-table-stub:DatacentersTable", shortCircuit: true };
  if ((context.parentURL ?? "").startsWith("erw-table-stub:")) return next(specifier, { ...context, parentURL: new URL("../../site/package.json", import.meta.url).href });
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === "erw-table-stub:DatacentersTable") return { format: "module", source: SRC, shortCircuit: true };
  return next(url, context);
}
