// Energy Research Warehouse (ERW) site, session 1180 (chain 091): the Grid tool's pages drawn by two trees of the code
// (before and after a change) on the same live answers, every figure compared. Session 1179's one-off, kept.
//
//   node scripts/same-figures.mjs --env <file holding SUPABASE_URL and SUPABASE_ANON_KEY> --before <tree> --after <tree>
//     --only <address>[,<address>...] --out <dir> [--sizes]
//
// Session 1411: --only also takes /grid/caiso/alerts, the Flex Alert scorecard (its own page file, no search parameters).
//
// Session 1183: with --sizes each page is also drawn to its markup (sizeOf: the HTML and the flight payload Next would
// send, estimated outside Next, a client component's own markup not counted), its bytes before and after written to
// --out as sizes.json, and a page that grew by more than 15 percent or 100 KB marked OVER (the exit stays the figures').
//
// A tree is a checkout of the repository (its site/ is walked). A proxy on 127.0.0.1 sends each distinct request to
// Supabase once, one at a time, with the anon key, and keeps every answer in memory (the REST API and the public
// Storage object alike: the proxy stands where SUPABASE_URL points, and both are read through it); the tree before is
// walked first, then the tree after, each in its own node (scripts/alias-register.mjs and tsx-register.mjs, as
// time-grid-reads.mjs), so both draw the same rows. A page is one render (a new globalThis.__erwRequestCache, React's
// `cache` of scripts/tsx-loader.mjs). For each address: every figure (an element's data-check, data-raw and its
// text), every held figure (data-license-held) and every panel name (data-grid-panel), in walk order; the two trees
// must give the same lists. The answers are never written: --out gets the two lists of figures (figures_before.json,
// figures_after.json) and nothing else. A request only the tree after makes (a read the change narrowed) is sent then,
// and listed by its table, so it is seen to be the change's own. Exit 0 when every page is the same, 1 otherwise, 2 on
// bad usage.
//
// The walk (figuresOf) and the comparison (compareFigures) are exported for scripts/test-grid-units.mjs.
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ELEMENT = new Set([Symbol.for("react.transitional.element"), Symbol.for("react.element")]);
const MEMO = Symbol.for("react.memo");
const FORWARD = Symbol.for("react.forward_ref");

/** An address of /grid to the page's search parameters: "/grid?grid=ercot&view=mix" to { grid: "ercot", view: "mix" }. */
export function paramsOf(address) {
  const u = new URL(address, "https://x.invalid");
  if (u.pathname !== "/grid") throw new Error(`same-figures: only /grid addresses are walked (${address})`);
  return Object.fromEntries(u.searchParams);
}

/** The text a server element draws (a component that is not async is called; an async one is "<async>"). */
export function textOf(node) {
  if (node === null || node === undefined || typeof node === "boolean") return "";
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(textOf).join("");
  if (ELEMENT.has(node?.$$typeof)) {
    const t = node.type;
    if (typeof t === "function" && !t.__erwClient) {
      try { const o = t(node.props ?? {}); if (o && typeof o.then !== "function") return textOf(o); } catch { return "<throws>"; }
      return "<async>";
    }
    return textOf(node.props?.children);
  }
  return "";
}

/** Walk a server tree as Next renders it (scripts/time-grid-reads.mjs walk) and keep, in order, every figure, held
 *  figure and panel name of its host elements, and every component that threw. */
