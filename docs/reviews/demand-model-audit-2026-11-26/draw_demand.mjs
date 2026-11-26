// Session 10214 (demand audit): /demand drawn to HTML with the site's own code (the page file's default export, no
// build, no server, no request). Writes every figure the page marks (data-n), every hover (title, data-tip) and the
// visible text, for the addresses named.
// node --import ./scripts/tsx-register.mjs ../runs/c10214/draw_demand.mjs <out prefix> [query ...]   (run from site/)
// a query is like "area=pjm&rank=peak" or "view=weather"; none means the default address /demand
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const React = await import(pathToFileURL(req.resolve("react")).href);
// every request refused: the page draws from its committed files; a live read (the downloads' catalogue) fails as a
// failed read does on the site
const asked = [];
globalThis.fetch = async (url) => { asked.push(String(url)); throw new Error("no request in this audit"); };
/** An async server component cannot be drawn by renderToStaticMarkup: each one in the tree is awaited first. */
async function resolveTree(node) {
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  const t = node.type;
  if (typeof t === "function" && t.constructor && t.constructor.name === "AsyncFunction") return resolveTree(await t(node.props));
  if (node.props && node.props.children !== undefined) return React.cloneElement(node, undefined, ...[].concat(await resolveTree(node.props.children)));
  return node;
}
const Page =(await import(pathToFileURL(path.join(site, "app", "demand", "page.tsx")).href)).default;
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const prefix = process.argv[2];
const queries = process.argv.slice(3);
if (!queries.length) queries.push("");
for (const q of queries) {
  const sp = Object.fromEntries(new URLSearchParams(q));
  const el = await Page({ searchParams: Promise.resolve(sp) });
  const html = renderToStaticMarkup(await resolveTree(el));
  const name = q ? q.replace(/[=&]/g, "_") : "default";
  const figs = [...html.matchAll(/data-n="([^"]*)"[^>]*>([^<]*)</g)].map((m) => [unq(m[1]), unq(m[2])]);
  const titles = [...html.matchAll(/title="([^"]*)"/g)].map((m) => unq(m[1]));
  const tips = [...html.matchAll(/data-tip="([^"]*)"/g)].map((m) => unq(m[1]));
  const text = unq(html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  fs.writeFileSync(`${prefix}_${name}_figures.json`, JSON.stringify(figs, null, 0));
  const em = html.split(String.fromCharCode(0x2014)).length - 1;
  fs.writeFileSync(`${prefix}_${name}.txt`, [`/demand?${q}: ${html.length} characters, ${figs.length} marked figures, ${titles.length} titles, ${tips.length} chart tips; em dashes: ${em}`, "", "== titles", ...titles, "", "== chart tips", ...tips, "", "== visible text", text].join("\n"));
  console.log(`/demand?${q}: ${figs.length} figures, ${titles.length} titles, ${tips.length} tips -> ${prefix}_${name}.*`);
}
