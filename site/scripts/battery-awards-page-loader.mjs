// Energy Research Warehouse (ERW) site, session 7514 (chain 304, part B): a stand-in for next/font/google, which exists
// only inside a Next build, so components/Brand.tsx can be imported by a script that draws a whole page to HTML
// (scripts/battery-awards-page.mjs). Each family is given an empty class; nothing else is replaced.
const FONT = "const f = () => ({ variable: '', className: '', style: { fontFamily: 'sans-serif' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stand-in:google", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-font-stand-in:google") return { format: "module", source: FONT, shortCircuit: true };
  return next(url, context);
}
