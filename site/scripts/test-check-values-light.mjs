// Energy Research Warehouse (ERW) site, session 1186 (chain 091): check-values.mjs on the Grid pages, lighter, every
// result the same. check-values is run as it is (a child node) against a site and a Supabase that live in this test on
// 127.0.0.1: two Grid addresses carry keys of each kind session 1186 made lighter (net|, nettie|, netbal|, fcerr|,
// degday|, calc| with operands two keys share, fmt|, series| of one table, entity and hour, series_sum| and series_max|
// of one window, gridq|, awe|days), each right key with the value the key's own query or the page's own function gives,
// and wrong keys beside them. The rows are real: the committed snapshot (data/grid_network.json, served as the Storage
// object), scripts/fixtures/grid_balance.json (the week's net generation and demand of the seven grids),
// scripts/fixtures/grid_yesterday.json (ERCOT's demand and day-ahead forecast and two stations' temperatures, one day),
// scripts/fixtures/caiso_queue_positions.json (CAISO's queue in energy_projects) and scripts/fixtures/caiso_alerts.json
// (caiso_grid_emergencies). One row is there twice on purpose (ERCOT's forecast at one hour), so a group's answer that
// does not hold what a key's own query would is seen to send that query.
// Asserts: every right key is ok and every wrong key FAILs (a check is never weakened); and what is asked of Supabase:
// the snapshot once a page (it was once a key), each series a pair of keys reads once (fcerr, degday, netbal), an operand
// two calc| keys share once, a group of series| keys in one request, a window's sums and maxima in one, the queue once,
// the alerts table once. Needs no build, no network and no node_modules.
//
//   node scripts/test-check-values-light.mjs
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as K from "../lib/gridKeys.ts";
import * as N from "../lib/network.ts";
import * as Y from "../lib/gridYesterday.ts";
import * as FMT from "./check-format.mjs";
import * as CALC from "./check-calc.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const SNAP_TEXT = fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8");
const snap = JSON.parse(SNAP_TEXT);
const fixture = (f) => JSON.parse(fs.readFileSync(path.join(here, "fixtures", f), "utf-8"));
const bal = fixture("grid_balance.json"), yd = fixture("grid_yesterday.json"), queue = fixture("caiso_queue_positions.json"), alerts = fixture("caiso_alerts.json");
const norm = (t) => new Date(t).toISOString().replace(".000Z", "Z");

// the rows of the test's Supabase: series rows { table_name, entity, variable, ts_utc, value }
const ROWS = [];
for (const ba of ["SWPP", "CISO"]) {
  for (const [ts, v] of bal.generation[ba]) ROWS.push({ table_name: "eia930_all_generation", entity: `eia930:${ba}`, variable: "net_generation_mw", ts_utc: ts, value: v });
  for (const [ts, v] of bal.demand[ba]) ROWS.push({ table_name: "eia930_all_demand", entity: `eia930:${ba}`, variable: "demand_mw", ts_utc: ts, value: v });
}
for (const r of yd.demand) ROWS.push({ table_name: "eia930_all_demand", entity: "eia930:ERCO", variable: "demand_mw", ...r });
for (const r of yd.forecast) ROWS.push({ table_name: "eia930_all_demand", entity: "eia930:ERCO", variable: "demand_forecast_mw", ...r });
for (const [st, rows] of Object.entries(yd.temps)) for (const r of rows) ROWS.push({ table_name: "weather_obs_hourly", entity: `nws:${st}`, variable: "temperature_f", ...r });
const h1 = norm(yd.demand[3].ts_utc), h2 = norm(yd.demand[5].ts_utc), h3 = norm(yd.demand[7].ts_utc);
ROWS.push({ ...ROWS.find((r) => r.entity === "eia930:ERCO" && r.variable === "demand_forecast_mw" && norm(r.ts_utc) === h2) });   // the row twice
const EVENTS = alerts.rows.map((r) => ({ table_name: alerts.table, ...r }));

/** PostgREST's answer to the filters check-values sends: eq., in.(), like.<prefix>*, and=(<col>.gte|gt|lte|lt.<t>,...),
 *  select, limit, offset; rows sorted by entity (or entity_id, or event_date and event_id), time and variable. */
