// Session 10238: the five small pages drawn to HTML with the site's own code, their default views, for the audit's
// arithmetic and for reading a words branch once more. Run from site/ with the site's loaders and the Brand stand-in:
//   node --import ../runs/c10238/register.mjs ../runs/c10238/draw.mjs <main copy> <out prefix> [needle ...]
// The only database read answered is /shoulder's (shoulder_hours_monthly, from the main copy's table, read and never
// written); every other read gets no rows. No request leaves the machine. For each needle: the sentence that holds it,
// or MISSING (exit 1). A map canvas is not drawn; the words around it are.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [mainCopy, prefix, ...needles] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";

// the shoulder table, as the live set would answer it: entity, variable, ts_utc, value, ordered as the page asks
const csvPath = path.join(mainCopy, "warehouse", "output", "shoulder_hours_monthly.csv");
const lines = fs.readFileSync(csvPath, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const head = lines[0].split(",");
const ix = (k) => head.indexOf(k);
const SH = lines.slice(1).map((l) => l.split(",")).map((c) => ({ entity: c[ix("entity")], variable: c[ix("variable")], ts_utc: c[ix("ts_utc")], value: c[ix("value")] }))
  .sort((a, b) => (a.entity < b.entity ? -1 : a.entity > b.entity ? 1 : a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : a.ts_utc > b.ts_utc ? 1 : 0));
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  let rows = [];
  if (u.searchParams.get("table_name") === "eq.shoulder_hours_monthly") {
    const off = Number(u.searchParams.get("offset") ?? 0), lim = Number(u.searchParams.get("limit") ?? 1000);
    rows = SH.slice(off, off + lim);
  }
  return new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json", "content-range": `0-${rows.length}/*` } });
};

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
const ent = (s) => s.replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ");
const words = (s) => ent(s.replace(/<title>[\s\S]*?<\/title>/g, " ").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
let text = "";
const keep = async (name, make) => {
  try {
    const html = renderToStaticMarkup(await resolveTree(await make()));
    fs.writeFileSync(`${prefix}_${name}.html`, html);
    fs.writeFileSync(`${prefix}_${name}.txt`, words(html));
    text += " " + words(html);
    console.log(`${name}: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
  } catch (e) {
    console.log(`${name}: NOT DRAWN (${e && e.message ? e.message.slice(0, 300) : e})`);
    process.exitCode = 1;
  }
};
const noQuery = { searchParams: Promise.resolve({}) };
await keep("about", async () => React.createElement((await imp("app/about/page.tsx")).default));
await keep("subscribe", async () => React.createElement((await imp("app/subscribe/page.tsx")).default, noQuery));
await keep("shoulder", async () => React.createElement((await imp("app/shoulder/page.tsx")).default, noQuery));
// /attention: the page's lead and its view (the page's Cite, downloads and related links suspend outside a Next server,
// so the view is drawn with the page's own file, data/attention.json, and the lead is read from the page's file)
await keep("attention", async () => {
  const { AttentionView } = await imp("app/attention/AttentionView.tsx");
  const file = JSON.parse(fs.readFileSync(path.join(site, "data", "attention.json"), "utf-8"));
  return React.createElement(AttentionView, { file, statesGeo: { type: "FeatureCollection", features: [] } });
});
await keep("resources", async () => React.createElement((await imp("app/resources/view.tsx")).ResourcesView));
let fail = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { console.log(`MISSING: ${n}`); fail = 1; continue; }
  const a = Math.max(0, text.lastIndexOf(". ", i) + 2), b = text.indexOf(". ", i + n.length);
  console.log(`FOUND: ${text.slice(a, b < 0 ? i + n.length + 80 : b + 1).slice(0, 600)}`);
}
if (fail) process.exitCode = 1;
