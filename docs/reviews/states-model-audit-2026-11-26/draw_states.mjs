// Session 10223 (states audit): /states drawn to HTML with the site's own code (the page file's default export, no
// build, no server, every request refused). Writes every figure the page marks (data-fig, data-not-held, data-none),
// every hover (title) and the visible text, for the addresses named.
// node --import ./scripts/tsx-register.mjs ../runs/c10223/draw_states.mjs <out prefix> [query ...]   (run from site/)
// a query is like "a=CA&b=WV"; none means the default address /states
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
const Page = (await import(pathToFileURL(path.join(site, "app", "states", "page.tsx")).href)).default;
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const prefix = process.argv[2];
const queries = process.argv.slice(3);
if (!queries.length) queries.push("");
for (const q of queries) {
  const sp = Object.fromEntries(new URLSearchParams(q));
  const el = await Page({ searchParams: Promise.resolve(sp) });
  const html = renderToStaticMarkup(await resolveTree(el));
  const name = q ? q.replace(/[=&]/g, "_") : "default";
  const figs = [...html.matchAll(/<span([^>]*)data-fig="([^"]*)"[^>]*>([^<]*)</g)].map((m) => {
    const t = /title="([^"]*)"/.exec(m[1]);
    return [unq(m[2]), unq(m[3]), t ? unq(t[1]) : ""];
  });
  const notHeld = [...html.matchAll(/<span([^>]*)data-not-held="([^"]*)"[^>]*>([^<]*)</g)].map((m) => {
    const t = /title="([^"]*)"/.exec(m[1]);
    return [unq(m[2]), unq(m[3]), t ? unq(t[1]) : ""];
  });
  const none = [...html.matchAll(/data-none="([^"]*)"/g)].map((m) => unq(m[1]));
  const titles = [...html.matchAll(/title="([^"]*)"/g)].map((m) => unq(m[1]));
  const text = unq(html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));
  fs.writeFileSync(`${prefix}_${name}.html`, html);
  fs.writeFileSync(`${prefix}_${name}_figures.json`, JSON.stringify({ figs, notHeld, none }, null, 0));
  const em = html.split(String.fromCharCode(0x2014)).length - 1;
  fs.writeFileSync(`${prefix}_${name}.txt`, [`/states?${q}: ${html.length} characters, ${figs.length} marked figures, ${notHeld.length} not held, ${none.length} none, ${titles.length} titles; em dashes: ${em}; requests asked: ${asked.length}`, "", "== titles", ...titles, "", "== visible text", text].join("\n"));
  console.log(`/states?${q}: ${figs.length} figures, ${notHeld.length} not held, ${none.length} none, ${titles.length} titles -> ${prefix}_${name}.*`);
}
process.exitCode = 0;
