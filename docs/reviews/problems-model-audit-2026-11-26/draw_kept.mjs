// Session 10229 (problems audit): a set's page drawn to HTML with the site's own code from the live reads kept on
// 16 November 2026 (replication/problem_sets/live_reads.json and live_rows.csv), the clock set to the kept one, every
// other request refused, as site/scripts/problem-sets-figures.mjs replay serves them. Writes the page's HTML and its
// visible text, for the words to be read.
// node --import ./scripts/problem-sets-register.mjs ../runs/c10229/draw_kept.mjs <kept dir> <out prefix> <slug> [slug ...]   (from site/)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const site = process.cwd();
const [dirArg, prefix, ...slugs] = process.argv.slice(2);
const dir = path.resolve(dirArg);
const req = createRequire(path.join(site, "package.json"));
const { renderToStaticMarkup } = await import(pathToFileURL(req.resolve("react-dom/server")).href);
const React = await import(pathToFileURL(req.resolve("react")).href);
const NULL = "\\N", COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq"];
function parseCsvLine(line) {
  const out = []; let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) { if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c; }
    else if (c === '"') q = true; else if (c === ",") { out.push(cur); cur = ""; } else cur += c;
  }
  out.push(cur);
  return out;
}
const r = JSON.parse(fs.readFileSync(path.join(dir, "live_reads.json"), "utf-8"));
const kept = new Map(), byId = new Map(r.reads.map((x) => [x.id, x.address]));
for (const x of r.reads) kept.set(x.address, []);
const lines = fs.readFileSync(path.join(dir, "live_rows.csv"), "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const head = parseCsvLine(lines[0]);
for (const l of lines.slice(1)) {
  const c = parseCsvLine(l), o = {};
  head.forEach((k, i) => { o[k] = c[i] === NULL ? null : c[i]; });
  const row = {};
  for (const k of COLS) row[k] = k === "value" ? (o[k] === null ? null : Number(o[k])) : o[k];
  kept.get(byId.get(Number(o.read)))?.push(row);
}
process.env.SUPABASE_URL = "https://kept-reads.invalid";
process.env.SUPABASE_ANON_KEY = "kept";
const NOW = Date.parse(r.now);
Date.now = () => NOW;
const strip = (s) => { const x = new URL(s, "http://x"); x.searchParams.delete("offset"); return x.pathname + x.search; };
let refused = 0;
globalThis.fetch = async (input) => {
  const u = new URL(typeof input === "string" ? input : input.url);
  if (!u.pathname.startsWith("/rest/v1/")) { refused += 1; return new Response("not kept", { status: 404 }); }
  const address = u.pathname + u.search, offset = Number(u.searchParams.get("offset") ?? "0");
  if (!kept.has(address) && !(offset > 0)) { refused += 1; throw new Error(`a read that was not kept: ${address}`); }
  const rows = offset > 0 ? [] : [...kept.entries()].filter(([a]) => strip(a) === strip(address)).flatMap(([, x]) => x);
  return new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json" } });
};
async function resolveTree(node) {
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  const t = node.type;
  if (typeof t === "function" && t.constructor && t.constructor.name === "AsyncFunction") return resolveTree(await t(node.props));
  if (node.props && node.props.children !== undefined) return React.cloneElement(node, undefined, ...[].concat(await resolveTree(node.props.children)));
  return node;
}
const unq = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
const Live = (await import(pathToFileURL(path.join(site, "app", "learn", "problems", "[slug]", "page.tsx")).href)).default;
for (const slug of slugs) {
  const html = renderToStaticMarkup(await resolveTree(await Live({ params: Promise.resolve({ slug }) })));
  const text = unq(html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " "));
  fs.writeFileSync(`${prefix}_${slug}.html`, html);
  fs.writeFileSync(`${prefix}_${slug}.txt`, `${slug} drawn from the reads kept at ${r.now}: ${html.length} characters; em dashes ${html.split(String.fromCharCode(0x2014)).length - 1}; requests refused ${refused}\n\n${text}\n`);
  console.log(`${slug}: ${html.length} characters, refused ${refused}`);
}
process.exitCode = 0;
