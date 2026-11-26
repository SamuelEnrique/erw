// Session 10228: the company pages drawn to HTML with the site's own code (app/companies/page.tsx, app/companies/[id]/
// page.tsx, and the deals page's companies tab app/companies/view.tsx), from the page files on disk
// (site/data/companies/), so the audit reads what a visitor is printed and a words branch's sentences are read as drawn.
// Run from site/:
//   node --import ../runs/c10228/register.mjs ../runs/c10228/draw_companies.mjs <out prefix> [needle ...]
// The companies tab's live-set read is answered from ../runs/c10228/energy_companies.json when that file exists (the
// main copy's energy_companies.csv as the live set would serve it); every other read answers no rows. No request leaves
// the machine. Prints each drawing's size and whether an em dash is in it; for each needle the sentence that holds it,
// or MISSING (exit 1).
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
const ecPath = path.join(site, "..", "runs", "c10228", "energy_companies.json");
const ec = fs.existsSync(ecPath) ? JSON.parse(fs.readFileSync(ecPath, "utf-8")) : [];

process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const json = (rows) => new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json", "content-range": `0-${Math.max(0, rows.length - 1)}/${rows.length}` } });
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = u.searchParams;
  const t = (q.get("table_name") ?? "").replace(/^eq\./, "");
  let rows = [];
  if (u.pathname.endsWith("/entities") && t === "energy_companies") rows = ec;
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
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

let text = "";
const keep = (name, html) => {
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  const t = words(html);
  fs.writeFileSync(`${prefix}_${name}.txt`, t);
  text += " " + t;
  console.log(`${name}: ${html.length} bytes drawn; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
};
const Index = (await imp("app/companies/page.tsx")).default;
const One = (await imp("app/companies/[id]/page.tsx")).default;
const draws = [
  ["index", () => Index({ searchParams: Promise.resolve({}) })],
  ["index_policy", () => Index({ searchParams: Promise.resolve({ has: "policy" }) })],
  ["fpl", () => One({ params: Promise.resolve({ id: "eia-6452" }) })],
  ["google", () => One({ params: Promise.resolve({ id: "eia-64846" }) })],
  ["ceg", () => One({ params: Promise.resolve({ id: "eia-65506" }) })],
];
if (ec.length) {
  const { CompaniesView } = await imp("app/companies/view.tsx");
  draws.push(["tab", () => CompaniesView()]);
}
for (const [name, f] of draws) {
  try {
    keep(name, renderToStaticMarkup(await resolveTree(await f())));
  } catch (e) { console.log(`${name}: not drawn: ${String(e.stack).slice(0, 600)}`); }
}

let missing = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { missing++; console.log(`MISSING: ${n}`); continue; }
  const a = Math.max(text.lastIndexOf(". ", i) + 2, i - 300), b = text.indexOf(". ", i + n.length);
  console.log(`READ: ...${text.slice(a, b < 0 ? i + n.length + 200 : b + 1)}`);
}
process.exitCode = missing ? 1 : 0;