function answer(params, table = ROWS) {
  const p = new URLSearchParams(params);
  let rows = table;
  const time = (k) => k === "ts_utc" || k === "event_date";
  for (const [k, v] of p) {
    if (["select", "order", "limit", "offset", "and"].includes(k)) continue;
    if (v.startsWith("eq.")) rows = rows.filter((r) => (time(k) ? Date.parse(r[k]) === Date.parse(v.slice(3)) : String(r[k]) === v.slice(3)));
    else if (v.startsWith("in.(")) { const set = new Set(v.slice(4, -1).split(",").map((x) => x.replace(/^"(.*)"$/, "$1"))); rows = rows.filter((r) => set.has(String(r[k]))); }
    else if (v.startsWith("like.") && v.endsWith("*")) rows = rows.filter((r) => String(r[k] ?? "").startsWith(v.slice(5, -1)));
    else throw new Error(`the test's Supabase does not answer ${k}=${v}`);
  }
  const and = p.get("and");
  if (and) for (const c of and.slice(1, -1).split(",")) {
    const [col, op, ...t] = c.split(".");
    const x = Date.parse(t.join("."));
    rows = rows.filter((r) => { const y = Date.parse(r[col]); return op === "gte" ? y >= x : op === "gt" ? y > x : op === "lte" ? y <= x : op === "lt" ? y < x : false; });
  }
  const by = (r) => [r.entity ?? r.entity_id ?? "", r.ts_utc ? Date.parse(r.ts_utc) : r.event_date ? Date.parse(r.event_date) : 0, r.variable ?? r.event_id ?? ""];
  rows = [...rows].sort((a, b) => { const x = by(a), y = by(b); return String(x[0]).localeCompare(String(y[0])) || x[1] - y[1] || String(x[2]).localeCompare(String(y[2])); });
  const off = Number(p.get("offset") ?? 0), lim = p.get("limit") ? Number(p.get("limit")) : Infinity;
  const cols = (p.get("select") ?? "value").split(",").map((c) => c.split(":")[0]);
  return rows.slice(off, off + lim).map((r) => Object.fromEntries(cols.map((c) => [c, r[c]])));
}
const rowsOf = (filter) => answer(filter);

// the hour shown and the week: the snapshot's newest hour with ERCOT's ties, and its whole window
const from = snap.hours[0], to = snap.hours[snap.hours.length - 1];
const hour = [...snap.hours].reverse().find((h) => N.netValue(snap, `net|ties|ERCO|${h}`) > 0);
assert.ok(hour, "the snapshot holds an hour with ERCOT's ties");
const otherOf = (ba) => { const l = snap.links.find((x) => (x.a === ba || x.b === ba) && x.mw.some((m) => m !== null)); return l.a === ba ? l.b : l.a; };
const nettie = (stat, ba) => `nettie|${stat}|${ba}|${otherOf(ba)}|${from}|${to}`;

// the day of the fixture's Yesterday, and its peak hour (the Mix tab's miss at the peak: calc|diff and calc|diffpct)
const day = yd.day, d0 = `${day}T00:00:00Z`, d1 = norm(Date.parse(d0) + 86_400_000);
const peak = yd.demand.reduce((a, r) => (r.value > a.value ? r : a));
const peakHour = norm(peak.ts_utc);
const D = `series~eia930_all_demand~eia930:ERCO~demand_mw~${peakHour}`, F = `series~eia930_all_demand~eia930:ERCO~demand_forecast_mw~${peakHour}`;
/** A series| key's value as its own query gives it: the first row of the table, entity, variable and hour. */
const seriesOf = (k) => { const [, t, e, v, at] = k.split(/[|~]/); return rowsOf({ table_name: `eq.${t}`, entity: `eq.${e}`, variable: `eq.${v}`, ts_utc: `eq.${at}`, select: "value" })[0]?.value; };
const seriesOne = seriesOf;
/** A series_sum| or series_max| key's value as its own query gives it. */
const rangeOf = (k) => {
  const [kind, t, v, s, e, ent] = k.split("|");
  const rows = rowsOf({ table_name: `eq.${t}`, variable: v.includes(",") ? `in.(${v})` : `eq.${v}`, and: `(ts_utc.gte.${s},ts_utc.lt.${e})`, ...(ent ? { entity: `eq.${ent}` } : {}), select: "value" });
  return kind === "series_max" ? Math.max(...rows.map((r) => r.value)) : rows.reduce((a, r) => a + r.value, 0);
};
const miss = Y.forecastMiss(rowsOf({ table_name: "eq.eia930_all_demand", entity: "eq.eia930:ERCO", variable: "eq.demand_mw", and: `(ts_utc.gte.${d0},ts_utc.lt.${d1})`, select: "ts_utc,value" }),
  rowsOf({ table_name: "eq.eia930_all_demand", entity: "eq.eia930:ERCO", variable: "eq.demand_forecast_mw", and: `(ts_utc.gte.${d0},ts_utc.lt.${d1})`, select: "ts_utc,value" }));
