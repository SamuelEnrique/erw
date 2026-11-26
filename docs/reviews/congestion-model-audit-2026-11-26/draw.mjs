// Session 10220 (congestion audit): /congestion drawn to HTML with the site's own code, no build, no database (the page
// reads only site/data/conditions/congestion.json). Run from site/:
//   node --import ./scripts/tsx-register.mjs ../runs/c10220/draw.mjs <out dir> [tag]
// Writes, for each address, <tag>_<name>.html, <tag>_<name>.txt (visible words), <tag>_<name>_fig.json (every data-fig
// figure with its key and words) and <tag>_<name>_titles.txt (every hover, title attribute or Hint words).
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [outDir, tag = "main"] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);
globalThis.fetch = async () => new Response("stand-in: no request", { status: 404 });
console.error = () => {};
fs.mkdirSync(outDir, { recursive: true });

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
// In page order, as a list: the two ranked lists use the same keys (h-0 ...), so a map would lose the first list.
function figures(html) {
  const out = [];
  const re = /data-(fig|not-held)="([^"]+)"/g;
  let m;
  while ((m = re.exec(html))) {
    const start = html.indexOf(">", m.index) + 1;
    // the figure's words: up to the close of its outer span (a Num inside adds one level)
    let depth = 1, i = start;
    while (depth > 0 && i < html.length) {
      const o = html.indexOf("<span", i), c = html.indexOf("</span>", i);
      if (c < 0) break;
      if (o >= 0 && o < c) { depth++; i = o + 5; } else { depth--; i = c + 7; }
    }
    out.push([m[1], ent(m[2]), words(html.slice(start, i - 7))]);
  }
  return out;
}
function titles(html) {
  const t = [];
  for (const m of html.matchAll(/title="([^"]*)"/g)) t.push(ent(m[1]));
  return [...new Set(t)];
}

const Page = (await imp("app/congestion/page.tsx")).default;
const views = [
  ["default", {}], ["caiso", { op: "caiso" }], ["spp_all", { op: "spp", year: "all" }],
  ["two", { a: "spp:SPPNORTH_HUB", b: "caiso:TH_SP15_GEN-APND" }],
];
for (const [name, sp] of views) {
  try {
    const html = renderToStaticMarkup(await resolveTree(await Page({ searchParams: Promise.resolve(sp) })));
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.html`), html);
    fs.writeFileSync(path.join(outDir, `${tag}_${name}.txt`), words(html) + "\n");
    fs.writeFileSync(path.join(outDir, `${tag}_${name}_fig.json`), JSON.stringify(figures(html), null, 1));
    fs.writeFileSync(path.join(outDir, `${tag}_${name}_titles.txt`), titles(html).join("\n") + "\n");
    console.log(`${name}: ${html.length} bytes; em dash ${html.includes(String.fromCharCode(0x2014)) ? "FOUND" : "none"}`);
  } catch (e) {
    console.log(`${name}: failed ${String(e?.stack ?? e).slice(0, 800)}`);
  }
}
process.exitCode = 0;
