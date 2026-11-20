// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): problem set "A storm across the country".
// Winter Storm Elliott (December 2022) in Tennessee and the Carolinas beside Winter Storm Uri (February 2021) in Texas:
// demand, what ran and what moved between regions, each at one hour of the event's window. Every figure is read from a
// committed page file and carries its pf| key (lib/pagefile.ts):
//   site/data/regions/events/elliott_2022.json, site/data/regions/events/uri_2021.json
// each region's hourly demand, net generation, net imports and generation by source over the window and its baseline,
// and each pair of regions' hourly flow, as "The whole country" on each event page draws them (app/events/WholeCountry.tsx).
// The hour of a question is the region's highest hour of demand in the window (the page's "Highest hour"), found from the
// file by its rule; the replication finds it again (replication/problem_sets/replicate_country.py).
import type { Question } from "@/lib/problems";
import { REGION_NAME } from "@/lib/countryfiles";
import { argmax, calc, fig, hourAt, open, type Built, type Meta, type SetGuide } from "./common";

const E = "regions/events/elliott_2022.json", U = "regions/events/uri_2021.json";
const REG = "eia930_region_hourly", FUEL = "eia930_region_fuel_hourly", PAIR = "eia930_region_pair_hourly";
type Series = (number | null)[];
type Region = { demand_mw: Series; net_generation_mw: Series; net_imports_mw: Series; gen: Record<string, Series>; baseline: { demand_mw: Series; net_imports_mw: Series; gen: Record<string, Series> } };
type EventFile = { title: string; start: string; end: string; baseline: string; hours: { start: string; step_hours: number; n: number }; regions: Record<string, Region>; pairs: Record<string, Record<string, Series>> };

export const META: Meta = {
  slug: "storm-across-the-country", title: "A storm across the country: Elliott and Uri",
  line: "Winter Storm Elliott in Tennessee and the Carolinas beside Winter Storm Uri in Texas: the highest hour of demand against the baseline, what ran in that hour, and the power that moved between regions.",
  teacher: "About 45 minutes. Prerequisites: MW, a baseline (the same days of earlier years), the sign of a flow. Students should open /events/elliott-2022 and /events/uri-2021 at The whole country, read the table Each region across the event, pick a region under A region hour by hour and read its charts at the hour a question names (UTC).",
  pages: [{ href: "/events/elliott-2022#whole-country", label: "Elliott: the whole country" }, { href: "/events/uri-2021#whole-country", label: "Uri: the whole country" }, { href: "/data/methods/regions_pages", label: "Method: the regions' files" }],
};

export const GUIDE_ENTRY: SetGuide = {
  can: "find a region's highest hour of a storm, set it against the baseline, and read what ran and what moved in that hour",
  grids: ["EIA's thirteen regions of the lower 48"],
  tables: [REG, FUEL, PAIR],
  skills: ["the highest hour of a window", "a baseline hour", "a share of generation", "the direction of a flow", "two reports of one flow"],
  order: ["s1", "s2", "s3", "s5", "s4", "s6", "s7"],
  files: [E, U],
};

const name = (c: string) => REGION_NAME[c] ?? c;

