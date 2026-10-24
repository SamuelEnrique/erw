// Energy Research Warehouse (ERW) site, session 1404 (chain 100): the Grid page (app/grid/page.tsx) drawn outside Next on
// committed real rows, block by block, with its rendered words. For scripts/test-grid-render.mjs.
//
// The stand-in for PostgREST and Storage is session 1182's (scripts/test-grid-files.mjs), on the same committed fixtures,
// assembled the same way: session 1181's rows (fixtures/grid_failed_reads.json) and the week's generation and demand
// (grid_balance.json), the scarcity strip (scarcity_strip.json), CAISO's and ERCOT's notices (caiso_alerts.json,
// ercot_notices.json), session 1152's monthly mix (tests/fixtures/session1152/mix_hourly_erco.json), ERCOT's
// ba_supply_monthly and CAISO's monthly mix (grid_files.json), the Lower 48's states (lower48_mix.json), the hubs' prices
// (hub_price.json), the cleanest hours' week (clean_week.json), and the committed snapshot (data/grid_network.json). Every
// other table answers no row. The clock is the fixtures' read time.
//
// The walk is the one of test-grid-files.mjs and test-grid-failed-reads.mjs (every server component called, a client
// component's props walked, one render a page), and it keeps, for each block (a data-grid-panel name, the balance, the
// replayed day, the gravity day, a held line, the Exchange and stress views): its figures (data-check with data-raw),
// its rendered text (the strings the server draws, in order, spaces as written), the words on hover (a title, a
// Missing's reason, a chart's accessible name), its headings, its ids (and the id of an element that holds it alone), its links to a method note, its files (data-grid-file), and the errors a component threw.
// A block inside another adds its text and figures to the one around it too (`text` and `all`), keeping its own (`nums`).
// Session 1422: the older blocks without a name on the page are named here as overlays (older_<name>, OLDER_MARKS and
// OLDER_COMPONENTS below), which take nothing from the blocks around them; a written block's markdown is read as its words.
// Importing this module sets the environment, the clock and globalThis.fetch for the whole process: a test imports it
// first and alone.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const ORIGIN = "https://erw-session1404.invalid";
process.env.SUPABASE_URL = `${ORIGIN}/rest/v1/`;
process.env.SUPABASE_ANON_KEY = "session1404-test";
process.env.ERW_PAGES_TOGETHER = "1";
for (const k of ["ERW_READ_TIMING", "NEXT_PHASE", "NEXT_RUNTIME", "SUPABASE_SERVICE_KEY", "GRID_FILES_OUT", "ERW_SIZES"]) delete process.env[k];
console.error = () => {};

const fx = (f) => JSON.parse(fs.readFileSync(path.join(here, "fixtures", f), "utf-8"));
const mine = fx("grid_failed_reads.json"), bal = fx("grid_balance.json"), strip = fx("scarcity_strip.json");
const caisoN = fx("caiso_alerts.json"), ercotN = fx("ercot_notices.json"), files = fx("grid_files.json");
const monthly = JSON.parse(fs.readFileSync(path.join(SITE, "..", "tests", "fixtures", "session1152", "mix_hourly_erco.json"), "utf-8")).monthly;
const snapText = fs.readFileSync(path.join(SITE, "data", "grid_network.json"), "utf-8");

export const NOW = Date.parse(mine.read_at);
Date.now = () => NOW;
const realSetTimeout = globalThis.setTimeout;
globalThis.setTimeout = (f, ms, ...a) => realSetTimeout(f, ms === 1000 || ms === 3000 ? 0 : ms, ...a);

