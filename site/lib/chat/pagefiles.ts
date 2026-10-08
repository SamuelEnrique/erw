// Energy Research Warehouse (ERW) site, session 153: Ask ERCOT reads what stands behind four pages built this week:
// "What a datacenter pays" (/cost-of-power), "Curtailment" with "Where free energy is" (/curtailment), "What a
// generator earns" (/cost-of-power/seller: the capture price) and "Where the resources are" (/resources).
//
// What each page shows comes from one of four kinds of source, and each kind is made readable in its own way:
//   (a) a public table already in the site's live set: it joins the tables the query tool reads (PAGES_TABLES below),
//       with its entry in the guide the model is given (pagesGuide);
//   (b) a public table that is not in the live set: none was needed, so nothing is loaded for this session;
//   (c) a file the site ships that no table holds (the capture prices, free energy, the shares and worth of
//       curtailment, the datacenter page's hourly prices, a resource layer): the tool page_file below reads THE SAME
//       FILE THE PAGE READS, through the page's own functions (lib/capture.ts, lib/freeenergy.ts, lib/curtailment.ts,
//       lib/datacenter.ts, lib/resources.ts), so a figure it returns is the page's figure and no second copy can drift;
//   (d) an internal table (HELD below): never read. The guide says so and the tools refuse it by name: "held, not
//       shown", with the publisher's own words as the reason and never a figure.
// MISO reads "paused while terms are reviewed" and PJM "licensed source needed": no figure of either is returned.
//
// The switch: ASK_PAGES=off on the server leaves the panel as session 148 left it (the tables not offered, the tool
// not offered, the guide not given). Unset, they are offered. lib/chat/spec_ercot.json, which warehouse/chat/ercot.py
// exports, is not touched. Nothing here reads the database and nothing here is read by a live page.
import "server-only";
import fs from "node:fs";
import path from "node:path";
import texasJson from "@/data/curtailment/ercot.json";
import freeJson from "@/data/curtailment/free_energy.json";
import sharesJson from "@/data/curtailment/shares.json";
import worthJson from "@/data/curtailment/worth.json";
import captureJson from "@/data/seller/capture.json";
import { counted, figure, twelve, years as captureYears, type CaptureFile, type Fuel, type Market, type Months } from "@/lib/capture";
import { periodShare, shareMarks, shareReason, yearShare, type SharesFile } from "@/lib/curtailment";
import { ASSUMED, badMonth, gpuHour, last36, lastTwelve, monthsOf, span, years as costYears, type Buy } from "@/lib/datacenter";
import { INDEX, yearFiles } from "@/lib/datacenterdata";
import { FACE, hasGap, hasPair, heatMonth, isHeld, ranked, type FreeFile, type NotHeld, type WindowName, type WorthMonth } from "@/lib/freeenergy";
import { PAGE_FILES, PAGE_FILE_HREF } from "./pagelinks";
import { decimalsOf, decodeGrid, filesOf, inGeometry, legendOf, pyramidsOf, valueAt, type Geometry, type GridFile, type Layer, type Manifest } from "@/lib/resources";

type Json = Record<string, unknown>;
const CAPTURE = captureJson as unknown as CaptureFile;
const FREE = freeJson as unknown as FreeFile;
const SHARES = sharesJson as unknown as SharesFile;
type WorthSide = { freq: string; tables: string[]; months?: Record<string, WorthMonth>; years?: Record<string, WorthMonth & { months?: number }>; window?: WorthMonth; missing?: unknown };
type WorthGrid = { name: string; whose: string; table: string; main_hub?: string; last_month?: string; missing?: string; months_missing?: string; hubs?: Record<string, Record<string, WorthSide>> };
const WORTH = worthJson as unknown as { built: string; threshold_usd_per_mwh: number; rules: Record<string, string>; grids: Record<string, WorthGrid>; not_held: Record<string, string> };
type TexasPart = { generation_mwh: number; hsl_mwh: number; below_hsl_mwh: number; above_hsl_mwh?: number; share_pct: number | null };
type TexasDay = { hours_held: number; hours_in_day: number; whole: boolean; wind: TexasPart; solar: TexasPart; both: TexasPart };
const TEXAS = texasJson as unknown as { built: string; first_day: string; last_day: string; whole_days: number; hours_held: number; window: { wind: TexasPart; solar: TexasPart; both: TexasPart };
  days: Record<string, TexasDay>; months: Record<string, { hours_held: number; hours_in_month: number; missing?: string }>; month_reason: string; history_reason: string };

export { PAGE_FILES, PAGE_FILE_HREF };

// ---------------------------------------------------------------------------------------------------------------------
// (a) the public tables of the live set that the four pages read, and the rows of each this panel reads. The
// curtailment tables are California's and SPP's as well as Texas's: the page is one tool for every grid, and so is
// what Ask reads of it. The tables the datacenter page borrows from other tools, and the two of its view "Grid by
// grid", are read for ERCOT alone.
// ---------------------------------------------------------------------------------------------------------------------

export const PAGES_FILTERS: Record<string, Record<string, string | string[]>> = {
  iso_curtailment_monthly: {},
  caiso_curtailment_daily: {},
  spp_curtailment_daily: {},
  ercot_wind_solar_hsl_daily: {},
  caiso_curtailment_profile: {},
  eia930_demand_growth: { entity: "eia930:ERCO" },
  interconnection_queue_summary: { entity: ["queue:ercot:all", "queue:ercot:solar", "queue:ercot:wind", "queue:ercot:battery", "queue:ercot:gas", "queue:ercot:other"] },
  ercot_large_load_status: {},
  // the view "Grid by grid" of /cost-of-power (cost_of_power_monthly is in the guide since session 92)
  cost_of_power_hourly_profile: { entity: "ercot:HB_HUBAVG" },
  cost_of_power_carbon: { entity: "ercot:HB_HUBAVG" },
};
export const PAGES_TABLES: string[] = Object.keys(PAGES_FILTERS);
/** What each holds, for a refusal that names one as the nearest thing held. */
export const PAGES_HOLDS: Record<string, string> = {
  iso_curtailment_monthly: "Wind and solar curtailment by month at CAISO and SPP since 2014, with the share of available output curtailed.",
  caiso_curtailment_daily: "CAISO's wind and solar curtailment by day (the newest 100 days on the site).",
  spp_curtailment_daily: "SPP's wind and solar curtailment by day (the newest 100 days on the site).",
  ercot_wind_solar_hsl_daily: "ERCOT wind and solar output below the limit the plants reported, by day: the ERW's estimate, from 19 September 2026.",
  caiso_curtailment_profile: "California's curtailment by month since 2019: by hour of the day, by CAISO's reason, and against battery charging.",
  eia930_demand_growth: "Demand growth since 2019: the average and the highest hour of each year.",
  interconnection_queue_summary: "The interconnection queue summed by technology and by the year a request entered: active, operating and withdrawn MW, and the median years to operation.",
  ercot_large_load_status: "ERCOT's large load status reports: the MW approved to energize and observed running.",
  cost_of_power_hourly_profile: "The average real-time price at the hub by hour of the day, for each of the last thirteen months.",
  cost_of_power_carbon: "The load-weighted real-time price beside the carbon intensity of generation and of demand, by month.",
  [PAGE_FILES.cost]: "What a flat load paid for energy at each hub and zone the page holds, by month and year (the datacenter page's own file).",
  [PAGE_FILES.capture]: "The capture price of solar and wind at every public hub and zone, by month (the seller page's own file).",
  [PAGE_FILES.shares]: "The share of available wind and solar output curtailed, every month, at CAISO and SPP (the curtailment page's own file).",
  [PAGE_FILES.texas]: "Texas wind and solar output below the reported limit, the days held since 28 September 2026 (the ERW's estimate).",
  [PAGE_FILES.free]: "Where free energy is: the hours priced below zero and under USD 5 per MWh at each hub and zone, the last month and the last twelve.",
  [PAGE_FILES.worth]: "What curtailed energy was worth at the hub's price, by month (California) and over the hours held (Texas).",
  [PAGE_FILES.resources]: "The natural resource layers of the map: wind, solar, geothermal, oil and gas basins and plays, biomass, offshore wind leases.",
};
/** Every name a refusal may give as nearest, beyond the guide's own. */
export const PAGES_NEAR: string[] = [...PAGES_TABLES, ...Object.values(PAGE_FILES)];

/** Whether the panel offers the four pages' sources: always, unless the server says ASK_PAGES=off. */
export function pagesOffered(env: string | undefined = process.env.ASK_PAGES): boolean {
  return env !== "off";
}

// ---------------------------------------------------------------------------------------------------------------------
// (d) held, not shown. Each reason is the publisher's own sentence, as the page's Method note quotes it.
// ---------------------------------------------------------------------------------------------------------------------

