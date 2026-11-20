// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): problem set "Where energy goes". Energy used by
// industry, by fuel and by state, every figure read from the committed page file site/data/industry.json (written by
// warehouse/derived/industry_page.py, method docs/methods/industry_page.md) with its pf| key (lib/pagefile.ts):
//   monthly          the industrial sector's consumption by source, month by month (EIA, Monthly Energy Review, Table 2.4)
//   industries       manufacturing's fuel by industry and census region, and each industry's electricity (EIA, 2022 MECS)
//   states_annual    each state's industrial consumption by source and year (EIA, State Energy Data System)
// The page that draws the file (/industry) is another machine's work; the questions name the file's fields, which are
// the page's figures. The month, the industries and the year are chosen by rules written beside them, never typed.
import type { Question } from "@/lib/problems";
import { calc, fig, monthWords, open, type Built, type Meta, type SetGuide } from "./common";

const F = "industry.json";
const MER = "eia_sector_energy_consumption_monthly", MECS = "eia_mecs_manufacturing", SEDS = "eia_seds_industrial_annual";
type Num = number | null;
type Industry = { naics: string; name: string; by_region: Record<string, Record<string, Num>>; electricity_mwh: Record<string, Record<string, Num>> };
type IndustryFile = {
  monthly: { unit: string; months: string[]; labels: Record<string, string>; by_source: Record<string, Num[]> };
  industries: { survey_year: number; ranked_3_digit: string[]; industries: Record<string, Industry> };
  states_annual: { years: string[]; states: Record<string, { consumption_tbtu: Record<string, Num[]> }> };
};

export const META: Meta = {
  slug: "where-energy-goes", title: "Where energy goes: industry, by fuel and by state",
  line: "The industrial sector's energy month by month and what electrical losses add, the manufacturing industries that use the most and on which fuels, a factory that makes its own power, and two states compared.",
  teacher: "About 45 minutes. Prerequisites: TBtu (a trillion British thermal units), a share, a ratio, the difference between a survey of factories and a count of a whole sector. Students read site/data/industry.json, the file the industry page draws, and the method note; every figure is EIA's as printed.",
  pages: [{ href: "/data/methods/industry_page", label: "Method: energy use by industry" }],
};

export const GUIDE_ENTRY: SetGuide = {
  can: "read the industrial sector's energy by source and by industry, tell end use from losses, and compare industries and states by a share and a ratio",
  grids: ["the United States, its four census regions and its states"],
  tables: [MER, MECS, SEDS],
  skills: ["TBtu", "end use against losses", "a share of a total", "a ratio of two years", "a survey against a sector"],
  order: ["i1", "i2", "i3", "i6", "i4", "i7", "i5"],
  files: [F],
};

