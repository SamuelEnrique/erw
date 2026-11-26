// Session 10214 (demand audit): the consumption view of /demand drawn to HTML with the site's own code (the page file's
// default export at ?view=consumption, no build, no server). Every read of the live set is answered from a fixture of the
// main copy's two tables (consumption_fixture.py); every other request is refused. Writes the visible text and hovers.
// node --import ./scripts/battery-awards-page-register.mjs ../runs/c10214/draw_consumption.mjs <fixture.json> <out prefix>   (run from site/)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const React = await import(pathToFileURL(req.resolve("react")).href);
const fx = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
process.env.SUPABASE_URL = "https://fixture.invalid/rest/v1/";
process.env.SUPABASE_ANON_KEY = "fixture";
const asked = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  asked.push(u.pathname + u.search);
  const table = (u.searchParams.get("table_name") || "").replace(/^eq\./, "");
  if (!u.pathname.endsWith("/series") || !fx[table]) throw new Error(`refused: ${u}`);
  let rows = fx[table];
  const v = u.searchParams.get("variable");
  if (v) rows = rows.filter((r) => r.variable === v.replace(/^eq\./, ""));
  const off = Number(u.searchParams.get("offset") || 0), lim = Number(u.searchParams.get("limit") || 1000);
  const page = rows.slice(off, off + lim);
  return new Response(JSON.stringify(page), { status: 200, headers: { "content-type": "application/json", "content-range": `${off}-${off + page.length - 1}/*` } });
};
async function resolveTree(node) {
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  const t = node.type;
  if (typeof t === "function" && t.constructor && t.constructor.name === "AsyncFunction") return resolveTree(await t(node.props));
  if (node.props && node.props.children !== undefined) return React.cloneElement(node, undefined, ...[].concat(await resolveTree(node.props.children)));
  return node;
}
const Page = (await import(pathToFileURL(path.join(site, "app", "demand", "page.tsx")).href)).default;
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const html = renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve({ view: "consumption" }) })));
const titles = [...html.matchAll(/title="([^"]*)"/g)].map((m) => unq(m[1]));
const text = unq(html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));
const em = html.split(String.fromCharCode(0x2014)).length - 1;
fs.writeFileSync(`${process.argv[3]}.html`, html);
fs.writeFileSync(`${process.argv[3]}.txt`, [`/demand?view=consumption: ${html.length} characters, ${titles.length} titles; em dashes: ${em}`, "", "== asked", ...asked, "", "== titles", ...titles, "", "== visible text", text].join("\n"));
console.log(`written ${process.argv[3]}.txt: ${titles.length} titles, ${asked.length} reads answered`);