export const HELD_WORDS = "held, not shown";
export const PAUSED_WORDS: Record<string, string> = { miso: "paused while terms are reviewed", pjm: "licensed source needed" };
export type Held = { table: string; what: string; names: RegExp; reason: string; nearest: string; say: string };
const ISONE_NOTICE = 'ISO-NE\'s legal notice says: "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws."';
const NYISO_NOTICE = 'NYISO\'s legal notice says: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety."';
const PUCT_NOTICE = 'The Public Utility Commission of Texas\'s link policy says: "all PUCT content is protected by federal copyright laws" and "Site owners should contact the PUCT to request permission to use or copy content from the PUCT\'s website."';
export const HELD: Held[] = [
  { table: "isone_zone_prices_history", what: "ISO-NE's load zone prices, the history from 2019 to August 2026", names: /isone_zone_prices_history|zone_prices_history_isone/i,
    reason: `${ISONE_NOTICE} The owner ruled on 7 October 2026 that they stay internal.`, nearest: PAGE_FILES.cost,
    say: "What is held and shown of ISO-NE: its internal hub since September 2024 and each load zone since 26 August 2026, from its public reports." },
  { table: "isone_ddg_undelivered_monthly", what: "ISO-NE's monthly undelivered energy of its dispatchable wind and solar plants (its curtailment figure)", names: /isone_ddg_undelivered_monthly|ddg_undelivered/i,
    reason: `${ISONE_NOTICE} The owner ruled on 7 October 2026: pulled and held internal, not shown.`, nearest: "iso_curtailment_monthly",
    say: "No curtailment figure of ISO-NE is shown. Curtailment is shown for CAISO and SPP, and as the ERW's estimate for Texas." },
  { table: "isone_zone_load_hourly", what: "ISO-NE's hourly demand by zone", names: /isone_zone_load_hourly/i,
    reason: ISONE_NOTICE, nearest: PAGE_FILES.cost, say: "No demand by zone of ISO-NE is shown." },
  { table: "nyiso_load_queue", what: "New York's load in line (NYISO's load interconnection requests)", names: /nyiso_load_queue/i,
    reason: `${NYISO_NOTICE} The owner ruled on 7 October 2026 that the rows are shown only if NYISO's terms allow it; by their words they do not.`, nearest: PAGE_FILES.cost,
    say: "No megawatt, request or zone of New York's load in line is shown." },
  { table: "texas_transmission_matrix", what: "the Public Utility Commission of Texas's transmission charge matrices (the wholesale transmission rate for all of ERCOT)", names: /texas_transmission_matrix/i,
    reason: `The table is held internal. ${PUCT_NOTICE}`, nearest: PAGE_FILES.cost,
    say: "Ask reads no figure of it. The page /cost-of-power prints each figure as the filing prints it, with its docket and page; the 2026 matrices are filed, not approved (the docket was remanded and has no signed order)." },
  { table: "texas_delivery_charges", what: "the delivery and transmission charges of the four large Texas wires utilities' tariffs", names: /texas_delivery_charges/i,
    reason: "The table is held internal: each figure was read from a tariff by a model and is kept with the line it was read from.", nearest: PAGE_FILES.cost,
    say: "Ask reads no figure of it. The page /cost-of-power prints each charge as its tariff prints it, with its document, page and date; no total delivery cost is given there either." },
];
/** The refusal of a held table, as a tool result the model reads: its name, the words, the reason, and no figure. */
export function heldRefusal(h: Held): Json {
  return { error: `${h.table} is ${HELD_WORDS}: ${h.what}. ${h.reason} ${h.say} State no figure of it. Answer with not_in_warehouse true, say that it is "${HELD_WORDS}" and why, and name ${h.nearest} in nearest.`, held_not_shown: h.table };
}
/** The held table a tool call names, if any: a query, a description or a comparison of one, by its name. */
export function heldIn(input: unknown): Held | null {
  const names: string[] = [];
  const walk = (v: unknown): void => {
    if (typeof v === "string") names.push(v);
    else if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === "object") Object.values(v as Json).forEach(walk);
  };
  walk(input);
  return HELD.find((h) => names.some((n) => h.names.test(n))) ?? null;
}
const paused = (grid: string, table: string): Json | null => (PAUSED_WORDS[grid]
  ? { table, grid: grid.toUpperCase(), words: PAUSED_WORDS[grid], note: `No figure of ${grid.toUpperCase()} is shown on this site: ${PAUSED_WORDS[grid]}. Answer with not_in_warehouse true and these words, and state no figure.`, tier: "site file", license: "public" }
  : null);

// ---------------------------------------------------------------------------------------------------------------------
// (c) the tool that reads the pages' own files
// ---------------------------------------------------------------------------------------------------------------------

export const PAGE_FILE_VIEWS = ["cost", "regions", "demand", "capture", "hubs", "share", "free_energy", "worth", "layers", "layer", "value_at", "features"] as const;
export const PAGE_FILE_TOOL = {
  name: "page_file",
  description: "Reads the files behind four pages of this site, the same files the pages read, through the pages' own functions: a figure it returns is the figure the page shows. Every grid these pages show is read (ERCOT, CAISO, NYISO, ISO-NE, SPP); MISO and PJM return their words and no figure. Views: " +
    "\"cost\" (/cost-of-power: what a flat load paid for energy at a hub or zone: the last twelve months, a bad month, power per GPU-hour, and each year or month in result; give grid, and place and market when named), " +
    "\"regions\" (/cost-of-power: every hub and zone of a grid, a flat load, the last twelve months), " +
    "\"demand\" (/cost-of-power, will the power be there: the hours a grid was tight in each year, its highest hour, and demand by region), " +
    "\"capture\" (/cost-of-power/seller: the capture price of solar or wind at a hub: the last twelve months against the flat average, and each year or month in result; give grid, fuel, and place and market when named), " +
    "\"hubs\" (/cost-of-power/seller: the capture price at every hub and zone of a grid, the last twelve months), " +
    "\"share\" (/curtailment: the share of available wind and solar output curtailed: CAISO and SPP by month or year; ERCOT the days held of the ERW's estimate), " +
    "\"free_energy\" (/curtailment: the hours priced below zero and under USD 5 per MWh at each hub and zone of a grid, window \"year\" for the last twelve months or \"month\" for the last month; with place, that place's hours by month), " +
    "\"worth\" (/curtailment: what curtailed energy was worth at a hub's price: CAISO by month or year, ERCOT over the hours held), " +
    "\"layers\" (/resources: every natural resource layer with its unit, publisher, vintage and range), \"layer\" (one layer in full, with what it is not), " +
    "\"value_at\" (the value of a layer at a longitude and latitude), \"features\" (the shapes or sites of a layer by name: basins, plays, counties, lease areas, hydrothermal systems). " +
    "A result with rows in result can be named in series for a chart or table.",
  input_schema: {
    type: "object" as const, additionalProperties: false,
    properties: {
      view: { type: "string", enum: [...PAGE_FILE_VIEWS] },
      grid: { type: "string", description: "ercot, caiso, nyiso, isone or spp" },
      place: { type: "string", description: "a hub or zone as the operator names it: HB_WEST, LZ_NORTH, HB_HUBAVG, TH_SP15_GEN-APND, N.Y.C., .H.INTERNAL_HUB, SPPNORTH_HUB" },
      market: { type: "string", enum: ["rt", "da"], description: "rt real time (the default where it is held), da day-ahead" },
      fuel: { type: "string", enum: ["solar", "wind"] },
      period: { type: "string", description: "a year (2025) or a month (2026-09)" },
      by: { type: "string", enum: ["year", "month"], description: "the rows of result: by year (the default) or by month" },
      window: { type: "string", enum: ["year", "month"], description: "free_energy: the last twelve months (year) or the last month" },
      layer: { type: "string", description: "a resource layer's id, from view layers" },
      lon: { type: "number" }, lat: { type: "number" },
      name: { type: "string", description: "features: words of a feature's name (Permian, Barnett, Potter, TX)" },
    },
    required: ["view"],
  },
};

const r2 = (v: number) => Math.round(v * 100) / 100;
const r1 = (v: number) => Math.round(v * 10) / 10;
const r0 = (v: number) => Math.round(v);
const base = (table: string, built: string, source: string): Json => ({ table, tier: "site file", license: "public", data_version: `built ${built}`, source_report: source });
const fail = (error: string): Json => ({ error });
const GRIDS = ["ercot", "caiso", "nyiso", "isone", "spp"];
const gridOf = (a: Json): string => String(a.grid ?? "ercot").toLowerCase().replace(/[^a-z]/g, "").replace(/^isonewengland$|^newengland$/, "isone").replace(/^california$/, "caiso").replace(/^texas$/, "ercot").replace(/^newyork$/, "nyiso");
const marketName = (m: string) => (m === "da" ? "day-ahead" : "real time");

// ---- /cost-of-power -------------------------------------------------------------------------------------------------

const FLAT = { run: "flat" as const, n: 0, pct: 0, shift: 0 };
const COST_NOT = "Wholesale energy only, at a hub or zone price: no delivery, transmission, demand or retail charge is in it. A hub or zone is an average over many points, not a site. A flat load draws its size in every hour; the flexible loads of the page are computed there from the reader's own inputs and are not read here. A month counts when at least 95 percent of its hours are held, and nothing is filled.";

/** A grid's yearly files of hourly prices, read by the page's own reader (lib/datacenterdata.ts, yearFiles). The folder
 * is written out here so that the server's file trace of the ask route holds it (the page's own route names it in
 * next.config.ts); a year the index names whose file is not on the server is said, and no figure is given. */
