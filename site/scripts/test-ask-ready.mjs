// Energy Research Warehouse (ERW) site, session 156: Ask ERCOT to ready. What the session added, tested with no model
// call and no request: the reads are the ones recorded from the site's live set on 8 October 2026
// (tests/fixtures/session156/form_reads.json, written by scripts/record-ask-ready.mjs); a request that was not recorded
// fails the test. Where the loop is run, a stand-in answers for the model's API, as in scripts/test-ask-speed.mjs.
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-ready.mjs
//
// What is held here:
//   1. the three things the query does in one call, each set against the recorded rows worked again in this file:
//      the average day by hour (24 values as one series, with the days behind each hour, a short hour carrying its own
//      count), a date column grouped by year (megawatts and count), and the newest day held;
//   2. a series is asked for by its entity alone, and what it returns is what "entity or node" returned;
//   3. the two switches are on by default, the server can turn each off, and the default lives in one place;
//   4. the owner's ruling on two sources: the operator's own figure leads, the derived one is named, both in one answer;
//   5. the sentence that says which source holds Texas's curtailment share;
//   6. the closing words of a refusal about another grid name the tool as it now is, and the judge asks for them.
// Exit 1 on a failure.
import assert from "node:assert/strict";
import fs from "node:fs";
import { judge } from "./eval-judge.mjs";

const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf8");
const FIX = JSON.parse(read("../../tests/fixtures/session156/form_reads.json"));
const FIX143 = JSON.parse(read("../../tests/fixtures/session143/tool_reads.json"));
const SET = JSON.parse(read("../../warehouse/chat/eval_ercot_panel.json"));
const PAGES = JSON.parse(read("../../warehouse/chat/eval_ercot_pages.json"));
const DASH = String.fromCharCode(0x2014);

// the recorded reads stand in for the database: a request that was not recorded fails the test
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
const log = [];
const fixtureFetch = async (url) => {
  const key = String(url);
  const body = FIX.reads[key];
  if (body === undefined) throw new Error(`a read that was not recorded: ${decodeURIComponent(key).slice(0, 320)}`);
  log.push(key);
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};
globalThis.fetch = fixtureFetch;

