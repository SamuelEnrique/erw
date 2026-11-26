// Session 10211: the datacenter tracker drawn to HTML with the site's own code, so a words branch's new sentences are read
// as a reader meets them. Run from site/:
//   node --import ../runs/c10211/register.mjs ../runs/c10211/draw_tracker.mjs <rows dir> <out prefix> <needle> [needle ...]
// Draws (1) app/datacenters/page.tsx whole, both views, as a visitor meets it today (datacenter_facilities held; the live
// set's requests answered from the rows dir: the queue sites and active positions; every other read answers no rows), and
// (2) the facility components the hold keeps off the page, drawn with the rows as the page would draw them once the hold
// allows (Body with its top block and list, Rollups, Timeline, DcCharts). Prints, for each needle, the sentence of the
// drawn text that holds it, or MISSING; exit 1 when a needle is missing. No request leaves the machine.
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
const read = (n) => JSON.parse(fs.readFileSync(path.join(rowsDir, n), "utf-8"));
const facilities = read("datacenter_facilities.json"), sites = read("queue_sites.json"), active = read("queue_active.json");

process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const json = (rows) => new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json" } });
globalThis.fetch = async (url) => {
  const q = new URL(String(url)).searchParams;
  const t = (q.get("table_name") ?? "").replace(/^eq\./, "");
  let rows = [];
  if (t.endsWith("_interconnection_queue")) {
    if (q.get("status") === "eq.active") rows = active.filter((r) => r.table_name === t);
    else {
      const pat = new RegExp((q.get("name") ?? q.get("extra->>fuel_technology") ?? "").replace(/^imatch\./, ""), "i");
      const field = q.get("name") ? (r) => r.name ?? "" : (r) => r.extra?.fuel_technology ?? "";
      rows = sites.filter((r) => r.table_name === t && pat.test(field(r)));
    }
  }
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 1000);
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
const Page = (await imp("app/datacenters/page.tsx")).default;
for (const view of ["facilities", "grids"]) {
  keep(`page_${view}`, renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve(view === "grids" ? { view: "grids" } : {}) }))));
}
const { Body, toFacility } = await imp("app/datacenters/Body.tsx");
const { Rollups } = await imp("app/datacenters/Rollups.tsx");
const { Timeline } = await imp("app/datacenters/Timeline.tsx");
const { DcCharts } = await imp("app/datacenters/DcCharts.tsx");
const h = React.createElement;
for (const [name, el] of [["body", Body({ rows: facilities.map(toFacility), today: "2026-11-26" })], ["rollups", h(Rollups, { rows: facilities })],
  ["timeline", h(Timeline, { rows: facilities })], ["charts", h(DcCharts, { rows: facilities })]]) {
  try { keep(`unheld_${name}`, renderToStaticMarkup(await resolveTree(el))); } catch (e) { console.log(`unheld_${name}: not drawn: ${String(e.message).slice(0, 120)}`); }
}

let missing = 0;
for (const n of needles) {
  const i = text.indexOf(n);
  if (i < 0) { missing++; console.log(`MISSING: ${n}`); continue; }
  const a = Math.max(text.lastIndexOf(". ", i) + 2, i - 400), b = text.indexOf(". ", i + n.length);
  console.log(`READ: ...${text.slice(a, b < 0 ? i + n.length + 200 : b + 1)}`);
}
process.exitCode = missing ? 1 : 0;
