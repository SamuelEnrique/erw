// Energy Research Warehouse (ERW) site, session 148: the proof that reading the pages of one large query together
// (lib/supabase.ts, restPaged) returns what reading them one after another returned. It reads every Supabase read the
// three live pages make (/cost-of-power/battery, /network, /storage) both ways and compares every row, in order.
//
//   node --env-file=.env.local --import ./scripts/alias-register.mjs scripts/compare-paged-reads.mjs
//        [--together 4] [--at-once] [--record ../tests/fixtures/session148/paged_reads.json] [--list]
//
// --at-once also sends each page's reads all at the same moment, as a rendering of the page does, every read with its
// pages together, and sets each result against the same read made alone, one page after another.
//
// WHICH READS. The pages' own functions are called with a stand-in for the database that answers every request with no
// rows, and each request they send is noted: app/storage/page.tsx's four reads (lib/data.ts storageUnits and series),
// app/network/data.ts liveExtras (demand, batteries, CAISO's batteries, a hub price a grid) and supplyRows for each of
// the seven grids. No request leaves this machine in that step. The battery page's two reads are functions of its
// page file (rowsOf and stressOf), which Node cannot import: their queries are written here as the page writes them,
// for both grids, both strategies and the three durations (tests/test_session148.py holds the two against the page).
// THEN each distinct read is made twice with the anon key, as the site reads: with the pages asked for one after
// another (together 1: the reader as it was) and together (--together, default 4), and the two results are compared
// row by row as JSON. Reads only; public rows only; no model call; nothing is written but --record's file.
// --record keeps one real read of three pages (ERCOT's ECRS reserve price, hour by hour, 1 June to 10 September 2025)
// with every page as the database answered it, for scripts/test-ask-speed.mjs. --list prints the reads and asks nothing.
// Exit 0 when every read is the same both ways, 1 when one differs or fails, 2 on bad arguments.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (name, d) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : d; };
const together = Number(opt("--together", "4"));
if (!Number.isInteger(together) || together < 2 || together > 8) { console.log("--together takes a whole number from 2 to 8"); process.exit(2); }
if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY) { console.log("SUPABASE_URL and SUPABASE_ANON_KEY are needed (node --env-file=.env.local ...)"); process.exit(2); }
const origin = new URL(process.env.SUPABASE_URL).origin;

// ---------------------------------------------------------------- 1. which reads the three live pages make
const real = globalThis.fetch;
const noted = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  if (u.origin === origin && u.pathname.startsWith("/rest/v1/")) {
    const q = Object.fromEntries(u.searchParams);
    delete q.limit; delete q.offset;
    noted.push({ table: u.pathname.slice("/rest/v1/".length), query: q });
    return new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
  }
  throw new Error(`a request this script does not make: ${u.origin}${u.pathname}`);
};
const sb = await import("../lib/supabase.ts");
const data = await import("../lib/data.ts");
const net = await import("../app/network/data.ts");
const stack = await import("../lib/batterystack.ts");
const reads = [];
const take = (page) => { for (const r of noted.splice(0)) reads.push({ page, ...r }); };

// /storage (app/storage/page.tsx, Storage): its four reads, as it makes them
const since30 = data.daysAgo(31);
await Promise.all([data.storageUnits(), data.series("storage_daily_cycle", { since: data.daysAgo(45) }),
  data.series("eia930_all_storage", { variable: "net_generation_battery_mw", since: since30 }), data.series("caiso_battery_storage", { variable: "batteries_mw", since: since30 })]);