const { runTool } = await import("../lib/chat/tools.ts");
const ask = await import("../lib/chat/ask.ts");
const { ercotProfile, profile153 } = await import("../lib/chat/ercot.ts");
const forms = await import("../lib/chat/forms.ts");
const ready = await import("../lib/chat/ready.ts");
const sw = await import("../lib/chat/switches.ts");
const pf = await import("../lib/chat/pagefiles.ts");
const panel = await import("../lib/chat/panel.ts");
const profile = ercotProfile();

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${String(e.stack ?? e.message).split("\n").slice(0, 8).join("\n   ")}`); }
};
const CALL = Object.fromEntries(FIX.calls.map((c, i) => [c.id, { ...c, recorded: FIX.results[i] }]));
/** One recorded call again: what the tool returns, and the requests it sent to the tables (not the catalogue or the registry). */
const run = async (id, input = CALL[id].input) => {
  const from = log.length;
  const r = await runTool("query", input, profile.scope);
  const sent = log.slice(from).map((k) => ({ key: k, u: new URL(k) })).filter((x) => /\/(series|entities|events)$/.test(x.u.pathname)).map((x) => ({ ...Object.fromEntries(x.u.searchParams), _table: x.u.pathname.split("/").pop(), _rows: FIX.reads[x.key] }));
  return { ...r, sent };
};
const round6 = (x) => Math.round(x * 1e6) / 1e6;
const HOURS = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, "0"));
/** A UTC time as its day and hour on Texas's clock: worked here, apart from the tool. */
const central = (t) => {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-CA", { timeZone: "America/Chicago", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", hourCycle: "h23" }).formatToParts(new Date(t)).map((x) => [x.type, x.value]));
  return { day: `${p.year}-${p.month}-${p.day}`, hour: p.hour };
};

// ================================================================== the recorded calls

await test("every recorded call returns, from the recorded reads, what it returned from the live set", async () => {
  assert.equal(FIX.calls.length, 17);
  assert.ok(!JSON.stringify(FIX).includes("supabase.co") && !/eyJ[A-Za-z0-9_-]{20,}/.test(JSON.stringify(FIX)));   // no address of the database, no key
  for (const c of FIX.calls) {
    const r = await runTool(c.name, c.input, profile.scope);
    // session 168: the local words beside each time (lib/chat/plaintime.ts) are newer than the recording and are set apart
    assert.deepEqual(JSON.parse(JSON.stringify(r, (k, v) => (k.endsWith("_local") ? undefined : v))), CALL[c.id].recorded, c.id);
  }
});

// ================================================================== 1. the average day by hour

await test("the average day by hour, from hourly rows: 24 values as one series, each the mean of that local hour, with the days behind it", async () => {
  const r = await run("h13_hours");
  assert.equal(r.isError, false);
  assert.equal(r.sent.length, 1);                                       // one request: the rows of the period, read once
  const rows = r.sent[0]._rows;
  assert.equal(rows.length, 355);
  // worked again here from the recorded rows: the mean of each hour of Texas's day, its rows and its days
  const by = new Map();
  for (const x of rows) { const c = central(x.t); if (!by.has(c.hour)) by.set(c.hour, { v: [], days: new Set() }); by.get(c.hour).v.push(Number(x.v)); by.get(c.hour).days.add(c.day); }
  const want = [...by.keys()].sort().map((h) => ({ hour_of_day: h, value: round6(by.get(h).v.reduce((a, b) => a + b, 0) / by.get(h).v.length), n: by.get(h).v.length, days: by.get(h).days.size }));
  assert.deepEqual(r.out.result, want);
  assert.deepEqual(r.out.result.map((x) => x.hour_of_day), HOURS);      // 24 rows, "00" to "23", in order
  assert.equal(r.out.n_groups, 24);
  assert.equal(r.out.result.reduce((a, x) => a + x.n, 0), rows.length); // every row is in one hour and no row is made
  // a short hour carries its count: the newest day is held to 18:00 Central, so the five hours after it have one day fewer
  const a = r.out.average_day;
  assert.equal(a.days_in_period, 15);
  assert.deepEqual(a.short_hours, ["19", "20", "21", "22", "23"].map((h) => ({ hour_of_day: h, days: 14 })));
  assert.deepEqual(a.hours_not_held, []);
  assert.ok(r.out.result.filter((x) => x.hour_of_day < "19").every((x) => x.days === 15 && x.n === 15));
  assert.ok(a.note.includes("nothing is filled"));
  // the batteries charge at midday and discharge in the evening: the rows say so, and the summary is the rows' own
  assert.equal(r.out.summary.lowest.hour_of_day, "10");
  assert.equal(r.out.summary.highest.hour_of_day, "19");
  assert.equal(r.out.filters.tz, "America/Chicago");
});

await test("the average day by hour, where the table's variables are the hours: one request for the 24, each value the table's own row", async () => {
  const r = await run("h24_family_month");
  assert.equal(r.isError, false);
  assert.equal(r.sent.length, 1);                                       // sessions 148 and 153 read these a few at a time, a model call each
  const names = HOURS.map((h) => `avg_wind_mw_h${h}`);
  assert.equal(r.sent[0].variable, `in.(${[...names, "days_held"].map((v) => `"${v}"`).join(",")})`);
  const rows = r.sent[0]._rows, held = rows.find((x) => x.variable === "days_held").v;
  assert.equal(rows.length, 25);
  assert.equal(held, 30);                                               // September 2026: every day of the month is behind each hour
  assert.deepEqual(r.out.result, names.map((v, i) => ({ hour_of_day: HOURS[i], value: rows.find((x) => x.variable === v).v, n: 1, days: held })));
  assert.equal(r.out.rows_matched, 24);                                 // the count of days is read beside the 24 and is not one of them
  assert.deepEqual(r.out.units, ["MW"]);
  assert.equal(r.out.warning, undefined);                               // 24 variables are one family here, not a mixture
  assert.deepEqual([r.out.average_day.hours, r.out.average_day.periods, r.out.average_day.first_period], [24, 1, "2026-09-01"]);
  // wind is lowest at midday and highest late at night: session 148's answer gave these two from four separate reads
  assert.deepEqual([r.out.summary.lowest, r.out.summary.highest], [{ hour_of_day: "12", value: 7280 }, { hour_of_day: "23", value: 17361.4 }]);
  // any one of the 24 names, or the way a guide writes the family, stands for it
  for (const v of ["avg_wind_mw_h", "avg_wind_mw_h07", "avg_wind_mw_hNN", "avg_wind_mw_hHH"]) assert.deepEqual(forms.hourFamily(v).names, names);
  assert.equal(forms.hourFamily("wind_mwh"), null);
  assert.equal(forms.hourFamily("battery_operating_mw_lt2h"), null);
});

await test("a family of hours with its own family of days, and over several months: the days are the table's, added up, and the mean says what it is", async () => {
  const d = await run("family_with_days");
  const rows = d.sent[0]._rows;
  assert.equal(d.sent.length, 1);
  assert.equal(rows.length, 48);                                        // rt_mean_h00 to _h23 and rt_days_h00 to _h23
  assert.deepEqual(d.out.result, HOURS.map((h) => ({ hour_of_day: h, value: rows.find((x) => x.variable === `rt_mean_h${h}`).v, n: 1, days: rows.find((x) => x.variable === `rt_days_h${h}`).v })));
  assert.deepEqual(forms.hourFamily("rt_mean_h").days, HOURS.map((h) => `rt_days_h${h}`));
  assert.deepEqual(d.out.units, ["USD/MWh"]);
  const m = await run("family_three_months");
  const all = m.sent[0]._rows;
  assert.equal(all.length, 75);                                         // three months of 24 hours, and three counts of days
  const heldDays = all.filter((x) => x.variable === "days_held").map((x) => x.v);
  assert.deepEqual(heldDays, [31, 31, 30]);
  for (const x of m.out.result) {
    const vs = all.filter((y) => y.variable === `avg_wind_mw_h${x.hour_of_day}`).map((y) => y.v);
    assert.deepEqual([x.value, x.n, x.days], [round6(vs.reduce((a, b) => a + b, 0) / 3), 3, 92], x.hour_of_day);
  }
  assert.ok(m.out.average_day.note.includes("the mean over the 3 periods read") && m.out.average_day.note.includes("not weighted by their days"));
});

await test("what the average day cannot be asked of is refused before any row is read, with what to give", async () => {
  const noStem = await run("x", { table: "generation_mix_hourly_profile", aggregation: "mean", entity: "iso:ercot", variable: "wind_mwh", group_by: "hour_of_day" });
  assert.ok(noStem.isError && noStem.out.error.includes("no hour of their own") && noStem.out.error.includes('"avg_wind_mw_h"'));
  assert.equal(noStem.sent.length, 0);
  const things = await run("x", { table: "ercot_interconnection_queue", aggregation: "count", group_by: "hour_of_day" });
  assert.ok(things.isError && things.out.error.includes("series tables only"));
  assert.equal(things.sent.length, 0);
  const odd = await run("x", { table: "eia930_all_demand", aggregation: "mean", group_by: "hour_of_week" });
  assert.ok(odd.isError && odd.out.error.includes("hour_of_day"));
});

await test("24 values are one series the page can show, and the judge's rule for a chart passes it", async () => {
  for (const id of ["h13_family_newest", "h13_hours", "h24_family_month"]) {
    const r = await run(id);
    const records = [{ tool: "query", input: CALL[id].input, out: profile.tag("query", CALL[id].input, r.out, 1), isError: false }];
    const draft = { answer: "x", citations: [{ table: r.out.table, source_report: "", data_version: "", tier: "" }], not_in_warehouse: false, form: "chart", series: ["r1"], followups: ["a?", "b?"], premise: "" };
    assert.deepEqual(profile.extraProblems(draft, records, []), [], id);
    const done = profile.finish("answered", draft, records);
    assert.equal(done.series.length, 1, id);
    assert.equal(done.series[0].group_by, "hour_of_day");
    assert.deepEqual(done.series[0].rows.map((x) => [x.key, x.value]), r.out.result.map((x) => [x.hour_of_day, x.value]));
    // session 161: the hours of a day are the 24 points of one line (the shared chart has an hour-of-day axis now), each
    // point the row fetched; until then the page showed them as a table of 24 rows (points 0, not_drawn 24)
    assert.deepEqual(done.series[0].check, { rows_fetched: 24, rows: 24, same: true, points: 24, not_drawn: 0 });
    assert.equal(done.series[0].kind, "line");
    assert.deepEqual(judge({ kind: "chart" }, { status: "answered", answer: "The batteries charge at midday and discharge in the evening.", citations: draft.citations, series: done.series }), []);
  }
});

// ================================================================== 2. a date column grouped by year

await test("a date column grouped by year: megawatts and count for each year, each the recorded rows' own sum", async () => {
  const r = await run("h14_by_year");
  assert.equal(r.isError, false);
  assert.equal(r.sent.length, 1);
  assert.deepEqual([r.sent[0]._table, r.sent[0].select, r.sent[0].order], ["entities", "t:extra->>proposed_in_service_date,v:capacity_mw,id:entity_id", "entity_id.asc"]);
  assert.deepEqual([r.sent[0].status, r.sent[0]["extra->>fuel_technology"]], ['in.("active")', 'in.("Other - Battery Energy Storage")']);
  const rows = r.sent[0]._rows;
  assert.equal(rows.length, 628);
  assert.equal(new Set(rows.map((x) => x.id)).size, 628);               // each request of the queue once
  const by = new Map();
  for (const x of rows) { const y = x.t.slice(0, 4); if (!by.has(y)) by.set(y, []); by.get(y).push(Number(x.v)); }
  const want = [...by.keys()].sort().map((y) => ({ year: y, value: round6(by.get(y).reduce((a, b) => a + b, 0)), n: by.get(y).length }));
  assert.deepEqual(r.out.result, want);
  assert.deepEqual(r.out.result.map((x) => x.year), ["2025", "2026", "2027", "2028", "2029", "2030", "2031", "2032"]);
  assert.deepEqual(r.out.result.find((x) => x.year === "2028"), { year: "2028", value: 45624.26, n: 251 });   // the year with the most megawatts planned
  assert.equal(r.out.result.reduce((a, x) => a + x.n, 0), 628);
  assert.equal(r.out.summary.sum_of_rows, 118905.95);                   // the total session 148's answer gave, when it could not split it by year
  assert.deepEqual(r.out.date_column.rows_without_a_date, 0);
  assert.equal(r.out.filters.date_column, "proposed_in_service_date");
  // the series is a line over the years: every row a point of the chart
  const records = [{ tool: "query", input: CALL.h14_by_year.input, out: profile.tag("query", CALL.h14_by_year.input, r.out, 1), isError: false }];
  const done = profile.finish("answered", { answer: "x", citations: [{ table: "ercot_interconnection_queue", source_report: "", data_version: "", tier: "source" }], not_in_warehouse: false, form: "chart", series: ["r1"], followups: [], premise: "" }, records);
  assert.deepEqual(done.series[0].check, { rows_fetched: 8, rows: 8, same: true, points: 8, not_drawn: 0 });
  assert.deepEqual(done.series[0].rows[3], { key: "2028", value: 45624.26, n: 251 });
});

await test("a date column bounds as well as groups; without it the tool says which columns hold a date; a series table has none", async () => {
  const b = await run("date_bounded");
  const rows = b.sent[0]._rows.filter((x) => x.t >= "2028-01-01" && x.t < "2029-01-01");
  assert.equal(b.sent[0]._rows.length, 77);
  assert.equal(b.out.rows_matched, rows.length);
  assert.equal(rows.length, 26);
  assert.ok(b.out.result.every((x) => x.month.startsWith("2028-")));
  assert.equal(b.out.result.reduce((a, x) => a + x.n, 0), 26);
  assert.equal(b.out.summary.sum_of_rows, round6(rows.reduce((a, x) => a + Number(x.v), 0)));
  const none = await run("no_date_column");
  assert.deepEqual([none.out.rows_matched, none.out.n_groups, none.out.result], [77, 0, []]);
  assert.ok(none.out.note.includes("give date_column") && none.out.note.includes("queue_date, proposed_in_service_date"));
  const series = await run("x", { table: "eia930_all_demand", aggregation: "mean", date_column: "retrieved_at", group_by: "year" });
  assert.ok(series.isError && series.out.error.includes("entities and events tables only"));
  const unknown = await run("x", { table: "ercot_interconnection_queue", aggregation: "sum", date_column: "online_date", group_by: "year" });
  assert.ok(unknown.isError && unknown.out.error.includes("proposed_in_service_date"));
  const hour = await run("x", { table: "ercot_interconnection_queue", aggregation: "sum", date_column: "queue_date", group_by: "hour" });
  assert.ok(hour.isError && hour.out.error.includes("not an hour"));
  for (const r of [series, unknown, hour]) assert.equal(r.sent.length, 0);
  assert.equal(forms.dateLabel("2028-06-01", "year"), "2028");
  assert.equal(forms.dateLabel("2028-06-01", "month"), "2028-06");
  assert.equal(forms.dateLabel("2028-06-01T00:00:00Z", "day"), "2028-06-01");
  for (const v of ["", null, undefined, "2021.0", "06/01/2028", "20280601"]) assert.equal(forms.dateLabel(v, "year"), null);   // not a date as a column writes one: in no year
  assert.deepEqual(forms.dateColumns(["entity_id", "status_date", "queue_date", "update", "proposed_in_service_date"]), ["status_date", "queue_date", "proposed_in_service_date"]);
});

// ================================================================== 3. the newest day held

await test("the newest day held: one small read finds the newest whole day, and the query answers over it", async () => {
  const r = await run("h03_newest_by_hour");
  assert.equal(r.isError, false);
  assert.equal(r.sent.length, 2);                                       // the read that finds the day, and the day: where a model searched in 5 to 10 calls
  const [find, day] = r.sent;
  assert.deepEqual([find.select, find.order, find.limit], ["t:ts_utc,entity,variable,freq", "ts_utc.desc.nullslast", String(forms.NEWEST_READ)]);
  assert.equal(find.and, '(entity.eq."eia930:ERCO",ts_utc.lt.2026-10-08T05:00:00.000Z)');      // before today, on Texas's clock
  assert.equal(day.and, '(entity.eq."eia930:ERCO",ts_utc.gte.2026-10-03T05:00:00.000Z,ts_utc.lt.2026-10-04T05:00:00.000Z)');
  // worked again here from the recorded rows: the hours each Central day holds, newest first
  const counts = new Map();
  for (const x of find._rows) { const c = central(x.t).day; counts.set(c, (counts.get(c) ?? 0) + 1); }
  const days = [...counts.keys()].sort().reverse();
  assert.deepEqual([days[0], counts.get(days[0])], ["2026-10-04", 19]);  // the newest day is held to 18:00 Central: not whole
  assert.deepEqual([days[1], counts.get(days[1])], ["2026-10-03", 24]);
  assert.deepEqual(r.out.newest, { asked: "newest", held: true, day: "2026-10-03", tz: "America/Chicago", whole: true, rows: 24, rows_in_a_whole_day: 24, newest_row_at: "2026-10-04T23:00:00Z",
    newest_row_at_local: "6 pm Central, 4 October 2026",  // session 168: the same moment in ERCOT's words (lib/chat/plaintime.ts)
    newer_days_not_whole: [{ day: "2026-10-04", rows: 19, of: 24 }], before: "2026-10-08", day_before: "2026-10-07", day_before_held: false, note: r.out.newest.note });
  // the day itself, hour by hour: each value the recorded row's
  assert.equal(day._rows.length, 24);
  assert.deepEqual(r.out.result, day._rows.map((x) => ({ hour: `${central(x.t).day} ${central(x.t).hour}:00`, value: Number(x.v), n: 1 })));
  assert.deepEqual([r.out.summary.lowest, r.out.summary.highest], [{ hour: "2026-10-03 04:00", value: 49966 }, { hour: "2026-10-03 16:00", value: 62432 }]);   // what session 148's answer gave after eight tool calls
  // an answer may say which day was asked and which was read: every number of both is in the tool result
  assert.deepEqual(ask.unverified("Yesterday (2026-10-07) is not held whole; the newest whole day is 2026-10-03, when demand ran from 49966 MW to 62432 MW.", [JSON.stringify(r.out)]), []);
  // the lowest hour of the same day, as one figure
  const s = await run("s12_newest_min");
  assert.equal(s.sent.length, 2);
  const low = day._rows.reduce((a, b) => (Number(b.v) < Number(a.v) ? b : a));
  // session 168: the hour of the lowest demand comes with its words in ERCOT's own time, for the answer to copy (lib/chat/plaintime.ts)
  assert.deepEqual(s.out.result, [{ value: Number(low.v), n: 24, at: "2026-10-03T09:00:00Z", at_local: "4 am Central, 3 October 2026", entity: "eia930:ERCO" }]);
  assert.deepEqual(s.out.newest, r.out.newest);
});

await test("the newest day of a table of days is its newest row, of quarter hours a day of 96; more than one series, or a start, is refused", async () => {
  const d = await run("newest_daily_table");
  assert.equal(d.sent.length, 2);
  assert.equal(d.sent[0].limit, String(forms.NEWEST_READ_DATED));
  assert.deepEqual([d.out.newest.day, d.out.newest.day_before, d.out.newest.day_before_held, d.out.newest.step], ["2026-10-07", "2026-10-07", true, "P1D"]);   // yesterday is held: it is the day read
  assert.equal(d.out.rows_matched, 1);
  assert.equal(d.sent[1]._rows.length, 1);
  assert.deepEqual(d.out.result, [{ value: Number(d.sent[1]._rows[0].v), n: 1 }]);
  const q = await run("newest_quarter_hours");
  assert.deepEqual([q.out.newest.day, q.out.newest.whole, q.out.newest.rows, q.out.newest.rows_in_a_whole_day], ["2026-10-06", true, 96, 96]);
  assert.equal(q.sent[1]._rows.length, 96);
  assert.equal(q.out.result[0].value, Math.max(...q.sent[1]._rows.map((x) => Number(x.v))));
  const month = await run("h13_family_newest");                          // on a table of months: the newest month, and its 24 hours in one read
  assert.deepEqual([month.sent.length, month.sent[0].variable, month.out.newest.day, month.out.newest.step, month.out.result.length], [2, "eq.avg_battery_mw_h00", "2026-09-01", "P1M", 24]);
  assert.deepEqual([month.out.summary.lowest, month.out.summary.highest], [{ hour_of_day: "09", value: -8303 }, { hour_of_day: "19", value: 8280.7667 }]);
  const two = await run("newest_two_series");
  assert.ok(two.isError && two.out.error.includes("give entity and variable"));
  assert.equal(two.sent.length, 1);
  const withStart = await run("x", { table: "eia930_all_demand", aggregation: "min", entity: "eia930:ERCO", variable: "demand_mw", day: "newest", start: "2026-10-01" });
  assert.ok(withStart.isError && withStart.out.error.includes("give no start"));
  const other = await run("x", { table: "eia930_all_demand", aggregation: "min", entity: "eia930:ERCO", variable: "demand_mw", day: "yesterday" });
  assert.ok(other.isError && other.out.error.includes('day must be "newest"'));
  const things = await run("x", { table: "ercot_interconnection_queue", aggregation: "count", day: "newest" });
  assert.ok(things.isError && things.out.error.includes("series tables only"));
  for (const r of [withStart, other, things]) assert.equal(r.sent.length, 0);
});

await test("a whole day is every step its local day has: 23, 24 or 25 hours of them, and never a day made whole", () => {
  assert.deepEqual([forms.stepsPerHour(["PT1H", "PT1H"]), forms.stepsPerHour(["PT15M"]), forms.stepsPerHour(["PT5M"]), forms.stepsPerHour(["PT30M"])], [1, 4, 12, 2]);
  for (const f of [["PT1H", "PT15M"], ["P1D"], ["PT7M"], [], [null]]) assert.equal(forms.stepsPerHour(f), null);      // a step the tool cannot count a day by
  // clock times, newest first (they are instants, not data): a day of 24 hours, the day before whole, the newest in part
  const hours = (day, n) => Array.from({ length: n }, (_, i) => `${day}T${String(i).padStart(2, "0")}:00:00Z`).reverse();
  const dayOf = (t) => t.slice(0, 10);
  const part = forms.newestWholeDay([...hours("2026-10-04", 19), ...hours("2026-10-03", 24), ...hours("2026-10-02", 24)], dayOf, () => 24, false);
  assert.deepEqual(part.pick, { day: "2026-10-03", rows: 24, of: 24, whole: true });
  assert.deepEqual(part.days.map((d) => [d.day, d.rows, d.whole]), [["2026-10-04", 19, false], ["2026-10-03", 24, true], ["2026-10-02", 24, true]]);
  // the day the clocks go forward has 23 hours and is whole with 23; with 24 expected it would not be
  assert.equal(forms.newestWholeDay(hours("2026-03-08", 23), dayOf, () => 23, false).pick.whole, true);
  assert.equal(forms.newestWholeDay(hours("2026-03-08", 23), dayOf, () => 24, false).pick.whole, false);
  // no whole day among the rows read: the newest day, said to be in part, never filled
  assert.deepEqual(forms.newestWholeDay([...hours("2026-10-04", 19), ...hours("2026-10-03", 20)], dayOf, () => 24, false).pick, { day: "2026-10-04", rows: 19, of: 24, whole: false });
  // a read that came back full may have cut its oldest day short: that day is not judged
  assert.deepEqual(forms.newestWholeDay([...hours("2026-10-04", 24), ...hours("2026-10-03", 5)], dayOf, () => 24, true).days.map((d) => d.day), ["2026-10-04"]);
  // a step that is not known: the newest day, and whether it is whole is not said
  assert.deepEqual(forms.newestWholeDay(hours("2026-10-04", 19), dayOf, () => null, false).pick, { day: "2026-10-04", rows: 19, of: null, whole: null });
  assert.equal(forms.newestWholeDay([], dayOf, () => 24, false).pick, null);
});

// ================================================================== the entity first

await test("a series is asked for by its entity alone, and what comes back is what 'entity or node' returned", async () => {
  const r = await run("west_by_day");
  assert.equal(r.sent.length, 1);
  assert.equal(r.sent[0].or, undefined);
  assert.equal(r.sent[0].and, '(entity.eq."ercot:HB_WEST",ts_utc.gte.2026-09-01T00:00:00.000Z,ts_utc.lt.2026-10-01T00:00:00.000Z)');
  // session 143 recorded the same call under "entity or node" on 7 October: the same 30 rows, value for value
  const old = FIX143.results[0].out, oldRead = Object.keys(FIX143.reads).find((k) => decodeURIComponent(k).includes('or=(entity.eq."ercot:HB_WEST",node.eq."ercot:HB_WEST")'));
  assert.ok(oldRead);
  assert.deepEqual(r.sent[0]._rows.map((x) => [x.t, x.v]), FIX143.reads[oldRead].map((x) => [x.t, x.v]));
  assert.deepEqual([r.out.result, r.out.summary, r.out.rows_matched], [old.result, old.summary, old.rows_matched]);
  // a node as the ISO writes it: no row has it as its entity, so the same read is made for the node
  const n = await run("by_node");
  assert.deepEqual(n.sent.map((x) => [x.and.split(",")[0], x._rows.length]), [['(entity.eq."HB_NORTH"', 0], ['(node.eq."HB_NORTH"', 7]]);
  assert.equal(n.out.rows_matched, 7);
  // a scope's own filter on the entity stands beside the entity asked for and is never replaced by it: another grid's rows are not read
  const o = await run("another_grid_in_scope");
  assert.equal(o.out.rows_matched, 0);
  assert.ok(o.sent.length === 2 && o.sent.every((x) => x.entity === 'in.("iso:ercot")' && x._rows.length === 0));
  assert.deepEqual(o.sent.map((x) => x.and.split(",")[0]), ['(entity.eq."iso:caiso"', '(node.eq."iso:caiso"']);
  const src = read("../lib/chat/tools.ts");
  assert.ok(!src.includes("node.eq.${quote(a.entity)})`"));              // the one request for "entity or node" is gone
  assert.ok(src.includes("const byEntity = await one(\"entity\");") && src.includes("const byNode = await one(\"node\");"));
});

