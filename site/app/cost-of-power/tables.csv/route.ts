// Energy Research Warehouse (ERW) site, session 213: GET /cost-of-power/tables.csv?grid=..&region=..&mw=..&run=..&buy=..
// The tables "What a datacenter pays" drew until this session and draws no longer (the owner's chain prompt of
// 12 October 2026, the battery page's layout: extra tables go into the CSV download), in one long-form CSV, a row a
// cell: `table`, `row`, `column`, `value`, `note`. The tables: the three grid questions as the page drew them, "Will
// the power be there" (power_there), "How clean" (how_clean) and "How soon" (how_soon), the waits of a large load by
// stage (waits, with the figures the grid's own entities stated: waits_stated) and the rules in motion (rules, the
// grid's and the federal rows), every region of the grid over its own last twelve months (regions), the Commission's
// transmission charge matrix (matrix) and, where NYISO's file holds them, New York's load in line request by request
// (ny_load). The same read and arithmetic as the page (model.ts; lib/howsoon.ts and lib/rules.ts write the words the
// page's two blocks wrote). A value not held is blank, with its reason in `note`. In review, the address answers a
// visitor as the page does.
// Session 236: two more tables. "delivery": Texas's delivery tariffs line by line as filed (the schedule's name, its
// rate and unit as printed, its page, date and document, the line it was read from), each with what it comes to in USD
// per MWh for a flat load of the reader's size, and the sums by component and the total the page states
// (lib/datacenter/delivery.ts). "scenario_b_site": scenario B's own site, when the address names one (`bsite`): its
// two ways of running over its own last twelve months, and its scarce hours and carbon as the page states them.
import { hh, monthsWords, two, whole } from "@/lib/datacenter";
import { DELIVERY, INDEX } from "@/lib/datacenterdata";
import { basisOf, conditional, deliveryOf, kindOf, perMwh, slugOf, utilitiesOf } from "@/lib/datacenter/delivery";
import { basisWords, blockOf as waitsBlockOf, dayWords as waitsDay, measuredTip, measuredWords, notHereWhy, notYetWhy, sentenceOf, sourceWords, statedTip, waitingTip, waitingWords, NOT_HELD_WHY as WAITS_NOT_HELD, PAUSED_WHY as WAITS_PAUSED } from "@/lib/howsoon";
import { howSoonFile } from "@/lib/howsoondata";
import { statusOf } from "@/lib/release";
import { blockOf as rulesBlockOf, dayWords as rulesDay, docketTip, docketWords, linkOf, readOf, rulesGrid, statusOf as ruleStatus } from "@/lib/rules";
import { rulesFile } from "@/lib/rulesdata";
import * as stress from "@/lib/stress";
import { internalView } from "../battery/read";
import { cell, csv, text } from "../seller/csv";
import { DEMAND, NOWHERE, NYLOAD, NY_HELD_WHY, NY_HELD_WORDS, NY_SHOWN, QUEUES, day, inputsFrom, loadModel } from "../model";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;
  const q = Object.fromEntries([...sp.entries()]) as Record<string, string | undefined>;
  if (!(await internalView()) && statusOf("/cost-of-power") === "review") return text("in review: this download opens with the page it belongs to", 404);
  let M;
  try {
    M = await loadModel(inputsFrom(q), typeof q.buy === "string", q.grid, q);
  } catch (e) {
    return text(`the price files could not be read: ${e instanceof Error ? e.message : String(e)}`, 503);
  }
  const { x, g, market, size, regionRows, sf, sy, peak, peakAt, fuels, growth, lastTight, zones, withheld, cy, cv, own, qv, ll, flex, matrix, gridNames, waitsFor } = M;
  const name = g?.name ?? x.grid;
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const lines: string[] = [
    `# Energy Research Warehouse (ERW): the tables of "What a datacenter pays" beside the page, ${size} at ${x.region} in ${name}, buying ${market}`,
    `# long form: one row a cell (table, row, column, value, note); a value not held is blank with its reason in note`,
    `# sources: the demand, mix and queue tools' own files (eia930_demand_growth, grid_stress_yearly, clean_energy_summary, clean_energy_hourly, interconnection_queue_summary, ercot_large_load_status), the operator's hourly demand where held, the page's price files (data/datacenter, built ${INDEX.built.slice(0, 10)}), data/datacenter/how_soon.json and data/datacenter/rules.json (aggregates; no request's name is in them), NYISO's load interconnection requests where its terms allow; read at ${now}`,
    `# method: /data/methods/datacenter_pays_algorithm (sections 4.7 to 4.9 and 4.11 as the page drew them until session 213; the waits and the rules: /data/methods/datacenter_cost); the page: /cost-of-power`,
    "table,row,column,value,note",
  ];
  const put = (table: string, row: string, column: string, value: unknown, note = "") => lines.push([table, row, column, value, note].map(cell).join(","));
  const f2 = (v: number | null | undefined) => (v === null || v === undefined || !Number.isFinite(v) ? "" : v.toFixed(2));

  // 0. session 228: the three answers, as the page states them (lib/datacenter/answers.ts), each figure with its check key's name
  const A = M.answers?.ok ? M.answers.data : null;
  if (A) {
    const words = M.answerFacts.words;
    const S = "scarce_hours", sc = A.scarcity;
    put(S, "last_twelve_months", "hours", String(sc.hours), `at or above USD ${sc.level} per MWh at ${M.answerFacts.place}; ${sc.months[0]} to ${sc.months.at(-1)}; check key dc|${M.answersKey}|scarce:hours`);
    put(S, "last_twelve_months", "flat_load_usd", String(Math.round(sc.flatUsd * x.mw)), `what a flat load of ${size} paid in them; dc|${M.answersKey}|scarce:flat_usd`);
    for (const k of ["flat", "flex", "shift"] as const) {
      put(S, `way_${k}`, "words", words[k], A.held[k] ? "" : "not held here");
      if (A.held[k]) { put(S, `way_${k}`, "hours_off", String(sc.ways[k].off), `dc|${M.answersKey}|scarce:off:${k}`); put(S, `way_${k}`, "paid_usd", String(Math.round(sc.ways[k].paidUsd * x.mw))); put(S, `way_${k}`, "avoided_usd", String(Math.round(sc.ways[k].avoidedUsd * x.mw)), `dc|${M.answersKey}|scarce:avoided_usd:${k}`); }
    }
    for (const r of sc.byMonth) { put(S, `month_${r.m}`, "hours", String(r.hours)); put(S, `month_${r.m}`, "flat_load_usd", String(Math.round(r.usd * x.mw))); }
    sc.byHour.forEach((n, h) => { if (n) put(S, `clock_${String(h).padStart(2, "0")}`, "hours", String(n), `${M.answerFacts.stdName}, the hour starting ${String(h).padStart(2, "0")}:00`); });
    if (A.notices) { put(S, "operator_notices", "count", String(A.notices.count), A.notices.held ? `caiso_grid_emergencies, the notices dated in the twelve months; the table runs to ${A.notices.last}` : "no notice held"); for (const [t, n] of Object.entries(A.notices.byType)) put(S, "operator_notices", t, String(n)); }
    const C = "carbon", c = A.carbon;
    for (const k of ["flat", "flex", "shift"] as const) {
      put(C, `last_twelve_months_${k}`, "kg_co2_per_mwh", f2(c.l12[k].kgPerMwh), c.l12[k].kgPerMwh === null ? (A.held[k] ? "no month of the twelve has an intensity" : "not held here") : `${words[k]}; the grid's monthly intensity of consumed electricity weighted by the load's energy in each month, over the ${c.l12[k].months} of ${c.l12[k].of} months with an intensity; dc|${M.answersKey}|co2:l12:kg:${k}`);
      put(C, `last_twelve_months_${k}`, "tonnes_co2_a_year", c.l12[k].tonnesPerMw === null ? "" : String(Math.round(c.l12[k].tonnesPerMw! * x.mw)), `for ${size}; dc|${M.answersKey}|co2:l12:tonnes:${k}`);
      put(C, `hourly_window_${k}`, "kg_co2_per_mwh", f2(c.window.ways[k]), c.window.ways[k] === null ? "not held" : `${words[k]}; the load's own hours over ${c.window.hours} hours, ${c.window.from} to ${c.window.to}; dc|${M.answersKey}|co2:window:${k}`);
    }
    put(C, "hourly_window_grid", "kg_co2_per_mwh", f2(c.window.grid), `the grid's mean over the same ${c.window.hours} hours; dc|${M.answersKey}|co2:window:grid`);
    for (const r of c.years) put(C, `year_${r.y}`, "kg_co2_per_mwh", f2(r.kg), `the mean of ${r.months} months held; dc|${M.answersKey}|co2:year:${r.y}`);
    for (const r of c.monthly) put(C, `month_${r.m}`, "kg_co2_per_mwh", f2(r.kg), "carbon_intensity_monthly, intensity_demand");
    const L = "large_load";
    if (A.largeLoad) {
      for (const r of A.largeLoad.reports) {
        put(L, `report_${r.day}`, "approved_to_energize_mw", r.approved === null ? "" : String(r.approved), `ercot_large_load_status; dc|${M.answersKey}|ll:report:${r.day}:approved`);
        put(L, `report_${r.day}`, "observed_nonsimultaneous_peak_mw", r.running === null ? "" : String(r.running));
        put(L, `report_${r.day}`, "observed_simultaneous_peak_mw", r.simultaneous === null ? "" : String(r.simultaneous));
        if (r.submissions !== null) { put(L, `report_${r.day}`, "new_submissions_count", String(r.submissions)); put(L, `report_${r.day}`, "new_submissions_mw", r.submissionsMw === null ? "" : String(r.submissionsMw)); }
      }
      if (A.largeLoad.approvedChange !== null) put(L, "change", "approved_to_energize_mw", String(A.largeLoad.approvedChange), `${A.largeLoad.yearAgo?.day} to ${A.largeLoad.latest?.day}; dc|${M.answersKey}|ll:approved_change (the absolute change)`);
    } else put(L, "none", "approved_to_energize_mw", "", `${name} publishes no figure of large load waiting or energized that the warehouse holds as a public table.`);
    put(L, "rules_in_motion", "count", String(M.rules.count), M.rules.words);
  }

  // 0b. session 236: scenario B's own site, when it has one
  if (M.bSite && M.facts.b) {
    const B = "scenario_b_site", fb = M.facts.b;
    put(B, "site", "place", fb.place, fb.span ? `its own last twelve months: ${fb.span}` : "twelve complete months are not held there");
    (["flat", "flexible"] as const).forEach((label, i) => {
      const w = fb.ways[i];
      put(B, `way_${label}`, "usd_per_mwh", f2(w?.per), w ? M.facts.words[i] : fb.why[i]);
      if (w) { put(B, `way_${label}`, "usd_a_year", String(Math.round(w.cost * x.mw)), `for ${size}`); put(B, `way_${label}`, "mwh_a_year", String(Math.round(w.energy * x.mw))); }
      const bad = fb.bads[i];
      if (bad) put(B, `way_${label}`, "bad_month_usd_per_mwh", f2(bad.per), `${bad.m}; one month in ten of the ${bad.of} held cost this or more`);
    });
    const AB = M.answersB?.ok ? M.answersB.data : null;
    if (AB) {
      put(B, "scarce_hours", "hours", String(AB.scarcity.hours), `at or above USD ${AB.scarcity.level} per MWh; check key dc|${M.answersKeyB}|scarce:hours`);
      put(B, "scarce_hours", "flat_load_usd", String(Math.round(AB.scarcity.flatUsd * x.mw)), `dc|${M.answersKeyB}|scarce:flat_usd`);
      for (const k of ["flat", "flex", "shift"] as const) put(B, `carbon_${k}`, "kg_co2_per_mwh", f2(AB.carbon.l12[k].kgPerMwh), AB.carbon.l12[k].kgPerMwh === null ? "not held" : `dc|${M.answersKeyB}|co2:l12:kg:${k}`);
    } else put(B, "scarce_hours", "hours", "", M.answersB && !M.answersB.ok ? `the live set could not be read: ${M.answersB.reason}` : "twelve complete months are not held there");
  }

  // 1. will the power be there
  const T = "power_there";
  if (growth?.avg_demand_growth_since_2019_pct !== undefined) {
    put(T, `demand_growth_2019_to_${DEMAND.last_year}`, "average_pct", f2(growth.avg_demand_growth_since_2019_pct), "/demand");
    put(T, `demand_growth_2019_to_${DEMAND.last_year}`, "highest_hour_pct", f2(growth.peak_demand_growth_since_2019_pct));
  } else put(T, `demand_growth_2019_to_${DEMAND.last_year}`, "average_pct", "", `No whole year of ${DEMAND.last_year} or of 2019 is held for this grid in the demand table.`);
  if (peak !== null) { put(T, `highest_hour_of_demand${sy ? `_${sy}` : ""}`, "mw", String(Math.round(peak)), "/mix?view=stress"); if (peakAt && sf) put(T, `highest_hour_of_demand${sy ? `_${sy}` : ""}`, "when", stress.when(peakAt, sf.tz)); }
  else put(T, "highest_hour_of_demand", "mw", "", "The year's highest hour is not in the grid stress table for this grid.");
  if (fuels.length) for (const f of fuels) put(T, `installed_capacity${sy ? `_${sy}` : ""}`, f.name, String(Math.round(f.capacity!)), peak ? `${two((100 * f.capacity!) / peak)} percent of the year's highest hour of demand` : "");
  else put(T, "installed_capacity", "mw", "", "No installed capacity is held for this grid and year.");
  const noDemand = withheld ? `${name} publishes its hourly demand by zone, and its legal notice restricts duplication of its content. The table is held internally and nothing of it is shown.` : `The operator's own hourly demand is not held for ${name}, so its tight hours are not counted.`;
  if (lastTight) {
    put(T, `hours_tight_${lastTight.y}`, "hours", String(Math.round(lastTight.d.tight_hours!)), lastTight.when ? `in ${monthsWords(lastTight.when.months)}, between ${hh(lastTight.when.from)} and ${hh(lastTight.when.to + 1)}; tight: at or above ${INDEX.tight * 100} percent of the year's highest hour` : `tight: at or above ${INDEX.tight * 100} percent of the year's highest hour`);
    put(T, `hours_tight_${lastTight.y}`, "this_load_off_in", x.run === "flat" ? "0" : x.run === "shift" ? "" : lastTight.down === null ? "" : String(lastTight.down),
      x.run === "flat" ? "a flat load runs in every hour" : x.run === "shift" ? "A load that shifts energy within the day is never off for a whole hour by rule, so its tight hours are not counted here." : lastTight.down === null ? "No price is held for this region in that year." : "");
  } else put(T, "hours_tight", "hours", "", noDemand);
  const zoneRows = Object.entries(zones).map(([z, ys]) => {
    const wholeYears = Object.keys(ys).filter((y) => ys[y].hours_held >= 0.95 * ys[y].hours_due && ys[y].hours_due >= 8760).sort();
    const a = wholeYears[0], b = wholeYears.at(-1);
    return { z, a, b, from: a ? ys[a].mean_mw : null, to: b ? ys[b].mean_mw : null, peak: b ? ys[b].peak_mw : null };
  }).filter((r) => r.a && r.b && r.a !== r.b);
  if (zoneRows.length) for (const r of zoneRows) {
    put(T, `demand_by_region_${r.z}`, `average_mw_${r.a}`, String(Math.round(r.from!)), r.z === x.region ? "the load's own region" : "");
    put(T, `demand_by_region_${r.z}`, `average_mw_${r.b}`, String(Math.round(r.to!)));
    put(T, `demand_by_region_${r.z}`, "change_pct", f2((100 * (r.to! - r.from!)) / r.from!));
    put(T, `demand_by_region_${r.z}`, `highest_hour_mw_${r.b}`, String(Math.round(r.peak!)));
  } else put(T, "demand_by_region", "average_mw", "", Object.keys(zones).length ? "No region holds two whole years of hourly demand." : withheld ? noDemand : `Hourly demand by region is not held for ${name}.`);

  // 2. how clean
  const C = "how_clean", notClean = "Not in the clean energy table for this grid and year.";
  put(C, `carbon_free_share_of_generation${cy ? `_${cy}` : ""}`, "pct", f2(cv?.share), cv?.share != null ? "/mix?view=clean" : "The year's carbon-free share is not in the clean energy table for this grid.");
  put(C, `a_flat_load_meets_hour_by_hour${cy ? `_${cy}` : ""}`, "pct", f2(cv?.flat), cv?.flat != null ? "" : notClean);
  put(C, `matched_hour_by_hour_buying_the_whole_year${cy ? `_${cy}` : ""}`, "energy_pct", f2(cv?.match.mix?.[100]?.energy), cv?.match.mix?.[100]?.energy != null ? "carbon-free energy equal to the load's whole year, shaped like the grid's own, against 100 percent on the annual count" : notClean);
  put(C, `matched_hour_by_hour_buying_the_whole_year${cy ? `_${cy}` : ""}`, "hours_fully_covered_pct", f2(cv?.match.mix?.[100]?.hours), cv?.match.mix?.[100]?.hours != null ? "" : notClean);
  put(C, `carbon_per_mwh_a_flat_load${cy ? `_${cy}` : ""}`, "kg_co2_per_mwh", f2(cv?.carbon.flat), cv?.carbon.flat != null ? "" : notClean);
  put(C, `this_loads_own_hours${cy ? `_${cy}` : ""}`, "pct", f2(own?.load), own?.load != null ? `the grid's carbon-free share in each hour, weighted by this load in that hour, over ${whole(own.hours)} hours${flex && own.flat !== null ? `; a flat load over the same hours ${two(own.flat)}` : ""}` : cy ? `The carbon-free share by hour is not held for ${name} in ${cy} at the hours this region's price is held.` : "No year of the clean energy table is held for this grid.");

  // 3. how soon
  const S = "how_soon";
  if (qv) { put(S, "generation_waiting_to_connect", "mw", String(Math.round(qv.total_active_mw)), "/queues"); put(S, "generation_waiting_to_connect", "active_requests", String(Math.round(qv.total_active_requests))); }
  else put(S, "generation_waiting_to_connect", "mw", "", "The interconnection queue summary holds no row for this grid.");
  if (qv?.median_years_to_operation !== undefined) { put(S, "request_to_operation_median", "years", f2(qv.median_years_to_operation), `over ${whole(qv.years_to_operation_n)} projects`); }
  else put(S, "request_to_operation_median", "years", "", "Too few dated projects to state a median for this grid.");
  if (qv?.past_operating_share_pct !== undefined) { put(S, `requests_entered_${QUEUES.past[0]}_to_${QUEUES.past[1]}`, "operating_pct", f2(qv.past_operating_share_pct)); put(S, `requests_entered_${QUEUES.past[0]}_to_${QUEUES.past[1]}`, "withdrawn_pct", f2(qv.past_withdrawn_share_pct)); }
  else put(S, `requests_entered_${QUEUES.past[0]}_to_${QUEUES.past[1]}`, "operating_pct", "", "Not in the queue summary for this grid.");
  if (ll) { put(S, "large_load_approved_to_energize", "mw", String(Math.round(ll.last.approved!)), `ERCOT, ${ll.last.day}; /datacenters`); put(S, "large_load_approved_to_energize", "observed_running_mw", String(Math.round(ll.last.nonsimultaneous!))); }
  else put(S, "large_load_approved_to_energize", "mw", "", x.grid === "ercot" ? "ERCOT's large load status table holds no report with these figures." : `${name} publishes no figure of large load approved or running that the warehouse holds.`);
  if (x.grid === "nyiso") {
    if (NY_SHOWN) { for (const z of NYLOAD.zones) { put(S, `large_load_in_line_${z.zone_name}`, "mw", String(z.mw), z.zone_name === x.region ? "the load's own zone" : ""); put(S, `large_load_in_line_${z.zone_name}`, "requests", String(z.requests), z.by_status.map((b) => `${b.status}: ${b.requests} requests, ${b.mw} MW`).join("; ")); } put(S, "large_load_in_line_New_York", "mw", String(NYLOAD.total.mw), `${NYLOAD.source.name}, sheet "Load Projects", as NYISO last changed it on ${NYLOAD.source.workbook_last_modified}. ${NYLOAD.rule.in_line}`); }
    else put(S, "large_load_in_line", "mw", "", `${NY_HELD_WORDS}: ${NY_HELD_WHY}`);
  } else put(S, "large_load_in_line", "mw", "", x.grid === "ercot" ? `${NOWHERE}: ERCOT publishes the large load seeking interconnection as system totals in slide decks, with no table by zone or county. A search on 7 October 2026 found no public list by place.` : `${NOWHERE}: a search on 7 October 2026 found no public list of the large load waiting for power in ${name} by place. The pieces sit in utility planning filings, rate cases and operator reports.`);

  // 4. how long a large load waits, by stage (lib/howsoon.ts writes the words the page's block wrote)
  const W = "waits";
  const { file: wf, error: werr } = howSoonFile();
  const wb = waitsBlockOf(wf, waitsFor), wg = wb.entry, wname = gridNames[waitsFor] ?? waitsFor.toUpperCase(), wplace = wg?.place ?? wname;
  put(W, "sentence", "words", sentenceOf(wf, waitsFor, wname), `for ${wplace}`);
  if (wb.state === "paused") put(W, "state", "words", "paused while terms are reviewed", WAITS_PAUSED);
  else if (wb.state === "not held") put(W, "state", "words", "", werr && werr !== "not there" ? `The file of measured waits could not be read: ${werr}.` : WAITS_NOT_HELD);
  else if (wb.state === "measured" && wg && wg.copies) {
    wg.stages.forEach((st, i) => {
      const row = `stage_${i + 1}_${st.label.replace(/[^A-Za-z0-9]+/g, "_")}`;
      put(W, row, "measured_here", st.measured.n ? `${st.measured.n} requests: ${measuredWords(st)}` : "", measuredTip(st, wg.copies!, wf!));
      put(W, row, "still_waiting", st.waiting.n ? `${st.waiting.n} requests: ${waitingWords(st)} (lower bound)` : "none", waitingTip(st, wg.copies!, wf!));
      st.stated.forEach((s, j) => put(W, row, `stated_${j + 1}`, s.figure, `${statedTip(s)}${s.url ? ` ${s.url}` : ""}`));
    });
    put(W, "copies", "words", sourceWords(wg.copies), `${wg.copies.n === null ? "dated copies" : `${wg.copies.n} dated copies`}, ${waitsDay(wg.copies.first)} to ${waitsDay(wg.copies.last)}; the file built ${waitsDay(wf!.built_at_utc)}`);
  } else {
    put(W, "state", "words", wb.state === "not measured here" ? "not measured here" : "not measured yet", wb.state === "not measured here" && wg ? notHereWhy(wg) : notYetWhy(wname));
  }
  if (wg && wg.stated.length) wg.stated.forEach((s, i) => { put("waits_stated", `stated_${i + 1}`, "whose", basisWords(s), s.stated_by); put("waits_stated", `stated_${i + 1}`, "figure", s.figure, statedTip(s)); put("waits_stated", `stated_${i + 1}`, "covers", s.covers); put("waits_stated", `stated_${i + 1}`, "document", `${s.document}${s.date ? `, ${waitsDay(s.date) ?? s.date}` : ""}${s.page ? `, page ${s.page}` : ""}`, s.url ?? ""); });

  // 5. the rules in motion (lib/rules.ts writes the words the page's block wrote)
  const R = "rules";
  const rgrid = rulesGrid(q.grid, x.grid), rname = gridNames[rgrid] ?? rgrid.toUpperCase();
  const { file: rf, error: rerr } = rulesFile();
  const rb = rulesBlockOf(rf, rgrid);
  const ruleRows = (rows: typeof rb.rows, group: string) => rows.forEach((r) => {
    const row = `${group}_${r.id}`, st = ruleStatus(r), rd = readOf(r);
    put(R, row, "date", rulesDay(r.date) ?? "", rulesDay(r.date) ? "" : "The document states no date for this row.");
    put(R, row, "status", st.words, st.why);
    put(R, row, "regulator_and_docket", docketWords(r), `${docketTip(r)}${linkOf(r) ? ` ${linkOf(r)}` : ""}`);
    if ((r.title ?? "").trim() || (r.topic ?? "").trim()) put(R, row, (r.title ?? "").trim() ? "title" : "topic", ((r.title ?? "").trim() || (r.topic ?? "").trim()), (r.why_here ?? "").trim());
    put(R, row, "model_read", rd.line ?? "", rd.line ? "a model's read of the document, not the regulator's words" : rd.why);
  });
  if (rb.state === "paused") put(R, "state", "words", rb.words ?? "paused while terms are reviewed", rb.why ?? "");
  else {
    if (rb.state === "shown") ruleRows(rb.rows, rname.replace(/[^A-Za-z0-9]+/g, "_"));
    else put(R, "state", "words", rb.state === "none" ? (rb.words ?? "none held") : "", rb.state === "none" ? (rb.why ?? "") : rerr && rerr !== "not there" ? `The file of rules in motion could not be read: ${rerr}.` : rb.why ?? "");
    if (rf) {
      if (rb.federal.length) ruleRows(rb.federal, "federal"); else put(R, "federal", "words", "none held", "No federal action in motion that names no grid operator is held.");
      if (rf.built_at_utc) put(R, "file", "built", rf.built_at_utc.slice(0, 10), Number(rf.window_months) > 0 ? `It holds proceedings that are open, and orders and rules dated in the ${Number(rf.window_months)} months before it.` : "");
    }
  }

  // 6. every region of the grid over its own last twelve months, a flat load
  for (const r of regionRows) put("regions", r.id, "flat_usd_per_mwh", f2(r.per), r.per !== null ? `${r.sp}${r.name ? `; ${r.name}` : ""}${r.id === x.region ? "; the load's own region" : ""}` : r.from ? `Held from ${day(r.from)}: ${whole(r.hours)} hours, not yet twelve complete months.` : `No ${market} price is held for this region.`);
  // 6b. session 236: Texas's delivery tariffs, line by line as filed, and the page's sums by component (ERCOT)
  if (x.grid === "ercot") {
    const D = "delivery";
    for (const u of utilitiesOf(DELIVERY.rows)) {
      const d = deliveryOf(DELIVERY.rows, u, x.mw), slug = slugOf(u);
      DELIVERY.rows.filter((r) => r.utility === u).forEach((r, i) => {
        const row = `${slug}_line_${String(i + 1).padStart(2, "0")}`, v = perMwh(r, x.mw), b = basisOf(r.unit);
        put(D, row, "schedule", r.charge, `${r.utility}, ${r.rate_class}`);
        put(D, row, "component", kindOf(r), r.why ?? "");
        put(D, row, "rate_as_filed", r.value_as_written, `${r.unit}${r.column ? `; column ${r.column}` : ""}`);
        put(D, row, "rate", String(r.value), r.unit);
        put(D, row, "usd_per_mwh_flat_load", conditional(r) || v === null ? "" : v.toFixed(4), conditional(r) ? `not added: ${r.applies}` : v === null ? "the unit names no basis, so the line is not converted" : b === "energy" ? "the rate per kWh times 1,000" : b === "customer_month" ? `the rate times 12 over ${x.mw} MW times 8,760 hours (one account, one meter)` : "the rate times 12,000 over 8,760 (the load's size as its demand; a kVA as a kW)");
        put(D, row, "document", r.document, `${r.page ? `page ${r.page}` : ""}${r.effective ? `; effective ${r.effective}` : ""}; ${r.url}`);
        put(D, row, "line_read", r.sentence, r.terms);
      });
      for (const c of d.components) put(D, `${slug}_sum`, c.kind, c.perMwh.toFixed(2), `${c.lines} lines added${c.conditional ? `, ${c.conditional} conditional left out` : ""}${c.unread ? `, ${c.unread} not converted` : ""}; check key dcd|${x.mw}|${slug}:${c.kind}`);
      put(D, `${slug}_sum`, "total", d.total.toFixed(2), `USD per MWh for a flat load of ${size}; never added to the market cost; check key dcd|${x.mw}|${slug}:total`);
    }
    for (const w of DELIVERY.withheld) put(D, slugOf(w.utility), "total", "", `${w.words}: ${w.why}`);
  }
  // 7. the Commission's transmission charge matrix, as printed (ERCOT)
  for (const r of matrix) put("matrix", `${r.year}${r.matrix ? `_matrix_${r.matrix}` : ""}_${r.scope.replace(/[^A-Za-z0-9]+/g, "_")}`, r.quantity, String(r.value), `${r.status === "approved" ? "approved" : "filed, not approved"}; ${r.document}, filed ${r.filed}; column "${r.header}"${r.scan_url || r.url ? `; ${r.scan_url || r.url}` : ""}`);
  if (x.grid === "ercot" && !matrix.length) put("matrix", "none", "postage_stamp_rate", "", "The Commission's transmission charge matrices are not in this page's files yet.");
  // 8. New York's load in line, request by request, where NYISO's terms allow it
  if (x.grid === "nyiso" && NY_SHOWN) {
    for (const r of NYLOAD.rows.filter((k) => k.in_line).sort((a, b) => (b.mw ?? 0) - (a.mw ?? 0))) {
      const row = `${r.queue_position}_${r.sheet_row}`;
      put("ny_load", row, "request", r.name, [r.end_use_words, r.utility ? `utility: ${r.utility}` : ""].filter(Boolean).join("; "));
      put("ny_load", row, "zone", `${r.zone} ${r.zone_name}`, r.zone_name === x.region ? "the load's own zone" : "");
      put("ny_load", row, "county", r.county);
      put("ny_load", row, "mw", r.mw === null ? "" : String(r.mw), r.mw === null ? "NYISO's sheet prints no megawatts for this request." : "");
      put("ny_load", row, "requested", r.request_date_printed);
      put("ny_load", row, "proposed_in_service", r.proposed_in_service_printed);
      put("ny_load", row, "status", r.status, `${NYLOAD.source.name}, sheet "${r.sheet}", row ${r.sheet_row}; the workbook as NYISO last changed it on ${NYLOAD.source.workbook_last_modified}`);
    }
  }
  return csv(lines, `erw_datacenter_tables_${x.grid}_${x.region.replace(/[^A-Za-z0-9_.-]/g, "_")}.csv`);
}
