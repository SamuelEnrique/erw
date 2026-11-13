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
| Discount rate (real) | 7 percent | OMB Circular A-94 (December 2025 text), section 8.b(1): constant-dollar benefit-cost analyses "should report net present value and other outcomes determined using a real discount rate of 7 percent". Its tip names the alternative: Appendix C (6 March 2026), the real 30-year Treasury rate of 2.0 percent, for cost-effectiveness analysis |
| Capacity factor (wind, PV) | the state's median plant, else the national median | `capacity_factors.json` (section 4) |
| PV inverter loading ratio (DC over AC) | the state's median plant, else the national median | `capacity_factors.json` |
| Sales tax rate | the state's rate plus its population-weighted average local rate, midyear 2026 | `sales_tax.json` (Tax Foundation) |
| Sales tax exemption on generating equipment | 0 percent | no state's exemption has been read (section 5): the line is labelled "before exemptions" |
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

**Operations.** Operating spending does not scale with capital cost (JEDI's O&M is its own default per MW): E_o = e_k,s(operations, effect, measure) times MW_basis times L, each operating year. MW_basis is nameplate MW, or MW_DC for PV.

**Output** is computed and downloaded but not charted (the page charts jobs, earnings and the taxes).

## 4. Property tax

A power plant's property tax is set by each state's law, often in place of the general property tax, and by local levies. The tool computes a figure only from a statute it has read, quoted in `site/data/forecast/property_rules.json`. Four kinds:

- **capacity**: USD per MW of nameplate a year. Nebraska's nameplate capacity tax (77-6203(1)(a)): USD 3,518 per MW. South Dakota (10-35-18, with 10-35-16's definition of nameplate capacity in kilowatts): three dollars a kW, USD 3,000 per MW, for a wind farm or solar facility of at least 5 MW.
- **production**: USD per MWh produced, MWh = MW times 8,760 times the capacity factor. Minnesota's wind tax (272.029 subd. 3): 0.12 cents per kWh above 12 MW, 0.036 cents for 2 to 12 MW, 0.012 cents for 0.25 to 2 MW (USD 1.20, 0.36 and 0.12 per MWh); Minnesota's solar tax (272.0295 subd. 3): USD 1.20 per MWh above 1 MW AC. South Dakota (10-35-19.1): USD 0.00045 per kWh for a wind farm first producing after 31 March 2015, USD 0.00090 per kWh for a solar facility. South Dakota's taxes are "in lieu of all taxes [...] on the personal and real property" of the facility (10-35-17).
- **valuation**: a statutory taxable value times the local levy. Iowa's special valuation of wind property (427B.26(2)), where a county or city ordinance adopts it: 0 percent of net acquisition cost in the first assessment year, then 5 points more each year to 30 percent from the seventh. Net acquisition cost is the reader's capital cost. The levy (USD per 1,000 of taxable value) has no statewide figure held: the reader types it; without it no figure is drawn.
- **reader's rate**: in a state with no rule held, the reader may type an effective rate (percent of the capital cost) and a number of years over which the taxable value falls in a straight line to 0. Neither has a default: both are the reader's, and the page says so.

