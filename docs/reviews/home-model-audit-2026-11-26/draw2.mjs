// Session 10236: the two words of site/lib/pages.ts this audit changes (the tour's and the Thesis Builder's lines) as
// /about draws them (app/about/page.tsx, every group's tools with their lines), and the method note docs/methods/thesis.md
// as the site renders a note (lib/markdown.ts, render), read fresh from the branch's file. Run from site/:
//   node --import ../runs/c10236/register.mjs ../runs/c10236/draw2.mjs <out prefix> [needle ...]
// No database read is answered (every read gets no rows); no request leaves the machine. For each needle the sentence
// that holds it, or MISSING (exit 1).
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
globalThis.fetch = async () => new Response("[]", { status: 200, headers: { "content-type": "application/json", "content-range": "0-0/0" } });

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
const ent = (s) => s.replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
let text = "";
const keep = (name, html) => {
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  text += " " + words(html);
  console.log(`${name}: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
};
const About = (await imp("app/about/page.tsx")).default;
keep("about", renderToStaticMarkup(await resolveTree(React.createElement(About))));
const { render } = await imp("lib/markdown.ts");
keep("thesis_note", render(fs.readFileSync(path.join(site, "..", "docs", "methods", "thesis.md"), "utf-8"), "docs/methods/thesis.md"));
let fail = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { console.log(`MISSING: ${n}`); fail = 1; continue; }
  const a = Math.max(0, text.lastIndexOf(". ", i) + 2), b = text.indexOf(". ", i + n.length);
  console.log(`FOUND: ${text.slice(a, b < 0 ? i + n.length + 80 : b + 1)}`);
}
process.exitCode = fail;
