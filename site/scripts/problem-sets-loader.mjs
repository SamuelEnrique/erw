// Energy Research Warehouse (ERW) site, session 7534 (chain 304): stand-ins for two modules that exist only inside a
// Next build, so the problem sets' pages can be drawn to HTML by a script (scripts/problem-sets-figures.mjs):
//   - next/font/google, for components/Brand.tsx: each family is given an empty class;
//   - next/navigation, for the pages' notFound() (a set or an edition that does not exist throws, as Next's does) and the
//     address's hooks (no address, a router that goes nowhere), as scripts/tsx-loader.mjs gives them.
// Nothing else is replaced.
const FONT = "const f = () => ({ variable: '', className: '', style: { fontFamily: 'sans-serif' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
const NAV = `export function notFound() { const e = new Error("NEXT_NOT_FOUND"); e.digest = "NEXT_NOT_FOUND"; throw e; }
export function redirect(to) { const e = new Error("NEXT_REDIRECT " + to); e.digest = "NEXT_REDIRECT"; throw e; }
export const useRouter = () => ({ push() {}, replace() {}, refresh() {}, prefetch() {} });
export const usePathname = () => "/"; export const useSearchParams = () => new URLSearchParams();`;
const STUBS = { "next/font/google": FONT, "next/navigation": NAV };
export async function resolve(specifier, context, next) {
  if (specifier in STUBS) return { url: `erw-problem-sets-stand-in:${specifier}`, shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url.startsWith("erw-problem-sets-stand-in:")) return { format: "module", source: STUBS[url.slice("erw-problem-sets-stand-in:".length)], shortCircuit: true };
  return next(url, context);
}