take("/storage");
// /network (app/network/page.tsx): the live week's extras from the snapshot's first hour, and each grid's supply rows
const committed = JSON.parse(fs.readFileSync(path.resolve(here, "..", "data", "grid_network.json"), "utf8"));
await net.liveExtras({ hours: committed.hours });
for (const ba of Object.values(net.ISO_BA)) await net.supplyRows(ba);
take("/network");
// /cost-of-power/battery (app/cost-of-power/battery/page.tsx, rowsOf and stressOf), for every grid that is open
for (const g of stack.GRIDS.filter((x) => x.ready))
  for (const strat of ["foresight", "dayahead"]) for (const dur of [2, 4, 8]) {
    reads.push({ page: "/cost-of-power/battery", table: "series", query: { select: "variable,ts_utc,value", table_name: `eq.${stack.TABLE}`, entity: `eq.${g.entity}`, variable: `like.${strat}_${dur}h_*`, order: "variable,ts_utc" } });
    reads.push({ page: "/cost-of-power/battery", table: "series", query: { select: "variable,ts_utc,value,event", table_name: `eq.${stack.STRESS_TABLE}`, entity: `eq.${g.entity}`, variable: `like.${strat}_${dur}h_*`, order: "variable,ts_utc" } });
  }
const seen = new Set();
const distinct = reads.filter((r) => { const k = `${r.table} ${JSON.stringify(r.query)}`; if (seen.has(k)) return false; seen.add(k); return true; });
const name = (r) => `${(r.query.table_name ?? r.table).replace(/^eq\./, "")}${r.query.entity ? ` ${r.query.entity.replace(/^eq\./, "")}` : ""}${r.query.variable ? ` ${r.query.variable.replace(/^(eq|like|in)\./, "")}` : ""}${r.query.and ? ` ${r.query.and}` : ""}`.slice(0, 110);
if (args.includes("--list")) { for (const r of distinct) console.log(`${r.page}  ${r.table}  ${JSON.stringify(r.query)}`); console.log(`${distinct.length} reads; nothing was asked`); process.exit(0); }

// ---------------------------------------------------------------- 2. each read, both ways
let requests = 0, bytes = 0;
const urls = [];
globalThis.fetch = async (url, init) => {
  requests += 1;
  const res = await real(url, { headers: init?.headers });
  const body = await res.text();
  bytes += body.length;
  urls.push([String(url), res.status, body]);
  return new Response(body, { status: res.status, headers: { "content-type": "application/json" } });
};
const MAX = 50_000;
let differ = 0, failed = 0, rowsAll = 0, paged = 0, msSerial = 0, msTogether = 0;
const both = async (r) => {
  const t0 = Date.now();
  const a = await sb.restPaged(r.table, r.query, 0, MAX, 1).then((rows) => ({ rows }), (e) => ({ error: e.message }));
  const t1 = Date.now();
  const b = await sb.restPaged(r.table, r.query, 0, MAX, together).then((rows) => ({ rows }), (e) => ({ error: e.message }));
  const t2 = Date.now();
  return { a, b, ms: [t1 - t0, t2 - t1] };
};
for (const r of distinct) {
  const { a, b, ms } = await both(r);
  if (a.error || b.error) {
    const same = a.error === b.error;
    failed += 1;
    console.log(`FAILED ${r.page} ${name(r)}: one after another: ${a.error ?? `${a.rows.length} rows`}; together: ${b.error ?? `${b.rows.length} rows`}${same ? " (the same failure)" : ""}`);
    continue;
  }
  let at = -1;
  if (a.rows.length !== b.rows.length) at = Math.min(a.rows.length, b.rows.length);
  else for (let i = 0; i < a.rows.length; i++) if (JSON.stringify(a.rows[i]) !== JSON.stringify(b.rows[i])) { at = i; break; }
  const pages = Math.floor(a.rows.length / 1000) + 1;
  rowsAll += a.rows.length;
  if (pages > 1) { paged += 1; msSerial += ms[0]; msTogether += ms[1]; }
  if (at >= 0) differ += 1;
  console.log(`${at >= 0 ? "DIFFERS" : "same   "} ${r.page} ${name(r)}: ${a.rows.length} rows, ${pages} page${pages > 1 ? "s" : ""}, one after another ${ms[0]} ms, together ${ms[1]} ms${at >= 0 ? `; first difference at row ${at} (${a.rows.length} and ${b.rows.length} rows)` : ""}`);
}
console.log(`${distinct.length} reads of the three live pages, ${rowsAll} rows compared; ${distinct.length - differ - failed} the same both ways, ${differ} differ, ${failed} failed; ${paged} reads of more than one page took ${msSerial} ms one after another and ${msTogether} ms with ${together} pages together; ${requests} requests, ${bytes} bytes`);