// ================================================================== the two switches

await test("the two switches are on by default, the server turns each off, and the default lives in one place", () => {
  assert.deepEqual({ ...sw.SWITCH_DEFAULTS }, { ASK_RULE_PLAN: "on", ASK_READER_EFFORT: "low" });
  assert.equal(sw.rulePlanOn({}), true);
  assert.equal(sw.rulePlanOn({ ASK_RULE_PLAN: "" }), true);                // set to nothing is not set
  assert.equal(sw.rulePlanOn({ ASK_RULE_PLAN: "on" }), true);
  for (const v of ["off", "OFF", "0", "false", "no"]) assert.equal(sw.rulePlanOn({ ASK_RULE_PLAN: v }), false, v);
  assert.equal(sw.readerEffort({}), "low");
  assert.equal(sw.readerEffort({ ASK_READER_EFFORT: "medium" }), "medium");
  assert.equal(sw.readerEffort({ ASK_READER_EFFORT: "off" }), "off");
  assert.equal(ask.effortOf("planner", "medium", {}), "low");
  assert.equal(ask.effortOf("planner", "medium", { ASK_READER_EFFORT: "off" }), "medium");
  assert.equal(ask.effortOf("planner", "medium", { ASK_READER_EFFORT: "high" }), "high");
  assert.equal(ask.effortOf("writer", "medium", {}), "medium");            // the writing turn is as it was
  // the default is in lib/chat/switches.ts and nowhere else: the loop reads neither variable and names neither value
  const loop = read("../lib/chat/ask.ts"), swSrc = read("../lib/chat/switches.ts");
  assert.ok(swSrc.includes('export const SWITCH_DEFAULTS = { ASK_RULE_PLAN: "on", ASK_READER_EFFORT: "low" } as const;'));
  assert.ok(!swSrc.includes("import "));
  assert.ok(loop.includes('import { readerEffort, rulePlanOn } from "./switches";'));
  assert.ok(!loop.includes("process.env.ASK_RULE_PLAN") && !loop.includes("env.ASK_READER_EFFORT") && !loop.includes("SWITCH_DEFAULTS"));
  for (const f of ["../lib/chat/ercot.ts", "../lib/chat/tools.ts", "../lib/chat/plan.ts", "../app/api/ask/route.ts"]) assert.ok(!/process\.env\.ASK_(RULE_PLAN|READER_EFFORT)/.test(read(f)), f);
  // no switch touches a ceiling, and the ceilings are as they were
  const limits = JSON.parse(read("../lib/chat/limits.json"));
  assert.deepEqual([limits.daily_usd, limits.monthly_usd, limits.per_visitor_per_day], [3, 30, 15]);
  assert.ok(!/ASK_DAILY_USD|ASK_MONTHLY_USD|ASK_PER_VISITOR/.test(swSrc + read("../lib/chat/forms.ts") + read("../lib/chat/ready.ts")));
  for (const k of ["ASK_RULE_PLAN", "ASK_READER_EFFORT", "ASK_FORMS", "ASK_PAGES", "ASK_ROLLUP"]) assert.equal(process.env[k], undefined, `${k} is set where the tests run`);
});