export async function figuresOf(node, rec = { nums: [], held: [], panels: [], errors: [] }, seen = new WeakSet()) {
  if (node === null || node === undefined || typeof node !== "object") return rec;
  if (typeof node.then === "function") {
    let v;
    try { v = await node; } catch (e) { rec.errors.push(String(e?.message ?? e)); return rec; }
    return figuresOf(v, rec, seen);
  }
  if (seen.has(node)) return rec;
  seen.add(node);
  if (ELEMENT.has(node.$$typeof)) {
    let type = node.type;
    const props = node.props ?? {};
    if (type && typeof type === "object" && type.$$typeof === MEMO) type = type.type;
    if (type && typeof type === "object" && type.$$typeof === FORWARD) type = type.render;
    if (typeof type === "string") {
      if (props["data-check"] !== undefined) rec.nums.push({ check: props["data-check"], raw: props["data-raw"], text: textOf(props.children) });
      if (props["data-license-held"] !== undefined) rec.held.push(props["data-license-held"]);
      if (props["data-grid-panel"] !== undefined) rec.panels.push(props["data-grid-panel"]);
    }
    if (typeof type === "function" && !type.__erwClient && !type.prototype?.isReactComponent) {
      let o;
      try { o = type(props); if (o && typeof o.then === "function") o = await o; } catch (e) { rec.errors.push(`${type.name}: ${e?.message ?? e}`); return rec; }
      return figuresOf(o, rec, seen);
    }
    for (const v of Object.values(props)) await figuresOf(v, rec, seen);
    return rec;
  }
  if (Array.isArray(node) || typeof node[Symbol.iterator] === "function") { for (const v of node) await figuresOf(v, rec, seen); return rec; }
  const proto = Object.getPrototypeOf(node);
  if (proto === Object.prototype || proto === null) for (const v of Object.values(node)) await figuresOf(v, rec, seen);
  return rec;
}

/** Two walks of the same addresses, page by page: a page is the same when its figures, held figures and panel names
 *  are equal, in order, and neither walk had an error. Returns each page's line and the first ten unequal figures. */
export function compareFigures(before, after) {
  const pages = [];
  let figures = 0;
  for (const name of Object.keys(before)) {
    const x = before[name], y = after[name];
    if (!y) { pages.push({ name, same: false, line: `DIFF ${name}: not walked after`, diffs: [] }); continue; }
    const same = JSON.stringify(x.nums) === JSON.stringify(y.nums) && JSON.stringify(x.held) === JSON.stringify(y.held)
      && JSON.stringify(x.panels) === JSON.stringify(y.panels) && !x.errors.length && !y.errors.length;
    figures += x.nums.length;
    const diffs = [];
    for (let i = 0; i < Math.max(x.nums.length, y.nums.length) && diffs.length < 10; i++) {
      if (JSON.stringify(x.nums[i]) !== JSON.stringify(y.nums[i])) diffs.push({ i, before: x.nums[i] ?? null, after: y.nums[i] ?? null });
    }
    pages.push({ name, same, diffs,
      line: `${same ? "same" : "DIFF"} ${name}: ${x.nums.length} figures before, ${y.nums.length} after, held ${x.held.length}/${y.held.length}, panels ${x.panels.length}/${y.panels.length}, errors ${x.errors.length}/${y.errors.length}` });
  }
  return { pages, figures, differ: pages.filter((p) => !p.same).length };
}

const escText = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const escAttr = (s) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;");
const ATTR = { className: "class", htmlFor: "for" };

/** Session 1183: a server tree reduced as Next's flight payload carries it: a host element is ["$", tag, props], a
 *  client component ["$", "C:<module#export>", props] (its props as handed to it, functions dropped), a server
 *  component what it returns; a promise awaited. Each component is called once. */