function pricesOf(grid: string) {
  for (const y of INDEX.grids[grid]?.years ?? []) {
    if (!fs.existsSync(path.join(process.cwd(), "data", "datacenter", `${grid}_${y}.json`))) throw new Error(`the year ${y} of ${grid}'s hourly prices is not on the server`);
  }
  return yearFiles(grid);
}
function costMonths(grid: string, region: string, market: Buy) {
  const ms = monthsOf(pricesOf(grid), region, market, FLAT);
  const l12 = lastTwelve(ms);
  return { ms, l12, s12: l12 ? span(l12) : null };
}
function cost(a: Json): Json {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.cost);
  if (words) return words;
  const g = INDEX.grids[grid];
  if (!g) return fail(`no grid ${JSON.stringify(a.grid)} on /cost-of-power; grids: ${Object.keys(INDEX.grids).join(", ")}`);
  const region = a.place === undefined ? g.regions.find((r) => r.id === g.main) : g.regions.find((r) => r.id.toLowerCase() === String(a.place).toLowerCase());
  if (!region) return fail(`no hub or zone ${JSON.stringify(a.place)} in ${g.name} on /cost-of-power; held: ${g.regions.map((r) => r.id).join(", ")}`);
  // the page's own rule: real time unless the address names day-ahead; day-ahead when real time holds no twelve complete months and day-ahead does
  let market: Buy = a.market === "da" ? "da" : "rt";
  if (!region[market]) { if (a.market !== undefined) return fail(`no ${marketName(market)} price is held for ${region.id}; held: ${(["rt", "da"] as const).filter((m) => region[m]).map(marketName).join(", ")}`); market = market === "rt" ? "da" : "rt"; }
  let c = costMonths(grid, region.id, market);
  if (a.market === undefined && market === "rt" && !c.l12 && region.da) { const d = costMonths(grid, region.id, "da"); if (d.l12) { market = "da"; c = d; } }
  const side = region[market]!;
  const ys = costYears(c.ms);
  const w36 = last36(c.ms), bad = badMonth(w36?.months ?? []);
  const byMonth = a.by === "month";
  const period = typeof a.period === "string" ? a.period : null;
  const rows = byMonth
    ? c.ms.filter((r) => r.complete && (!period || r.m.startsWith(period.slice(0, 4)))).map((r) => ({ month: r.m, value: r2(r.flat / r.held), hours_held: r.held, hours_in_month: r.due }))
    : ys.filter((r) => r.flat !== null).map((r) => ({ year: r.y, value: r2(r.flat as number), months_counted: r.months, whole_year: r.complete }));
  const out: Json = {
    ...base(PAGE_FILES.cost, INDEX.built, `What a datacenter pays (docs/methods/datacenter_cost.md): hourly prices of ${side.tables.join(", ")}`),
    page: "/cost-of-power", grid: g.name, place: region.id, place_kind: region.kind ?? (/hub/i.test(region.id) ? "hub" : "zone"), market: marketName(market), load: "a flat load, per MW", prices_held: { from: side.first.slice(0, 10), to: side.last.slice(0, 10) },
    last_twelve_months: c.l12 && c.s12 && c.s12.flat !== null
      ? { from: c.l12[0].m, to: c.l12[11].m, usd_per_mwh: r2(c.s12.flat), usd_per_mw: r0(c.s12.flatCost), mwh_per_mw: r0(c.s12.energy),
        power_per_gpu_hour_usd: Math.round(gpuHour(c.s12.flat, ASSUMED.gpu.value, ASSUMED.pue.value) * 10000) / 10000, gpu_assumptions: `${ASSUMED.gpu.value} kW per GPU and an overhead ratio of ${ASSUMED.pue.value}, the page's stated defaults` }
      : { not_held: `twelve complete months of ${marketName(market)} prices are not held for ${region.id}: it is held from ${side.first.slice(0, 10)}` },
    bad_month: bad && bad.energy ? { month: bad.m, usd_per_mwh: r2(bad.cost / bad.energy), what: `the worst tenth of the ${w36!.months.length} complete months from ${w36!.months[0].m} to ${w36!.to}: one month in ten cost this or more` } : null,
    is_not: COST_NOT,
  };
  if (period && period.length === 4 && !byMonth) { const y = ys.find((r) => r.y === period); out.year = y && y.flat !== null ? { year: y.y, usd_per_mwh: r2(y.flat), months_counted: y.months, whole_year: y.complete } : { year: period, not_held: `no counted month of ${period} is held for ${region.id}` }; }
  if (period && period.length === 7) { const m = c.ms.find((r) => r.m === period); out.month = m ? { month: m.m, usd_per_mwh: r2(m.flat / m.held), hours_held: m.held, hours_in_month: m.due, counted: m.complete } : { month: period, not_held: `no hour of ${period} is held for ${region.id}` }; }
  return { ...out, title: `A flat load at ${region.id}, ${g.name}, ${marketName(market)}, USD per MWh, by ${byMonth ? "month" : "year"}`, group_by: byMonth ? "month" : "year", units: ["USD/MWh"], result: rows, rows_matched: rows.length,
    result_note: byMonth ? "each row is a month counted (at least 95 percent of its hours held): the mean of its hourly prices" : "each row is a calendar year from its counted months; a year with whole_year false holds only months_counted months" };
}
function regions(a: Json): Json {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.cost);
  if (words) return words;
  const g = INDEX.grids[grid];
  if (!g) return fail(`no grid ${JSON.stringify(a.grid)} on /cost-of-power; grids: ${Object.keys(INDEX.grids).join(", ")}`);
  const market: Buy = a.market === "da" ? "da" : "rt";
  const rows: Json[] = [], notHeld: Json[] = [];
  for (const r of g.regions) {
    const c = r[market] ? costMonths(grid, r.id, market) : null;
    if (c?.l12 && c.s12 && c.s12.flat !== null) rows.push({ place: r.id, value: r2(c.s12.flat), from: c.l12[0].m, to: c.l12[11].m, kind: r.kind ?? "" });
    else notHeld.push({ place: r.id, why: r[market] ? `held from ${r[market]!.first.slice(0, 10)}: not yet twelve complete months` : `no ${marketName(market)} price is held` });
  }
  return { ...base(PAGE_FILES.cost, INDEX.built, "What a datacenter pays (docs/methods/datacenter_cost.md): every region of the grid, a flat load"), page: "/cost-of-power", grid: g.name, market: marketName(market), load: "a flat load, per MW",
    title: `A flat load at every hub and zone of ${g.name}, ${marketName(market)}, the last twelve months, USD per MWh`, group_by: "place", units: ["USD/MWh"], result: rows, rows_matched: rows.length, not_held: notHeld,
    result_note: "each place over its own last twelve complete months (from and to); places with fewer are under not_held", is_not: COST_NOT };
}

const DEMAND_NOT = "An hour is counted tight when the grid's demand was at or above 95 percent of that year's highest hour: a count of hours near the year's own peak, not a measure of scarcity, of reserves or of any emergency. It is the operator's own hourly demand; a year is whole when at least 95 percent of its hours are held, and the year now running is not. Demand by region is the operator's own zones or areas, which are not the price hubs and zones.";
function demand(a: Json): Json {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.cost);
  if (words) return words;
  const g = INDEX.grids[grid];
  if (!g) return fail(`no grid ${JSON.stringify(a.grid)} on /cost-of-power; grids: ${Object.keys(INDEX.grids).join(", ")}`);
  if (g.demand_source?.startsWith("withheld:")) return heldRefusal(HELD.find((h) => h.table === "isone_zone_load_hourly")!);
  const head = { ...base(PAGE_FILES.cost, INDEX.built, `What a datacenter pays, will the power be there (docs/methods/datacenter_cost.md): ${g.demand_source ?? "no hourly demand of the operator is held"}`), page: `/cost-of-power?grid=${grid}#there`, grid: g.name, is_not: DEMAND_NOT };
  const ys = Object.entries(g.demand ?? {}).filter(([, d]) => d.tight_hours !== undefined).sort(([x], [y]) => x.localeCompare(y));
  if (!ys.length) return { ...head, not_held: `the operator's own hourly demand is not held for ${g.name}, so its tight hours are not counted` };
  const rows = ys.map(([y, d]) => ({ year: y, value: d.tight_hours as number, highest_hour_mw: d.peak_mw === undefined ? null : r0(d.peak_mw), mean_mw: d.mean_mw === undefined ? null : r0(d.mean_mw), hours_held: d.hours_held, whole_year: d.whole === true }));
  const zones = Object.entries(g.zones ?? {}).flatMap(([z, by]) => {
    const whole = Object.keys(by).filter((y) => by[y].hours_held >= 0.95 * by[y].hours_due && by[y].hours_due >= 8760).sort();   // the page's own rule (ZoneCell)
    const first = whole[0], last = whole.at(-1);
    return first && last && first !== last ? [{ region: z, first_whole_year: first, mean_mw_then: r0(by[first].mean_mw), newest_whole_year: last, mean_mw_now: r0(by[last].mean_mw), highest_hour_mw_now: r0(by[last].peak_mw), change_pct: r2((100 * (by[last].mean_mw - by[first].mean_mw)) / by[first].mean_mw) }] : [];
  });
  return { ...head, tight_means: `demand at or above ${Math.round(INDEX.tight * 100)} percent of the year's highest hour, in ${g.std_name}`, demand_by_region: zones.length ? zones : { not_held: `hourly demand by region is not held for ${g.name}, or no region holds two whole years` },
    title: `${g.name}: hours the grid was tight, by year`, group_by: "year", units: ["hours"], result: rows, rows_matched: rows.length,
    result_note: "value is the year's hours within 5 percent of its own highest hour; a year with whole_year false is not whole (the year now running)" };
}

