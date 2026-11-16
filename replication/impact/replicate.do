* ERW, Local impact (/impact, the forecast tool): the five headline figures of the page as it opens, rebuilt in Stata.

* The default project: 200 MW of land-based wind in Texas, first construction year 2027, 1 construction year, 25 operating years, local content and operating spending 100 percent of JEDI's, real discount rate 7 percent. Method: docs/methods/forecast.md, sections 2, 3, 5, 6 and 8, and section 12 (this replication).

* Session 7506 (chain 304), 16 November 2026. Not run: Stata is not on the machine that wrote it. Its Python mirror was run (python replication/impact/replicate.py --in-dir warehouse/output --headline) and printed the expected values below; the page's own view, drawn to HTML, shows the same five (replication/impact/page_figures.json, case "default").

* Expected values (16 November 2026), what this file displays:

*   1. construction jobs, job-years: 515.1                      (the page: 515)

*   2. operating jobs, each year: 44.74                         (the page: 44.7)

*   3. construction earnings, USD of 2025: 41,045,772           (the page: USD 41 million)

*   4. taxes, present value, USD of 2025: 19,915,038            (the page: USD 19.9 million)

*   5. earnings, present value, USD of 2025: 83,592,616         (the page: USD 83.6 million)

* Before it, once, from the repository's root: python replication/impact/replicate.py --in-dir warehouse/output --rows

* That writes rows/jedi_tx_wind.csv: the 24 rows of the table nlr_jedi_multipliers for land-based wind in Texas (JEDI's jobs, earnings and output per MW of its default project, 2017 dollars), with NLR's notice in rows/NOTICE.txt. Run this file from its own folder (replication/impact). It needs no package.

clear all

import delimited using "rows/jedi_tx_wind.csv", varnames(1) asdouble clear

* ---- the inputs, each the page's default (docs/methods/forecast.md, section 2) ----

* EIA's case size for onshore wind, MW (capital cost study for AEO2025, case 13)

scalar mw = 200

* EIA's overnight cost in Texas (Houston), USD per kW of 2023 (site/data/forecast/eia_capex.json, Appendix A, table 1-13)

scalar cost_2023 = 1408

* the GDP implicit price deflator, 2017 = 100 (site/data/forecast/deflator.json; BEA's line as EIA's STEO carries it, series GDPDIUS)

scalar index_2017 = 99.99975

scalar index_2023 = 122.452

scalar index_2025 = 128.90425

* JEDI's default construction cost per MW in Texas, USD of 2017 (site/data/forecast/jedi_costs.json)

scalar jedi_cost_per_mw = 1527788.35

* local content and operating spending, percent of JEDI's default; the real discount rate, percent (OMB Circular A-94)

scalar local = 100

scalar om = 100

scalar rate = 7

* construction years (EIA: 9 months, in whole years) and operating years (EIA's operating life)

scalar build = 1

scalar life = 25

* sales and use tax: Texas's state rate plus its average local rate, percent (Tax Foundation, midyear 2026: 6.25 + 1.95); JEDI's taxable share of the cost, percent; the exemption held for Texas wind, percent

scalar sales_rate = 8.2

scalar taxable = 81.9282

scalar exempt = 0

* ---- section 2: the capital cost in 2025 dollars, to the cent, as the page holds it ----

scalar capex = round(cost_2023 * index_2025 / index_2023, 0.01)

* the spending in 2025 dollars, and in JEDI's dollars (2017)

scalar spend = capex * mw * 1000

scalar spend_jedi = spend * index_2017 / index_2025

* ---- section 3: JEDI's per MW figures ----

quietly summarize per_mw if phase == "construction" & effect == "total" & measure == "jobs"

scalar pc_jobs = r(mean)

quietly summarize per_mw if phase == "construction" & effect == "total" & measure == "earnings"

scalar pc_earn = r(mean)

quietly summarize per_mw if phase == "operations" & effect == "total" & measure == "jobs"

scalar po_jobs = r(mean)

quietly summarize per_mw if phase == "operations" & effect == "total" & measure == "earnings"

scalar po_earn = r(mean)

* construction: proportional to the spending; dollars converted from 2017 to 2025

scalar c_jobs = pc_jobs / jedi_cost_per_mw * spend_jedi * local / 100

scalar c_earn = pc_earn / jedi_cost_per_mw * spend_jedi * local / 100 * index_2025 / index_2017

* operations: per MW, each operating year

scalar o_jobs = po_jobs * mw * local / 100 * om / 100

scalar o_earn = po_earn * mw * local / 100 * om / 100 * index_2025 / index_2017

* ---- section 5: sales and use tax on the taxable share of the spending, spread evenly over the construction years ----

scalar sales_tax = spend * taxable / 100 * sales_rate / 100 * (1 - exempt / 100)

* ---- section 8: present values at the first construction year ----

* Texas taxes no wages (section 6) and its property tax needs the county's levy, which has no default (section 4): the taxes are the sales and use tax

scalar pv_taxes = 0

scalar pv_earn = 0

local b = build

local n = build + life

forvalues t = 1/`b' {
    scalar pv_taxes = pv_taxes + (sales_tax / build) / (1 + rate / 100)^(`t' - 1)
    scalar pv_earn = pv_earn + (c_earn / build) / (1 + rate / 100)^(`t' - 1)
}

local first = `b' + 1

forvalues t = `first'/`n' {
    scalar pv_earn = pv_earn + o_earn / (1 + rate / 100)^(`t' - 1)
}

display "the default project: 200 MW of land-based wind in Texas, 2027, 1 construction year, 25 operating years, 7 percent real"

display "1. construction jobs, job-years: " %9.1fc c_jobs

display "2. operating jobs, each year: " %9.2fc o_jobs

display "3. construction earnings, USD of 2025: " %15.0fc c_earn

display "4. taxes, present value, USD of 2025: " %15.0fc pv_taxes

display "5. earnings, present value, USD of 2025: " %15.0fc pv_earn