// ---- the loop itself, with a stand-in for the model (as scripts/test-ask-speed.mjs: no model is called; the key is not a key)
const sse = (reply) => {
  const ev = (type, data) => `event: ${type}\ndata: ${JSON.stringify({ type, ...data })}\n\n`;
  const blocks = reply.tools ? reply.tools.map((t, i) => [{ type: "tool_use", id: `toolu_fixture_${i + 1}`, name: t.name, input: {} }, { type: "input_json_delta", partial_json: JSON.stringify(t.input) }])
    : [[{ type: "text", text: "" }, { type: "text_delta", text: reply.text }]];
  return ev("message_start", { message: { id: "msg_fixture", type: "message", role: "assistant", model: "claude-sonnet-5-5", content: [], stop_reason: null, stop_sequence: null,
    usage: { input_tokens: 100, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 } } }) +
    blocks.map(([start, delta], index) => ev("content_block_start", { index, content_block: start }) + ev("content_block_delta", { index, delta }) + ev("content_block_stop", { index })).join("") +
    ev("message_delta", { delta: { stop_reason: reply.tools ? "tool_use" : "end_turn", stop_sequence: null }, usage: { output_tokens: 50 } }) + ev("message_stop", {});
};
const SWITCHES = ["ASK_RULE_PLAN", "ASK_READER_EFFORT", "ASK_FORMS", "ANTHROPIC_API_KEY"];
const TODAY = "2026-10-08";
const through = async (question, switches, script) => {
  const kept = Object.fromEntries(SWITCHES.map((k) => [k, process.env[k]]));
  Object.assign(process.env, { ANTHROPIC_API_KEY: "a-stand-in-not-a-key", ...switches });
  const sent = [], events = [];
  globalThis.fetch = async (url, init) => {
    const u = new URL(typeof url === "string" ? url : url.url ?? String(url));
    if (u.hostname === "api.anthropic.com") {
      if (u.pathname === "/v1/models") return new Response(JSON.stringify({ data: [{ type: "model", id: "claude-sonnet-5-5", display_name: "a stand-in", created_at: "2026-01-01T00:00:00Z" }], has_more: false, first_id: "claude-sonnet-5-5", last_id: "claude-sonnet-5-5" }), { status: 200, headers: { "content-type": "application/json" } });
      assert.equal(u.pathname, "/v1/messages");
      const body = JSON.parse(String(init.body));
      sent.push(body);
      return new Response(sse(script(body, sent.length)), { status: 200, headers: { "content-type": "text/event-stream", "request-id": `req_fixture_${sent.length}` } });
    }
    if ((init?.method ?? "GET") === "POST") return new Response("", { status: 201 });      // the cost ledger's row goes nowhere
    return fixtureFetch(url);
  };
  try {
    const r = await ask.ask(question, TODAY, null, ercotProfile(), null, { onEvent: (e) => events.push(e.type) });
    return { r, sent, events };
  } finally { globalThis.fetch = fixtureFetch; for (const k of SWITCHES) { if (kept[k] === undefined) delete process.env[k]; else process.env[k] = kept[k]; } }
};
const byId = Object.fromEntries(SET.questions.map((q) => [q.id, q.q]));
const said = (body) => body.messages.map((x) => (typeof x.content === "string" ? x.content : JSON.stringify(x.content))).join("\n");
const WEST = CALL.west_by_day.recorded.out;
const westDraft = () => JSON.stringify({ form: "chart", not_in_warehouse: false, series: ["r1"], premise: "",
  answer: `The West hub's day-ahead price ranged from ${WEST.summary.lowest.value} to ${WEST.summary.highest.value} USD/MWh over the month (ercot_hub_prices_daily).`,
  citations: [{ table: "ercot_hub_prices_daily", source_report: WEST.source_report, data_version: WEST.data_version, tier: "derived" }], nearest: [],
  followups: ["How did the North hub compare over the same month?", "Which day of the month was the dearest?"] });

