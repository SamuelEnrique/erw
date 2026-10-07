// Energy Research Warehouse (ERW) site, session 137: Ask ERCOT as the answer panel. What the session adds to the
// ERCOT profile (lib/chat/ercot.ts), kept apart from lib/chat/spec_ercot.json, which warehouse/chat/ercot.py exports
// and this file does not touch:
//
//   1. THE FORM OF AN ANSWER. Words alone for a question about an idea; one or two sentences for one figure; a short
//      answer with the series it fetched for a question about how something moved; a table for a breakdown. The
//      answer says which ("form"), and a chart is shown only for "chart" or "table": never for its own sake.
//   2. THE ERCOT PAGE'S WRITTEN CONTENT (docs/grids/ercot.md: who runs the grid, how its market sets prices, what
//      makes it different, the short history, the glossary) is carried in the system prompt, so a question about an
//      idea is answered in one model call, citing it. Its numbers (a year, a date) count as given.
//   3. THE TABLES LANDED ON 6 OCTOBER 2026. The price board and Supply and trade are files of this site
//      (data/board.json, data/supply.json), built from tables held out of the live set: the tool page_figures reads
//      the rows of them that are ERCOT's or no grid's. The energy mix's three tables are in the live set and are
//      read with query like any other.
//   4. WHAT IS REFUSED says where to look: another grid's own page, the nearest table held.
//
// A grid is a parameter: panelFor("ercot") is the only panel today, because ERCOT is the only grid with a profile.
import "server-only";
import type Anthropic from "@anthropic-ai/sdk";
import board from "@/data/board.json";
import supply from "@/data/supply.json";
import { DOCS } from "@/lib/markdown";

type Json = Record<string, unknown>;
export const FORMS = ["words", "sentence", "chart", "table"] as const;
export type Form = (typeof FORMS)[number];
export const NOTES_TABLE = (slug: string) => `docs/grids/${slug}.md`;
export const PAGE_TABLES: Record<string, string> = { board: "site/data/board.json", supply: "site/data/supply.json" };
/** The mix tables loaded into the live set on 6 October 2026: read with query, described in the addendum. */
export const MIX_TABLES = ["generation_mix_hourly_profile", "clean_energy_summary", "grid_stress_yearly"];
/** What each holds, for a refusal that names one as the nearest thing held (as spec_ercot.json "holds" does for the guide's tables). */
export const MIX_HOLDS: Record<string, string> = {
  generation_mix_hourly_profile: "by month: each source's generation in MWh and its share, and each source's average MW at each hour of the day",
  clean_energy_summary: "by month: the carbon-free share of generation, by hour of the day too, and the cost and carbon of a flat load",
  grid_stress_yearly: "by year: the evening ramp, the lowest net load, the tightest hours and the longest calm stretches",
};
const OTHER_GRIDS = ["caiso", "isone", "iso-ne", "miso", "nyiso", "pjm", "spp"];
const MAX_ROWS = 12;

export const FORM_SCHEMA = { type: "string", enum: [...FORMS], description: "words: an idea, from the written content, no series. sentence: one figure, no series. chart: a series over time. table: a breakdown across categories." };

export const PAGE_TOOL: Anthropic.Tool = {
  name: "page_figures",
  description: "Rows of two pages of this site built on 6 October 2026 from tables the query tool cannot reach: the price board (page \"board\": ERCOT hub prices day-ahead and real time with their moves over a day, a week, a month and a year, on-peak and off-peak, the spark spread and implied heat rate, day-ahead less real time, battery spreads, reserve prices; Henry Hub and Waha natural gas, crude oil, refined products, Treasury yields) and Supply and trade (page \"supply\": natural gas in storage, crude and product stocks, production, refining, trade, the natural gas and coal burned for power in ERCOT, the energy ERCOT's day-ahead market cleared, managed money positions; weekly). Only rows that are ERCOT's or no grid's are returned. Give \"find\" (a few words) to list matching rows with their latest value, date and changes; give \"series\" (a row id from such a list) for that row's recent points (the board: its last 30; supply: its last 52 weeks), which can be named in series for a chart. One call is enough for most questions: a find also returns the recent points of its first row (in result, which can be named in series), and a series also returns that row's latest value and changes.",
  input_schema: { type: "object", additionalProperties: false, properties: { page: { type: "string", enum: ["board", "supply"] }, find: { type: "string" }, series: { type: "string" } }, required: ["page"] },
};

type BoardRow = { id: string; group: string; label: string; at?: string; unit?: string; freq?: string; status: string; note?: string; source?: number; tags?: Record<string, string>;
  last?: { t: string; v: number }; moves?: Record<string, { t: string; v: number; ch: number; pct: number | null } | null>; range?: { lo: number; hi: number }; spark?: { t0: string; d: number[]; v: number[] } };