export async function build(): Promise<Built> {
  const d = open<IndustryFile>(F);
  const mo = d.monthly, ind = d.industries;
  const mf = (src: string, j: number) => fig(F, ["monthly", "by_source", src, j], mo.unit);
  const inf = (code: string, region: string, fuel: string) => fig(F, ["industries", "industries", code, "by_region", region, fuel], "TBtu");
  const ele = (code: string, part: string) => fig(F, ["industries", "industries", code, "electricity_mwh", "us", part], "MWh");
  const nm = (code: string) => ind.industries[code].name;
  const yr = ind.survey_year;

  // the month: the newest the file holds a total for, and the same month a year before
  const j = mo.months.map((m, k) => ({ m, k })).filter((x) => typeof mo.by_source.total[x.k] === "number").at(-1)!.k;
  const jPrev = mo.months.indexOf(`${Number(mo.months[j].slice(0, 4)) - 1}${mo.months[j].slice(4)}`);
  const m0 = monthWords(mo.months[j]), m1 = monthWords(mo.months[jPrev]);
  const [first, second] = ind.ranked_3_digit;

  // ---------------------------------------------------------------- worked example: the first industry's natural gas
  const xg = inf(first, "us", "natural_gas"), xt = inf(first, "us", "total");
  const example: Question = {
    id: "ix", tables: [MECS],
    q: `In ${yr}, how much fuel did ${nm(first)} (NAICS ${first}) consume in the United States in all, how much of it was natural gas, and what share is that?`,
    answer: [`${nm(first)}: in all `, xt, ", natural gas ", xg, ", or ", calc("pct", xg, xt, "%"), "."],
    line: [xg, " / ", xt, " x 100 = ", calc("pct", xg, xt, "%")],
    steps: [[`In site/data/industry.json: industries, industries, ${first}, by_region, us: total and natural_gas.`], ["Total ", xt, "; natural gas ", xg, "."],
      ["Share: ", xg, " / ", xt, " x 100 = ", calc("pct", xg, xt, "%"), "."]],
    why: `A survey of factories (EIA's Manufacturing Energy Consumption Survey of ${yr}) counts each fuel a plant uses, so an industry's total can be split by fuel.`,
  };

  // ---------------------------------------------------------------- i1: end use and losses in the newest month
  const tot = mf("total", j), end = mf("end_use_total", j), loss = mf("electrical_system_losses", j), lessEnd = calc("diff", tot, end, mo.unit);
  const q1: Question = {
    id: "i1", tables: [MER],
    q: `In ${m0}, the newest month of the file, how much energy did the industrial sector consume in all, how much was end use, and how far apart are they? Compare with the sector's share of electrical system losses.`,
    answer: [`${m0}: in all `, tot, ", end use ", end, ": apart by ", lessEnd, "; the losses the file gives are ", loss, "."],
    line: [tot, " - ", end, " = ", lessEnd, "; electrical_system_losses = ", loss],
    steps: [[`In site/data/industry.json: monthly, by_source, at position ${j} of monthly, months (${mo.months[j]}).`], ["total ", tot, "; end_use_total ", end, "."],
      ["Subtract: ", tot, " - ", end, " = ", lessEnd, "; electrical_system_losses, ", loss, `, is ${mo.labels.electrical_system_losses}.`]],
    why: "Electricity loses energy on its way from the power plant: the sector's total counts its share of those losses, and its end use counts only what reached it.",
  };

  // ---------------------------------------------------------------- i2: a year apart
  const totPrev = mf("total", jPrev);
  const q2: Question = {
    id: "i2", tables: [MER],
    q: `How much energy did the industrial sector consume in ${m0} and in ${m1}, a year before, and the first is how many times the second?`,
    answer: [`${m0} `, tot, `, ${m1} `, totPrev, ": ", calc("ratio", tot, totPrev, "times"), "."],
    line: [tot, " / ", totPrev, " = ", calc("ratio", tot, totPrev, "times")],
    steps: [[`monthly, by_source, total at positions ${j} (${mo.months[j]}) and ${jPrev} (${mo.months[jPrev]}).`], ["Divide: ", tot, " / ", totPrev, " = ", calc("ratio", tot, totPrev, "times"), "."]],
    why: "A month is set against the same month of the year before, so the season is the same on both sides and only the year differs.",
  };

  // ---------------------------------------------------------------- i3: the two largest industries
  const at1 = inf(first, "us", "total"), at2 = inf(second, "us", "total");
  const q3: Question = {
    id: "i3", tables: [MECS],
    q: `The industries ranked by fuel consumption in ${yr}: which two used the most, how much did each use, and the first's is how many times the second's?`,
    answer: [`${nm(first)} `, at1, `, ${nm(second)} `, at2, ": ", calc("ratio", at1, at2, "times"), "."],
    line: [at1, " / ", at2, " = ", calc("ratio", at1, at2, "times")],
    steps: [[`industries, ranked_3_digit, lists the industries from the largest: ${first} (${nm(first)}) and ${second} (${nm(second)}) first.`],
      ["Each one's by_region, us, total: ", at1, " and ", at2, "."], ["Divide: ", at1, " / ", at2, " = ", calc("ratio", at1, at2, "times"), "."]],
    why: "A few industries that turn raw materials into chemicals, fuels, paper and metals use most of manufacturing's energy; most others use far less.",
  };

  // ---------------------------------------------------------------- i4: the second industry's "other" fuels
  const so = inf(second, "us", "other"), st = inf(second, "us", "total");
  const q4: Question = {
    id: "i4", tables: [MECS],
    q: `${nm(second)} in ${yr}: how much of its fuel does the survey count as "other", of how much in all, and what share is that?`,
    answer: ["Other ", so, " of ", st, ", or ", calc("pct", so, st, "%"), "."],
    line: [so, " / ", st, " x 100 = ", calc("pct", so, st, "%")],
    steps: [[`industries, industries, ${second}, by_region, us: other `, so, ", total ", st, "."], ["Share: ", so, " / ", st, " x 100 = ", calc("pct", so, st, "%"), "."]],
    why: `The survey names a column for each common fuel; "other" holds what has no column of its own${second === "324" ? ", which for a refinery includes fuels it makes from its own crude oil" : ""}, so a large "other" is not an unknown.`,
  };

  // ---------------------------------------------------------------- i5: a factory that makes its own power
  const on = ele(first, "elec_onsite_generation"), net = ele(first, "elec_net_demand");
  const q5: Question = {
    id: "i5", tables: [MECS],
    q: `${nm(first)} in ${yr}: how much electricity did its plants generate on site, what was its net demand for electricity, and what share of the net demand is the on-site generation?`,
    answer: ["On site ", on, ", net demand ", net, ": ", calc("pct", on, net, "%"), "."],
    line: [on, " / ", net, " x 100 = ", calc("pct", on, net, "%")],
    steps: [[`industries, industries, ${first}, electricity_mwh, us: elec_onsite_generation `, on, "; elec_net_demand ", net, "."], ["Share: ", on, " / ", net, " x 100 = ", calc("pct", on, net, "%"), "."]],
    why: "Many large plants burn fuel to make both steam and electricity (cogeneration), so part of their electricity never passes through the grid and is not in the utilities' sales.",
  };

  // ---------------------------------------------------------------- i6: one region's share of an industry
  const sr = inf(first, "south", "total");
  const q6: Question = {
    id: "i6", tables: [MECS],
    q: `${nm(first)} in ${yr}: how much fuel did its plants in the South census region consume, of how much in the United States, and what share is that?`,
    answer: ["The South ", sr, " of ", xt, ", or ", calc("pct", sr, xt, "%"), "."],
    line: [sr, " / ", xt, " x 100 = ", calc("pct", sr, xt, "%")],
    steps: [[`industries, industries, ${first}, by_region: south, total, `, sr, "; us, total, ", xt, "."], ["Share: ", sr, " / ", xt, " x 100 = ", calc("pct", sr, xt, "%"), "."]],
    why: "An industry settles where its raw materials, its fuel and its customers are, so one census region can hold most of an industry's energy use.",
  };

  // ---------------------------------------------------------------- i7: two states
  const sa = d.states_annual;
  const tx = sa.states.TX.consumption_tbtu.total, la = sa.states.LA.consumption_tbtu.total;
  const y = sa.years.map((v, k) => ({ v, k })).filter((x) => typeof tx[x.k] === "number" && typeof la[x.k] === "number").at(-1)!;
  const T = fig(F, ["states_annual", "states", "TX", "consumption_tbtu", "total", y.k], "TBtu"), Lz = fig(F, ["states_annual", "states", "LA", "consumption_tbtu", "total", y.k], "TBtu");
  const q7: Question = {
    id: "i7", tables: [SEDS],
    q: `In ${y.v}, the newest year the file holds for both, how much energy did the industrial sector consume in Texas and in Louisiana, and Texas's is how many times Louisiana's?`,
    answer: [`${y.v}: Texas `, T, ", Louisiana ", Lz, ": ", calc("ratio", T, Lz, "times"), "."],
    line: [T, " / ", Lz, " = ", calc("ratio", T, Lz, "times")],
    steps: [[`states_annual, states, TX and LA, consumption_tbtu, total, at position ${y.k} of states_annual, years (${y.v}).`], ["Texas ", T, ", Louisiana ", Lz, "."],
      ["Divide: ", T, " / ", Lz, " = ", calc("ratio", T, Lz, "times"), ". The State Energy Data System counts the whole industrial sector (farms, mines and construction included), not only factories."]],
    why: "A state's industrial energy follows its refineries and chemical plants more than its population, so a smaller state can use a large share.",
  };

  return { example, questions: [q1, q2, q3, q4, q5, q6, q7] };
}
