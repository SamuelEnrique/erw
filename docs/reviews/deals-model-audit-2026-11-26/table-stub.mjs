// Session 10215 (after session 10211's): a module hook that answers app/deals/page.tsx's "./DealsTable" with a plain
// stand-in, so the first tab's lead and month cells can be drawn without the table (the table's client component suspends
// under renderToStaticMarkup). The table carries the rows themselves and its column tips, no sentence an audit branch
// changes. Registered by register.mjs after the site's loaders.
const SRC = `import { createElement } from "react";
export function DealsTable({ rows }) { return createElement("div", { "data-table-stub": String(rows.length) }); }
export function usd(v) { return String(v); }`;

export async function resolve(specifier, context, next) {
  if (specifier === "./DealsTable" && (context.parentURL ?? "").includes("/app/deals/page")) return { url: "erw-table-stub:DealsTable", shortCircuit: true };
  if ((context.parentURL ?? "").startsWith("erw-table-stub:")) return next(specifier, { ...context, parentURL: new URL("../../site/package.json", import.meta.url).href });
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === "erw-table-stub:DealsTable") return { format: "module", source: SRC, shortCircuit: true };
  return next(url, context);
}