// ---- /cost-of-power/seller: the capture price -----------------------------------------------------------------------

const CAPTURE_NOT = "It is the fleet's shape, not a site's: the price of each hour is weighed by the whole grid's solar or wind generation of that hour, so a single plant's resource, curtailment, congestion and node price are not in it. It is a price at a hub or zone, not what a plant with a contract earns, and no cost is taken off. The page's hybrid figure \"Combined\" is two revenues added (a solar plant's and a battery's, each priced as if it stood alone) and is not read here.";
function captureSide(a: Json): { error: Json } | { grid: string; name: string; hub: string; market: Market; fuel: Fuel; months: Months | undefined; tables: string[]; first: string; last: string } {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.capture);
  if (words) return { error: words };
  const g = CAPTURE.grids[grid];
  if (!g) return { error: fail(`no grid ${JSON.stringify(a.grid)} on /cost-of-power/seller; grids: ${Object.keys(CAPTURE.grids).join(", ")}`) };
  const hub = a.place === undefined ? g.hubs.find((h) => h.id === g.main) : g.hubs.find((h) => h.id.toLowerCase() === String(a.place).toLowerCase());
  if (!hub) return { error: fail(`no hub or zone ${JSON.stringify(a.place)} in ${g.name} on /cost-of-power/seller; held: ${g.hubs.map((h) => h.id).join(", ")}`) };
  if (a.fuel !== "solar" && a.fuel !== "wind") return { error: fail('fuel must be "solar" or "wind": the capture price is held for those two') };
  let market: Market = a.market === "da" ? "da" : "rt";
  if (!hub[market]) { if (a.market !== undefined) return { error: fail(`no ${marketName(market)} price is held for ${hub.id}`) }; market = market === "rt" ? "da" : "rt"; }
  const side = hub[market]!;
  return { grid, name: g.name, hub: hub.id, market, fuel: a.fuel, months: side[a.fuel], tables: side.tables, first: side.first, last: side.last };
}
const figureOf = (f: { price: number; flat: number; premium: number; pct: number | null; hours: number }) => ({ capture_price_usd_per_mwh: r2(f.price), flat_average_usd_per_mwh: r2(f.flat), premium_usd_per_mwh: r2(f.premium), premium_pct_of_flat: f.pct === null ? null : r1(f.pct), hours: f.hours });
function capture(a: Json): Json {
  const s = captureSide(a);
  if ("error" in s) return s.error;
  const t = twelve(s.months, CAPTURE.near);
  const ys = captureYears(s.months, CAPTURE.near);
  const byMonth = a.by === "month", period = typeof a.period === "string" ? a.period : null;
  const months = s.months ?? {};
  const rows = byMonth
    ? Object.keys(months).sort().filter((m) => counted(months[m], CAPTURE.near) && (!period || m.startsWith(period.slice(0, 4)))).flatMap((m) => { const f = figure([months[m]]); return f ? [{ month: m, value: r2(f.price), flat_average: r2(f.flat), premium: r2(f.premium) }] : []; })
    : ys.flatMap((y) => (y.f ? [{ year: y.y, value: r2(y.f.price), flat_average: r2(y.f.flat), premium: r2(y.f.premium), months_counted: y.months, whole_year: y.whole }] : []));
  const out: Json = {
    ...base(PAGE_FILES.capture, CAPTURE.built, `What a generator earns, the capture price (docs/methods/cost_of_power.md): prices of ${s.tables.join(", ")}, weighed by the grid's hourly ${s.fuel} generation`),
    page: "/cost-of-power/seller", grid: s.name, place: s.hub, market: marketName(s.market), fuel: s.fuel, prices_held: { from: s.first.slice(0, 10), to: s.last.slice(0, 10) },
    what: "generation-weighted price: the sum of price times the grid's generation over the sum of the generation; the flat average is the mean price of the same hours; the premium is the first less the second (below zero: a discount)",
    last_twelve_months: t ? { from: t.from, to: t.to, ...figureOf(t) } : { not_held: "no twelve consecutive counted months are held for this hub, market and fuel" },
    is_not: CAPTURE_NOT,
  };
  if (period && period.length === 4 && !byMonth) { const y = ys.find((r) => r.y === period); out.year = y?.f ? { year: y.y, ...figureOf(y.f), months_counted: y.months, whole_year: y.whole } : { year: period, not_held: `no counted month of ${period} is held` }; }
  if (period && period.length === 7) { const f = months[period] && counted(months[period], CAPTURE.near) ? figure([months[period]]) : null; out.month = f ? { month: period, ...figureOf(f) } : { month: period, not_held: "the month is not counted: under 95 percent of its hours hold both a price and the generation" }; }
  return { ...out, title: `The capture price of ${s.fuel} at ${s.hub}, ${s.name}, ${marketName(s.market)}, USD per MWh, by ${byMonth ? "month" : "year"}`, group_by: byMonth ? "month" : "year", units: ["USD/MWh"], result: rows, rows_matched: rows.length,
    result_note: "value is the generation-weighted price; flat_average is the mean price of the same hours; a year with whole_year false holds only months_counted months" };
}
function hubs(a: Json): Json {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.capture);
  if (words) return words;
  const g = CAPTURE.grids[grid];
  if (!g) return fail(`no grid ${JSON.stringify(a.grid)} on /cost-of-power/seller; grids: ${Object.keys(CAPTURE.grids).join(", ")}`);
  if (a.fuel !== "solar" && a.fuel !== "wind") return fail('fuel must be "solar" or "wind"');
  const market: Market = a.market === "da" ? "da" : "rt", fuel = a.fuel as Fuel;
  const rows: Json[] = [], notHeld: string[] = [];
  for (const h of g.hubs) {
    const t = twelve(h[market]?.[fuel], CAPTURE.near);
    if (t) rows.push({ place: h.id, value: r2(t.price), flat_average: r2(t.flat), premium: r2(t.premium), premium_pct_of_flat: t.pct === null ? null : r1(t.pct), from: t.from, to: t.to });
    else notHeld.push(h.id);
  }
  return { ...base(PAGE_FILES.capture, CAPTURE.built, "What a generator earns, the capture price (docs/methods/cost_of_power.md): every hub and zone of the grid"), page: "/cost-of-power/seller", grid: g.name, market: marketName(market), fuel,
    title: `The capture price of ${fuel} at every hub and zone of ${g.name}, ${marketName(market)}, the last twelve months, USD per MWh`, group_by: "place", units: ["USD/MWh"], result: rows, rows_matched: rows.length,
    no_last_twelve_months: notHeld, result_note: "value is the generation-weighted price over each place's own last twelve counted months; premium is value less flat_average", is_not: CAPTURE_NOT };
}

// ---- /curtailment ---------------------------------------------------------------------------------------------------

