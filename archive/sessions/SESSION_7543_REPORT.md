# Session 7543 report: `/demand` read as a utility planner (chain 304, part C, samueloldlaptop, 16 November 2026)

Branch `wip/7543-demand-read`, stacked on origin/main `e6c266166`. The read: `docs/reviews/demand-read-2026-11-16.md` (18 rows). The test: `site/scripts/test-demand-read.mjs` (24 of 24).

## What was done

- The reader and five cases written first: a utility planner (load forecasting, a PJM member utility); PJM 2019 to 2026 and its record hour of 2 July 2026; ERCOT's summer peak of 22 July 2026 with the weather taken out; SPP's 2025 energy on both tabs; CAISO's 2026 so far beside California's retail sales; Virginia and New Mexico on the consumption tab.
- Every view drawn to HTML by the page's own function (no build: memory), from the site's committed copies; the consumption tab's live-set reads answered from this machine's EIA tables cut to the live set's 850 days. Every hover read.
- 12 site rows fixed with a test, 2 data machine rows, 3 rulings, 1 browser row (three reads).
- Two pages, one figure: `/grid`'s Records agree with this page's peak in 56 of 56 grid-years (MW and hour); the weather tab's summer peaks agree with the as-metered peaks in 34 of 34; the All grids tab's growth is another period, now said with its figure; the explorer's words on retail sales and on the hour are now this page's too.
- Files of the other machine's stack touched (the tool is the lab desktop's, chain 301): `site/app/demand/page.tsx`, `site/components/demand/Weather.tsx`, `site/lib/demandpage.ts`, `site/lib/demandweather.ts` (two functions added, nothing changed), `site/app/consumption/view.tsx`, `site/scripts/check-demand-weather.mjs` (the summary's counts). Not touched: the method notes, `replication/demand/`, the signature pack, `site/lib/decisions.ts`, `site/lib/license.ts`, `site/components/Num.tsx`, `site/lib/release.ts`, any table or builder, any `site/data` file.
- Tests run: `test-demand-read.mjs` 24 of 24; pytest `test_session114_part2, 126, 129, 152, 239, 331` (128 passed, 5 skipped by their rules) and `7018_demand_done, 7022_demand_growth, 7508_demand_growth, 7517_demand_growth_read` (31 passed); `tsc` with the site's settings on the five changed source files and what they import: exit 0. Not run: `check-demand.mjs`, `check-demand-weather.mjs`, `check-values` (they need a built site).

## What to review

- `https://erw-flame.vercel.app/demand?area=pjm`: under the lead, after "Weather is not removed.", rest on "Demand at the grid is not retail sales." (the explorer's line); in "Year by year" rest on the heads "On the year before, percent" (ERCOT +5.57 here and +5.21 on the All grids tab, same table, another period) and "When, local time" (an hour named by its start); in "Where the growth is" rest on "How to read the cells" ("dark grey a fall").
- `https://erw-flame.vercel.app/demand?area=caiso`: the line after the lead also reads "California's base year is low in its early months." with the register's entry on hover and a link to `/data/faults`.
- `https://erw-flame.vercel.app/demand?view=weather&figure=summer&year=2026`: the sentence above the chart reads "... in 0 of the 7 grids that hold the figure, and by less than it explains in 1: NYISO (-7.8 percent, give or take 3.9); in 1 ... smaller than the fit's own error; in 5 the peak hour was hotter than any hour of 2019 to 2021, beyond the weather the fit saw, so the figure is not called a finding: ERCOT (+16.0 ...)". Rest on a "Metered, MW" cell.
- `https://erw-flame.vercel.app/demand?view=weather`: the default sentence is word for word as before; rest on ERCOT 2025's "55,666" (55,717 on the as-metered tab, 51 MW apart, and why).
- `https://erw-flame.vercel.app/demand?view=consumption`: whole MWh; "What is compared" and "How to read the table" hovers in place of the grey notes; rest on New Mexico's residential "no data" (2026-03 to 2026-06).

## Needs the key

- Nothing. No model was called.

## Decisions made without you

- The consumption tab's hovers use the page's own placeholder (`components/demand/Hint.tsx`), which draws its words grey with a dotted line, as the other two tabs have since session 152 (ruling row 16 asks whether to restyle it).
- The line on retail sales and the California base are read from the files that hold them on another page (`app/explore/demand-growth/Decisions.tsx`, `data/data_faults.json`), not copied, so the pages cannot drift apart.
- The summary of the weather tab keeps its sentence word for word wherever no finding is below zero and no peak is beyond the fit's weather (the default view among them); its check keys `sum|found` and `sum|not` now count the grids above zero and the grids inside the fit's error, and `check-demand-weather.mjs` is changed to match.
- Sales in whole MWh, not TWh: the column's unit is unchanged, the hundredths dropped (the raw value stays on each check key).

## For Samuel's ruling

- Row 15: a zone's own growth (Dominion's and every EIA-930 sub-region's): default not on `/demand` until `subregion_demand_growth` is on Redivis's draft and in the live set (your upload).
- Row 16: the hover placeholders of `/demand` are grey text: default kept; one change restyles them to ink across the three tabs.
- Row 17: the weather tab calls no 2026 summer peak a finding in five of seven grids, because each was hotter than any hour of 2019 to 2021: default the method's three years stay.

## Rows for the coordinator

### (a) Landing request (`docs/state/landing_request_oldlaptop.md`)

| 41 | `wip/7543-demand-read` | the branch head (in the return) | `7543-demand-read` | 7543 | 2026-11-16 | `site/scripts/test-demand-read.mjs` (24 of 24, every view drawn to HTML by the page's own function without a build, the consumption tab on made-up rows, five cases); pytest `test_session114_part2, 126, 129, 152, 239, 331, 7018_demand_done, 7022_demand_growth, 7508_demand_growth, 7517_demand_growth_read`: 159 passed, 5 skipped by their rules; `tsc` on the five changed source files, exit 0; not built here (memory); `check-demand`, `check-demand-weather`, `check-values` and `check-routes` not run | requested |

## Row 41: what it holds (chain 304, part C, session 7543, `/demand` read as a utility planner)

- **Stacked on** origin/main `e6c266166`. Report: `archive/sessions/SESSION_7543_REPORT.md` on the branch.
- **What changes:** `site/app/demand/page.tsx` (the line on retail sales and, for California, the base year, after "Weather is not removed."; the hovers of "On the year before, percent" and "When, local time"; the heat map's hover: "dark grey a fall" and how an hour is named; the consumption tab's line on retail sales), `site/components/demand/Weather.tsx` (the summary sentence in four parts; the "Metered, MW" head and cell hovers), `site/lib/demandpage.ts` (`HOUR_WHY`, `CA_BASE_FAULT`, `caBaseWhy`, type `Fault`), `site/lib/demandweather.ts` (`summaryParts`, `meteredWhy`), `site/app/consumption/view.tsx` (whole MWh; the two grey notes as hovers; a "no data" cell's hover names its missing months, `missingWhy`; an empty energy-review read is said, not thrown), `site/scripts/check-demand-weather.mjs` (the summary's counts). New: `site/scripts/test-demand-read.mjs`, `docs/reviews/demand-read-2026-11-16.md`.
- **What does not change:** any table, builder or `site/data` file; the method notes, `replication/demand/`, the signature pack; `site/lib/decisions.ts`, `site/lib/license.ts`, `site/components/Num.tsx`, `site/lib/release.ts`, `check-values.mjs`; `app/explore/demand-growth/Decisions.tsx` (read, not changed). No figure on the as-metered or weather tab moves and no check key is renamed; the weather summary's `sum|found` and `sum|not` count the grids above zero and inside the fit's error (the same numbers wherever no finding is below zero and no peak beyond the fit's weather, the default view among them), and two keys are new (`sum|down`, `sum|beyond`). The consumption tab's sales are printed whole (their check keys and raw values as before).
- **Before landing:** a site build on the landing machine; `node --import ./scripts/battery-awards-page-register.mjs scripts/test-demand-read.mjs`; `check-demand.mjs` and `check-demand-weather.mjs` on the build; `check-values` on `/demand` (three tabs).
- **Snapshot differences to expect:** none on the 25 addresses (`/demand` is in review; a visitor is shown the in-review page). **Tables:** none.
- **After the landing:** browser reads 196 to 198; data requests 169 and 170 are the data machine's and do not hold this row.

### (b) Browser reads (`docs/state/browser_reads_wanted.md`)

| 196 | 2026-11-16 | 7543 | `wip/7543-demand-read` (row 41) | `https://erw-flame.vercel.app/demand?area=caiso`, at 1280 and at 390 px | The line under the lead ("Weather is not removed. ... Demand at the grid is not retail sales. ... California's base year is low in its early months. The register's entry."); hover each placeholder; hover the heads "On the year before, percent" and "When, local time" | The line wraps without sideways scroll at 390 px; the retail-sales hover begins "Demand at the grid is not sales to customers."; the California hover begins "EIA's California demand stands about 3,000 MW under CAISO's own load"; the two heads show their hovers (CAISO +0.24 here, +5.18 on the All grids tab; "An hour is named by its start") and the table still scrolls in its frame | wanted |
| 197 | 2026-11-16 | 7543 | `wip/7543-demand-read` (row 41) | `https://erw-flame.vercel.app/demand?view=weather&figure=summer&year=2026`, at 1280 and at 390 px | The sentence above the chart; hover a "Metered, MW" cell and its column head | The sentence reads "... and by less than it explains in 1: NYISO ...; in 1 ... smaller than the fit's own error; in 5 the peak hour was hotter than any hour of 2019 to 2021 ..."; a cell's hover gives its hours and the as-metered highest hour ("the same hour"); no sideways scroll | wanted |
| 198 | 2026-11-16 | 7543 | `wip/7543-demand-read` (row 41) | `https://erw-flame.vercel.app/demand?view=consumption`, at 390 px | The two placeholders "What is compared" and "How to read the table"; New Mexico's and Colorado's residential "no data"; the MWh columns | The placeholders show the old notes' words on hover; "no data" names its months (New Mexico 2026-03 to 2026-06, Colorado 2026-05, or none if the data machine filled them); MWh are whole; the tables scroll in their frames, the page does not | wanted |

### (c) Data requests (`docs/state/data_requests_done_line.md`)

| 169 | 2026-11-16 | 7543 (chain 304, samueloldlaptop; branch `wip/7543-demand-read`) | `eia_retail_sales_monthly` | No row for `eia:retail_sales:NM:RES` of 2026-03, 2026-04, 2026-05 and 2026-06, nor for `eia:retail_sales:CO:RES` of 2026-05, in the copy retrieved 5 November 2026, while both states' all-sector rows of those months are held; `/demand?view=consumption` draws "no data" for both. Say whether EIA's API gives these five months (withheld by EIA, or dropped by the connector) and, if it does, fill them and load the live set | EIA API v2, electricity/retail-sales (Form EIA-861M); the read's rows 10 and 13 | requested |
| 170 | 2026-11-16 | 7543 (chain 304, samueloldlaptop; branch `wip/7543-demand-read`) | `eia930_demand_weather`, `site/data/demand_weather.json` | Built 6 October 2026 with weather to 27 September 2026, while the as-metered copy (`demand_growth.json`) is of 6 November; no schedule builds it (`warehouse/run_daily.sh`, the workflows). Rebuild with NOAA's hours to the newest day (`warehouse/derived/demand_weather.py --snapshot`) and say whether it should join a schedule | NOAA NCEI Local Climatological Data; EIA-930; the read's row 14 | requested |

### (d) Progress (`docs/state/progress_c304.md`, part C)

done `<head>` on `wip/7543-demand-read` (landing row 41): the reader a utility planner (load forecasting, a PJM member utility) reading three tabs (as metered, weather taken out, consumption); five cases (PJM 2019 to 2026 and its record hour of 2 July 2026; ERCOT's summer peak of 22 July 2026 with the weather taken out; SPP's 2025 energy on both tabs; CAISO's 2026 so far beside California's sales; Virginia and New Mexico's sales); `/grid`'s Records agree 56 of 56 grid-years, the weather tab's summer peaks 34 of 34; rows: 18 (12 site fixed, 2 data machine, 1 browser (three reads), 3 rulings)
