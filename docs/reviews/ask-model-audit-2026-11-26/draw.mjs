// Session 10234 (the chat's audit): a page drawn to HTML with the site's own code, no build, no database, no network.
// Run from site/:  node --import ./scripts/tsx-register.mjs ../runs/s10234/draw.mjs <page path under app> <out file> [needle ...]
// Writes the visible words to <out file> and prints, for each needle, whether the words hold it.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
import { register } from "node:module";

// the site's own stand-in for next/font/google (components/Brand.tsx loads its families at import)
register(pathToFileURL(path.join(process.cwd(), "scripts", "font-stub-loader.mjs")).href, import.meta.url);
const [rel, outFile, ...needles] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const asked = [];
globalThis.fetch = async (url) => { asked.push(String(url)); return new Response("stand-in: not held", { status: 404 }); };

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
const words = (s) => ent(s.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

const Page = (await import(pathToFileURL(path.join(site, rel)).href)).default;
const tree = await resolveTree(await Page({ searchParams: Promise.resolve({}) }));
const html = renderToStaticMarkup(tree);
const text = words(html);
fs.writeFileSync(outFile, text + "\n");
for (const n of needles) console.log(`${text.includes(n) ? "FOUND" : "MISSING"}: ${n}`);
console.log(`words ${text.length}; network reads ${asked.length}`);
process.exitCode = 0;
