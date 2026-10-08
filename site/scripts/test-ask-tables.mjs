// Energy Research Warehouse (ERW) site, session 153: Ask ERCOT reads what stands behind four pages (/cost-of-power,
// /curtailment, /cost-of-power/seller, /resources). No model and no request: the pages' own files are read from this
// copy, and the two questions answered from tables are replayed on reads recorded from the site's database
// (tests/fixtures/session153/table_reads.json).
//
//   node --import ./scripts/alias-register.mjs scripts/test-ask-tables.mjs
//
// What is held here: every new source is in the panel with what it is and what it is not; a table held internally is
// refused by its name by every tool, and no figure of it leaves; MISO and PJM give their words and no figure; the
// tool page_file returns the page's own figure (set against the pages' own functions and against the numbers that
// warehouse/chat/eval/ercot_pages_expected.py computed from the same files in another language); the 20 questions are
// well formed and the judge's added rules hold what they say; ASK_PAGES=off leaves the panel as session 148 left it.
import assert from "node:assert/strict";
import fs from "node:fs";
import { judge, holds, numbersIn, decimals } from "./eval-judge.mjs";

const read = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf8");
const FIX = JSON.parse(read("../../tests/fixtures/session153/table_reads.json"));
const SET = JSON.parse(read("../../warehouse/chat/eval_ercot_pages.json"));
const OLD = JSON.parse(read("../../warehouse/chat/eval_ercot_panel.json"));

// the recorded reads stand in for the database: the catalogue, the registry of sources (empty), and the rows recorded
process.env.SUPABASE_URL = "https://fixture.invalid";
process.env.SUPABASE_ANON_KEY = "fixture";
const log = [];
globalThis.fetch = async (url) => {
  const u = new URL(String(url)), q = Object.fromEntries(u.searchParams);
  log.push(`${u.pathname.split("/").pop()} ${q.table_name ?? ""} ${q.variable ?? ""}`.trim());
  let body;
  if (u.pathname.endsWith("/catalogue")) body = FIX.catalogue;
  else if (u.pathname.endsWith("/sources") || u.pathname.endsWith("/headers")) body = [];
  else if (u.pathname.endsWith("/series")) {
    const table = q.table_name.replace(/^eq\./, ""), variable = (q.variable ?? "").replace(/^eq\./, "");
    if (!FIX.rows.some((r) => r.table_name === table)) throw new Error(`a read of ${table} that was not recorded`);
    const [, lo] = /ts_utc\.gte\.([^,)]+)/.exec(q.and ?? "") ?? [], [, hi] = /ts_utc\.lt\.([^,)]+)/.exec(q.and ?? "") ?? [];
    // session 156: the query asks for a series by its entity alone, a term of "and" (it was "entity or node" in "or");
    // a read by node, which the tool makes only when no row has the entity, finds nothing here (the rows hold no node)
    const entity = /entity\.eq\."([^"]+)"/.exec(q.and ?? q.or ?? "")?.[1];
    if (/node\.eq\./.test(q.and ?? "")) return new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
    body = FIX.rows.filter((r) => r.table_name === table && (!variable || r.variable === variable) && (!entity || r.entity === entity) && (!lo || Date.parse(r.ts_utc) >= Date.parse(lo)) && (!hi || Date.parse(r.ts_utc) < Date.parse(hi)))
      .sort((x, y) => (x.ts_utc < y.ts_utc ? -1 : x.ts_utc > y.ts_utc ? 1 : 0)).map((r) => ({ t: r.ts_utc, v: r.value, entity: r.entity, variable: r.variable, unit: r.unit }));
  } else throw new Error(`a request the fixture does not hold: ${u.pathname}`);
  return new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } });
};

const pf = await import("../lib/chat/pagefiles.ts");
const links = await import("../lib/chat/pagelinks.ts");
const { ercotProfile, profile153 } = await import("../lib/chat/ercot.ts");
const { runTool } = await import("../lib/chat/tools.ts");
const cap = await import("../lib/capture.ts");
const dc = await import("../lib/datacenter.ts");
const dcData = await import("../lib/datacenterdata.ts");
const cur = await import("../lib/curtailment.ts");
const fe = await import("../lib/freeenergy.ts");
const res = await import("../lib/resources.ts");
const profile = ercotProfile();

let n = 0, failed = 0;
const test = async (name, f) => {
  n += 1;
  try { await f(); console.log(`ok ${n} ${name}`); } catch (e) { failed += 1; console.log(`FAIL ${n} ${name}\n   ${e.message.split("\n").slice(0, 6).join("\n   ")}`); }
};
const at = (o, p) => p.split(".").reduce((a, k) => (a === null || a === undefined ? a : a[k]), o);
const own = async (name, input) => { const r = await profile.ownTool(name, input); assert.ok(r, `${name} is not the profile's tool`); return r; };
const guide = pf.pagesGuide();
const DASH = String.fromCharCode(0x2014);

// ---- every new entry is in the catalogue, with what it is and what it is not