export async function build(): Promise<Built> {
  const el = open<EventFile>(E), ur = open<EventFile>(U);
  /** The hour of a region's highest demand in an event's window, the figure, the baseline at that hour, and the words of its time. */
  const peak = (file: string, f: EventFile, r: string) => {
    const i = argmax(f.regions[r].demand_mw);
    return { i, at: hourAt(f.hours.start, f.hours.step_hours, i), d: fig(file, ["regions", r, "demand_mw", i], "MW"), b: fig(file, ["regions", r, "baseline", "demand_mw", i], "MW") };
  };
  const at = (file: string, r: string, path: (string | number)[], u = "MW") => fig(file, ["regions", r, ...path], u);

  // ---------------------------------------------------------------- worked example: the Carolinas in Elliott
  const c = peak(E, el, "CAR"), cr = calc("ratio", c.d, c.b, "times");
  const example: Question = {
    id: "sx", tables: [REG],
    q: `Winter Storm Elliott (${el.start} to ${el.end}): what was the Carolinas' highest hour of demand in the window, when was it, what was the baseline's demand in that hour, and how many times the baseline was it?`,
    answer: [`${c.at}: `, c.d, " against a baseline of ", c.b, ": ", cr, " the baseline."],
    line: [c.d, " / ", c.b, " = ", cr],
    steps: [["On /events/elliott-2022, The whole country, the table Each region across the event: the Carolinas' Highest hour, ", c.d, `, at ${c.at}, and Baseline that hour, `, c.b, "."],
      [`In site/data/regions/events/elliott_2022.json: regions, CAR, demand_mw, the largest value (position ${c.i} of the window's hours, counted from ${el.hours.start}); baseline, demand_mw, the same position.`],
      ["Divide: ", c.d, " / ", c.b, " = ", cr, "."]],
    why: `A baseline is ${el.baseline}: the same hour of ordinary days, so the ratio says how far the storm pushed demand above normal.`,
  };

  // ---------------------------------------------------------------- s1: Tennessee in Elliott
  const tn = peak(E, el, "TEN"), tr = calc("ratio", tn.d, tn.b, "times");
  const q1: Question = {
    id: "s1", tables: [REG],
    q: "Winter Storm Elliott: what was Tennessee's highest hour of demand in the window, when was it, what was the baseline's demand in that hour, and how many times the baseline was it?",
    answer: [`${tn.at}: `, tn.d, " against ", tn.b, ": ", tr, " the baseline."],
    line: [tn.d, " / ", tn.b, " = ", tr],
    steps: [["The table Each region across the event, Tennessee: Highest hour ", tn.d, `, at ${tn.at}; Baseline that hour `, tn.b, "."],
      [`Or regions, TEN, demand_mw at position ${tn.i}, and baseline, demand_mw at the same position.`], ["Divide: ", tn.d, " / ", tn.b, " = ", tr, "."]],
    why: "A region whose homes heat with electricity sees its demand jump in a cold snap, and its highest hour is what its plants and wires must meet.",
  };

  // ---------------------------------------------------------------- s2: Texas in Uri
  const tx = peak(U, ur, "TEX"), txd = calc("diff", tx.d, tx.b, "MW");
  const q2: Question = {
    id: "s2", tables: [REG],
    q: `Winter Storm Uri (${ur.start} to ${ur.end}): what was Texas's highest hour of demand in the window, when was it, and by how many MW did it exceed the baseline's demand in that hour?`,
    answer: [`${tx.at}: `, tx.d, " against ", tx.b, ": ", txd, " above the baseline."],
    line: [tx.d, " - ", tx.b, " = ", txd],
    steps: [["On /events/uri-2021, The whole country, Texas: Highest hour ", tx.d, `, at ${tx.at}; Baseline that hour `, tx.b, "."],
      [`Or site/data/regions/events/uri_2021.json: regions, TEX, demand_mw at position ${tx.i}; baseline, demand_mw at the same position. The baseline here is ${ur.baseline}.`],
      ["Subtract: ", tx.d, " - ", tx.b, " = ", txd, "."]],
    why: "The file's demand is the load the region's operators measured: in hours when customers' power was cut, they wanted more than the file shows, so the highest hour in the file can come before the worst of a storm.",
  };

  // ---------------------------------------------------------------- s3: what ran in Tennessee at its peak
  const tg = at(E, "TEN", ["gen", "natural_gas", tn.i]), tc = at(E, "TEN", ["gen", "coal", tn.i]), tu = at(E, "TEN", ["gen", "nuclear", tn.i]), th = at(E, "TEN", ["gen", "hydro", tn.i]);
  const tnet = at(E, "TEN", ["net_generation_mw", tn.i]), tgb = at(E, "TEN", ["baseline", "gen", "natural_gas", tn.i]);
  const q3: Question = {
    id: "s3", tables: [FUEL, REG],
    q: `In Tennessee's highest hour of Elliott (${tn.at}), how much did natural gas, coal, nuclear and hydro generate, what share of the region's net generation was natural gas, and how many times the baseline's natural gas in that hour was it?`,
    answer: ["Natural gas ", tg, ", coal ", tc, ", nuclear ", tu, ", hydro ", th, "; natural gas was ", calc("pct", tg, tnet, "%"), " of net generation (", tnet, ") and ", calc("ratio", tg, tgb, "times"), " the baseline's ", tgb, "."],
    line: [tg, " / ", tnet, " x 100 = ", calc("pct", tg, tnet, "%"), "; ", tg, " / ", tgb, " = ", calc("ratio", tg, tgb, "times")],
    steps: [["Pick Tennessee under A region hour by hour and read Generation by source at that hour; or regions, TEN, gen, each source at position ", `${tn.i}.`],
      ["Natural gas ", tg, ", coal ", tc, ", nuclear ", tu, ", hydro ", th, "; net_generation_mw ", tnet, "."],
      ["Share: ", tg, " / ", tnet, " x 100 = ", calc("pct", tg, tnet, "%"), "."], ["The baseline's natural gas that hour: ", tgb, "; ", tg, " / ", tgb, " = ", calc("ratio", tg, tgb, "times"), "."]],
    why: "Nuclear plants run near their full output in most hours, so the extra demand of a storm hour falls to the plants that can be turned up, such as gas, coal and hydro.",
  };

  // ---------------------------------------------------------------- s4: what ran in Texas at its peak
  const xw = at(U, "TEX", ["gen", "wind", tx.i]), xwb = at(U, "TEX", ["baseline", "gen", "wind", tx.i]);
  const xg = at(U, "TEX", ["gen", "natural_gas", tx.i]), xgb = at(U, "TEX", ["baseline", "gen", "natural_gas", tx.i]);
  const q4: Question = {
    id: "s4", tables: [FUEL],
    q: `In Texas's highest hour of Uri (${tx.at}), how did wind and natural gas generation compare with the baseline's in that hour?`,
    answer: ["Wind ", xw, " against ", xwb, ", a difference of ", calc("diff", xw, xwb, "MW"), "; natural gas ", xg, " against ", xgb, ", ", calc("ratio", xg, xgb, "times"), " the baseline."],
    line: [xw, " - ", xwb, " = ", calc("diff", xw, xwb, "MW"), "; ", xg, " / ", xgb, " = ", calc("ratio", xg, xgb, "times")],
    steps: [[`Pick Texas under A region hour by hour on /events/uri-2021 and read Generation by source at ${tx.at}; or regions, TEX, gen and baseline, gen, at position ${tx.i}.`],
      ["Wind: ", xw, ", baseline ", xwb, "; ", xw, " - ", xwb, " = ", calc("diff", xw, xwb, "MW"), "."],
      ["Natural gas: ", xg, ", baseline ", xgb, "; ", xg, " / ", xgb, " = ", calc("ratio", xg, xgb, "times"), "."]],
    why: "One hour is not the storm: the same comparison at other hours of the window gives other answers, so the hour should be named whenever such a figure is quoted.",
  };

  // ---------------------------------------------------------------- s5: what moved into Tennessee at its peak
  const nbs = Object.keys(el.pairs).filter((k) => k.endsWith("-TEN")).sort();
  const flows = nbs.map((k) => ({ from: k.split("-")[0], v: fig(E, ["pairs", k, "flow_mw", tn.i], "MW") }));
  const top = flows.reduce((a, b) => (b.v.v > a.v.v ? b : a));
  const ti = at(E, "TEN", ["net_imports_mw", tn.i]), tib = at(E, "TEN", ["baseline", "net_imports_mw", tn.i]);
  const outWords = flows.filter((f) => f.v.v < 0).map((f) => name(f.from));
  const q5: Question = {
    id: "s5", tables: [REG, PAIR],
    q: `In the same hour (${tn.at}), what were Tennessee's net imports, and its baseline's? How much flowed between Tennessee and each of its ${flows.length} neighbours, and which sent the most into Tennessee?`,
    answer: ["Net imports ", ti, " against ", tib, " in the baseline. ", ...flows.flatMap((f, j) => [`${j ? "; " : ""}${name(f.from)} to Tennessee `, f.v]), `. The most from ${name(top.from)}${outWords.length ? `; below zero, Tennessee sent power to ${outWords.join(", ")}` : ""}.`],
    line: [`the largest flow into Tennessee = `, top.v, ` (${name(top.from)}); net imports `, ti, " against ", tib],
    steps: [["Tennessee's net_imports_mw at that hour (above zero it imports): ", ti, "; the baseline's: ", tib, "."],
      [`Under pairs, each pair ending in TEN (power from the first region to Tennessee, above zero), flow_mw at position ${tn.i}: `, ...flows.flatMap((f, j) => [`${j ? "; " : ""}${f.from}-TEN `, f.v]), "."],
      ["The table Power between regions, pair by pair gives the same pairs over the whole window, in the direction of the net flow."]],
    why: "In a storm a region leans on its neighbours: the flows show which of them had power to spare in that hour, and that it can send power out on one tie while it takes power in on another.",
  };

  // ---------------------------------------------------------------- s6: two regions' imports at their peaks
  const xi = at(U, "TEX", ["net_imports_mw", tx.i]);
  const q6: Question = {
    id: "s6", tables: [REG],
    q: `Compare the two storms: at its highest hour, how much did Texas import in Uri, and Tennessee in Elliott? Tennessee's net imports were how many times Texas's?`,
    answer: ["Texas ", xi, " at ", tx.d, " of demand; Tennessee ", ti, " at ", tn.d, ": Tennessee's net imports were ", calc("ratio", ti, xi, "times"), " Texas's."],
    line: [ti, " / ", xi, " = ", calc("ratio", ti, xi, "times")],
    steps: [[`Texas, regions, TEX, net_imports_mw at position ${tx.i} of Uri's window: `, xi, "."], [`Tennessee, regions, TEN, net_imports_mw at position ${tn.i} of Elliott's window: `, ti, "."],
      ["Divide: ", ti, " / ", xi, " = ", calc("ratio", ti, xi, "times"), "."]],
    why: "The Texas region of EIA-930 is ERCOT, a grid joined to its neighbours only through a few direct-current ties, so it can import little; Tennessee is part of the Eastern Interconnection, tied to four neighbouring regions.",
  };

  // ---------------------------------------------------------------- s7: two reports of one flow in an hour
  const ka = fig(U, ["pairs", "CENT-TEX", "flow_mw_a", tx.i], "MW"), kb = fig(U, ["pairs", "CENT-TEX", "flow_mw_b", tx.i], "MW");
  const q7: Question = {
    id: "s7", tables: [PAIR],
    q: `In Texas's highest hour of Uri (${tx.at}), how much power did the Central region report sending to Texas, how much did Texas report receiving, and how far apart are the two reports?`,
    answer: ["Central reported ", ka, ", Texas ", kb, ": apart by ", calc("diff", ka, kb, "MW"), "."],
    line: [ka, " - ", kb, " = ", calc("diff", ka, kb, "MW")],
    steps: [[`Under pairs, CENT-TEX (power from Central to Texas, above zero): flow_mw_a, Central's own report, and flow_mw_b, Texas's report turned to the same direction, at position ${tx.i}.`],
      ["Central ", ka, ", Texas ", kb, "; ", ka, " - ", kb, " = ", calc("diff", ka, kb, "MW"), "."],
      ["The page's flow_mw takes the first region's report where it is held, else the second's."]],
    why: "Even in a single hour two operators can report one flow differently; the file keeps both, and the page says which one it draws.",
  };

  return { example, questions: [q1, q2, q3, q4, q5, q6, q7] };
}

