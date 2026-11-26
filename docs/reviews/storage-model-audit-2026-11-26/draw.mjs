// Session 10212 (storage audit): /storage (its three tabs) and /storage/places drawn to HTML with the site's own code, no
// build and no database. The page's live reads (storage_capacity, storage_daily_cycle, eia930_all_storage,
// caiso_battery_storage, storage_buildout_monthly) are answered from fixture.json (rows of the trial folder's tables,
// rebuilt by the page's own builders from the main copy's inputs, read only); every other request is refused. Run from site/:
//   node --import ../runs/c10212/register.mjs ../runs/c10212/draw.mjs <fixture.json> <out dir> [tag] [now ISO]
// Writes, for each view, <tag>_<name>.html, <tag>_<name>.txt (visible words), <tag>_<name>_n.json (every data-check
// figure with its key and raw value, and every data-fig / data-row figure) and <tag>_asked.txt (every read the page made).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [fxPath, outDir, tag = "main", nowIso = "2026-11-05T12:00:00Z"] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
const fx = JSON.parse(fs.readFileSync(fxPath, "utf-8"));
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const NOW = Date.parse(nowIso);
Date.now = () => NOW;
const RealDate = Date;
globalThis.Date = class extends RealDate {
  constructor(...a) { if (a.length === 0) super(NOW); else super(...a); }
  static now() { return NOW; }
};
const asked = [];
const strip = (s, p) => (s ?? "").startsWith(p) ? s.slice(p.length) : null;
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  const q = u.searchParams;
  const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
  const kind = u.pathname.endsWith("/series") ? "series" : u.pathname.endsWith("/entities") ? "entities" : "";
  if (!kind || !fx[name]) { asked.push(`refused ${u.pathname} ${name}`); return new Response("stand-in: not held", { status: 404 }); }
  let rows = fx[name];
  const ent = strip(q.get("entity"), "eq.");
  const v = strip(q.get("variable"), "eq.");
  const ts = q.get("ts_utc") ?? "";
  if (ent) rows = rows.filter((r) => r.entity === ent);
  if (v) rows = rows.filter((r) => r.variable === v);
  if (ts.startsWith("gte.")) rows = rows.filter((r) => r.ts_utc >= ts.slice(4));
  if (ts.startsWith("in.(")) { const set = new Set(ts.slice(4, -1).split(",").map((s) => s.replace(/"/g, ""))); rows = rows.filter((r) => set.has(r.ts_utc)); }
  if ((q.get("order") ?? "") === "ts_utc.desc") rows = [...rows].sort((a, b) => b.ts_utc.localeCompare(a.ts_utc));
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 100000);
  asked.push(`${kind} ${name} ${ent ?? ""} ${v ?? ""} ${ts}: ${rows.length} (offset ${off})`);
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
  for (const m of html.matchAll(/data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([^<]*)</g)) out[ent(m[1])] = { raw: ent(m[2]), shown: ent(m[3]) };
  for (const m of html.matchAll(/data-(fig|row)="([^"]+)"[^>]*>([^<]*)</g)) out[`${m[1]}:${ent(m[2])}`] = { shown: ent(m[3]) };
  return out;
}

const Page = (await imp("app/storage/page.tsx")).default;
const Places = (await imp("app/storage/places/page.tsx")).default;
const views = [
  ["default", Page, {}], ["buildout", Page, { tab: "buildout" }], ["buildout_ercot", Page, { tab: "buildout", grid: "ercot" }],
  ["buildout_caiso_mwh", Page, { tab: "buildout", grid: "caiso", measure: "mwh" }], ["owners", Page, { tab: "owners" }], ["places", Places, {}],
];
for (const [name, P, sp] of views) {
  try {
    const html = renderToStaticMarkup(await resolveTree(await P({ searchParams: Promise.resolve(sp) })));
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.html`), html);
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.txt`), words(html) + "\n");
    fs.writeFileSync(path.join(outDir, `${tag}_${name}_n.json`), JSON.stringify(figures(html), null, 1));
    console.log(`${name}: ${html.length} bytes; ${Object.keys(figures(html)).length} figures; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
  } catch (e) {
    console.log(`${name}: failed ${String(e?.stack ?? e).slice(0, 600)}`);
  }
}
fs.writeFileSync(path.join(outDir, `${tag}_asked.txt`), asked.join("\n") + "\n");
process.exitCode = 0;
