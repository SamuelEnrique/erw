// Energy Research Warehouse (ERW) site, session 1160: every read the Grid tool's pages make, found by calling the pages
// as they are, and each timed three times against Supabase, one request at a time.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/time-grid-reads.mjs \
//     --env <file holding SUPABASE_URL and SUPABASE_ANON_KEY> [--out ../runs/s1160/reads.json] [--top 20] [--only <page>[,<page>...]]
//
// No build and no server. The pages' modules are imported as they are (scripts/tsx-loader.mjs transpiles them, and
// stands in for the browser's components, which never read Supabase), and each page is called with its address's
// query and walked as Next would render it on the server: every server component it draws is called, every read it
// makes goes through lib/supabase.ts unchanged (ERW_PAGES_TOGETHER=1: the pages of a large read one after another,
// as the build reads them, so no page past the end is asked for). The fetch they call is this script's:
//   - it sends only to the Supabase origin named in SUPABASE_URL (any other request is refused, and said so);
//   - it sends one request at a time, the next only once the last has answered;
//   - a request the page asked for before, by this page or another, is answered from the first answer, as Next's
//     fetch cache answers it on a server (the count of times a page asked is kept: a read asked for twice is listed).
//   - session 1179: each page is one render of React's `cache` (a new globalThis.__erwRequestCache a page, which
//     scripts/tsx-loader.mjs's "react" keeps its answers in), so a read shared through `cache` is asked for once a
//     page, as on Next's server, and a page that declares a read for the render (lib/gridReads.ts) is walked as it runs.
// Then every distinct request is sent twice more, alone, one after another: three times in all. The time is from the
// request to its answer's headers (session 580's measure, lib/supabase.ts readLine) and, beside it, to the body's end.
// Only SUPABASE_URL and SUPABASE_ANON_KEY are read from the --env file; neither is printed or written: the output
// names each request by its path and query (the key travels in a header).
// Writes nothing but --out (a JSON of every request, every page and each one's reads). Exit 0, 1 when a page threw
// or a request failed, 2 on bad usage.
import fs from "node:fs";
import { rowsOf } from "./slow-reads.mjs";

export const GRIDS = ["us48", "ercot", "caiso", "pjm", "miso", "nyiso", "isone", "spp"];
export const VIEWS = ["network", "mix", "clean", "gravity"];

/** The addresses read: /grid as it opens, each grid on each tab, the energy mix by month for the two grids that draw
 *  alert days on it, and the Flex Alert scorecard. /network redirects to /grid?view=network (next.config.ts), the
 *  Lower 48's Network tab, read here as /grid?grid=us48&view=network. */
export function pages() {
  const out = [{ name: "/grid", page: "grid", sp: {} }];
  for (const g of GRIDS) for (const v of VIEWS) out.push({ name: `/grid?grid=${g}&view=${v}`, page: "grid", sp: { grid: g, view: v } });
  for (const g of ["ercot", "caiso"]) out.push({ name: `/grid?grid=${g}&view=mix&mixp=month`, page: "grid", sp: { grid: g, view: "mix", mixp: "month" } });
  out.push({ name: "/grid/caiso/alerts", page: "alerts", sp: {} });
  return out;
}

export function median(xs) {
  const s = xs.filter((x) => Number.isFinite(x)).sort((a, b) => a - b);
  if (!s.length) return null;
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2);
}

/** A request named by its path and query: the endpoint, the ERW table, the filter (every parameter but select, order,
 *  limit and offset), the columns, the order, the page. */
