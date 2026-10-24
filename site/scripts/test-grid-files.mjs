// Energy Research Warehouse (ERW) site, session 1182 (chain 091): each panel chains 077 and 078 added to the Grid tool
// offers its table as a file (components/grid/PanelFile.tsx), and the file's figures are exactly the page's. Without a
// build, a server or a request leaving this machine.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-files.mjs
//
// The page (app/grid/page.tsx) is called as it is and walked as Next renders it on the server (session 1181's
// test-grid-failed-reads.mjs: every server component called, one render a page), its reads answered by the same stand-in
// for PostgREST and Storage over committed real rows (the fixtures that test reads, session 1152's monthly mix rows,
// and fixtures/grid_files.json: ERCOT's rows of ba_supply_monthly and CAISO's monthly mix, read once with the anon key). The clock is the
// fixtures' read time. For each address, each block of the page (a named panel, the balance, the replayed day, the
// Exchange blocks, the stress view) is cut out with its figures (every data-check and data-raw) and its files (every
// link data-grid-file, its data: address decoded). For each block that draws a figure:
//   files     the block offers at least one file; each is named erw_<panel>[_<part>].csv and is an attachment (download)
//   header    the file opens with its provenance: the panel and page, the tables, the filter, the hour or window, the time
//             drawn; then its columns, and every row has as many cells as there are columns
//   same      the file is the one components/grid/PanelFile.tsx panelFile() writes from the cells the panel draws
//   figures   the figures of the block's files (each check key and value) are the block's figures on the page, no more and
//             no fewer; each figure's value is written whole in the file, in a cell or in a "Figure:" line of its header
// And: a held grid's figure is written "license needed", never its value, in a cell and in a header line (lib/license.ts,
// on a day it is held); a cell in words is written in those words; a value with a comma or a quote is quoted.
// Session 1183: and each block carries its anchor (lib/gridAnchors.ts: the id on the block, on an element inside it, or
// on the element that holds it alone), and no id is drawn twice on a page.
// Session 1184: and each block links its method, the section of its note (lib/gridAnchors.ts GRID_METHOD).
// Prints one line a case; exit 0 when every case holds, 1 otherwise.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h, Fragment } from "react";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const ORIGIN = "https://erw-session1182.invalid";
process.env.SUPABASE_URL = `${ORIGIN}/rest/v1/`;
process.env.SUPABASE_ANON_KEY = "session1182-test";
process.env.ERW_PAGES_TOGETHER = "1";
for (const k of ["ERW_READ_TIMING", "NEXT_PHASE", "NEXT_RUNTIME", "SUPABASE_SERVICE_KEY"]) delete process.env[k];
console.error = () => {};

const fx = (f) => JSON.parse(fs.readFileSync(path.join(here, "fixtures", f), "utf-8"));
const mine = fx("grid_failed_reads.json"), bal = fx("grid_balance.json"), strip = fx("scarcity_strip.json");
const caisoN = fx("caiso_alerts.json"), ercotN = fx("ercot_notices.json"), files = fx("grid_files.json");
const monthly = JSON.parse(fs.readFileSync(path.join(SITE, "..", "tests", "fixtures", "session1152", "mix_hourly_erco.json"), "utf-8")).monthly;
const snapText = fs.readFileSync(path.join(SITE, "data", "grid_network.json"), "utf-8");

const NOW = Date.parse(mine.read_at);
Date.now = () => NOW;
const realSetTimeout = globalThis.setTimeout;
globalThis.setTimeout = (f, ms, ...a) => realSetTimeout(f, ms === 1000 || ms === 3000 ? 0 : ms, ...a);

