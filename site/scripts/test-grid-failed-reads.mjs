// Energy Research Warehouse (ERW) site, session 1181 (chain 091): every panel chains 077 and 078 added to the Grid tool,
// drawn with a read that fails, one failure at a time. Without a build, a server or a request leaving this machine.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-failed-reads.mjs
//
// The page (app/grid/page.tsx) is called as it is and walked as Next renders it on the server (scripts/time-grid-reads.mjs
// and same-figures.mjs: every server component called, a client component's props walked), one render a page (a new
// globalThis.__erwRequestCache, React's `cache` of scripts/tsx-loader.mjs). Its reads go through lib/supabase.ts unchanged,
// to a stand-in for PostgREST and for the public Storage object that answers from committed real rows: the committed
// snapshot (data/grid_network.json) and its week's generation and demand (fixtures/grid_balance.json), ERCOT's generation
// and demand and the seven grids' carbon intensity (fixtures/grid_failed_reads.json), the scarcity strip's rows and prices
// (fixtures/scarcity_strip.json), CAISO's and ERCOT's notices (fixtures/caiso_alerts.json, ercot_notices.json); every
// other table answers no row. The clock is the fixture's read time (Date.now), so each window holds its rows.
// A failure is one table's reads answered, as session 537's scripts/failing-read-proxy.mjs answers them, with:
//   timeout  HTTP 500 with the statement timeout's code (57014), past lib/supabase.ts's two retries (their waits run at once);
//   http500  a plain HTTP 500, not retried;
//   empty    HTTP 200 and no row (a table being reloaded answers so);
// and the Storage object fails with an HTTP 500 or an answer that is not a snapshot. The replay's committed daily file
// "fails" by not being found (fs.readFileSync throws ENOENT for it, once).
// For each case: the page is drawn with no component throwing; every panel the page draws with every read answered is
// still there by name; the panel draws no figure (data-check) that it does not draw with every read answered, none whose
// key names the failed table, and no figure's value moved; on a timeout or an HTTP 500 the panel says what could not be
// read in the site's words (Missing "could not be read", NoData's "no data", the mix view's "working on it", or "could not
// be read just now"), and never "not held" for the figures of the read that failed; an empty answer of a window says
// what an empty answer is ("not held", "no row"), an empty answer of a whole table that always holds rows (the two
// notice tables) is a failed read. The panels that read no database (the stored examples under Ask, the stress view and
// the committed-file views, the held queue line) draw the same with every read failing. And a failed read made inside
// Next asks the page for a short revalidation (session 537's mark), the empty notices' guard too; no Grid read is
// required() (the page is drawn on demand: a required read would throw an error page at the visitor).
// Prints one line a case; exit 0 when every case holds, 1 otherwise.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const ORIGIN = "https://erw-session1181.invalid";
process.env.SUPABASE_URL = `${ORIGIN}/rest/v1/`;
process.env.SUPABASE_ANON_KEY = "session1181-test";
process.env.ERW_PAGES_TOGETHER = "1";
for (const k of ["ERW_READ_TIMING", "NEXT_PHASE", "NEXT_RUNTIME", "SUPABASE_SERVICE_KEY"]) delete process.env[k];
console.error = () => {};   // lib/supabase.ts says each failed read on the console; the cases say what matters

const fx = (f) => JSON.parse(fs.readFileSync(path.join(here, "fixtures", f), "utf-8"));
const mine = fx("grid_failed_reads.json"), bal = fx("grid_balance.json"), strip = fx("scarcity_strip.json");
const caisoN = fx("caiso_alerts.json"), ercotN = fx("ercot_notices.json");
const snapText = fs.readFileSync(path.join(SITE, "data", "grid_network.json"), "utf-8");

// the clock: the fixture's read time, so daysAgo(n) and the render's "today" are the day the rows were read
const NOW = Date.parse(mine.read_at);
Date.now = () => NOW;
// lib/supabase.ts waits 1 and 3 seconds before retrying a statement timeout: here at once
const realSetTimeout = globalThis.setTimeout;
globalThis.setTimeout = (f, ms, ...a) => realSetTimeout(f, ms === 1000 || ms === 3000 ? 0 : ms, ...a);

// ------------------------------------------------------------------ the rows the stand-in holds, by table
const T = new Map();
const add = (table, rows) => T.set(table, [...(T.get(table) ?? []), ...rows]);
const asSeries = (entity, variable, ts, value, unit = "MW") => ({ entity, variable, ts_utc: ts, value, unit, freq: "PT1H", event: "" });
for (const [t, rows] of Object.entries(mine.rows)) add(t, rows.map(([e, v, ts, x]) => asSeries(e, v, ts, x, t.startsWith("carbon") ? "kg/MWh" : "MW")));
const tsOf = (t) => t.replace("Z", "+00:00");
const have = new Set(T.get("eia930_all_generation").map((r) => `${r.entity}|${r.variable}|${Date.parse(r.ts_utc)}`));
// session 1406: grid_balance.json holds each grid's week as [ts_utc, value] rows (its `about`); they are added as they are
// (each had been read as the value of an hour, so six grids' generation and demand were NaN)
for (const [ba, vals] of Object.entries(bal.generation)) {
  add("eia930_all_generation", vals.filter(([h, v]) => v !== null && !have.has(`eia930:${ba}|net_generation_mw|${Date.parse(h)}`)).map(([h, v]) => asSeries(`eia930:${ba}`, "net_generation_mw", tsOf(h), v)));
}
const haveD = new Set(T.get("eia930_all_demand").map((r) => `${r.entity}|${Date.parse(r.ts_utc)}`));
for (const [ba, vals] of Object.entries(bal.demand)) {
  add("eia930_all_demand", vals.filter(([h, v]) => v !== null && !haveD.has(`eia930:${ba}|${Date.parse(h)}`)).map(([h, v]) => asSeries(`eia930:${ba}`, "demand_mw", tsOf(h), v)));
}
// session 1406: EIA-930's Lower 48 (eia930:US48) demand over the snapshot's week (fixtures/lower48_demand.json, read once with
// the anon key), so the Lower 48's Network panel draws its own demand beside the seven's
add("eia930_all_demand", fx("lower48_demand.json").rows.map(([ts, v]) => asSeries("eia930:US48", "demand_mw", ts, v)));
for (const [g, entity, price] of [["ercot", "iso:ercot", "ercot:HB_HUBAVG|spp_rtm"], ["caiso", "iso:caiso", "caiso:TH_SP15_GEN-APND|lmp_rtm_15m_mean"]]) {
  add("scarcity_hours_by_grid", strip[g].rows.map((r) => ({ ...asSeries(entity, r.variable, r.ts_utc, r.value, "flag") })));
  const [pe, pv] = price.split("|");
  add("iso_rtm_hub_prices", strip[g].prices.map((r) => ({ ...asSeries(pe, pv, r.ts_utc, r.value, "USD/MWh"), freq: "PT15M" })));
}
add("ercot_hub_prices_daily", strip.ercot.daily.map((r) => ({ ...asSeries("ercot:HB_HUBAVG", "rt_max", r.ts_utc, r.value, "USD/MWh"), freq: "P1D" })));
add("caiso_grid_emergencies", caisoN.rows.map((r) => ({ event_id: r.event_id, event_date: `${r.event_date}T00:00:00+00:00`, event_type: r.event_type, extra: { region: r.region ?? "", time_frame: r.time_frame ?? "" } })));
add("ercot_grid_notices", ercotN.rows.map((r) => ({ event_id: r.event_id, event_date: `${r.event_date}T00:00:00+00:00`, event_type: r.event_type, extra: r.extra })));
// session 1185: the 48 contiguous states and DC of state_generation_mix_monthly (fixtures/lower48_mix.json), the Lower 48 by month
const l48 = fx("lower48_mix.json");
add("state_generation_mix_monthly", Object.entries(l48.months).flatMap(([m, states]) => Object.entries(states).flatMap(([st, vals]) => vals.flatMap((v, i) => (v === null ? [] : [{ ...asSeries(`eia:${st}`, `net_generation_${l48.stems[i]}_mwh`, `${m}-01T00:00:00+00:00`, v, "MWh"), freq: "P1M" }])))));

