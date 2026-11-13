# Review pack: What a project does for a state

- **Address:** `/impact` (production `https://erw-flame.vercel.app/impact`, opened after `https://erw-flame.vercel.app/internal/open`). The economic forecasting tool, tool 17 of the platform, in the menu as "Local impact" (the name is a ruling, question 1 of part 9).
- **Status:** in review, like every page (`site/lib/release.ts`); a visitor sees the in-review page, the review needs the internal view.
- **Written from:** branch `wip/4250-forecast` (chain 239 and 240, lab-desktop window 4, sessions 4200 to 4259, 13 November 2026). Row 1 of `docs/state/landing_request_desktop_w4.md` landed at `71f8442ed`; rows 2 to 4 wait, and row 4 lands them all.
- **This pack replaces** the pack of sessions 345 to 347 (the snapshot tool on the same address, commit `098a87ca2`): that tool's model, JEDI's per-MW figures, is step 1 here and its method stays in `docs/methods/economic_impact.md`. The forecast's own method is `docs/methods/forecast.md` (internal, never on the page).
- **Numbers:** computed on 13 November 2026 with `site/lib/forecast.ts` from the parameter files in `site/data/forecast/` and the rows of `nlr_jedi_multipliers` (`tests/fixtures/forecast/jedi_rows.json`, the live rows of those states). The default case is land-based wind in Texas.

## 1. What it is for, and for whom

- **The question:** what one generating project brings the state it is built in, year by year from the first construction year to the last operating year: jobs (on site, supply chain, induced), earnings and output, and the state's and counties' taxes on it (property, sales and use, income, severance), with each stream's total and present value.
- **For whom:** a county or state official weighing a project, a developer preparing the local case, a journalist checking a claim, a student of input-output models.
- **What it gives:** two scenarios, A and B, side by side; jobs and taxes by year as charts (hover gives each year) and as a table; the same scenario in every other state; downloads of the run as CSV, a Python script and a Stata do-file that recompute both scenarios and print the tool's totals beside their own.
- **Default case:** land-based wind in Texas, 200 MW at USD 1,482.19 per kW (EIA's cost for Texas, in 2025 dollars), built in 2027, 25 operating years: 515.13 construction job-years, 44.74 jobs in each operating year, USD 41.05 million of construction earnings and USD 3.65 million a year of operating earnings (2025 dollars). Sales and use tax USD 19.92 million, before Texas's manufacturing exemption (no share held, its field says so); no property tax rule held; Texas taxes no wages.
- **What it is not:** a net effect, a forecast of hiring, a fiscal note or advice. No sentence on the page says whether to build; nothing on the page explains except the hover tips.

## 2. The model, step by step

1. **JEDI's per-MW effects** for the technology and state are read from `nlr_jedi_multipliers` (`Impact()` in `site/app/impact/page.tsx`; the table's own method in `docs/methods/economic_impact.md`).
2. **JEDI's default cost per MW in each state** is computed by JEDI's own formulas, without a warehouse write (`warehouse/forecast/jedi_costs.py`, written to `site/data/forecast/jedi_costs.json`), so that construction effects scale with the reader's spending: E = e / C times the spending in JEDI's dollars times the local content (`run()` in `site/lib/forecast.ts`).
3. **The defaults** (EIA's capital cost by state, construction time and life; LBNL's capacity factors and loading ratios; Tax Foundation's rates; the statutes' rules) are set by `defaults()` in `site/lib/forecast.ts` from the files `warehouse/forecast/eia_capex.py` and `warehouse/forecast/params.py` wrote.
4. **Dollars**: every input and output in 2025 dollars by the GDP deflator as EIA's STEO carries it (`deflator.json`; the conversion inside `run()`).
5. **Each year** (`run()`): construction effects spread evenly over the construction years; operating effects each year, MW (DC for PV) times JEDI's per-MW figure times local content times the operating spending share.
6. **Property tax** by the state's rule where a statute is read (`propertyTax()` in `site/lib/forecast.ts`, the rules quoted in `site/data/forecast/property_rules.json`), else the reader's own rate, else no figure.
7. **Sales and use tax** on construction spending, JEDI's taxable share times the rate times one less the exemption (`run()`; `jedi_taxable.json`, `sales_tax.json`, `sales_exemptions.json`).
8. **State income tax** on each job as a single filer (`incomeTax()`; `income_tax.json`), and **severance** on a gas plant's in-state fuel through `/severance`'s own rules (`compute` in `site/lib/severance.ts`, passed to `run()`).
9. **Present values** at the real discount rate, and the sums (`run()`; `stat()` reads any figure by its key).
10. **The page** (`site/app/impact/Forecast.tsx`): the left box (`Panel`, fields and tips from `FIELDS` in `site/lib/forecastui.ts`), A and B (`Compare`), the years (`Years`), the other states (`OtherStates`), the downloads (`site/lib/forecastfiles.ts`: `csvOf`, `pythonOf`, `stataOf`).
11. **Every figure is checked**: each is a `Num` keyed `forecast|<inputs>|<figure>` (`inputsKey()`), and `site/scripts/check-values.mjs` recomputes it with `run()` from its own read of the table and the files.