const SHARE_NOT = "The grids' figures do not mean the same thing and are never added up. CAISO's and SPP's are the operators' own curtailment figures; ERCOT publishes none, and Texas's figure is the ERW's estimate (output below the limit the plants reported), which includes anything that keeps output under the limit and begins on 28 September 2026. CAISO's shares of 2026 rest on its Today's Outlook output, which shows more output than its Daily Renewable Report, so a share on the report's output would be higher. SPP's denominator is EIA's hourly output, built by the ERW. The data does not say where a curtailment happened.";
function share(a: Json): Json {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.shares);
  if (words) return words;
  if (grid === "isone") return heldRefusal(HELD.find((h) => h.table === "isone_ddg_undelivered_monthly")!);
  if (grid === "nyiso") return { table: PAGE_FILES.shares, grid: "NYISO", words: "not in the ERW", note: `${FACE.nyiso.line} State no figure.`, tier: "site file", license: "public" };
  const period = typeof a.period === "string" ? a.period : null;
  if (grid === "ercot") {
    const days = Object.keys(TEXAS.days).sort().filter((d) => TEXAS.days[d].whole && TEXAS.days[d].both.share_pct !== null);
    const rows = days.map((d) => ({ day: d, value: r2(TEXAS.days[d].both.share_pct as number), below_limit_mwh: r0(TEXAS.days[d].both.below_hsl_mwh), wind_pct: TEXAS.days[d].wind.share_pct, solar_pct: TEXAS.days[d].solar.share_pct }));
    const w = TEXAS.window;
    return { ...base(PAGE_FILES.texas, TEXAS.built, "Curtailment, Texas (docs/methods/curtailment.md): ERCOT's hourly wind and solar output and High Sustained Limit, ercot_wind_solar_hsl_hourly"), page: "/curtailment?grid=ercot", grid: "ERCOT",
      whose: FACE.ercot.line, days_held: { whole_days: TEXAS.whole_days, from: TEXAS.first_day, to: TEXAS.last_day },
      over_the_days_held: { below_limit_mwh: r0(w.both.below_hsl_mwh), share_of_limit_pct: w.both.share_pct, wind_below_limit_mwh: r0(w.wind.below_hsl_mwh), wind_share_pct: w.wind.share_pct, solar_below_limit_mwh: r0(w.solar.below_hsl_mwh), solar_share_pct: w.solar.share_pct },
      a_whole_month: { not_held: TEXAS.month_reason }, before_the_first_day: { not_held: TEXAS.history_reason },
      title: "Texas wind and solar output below the reported limit, percent of the limit, by day", group_by: "day", units: ["percent"], result: rows, rows_matched: rows.length,
      result_note: "each row is a whole Central day: output below the High Sustained Limit over the limit, wind and solar together; an estimate, not a curtailment figure of ERCOT's", is_not: SHARE_NOT };
  }
  const sg = SHARES.grids[grid];
  if (!sg) return fail(`no share of curtailment is held for ${JSON.stringify(a.grid)}; grids: caiso, spp, ercot`);
  const marks = shareMarks(sg);
  const month = (m: string) => { const r = sg.months[m]; return { month: m, share_pct: r2(r.share_pct), curtailed_mwh: r0(r.curtailed_mwh), wind_and_solar_output_mwh: r0(r.output_mwh), days_held: r.days_held, days_in_month: r.days_in_month, output_from: SHARES.basis_words[r.basis] ?? r.basis }; };
  const yearsHeld = [...new Set(Object.keys(sg.months).map((m) => m.slice(0, 4)))].sort();
  const byMonth = a.by === "month" || (period !== null && a.by !== "year");
  const rows = byMonth
    ? Object.keys(sg.months).sort().filter((m) => !period || m.startsWith(period.slice(0, 4))).map((m) => ({ month: m, value: r2(sg.months[m].share_pct), curtailed_mwh: r0(sg.months[m].curtailed_mwh) }))
    : yearsHeld.flatMap((y) => { const s = yearShare(sg, y); return s ? [{ year: y, value: r2(s.share), curtailed_mwh: r0(s.curtailed), months_with_a_share: s.months }] : []; });
  const out: Json = { ...base(PAGE_FILES.shares, SHARES.built, `Curtailment, the share of available output (docs/methods/curtailment.md): ${SHARES.definitions[grid] ?? SHARES.definition}`), page: `/curtailment${grid === "caiso" ? "" : `?grid=${grid}`}`, grid: grid.toUpperCase(),
    whose: FACE[grid]?.line ?? "", definition: SHARES.definition, months_with_a_share: sg.months_with_share,
    newest_month: marks ? month(marks.last) : null, highest_month: marks ? month(marks.highest) : null, is_not: SHARE_NOT };
  if (period) {
    const p = periodShare(sg, period);
    out.period = p ? (period.length === 7 ? month(period) : { year: period, share_pct: r2(p.share), curtailed_mwh: r0(p.curtailed), months_with_a_share: p.months, what: "the year's curtailed MWh over its curtailed plus output MWh, over its months that have a share" })
      : { period, not_held: period.length === 7 ? shareReason(sg, period) : `no month of ${period} has a share` };
  }
  if (sg.not_covered) out.not_covered = sg.not_covered;
  return { ...out, title: `${grid.toUpperCase()}: the share of available wind and solar output curtailed, percent, by ${byMonth ? "month" : "year"}`, group_by: byMonth ? "month" : "year", units: ["percent"], result: rows, rows_matched: rows.length,
    result_note: byMonth ? "each row is a month with a share" : "each row is a year from its months that have a share (months_with_a_share): the newest year is partial" };
}

const FREE_NOT = "These are counts of hours by price at a hub or zone, not energy that can be had for nothing: a negative or near-zero wholesale price is not a retail price, and delivery, demand and other charges are not in it. A hub or zone is an average over many points, not a site, and the data does not say where power was curtailed. An hour is real time where the place holds it for 95 percent of the window, otherwise day-ahead (basis says which). Under USD 5 includes the hours below zero, each hour once.";
function freeEnergy(a: Json): Json {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.free);
  if (words) return words;
  const g = FREE.grids[grid];
  if (!g) return fail(`no grid ${JSON.stringify(a.grid)} in "Where free energy is"; grids: ${Object.keys(FREE.grids).join(", ")}`);
  const w: WindowName = a.window === "month" ? "month" : "year";
  const windowWords = w === "year" ? `the twelve months ${FREE.year_months[0]} to ${FREE.end_month}` : `the month ${FREE.end_month}`;
  const head = { ...base(PAGE_FILES.free, FREE.built, "Curtailment, where free energy is (docs/methods/curtailment.md): the public hub and zone prices the ERW holds"), page: `/curtailment?grid=${grid}#free-energy`, grid: g.name, window: windowWords, threshold_usd_per_mwh: FREE.threshold_usd_per_mwh, is_not: FREE_NOT };
  if (a.place !== undefined) {
    const l = g.locations.find((x) => x.id.toLowerCase() === String(a.place).toLowerCase());
    if (!l) return fail(`no hub or zone ${JSON.stringify(a.place)} in ${g.name}; held: ${g.locations.map((x) => x.id).join(", ")}`);
    const win = l[w];
    const rows = FREE.year_months.map((m, i) => ({ month: m, value: heatMonth(l.heat, "under5", i), below_zero: heatMonth(l.heat, "negative", i), hours_held: heatMonth(l.heat, "held", i) }));
    return { ...head, place: l.id, place_kind: l.kind,
      in_the_window: isHeld(win) ? { hours_under_usd_5: win.under5, hours_below_zero: win.negative, mean_price_usd_per_mwh: r2(win.mean), hours_held: win.hours_held, hours_in_window: win.hours_in_window, basis: marketName(win.basis) } : { not_held: (win as NotHeld).missing },
      title: `${l.id}, ${g.name}: hours priced under USD ${FREE.threshold_usd_per_mwh} per MWh, by month, ${marketName(l.heat.basis)}`, group_by: "month", units: ["hours"], result: rows, rows_matched: rows.length,
      result_note: "each row is a month of the last twelve: value is its hours under the threshold (the hours below zero among them), of hours_held" };
  }
  const rows = ranked(g, w).map((l) => ({ place: l.id, value: l.win.under5, below_zero: l.win.negative, mean_price: r2(l.win.mean), hours_held: l.win.hours_held, basis: marketName(l.win.basis), kind: l.kind }));
  const gap = g.gap[w];
  const pairs = Object.values(FREE.compare).filter((c) => c.grid === grid).flatMap((c) => (["zone", "hub"] as const).flatMap((k) => { const p = c[k]?.[w]; return p && hasPair(p) ? [{ what: c.words, a: c[k]!.a, b: c[k]!.b, hours: p.hours_common, basis: marketName(p.basis), a_mean_price: p.a.mean, b_mean_price: p.b.mean, a_hours_under_usd_5: p.a.under5, b_hours_under_usd_5: p.b.under5, mean_b_less_a: p.mean_b_less_a }] : []; }));
  return { ...head, title: `${g.name}: hours priced under USD ${FREE.threshold_usd_per_mwh} per MWh at each hub and zone, ${windowWords}`, group_by: "place", units: ["hours"], result: rows, rows_matched: rows.length,
    cheapest_against_dearest: hasGap(gap) ? { cheapest: gap.cheapest.id, cheapest_mean_price: gap.cheapest.mean, dearest: gap.dearest.id, dearest_mean_price: gap.dearest.mean, gap_usd_per_mwh: gap.gap, hours: gap.hours_common, basis: marketName(gap.basis) } : { not_held: (gap as { missing: string }).missing },
    pairs, not_held: g.locations.filter((l) => !isHeld(l[w])).map((l) => ({ place: l.id, why: (l[w] as NotHeld).missing })),
    result_note: "places in order of their hours under the threshold; value includes the hours below zero (below_zero); an average of hubs is not a place and is left out" };
}

