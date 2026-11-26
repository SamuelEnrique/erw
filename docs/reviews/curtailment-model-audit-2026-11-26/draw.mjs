// Session 10210 (curtailment audit): /curtailment and /curtailment/where-when drawn to HTML with the site's own code, no
// build and no database. The page's two live reads (iso_curtailment_monthly and the grid's daily table) are answered
// from fixture.json (rows of the main copy's tables, read only); every other request is refused. Run from site/:
//   node --import ../runs/c10210/register.mjs ../runs/c10210/draw.mjs <fixture.json> <out dir> [tag]
// Writes, for each address, <tag>_<name>.html, <tag>_<name>.txt (visible words) and <tag>_<name>_n.json (every data-n
// and data-fig figure with its key), and <tag>_asked.txt (every read the page made).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [fxPath, outDir, tag = "main"] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
const fx = JSON.parse(fs.readFileSync(fxPath, "utf-8"));
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const NOW = Date.parse("2026-11-26T12:00:00Z");
Date.now = () => NOW;
const asked = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = u.searchParams;
  const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
  if (!u.pathname.endsWith("/series") || !fx[name]) { asked.push(`refused ${u.pathname} ${name}`); return new Response("stand-in: not held", { status: 404 }); }
  const ent = (q.get("entity") ?? "").replace(/^eq\./, "");
  const v = (q.get("variable") ?? "").replace(/^eq\./, "");
  const since = (q.get("ts_utc") ?? "gte.").replace(/^gte\./, "");
  const rows = fx[name].filter((r) => (!ent || r.entity === ent) && (!v || r.variable === v) && r.ts_utc >= since);
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 100000);
  asked.push(`${name} ${ent} ${v} since ${since}: ${rows.length}`);
  return new Response(JSON.stringify(rows.slice(off, off + lim)), { status: 200, headers: { "content-type": "application/json" } });
};
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
  for (const m of html.matchAll(/data-(n|fig)="([^"]+)"[^>]*>([^<]*)</g)) out[ent(m[2])] = ent(m[3]);
  return out;
}

const Page = (await imp("app/curtailment/page.tsx")).default;
const WW = (await imp("app/curtailment/where-when/page.tsx")).default;
const views = [
  ["default", Page, {}], ["spp", Page, { grid: "spp" }], ["ercot", Page, { grid: "ercot" }], ["isone", Page, { grid: "isone" }], ["nyiso", Page, { grid: "nyiso" }],
  ["caiso2025", Page, { period: "2025" }], ["ww", WW, {}], ["ww_both", WW, { fuel: "both" }], ["ww_sp15", WW, { a: "caiso", b: "caiso:TH_SP15_GEN-APND" }],
];
for (const [name, P, sp] of views) {
  try {
    const html = renderToStaticMarkup(await resolveTree(await P({ searchParams: Promise.resolve(sp) })));
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.html`), html);
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.txt`), words(html) + "\n");
    fs.writeFileSync(path.join(outDir, `${tag}_${name}_n.json`), JSON.stringify(figures(html), null, 1));
    console.log(`${name}: ${html.length} bytes; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
  } catch (e) {
    console.log(`${name}: failed ${String(e?.stack ?? e).slice(0, 600)}`);
  }
}
fs.writeFileSync(path.join(outDir, `${tag}_asked.txt`), asked.join("\n") + "\n");
process.exitCode = 0;