// ------------------------------------------------------------------ the rows the stand-in holds (session 1182's)
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
const l48 = fx("lower48_mix.json");
add("state_generation_mix_monthly", Object.entries(l48.months).flatMap(([m, states]) => Object.entries(states).flatMap(([st, vals]) => vals.flatMap((v, i) => (v === null ? [] : [{ ...asSeries(`eia:${st}`, `net_generation_${l48.stems[i]}_mwh`, `${m}-01T00:00:00+00:00`, v, "MWh"), freq: "P1M" }])))));
const hubFx = fx("hub_price.json");
for (const [k, rs] of Object.entries(hubFx.rows)) { const [e, v] = k.split("|"); add("iso_rtm_hub_prices", rs.map(([ts, x]) => ({ ...asSeries(e, v, ts, x, "USD/MWh"), freq: "PT15M" }))); }
const weekFx = fx("clean_week.json");
const haveC = new Set(T.get("carbon_intensity_hourly").map((r) => `${r.entity}|${r.variable}|${Date.parse(r.ts_utc)}`));
for (const [k, rs] of Object.entries(weekFx.week.rows)) { const [e, v] = k.split("|"); add("carbon_intensity_hourly", rs.filter(([ts]) => !haveC.has(`${k}|${Date.parse(ts)}`)).map(([ts, x]) => asSeries(e, v, tsOf(ts), x, "kg/MWh"))); }
// session 1415: carbon_intensity_monthly's intensity_generation, every row the live set holds (fixtures/carbon_monthly.json,
// read once with the anon key), so the Clean tab's "Monthly since 2018" (grid_carbonmonth_<grid>) draws its figures
const monthlyC = fx("carbon_monthly.json");
add("carbon_intensity_monthly", monthlyC.rows.map(([e, ts, x]) => ({ ...asSeries(e, monthlyC.variable, ts, x, monthlyC.unit), freq: monthlyC.freq })));
// two more committed fixtures, for the grid's own older blocks the pinned tests read: the battery units of storage_capacity
// (fixtures/grid_units.json, session 1180: PJM, SPP and MISO whole, every tenth other unit) for the Batteries block, and
// ERCOT's UTC day of 21 October 2026 (fixtures/grid_yesterday.json, session 1166: demand, the day-ahead forecast, the
// stations' temperatures) for the block "Yesterday"; an hour of demand already held is not added twice
add("storage_capacity", fx("grid_units.json").rows.map((r) => ({ entity_id: r.entity_id, capacity_mw: r.capacity_mw, status: r.status, extra: { iso: r.iso, energy_capacity_mwh: r.mwh, state: r.state, planned_year: r.planned_year } })));
const yest = fx("grid_yesterday.json");
const haveY = new Set(T.get("eia930_all_demand").filter((r) => r.entity === "eia930:ERCO").map((r) => Date.parse(r.ts_utc)));
add("eia930_all_demand", yest.demand.filter((r) => !haveY.has(Date.parse(r.ts_utc))).map((r) => asSeries("eia930:ERCO", "demand_mw", r.ts_utc, r.value)));
add("eia930_all_demand", yest.forecast.map((r) => asSeries("eia930:ERCO", "demand_forecast_mw", r.ts_utc, r.value)));
for (const [st, rs] of Object.entries(yest.temps)) add("weather_obs_hourly", rs.map((r) => asSeries(`nws:${st}`, "temperature_f", r.ts_utc, r.value, "F")));
// session 1420 (chain 111): the older blocks' own rows, so each draws its figures and its file: four tables of session
// 1411's committed reads (fixtures/grid_older_reads.json: ERCOT's battery cycle and price board, CAISO's daily
// reliability series) and CAISO's queue positions of energy_projects (fixtures/caiso_queue_positions.json, session 1186,
// real rows of the four fields the block reads; the fixture holds no entity_id, so each row is given one here,
// caiso_queue:standin-<n>, for the read's prefix filter only: no id is drawn or keyed)
export const OLDER_TABLES = ["storage_daily_cycle", "price_board_latest", "price_board_peak_offpeak", "caiso_reliability_daily"];
const olderRows = fx("grid_older_reads.json").rows;
for (const t of OLDER_TABLES) {
  for (const [k, rs] of Object.entries(olderRows[t])) {
    const [e, v, unit, freq] = k.split("|");
    add(t, rs.map(([ts, x]) => ({ ...asSeries(e, v, tsOf(ts), x, unit), freq: freq ?? "" })));
  }
}
add("energy_projects", fx("caiso_queue_positions.json").rows.map((r, i) => ({ entity_id: `caiso_queue:standin-${String(i).padStart(4, "0")}`, capacity_mw: r.capacity_mw, status: r.status, extra: { technology_group: r.tech, source_table: r.src } })));
// session 1422 (chain 111): the two tables the Mix tab's older "today so far" and "monthly mix since 2001" read, which no
// committed fixture held (fixtures/grid_mix_now.json, read once with the anon key): eia930_generation_latest for ERCOT,
// ISO-NE and the Lower 48, and state_generation_mix_monthly for the United States
const mixNow = fx("grid_mix_now.json");
for (const [t, unit, freq] of [["eia930_generation_latest", "MW", "PT1H"], ["state_generation_mix_monthly", "MWh", "P1M"]]) {
  for (const [k, rs] of Object.entries(mixNow[t])) { const [e, v] = k.split("|"); add(t, rs.map(([ts, x]) => ({ ...asSeries(e, v, tsOf(ts.length === 10 ? `${ts}T00:00:00+00:00` : ts), x, unit), freq }))); }
}

