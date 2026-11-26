// Session 10233: the data and methodology pages drawn to HTML with the site's own code (app/data/page.tsx, app/data/
// faults/page.tsx, app/data/licenses/page.tsx, app/data/standard/page.tsx, app/data/methods/[slug]/page.tsx for
// impossible_hours and packages), so the audit reads what a visitor is printed and a words branch's sentences are read
// as drawn. Run from site/:
//   node --import ../runs/c10233/register.mjs ../runs/c10233/draw_data.mjs <out prefix> [needle ...]
// The catalogue read is answered from ../runs/c10233/catalogue.json (make_catalogue.py: coverage.csv as the loader
// writes it and the anon key reads it); every other read answers no rows. No request leaves the machine. The data
// standard is read fresh from ../docs/datastandard.md into the content bundle's DOCS (the bundle is of this morning), so
// a branch's edit of the standard is drawn. Prints each drawing's size and whether an em dash is in it; for each needle
// the sentence that holds it, or MISSING (exit 1).
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
const cat = JSON.parse(fs.readFileSync(path.join(site, "..", "runs", "c10233", "catalogue.json"), "utf-8"));

process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const json = (rows) => new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json", "content-range": `0-${Math.max(0, rows.length - 1)}/${rows.length}` } });
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = u.searchParams;
  let rows = [];
  if (u.pathname.endsWith("/catalogue")) rows = cat;
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 100000);
  return json(rows.slice(off, off + lim));
};
Date.now = () => Date.parse("2026-11-26T12:00:00Z");

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
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&ldquo;|&rdquo;/g, '"');
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

let text = "";
let fail = 0;
const keep = (name, html) => {
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  const t = words(html);
  fs.writeFileSync(`${prefix}_${name}.txt`, t);
  text += " " + t;
  const titles = Array.from(new Set(Array.from(html.matchAll(/title="([^"]*)"/g), (m) => ent(m[1]))));
  text += " " + titles.join(". ");
  console.log(`${name}: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
};
const draw = async (name, el) => keep(name, renderToStaticMarkup(await resolveTree(el)));

const md = await imp("lib/markdown.ts");
md.DOCS.datastandard = fs.readFileSync(path.join(site, "..", "docs", "datastandard.md"), "utf-8");

const Data = (await imp("app/data/page.tsx")).default;
await draw("data", await Data());
const Faults = (await imp("app/data/faults/page.tsx")).default;
await draw("faults", Faults());
const Licenses = (await imp("app/data/licenses/page.tsx")).default;
await draw("licenses", Licenses());
const Standard = (await imp("app/data/standard/page.tsx")).default;
await draw("standard", Standard());
const Method = (await imp("app/data/methods/[slug]/page.tsx")).default;
for (const slug of ["impossible_hours", "packages"]) await draw(`method_${slug}`, await Method({ params: Promise.resolve({ slug }) }));

// the /data table's cells, one line a row, for compare.py
const html = fs.readFileSync(`${prefix}_data.html`, "utf-8");
const body = html.slice(html.indexOf("<tbody>"), html.indexOf("</tbody>"));
const out = [];
for (const tr of body.split("<tr ").slice(1)) {
  const id = (tr.match(/id="([^"]+)"/) || [])[1];
  const cells = Array.from(tr.matchAll(/<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/g), (m) => words(m[1]));
  out.push({ id, cells });
}
fs.writeFileSync(`${prefix}_data_rows.json`, JSON.stringify(out));
console.log(`data table rows drawn: ${out.length}`);

for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { console.log(`MISSING: ${n}`); fail = 1; continue; }
  console.log(`found: ${text.slice(Math.max(0, i - 80), i + n.length + 120)}`);
}
process.exitCode = fail;