export async function reduceTree(node, seen = new WeakSet(), depth = 0) {
  if (node === null || node === undefined || typeof node === "boolean") return null;
  if (typeof node === "string" || typeof node === "number") return node;
  if (typeof node === "function" || typeof node === "symbol" || typeof node === "bigint" || depth > 400) return null;
  if (typeof node.then === "function") { try { return await reduceTree(await node, seen, depth + 1); } catch { return null; } }
  if (node instanceof Date) return node.toISOString();
  if (seen.has(node)) return null;
  seen.add(node);
  if (ELEMENT.has(node.$$typeof)) {
    let type = node.type;
    const props = node.props ?? {};
    if (type && typeof type === "object" && type.$$typeof === MEMO) type = type.type;
    if (type && typeof type === "object" && type.$$typeof === FORWARD) type = type.render;
    if (typeof type === "function" && !type.__erwClient && !type.prototype?.isReactComponent) {
      let o;
      try { o = type(props); if (o && typeof o.then === "function") o = await o; } catch { return null; }
      return reduceTree(o, seen, depth + 1);
    }
    const p = {};
    for (const [k, v] of Object.entries(props)) { const r = await reduceTree(v, seen, depth + 1); if (r !== null) p[k] = r; }
    if (typeof type === "string") return ["$", type, p];
    return ["$", typeof type === "function" ? `C:${type.__erwClient ?? type.name}` : "F", p];   // a client component, a fragment, a provider
  }
  if (Array.isArray(node) || typeof node[Symbol.iterator] === "function") { const out = []; for (const v of node) out.push(await reduceTree(v, seen, depth + 1)); return out; }
  const out = {};
  for (const [k, v] of Object.entries(node)) { const r = await reduceTree(v, seen, depth + 1); if (r !== null) out[k] = r; }
  return out;
}

/** The HTML of a reduced tree: each host element with its attributes and children, a client component drawn by the
 *  children it was handed (its own markup is not known outside Next, the same before and after). `files` counts the
 *  links whose href is a data: address, and their bytes. */
export function htmlOf(r, files = { n: 0, bytes: 0 }) {
  if (r === null || r === undefined) return "";
  if (typeof r === "string" || typeof r === "number") return escText(String(r));
  if (!Array.isArray(r)) return "";
  if (r[0] !== "$") return r.map((x) => htmlOf(x, files)).join("");
  const [, tag, p] = r;
  if (!tag.startsWith("C:") && tag !== "F") {
    let attrs = "";
    for (const [k, v] of Object.entries(p)) {
      if (k === "children" || k === "key" || k === "ref" || k === "dangerouslySetInnerHTML") continue;
      const name = ATTR[k] ?? k;
      if (v === true) attrs += ` ${name}`;
      else if (typeof v === "string" || typeof v === "number") attrs += ` ${name}="${escAttr(String(v))}"`;
      else if (k === "style" && v && typeof v === "object") attrs += ` style="${escAttr(Object.entries(v).map(([a, b]) => `${a}:${b}`).join(";"))}"`;
    }
    if (tag === "a" && typeof p.href === "string" && p.href.startsWith("data:")) { files.n++; files.bytes += Buffer.byteLength(p.href, "utf8"); }
    const inner = p.dangerouslySetInnerHTML?.__html ?? htmlOf(p.children, files);
    return `<${tag}${attrs}>${inner}</${tag}>`;
  }
  return htmlOf(p.children, files);
}

/** Session 1183: a page's size as Next would send it, estimated outside Next: its HTML (htmlOf) and its flight payload
 *  (the reduced tree as JSON), in bytes, and the data: links among them. Next's document holds both, so a figure
 *  or a link drawn on the server is counted twice, as it is sent; a client component's own markup is not counted. */
export async function sizeOf(node) {
  const r = await reduceTree(node);
  const files = { n: 0, bytes: 0 };
  const html = Buffer.byteLength(htmlOf(r, files), "utf8");
  const flight = Buffer.byteLength(JSON.stringify(r), "utf8");
  return { html, flight, total: html + flight, files: files.n, fileBytes: files.bytes };
}

/** Session 1183: the size of each page before and after, and whether it grew by more than 15 percent or 100 KB. */
export function sizeRows(before, after, pct = 15, kb = 100) {
  return Object.keys(before).filter((n) => before[n].size && after[n]?.size).map((name) => {
    const b = before[name].size, a = after[name].size, grew = a.total - b.total;
    return { name, before: b.total, after: a.total, grew, pct: Math.round((1000 * grew) / b.total) / 10, html: [b.html, a.html], flight: [b.flight, a.flight],
      filesBefore: b.files, filesAfter: a.files, fileBytesAfter: a.fileBytes, over: grew > (pct / 100) * b.total || grew > kb * 1024 };
  });
}