// ---------------------------------------------------------------- 2b. a page's reads all at once, as a page sends them
// A page does not make its reads one at a time: /storage sends its four together, /network its sixteen. So each page's
// reads are sent at once here, every one with its pages together, and each result is set against the same read made
// alone with one page after another. This is the most the database is asked at one moment by one rendering of a page
// (the battery page renders one grid, strategy and duration at a time: its two reads; here all its 24 go at once).
if (args.includes("--at-once")) {
  for (const page of [...new Set(distinct.map((r) => r.page))]) {
    const mine = distinct.filter((r) => r.page === page);
    const t0 = Date.now();
    const got = await Promise.all(mine.map((r) => sb.restPaged(r.table, r.query, 0, MAX, together).then((rows) => ({ rows }), (e) => ({ error: e.message }))));
    const ms = Date.now() - t0;
    let bad = 0, n = 0;
    for (const [i, r] of mine.entries()) {
      const alone = await sb.restPaged(r.table, r.query, 0, MAX, 1).then((rows) => ({ rows }), (e) => ({ error: e.message }));
      const same = !got[i].error && !alone.error && JSON.stringify(got[i].rows) === JSON.stringify(alone.rows);
      n += alone.rows?.length ?? 0;
      if (!same) { bad += 1; differ += 1; console.log(`DIFFERS at once: ${page} ${name(r)}: ${got[i].error ?? `${got[i].rows.length} rows`} against ${alone.error ?? `${alone.rows.length} rows`}`); }
    }
    console.log(`${bad ? "DIFFERS" : "same   "} ${page}: its ${mine.length} reads sent at once, each with ${together} pages together, ${ms} ms, ${n} rows; ${mine.length - bad} equal to the read made alone, one page after another`);
  }
  console.log(`after the reads at once: ${requests} requests, ${bytes} bytes in all`);
}

// ---------------------------------------------------------------- 3. one real read of three pages, kept for the tests
const rec = opt("--record", "");
if (rec) {
  const q = { select: "t:ts_utc,v:value", table_name: "eq.ercot_as_prices", entity: "eq.ercot:ECRS", variable: "eq.mcpc_dam", and: "(ts_utc.gte.2025-06-01T05:00:00Z,ts_utc.lt.2025-09-10T05:00:00Z)", order: "ts_utc.asc.nullslast" };
  urls.length = 0;
  const { a, b } = await both({ table: "series", query: q });
  if (a.error || b.error || JSON.stringify(a.rows) !== JSON.stringify(b.rows)) { console.log(`the read to record failed or differed: ${a.error ?? b.error ?? "rows differ"}`); process.exit(1); }
  const pages = {};
  for (const [url, status, body] of urls) { const u = new URL(url); pages[`limit=${u.searchParams.get("limit")}&offset=${u.searchParams.get("offset")}`] = { status, rows: JSON.parse(body).length }; }
  const out = path.resolve(rec);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify({ _: "Energy Research Warehouse (ERW), session 148: one read of the Supabase live set (the anon key) that takes three pages, recorded by site/scripts/compare-paged-reads.mjs --record: ERCOT's day-ahead clearing price for ECRS, hour by hour, 1 June to 10 September 2025 (table ercot_as_prices; t is the hour's start in UTC, v the price in USD per MW per hour). Real rows in the order the database returned them; pages lists every request the two readers sent and how many rows each answered.",
    recorded_at: new Date().toISOString(), table: "series", query: q, pages, rows: a.rows }) + "\n");
  console.log(`recorded ${a.rows.length} rows of ${Object.keys(pages).length} distinct pages in ${out}`);
}
process.exit(differ || failed ? 1 : 0);
