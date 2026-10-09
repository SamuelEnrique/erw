// Energy Research Warehouse (ERW) site, session 161: Ask ERCOT's average day as a line, and the two slow shapes of
// session 156 as one call each. Tested with no model call and no request: the reads are the ones recorded from the
// site's live set (tests/fixtures/session161/week_reads.json), each with the moment the tool took as "now"; a request
// that was not recorded fails the test.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-161.mjs
//   node --env-file=.env.local --import ./scripts/alias-register.mjs scripts/test-ask-161.mjs --record
//
// --record reads the live set with the anon key, as the site reads (no model call, nothing written), and writes the
// fixture: real rows, nothing invented; the database's address is replaced by a stand-in.
//
// What is held here:
//   1. the 24 hours of a day are the 24 points of one line, each the row fetched, and a time series is drawn as before;
//   2. "this week" is one call: the days of the week that are held, the figure over those, worked again here from the
//      recorded rows; when no day of the week is held, the newest seven days held, and the result says so;
//   3. generation by fuel over a stretch of days is planned by rule as two reads (every fuel at once, and the total
//      rolled up by day), and the near-misses are left to the model as before.
// Exit 1 on a failure.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const file = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "tests", "fixtures", "session161", "week_reads.json");
const record = process.argv.includes("--record");
const CT = "America/Chicago";
const DEMAND = { table: "eia930_all_demand", aggregation: "max", entity: "eia930:ERCO", variable: "demand_mw", day: "this_week", tz: CT };
// each call with the moment it is asked at. "held": a Thursday whose week the table holds whole days of; "not_held": a
// Monday after the newest row, so no day of its week is held; "by_day": the same week as "held", day by day
const CALLS = [
  { id: "held", now: "2026-10-01T18:00:00Z", input: DEMAND },
  { id: "by_day", now: "2026-10-01T18:00:00Z", input: { ...DEMAND, group_by: "day" } },
  { id: "not_held", now: "2026-10-26T15:00:00Z", input: DEMAND },
  { id: "week_rows", now: "2026-10-01T18:00:00Z", input: { table: "eia930_all_demand", aggregation: "max", entity: "eia930:ERCO", variable: "demand_mw", start: "2026-09-28", end: "2026-10-02", tz: CT, group_by: "hour" } },
  { id: "fuels", now: "2026-10-01T18:00:00Z", input: { table: "eia930_all_generation", aggregation: "mean", entity: "eia930:ERCO", start: "2026-09-24", end: "2026-10-01", tz: CT, group_by: "variable" } },
  { id: "total_by_day", now: "2026-10-01T18:00:00Z", input: { table: "eia930_all_generation", aggregation: "mean", entity: "eia930:ERCO", variable: "net_generation_mw", start: "2026-09-24", end: "2026-10-01", tz: CT, group_by: "day" } },
];

const FIX = record ? { reads: {}, results: {} } : JSON.parse(fs.readFileSync(file, "utf8"));
const realNow = Date.now, real = globalThis.fetch;
if (record) {
  const origin = new URL(process.env.SUPABASE_URL).origin;
  const tables = new Set(CALLS.map((c) => c.input.table));
  globalThis.fetch = async (url, init) => {
    const res = await real(url, { headers: init?.headers });
    let json = JSON.parse(await res.text());
    if (new URL(String(url)).pathname.endsWith("/catalogue")) json = json.filter((r) => tables.has(r.table_name));
    FIX.reads[String(url).replace(origin, "https://fixture.invalid")] = json;
    return new Response(JSON.stringify(json), { status: res.status, headers: { "content-type": "application/json" } });
  };
} else {
  process.env.SUPABASE_URL = "https://fixture.invalid";
  process.env.SUPABASE_ANON_KEY = "fixture";
  globalThis.fetch = async (url) => {
    const body = FIX.reads[String(url)];
    if (body === undefined) throw new Error(`a read that was not recorded: ${decodeURIComponent(String(url)).slice(0, 320)}`);
    return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
  };
}

const { runTool } = await import("../lib/chat/tools.ts");
const { ercotProfile } = await import("../lib/chat/ercot.ts");
const { rulePlan } = await import("../lib/chat/plan.ts");
const series = await import("../lib/chat/series.ts");
const forms = await import("../lib/chat/forms.ts");
const profile = ercotProfile();
const at = async (c) => {
  Date.now = () => Date.parse(c.now);
  try { return await runTool("query", c.input, profile.scope); } finally { Date.now = realNow; }
};

