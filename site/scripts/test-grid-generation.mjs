// Energy Research Warehouse (ERW) site, session 1179 (chain 091): the proof, without a build and without a request
// leaving this machine, that the Mix tab's one read of a grid's generation gives each reader the rows its own read gave.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-generation.mjs
//
// The reads are answered by session 1160's stand-in for PostgREST (scripts/test-grid-reads.mjs) over real rows
// (tests/fixtures/session1152/mix_hourly_erco.json: ERCOT's EIA-930 generation and demand, 20 to 22 October 2026), which
// counts what it is asked. A render is a new globalThis.__erwRequestCache (scripts/tsx-loader.mjs keeps React's `cache`
// in it, as Next keeps one a request). The clock is held at 2026-10-30 07:00 UTC: the 45 and 34 days hold the fixture
// whole, the 10 days begin at 20 October 07:00 and the 9 days at 21 October 07:00, inside it.
// Cases:
//   1. lib/gridReads.ts rowsSince: the rows of a read from an earlier start, cut at a later one, are the rows and the
//      order of the read from the later start, for starts before, inside and after the rows; latestHourOf: what
//      latestHour's two requests give (the newest total, the newest total left out, an empty window).
//   2. One render: shareGeneration then generationSince for the 45, 10 and 9 days (the three readers' own starts) and
//      latestHour's 34 days: one request in all, each reader's rows equal to its own read made apart; a start before
//      the shared one, another entity, another table read as before.
//   3. No render (React's `cache` outside a request): each reader reads on its own, with the same rows.
//   4. A failed shared read fails each reader with the read's own error, and is not asked for again in the render.
//   5. components/grid/Conditions.tsx loadConditions ("Yesterday" and the mix table's row) and lib/grid.ts load in one
//      render: the generation asked for once, loadConditions's day, demand and mix and load's rows as each read apart.
//   6. scripts/tsx-loader.mjs's `cache`: one answer per function and arguments in a render, none kept outside one,
//      a throw kept as a throw, and a new render asks again.
// Prints one line a case; exit 0 when every case holds, 1 otherwise.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { cache } from "react";

const here = path.dirname(fileURLToPath(import.meta.url));
const ORIGIN = "https://erw-session1179.invalid";
process.env.SUPABASE_URL = `${ORIGIN}/rest/v1/`;
process.env.SUPABASE_ANON_KEY = "session1179-test";
process.env.ERW_PAGES_TOGETHER = "1";
delete process.env.ERW_READ_TIMING;
delete process.env.NEXT_PHASE;
delete process.env.NEXT_RUNTIME;
const NOW = Date.parse("2026-10-30T07:00:00Z");
Date.now = () => NOW;

const fixture = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "session1152", "mix_hourly_erco.json"), "utf-8"));
const TABLES = { eia930_all_generation: fixture.generation, eia930_all_demand: fixture.demand };

let sent = [];
let failing = false;
function postgrest(url) {
  const u = new URL(url);
  const p = u.searchParams;
  const table = (p.get("table_name") ?? "").replace(/^eq\./, "");
  if (failing && table === "eia930_all_generation") {
    sent.push({ table, query: u.search, rows: 0 });
    return new Response(JSON.stringify({ code: "PGRST000", message: "session 1179 test: the read fails" }), { status: 400, headers: { "content-type": "application/json" } });
  }
  let rows = [...(TABLES[table] ?? [])];
  for (const [k, v] of rows.length ? p : []) {
    if (["select", "order", "limit", "offset", "table_name"].includes(k)) continue;
    if (v.startsWith("eq.")) rows = rows.filter((r) => String(r[k]) === v.slice(3));
    else if (v.startsWith("gte.")) rows = rows.filter((r) => Date.parse(r[k]) >= Date.parse(v.slice(4)));
    else throw new Error(`the stand-in does not know the filter ${k}=${v}`);
  }
  const order = rows.length ? p.get("order") ?? "" : "";
  if (order === "ts_utc.desc") rows.sort((a, b) => Date.parse(b.ts_utc) - Date.parse(a.ts_utc));
  else if (order.startsWith("entity,variable,ts_utc")) rows.sort((a, b) => a.entity.localeCompare(b.entity) || a.variable.localeCompare(b.variable) || Date.parse(a.ts_utc) - Date.parse(b.ts_utc));
  else if (order) throw new Error(`the stand-in does not know the order ${order}`);
  const off = Number(p.get("offset") ?? 0), lim = Number(p.get("limit") ?? 1000);
  const page = rows.slice(off, off + lim);
  sent.push({ table, query: u.search, rows: page.length });
  return new Response(JSON.stringify(page), { status: 200, headers: { "content-type": "application/json", "content-range": page.length ? `${off}-${off + page.length - 1}/*` : "*/0" } });
}
globalThis.fetch = async (url) => {
  const u = new URL(String(url));
  if (u.origin !== ORIGIN) throw new Error(`a request this test does not make: ${u.origin}`);
  return postgrest(String(url));
};
const silent = console.error;
console.error = () => undefined;   // attempt() logs a failed read; case 4 fails reads on purpose

