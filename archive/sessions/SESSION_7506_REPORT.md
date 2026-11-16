# Session 7506 report: the forecast tool (Local impact, `/impact`) at the done line

Energy Research Warehouse (ERW), chain 304 (`queue/done/304-day-16-november-oldlaptop-done-line-economics.md`), samueloldlaptop, 16 November 2026. Branch `wip/7506-impact`, worktree `erw-7506`. Unattended. Model spend USD 0. Nothing pushed.

## At the top

- **No figure the page shows was found wrong by its own rules, and the page's code is unchanged.** The replication meets the page on every figure: `7593 of 7593 inside the tolerance`.
- **One parameter is read wrong in a file a builder writes (not fixed here, a data request):** Utah's "$966 credit" of Tax Foundation's table is held as a standard deduction in `site/data/forecast/income_tax.json`, so every Utah plant's income tax is drawn too high, by at most 18 to 31 percent depending on the plant (Cape Generating Station: USD 28.4 million over the life as drawn, USD 23.4 million if read as a full credit; the truth is between, as the credit falls with income). Faults file row 4.
- **The replication is not blind.** I read the page's library (`site/lib/forecast.ts`) to call it before I wrote the Python, so the Python is a second implementation written to the note as I completed it, not an independent reading of the note as it stood. What it proves: the completed note and the page compute the same figures, and a changed parameter is caught.
- **The requests to publishers (15) were made by a read-only helper agent** under my written rules (robots first, the ruled User-Agent, a log). I then read every figure I use in the saved text myself. `docs.nlr.gov`'s robots address redirects to an HTML page of `www.nlr.gov` (whose robots file allows everything); the helper took that as no rule and fetched two PDFs. If you read that redirect as a refusal, set the JEDI II rows aside.
- Stata was not run (not on this machine). No browser was used: every "the page shows" below is the page's own view drawn to HTML with the site's code.
- Not finished: NREL's section 1603 report and its Colorado 1,000 MW papers were not read (time); no NREL utility solar result with jobs and earnings was found.

## What was done, by part