const WORTH_NOT = "The value is each hour's curtailed MWh times the hub's price of that hour: what the energy would have fetched at the hub, not a loss anyone booked, and negative when it was curtailed in hours priced below zero. The data does not locate a curtailment, so the hub's price stands for a place the data does not name. An hour with no price is left out of both the MWh and the dollars. Texas's is the ERW's estimate over the hours held, never a month. SPP is held by day only and nothing of it is valued.";
function worth(a: Json): Json {
  const grid = gridOf(a);
  const words = paused(grid, PAGE_FILES.worth);
  if (words) return words;
  const g = WORTH.grids[grid];
  const head = { ...base(PAGE_FILES.worth, WORTH.built, "Curtailment, what it is worth (docs/methods/curtailment.md)"), page: `/curtailment?grid=${grid}#worth`, is_not: WORTH_NOT };
  if (!g) return WORTH.not_held[grid] ? { ...head, grid: grid.toUpperCase(), not_held: WORTH.not_held[grid] } : fail(`no grid ${JSON.stringify(a.grid)} in "What it is worth"; grids: ${Object.keys(WORTH.grids).join(", ")}`);
  if (!g.hubs) return { ...head, grid: g.name, not_held: g.missing ?? "nothing is valued for this grid" };
  const hubId = a.place === undefined ? g.main_hub! : Object.keys(g.hubs).find((h) => h.toLowerCase() === String(a.place).toLowerCase());
  if (!hubId || !g.hubs[hubId]) return fail(`curtailed energy is valued at ${Object.keys(g.hubs).join(", ")} for ${g.name}, not at ${JSON.stringify(a.place)}`);
  const market = a.market === "da" ? "da" : "rt";
  const side = g.hubs[hubId][market];
  if (!side) return fail(`no ${marketName(market)} value is held at ${hubId}`);
  const fig = (m: WorthMonth & { months?: number }) => ({ curtailed_mwh_priced: r0(m.curtailed_mwh_priced), value_usd: m.value_usd ?? null, usd_per_mwh_curtailed: m.usd_per_mwh_curtailed ?? null, share_of_mwh_in_hours_below_zero_pct: m.share_mwh_negative_pct ?? null,
    share_of_mwh_in_hours_under_usd_5_pct: m.share_mwh_under5_pct ?? null, mean_price_all_hours: m.price_all_hours_mean ?? null, mean_price_curtailed_hours: m.price_curtailed_hours_mean ?? null, hours_priced: m.hours_priced, ...(m.months !== undefined ? { months: m.months } : {}) });
  const out: Json = { ...head, grid: g.name, whose: g.whose === "operator" ? "the operator's own curtailment figure" : "the ERW's estimate, not a curtailment figure of the operator's", place: hubId, market: marketName(market), prices_from: side.tables.join(", ") };
  if (side.window) return { ...out, over_the_hours_held: fig(side.window), a_whole_month: { not_held: g.months_missing ?? "no whole month is held" } };
  const months = side.months ?? {}, yearsHeld = side.years ?? {};
  const period = typeof a.period === "string" ? a.period : null;
  const newest = Object.keys(months).sort().at(-1);
  if (newest) out.newest_month = { month: newest, ...fig(months[newest]) };
  if (period) out.period = period.length === 7 ? (months[period] ? { month: period, ...fig(months[period]) } : { month: period, not_held: "the month is not valued: the curtailment covers under 90 percent of its days or the price under 95 percent of its hours" })
    : (yearsHeld[period] ? { year: period, ...fig(yearsHeld[period]) } : { year: period, not_held: `no month of ${period} is valued` });
  const byYear = a.by === "year";
  const rows = byYear ? Object.keys(yearsHeld).sort().flatMap((y) => (yearsHeld[y].usd_per_mwh_curtailed !== undefined ? [{ year: y, value: yearsHeld[y].usd_per_mwh_curtailed as number, value_usd: yearsHeld[y].value_usd ?? null, months: yearsHeld[y].months ?? null }] : []))
    : Object.keys(months).sort().filter((m) => !period || m.startsWith(period.slice(0, 4))).flatMap((m) => (months[m].usd_per_mwh_curtailed !== undefined ? [{ month: m, value: months[m].usd_per_mwh_curtailed as number, value_usd: months[m].value_usd ?? null, curtailed_mwh_priced: r0(months[m].curtailed_mwh_priced) }] : []));
  return { ...out, title: `${g.name}: what curtailed wind and solar energy was worth at ${hubId}, ${marketName(market)}, USD per MWh curtailed, by ${byYear ? "year" : "month"}`, group_by: byYear ? "year" : "month", units: ["USD/MWh"], result: rows, rows_matched: rows.length,
    result_note: "value is USD per MWh curtailed: the dollars over the MWh that have a price; value_usd is the dollars" };
}

// ---- /resources -----------------------------------------------------------------------------------------------------

const RESOURCES_NOT = "A resource layer is the publisher's estimate of a resource over an area. It is not a siting study, and it says nothing of land use, access to transmission, permits or cost. A value is the stored value of one cell, or of one shape or site, in the source's own unit; nothing is smoothed or filled. The wind capacity factor layer is not a gross capacity factor and is not called one: it is the capacity factor column of the laboratory's supply curve. No place name is looked up: a place is a longitude and a latitude.";
// Each path is written out to its folder, as lib/resourcesdata.ts writes it, so that the server's file trace of the
// ask route holds the folder of layers and the list, and nothing more.
function layerPath(file: string): string | null {
  if (!/^[A-Za-z0-9._-]+$/.test(file) || file.includes("..")) return null;   // a bare file name, never a path
  const p = path.join(process.cwd(), "data", "resources", "layers", file);
  return fs.existsSync(p) ? p : null;
}
let MANIFEST: Manifest | null = null;
/** The list of layers the page reads (data/resources/manifest.json), with the layers whose files are on the server. */
export function manifest(): Manifest {
  if (MANIFEST) return MANIFEST;
  const raw = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "resources", "manifest.json"), "utf8")) as Manifest;
  MANIFEST = { ...raw, layers: (raw.layers ?? []).filter((l) => filesOf(l).some((f) => layerPath(f))) };
  return MANIFEST;
}
const layerFiles = new Map<string, unknown>();
function readLayer(file: string): unknown {
  if (layerFiles.has(file)) return layerFiles.get(file);
  if (!layerPath(file)) throw new Error(`the file ${file} of the layer is not on the server`);
  // the path is written out again where it is read: a path held in a variable makes the build trace the whole project
  const v = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "resources", "layers", file), "utf8")) as unknown;
  if (layerFiles.size >= 6) layerFiles.delete(layerFiles.keys().next().value as string);   // a few layers are kept: the largest is under 3 MB
  layerFiles.set(file, v);
  return v;
}
const layerHead = (l: Layer): Json => { const lg = legendOf(l); return { layer: l.id, title: l.title, group: l.group, kind: l.kind, unit: l.unit ?? "", publisher: l.publisher ?? "", vintage: l.vintage ?? "", ...(lg ? { range: { lowest: lg.min, highest: lg.max } } : {}) }; };
const resourcesBase = (l?: Layer): Json => ({ ...base(PAGE_FILES.resources, String(manifest().built_at_utc ?? ""), l ? `Where the resources are (docs/methods/resources.md): ${l.publisher ?? ""}, ${l.source_title ?? l.title}` : "Where the resources are (docs/methods/resources.md): each layer names its publisher"), page: "/resources" });
function findLayer(a: Json): Layer | Json {
  const id = String(a.layer ?? "").toLowerCase().trim();
  const ls = manifest().layers;
  const l = ls.find((x) => x.id.toLowerCase() === id) ?? ls.find((x) => id && (x.id.toLowerCase().includes(id) || x.title.toLowerCase().includes(id)));
  return l ?? fail(`no resource layer ${JSON.stringify(a.layer)}; layers: ${ls.map((x) => x.id).join(", ")}`);
}
function layers(): Json {
  const m = manifest();
  const rows = m.layers.map(layerHead);
  return { ...resourcesBase(), layers: rows, layers_held: rows.length, not_held: (m.missing ?? []).map((x) => ({ layer: x.id ?? x.title ?? "", why: x.reason ?? x.why ?? "" })), is_not: RESOURCES_NOT };
}
type Feature = { properties: Json & { name?: string; kind?: string; value?: number | null; value_unit?: string }; geometry: Geometry };
function featuresOf(l: Layer): { name: string; kind: string; value: number | null; unit: string; props: Json; geometry: Geometry | null; lon?: number; lat?: number }[] {
  const d = readLayer(filesOf(l)[0]) as { features?: Feature[]; columns?: string[]; rows?: unknown[][] };
  if (Array.isArray(d.features)) return d.features.map((f) => ({ name: String(f.properties.name ?? ""), kind: String(f.properties.kind ?? ""), value: typeof f.properties.value === "number" ? f.properties.value : null, unit: String(f.properties.value_unit ?? l.unit ?? ""), props: f.properties, geometry: f.geometry }));
  const cols = d.columns ?? [];
  return (d.rows ?? []).map((r) => { const o = Object.fromEntries(cols.map((c, i) => [c, r[i]])) as Json; return { name: String(o.name ?? o.id ?? ""), kind: "site", value: typeof o.value === "number" ? o.value : null, unit: l.unit ?? "", props: o, geometry: null, lon: Number(o.lon), lat: Number(o.lat) }; });
}
const plain = (v: number) => (Math.abs(v) >= 1000 ? Math.round(v * 10) / 10 : Math.round(v * 10000) / 10000);
function layer(a: Json): Json {
  const l = findLayer(a);
  if ("error" in l) return l as Json;
  const L = l as Layer;
  const out: Json = { ...resourcesBase(L), ...layerHead(L), what_it_is: [L.value_label, L.source_title].filter(Boolean).join(". From: "), extent: L.extent ?? "", source_url: L.source_url ?? "", retrieved: (L.retrieved_at_utc ?? "").slice(0, 10),
    ...(L.source_resolution ? { the_sources_grain: L.source_resolution } : {}), ...(L.reduction ? { how_it_was_reduced: L.reduction } : {}), ...(L.classes?.length ? { classes: L.classes.map((c) => `${c.value}: ${c.label}`) } : {}),
    ...(L.kind === "grid" ? { cells_of_degrees: (L.levels ?? []).map((v) => v.cell_deg).sort((x, y) => y - x), parts_in_files_of_their_own: pyramidsOf(L).slice(1).map((p) => p.extent) } : {}),
    what_it_is_not: L.notes_for_method ?? "", is_not: RESOURCES_NOT };
  if (L.kind !== "grid") { const fs2 = featuresOf(L); out.features_held = fs2.length; const names = [...new Set(fs2.map((f) => f.name).filter(Boolean))]; if (names.length <= 60) out.names = names; }
  return out;
}
function valueAtPlace(a: Json): Json {
  const l = findLayer(a);
  if ("error" in l) return l as Json;
  const L = l as Layer;
  const lon = Number(a.lon), lat = Number(a.lat);
  if (a.lon === undefined || a.lat === undefined || !Number.isFinite(lon) || !Number.isFinite(lat) || lon < -180 || lon > 180 || lat < -90 || lat > 90) return fail("value_at needs lon and lat in degrees (west is negative): no place name is looked up");
  const head = { ...resourcesBase(L), ...layerHead(L), at: { lon, lat }, is_not: RESOURCES_NOT };
  if (L.kind === "grid") {
    // the finest level of the pyramid that holds the place: the layer's own, then a part kept in files of its own
    for (const p of pyramidsOf(L)) {
      if (p.box && (lon < p.box[0] || lon > p.box[2] || lat < p.box[1] || lat > p.box[3])) continue;
      const finest = [...p.levels].filter((v) => layerPath(v.file)).sort((x, y) => x.cell_deg - y.cell_deg)[0];
      if (!finest) continue;
      const f = readLayer(finest.file) as GridFile;
      const v = valueAt(decodeGrid(f), lon, lat);
      if (v === null) continue;
      const d = decimalsOf(f.scale);
      return { ...head, value: Math.round(v * 10 ** d) / 10 ** d, cell_of_degrees: finest.cell_deg, ...(p.extent ? { part: p.extent } : {}),
        what: `${L.value_label ?? L.title}: the stored value of the cell of ${finest.cell_deg} degrees that holds this place, the finest level the page draws; a coarser level shown at a wider zoom is the mean of the source's cells inside it and can read slightly differently` };
    }
    return { ...head, value: null, not_held: "the layer holds no value at this place: outside its extent, or a cell the source leaves empty" };
  }
  const fs2 = featuresOf(L);
  if (fs2.length && fs2[0].geometry) {
    const hits = fs2.filter((f) => inGeometry(f.geometry, lon, lat)).slice(0, 8).map((f) => ({ name: f.name, kind: f.kind, value: f.value === null ? null : plain(f.value), unit: f.unit }));
    return { ...head, shapes_that_hold_this_place: hits, ...(hits.length ? {} : { not_held: "no shape of the layer holds this place" }) };
  }
  // a layer of sites: the site whose square of the source's own spacing holds the place, if any
  const half = ((L.point_spacing_km ?? 0) / 2) / 111.32;
  if (!(half > 0)) return fail(`${L.id} is a layer of sites with no spacing: read it by name with view features`);
  const hit = fs2.filter((f) => Math.abs((f.lat ?? 99) - lat) <= half && Math.abs((f.lon ?? 999) - lon) <= half / Math.max(0.1, Math.cos((lat * Math.PI) / 180)))
    .sort((x, y) => Math.hypot((x.lon as number) - lon, (x.lat as number) - lat) - Math.hypot((y.lon as number) - lon, (y.lat as number) - lat))[0];
  return hit ? { ...head, value: hit.value === null ? null : plain(hit.value), site: { lon: hit.lon, lat: hit.lat }, what: `${L.value_label ?? L.title}: the source's site whose square of ${L.point_spacing_km} km holds this place`, columns: L.columns_meaning ?? {}, row: hit.props }
    : { ...head, value: null, not_held: `no site of the source lies within its own spacing (${L.point_spacing_km} km) of this place` };
}
function features(a: Json): Json {
  const l = findLayer(a);
  if ("error" in l) return l as Json;
  const L = l as Layer;
  if (L.kind === "grid") return fail(`${L.id} is a grid: read it at a place with view value_at (lon, lat)`);
  const all = featuresOf(L);
  const words = String(a.name ?? "").toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length > 1);
  const found = words.length ? all.filter((f) => words.every((w) => f.name.toLowerCase().includes(w))) : all;
  const rows = found.slice(0, 40).map((f) => ({ name: f.name, value: f.value === null ? null : plain(f.value), kind: f.kind }));
  return { ...resourcesBase(L), ...layerHead(L), what_it_is: L.value_label ?? "", features_held: all.length, features_found: found.length,
    title: `${L.title}${words.length ? `: ${String(a.name)}` : ""}, ${L.unit ?? ""}`.replace(/, $/, ""), group_by: "name", units: L.unit ? [L.unit] : [], result: rows, rows_matched: found.length,
    result_note: `${found.length > rows.length ? `the first ${rows.length} of ${found.length} found; ` : ""}value is ${L.value_label ?? "the layer's value"}${L.unit ? `, in ${L.unit}` : ""}; a feature with no value prints none in the source`,
    ...(found.length === 1 ? { feature: found[0].props } : {}), what_it_is_not: L.notes_for_method ?? "", is_not: RESOURCES_NOT };
}

