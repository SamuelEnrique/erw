# Forecast: what a generating project brings a state and its counties, year by year

Energy Research Warehouse (ERW), tool 17 of the platform (`docs/platform-tools.md`), the economic forecasting tool. Chain 239 (lab-desktop window 4), sessions 4200 on, 13 November 2026. **Internal: this note is never shown on the page.** It extends `docs/methods/economic_impact.md` (sessions 345 to 347, JEDI's per-MW figures, which this note does not repeat) from a single snapshot to a forecast by year over the project's life, with taxes and a present value, for two scenarios side by side.

Tables read: `nlr_jedi_multipliers`, `impact_tax_rules` (severance), `lbnl_wind_capacity_factors`, `lbnl_solar_projects`, `eia860_plants_annual`, `eia_steo_forecasts`. Parameter files (each with its source, its request and the date read): `site/data/forecast/*.json`, written by `warehouse/forecast/*.py` or, for statute rules, by hand from the statute's words. Window A is asked for tables in `docs/state/data_requests_forecast.md`.

## 1. What the tool computes

For one project, the reader's or one picked from EIA-860M's planned generators: technology (land-based wind, utility PV, natural gas combined cycle, geothermal), MW, state and county, capital cost, first construction year, construction years and operating years. For each calendar year from the first construction year to the last operating year:

- jobs (FTE) and earnings (2025 dollars), onsite, supply chain and induced, from JEDI (section 3);
- property tax, where the state's rule is held (section 4);
- sales and use tax on construction spending (section 5);
- state income tax on the earnings (section 6);
- severance tax on in-state gas a gas plant burns, where the reader gives an in-state share (section 7);

and each stream's sum and present value at the reader's discount rate (section 8). Every dollar is a 2025 dollar (section 2). Two scenarios, A and B, each a full set of inputs.

## 2. Inputs, defaults and units

| Input | Default | Source of the default |
|---|---|---|
| Technology | land-based wind | the page's own default, as `/impact`'s |
| State | Texas | as `/impact`'s |
| MW | 200 for wind, 150 for PV, 1,227 for gas, 50 for geothermal | EIA's case size (capital cost study for AEO2025, cases 13, 16, 5, 11). PV MW are AC |
| Capital cost (USD/kW, 2025 dollars) | EIA's overnight cost for the technology in the state, 2023 dollars times index(2025) / index(2023); a state with several cities is their plain mean; a state EIA does not give takes EIA's base case | `site/data/forecast/eia_capex.json` (Appendix A, tables 1-13, 1-16, 1-5, 1-11) and `deflator.json` |
| First construction year | 2027 | the first full calendar year after today (13 November 2026); a choice, no source |
| Construction years | ceil(EIA's plant construction time / 12): wind 1 (9 months), PV 1 (12), gas 2 (24), geothermal 2 (18) | EIA's case tables, "Plant Construction Time" |
| Operating years | EIA's operating life: wind 25, PV 35, gas 40, geothermal 40 | EIA's case tables, "Operating Life" |
| Local content | 100 percent of JEDI's default shares | as `/impact`'s (`economic_impact.md`, section 1) |
| Operating spending | 100 percent of JEDI's default O&M | JEDI's own; section 9 shows JEDI's PV operating jobs at 3.5 times a 2018 study's, so the reader may scale it |
| Discount rate (real) | 7 percent | OMB Circular A-94 (December 2025 text), section 8.b(1): constant-dollar benefit-cost analyses "should report net present value and other outcomes determined using a real discount rate of 7 percent". Its tip names the alternative: Appendix C (6 March 2026), the real 30-year Treasury rate of 2.0 percent, for cost-effectiveness analysis |
| Capacity factor (wind, PV) | the state's median plant, else the national median | `capacity_factors.json` (section 4) |
| PV inverter loading ratio (DC over AC) | the state's median plant, else the national median | `capacity_factors.json` |
| Sales tax rate | the state's rate plus its population-weighted average local rate, midyear 2026 | `sales_tax.json` (Tax Foundation) |
| Sales tax exemption on generating equipment | the state's statute where read (Minnesota wind: 100 percent), else 0 | `sales_exemptions.json` (section 5); with 0 the line is labelled "before exemptions" |
| Property tax: Iowa wind's special valuation | off | an ordinance of the county or city must adopt it (Iowa Code 427B.26(1)) |
| Property tax: local levy (Iowa) or effective rate (states with no rule) | none | no public statewide figure is held (section 4) |
| Gas plant: heat rate, capacity factor | EIA's case 5 heat rate (6,266 Btu/kWh); JEDI's gas default capacity factor (65 percent) | EIA's case table; JEDI gas model, ProjectData |
| Gas plant: in-state share of its fuel | 0 percent | JEDI gas model's "Produced Locally (Percent)", saved at 0 |
| Gas price (USD/MMBtu, 2025) | the mean of EIA STEO's monthly Henry Hub spot price for 2025 | `eia_steo_forecasts`, series `NGHHUUS` |

**Dollars.** Every input and output is in 2025 dollars. A figure of year y is converted by index(2025) / index(y), the GDP implicit price deflator (BEA's NIPA Table 1.1.9 line, as EIA's STEO carries it, series `GDPDIUS`; 2010 89.6185, 2017 99.99975, 2023 122.452, 2025 128.90425). Flows are constant-dollar: no inflation is added in later years, and the discount rate is real (OMB A-94, section 7.a: "Nominal and real values must not be combined in the same analysis").

**MW basis.** JEDI's per-MW figures are per nameplate MW (wind, gas, geothermal) or per MW DC (PV). The reader's PV MW are AC (EIA's cost, the production taxes and Minnesota's threshold are AC). PV's JEDI basis is MW_DC = MW_AC times the loading ratio.

## 3. Jobs, earnings and output

JEDI gives, for technology k and state s, the effect per MW of its default project, e_k,s(phase, effect, measure) (`nlr_jedi_multipliers`), and its default construction cost per MW, C_k,s, in its own dollar year y_k (`jedi_costs.json`, from `jedi_recalc.py`'s own evaluation; wind 2017, the others 2010).

**Construction.** JEDI's effects are proportional to spending (input-output, `economic_impact.md`, "Fixed recipes"). The reader spends S = capex (USD/kW, 2025) times MW times 1,000, which is S times index(y_k) / index(2025) in JEDI's dollars. The construction effect is

  E_c(effect, measure) = e_k,s(construction, effect, measure) / C_k,s times S_JEDI times L,

where L is the local content (percent / 100) and S_JEDI is the spending in JEDI's dollar year. Jobs are job-years; earnings and output are then converted to 2025 dollars (times index(2025) / index(y_k)). At JEDI's own project and costs this is JEDI's own figure (S_JEDI / C_k,s is JEDI's MW). For PV the cost per MW is per MW DC, and S counts AC kW, so S_JEDI / C_k,s is MW DC at JEDI's cost: the formula needs no separate conversion.

The job-years and earnings are spread evenly over the construction years (JEDI states a total for the construction period, not its profile; an even spread is the tool's assumption, and the tip says so).

**Operations.** Operating spending does not scale with capital cost (JEDI's O&M is its own default per MW): E_o = e_k,s(operations, effect, measure) times MW_basis times L times O, each operating year, O the operating spending (percent of JEDI's default / 100). MW_basis is nameplate MW, or MW_DC for PV.

**Output** is computed and downloaded but not charted (the page charts jobs, earnings and the taxes).

## 4. Property tax

A power plant's property tax is set by each state's law, often in place of the general property tax, and by local levies. The tool computes a figure only from a statute it has read, quoted in `site/data/forecast/property_rules.json`. Four kinds:

- **capacity**: USD per MW of nameplate a year (North Dakota's capacity taxes below too). Nebraska's nameplate capacity tax (77-6203(1)(a)): USD 3,518 per MW. South Dakota (10-35-18, with 10-35-16's definition of nameplate capacity in kilowatts): three dollars a kW, USD 3,000 per MW, for a wind farm or solar facility of at least 5 MW.
- **production**: USD per MWh produced, MWh = MW times 8,760 times the capacity factor. Minnesota's wind tax (272.029 subd. 3): 0.12 cents per kWh above 12 MW, 0.036 cents for 2 to 12 MW, 0.012 cents for 0.25 to 2 MW (USD 1.20, 0.36 and 0.12 per MWh); Minnesota's solar tax (272.0295 subd. 3): USD 1.20 per MWh above 1 MW AC. South Dakota (10-35-19.1): USD 0.00045 per kWh for a wind farm first producing after 31 March 2015, USD 0.00090 per kWh for a solar facility. South Dakota's taxes are "in lieu of all taxes [...] on the personal and real property" of the facility (10-35-17). North Dakota (57-33.2-04, read from the Century Code's chapter PDF): a wind generator pays USD 2.50 per kW of rated capacity (USD 2,500 per MW) and half a mill per kWh (USD 0.50 per MWh); a grid-connected generator of 100 kW or more from another source than coal or wind (PV, gas, geothermal) pays 50 cents per kW (USD 500 per MW) and one mill per kWh (USD 1 per MWh); both in lieu of property taxes except on land (57-33.2-05). Geothermal holds no capacity factor in the tool, so its production tax is not computed, only its capacity tax.
- **valuation**: a statutory taxable value times the local levy. Iowa's special valuation of wind property (427B.26(2)), where a county or city ordinance adopts it: 0 percent of net acquisition cost in the first assessment year, then 5 points more each year to 30 percent from the seventh. Net acquisition cost is the reader's capital cost. The levy (USD per 1,000 of taxable value) has no statewide figure held: the reader types it; without it no figure is drawn.
- **exempt for a number of years**: Kansas exempts property used to generate electricity from wind, solar or geothermal for the 10 taxable years after construction is completed, for an application after 31 December 2016 (K.S.A. 79-201, Eleventh). The tool charges 0 for those years and holds no rule after them: those years are not held unless the reader types a rate, and the life then has no property tax total (a sum of the held years would read as the life's).
- **local option with a rate**: Oregon (sections 1 to 3, chapter 571, Oregon Laws 2015, printed in the notes to ORS 307.175): a county and a solar project outside any city may agree to exempt the project and take a fee in lieu of USD 5,500 to 7,000 per MW of nameplate a year, for up to 20 years; section 1 is repealed on 2 January 2028, and a project exempt by then keeps its agreement's term. The tool offers it with the same switch as Iowa's ordinance (off by default) and a rate held to the statute's range, default USD 7,000, the statute's maximum and its one fixed rate until 2021 (a ruling); after 20 years no rule is held. Virginia's revenue share (58.1-2636, up to USD 1,400 per MW AC by local ordinance, raised 10 percent in nominal terms on 1 July 2026 and every five years) is read and not held: in constant 2025 dollars its nominal steps need a price forecast the tool does not hold (a ruling).
- **reader's rate**: in a state with no rule held, or in the years after an exemption, the reader may type an effective rate (percent of the capital cost) and a number of years over which the taxable value falls in a straight line to 0. Neither has a default: both are the reader's, and the page says so.

Each tax is charged for whole operating years, from the first (the statutes' first-year proration is not modeled). The land under the project is not modeled anywhere.

**Capacity factors** (`capacity_factors.json`, from warehouse tables): wind, the 2025 capacity factor of plants with a commercial operation year 2019 to 2024 (`lbnl_wind_capacity_factors`), placed in their state by EIA-860 (`eia860_plants_annual`); PV, the 2024 AC capacity factor of plants built 2019 to 2023 (`lbnl_solar_projects`). The state's median plant where the state has at least 3, else the national median (wind 0.3832 over 388 plants, PV 0.2210 over 764).

**Read and not yet held** (each a ruling or a later session): Illinois (35 ILCS 200/10-605 and 10-745: www.ilga.gov failed Python's certificate verification on 13 November; read again with the system's trust store, the certificate verifies and the site answers "Access Denied" (HTTP 403) to an automated read, its robots file included: a refusal, honoured), Ohio (R.C. 5727.75, the payment in lieu: codes.ohio.gov's robots file disallows every path), Texas (chapter 312 abatements are negotiated; county and school rates are a table window A could hold from the Comptroller), Minnesota's equipment exemption (272.02), Nebraska's definition of a renewable facility (77-6201), Wyoming, North Dakota, Kansas, Colorado, New Mexico, Louisiana. The Lincoln Institute's 50-state property tax study (effective rates on industrial property) sits on storage.pardot.com, whose robots file disallows every path.

## 5. Sales and use tax on construction spending

T_sales = S times (taxable share) times (state rate + average local rate) times (1 - exemption share), spread evenly over the construction years.

- **The taxable share** is JEDI's own base, its "Sales Tax (Materials & Equipment Purchases)" line (`jedi_taxable.json`): wind 0.819282 (the tax over the rate times the cost before tax, at JEDI's saved project), gas 0.605882 (the same), PV 0.642105 (JEDI's utility materials and equipment share; JEDI's PV default exempts it entirely), geothermal none (JEDI's model has no sales tax line: no figure unless the reader types a share).
- **EIA's capital cost excludes sales tax** (the study, "Basis of estimates": equipment and material costs are "inclusive of purchase price, duties, and freight, (but excluding any sales tax)"), so the tax is added to, not taken from, the capital cost. The tool does not add it to the spending that drives JEDI's effects.
- **Rates**: Tax Foundation's midyear 2026 table (`sales_tax.json`), CC BY-NC 4.0: as the ERW is today, may be public with attribution; if the ERW sells anything, needs permission (`docs/licenses.md`'s two verdicts).
- **Exemptions**: many states exempt generating equipment, wholly or in part. An exemption read from the state's statute is the default for that state and technology (`sales_exemptions.json`, quoted): Minnesota exempts wind energy conversion systems and the materials to build them (297A.68, subd. 12), so Minnesota wind's default exemption is 100 percent. Iowa exempts wind energy conversion property and its materials (423.3(54)): 100 percent; and "solar energy equipment", equipment primarily used to collect and convert solar radiation or carry it to a point of use (423.3(90)): the modules and inverters are that equipment, (0.368421 + 0.063158) / 0.642105 = 67.2 percent of the tax on JEDI's materials and equipment; racking and wiring are not named, and whether the exemption reaches them is a ruling (default: it does not). Texas: the Comptroller's letter rulings (for example 201907005L, 2019) apply the manufacturing exemption of Tax Code 151.318 to equipment that generates electricity (solar modules, wind turbines) and not to every item of a facility; the statute's text could not be read as text from the Legislature's site (statutes.capitol.texas.gov serves a script-built page) and no exempt share is held, so Texas's default stays 0 and its field says the figure is an upper bound before that exemption (a ruling). North Dakota (57-39.2-04.2) exempts the production equipment and every other purchase for building a "power plant", which includes any non-coal, non-wind facility of 100 kW or more selling its power: PV, gas and geothermal 100 percent; a wind facility counts only if completed before 2017, so a new wind plant has none. Nebraska's exemption for community-based energy development projects (77-2704.57) was repealed by Laws 2026, LB901, operative 1 July 2026 (request 72): none. South Dakota's relief for wind and other facilities is a discretionary reinvestment payment, not an exemption: none. Every other state and technology has none read: the default is 0 and the line says "before exemptions".

## 6. State income tax on earnings

For each year and phase, the average earnings per job w = earnings / jobs (2025 dollars). Each job is taxed as one single filer with wages w: taxable income = max(0, w - standard deduction - personal exemption), the tax its brackets give, less any personal credit, not below 0; the year's tax = jobs times that tax (`income_tax.json`, Tax Foundation 2026, single filer). Brackets are 2026's, held fixed in real terms over the project's life (no indexation is modeled). Not modeled: the table's footnotes (recapture, phase-outs, credits beyond the personal one), local income taxes, workers living in another state, and the tax on the output's other incomes (profits, rents). States with no tax on wages (Alaska, Florida, Nevada, New Hampshire, South Dakota, Tennessee, Texas, Washington, Wyoming) show 0, said as such.

## 7. Severance tax on a gas plant's in-state fuel

Severance is the wells' tax, not the plant's (`economic_impact.md`, section 2). The tool computes it only on the share of the plant's fuel the reader says is produced in the state (default 0, JEDI's saved share), with the state's rules as `/severance` holds them (Texas, Louisiana, New Mexico; `site/lib/severance.ts`, `compute`): fuel (MMBtu a year) = MW times 8,760 times the capacity factor times the heat rate (Btu/kWh) / 1,000; volume (Mcf) = MMBtu / 1.034, EIA's heat content of natural gas delivered to electric power in 2024, 1,034 Btu per cubic foot ("Heat Content of Natural Gas Consumed", https://www.eia.gov/dnav/ng/ng_cons_heat_dcu_nus_a.htm, read 13 November 2026); the price per Mcf = the price per MMBtu times 1.034. The defaults are in `site/data/forecast/gas.json`: EIA's case 5 heat rate (6,266 Btu/kWh, HHV), JEDI's capacity factor (0.65) and 2025's mean Henry Hub price (USD 3.5267/MMBtu, the 12 history months of `NGHHUUS`). In other states no rule is held.

## 8. Present value

PV = sum over years t of x_t / (1 + r)^(t - t0), r the real discount rate and t0 the first construction year (each year's flow counted at the start of the year it falls in). Shown for each stream and for the taxes together; jobs are summed, not discounted.

## 9. Cross-check against published studies

Session 4209 (chain 239). `site/scripts/forecast-crosscheck.mjs` runs each study's own project (technology, state, MW, cost in its dollar year, life) through `lib/forecast.ts` at the tool's defaults otherwise, and sets the model's statewide figures beside the study's (the model's dollars converted back to the study's year). Each study was read on 13 November 2026 (requests 49, 50 and 54 of `runs/w4/probe.csv`, robots files first).

| Study | Project as the study states it | Figure | Published | Model | Model / published |
|---|---|---|---:|---:|---:|
| Jayhawk Wind, Kansas: economic development report, November 2019 ([fortscott.biz](https://fortscott.biz/wp-content/uploads/2019/12/Jayhawk-Wind-Economic-Development-Report-Final-November-20191.pdf)); JEDI Wind, 2017 IMPLAN state multipliers, the project's own spending | about 195 MW; "an investment of almost $250 million" (2019 dollars); 25 years | construction jobs, total | 634 | 517 | 0.82 |
| | | construction jobs: onsite / supply chain / induced | 190 / 321 / 123 | 77 / 308 / 132 | 0.40 / 0.96 / 1.07 |
| | | construction earnings, output (2019 dollars) | 36.7 m / 98.2 m | 27.7 m / 78.7 m | 0.75 / 0.80 |
| | | operating jobs, total (onsite) | 43 (9) | 34 (8.8) | 0.79 (0.98) |
| | | operating earnings, output a year | 2.2 m / 7.5 m | 1.9 m / 5.9 m | 0.86 / 0.78 |
| Glendive Wind, Montana: NextEra's summary of a 2024 study by Strategic Economic Research ([nexteraenergyresources.com](https://www.nexteraenergyresources.com/content/dam/neer/us/en/microsites/PDF/glendive-prairie-econ-impact.pdf)); IMPLAN with JEDI | "up to 800 megawatts", "$1 billion investment" (2024 dollars) | construction jobs | "Approx. 400" | 1,730 total; 272 onsite | 4.3 (total); 0.68 (onsite) |
| Utility-scale solar in Ohio, Ohio University, 31 July 2020, low scenario ([PDF](https://static1.squarespace.com/static/56a8596376d99c0164fc16bd/t/5f50094e9c0ff3029d54bc6c/1599080786155/Measuring+the+Economic+Impacts+of+Utility-Scale+Solar+in+Ohio+---+FINAL%2C+7.31.2020.pdf)); JEDI PV with 2018 IMPLAN multipliers and NREL's Q1 2018 benchmark; 80 percent Ohio labor, 30 percent Ohio materials | 2.5 GW DC; construction cost USD 3,592,192,939 (2018 dollars); 40 years | construction jobs, total (direct) | 18,039 (8,536) | 19,835 (9,881) | 1.10 (1.16) |
| | | construction output (2018 dollars) | "roughly $3.2B" | 2.43 bn | 0.76 |
| | | operating jobs a year | 207 | 733 | 3.54 |
| | | tax revenue a year | "up to $22.5M" (USD 9,000 per MW, Ohio's payment in lieu ceiling) | no rule held (codes.ohio.gov disallows every path) | none |

| Indiana's first 1,000 MW of wind, NREL/TP-6A20-60914, 2014 ([docs.nlr.gov](https://docs.nlr.gov/docs/fy14osti/60914.pdf), request 78); JEDI Wind with the seven projects' own expenditures and local shares (about 20 percent of construction and 40 percent of O&M in Indiana) | per 1,000 MW of the 1,339 MW built 2008 to 2011; construction expenditure USD 2,487 million for the 1,339 MW (2010 dollars), scaled | construction jobs | "more than 4,400" | 4,537 | 1.03 |
| | | operating jobs a year | "approximately 260" | 232 | 0.89 |
| | | property tax a year | "more than $8 million" | no rule held (Indiana's are negotiated abatements) | none |

Session 4253 added Indiana. Two more studies were sought and not used: a West Virginia gas plant study whose host disallows ClaudeBot and anthropic-ai by name, and a regional battery study (no JEDI model, not statewide).

**What the differences say.**

- **Local content is the study's, not JEDI's default.** Jayhawk's developer planned far more onsite spending in Kansas than JEDI's default shares (onsite jobs 190 against the model's 77), while the supply chain and induced lines agree within 7 percent. Ohio's 80 percent labor and 30 percent materials are close to JEDI's utility defaults, and its construction jobs agree within 10 percent. Indiana's projects, modeled with their own costs and local shares, agree within 3 percent (construction) and 11 percent (operations). The tool's local content input is where a reader with a project's spending plan moves the figure.
- **JEDI's PV operating figures are high for today's plants.** JEDI's utility PV default holds 0.185 onsite FTE per MW DC a year (2010 operating costs), so 2.5 GW gives 461 onsite operating jobs against Ohio's 207 in total, which used NREL's 2018 O&M benchmark. The tool's PV operating jobs are therefore an upper reading; the tip on the operating figures says so, and a later session may add an operating spending input (percent of JEDI's default), as Ohio's study changed JEDI's costs.
- **A headline count may not say what it counts.** Glendive's "approx. 400 construction jobs" is a summary's headline; the model's onsite jobs (272) are nearer to it than its total (1,730), and job-years spread over a short build can be read as a peak headcount. The study itself was not found; the comparison is kept with that caveat, not dropped.
- **Dollar figures** run about 0.75 to 0.86 of the studies': JEDI's default multipliers are of 2014 to 2019 and its default cost mixes are of 2010 to 2017; the studies updated both.
- **Taxes.** Ohio's tax figure is its statutory payment in lieu, the rule this chain could not read (Ohio's code site disallows automated reads). Kansas, Jayhawk's state, exempts the project for ten years under a payment in lieu of USD 2,000 per MW ("Assumes $2,000/MW/year [...] for the first ten years of the Project's life while the property tax exemption is in place"), a negotiated agreement the tool cannot hold.

**A tax check: Minnesota's wind production tax in 2024.** The Center for Rural Affairs' fact sheet of February 2025 ([cfra.org](https://www.cfra.org/sites/default/files/publications/MN%20Wind%20Tax%20Revenue%20Fact%20Sheet%2002-25%20WEB.pdf), request 70; its source the Department of Revenue's county energy production report, which this chain did not read) gives Lincoln County USD 3,914,438.52 of wind production tax on 3,293,278.92 MWh in fiscal 2024, USD 1.189 per MWh: within 1 percent of the statute's USD 1.20 for systems above 12 MW (the rest a smaller system's lower rate), so the tool's rate is the county's. Statewide, USD 16.1 million on 4,928.7 MW of installed capacity (EIA's figure in the same sheet) is USD 3,267 per MW, which at USD 1.20 per MWh implies a fleet capacity factor near 0.31. The tool's default for a new Minnesota wind plant is 0.4197, the median of 19 plants built 2019 to 2024: a new plant produces more than the fleet of all ages (older turbines, smaller systems at lower rates), and the capacity factor is an input a reader with a project's own estimate changes. The fact sheet's other rows are not used: their columns do not align in the text the PDF yields.

## 10. What the tool cannot see

- Everything in `economic_impact.md`'s "What JEDI cannot see": gross effects, not net; IMPLAN multipliers of 2014 to 2019; fixed recipes; no displacement.
- Abatements negotiated project by project (Texas chapter 312, Louisiana's ITEP, New Mexico's industrial revenue bonds, payments in lieu agreed with a county): they are not statutes with a rate, so the tool cannot hold them; the reader's rate input is the place for one.
- Federal taxes and credits, and the owner's state corporate income or franchise tax.
- Decommissioning, repowering, degradation of output over the life (the capacity factor is held constant).

**Sources missing or paid** (each also a ruling): BLS QCEW and CPI (www.bls.gov and api.bls.gov refuse automated reads); BEA's own tables (apps.bea.gov's flat files are disallowed; its API needs a key); the Lincoln Institute study (its host disallows all); county levies in every state; the property tax statutes of the states in section 4's last paragraph.

## 11. Check keys

Every figure of the A and B table and of the table by year is a `Num` whose key is `forecast|<every input of its scenario, in KEY_ORDER>|<figure>` (`site/lib/forecast.ts`, `inputsKey`, `parseKey`, `stat`). `site/scripts/check-values.mjs` (`p[0] === "forecast"`) recomputes it with `run` and `stat` from its own read of the technology's and state's rows of `nlr_jedi_multipliers`, the parameter files read from disk, and `/severance`'s own `compute` for a gas plant's in-state fuel. The figures: `c:<measure>:<effect>` and `o:<measure>:<effect>` (construction over the build, each operating year), `sum:<stream>` and `pv:<stream>` (the life, and its present value), `pv:taxes`, `y1:<stream>` (the first operating year) and `year:<yyyy>:<stream>`. The addresses check-values reads: `/impact`, `/impact?tech=utility_pv&state=mn&bstate=sd`, `/impact?tech=natural_gas&state=tx&instate=50&btech=geothermal&bstate=ca`, `/impact?state=ia&iaval=1&levy=30&bstate=ne`, each with a floor of 10 keys.