// ------------------------------------------------------------------ the rows the stand-in holds (session 1181's, and two more tables)
const T = new Map();
const add = (table, rows) => T.set(table, [...(T.get(table) ?? []), ...rows]);
const asSeries = (entity, variable, ts, value, unit = "MW") => ({ entity, variable, ts_utc: ts, value, unit, freq: "PT1H", event: "" });
for (const [t, rows] of Object.entries(mine.rows)) add(t, rows.map(([e, v, ts, x]) => asSeries(e, v, ts, x, t.startsWith("carbon") ? "kg/MWh" : "MW")));
const tsOf = (t) => t.replace("Z", "+00:00");
const have = new Set(T.get("eia930_all_generation").map((r) => `${r.entity}|${r.variable}|${Date.parse(r.ts_utc)}`));
// session 1406: grid_balance.json holds each grid's week as [ts_utc, value] rows (its `about`); they are added as they are
// (each had been read as the value of an hour, so six grids' generation and demand were NaN)
for (const [ba, vals] of Object.entries(bal.generation)) {
  add("eia930_all_generation", vals.filter(([x, v]) => v !== null && !have.has(`eia930:${ba}|net_generation_mw|${Date.parse(x)}`)).map(([x, v]) => asSeries(`eia930:${ba}`, "net_generation_mw", tsOf(x), v)));
}
const haveD = new Set(T.get("eia930_all_demand").map((r) => `${r.entity}|${Date.parse(r.ts_utc)}`));
for (const [ba, vals] of Object.entries(bal.demand)) {
  add("eia930_all_demand", vals.filter(([x, v]) => v !== null && !haveD.has(`eia930:${ba}|${Date.parse(x)}`)).map(([x, v]) => asSeries(`eia930:${ba}`, "demand_mw", tsOf(x), v)));
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
add("generation_mix_hourly_profile", monthly.map((r) => ({ ...asSeries(r.entity, r.variable, r.ts_utc, r.value, "MWh"), freq: "P1M" })));
add("generation_mix_hourly_profile", files.generation_mix_hourly_profile.map((r) => ({ ...asSeries(r.entity, r.variable, r.ts_utc, r.value, "MWh"), freq: "P1M" })));
add("ba_supply_monthly", files.ba_supply_monthly.map((r) => ({ ...asSeries(r.entity, r.variable, r.ts_utc, r.value, ""), freq: "P1M" })));
// session 1185: the 48 contiguous states and DC of state_generation_mix_monthly, 2025-08 to 2026-08 (fixtures/lower48_mix.json), for the Lower 48 by month
const l48 = fx("lower48_mix.json");
add("state_generation_mix_monthly", Object.entries(l48.months).flatMap(([m, states]) => Object.entries(states).flatMap(([st, vals]) => vals.flatMap((v, i) => (v === null ? [] : [{ ...asSeries(`eia:${st}`, `net_generation_${l48.stems[i]}_mwh`, `${m}-01T00:00:00+00:00`, v, "MWh"), freq: "P1M" }])))));

// session 1402: the hub's real-time price beside the hourly mix (fixtures/hub_price.json: ERCOT's, SPP's and CAISO's hubs in
// iso_rtm_hub_prices, read once with the anon key on 24 October 2026), so the panel grid_hubprice_<grid> draws its figures
const hubFx = fx("hub_price.json");
for (const [k, rs] of Object.entries(hubFx.rows)) { const [e, v] = k.split("|"); add("iso_rtm_hub_prices", rs.map(([ts, x]) => ({ ...asSeries(e, v, ts, x, "USD/MWh"), freq: "PT15M" }))); }
// session 1403: the cleanest hours, live (fixtures/clean_week.json: carbon_intensity_hourly, intensity_generation, ERCOT's,
// California's and MISO's rows from 8 October 2026, read once with the anon key on 24 October 2026; an hour the stand-in
// already holds is not added twice), so the panel grid_cleanweek_<grid> draws its week
const weekFx = fx("clean_week.json");
const haveC = new Set(T.get("carbon_intensity_hourly").map((r) => `${r.entity}|${r.variable}|${Date.parse(r.ts_utc)}`));
for (const [k, rs] of Object.entries(weekFx.week.rows)) { const [e, v] = k.split("|"); add("carbon_intensity_hourly", rs.filter(([ts]) => !haveC.has(`${k}|${Date.parse(ts)}`)).map(([ts, x]) => asSeries(e, v, tsOf(ts), x, "kg/MWh"))); }
// session 1415: carbon_intensity_monthly's intensity_generation, every row the live set holds (fixtures/carbon_monthly.json,
// read once with the anon key on 24 October 2026), so the Clean tab's "Monthly since 2018" (grid_carbonmonth_<grid>) draws
// its figures and its file
const monthlyC = fx("carbon_monthly.json");
add("carbon_intensity_monthly", monthlyC.rows.map(([e, ts, x]) => ({ ...asSeries(e, monthlyC.variable, ts, x, monthlyC.unit), freq: monthlyC.freq })));
// session 1420 (chain 111): the older blocks' own rows, as scripts/grid-render-standin.mjs adds them, so each draws its
// figures and its file: the battery units (fixtures/grid_units.json, session 1180), four tables of session 1411's committed
// reads (fixtures/grid_older_reads.json: ERCOT's battery cycle and price board, CAISO's daily reliability series) and
// CAISO's queue positions (fixtures/caiso_queue_positions.json, session 1186: real rows of the four fields the block reads;
// each given an id, caiso_queue:standin-<n>, for the read's prefix filter only: no id is drawn or keyed)
add("storage_capacity", fx("grid_units.json").rows.map((r) => ({ entity_id: r.entity_id, capacity_mw: r.capacity_mw, status: r.status, extra: { iso: r.iso, energy_capacity_mwh: r.mwh, state: r.state, planned_year: r.planned_year } })));
const olderRows = fx("grid_older_reads.json").rows;
for (const t of ["storage_daily_cycle", "price_board_latest", "price_board_peak_offpeak", "caiso_reliability_daily"]) {
  for (const [k, rs] of Object.entries(olderRows[t])) {
    const [e, v, unit, freq] = k.split("|");
    add(t, rs.map(([ts, x]) => ({ ...asSeries(e, v, tsOf(ts), x, unit), freq: freq ?? "" })));
  }
}
add("energy_projects", fx("caiso_queue_positions.json").rows.map((r, i) => ({ entity_id: `caiso_queue:standin-${String(i).padStart(4, "0")}`, capacity_mw: r.capacity_mw, status: r.status, extra: { technology_group: r.tech, source_table: r.src } })));

const cmp = (a, b) => (a === b ? 0 : a === undefined || a === null ? -1 : b === undefined || b === null ? 1 : a < b ? -1 : 1);
const val = (r, col) => (col.startsWith("extra->>") ? r.extra?.[col.slice(8)] ?? null : r[col]);
function test1(r, col, cond) {
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
  let rows = [...(T.get(table) ?? [])];
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
  if (u.pathname.startsWith("/storage/")) return new Response(snapText, { status: 200, headers: { "content-type": "application/json" } });
  return postgrest(u);
};

// ------------------------------------------------------------------ the walk, by block
const ELEMENT = new Set([Symbol.for("react.transitional.element"), Symbol.for("react.element")]);
const MEMO = Symbol.for("react.memo");
const FORWARD = Symbol.for("react.forward_ref");
const BLOCKS = [["data-grid-panel", (v) => v], ["data-grid-balance", (v) => `balance_${v}`], ["data-grid-replay-day", (v) => `replay_${v}`],
  ["data-grid-view", (v) => `view_${v}`], ["data-mix", (v) => `mixview_${v}`]];
const block = (rec, name) => (rec[name] ??= { nums: [], files: [], made: [], errors: [], ids: [], methods: [] });
// session 1183: every id the page draws, in order (a symbol key: the blocks are the record's own keys)
const IDS = Symbol("ids");
const PF = await import("../components/grid/PanelFile.tsx");
async function walk(node, rec, at, seen, wrap) {
  if (node === null || node === undefined || typeof node !== "object") return;
  if (typeof node.then === "function") {
    let v;
    try { v = await node; } catch (e) { block(rec, at).errors.push(String(e?.message ?? e)); return; }
    return walk(v, rec, at, seen, wrap);
  }
  if (seen.has(node)) return;
  seen.add(node);
  if (ELEMENT.has(node.$$typeof)) {
    let type = node.type;
    const props = node.props ?? {};
    if (type && typeof type === "object" && type.$$typeof === MEMO) type = type.type;
    if (type && typeof type === "object" && type.$$typeof === FORWARD) type = type.render;
    let p = at;
    let under;   // session 1183: the id of an element that holds one element alone, handed to that element
    if (typeof type === "string") {
      let named = false;
      for (const [a, f] of BLOCKS) if (props[a] !== undefined) { p = f(props[a]); block(rec, p); named = true; }
      if (props.id !== undefined) { (rec[IDS] ??= []).push(String(props.id)); block(rec, p).ids.push(String(props.id)); }
      if (named && wrap) block(rec, p).ids.push(wrap);
      if (props.id !== undefined && props.children && typeof props.children === "object" && !Array.isArray(props.children) && ELEMENT.has(props.children.$$typeof)) under = String(props.id);
      if (props["data-check"] !== undefined) block(rec, p).nums.push(`${props["data-check"]}=${props["data-raw"]}`);
      if (props["data-grid-file"] !== undefined) block(rec, p).files.push({ id: props["data-grid-file"], href: props.href, download: props.download,
        rows: props["data-grid-file-rows"], figures: props["data-grid-file-figures"] });
    }
    // session 1184: every link to a method note the block draws (a SiteLink or a link, before the release gate draws it)
    if (typeof props.href === "string" && props.href.startsWith("/data/methods/")) block(rec, p).methods.push(props.href);
    if (type === PF.PanelFile) block(rec, p).made.push(PF.panelFile(props.of, props.columns, props.rows));
    if (typeof type === "function" && !type.__erwClient && !type.prototype?.isReactComponent) {
      let o;
      try { o = type(props); if (o && typeof o.then === "function") o = await o; } catch (e) { block(rec, p).errors.push(`${type.name}: ${e?.message ?? e}`); return; }
      return walk(o, rec, p, seen, wrap);
    }
    if (typeof type !== "string") under = wrap;   // a fragment or a client component hands the wrapper on
    const drawn = (v) => v && typeof v === "object" && (ELEMENT.has(v.$$typeof) || (Array.isArray(v) && v.some((x) => drawn(x) || (Array.isArray(x) && x.some(drawn)))) || (!Array.isArray(v) && Object.values(v).some((x) => x && ELEMENT.has(x.$$typeof))));
    for (const [k, v] of Object.entries(props)) if (k === "children" || (drawn(v) && type !== PF.PanelFile)) await walk(v, rec, p, seen, k === "children" ? under : undefined);
    return;
  }
  if (Array.isArray(node) || typeof node[Symbol.iterator] === "function") { for (const v of node) await walk(v, rec, at, seen); return; }
  const proto = Object.getPrototypeOf(node);
  if (proto === Object.prototype || proto === null) for (const v of Object.values(node)) await walk(v, rec, at, seen);
}

const page = await import("../app/grid/page.tsx");
async function draw(sp) {
  globalThis.__erwRequestCache = new Map();
  const rec = {};
  try { await walk(page.default({ searchParams: Promise.resolve(sp) }), rec, "_page", new WeakSet()); }
  catch (e) { block(rec, "_page").errors.push(`the page: ${e?.message ?? e}`); }
  delete globalThis.__erwRequestCache;
  return rec;
}

/** A CSV text to its rows of cells (quoted cells read as CSV). */
function parseCsv(text) {
  const rows = [];
  let row = [], cur = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; continue; }
    if (c === '"') { q = true; continue; }
    if (c === ",") { row.push(cur); cur = ""; continue; }
    if (c === "\n") { row.push(cur); rows.push(row); row = []; cur = ""; continue; }
    cur += c;
  }
  if (cur !== "" || row.length) { row.push(cur); rows.push(row); }
  return rows;
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