await test("with nothing set on the server, a planned question is one model call, and the model's own reading turn is at the lower effort", async () => {
  // the rule on, by default: no reading turn by the model, the read made by code, the writer at the effort it always had
  const ruled = await through(byId.h16, {}, () => ({ text: westDraft() }));
  assert.equal(ruled.sent.length, 1);
  assert.equal(ruled.sent[0].tools, undefined);
  assert.equal(ruled.sent[0].output_config.effort, "medium");
  assert.deepEqual([ruled.r.status, ruled.r.planned_by, ruled.r.plan_shape, ruled.r.usage.requests], ["answered", "rule", "hub price", 1]);
  assert.deepEqual(ruled.r.series[0].check, { rows_fetched: 30, rows: 30, same: true, points: 30, not_drawn: 0 });
  // the rule turned off on the server: the question is the model's, and its reading turn is at the lower effort, by default
  const script = (body, k) => (k === 1 ? { tools: [{ name: "query", input: CALL.west_by_day.input }] } : { text: westDraft() });
  const model = await through(byId.h16, { ASK_RULE_PLAN: "off" }, script);
  assert.deepEqual(model.sent.map((b) => b.output_config.effort), ["low", "medium"]);
  assert.deepEqual([model.r.status, model.r.planned_by, model.r.usage.requests], ["answered", undefined, 2]);
  assert.deepEqual(model.r.series[0].rows, ruled.r.series[0].rows);                     // the same rows either way
  // both turned off on the server: the tool as session 148 left it in the code
  const off = await through(byId.h16, { ASK_RULE_PLAN: "off", ASK_READER_EFFORT: "off" }, script);
  assert.deepEqual(off.sent.map((b) => b.output_config.effort), ["medium", "medium"]);
  // a question the rule does not plan (an idea) is one call, the model's, with its tools, at the lower effort
  const idea = JSON.stringify({ form: "words", not_in_warehouse: false, series: [], premise: "", answer: "A hub is a set of points on the grid whose prices are averaged into one price that traders use to buy and sell power.",
    citations: [{ table: "docs/grids/ercot.md", source_report: "docs/grids/ercot.md: text written for the ERW's ERCOT page; each section names its ISO and EIA sources", data_version: "the site's build", tier: "written" }], nearest: [],
    followups: ["How does ERCOT set prices?", "What is a load zone?"] });
  const c = await through(byId.c02, {}, () => ({ text: idea }));
  assert.deepEqual([c.r.status, c.r.form, c.r.planned_by, c.sent.length, c.sent[0].output_config.effort], ["answered", "words", undefined, 1, "low"]);
});

