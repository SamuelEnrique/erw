// Session 10219 (conditions audit): /conditions drawn to HTML with the site's own code, no build and no database. The
// page reads only its committed files (site/data/conditions/*.json); any network read is refused and listed. Run from site/:
//   node --import ../runs/c10219/register.mjs ../runs/c10219/draw.mjs <out dir> <tag>
// Writes, for each view, <tag>_<name>.html, <tag>_<name>.txt (visible words), <tag>_<name>_n.json (every data-check
// figure with its key, raw value and shown text) and <tag>_asked.txt (every network read, refused).
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
function figures(html) {
  const out = {};
  for (const m of html.matchAll(/data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([^<]*)</g)) out[ent(m[1])] = { raw: ent(m[2]), shown: ent(m[3]) };
  return out;
}
// every title attribute (the hovers), so a word that sits in a hover is read too
const titles = (s) => [...s.matchAll(/title="([^"]*)"/g)].map((m) => ent(m[1]));

const Page = (await imp("app/conditions/page.tsx")).default;
const views = [
  ["default", {}], ["caiso", { a: "caiso" }], ["spp", { a: "spp" }], ["caiso_heat_2020", { a: "caiso", event: "caiso_heat_2020" }],
  ["ercot_covid", { a: "ercot", event: "covid_2020" }], ["ercot_uri", { a: "ercot", event: "uri_2021" }],
  ["pjm_covid", { a: "pjm", event: "covid_2020" }], ["caiso_spp_heat_2022", { a: "caiso", event: "caiso_heat_2022", b: "spp" }],
];
for (const [name, sp] of views) {
  try {
    const html = renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve(sp) })));
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.html`), html);
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.txt`), words(html) + "\n\nHOVERS\n" + titles(html).join("\n") + "\n");
    fs.writeFileSync(path.join(outDir, `${tag}_${name}_n.json`), JSON.stringify(figures(html), null, 1));
    console.log(`${name}: ${html.length} bytes; ${Object.keys(figures(html)).length} figures; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
  } catch (e) {
    console.log(`${name}: failed ${String(e?.stack ?? e).slice(0, 600)}`);
  }
}
fs.writeFileSync(path.join(outDir, `${tag}_asked.txt`), asked.join("\n") + "\n");
process.exitCode = 0;