/** The child: walk one tree's /grid at each address, one render a page, and write the figures. Session 1183: with
 *  ERW_SIZES=1 the page is drawn a second time in the same render (its reads answered from the first) and its size kept. */
async function walkTree(site, addresses, out) {
  process.env.ERW_PAGES_TOGETHER = "1";
  delete process.env.ERW_READ_TIMING;
  delete process.env.NEXT_PHASE;
  delete process.env.NEXT_RUNTIME;
  delete process.env.SUPABASE_SERVICE_KEY;
  const page = await import(pathToFileURL(path.join(site, "app", "grid", "page.tsx")).href);
  // session 1411: the Flex Alert scorecard, the Grid tool's page of its own (no search parameters), walked the same way
  const OWN_PAGES = { "/grid/caiso/alerts": ["app", "grid", "caiso", "alerts", "page.tsx"] };
  const own = {};
  for (const name of addresses) if (OWN_PAGES[name]) own[name] = await import(pathToFileURL(path.join(site, ...OWN_PAGES[name])).href);
  const drawOf = (name) => (own[name] ? own[name].default() : page.default({ searchParams: Promise.resolve(paramsOf(name)) }));
  const result = {};
  for (const name of addresses) {
    globalThis.__erwRequestCache = new Map();
    const rec = await figuresOf(drawOf(name));
    if (process.env.ERW_SIZES === "1") rec.size = await sizeOf(drawOf(name));
    delete globalThis.__erwRequestCache;
    result[name] = rec;
    console.log(`${name}: ${rec.nums.length} figures, ${rec.held.length} held, ${rec.panels.length} panels, ${rec.errors.length} errors`);
  }
  fs.writeFileSync(out, JSON.stringify(result));
}

