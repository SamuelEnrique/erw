// Energy Research Warehouse (ERW) site, session 156: records what the query tool's three new forms read from the live
// set, request by request, into tests/fixtures/session156/form_reads.json, so that scripts/test-ask-ready.mjs can run
// the same calls again with no request and set what they return against the recorded rows.
//
//   node --env-file=.env.local --import ./scripts/alias-register.mjs scripts/record-ask-ready.mjs
//
// Reads only, with the anon key, as the site reads. No model call, nothing written to the database. The database's
// address is replaced by a stand-in in the file, and the catalogue is cut to the tables the calls read: real rows,
// nothing invented. Every request is counted and printed with its milliseconds (the first number of each line is what
// the database took for that request on this run).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const out = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "tests", "fixtures", "session156", "form_reads.json");
const CT = "America/Chicago";
// `end` is the day the fixture was recorded on (8 October 2026): "yesterday" is then 7 October
export const CALLS = [
  // 1. the average day by hour
  { id: "h13_family_newest", name: "query", input: { table: "shoulder_hours_monthly", aggregation: "mean", entity: "iso:ercot", variable: "avg_battery_mw_h", group_by: "hour_of_day", day: "newest" } },
  { id: "h13_hours", name: "query", input: { table: "eia930_all_storage", aggregation: "mean", entity: "eia930:ERCO", variable: "net_generation_battery_mw", group_by: "hour_of_day", tz: CT, start: "2026-09-22" } },
  { id: "h24_family_month", name: "query", input: { table: "generation_mix_hourly_profile", aggregation: "mean", entity: "iso:ercot", variable: "avg_wind_mw_h", group_by: "hour_of_day", start: "2026-09-01", end: "2026-10-01" } },
  { id: "family_three_months", name: "query", input: { table: "generation_mix_hourly_profile", aggregation: "mean", entity: "iso:ercot", variable: "avg_wind_mw_hNN", group_by: "hour_of_day", start: "2026-07-01", end: "2026-10-01" } },
  { id: "family_with_days", name: "query", input: { table: "cost_of_power_hourly_profile", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "rt_mean_h00", group_by: "hour_of_day", start: "2026-09-01", end: "2026-10-01" } },
  // 2. a date column grouped by year
  { id: "h14_by_year", name: "query", input: { table: "ercot_interconnection_queue", aggregation: "sum", date_column: "proposed_in_service_date", group_by: "year", where: { status: "active", fuel_technology: "Other - Battery Energy Storage" } } },
  { id: "date_bounded", name: "query", input: { table: "ercot_interconnection_queue", aggregation: "sum", date_column: "proposed_in_service_date", group_by: "month", start: "2028-01-01", end: "2029-01-01", where: { status: "active", fuel_technology: "Wind - Wind Turbine" } } },
  { id: "no_date_column", name: "query", input: { table: "ercot_interconnection_queue", aggregation: "sum", group_by: "year", where: { status: "active", fuel_technology: "Wind - Wind Turbine" } } },
  // 3. the newest day held
  { id: "h03_newest_by_hour", name: "query", input: { table: "eia930_all_demand", aggregation: "mean", entity: "eia930:ERCO", variable: "demand_mw", group_by: "hour", day: "newest", end: "2026-10-08", tz: CT } },
  { id: "s12_newest_min", name: "query", input: { table: "eia930_all_demand", aggregation: "min", entity: "eia930:ERCO", variable: "demand_mw", day: "newest", end: "2026-10-08", tz: CT } },
  { id: "newest_daily_table", name: "query", input: { table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_HUBAVG", variable: "da_mean", day: "newest", end: "2026-10-08" } },
  { id: "newest_quarter_hours", name: "query", input: { table: "iso_rtm_hub_prices", aggregation: "max", entity: "ercot:HB_HUBAVG", variable: "spp_rtm", day: "newest", tz: CT } },
  { id: "newest_two_series", name: "query", input: { table: "grid_stress_yearly", aggregation: "latest", entity: "iso:ercot", day: "newest" } },
  // the entity first: a hub by its entity, a hub by its node (no row has that entity: the node is read), and a scope's own filter kept
  { id: "west_by_day", name: "query", input: { table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_WEST", variable: "da_mean", start: "2026-09-01", end: "2026-10-01", group_by: "day" } },
  { id: "by_node", name: "query", input: { table: "ercot_hub_prices_daily", aggregation: "mean", entity: "HB_NORTH", variable: "da_mean", start: "2026-09-01", end: "2026-09-08" } },
  { id: "another_grid_in_scope", name: "query", input: { table: "generation_mix_hourly_profile", aggregation: "sum", entity: "iso:caiso", variable: "wind_mwh", start: "2026-09-01", end: "2026-10-01" } },
  // source precedence: the derived figure of the year's highest hourly demand (the operator's own is in the page's file)
  { id: "peak_derived", name: "query", input: { table: "grid_stress_yearly", aggregation: "latest", entity: "iso:ercot", variable: "peak_demand_mw", start: "2026-01-01", end: "2027-01-01" } },
];
const TABLES = new Set(CALLS.map((c) => c.input.table));
const origin = new URL(process.env.SUPABASE_URL).origin;
const reads = {}, log = [];
const real = globalThis.fetch;
let requests = 0, bytes = 0, current = "";
globalThis.fetch = async (url, init) => {
  const t = Date.now();
  const res = await real(url, { headers: init?.headers });
  const body = await res.text();
  requests += 1; bytes += body.length;
  const u = new URL(String(url));
  let json = JSON.parse(body);
  if (u.pathname.endsWith("/catalogue")) json = json.filter((r) => TABLES.has(r.table_name));
  const key = String(url).replace(origin, "https://fixture.invalid");
  reads[key] = json;
  log.push({ call: current, what: u.pathname.split("/").pop(), rows: Array.isArray(json) ? json.length : null, ms: Date.now() - t, status: res.status });
  return new Response(JSON.stringify(json), { status: res.status, headers: { "content-type": "application/json" } });
};
const { runTool } = await import("../lib/chat/tools.ts");
const { ercotProfile } = await import("../lib/chat/ercot.ts");
const scope = ercotProfile().scope;
const results = [];
for (const c of CALLS) {
  current = c.id;
  const t = Date.now();
  const r = await runTool(c.name, c.input, scope);
  results.push(r);
  const mine = log.filter((l) => l.call === c.id);
  console.log(`${c.id}: ${r.isError ? "ERROR " + r.out.error.slice(0, 140) : `ok, ${r.out.rows_matched} rows matched, ${Array.isArray(r.out.result) ? r.out.result.length : 0} rows of result`}; ${Date.now() - t} ms in all; requests: ${mine.map((l) => `${l.what} ${l.rows} rows ${l.ms} ms`).join(", ")}`);
}
// the tables' summaries the loop asks for before a question (the variables of the newest period of the energy mix's
// tables): recorded too, so that a test that runs the loop on these reads sends no request that is not here
current = "summaries";
const brief = await ercotProfile().brief();
console.log(`summaries: ${brief.length} characters; requests: ${log.filter((l) => l.call === "summaries").map((l) => `${l.what} ${l.rows} rows ${l.ms} ms`).join(", ")}`);
fs.mkdirSync(path.dirname(out), { recursive: true });
// one line a call, a read and a result, so that the file is no longer than its rows
const lines = (o) => `{\n${Object.entries(o).map(([k, v]) => `  ${JSON.stringify(k)}: ${JSON.stringify(v)}`).join(",\n")}\n }`;
const list = (a) => `[\n${a.map((v) => `  ${JSON.stringify(v)}`).join(",\n")}\n ]`;
const about = "Energy Research Warehouse (ERW), session 156: what the query tool's three new forms (the average day by hour, a date column by year, the newest day held), the entity-first filter and one figure held twice read from the Supabase live set (the anon key), request by request, recorded by site/scripts/record-ask-ready.mjs. Real rows; the catalogue is cut to the tables read; the database's address is a stand-in.";
fs.writeFileSync(out, `{\n "_": ${JSON.stringify(about)},\n "recorded_at": ${JSON.stringify(new Date().toISOString())},\n "calls": ${list(CALLS)},\n "reads": ${lines(reads)},\n "results": ${list(results)},\n "requests": ${list(log)}\n}\n`);
console.log(`${requests} requests, ${bytes} bytes read; ${Object.keys(reads).length} distinct reads recorded in ${path.relative(process.cwd(), out)}; no write, no model call`);