await test("the ten tables of the live set are in the panel's scope, each with its rows, its entry in the guide and what it holds", () => {
  assert.deepEqual(pf.PAGES_TABLES, ["iso_curtailment_monthly", "caiso_curtailment_daily", "spp_curtailment_daily", "ercot_wind_solar_hsl_daily", "caiso_curtailment_profile", "eia930_demand_growth", "interconnection_queue_summary", "ercot_large_load_status", "cost_of_power_hourly_profile", "cost_of_power_carbon"]);
  for (const t of pf.PAGES_TABLES) {
    assert.ok(profile.scope.tables.includes(t), `${t} is not in the scope`);
    assert.deepEqual(profile.scope.filters[t], pf.PAGES_FILTERS[t]);
    assert.ok(guide.includes(t), `the guide does not name ${t}`);
    assert.ok(pf.PAGES_HOLDS[t], `no words for ${t} as the nearest thing held`);
    const c = FIX.catalogue.find((r) => r.table_name === t);
    assert.ok(c && ["yes", "review"].includes(c.in_live_set) && c.license === "public", `${t} is not a public table of the live set in the recorded catalogue`);
  }
  // the curtailment tables are every grid's the page shows; those the datacenter page borrows, and its grid-by-grid view's, are ERCOT's rows only
  for (const t of ["cost_of_power_hourly_profile", "cost_of_power_carbon"]) assert.deepEqual(pf.PAGES_FILTERS[t], { entity: "ercot:HB_HUBAVG" });
  for (const t of ["iso_curtailment_monthly", "caiso_curtailment_daily", "spp_curtailment_daily", "caiso_curtailment_profile"]) assert.deepEqual(pf.PAGES_FILTERS[t], {});
  assert.deepEqual(pf.PAGES_FILTERS.eia930_demand_growth, { entity: "eia930:ERCO" });
  assert.ok(pf.PAGES_FILTERS.interconnection_queue_summary.entity.every((e) => e.startsWith("queue:ercot:")));
  assert.ok(profile.system.includes(guide) && profile153().system.endsWith(guide));   // session 156: the guide is whole in the served prompt, and one block follows it (it was the end)
});

await test("the tool page_file is offered beside the others, and each of its views is in the guide with what it is not", () => {
  assert.deepEqual(profile.tools.map((t) => t.name), ["page_figures", "page_file"]);
  assert.deepEqual([...pf.PAGE_FILE_TOOL.input_schema.properties.view.enum], [...pf.PAGE_FILE_VIEWS]);
  for (const v of pf.PAGE_FILE_VIEWS) { assert.ok(guide.includes(`"${v}"`), `the guide does not name the view ${v}`); assert.ok(pf.PAGE_FILE_TOOL.description.includes(`"${v}"`), v); }
  // what each is not, in the words of the pages' own Method notes
  for (const words of [
    "IT IS NOT a bill: wholesale energy only", "a hub or zone is an average over many points, not a site", "NOT a measure of scarcity or of an emergency",                 // datacenter_cost.md
    "it is the FLEET'S SHAPE", "it is not what a plant with a contract earns", '"Combined" is two revenues added',          // cost_of_power.md
    "ERCOT publishes no curtailment figure", "the ERW's ESTIMATE", "held from 28 September 2026", "Never add the grids up",  // curtailment.md
    "CAISO's shares of 2026 rest on its Today's Outlook output", "The data does not say where a curtailment happened",
    "IT IS NOT energy for nothing", "IT IS NOT a loss anyone booked",
    "IT IS NOT a siting study", "NOT a gross capacity factor and is never called one", "No place name is looked up",     // resources.md
    "the 2026 matrices are filed, not approved",
    '"paused while terms are reviewed"', '"licensed source needed"', "HELD, NOT SHOWN",
  ]) assert.ok(guide.includes(words), `the guide lacks: ${words}`);
  assert.ok(!guide.includes(DASH) && !JSON.stringify(pf.PAGE_FILE_TOOL).includes(DASH));
  // each "is not" stands in a Method note: the sentence the guide rests on is there, word for word
  const notes = { cost: read("../../docs/methods/datacenter_cost.md"), seller: read("../../docs/methods/cost_of_power.md"), curtailment: read("../../docs/methods/curtailment.md"), page: read("../app/resources/page.tsx") };
  const flat = (s) => s.replace(/\s+/g, " ");
  for (const [note, words] of [["cost", "**The 2026 matrices are not approved**"], ["cost", "**A hub is not a site.**"], ["cost", "**Wholesale energy only.**"], ["seller", "**It is the fleet's shape, not a site's:**"],
    ["seller", "**Combined** is the two revenues added, and nothing else"], ["curtailment", "So the months of 2026 rest on Today's Outlook"], ["curtailment", "ERCOT publishes no curtailment figure"],
    ["curtailment", "it is what the energy would have fetched at the hub, not a loss anyone booked"], ["page", "It is not a siting study, and it says nothing of land use, access to transmission, permits or cost."]]) assert.ok(flat(notes[note]).includes(words), `${note}: ${words}`);
  const cf = pf.manifest().layers.find((l) => l.id === "wind_capacity_factor");
  assert.ok(cf.notes_for_method.includes("so this is not one, and it is not named one"));
});