const dd = Y.degreeDay(rowsOf({ table_name: "eq.weather_obs_hourly", entity: "eq.nws:KDFW", variable: "eq.temperature_f", and: `(ts_utc.gte.${d0},ts_utc.lt.${d1})`, select: "ts_utc,value" }));
assert.ok(dd && miss.mape !== null);
const otherKind = dd.kind === "cdd" ? "hdd" : "cdd";
const netbal = (what, ba) => {
  const read = (table, variable) => rowsOf({ table_name: `eq.${table}`, entity: `eq.eia930:${ba}`, variable: `eq.${variable}`, and: `(ts_utc.gte.${from},ts_utc.lte.${to})`, select: "ts_utc,value" });
  return K.netbalValue(`netbal|${what}|${ba}|${from}|${to}`, [snap, snap], read("eia930_all_generation", "net_generation_mw"), read("eia930_all_demand", "demand_mw"));
};
/** gridq|<queue>|<status>|<tech>|<n or mw> as the key's own read gives it (every position of the queue). */
const gridqOf = (k) => {
  const [, table, status, tech, what] = k.split("|");
  const m = queue.rows.filter((r) => r.src === table && r.status === status && (r.tech ?? "unknown") === tech);
  return what === "n" ? m.length : Math.round(m.reduce((a, r) => a + (r.capacity_mw === null ? 0 : Number(r.capacity_mw)), 0) * 10) / 10;
};
/** awe|days|<type>|<year> as the key's own query gave it: the type's rows from <year>-01-01 to <year>-12-31T23:59:59Z. */
const aweDaysOf = (k) => {
  const [, , type, year] = k.split("|");
  const rows = answer({ table_name: `eq.${alerts.table}`, event_type: `eq.${type}`, and: `(event_date.gte.${year}-01-01,event_date.lte.${year}-12-31T23:59:59Z)`, select: "event_date" }, EVENTS);
  return new Set(rows.map((r) => String(r.event_date).slice(0, 10))).size;
};
const Q = "caiso_interconnection_queue";

