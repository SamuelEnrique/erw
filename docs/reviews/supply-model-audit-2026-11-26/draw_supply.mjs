// Session 10222 (supply audit): /supply drawn to HTML with the site's own code (the page file's default export, no
// build, no server, no request). Writes every figure the page marks (data-n), every hover (title) and the visible text.
// node --import ./scripts/tsx-register.mjs ../runs/c10222/draw_supply.mjs <out prefix> [query ...]   (run from site/)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const React = await import(pathToFileURL(req.resolve("react")).href);
const asked = [];
globalThis.fetch = async (url) => { asked.push(String(url)); throw new Error("no request in this audit"); };
async function resolveTree(node) {
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  const t = node.type;
  if (typeof t === "function" && t.constructor && t.constructor.name === "AsyncFunction") return resolveTree(await t(node.props));
  if (node.props && node.props.children !== undefined) return React.cloneElement(node, undefined, ...[].concat(await resolveTree(node.props.children)));
  return node;
}
const Page = (await import(pathToFileURL(path.join(site, "app", "supply", "page.tsx")).href)).default;
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const prefix = process.argv[2];
const queries = process.argv.slice(3);
if (!queries.length) queries.push("");
for (const q of queries) {
  const sp = Object.fromEntries(new URLSearchParams(q));
  const el = await Page({ searchParams: Promise.resolve(sp) });
  const html = renderToStaticMarkup(await resolveTree(el));
  const name = q ? q.replace(/[=&,]/g, "_") : "default";
  const figs = [...html.matchAll(/data-n="([^"]*)"[^>]*>([^<]*)</g)].map((m) => [unq(m[1]), unq(m[2])]);
  const cfigs = [...html.matchAll(/data-cn="([^"]*)"[^>]*>([^<]*)</g)].map((m) => [unq(m[1]), unq(m[2])]);
  const titles = [...html.matchAll(/title="([^"]*)"/g)].map((m) => unq(m[1]));
  const text = unq(html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  fs.writeFileSync(`${prefix}_${name}_figures.json`, JSON.stringify({ n: figs, cn: cfigs }, null, 0));
  const em = html.split(String.fromCharCode(0x2014)).length - 1;
  fs.writeFileSync(`${prefix}_${name}.txt`, [`/supply?${q}: ${html.length} characters, ${figs.length} marked figures, ${cfigs.length} country figures, ${titles.length} titles; em dashes: ${em}; requests refused: ${asked.length}`, "", "== titles", ...titles, "", "== visible text", text].join("\n"));
  console.log(`/supply?${q}: ${figs.length} figures, ${cfigs.length} country figures, ${titles.length} titles -> ${prefix}_${name}.*`);
}
