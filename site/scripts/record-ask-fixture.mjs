// Energy Research Warehouse (ERW) site, session 143: records what three tool calls of Ask ERCOT read from the live set,
// request by request, into tests/fixtures/session143/tool_reads.json, so that scripts/test-ask-speed.mjs can run the
// same calls again with no request (one after another, and together) and compare what they return.
//
//   node --env-file=.env.local --import ./scripts/alias-register.mjs scripts/record-ask-fixture.mjs
//
// Reads only, with the anon key, as the site reads. No model call. The database's address is replaced by a stand-in in
// the file, and the catalogue is cut to the tables the calls read: real rows, nothing invented.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const out = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "tests", "fixtures", "session143", "tool_reads.json");
export const CALLS = [
  { name: "query", input: { table: "ercot_hub_prices_daily", aggregation: "mean", entity: "ercot:HB_WEST", variable: "da_mean", start: "2026-09-01", end: "2026-10-01", group_by: "day" } },
  { name: "query", input: { table: "ercot_peak_premium_annual", aggregation: "latest", entity: "ercot:HB_HUBAVG", variable: "peak_minus_midday_median", group_by: "year" } },
  { name: "query", input: { table: "carbon_intensity_monthly", aggregation: "mean", entity: "eia930:ERCO", variable: "intensity_generation", start: "2026-09-01", end: "2026-10-01" } },
];
const TABLES = new Set(CALLS.map((c) => c.input.table));
const origin = new URL(process.env.SUPABASE_URL).origin;
const reads = {};
const real = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  const res = await real(url, { headers: init?.headers });
  const body = await res.text();
  const u = new URL(String(url));
  let json = JSON.parse(body);
  if (u.pathname.endsWith("/catalogue")) json = json.filter((r) => TABLES.has(r.table_name));
  reads[String(url).replace(origin, "https://fixture.invalid")] = json;
  return new Response(JSON.stringify(json), { status: res.status, headers: { "content-type": "application/json" } });
};
const { runTool } = await import("../lib/chat/tools.ts");
const { ercotProfile } = await import("../lib/chat/ercot.ts");
const scope = ercotProfile().scope;
const results = [];
for (const c of CALLS) results.push(await runTool(c.name, c.input, scope));
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify({ _: "Energy Research Warehouse (ERW), session 143: what three tool calls of Ask ERCOT read from the Supabase live set (the anon key), request by request, recorded by site/scripts/record-ask-fixture.mjs. Real rows; the catalogue is cut to the three tables read; the database's address is a stand-in.", recorded_at: new Date().toISOString(), calls: CALLS, reads, results }, null, 1) + "\n");
console.log(`${Object.keys(reads).length} reads recorded; results: ${results.map((r) => `${r.isError ? "ERROR" : "ok"} ${JSON.stringify(r.out).length} chars`).join(", ")}`);