/** As check-values reads a page's text: a whole number with commas, else two decimals. */
const shown = (x) => (Number.isInteger(x) ? x.toLocaleString("en-US") : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
const fig = (check, raw, text = shown(raw)) => ({ check, raw, text });
const own = (check, f) => fig(check, f(check));
const RIGHT = {
  "/grid?grid=ercot&view=exchange": [
    fig(`net|export|ERCO|${hour}`, N.netValue(snap, `net|export|ERCO|${hour}`)),
    fig(`net|ties|ERCO|${hour}`, N.netValue(snap, `net|ties|ERCO|${hour}`)),
    fig(`net|tie|ERCO|${otherOf("ERCO")}|${hour}`, N.netValue(snap, `net|tie|ERCO|${otherOf("ERCO")}|${hour}`)),
    ...["mean", "min", "max", "hours"].map((s) => fig(nettie(s, "ERCO"), K.nettieValue(nettie(s, "ERCO"), [snap, snap]))),
    fig(`netbal|absmean|SWPP|${from}|${to}`, netbal("absmean", "SWPP")),
    fig(`netbal|hours|SWPP|${from}|${to}`, netbal("hours", "SWPP")),
    fig(`fmt|f1|fcerr|mape|eia930:ERCO|${d0}|${d1}`, miss.mape, FMT.formText("f1", miss.mape)),
    fig(`fcerr|hours|eia930:ERCO|${d0}|${d1}`, miss.hours),
    fig(`fmt|f1|degday|${dd.kind}|nws:KDFW|${day}`, dd.value, FMT.formText("f1", dd.value)),
    own(`series|eia930_all_demand|eia930:ERCO|demand_mw|${h1}`, seriesOf),
    own(`series|eia930_all_demand|eia930:ERCO|demand_forecast_mw|${h1}`, seriesOf),
    own(`series|eia930_all_demand|eia930:ERCO|demand_mw|${h2}`, seriesOf),
    own(`series|eia930_all_demand|eia930:ERCO|demand_forecast_mw|${h2}`, seriesOf),   // its row is there twice: its own query
    own(`series|eia930_all_demand|eia930:ERCO|demand_forecast_mw|${h3}`, seriesOf),
    own(`series_sum|eia930_all_demand|demand_mw|${d0}|${d1}|eia930:ERCO`, rangeOf),
    own(`series_max|eia930_all_demand|demand_forecast_mw|${d0}|${d1}|eia930:ERCO`, rangeOf),
    own(`series_sum|eia930_all_demand|demand_mw,demand_forecast_mw|${d0}|${d1}|eia930:ERCO`, rangeOf),
  ],
  "/grid?grid=caiso&view=exchange": [
    ...["mean", "min", "hours"].map((s) => fig(nettie(s, "CISO"), K.nettieValue(nettie(s, "CISO"), [snap, snap]))),
    fig(`netbal|absmean|CISO|${from}|${to}`, netbal("absmean", "CISO")),
    fig(`netbal|hours|CISO|${from}|${to}`, netbal("hours", "CISO")),
    fig(`fmt|pm0|calc|diff|${D}|${F}`, CALC.calcOf("diff", [seriesOne(D), seriesOne(F)]), FMT.formText("pm0", CALC.calcOf("diff", [seriesOne(D), seriesOne(F)]))),
    fig(`fmt|f1|calc|diffpct|${D}|${F}`, CALC.calcOf("diffpct", [seriesOne(D), seriesOne(F)]), FMT.formText("f1", CALC.calcOf("diffpct", [seriesOne(D), seriesOne(F)]))),
    fig(`calc|ratio|${D}|${F}`, CALC.calcOf("ratio", [seriesOne(D), seriesOne(F)])),
    fig(`net|lag|${hour}|${snap.built}`, N.netValue(snap, `net|lag|${hour}|${snap.built}`)),
    own(`gridq|${Q}|active|storage|n`, gridqOf),
    own(`gridq|${Q}|active|storage|mw`, gridqOf),
    own(`gridq|${Q}|completed|solar|n`, gridqOf),
    own("awe|days|transmission_emergency|2024", aweDaysOf),
    own("awe|days|rmo|2022", aweDaysOf),
    own("awe|days|flex_alert|2022", aweDaysOf),
  ],
};
for (const figs of Object.values(RIGHT)) for (const f of figs) assert.ok(f.raw !== undefined && f.raw !== null && Number.isFinite(Number(f.raw)), `the fixture gives ${f.check} a value`);
assert.equal(rowsOf({ table_name: "eq.eia930_all_demand", entity: "eq.eia930:ERCO", variable: "eq.demand_forecast_mw", ts_utc: `eq.${h2}`, select: "value" }).length, 2);
// wrong keys beside them: a value moved, a key with no value, a tie's week one MW off, a count one off
const WRONG = {
  "/grid?grid=ercot&view=exchange": [
    fig("net|ties|ERCO|2001-01-01T00:00:00Z", 1),   // an hour neither snapshot holds: no value
    fig(`fmt|f1|degday|${otherKind}|nws:KDFW|${day}`, dd.value, FMT.formText("f1", dd.value)),
    fig(`series|eia930_all_demand|eia930:ERCO|demand_mw|${h3}`, seriesOf(`series|eia930_all_demand|eia930:ERCO|demand_mw|${h3}`) + 1),   // in h3's group
    fig(`series|eia930_all_demand|eia930:ERCO|net_generation_mw|${h1}`, 1000),   // in h1's group, a variable with no row
    fig(`series_sum|eia930_all_demand|demand_forecast_mw|${d0}|${d1}|eia930:ERCO`, rangeOf(`series_sum|eia930_all_demand|demand_forecast_mw|${d0}|${d1}|eia930:ERCO`) + 10),
  ],
  "/grid?grid=caiso&view=exchange": [
    fig(nettie("max", "CISO"), K.nettieValue(nettie("max", "CISO"), [snap, snap]) + 1),
    fig(`calc|diff|${D}|${F}`, CALC.calcOf("diff", [seriesOne(D), seriesOne(F)]) + 5),
    fig(`netbal|hours|CISO|${from}|${snap.hours[snap.hours.length - 25]}`, netbal("hours", "CISO")),   // the week's count on a window a day shorter
    fig(`fcerr|mape|eia930:ERCO|${d0}|${d1}`, miss.mape + 0.25),
    fig(`gridq|${Q}|completed|wind|n`, gridqOf(`gridq|${Q}|completed|wind|n`) + 1),
    fig("awe|days|eea_watch|2022", aweDaysOf("awe|days|eea_watch|2022") + 1),
  ],
};

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
function page(address) {
  const spans = [...RIGHT[address], ...WRONG[address]];
  return `<!doctype html><html><body>${spans.map((f) => `<p><span data-check="${esc(f.check)}" data-raw="${esc(f.raw)}">${esc(f.text)}</span></p>`).join("")}</body></html>`;
}

// the test's Supabase and site; every request counted
const asked = [];
const supa = http.createServer((req, res) => {
  const u = new URL(req.url, "http://x.invalid");
  if (u.pathname === `/${N.NETWORK_OBJECT}`) { asked.push({ what: "snapshot", at: phase }); res.writeHead(200, { "content-type": "application/json" }).end(SNAP_TEXT); return; }
  const table = { "/rest/v1/series": ROWS, "/rest/v1/entities": queue.rows.map((r, i) => ({ entity_id: `caiso_queue:${String(i).padStart(4, "0")}`, table_name: "energy_projects", ...r })), "/rest/v1/events": EVENTS }[u.pathname];
  if (table) {
    try {
      const rows = answer(u.search.slice(1), table);
      // a wrong EIA-930 hour's row is read for its loaded_at (scripts/check-revised.mjs): that read is counted apart
      asked.push({ what: (u.searchParams.get("select") ?? "").startsWith("loaded_at") ? "revised" : u.pathname.split("/").pop(), at: phase,
        q: Object.fromEntries([...u.searchParams].filter(([k]) => !["limit", "offset", "order", "select"].includes(k))) });
      res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify(rows));
    } catch (e) { res.writeHead(400).end(String(e.message)); }
    return;
  }
  asked.push({ what: `other ${u.pathname}`, at: phase });
  res.writeHead(404).end("[]");
});
let phase = "";
const site = http.createServer((req, res) => {
  const u = new URL(req.url, "http://x.invalid");
  if (req.method === "POST" && u.pathname === "/internal/unlock") { res.writeHead(303, { "set-cookie": "erw_view=internal; Path=/", location: "/" }).end(); return; }
  const a = u.pathname + u.search;
  if (!RIGHT[a]) { res.writeHead(404).end("no"); return; }
  phase = a;
  res.writeHead(200, { "content-type": "text/html" }).end(page(a));
});
await new Promise((r) => supa.listen(0, "127.0.0.1", r));
await new Promise((r) => site.listen(0, "127.0.0.1", r));
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "erw-cv-light-"));
const SCRIPT = path.join(here, process.env.CHECK_VALUES_LIGHT_SCRIPT ?? "check-values.mjs");   // another copy of the script, to read it the same way
const run = await new Promise((resolve) => {
  const env = { ...process.env, SUPABASE_URL: `http://127.0.0.1:${supa.address().port}/rest/v1/`, SUPABASE_ANON_KEY: "test-key", INTERNAL_COSTS_TOKEN: "test-token",
    CHECK_VALUES_PAGES: Object.keys(RIGHT).join(","), CHECK_VALUES_STATE: path.join(tmp, "state.json") };
  for (const k of ["SUPABASE_SERVICE_KEY", "CHECK_VALUES_RESUME", "CHECK_VALUES_WRITE_FLOOR"]) delete env[k];
  const p = spawn(process.execPath, [SCRIPT, `http://127.0.0.1:${site.address().port}`], { cwd: path.join(here, ".."), env, stdio: ["ignore", "pipe", "pipe"] });
  let o = "";
  p.stdout.on("data", (d) => (o += d));
  p.stderr.on("data", (d) => (o += d));
  p.on("close", (code) => resolve({ code, o }));
});
supa.close();
site.close();
fs.rmSync(tmp, { recursive: true, force: true });
const lines = run.o.split(/\r?\n/).filter((l) => /^(ok  |FAIL) \| /.test(l)).map((l) => { const [s, pg, c] = l.split(" | "); return { s: s.trim(), page: pg, check: c, line: l }; });
const statusOf = (check) => lines.filter((l) => l.check === check).map((l) => l.s);