await test("each file a view reads is named as a source with its page, and may be given as the nearest thing held", () => {
  for (const f of Object.values(links.PAGE_FILES)) {
    assert.ok(fs.existsSync(new URL(`../../${f}`, import.meta.url)), `${f} is not a file of this site`);
    assert.ok(links.PAGE_FILE_HREF[f]?.href.startsWith("/"), f);
    assert.ok(pf.PAGES_HOLDS[f], f);
    assert.ok(pf.PAGES_NEAR.includes(f));
  }
  assert.ok(read("../components/ask/AskPanel.tsx").includes("if (PAGE_FILE_HREF[table]) return PAGE_FILE_HREF[table];"));
  // a refusal that names one of them as nearest passes the profile's own check, and the reader is shown what it holds
  const draft = { answer: "held, not shown", citations: [], not_in_warehouse: true, form: "words", series: [], followups: ["What did California curtail last month?", "What share did SPP curtail last year?"], nearest: ["iso_curtailment_monthly", links.PAGE_FILES.shares], premise: "" };
  assert.deepEqual(profile.extraProblems(draft, [], []), []);
  const shown = profile.finish("not_in_warehouse", draft, []);
  assert.deepEqual(shown.nearest.map((x) => x.table), draft.nearest);
  assert.ok(shown.nearest.every((x) => x.holds.length > 20));
});

await test("ASK_PAGES=off leaves the panel as session 148 left it", () => {
  assert.equal(pf.pagesOffered(undefined), true);
  assert.equal(pf.pagesOffered("off"), false);
  // session 156: the profile the route serves is this session's with one layer more (ercotProfile); what session 153
  // added, and what its switch takes away, is held on the profile as that session left it (profile153)
  const on = profile153();
  assert.ok(on.system.endsWith(guide));
  const before = process.env.ASK_PAGES;
  process.env.ASK_PAGES = "off";
  try {
    const off = profile153();
    assert.equal(off.system, on.system.slice(0, -guide.length));
    assert.ok(!off.system.includes("page_file") && !off.system.includes("iso_curtailment_monthly"));
    const served = ercotProfile();                                        // and the served profile names no page's source either
    assert.ok(served.system.startsWith(off.system) && !served.system.includes("page_file") && pf.PAGES_TABLES.every((t) => !served.system.includes(t)));
    assert.deepEqual(off.tools.map((t) => t.name), ["page_figures"]);
    assert.equal(off.scope.tables.length, profile.scope.tables.length - pf.PAGES_TABLES.length);
    assert.ok(pf.PAGES_TABLES.every((t) => !off.scope.tables.includes(t)));
    assert.equal(off.ownTool("page_file", { view: "layers" }), null);     // not its tool: the loop answers "unknown tool"
  } finally { if (before === undefined) delete process.env.ASK_PAGES; else process.env.ASK_PAGES = before; }
  assert.equal(process.env.ASK_PAGES, undefined);
});

// ---- an internal table is refused by name, and no figure of it leaves

const delivery = JSON.parse(read("../data/datacenter/texas_delivery.json"));
const internalFigures = [...new Set([...(delivery.matrix ?? []), ...delivery.rows].flatMap((r) => [String(r.value_as_written ?? "").replace(/[^0-9.]/g, ""), String(r.value)]).filter((s) => /\d\.\d{3,}/.test(s) || /^\d{6,}(\.\d+)?$/.test(s)))];   // a figure exact enough to be told from any other number: three decimals or more, or six digits or more

