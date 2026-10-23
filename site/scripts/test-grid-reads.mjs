// Energy Research Warehouse (ERW) site, session 1160: the proof, without a build and without a request leaving this
// machine, of the reads session 1160 changed on the Grid tool and of the pure parts of its timing script.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-reads.mjs
//
// The Supabase reads are answered by a stand-in for PostgREST over real rows (tests/fixtures/session1152/
// mix_hourly_erco.json: ERCOT's EIA-930 generation and demand from 20 to 22 October 2026, read by session 1152). It
// evaluates the filters the site sends (eq, gte, the key's order or ts_utc.desc, limit, offset) and counts what it
// was asked. Cases:
//   1. lib/gridReads.ts latestHour gives the Now view the hour and fuels the 34-day read gave, in two small requests;
//      with the newest hour's total left out it falls back to the hour before, as the 34-day read does; an empty window
//      gives nothing, as before.
//   2. components/grid/Conditions.tsx loadConditions with { weather: false } sends no weather_obs_hourly request and
//      returns the same day, demand and mix; without it the station is read, as before.
//   3. lib/reliability.ts gridNotices sends the request it sent before, with and without bounds.
//   4. scripts/time-grid-reads.mjs: median, readOf, envFrom, walk (an async component, a client stand-in's children,
//      a component that throws, elements inside plain props), the recorder (one request at a time, a repeated request
//      answered from the first, any other origin refused) and summarize; scripts/tsx-loader.mjs's client stand-ins.
// Prints one line a case; exit 0 when every case holds, 1 otherwise.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement } from "react";

const here = path.dirname(fileURLToPath(import.meta.url));
const ORIGIN = "https://erw-session1160.invalid";
process.env.SUPABASE_URL = `${ORIGIN}/rest/v1/`;
process.env.SUPABASE_ANON_KEY = "session1160-test";
process.env.ERW_PAGES_TOGETHER = "1";
delete process.env.ERW_READ_TIMING;
delete process.env.NEXT_PHASE;
delete process.env.NEXT_RUNTIME;

const fixture = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "session1152", "mix_hourly_erco.json"), "utf-8"));
const TABLES = { eia930_all_generation: fixture.generation, eia930_all_demand: fixture.demand };