Each tax is charged for whole operating years, from the first (the statutes' first-year proration is not modeled). The land under the project is not modeled anywhere.

**Capacity factors** (`capacity_factors.json`, from warehouse tables): wind, the 2025 capacity factor of plants with a commercial operation year 2019 to 2024 (`lbnl_wind_capacity_factors`), placed in their state by EIA-860 (`eia860_plants_annual`); PV, the 2024 AC capacity factor of plants built 2019 to 2023 (`lbnl_solar_projects`). The state's median plant where the state has at least 3, else the national median (wind 0.3832 over 388 plants, PV 0.2210 over 764).

**Read and not yet held** (each a ruling or a later session): Illinois (35 ILCS 200/10-605 and 10-745: www.ilga.gov failed certificate verification on 13 November; not bypassed), Ohio (R.C. 5727.75, the payment in lieu: codes.ohio.gov's robots file disallows every path), Texas (chapter 312 abatements are negotiated; county and school rates are a table window A could hold from the Comptroller), Minnesota's equipment exemption (272.02), Nebraska's definition of a renewable facility (77-6201), Wyoming, North Dakota, Kansas, Colorado, New Mexico, Louisiana. The Lincoln Institute's 50-state property tax study (effective rates on industrial property) sits on storage.pardot.com, whose robots file disallows every path.

## 5. Sales and use tax on construction spending

T_sales = S times (taxable share) times (state rate + average local rate) times (1 - exemption share), spread evenly over the construction years.

- **The taxable share** is JEDI's own base, its "Sales Tax (Materials & Equipment Purchases)" line (`jedi_taxable.json`): wind 0.819282 (the tax over the rate times the cost before tax, at JEDI's saved project), gas 0.605882 (the same), PV 0.642105 (JEDI's utility materials and equipment share; JEDI's PV default exempts it entirely), geothermal none (JEDI's model has no sales tax line: no figure unless the reader types a share).
- **EIA's capital cost excludes sales tax** (the study, "Basis of estimates": equipment and material costs are "inclusive of purchase price, duties, and freight, (but excluding any sales tax)"), so the tax is added to, not taken from, the capital cost. The tool does not add it to the spending that drives JEDI's effects.
- **Rates**: Tax Foundation's midyear 2026 table (`sales_tax.json`), CC BY-NC 4.0: as the ERW is today, may be public with attribution; if the ERW sells anything, needs permission (`docs/licenses.md`'s two verdicts).
- **Exemptions**: many states exempt generating equipment, wholly or in part. None has been read, so the default is 0 and the line says "before exemptions". A state's exemption, read from its statute, becomes its default.

## 6. State income tax on earnings

For each year and phase, the average earnings per job w = earnings / jobs (2025 dollars). Each job is taxed as one single filer with wages w: taxable income = max(0, w - standard deduction - personal exemption), the tax its brackets give, less any personal credit, not below 0; the year's tax = jobs times that tax (`income_tax.json`, Tax Foundation 2026, single filer). Brackets are 2026's, held fixed in real terms over the project's life (no indexation is modeled). Not modeled: the table's footnotes (recapture, phase-outs, credits beyond the personal one), local income taxes, workers living in another state, and the tax on the output's other incomes (profits, rents). States with no tax on wages (Alaska, Florida, Nevada, New Hampshire, South Dakota, Tennessee, Texas, Washington, Wyoming) show 0, said as such.

## 7. Severance tax on a gas plant's in-state fuel

Severance is the wells' tax, not the plant's (`economic_impact.md`, section 2). The tool computes it only on the share of the plant's fuel the reader says is produced in the state (default 0, JEDI's saved share), with the state's rules as `/severance` holds them (Texas, Louisiana, New Mexico; `site/lib/severance.ts`, `compute`): fuel (MMBtu a year) = MW times 8,760 times the capacity factor times the heat rate (Btu/kWh) / 1,000; volume (Mcf) = MMBtu / 1.036 (EIA's average heat content of natural gas delivered to consumers, 1,036 Btu per cubic foot, a figure the next session cites from EIA's page); the price per Mcf = the price per MMBtu times 1.036. In other states no rule is held.

## 8. Present value

PV = sum over years t of x_t / (1 + r)^(t - t0), r the real discount rate and t0 the first construction year (each year's flow counted at the start of the year it falls in). Shown for each stream and for the taxes together; jobs are summed, not discounted.

## 9. Cross-check against published studies

(Session 4209 to 4210: at least three published impact studies of projects, each with its source; the model run with the study's inputs; the differences and their reasons.)

## 10. What the tool cannot see

- Everything in `economic_impact.md`'s "What JEDI cannot see": gross effects, not net; IMPLAN multipliers of 2014 to 2019; fixed recipes; no displacement.
- Abatements negotiated project by project (Texas chapter 312, Louisiana's ITEP, New Mexico's industrial revenue bonds, payments in lieu agreed with a county): they are not statutes with a rate, so the tool cannot hold them; the reader's rate input is the place for one.
- Federal taxes and credits, and the owner's state corporate income or franchise tax.
- Decommissioning, repowering, degradation of output over the life (the capacity factor is held constant).

**Sources missing or paid** (each also a ruling): BLS QCEW and CPI (www.bls.gov and api.bls.gov refuse automated reads); BEA's own tables (apps.bea.gov's flat files are disallowed; its API needs a key); the Lincoln Institute study (its host disallows all); county levies in every state; the property tax statutes of the states in section 4's last paragraph.

## 11. Check keys

(Session 4211 on: every figure on the page a `Num` with a key `forecast|<scenario inputs>|<figure>` that `site/scripts/check-values.mjs` recomputes with `site/lib/forecast.ts`.)
