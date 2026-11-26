// Session 10215: the deal pages drawn to HTML with the site's own code, so a words branch's new sentences are read as a
// reader meets them. Run from site/:
//   node --import ../runs/c10215/register.mjs ../runs/c10215/draw_deals.mjs <rows dir> <out prefix> <needle> [needle ...]
// With ERW_DRAW_UNHELD=1 the license file is read without energy_deals (unhold-stub.mjs) and the live set's read of the
// deals is answered from <rows dir>/energy_deals.json: the pages as they draw once the hold allows. Without it, the pages
// as a visitor meets them today (every deal view draws the hold). Draws app/deals/page.tsx for the first tab, the tracker,
// the comparables, the AI view, the charts and the companies tab. Every other read answers no rows, except the
// catalogue's row count of energy_deals (583, the coverage file's). Prints, for each needle, the sentence of the drawn
// text that holds it, or MISSING; exit 1 when a needle is missing. No request leaves the machine.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [rowsDir, prefix, ...needles] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
const deals = JSON.parse(fs.readFileSync(path.join(rowsDir, "energy_deals.json"), "utf-8"));
const unheld = process.env.ERW_DRAW_UNHELD === "1";

process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const json = (rows) => new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json", "content-range": `0-${Math.max(0, rows.length - 1)}/${rows.length}` } });
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = u.searchParams;
  const t = (q.get("table_name") ?? "").replace(/^eq\./, "");
  let rows = [];
  if (u.pathname.endsWith("/events") && t === "energy_deals") rows = deals;
  if (u.pathname.endsWith("/catalogue")) rows = [{ table_name: "energy_deals", n_rows: 583, license: "public", in_live_set: "yes" }];
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 100000);
  return json(rows.slice(off, off + lim));
};
Date.now = () => Date.parse("2026-11-26T12:00:00Z");

async function resolveTree(node) {
  if (node == null || typeof node !== "object") return node;
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  if (typeof node.type === "function" && node.type.constructor?.name === "AsyncFunction") return resolveTree(await node.type(node.props));
  // the first tab's Body (a plain function of page.tsx, no hook) holds an async Cite: drawn here so its children resolve
  if (typeof node.type === "function" && node.type.name === "Body") return resolveTree(node.type(node.props));
  const kids = node.props?.children;
  if (kids === undefined) return node;
  const rk = await resolveTree(kids);
  return React.cloneElement(node, undefined, ...(Array.isArray(rk) ? rk : [rk]));
}
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

let text = "";
const keep = (name, html) => {
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  const t = words(html);
  fs.writeFileSync(`${prefix}_${name}.txt`, t);
  text += " " + t;
  console.log(`${name}: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}; held sentence ${t.includes("The hold covers every row") ? "drawn" : "not drawn"}`);
};
const Page = (await imp("app/deals/page.tsx")).default;
for (const [name, sp] of [["deals", {}], ["tracker", { tab: "tracker" }], ["comparables", { view: "comparables" }], ["ai", { view: "ai" }],
  ["ai_grid", { view: "ai", aby: "grid" }], ["charts", { view: "charts" }], ["companies", { tab: "companies" }]]) {
  try {
    keep(`${unheld ? "unheld" : "held"}_${name}`, renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve(sp) }))));
  } catch (e) { console.log(`${name}: not drawn: ${String(e.stack).slice(0, 400)}`); }
}

let missing = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { missing++; console.log(`MISSING: ${n}`); continue; }
  const a = Math.max(text.lastIndexOf(". ", i) + 2, i - 300), b = text.indexOf(". ", i + n.length);
  console.log(`READ: ...${text.slice(a, b < 0 ? i + n.length + 200 : b + 1)}`);
}
process.exitCode = missing ? 1 : 0;