type SupplyRow = { id: string; group: string; label: string; at?: string; unit?: string; freq?: string; status: string; note?: string; source?: number;
  last?: { t: string; v: number }; prev?: { t: string; v: number; ch: number } | null; year?: { t: string; v: number; ch: number; pct: number } | null; avg5?: { v: number; ch?: number } | null; spark?: { t: string[]; v: number[] } };
const BOARD = board as unknown as { built: string; sources: string[]; groups: { id: string; title: string }[]; rows: BoardRow[] };
const SUPPLY = supply as unknown as { built: string; sources: string[]; groups: { id: string; title: string }[]; rows: SupplyRow[] };

/** The rows a grid's panel may read: the grid's own and those of no grid. Another grid's row is never returned. */
export function boardRows(iso: string): BoardRow[] {
  return BOARD.rows.filter((r) => !r.tags?.grid || r.tags.grid.toUpperCase() === iso.toUpperCase());
}
export function supplyRows(slug: string): SupplyRow[] {
  // a row of the two per-grid groups belongs to the grid its id names; "burn-all" is seven grids together, so no one grid's
  const grids = [slug, ...OTHER_GRIDS.filter((g) => g !== slug)];
  const gridOf = (id: string) => (/^(burn|cleared)-/.test(id) ? grids.find((g) => id.startsWith(`burn-${g}`) || id.startsWith(`cleared-${g}`)) ?? "several" : null);
  return SUPPLY.rows.filter((r) => { const g = gridOf(r.id); return g === null || g === slug; });
}

const round = (v: number) => Math.round(v * 10000) / 10000;
const addDays = (t0: string, n: number) => new Date(Date.parse(`${t0}T00:00:00Z`) + n * 86400000).toISOString().slice(0, 10);

function match<T extends { id: string; label: string; at?: string; group: string }>(rows: T[], groups: { id: string; title: string }[], find: string): T[] {
  const title = Object.fromEntries(groups.map((g) => [g.id, g.title]));
  const words = find.toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length > 1);
  if (!words.length) return rows.slice(0, MAX_ROWS);
  return rows.map((r) => {
    const text = `${r.label} ${r.at ?? ""} ${r.id} ${title[r.group] ?? ""}`.toLowerCase();
    return [words.filter((w) => text.includes(w)).length, r] as const;
  }).filter(([n]) => n > 0).sort((a, b) => b[0] - a[0]).slice(0, MAX_ROWS).map(([, r]) => r);
}

