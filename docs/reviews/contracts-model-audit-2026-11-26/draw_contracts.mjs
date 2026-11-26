// Session 10226: /contracts drawn to HTML with the site's own code (app/contracts/page.tsx), no build, no request.
// The two database functions are answered from the rows written by runs/c10226/served.py (the replication's copy_rows.py),
// by a stand-in for fetch, as site/scripts/contracts-figures.mjs does.
//   cd site && node --import ./scripts/tsx-register.mjs ../runs/c10226/draw_contracts.mjs <rows dir> <out.html> [query string]
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire, register } from "node:module";

register(`data:text/javascript,${encodeURIComponent(`
const SRC = "const f = (o) => ({ variable: o?.variable ?? '', className: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
export async function resolve(s, c, next) { return s === "next/font/google" ? { url: "erw-font-stub:google", shortCircuit: true } : next(s, c); }
export async function load(u, c, next) { return u === "erw-font-stub:google" ? { format: "module", source: SRC, shortCircuit: true } : next(u, c); }
`)}`);

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const [dir, out, qs] = process.argv.slice(2);
const summary = JSON.parse(fs.readFileSync(path.join(dir, "summary.json"), "utf-8"));
process.env.SUPABASE_URL = "https://rows.invalid";
process.env.SUPABASE_ANON_KEY = "stand-in";
process.env.INTERNAL_COSTS_TOKEN = "stand-in-token-of-session-10226-draw";
let asked = 0;
globalThis.fetch = async (url, init) => {
  asked++;
  const fn = String(url).split("/rpc/")[1] ?? "";
  const args = JSON.parse(init?.body ?? "{}");
  const answer = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
  if (fn === "internal_eqr_summary") return answer(summary);
  if (fn === "internal_eqr_contracts") {
    const q = `${args.p_from.slice(0, 4)}-Q${Math.floor((Number(args.p_from.slice(5, 7)) - 1) / 3) + 1}`;
    const file = path.join(dir, "quarters", `${q}.json`);
    return answer(fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf-8")) : []);
  }
  return answer({ message: `the stand-in answers no ${url}` }, 404);
};
const { default: Page } = await import(pathToFileURL(path.join(site, "app", "contracts", "page.tsx")).href);
const q = Object.fromEntries(new URLSearchParams(qs ?? ""));
const html = renderToStaticMarkup(await Page({ searchParams: Promise.resolve(q) }));
fs.writeFileSync(out, html);
console.log(`written ${out}: ${html.length} characters, ${asked} reads answered; em dashes: ${html.split(String.fromCharCode(0x2014)).length - 1}`);
