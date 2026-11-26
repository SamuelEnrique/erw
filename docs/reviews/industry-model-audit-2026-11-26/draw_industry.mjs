// Session 10224: /industry drawn to HTML with the site's own code (app/industry/page.tsx whole, the Decisions fold with
// it), so its figures can be set beside an independent restatement and a words branch's new sentences read as a reader
// meets them. Run from site/:
//   node --import ../runs/c10224/register.mjs ../runs/c10224/draw_industry.mjs <out prefix> [query string] [-- needle ...]
// Writes <prefix>.html, <prefix>.txt (the visible words) and <prefix>_figures.json: every marked figure
// (data-fig="key" -> its printed text; data-not-held="key" -> null), every hover's words (title="..."), and the
// decisions' default and source words. Prints, for each needle, the sentence of the text (or hover) that holds it, or
// MISSING; exit 1 when a needle is missing. No request leaves the machine.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const cut = args.indexOf("--");
const [prefix, query = ""] = cut < 0 ? args : args.slice(0, cut);
const needles = cut < 0 ? [] : args.slice(cut + 1);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
globalThis.fetch = async () => new Response("[]", { status: 200, headers: { "content-type": "application/json" } });

async function resolveTree(node) {
  if (node == null || typeof node !== "object") return node;
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  if (typeof node.type === "function" && node.type.constructor?.name === "AsyncFunction") return resolveTree(await node.type(node.props));
  const kids = node.props?.children;
  if (kids === undefined) return node;
  const rk = await resolveTree(kids);
  return React.cloneElement(node, undefined, ...(Array.isArray(rk) ? rk : [rk]));
}
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

const Page = (await imp("app/industry/page.tsx")).default;
const q = Object.fromEntries(new URLSearchParams(query));
const html = renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve(q) })));
fs.writeFileSync(`${prefix}.html`, html);
const text = words(html);
fs.writeFileSync(`${prefix}.txt`, text);
const figs = {};
for (const m of html.matchAll(/data-fig="([^"]+)"[^>]*>([\s\S]*?)<\/span>/g)) figs[m[1]] = ent(m[2].replace(/<!-- -->/g, ""));
for (const m of html.matchAll(/data-not-held="([^"]+)"/g)) if (!(m[1] in figs)) figs[m[1]] = null;
const titles = [...html.matchAll(/title="([^"]*)"/g)].map((m) => ent(m[1]));
const hovers = [...new Set(titles)];
fs.writeFileSync(`${prefix}_figures.json`, JSON.stringify({ query, figures: figs, hovers }, null, 1));
console.log(`${query || "default"}: ${html.length} bytes drawn; ${Object.keys(figs).length} marked figures (${Object.values(figs).filter((v) => v === null).length} not held); ${hovers.length} distinct hovers; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);

let missing = 0;
const hay = `${text} ${hovers.join(" ")}`;
for (const n of needles) {
  const i = hay.indexOf(n);
  if (i < 0) { missing++; console.log(`MISSING: ${n}`); continue; }
  const a = Math.max(hay.lastIndexOf(". ", i) + 2, i - 300), b = hay.indexOf(". ", i + n.length);
  console.log(`READ: ...${hay.slice(a, b < 0 ? i + n.length + 200 : b + 1)}`);
}
process.exitCode = missing ? 1 : 0;
