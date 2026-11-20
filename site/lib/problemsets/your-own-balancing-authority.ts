// Energy Research Warehouse (ERW) site, session 8905 (chain 590, part C): problem set "Your own balancing authority", the
// fifth set of the whole country. Every figure is read from a committed page file of an authority's own facts and carries
// its pf| key (lib/pagefile.ts):
//   site/data/regions/authority/tva.json    the Tennessee Valley Authority: what it owns, what is coming and going, what
//                                            it generated, whom it trades with, its size and the large-load rows placed there
//   site/data/regions/authority/erco.json   ERCOT, and
//   site/data/regions/authority/ciso.json   CAISO: the two authorities whose carbon the student compares (EIA's hourly CO2
//                                            estimates cover the seven grid operators only, so the TVA file holds none)
// Written by warehouse/derived/authority_facts.py (method docs/methods/authority_facts.md) and drawn by the Grid tool's
// panel, "Its own facts", on a click of an authority on the map. The plant, the partner, the retirement and the addition
// asked about are chosen by rules written beside them, from the files, never typed; a file rebuilt later gives the same
// questions on its newest figures.
import type { Question } from "@/lib/problems";
import { argmax, calc, fig, monthWords, open, type Built, type Meta, type SetGuide } from "./common";

const A = "regions/authority/tva.json", E = "regions/authority/erco.json", C = "regions/authority/ciso.json";
const OWN = "eia860m_operating_generators", PLAN = "eia860m_planned_generators", RET = "eia860m_retired_generators";
const GEN = "eia930_region_fuel_hourly", CO2 = "eia930_all_emissions", TRADE = "ba_trade_partners", DEMAND = "eia930_ba_demand_hourly", LL = "large_load_public";
type Row = { year: number; technology_group: string; mw: number; generators: number };
type Authority = {
  code: string; name: string; region: string;
  owns: { vintage: string; generators: number; total_mw: number; capacity_mw: Record<string, number>; largest_plants: { name: string; state: string; mw: number; technology_group: string; operator: string }[] };
  coming: { vintage: string; additions: Row[]; retirements: Row[] };
  burns: { months: string[]; share_pct: Record<string, number>; co2: { intensity_kg_per_mwh: number | null; why?: string } };
  trades: { year: number; partners: { code: string; name: string; exchange_gross_mwh: number; net_import_mwh: number }[]; net_import_share_of_demand_pct: number };
  size: { peak_mw: number; peak_local: string; tz: string; growth_year: number; growth_since_2019_pct: number };
  large_loads: { count: number; why?: string };
};

export const META: Meta = {
  slug: "your-own-balancing-authority", title: "Your own balancing authority: what it owns, what is coming, how clean it is, whom it leans on",
  line: "The Tennessee Valley Authority's power plants and its largest, what it plans to build and retire, what its nuclear and gas plants generated against what they could, the neighbour it imports from, two grids' carbon side by side, and how fast its demand grew.",
  teacher: "About 45 minutes. Prerequisites: MW against MWh, a share, a ratio, a difference in percentage points. Students open the Grid tool's map (/grid, the network view, Map), click the Tennessee Valley Authority and read the block Its own facts; then repeat any question for the authority they live in, from its own file under site/data/regions/authority/. The worked answers read site/data/regions/authority/tva.json, erco.json and ciso.json.",
  pages: [{ href: "/grid?grid=us48&view=network&shape=map", label: "The map of the balancing authorities" }, { href: "/data/methods/authority_facts", label: "Method: every authority's own facts" }],
};

export const GUIDE_ENTRY: SetGuide = {
  can: "read a balancing authority's own facts, compare a fleet's share of capacity with its share of generation, and say whom an authority leans on and how clean its power is",
  grids: ["the Tennessee Valley Authority", "ERCOT", "CAISO", "any balancing authority of the lower 48"],
  tables: [OWN, PLAN, RET, GEN, CO2, TRADE, DEMAND, LL],
  skills: ["MW against MWh", "a share of a total", "capacity against generation", "net against gross exchange", "a ratio", "percentage points"],
  order: ["b1", "b2", "b6", "b3", "b4", "b5", "b7"],
  files: [A, E, C],
};