if (record) {
  for (const c of CALLS) {
    const r = await at(c);
    FIX.results[c.id] = JSON.parse(JSON.stringify(r));
    console.log(`${c.id}: ${r.isError ? "ERROR " + r.out.error.slice(0, 200) : `${r.out.rows_matched} rows matched`}`);
  }
  const text = JSON.stringify(FIX);
  assert.ok(!text.includes("supabase.co") && !/eyJ[A-Za-z0-9_-]{20,}/.test(text), "the database's address or a key is in the fixture");
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const lines = (o) => `{\n${Object.entries(o).map(([k, v]) => `  ${JSON.stringify(k)}: ${JSON.stringify(v)}`).join(",\n")}\n }`;
  fs.writeFileSync(file, `{\n "recorded": ${JSON.stringify(new Date().toISOString())},\n "note": "Session 161: what the query tool read from the site's live set for scripts/test-ask-161.mjs. Real rows; the database's address is a stand-in.",\n "reads": ${lines(FIX.reads)},\n "results": ${lines(FIX.results)}\n}\n`);
  console.log(`wrote ${file}: ${Object.keys(FIX.reads).length} reads`);
  process.exit(0);
}

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${String(e.stack ?? e.message).split("\n").slice(0, 8).join("\n   ")}`); }
};
const HOURS = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, "0"));
/** A UTC time as its day on Texas's clock: worked here, apart from the tool. */
const central = (t) => {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-CA", { timeZone: CT, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date(t)).map((x) => [x.type, x.value]));
  return `${p.year}-${p.month}-${p.day}`;
};
const call = Object.fromEntries(CALLS.map((c) => [c.id, c]));

// ================================================================== 1. the hours of a day as one line

await test("the 24 hours of a day are 24 points of one line, each the row fetched; a key that is not an hour is left to the table", () => {
  const rows = HOURS.map((h, i) => ({ key: h, value: 100 + i }));
  const d = series.chartPoints(rows, forms.HOUR_OF_DAY);
  assert.equal(series.HOUR_GROUP, forms.HOUR_OF_DAY);
  assert.deepEqual(d.points, rows.map((r, i) => ({ t: i, v: r.value })));
  assert.deepEqual(d.undrawn, []);
  assert.ok(series.isDrawn("line", d) && series.pointsAreRows(rows, d, forms.HOUR_OF_DAY));
  // an hour with no value held is not a point and nothing is drawn in its place
  const gap = series.chartPoints([...rows.slice(0, 5), { key: "05", value: null }, ...rows.slice(6)], forms.HOUR_OF_DAY);
  assert.deepEqual([gap.points.length, gap.undrawn], [23, [{ key: "05", why: "no value" }]]);
  for (const key of ["24", "7", "2021", "noon", "2021-03-05 14:00"]) assert.deepEqual(series.chartPoints([{ key, value: 1 }], forms.HOUR_OF_DAY).undrawn, [{ key, why: "not a time" }], key);
  // a point moved is not the row fetched
  assert.ok(!series.pointsAreRows(rows, { points: d.points.map((p, i) => (i === 3 ? { ...p, v: p.v + 1 } : p)), undrawn: [] }, forms.HOUR_OF_DAY));
});

await test("a series over time is drawn as it was: the hours of a day are not times unless the group says so", () => {
  const rows = [{ key: "2021", value: 1 }, { key: "2022-03", value: 2 }, { key: "2023-05-09 14:00", value: 3 }];
  for (const group of [undefined, "year", "month", "day", "hour"]) {
    const d = series.chartPoints(rows, group);
    assert.deepEqual(d.points.map((p) => p.t), rows.map((r) => series.keySeconds(r.key)), String(group));
    assert.ok(series.pointsAreRows(rows, d, group));
  }
  assert.deepEqual(series.chartPoints(HOURS.map((h) => ({ key: h, value: 1 }))).points, []);          // "00" to "23" with no group: not times, as before
  assert.equal(series.keySeconds("13"), null);
});

// ================================================================== 2. this week, one call

await test("every recorded call returns, from the recorded reads, what it returned from the live set", async () => {
  // session 168: the local words beside each time (lib/chat/plaintime.ts) are newer than the recording and are set apart
  for (const c of CALLS) assert.deepEqual(JSON.parse(JSON.stringify(await at(c), (k, v) => (k.endsWith("_local") ? undefined : v))), FIX.results[c.id], c.id);
});

await test("this week, when its days are held: one result over those days, each day listed with its rows, the figure worked again here", async () => {
  const r = await at(call.held);
  assert.ok(!r.isError, JSON.stringify(r.out).slice(0, 300));
  const w = r.out.week;
  // 1 October 2026 is a Thursday: the week is Monday 28 September to that day
  assert.deepEqual([w.asked, w.tz, w.week, w.held, w.period_read], ["this_week", CT, { from: "2026-09-28", to: "2026-10-01" }, true, { from: "2026-09-28", to: "2026-10-01" }]);
  assert.deepEqual(w.days.map((d) => d.day), ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01"]);
  // the same rows read hour by hour with a start and an end: the days they fall on, and the highest of them
  const hours = (await at(call.week_rows)).out.result;
  const byDay = new Map();
  for (const h of hours) byDay.set(h.hour.slice(0, 10), (byDay.get(h.hour.slice(0, 10)) ?? 0) + 1);
  assert.deepEqual(w.days.map((d) => [d.day, d.rows]), w.days.map((d) => [d.day, byDay.get(d.day) ?? 0]));
  assert.ok(w.days.every((d) => d.of === 24 && d.whole === (d.rows === 24)));
  assert.deepEqual(w.days_held, w.days.filter((d) => d.rows > 0).map((d) => d.day));
  assert.deepEqual(w.days_not_held, w.days.filter((d) => d.rows === 0).map((d) => d.day));
  assert.equal(r.out.rows_matched, hours.length);
  assert.equal(r.out.result[0].value, Math.max(...hours.map((h) => h.value)));
  assert.ok(w.days_held.includes(central(r.out.result[0].at)));        // the hour it fell in is on a day of the week that is held
  // day by day, the same week: a row for each day held, and the highest of them is the week's
  const d = await at(call.by_day);
  assert.deepEqual(d.out.result.map((x) => x.day), w.days_held);
  assert.equal(Math.max(...d.out.result.map((x) => x.value)), r.out.result[0].value);
});

await test("this week, when no day of it is held: the newest seven days held, and the result says so; nothing is filled", async () => {
  const r = await at(call.not_held);
  assert.ok(!r.isError, JSON.stringify(r.out).slice(0, 300));
  const w = r.out.week;
  assert.deepEqual([w.week, w.held], [{ from: "2026-10-26", to: "2026-10-26" }, false]);
  assert.ok(w.period_read.to < "2026-10-26" && w.days.length === 7 && w.days[6].day === w.period_read.to && w.days[0].day === w.period_read.from);
  assert.equal(central(w.newest_row_at), w.period_read.to);            // the seven days end on the day of the newest row held
  assert.equal(w.days.reduce((a, d) => a + d.rows, 0), r.out.rows_matched);
  assert.ok(/no day of this week is held yet/.test(w.note) && typeof r.out.result[0].value === "number");
  assert.ok(w.days.every((d) => d.whole === (d.rows === d.of)));
});

await test("this week takes no start, no end and no table of months; the model is shown it, and told to answer from the one result", async () => {
  for (const more of [{ start: "2026-09-28" }, { end: "2026-10-02" }]) {
    const r = await at({ now: call.held.now, input: { ...DEMAND, ...more } });
    assert.ok(r.isError && r.out.error.includes("this_week"), JSON.stringify(r.out).slice(0, 200));
  }
  const odd = await at({ now: call.held.now, input: { ...DEMAND, day: "last_week" } });
  assert.ok(odd.isError && odd.out.error.includes('"newest" or "this_week"'));
  const q = forms.extendTools([{ name: "query", description: "", input_schema: { properties: { group_by: { description: "" } } } }])[0];
  assert.deepEqual(q.input_schema.properties.day.enum, ["newest", "this_week"]);
  const guide = forms.formsGuide();
  for (const words of ['day "this_week"', "Answer from this one result and call nothing more for it", "say first that this week is not held yet", 'group_by "variable"', "never one call for each fuel", "THREE THINGS THE QUERY DOES IN ONE CALL (session 156)"]) assert.ok(guide.includes(words), words);
  assert.ok(!guide.includes(String.fromCharCode(0x2014)));
});

// ================================================================== 3. generation by fuel over a stretch of days

await test("generation by fuel over the past seven days is planned by rule: every fuel in one read, the total rolled up by day in a second", async () => {
  const today = "2026-10-01";
  const want = { table: "eia930_all_generation", aggregation: "mean", entity: "eia930:ERCO", start: "2026-09-24", end: "2026-10-01", tz: CT };
  for (const q of ["Show ERCOT's generation by fuel over the past seven days.", "Show ERCOT's generation by fuel over the past 7 days.", "What was ERCOT's electricity generation by source over the last seven days?"]) {
    const p = rulePlan(q, today);
    assert.deepEqual(p, { shape: "generation by fuel", calls: [{ name: "query", input: { ...want, group_by: "variable" } }, { name: "query", input: { ...want, variable: "net_generation_mw", group_by: "day" } }] }, q);
  }
  assert.deepEqual([call.fuels.input, call.total_by_day.input], rulePlan("Show ERCOT's generation by fuel over the past seven days.", today).calls.map((c) => c.input));
  // what the two reads return: a row for each fuel with the hours behind it and no warning that variables are mixed; a row for each day
  const fuels = (await at(call.fuels)).out, days = (await at(call.total_by_day)).out;
  assert.ok(fuels.result.length >= 6 && fuels.result.every((r) => /^net_generation_/.test(r.variable) && typeof r.value === "number" && r.n > 0) && fuels.warning === undefined);
  for (const v of ["net_generation_mw", "net_generation_natural_gas_mw", "net_generation_wind_mw", "net_generation_solar_mw"]) assert.ok(fuels.result.some((r) => r.variable === v), v);
  assert.ok(days.result.length >= 3 && days.result.length <= 7 && days.result.every((r) => r.day >= "2026-09-24" && r.day < "2026-10-01"));
  assert.equal(days.result.reduce((a, r) => a + r.n, 0), fuels.result.find((r) => r.variable === "net_generation_mw").n);       // the days' hours are the total's hours
  // both are series the page can show: the days as a line, the fuels as rows
  const records = [call.fuels, call.total_by_day].map((c, i) => ({ tool: "query", input: c.input, out: profile.tag("query", c.input, i ? days : fuels, i + 1), isError: false }));
  const draft = { answer: "x", citations: [{ table: "eia930_all_generation", source_report: "", data_version: "", tier: "" }], not_in_warehouse: false, form: "chart", series: ["r2", "r1"], followups: ["a?", "b?"], premise: "" };
  const done = profile.finish("answered", draft, records);
  assert.deepEqual(done.series.map((s) => [s.group_by, s.kind, s.check.same]), [["day", "line", true], ["variable", "bar", true]]);
});

await test("a near-miss is left to the model, and no question of the three older shapes is read differently", () => {
  const today = "2026-10-01";
  for (const q of ["Show ERCOT's generation by fuel over the past 60 days.", "Show ERCOT's generation by fuel this year.", "Show ERCOT's generation by fuel.", "Show ERCOT's wind generation by fuel over the past seven days.",
    "Show ERCOT's generation by fuel over the past seven days at the North hub.", "Show ERCOT's average generation by fuel over the past seven days.", "Show ERCOT's generation by fuel month by month over the past seven days.",
    "Show ERCOT's generation by fuel over the past two days.", "Show CAISO's generation by fuel over the past seven days.", "Show ERCOT's generation by fuel over the past seven days and the forecast."]) assert.equal(rulePlan(q, today), null, q);
  // a count of days as a word is read only with "by fuel": the hub price question is the model's, as it was
  assert.equal(rulePlan("What was the day-ahead Hub Average price day by day over the last seven days?", today), null);
  assert.equal(rulePlan("What was the day-ahead Hub Average price day by day over the last 7 days?", today).shape, "hub price");
});

console.log(failed ? `${failed} of ${n} tests FAILED` : `${n} tests pass`);
process.exit(failed ? 1 : 0);