## 3. Every assumption

| Assumption | Default | Source |
|---|---|---|
| Technology and state | Land-based wind, Texas | The page's own choice, as the snapshot tool's |
| MW | Wind 200, PV 150 (AC), gas 1,227, geothermal 50 | EIA, capital cost study for AEO2025, cases 13, 16, 5 and 11 |
| Capital cost | EIA's overnight cost in the state, 2023 dollars raised to 2025; several cities averaged; else EIA's base case | EIA study, Appendix A tables 1-13, 1-16, 1-5, 1-11 (`eia_capex.json`) |
| First construction year | 2027 | The first full year after 13 November 2026; a choice, no source |
| Construction years | Wind 1, PV 1, gas 2, geothermal 2 | EIA's plant construction time, rounded up to whole years |
| Operating years | Wind 25, PV 35, gas 40, geothermal 40 | EIA's operating life |
| Local content, operating spending | 100 percent of JEDI's defaults | JEDI's own shares and O&M; the cross-check (part 4) shows when a reader should move them |
| Construction profile | Even over the construction years | JEDI states a total, not a profile; the tool's assumption, said in the tip |
| Dollars | 2025, by the GDP implicit price deflator | BEA's index as EIA STEO carries it, series `GDPDIUS` (`deflator.json`) |
| Discount rate | 7 percent real | OMB Circular A-94 (December 2025), section 8.b(1); the tip names Appendix C's 2.0 percent |
| Capacity factor, PV loading ratio | The state's median plant (3 or more), else the national median | `lbnl_wind_capacity_factors`, `lbnl_solar_projects`, placed by `eia860_plants_annual` (`capacity_factors.json`) |
| Sales tax | State rate plus population-weighted local rate, midyear 2026, on JEDI's taxable share | Tax Foundation (CC BY-NC 4.0); JEDI's "Sales Tax (Materials & Equipment Purchases)" line |
| Sales tax exemption | The statute where read (Minnesota wind, Iowa wind and solar equipment, North Dakota's power plants), else 0 and "before exemptions" | `sales_exemptions.json`, each quoted |
| Income tax | Each job a single filer at the phase's average wage, 2026 brackets held in real terms | Tax Foundation 2026 (`income_tax.json`) |
| Property tax | Every state and DC: the statute or revenue guidance where a figure is fixed (a value per MW, an assessment ratio, a capacity or production tax, an exemption), a cited statewide levy where published, else the reader's levy or rate; where none could be read, a note saying why | `property_rules.json`, each rule quoted, its citation in the hover | `property_rules.json`, each rule quoted with its section |
| Gas plant fuel | Heat rate 6,266 Btu/kWh, capacity factor 0.65, in-state share 0, Henry Hub 2025 mean USD 3.5267/MMBtu | EIA case 5; JEDI gas model; `eia_steo_forecasts` `NGHHUUS` (`gas.json`) |

## 4. The cross-checks

| What was compared | With what | Result |
|---|---|---|
| Jayhawk Wind, Kansas, 2019 study (JEDI, the project's own spending), construction jobs | The model at the study's MW and cost | 517 against 634: 0.82 (supply chain 0.96, induced 1.07, onsite 0.40) |
| Jayhawk, operating jobs a year | The same | 34 against 43: 0.79 (onsite 0.98) |
| Jayhawk, construction earnings and output (2019 dollars) | The same | 0.75 and 0.80 |
| Ohio utility solar, Ohio University 2020, low scenario, construction jobs | The model at 2.5 GW DC and its cost | 19,835 against 18,039: 1.10 (direct 1.16) |
| Ohio, operating jobs a year | The same | 733 against 207: 3.54 (JEDI's 2010 PV O&M; the operating spending input added in answer) |
| Glendive Wind, Montana, NextEra's 2024 summary | The model at 800 MW and USD 1 billion | "Approx. 400" against 1,730 total and 272 onsite: the headline does not say what it counts |
| Indiana's first 1,000 MW of wind, NREL 2014, construction jobs | The model at the projects' cost | 4,537 against "more than 4,400": 1.03 |
| Indiana, operating jobs a year | The same | 232 against "approximately 260": 0.89 |
| Rush Creek, Colorado, NREL 2019, construction jobs | The model at 600 MW and USD 1,164/kW (2018) | 1,523 against 2,970: 0.51; 0.71 without Vestas's 830 Colorado factory jobs |
| Rush Creek, operating jobs a year | The same | 123 against "approximately 180": 0.69 |
| NREL's Wyoming study (2013): a 225 MW gas plant, Wyoming's figures | The model at the study's MW and cost | Construction jobs 551 against 573: 0.96; operating 0.86; sales tax 0.90 |
| The same study: a 900 MW wind plant | The same | Construction jobs 1.03; operating 0.70 (leases counted by the study); sales tax 0.80; generation tax 1.01 |
| NREL's 1,000 MW of wind in Texas (2011) and in Maine (2008) | The model at each study's MW and cost | Texas construction 2.41 (the study's 0 percent in-state equipment), operations 0.93; Maine 1.45 and 0.51 |
| Three NREL state-level solar studies: Georgia, New York, Mississippi (2013) | The same | Construction 0.70 to 0.76 (on-site 0.82 to 0.99), operations 0.74 to 0.99 |
| South Spur Solar, Colorado (2025, IMPLAN) | The model at 158 MW AC and USD 173 million | Construction 2.18 (the study's low in-state share), operations 3.40 (JEDI's 2010 solar O&M) |
| Minnesota's wind production tax, Lincoln County, fiscal 2024 (Center for Rural Affairs) | The statute's USD 1.20 per MWh | USD 1.189 per MWh: within 1 percent |
| Every figure on five `/impact` addresses, tables by year included | check-values' own recomputation | 785 of 785 (13 November, after Arizona) |
| The Python and Stata downloads | The tool's totals for both scenarios | The Python script equal to 1e-6 in the node tests (Florida and Wyoming pairs included); the do-file prints both side by side (not run: no Stata on this machine) |

The studies, their requests and the reasons for each gap are in `docs/methods/forecast.md`, section 9, and `docs/reviews/forecast-crosscheck-2026-11-13.json` (`site/scripts/forecast-crosscheck.mjs`).

## 5. The edge cases tested

| Case | What the page does |
|---|---|
| A technology JEDI gives no figure for in a state (gas in DC or Hawaii) | No figure, and a line saying JEDI gives none |
| A state with no property tax rule | "Not held" unless the reader types a rate and the years of its fall; the taxes' total then leaves property out and says so |
| Kansas's ten-year exemption | USD 0 for ten years, then not held unless the reader types a rate (fault 15 fixed the trim that lost the years) |
| Oregon's fee in lieu, 20 years in a 35-year life | Drawn for its 20 years; the life's total names the years held (fault 17) |
| Wyoming's wind excise | From the fourth operating year, MWh shown in the table (fault 20), added to the reader's own rate |
| Florida, Arizona, North Carolina and Maryland | Only on the reader's own rate: 20 percent of the base through 2037 or 2040 (North Carolina in every year), all of it after; Maryland 50 percent of the base, every technology, every year; Virginia 80, 70 and 60 percent exempt by years in service for 5 to 150 MW AC (EIA's default 150 MW is outside the band) |
| Michigan and Nevada | Behind the local option's switch, off by default: Michigan's USD 7,000 per MW AC for 20 years (2 MW at least); Nevada's 55 percent off the reader's rate for 20 years from the first construction year |
| Vermont and Wisconsin | Vermont's USD 4 per kW capacity tax with the reader's own rate added; Wisconsin's USD 5,000 per MW a year paid by the state to the municipality and county, held on the property tax line |
| Geothermal | No capacity factor held: no production tax, no MWh; capacity taxes only (fault 2 fixed the Python file) |
| A scenario in other states | Each state resolved from its own defaults, not the scenario's state's (fault 14) |
| An input out of range | No figure for that scenario and a line saying an input is out of range |
| A planned project picked from EIA-860M | Its technology, MW, state, county and year filled in; every field still editable |

The 20 faults found in the readings, each fixed with a test or ruled, are in `docs/reviews/forecast-faults-2026-11-13.md`.

## 6. What the model cannot see, ranked

1. **The counterfactual.** Gross effects of an input-output model: nothing displaced, no other plant's jobs lost.
2. **Negotiated abatements.** Texas chapter 312, Louisiana's ITEP, New Mexico's industrial revenue bonds, payments in lieu agreed with a county: no statute rate to hold. The reader's rate is the place for one.
3. **County levies.** None held in any state; Iowa's valuation and every state without a rule need the reader's levy or rate (data request row 5 asks for Texas's).
4. **The project's own spending plan.** JEDI's default local shares; the cross-check's largest gaps (Rush Creek, Jayhawk's onsite jobs) are in-state factories and developers' plans.
5. **Today's operating costs for PV.** JEDI's 2010 O&M gives 3.5 times a 2018 study's operating jobs; the operating spending input corrects it.
6. **Federal taxes and credits**, the owner's corporate income or franchise tax, and Arizona's deduction of federal credits from its taxable cost.
7. **Output over the life.** Capacity factor constant: no degradation, repowering or decommissioning.
8. **Where workers live.** Income tax counts every job in the state, as a single filer.

## 7. The ten hardest questions

### 1. The developer says 3,000 construction jobs and the page says 515 job-years. Who is right?
Both may be: a job-year is one full-time job for a year. The page counts as JEDI counts; Glendive's headline (part 4) is an example of a count that does not say what it counts.

### 2. Why does Texas show no property tax, the largest tax a plant pays?
Texas taxes plants at local rates under negotiated abatements; no statewide rule with a rate exists to hold. A reader with a rate types it.

### 3. Why is the sales tax for Texas so large?
It is before Texas's manufacturing exemption, which the Comptroller applies to generating equipment; the statute could not be read as text and no share is held. The field says it is an upper bound (ruling 7 of the note).

### 4. Why do the studies differ from the model by as much as half?
Each study used the developer's own spending and local shares; the model uses JEDI's defaults. Where a study used the projects' own costs (Indiana), it agrees within 3 percent.

### 5. Is a 7 percent discount rate right for a county's revenue?
It is OMB's base case for constant-dollar benefit-cost analysis; the tip names Appendix C's 2.0 percent, and the rate is an input.

### 6. Why are taxes flat in real terms when statutes set nominal rates?
Every flow is in 2025 dollars; a nominal statute rate (USD per MWh) loses value with inflation, which the tool does not forecast. That is why Virginia's indexed revenue share is not held (ruling 10).

### 7. Why does Florida's exemption need the reader's rate?
The statute exempts 80 percent of the value but sets no rate; the county's millage is not held. The tool applies the reader's rate to the remaining 20 percent.

### 8. Can the earnings be checked against BLS wages?
Not on this machine: www.bls.gov and api.bls.gov refuse automated reads (ruling 3). JEDI's earnings stand.

### 9. Why are some states' sales tax rates from a think tank, not the states?
Tax Foundation's table is the one 50-state compilation; it is CC BY-NC (ruling 4: used with attribution while the ERW sells nothing).

### 10. Can the result be reproduced without the site?
Yes: the Python and Stata downloads carry every parameter of both scenarios and the table's rows, recompute every year, and print the tool's totals beside their own.

## 8. What Samuel's Stata run must reproduce

The page's Stata button writes `erw_local_impact_run.do` for the two scenarios on screen; it holds the JEDI rows and every parameter, so no other file is needed:

```stata
* the default page (A: Texas wind; B: as A until changed), downloaded from /impact's Downloads
do erw_local_impact_run.do
* it ends by printing, for each scenario, "tool" and "do-file" side by side:
* jobs, earnings, property, sales, income, severance and the present value of taxes
* for the default A: jobs 1,633.52 over the life; sales USD 19,915,038; income 0; property not held
```

The same in Python: `python erw_local_impact_run.py`, which prints each total beside the tool's and "same" when they agree to one part in a million. The do-file was written and its arithmetic mirrored in the node tests, but not run: Stata is not on this machine.

## 9. Questions only Samuel can answer

1. **The page's name.** (a) "Local impact" (the menu since session 4200); (b) another plain noun.
2. **Tax Foundation's CC BY-NC tables.** (a) used with attribution while the ERW sells nothing; (b) replaced by statutes before any paid product.
3. **BLS and BEA.** (a) leave as is (JEDI's earnings, STEO's deflator); (b) a BEA API key for its own deflator; (c) a manual BLS download.
4. **Texas's sales tax exemption share.** (a) 0, an upper bound, as now; (b) a share read from a Comptroller ruling.
5. **Iowa's solar exemption and racking and wiring.** (a) it does not reach them (67.2 percent exempt); (b) it does.
6. **Kansas's exemption** assumed granted by the Board of Tax Appeals. (a) assumed; (b) off by default.
7. **Oregon's fee.** (a) USD 7,000 per MW, the statute's maximum; (b) the range's middle.
8. **Virginia's revenue share** with a price forecast. (a) left out; (b) held with STEO's price path.
9. **Illinois and Ohio,** whose statute sites refuse this machine. (a) no rule held; (b) a person reads them and a session types the rules.
10. **The shared chart's year labels for long lives** (fault 13). (a) left as they are; (b) thinned in `SeriesChart`, which moves every page.
11. **The old method note.** `docs/methods/economic_impact.md` describes the snapshot page; (a) keep it as the table's method; (b) fold it into `forecast.md`.

## Where every number comes from

- **Jobs, earnings and output per MW:** `nlr_jedi_multipliers` (NLR's JEDI models, read for every state; notice at `https://www.nlr.gov/disclaimer`), read on the page from Supabase and by check-values.
- **Parameters:** `site/data/forecast/*.json`, each with its source, request number (`runs/w4/probe.csv` of chain 239) and the date read; the statute rules quoted word for word.
- **The default case in part 1 and part 8:** computed on 13 November 2026 by `run()` with the Texas rows of the fixture and the parameter files (`runs/w4/pack_numbers.mjs`, not in git).
- **The cross-check:** `site/scripts/forecast-crosscheck.mjs` and `docs/methods/forecast.md`, section 9.
- **The faults and readings:** `docs/reviews/forecast-faults-2026-11-13.md`; the session reports `archive/sessions/SESSION_4200_REPORT.md` to `SESSION_4259_REPORT.md`.
