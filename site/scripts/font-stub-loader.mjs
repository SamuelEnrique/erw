// Energy Research Warehouse (ERW) site, session 7540 (chain 304, part C): a loader hook that stands in for next/font/google,
// so a script can draw a page that wraps itself in <Brand> (components/Brand.tsx loads the brand's three families at
// import, which only a Next.js build can do). Each family becomes a function that returns empty class names and a
// font-family; nothing is fetched. Registered by the script that needs it, after scripts/tsx-register.mjs:
//   import { register } from "node:module"; register("./font-stub-loader.mjs", import.meta.url);
const STUB = "const f = () => ({ variable: \"\", className: \"\", style: { fontFamily: \"sans-serif\" } });"
  + " export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f, Inter = f;";

export async function resolve(specifier, context, nextResolve) {
  if (specifier === "next/font/google") return { url: `data:text/javascript,${encodeURIComponent(STUB)}`, shortCircuit: true };
  return nextResolve(specifier, context);
}