// session 1402: the hub's real-time price beside the hourly mix (fixtures/hub_price.json: ERCOT's, SPP's and CAISO's hubs in
// iso_rtm_hub_prices from 19 to 23 October 2026, read once with the anon key), so grid_hubprice_<grid> draws its figures
for (const [k, rs] of Object.entries(fx("hub_price.json").rows)) { const [e, v] = k.split("|"); add("iso_rtm_hub_prices", rs.map(([ts, x]) => ({ ...asSeries(e, v, ts, x, "USD/MWh"), freq: "PT15M" }))); }
// session 1403: the cleanest hours, live (fixtures/clean_week.json: carbon_intensity_hourly from 8 October 2026 for ERCOT,
// California and MISO, read once with the anon key; an hour already held is not added twice), so grid_cleanweek_<grid> draws its week
const haveC = new Set(T.get("carbon_intensity_hourly").map((r) => `${r.entity}|${r.variable}|${Date.parse(r.ts_utc)}`));
for (const [k, rs] of Object.entries(fx("clean_week.json").week.rows)) { const [e, v] = k.split("|"); add("carbon_intensity_hourly", rs.filter(([ts]) => !haveC.has(`${k}|${Date.parse(ts)}`)).map(([ts, x]) => asSeries(e, v, tsOf(ts), x, "kg/MWh"))); }

// session 1411: the older blocks (fixtures/grid_older_reads.json, read once with the anon key): ERCOT's battery cycle, price
// board, monthly carbon intensity and station temperatures, CAISO's daily series, the Flex Alert scorecard's two tables; and
// the battery units of storage_capacity (fixtures/grid_units.json, session 1180), as scripts/grid-render-standin.mjs adds them.
// The catalogue (the citations' source reports) is answered only while `withCatalogue` is set (the cases of session 1411):
// every case before them ran on a stand-in that answers it no row, so each draws as it did.
const older = fx("grid_older_reads.json");
for (const [t, groups] of Object.entries(older.rows)) {
  for (const [k, rs] of Object.entries(groups)) {
    const [e, v, unit, freq] = k.split("|");
    add(t, rs.map(([ts, x]) => ({ ...asSeries(e, v, tsOf(ts), x, unit), freq: freq ?? "" })));
  }
}
add("storage_capacity", fx("grid_units.json").rows.map((r) => ({ entity_id: r.entity_id, capacity_mw: r.capacity_mw, status: r.status, extra: { iso: r.iso, energy_capacity_mwh: r.mwh, state: r.state, planned_year: r.planned_year } })));
const CATALOGUE = older.catalogue.map(([table_name, tier, source_report, license, in_live_set]) => ({ table_name, tier, source_report, license, in_live_set }));
let withCatalogue = false;