const { daysAgo, series } = await import("../lib/data.ts");
const R = await import("../lib/gridReads.ts");
const { loadConditions } = await import("../components/grid/Conditions.tsx");
const { load, gridOf } = await import("../lib/grid.ts");
const { attempt } = await import("../lib/supabase.ts");

let failed = 0;
const check = (name, ok, detail = "") => { console.log(`${ok ? "ok  " : "FAIL"} ${name}${detail ? `: ${detail}` : ""}`); if (!ok) failed++; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const render = () => { globalThis.__erwRequestCache = new Map(); };
const done = () => { delete globalThis.__erwRequestCache; };
const genAsked = () => sent.filter((s) => s.table === R.GENERATION).length;

const E = "eia930:ERCO", GEN = R.GENERATION;
check("the table shared is eia930_all_generation", GEN === "eia930_all_generation");

// 1. the slices
{
  const all = await series(GEN, { entity: E, since: "2026-10-19T00:00:00Z" });
  const starts = ["2026-10-19T00:00:00Z", "2026-10-20T00:00:00Z", "2026-10-21T07:00:00Z", "2026-10-22T23:00:00Z", "2026-10-23T00:00:00Z"];
  let ok = true;
  const sizes = [];
  for (const s of starts) {
    const own = await series(GEN, { entity: E, since: s });
    const cut = R.rowsSince(all, s);
    sizes.push(own.length);
    if (!same(own, cut)) ok = false;
  }
  check("rowsSince: the rows and order of the read from each start", ok && all.length === fixture.generation.length && sizes.at(-1) === 0, sizes.join(", "));

  const S34 = daysAgo(34);
  const own = await R.latestHour(GEN, E, "net_generation_mw", S34);
  const cut = R.latestHourOf(all, "net_generation_mw", S34);
  check("latestHourOf: the newest total's hour and after, as latestHour's two requests", own.length > 0 && same(own, cut), `${cut[0]?.ts_utc}, ${cut.length} rows`);
  const last = all.filter((r) => r.variable === "net_generation_mw").map((r) => r.ts_utc).sort().at(-1);
  const less = all.filter((r) => !(r.variable === "net_generation_mw" && r.ts_utc === last));
  const fell = R.latestHourOf(less, "net_generation_mw", S34);
  const prev = less.filter((r) => r.variable === "net_generation_mw").map((r) => r.ts_utc).sort().at(-1);
  check("latestHourOf: the newest total left out, the hour before and every row after it", fell.length > 0 && Date.parse(fell[0].ts_utc) === Date.parse(prev) && same(fell, less.filter((r) => Date.parse(r.ts_utc) >= Date.parse(prev))), prev);
  check("latestHourOf: an empty window gives no rows", R.latestHourOf(all, "net_generation_mw", "2026-10-23T00:00:00Z").length === 0 && R.latestHourOf([], "net_generation_mw", S34).length === 0);
}

// 2. one render
{
  const S45 = daysAgo(45), S34 = daysAgo(34), S10 = daysAgo(10), S9 = daysAgo(9);
  sent = [];
  const apart = {
    s45: await series(GEN, { entity: E, since: S45 }), s10: await series(GEN, { entity: E, since: S10 }),
    s9: await series(GEN, { entity: E, since: S9 }), latest: await R.latestHour(GEN, E, "net_generation_mw", S34),
  };
  const askedApart = genAsked();
  render();
  sent = [];
  R.shareGeneration(E, S45);
  const shared = {
    s45: await R.generationSince(E, S45), s10: await R.generationSince(E, S10),
    s9: await R.generationSince(E, S9), latest: await R.latestHour(GEN, E, "net_generation_mw", S34),
  };
  const askedShared = genAsked();
  check("one render: the 45, 10 and 9 days and the newest hour, each as its own read gave", same(apart, shared) && shared.s45.length > shared.s10.length && shared.s10.length > shared.s9.length && shared.s9.length > 0 && shared.latest.length > 0,
    `${shared.s45.length}, ${shared.s10.length}, ${shared.s9.length} and ${shared.latest.length} rows`);
  check("one render: one request in all (five apart)", askedShared === 1 && askedApart === 5, `${askedApart} apart, ${askedShared} shared`);
  check("one render: the request is the 45 days, every variable", sent[0]?.query.includes(`ts_utc=gte.${encodeURIComponent(S45)}`) && !sent[0]?.query.includes("variable="), sent[0]?.query);
  R.shareGeneration(E, S10);   // a second share of the entity holds the first
  sent = [];
  await R.generationSince(E, S10);
  check("one render: a second share reads nothing", genAsked() === 0);
  const earlier = await R.generationSince(E, daysAgo(60));
  check("one render: a start before the shared one is read as before", genAsked() === 1 && same(earlier, await series(GEN, { entity: E, since: daysAgo(60) })));
  sent = [];
  await R.generationSince("eia930:PJM", S10);
  await R.latestHour("eia930_all_demand", E, "demand_mw", S34);
  check("one render: another entity, another table read as before", genAsked() === 1 && sent.filter((s) => s.table === "eia930_all_demand").length === 2);
  done();
}

// 3. no render
{
  sent = [];
  R.shareGeneration(E, daysAgo(45));
  const a = await R.generationSince(E, daysAgo(10));
  const b = await R.generationSince(E, daysAgo(9));
  const asked = genAsked();
  check("no render: each reader reads on its own (the share's read too), the same rows", asked === 3 && same(a, await series(GEN, { entity: E, since: daysAgo(10) })) && same(b, await series(GEN, { entity: E, since: daysAgo(9) })), `${asked} requests`);
}

// 4. a failed shared read
{
  render();
  failing = true;
  sent = [];
  R.shareGeneration(E, daysAgo(45));
  const x = await attempt(() => R.generationSince(E, daysAgo(10)));
  const y = await attempt(() => R.generationSince(E, daysAgo(9)));
  const z = await attempt(() => R.latestHour(GEN, E, "net_generation_mw", daysAgo(34)));
  const asked = genAsked();
  failing = false;
  sent = [];
  const w = await attempt(() => R.generationSince(E, daysAgo(10)));
  check("a failed shared read: each reader fails with its error", !x.ok && !y.ok && !z.ok && x.reason === y.reason && y.reason === z.reason && x.reason.includes("session 1179 test: the read fails"), !x.ok ? x.reason.slice(0, 90) : "read");
  check("a failed shared read: asked once in the render, and still failed for the render", asked >= 1 && asked <= 4 && !w.ok && genAsked() === 0, `${asked} request(s)`);
  done();
}

// 5. loadConditions and load in one render
{
  const ba = { code: "erco", entity: E, label: "ERCOT", tz: "America/Chicago", station: "" };
  const g = gridOf("ercot");
  const keep = (r) => ({ day: r.day, note: r.note, demand: r.demand, gen: r.gen, genDay: r.genDay, genNote: r.genNote, error: r.error });
  const apartC = await loadConditions(ba, "2026-10-21", { weather: false });
  const apartL = await load(g);
  render();
  sent = [];
  const L = await load(g);
  const C = await loadConditions(ba, "2026-10-21", { weather: false });
  const C2 = await loadConditions(ba, "2026-10-21");
  const asked = genAsked();
  done();
  check("loadConditions in a render after load: the same day, demand and mix", same(keep(apartC), keep(C)) && same(keep(apartC), keep(C2)) && C.gen.length > 0 && C.genDay === "2026-10-21", `${C.gen.length} mix rows of ${C.genDay}`);
  check("load in a render: the same 45 days of generation", same(apartL.gen, L.gen) && L.gen.length === fixture.generation.length && !L.errors.gen);
  check("load and loadConditions in a render: the generation asked for once", asked === 1, `${asked}`);
}

// 6. the loader's cache
{
  let n = 0;
  const f = cache((a, b) => { n++; return `${a}|${b?.k ?? b}`; });
  const o = { k: "o" };
  f("x"); f("x");
  const outside = n;
  render();
  n = 0;
  const v1 = f("x", 1), v2 = f("x", 1), v3 = f("x", 2), v4 = f("x", o), v5 = f("x", o), v6 = f("x", { k: "o" });
  const inside = n;
  render();
  n = 0;
  f("x", 1);
  const again = n;
  const t = cache(() => { n++; throw new Error("kept"); });
  n = 0;
  let thrown = 0;
  for (let i = 0; i < 2; i++) try { t(); } catch (e) { if (e.message === "kept") thrown++; }
  done();
  check("cache: outside a render every call runs", outside === 2);
  check("cache: in a render one answer per arguments (a string by value, an object by identity)", inside === 4 && v1 === v2 && v1 !== v3 && v4 === v5 && v6 === v5, `${inside} calls`);
  check("cache: a new render asks again; a throw is kept as a throw", again === 1 && thrown === 2 && n === 1);
}

console.error = silent;
console.log(failed ? `${failed} case(s) failed` : "every case holds");
process.exit(failed ? 1 : 0);