const tech = (g: string) => g.replace(/_/g, " ");

export async function build(): Promise<Built> {
  const a = open<Authority>(A);
  const e = open<Authority>(E);
  const c = open<Authority>(C);
  const nm = a.name;
  const cap = (g: string) => fig(A, ["owns", "capacity_mw", g], "MW");
  const total = fig(A, ["owns", "total_mw"], "MW");

  // ---------------------------------------------------------------- worked example: nuclear's share of what it owns
  const xn = cap("nuclear"), xs = calc("pct", xn, total, "%");
  const example: Question = {
    id: "bx", tables: [OWN],
    q: `How much generating capacity does the ${nm} hold in all, how much of it is nuclear, and what share is that?`,
    answer: [`In all `, total, ", nuclear ", xn, ", or ", xs, ` (EIA-860M of ${a.owns.vintage}).`],
    line: [xn, " / ", total, " x 100 = ", xs],
    steps: [["On /grid, the network view, Map: click the Tennessee Valley Authority and read Its own facts, What it owns; or open site/data/regions/authority/tva.json."],
      ["owns, total_mw is every operating generator EIA places in the authority, ", total, "; owns, capacity_mw, nuclear is ", xn, "."],
      ["Share: ", xn, " / ", total, " x 100 = ", xs, "."]],
    why: "An authority's capacity is the sum of the net summer capacity of the plants EIA places in it, so each fuel's part of it is a share of one total.",
  };

  // ---------------------------------------------------------------- b1: its largest plant
  const top = a.owns.largest_plants[0];
  const tp = fig(A, ["owns", "largest_plants", 0, "mw"], "MW"), tps = calc("pct", tp, total, "%");
  const q1: Question = {
    id: "b1", tables: [OWN],
    q: `Which is the ${nm}'s largest power plant, how much capacity does it have, and what share of the authority's capacity is that?`,
    answer: [`${top.name} (${top.state}, ${tech(top.technology_group)}): `, tp, " of ", total, ", or ", tps, "."],
    line: [tp, " / ", total, " x 100 = ", tps],
    steps: [["owns, largest_plants lists the ten largest plants from the largest: the first is ", `${top.name}, `, tp, "."],
      ["Share of owns, total_mw: ", tp, " / ", total, " x 100 = ", tps, "."]],
    why: "A few large plants hold much of an authority's capacity, so the loss of one of them on a cold morning is felt across the whole authority.",
  };

  // ---------------------------------------------------------------- b2: capacity against generation
  const gn = fig(A, ["burns", "share_pct", "nuclear"], "%"), gg = fig(A, ["burns", "share_pct", "natural_gas"], "%");
  const cn = calc("pct", cap("nuclear"), total, "%"), cg = calc("pct", cap("natural_gas"), total, "%");
  const [m0, m1] = a.burns.months.map(monthWords);
  const q2: Question = {
    id: "b2", tables: [OWN, GEN],
    q: `For the ${nm}, what share of its capacity is nuclear and what share is natural gas, and what share of its generation from ${m0} to ${m1} did each make? Which fleet runs harder?`,
    answer: ["Nuclear: ", cn, " of capacity, ", gn, " of generation. Natural gas: ", cg, " of capacity, ", gg, " of generation. ",
      gn.v / cn.v > gg.v / cg.v ? "Nuclear makes the larger share of generation for its share of capacity: it runs nearly every hour, gas plants run when they are needed." : "Natural gas makes the larger share of generation for its share of capacity in these months."],
    line: [cap("nuclear"), " / ", total, " x 100 = ", cn, "; ", cap("natural_gas"), " / ", total, " x 100 = ", cg, "; burns, share_pct: ", gn, " and ", gg],
    steps: [["Capacity shares from owns: ", cap("nuclear"), " and ", cap("natural_gas"), " of ", total, ": ", cn, " and ", cg, "."],
      [`Generation shares from burns, share_pct, over ${m0} to ${m1}: nuclear `, gn, ", natural gas ", gg, "."],
      ["Compare each fleet's share of generation with its share of capacity."]],
    why: "Capacity says what a fleet could make in an hour; generation says what it made. A fleet whose share of generation is above its share of capacity runs more of the year than the others.",
  };

  // ---------------------------------------------------------------- b3: the largest retirement planned
  const ri = argmax(a.coming.retirements.map((r) => r.mw)), rr = a.coming.retirements[ri];
  const rm = fig(A, ["coming", "retirements", ri, "mw"], "MW"), rc = cap(rr.technology_group), rs = calc("pct", rm, rc, "%");
  const q3: Question = {
    id: "b3", tables: [RET, OWN],
    q: `Of the retirements the ${nm}'s owners have planned, which year and fuel has the most megawatts, how many, and what share of the authority's operating ${tech(rr.technology_group)} capacity is that?`,
    answer: [`${rr.year}, ${tech(rr.technology_group)}: `, rm, ` (${rr.generators} generators) of `, rc, ", or ", rs, "."],
    line: [rm, " / ", rc, " x 100 = ", rs],
    steps: [["coming, retirements lists the planned retirements by year and fuel; the largest is ", `${rr.year}, ${tech(rr.technology_group)}, `, rm, "."],
      [`owns, capacity_mw, ${rr.technology_group}: `, rc, "."], ["Share: ", rm, " / ", rc, " x 100 = ", rs, "."]],
    why: "A planned retirement date is the owner's own, as EIA-860M reports it; it can move, but it says which part of the fleet the owner expects to close.",
  };

  // ---------------------------------------------------------------- b4: the largest addition planned
  const ai = argmax(a.coming.additions.map((r) => r.mw)), ar = a.coming.additions[ai];
  const am = fig(A, ["coming", "additions", ai, "mw"], "MW"), ac = cap(ar.technology_group), ash = calc("pct", am, ac, "%");
  const q4: Question = {
    id: "b4", tables: [PLAN, OWN],
    q: `Of the generators planned in the ${nm}, which year and fuel has the most megawatts, how many, and how large is that against its operating ${tech(ar.technology_group)} capacity today?`,
    answer: [`${ar.year}, ${tech(ar.technology_group)}: `, am, ` (${ar.generators} generators), or `, ash, " of today's ", ac, "."],
    line: [am, " / ", ac, " x 100 = ", ash],
    steps: [["coming, additions lists the planned generators by planned year and fuel; the largest is ", `${ar.year}, ${tech(ar.technology_group)}, `, am, "."],
      [`owns, capacity_mw, ${ar.technology_group}: `, ac, "."], ["Share: ", am, " / ", ac, " x 100 = ", ash, "."]],
    why: "Planned generators often slip or are cancelled, so a plan is read as what the owners intend, set against what already runs.",
  };

  // ---------------------------------------------------------------- b5: whom it leans on
  const pi = argmax(a.trades.partners.map((p) => p.exchange_gross_mwh)), pp = a.trades.partners[pi];
  const pn = fig(A, ["trades", "partners", pi, "net_import_mwh"], "MWh"), pg = fig(A, ["trades", "partners", pi, "exchange_gross_mwh"], "MWh");
  const pr = calc("pct", pn, pg, "%"), sh = fig(A, ["trades", "net_import_share_of_demand_pct"], "%");
  const q5: Question = {
    id: "b5", tables: [TRADE],
    q: `In ${a.trades.year}, with which neighbour did the ${nm} exchange the most power, what was its net import from that neighbour against the gross exchange, and what share of its demand were its net imports from all neighbours?`,
    answer: [`${pp.name} (${pp.code}): net import `, pn, " of a gross exchange of ", pg, ", or ", pr, ". From all neighbours, net imports were ", sh, " of demand."],
    line: [pn, " / ", pg, " x 100 = ", pr, "; trades, net_import_share_of_demand_pct = ", sh],
    steps: [["trades, partners lists the five largest partners by gross exchange; the largest is ", `${pp.code}, gross `, pg, ", net ", pn, " (above zero, power came in)."],
      ["Net against gross: ", pn, " / ", pg, " x 100 = ", pr, ". Near 100 percent the power ran one way nearly every hour."],
      ["trades, net_import_share_of_demand_pct: ", sh, "."]],
    why: "Gross exchange counts power both ways; net counts what was left after the two directions cancel, which is what the authority leaned on its neighbour for.",
  };

  // ---------------------------------------------------------------- b6: how clean, two grids side by side
  const ie = fig(E, ["burns", "co2", "intensity_kg_per_mwh"], "kg CO2 per MWh"), ic = fig(C, ["burns", "co2", "intensity_kg_per_mwh"], "kg CO2 per MWh");
  const ir = calc("ratio", ie, ic, "times");
  const q6: Question = {
    id: "b6", tables: [CO2, GEN],
    q: `Over ${m0} to ${m1}, how much CO2 did each MWh generated in ERCOT and in CAISO carry, by EIA's estimates, and ERCOT's is how many times CAISO's? Why does the ${nm}'s file give no figure?`,
    answer: ["ERCOT ", ie, ", CAISO ", ic, ": ERCOT's is ", ir, " CAISO's. ", `The ${nm}'s file says why it has none: ${a.burns.co2.why ?? "no estimate is held"}.`],
    line: [ie, " / ", ic, " = ", ir],
    steps: [["In site/data/regions/authority/erco.json and ciso.json: burns, co2, intensity_kg_per_mwh: ", ie, " and ", ic, "."],
      ["Divide: ", ie, " / ", ic, " = ", ir, "."],
      ["In tva.json, burns, co2, intensity_kg_per_mwh is empty and burns, co2, why gives the reason."]],
    why: "The carbon a MWh carries follows the mix: more coal and gas, more CO2. A blank with its reason is a fact too: the estimate is not held for that authority, which is not the same as zero.",
  };

  // ---------------------------------------------------------------- b7: its size and growth, against ERCOT
  const pk = fig(A, ["size", "peak_mw"], "MW"), ga = fig(A, ["size", "growth_since_2019_pct"], "%"), ge = fig(E, ["size", "growth_since_2019_pct"], "%");
  const gd = calc("diff", ge, ga, "percentage points"), le = fig(E, ["large_loads", "count"], "rows"), la = fig(A, ["large_loads", "count"], "rows");
  const q7: Question = {
    id: "b7", tables: [DEMAND, LL],
    q: `What was the ${nm}'s highest demand and when, how much did its demand grow from 2019 to ${a.size.growth_year}, and ERCOT's growth was how many points more? How many public large-load rows are placed in each?`,
    answer: ["Peak ", pk, ` at ${a.size.peak_local} local time (${a.size.tz}); growth since 2019 `, ga, ", ERCOT's ", ge, ": ", gd, " more. Public large-load rows: the TVA ", la, ", ERCOT ", le, "."],
    line: [ge, " - ", ga, " = ", gd],
    steps: [["size, peak_mw and peak_local in tva.json: ", pk, `, ${a.size.peak_local}.`], ["size, growth_since_2019_pct: the TVA ", ga, ", ERCOT ", ge, "."],
      ["Subtract: ", ge, " - ", ga, " = ", gd, "."], ["large_loads, count in each file: ", la, " and ", le, "."]],
    why: "Demand growth since 2019 is where new load shows first; the large-load rows are the public announcements the ERW has read, not every request an authority has received.",
  };

  return { example, questions: [q1, q2, q3, q4, q5, q6, q7] };
}
