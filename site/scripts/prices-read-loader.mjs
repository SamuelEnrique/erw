// Energy Research Warehouse (ERW) site, session 7539 (chain 304, part C): a stand-in for next/navigation that also
// carries notFound and redirect (app/prices/[entity]/page.tsx calls notFound), so the hub page can be drawn without a
// build (scripts/prices-read-page.mjs). notFound throws an error named NEXT_NOT_FOUND, as Next's does; the hooks are
// those of scripts/tsx-loader.mjs's stand-in. Nothing else is replaced.
const NAV = `export const useRouter = () => ({ push() {}, replace() {}, refresh() {}, prefetch() {} });
export const usePathname = () => "/"; export const useSearchParams = () => new URLSearchParams();
export function notFound() { const e = new Error("NEXT_NOT_FOUND"); e.digest = "NEXT_NOT_FOUND"; throw e; }
export function redirect(to) { const e = new Error("NEXT_REDIRECT " + to); e.digest = "NEXT_REDIRECT"; throw e; }`;
export async function resolve(specifier, context, next) {
  if (specifier === "next/navigation") return { url: "erw-prices-stand-in:navigation", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-prices-stand-in:navigation") return { format: "module", source: NAV, shortCircuit: true };
  return next(url, context);
}
