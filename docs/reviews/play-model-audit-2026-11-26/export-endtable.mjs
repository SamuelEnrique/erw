// Session 10227: a module hook (register.mjs) that (1) adds "export { EndTable };" to site/app/play/battery/Game.tsx as
// loaded, and (2) answers next/navigation with the site loader's stand-in plus redirect (the battery page imports it for
// its old ?more=1 address; a drawing never reaches it), which the site's stand-in lacks.
const NAV = `export const useRouter = () => ({ push() {}, replace() {}, refresh() {}, prefetch() {} });
export const usePathname = () => "/"; export const useSearchParams = () => new URLSearchParams();
export function redirect(to) { throw new Error("redirect to " + to + " (not reached in a drawing)"); }`;

export async function resolve(specifier, context, next) {
  if (specifier === "next/navigation") return { url: "erw-c10227-stub:next/navigation", shortCircuit: true };
  return next(specifier, context);
}

export async function load(url, context, next) {
  if (url === "erw-c10227-stub:next/navigation") return { format: "module", source: NAV, shortCircuit: true };
  const r = await next(url, context);
  if (url.startsWith("file:") && url.replace(/\\/g, "/").endsWith("/app/play/battery/Game.tsx")) {
    return { ...r, source: `${String(r.source)}\nexport { EndTable };\n` };
  }
  return r;
}