let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };

test("the run read both pages and failed (the wrong keys), with nothing else failing", () => {
  assert.equal(run.code, 1, run.o.slice(-2000));
  for (const l of lines.filter((x) => x.s === "FAIL")) assert.ok(Object.values(WRONG).flat().some((w) => w.check === l.check), `only a wrong key fails: ${l.line}`);
});
test("every right key of each kind is ok, on its page, with the value its own query gives", () => {
  for (const figs of Object.values(RIGHT)) for (const f of figs) {
    assert.deepEqual(statusOf(f.check), ["ok"], `${f.check}: ${lines.filter((l) => l.check === f.check).map((l) => l.line).join(" / ") || "no line"}`);
  }
});
test("every wrong key FAILs: a value moved (calc, netbal, fcerr, series, a sum, a tie's week, a queue count, alert days), a key with no value (net, degday's other side, a variable with no row)", () => {
  for (const w of Object.values(WRONG).flat()) assert.deepEqual(statusOf(w.check), ["FAIL"], w.check);
});
test("the network snapshot is fetched once a page, not once a key", () => {
  const snaps = asked.filter((a) => a.what === "snapshot");
  const keysOnPages = Object.values(RIGHT).flat().filter((f) => /^(net|nettie|netbal)\|/.test(f.check)).length;
  assert.ok(keysOnPages >= 10, `${keysOnPages} snapshot keys`);
  assert.deepEqual(snaps.map((a) => a.at), Object.keys(RIGHT));
});
test("each series two keys read is asked once a run (fcerr's pair, netbal's pair, degday's two sides, a shared calc operand)", () => {
  const series = asked.filter((a) => a.what === "series");
  const seen = new Map();
  for (const a of series) { const k = JSON.stringify(a.q); seen.set(k, (seen.get(k) ?? 0) + 1); }
  for (const [k, c] of seen) assert.equal(c, 1, `asked ${c} times: ${k}`);
  const of = (pred) => series.filter((a) => pred(a.q)).length;
  assert.equal(of((q) => q.entity === "eq.eia930:ERCO" && /^eq\./.test(q.variable) && q.and === `(ts_utc.gte.${d0},ts_utc.lt.${d1})`), 2, "fcerr: demand and forecast, once each");
  assert.equal(of((q) => q.table_name === "eq.weather_obs_hourly"), 1, "degday: the station's day once, for both sides");
  assert.equal(of((q) => q.entity === "eq.eia930:CISO" && q.and === `(ts_utc.gte.${from},ts_utc.lte.${to})`), 2, "netbal: CISO's generation and demand of the week, once each");
  assert.equal(of((q) => q.ts_utc === `eq.${peakHour}`), 1, "calc: the peak's demand and forecast, one request for three keys");
});
test("a page's series| keys of one table, entity and hour are one request; a variable whose rows are two sends its own query", () => {
  const series = asked.filter((a) => a.what === "series");
  const at = (h) => series.filter((a) => a.q.ts_utc === `eq.${h}`).map((a) => a.q.variable);
  assert.deepEqual(at(h1), ['in.("demand_forecast_mw","demand_mw","net_generation_mw")'], "h1: the group, the variable with no row in it too");
  assert.deepEqual(at(h2), ['in.("demand_forecast_mw","demand_mw")', "eq.demand_forecast_mw"], "h2: the group, then the twice-held row's own query");
  assert.deepEqual(at(h3), ['in.("demand_forecast_mw","demand_mw")']);
  assert.deepEqual(asked.filter((a) => a.what === "revised").map((a) => [a.q.variable, a.q.ts_utc]), [["eq.demand_mw", `eq.${h3}`]],
    "the wrong hour's row is read for its loaded_at, as before: a revision is told apart from a wrong figure");
});
test("a page's series_sum| and series_max| keys of one window and entity are one request", () => {
  const series = asked.filter((a) => a.what === "series" && a.q.and === `(ts_utc.gte.${d0},ts_utc.lt.${d1})` && a.q.entity === "eq.eia930:ERCO" && !/^eq\./.test(a.q.variable));
  assert.deepEqual(series.map((a) => a.q.variable), ['in.("demand_forecast_mw","demand_mw")']);
});
test("the queue is read once a run for its gridq| keys, the alerts table once for the awe|days keys", () => {
  assert.equal(asked.filter((a) => a.what === "entities").length, 1);
  const ev = asked.filter((a) => a.what === "events");
  assert.equal(ev.length, 1);
  assert.equal(ev[0].q.event_type, undefined, "the whole table, as awe|last and awe|ndays read it");
});
console.log(`${n} tests passed`);