/** page_file: one view of one page's own file. A plain message under "error" is the model's to read. */
export function pageFile(input: unknown): Json {
  const a = (input ?? {}) as Json;
  const held = heldIn(a);
  if (held) return heldRefusal(held);
  try {
    switch (a.view) {
      case "cost": return cost(a);
      case "regions": return regions(a);
      case "demand": return demand(a);
      case "capture": return capture(a);
      case "hubs": return hubs(a);
      case "share": return share(a);
      case "free_energy": return freeEnergy(a);
      case "worth": return worth(a);
      case "layers": return layers();
      case "layer": return layer(a);
      case "value_at": return valueAtPlace(a);
      case "features": return features(a);
      default: return fail(`view must be one of ${PAGE_FILE_VIEWS.join(", ")}`);
    }
  } catch (e) {
    return fail(`the page's file could not be read, so no figure is given: ${(e as Error).message}`);
  }
}
export { GRIDS as PAGE_FILE_GRIDS };

// ---------------------------------------------------------------------------------------------------------------------
// The guide: what the model is told of all of it, appended to the profile's system prompt when the pages are offered.
// Every "is not" is taken from the page's own Method note (docs/methods/datacenter_cost.md, curtailment.md,
// cost_of_power.md, resources.md); none is a new claim.
// ---------------------------------------------------------------------------------------------------------------------