/** page_figures: the rows found, or one row's recent points. Throws a plain message the model is shown. */
export function pageFigures(a: { page?: string; find?: string; series?: string }, slug: string, iso: string): Json {
  const page = a.page === "board" || a.page === "supply" ? a.page : null;
  if (!page) return { error: 'page must be "board" or "supply"' };
  const table = PAGE_TABLES[page];
  const built = page === "board" ? BOARD.built : SUPPLY.built;
  const base = { table, tier: "site file", license: "public", data_version: `built ${built}` };
  if (page === "board") {
    const rows = boardRows(iso);
    const figures = (r: BoardRow) => ({
      row: r.id, label: r.label, at: r.at ?? "", unit: r.unit ?? "", step: r.freq ?? "", status: r.status,
      ...(r.status === "ok" && r.last ? { latest: { date: r.last.t, value: round(r.last.v) },
        ...Object.fromEntries(Object.entries({ d: "change_on_the_day_before", w: "change_on_a_week_before", m: "change_on_a_month_before", y: "change_on_a_year_before" })
          .map(([k, name]) => [name, r.moves?.[k] ? { date: r.moves[k]!.t, value: round(r.moves[k]!.v), change: round(r.moves[k]!.ch), ...(r.moves[k]!.pct !== null ? { percent: r.moves[k]!.pct } : {}) } : null])),
        ...(r.range ? { one_year_low: round(r.range.lo), one_year_high: round(r.range.hi) } : {}), source: BOARD.sources[r.source ?? -1] ?? "" } : { note: r.note ?? "no value is held" }),
    });
    const points = (r: BoardRow) => r.spark!.d.map((d, i) => ({ day: addDays(r.spark!.t0, d), value: round(r.spark!.v[i]) }));
    if (a.series) {
      const r = rows.find((x) => x.id === a.series);
      if (!r) return { error: `no row ${JSON.stringify(a.series)} for ${iso} on the price board; use find to list rows` };
      if (r.status !== "ok" || !r.spark) return { ...base, row: r.id, label: r.label, status: r.status, note: r.note ?? "no value is held" };
      const result = points(r);
      // session 143: the row's own figures come with its points, so one call serves a figure and a chart
      return { ...base, row: r.id, title: `${r.label}${r.at ? `, ${r.at}` : ""}`, group_by: "day", units: r.unit ? [r.unit] : [], result, rows_matched: result.length, source_report: BOARD.sources[r.source ?? -1] ?? "the price board", result_note: `the row's last ${result.length} points, as the price board holds them`, figures: figures(r) };
    }
    const found = match(rows, BOARD.groups, a.find ?? "");
    // session 143: a search also returns the recent points of its first row, so a question about one row is one call
    const top = found[0]?.status === "ok" && found[0].spark ? found[0] : null;
    const first = top ? { result_row: top.id, title: `${top.label}${top.at ? `, ${top.at}` : ""}`, group_by: "day", units: top.unit ? [top.unit] : [], result: points(top), result_note: `result holds the last ${top.spark!.d.length} points of the first row found (${top.id}), as the price board holds them; for another row's points call again with series` } : {};
    return { ...base, source_report: "the price board (docs/methods/price_board.md); each row names its own source", rows: found.map(figures), rows_found: found.length, ...first };
  }
  const rows = supplyRows(slug);
  const figures = (r: SupplyRow) => ({
    row: r.id, label: r.label, at: r.at ?? "", unit: r.unit ?? "", step: r.freq ?? "", status: r.status,
    ...(r.status === "ok" && r.last ? { latest: { date: r.last.t, value: round(r.last.v) },
      period_before: r.prev ? { date: r.prev.t, value: round(r.prev.v), change: round(r.prev.ch) } : null,
      a_year_before: r.year ? { date: r.year.t, value: round(r.year.v), change: round(r.year.ch), percent: r.year.pct } : null,
      five_year_average: r.avg5 ? { value: round(r.avg5.v) } : null, source: SUPPLY.sources[r.source ?? -1] ?? "" } : { note: r.note ?? "no value is held" }),
  });
  const points = (r: SupplyRow) => r.spark!.t.map((t, i) => ({ day: t, value: round(r.spark!.v[i]) }));
  if (a.series) {
    const r = rows.find((x) => x.id === a.series);
    if (!r) return { error: `no row ${JSON.stringify(a.series)} on Supply and trade for ${iso}; use find to list rows` };
    if (r.status !== "ok" || !r.spark) return { ...base, row: r.id, label: r.label, status: r.status, note: r.note ?? "no value is held" };
    const result = points(r);
    return { ...base, row: r.id, title: `${r.label}${r.at ? `, ${r.at}` : ""}`, group_by: "day", units: r.unit ? [r.unit] : [], result, rows_matched: result.length, source_report: SUPPLY.sources[r.source ?? -1] ?? "Supply and trade", result_note: `the row's last ${result.length} points, as Supply and trade holds them`, figures: figures(r) };
  }
  const found = match(rows, SUPPLY.groups, a.find ?? "");
  const top = found[0]?.status === "ok" && found[0].spark ? found[0] : null;
  const first = top ? { result_row: top.id, title: `${top.label}${top.at ? `, ${top.at}` : ""}`, group_by: "day", units: top.unit ? [top.unit] : [], result: points(top), result_note: `result holds the last ${top.spark!.t.length} points of the first row found (${top.id}), as Supply and trade holds them; for another row's points call again with series` } : {};
  return { ...base, source_report: "Supply and trade (docs/methods/supply_and_trade.md); each row names its own source", rows: found.map(figures), rows_found: found.length, ...first };
}

/** The written content of a grid's page, as the system prompt carries it. */
export const notesOf = (slug: string): string => DOCS.grids[slug] ?? "";

