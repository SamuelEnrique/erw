// Session 10207: the severance page drawn to HTML with the site's own code, both tabs, so a words branch's new sentences
// are read as a reader meets them (in the drawn text, the decisions' tips included). Run from site/:
//   node --import ../runs/c10207/register.mjs ../runs/c10207/draw_words.mjs <eia_fuel_spot_prices.csv> <out prefix> <needle> [needle ...]
// Prints, for each needle, the sentence of the drawn text that holds it, or MISSING. Exit 1 when a needle is missing.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [csvPath, prefix, ...needles] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);

const lines = fs.readFileSync(csvPath, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const cols = lines[0].split(",");
const ix = (c) => cols.indexOf(c);
const by = {};
for (const l of lines.slice(1)) {
  const r = l.split(",");
  (by[r[ix("entity")]] ??= []).push({ entity: r[ix("entity")], variable: r[ix("variable")], ts_utc: r[ix("ts_utc")], value: Number(r[ix("value")]), unit: r[ix("unit")], freq: r[ix("freq")] });
}
for (const k of Object.keys(by)) by[k].sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
globalThis.fetch = async (url) => {
  const q = new URL(String(url)).searchParams;
  if (q.get("table_name") !== "eq.eia_fuel_spot_prices") return new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
  const since = (q.get("ts_utc") ?? "gte.").replace(/^gte\./, "");
  const rows = (by[(q.get("entity") ?? "").replace(/^eq\./, "")] ?? []).filter((r) => r.variable === (q.get("variable") ?? "").replace(/^eq\./, "") && r.ts_utc >= since);
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 1000);
  return new Response(JSON.stringify(rows.slice(off, off + lim)), { status: 200, headers: { "content-type": "application/json" } });
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
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

const Page = (await imp("app/severance/page.tsx")).default;
let text = "";
for (const tab of ["calculator", "lease"]) {
  const html = renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve(tab === "lease" ? { tab: "lease" } : {}) })));
  fs.writeFileSync(`${prefix}_${tab}.html`, html);
  const t = words(html);
  fs.writeFileSync(`${prefix}_${tab}.txt`, t);
  text += " " + t;
  console.log(`${tab}: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
}
let missing = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { missing++; console.log(`MISSING: ${n}`); continue; }
  const a = Math.max(text.lastIndexOf(". ", i) + 2, i - 400), b = text.indexOf(". ", i + n.length);
  console.log(`READ: ...${text.slice(a, b < 0 ? i + n.length + 200 : b + 1)}`);
}
process.exitCode = missing ? 1 : 0;
