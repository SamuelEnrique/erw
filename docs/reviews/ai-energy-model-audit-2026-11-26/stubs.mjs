// Session 10221: stand-ins for next/font/google and next/navigation, word for word the ones of
// site/scripts/test-reader-pages-render.mjs (no file behind the fonts; notFound and redirect throw as inside Next).
const SRC = "const f = (o) => ({ variable: o?.variable ?? '', className: '', style: { fontFamily: 'stand-in' } }); export const Inter = f, IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
const NAV = "export function notFound() { throw new Error('notFound'); } export function redirect(u) { throw new Error('redirect ' + u); } export const usePathname = () => '/'; export const useRouter = () => ({ push() {}, replace() {}, refresh() {} }); export const useSearchParams = () => new URLSearchParams();";
export async function resolve(s, c, next) {
  if (s === "next/font/google") return { url: "erw-font-stub:google", shortCircuit: true };
  if (s === "next/navigation") return { url: "erw-nav-stub:navigation", shortCircuit: true };
  return next(s, c);
}
export async function load(u, c, next) {
  if (u === "erw-font-stub:google") return { format: "module", source: SRC, shortCircuit: true };
  if (u === "erw-nav-stub:navigation") return { format: "module", source: NAV, shortCircuit: true };
  return next(u, c);
}