await test("the model is shown the query with its three arguments, in compare's two queries too; ASK_FORMS=off shows the tools as they were; the exported spec is untouched", async () => {
  const spec = JSON.parse(read("../lib/chat/spec.json"));
  const before = JSON.stringify(spec.tools);
  const more = forms.extendTools(spec.tools);
  assert.equal(JSON.stringify(spec.tools), before);                        // nothing is changed in place
  const q = more.find((t) => t.name === "query"), cmp = more.find((t) => t.name === "compare");
  for (const s of [q.input_schema, cmp.input_schema.properties.a, cmp.input_schema.properties.b]) {
    assert.deepEqual(s.properties.day.enum, ["newest", "this_week"]);   // session 161: the week now running, one call
    assert.equal(s.properties.date_column.type, "string");
    assert.ok(s.properties.group_by.description.includes('"hour_of_day"') && s.properties.group_by.description.startsWith(spec.tools.find((t) => t.name === "query").input_schema.properties.group_by.description));
    assert.equal(s.additionalProperties, false);
  }
  assert.deepEqual(more.filter((t) => !["query", "compare"].includes(t.name)), spec.tools.filter((t) => !["query", "compare"].includes(t.name)));
  assert.ok(!("day" in spec.tools.find((t) => t.name === "query").input_schema.properties));
  const specErcot = read("../lib/chat/spec_ercot.json");
  for (const words of ["hour_of_day", "date_column", "source_precedence", "four pages"]) assert.ok(!specErcot.includes(words) && !before.includes(words), words);
  // what the loop sends: the three arguments are on the query the model sees, and the tools are otherwise the same
  const script = (body, k) => (k === 1 ? { tools: [{ name: "query", input: CALL.west_by_day.input }] } : { text: westDraft() });
  const on = await through(byId.h16, { ASK_RULE_PLAN: "off" }, script);
  const shown = on.sent[0].tools.find((t) => t.name === "query");
  assert.ok("day" in shown.input_schema.properties && "date_column" in shown.input_schema.properties && shown.description.includes("Three more forms"));
  assert.deepEqual(on.sent[0].tools.map((t) => t.name), [...spec.tools.map((t) => t.name), "page_figures", "page_file"]);
  assert.ok(on.sent[0].system[0].text.includes(forms.formsGuide()) && on.sent[0].system[0].text.includes(ready.readyGuide()));
  const off = await through(byId.h16, { ASK_RULE_PLAN: "off", ASK_FORMS: "off" }, script);
  assert.deepEqual(off.sent[0].tools.find((t) => t.name === "query"), spec.tools.find((t) => t.name === "query"));
  assert.equal(off.sent[0].system[0].text, profile153().system);            // the prompt as session 153 left it, to the letter
  assert.equal(forms.formsOffered(undefined), true);
  assert.equal(forms.formsOffered("off"), false);
  // the guide names what the model must give for each of the three, and the tables of the questions that failed
  const g = forms.formsGuide();
  for (const words of ['group_by "hour_of_day"', '"avg_wind_mw_h"', '"avg_battery_mw_h"', 'date_column "proposed_in_service_date"', '"Other - Battery Energy Storage"', 'day "newest"', "end is today's date", "do not search day by day", "Never read the hours a few at a time"]) assert.ok(g.includes(words), words);
  assert.ok(!forms.formsGuide(false).includes("cost_of_power_hourly_profile") && !forms.formsGuide(false).includes("caiso_curtailment_profile") && g.includes("cost_of_power_hourly_profile"));
});

// ================================================================== source precedence

const demandOf = async () => (await profile.ownTool("page_file", { view: "demand", grid: "ercot" })).out;