const cmp = (a, b) => (a === b ? 0 : a === undefined || a === null ? -1 : b === undefined || b === null ? 1 : a < b ? -1 : 1);
const val = (r, col) => (col.startsWith("extra->>") ? r.extra?.[col.slice(8)] ?? null : r[col]);
function test1(r, col, cond) {
  if (cond.startsWith("not.")) return !test1(r, col, cond.slice(4));   // session 1412: the scorecard's model read (variable=not.like.coef_*), as test-grid-failed-reads.mjs (1411)
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

// ------------------------------------------------------------------ the walk, by block, with the words
const ELEMENT = new Set([Symbol.for("react.transitional.element"), Symbol.for("react.element")]);
const MEMO = Symbol.for("react.memo");
const FORWARD = Symbol.for("react.forward_ref");
export const BLOCKS = [["data-grid-panel", (v) => v], ["data-grid-balance", (v) => `balance_${v}`], ["data-grid-replay-day", (v) => `replay_${v}`],
  ["data-gravity-day", () => "gravityday"], ["data-grid-held", (v) => `held_${v}`], ["data-grid-view", (v) => `view_${v}`], ["data-mix", (v) => `mixview_${v}`],
  ["data-alerts-days", () => "alerts_days"]];   // session 1412: the Flex Alert scorecard's small charts
// Session 1422 (chain 111): the older blocks that stood before chain 077 and carry no name of their own on the page are
// named here only, for their render cases, by what the page already draws: a Section or ToolSection by its title
// (older_<title>), a <section> of its own by its id (older_#<id>), and the lines and rows below by their attribute or
// component (OLDER_MARKS). Such a block is an overlay: it takes nothing from the blocks around it (their figures, ids,
// links and files stay theirs, as they were), and its own are those not inside a named panel within it.
export const OLDER_MARKS = [["data-now-sentence", () => "older_the sentence"], ["data-grid-parts", (v) => `older_parts_${v}`], ["data-grid-network", () => "older_the network's server lines"],
  ["data-ask-side", () => "older_the Ask aside"]];
export const OLDER_COMPONENTS = { ToolHeader: () => "older_the header", HeadlineRow: () => "older_the headline numbers", SourceLine: () => "older_the source line", CaisoBreakNote: () => "older_CAISO's break note",
  Decisions: () => "older_the decisions" };
const newBlock = () => ({ nums: [], all: [], text: [], hover: [], heads: [], ids: [], methods: [], files: [], errors: [] });
const HEAD = new Set(["h1", "h2", "h3", "h4"]);
const ENTITY = { "&apos;": "'", "&quot;": '"', "&amp;": "&", "&lt;": "<", "&gt;": ">", "&nbsp;": " " };
const SECTIONS = new WeakSet();   // session 1422: the <section> a Section or ToolSection draws, named by its title, not again by its id
const SECTION_FNS = new Set(["Section", "ToolSection"]);
/** Session 1422: f(block, own) for each older block's overlay open here (`sh`, [name, the block it lies in]); own when
 *  the element is in that block itself, not in a named panel inside it. */
function over(rec, sh, me, f) {
  const done = new Set();
  for (const [n, base] of sh) { if (done.has(n)) continue; done.add(n); f(rec[n] ??= newBlock(), base === me); }
}
async function walk(node, rec, stack, seen, wrap, head, sh = []) {
  const at = stack[stack.length - 1];
  const each = (f) => { for (const n of new Set(stack)) f(rec[n] ??= newBlock(), n === at); };
  if (node === null || node === undefined || typeof node === "boolean") return;
  if (typeof node === "string" || typeof node === "number") { each((b) => b.text.push(String(node))); over(rec, sh, at, (b, own) => { b.text.push(String(node)); if (own) (b.own ??= []).push(String(node)); }); if (head) head.push(String(node)); return; }
  if (typeof node !== "object") return;
  if (typeof node.then === "function") {
    let v;
    try { v = await node; } catch (e) { (rec[at] ??= newBlock()).errors.push(String(e?.message ?? e)); over(rec, sh, at, (b) => b.errors.push(String(e?.message ?? e))); return; }
    return walk(v, rec, stack, seen, wrap, head, sh);
  }
  if (seen.has(node)) return;
  seen.add(node);
  if (ELEMENT.has(node.$$typeof)) {
    let type = node.type;
    const props = node.props ?? {};
    if (type && typeof type === "object" && type.$$typeof === MEMO) type = type.type;
    if (type && typeof type === "object" && type.$$typeof === FORWARD) type = type.render;
    let st = stack, under, h = head, s2 = sh;
    if (typeof type === "string") {
      let named = false;
      for (const [a, f] of BLOCKS) if (props[a] !== undefined) { st = [...st, f(props[a])]; rec[f(props[a])] ??= newBlock(); named = true; }
      const me = st[st.length - 1];
      // session 1422: the older blocks' overlays this element opens (its attribute, or a <section> of its own by its id)
      const opens = OLDER_MARKS.filter(([a]) => props[a] !== undefined).map(([a, f]) => f(props[a]));
      if (type === "section" && props.id !== undefined && !SECTIONS.has(node)) opens.push(`older_#${props.id}`);
      if (opens.length) s2 = [...sh, ...opens.map((n) => [n, me])];
      const ov = (f) => over(rec, s2, me, f);
      const mine = (f) => { for (const n of new Set(st)) f(rec[n] ??= newBlock(), n === me); };
      if (props.id !== undefined) { rec[me].ids.push(String(props.id)); ov((b, own) => own && b.ids.push(String(props.id))); }
      // session 1183's rule: an id on an element that holds one element alone is that element's (the anchor of a panel whose own
      // element a pinned test holds word for word)
      if (named && wrap) rec[me].ids.push(wrap);
      if (props.id !== undefined && props.children && typeof props.children === "object" && !Array.isArray(props.children) && ELEMENT.has(props.children.$$typeof)) under = String(props.id);
      if (HEAD.has(type)) { h = []; rec[me].heads.push(h); ov((b, own) => own && b.heads.push(h)); }
      if (props["data-check"] !== undefined) {
        const k = `${props["data-check"]}=${props["data-raw"]}`;
        mine((b, own) => { b.all.push(k); if (own) b.nums.push(k); });
        ov((b, own) => { b.all.push(k); if (own) b.nums.push(k); });
      }
      if (typeof props.title === "string" && props.title) { mine((b) => b.hover.push(props.title)); ov((b) => b.hover.push(props.title)); }
      if (props["data-grid-file"] !== undefined) { rec[me].files.push(String(props["data-grid-file"])); ov((b, own) => own && b.files.push(String(props["data-grid-file"]))); }
      // session 1422: a written block's rendered markdown (YourGrid.tsx Written) is words a reader reads: its text, tags taken out
      const html = props.dangerouslySetInnerHTML?.__html;
      if (typeof html === "string") { const t = html.replace(/<[^>]*>/g, " "); mine((b) => b.text.push(t)); ov((b, own) => { b.text.push(t); if (own) (b.own ??= []).push(t); }); }
    }
    const top = st[st.length - 1];
    if (typeof props.href === "string" && props.href.startsWith("/data/methods/")) { (rec[top] ??= newBlock()).methods.push(props.href); over(rec, s2, top, (b, own) => own && b.methods.push(props.href)); }
    // a client component is not drawn here: its accessible name (a chart's ariaLabel) is kept with the words on hover
    if (typeof type === "function" && type.__erwClient && typeof props.ariaLabel === "string") { (rec[top] ??= newBlock()).hover.push(props.ariaLabel); over(rec, s2, top, (b) => b.hover.push(props.ariaLabel)); }
    if (typeof type === "function" && !type.__erwClient && !type.prototype?.isReactComponent) {
      // session 1422: an older block a component draws (a Section by its title, OLDER_COMPONENTS by its name)
      const nm = OLDER_COMPONENTS[type.name]?.() ?? (SECTION_FNS.has(type.name) && typeof props.title === "string" ? `older_${props.title}` : null);
      const s3 = nm ? [...s2, [nm, top]] : s2;
      let o;
      try { o = type(props); if (o && typeof o.then === "function") o = await o; } catch (e) { (rec[top] ??= newBlock()).errors.push(`${type.name}: ${e?.message ?? e}`); over(rec, s3, top, (b) => b.errors.push(`${type.name}: ${e?.message ?? e}`)); return; }
      if (SECTION_FNS.has(type.name) && o && typeof o === "object") SECTIONS.add(o);
      return walk(o, rec, st, seen, wrap, h, s3);
    }
    if (typeof type !== "string") under = wrap;   // a fragment or a client component hands the wrapper on
    const drawn = (v) => v && typeof v === "object" && (ELEMENT.has(v.$$typeof) || (Array.isArray(v) && v.some((x) => drawn(x) || (Array.isArray(x) && x.some(drawn)))) || (!Array.isArray(v) && Object.values(v).some((x) => x && ELEMENT.has(x.$$typeof))));
    for (const [k, v] of Object.entries(props)) if (k === "children" || drawn(v)) await walk(v, rec, st, seen, k === "children" ? under : undefined, k === "children" ? h : undefined, s2);
    return;
  }
  if (Array.isArray(node) || typeof node[Symbol.iterator] === "function") { for (const v of node) await walk(v, rec, stack, seen, undefined, head, sh); return; }
  const proto = Object.getPrototypeOf(node);
  if (proto === Object.prototype || proto === null) for (const v of Object.values(node)) await walk(v, rec, stack, seen, undefined, head, sh);
}

/** The words as a reader reads them: the strings in order, entities read, every run of space one space. */
export const words = (parts) => parts.join("").replace(/&[a-z]+;/g, (e) => ENTITY[e] ?? e).replace(/\s+/g, " ").trim();

const page = await import("../app/grid/page.tsx");
/** Draws /grid with the query `sp`: { block name: { nums, all, text, hover, heads, ids, methods, files, errors } }, text,
 *  hover and headings (h1 to h4) as words. */
export async function draw(sp) {
  globalThis.__erwRequestCache = new Map();
  const rec = {};
  try { await walk(page.default({ searchParams: Promise.resolve(sp) }), rec, ["_page"], new WeakSet()); }
  catch (e) { (rec._page ??= newBlock()).errors.push(`the page: ${e?.message ?? e}`); }
  delete globalThis.__erwRequestCache;
  // session 1422: an older block's overlay keeps its own words apart too (`own`: not those of a named panel inside it)
  for (const b of Object.values(rec)) { b.text = words(b.text); b.hover = b.hover.map((x) => words([x])); b.heads = b.heads.map((x) => words(x)).filter(Boolean); if (b.own) b.own = words(b.own); }
  return rec;
}

// Session 1412 (chain 107): the Flex Alert scorecard (app/grid/caiso/alerts/page.tsx), drawn as /grid is, on session 1411's
// committed rows of its two tables (fixtures/grid_older_reads.json: flex_alert_effects' yearly rows and seven alert days with
// their evening hours, flex_alert_model without its coefficients) and CAISO's notices above. The two tables are held only
// while the scorecard is drawn, so every /grid case draws as it did.
const olderFx = fx("grid_older_reads.json");
const SCORECARD = Object.fromEntries(["flex_alert_effects", "flex_alert_model"].map((t) => [t, Object.entries(olderFx.rows[t]).flatMap(([k, rs]) => {
  const [e, v, unit, freq] = k.split("|");
  return rs.map(([ts, x]) => ({ ...asSeries(e, v, tsOf(ts), x, unit), freq: freq ?? "" }));
})]));
/** Draws /grid/caiso/alerts: { block name: ... } as draw() gives. */
export async function drawAlerts() {
  const alertsPage = await import("../app/grid/caiso/alerts/page.tsx");
  for (const [t, rows] of Object.entries(SCORECARD)) T.set(t, rows);
  globalThis.__erwRequestCache = new Map();
  const rec = {};
  try { await walk(alertsPage.default(), rec, ["_page"], new WeakSet()); }
  catch (e) { (rec._page ??= newBlock()).errors.push(`the page: ${e?.message ?? e}`); }
  finally { delete globalThis.__erwRequestCache; for (const t of Object.keys(SCORECARD)) T.delete(t); }
  for (const b of Object.values(rec)) { b.text = words(b.text); b.hover = b.hover.map((x) => words([x])); b.heads = b.heads.map((x) => words(x)).filter(Boolean); }
  return rec;
}
