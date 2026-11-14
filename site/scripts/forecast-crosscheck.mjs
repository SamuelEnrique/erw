// Session 4209 (chain 239): the forecast model against published impact studies (docs/methods/forecast.md, section 9).
// Each study's own project (technology, state, MW, cost and its dollar year) runs through lib/forecast.ts at the tool's
// defaults otherwise; the study's published statewide figures stand beside the model's. The studies' local content is
// their own (the developer's spending plan), the model's is JEDI's default: that is the first reason for a difference.
//
//   node site/scripts/forecast-crosscheck.mjs <nlr_jedi_multipliers.csv> [--json out.json]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const F = await import("../lib/forecast.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = {
  jediCosts: data("jedi_costs.json"), eiaCapex: data("eia_capex.json"), deflator: data("deflator.json"), capacity: data("capacity_factors.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), property: data("property_rules.json"), taxable: data("jedi_taxable.json"), gas: data("gas.json"),
};

function readRows(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const at = (k) => head.indexOf(k);
  return lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
    .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
}

// Each study: what it says, where, and the inputs it states. Figures are the study's statewide totals.
export const STUDIES = [
  {
    id: "jayhawk_ks", title: "Jayhawk Wind Energy Project (Bourbon and Crawford Counties, Kansas): economic development report, November 2019",
    url: "https://fortscott.biz/wp-content/uploads/2019/12/Jayhawk-Wind-Economic-Development-Report-Final-November-20191.pdf", request: 50,
    method: "JEDI Wind with 2017 IMPLAN state multipliers and the project's own spending and local shares; 25-year life",
    tech: "land_based_wind", state: "ks", mw: 195, cost_usd: 250e6, cost_year: 2019, cost_words: "an investment of almost $250 million", life: 25,
    published: { "construction:total:jobs": 634, "construction:onsite:jobs": 190, "construction:supply_chain:jobs": 321, "construction:induced:jobs": 123,
      "construction:total:earnings": 36.7e6, "construction:total:output": 98.2e6, "operations:total:jobs": 43, "operations:onsite:jobs": 9,
      "operations:total:earnings": 2.2e6, "operations:total:output": 7.5e6 },
    published_words: "634 (190 direct) local jobs during construction for the State of Kansas; 43 (9 direct) long-term jobs for the State of Kansas; over $36.7 million in local earnings during construction for the State of Kansas; over $2.2 million in local long-term earnings; over $98.2 million in local output during construction; over $7.5 million in local long-term output",
    dollars_of: 2019,
  },
  {
    id: "glendive_mt", title: "Glendive Wind (Prairie County, Montana), NextEra Energy Resources: economic impact summary of a 2024 study by Strategic Economic Research",
    url: "https://www.nexteraenergyresources.com/content/dam/neer/us/en/microsites/PDF/glendive-prairie-econ-impact.pdf", request: 49,
    method: "IMPLAN multipliers with NREL's JEDI model, statewide",
    tech: "land_based_wind", state: "mt", mw: 800, cost_usd: 1e9, cost_year: 2024, cost_words: "$1 billion investment in Prairie County; up to 800 megawatts", life: 30,
    published: { "construction:total:jobs": 400 },
    published_words: "Approx. 400 construction jobs in the state of Montana",
    dollars_of: 2024,
  },
  {
    id: "ohio_pv_low", title: "Measuring the Economic Impacts of Utility-Scale Solar in Ohio, Ohio University (Voinovich School), 31 July 2020: the low scenario",
    url: "https://static1.squarespace.com/static/56a8596376d99c0164fc16bd/t/5f50094e9c0ff3029d54bc6c/1599080786155/Measuring+the+Economic+Impacts+of+Utility-Scale+Solar+in+Ohio+---+FINAL%2C+7.31.2020.pdf", request: 54,
    method: "JEDI PV updated with 2018 IMPLAN multipliers and NREL's Q1 2018 one-axis tracker utility cost benchmark; 80 percent Ohio labor and 30 percent Ohio materials; DC capacity; 2018 dollars; 40-year life",
    tech: "utility_pv", state: "oh", mw_dc: 2500, cost_usd: 3592192939, cost_year: 2018, cost_words: "Project Construction or Installation Cost, Low (2.5 GW): $3,592,192,939", life: 40,
    published: { "construction:total:jobs": 18039, "construction:onsite:jobs": 8536, "operations:total:jobs": 207, "construction:total:output": 3.2e9, "property:year": 22.5e6 },
    published_words: "a total of 18,039 one-time construction phase jobs, and 207 annual operations and maintenance (O&M) phase jobs; 8,536 direct construction jobs; roughly $3.2B construction phase economic impacts; up to $22.5M in annual tax revenues",
    dollars_of: 2018,
  },
  {
    id: "indiana_wind", title: "Economic Impacts from Indiana's First 1,000 Megawatts of Wind Power, NREL/TP-6A20-60914 (Tegen, Keyser and Flores-Espino, 2014)",
    url: "https://docs.nlr.gov/docs/fy14osti/60914.pdf", request: 78,
    method: "JEDI Wind with the seven projects' own expenditures and local shares (1,339 MW built 2008 to 2011; about 20 percent of construction spending and 40 percent of O&M in Indiana), results per 1,000 MW in 2010 real dollars",
    tech: "land_based_wind", state: "in", mw: 1000, cost_usd: 2487e6 / 1.339, cost_year: 2010, cost_words: "Table 3: construction expenditure USD 2,487 million for the 1,339 MW analyzed (equipment 1,830, materials 331, construction labor 159, development and other 167), scaled to 1,000 MW", life: 20,
    published: { "construction:total:jobs": 4400, "operations:total:jobs": 260, "property:year": 8e6 },
    published_words: "Supported employment totaling more than 4,400 full-time-equivalent (FTE) jobs in Indiana during the construction periods; Supports approximately 260 ongoing Indiana jobs; Generates more than $8 million in annual property taxes (per 1,000 MW)",
    dollars_of: 2010,
  },
  {
    id: "rush_creek_co", title: "Economic Impacts from Wind Energy in Colorado, Case Study: Rush Creek Wind Farm, NREL/TP-5000-73659 (2019)",
    url: "https://docs.nlr.gov/docs/fy19osti/73659.pdf", request: 80,
    method: "JEDI Wind with the project's known costs from Xcel Energy's PUC filings and JEDI's default shares for the rest; Vestas's Colorado turbine factories in the supply chain; 2018 dollars",
    tech: "land_based_wind", state: "co", mw: 600, cost_usd: 698137648, cost_year: 2018, cost_words: "Table 11: Total Capital Cost $698,137,648; Installed Project Cost $1,164/kW; 600 MW", life: 25,
    published: { "construction:total:jobs": 2970, "construction:onsite:jobs": 290, "construction:supply_chain:jobs": 1840, "construction:induced:jobs": 840, "operations:total:jobs": 180 },
    published_words: "The Rush Creek Wind Farm construction supports an estimated 2,970 FTE jobs [...] the 290 FTEs include 245 FTEs for on-site construction and interconnection labor [...] 1,840 FTEs were local revenue, turbine, and supply chain workers [...] an additional 840 FTE-induced jobs; Supports approximately 180 jobs in Colorado annually",
    dollars_of: 2018,
  },
  {
    id: "wyoming_gas", title: "Estimated Economic Development Impacts from New Generation and Transmission in Wyoming and Colorado, NREL/TP-6A20-57411 (Lantz, Tegen and others, March 2013): the 225 MW gas plant, Wyoming's share",
    url: "https://docs.nlr.gov/docs/fy13osti/57411.pdf", request: 107,
    method: "JEDI Natural Gas with IMPLAN 2008 state multipliers and the Wyoming Infrastructure Authority's local shares (24 percent of construction and 39 percent of O&M spending in Wyoming, Table C3); jobs averaged over a three-year build (the cumulative figure is three times the average); dollar year not stated, taken as 2012",
    tech: "natural_gas", state: "wy", mw: 225, cost_usd: 280e6, cost_year: 2012, cost_words: "Table 1: installed cost $280 million; a natural gas-fired generation facility with a nameplate capacity of 225 MW", life: 20,
    published: { "construction:total:jobs": 191 * 3, "construction:onsite:jobs": 103 * 3, "construction:supply_chain:jobs": 47 * 3, "construction:induced:jobs": 40 * 3,
      "operations:total:jobs": 36, "operations:onsite:jobs": 11, "sales:total": 10.2e6 },
    published_words: "Table 6 (annual average over three years, Wyoming, gas): project development and onsite labor 103, turbine, power generation and equipment supply chain 47, induced 40, total 191; Table 7 (Wyoming, gas): onsite 11, supply chain 16, induced 9, total 36; Table 2: Wyoming sales/use tax revenue, gas, $10,200 thousand (6 percent on capital goods and materials)",
    dollars_of: 2012,
  },
  {
    id: "wyoming_wind", title: "The same study: the 900 MW wind plant, Wyoming's share (turbines made in Colorado)",
    url: "https://docs.nlr.gov/docs/fy13osti/57411.pdf", request: 107,
    method: "JEDI Wind with IMPLAN 2008 multipliers; turbines, blades and nacelles from Colorado (0 percent of turbine spending in Wyoming, 18 percent of all construction spending, Table C1); a 48.5 percent capacity factor for the generation tax; dollar year taken as 2012",
    tech: "land_based_wind", state: "wy", mw: 900, cost_usd: 1350e6, cost_year: 2012, cost_words: "Table 1: installed cost $1,350 million; a 900-MW wind power plant", life: 20, cf: 0.485,
    published: { "construction:total:jobs": 832 * 3, "construction:onsite:jobs": 151 * 3, "construction:supply_chain:jobs": 569 * 3, "construction:induced:jobs": 112 * 3,
      "operations:total:jobs": 217, "operations:onsite:jobs": 41, "sales:total": 74.2e6, "property:year4": 3.8e6 },
    published_words: "Table 6 (Wyoming, wind): onsite 151, supply chain 569, induced 112, total 832 a year over three years; Table 7 (Wyoming, wind): onsite 41, supply chain 121, induced 55, total 217; Table 2: Wyoming sales/use tax, wind, $74,200 thousand; Table 3: generation tax, wind, $3,800 thousand a year (the $1/MWh tax at a 48.5 percent net capacity factor)",
    dollars_of: 2012,
  },
  {
    id: "texas_wind_1000", title: "Economic Development Impact of 1,000 MW of Wind Energy in Texas, NREL/TP-6A20-50400 (Reategui and Hendrickson, August 2011)",
    url: "https://docs.nlr.gov/docs/fy11osti/50400.pdf", request: 121,
    method: "JEDI Wind with costs and local shares from Texas projects' data (Tables 2 to 5); results in 2009 real dollars; out-of-state workers excluded; statewide",
    tech: "land_based_wind", state: "tx", mw: 1000, cost_usd: 2e9, cost_year: 2009, cost_words: "This study assumes that 1,000 MW of wind energy represents approximately $2 billion in investment (Table 2: installed project cost $1,650-$2,200/kW, 2009 dollars)", life: 20,
    published: { "construction:total:jobs": 2100, "construction:onsite:jobs": 600, "construction:supply_chain:jobs": 1000, "construction:induced:jobs": 500,
      "operations:total:jobs": 240, "operations:onsite:jobs": 60 },
    published_words: "Generated over 2,100 full-time-equivalent (FTE) jobs within the state of Texas; Currently supports approximately 240 permanent Texas jobs; Figure 3: construction phase over 600 FTE jobs (on-site), over 1,000 FTE jobs (local revenue, turbine and supply chain), over 500 FTE jobs (induced); operational phase 60 long-term jobs, 100 jobs, 80 jobs",
    dollars_of: 2009,
  },
  {
    id: "maine_wind_1000", title: "Maine Economic Impacts from 1,000 MW of New Wind Development, Wind Powering America fact sheet, NREL (Lantz and Tegen), DOE/GO-102008-2672, October 2008",
    url: "https://docs.nlr.gov/docs/fy09osti/44146.pdf", request: 122,
    method: "JEDI Wind with inputs from interviews with Maine contacts (developers, contractors, assessors); 2007 constant dollars; construction plus 20 years; totals only (the sheet's direct category is not JEDI's on-site line)",
    tech: "land_based_wind", state: "me", mw: 1000, cost_usd: 1980e6, cost_year: 2007, cost_words: "Data Inputs: Construction Cost $1,980/kW; Operations and Maintenance $24.70/kW/yr", life: 20,
    published: { "construction:total:jobs": 3896, "operations:total:jobs": 540 },
    published_words: "New Local Jobs During Construction: 3,896; New Local Long-term Jobs: 540 (construction phase 2,042 direct and 1,854 indirect and induced; operational phase 254 and 286)",
    dollars_of: 2007,
  },
  {
    id: "georgia_pv_tronox", title: "Feasibility Study of Economics and Performance of Solar Photovoltaics at the Tronox Facility in Savannah, Georgia, NREL/TP-7A30-57958 (2013)",
    url: "https://docs.nlr.gov/docs/fy13osti/57958.pdf", request: 170,
    method: "JEDI PV at state level (Georgia, utility, fixed mount); every installation cost line 100 percent purchased in the state, modules, inverters, mounting and electrical not made there; 2012 dollars",
    tech: "utility_pv", state: "ga", mw_dc: 8.5, cost_usd: 29698320, cost_year: 2012, cost_words: "Total Project Size - DC Nameplate Capacity (kW) 8,500.0; Installed System Cost $29,698,320; Money Value (Dollar Year) 2012", life: 25,
    published: { "construction:total:jobs": 235.4, "construction:onsite:jobs": 92.2, "construction:supply_chain:jobs": 84.2, "construction:induced:jobs": 59.0, "operations:total:jobs": 3.2, "operations:onsite:jobs": 2.0 },
    published_words: "Total Impacts 235.4 (construction); Subtotal 92.2 (project development and on-site); Subtotal 84.2 (module and supply chain); Induced Impacts 59.0; operations: Total Impacts 3.2; PV Project Labor Only 2.0",
    dollars_of: 2012,
  },
  {
    id: "new_york_pv_lackawanna", title: "Feasibility Study of Economics and Performance of Solar Photovoltaics at the Former Bethlehem Steel Plant Brownfield Site in Lackawanna, New York, NREL/TP-7A40-58194 (2013)",
    url: "https://docs.nlr.gov/docs/fy13osti/58194.pdf", request: 171,
    method: "JEDI PV at state level (New York, utility, single-axis tracking); installation cost lines 100 percent purchased in the state, equipment not made there; 2012 dollars",
    tech: "utility_pv", state: "ny", mw_dc: 2.0, cost_usd: 6700000, cost_year: 2012, cost_words: "Project Size - DC Nameplate Capacity (KW) 2,000.0; Installed System Cost $6,700,000; Dollar Year 2012", life: 25,
    published: { "construction:total:jobs": 49.1, "construction:onsite:jobs": 18.6, "construction:supply_chain:jobs": 17.9, "construction:induced:jobs": 12.6, "operations:total:jobs": 0.7, "operations:onsite:jobs": 0.5 },
    published_words: "the total proposed system is estimated to support 49.1 direct and indirect jobs per year for the duration of the procurement and construction period; Subtotal 18.6; Subtotal 17.9; Induced Impacts 12.6; operations Total Impacts 0.7; PV Project Labor Only 0.5",
    dollars_of: 2012,
  },
  {
    id: "mississippi_pv_kerr_mcgee", title: "Feasibility Study of Economics and Performance of Solar Photovoltaics at the Kerr McGee Site in Columbus, Mississippi, NREL/TP-7A30-57251 (2013)",
    url: "https://docs.nlr.gov/docs/fy13osti/57251.pdf", request: 172,
    method: "JEDI PV at state level (Mississippi, large commercial application, not utility); installation lines 100 percent purchased in the state; 2010 dollars (the subagent's read of the dollar year)",
    tech: "utility_pv", state: "ms", mw_dc: 5.0, cost_usd: 13950000, cost_year: 2010, cost_words: "Total Project Size - DC Nameplate Capacity (kW) 5,000; Project Construction or Installation Cost $13,950,000; Base Installed System Cost ($/kWDC) $2,795", life: 30,
    published: { "construction:total:jobs": 141.2, "construction:onsite:jobs": 55.6, "construction:supply_chain:jobs": 57.9, "construction:induced:jobs": 27.7, "operations:total:jobs": 1.5, "operations:onsite:jobs": 0.9 },
    published_words: "Total Impacts 141.2 (construction); 55.6 on-site; 57.9 supply chain; 27.7 induced; operations Total Impacts 1.5; PV Project Labor Only 0.9",
    dollars_of: 2010,
  },
  {
    id: "colorado_pv_south_spur", title: "Economic Impact Analysis of the South Spur Solar Project, Strategic Economic Research (Loomis, Loomis, Thankan) for Bechtel, 2025, hosted by Yuma County, Colorado",
    url: "https://yumacounty.net/wp-content/uploads/2025/08/South-Spur-Solar-Full-Report.pdf", request: 187,
    method: "IMPLAN, 2022 State of Colorado dataset, with Bechtel's cost estimates and in-state shares (not published); statewide; dollar year not stated (taken as 2025, the report's year); an optional 79 MW battery may or may not be in the investment",
    tech: "utility_pv", state: "co", mw: 158, cost_usd: 173e6, cost_year: 2025, cost_words: "a 158-megawatt alternating current (MWac) utility-scale solar powered-electric generation facility [...] The total Project represents an investment in excess of $173 million.", life: 35,
    published: { "construction:total:jobs": 326, "construction:onsite:jobs": 172, "construction:supply_chain:jobs": 86, "construction:induced:jobs": 68, "operations:total:jobs": 17.3, "operations:onsite:jobs": 3.0 },
    published_words: "326 new local jobs during construction for the State of Colorado; 17.3 new local long-term jobs for the State of Colorado (Table 5.1: construction 172 direct, 86 indirect, 68 induced; operations 3.0 onsite, 9.2 indirect, 5.1 induced)",
    dollars_of: 2025,
  },
  // ---- session 6004 (chain 270, samueloldlaptop, 14 November 2026): one study per technology per region where one was readable.
  // "request" names the chain's read (two read-only subagents of session 6000; nc, il, la and the geothermal guide read again by this chain).
  {
    id: "nc_wind_nrel", title: "Economic Benefits, Carbon Dioxide (CO2) Emissions Reductions, and Water Conservation Benefits from 1,000 Megawatts (MW) of New Wind Power in North Carolina, NREL Wind Powering America (Lantz and Tegen), March 2009, NREL/FS-500-44916",
    url: "https://docs.nlr.gov/docs/fy09osti/44916.pdf", request: "s6004 (spot-checked)", region: "Southeast",
    method: "JEDI Wind, North Carolina statewide, 2007 constant dollars, state-specific inputs from interviews",
    tech: "land_based_wind", state: "nc", mw: 1000, cost_usd: 1650e6, cost_year: 2007, cost_words: "Data Inputs: Construction Cost $1,650/kW; O&M $24.70/kW", life: 20,
    published: { "construction:total:jobs": 2989, "construction:onsite:jobs": 1628, "operations:total:jobs": 457, "operations:onsite:jobs": 243 },
    published_words: "Construction Phase: 1,628 new jobs [direct]; Indirect and Induced Impacts: Construction Phase: 1,361 new jobs; Operational Phase: 243 new long-term jobs [direct]; New Local Jobs During Construction: 2,989; New Local Long-term Jobs: 457",
    dollars_of: 2007,
  },
  {
    id: "livingston_il", title: "Economic Impact Analysis for Livingston County Wind Project in Livingston County, Illinois, Strategic Economic Research for EDF Renewables, November 2021 (the developer's report)",
    url: "https://www.edf-re.com/wp-content/uploads/Livingston-County-Wind-refresh-11.29.21.pdf", request: "s6004 (spot-checked)", region: "Midwest",
    method: "JEDI Wind (W6-28-19) with 2019 State of Illinois IMPLAN multipliers and the developer's in-state shares (not printed); the cost's dollar year is not stated (taken as 2021, the report's year)",
    tech: "land_based_wind", state: "il", mw: 255, cost_usd: 378e6, cost_year: 2021, cost_words: "The Project represents an investment of $378 million in Livingston County", life: 25,
    published: { "construction:total:jobs": 1277, "construction:onsite:jobs": 226, "construction:supply_chain:jobs": 715, "construction:induced:jobs": 336,
      "construction:total:earnings": 85122945, "construction:total:output": 208668268, "operations:total:jobs": 61, "operations:onsite:jobs": 15,
      "operations:total:earnings": 3621803, "operations:total:output": 12800879 },
    published_words: "new local jobs created or retained during construction total [...] 1,277 for the State of Illinois. New local long-term jobs created from the Project total [...] 61 for the State of Illinois. [Table 3: direct 226, indirect 715, induced 336; operations 15, 23, 23.] new local earnings during construction total [...] over $85.1 million for the State of Illinois [...] new local long-term output totals [...] over $12.8 million for the State of Illinois",
    dollars_of: 2021,
  },
  {
    id: "corona_nm", title: "Report on the Economic and Fiscal Impacts of the Corona Wind Projects, New Mexico, Moss Adams LLP for Pattern Development, 28 February 2018 (the developer's report)",
    url: "https://patternenergy.com/wp-content/uploads/2021/09/final_fiscal_and_economic_impact_study.pdf", request: "s6004", region: "Southwest",
    method: "direct construction jobs from the developer's labor hours (2,080 hours a job), every worker wherever from (356 of the 1,186 local to three counties); output by IMPLAN 2015 New Mexico for three counties only (not compared); no indirect or induced jobs",
    tech: "land_based_wind", state: "nm", mw: 2200, cost_usd: 2.4e9, cost_year: 2018, cost_words: "approximately $2.4 billion in capital investment for the development of the Corona Wind Projects (dollar year not stated)", life: 30,
    published: { "construction:onsite:jobs": 1186, "operations:onsite:jobs": 94 },
    published_words: "creating an estimated 1,186 total jobs during construction, with an estimated 356 of those jobs sourced from local labor resources [...] approximately 94 full-time personnel with a payroll estimated to be approximately $4.5 million per year",
    dollars_of: 2018,
  },
  {
    id: "lsu_la_cc", title: "Moving to the Front of the Lines: The Economic Impact of Independent Power Plant Development in Louisiana, Dismukes, Mesyanzhinov and Olatubi, LSU Center for Energy Studies, October 2001 (Table 4.1's combined cycle plant, Tables 9 and 11)",
    url: "https://www.lsu.edu/ces/publications/2001/ipp_study_final.pdf", request: "s6004 (spot-checked)", region: "Southeast",
    method: "input-output model, Louisiana statewide, 2000 dollars, construction as one year; a construction spending profile with many inputs bought outside Louisiana (direct construction output USD 113.3 million of the USD 360 million cost)",
    tech: "natural_gas", state: "la", mw: 600, cost_usd: 360e6, cost_year: 2000, cost_words: "Table 4.1: Combined Cycle, Assumed Capacity 600 MW, Assumed Installed Cost/kW $600 [600 x 600,000 kW; the tables' values are in 2000 dollars]", life: 30,
    published: { "construction:total:jobs": 419, "construction:onsite:jobs": 216, "construction:supply_chain:jobs": 87, "construction:induced:jobs": 116,
      "construction:total:earnings": 13224111, "construction:total:output": 128539833, "operations:total:jobs": 66, "operations:onsite:jobs": 30,
      "operations:total:earnings": 3148415, "operations:total:output": 81235815 },
    published_words: "Table 9: Labor Income 7,576,048 / 2,827,361 / 2,820,702 / 13,224,111; Output 113,282,247 / 7,402,114 / 7,855,472 / 128,539,833; Employment 216 / 87 / 116 / 419. Table 11 operations: Employment 30 / 8 / 28 / 66; Labor Income total 3,148,415; Output total 81,235,815. All values, except employment, are in 2000 dollars",
    dollars_of: 2000,
  },
  {
    id: "msu_mi_gas", title: "The Economic Impact of Replacing Coal with Natural Gas for Electricity Production, Knudson, Michigan State University Strategic Marketing Institute Working Paper 01-0811, August 2011 (Table 1, plant construction)",
    url: "https://archive.lib.msu.edu/eres/open/naturalgaseconomicimpactstudy.pdf", request: "s6004", region: "Midwest",
    method: "IMPLAN, Michigan statewide, 2011 dollars; a fleet of about four 250 MW plants a year (1,000 MW), every dollar of spending treated as spent in Michigan (direct output equals the cost); direct is IMPLAN's direct effect, not on-site labor alone",
    tech: "natural_gas", state: "mi", mw: 1000, cost_usd: 1125e6, cost_year: 2011, cost_words: "The cost of installing new gas equipment is $1.12 million per megawatt (MW). Table 1 Plant Construction direct output per year $1,125.0 million", life: 30,
    published: { "construction:total:jobs": 17346, "construction:onsite:jobs": 9094, "construction:total:output": 2218.2e6 },
    published_words: "Table 1: Summary of the Economic Impact of Construction, Scenario I: Plant Construction, Output Per Year (Millions of $) Direct $1,125.0, Total $2,218.2; Employment Direct 9,094, Total 17,346. Output is measured in 2011 dollars",
    dollars_of: 2011,
  },
  {
    id: "jedi_geo_co", title: "Jobs and Economic Development Impact (JEDI) Model Geothermal User Reference Guide, Johnson, Augustine and Goldberg, NREL/TP-6A20-55781, 2012: the worked example of Figure 1 (a 30 MW net binary plant in Colorado, 2010)",
    url: "https://docs.nlr.gov/docs/fy12osti/55781.pdf", request: "s6004 (spot-checked)", region: "West",
    method: "JEDI Geothermal (simple model) with its default Colorado shares, 2010 dollars: JEDI's own example, so a check of the tool's later JEDI multipliers and its cost scaling, not an independent study",
    tech: "geothermal", state: "co", mw: 30, cost_usd: 106947804, cost_year: 2010, cost_words: "Nominal Plant Size (MW net output) 30.0; Installed Project Cost ($/kW) $3,565; Installed Project Cost $106,947,804; Money Value (Dollar Year) 2010", life: 30,
    published: { "construction:total:jobs": 432, "construction:onsite:jobs": 223, "construction:supply_chain:jobs": 128, "construction:induced:jobs": 81,
      "construction:total:earnings": 26.12e6, "construction:total:output": 61.44e6, "operations:total:jobs": 24, "operations:onsite:jobs": 14,
      "operations:total:earnings": 2.39e6, "operations:total:output": 5.22e6 },
    published_words: "432 full-time equivalent (FTE) jobs are supported, generating over $26 million in earnings and over $61 million in total economic activity during project development and construction. These include a total of 223 FTE jobs from project development [...] 128 from the turbine and supply chain, and 81 from induced impacts [...] 14 full-time operations and maintenance jobs [...] for a total of 24",
    dollars_of: 2010,
  },
  {
    id: "killingly_ct", title: "Killingly Energy Center: An Analysis of Need and Economic & Environmental Impacts, PA Consulting Group for NTE Connecticut, 2016 (Appendix B of the Connecticut Siting Council Docket 470 application)",
    url: "https://portal.ct.gov/-/media/csc/1_dockets-medialibrary/media_do400-499/docket470/application_reload/volume2/appendixbeconomicpdf.pdf?rev=67d10ccb5cbc4ab986777810d2e5f3ce&hash=A839150DA3E87986B1E92484ED24E8E9", request: "s6006 (spot-checked)", region: "Northeast",
    method: "JEDI natural gas with Connecticut's in-state shares (26 percent of the construction cost spent in Connecticut: no generating equipment, 65 percent of the plant's construction labor), Connecticut statewide; jobs per year 2017 to 2020 added here into job-years; the dollar year is not stated (taken as 2016, the report's year); the ratepayer savings lines left out",
    tech: "natural_gas", state: "ct", mw: 500, cost_usd: 537e6, cost_year: 2016, cost_words: "KEC's total equipment and construction costs are projected to be $537 million [...] KEC is a planned 500 MW natural gas-fired electric generating facility", life: 30,
    published: { "construction:total:jobs": 1132, "construction:onsite:jobs": 599, "construction:total:earnings": 160e6, "construction:total:output": 235e6,
      "operations:total:jobs": 74, "operations:onsite:jobs": 28, "operations:total:earnings": 8e6, "operations:total:output": 17e6 },
    published_words: "Table 2-3: Construction Period FTEs per year 180, 515, 386, 51 (2017 to 2020); Facility Operations 74. Table 2-4: Direct construction 95, 273, 204, 27; direct operations 28. The construction of KEC will support the creation of approximately $160 million in salary and wages to Connecticut employees from 2017-2020 [...] During the construction period, 2017-2020, economic output is projected to total $235 million. [Operations, 2022: earnings $8 million, output $17 million.]",
    dollars_of: 2016,
  },
];

