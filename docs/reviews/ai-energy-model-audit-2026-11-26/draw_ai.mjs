// Session 10221: /ai-energy drawn to HTML with the site's own code (app/ai-energy/page.tsx whole, the Decisions fold
// with it), so its figures can be set beside an independent restatement and a words branch's new sentences read as a
// reader meets them. Run from site/:
//   node --import ../runs/c10221/register.mjs ../runs/c10221/draw_ai.mjs <out prefix> [needle ...]
// Draws the default view (no query), and each order and each measure the form offers. Writes <prefix>_default.html and
// .txt, and <prefix>_views.json (for each query: the row ids in the order drawn). Prints, for each needle, the sentence
// of the default view's text that holds it, or MISSING; exit 1 when a needle is missing. No request leaves the machine.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [prefix, ...needles] = process.argv.slice(2);
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
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

const Page = (await imp("app/ai-energy/page.tsx")).default;
const draw = async (q) => renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve(q) })));
const html = await draw({});
fs.writeFileSync(`${prefix}_default.html`, html);
const text = words(html);
fs.writeFileSync(`${prefix}_default.txt`, text);
console.log(`default: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);

const ids = (h) => [...h.matchAll(/data-ai-row="([^"]+)"/g)].map((m) => m[1]);
const views = { default: ids(html) };
for (const sort of ["publisher", "measures", "newest", "oldest"]) views[`sort=${sort}`] = ids(await draw({ sort }));
const opts = [...html.matchAll(/<option value="([^"]*)"/g)].map((m) => ent(m[1]));
for (const m of opts.filter((o) => !["publisher", "measures", "newest", "oldest", "all"].includes(o))) views[`m=${m}`] = ids(await draw({ m }));
fs.writeFileSync(`${prefix}_views.json`, JSON.stringify(views, null, 1));
console.log(`views drawn: ${Object.keys(views).length}`);

let missing = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { missing++; console.log(`MISSING: ${n}`); continue; }
  const a = Math.max(text.lastIndexOf(". ", i) + 2, i - 400), b = text.indexOf(". ", i + n.length);
  console.log(`READ: ...${text.slice(a, b < 0 ? i + n.length + 200 : b + 1)}`);
}
process.exitCode = missing ? 1 : 0;
