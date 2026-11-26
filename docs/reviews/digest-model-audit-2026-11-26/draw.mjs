// Session 10235 (the Digest and Roundup audit): the Digest's and the Roundup's pages drawn to HTML with the site's own
// code (react-dom/server renderToStaticMarkup through the site's loaders and the Brand stand-in of session 10207), no
// build, no server, no browser. Every network read is refused and listed (the Digest's revision notes read the live
// set; refused, the page shows no note, as it does when a read fails). Run from site/:
//   node --import <runs>/register.mjs <runs>/draw.mjs <out dir> <tag>
// Writes <tag>_<view>.html and <tag>_<view>.txt (the visible words, then every hover) and <tag>_asked.txt.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [outDir, tag = "main"] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const asked = [];
globalThis.fetch = async (url) => { asked.push(`refused ${String(url)}`); return new Response("stand-in: not held", { status: 404 }); };
console.error = () => {};

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
const titles = (s) => [...s.matchAll(/title="([^"]*)"/g)].map((m) => ent(m[1]));

const views = [
  ["roundup_index", "app/roundup/page.tsx", null],
  ["roundup_W45", "app/roundup/[week]/page.tsx", { week: "2026-W45" }],
  ["digest_2026-11-21", "app/digest/[date]/page.tsx", { date: "2026-11-21" }],
  ["digest_2026-11-14", "app/digest/[date]/page.tsx", { date: "2026-11-14" }],
  ["digest_2026-11-12", "app/digest/[date]/page.tsx", { date: "2026-11-12" }],
  ["digest_index", "app/digest/page.tsx", null],
];
for (const [name, file, params] of views) {
  try {
    const Page = (await imp(file)).default;
    const el = params ? await Page({ params: Promise.resolve(params) }) : await Page();
    const html = renderToStaticMarkup(await resolveTree(el));
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.html`), html);
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.txt`), words(html) + "\n\nHOVERS\n" + titles(html).join("\n") + "\n");
    console.log(`${name}: ${html.length} bytes; held marks ${(html.match(/data-license-held=/g) ?? []).length}; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
  } catch (e) {
    console.log(`${name}: failed ${String(e?.stack ?? e).slice(0, 600)}`);
  }
}
fs.writeFileSync(path.join(outDir, `${tag}_asked.txt`), asked.join("\n") + "\n");