await test("a table held internally is refused by its name by every tool, with the publisher's words and never a figure", async () => {
  assert.deepEqual(pf.HELD.map((h) => h.table), ["isone_zone_prices_history", "isone_ddg_undelivered_monthly", "isone_zone_load_hourly", "nyiso_load_queue", "texas_transmission_matrix", "texas_delivery_charges"]);
  assert.equal(pf.HELD_WORDS, "held, not shown");
  assert.ok(internalFigures.length >= 40, `the page's file of Texas charges holds its figures (${internalFigures.length} told apart)`);
  const before = log.length;
  for (const h of pf.HELD) {
    const calls = [["query", { table: h.table, aggregation: "latest" }], ["describe_table", { table: h.table }],
      ["compare", { a: { table: h.table, aggregation: "mean" }, b: { table: "ercot_hub_prices_daily", aggregation: "mean" } }], ["page_file", { view: "cost", place: h.table }], ["list_tables", { sector: h.table }]];
    for (const [name, input] of calls) {
      const r = await own(name, input);
      assert.equal(r.isError, true, `${name} of ${h.table}`);
      assert.ok(r.out.error.startsWith(`${h.table} is held, not shown: `), r.out.error.slice(0, 80));
      assert.equal(r.out.held_not_shown, h.table);
      assert.ok(r.out.error.includes("State no figure of it") && r.out.error.includes(h.nearest));
      for (const f of internalFigures) assert.ok(!r.out.error.includes(f), `a figure of the internal file is in the refusal: ${f}`);
    }
    assert.ok(guide.includes(`- ${h.table}: ${h.what}`), `the guide does not say that ${h.table} is held`);
    assert.ok(pf.PAGES_NEAR.includes(h.nearest) || profile.scope.tables.includes(h.nearest), `${h.nearest} is no table of the guide`);
    assert.ok(!profile.scope.tables.includes(h.table), `${h.table} is in the scope`);
  }
  assert.equal(log.length, before, "a refusal read the database");
  // the publishers' own sentences, as the Method notes quote them
  const cost = read("../../docs/methods/datacenter_cost.md").replace(/\s+/g, " "), curt = read("../../docs/methods/curtailment.md").replace(/\s+/g, " ");
  const quoted = (h) => [...h.reason.matchAll(/"([^"]{30,})"/g)].map((m) => m[1]);
  for (const h of pf.HELD) for (const s of quoted(h)) assert.ok(cost.includes(s) || curt.includes(s), `not in a Method note, word for word: ${s.slice(0, 60)}`);
  assert.ok(quoted(pf.HELD[0]).length && quoted(pf.HELD[3]).length && quoted(pf.HELD[4]).length);
  // the grids' own views: ISO-NE's curtailment is held, New York's is not in the ERW, and neither gives a figure
  const isone = pf.pageFile({ view: "share", grid: "isone", period: "2026-08" });
  assert.ok(isone.error.startsWith("isone_ddg_undelivered_monthly is held, not shown"));
  const ny = pf.pageFile({ view: "share", grid: "nyiso" });
  assert.equal(ny.words, "not in the ERW");
  assert.equal(ny.result, undefined);
  // no figure of the internal tables is in the guide, the tool's description, or any result of the tool on Texas
  const everything = [guide, JSON.stringify(pf.PAGE_FILE_TOOL), ...["cost", "regions", "demand"].map((v) => JSON.stringify(pf.pageFile({ view: v, grid: "ercot" })))].join(" ");
  for (const f of internalFigures) assert.ok(!everything.includes(f), `a figure of the internal file is given: ${f}`);
  // New York's load in line: the site's file holds no request, and the tool has no view of it
  const nyq = JSON.parse(read("../data/nyiso_load_queue.json"));
  assert.equal(nyq.shown, false);
  assert.ok(!("rows" in nyq) && !("zones" in nyq));
  assert.ok(!read("../lib/chat/pagefiles.ts").includes("nyiso_load_queue.json") && !read("../lib/chat/pagefiles.ts").includes("texas_delivery.json"));
});

await test("MISO reads \"paused while terms are reviewed\" and PJM \"licensed source needed\", in every view, with no figure", () => {
  for (const [grid, words] of [["miso", "paused while terms are reviewed"], ["pjm", "licensed source needed"]]) {
    for (const view of ["cost", "regions", "demand", "capture", "hubs", "share", "free_energy", "worth"]) {
      const out = pf.pageFile({ view, grid, fuel: "wind", place: "INDIANA.HUB" });
      assert.equal(out.words, words, `${view} ${grid}`);
      assert.equal(out.error, undefined);
      assert.equal(out.result, undefined);
      assert.deepEqual(numbersIn(JSON.stringify({ ...out, table: "" })), [], `a number in ${view} of ${grid}`);
    }
  }
});

// ---- a file tool returns the page's own figure

await test("the capture price is the seller page's: its own functions on its own file, at the cents the page prints", () => {
  const file = JSON.parse(read("../data/seller/capture.json"));
  for (const [grid, hub, market, fuel] of [["ercot", "HB_WEST", "rt", "solar"], ["ercot", "HB_HUBAVG", "da", "wind"], ["caiso", "TH_SP15_GEN-APND", "rt", "solar"], ["nyiso", "N.Y.C.", "da", "wind"], ["spp", "SPPNORTH_HUB", "rt", "wind"]]) {
    const out = pf.pageFile({ view: "capture", grid, place: hub, market, fuel });
    const t = cap.twelve(cap.hubOf(file, grid, hub)[market][fuel], file.near);
    assert.ok(t, `${hub} ${fuel}`);
    // the page prints two(mine.price), signed(mine.premium), two(mine.flat) and signed(mine.pct, 1) (app/cost-of-power/seller/page.tsx)
    assert.equal(out.last_twelve_months.capture_price_usd_per_mwh.toFixed(2), cap.two(t.price).replace(/,/g, ""));
    assert.equal(out.last_twelve_months.flat_average_usd_per_mwh.toFixed(2), cap.two(t.flat).replace(/,/g, ""));
    assert.equal(cap.signed(out.last_twelve_months.premium_usd_per_mwh), cap.signed(t.premium));
    assert.equal(cap.signed(out.last_twelve_months.premium_pct_of_flat, 1), cap.signed(t.pct, 1));
    assert.deepEqual([out.last_twelve_months.from, out.last_twelve_months.to], [t.from, t.to]);
    assert.equal(out.table, "site/data/seller/capture.json");
    assert.ok(out.is_not.includes("the fleet's shape, not a site's"));
    const ys = cap.years(cap.hubOf(file, grid, hub)[market][fuel], file.near).filter((y) => y.f);
    assert.deepEqual(out.result.map((r) => [r.year, r.value.toFixed(2)]), ys.map((y) => [y.y, cap.two(y.f.price).replace(/,/g, "")]));
  }
  const all = pf.pageFile({ view: "hubs", grid: "ercot", fuel: "solar" });
  assert.equal(all.result.length + all.no_last_twelve_months.length, file.grids.ercot.hubs.length);
  assert.ok(pf.pageFile({ view: "capture", grid: "ercot", fuel: "gas" }).error.includes('"solar" or "wind"'));
  assert.ok(pf.pageFile({ view: "capture", grid: "ercot", fuel: "solar", place: "HB_NOWHERE" }).error.includes("held: HB_HUBAVG"));   // never the main hub in place of one that is not held
});