function envFrom(text) {
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    const m = /^\s*(?:export\s+)?(SUPABASE_URL|SUPABASE_ANON_KEY)\s*=\s*(.*)\s*$/.exec(line);
    if (m) out[m[1]] = m[2].replace(/^(["'])(.*)\1$/, "$2");
  }
  return out;
}

async function main(args) {
  const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
  if (opt("--walk")) return walkTree(opt("--walk"), opt("--pages").split(","), opt("--out"));
  const [envFile, before, after, only, out] = ["--env", "--before", "--after", "--only", "--out"].map(opt);
  if (!envFile || !before || !after || !only || !out) {
    console.log("usage: same-figures.mjs --env <file> --before <tree> --after <tree> --only <address>[,<address>...] --out <dir>");
    process.exit(2);
  }
  const work = path.resolve(out);   // the walks run in each tree's site/
  const env = envFrom(fs.readFileSync(envFile, "utf-8"));
  if (!env.SUPABASE_URL || !env.SUPABASE_ANON_KEY) { console.log(`same-figures: ${envFile} does not name SUPABASE_URL and SUPABASE_ANON_KEY`); process.exit(2); }
  const origin = new URL(env.SUPABASE_URL).origin;
  const kept = new Map();
  const misses = { before: 0, after: 0 }, hits = { before: 0, after: 0 }, fresh = [];
  let phase = "before";
  let chain = Promise.resolve();
  const server = http.createServer(async (req, res) => {
    if (req.method !== "GET") { res.writeHead(405).end("reads only"); return; }
    const key = req.url;
    let got = kept.get(key);
    if (!got) {
      misses[phase]++;
      if (phase === "after") fresh.push(key);
      got = { pending: (chain = chain.then(async () => {
        try {
          const r = await fetch(origin + key, { headers: { apikey: req.headers.apikey ?? "", authorization: req.headers.authorization ?? "", accept: req.headers.accept ?? "application/json", prefer: req.headers.prefer ?? "" }, signal: AbortSignal.timeout(60_000) });
          return { status: r.status, range: r.headers.get("content-range"), type: r.headers.get("content-type"), body: Buffer.from(await r.arrayBuffer()) };
        } catch (e) {
          return { status: 502, range: null, type: "text/plain", body: Buffer.from(`same-figures: ${e?.message ?? e}`) };
        }
      })) };
      kept.set(key, got);
    } else hits[phase]++;
    const a = await got.pending;
    const h = { "content-type": a.type ?? "application/json" };
    if (a.range) h["content-range"] = a.range;
    res.writeHead(a.status, h);
    res.end(a.body);
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const port = server.address().port;
  fs.mkdirSync(work, { recursive: true });
  const self = fileURLToPath(import.meta.url);
  const run = (tree, out) => new Promise((resolve) => {
    const site = path.resolve(tree, "site");
    const childEnv = { ...process.env, SUPABASE_URL: `http://127.0.0.1:${port}/rest/v1/`, SUPABASE_ANON_KEY: env.SUPABASE_ANON_KEY };
    if (args.includes("--sizes")) childEnv.ERW_SIZES = "1";   // session 1183
    delete childEnv.SUPABASE_SERVICE_KEY;
    const p = spawn(process.execPath, ["--import", "./scripts/alias-register.mjs", "--import", "./scripts/tsx-register.mjs", self, "--walk", site, "--pages", only, "--out", out],
      { cwd: site, env: childEnv, stdio: ["ignore", "pipe", "pipe"] });
    let o = "";
    p.stdout.on("data", (d) => (o += d));
    p.stderr.on("data", (d) => (o += d));
    p.on("close", (code) => resolve({ code, o }));
  });
  const t0 = new Date();
  const fb = path.join(work, "figures_before.json"), fa = path.join(work, "figures_after.json");
  const b = await run(before, fb);
  phase = "after";
  const a = await run(after, fa);
  server.close();
  console.log(`before: exit ${b.code}\n${b.o}after: exit ${a.code}\n${a.o}`);
  console.log(`from ${t0.toISOString()} to ${new Date().toISOString()}; distinct requests sent to Supabase: ${kept.size} (before ${misses.before}, after ${misses.after} new); answered from memory: before ${hits.before}, after ${hits.after}`);
  for (const k of fresh) { const u = new URL(k, "https://x.invalid"); console.log(`asked only after: ${u.pathname} ${u.searchParams.get("table_name") ?? ""} ${[...u.searchParams].filter(([n]) => !["select", "table_name", "order", "limit", "offset"].includes(n)).map(([n, v]) => `${n}=${v}`).join("&")}`); }
  if (b.code || a.code) process.exit(1);
  const cmp = compareFigures(JSON.parse(fs.readFileSync(fb, "utf-8")), JSON.parse(fs.readFileSync(fa, "utf-8")));
  for (const p of cmp.pages) {
    console.log(p.line);
    for (const d of p.diffs) console.log(`  ${d.i}: ${JSON.stringify(d.before)}\n  ${d.i}: ${JSON.stringify(d.after)}`);
  }
  console.log(`${cmp.differ ? `${cmp.differ} page(s) differ` : "every page the same"}; ${cmp.figures} figures compared`);
  if (args.includes("--sizes")) {
    // session 1183: each page's size before and after (bytes of its HTML and flight payload, estimated outside Next),
    // and the pages that grew by more than 15 percent or 100 KB
    const B = JSON.parse(fs.readFileSync(fb, "utf-8")), A = JSON.parse(fs.readFileSync(fa, "utf-8"));
    const rows = sizeRows(B, A);
    fs.writeFileSync(path.join(work, "sizes.json"), JSON.stringify(rows, null, 1));
    for (const r of rows) console.log(`size ${r.name}: ${r.before} to ${r.after} bytes (${r.grew >= 0 ? "+" : ""}${r.grew}, ${r.pct}%), data: links ${r.filesBefore} to ${r.filesAfter} (${r.fileBytesAfter} bytes)${r.over ? " OVER" : ""}`);
    console.log(`sizes: ${rows.filter((r) => r.over).length} page(s) over 15 percent or 100 KB; the largest growth ${Math.max(0, ...rows.map((r) => r.grew))} bytes`);
  }
  process.exit(cmp.differ ? 1 : 0);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main(process.argv.slice(2));
