// Session 10227 (play audit): /play/battery (its three modes), the battery game's end table (Normal and Hard, after the
// perfect play and a naive one on the 2023-08-10 level) and /play/ev drawn to HTML with the site's own code, no build and
// no database: every network read is refused and listed. Run from site/:
//   node --import ../runs/c10227/register.mjs ../runs/c10227/draw.mjs <out dir> <tag>
// Writes <tag>_<view>.html and <tag>_<view>.txt (the visible words, then every title attribute, the hovers) and
// <tag>_asked.txt.
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
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const asked = [];
globalThis.fetch = async (url) => { asked.push(`refused ${String(url)}`); return new Response("stand-in: not held", { status: 404 }); };
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
const titles = (s) => [...s.matchAll(/title="([^"]*)"/g)].map((m) => ent(m[1]));
fs.mkdirSync(outDir, { recursive: true });
const save = (name, html) => {
  fs.writeFileSync(path.join(outDir, `${tag}_${name}.html`), html);
  fs.writeFileSync(path.join(outDir, `${tag}_${name}.txt`), `${words(html)}\n\n--- hovers ---\n${titles(html).join("\n")}\n`);
  console.log(`${name}: ${html.length} characters, ${titles(html).length} hovers`);
};

const battery = await imp("app/play/battery/page.tsx");
for (const mode of ["easy", "normal", "hard"]) {
  const html = renderToStaticMarkup(await resolveTree(await battery.default({ searchParams: Promise.resolve({ mode }) })));
  save(`battery_${mode}`, html);
}

// the end table, drawn as the game draws it after a play
const B = await imp("lib/battery.ts");
const G = await imp("app/play/battery/Game.tsx");
const levels = JSON.parse(fs.readFileSync(path.join(site, "data", "battery_levels.json"), "utf-8")).levels;
const L = levels.find((l) => l.date === "2023-08-10");
for (const mode of ["normal", "hard"]) {
  const rules = B.rulesOf(B.DEFAULT_SETTINGS, mode, []);
  const best = B.optimum(L.price, rules);
  const naive = L.price.map((_, i) => (i >= 8 && i < 20 ? 1 : i >= 68 && i < 80 ? -1 : 0));
  const html = renderToStaticMarkup(React.createElement(G.EndTable, { mine: B.tally(L.price, naive, rules), perfect: B.tally(L.price, best.actions, rules), none: B.noBattery(L.price, rules), rules, big: false }));
  save(`endtable_${mode}`, html);
}

const ev = await imp("app/play/ev/page.tsx");
save("ev", renderToStaticMarkup(await resolveTree(ev.default())));
fs.writeFileSync(path.join(outDir, `${tag}_asked.txt`), asked.join("\n") + "\n");
console.log(`network reads refused: ${asked.length}`);
