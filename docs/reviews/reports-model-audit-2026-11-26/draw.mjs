// Session 10232 (reports audit): the two draft reports drawn to HTML with the site's own code, no build and no
// database. Every read of the live set is answered from the warehouse CSVs in <csv dir> (read only), as PostgREST
// would answer a series read (table_name, limit, offset); any other read is refused and listed. Run from site/:
//   node --import ../runs/c10232/register.mjs ../runs/c10232/draw.mjs <csv dir> <out dir> <tag>
// Writes <tag>_<page>.html, .txt (visible words, then every hover), _n.json (every data-check figure: key, raw, shown)
// and <tag>_asked.txt (every read: served or refused).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [csvDir, outDir, tag = "main"] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
const TOKEN = "stand-in-token-for-the-audit-drawing-0000";
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
process.env.INTERNAL_COSTS_TOKEN = TOKEN;

function parseLine(line) {
  const out = []; let cur = ""; let q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) { if (c === '"') { if (line[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; }
    else if (c === '"') q = true; else if (c === ",") { out.push(cur); cur = ""; } else cur += c;
  }
  out.push(cur);
  return out;
}
const cache = new Map();
function rowsOf(table) {
  if (cache.has(table)) return cache.get(table);
  const p = path.join(csvDir, `${table}.csv`);
  if (!fs.existsSync(p)) return null;
  const lines = fs.readFileSync(p, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = parseLine(lines[0]);
  const ix = (k) => head.indexOf(k);
  const rows = lines.slice(1).map(parseLine).map((f) => ({
    entity: f[ix("entity")], variable: f[ix("variable")], ts_utc: f[ix("ts_utc")], value: Number(f[ix("value")]),
    unit: f[ix("unit")] ?? "", freq: f[ix("freq")] ?? "",
  }));
  rows.sort((a, b) => (a.entity < b.entity ? -1 : a.entity > b.entity ? 1 : a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : a.ts_utc > b.ts_utc ? 1 : 0));
  cache.set(table, rows);
  return rows;
}
const asked = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const tn = u.searchParams.get("table_name") ?? "";
  if (u.pathname.endsWith("/series") && tn.startsWith("eq.")) {
    const rows = rowsOf(tn.slice(3));
    if (rows) {
      const off = Number(u.searchParams.get("offset") ?? 0), lim = Number(u.searchParams.get("limit") ?? 1000);
      asked.push(`served ${tn.slice(3)} offset ${off}`);
      return new Response(JSON.stringify(rows.slice(off, off + lim)), { status: 200, headers: { "content-type": "application/json" } });
    }
  }
  asked.push(`refused ${String(url)}`);
  return new Response("stand-in: not held", { status: 404 });
};
console.error = () => {};
console.warn = () => {};

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
const words = (s) => ent(s.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/g, "").replace(/<title>/g, " [hover: ").replace(/<\/title>/g, "] ").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
function figures(html) {
  const out = [];
  for (const m of html.matchAll(/data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([^<]*)</g)) out.push({ key: ent(m[1]), raw: ent(m[2]), shown: ent(m[3]) });
  return out;
}
const held = (html) => [...html.matchAll(/data-license-held="([^"]*)"/g)].length;

for (const [name, rel] of [["shape-premium", "app/reports/draft/shape-premium/page.tsx"], ["ai-gigawatts", "app/reports/draft/ai-gigawatts/page.tsx"]]) {
  try {
    const Page = (await imp(rel)).default;
    const html = renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve({ token: TOKEN }) })));
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.html`), html);
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.txt`), words(html) + "\n");
    fs.writeFileSync(path.join(outDir, `${tag}_${name}_n.json`), JSON.stringify(figures(html), null, 1));
    console.log(`${name}: ${html.length} bytes; ${figures(html).length} figures; ${held(html)} drawn as license needed; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
  } catch (e) {
    console.log(`${name}: failed ${String(e?.stack ?? e).slice(0, 800)}`);
  }
}
fs.writeFileSync(path.join(outDir, `${tag}_asked.txt`), asked.join("\n") + "\n");