// ------------------------------------------------------------------ the stand-in for PostgREST and Storage
let fail = null;   // { table, kind }; table "storage:snapshot" for the Storage object, "*" for every table
let asked = new Set();
const cmp = (a, b) => (a === b ? 0 : a === undefined || a === null ? -1 : b === undefined || b === null ? 1 : a < b ? -1 : 1);
const val = (r, col) => (col.startsWith("extra->>") ? r.extra?.[col.slice(8)] ?? null : r[col]);
function test1(r, col, cond) {
  if (cond.startsWith("not.")) return !test1(r, col, cond.slice(4));   // session 1411: the scorecard's model read (variable=not.like.coef_*)
  const m = /^(eq|neq|gte|gt|lte|lt|like|in|is)\.(.*)$/s.exec(cond);
  if (!m) throw new Error(`the stand-in does not know the filter ${col}=${cond}`);
  const [, op, raw] = m;
  const v = val(r, col);
  const time = col === "ts_utc" || col === "event_date";
  const x = time ? Date.parse(v) : v;
  const y = time && op !== "in" && op !== "is" ? Date.parse(raw) : raw;
  if (op === "eq") return String(v) === raw;
  if (op === "neq") return String(v) !== raw;
  if (op === "is") return raw === "null" ? v === null || v === undefined : false;
  if (op === "in") return raw.slice(1, -1).split(",").map((s) => s.trim().replace(/^"|"$/g, "")).includes(String(v));
  if (op === "like") return new RegExp(`^${raw.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*")}$`).test(String(v));
  if (op === "gte") return x >= y;
  if (op === "gt") return x > y;
  if (op === "lte") return x <= y;
  return x < y;
}
function postgrest(u) {
  const p = u.searchParams;
  const table = (p.get("table_name") ?? "").replace(/^eq\./, "") || u.pathname.replace(/^\/rest\/v1\//, "");
  let rows = [...(table === "catalogue" ? (withCatalogue ? CATALOGUE : []) : T.get(table) ?? [])];
  for (const [k, v] of p) {
    if (["select", "order", "limit", "offset", "table_name"].includes(k)) continue;
    if (!rows.length) break;
    if (k === "and") {
      for (const part of v.slice(1, -1).split(",")) { const [col, ...rest] = part.split("."); rows = rows.filter((r) => test1(r, col, rest.join("."))); }
      continue;
    }
    rows = rows.filter((r) => test1(r, k, v));
  }
  const order = (p.get("order") ?? "").split(",").filter(Boolean).map((o) => { const [c, d] = o.split("."); return { c, desc: d === "desc" }; });
  rows.sort((a, b) => { for (const o of order) { const c = cmp(val(a, o.c), val(b, o.c)); if (c) return o.desc ? -c : c; } return 0; });
  const off = Number(p.get("offset") ?? 0), lim = Number(p.get("limit") ?? 1000);
  const page = rows.slice(off, off + lim).map((r) => {
    const sel = p.get("select");
    if (!sel || sel === "*") return r;
    const o = {};
    for (const col of sel.split(",")) {
      const [name, src] = col.includes(":") ? col.split(":") : [col, col];
      o[name] = val(r, src) ?? null;
    }
    return o;
  });
  const total = p.get("limit") === "1" && rows.length ? `/${rows.length}` : "/*";
  return new Response(JSON.stringify(page), { status: 200, headers: { "content-type": "application/json", "content-range": page.length ? `${off}-${off + page.length - 1}${total}` : `*/${rows.length}` } });
}
globalThis.fetch = async (input) => {
  const u = new URL(String(input?.url ?? input));
  if (u.origin !== ORIGIN) throw new Error(`a request this test does not make: ${u.origin}`);
  const storage = u.pathname.startsWith("/storage/");
  const t = storage ? "storage:snapshot" : (u.searchParams.get("table_name") ?? "").replace(/^eq\./, "") || u.pathname.replace(/^\/rest\/v1\//, "");
  asked.add(t);
  if (fail && (fail.table === t || (fail.table === "*" && !storage))) {
    if (fail.kind === "timeout") return new Response('{"code":"57014","message":"canceling statement due to statement timeout"}', { status: 500 });
    if (fail.kind === "http500") return new Response('{"message":"session 1181: this read fails on purpose"}', { status: 500 });
    if (fail.kind === "empty") return storage ? new Response("{}", { status: 200 }) : new Response("[]", { status: 200, headers: { "content-type": "application/json", "content-range": "*/0" } });
  }
  if (storage) return new Response(snapText, { status: 200, headers: { "content-type": "application/json" } });
  return postgrest(u);
};

// the replay's committed daily file, not found once (lib/gridReplayFile.ts reads it with fs.readFileSync)
let replayGone = false;
const realRead = fs.readFileSync;
fs.readFileSync = function (file, ...a) {
  if (replayGone && /daily_\d{4}\.json$/.test(String(file))) { const e = new Error(`ENOENT: no such file, open '${file}'`); e.code = "ENOENT"; throw e; }
  return realRead.call(this, file, ...a);
};

// ------------------------------------------------------------------ the walk, by panel
const ELEMENT = new Set([Symbol.for("react.transitional.element"), Symbol.for("react.element")]);
const MEMO = Symbol.for("react.memo");
const FORWARD = Symbol.for("react.forward_ref");
/** The blocks a render is cut into: each named panel, and the blocks of chain 078 inside or beside them. */
const BLOCKS = [["data-grid-panel", (v) => v], ["data-grid-balance", (v) => `balance_${v}`], ["data-grid-replay-day", (v) => `replay_${v}`],
  ["data-gravity-day", () => "gravityday"], ["data-eia930-drawn", () => "preliminary"], ["data-grid-held", (v) => `held_${v}`],
  ["data-grid-queue-unread", () => "queue_unread"], ["data-mix", (v) => `mixview_${v}`]];
const block = (rec, name) => (rec[name] ??= { nums: [], text: [], errors: [], charts: [] });   // session 1402: charts, each TimeChart drawn (its series' names, a strip marked)
// session 1411: the older blocks are not named panels; each is recorded, beside the block it is drawn in, under its Section's
// title (older_Batteries, older_What it costs, older_How clean, older_Reliability, older_ERCOT: yesterday)
const OLDER = /^(Batteries|What it costs|How clean|Reliability|.*: yesterday)$/;
async function walk(node, rec, at, seen, also = []) {
  if (node === null || node === undefined || typeof node === "boolean") return;
  if (typeof node === "string" || typeof node === "number") { block(rec, at).text.push(String(node)); for (const a of also) block(rec, a).text.push(String(node)); return; }
  if (typeof node !== "object") return;
  if (typeof node.then === "function") {
    let v;
    try { v = await node; } catch (e) { block(rec, at).errors.push(String(e?.message ?? e)); return; }
    return walk(v, rec, at, seen, also);
  }
  if (seen.has(node)) return;
  seen.add(node);
  if (ELEMENT.has(node.$$typeof)) {
    let type = node.type;
    const props = node.props ?? {};
    if (type && typeof type === "object" && type.$$typeof === MEMO) type = type.type;
    if (type && typeof type === "object" && type.$$typeof === FORWARD) type = type.render;
    let p = at;
    if (typeof type === "string") {
      for (const [a, f] of BLOCKS) if (props[a] !== undefined) { p = f(props[a]); block(rec, p); }
      if (props["data-check"] !== undefined) block(rec, p).nums.push({ check: String(props["data-check"]), raw: String(props["data-raw"]) });
      if (props["data-missing"] !== undefined && typeof props.title === "string") block(rec, p).text.push(` [why: ${props.title}] `);
      for (const a of also) {
        if (props["data-check"] !== undefined) block(rec, a).nums.push({ check: String(props["data-check"]), raw: String(props["data-raw"]) });
        if (props["data-missing"] !== undefined && typeof props.title === "string") block(rec, a).text.push(` [why: ${props.title}] `);
      }
    }
    if (typeof type === "function" && type.name === "Section" && OLDER.test(String(props.title ?? ""))) { also = [...also, `older_${props.title}`]; block(rec, also.at(-1)); }
    if (typeof type === "function" && String(type.__erwClient ?? "").endsWith("#TimeChart")) block(rec, p).charts.push([`chart:${props.ariaLabel ?? ""}`, ...(props.series ?? []).map((x) => (x.strip ? `strip:${x.name}` : x.name))]);
    if (typeof type === "function" && !type.__erwClient && !type.prototype?.isReactComponent) {
      let o;
      try { o = type(props); if (o && typeof o.then === "function") o = await o; } catch (e) { block(rec, p).errors.push(`${type.name}: ${e?.message ?? e}`); return; }
      return walk(o, rec, p, seen, also);
    }
    // a host element: its children and the elements in its props; a client component's stand-in: the same (its data props,
    // a chart's points or the network's snapshot, are not drawn on the server)
    const drawn = (v) => v && typeof v === "object" && (ELEMENT.has(v.$$typeof) || (Array.isArray(v) && v.some((x) => drawn(x) || (Array.isArray(x) && x.some(drawn)))) || (!Array.isArray(v) && Object.values(v).some((x) => x && ELEMENT.has(x.$$typeof))));
    for (const [k, v] of Object.entries(props)) if (k === "children" || drawn(v)) await walk(v, rec, p, seen, also);
    return;
  }
  if (Array.isArray(node) || typeof node[Symbol.iterator] === "function") { for (const v of node) await walk(v, rec, at, seen, also); return; }
  const proto = Object.getPrototypeOf(node);
  if (proto === Object.prototype || proto === null) for (const v of Object.values(node)) await walk(v, rec, at, seen, also);
}

const page = await import("../app/grid/page.tsx");
const sb = await import("../lib/supabase.ts");
async function draw(sp, f = null) {
  fail = f;
  asked = new Set();
  globalThis.__erwRequestCache = new Map();
  const rec = {};
  try { await walk(page.default({ searchParams: Promise.resolve(sp) }), rec, "_page", new WeakSet()); }
  catch (e) { block(rec, "_page").errors.push(`the page: ${e?.message ?? e}`); }
  delete globalThis.__erwRequestCache;
  fail = null;
  for (const b of Object.values(rec)) b.text = b.text.join("").replace(/\s+/g, " ").trim();
  return { rec, asked: new Set(asked) };
}

// ------------------------------------------------------------------ the cases
let failures = 0, cases = 0;
async function check(name, f) {
  cases++;
  try {
    const why = await f();
    if (why) { failures++; console.log(`FAIL ${name}: ${why}`); } else console.log(`ok   ${name}`);
  } catch (e) {
    failures++;
    console.log(`FAIL ${name}: threw ${e?.stack ?? e}`);
  }
}
const NAMED = /^(grid_(network|gravity|clean24|mix|scarcity|caisoalert|ercotnotice|ask|hubprice)_|balance_|replay_|gravityday|preliminary|held_|queue_unread|mixview_)/;
// session 1403: the cleanest hours, live, is a named panel too (beside NAMED, whose words test_session1402 pins)
const NAMED_1403 = /^grid_cleanweek_/;
// session 1415: and the Clean tab's carbon blocks, the ranked table and the monthly since 2018
const NAMED_1415 = /^grid_carbon(rank|month)_/;
const SAYS = /could not be read|no data for|working on it/;
const baselines = new Map();
async function base(sp) {
  const k = JSON.stringify(sp) + (withCatalogue ? "|catalogue" : "");   // session 1411: a baseline with the catalogue answered is its own
  if (!baselines.has(k)) baselines.set(k, await draw(sp));
  return baselines.get(k);
}

/** One panel, one table, one failure kind: the checks of the header. `emptySays`: what an empty answer must say;
 *  `wholeTable`: an empty answer is a failed read; `snapshotHolds`: a figure keyed by the table may stand, the snapshot's
 *  own (the hourly refresh read it), as long as it is the figure drawn with every read answered. */
async function failing(sp, panel, table, kind, { emptySays, wholeTable, snapshotHolds } = {}) {
  const ok = await base(sp);
  const x = ok.rec[panel];
  if (!x) return `the panel ${panel} is not drawn with every read answered (blocks: ${Object.keys(ok.rec).join(", ")})`;
  if (!ok.asked.has(table)) return `the page does not read ${table} (it reads ${[...ok.asked].join(", ")})`;
  const got = await draw(sp, { table, kind });
  const errs = Object.entries(got.rec).flatMap(([b, r]) => r.errors.map((e) => `${b}: ${e}`));
  if (errs.length) return `a component threw: ${errs[0]}`;
  const lost = Object.keys(ok.rec).filter((b) => (NAMED.test(b) || NAMED_1403.test(b) || NAMED_1415.test(b)) && !got.rec[b] && b !== "queue_unread");
  if (lost.length) return `panels no longer drawn: ${lost.join(", ")}`;
  const y = got.rec[panel];
  const before = new Map(x.nums.map((n) => [n.check, n.raw]));
  const fresh = y.nums.filter((n) => !before.has(n.check));
  if (fresh.length) return `${fresh.length} figure(s) the panel does not draw when the read succeeds: ${fresh.slice(0, 3).map((n) => `${n.check}=${n.raw}`).join("; ")}`;
  const moved = y.nums.filter((n) => before.get(n.check) !== n.raw);
  if (moved.length) return `${moved.length} figure(s) moved: ${moved.slice(0, 3).map((n) => `${n.check} ${before.get(n.check)} to ${n.raw}`).join("; ")}`;
  const named = y.nums.filter((n) => n.check.includes(`|${table}|`));
  if (named.length && kind !== "empty" && !snapshotHolds) return `${named.length} figure(s) of the failed table drawn: ${named[0].check}`;
  if (kind === "empty" && !wholeTable) {
    if (emptySays && !emptySays.test(y.text)) return `an empty answer does not say ${emptySays}: ${y.text.slice(0, 400)}`;
    return x.nums.length && y.nums.length === x.nums.length && x.text === y.text && T.get(table)?.length ? "an empty answer changed nothing in the panel" : "";
  }
  if (!SAYS.test(y.text)) return `the panel does not say what could not be read: ${y.text.slice(0, 500)}`;
  if (!y.text.includes(table) && !y.text.includes("Supabase")) return `the panel's words do not name the read that failed: ${y.text.slice(0, 400)}`;
  return "";
}

const KINDS = ["timeout", "http500", "empty"];
const ERCOT_NET = { grid: "ercot", view: "network" };
const ERCOT_MIX = { grid: "ercot", view: "mix" };
const CAISO_MIX = { grid: "caiso", view: "mix" };

// 1. the Network tab: the grid's ties and demand (grid_network_), the balance (session 1165)
for (const kind of KINDS) {
  await check(`grid_network_ercot and balance_ERCO, eia930_all_demand, ${kind}: the hour's demand is the snapshot's, the week said not read`, async () => {
    const why = await failing(ERCOT_NET, "balance_ERCO", "eia930_all_demand", kind, { emptySays: /No hour of the week holds all three/, snapshotHolds: true });
    if (why) return why;
    const ok = (await base(ERCOT_NET)).rec.grid_network_ercot, got = (await draw(ERCOT_NET, { table: "eia930_all_demand", kind })).rec.grid_network_ercot;
    if (JSON.stringify(ok.nums) !== JSON.stringify(got.nums)) return "the network panel's figures moved (its hour's demand is the snapshot's own)";
    const y = (await draw(ERCOT_NET, { table: "eia930_all_demand", kind })).rec.balance_ERCO;
    return kind !== "empty" && y.nums.some((n) => n.check.startsWith("netbal|")) ? "a week figure computed without the demand" : "";
  });
  await check(`balance_ERCO (1165), eia930_all_generation, ${kind}: no generation, gap or week figure, its words`, async () => {
    const why = await failing(ERCOT_NET, "balance_ERCO", "eia930_all_generation", kind, { emptySays: /not held/ });
    if (why) return why;
    if (kind === "empty") return "";
    const y = (await draw(ERCOT_NET, { table: "eia930_all_generation", kind })).rec.balance_ERCO;
    if (y.nums.some((n) => n.check.startsWith("calc|bal|") || n.check.startsWith("netbal|"))) return "a gap or a week figure computed without the generation";
    if (/No hour of the week holds all three/.test(y.text) || /a part is not held/.test(y.text)) return "the failed read is said as 'not held'";
    return /not computed: a part could not be read/.test(y.text) && /The week's gap is not computed: its hours/.test(y.text) ? "" : `the gap and the week do not say why: ${y.text.slice(0, 400)}`;
  });
}
// 1b. session 1406: the Lower 48 on the Network tab (grid_network_us48, components/grid/Lower48Demand.tsx): a failed read
// of eia930_all_demand takes the Lower 48's own demand and the share, said "could not be read"; each grid's demand the
// snapshot holds for the hour stands (the snapshot's own, as on the grid's panel), and the seven's net exchange stands
const US48_NET = { grid: "us48", view: "network" };
for (const kind of KINDS) {
  await check(`grid_network_us48 (1406), eia930_all_demand, ${kind}: no Lower 48 demand or share, ${kind === "empty" ? "said not held" : "said not read"}; the exchange stands`, async () => {
    const why = await failing(US48_NET, "grid_network_us48", "eia930_all_demand", kind, { emptySays: /the Lower 48's demand is not held for the hour, so the share is not computed/, snapshotHolds: true });
    if (why) return why;
    const ok = (await base(US48_NET)).rec.grid_network_us48, y = (await draw(US48_NET, { table: "eia930_all_demand", kind })).rec.grid_network_us48;
    if (y.nums.some((n) => n.check.includes("eia930:US48") || n.check.startsWith("calc|addpct|"))) return "the Lower 48's demand or the share drawn without its read";
    const keep = (r) => r.nums.filter((n) => n.check.startsWith("net|") || n.check.startsWith("calc|add|net~")).map((n) => `${n.check}=${n.raw}`).join(";");
    if (keep(ok) !== keep(y)) return "the seven's net exchange moved";
    return kind === "empty" || /the Lower 48's demand (\[why: eia930_all_demand could not be read just now: [^\]]*\] )?could not be read for the hour, so the share is not computed/.test(y.text) ? "" : `the Lower 48's demand is not said not read: ${y.text.slice(y.text.indexOf("Their demand"), y.text.indexOf("Their demand") + 300)}`;
  });
}
for (const kind of ["http500", "empty"]) {
  await check(`grid_network_ercot, the hourly snapshot (Storage), ${kind}: the committed snapshot drawn and said`, async () => {
    const ok = await base(ERCOT_NET);
    const got = await draw(ERCOT_NET, { table: "storage:snapshot", kind });
    const a = ok.rec.grid_network_ercot, b = got.rec.grid_network_ercot;
    if (!b) return "the panel is not drawn";
    if (JSON.stringify(a.nums) !== JSON.stringify(b.nums)) return "the committed snapshot's figures differ from the same snapshot served";
    return got.rec._page.text.includes("the daily snapshot: the hourly copy was not reachable") ? "" : "the source line does not say the hourly copy was not reachable";
  });
}
await check("preliminary (1171): the sentence on EIA-930's revisions is drawn with every read failing", async () => {
  const got = await draw(ERCOT_NET, { table: "*", kind: "http500" });
  return got.rec.preliminary && /preliminary and EIA revises them/.test(got.rec.preliminary.text) ? "" : "not drawn";
});

// 2. the Gravity tab
for (const kind of KINDS) {
  await check(`grid_gravity_ercot, eia930_all_generation, ${kind}: no generation or share drawn, its words`, async () => {
    const why = await failing({ grid: "ercot", view: "gravity" }, "grid_gravity_ercot", "eia930_all_generation", kind, { emptySays: /not held/ });
    if (why || kind === "empty") return why;
    const y = (await draw({ grid: "ercot", view: "gravity" }, { table: "eia930_all_generation", kind })).rec.grid_gravity_ercot;
    if (y.nums.some((n) => n.check.startsWith("calc|pct|"))) return "a share computed without the generation";
    return /not held/.test(y.text.replace(/\[why:[^\]]*\]/g, "")) ? "the failed read is said as 'not held'" : "";
  });
}

// 3. the Clean tab: the last 24 hours' keyed table
for (const kind of KINDS) {
  await check(`grid_clean24_ercot, carbon_intensity_hourly, ${kind}: the panel's place says why, no figure`, async () => {
    const why = await failing({ grid: "ercot", view: "clean" }, "grid_clean24_ercot", "carbon_intensity_hourly", kind, { emptySays: /has no row in the last 7 days/ });
    if (why) return why;
    const y = (await draw({ grid: "ercot", view: "clean" }, { table: "carbon_intensity_hourly", kind })).rec.grid_clean24_ercot;
    return y.nums.length ? `${y.nums.length} figures drawn` : "";
  });
  // session 1403: the cleanest hours, live (grid_cleanweek_<grid>), beside the committed view: no figure, "could not be
  // read", the committed view beside it drawn as with every read answered
  await check(`grid_cleanweek_ercot (1403), carbon_intensity_hourly, ${kind}: no figure, its words, the committed view as before`, async () => {
    const sp = { grid: "ercot", view: "clean" };
    const why = await failing(sp, "grid_cleanweek_ercot", "carbon_intensity_hourly", kind, { emptySays: /no local day of the last 12 holds all its hours/ });
    if (why) return why;
    const ok = await base(sp), got = await draw(sp, { table: "carbon_intensity_hourly", kind });
    const y = got.rec.grid_cleanweek_ercot;
    if (y.nums.length) return `${y.nums.length} figures drawn`;
    if (kind !== "empty" && !/could not be read/.test(y.text)) return "the panel does not say could not be read";
    const x = ok.rec.grid_cleanweek_ercot;
    if (new Set(x.nums.map((n) => n.check.split("|")[0])).size !== 4) return `with every read answered: ${x.nums.map((n) => n.check).join("; ")}`;
    return JSON.stringify(ok.rec.mixview_clean.nums) === JSON.stringify(got.rec.mixview_clean.nums) ? "" : "the committed view's figures moved";
  });
  // session 1415: the Clean tab's carbon blocks, named panels since this session: the ranked table on a failed
  // carbon_intensity_hourly read, the monthly since 2018 on a failed carbon_intensity_monthly read (and the note's two
  // figures of the committed file go with the chart they describe): no figure, the panel's place says why, its method kept
  for (const [panel, table, emptySays] of [["grid_carbonrank_ercot", "carbon_intensity_hourly", /has no row in the last 7 days/], ["grid_carbonmonth_ercot", "carbon_intensity_monthly", /returned no rows/]]) {
    await check(`${panel} (1415), ${table}, ${kind}: the panel's place says why, no figure, its method line`, async () => {
      const sp = { grid: "ercot", view: "clean" };
      const why = await failing(sp, panel, table, kind, { emptySays });
      if (why) return why;
      const x = (await base(sp)).rec[panel], y = (await draw(sp, { table, kind })).rec[panel];
      if (!x.nums.length) return "no figure with every read answered";
      if (y.nums.length) return `${y.nums.length} figures drawn`;
      return /Method: the Clean tab's carbon blocks, keyed/.test(y.text) ? "" : "the method line is lost";
    });
  }
}

// 4. the Mix tab: the energy mix panel (1152)
for (const kind of KINDS) {
  await check(`grid_mix_ercot, eia930_all_generation, ${kind}: no figure, the hourly mix said not read`, async () => {
    const why = await failing(ERCOT_MIX, "grid_mix_ercot", "eia930_all_generation", kind);
    if (why) return why;
    const y = (await draw(ERCOT_MIX, { table: "eia930_all_generation", kind })).rec.grid_mix_ercot;
    return y.nums.length ? `${y.nums.length} figures drawn` : "";
  });
  await check(`grid_mix_ercot, eia930_all_demand, ${kind}: no peak demand figure, never "not held" on a failure`, async () => {
    const why = await failing(ERCOT_MIX, "grid_mix_ercot", "eia930_all_demand", kind, { emptySays: /Demand is not held for these hours/ });
    if (why) return why;
    const y = (await draw(ERCOT_MIX, { table: "eia930_all_demand", kind })).rec.grid_mix_ercot;
    if (kind !== "empty" && /Demand is not held/.test(y.text)) return "the failed read is said as 'not held'";
    return y.nums.some((n) => n.check.includes("demand")) ? "a demand figure drawn" : "";
  });
}

// 5. the scarcity strip (1154, 1155, 1174), ERCOT and CAISO
for (const kind of KINDS) {
  await check(`grid_scarcity_ercot, scarcity_hours_by_grid, ${kind}: the strip says why, no count`, async () => {
    const why = await failing(ERCOT_MIX, "grid_scarcity_ercot", "scarcity_hours_by_grid", kind, { emptySays: /holds no hour of ERCOT/ });
    if (why) return why;
    const y = (await draw(ERCOT_MIX, { table: "scarcity_hours_by_grid", kind })).rec.grid_scarcity_ercot;
    return y.nums.length ? `${y.nums.length} figures drawn` : "";
  });
  await check(`grid_scarcity_ercot, iso_rtm_hub_prices, ${kind}: no 15-minute price, never "not in the live set" on a failure`, async () => {
    const why = await failing(ERCOT_MIX, "grid_scarcity_ercot", "iso_rtm_hub_prices", kind, { emptySays: /No 15-minute price of these days is in the live set/ });
    if (why) return why;
    const y = (await draw(ERCOT_MIX, { table: "iso_rtm_hub_prices", kind })).rec.grid_scarcity_ercot;
    return kind !== "empty" && /No 15-minute price of these days is in the live set/.test(y.text) ? "the failed read is said as not in the live set" : "";
  });
  await check(`grid_scarcity_ercot, ercot_hub_prices_daily, ${kind}: no daily price figure, its words`, async () => {
    return failing(ERCOT_MIX, "grid_scarcity_ercot", "ercot_hub_prices_daily", kind);
  });
  await check(`grid_scarcity_ercot, ercot_grid_notices (1174), ${kind}: no call-day count, its words (an empty whole table is a failed read)`, async () => {
    const why = await failing(ERCOT_MIX, "grid_scarcity_ercot", "ercot_grid_notices", kind, { wholeTable: true });
    if (why) return why;
    const y = (await draw(ERCOT_MIX, { table: "ercot_grid_notices", kind })).rec.grid_scarcity_ercot;
    return y.nums.some((n) => n.check.startsWith("ercotn|")) ? "a notice count drawn" : "";
  });
  await check(`grid_scarcity_caiso, caiso_grid_emergencies (1155), ${kind}: no alert-day count, its words (an empty whole table is a failed read)`, async () => {
    const why = await failing(CAISO_MIX, "grid_scarcity_caiso", "caiso_grid_emergencies", kind, { wholeTable: true });
    if (why) return why;
    const y = (await draw(CAISO_MIX, { table: "caiso_grid_emergencies", kind })).rec.grid_scarcity_caiso;
    return y.nums.some((n) => n.check.startsWith("awe|")) ? "an alert count drawn" : "";
  });
  await check(`grid_scarcity_caiso, iso_rtm_hub_prices, ${kind}: no 15-minute price figure`, async () => {
    return failing(CAISO_MIX, "grid_scarcity_caiso", "iso_rtm_hub_prices", kind, { emptySays: /No 15-minute price of these days is in the live set/ });
  });
}

// 6. the notice state lines: CAISO's alerts (1155) and ERCOT's notices (1174)
for (const kind of KINDS) {
  await check(`grid_caisoalert_caiso, caiso_grid_emergencies, ${kind}: no date or count, "could not be read just now", never "no alert today"`, async () => {
    const why = await failing(CAISO_MIX, "grid_caisoalert_caiso", "caiso_grid_emergencies", kind, { wholeTable: true });
    if (why) return why;
    const y = (await draw(CAISO_MIX, { table: "caiso_grid_emergencies", kind })).rec.grid_caisoalert_caiso;
    return y.nums.length || /No Energy Emergency Alert or Flex Alert/.test(y.text) || /holds no notice/.test(y.text) ? `drawn as if read: ${y.text.slice(0, 300)}` : "";
  });
  await check(`grid_ercotnotice_ercot, ercot_grid_notices, ${kind}: no date or count, "could not be read just now", never "no call"`, async () => {
    const why = await failing(ERCOT_MIX, "grid_ercotnotice_ercot", "ercot_grid_notices", kind, { wholeTable: true });
    if (why) return why;
    const y = (await draw(ERCOT_MIX, { table: "ercot_grid_notices", kind })).rec.grid_ercotnotice_ercot;
    return y.nums.length || /No call on supply or demand is held/.test(y.text) || /holds no notice/.test(y.text) ? `drawn as if read: ${y.text.slice(0, 300)}` : "";
  });
}

for (const kind of KINDS) {
  await check(`CAISO's Reliability section (the count of notices keyed by 1166), caiso_grid_emergencies, ${kind}: never "holds 0 notices"`, async () => {
    const ok = await base(CAISO_MIX);
    const all = (r) => Object.values(r.rec).flatMap((b) => b.nums);
    if (!all(ok).some((n) => n.check === "awe|rows|any")) return "the count is not drawn with every read answered";
    const got = await draw(CAISO_MIX, { table: "caiso_grid_emergencies", kind });
    if (all(got).some((n) => n.check.startsWith("awe|"))) return "a notice figure drawn";
    // session 1420: the section is a named panel (grid_reliability_caiso), its words that block's; the page's are read too
    const t = [got.rec._page, got.rec.grid_reliability_caiso].filter(Boolean).map((b) => b.text).join(" ").replace(/ ?\[why:[^\]]*\] ?/g, " ").replace(/\s+/g, " ");
    if (/The table holds 0 notices/.test(t) || /the latest on no day/.test(t)) return "the failed read is said as an empty table";
    return /The table's notices could not be read/.test(t) ? "" : "the section does not say the notices could not be read";
  });
}

// 6a. session 1402: the hub's real-time price beside the hourly mix (grid_hubprice_<grid>): on a failed price read no figure,
// "could not be read", and the mix chart above still drawn, without its strip; CAISO's price, drawn alone, the same
for (const kind of KINDS) {
  await check(`grid_hubprice_ercot (1402), iso_rtm_hub_prices, ${kind}: no figure, the mix chart still drawn without its strip`, async () => {
    const why = await failing(ERCOT_MIX, "grid_hubprice_ercot", "iso_rtm_hub_prices", kind, { emptySays: /holds its four 15-minute prices in iso_rtm_hub_prices/ });
    if (why) return why;
    const charts = (r) => Object.values(r.rec).flatMap((b) => b.charts);
    const hourly = (c) => /hourly net generation by fuel/.test(c[0]);
    const ok = charts(await base(ERCOT_MIX)).find(hourly);
    if (!ok || !ok.some((n) => n.startsWith("strip:"))) return `with every read answered the hourly chart has no strip (${JSON.stringify(ok)})`;
    const got = await draw(ERCOT_MIX, { table: "iso_rtm_hub_prices", kind });
    const mix = charts(got).find(hourly);
    if (!mix) return "the hourly mix chart is not drawn";
    if (mix.some((n) => n.startsWith("strip:"))) return "the strip is drawn without its read";
    return kind !== "empty" && !/could not be read/.test(got.rec.grid_hubprice_ercot.text) ? "the panel does not say could not be read" : "";
  });
  await check(`grid_hubprice_caiso (1402, drawn alone), iso_rtm_hub_prices, ${kind}: no figure and no chart, its words`, async () => {
    const why = await failing(CAISO_MIX, "grid_hubprice_caiso", "iso_rtm_hub_prices", kind, { emptySays: /no day of the last 9 holds its 24 hours whole in iso_rtm_hub_prices/ });
    if (why) return why;
    const y = (await draw(CAISO_MIX, { table: "iso_rtm_hub_prices", kind })).rec.grid_hubprice_caiso;
    return y.charts.length ? "a price chart drawn without its read" : "";
  });
}
await check("grid_hubprice_ercot (1402), eia930_all_generation fails: no mix chart, the price drawn alone over its own days", async () => {
  const got = await draw(ERCOT_MIX, { table: "eia930_all_generation", kind: "timeout" });
  const b = got.rec.grid_hubprice_ercot;
  if (!b) return "no panel";
  if (b.charts.length !== 1 || b.charts[0].length !== 2) return `charts ${JSON.stringify(b.charts)}`;
  return b.nums.length === 4 && /so the price is drawn alone/.test(b.text) ? "" : `${b.nums.length} figures: ${b.text.slice(0, 300)}`;
});

// 6b. session 1185: the Lower 48 by month (grid_mix_us48, mixp=month), the sum of the states of state_generation_mix_monthly
for (const kind of KINDS) {
  await check(`grid_mix_us48 (1185, by month), state_generation_mix_monthly, ${kind}: no figure, ${kind === "empty" ? "no month of the 49 said" : "the view said not read (working on it)"}`, async () => {
    const sp = { grid: "us48", view: "mix", mixp: "month" };
    const why = await failing(sp, "grid_mix_us48", "state_generation_mix_monthly", kind, { emptySays: /holds every one of the 48 contiguous states and DC, so no month of the Lower 48 is drawn/ });
    if (why) return why;
    const ok = (await base(sp)).rec.grid_mix_us48;
    if (!ok.nums.some((n) => n.check.startsWith("states_sum|"))) return "the view draws no states_sum figure with every read answered";
    const y = (await draw(sp, { table: "state_generation_mix_monthly", kind })).rec.grid_mix_us48;
    return y.nums.length ? `${y.nums.length} figures drawn` : "";
  });
}

// 7. what reads no database draws the same with every read failing
const same = async (sp, panel) => {
  const ok = await base(sp);
  const got = await draw(sp, { table: "*", kind: "http500" });
  if (!ok.rec[panel]) return `${panel} is not drawn with every read answered`;
  if (!got.rec[panel]) return `${panel} is not drawn with every read failing`;
  const errs = Object.entries(got.rec).flatMap(([b, r]) => r.errors.map((e) => `${b}: ${e}`));
  if (errs.length) return `a component threw: ${errs[0]}`;
  return JSON.stringify(ok.rec[panel].nums) === JSON.stringify(got.rec[panel].nums) && ok.rec[panel].text === got.rec[panel].text ? "" : `${panel} differs with every read failing`;
};
await check("grid_ask_ercot (1157), the stored examples: the same with every read failing (it reads no database)", () => same(ERCOT_MIX, "grid_ask_ercot"));
await check("mixview_stress (1168), the stress charts and keyed tables: the same with every read failing (committed files)", () => same({ grid: "ercot", view: "mix", mix: "stress" }, "mixview_stress"));
await check("mixview_day (1166), the committed-file view's keys: the same with every read failing", () => same({ grid: "ercot", view: "mix", mix: "day" }, "mixview_day"));
await check("held_ISO-NE's interconnection queue (1167): \"license needed\" with every read failing (the held rows are never asked for)", () => same({ grid: "isone", view: "mix" }, "held_ISO-NE's interconnection queue"));

// 8. the interconnection queue of a grid not held: a failed read is not "not in the warehouse yet"
for (const kind of ["timeout", "http500"]) {
  await check(`ERCOT's interconnection queue, energy_projects, ${kind}: "could not be read", never "not in the warehouse yet"`, async () => {
    const got = await draw(ERCOT_MIX, { table: "energy_projects", kind });
    const q = got.rec.queue_unread;
    if (!q) return "no queue_unread block";
    if (!/could not be read/.test(q.text) || !q.text.includes("energy_projects")) return `its words: ${q.text}`;
    return /interconnection queue in the live set/.test(got.rec._page.text) ? "it still says 'not in the warehouse yet'" : "";
  });
}

// 9. the replayed day (1170): its committed file not found
await check("replay_ERCO (1170), the replay's daily file not found: no figure, the file named as not read", async () => {
  const sp = { grid: "ercot", view: "network", net: "day", t: "2021-02-15", node: "ERCO" };
  replayGone = true;
  const got = await draw(sp);
  replayGone = false;
  const r = got.rec.replay_ERCO;
  if (!r) return "no replay block";
  if (r.nums.length) return `${r.nums.length} figures drawn`;
  if (!/no data for/.test(r.text) || !/could not be read on the server \(ENOENT\)/.test(r.text)) return `its words: ${r.text.slice(0, 300)}`;
  const back = await draw(sp);
  return back.rec.replay_ERCO?.nums.length ? "" : "the file found again draws no figure (a failed read was kept)";
});
await check("gravityday (1170), the replay's daily file not found: \"could not be read\", never \"not held\"", async () => {
  const sp = { grid: "ercot", view: "gravity", net: "day", t: "2020-08-14" };   // another year: a file read is kept once found
  replayGone = true;
  const got = await draw(sp);
  replayGone = false;
  const r = got.rec.gravityday;
  if (!r) return "no gravity day line";
  if (r.nums.length) return `${r.nums.length} figures drawn`;
  if (!/could not be read/.test(r.text) || /is \s*not held/.test(r.text.replace(/\[why:[^\]]*\]/g, ""))) return `its words: ${r.text.slice(0, 300)}`;
  return (await draw(sp)).rec.gravityday?.nums.length ? "" : "the file found again draws no figure";
});

// 10. no failed read is kept in a cached page
await check("inside Next a failed read on the Grid page asks for a revalidation of RETRY seconds (session 537), the empty notices too", async () => {
  process.env.NEXT_RUNTIME = "nodejs";
  try {
    const n0 = (globalThis.__erwCacheCalls ?? []).length;
    await draw(CAISO_MIX, { table: "caiso_grid_emergencies", kind: "http500" });
    const n1 = (globalThis.__erwCacheCalls ?? []).length;
    await draw(CAISO_MIX, { table: "caiso_grid_emergencies", kind: "empty" });
    const n2 = (globalThis.__erwCacheCalls ?? []).length;
    const marks = (globalThis.__erwCacheCalls ?? []).slice(n0);
    if (n1 === n0) return "the failed read made no mark";
    if (n2 === n1) return "the empty whole table made no mark";
    return marks.every((m) => m.options?.revalidate === sb.RETRY && JSON.stringify(m.keyParts) === '["erw-failed-read"]') ? "" : `a mark of ${JSON.stringify(marks[0])}`;
  } finally {
    delete process.env.NEXT_RUNTIME;
  }
});
await check("no read of the Grid page is required(): the page is drawn on demand, so a failed read is never kept in a cached page", async () => {
  const files = ["app/grid/page.tsx", ...fs.readdirSync(path.join(SITE, "components", "grid")).map((f) => `components/grid/${f}`), "app/network/data.ts",
    ...["lib/grid.ts", "lib/gridReads.ts", "lib/gridErcotNotices.ts", "lib/reliability.ts", "lib/network.ts"]];
  const hit = files.filter((f) => /\brequired\s*\(/.test(realRead(path.join(SITE, f), "utf-8")));
  if (hit.length) return `required() in ${hit.join(", ")}`;
  const src = realRead(path.join(SITE, "app", "grid", "page.tsx"), "utf-8");
  return /await searchParams/.test(src) ? "" : "the page no longer reads its address (it would be prerendered and cached: read every read again)";
});

// 11. session 1411 (chain 107): the older blocks on a failed read (session 1181's list): YourGrid's battery cycle and units, the
// price board, the carbon intensity (hourly and monthly), the station's temperatures in "Yesterday", CAISO's daily series,
// the table citations (the catalogue) and the Flex Alert scorecard's notices column. Each says "could not be read" with the
// table and the reason on hover, draws no figure of the read, and is drawn as before when the read succeeds. The catalogue
// is answered from here on, so each citation draws its source reports with every read answered.
withCatalogue = true;
const CLEAN = { grid: "ercot", view: "clean" };
await check("the older blocks (1411), every read answered: each draws its figures, its citations their source reports", async () => {
  const m = (await base(ERCOT_MIX)).rec, c = (await base(CLEAN)).rec, ca = (await base(CAISO_MIX)).rec;
  const has = (b, re, n = 1) => (b && b.nums.filter((x) => re.test(x.check)).length >= n ? "" : `${re}`);
  const why = [has(m.older_Batteries, /^series\|storage_daily_cycle\|/, 2), has(m.older_Batteries, /^storage\|iso_mw\|ERCOT\|/, 3),
    has(m["older_What it costs"], /^series\|price_board_latest\|/, 3), has(m["older_What it costs"], /^series\|price_board_peak_offpeak\|/, 2),
    has(c["older_How clean"], /^series\|carbon_intensity_hourly\|/, 2), has(c["older_How clean"], /^series\|carbon_intensity_monthly\|/, 2),
    has(m["older_ERCOT: yesterday"], /degday\|/, 4), has(ca.older_Reliability, /^series\|caiso_reliability_daily\|/, 40)].filter(Boolean);
  if (why.length) return `not drawn with every read answered: ${why.join("; ")}`;
  return /\(source report /.test(m.older_Batteries.text) && !/could not be read/.test(m.older_Batteries.text) ? "" : `the citations: ${m.older_Batteries.text.slice(-400)}`;
});
const notSaid = (y, re) => (re.test(y.text.replace(/ ?\[why:[^\]]*\] ?/g, " ")) ? `the failed read is said as ${re}` : "");
for (const kind of KINDS) {
  await check(`older_Batteries (1411), storage_daily_cycle, ${kind}: no cycle figure, never "EIA-930 has no battery series"; the units stand`, async () => {
    const why = await failing(ERCOT_MIX, "older_Batteries", "storage_daily_cycle", kind, { emptySays: /EIA-930 has no battery series for this grid/ });
    if (why || kind === "empty") return why;
    const ok = (await base(ERCOT_MIX)).rec.older_Batteries, y = (await draw(ERCOT_MIX, { table: "storage_daily_cycle", kind })).rec.older_Batteries;
    const units = (r) => r.nums.filter((n) => n.check.startsWith("storage|")).map((n) => `${n.check}=${n.raw}`).join(";");
    return notSaid(y, /no battery series/) || (units(ok) === units(y) ? "" : "the units' figures moved");
  });
  await check(`older_Batteries (1411), storage_capacity, ${kind}: no unit figure, never "not in the warehouse yet"; the cycle stands`, async () => {
    const why = await failing(ERCOT_MIX, "older_Batteries", "storage_capacity", kind, { emptySays: /battery units mapped to ERCOT/ });
    if (why || kind === "empty") return why;
    const y = (await draw(ERCOT_MIX, { table: "storage_capacity", kind })).rec.older_Batteries;
    if (y.nums.some((n) => n.check.startsWith("storage|"))) return "a unit figure drawn";
    return notSaid(y, /Not in the warehouse yet: battery units/) || (y.nums.some((n) => n.check.startsWith("series|storage_daily_cycle|")) ? "" : "the cycle is not drawn");
  });
  await check(`older_What it costs (1411), price_board_latest, ${kind}: no price figure, never "not in the warehouse yet"`, async () => {
    const why = await failing(ERCOT_MIX, "older_What it costs", "price_board_latest", kind, { emptySays: /Not in the warehouse yet: ERCOT's hub prices/ });
    if (why || kind === "empty") return why;
    const y = (await draw(ERCOT_MIX, { table: "price_board_latest", kind })).rec["older_What it costs"];
    return y.nums.length ? `${y.nums.length} figures drawn` : notSaid(y, /Not in the warehouse yet/);
  });
  await check(`older_What it costs (1411), price_board_peak_offpeak, ${kind}: no peak figure, never "none"; the latest days' prices stand`, async () => {
    const why = await failing(ERCOT_MIX, "older_What it costs", "price_board_peak_offpeak", kind, { emptySays: /none/ });
    if (why || kind === "empty") return why;
    const ok = (await base(ERCOT_MIX)).rec["older_What it costs"], y = (await draw(ERCOT_MIX, { table: "price_board_peak_offpeak", kind })).rec["older_What it costs"];
    const latest = (r) => r.nums.filter((n) => n.check.startsWith("series|price_board_latest|")).map((n) => `${n.check}=${n.raw}`).join(";");
    if (latest(ok) !== latest(y)) return "the latest days' prices moved";
    return /off-peak, same day ?(\[why:[^\]]*\] )?could not be read/.test(y.text) ? notSaid(y, /\bnone\b/) : `the cells: ${y.text.slice(0, 500)}`;
  });
  await check(`older_How clean (1411), carbon_intensity_hourly, ${kind}: no hourly figure, never "not in the warehouse yet"`, async () => {
    const why = await failing(CLEAN, "older_How clean", "carbon_intensity_hourly", kind, { emptySays: /Not in the warehouse yet: ERCOT's carbon intensity/ });
    if (why || kind === "empty") return why;
    const y = (await draw(CLEAN, { table: "carbon_intensity_hourly", kind })).rec["older_How clean"];
    return y.nums.length ? `${y.nums.length} figures drawn` : notSaid(y, /Not in the warehouse yet/);
  });
  await check(`older_How clean (1411), carbon_intensity_monthly, ${kind}: no monthly figure, ${kind === "empty" ? "the line not drawn" : "said not read"}; the hour stands`, async () => {
    const why = await failing(CLEAN, "older_How clean", "carbon_intensity_monthly", kind);
    if (why) return why;
    const ok = (await base(CLEAN)).rec["older_How clean"], y = (await draw(CLEAN, { table: "carbon_intensity_monthly", kind })).rec["older_How clean"];
    if (y.nums.some((n) => n.check.includes("|carbon_intensity_monthly|"))) return "a monthly figure drawn";
    const hour = (r) => r.nums.filter((n) => n.check.includes("|carbon_intensity_hourly|")).map((n) => `${n.check}=${n.raw}`).join(";");
    return hour(ok) === hour(y) ? "" : "the hourly figures moved";
  });
  await check(`older_ERCOT: yesterday (1411), weather_obs_hourly, ${kind}: no degree day, ${kind === "empty" ? "each day not computed" : "never \"not computed (0 of 24 hours)\""}; demand stands`, async () => {
    const why = await failing(ERCOT_MIX, "older_ERCOT: yesterday", "weather_obs_hourly", kind, { emptySays: /not computed \(0 of 24 hours in weather_obs_hourly\)/ });
    if (why) return why;
    const ok = (await base(ERCOT_MIX)).rec["older_ERCOT: yesterday"], y = (await draw(ERCOT_MIX, { table: "weather_obs_hourly", kind })).rec["older_ERCOT: yesterday"];
    if (y.nums.some((n) => n.check.includes("degday|"))) return "a degree day drawn";
    const dem = (r) => r.nums.filter((n) => !n.check.includes("degday|")).map((n) => `${n.check}=${n.raw}`).join(";");
    if (dem(ok) !== dem(y)) return "the demand figures moved";
    return kind === "empty" ? "" : notSaid(y, /not computed \(/) || (/Degree days at KDFW: ?(\[why: weather_obs_hourly could not be read just now[^\]]*\] )?could not be read/.test(y.text) ? "" : "the degree days are not said not read");
  });
  await check(`older_Reliability (1411), caiso_reliability_daily, ${kind}: no daily figure, both tables said not read (an empty answer is a failed read); the notices stand`, async () => {
    const why = await failing(CAISO_MIX, "older_Reliability", "caiso_reliability_daily", kind, { wholeTable: true });
    if (why) return why;
    const ok = (await base(CAISO_MIX)).rec.older_Reliability, y = (await draw(CAISO_MIX, { table: "caiso_reliability_daily", kind })).rec.older_Reliability;
    if (y.nums.some((n) => n.check.includes("|caiso_reliability_daily|"))) return "a daily figure drawn";
    const awe = (r) => r.nums.filter((n) => n.check.startsWith("awe|")).map((n) => `${n.check}=${n.raw}`).join(";");
    if (awe(ok) !== awe(y)) return "the notices' figures moved";
    return /The daily peaks (\[why:[^\]]*\] )?could not be read/.test(y.text) && /The latest days (\[why:[^\]]*\] )?could not be read/.test(y.text) ? notSaid(y, /not held/) : `its words: ${y.text.slice(0, 400)}`;
  });
}
await check("older_Reliability (1411), one daily read failing (evening_ramp_mw, the rest answered): its cells \"could not be read\", every other figure as before", async () => {
  // the stand-in fails a whole table; here the ramp's read alone answers an HTTP 500, the other daily reads as they are
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (input, ...a) => {
    const u = new URL(String(input?.url ?? input));
    if (u.searchParams.get("table_name") === "eq.caiso_reliability_daily" && u.searchParams.get("variable") === "eq.evening_ramp_mw") return new Response('{"message":"session 1411: this read fails on purpose"}', { status: 500 });
    return realFetch(input, ...a);
  };
  try {
    const ok = (await base(CAISO_MIX)).rec.older_Reliability, y = (await draw(CAISO_MIX)).rec.older_Reliability;
    if (y.nums.some((n) => n.check.includes("|evening_ramp_mw|"))) return "a ramp figure drawn";
    const before = new Map(ok.nums.map((n) => [n.check, n.raw]));
    const lost = ok.nums.filter((n) => !n.check.includes("|evening_ramp_mw|") && !y.nums.some((m) => m.check === n.check && m.raw === n.raw));
    if (lost.length) return `${lost.length} other figure(s) lost or moved: ${lost[0].check}`;
    if (y.nums.some((n) => before.get(n.check) !== n.raw)) return "a figure moved";
    return /caiso_reliability_daily \(evening_ramp_mw\) could not be read just now/.test(y.text) ? notSaid({ text: y.text.replace(/Batteries at the evening peak[\s\S]*$/, "") }, /not held/) : "the ramp's cells do not say why";
  } finally {
    globalThis.fetch = realFetch;
  }
});
for (const kind of KINDS) {
  await check(`the table citations (1411), catalogue, ${kind}: "the source reports could not be read", no figure moved (its empty answer was already a failed read)`, async () => {
    const why = await failing(ERCOT_MIX, "older_Batteries", "catalogue", kind, { wholeTable: true });
    if (why) return why;
    const y = (await draw(ERCOT_MIX, { table: "catalogue", kind })).rec.older_Batteries;
    if (/\(source report /.test(y.text)) return "a source report drawn without its read";
    return /\(the source reports (\[why: catalogue could not be read just now[^\]]*\] )?could not be read\)/.test(y.text) ? "" : `its words: ${y.text.slice(-400)}`;
  });
}

// the Flex Alert scorecard (/grid/caiso/alerts), drawn as the Grid page is, at "_alerts"
const alertsPage = await import("../app/grid/caiso/alerts/page.tsx");
async function drawAlerts(f = null) {
  fail = f;
  asked = new Set();
  globalThis.__erwRequestCache = new Map();
  const rec = {};
  try { await walk(alertsPage.default(), rec, "_alerts", new WeakSet()); }
  catch (e) { block(rec, "_alerts").errors.push(`the page: ${e?.message ?? e}`); }
  delete globalThis.__erwRequestCache;
  fail = null;
  for (const b of Object.values(rec)) b.text = b.text.join("").replace(/\s+/g, " ").trim();
  return { rec, asked: new Set(asked) };
}
const alertsOk = await drawAlerts();
for (const kind of KINDS) {
  await check(`the Flex Alert scorecard's notices column (1411), caiso_grid_emergencies, ${kind}: ${kind === "empty" ? "blank as before (a window)" : "each day \"could not be read\""}, every figure as before`, async () => {
    const x = alertsOk.rec._alerts;
    const errs = Object.values(alertsOk.rec).flatMap((r) => r.errors);
    if (errs.length) return `with every read answered a component threw: ${errs[0]}`;
    if (!alertsOk.asked.has("caiso_grid_emergencies")) return "the scorecard does not read caiso_grid_emergencies";
    if (x.nums.length < 50) return `with every read answered only ${x.nums.length} figures`;
    if (/could not be read/.test(x.text)) return "with every read answered the page says not read";
    const got = await drawAlerts({ table: "caiso_grid_emergencies", kind });
    const y = got.rec._alerts;
    const e2 = Object.values(got.rec).flatMap((r) => r.errors);
    if (e2.length) return `a component threw: ${e2[0]}`;
    if (JSON.stringify(x.nums) !== JSON.stringify(y.nums)) return "the scorecard's figures moved";
    const said = (y.text.match(/\[why: caiso_grid_emergencies could not be read just now/g) ?? []).length;
    if (kind === "empty") return said ? "an empty window said as a failed read" : "";
    const days = (x.text.match(/EEA \d|Stage \d|Flex Alert, |Warning|Alert,/g) ?? []).length;
    return said >= 1 && days ? "" : `${said} cells say could not be read (${days} notice names with every read answered)`;
  });
}

await check("inside Next an empty answer of CAISO's daily peaks (a whole series) asks for a revalidation of RETRY seconds (1411)", async () => {
  process.env.NEXT_RUNTIME = "nodejs";
  try {
    const n0 = (globalThis.__erwCacheCalls ?? []).length;
    await draw(CAISO_MIX, { table: "caiso_reliability_daily", kind: "empty" });
    const marks = (globalThis.__erwCacheCalls ?? []).slice(n0);
    if (!marks.length) return "the empty daily series made no mark";
    return marks.every((m) => m.options?.revalidate === sb.RETRY && JSON.stringify(m.keyParts) === '["erw-failed-read"]') ? "" : `a mark of ${JSON.stringify(marks[0])}`;
  } finally {
    delete process.env.NEXT_RUNTIME;
  }
});

console.log(failures ? `${failures} of ${cases} case(s) failed` : `every case holds (${cases} cases)`);
process.exitCode = failures ? 1 : 0;
