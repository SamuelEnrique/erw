// Session 1173: the Grid pack's figures read on production through the internal view (walk-1161.mjs's door and parsers).
// Usage: node docs/brand/review-1173/walk-1173.mjs <the main checkout, whose .env holds INTERNAL_COSTS_TOKEN> <out dir>.
// Run 24 October 2026 at 00:58 UTC (the 18 addresses, then the five Gravity tabs of PJM, MISO, NYISO, ISO-NE and SPP as a
// second run); walk-1173-prod.json beside it is cut from the two records (panels, the first keys outside them, the sentences
// the pack quotes). The token is posted, never printed or put in an address.
import fs from "node:fs";
import path from "node:path";
const repo = process.argv[2];
const out = process.argv[3];
const url = "file:///" + path.join(repo, "site/scripts/browser.mjs").replace(/\\/g, "/");
const { env, unlockPost } = await import(url);
const base = "https://erw-flame.vercel.app";
const u = await unlockPost(base, env("INTERNAL_COSTS_TOKEN"));
const cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log("no cookie"); process.exit(1); }
fs.mkdirSync(out, { recursive: true });
const pages = [
  "/grid", "/grid?grid=ercot", "/grid?grid=caiso", "/grid?grid=spp", "/grid?grid=nyiso", "/grid?grid=isone",
  "/grid?grid=ercot&view=network", "/grid?view=network", "/grid?grid=caiso&view=network",
  "/grid?grid=ercot&view=gravity&shape=gravity", "/grid?grid=caiso&view=gravity&shape=gravity", "/grid?grid=us48&view=gravity&shape=gravity",
  "/grid?grid=ercot&view=clean", "/grid?grid=caiso&view=clean", "/grid/caiso/alerts",
  "/grid?grid=ercot&view=network&net=day&t=2021-02-15", "/network", "/mix",
  "/grid?grid=pjm&view=gravity&shape=gravity", "/grid?grid=miso&view=gravity&shape=gravity", "/grid?grid=nyiso&view=gravity&shape=gravity",
  "/grid?grid=isone&view=gravity&shape=gravity", "/grid?grid=spp&view=gravity&shape=gravity",
];
const dec = (s) => s.replace(/&amp;/g, "&").replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;|&#160;/g, " ");
const text = (h) => dec(h.replace(/<script[\s\S]*?<\/script>/g, " ").replace(/<style[\s\S]*?<\/style>/g, " ").replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
function element(html, at) {
  const open = html.lastIndexOf("<", at);
  const tag = html.slice(open + 1).match(/^([a-zA-Z0-9]+)/)[1];
  const re = new RegExp(`<(/?)${tag}(?=[\\s>/])[^>]*>`, "g");
  re.lastIndex = open;
  let depth = 0, m;
  while ((m = re.exec(html))) {
    if (m[0].endsWith("/>")) continue;
    depth += m[1] ? -1 : 1;
    if (depth === 0) return html.slice(open, m.index + m[0].length);
  }
  return html.slice(open);
}
function figures(h) {
  const res = [];
  for (const m of h.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)) res.push({ key: dec(m[1]), raw: dec(m[2]), shown: text(m[3]) });
  return res;
}
const record = [];
for (const p of pages) {
  const t0 = Date.now();
  const r = await fetch(base + p, { headers: { Cookie: cookie, "User-Agent": "erw-check (node)" }, redirect: "follow" });
  const html = await r.text();
  const ms = Date.now() - t0;
  const name = p.replace(/[^a-z0-9]+/gi, "_").replace(/^_|_$/g, "") || "root";
  fs.writeFileSync(path.join(out, `${name}.html`), html);
  fs.writeFileSync(path.join(out, `${name}.txt`), text(html));
  const panels = [];
  const seen = new Set();
  for (const m of html.matchAll(/data-grid-panel="([^"]+)"/g)) {
    if (seen.has(m[1])) continue;
    seen.add(m[1]);
    const el = element(html, m.index);
    panels.push({ panel: m[1], figures: figures(el), text: text(el).slice(0, 3000) });
  }
  const all = figures(html);
  const held = [...html.matchAll(/data-license-held="([^"]+)"/g)].length;
  const rec = { address: p, status: r.status, ms, final: r.url.replace(base, ""), bytes: html.length, keys: all.length, held, panels, all,
    h2: [...html.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/g)].map((x) => text(x[1])).slice(0, 40) };
  record.push(rec);
  console.log(`${r.status} ${ms} ms ${p} -> ${rec.final} | ${html.length} bytes | ${all.length} keys | ${held} held | panels ${panels.map((x) => `${x.panel}:${x.figures.length}`).join(" ")}`);
}
fs.writeFileSync(path.join(out, "walk1173.json"), JSON.stringify({ at: new Date().toISOString(), base, record }, null, 1));
console.log("at " + new Date().toISOString());