/** The checks of the header for one block: its files, their provenance, and its figures. */
function blockHolds(b, name) {
  if (b.errors.length) return `a component threw: ${b.errors[0]}`;
  if (!b.nums.length) return `${name} draws no figure`;
  if (!b.files.length) return `${name} draws ${b.nums.length} figures and offers no file`;
  if (b.made.length !== b.files.length) return `${b.files.length} links and ${b.made.length} PanelFile calls`;
  const inFiles = new Set();
  for (const [i, f] of b.files.entries()) {
    const m = b.made[i];
    if (!f.href?.startsWith("data:text/csv;charset=utf-8,")) return `${f.id}: the link is not a CSV data address`;
    if (f.download !== m.name || !/^erw_grid_[a-z0-9_]+\.csv$/i.test(f.download)) return `${f.id}: downloads as ${f.download}`;
    const csv = decodeURIComponent(f.href.slice("data:text/csv;charset=utf-8,".length));
    if (csv !== m.csv) return `${f.id}: the file is not the one panelFile() writes from the panel's cells`;
    const lines = csv.split("\n");
    const top = lines.filter((l) => l.startsWith("# "));
    const want = [/^# ERW \(Energy Research Warehouse\), the Grid tool: /, /^# Panel: grid_[a-z0-9_]+.*, on the page \/grid\?/, /^# Tables: [a-z0-9_]+ /, /^# Filter: \S/, /^# (Hour|Window): \S/, /^# Drawn: \d{4}-\d\d-\d\dT/];
    const miss = want.filter((r) => !top.some((l) => r.test(l)));
    if (miss.length) return `${f.id}: the header lacks ${miss.map(String).join(", ")}`;
    if (!top.find((l) => l.startsWith("# Drawn: ")).includes(new Date(NOW).toISOString())) return `${f.id}: the drawing time is not the render's`;
    const body = parseCsv(lines.filter((l) => !l.startsWith("# ")).join("\n"));
    const width = body[0].length;
    if (body.length - 1 !== Number(f.rows)) return `${f.id}: ${body.length - 1} rows, the link says ${f.rows}`;
    if (body.some((r) => r.length !== width)) return `${f.id}: a row's cells are not its ${width} columns`;
    const cells = new Set(body.slice(1).flat());
    const beside = top.filter((l) => l.startsWith("# Figure: "));
    for (const g of m.figs) {
      const raw = String(g.raw);
      if (!cells.has(raw) && !beside.some((l) => l.includes(`: ${raw} (key ${g.check})`) || l.includes(`: ${raw}`))) return `${f.id}: ${g.check}=${raw} is not written in the file`;
      inFiles.add(`${g.check}=${raw}`);
    }
    if (Number(f.figures) !== m.figs.length) return `${f.id}: the link says ${f.figures} figures, the file holds ${m.figs.length}`;
  }
  const onPage = new Set(b.nums);
  const notInFile = [...onPage].filter((x) => !inFiles.has(x)), notOnPage = [...inFiles].filter((x) => !onPage.has(x));
  if (notInFile.length) return `${notInFile.length} figure(s) of the page not in its files: ${notInFile.slice(0, 3).join("; ")}`;
  if (notOnPage.length) return `${notOnPage.length} figure(s) of the files not on the page: ${notOnPage.slice(0, 3).join("; ")}`;
  return "";
}

const PAGES = [
  [{ grid: "ercot", view: "network" }, ["grid_network_ercot", "balance_ERCO"]],
  [{ grid: "caiso", view: "network" }, ["grid_network_caiso", "balance_CISO"]],
  [{ grid: "us48", view: "network" }, ["grid_network_us48"]],
  [{ grid: "ercot", view: "network", net: "day", t: "2021-02-15", node: "ERCO" }, ["replay_ERCO", "grid_network_ercot", "balance_ERCO"]],
  [{ grid: "us48", view: "network", net: "day", t: "2021-02-15", node: "BPAT" }, ["replay_BPAT"]],
  [{ grid: "ercot", view: "gravity" }, ["grid_gravity_ercot", "view_exchange"]],
  [{ grid: "ercot", view: "gravity", net: "day", t: "2020-08-14" }, ["grid_gravity_ercot"]],
  [{ grid: "us48", view: "gravity" }, ["grid_gravity_us48", "view_exchange"]],
  [{ grid: "ercot", view: "clean" }, ["grid_clean24_ercot", "grid_cleanweek_ercot", "mixview_clean", "grid_carbonrank_ercot", "grid_carbonmonth_ercot"]],   // session 1403: the cleanest hours, live; session 1414: the Clean tab's tables; session 1415: its carbon blocks
  [{ grid: "caiso", view: "clean" }, ["mixview_clean"]],   // session 1414: the Clean tab's tables keyed whole, each with its file
  [{ grid: "isone", view: "clean" }, ["mixview_clean"]],   // session 1414: a held grid: its cells license needed, the seven grids' others keyed and filed
  // session 1415: the Clean tab's carbon blocks, the ranked table and the monthly since 2018, each with its file, on the Lower 48
  [{ grid: "us48", view: "clean" }, ["grid_carbonrank_us48", "grid_carbonmonth_us48", "grid_clean24_us48"]],
  [{ grid: "ercot", view: "mix" }, ["grid_mix_ercot", "grid_scarcity_ercot", "grid_ercotnotice_ercot", "grid_hubprice_ercot",   // session 1402: the hub's price
    "grid_nowmix_ercot", "grid_rightnow_ercot", "grid_batteries_ercot", "grid_cost_ercot"]],   // session 1420: the older blocks' files
  [{ grid: "ercot", view: "mix", mixp: "month" }, ["grid_mix_ercot"]],
  [{ grid: "caiso", view: "mix" }, ["grid_scarcity_caiso", "grid_caisoalert_caiso", "grid_hubprice_caiso",   // session 1402: CAISO's price, drawn alone
    "grid_rightnow_caiso", "grid_batteries_caiso", "grid_building_caiso", "grid_reliability_caiso"]],   // session 1420: the older blocks' files (CAISO's queue, its reliability)
  [{ grid: "isone", view: "mix" }, ["grid_rightnow_isone", "grid_batteries_isone"]],   // session 1420: a held grid: its prices and queue held, no file of them (below)
  [{ grid: "caiso", view: "mix", mixp: "month" }, ["grid_mix_caiso"]],
  [{ grid: "us48", view: "mix", mixp: "month" }, ["grid_mix_us48"]],   // session 1185: the Lower 48 by month, the sum of the states
  [{ grid: "ercot", view: "mix", mix: "stress" }, ["mixview_stress"]],
  // session 1413: the computed views, keyed (filecalc|), each table with its file
  [{ grid: "ercot", view: "mix", mix: "day" }, ["mixview_day"]],
  [{ grid: "ercot", view: "mix", mix: "duck" }, ["mixview_duck"]],
  [{ grid: "caiso", view: "mix", mix: "duck" }, ["mixview_duck"]],
  [{ grid: "ercot", view: "mix", mix: "history" }, ["mixview_history"]],
  [{ grid: "ercot", view: "mix", mix: "supply" }, ["mixview_supply"]],
];
// GRID_FILES_OUT=<dir>: each file drawn is also written there, to read (nothing is written otherwise)
const OUT = process.env.GRID_FILES_OUT;
for (const [sp, blocks] of PAGES) {
  const rec = await draw(sp);
  const q = new URLSearchParams(sp).toString();
  if (OUT) for (const f of Object.values(rec).flatMap((r) => r.files)) fs.writeFileSync(path.join(OUT, f.download), decodeURIComponent(f.href.slice("data:text/csv;charset=utf-8,".length)));
  for (const name of blocks) {
    await check(`/grid?${q}: ${name}`, () => (rec[name] ? blockHolds(rec[name], name) : `no block ${name} (blocks: ${Object.keys(rec).join(", ")})`));
  }
  await check(`/grid?${q}: no component threw, and every file on the page is in a block that draws figures`, () => {
    const errs = Object.entries(rec).flatMap(([b, r]) => r.errors.map((e) => `${b}: ${e}`));
    if (errs.length) return errs[0];
    const stray = Object.entries(rec).filter(([, r]) => r.files.length && !r.nums.length).map(([b]) => b);
    return stray.length ? `files in blocks without a figure: ${stray.join(", ")}` : "";
  });
}

// ------------------------------------------------------------------ session 1183: each panel's anchor, and no id twice
const GA = await import("../lib/gridAnchors.ts");
const AN = GA.GRID_ANCHOR;
const gridOfBlock = (name) => name.split("_").slice(2).join("_");
/** The anchors a block must carry, for the page's query (each list: every one of them; `oneOf`: at least one). */
function anchorsOf(name, sp) {
  const grids = (sp.grids ?? sp.grid ?? "ercot").split(",");
  if (name.startsWith("grid_network_")) return [AN.network];
  if (name.startsWith("balance_")) return [AN.balance];
  if (name.startsWith("replay_")) return [AN.replay];
  if (name.startsWith("grid_gravity_")) return [AN.gravity];
  if (name === "view_exchange") return (sp.grid ?? "us48") === "us48" ? [AN.exchangeGrids] : [AN.exchangeTies, AN.exchangeMonths];
  if (name.startsWith("grid_clean24_")) return [AN.clean24];
  if (name.startsWith("grid_mix_")) return { oneOf: [AN.mix, `${AN.mix}-${gridOfBlock(name)}`] };
  if (name.startsWith("grid_scarcity_")) return [AN.scarcity];
  if (name === "grid_caisoalert_caiso") return [AN.caisoAlerts];
  if (name === "grid_ercotnotice_ercot") return [AN.ercotNotices];
  if (name.startsWith("grid_ask_")) return [AN.ask];
  if (name === "mixview_stress") return [...grids.flatMap((g, i) => ["stressRamp", "stressTight", "stressCalm"].map((k) => GA.anchorOf(k, i, g))), AN.stressGrids];
  return null;
}
const ANCHOR_PAGES = [...PAGES.map(([sp]) => sp), { grid: "us48", view: "mix" }, { grid: "ercot", view: "mix", grids: "ercot,caiso" },
  { grid: "ercot", view: "mix", mix: "stress", grids: "ercot,caiso" }, { grid: "nyiso", view: "clean" }];
const seenAnchors = new Set();
// session 1184: a panel's key in lib/gridAnchors.ts from its anchor (a second grid's anchor is the anchor and the grid)
const keyOfAnchor = (a) => Object.keys(AN).find((k) => a === AN[k]) ?? Object.keys(AN).find((k) => a.startsWith(`${AN[k]}-`));
const seenMethods = new Set();
for (const sp of ANCHOR_PAGES) {
  const rec = await draw(sp);
  const q = new URLSearchParams(sp).toString();
  await check(`/grid?${q}: each panel carries its anchor (lib/gridAnchors.ts), and no id is drawn twice`, () => {
    const why = [];
    for (const [name, b] of Object.entries(rec)) {
      const want = anchorsOf(name, sp);
      if (!want) continue;
      if (Array.isArray(want)) { for (const a of want) { if (b.ids.includes(a)) seenAnchors.add(a); else why.push(`${name} lacks #${a} (ids: ${b.ids.join(", ") || "none"})`); } }
      else if (want.oneOf.some((a) => b.ids.includes(a))) want.oneOf.forEach((a) => b.ids.includes(a) && seenAnchors.add(a));
      else why.push(`${name} lacks #${want.oneOf.join(" or #")} (ids: ${b.ids.join(", ") || "none"})`);
    }
    const ids = rec[IDS] ?? [];
    const twice = [...new Set(ids.filter((x, i) => ids.indexOf(x) !== i))];
    if (twice.length) why.push(`drawn twice: ${twice.join(", ")}`);
    if (!Object.keys(rec).some((n) => anchorsOf(n, sp))) why.push(`no panel drawn (blocks: ${Object.keys(rec).join(", ")})`);
    return why.join("; ");
  });
  // session 1184: and each panel drawn links its method, the section of its note (lib/gridAnchors.ts GRID_METHOD; the
  // fragment held to the rendered note by scripts/test-grid-methods.mjs)
  await check(`/grid?${q}: each panel links its method's own section (GRID_METHOD)`, () => {
    const why = [];
    for (const [name, b] of Object.entries(rec)) {
      const want = anchorsOf(name, sp);
      if (!want) continue;
      const keys = new Set((Array.isArray(want) ? want : want.oneOf.filter((a) => b.ids.includes(a))).map(keyOfAnchor));
      for (const k of keys) {
        seenMethods.add(k);
        if (!b.methods.includes(GA.GRID_METHOD[k])) why.push(`${name} (${k}) lacks ${GA.GRID_METHOD[k]} (links: ${b.methods.join(", ") || "none"})`);
      }
    }
    return why.join("; ");
  });
}
await check("every panel's method link is drawn on a page above (session 1184)", () => {
  const miss = Object.keys(GA.GRID_METHOD).filter((k) => !seenMethods.has(k));
  return miss.length ? `never drawn: ${miss.join(", ")}` : "";
});
await check("every anchor of lib/gridAnchors.ts is drawn on a page above, and every panel's address names its tab's words", () => {
  const miss = Object.values(AN).filter((a) => !seenAnchors.has(a));
  if (miss.length) return `never drawn: ${miss.join(", ")}`;
  const keys = new Set(GA.PANEL_ANCHORS.map((p) => p.key));
  const lost = Object.keys(AN).filter((k) => !keys.has(k));
  return lost.length ? `anchors without a panel address: ${lost.join(", ")}` : "";
});
await check("two grids on one page: the second grid's mix panel and stress tables take the anchor and the grid", async () => {
  const rec = await draw({ grid: "ercot", view: "mix", mix: "stress", grids: "ercot,caiso" });
  const ids = rec[IDS] ?? [];
  const want = ["stress-ramp", "stress-tight", "stress-calm", "stress-ramp-caiso", "stress-tight-caiso", "stress-calm-caiso", "stress-grids"];
  return want.every((a) => ids.includes(a)) && !ids.includes("stress-ramp-ercot") ? "" : `ids: ${ids.filter((x) => x.startsWith("stress")).join(", ")}`;
});

// session 1185: the Lower 48 by month is drawn from the states (lib/lower48.ts): every figure a states_sum key or a share of
// two, the file grid_mix_us48_monthly, the panel's method and the section of the sum (METHOD_MIX_US48)
await check("/grid?grid=us48&view=mix&mixp=month: the Lower 48 by month, the sum of the states, keyed, its file and both method links", async () => {
  const b = (await draw({ grid: "us48", view: "mix", mixp: "month" })).grid_mix_us48;
  if (!b) return "no block grid_mix_us48";
  const kinds = new Set(b.nums.map((x) => x.split("|")[0]));
  if (new Set(b.nums).size !== 2 + 9 * 3 || [...kinds].some((k) => k !== "states_sum" && k !== "calc")) return `${new Set(b.nums).size} figures, kinds ${[...kinds].join(", ")}`;
  if (b.files.map((f) => f.id).join(",") !== "grid_mix_us48_monthly") return `files ${b.files.map((f) => f.id).join(",")}`;
  if (!b.methods.includes(GA.METHOD_MIX) || !b.methods.includes(GA.METHOD_MIX_US48)) return `links ${b.methods.join(", ")}`;
  return b.nums.some((x) => x.startsWith("states_sum|state_generation_mix_monthly|net_generation_coal_mwh|2026-08-01T00:00:00Z|2026-09-01T00:00:00Z|lower48=")) ? "" : b.nums.slice(0, 3).join("; ");
});
// session 1402: the hub's price beside the hourly mix: four keyed figures of the three new kinds, its file, its anchor
// (#hub-price, and the grid after the first), its method; the held, paused and hubless grids one line and no read
await check("the hub's price beside the hourly mix: its figures, file, anchor and method; a second grid takes the anchor and its grid; the others say why", async () => {
  const rec = await draw({ grid: "ercot", view: "mix", grids: "ercot,caiso" });
  const e = rec.grid_hubprice_ercot, c = rec.grid_hubprice_caiso;
  if (!e || !c) return `blocks: ${Object.keys(rec).join(", ")}`;
  for (const [b, id] of [[e, GA.HUB_PRICE_ANCHOR], [c, `${GA.HUB_PRICE_ANCHOR}-caiso`]]) {
    const kinds = [...new Set(b.nums.map((x) => x.split("|")[0]))].sort().join(",");
    if (kinds !== "series_hmax,series_hmean,series_hn" || new Set(b.nums).size !== 4) return `${id}: ${b.nums.join("; ")}`;
    if (!b.ids.includes(id)) return `lacks #${id} (ids: ${b.ids.join(", ")})`;
    if (!b.methods.includes(GA.METHOD_HUB_PRICE)) return `${id}: links ${b.methods.join(", ")}`;
  }
  if (e.files.map((f) => f.id).join(",") !== "grid_hubprice_ercot") return `files ${e.files.map((f) => f.id).join(",")}`;
  for (const g of ["pjm", "miso", "nyiso", "isone", "us48"]) {
    const r = await draw({ grid: g, view: "mix" });
    const b = r[`grid_hubprice_${g}`];
    if (!b || b.nums.length || b.files.length) return `${g}: ${b ? `${b.nums.length} figures, ${b.files.length} files` : "no block"}`;
  }
  return "";
});
// session 1403: the cleanest hours, live: four keyed figures (series_n, series_min, series_max, series_mean), its file, its
// anchor (#clean-week, and the grid after the first), its method; a grid whose week is not whole in the stand-in says so
await check("the cleanest hours, live: its figures, file, anchor and method; a second grid takes the anchor and its grid", async () => {
  const rec = await draw({ grid: "ercot", view: "clean", grids: "ercot,caiso" });
  const e = rec.grid_cleanweek_ercot, c = rec.grid_cleanweek_caiso;
  if (!e || !c) return `blocks: ${Object.keys(rec).join(", ")}`;
  for (const [b, id, g] of [[e, GA.CLEAN_WEEK_ANCHOR, "ercot"], [c, `${GA.CLEAN_WEEK_ANCHOR}-caiso`, "caiso"]]) {
    const kinds = [...new Set(b.nums.map((x) => x.split("|")[0]))].sort().join(",");
    if (kinds !== "series_max,series_mean,series_min,series_n" || new Set(b.nums).size !== 4) return `${id}: ${b.nums.join("; ")}`;
    if (!b.ids.includes(id)) return `lacks #${id} (ids: ${b.ids.join(", ")})`;
    if (!b.methods.includes(GA.METHOD_CLEAN_WEEK)) return `${id}: links ${b.methods.join(", ")}`;
    if (b.files.map((f) => f.id).join(",") !== `grid_cleanweek_${g}`) return `files ${b.files.map((f) => f.id).join(",")}`;
    const why = blockHolds(b, `grid_cleanweek_${g}`);
    if (why) return `${id}: ${why}`;
  }
  if (!e.nums.includes("series_n|carbon_intensity_hourly|intensity_generation|2026-10-13T05:00:00Z|2026-10-20T05:00:00Z|eia930:ERCO=168")) return e.nums.join("; ");
  const n = (await draw({ grid: "nyiso", view: "clean" })).grid_cleanweek_nyiso;
  return !n ? "no block grid_cleanweek_nyiso" : n.nums.length || n.files.length ? `nyiso: ${n.nums.length} figures, ${n.files.length} files` : "";
});
// session 1406: the Lower 48 on the Network tab: under the seven grids' net exchange (its 14 figures and file as before),
// the seven's demand and the Lower 48's (US48) in the hour, the sum and the share (calc|add, calc|addpct), the seven's
// exchange and its two parts in words; a second file (grid_network_us48_demand), its anchor and its method
await check("the Lower 48's Network panel: the seven's demand and the Lower 48's, the sum, the share and the exchange; its file, anchor and method", async () => {
  const b = (await draw({ grid: "us48", view: "network" })).grid_network_us48;
  if (!b) return "no block grid_network_us48";
  if (b.files.map((f) => f.id).join(",") !== "grid_network_us48,grid_network_us48_demand") return `files ${b.files.map((f) => f.id).join(",")}`;
  if (!b.ids.includes(GA.LOWER48_DEMAND_ANCHOR)) return `lacks #${GA.LOWER48_DEMAND_ANCHOR} (ids: ${b.ids.join(", ")})`;
  if (!b.methods.includes(GA.METHOD_NETWORK) || !b.methods.includes(GA.METHOD_NETWORK_US48)) return `links ${b.methods.join(", ")}`;
  const keys = new Set(b.nums.map((x) => x.slice(0, x.lastIndexOf("="))));
  if (keys.size !== 14 + 13) return `${keys.size} figures, not 27`;
  if (!b.nums.includes("series|eia930_all_demand|eia930:US48|demand_mw|2026-10-21T23:00:00Z=497563")) return "no Lower 48 demand of 497563 MW";
  for (const k of ["calc|add|series~eia930_all_demand~", "calc|addpct|series~eia930_all_demand~", "calc|add|net~import~", "calc|add|net~tie~"]) if (![...keys].some((x) => x.startsWith(k))) return `no figure keyed ${k}...`;
  if (b.nums.some((x) => x.endsWith("=NaN"))) return "a figure without a value (NaN)";
  // the method link opens its section: the id the site's renderer writes for the heading (lib/markdown.ts)
  const MD = await import("../lib/markdown.ts");
  const html = String(MD.render(fs.readFileSync(path.join(SITE, "..", "docs", "methods", "grid_network.md"), "utf-8"), "docs/methods/grid_network.md"));
  if (!html.includes(`id="${GA.METHOD_NETWORK_US48.split("#")[1]}"`)) return `${GA.METHOD_NETWORK_US48}: no such heading in grid_network.md`;
  return blockHolds(b, "grid_network_us48");
});
// the ERCOT Exchange block's twelve months are drawn from the fixture (a file of its own, the neighbours')
await check("/grid?grid=ercot&view=gravity: the Exchange blocks offer two files, the ties' and the twelve months'", async () => {
  const b = (await draw({ grid: "ercot", view: "gravity" })).view_exchange;
  const ids = b.files.map((f) => f.id).join(",");
  return ids === "grid_exchange_ercot_ties,grid_exchange_ercot_twelve_months" ? "" : ids;
});

// ------------------------------------------------------------------ the file's cells, by themselves
const { Num } = await import("../components/Num.tsx");
const { Missing } = await import("../components/mix/Now.tsx");
const { licenseHeldRow, LICENSE_NEEDED } = await import("../lib/license.ts");
const HELD = "series|iso_hub_prices_history|iso:isone|lmp_da_mean|2026-10-20T00:00:00Z";
await check("a held grid's figure is written \"license needed\", never its value, in a cell and in a header line", () => {
  if (!licenseHeldRow("iso_hub_prices_history", "iso:isone", new Date(NOW))) return "the test's key is not held on the fixture's day: choose another";
  const of = { panel: "grid_test_isone", title: "t", page: "/grid?grid=isone", tables: ["iso_hub_prices_history"], filter: "iso:isone", window: "Hour: x",
    figures: [{ label: "held beside", value: { check: HELD, raw: 98765.4321 } }] };
  const f = PF.panelFile(of, ["Hub", "USD"], [["ISO-NE", h(Num, { check: HELD, raw: 12345.678 }, "12,346")], ["ERCOT", { check: "series|iso_rtm_hub_prices|ercot:HB_HUBAVG|spp_rtm|2026-10-20T00:00:00Z", raw: 41.5 }]]);
  if (f.csv.includes("12345.678") || f.csv.includes("98765.4321")) return "a held value is in the file";
  if (!f.csv.includes(`ISO-NE,${LICENSE_NEEDED}`) || !f.csv.includes(`# Figure: held beside: ${LICENSE_NEEDED}`)) return `the held cells: ${f.csv}`;
  if (f.held !== 2 || f.figs.length !== 1 || f.figs[0].raw !== 41.5) return `held ${f.held}, figures ${JSON.stringify(f.figs)}`;
  return f.csv.includes("ERCOT,41.5") ? "" : "the figure not held is not written";
});
await check("a cell in words is its words; a figure inside words is its value whole; a comma or a quote is quoted", () => {
  const F = ({ f }) => h("span", { title: f.tip }, h(Num, { check: f.check, raw: f.raw }, "1,234.5"));
  const of = { panel: "grid_test_ercot", title: "t", page: "/grid", tables: ["x"], filter: "y", window: "Window: z" };
  const f = PF.panelFile(of, ["A", "B", "C"], [[h(Fragment, null, "El Paso Electric ", h("span", null, "EPE")), h(F, { f: { check: "net|tie|ERCO|EPE|h", raw: -1234.5, tip: "" } }), h(Missing, { words: "could not be read", why: "w" })],
    ['say "this", and that', h("span", null, "MW ", h(Num, { check: "k|2", raw: 7 }, "7")), ""]]);
  const rows = f.csv.split("\n").filter((l) => l && !l.startsWith("#"));
  return rows[1] === "El Paso Electric EPE,-1234.5,could not be read" && rows[2] === '"say ""this"", and that",7,' ? "" : JSON.stringify(rows);
});

// ------------------------------------------------------------------ the two check scripts: their reader, on these pages
// scripts/grid-files.mjs is what check-table-downloads.mjs and check-download.mjs --grid read a served page with; here it
// reads the files of the pages drawn above, and a PanelFile drawn to HTML as Next writes it
const GF = await import("./grid-files.mjs");
const { renderToStaticMarkup } = await import("react-dom/server");
for (const [address, want] of GF.GRID_FILE_PAGES) {
  await check(`the checks' page ${address}: it offers ${want.join(", ")}, and each file is whole (scripts/grid-files.mjs)`, async () => {
    const rec = await draw(Object.fromEntries(new URL(address, "https://x.invalid").searchParams));
    const fs_ = Object.values(rec).flatMap((r) => r.files);
    const raws = new Set(Object.values(rec).flatMap((r) => r.nums.map((n) => n.slice(n.indexOf("=") + 1))));
    const miss = GF.missingFiles(fs_.map((f) => f.id), want);
    if (miss.length) return `missing ${miss.join(", ")} (offers ${fs_.map((f) => f.id).join(", ")})`;
    for (const f of fs_) {
      const got = { ...f, csv: decodeURIComponent(f.href.slice("data:text/csv;charset=utf-8,".length)), rows: Number(f.rows), figures: Number(f.figures) };
      const why = GF.gridFileProblems(got, raws);
      if (why.length) return `${f.id}: ${why.join("; ")}`;
    }
    return "";
  });
}
await check("scripts/grid-files.mjs reads a PanelFile from its HTML as React writes it (entities, quotes, a held figure), and finds a stray number", () => {
  const of = { panel: "grid_test_ercot", part: "x", title: "the test's table, \"quoted\" & <marked>", page: "/grid?grid=ercot&view=network", tables: ["eia930_all_interchange (a, b)"], filter: "ERCO's ties", window: "Hour: 2026-10-21 23:00 UTC" };
  const rows = [["Neighbour's \"name\", one", { check: "net|tie|ERCO|SWPP|h", raw: -49.5 }], ["ISO-NE", { check: HELD, raw: 3 }]];
  const html = renderToStaticMarkup(h(PF.PanelFile, { of, columns: ["Neighbour", "Flow, MW"], rows }));
  const [f, ...more] = GF.gridFilesOf(html);
  if (!f || more.length) return `read ${more.length + (f ? 1 : 0)} files`;
  if (f.csv !== PF.panelFile(of, ["Neighbour", "Flow, MW"], rows).csv) return "the file read from the HTML is not the one written";
  if (f.id !== "grid_test_ercot_x" || f.rows !== 2 || f.figures !== 1 || f.held !== 1) return JSON.stringify({ id: f.id, rows: f.rows, figures: f.figures, held: f.held });
  const ok = GF.gridFileProblems(f, new Set(["-49.5"]));
  if (ok.length) return `whole, it is said: ${ok.join("; ")}`;
  const stray = GF.gridFileProblems(f, new Set(["-49"]));
  return stray.some((x) => x.includes("no figure of the page")) ? "" : `a number not on the page passes: ${stray.join("; ")}`;
});
await check("scripts/check-table-downloads.mjs and check-download.mjs check the Grid panels' files (session 1182)", () => {
  const a = fs.readFileSync(path.join(here, "check-table-downloads.mjs"), "utf-8"), b = fs.readFileSync(path.join(here, "check-download.mjs"), "utf-8");
  if (!a.includes('from "./grid-files.mjs"') || !a.includes("GRID_FILE_PAGES") || !a.includes("missingFiles")) return "check-table-downloads.mjs does not read the panels' files";
  return b.includes('from "./grid-files.mjs"') && b.includes("--grid") && b.includes("gridFileProblems") ? "" : "check-download.mjs does not read the panels' files";
});

// session 1413: the computed views' tables (components/mix/views.tsx: the average day, the duck curve by year, the history
// by state, availability) each carry their anchor (lib/gridAnchors.ts MIX_VIEW_ANCHOR, a second grid or state the anchor
// and its name) and link their method (METHOD_MIX_VIEWS), and offer exactly their files
await check("the computed views: each table carries its anchor, links METHOD_MIX_VIEWS and offers its file; a second grid or state takes the anchor and its name", async () => {
  const MV = GA.MIX_VIEW_ANCHOR;
  const want = [
    [{ grid: "ercot", view: "mix", mix: "day", grids: "ercot,caiso" }, "mixview_day", [MV.dayShares, MV.dayPeak], ["grid_mixday_all_shares", "grid_mixday_all_peak"], 2],
    [{ grid: "ercot", view: "mix", mix: "duck", grids: "ercot,caiso" }, "mixview_duck", [MV.duckYears, `${MV.duckYears}-caiso`], ["grid_duck_ercot", "grid_duck_caiso"], 2],
    [{ grid: "ercot", view: "mix", mix: "history", states: "TX,CA" }, "mixview_history", [MV.historyShares, `${MV.historyShares}-ca`], ["grid_history_tx", "grid_history_ca"], 2],
    [{ grid: "ercot", view: "mix", mix: "supply", grids: "ercot,caiso" }, "mixview_supply", [MV.supplyMean, MV.supplyTight, `${MV.supplyTight}-caiso`], ["grid_supply_all_mean", "grid_supply_ercot_tight", "grid_supply_caiso_tight"], 3],
  ];
  for (const [sp, name, ids, files, lines] of want) {
    const rec = await draw(sp), b = rec[name];
    if (!b) return `no block ${name}`;
    const held = blockHolds(b, name);
    if (held) return `${name}: ${held}`;
    const miss = ids.filter((a) => !b.ids.includes(a));
    if (miss.length) return `${name} lacks #${miss.join(", #")} (ids: ${b.ids.join(", ")})`;
    if (b.files.map((f) => f.id).join(",") !== files.join(",")) return `${name}: files ${b.files.map((f) => f.id).join(",")}`;
    if (b.methods.filter((m) => m === GA.METHOD_MIX_VIEWS).length !== lines) return `${name}: ${b.methods.filter((m) => m === GA.METHOD_MIX_VIEWS).length} links to METHOD_MIX_VIEWS, not ${lines}`;
    const ids2 = rec[IDS] ?? [];
    const twice = [...new Set(ids2.filter((x, i) => ids2.indexOf(x) !== i))];
    if (twice.length) return `${name}: drawn twice: ${twice.join(", ")}`;
  }
  return "";
});

// session 1414: the Clean tab's five tables (components/mix/views.tsx CleanView) each carry their anchor (lib/gridAnchors.ts
// CLEAN_TABLE_ANCHOR, a second grid the anchor and its grid), link their method (METHOD_CLEAN_TABLES) and offer exactly
// their files; a held grid draws no table of its own, so its anchors and files are not drawn
await check("the Clean tab's tables: each carries its anchor, links METHOD_CLEAN_TABLES and offers its file; a second grid takes the anchor and its grid; a held grid has none of its own", async () => {
  const CA = GA.CLEAN_TABLE_ANCHOR;
  const want = [
    [{ grid: "ercot", view: "clean", grids: "ercot,caiso" }, [CA.shares, CA.purchase, CA.months, CA.shift, `${CA.purchase}-caiso`, `${CA.months}-caiso`, `${CA.shift}-caiso`, CA.grids],
      ["grid_clean_all_shares_2024", "grid_clean_ercot_purchase_2024", "grid_clean_ercot_months_2024", "grid_clean_ercot_shift", "grid_clean_caiso_purchase_2024", "grid_clean_caiso_months_2024", "grid_clean_caiso_shift", "grid_clean_all_grids_2024"], 8],
    [{ grid: "ercot", view: "clean", grids: "isone,ercot" }, [CA.shares, `${CA.purchase}-ercot`, `${CA.months}-ercot`, `${CA.shift}-ercot`, CA.grids],
      ["grid_clean_all_shares_2025", "grid_clean_ercot_purchase_2025", "grid_clean_ercot_months_2025", "grid_clean_ercot_shift", "grid_clean_all_grids_2025"], 5],
  ];
  for (const [sp, ids, files, lines] of want) {
    const rec = await draw(sp), b = rec.mixview_clean;
    if (!b) return `no block mixview_clean (blocks: ${Object.keys(rec).join(", ")})`;
    const held = blockHolds(b, "mixview_clean");
    if (held) return `${sp.grids}: ${held}`;
    const miss = ids.filter((a) => !b.ids.includes(a));
    if (miss.length) return `${sp.grids} lacks #${miss.join(", #")} (ids: ${b.ids.join(", ")})`;
    if (b.ids.some((a) => /^clean-(purchase|months|shift)-(isone|miso|nyiso)$/.test(a))) return `${sp.grids}: a held grid's anchor`;
    if (b.files.map((f) => f.id).join(",") !== files.join(",")) return `${sp.grids}: files ${b.files.map((f) => f.id).join(",")}`;
    if (b.methods.filter((m) => m === GA.METHOD_CLEAN_TABLES).length !== lines) return `${sp.grids}: ${b.methods.filter((m) => m === GA.METHOD_CLEAN_TABLES).length} links to METHOD_CLEAN_TABLES, not ${lines}`;
    if (b.files.some((f) => /isone|miso|nyiso/.test(f.id))) return `${sp.grids}: a held grid's file`;
    const ids2 = rec[IDS] ?? [];
    const twice = [...new Set(ids2.filter((x, i) => ids2.indexOf(x) !== i))];
    if (twice.length) return `${sp.grids}: drawn twice: ${twice.join(", ")}`;
  }
  return "";
});

// session 1415 (chain 107): the Clean tab's carbon blocks, "Carbon intensity now, ranked" (grid_carbonrank_<grid>) and
// "Monthly since 2018" (grid_carbonmonth_<grid>): each carries its anchor (lib/gridAnchors.ts EMISSIONS_ANCHOR, the same
// on every grid), links METHOD_EMISSIONS_BLOCKS once and offers its one file; the monthly block's file carries the two
// figures of the chart's note in its header (the months left out, the hours without hydro); no id is drawn twice
await check("the Clean tab's carbon blocks: each carries its anchor, links METHOD_EMISSIONS_BLOCKS and offers its file, the note's two figures in the monthly file", async () => {
  for (const grid of ["ercot", "caiso", "us48", "isone"]) {
    const rec = await draw({ grid, view: "clean" });
    for (const [part, anchor] of [["carbonrank", GA.EMISSIONS_ANCHOR.rank], ["carbonmonth", GA.EMISSIONS_ANCHOR.monthly]]) {
      const name = `grid_${part}_${grid}`, b = rec[name];
      if (!b) return `${grid}: no block ${name}`;
      const why = blockHolds(b, name);
      if (why) return `${grid}: ${why}`;
      if (!b.ids.includes(anchor)) return `${name} lacks #${anchor} (ids: ${b.ids.join(", ") || "none"})`;
      if (b.methods.filter((m) => m === GA.METHOD_EMISSIONS_BLOCKS).length !== 1) return `${name}: ${b.methods.filter((m) => m === GA.METHOD_EMISSIONS_BLOCKS).length} links to METHOD_EMISSIONS_BLOCKS`;
      if (b.files.map((f) => f.id).join(",") !== name) return `${name}: files ${b.files.map((f) => f.id).join(",")}`;
    }
    const m = rec[`grid_carbonmonth_${grid}`];
    const csv = decodeURIComponent(m.files[0].href.slice("data:text/csv;charset=utf-8,".length));
    for (const k of ["fmt|n0|filecalc|carbon_left_out_n|carbon_left_out.json|intensity_generation", "fmt|n0|file|carbon_left_out.json|hydro_gap.hours"]) {
      if (!m.nums.some((n) => n.startsWith(`${k}=`))) return `${grid}: the monthly block lacks ${k}`;
      if (!csv.includes(`(key ${k})`)) return `${grid}: the monthly file's header lacks ${k}`;
    }
    const ids = rec[IDS] ?? [];
    const twice = [...new Set(ids.filter((x, i) => ids.indexOf(x) !== i))];
    if (twice.length) return `${grid}: drawn twice: ${twice.join(", ")}`;
  }
  return "";
});

// session 1416 (chain 107): "Yesterday" and the mix table (components/grid/Conditions.tsx), named panels: each block's
// figures all in its file and back (blockHolds), its anchor (the ids the sections had), one link to METHOD_CONDITIONS
await check("\"Yesterday\" and the mix table: each carries its anchor, links METHOD_CONDITIONS once and offers its file, every figure in it", async () => {
  const code = { ercot: "erco", caiso: "ciso", isone: "isne", us48: "us48" };
  for (const grid of ["ercot", "caiso", "isone", "us48"]) {
    const rec = await draw({ grid, view: "mix" });
    for (const [name, anchor] of [[`grid_yesterday_${grid}`, GA.yesterdayAnchor(code[grid])], ["grid_mixtable_all", GA.CONDITIONS_ANCHOR.mixTable]]) {
      const b = rec[name];
      if (!b) return `${grid}: no block ${name}`;
      const why = blockHolds(b, name);
      if (why) return `${grid}: ${why}`;
      if (!b.ids.includes(anchor)) return `${name} lacks #${anchor} (ids: ${b.ids.join(", ") || "none"})`;
      if (b.methods.filter((m) => m === GA.METHOD_CONDITIONS).length !== 1) return `${name}: ${b.methods.filter((m) => m === GA.METHOD_CONDITIONS).length} links to METHOD_CONDITIONS`;
      if (b.files.map((f) => f.id).join(",") !== name) return `${name}: files ${b.files.map((f) => f.id).join(",")}`;
    }
    const ids = rec[IDS] ?? [];
    const twice = [...new Set(ids.filter((x, i) => ids.indexOf(x) !== i))];
    if (twice.length) return `${grid}: drawn twice: ${twice.join(", ")}`;
  }
  return "";
});

// session 1420: the checks' reader finds a file whose link counts a held figure the file does not write "license needed"
await check("scripts/grid-files.mjs: a file whose held figures are not written \"license needed\" is not whole (1420)", () => {
  const of = { panel: "grid_test_isone", title: "t", page: "/grid?grid=isone", tables: ["iso_hub_prices_history"], filter: "iso:isone", window: "Hour: x" };
  const rows = [["ISO-NE", { check: HELD, raw: 3 }], ["ERCOT", { check: "series|iso_rtm_hub_prices|ercot:HB_HUBAVG|spp_rtm|2026-10-20T00:00:00Z", raw: 41.5 }]];
  const [f] = GF.gridFilesOf(renderToStaticMarkup(h(PF.PanelFile, { of, columns: ["Hub", "USD"], rows })));
  if (GF.gridFileProblems(f, new Set(["41.5"])).length) return `whole, it is said: ${GF.gridFileProblems(f, new Set(["41.5"])).join("; ")}`;
  const bad = GF.gridFileProblems({ ...f, csv: f.csv.replace(`ISO-NE,${LICENSE_NEEDED}`, "ISO-NE,") }, new Set(["41.5"]));
  return bad.some((x) => x.includes("held figure")) ? "" : `a held figure left out passes: ${bad.join("; ") || "no problem"}`;
});

// session 1420 (chain 111): the older blocks' files (YourGrid's Right now, Batteries, What it costs, What is being built;
// Reliability's three tables; the Now view's mix in that hour): each block's figures all in its files and back
// (blockHolds), each file named for its block; a held grid's prices and queue draw no figure and offer no file; the
// datacenters' figures, held whole, are written "license needed" in the Building file; Reliability's daily files write the
// batteries' share and MW in two columns, and the days per year a blank where the page draws a dot
await check("the older blocks' files (1420): every figure in its block's file and back, a held grid's prices and queue never in a file", async () => {
  const want = { ercot: { grid_rightnow_ercot: ["grid_rightnow_ercot"], grid_batteries_ercot: ["grid_batteries_ercot"], grid_cost_ercot: ["grid_cost_ercot"], grid_nowmix_ercot: ["grid_nowmix_ercot"] },
    caiso: { grid_rightnow_caiso: ["grid_rightnow_caiso"], grid_batteries_caiso: ["grid_batteries_caiso"], grid_building_caiso: ["grid_building_caiso"],
      grid_reliability_caiso: ["grid_reliability_caiso_days_per_year", "grid_reliability_caiso_highest_peaks", "grid_reliability_caiso_latest_days"] },
    isone: { grid_rightnow_isone: ["grid_rightnow_isone"], grid_batteries_isone: ["grid_batteries_isone"], grid_cost_isone: [], grid_building_isone: [], grid_nowmix_isone: [] } };
  const csvOf = (f) => decodeURIComponent(f.href.slice("data:text/csv;charset=utf-8,".length));
  for (const [grid, blocks] of Object.entries(want)) {
    const rec = await draw({ grid, view: "mix" });
    for (const [name, files] of Object.entries(blocks)) {
      const b = rec[name];
      if (!b) return `${grid}: no block ${name}`;
      if (b.files.map((f) => f.id).join(",") !== files.join(",")) return `${name}: files ${b.files.map((f) => f.id).join(",") || "none"}, not ${files.join(",") || "none"}`;
      if (files.length) { const why = blockHolds(b, name); if (why) return `${grid}: ${why}`; }
      else if (b.nums.length) return `${name}: ${b.nums.length} figures and no file`;
    }
    if (grid === "isone") {
      const all = Object.values(rec).flatMap((r) => r.files).map(csvOf).join("\n");
      if (/price_board_latest\||iso_hub_prices_history\||gridq\|isone/.test(all) || /isone_queue:/.test(all)) return "a held table's figure of ISO-NE in a file";
      // (the held lines' words, "license needed" and why, are held by test-grid-render.mjs's cases of the two blocks)
    }
    if (grid === "caiso") {
      const bld = csvOf(rec.grid_building_caiso.files[0]);
      if (!bld.includes("# Figure: Datacenter facilities mapped to CAISO: license needed") || !bld.includes("# Figure: Their MW, where a source states it: license needed")) return "the datacenters' figures are not written license needed";
      const [days, tight] = rec.grid_reliability_caiso.files.map(csvOf);
      if (/^\d{4},.*\./m.test(days.split("\n").filter((l) => !l.startsWith("#")).slice(1).join("\n"))) return "a dot in the days per year";
      const head = tight.split("\n").find((l) => !l.startsWith("#"));
      if (!head.includes("percent\",\"Batteries at the evening peak, MW\"")) return `the daily file's columns: ${head}`;
      if (!rec.grid_reliability_caiso.nums.some((n) => n.includes("|battery_mw_evening_peak|"))) return "no battery MW drawn on the fixture";
    }
  }
  return "";
});

console.log(failures ? `${failures} of ${cases} case(s) failed` : `every case holds (${cases} cases)`);
process.exitCode = failures ? 1 : 0;