await test("what a flat load paid is the datacenter page's: its own functions on its own yearly files", () => {
  for (const [grid, region, market] of [["ercot", "LZ_NORTH", "rt"], ["ercot", "HB_WEST", "da"], ["caiso", "TH_SP15_GEN-APND", "rt"], ["nyiso", "N.Y.C.", "da"]]) {
    const out = pf.pageFile({ view: "cost", grid, place: region, market });
    const ms = dc.monthsRuled(dcData.yearFiles(grid), region, market, { run: "flat", n: 0, pct: 0, shift: 0 }, "forecast").months;   // as the page's LoadView computes a flat load
    const l12 = dc.lastTwelve(ms), s12 = dc.span(l12);
    assert.equal(out.last_twelve_months.usd_per_mwh.toFixed(2), dc.two(s12.per));                                   // data-stat l12_per
    assert.equal(out.last_twelve_months.power_per_gpu_hour_usd.toFixed(4), dc.gpuHour(s12.per, dc.ASSUMED.gpu.value, dc.ASSUMED.pue.value).toFixed(4));   // data-stat gpu_hour
    const bad = dc.badMonth(dc.last36(ms).months);
    assert.equal(out.bad_month.usd_per_mwh.toFixed(2), dc.two(bad.cost / bad.energy));
    assert.deepEqual(out.result.map((r) => [r.year, r.value.toFixed(2)]), dc.years(ms).map((y) => [y.y, dc.two(y.flat)]));
    assert.ok(out.is_not.startsWith("Wholesale energy only"));
  }
  // ERCOT with no place named is the page's own default, its North load zone; a zone with day-ahead only is read day-ahead
  assert.equal(pf.pageFile({ view: "cost" }).place, dcData.INDEX.grids.ercot.main);
  assert.equal(pf.pageFile({ view: "cost", place: "LZ_AEN" }).market, "day-ahead");
  assert.ok(pf.pageFile({ view: "cost", place: "LZ_AEN", market: "rt" }).error.includes("no real time price is held"));
  // will the power be there: the index's own counts of tight hours, the page's rule for a region's two whole years; ISO-NE's demand is held, SPP's is not held
  const tight = pf.pageFile({ view: "demand", grid: "ercot" });
  assert.deepEqual(tight.result.map((r) => [r.year, r.value]), Object.entries(dcData.INDEX.grids.ercot.demand).filter(([, d]) => d.tight_hours !== undefined).sort(([x], [y]) => x.localeCompare(y)).map(([y, d]) => [y, d.tight_hours]));
  assert.equal(tight.demand_by_region.length, Object.keys(dcData.INDEX.grids.ercot.zones).length);
  assert.ok(tight.is_not.includes("not a measure of scarcity") && tight.result.at(-1).whole_year === false);
  assert.ok(pf.pageFile({ view: "demand", grid: "isone" }).error.startsWith("isone_zone_load_hourly is held, not shown"));
  assert.ok(pf.pageFile({ view: "demand", grid: "spp" }).not_held.includes("not held for SPP"));
  // ISO-NE's zones are the public six weeks only: no twelve months, and so no figure
  const z = pf.pageFile({ view: "cost", grid: "isone", place: ".Z.MAINE" });
  assert.ok(z.last_twelve_months.not_held && z.prices_held.from >= "2026-08-26");
});