export function readOf(key) {
  const u = new URL(key, "https://x.invalid");
  const p = u.searchParams;
  const endpoint = u.pathname.replace(/^\/rest\/v1\//, "").replace(/^\/storage\/v1\/object\/public\//, "storage:");
  const filter = [];
  for (const [k, v] of p) if (!["select", "order", "limit", "offset", "table_name"].includes(k)) filter.push(`${k}=${v}`);
  const t = p.get("table_name") ?? "";
  return { endpoint, table: t.startsWith("eq.") ? t.slice(3) : endpoint, filter: filter.join("&"), select: p.get("select") ?? "", order: p.get("order") ?? "", offset: Number(p.get("offset") ?? 0), limit: p.get("limit") ?? "" };
}

const ELEMENT = new Set([Symbol.for("react.transitional.element"), Symbol.for("react.element")]);
const MEMO = Symbol.for("react.memo");
const FORWARD = Symbol.for("react.forward_ref");

/** Walk what a server component returned as Next renders it on the server: a function component is called (awaited
 *  when async) and what it returns walked; a host element, a fragment, a provider or a client component's stand-in
 *  (scripts/tsx-loader.mjs marks them __erwClient) is not called, and what it was handed (its children and every
 *  other prop) is walked, as Next renders the server components passed to a client one. Arrays, iterables and plain
 *  objects are walked for elements inside them. A component that throws is noted with its name and its message. */
export async function walk(node, ctx = { calls: 0, errors: [] }, seen = new WeakSet()) {
  if (node === null || node === undefined) return ctx;
  const t = typeof node;
  if (t !== "object" && t !== "function") return ctx;
  if (t === "function") return ctx;   // a render prop or a handler: not drawn on the server
  if (typeof node.then === "function") {
    let v;
    try { v = await node; } catch (e) { ctx.errors.push(`a promise: ${e?.message ?? e}`); return ctx; }
    return walk(v, ctx, seen);
  }
  if (seen.has(node)) return ctx;
  seen.add(node);
  if (ELEMENT.has(node.$$typeof)) {
    let type = node.type;
    const props = node.props ?? {};
    if (type && typeof type === "object" && type.$$typeof === MEMO) type = type.type;
    if (type && typeof type === "object" && type.$$typeof === FORWARD) type = type.render;
    if (typeof type === "function" && !type.__erwClient && !type.prototype?.isReactComponent) {
      ctx.calls++;
      let out;
      try {
        out = type(props);
        if (out && typeof out.then === "function") out = await out;
      } catch (e) {
        ctx.errors.push(`${type.name || "a component"}: ${e?.message ?? e}`);
        return ctx;
      }
      return walk(out, ctx, seen);
    }
    for (const v of Object.values(props)) await walk(v, ctx, seen);
    return ctx;
  }
  if (Array.isArray(node) || (typeof node[Symbol.iterator] === "function" && !(node instanceof String))) {
    for (const v of node) await walk(v, ctx, seen);
    return ctx;
  }
  const proto = Object.getPrototypeOf(node);
  if (proto === Object.prototype || proto === null) for (const v of Object.values(node)) await walk(v, ctx, seen);
  return ctx;
}

/** The fetch the pages call: to `origin` only, one request at a time, each distinct request sent once and its answer
 *  kept for the next asker; `store.page` counts this page's asks. `realFetch` is the platform's. */
export function recorder(realFetch, origin, store, clock = () => performance.now()) {
  let chain = Promise.resolve();
  return async function fetchForPage(input, init = {}) {
    const url = String(input?.url ?? input);
    const u = new URL(url);
    if (u.origin !== origin) {
      store.refused.push(u.origin);
      throw new Error(`time-grid-reads: a request outside Supabase was refused (${u.origin})`);
    }
    const key = u.pathname + u.search;
    store.page.set(key, (store.page.get(key) ?? 0) + 1);
    let rec = store.reads.get(key);
    if (!rec) {
      rec = { key, url, headers: { ...(init.headers ?? {}) }, times: [], full: [], status: "", range: "", bytes: 0, body: null, type: "" };
      store.reads.set(key, rec);
      rec.pending = chain = chain.then(() => timeOne(realFetch, rec, true, clock));
    }
    await rec.pending;
    if (rec.status === "failed") throw new Error(`time-grid-reads: the request failed (${rec.error})`);
    const h = { "content-type": rec.type || "application/json" };
    if (rec.range) h["content-range"] = rec.range;
    return new Response(rec.body ?? "", { status: Number(rec.status), headers: h });
  };
}

/** One timed request of a kept read; `keep` keeps its body, for the page that asked. */
export async function timeOne(realFetch, rec, keep, clock = () => performance.now()) {
  const t0 = clock();
  try {
    const r = await realFetch(rec.url, { headers: rec.headers, signal: AbortSignal.timeout(60_000) });
    const head = clock();
    const text = await r.text();
    rec.times.push(Math.round(head - t0));
    rec.full.push(Math.round(clock() - t0));
    rec.status = String(r.status);
    rec.range = r.headers.get("content-range") ?? "";
    rec.type = r.headers.get("content-type") ?? "";
    rec.bytes = text.length;
    if (keep) rec.body = text;
  } catch (e) {
    rec.times.push(null);
    rec.full.push(null);
    rec.status = "failed";
    rec.error = e?.message ?? String(e);
  }
}

/** Rows a request answered: PostgREST's Content-Range (session 580's rowsOf), or the snapshot's one object. */
export function rowsOfRead(rec) {
  if (rec.key.includes("/storage/")) return 1;
  return rowsOf("rows", rec.range);
}

/** Every distinct request, slowest median first, with the pages that ask for it. */
export function summarize(reads, perPage) {
  const askers = new Map();
  for (const p of perPage) for (const [k, n] of p.asked) (askers.get(k) ?? askers.set(k, []).get(k)).push(n > 1 ? `${p.name} (${n} times)` : p.name);
  return [...reads.values()].map((r) => ({
    ...readOf(r.key), key: r.key, rows: rowsOfRead(r), bytes: r.bytes, status: r.status, times: r.times, full: r.full,
    median: median(r.times), medianFull: median(r.full), pages: askers.get(r.key) ?? [],
  })).sort((a, b) => (b.median ?? Infinity) - (a.median ?? Infinity));
}

const cell = (s) => String(s).replace(/\|/g, "\\|");

export function markdown(rows, n) {
  const out = ["| # | median ms (to headers) | three times | to body end | table | filter | order | offset | rows | pages |", "|---|---|---|---|---|---|---|---|---|---|"];
  rows.slice(0, n).forEach((r, i) => {
    const pagesShown = r.pages.length > 3 ? `${r.pages.slice(0, 3).join(", ")} and ${r.pages.length - 3} more` : r.pages.join(", ");
    out.push(`| ${i + 1} | ${r.median ?? "failed"} | ${r.times.map((x) => x ?? "failed").join(", ")} | ${r.medianFull ?? ""} | ${cell(r.table)} | ${cell(r.filter)} | ${cell(r.order)} | ${r.offset} | ${r.rows ?? "?"} | ${cell(pagesShown)} |`);
  });
  return out.join("\n");
}

/** SUPABASE_URL and SUPABASE_ANON_KEY from an env file, nothing else; neither is returned to be printed. */
export function envFrom(text) {
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    const m = /^\s*(?:export\s+)?(SUPABASE_URL|SUPABASE_ANON_KEY)\s*=\s*(.*)\s*$/.exec(line);
    if (m) out[m[1]] = m[2].replace(/^(["'])(.*)\1$/, "$2");
  }
  return out;
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/\\/g, "/").split("/").pop())) {
  const args = process.argv.slice(2);
  const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
  const envFile = opt("--env");
  if (!envFile) {
    console.log("usage: time-grid-reads.mjs --env <file> [--out reads.json] [--top 20] [--only <page>]");
    process.exit(2);
  }
  const env = envFrom(fs.readFileSync(envFile, "utf-8"));
  if (!env.SUPABASE_URL || !env.SUPABASE_ANON_KEY) {
    console.log(`time-grid-reads: ${envFile} does not name SUPABASE_URL and SUPABASE_ANON_KEY`);
    process.exit(2);
  }
  process.env.SUPABASE_URL = env.SUPABASE_URL;
  process.env.SUPABASE_ANON_KEY = env.SUPABASE_ANON_KEY;
  process.env.ERW_PAGES_TOGETHER = "1";
  delete process.env.ERW_READ_TIMING;
  delete process.env.NEXT_PHASE;
  delete process.env.NEXT_RUNTIME;
  delete process.env.SUPABASE_SERVICE_KEY;
  const origin = new URL(env.SUPABASE_URL).origin;
  const realFetch = globalThis.fetch;
  const store = { reads: new Map(), page: new Map(), refused: [] };
  globalThis.fetch = recorder(realFetch, origin, store);
  const top = Number(opt("--top")) > 0 ? Number(opt("--top")) : 20;
  const only = opt("--only");
  const started = new Date();
  const grid = await import("../app/grid/page.tsx");
  const alerts = await import("../app/grid/caiso/alerts/page.tsx");
  const perPage = [];
  // session 1179: --only takes a comma list of the addresses (an address holds no comma)
  const onlyList = only ? only.split(",") : null;
  for (const p of pages().filter((x) => !onlyList || onlyList.includes(x.name))) {
    store.page = new Map();
    // session 1179: one render's React cache a page (scripts/tsx-loader.mjs), as Next keeps one for each request
    globalThis.__erwRequestCache = new Map();
    const t0 = performance.now();
    const fn = p.page === "grid" ? grid.default : alerts.default;
    const ctx = await walk(fn({ searchParams: Promise.resolve(p.sp) }));
    delete globalThis.__erwRequestCache;
    perPage.push({ name: p.name, asked: [...store.page], calls: ctx.calls, errors: ctx.errors, ms: Math.round(performance.now() - t0) });
    const twice = [...store.page].filter(([, n]) => n > 1).length;
    console.log(`${p.name}: ${store.page.size} distinct requests, ${[...store.page.values()].reduce((a, b) => a + b, 0)} asked, ${twice} asked more than once, ${ctx.calls} components, ${ctx.errors.length} errors`);
    for (const e of ctx.errors) console.log(`  error: ${e}`);
  }
  const firstDone = new Date();
  for (const rec of store.reads.values()) rec.body = null;
  for (let round = 0; round < 2; round++) for (const rec of store.reads.values()) await timeOne(realFetch, rec, false);
  const ended = new Date();
  const rows = summarize(store.reads, perPage);
  const failed = rows.filter((r) => r.times.some((x) => x === null) || !/^2/.test(r.status));
  console.log("");
  console.log(`${rows.length} distinct requests from ${perPage.length} pages, each sent three times one at a time: ${started.toISOString()} to ${ended.toISOString()} (the pages walked by ${firstDone.toISOString()})`);
  console.log(`slower than 1 s (median): ${rows.filter((r) => (r.median ?? Infinity) > 1000).length}; failed or not 2xx: ${failed.length}; refused (not Supabase): ${store.refused.length}`);
  console.log("");
  console.log(markdown(rows, top));
  const out = opt("--out");
  if (out) {
    fs.writeFileSync(out, JSON.stringify({ started, firstDone, ended, pages: perPage.map((p) => ({ ...p, asked: p.asked.map(([k, n]) => ({ key: k, n })) })), reads: rows }, null, 1));
    console.log(`\nwritten: ${out}`);
  }
  const errors = perPage.reduce((a, p) => a + p.errors.length, 0);
  process.exit(errors || failed.length || store.refused.length ? 1 : 0);
}