/** A stand-in for PostgREST's series and events endpoints over the fixture's rows. */
let sent = [];
let rowsOf = TABLES;
function postgrest(url) {
  const u = new URL(url);
  const p = u.searchParams;
  const table = (p.get("table_name") ?? "").replace(/^eq\./, "");
  let rows = [...(rowsOf[table] ?? [])];
  // a table the fixture does not hold answers no rows, whatever it was asked
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

const { series } = await import("../lib/data.ts");
const { latestHour } = await import("../lib/gridReads.ts");
const { loadConditions } = await import("../components/grid/Conditions.tsx");
const { gridNotices } = await import("../lib/reliability.ts");
const T = await import("./time-grid-reads.mjs");
const L = await import("./tsx-loader.mjs");

let failed = 0;
const check = (name, ok, detail = "") => { console.log(`${ok ? "ok  " : "FAIL"} ${name}${detail ? `: ${detail}` : ""}`); if (!ok) failed++; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// the Now view's mix, as components/grid/NowView.tsx computes it from the rows it is given
const byTime = (a, b) => a.ts_utc.localeCompare(b.ts_utc);
function nowMix(rows) {
  const total = rows.filter((r) => r.variable === "net_generation_mw").sort(byTime).at(-1);
  const fuels = total ? rows.filter((r) => r.ts_utc === total.ts_utc && r.variable !== "net_generation_mw" && r.variable.startsWith("net_generation_")).sort((a, b) => b.value - a.value) : [];
  return { total, fuels };
}

const E = "eia930:ERCO", GEN = "eia930_all_generation";
const SINCE = "2026-10-19T00:00:00Z";   // before the fixture's first hour: the 34-day window holds it all

// 1. latestHour
{
  sent = [];
  const before = nowMix(await series(GEN, { entity: E, since: SINCE }));
  const askedBefore = sent.length, rowsBefore = sent.reduce((a, s) => a + s.rows, 0);
  sent = [];
  const after = nowMix(await latestHour(GEN, E, "net_generation_mw", SINCE));
  const rowsAfter = sent.reduce((a, s) => a + s.rows, 0);
  check("latestHour: the same total and fuels as the 34-day read", !!before.total && same(before, after), `${before.total?.ts_utc}, ${before.fuels.length} fuels`);
  check("latestHour: two requests, the hour's rows only", sent.length === 2 && rowsAfter === 1 + after.fuels.length + 1 && rowsAfter < rowsBefore, `${askedBefore} request(s) and ${rowsBefore} rows before, ${sent.length} and ${rowsAfter} after`);
  check("latestHour: the first request is the newest total in the window", sent[0].query.includes("variable=eq.net_generation_mw") && sent[0].query.includes("order=ts_utc.desc") && new URLSearchParams(sent[0].query).get("limit") === "1" && new URLSearchParams(sent[0].query).get("ts_utc") === `gte.${SINCE}`);

  // the newest hour's total left out (a subset of the real rows): both reads fall back to the hour before
  const last = fixture.generation.map((r) => r.ts_utc).sort().at(-1);
  rowsOf = { ...TABLES, [GEN]: fixture.generation.filter((r) => !(r.ts_utc === last && r.variable === "net_generation_mw")) };
  const b2 = nowMix(await series(GEN, { entity: E, since: SINCE }));
  const a2 = nowMix(await latestHour(GEN, E, "net_generation_mw", SINCE));
  check("latestHour: the newest total missing, the hour before, as before", !!b2.total && b2.total.ts_utc < last && same(b2, a2), b2.total?.ts_utc);
  rowsOf = TABLES;

  // an empty window
  const b3 = nowMix(await series(GEN, { entity: E, since: "2026-11-01T00:00:00Z" }));
  const a3 = await latestHour(GEN, E, "net_generation_mw", "2026-11-01T00:00:00Z");
  check("latestHour: an empty window gives no rows, as before", !b3.total && a3.length === 0);
}

// 2. loadConditions without the station
{
  const ba = { code: "erco", entity: E, label: "ERCOT", tz: "America/Chicago", station: "KDFW" };
  sent = [];
  const withWx = await loadConditions(ba, "2026-10-21");
  const wxAsked = sent.filter((s) => s.table === "weather_obs_hourly").length;
  sent = [];
  const without = await loadConditions(ba, "2026-10-21", { weather: false });
  const wxAfter = sent.filter((s) => s.table === "weather_obs_hourly").length;
  const keep = (r) => ({ day: r.day, note: r.note, demand: r.demand, gen: r.gen, genDay: r.genDay, genNote: r.genNote, error: r.error });
  check("loadConditions: the station is read by default", wxAsked === 1 && withWx.day === "2026-10-21");
  check("loadConditions { weather: false }: no station read, the same day, demand and mix", wxAfter === 0 && same(keep(withWx), keep(without)) && without.gen.length > 0, `${without.gen.length} mix rows of ${without.genDay}`);
}

// 3. gridNotices sends what it sent
{
  rowsOf = { caiso_grid_emergencies: [] };
  sent = [];
  await gridNotices();
  await gridNotices("2018-07-01", "2025-10-31");
  const q0 = new URLSearchParams({ select: "event_id,event_date,event_type,extra", table_name: "eq.caiso_grid_emergencies", order: "event_date,event_id", limit: "1000", offset: "0" });
  const q1 = new URLSearchParams({ select: "event_id,event_date,event_type,extra", table_name: "eq.caiso_grid_emergencies", order: "event_date,event_id", and: "(event_date.gte.2018-07-01,event_date.lte.2025-10-31T23:59:59Z)", limit: "1000", offset: "0" });
  check("gridNotices: the same requests, unbounded and bounded", sent.length === 2 && sent[0].query === `?${q0}` && sent[1].query === `?${q1}`);
  rowsOf = TABLES;
}

// 4. the timing script and the loader
{
  check("median", T.median([3, 1, 2]) === 2 && T.median([4, 1, 2, 3]) === 3 && T.median([null, 5]) === 5 && T.median([]) === null);
  const r = T.readOf("/rest/v1/series?select=a&table_name=eq.eia930_all_demand&entity=eq.eia930%3AERCO&order=ts_utc&limit=1000&offset=2000");
  check("readOf", r.table === "eia930_all_demand" && r.filter === "entity=eq.eia930:ERCO" && r.offset === 2000 && r.order === "ts_utc");
  check("readOf: the network's snapshot", T.readOf("/storage/v1/object/public/erw-public/network/grid_network.json").table === "storage:erw-public/network/grid_network.json");
  const env = T.envFrom("A=1\nSUPABASE_URL=https://x.supabase.co/rest/v1/\nSUPABASE_SERVICE_KEY=no\nSUPABASE_ANON_KEY=\"k\"\n");
  check("envFrom: the two names only", same(Object.keys(env).sort(), ["SUPABASE_ANON_KEY", "SUPABASE_URL"]) && env.SUPABASE_ANON_KEY === "k");

  const calls = [];
  async function Server({ n }) { calls.push(`server${n}`); return createElement("p", null, `n=${n}`); }
  function Throws() { throw new Error("boom"); }
  const Client = () => { calls.push("client called"); return null; };
  Client.__erwClient = "components/X.tsx#Client";
  const tree = createElement("div", null,
    createElement(Server, { n: 1 }),
    createElement(Client, { children: createElement(Server, { n: 2 }), aside: createElement(Server, { n: 3 }) }),
    [createElement(Throws, { key: "t" })],
    createElement("section", { items: [{ label: createElement(Server, { n: 4 }) }] }));
  const ctx = await T.walk(tree);
  check("walk: server components called, a client stand-in's props walked, not called", same(calls.sort(), ["server1", "server2", "server3", "server4"]) && ctx.calls === 5, calls.join(","));
  check("walk: a component that throws is noted", ctx.errors.length === 1 && ctx.errors[0].includes("Throws: boom"));

  let inFlight = 0, most = 0, real = 0;
  const slow = async (url) => { real++; inFlight++; most = Math.max(most, inFlight); await new Promise((r) => setTimeout(r, 5)); inFlight--; return new Response("[1]", { status: 200, headers: { "content-range": "0-0/*" } }); };
  const store = { reads: new Map(), page: new Map(), refused: [] };
  const f = T.recorder(slow, ORIGIN, store);
  const got = await Promise.all([f(`${ORIGIN}/rest/v1/series?a=1`), f(`${ORIGIN}/rest/v1/series?a=2`), f(`${ORIGIN}/rest/v1/series?a=1`)]);
  const bodies = await Promise.all(got.map((x) => x.text()));
  check("recorder: one request at a time, a repeat answered from the first", most === 1 && real === 2 && same(bodies, ["[1]", "[1]", "[1]"]) && store.page.get("/rest/v1/series?a=1") === 2);
  let refused = false;
  try { await f("https://elsewhere.invalid/x"); } catch { refused = true; }
  check("recorder: any other origin refused", refused && store.refused.length === 1 && real === 2);
  const rows = T.summarize(store.reads, [{ name: "/p", asked: [...store.page] }]);
  check("summarize: rows, times and the pages", rows.length === 2 && rows.every((x) => x.rows === 1 && x.times.length === 1) && rows.some((x) => x.pages[0] === "/p (2 times)"));

  check("tsx-loader: a client module is told by its directive", L.isClientModule('// note\n"use client";\nexport const A = 1;') && !L.isClientModule("export const A = 1;\n// \"use client\""));
  const js = L.transpile('"use client";\nexport function A() { return null; }\nexport const B = 1, C = 2;\nconst D = 3;\nexport { D as E };\nexport default function F() { return null; }\nexport type G = string;\n', "x.tsx");
  const names = L.exportNames(js).sort();
  check("tsx-loader: a client module's exports", same(names, ["A", "B", "C", "E", "default"]), names.join(","));
  check("tsx-loader: its stand-ins draw nothing and are marked", L.clientStub(["A", "default"], "components/X.tsx").includes("export const A = __erw(\"A\");") && L.clientStub(["default"], "x").includes("export default __erw('default');"));
}

console.log(failed ? `${failed} case(s) failed` : "every case holds");
process.exit(failed ? 1 : 0);