await test("curtailment's share, free energy and worth are the curtailment page's figures", () => {
  const shares = JSON.parse(read("../data/curtailment/shares.json")), free = JSON.parse(read("../data/curtailment/free_energy.json")), worth = JSON.parse(read("../data/curtailment/worth.json")), texas = JSON.parse(read("../data/curtailment/ercot.json"));
  for (const grid of ["caiso", "spp"]) {
    const sg = shares.grids[grid], marks = cur.shareMarks(sg);
    const out = pf.pageFile({ view: "share", grid, period: "2025" });
    assert.equal(out.newest_month.share_pct.toFixed(2), cur.two(sg.months[marks.last].share_pct));         // the page's <N k="share|last">
    assert.equal(out.highest_month.month, marks.highest);
    assert.equal(out.period.share_pct.toFixed(2), cur.two(cur.periodShare(sg, "2025").share));              // <N k="head|share"> for a year
    assert.equal(out.result.length, Object.keys(sg.months).filter((m) => m.startsWith("2025-")).length);
    assert.ok(out.is_not.includes("never added up"));
  }
  assert.ok(pf.pageFile({ view: "share", grid: "caiso", period: "2026-09" }).newest_month.output_from.includes("Today's Outlook"));
  const tx = pf.pageFile({ view: "share", grid: "ercot" });
  assert.equal(tx.over_the_days_held.share_of_limit_pct, texas.window.both.share_pct);
  assert.equal(tx.days_held.from, "2026-09-28");
  assert.equal(tx.result.length, texas.whole_days);
  assert.ok(tx.whose.includes("The ERW's estimate") && tx.a_whole_month.not_held);
  for (const [grid, w] of [["ercot", "year"], ["caiso", "month"], ["spp", "year"]]) {
    const out = pf.pageFile({ view: "free_energy", grid, window: w });
    const top = fe.ranked(free.grids[grid], w);
    assert.deepEqual(out.result.map((r) => [r.place, r.value, r.below_zero]), top.map((l) => [l.id, l.win.under5, l.win.negative]));   // the page's ranked places
  }
  const west = pf.pageFile({ view: "free_energy", grid: "ercot", place: "HB_WEST" });
  assert.equal(west.result.reduce((a, r) => a + r.value, 0), west.in_the_window.hours_under_usd_5);      // a whole year: the months add up to the year's count
  const w = pf.pageFile({ view: "worth", grid: "caiso", period: "2025" });
  assert.equal(w.period.usd_per_mwh_curtailed, worth.grids.caiso.hubs["TH_SP15_GEN-APND"].rt.years["2025"].usd_per_mwh_curtailed);
  assert.equal(pf.pageFile({ view: "worth", grid: "ercot" }).over_the_hours_held.value_usd, worth.grids.ercot.hubs.HB_HUBAVG.rt.window.value_usd);
  assert.ok(pf.pageFile({ view: "worth", grid: "spp" }).not_held.includes("held by day"));
});

await test("a resource layer gives its unit, publisher, vintage and range, the value of a cell, and a shape by name; never a place name", () => {
  const m = JSON.parse(read("../data/resources/manifest.json"));
  const all = pf.pageFile({ view: "layers" });
  assert.equal(all.layers_held, m.layers.length);
  for (const l of m.layers) { const row = all.layers.find((x) => x.layer === l.id); assert.ok(row && row.unit === (l.unit ?? "") && row.publisher === l.publisher && row.vintage === l.vintage, l.id); }
  // session 159: hydropower is held (two layers of Oak Ridge National Laboratory's), so it is no longer among what is
  // not held; what the list of layers names as not held, each with its reason, is what this view says is not held
  assert.deepEqual(all.not_held, (m.missing ?? []).map((x) => ({ layer: x.id, why: x.reason })));
  assert.ok(all.not_held.some((x) => x.layer === "wind_gross_capacity_factor" && x.why.includes("key issued to a named person")));
  assert.ok(!all.not_held.some((x) => /hydro/.test(x.layer)) && ["hydropower_npd", "hydropower_nsd"].every((id) => all.layers.some((x) => x.layer === id && x.unit === "MW" && x.publisher.startsWith("Oak Ridge National Laboratory"))));
  const one = pf.pageFile({ view: "layer", layer: "wind_capacity_factor" });
  assert.ok(one.what_it_is_not.includes("it is not named one") && one.is_not.includes("not a gross capacity factor"));
  // the cell under a place, by the page's own decoder (lib/resources.ts), at the finest level the page draws
  const l = m.layers.find((x) => x.id === "wind_speed_100m"), finest = [...l.levels].sort((a, b) => a.cell_deg - b.cell_deg)[0];
  const f = JSON.parse(read(`../data/resources/layers/${finest.file}`));
  const v = res.valueAt(res.decodeGrid(f), -101.83, 35.22);
  const out = pf.pageFile({ view: "value_at", layer: "wind_speed_100m", lon: -101.83, lat: 35.22 });
  assert.equal(res.show(out.value, res.decimalsOf(f.scale)), res.show(v, res.decimalsOf(f.scale)));         // what the hover prints
  assert.equal(out.cell_of_degrees, finest.cell_deg);
  assert.ok(out.value >= l.legend.min && out.value <= l.legend.max);
  assert.equal(pf.pageFile({ view: "value_at", layer: "wind_speed_100m", lon: -30, lat: 35 }).value, null);    // the open sea: outside the grid, and no value is made
  assert.ok(pf.pageFile({ view: "value_at", layer: "wind_speed_100m" }).error.includes("no place name is looked up"));
  assert.equal(pf.pageFile({ view: "value_at", layer: "solar_ghi", lon: -157.86, lat: 21.31 }).part, "Hawaii");
  assert.deepEqual(pf.pageFile({ view: "value_at", layer: "oil_gas_basins", lon: -102.08, lat: 31.99 }).shapes_that_hold_this_place.map((x) => x.name), ["Permian"]);
  const basins = JSON.parse(read("../data/resources/layers/oil_gas_basins.json")).features;
  const names = pf.pageFile({ view: "features", layer: "oil_gas_basins" });
  assert.deepEqual(names.result.map((r) => r.name), basins.map((b) => b.properties.name));
  assert.ok(pf.pageFile({ view: "features", layer: "wind_speed_100m" }).error.includes("is a grid"));
  // session 159: "hydropower" is part of two layers' names now, so it finds one (the first the list holds); a name that
  // is no layer's, "tidal", is still answered with the layers there are
  assert.equal(pf.pageFile({ view: "layer", layer: "hydropower" }).layer, "hydropower_npd");
  assert.equal(pf.pageFile({ view: "layer", layer: "hydropower_nsd" }).unit, "MW");
  assert.ok(pf.pageFile({ view: "layer", layer: "tidal" }).error.startsWith("no resource layer"));
});