await test("source precedence: the operator's own figure leads and the derived one is named, and each tool result says which it is", async () => {
  const t = ready.TWICE_HELD[0];
  assert.equal(t.operator.table, pf.PAGE_FILES.cost);                       // the datacenter page's file, built from ERCOT's own hourly load
  assert.ok(t.operator.whose.includes("the operator's own") && t.operator.whose.includes("ercot_zone_load_hourly"));
  for (const d of t.derived) { assert.ok(profile.scope.tables.includes(d.table), d.table); assert.ok(/ERW/.test(d.whose) && /EIA/.test(d.whose) && d.whose.includes("not ERCOT's own file")); }
  // the page's file says where its demand comes from: the operator's table, not EIA's
  const index = JSON.parse(read("../data/datacenter/index.json"));
  assert.ok(index.grids.ercot.demand_source.startsWith("ercot_zone_load_hourly"));
  // each result is told which it is, and what stands beside it
  const own = await demandOf();
  const ownNote = ready.precedenceOf("page_file", { view: "demand", grid: "ercot" }), derivedNote = ready.precedenceOf("query", CALL.peak_derived.input);
  assert.deepEqual(profile.tag("page_file", { view: "demand" }, own, 1).source_precedence, ready.precedenceOf("page_file", { view: "demand" }));
  assert.deepEqual([ownNote.leads, ownNote.also_held_in.map((x) => x.table)], ["this source", ["grid_stress_yearly", "eia930_demand_growth"]]);
  assert.deepEqual(profile.tag("query", CALL.peak_derived.input, CALL.peak_derived.recorded.out, 2).source_precedence, derivedNote);
  assert.ok(derivedNote.leads.startsWith("site/data/datacenter/index.json") && derivedNote.this_source.includes("derived by the ERW") && derivedNote.rule.includes("lead with it"));
  for (const note of [ownNote, derivedNote]) assert.ok(note.rule.includes("the operator's own data wins over a derived file, and the answer names both"));
  // every other result is told nothing: another grid's demand, another view, another variable, another tool
  for (const [tool, input] of [["page_file", { view: "demand", grid: "caiso" }], ["page_file", { view: "cost" }], ["query", { table: "grid_stress_yearly", variable: "evening_ramp_mw" }], ["query", CALL.west_by_day.input], ["describe_table", { table: "grid_stress_yearly" }]])
    assert.equal(ready.precedenceOf(tool, input), null, JSON.stringify(input));
  assert.equal(profile.tag("query", CALL.west_by_day.input, WEST, 3).source_precedence, undefined);
  // a refusal carries no note, and a result id is still set as before
  assert.equal(profile.tag("query", CALL.peak_derived.input, { error: "x" }, 4).source_precedence, undefined);
  assert.equal(profile.tag("query", CALL.peak_derived.input, CALL.peak_derived.recorded.out, 2).result_id, "r2");
  // the rule is in the briefing, with the case in hand
  const s = profile.system;
  for (const words of ["SOURCE PRECEDENCE (the owner's ruling of 8 October 2026)", "the operator's own data wins over a derived file, and the answer names both", "Never average the two", 'page_file view "demand", grid "ercot": highest_hour_mw', "grid_stress_yearly, variable peak_demand_mw, entity iso:ercot", "Call both at once"]) assert.ok(s.includes(words), words);
});

await test("the year's highest hourly demand: one reading turn fetches both, the answer leads with ERCOT's own and names the derived one, and both numbers are traced", async () => {
  const own = await demandOf();
  const y = own.result.find((x) => x.year === "2026"), derived = CALL.peak_derived.recorded.out.result[0].value;
  const index = JSON.parse(read("../data/datacenter/index.json"));
  assert.equal(y.highest_hour_mw, Math.round(index.grids.ercot.demand["2026"].peak_mw));   // the page's own figure, from ERCOT's own hourly load
  assert.equal(derived, 91075);                                              // the ERW's, from EIA's hourly demand, as recorded from the live set
  assert.notEqual(y.highest_hour_mw, derived);                               // two sources, two figures
  const answer = `ERCOT's highest hourly demand so far in 2026 is ${y.highest_hour_mw} MW in ERCOT's own hourly load (site/data/datacenter/index.json; ${y.hours_held} hours of the year are held). The ERW's figure derived from EIA's hourly demand is ${derived} MW (grid_stress_yearly).`;
  const draft = JSON.stringify({ form: "sentence", not_in_warehouse: false, series: [], premise: "", answer,
    citations: [{ table: "site/data/datacenter/index.json", source_report: own.source_report, data_version: own.data_version, tier: "site file" },
      { table: "grid_stress_yearly", source_report: CALL.peak_derived.recorded.out.source_report, data_version: CALL.peak_derived.recorded.out.data_version, tier: "derived" }], nearest: [],
    followups: ["How many hours was the grid tight this year?", "How has the highest hour grown year by year?"] });
  const script = (body, k) => (k === 1 ? { tools: [{ name: "page_file", input: { view: "demand", grid: "ercot" } }, { name: "query", input: CALL.peak_derived.input }] } : { text: draft });
  const { r, sent } = await through(byId.s16, {}, script);
  assert.equal(sent.length, 2);                                              // one reading turn, one writing turn
  assert.deepEqual([r.status, r.form, r.tool_calls, r.series.length], ["answered", "sentence", 2, 0]);
  assert.equal(r.answer, answer);
  assert.deepEqual(r.citations.map((c) => c.table), ["site/data/datacenter/index.json", "grid_stress_yearly"]);
  // the writer was given both results, each marked with which source it is
  const given = said(sent[1]);
  assert.ok(given.includes('"leads":"this source"') && given.includes('"leads":"site/data/datacenter/index.json, the operator\'s own"'));
  assert.equal(given.split('"source_precedence"').length - 1, 2);
  assert.deepEqual(judge(SET.questions.find((q) => q.id === "s16"), r), []);
  // the operator's figure leads in the answer: it comes first
  assert.ok(r.answer.indexOf(String(y.highest_hour_mw)) < r.answer.indexOf(String(derived)));
});

// ================================================================== Texas's curtailment share

await test("the briefing says which source holds Texas's curtailment share, in one sentence taken from the page's Method note", async () => {
  const line = ready.curtailmentSentence().trim();
  assert.ok(profile.system.includes(line));
  assert.equal(line.split(". ").length, 2);                                  // its heading and one sentence
  for (const words of ['page_file view "share", grid "ercot"', "site/data/curtailment/ercot.json", "from 28 September 2026", "ercot_wind_solar_hsl_daily holds the megawatt-hours below the limit by day from 19 September 2026 and no share", "never make a percent yourself"]) assert.ok(line.includes(words), words);
  // what the sentence says is what the sources hold: the file gives the share over its whole days; the table is megawatt-hours
  const texas = JSON.parse(read("../data/curtailment/ercot.json"));
  const share = (await profile.ownTool("page_file", { view: "share", grid: "ercot" })).out;
  assert.equal(share.table, "site/data/curtailment/ercot.json");
  assert.equal(share.over_the_days_held.share_of_limit_pct, texas.window.both.share_pct);
  assert.deepEqual(share.days_held, { whole_days: texas.whole_days, from: texas.first_day, to: texas.last_day });
  assert.equal(texas.first_day, "2026-09-28");
  assert.ok(pf.pagesGuide().includes("ercot_wind_solar_hsl_daily (public, tier source, daily, from 2026-09-19)") && pf.pagesGuide().includes("wind_below_hsl_mwh"));
  // the Method note it was taken from
  const note = read("../../docs/methods/curtailment.md");
  for (const words of ["from 28 September 2026", "The page's file is `ercot.json`", "A day is the Central clock day and is whole when every one of its 23, 24 or 25 hours is held", "`ercot_wind_solar_hsl_daily` (session 18) reads the system-wide reports"]) assert.ok(note.includes(words), words);
  // the question that failed in session 153 expects the file's own figure
  const p14 = PAGES.questions.find((q) => q.id === "p14");
  assert.deepEqual(p14.expect, [texas.window.both.share_pct]);
});