**1. The method note** (completed, not rewritten)
- `docs/methods/forecast.md`: new section 12. 12.1 holds eleven things sections 2 to 8 did not say and a second implementation needed (rounding of defaults; the address; what a planned project sets; the order of the property tax rules; the own rate's year index; each condition of a partial exemption; when the life has a total and what "Taxes, present value" adds; the income tax's wage; the severance rates used; the table by year's columns; which states the charts draw; how a figure is written).
- `docs/methods/economic_impact.md`: section 4, what changed since the page became the forecast (severance now computed on in-state fuel; property rules now held; the keys; the cost scaling).
- `docs/methods/impact_tax_rules.md`: how `/impact` uses the rules (it reads the JSON the table is built from; which rates).

**2. The replication** (`replication/impact/`)
- `replicate.py` (standard library): reads `nlr_jedi_multipliers`, `site/data/forecast/*.json`, the gas rules of `site/data/severance_rules.json`.
- `page_figures.json` and `.csv`: 7,593 figures of 17 addresses, read from the page's view drawn to HTML (`site/scripts/impact-figures.mjs`): the page as it opens; ten real planned projects (`projects.csv`, EIA-860M, inventory of planned generators as of September 2026, from the table `eia860m_planned_generators`); the six other addresses the value check reads.
- The ten: Dodge County Wind (MN, 228 MW, 2027), Rail Tie Wind (WY, 504 MW, 2029), Silver Queen Wind Farm (IA, 252 MW, 2028), Rocky Run Solar (VA, 300 MW, 2028), Grant Solar (SD, 99 MW, 2027), Gigawatt Solar (TX, 773 MW, 2028), CPV Basin Ranch Energy Center (TX, 1,445 MW combined cycle, 2029), Franklin Farms 1&2 (LA, 1,560.6 MW combined cycle, 2028), Cape Generating Station (UT, 86 MW geothermal, 2027), Fish Lake Geothermal (NV, 26.5 MW, 2027).
- As printed: `7593 of 7593 inside the tolerance` (`largest relative difference from the page's unrounded value: 3.12e-16`). By kind: 4,481 cells of the table by year, 2,186 of the two other-states charts, 484 defaults, 368 A and B figures, 74 cells drawn "not held" or "none".
- A changed parameter is caught: Texas's sales rate up 0.1 point, 40 figures differ; the 2017 index up 1 percent, 855.
- `replicate.py --parameters`: `forecast_tool_parameters beside the parameter files: 414 of 414 equal; 354 rows of the table not compared`.
- `replicate.do`: the five headline figures, expected values at its top. Not run.

**3. The cross-check** (`site/scripts/impact-crosscheck.mjs`, `docs/reviews/impact-crosscheck-2026-11-16.json`; table in "For the pack")
- Builds on the 22 studies of `docs/reviews/forecast-crosscheck-2026-11-14.json`; adds NREL's JEDI II paper (Colorado, 2006) and Nevada's own fiscal notes for a 2026 geothermal plant. No figure adjusted.

**4. The decisions block**
- The page's left box is its block (23 fields, default under each, source on hover, edited in place, A and B). Nothing added. Eight choices that move a figure and are not a field are listed in the note (12.4); three are ruling rows.

**5. The faults file** (`docs/reviews/impact-faults-2026-11-16.md`): 12 rows. Site faults fixed 0; note 3 (completed); data machine 2; ruling 7.

## Tests

Command, each file in its own process: `ERW_SPEND_CAP_USD=0 ERW_TABLES_DIR=C:\Users\lossa\Documents\erw\warehouse\output .venv\Scripts\python.exe -m pytest tests/<file> -q`

| File | Result |
|---|---|
| `tests/test_session7506_impact_replication.py` (new) | 11 passed (2 of them draw the page again from the day's table and run the replication against it; skipped where the table or node is absent) |
| `tests/test_session4203_forecast.py` (runs `site/scripts/test-forecast.test.mjs`) | 9 passed |
| `tests/test_session4219_forecast_faults.py` | 8 passed |
| `tests/test_session4221_forecast_readers.py` | 6 passed |
| `tests/test_session347.py` | 7 passed, 2 skipped |
| `tests/test_session409.py` | 6 passed |
| `tests/test_session3938.py` | 3 passed |
| `tests/test_session301.py` | 9 passed |
| `node --import ./scripts/tsx-register.mjs scripts/impact-figures.mjs <table> --check` | exit 0: the committed figures are what the page draws today |

No site build, no full suite, no landing gate (this machine's rules).

## What to review

No page's code changed. Two things to look at, both in review (internal view):

- `https://erw-flame.vercel.app/impact`: open it. A and B should read: Construction jobs 515; Operating jobs, each year 44.7; Construction earnings USD 41 million; Property tax "not held" (hover: the local levy is not given); Sales and use tax USD 19.9 million; State income tax USD 0; Taxes, present value USD 19.9 million; Earnings, present value USD 83.6 million.
- `https://erw-flame.vercel.app/data/methods/economic_impact`: scroll to the end. A new section 4, "The page since 13 November 2026, and where its replication is".

## For the pack

**What Samuel signs:** `docs/methods/forecast.md`, section 12.5 "Sign-off". It accepts: the model of sections 2 to 8 as completed by 12.1; the defaults and sources of the left box; the property and sales tax readings state by state (an upper bound where the hover says so); the cross-checks as the record of how far the tool stands from published studies; what section 10 says the tool cannot see. It leaves open the rulings below.

**What the tool is, in one line:** JEDI's jobs, earnings and output per MW for the state, scaled by the project's spending, plus four taxes computed from statutes and 2026 rates, year by year, with present values. Gross effects, not net.

**The five choices that matter most**

| Choice | Default | Source |
|---|---|---|
| Capital cost (construction jobs and earnings are proportional to it) | EIA's overnight cost for the technology in the state, 2023 dollars moved to 2025; Texas wind USD 1,482 per kW | EIA, capital cost study for AEO2025, Appendix A; the GDP price index as EIA's STEO carries it |
| Local content | 100 percent of JEDI's default shares | NLR's JEDI models; the studies show this moves the figure most (our construction jobs run 0.18 to 4.3 times a study's) |
| Operating spending | 100 percent of JEDI's default (costs of 2010 to 2017) | JEDI; for solar it gives 3.5 times a 2018 study's operating jobs, so the reader may scale it |
| Property tax: the local levy, the own rate, the local option | none, none, off: where a state's rule needs one, the property tax is "not held" | each state's statute in the hover; no statewide levy exists in most states |
| Discount rate, real | 7 percent | OMB Circular A-94, section 8.b(1); its Appendix C gives 2.0 percent |

The other eighteen fields: technology, state, size, first construction year, construction years, operating years, sales tax rate (Tax Foundation, midyear 2026), taxable share (JEDI's own base), exemption (the state's statute where read, else 0), fee in lieu, own rate's years, capacity factor (the state's median plant, LBNL), loading ratio, heat rate, in-state fuel (0), gas price (2025 Henry Hub mean).

**The cross-check** (ours through the page's own functions on each document's project; theirs read from the publisher's file on 16 November 2026)

| Figure | Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---:|---:|---|---:|---|
| Colorado wind, 680 MW at USD 1,400 per kW of 2005: construction jobs | 2,605 | 1,618 | NREL, *JEDI II: Jobs and Economic Development Impacts from Coal, Natural Gas, and Wind Power*, NREL/CP-500-40085, June 2006, Figure 4 | 1.61 times | two releases twelve years apart (2001 against 2016 state data, the paper's inputs against JEDI's default shares); the paper prints no local share for the equipment, so the gap cannot be split |
| the same: construction earnings, USD million of 2005 | 122.6 | 58.55 | the same (unit taken as millions, from the paper's charts) | 2.09 times | the same |
| the same: operating jobs a year (plant workers) | 140 (30.8) | 259 (88) | the same | 0.54 (0.35) | the paper staffs 0.13 workers a MW; the 2018 release 0.045 |
| the same: operating earnings a year, USD million of 2005 | 6.87 | 12.69 | the same | 0.54 | follows the jobs |
| Colorado gas, 270 MW: plant workers | 13.7 | 14 | the same | 0.98 | operating lines only: no cost is stated |
| Colorado gas: operating jobs a year, total | 44.7 | 369 | the same | 0.12 | the paper buys 40 percent of the fuel in the state; our default is 0 |
| Nevada geothermal, 36 MW, USD 178,446,043: construction jobs | 259 job-years on site | 211 "full-time construction jobs" | Nevada Governor's Office of Energy, Director's findings and order, application 26-0814G, Lone Mountain Geothermal (ORNI 56 LLC), 4 November 2026 | 1.23 times | workers against job-years; the order's Nevada payroll at USD 60 an hour is 87 job-years |
| the same: construction earnings on site | USD 22.8 million | USD 10,857,600 | the same | 2.10 times | the order counts Nevada residents only |
| the same: operating jobs on site | 23.1 | 0 | the same | none | the applicant states no employee at the plant |
| the same: property tax paid after the 55 percent abatement, first year | USD 876,631 | USD 876,653 | Nevada Department of Taxation, property tax fiscal note, 24 August 2026 | USD 22 | the rate typed is the note's own; the abatement rule is the state's |
| the same: paid after abatement, 20 years | USD 16.2 million | USD 15,034,766 | the same | 1.08 times | we count the 20 years from the first construction year; the Department from the first operating year; and its depreciation differs |
| the same: sales and use tax | not held | USD 405,537 (USD 5.9 million of purchases at 6.85 percent) | Nevada Department of Taxation, sales and use tax fiscal impact, 19 August 2026 | none | no taxable share is held for geothermal; the Budget Division's note states USD 86.4 million of purchases |

What it says: for jobs the tool is JEDI at its defaults and stands 0.5 to 2 times from a document, as the 22 earlier studies showed; for a tax computed from a statute it meets the state's own figure. All twenty rows are in `docs/reviews/impact-crosscheck-2026-11-16.json` and in the two tables of `docs/methods/forecast.md`, section 12.3.

**Run it in Stata**

```stata
cd "C:\path\to\erw\replication\impact"
log using "impact_stata_2026-11-16.log", text replace
do replicate.do
log close
```

Before it, once, from the repository's root: `python replication/impact/replicate.py --in-dir warehouse/output --rows`

Expected:
- `1. construction jobs, job-years: 515.1` (the page: 515)
- `2. operating jobs, each year: 44.74` (the page: 44.7)
- `3. construction earnings, USD of 2025: 41,045,772` (the page: USD 41 million)
- `4. taxes, present value, USD of 2025: 19,915,038` (the page: USD 19.9 million)
- `5. earnings, present value, USD of 2025: 83,592,616` (the page: USD 83.6 million)

The whole replication: `python replication/impact/replicate.py --in-dir warehouse/output` prints `7593 of 7593 inside the tolerance`.

**The rulings, in plain words** (each with the default taken; nothing on the page was changed)

1. **"Taxes, present value" adds only the taxes that have a figure and does not say which.** Texas wind's USD 19.9 million is sales tax alone; a Nevada geothermal plant shows USD 0 while its property and sales taxes are "not held". Default: unchanged.
2. **Nevada's 20 abated years are counted from the first construction year.** The state's own note counts them from the first operating year; the difference is 8 percent over 20 years for Lone Mountain. Default: unchanged.
3. **Geothermal has no taxable share for sales tax.** Nevada's notes give one plant's (3.3 or 48 percent of the investment, the two notes disagree). Default: stays "not given".
4. **New Mexico's district ad valorem production tax is left out of severance** (no district is asked). Default: unchanged, now said in the note.
5. **A tax levied beside the property tax stands alone on the property tax rows** (Wyoming's wind excise, Iowa's generation tax, Vermont's): Rail Tie Wind's USD 36.2 million "property tax over the life" is the excise alone. Default: unchanged.
6. **A Louisiana severance figure is computed from a rate whose warehouse table is held "license needed".** Default: unchanged, as `/severance` draws the same rate; rule it with `/severance`.
7. **The left box prints each default in grey under its field.** Your rule 9 of 16 November says defaults are hover tips only. Default: unchanged (you review this page yourself).
8. **Utah's credit** (the data request below): read it as a credit, as a deduction, or model its phase-out. Default: the file as it stands.
9. Still open from 13 November: rows 13 and 21 of `docs/reviews/forecast-faults-2026-11-13.md` (the shared chart's labels).

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 11:40 | 7506 | `site/data/forecast/income_tax.json` (builder `warehouse/forecast/params.py`) | Utah's `standard_deduction_single` is 966 and its text is "$966 credit": the builder tests the word "credit" only in the personal exemption's column. Hold Utah's figure as a credit (or as Samuel rules, faults row 4 of `docs/reviews/impact-faults-2026-11-16.md`), write the file again, and say what `/impact?tech=geothermal&state=ut&mw=86&start=2026` then shows for "State income tax over the life" (today USD 28.4 million) | Tax Foundation, state individual income tax rates and brackets, 2026 (the file's `source_url`) | requested |
| 2026-11-16 11:40 | 7506 | `capacity_factors.json`, `deflator.json`, `gas.json` against `lbnl_wind_capacity_factors`, `lbnl_solar_projects`, `eia860_plants_annual`, `eia_steo_forecasts` | These four tables are not on samueloldlaptop. Recompute from them and say equal or not: the wind medians (Texas 0.3692 over 83 plants; national 0.3832 over 388), the solar median (national 0.2210 over 764) and loading ratio (1.3247 over 761), the index of 2017, 2023 and 2025 (99.99975, 122.452, 128.90425) and the 2025 Henry Hub mean (3.5267) | the tables' own sources (LBNL, EIA-860, EIA STEO) | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 11:40 | 7506 | wip/7506-impact | `https://erw-flame.vercel.app/impact` | the A and B table at 1280 and at 390 px | Construction jobs 515; Operating jobs 44.7; Construction earnings USD 41 million; Sales and use tax USD 19.9 million; Taxes, present value USD 19.9 million; Earnings, present value USD 83.6 million; Property tax "not held", its hover "the local levy is not given"; no sideways scroll at 390 | wanted |
| 2026-11-16 11:40 | 7506 | wip/7506-impact | `https://erw-flame.vercel.app/impact?tech=land_based_wind&state=wy&mw=504&start=2028` | A and B, then open "Every year" | Property tax, first operating year USD 0; over the life USD 36.2 million; the table by year has an MWh column and Property tax USD 1.6 million from 2032 | wanted |
| 2026-11-16 11:40 | 7506 | wip/7506-impact | `https://erw-flame.vercel.app/impact?tech=geothermal&state=nv&mw=26.5&start=2026` | A and B | Taxes, present value USD 0, with Property tax and Sales and use tax "not held" (ruling 1) | wanted |
| 2026-11-16 11:40 | 7506 | wip/7506-impact | `https://erw-flame.vercel.app/impact?tech=geothermal&state=nv&mw=36&cost=4956.83&iaval=1&own=1.0917&ownyears=60` | A, "Property tax, first operating year"; the left box's Taxes group | USD 876,642 (the Department of Taxation's note: USD 876,653); the local option reads Yes | wanted |
| 2026-11-16 11:40 | 7506 | wip/7506-impact | `https://erw-flame.vercel.app/impact?tech=land_based_wind&state=mn&mw=228&start=2026` | the chart "Scenario A in other states", hover Minnesota; the taxes chart, hover a state | Minnesota is 4 of 51; the taxes chart's hover says whether a property tax statute is held | wanted |

## Landing request

- Head commit: the last commit of `wip/7506-impact` (the one that adds this report; its hash is in the session's reply).
- Tests: the eight files of "Tests" above (59 passed, 2 skipped) and the figures check.
- What changes: three method notes gain sections (one of them drawn at `/data/methods/economic_impact`, in review); new `replication/impact/` (5 files and `rows/.gitignore`), `site/scripts/impact-figures.mjs`, `site/scripts/impact-crosscheck.mjs`, `docs/reviews/impact-faults-2026-11-16.md`, `docs/reviews/impact-crosscheck-2026-11-16.json`, `tests/test_session7506_impact_replication.py`.
- What does not: `site/app/impact/`, `site/lib/`, `site/data/`, any table, any workflow, `site/lib/release.ts`.
- Pages a snapshot would differ on: none of the 25 (every page is in review; the method page's new section is behind the in-review page).

## Needs the key

None.

## Decisions made without you

- The named projects are ten planned plants of EIA-860M (the page's own "Planned project" list), not built plants: the tool takes no first construction year before 2026. Scenario B of each is EIA's case size in the same state.
- The page's figures are read from its view drawn to HTML; the two other-states charts carry no keyed number, so their values come from the page's functions with the page's rule of which states are drawn, and each drawn state's name is checked in the chart.
- The test draws the page again from the day's table and compares the two implementations there, so no committed figure is compared with the day's data (your ruling of 11 October).
- `rows/` for Stata is written by `replicate.py --rows` and not committed (a copy of NLR's data must carry its whole notice).
- The research requests were delegated to a read-only helper with written rules; its log and the saved documents are in `runs/7506/` (ignored, not committed). Iowa's NREL report (TP-6A20-53187) was fetched and not used: it states no earnings.
- Nevada's project: the geothermal plant, because the other 2026 applications are solar with storage. Its dollar year is not stated and is taken as 2025.
- For Nevada's property tax the reader's inputs are the note's own rate (USD 3.1191 per 100 on 35 percent of value, 1.0917 percent of cost) and 60 years (the note's 1.5 percent a year is 66.7; the field's most is 60). Chosen before the figures were compared, not tuned.
- JEDI II's earnings and output are taken as millions of 2005 dollars (the table prints no unit).
- The parameter table check is kept in `replicate.py --parameters`; it compares the 414 rows it can place and says 354 are not compared.

## For Samuel's ruling

The nine items of "The rulings, in plain words" above, each with its default. One more: whether `docs.nlr.gov`'s redirected robots address is "no rule" (default taken: yes, as the earlier NREL reads from the same host).

## Seen in another tool (one line each)

- `/severance`: its New Mexico figure asks a district for the ad valorem tax; `/impact` passes none. Same record, two totals for the same gas (ruling 4).