export function crosscheck(rows) {
  return STUDIES.map((s) => {
    const base = F.defaults(P, s.tech, s.state);
    const ilr = s.tech === "utility_pv" ? base.ilr : 1;
    const mw = s.mw ?? s.mw_dc / ilr;  // the model's PV MW are AC: the study's DC MW over the state's loading ratio
    const capex = (s.cost_usd * F.to2025(P, s.cost_year)) / (mw * 1000);
    const x = { ...base, mw, capex, life: s.life, ...(s.cf ? { cf: s.cf } : {}) };
    const r = F.run(x, rows, P);
    const back = 1 / F.to2025(P, s.dollars_of);  // the model's 2025 dollars in the study's dollars
    const model = {};
    for (const [k, v] of Object.entries(s.published)) {
      if (k === "property:year") { const y = r.years.find((t) => t.phase === "operations"); model[k] = y?.property ?? null; continue; }
      // session 4263: the sales and use tax over the build, and a later operating year's property line (Wyoming's excise starts in the fourth)
      if (k === "sales:total") { model[k] = r.sums.sales === null ? null : r.sums.sales * back; continue; }
      if (k === "property:year4") { const y = r.years.filter((t) => t.phase === "operations")[3]; model[k] = y?.property ?? null; continue; }  // a statute rate per MWh: no dollar year to convert
      const [ph, e, m] = k.split(":");
      const val = r[ph][m][e];
      model[k] = m === "jobs" ? val : val * back;
    }
    const lines = Object.keys(s.published).map((k) => ({ figure: k, published: s.published[k], model: model[k],
      ratio: model[k] === null || !s.published[k] ? null : model[k] / s.published[k] }));
    return { id: s.id, title: s.title, url: s.url, request: s.request, method: s.method, inputs: { tech: s.tech, state: s.state, mw, capex_2025_usd_per_kw: capex, life: s.life, ilr },
      published_words: s.published_words, cost_words: s.cost_words, dollars_of: s.dollars_of, lines };
  });
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const file = process.argv[2];
  if (!file || !fs.existsSync(file)) { console.error("usage: forecast-crosscheck.mjs <nlr_jedi_multipliers.csv> [--json out.json]"); process.exit(2); }
  const out = crosscheck(readRows(file));
  for (const s of out) {
    console.log(`\n${s.id}: ${s.inputs.tech} ${s.inputs.state} ${s.inputs.mw.toFixed(1)} MW, capex ${s.inputs.capex_2025_usd_per_kw.toFixed(0)} USD/kW (2025)`);
    for (const l of s.lines) console.log(`  ${l.figure.padEnd(32)} published ${String(l.published).padStart(12)}  model ${l.model === null ? "none" : l.model.toFixed(1).padStart(12)}  ratio ${l.ratio === null ? "-" : l.ratio.toFixed(3)}`);
  }
  const j = process.argv.indexOf("--json");
  if (j > 0) fs.writeFileSync(process.argv[j + 1], JSON.stringify({ written_by: "site/scripts/forecast-crosscheck.mjs", studies: out }, null, 1) + "\n");
}