// ================================================================== the closing words of a refusal

await test("a refusal about another grid closes in the tool's own name: the old words are gone from the prompt the model is given, and stay where they are still true", () => {
  const spec = JSON.parse(read("../lib/chat/spec_ercot.json"));
  const [[oldSpec], [oldPanel]] = ready.oldWords("ERCOT");
  assert.ok(spec.system.includes(oldSpec));                                  // the exported spec is as the Python loop writes it (that loop reads no page: its words are true)
  assert.ok(panel.addendum("ercot", "ERCOT").includes(oldPanel));
  assert.ok(profile153().system.includes(oldSpec) && profile153().system.includes(oldPanel));
  assert.deepEqual(ready.reworded(profile153().system, "ERCOT").missing, []);   // both sentences were found and reworded
  assert.ok(!profile.system.includes(oldSpec) && !profile.system.includes(oldPanel));
  assert.equal(profile.system.split("speaks for ERCOT only").length - 1, 1);    // once, in the rule that says never to write it
  assert.ok(profile.system.includes(`close with this sentence, as it stands: "${ready.CLOSING}"`));
  assert.ok(ready.CLOSING.startsWith("Ask ERCOT answers for the Texas grid, and for the other grids only what four pages of this site show"));
  assert.equal(ready.OLD_CLOSING.test(ready.CLOSING), false);
  for (const words of ['"held, not shown"', '"paused while terms are reviewed"', '"licensed source needed"', "/grid/<slug>", "the general chat at /ask"]) assert.ok(ready.closingRule().includes(words), words);
  // a prompt the sentences are not in is said, not passed over
  assert.equal(ready.reworded("no such words", "ERCOT").missing.length, 2);
  // without the four pages the tool does speak for ERCOT only: the old words stay, and no ruling about two sources is given
  const before = process.env.ASK_PAGES;
  process.env.ASK_PAGES = "off";
  try {
    const off = ercotProfile();
    assert.ok(off.system.includes(oldSpec) && off.system.includes(oldPanel) && !off.system.includes(ready.CLOSING) && !off.system.includes("SOURCE PRECEDENCE"));
    assert.ok(off.system.endsWith(forms.formsGuide(false)));                  // the three forms are the query's, whatever pages are offered
    assert.equal(off.tag("query", CALL.peak_derived.input, CALL.peak_derived.recorded.out, 1).source_precedence, undefined);
  } finally { if (before === undefined) delete process.env.ASK_PAGES; else process.env.ASK_PAGES = before; }
  // a tool's own message says what is read and no more
  const tools = read("../lib/chat/tools.ts");
  assert.ok(!tools.includes("this chat speaks for") && tools.includes("this chat reads the written notes of ${scope.iso} only"));
  // the page's own line says the same
  const page = read("../app/ask/ercot/page.tsx");
  assert.ok(!/speaks for ERCOT only/.test(page) && page.includes("only what four pages show"));
  assert.ok(![read("../lib/chat/forms.ts"), read("../lib/chat/ready.ts"), read("../lib/chat/switches.ts"), read("./test-ask-ready.mjs").replace("String.fromCharCode(0x2014)", ""), read("./record-ask-ready.mjs")].some((t) => t.includes(DASH)));
});

await test("the judge asks the thirteen refusals about another grid for the closing words, and every other question as before", () => {
  const close = "Ask ERCOT answers for[^.]{0,200}four pages", never = "(speaks|answers) for ERCOT only";
  const carried = [...SET.questions, ...PAGES.questions].filter((q) => q.close || q.never);
  assert.deepEqual(carried.map((q) => q.id), ["r01", "r02", "r03", "r04", "r05", "r06", "r16", "r19", "r22", "r23", "r25", "p19", "p20"]);
  assert.ok(carried.every((q) => q.kind === "refuse" && q.close === close && q.never === never));
  assert.ok(new RegExp(close, "i").test(ready.CLOSING));
  for (const [old] of ready.oldWords("ERCOT")) assert.ok(new RegExp(never, "i").test(old), old);
  // the fourteen other refusals (licensed data, a company's accounts, a forecast, advice) carry neither
  assert.equal(SET.questions.filter((q) => q.kind === "refuse" && !q.close).length, 14);
  assert.ok(SET.questions.filter((q) => q.kind === "refuse" && !q.close).every((q) => !/other grid|outside the warehouse/.test(q.why)));
  const r01 = SET.questions.find((q) => q.id === "r01"), p20 = PAGES.questions.find((q) => q.id === "p20");
  const ok = (answer) => ({ status: "not_in_warehouse", answer, series: [] });
  assert.deepEqual(judge(r01, ok(`PJM's Western Hub price is not held here. ${ready.CLOSING} PJM's own page is /grid/pjm, and the general chat at /ask covers the whole warehouse.`)), []);
  assert.deepEqual(judge(p20, ok(`MISO is paused while terms are reviewed, so no figure is given. ${ready.CLOSING}`)), []);
  // session 153's two refusals as they were given then: each now fails, for the old closing
  const then19 = "This chat answers for ERCOT only. ISO New England's curtailment of wind and solar is held, not shown: its monthly undelivered energy of dispatchable wind and solar plants is kept internal because of the publisher's legal notice. Its own page is /grid/isone, and the general chat at /ask covers the whole warehouse.";
  const then20 = "Not in the warehouse: MISO is paused while terms are reviewed, so no figure is given. This chat speaks for ERCOT only, and the general chat at /ask covers the whole warehouse.";
  assert.equal(judge(PAGES.questions.find((q) => q.id === "p19"), ok(then19)).length, 2);     // it does not close in the tool's own words, and it says the old ones
  assert.equal(judge(p20, ok(then20)).length, 2);
  assert.equal(judge(r01, ok("This panel answers for ERCOT only; PJM has its own page.")).length, 2);
  assert.equal(judge(r01, ok(`PJM is another grid. ${ready.CLOSING}`.replace("PJM", "It"))).length, 1);   // still must name what was asked
  // a refusal that carries neither field is judged exactly as it was
  const r11 = SET.questions.find((q) => q.id === "r11");
  assert.deepEqual(judge(r11, ok("ICE futures are licensed and not held; the nearest thing held is the day-ahead price.")), []);
  assert.ok(SET.rules_added_156.close && SET.rules_added_156.never && PAGES.rules_added_156.close && PAGES.rules_added_156.never);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