/** What the panel adds to a grid profile's system prompt. */
export function addendum(slug: string, iso: string): string {
  const notes = NOTES_TABLE(slug);
  return `

THE ANSWER PANEL (session 137). Your answer is shown right below the question box. Give it the form the question calls for and name that form in "form". These rules add to the rules above and, where they differ on the form of an answer, they govern.

- form "words": the question is about an idea, a rule, a definition or history (how ${iso} sets prices, what a hub is, what happened in a storm). A question that asks what something is, what happened, why or how, and asks for no figure ("how much", "what was the price", "how many"), is this form even when tables hold numbers about its subject: do not fetch them. Answer in plain words, at most 120, from THE WRITTEN CONTENT OF THE ${iso} PAGE below. Call no tool: the text is already here. Cite it in citations as table "${notes}", source_report "${notes}: text written for the ERW's ${iso} page; each section names its ISO and EIA sources", data_version "the site's build", tier "written". series must be empty. If the written content does not cover the idea, say so plainly and set not_in_warehouse true: do not answer from memory.
- form "sentence": the question asks for one figure, or two or three (a price on a day, a peak, a total, a count). Fetch it, then answer in one or two sentences, at most 50 words in all, with the figure, its unit and its date. Any note of how you read the question (which day "yesterday" is, which month "last month" is) is inside those 50 words: keep it to a few words, such as "(2026-10-05)". series must be empty: a single figure is never charted, even when the query that found it returned a grouped result.
- form "chart": the question asks how something moved over time or across the hours of a day (day by day, by month, by year, by hour). Fetch it grouped, answer in at most three sentences, at most 90 words in all including any note of how you read the question, saying what the series shows (its range, its high and low, its direction), and name the result in series. Do not list the rows in the answer: the page shows them.
- form "table": the question asks for a breakdown across categories (by fuel, by hub, by owner). As "chart": name the result in series; the page shows its rows as a table.
- Name in series only what the question asked to see. Never add a series for its own sake.
- ONE READING TURN (session 143). Ask for everything the question needs in a single turn of tool calls, all of them at once: they are read together, and every further turn costs the reader seconds. A grouped query's result carries a summary of its own rows (the lowest and the highest row with their keys, the first and the last, the change between them, the mean and the median of the rows, and the same aggregation over every matched row at once): take the high, the low, the range, the direction and the level from it, and run no further query for them. Never repeat a call already made: its result is above.
- The dates the guide above gives for a table's first and last rows were true when the guide was written; the tables grow every day. Never say that a recent day, yesterday or this week is not held without a query that came back empty: query the table for the days asked first, and if the newest rows stop before them, answer for the newest whole day held and say which day that is.

MORE SOURCES, LANDED ON 6 OCTOBER 2026.
- The tool page_figures reads two pages of this site. page "board": ${iso}'s hub prices with their moves, on-peak and off-peak, the spark spread and implied heat rate, day-ahead less real time, battery spreads, reserve prices; and prices of no grid: Henry Hub and Waha natural gas, crude oil, refined products, Treasury yields. page "supply": natural gas in storage, crude and product stocks, production, refining, trade, the natural gas and coal burned for power in ${iso} by week, the energy ${iso}'s day-ahead market cleared by week, managed money positions. Call it with find (a few words) to list rows, each with its latest value, its date and its changes; call it with series (a row id) for the row's recent points, which you may name in series. Its results are tool results: cite the table name it returns ("site/data/board.json" or "site/data/supply.json") with the row's own source as source_report.
- Use the tables of the guide first for ${iso}'s prices, demand, generation and batteries. Use page_figures for natural gas and oil prices, the spark spread, gas in storage, fuel burned for power, and day-ahead energy cleared.
- Three tables of the energy mix are read with query like any table of the guide, entity "iso:${slug}": generation_mix_hourly_profile (by month, each a row dated the month's first day: each source's generation in the month, variables wind_mwh, solar_mwh, coal_mwh, natural_gas_mwh, nuclear_mwh, hydro_mwh, storage_mwh, other_mwh and net_generation_mwh; each source's share, wind_share_pct and so on; and each source's average MW at each hour of the day, avg_wind_mw_h00 to avg_wind_mw_h23 and so on, with avg_demand_mw_hNN. Use it for generation by fuel by month or by year, which no table of the guide holds beyond the newest weeks), clean_energy_summary (by month: carbon_free_share_pct, the carbon-free share at each hour cf_share_pct_h00 to h23, and the cost and carbon of a flat load), grid_stress_yearly (by year: the evening ramp, the lowest net load, the tightest hours). Their exact variable names are listed under THE TABLES NOW when that list is given: query them directly, and call describe_table for one of them only when the list is not there.

WHAT IS NOT ANSWERED, AND WHERE TO SEND THE READER. For each of these set not_in_warehouse true, form "words", series empty, call no tool, name in the answer what was asked about, and fill nearest:
- Another grid (PJM, CAISO, MISO, NYISO, ISO-NE, SPP, IESO or any other grid or country). This panel answers for ${iso} only. Name the grid asked about and say that its own page is /grid/<slug> (pjm, caiso, miso, nyiso, isone, spp) when it is one of those six.
- Licensed data: futures and forward prices (ICE, CME, NYMEX), S&P Global and Platts assessments. Say it is licensed and not held, and name what is held nearest (a spot or day-ahead price).
- What a named company earned, was paid, bid, offered or owns in the market. The warehouse holds markets, not company accounts or confidential bids. Name the company and say so.
- A forecast of a price or of demand, or advice on what to buy. The warehouse holds what happened.

THE WRITTEN CONTENT OF THE ${iso} PAGE (${notes}):
${notesOf(slug)}`;
}