await test("a result with rows is marked like a query's and charted from its own rows; a figure alone is not", async () => {
  const r = await own("page_file", { view: "capture", grid: "ercot", fuel: "wind", place: "HB_HUBAVG" });
  const tagged = profile.tag("page_file", {}, r.out, 3);
  assert.equal(tagged.result_id, "r3");
  assert.equal(profile.tag("page_file", {}, pf.pageFile({ view: "layers" }), 4).result_id, undefined);
  assert.equal(profile.tag("page_file", {}, pf.pageFile({ view: "share", grid: "isone" }), 5).result_id, undefined);
  const records = [{ tool: "page_file", input: { view: "capture", grid: "ercot", fuel: "wind", place: "HB_HUBAVG" }, out: tagged, isError: false }];
  const draft = { answer: "x", form: "chart", series: ["r3"], citations: [{ table: tagged.table, source_report: tagged.source_report, data_version: tagged.data_version, tier: "site file" }], not_in_warehouse: false, followups: ["a?", "b?"], nearest: [], premise: "" };
  assert.deepEqual(profile.extraProblems(draft, records, []), []);
  const shown = profile.finish("answered", draft, records);
  assert.equal(shown.series.length, 1);
  assert.equal(shown.series[0].table, "site/data/seller/capture.json");
  assert.equal(shown.series[0].kind, "line");
  assert.ok(shown.series[0].check.same && shown.series[0].rows.length === tagged.result.length);
  assert.deepEqual(shown.series[0].rows.map((x) => [x.key, x.value]), tagged.result.map((x) => [x.year, x.value]));
});

// ---- the 20 questions

await test("the 20 questions are well formed: four pages, the kinds, one source each, two refusals with their words", () => {
  const qs = SET.questions;
  assert.equal(qs.length, 20);
  assert.equal(new Set(qs.map((q) => q.id)).size, 20);
  assert.ok(qs.every((q) => !OLD.questions.some((o) => o.id === q.id || o.q === q.q)), "a question of the 100 is repeated");
  const pages = ["/cost-of-power", "/curtailment", "/cost-of-power/seller", "/resources"];
  for (const p of pages) assert.ok(qs.filter((q) => q.page === p).length >= 4, `fewer than four questions about ${p}`);
  assert.ok(qs.every((q) => pages.includes(q.page) && ["sentence", "chart", "refuse"].includes(q.kind) && q.new === "pages153" && q.q.length <= 500 && !q.q.includes(DASH)));
  const kinds = (k) => qs.filter((q) => q.kind === k);
  assert.equal(kinds("refuse").length, 2);
  assert.ok(kinds("chart").length >= 6 && kinds("sentence").length >= 8);
  assert.deepEqual(kinds("refuse").map((q) => q.say).sort(), ["held, not shown", "paused while terms are reviewed"]);
  for (const q of qs) {
    assert.ok(q.source && q.read?.tool && q.read.input, q.id);
    if (q.kind === "sentence") assert.ok((q.expect ?? q.expect_all).length >= 1 && q.cite, `${q.id}: no expected number or source`);
    if (q.kind === "chart") assert.ok(q.series_has && q.series_rows >= 3 && q.cite, `${q.id}: no expected row`);
    if (q.cite) assert.ok(new RegExp(q.cite).test(q.source), `${q.id}: its own source does not match its pattern`);
    if (q.cite) assert.ok([...Object.values(links.PAGE_FILES), ...pf.PAGES_TABLES].some((t) => new RegExp(q.cite).test(t)), `${q.id}: no source of the panel matches`);
  }
  // every digit a question holds is one the answer may repeat; none of the questions names a number it expects
  for (const q of qs.filter((x) => x.expect)) for (const e of q.expect) assert.ok(!holds(q.q, e), `${q.id} gives its own answer`);
});