export function pagesGuide(): string {
  return `

FOUR PAGES OF THIS SITE (session 153): what a datacenter pays (/cost-of-power), curtailment and where free energy is (/curtailment), the capture price (/cost-of-power/seller) and where the resources are (/resources). You can read what stands behind them: ten tables with query, and the pages' own files with the tool page_file. These lines add to the rules above and govern where they differ.

WHICH GRIDS. These four pages are tools for every grid, so for what THEY show, and only for that, you answer for CAISO, NYISO, ISO-NE and SPP as well as ERCOT: curtailment and its share, the hours priced below zero or under USD 5 per MWh, what curtailed energy was worth, the capture price, what a flat load paid at a hub or zone over a year or a month, and a resource layer anywhere in the United States. Everything else about another grid is refused as before (its price on a day or in a week, its demand, its generation or fuel mix, its batteries, its capacity auction): say that its own page is /grid/<slug>. MISO: answer "paused while terms are reviewed", not_in_warehouse true, no figure. PJM: answer "licensed source needed", not_in_warehouse true, no figure. When no grid is named, the grid is ERCOT.

THE TOOL page_file reads the same files the pages read, through the pages' own functions, so its figure is the page's figure. Give view, and grid, place (a hub or zone as the operator names it), market (rt or da), fuel, period, by or window as the question names them; what the question does not name is left out and the page's default is taken (ERCOT; the grid's main place; real time). Its result is a tool result: cite the table name it returns (for example "site/data/seller/capture.json") with its source_report and data_version. A result with rows in result can be named in series. Every result carries is_not: when it bears on how the figure should be read, say it in a few words.
- view "cost" (/cost-of-power): what a FLAT load paid for energy at a hub or zone, USD per MWh: the last twelve complete months, a bad month (the worst tenth of the last 36), power per GPU-hour at the page's stated defaults, and each year (by "year") or month (by "month") in result. ERCOT's main place is the load zone LZ_NORTH (a Texas load settles at its load zone); its hubs are HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON, HB_BUSAVG and its other zones LZ_HOUSTON, LZ_SOUTH, LZ_WEST (LZ_AEN, LZ_CPS, LZ_LCRA, LZ_RAYBN day-ahead only), from 2015. CAISO: TH_SP15_GEN-APND, TH_NP15_GEN-APND, TH_ZP26_GEN-APND. NYISO: N.Y.C. and ten more zones, from 2019. ISO-NE: .H.INTERNAL_HUB, and its zones from 26 August 2026 only. SPP: SPPNORTH_HUB, SPPSOUTH_HUB. view "regions": every place of a grid at once. view "demand" (the page's "Will the power be there"): the hours a grid was tight in each year (demand at or above 95 percent of that year's highest hour: hours near the year's own peak, NOT a measure of scarcity or of an emergency), the year's highest hour, and average demand by the operator's own regions; ERCOT from 2015, CAISO, NYISO; ISO-NE's is held, not shown; SPP's is not held. IT IS NOT a bill: wholesale energy only, no delivery, transmission, demand or retail charge; a hub or zone is an average over many points, not a site; a flexible load (off in its dearest hours, or shifting) is computed on the page from the reader's own inputs and is not read here. For ERCOT's hub average by month, cost_of_power_monthly of the guide is still the table.
- view "capture" (/cost-of-power/seller): the capture price of solar or wind at a hub or zone: the generation-weighted price (the sum of price times the grid's generation, over the generation), the flat average of the same hours, and the premium or discount between them, for the last twelve counted months and by year or month. Give fuel. view "hubs": every hub and zone of a grid at once. IT IS NOT a site's price: it is the FLEET'S SHAPE, the whole grid's hourly solar or wind generation, at a hub's price, so one plant's resource, curtailment, congestion and node price are not in it; it is not what a plant with a contract earns; no cost is taken off. It differs from merchant_revenue_monthly's capture price (monthly, at ERCOT's hub average, weighed by output per MW installed): say which you read. The page's hybrid "Combined" is two revenues added, a solar plant's and a battery's, each priced as if it stood alone: it is not read here, and you never add the two yourself.
- view "share" (/curtailment): the share of available wind and solar output curtailed: curtailed MWh over curtailed plus output MWh. CAISO (149 months from May 2014) and SPP (from September 2018) by month or year; ERCOT: the days held. IT IS NOT one measure: CAISO's and SPP's figures are the operators' own; ERCOT publishes no curtailment figure, and Texas's is the ERW's ESTIMATE (output below the limit the plants reported, which includes anything that keeps output under the limit), held from 28 September 2026 for whole days only, never a month, and not comparable with the other two. Never add the grids up. CAISO's shares of 2026 rest on its Today's Outlook output, which shows more output than its Daily Renewable Report: a share on the report's output would be higher. SPP's denominator is EIA's hourly output. The data does not say where a curtailment happened. NYISO: "not in the ERW" (it prints a monthly figure in a document, not as data).
- view "free_energy" (/curtailment, "Where free energy is"): for each hub and zone of a grid, the hours priced below zero and the hours priced under USD 5 per MWh (which include those below zero, each hour once), with the mean price, over the last twelve months (window "year") or the last whole month (window "month"); the cheapest place against the dearest; West Texas against Houston and California north against south. With place: that place's hours by month. IT IS NOT energy for nothing: a count of hours at a wholesale price, with no delivery or demand charge; a hub or zone is not a site; it does not say where power was curtailed. Say whether the count is real time or day-ahead (basis).
- view "worth" (/curtailment, "What it is worth"): each hour's curtailed MWh times the hub's price of that hour: the dollars, USD per MWh curtailed, the share of the MWh in hours below zero and under USD 5, and the mean price of the curtailed hours against all hours. CAISO at TH_SP15_GEN-APND or TH_NP15_GEN-APND, by month from September 2024 or by year; ERCOT at HB_HUBAVG or HB_WEST, over the hours held only. IT IS NOT a loss anyone booked: it is what the energy would have fetched at the hub, negative when curtailed in hours below zero, and the hub stands for a place the data does not name. SPP: held by day only, nothing valued.
- views "layers", "layer", "value_at", "features" (/resources): the natural resource layers. "layers" lists them with unit, publisher, vintage and range; "layer" gives one in full with what it is not; "value_at" gives a layer's value at a longitude and latitude (lon, lat in degrees, west negative): a grid's cell (wind_speed_100m in m/s, solar_ghi and solar_dni in kWh/m2/day), the shapes that hold the place, or the supply curve site of wind_capacity_factor; "features" finds shapes or sites by name (oil_gas_basins, oil_gas_plays, biomass by "County, ST", offshore_wind_leases, geothermal_hydrothermal_sites). IT IS NOT a siting study: a layer is the publisher's estimate of a resource over an area and says nothing of land use, access to transmission, permits or cost. Refuse a siting judgment ("where should I build", "is this a good site", "the best place for"): not_in_warehouse true, say that the map holds resource layers and not a siting study, nearest "site/data/resources/manifest.json". The wind capacity factor layer is NOT a gross capacity factor and is never called one: it is the capacity factor column of the laboratory's supply curve for a 2035 turbine. Wind speed is a model's long-run average (2007 to 2013), not a measurement and not a forecast. No place name is looked up: when the question gives a longitude and latitude, use them; when it names only a place, say that the layer is read at a longitude and latitude and give the layer's range. No hydropower layer is held.

TEN TABLES behind these pages, read with query like any table of the guide (plain dates, no tz):
- iso_curtailment_monthly (public, tier derived, monthly): entities caiso:ISO (from 2014-05) and spp:SPP (from 2014-03). Variables, MWh: curtailed_solar_mwh, curtailed_wind_mwh; CAISO's reason curtailed_<fuel>_local_mwh and curtailed_<fuel>_system_mwh (2024 on); SPP's kinds curtailed_<fuel>_redispatch_mwh, _manual_mwh, _economic_mwh; solar_generation_mwh and wind_generation_mwh (CAISO, to 2025); and the share: share_curtailed_pct (percent), share_curtailed_mwh, share_output_mwh, share_hours_held, share_hours_in_month. A month is written only when every day of it is held: the month now running is not in it. It holds no ERCOT row. Always give entity and variable.
- caiso_curtailment_daily and spp_curtailment_daily (public, tier source, daily, the newest 100 days on this site): entity caiso:ISO; spp:SPP and, for SPP's western area, spp:SWPW. The same curtailed variables by day.
- ercot_wind_solar_hsl_daily (public, tier source, daily, from 2026-09-19): entity ercot:system. Variables wind_generation_mwh, wind_hsl_mwh, wind_below_hsl_mwh and the same for solar. Output below the High Sustained Limit: say "output below the limit", an estimate, never "curtailment".
- caiso_curtailment_profile (public, tier derived, monthly from 2019-01): entity caiso:ISO. curtailed_solar_mwh and curtailed_wind_mwh; by CAISO's reason (_local_, _system_, _unspecified_ before _mwh; a reason is given from 2022); by local hour of the day curtailed_solar_mwh_h00 to _h23 and curtailed_wind_mwh_h00 to _h23; from 2026 by category (_econ_, _ss_, _oi_); and, from September 2025, against the batteries: battery_charging_mwh, curtailed_mwh_battery_days, curtailed_while_charging_share_pct, avg_curtailed_mw_h00 to _h23, avg_battery_charging_mw_h00 to _h23. One figure for the whole system: it does not locate a curtailment, and that curtailment and charging fall in the same hours does not say the batteries could have taken it.
- eia930_demand_growth (public, yearly from 2019; ERCOT's rows): entity eia930:ERCO. avg_demand_mw, peak_demand_mw, avg_demand_growth_since_2019_pct, peak_demand_growth_since_2019_pct, avg_demand_growth_yoy_pct (each row dated 1 January of its year). Weather is not removed.
- interconnection_queue_summary (public, tier derived; ERCOT's rows): entities queue:ercot:all, queue:ercot:solar, queue:ercot:wind, queue:ercot:battery, queue:ercot:gas, queue:ercot:other. By the year a request ENTERED the queue (a row dated 1 January of that year): requests_entered, mw_entered, and mw_ and requests_ for active, operating, withdrawn, suspended. For the whole file (the row dated 2025-01-01): total_active_mw, total_active_requests, median_years_to_operation, past_operating_share_pct, past_withdrawn_share_pct. A request is not a plant, and it is generation waiting to connect, not load.
- ercot_large_load_status (public, tier source; nine reports from 2025-05-28 to 2026-03-26): entity ercot:large_load. approved_to_energize_mw, observed_nonsimultaneous_peak_mw, observed_simultaneous_peak_mw. It holds no queue by status, no list by place, and a request is not a built facility.
- cost_of_power_hourly_profile (public, tier derived, monthly, the last thirteen months; ERCOT's rows) and cost_of_power_carbon (public, tier derived, monthly from 2018-07; ERCOT's rows): entity ercot:HB_HUBAVG, the page's view "Grid by grid". The first: rt_mean_h00 to rt_mean_h23, the month's average real-time price at each local hour of the day, USD/MWh, with rt_days_h00 to _h23 (the days counted). The second: rt_load_weighted (USD/MWh) beside intensity_generation and intensity_demand (kgCO2/MWh). Hub prices, not a bill.

HELD, NOT SHOWN. These are held internally under their publishers' terms. Never state a figure of them from anywhere. Answer with not_in_warehouse true, say that it is "held, not shown" and why in one sentence, and name the nearest thing that is shown. A tool call that names one is refused by the tool.
${HELD.map((h) => `- ${h.table}: ${h.what}. ${h.reason} ${h.say} Nearest: ${h.nearest}.`).join("\n")}
- Also not anywhere: large load in line by region for any grid other than New York ("not published anywhere yet"); how long a new large load waits; delivery charges outside Texas.`;
}
