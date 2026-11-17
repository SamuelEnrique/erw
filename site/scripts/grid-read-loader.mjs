// Energy Research Warehouse (ERW) site, session 7565 (docs/reviews/grid-read-2026-11-16.md): a stand-in for
// next/dynamic, so a page that loads a client-only chart with dynamic(..., { ssr: false }) can be drawn to HTML by a
// script. The dynamic component draws nothing, as Next's server pass draws nothing for it; the rest of the page is the
// page's own markup. Nothing else is replaced.
const DYNAMIC = "export default function dynamic() { return function DynamicStandIn() { return null; }; }";
export async function resolve(specifier, context, next) {
  if (specifier === "next/dynamic" || specifier === "next/dynamic.js") return { url: "erw-dynamic-stand-in:next", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-dynamic-stand-in:next") return { format: "module", source: DYNAMIC, shortCircuit: true };
  return next(url, context);
}