await test("each question's read, replayed with no model, gives the number the script computed from the same file", async () => {
  for (const q of SET.questions) {
    const r = q.read;
    if (r.tool === "page_file") {
      const { out, isError } = await own("page_file", r.input);
      if (r.refused) { assert.ok(isError && out.error.startsWith(r.refused), q.id); continue; }
      if (r.words) { assert.equal(out.words, r.words, q.id); assert.equal(out.result, undefined); continue; }
      assert.equal(isError, false, `${q.id}: ${out.error}`);
      assert.ok(new RegExp(q.cite).test(out.table), `${q.id}: the tool names ${out.table}`);
      if (r.contains) { assert.ok(JSON.stringify(out).includes(r.contains), q.id); for (const e of q.expect_all) assert.ok(holds(JSON.stringify(out), e), `${q.id}: ${e}`); continue; }
      // session 159: p14 rests on site/data/curtailment/ercot.json, which the daily run rebuilds, so its share moves each day;
      // its read must still give a number, and the question file is written again by the script before an evaluation
      if (r.at && q.id === "p14") { const v = at(out, r.at); assert.equal(typeof v, "number", `${q.id}: ${r.at}`); continue; }
      if (r.at) { const v = at(out, r.at); assert.equal(r.abs ? Math.abs(v) : v, q.expect[0], `${q.id}: ${r.at}`); continue; }
      const [k, key] = Object.entries(r.row)[0];
      const row = out.result.find((x) => x[k] === key);
      assert.ok(row, `${q.id}: no row ${key}`);
      assert.equal(row.value, (q.series_has ?? { value: q.expect[0] }).value, q.id);
      if (q.series_rows) assert.equal(out.result.length, q.series_rows, `${q.id}: rows`);
    } else {
      const { out, isError } = await runTool(r.tool, r.input, profile.scope);
      assert.equal(isError, false, `${q.id}: ${out.error}`);
      assert.equal(out.result[0].value, q.expect[0], q.id);
      assert.ok(new RegExp(q.cite).test(out.table));
    }
  }
  // a table of another grid's rows is read whole under ERCOT's scope: California's rows are not filtered away
  const ca = await runTool("query", { table: "iso_curtailment_monthly", aggregation: "mean", entity: "caiso:ISO", variable: "share_curtailed_pct", start: "2025-01-01", end: "2026-01-01", group_by: "month" }, profile.scope);
  assert.equal(ca.out.result.length, 12);
  assert.ok(log.some((l) => l.startsWith("series eq.iso_curtailment_monthly")));
});

await test("the judge's added rules: a number at its own precision, a source, a row of a series; the 100 are judged as they were", () => {
  assert.equal(decimals(33.73), 2); assert.equal(decimals(9042), 0); assert.equal(decimals(0.0684), 4);
  assert.ok(holds("it paid 33.73 USD/MWh", 33.73) && holds("about 33.7", 33.73) && !holds("about 34", 33.73) && !holds("33.74", 33.73) && !holds("133.73", 33.73));
  assert.ok(holds("1,678 hours", 1678) && !holds("1,679 hours", 1678) && holds("382,842 MWh", 382842.084) && holds("61,763.2 square miles", 61763.2) && holds("61,763", 61763.2));
  assert.ok(holds("a discount of -14.66", 14.66) && holds("from 1998 to 2016", 1998) && holds("1998-2016", 2016) && !holds("19980", 1998));
  const q = SET.questions.find((x) => x.id === "p05"), cite = [{ table: "site/data/seller/capture.json" }];
  const good = { status: "answered", answer: `Solar captured ${q.expect[0]} USD/MWh at the West hub (site/data/seller/capture.json).`, series: [], citations: cite };
  assert.deepEqual(judge(q, good), []);
  assert.equal(judge(q, { ...good, answer: "Solar captured 99.99 USD/MWh." }).length, 1);
  assert.equal(judge(q, { ...good, citations: [{ table: "merchant_revenue_monthly" }] }).length, 1);       // the right number from another source is not this question's answer
  const c = SET.questions.find((x) => x.id === "p08"), rows = Array.from({ length: c.series_rows }, (_, i) => ({ key: i ? `H${i}` : c.series_has.key, value: i ? i : c.series_has.value }));
  const chart = { status: "answered", answer: "The capture price by hub.", citations: cite, series: [{ table: "site/data/seller/capture.json", rows, check: { same: true } }] };
  assert.deepEqual(judge(c, chart), []);
  assert.ok(judge(c, { ...chart, series: [{ ...chart.series[0], rows: rows.slice(1) }] }).length >= 1);
  const r = SET.questions.find((x) => x.kind === "refuse" && x.say === "held, not shown");
  // session 156: a refusal about another grid must also close in the tool's own name (its fields close and never); the
  // answer that passed here before closes with no such words, and now fails for that one reason
  const CLOSING_156 = " Ask ERCOT answers for the Texas grid, and for the other grids only what four pages of this site show: curtailment and free energy, what a datacenter pays, the capture price and the resource layers.";
  assert.deepEqual(judge(r, { status: "not_in_warehouse", answer: `ISO-NE's monthly figure is held, not shown: its terms restrict duplication.${CLOSING_156}`, series: [], citations: [] }), []);
  assert.equal(judge(r, { status: "not_in_warehouse", answer: "ISO-NE's monthly figure is held, not shown: its terms restrict duplication.", series: [], citations: [] }).length, 1);
  assert.equal(judge(r, { status: "not_in_warehouse", answer: `Another grid: see /grid/isone.${CLOSING_156}`, series: [], citations: [] }).length, 1);
  assert.equal(judge(r, { status: "answered", answer: `held, not shown.${CLOSING_156}`, series: [], citations: [] }).length, 1);
  // a question of the 100 carries none of the added fields: its verdict is the rule of its kind and nothing more
  assert.ok(OLD.questions.every((x) => !("expect" in x) && !("cite" in x) && !("series_has" in x) && !("must" in x) && !("series_rows" in x) && !("expect_all" in x)));
  assert.deepEqual(judge(OLD.questions.find((x) => x.id === "s01"), { status: "answered", answer: "It was 31.2 USD/MWh.", series: [], citations: [{ table: "ercot_hub_prices_daily" }] }), []);
});

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
