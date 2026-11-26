# The consumption page: its figures audited as a hostile expert would

Session 10214, chain 710 part D, 26 November 2026, the old laptop. Platform tool 23 (`docs/platform-tools.md`), "who uses the power, and where load is growing": `/demand` and its four views (as metered, the default; with the weather taken out; consumption; the whole country). Read as a utility load forecaster and an AI lab's siting team asking where load is growing, who want to find it wrong. The Grid audit of tonight (`grid-model-audit-2026-11-26.md`) is not repeated.

- Nothing changed on main but this file, its evidence folder (`docs/reviews/demand-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Each finding has its own branch, `wip/audit-demand-<n>`. Words-only fixes (branches 1, 3, 4, 5, 7) are for landing; branches 2, 6 and 8 show a figure and wait for the owner. Two data requests.

## In short

- **The arithmetic is right.** Every figure the default view prints (ERCOT, ranked by average demand) follows from EIA's hours as the note says: 87 of its 91 marked figures came out to the digit in an independent restatement from EIA-930's workbooks, and the other four are explained to the digit (the year so far needs October hours this machine holds only in part; formed from the page file's own ten months it is equal). Over the whole page file, every value of the whole years 2019 to 2025 of all eight areas is equal (24,204 values and peak hours equal; the 14 that differ are October 2026 hours missing here and EIA's revisions of the Lower 48). The consumption view restates equal too.
- **A peak the page prints as metered is EIA's estimate (finding 1).** MISO reported nothing on 24 July 2025; EIA's Adjusted demand filled the day, and its 120,343 MW is MISO's "highest hour of 2025" on the default view's ranking (+3.21 percent on 2019). MISO's own highest report is 118,106 MW (+1.29). The page says "Nothing is filled", true of the ERW, silent on EIA: 351 hours of the seven authorities since 2019 are EIA's estimates. Words for landing; the figure is the owner's.
- **"The same growth with the weather taken out" is not the same growth (finding 2).** The weather view measures against the mean of 2019 to 2021, a base with the lockdowns in it; for 2025, MISO +2.20 here and +4.10 there, NYISO -2.73 and -0.48. Words, for landing.
- **"The growth is largest in January at 02:00" is the weather of one month (finding 3).** It is the largest of 288 cells, one month of 2025 against one of 2019; the cell moves every year (July 02:00 to 2023, October 16:00 to 2024), and January 2025 was the coldest January held for ERCOT's cities. A siting team reads overnight growth as new flat load. Words, for landing.
- **"Where industrial and commercial load is growing fastest" ranks billing classes (finding 4).** Texas is sixth for commercial growth (+13.7 TWh) in the twelve months its industrial sales fell 7.7 TWh, the industrial line turning below the year before in every month from January 2026; the months are EIA's sample estimates, revised later; the sector totals hold 16 to 42 percent losses. Words, for landing.
- **One base year carries every growth (finding 7).** 2019 is the last whole year before the pandemic, as the page says, but EIA's file holds 2018 whole too. On 2018, CAISO's 2025 average is -0.74 percent (+4.45 on 2019), MISO's -0.63 (+2.20), NYISO's -5.92 (-2.73), PJM's +2.66 (+5.37): two grids change sign. The owner's ruling.
- **Smaller, and what is right.** ERCOT's "48 blank" hours hold a day after the record in every area (finding 5, the owner's); the year so far's newest month moves with EIA's revisions, the Lower 48's by 828 MW in a week (finding 6, words). Right as stated: growth between two years, not a trend (the trend's rate is within half a point a year of the endpoints' in every grid); no growth worded as caused by datacenters; state and balancing authority kept apart; ISO-NE, MISO and NYISO reach the page only through EIA-930 (public domain) and NOAA, never an operator's held table.
- **What a forecaster would add:** load by zone inside a grid (where in ERCOT the +27 percent sits: a data request), use per customer, weather-normal peaks, the large-load pipeline, and the size of EIA's revisions to retail sales (a data request).

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/demand/page.tsx` | The page. Four views in the address (`lib/demandpage.ts`); with none it draws the as-metered view for ERCOT ranked by average demand. The as-metered view (`MeteredView`): the summary sentence, three headlines, the years chart and table, the hours left out, the month-and-hour heat map and its extremes, change by month and by hour, the ranking of eight areas, California's break check (CAISO only), the decisions block. The hovers of "On the year before" (`yoyWhy`, the All grids tab's twelve months), "When, local time" (`HOUR_WHY`), demand against sales (`AGAINST_SALES`), California's base (`CA_2019`) |
| `site/lib/demandgrowth.ts` | The page's reading of its file: choices, the whole years, the year so far, the cells, by month and by hour, the extremes, the ranking, number formats. No arithmetic beyond picking and sorting |
| `site/lib/demandpage.ts` | The views, their addresses and method links, `HOUR_WHY`, the California fault's words |
| `site/components/demand/Growth.tsx`, `Hover.tsx`, `Hint.tsx` | The three charts (years, heat map, change bars), the mouse card, the hover placeholder |
| `site/components/demand/Weather.tsx`, `site/lib/demandweather.ts` | The second view: growth against the mean of 2019 to 2021, the part temperature and dew point explain, the rest with its uncertainty; the check on years left out; the 35 stations; New England under two rules; California across December 2025 |
| `site/app/consumption/view.tsx` | The third view: EIA-861M retail sales by state and sector (twelve months against twelve), the fastest growing states by sector, the shares table, and the Monthly Energy Review's industrial and commercial energy. Reads the live set |
| `site/components/demand/Country.tsx`, `CountryForecast.tsx`, `site/lib/countrydemand.ts`, `countryfiles.ts` | The fourth view: EIA's thirteen regions and every balancing authority from the data machine's page files, with a license gate; forecast against actual. Not re-done here (its replication met 449,440 of 449,440 on 19 November) |
| `site/lib/decisions.ts` `DEMAND_DECISIONS` | The nine decisions at the foot of the as-metered view, word for word in the note |
| `site/lib/siting.ts` `demandGrowth` | The All grids tab's twelve months over the twelve before, read by the "On the year before" hover |
| `site/data/demand_growth.json` | The page's file: eight areas, years 2019 to 2026 (2026 to October), built 2026-11-06 00:25 UTC from EIA's workbooks of 5 November |
| `site/data/demand_weather.json` | The weather view's file, built 2026-11-17, weather to 2026-11-06 |
| `warehouse/derived/demand_growth.py`, `impossible_hours.py`, `caiso_join.py` | The builder: EIA's Adjusted demand (the Lower 48's Demand), the hour dated by its start, California's late hours set back, the screen (within 25 percent of the median of the four hours around, above zero, within a third to three times the area's median), 95 and 90 percent rules, growth on 2019 |
| `warehouse/derived/demand_weather.py`, `warehouse/connectors/noaa_grid_weather.py` | The weather view's table and its weather (not rebuilt here) |
| `warehouse/connectors/eia_series.py` | The two consumption tables (`eia_retail_sales_monthly`, `eia_sector_energy_consumption_monthly`) |
| Notes | `docs/methods/demand_growth.md`, `demand_weather.md`, `consumption.md`, `eia_sector_energy_consumption_monthly.md`, `eia930_caiso_break.md`, `impossible_hours.md`; `replication/demand/`, `replication/demand_growth/` |

## The default view re-done, to the digit

The page is drawn with its own default export (`draw_demand.mjs`: no build, no server, every request refused, async parts awaited first). It marks 91 figures (`main_default_figures.json`, words in `main_default.txt`).

- **The restatement.** `extract.py` streams EIA-930's eight workbooks of 3 October 2026 (the main copy's raw folder, read only) to the hour's start, EIA's Demand and EIA's Adjusted demand. `restate.py` (standard library, none of the warehouse's or the site's code, written from the note's "Input", "Which hours are used", "The rows" and "The rule in full") rebuilds every value of the page's file from those hours, one UTC year at a time in memory. The range test is decided from the yearly medians; it leaves no hour's fate open in seven areas and six hours of ISO-NE open, none of which reaches a figure. October 2026, which the workbook of 3 October lacks, is taken from the main copy's `eia930_all_demand` (EIA's hourly route, read 13 November).
- **The whole file** (`restate_oct.out`): 24,204 values and peak hours equal. Every value of the whole years 2019 to 2025 of all eight areas is equal, and so are every month of 2026 to September of the seven authorities. What differs: the year so far and October of ERCOT, CAISO and PJM (EIA's hourly route lacks 48 to 55 of their October hours here, so October falls under 95 percent), and the Lower 48's August to October 2026 and year so far (EIA's revisions: August 592,629.3 MW in the file against 592,625.6 in the workbook of 3 October; September 541,551.6 against 541,210.6; October 460,894.6 against 460,066.5 on the hourly route). The 23 values only the restatement holds are the change rows in MW, which the file predates.
- **The default view** (`compare.out`): **87 of 91 marked figures equal from the hours.** The four others: the blank hours (72 in the run with October padded, where the API's missing days count as blank; 48 in the run on the workbook alone, equal), and the year so far of CAISO, PJM and the Lower 48 in the ranking (+11.10, +8.47, +10.21 from the hours, for the reasons above; +10.98, +8.34, +10.24 when formed from the page file's own ten months each weighted by its local hours, equal). ERCOT's own year so far is formed the same way (every hour of the window used, 7,295 of 7,295): +33.34 percent, 59,723 MW, equal; its highest hour so far (91,075 MW, 22 July 2026 17:00) equal from the hours.

| Figure (ERCOT, as metered) | Page | Restated |
|---|---|---|
| Average demand 2019, 2025 | 43,798 MW; 55,717 MW | the same (43,797.6; 55,717.2) |
| Growth since 2019 | +27.22 percent | +27.22 |
| Highest hour 2019, 2025 | 74,533 MW (12 August 2019, 16:00); 83,597 MW (18 August 2025, 17:00) | the same hours and values |
| Peak growth | +12.16 percent | +12.16 |
| 2026 so far against 2019 | +33.34 percent (59,723 against 44,791 MW) | the same |
| Year by year, 2020 to 2025 | averages, growths, year on year, peaks, peak growth, hours used | 42 of 42 equal |
| Hours left out | 0 apart, 0 at or below zero, 48 blank | the same (workbook run) |
| Largest and smallest cell | January 02:00 +42.55 (15,250 MW); September 14:00 +14.29 (9,034 MW) | the same; 288 of 288 cells held |
| The ranking | ERCOT, SPP, Lower 48, PJM, CAISO, MISO, ISO-NE, NYISO; 23 figures | the same order; 20 equal from the hours, 3 from the file's months |
| "On the year before" hover | +5.57 here; the All grids tab +5.21 (November 2025 to October 2026) | +5.57; +5.21 |

- **The consumption view** (`consumption.py` on the main copy's tables, set beside the view drawn from a fixture of the same rows, `draw_consumption.mjs`, `main_consumption.txt`): United States sales 4,122,912,132 MWh, +1.8 percent on the twelve months before, the four shares (37.0, 37.3, 25.5, 0.2 percent), and the twenty rows of the two "fastest" lists, equal. The live set may hold a newer month than this machine.

### One rule changed at a time

`measures.py` (`measures.out`), on the restated rows and the page's own files.

| Rule | The page | Changed to | Measured worth (2025's average demand unless said) |
|---|---|---|---|
| The base | 2019 | the mean of 2019 to 2021 (the weather view's) | MISO +2.20 becomes +4.04; NYISO -2.73 becomes -0.62; PJM +5.37 becomes +6.98; ISO-NE -2.54 becomes -1.38; Lower 48 +7.03 becomes +8.27; ERCOT +27.22 becomes +26.65; CAISO +4.45 becomes +3.20 |
| The base | 2019 | 2018 (whole in the same workbooks; `restate.py --base 2018`, `base2018.out`) | ERCOT +29.54; CAISO -0.74; PJM +2.66; MISO -0.63; SPP +9.62; NYISO -5.92; ISO-NE -6.51; Lower 48 +6.04. Peaks: CAISO -4.93, PJM +5.99, MISO +0.51 |
| The base | 2019 | 2021; 2022 | ERCOT +24.35; +13.35. PJM +5.91; +4.07. MISO +3.36; +1.63 |
| Endpoints | two years | a least-squares line through the logs of 2019 to 2025 | a year: ERCOT 4.09 becomes 4.54, SPP 1.78 becomes 2.05, PJM 0.88 becomes 0.92, MISO 0.36 becomes 0.48, Lower 48 1.14 becomes 1.33; without 2020, ERCOT 4.31, PJM 0.67 |
| The column | EIA's Adjusted demand | EIA's Demand (the authority's own report) | the largest move of any whole-year growth: MISO's 2025 peak +3.21 becomes +1.29 (finding 1); CAISO's 2025 average +4.45 becomes +4.58; all else within 0.1 point |
| The screen | the neighbour test | none (above zero and the range only) | PJM's 2020 peak becomes 224,345 MW (+44.48 percent), its 2019 peak 155,276 MW in December; CAISO's 2019 average 20 MW lower. The screen is needed and does what it says |
| The last year of the cells | 2025 | 2023; 2024 | ERCOT's largest cell: July 02:00 (+26.95); October 16:00 (+35.13); 2025's is January 02:00 (+42.55). Every area's moves (finding 3) |
| The weather | as metered on 2019 | the weather view's split (against 2019 to 2021) | ERCOT 2025: +26.55 = weather +2.37 + not explained +24.18 (give or take 4.04); SPP +12.70 = +0.18 + +12.52; NYISO -0.48 = -0.45 + -0.03 |

## Each claim against the code

- **Retail sales, total demand and net generation.** The as-metered view is demand at the balancing authority (EIA's Adjusted demand), which holds losses and, in California, the batteries' charging; the consumption view is retail sales, which leave out losses. The hover "Demand at the grid is not retail sales" says both, with figures (Texas sales +24.20 against ERCOT +27.22, 2019 to 2025). Net generation is not used on this page. Right. "United States retail sales" beside the Lower 48 is the 50 states and Washington beside the lower 48: named as such. Right.
- **Sector definitions and EIA's reclassifications.** The view ranks a class's sales as "load" growing; it shows neither the other class nor the all-sector change beside the list. **Finding 4.** The transportation column is said to be electric rail and transit, counted only in some states. Right.
- **Year on year against a trend.** The page says its growths are "differences between years, not a trend line" (the weather hint) and every growth is since 2019 or on the year before. Right as stated; the trend's rate is within half a point a year of the endpoints' in every grid (measured above).
- **Base year chosen after looking.** The decision says 2019 is "the last whole year before the pandemic in the file", which is true, and nothing shows it was chosen after looking. But EIA's per-area workbooks hold 2018 whole too (every area 8,712 to 8,760 hours used by the same screen; the builder reads 2018 for the screen's median and writes nothing of it), and a single base year carries its own weather and faults into every growth: on 2018 two grids' signs turn. **Finding 7.** The second view's base differs again: **finding 2.**
- **Months not whole.** The year so far ends with the last whole month (October; the file was built 6 November). A whole year is written at 95 percent of its hours used: ERCOT's 2025 is 8,736 of 8,760 (24 hours blank in December 2025), said in the table. Right.
- **EIA's revisions.** The Lower 48's newest months move with each workbook while EIA fills its members' late hours; the year so far's hover did not say so. **Finding 6.** EIA's estimates inside Adjusted demand: **finding 1.**
- **Weather normalization.** The second view: 35 airport stations, five a grid, weighted by 2020 metropolitan population; degrees from 65 F taken at each station, then weighted; a fit on 2019 to 2021 (the lockdowns of 2020 in it, said in the check's hover); dew point adopted by a rule set before the numbers. The page says what the remainder is not. Right as stated. Not on the page: ERCOT's five cities leave out west Texas, "where much of ERCOT's new load is" (the note says so).
- **Growth "because of datacenters".** No sentence of the four views gives a cause. The weather view's hover lists datacenters among things the remainder holds together and says the warehouse cannot split them; the note's list says who uses the power is not told apart. Right. The heat map's sentence invited the reading: **finding 3.**
- **State against balancing area.** The as-metered view is balancing authorities, the consumption view states; the sales hover says "A state is not a balancing authority"; the fourth view sets a region beside its grid with the data machine's sentence on why they differ. Right.
- **Held grids.** ISO-NE, MISO and NYISO reach the first two views only through EIA-930 (public domain) and NOAA; the fourth view draws a file whose license is not public with every cell blank. No operator's held table reaches a figure. Right.
- **The window.** Whole years 2019 to 2025 and January to October 2026, each said; the source line gives the build date; the consumption view names its newest month (2026-08) and the Monthly Energy Review's (2026-07). Right.
- **"The year's highest hour".** An hourly average, said in the decisions (ERCOT's own 2023 record 85,508 against 85,432 here). One of 105 peaks is an hour EIA estimated: **finding 1.**
- **"Hours left out: 48 blank".** **Finding 5.**

## What a forecaster's own number would hold that this does not

- **Where inside a grid.** ERCOT's +27.22 percent is one number for a grid of eight weather zones; a siting team asks which. EIA's ERCOT workbook carries eight subregions; this machine holds no table of them since 2019. A data request (row 1 below).
- **Use per customer against customers.** `eia_retail_sales_monthly` holds customer counts beside sales; the view shows neither customers nor sales per customer. Not measured here.
- **Weather-normal peaks.** The as-metered peaks are the year's hottest hour (ERCOT's 2025 peak is below 2024's); the weather view gives summer and winter peaks with a give or take of 6 to 7 points. A forecaster's 50/50 peak is not held.
- **The large-load pipeline.** The page links the interconnection queue; it draws no large-load request (`ercot_large_load_status` exists for ERCOT). Forecasts are several times the growth metered since 2019 (the note's table of published forecasts).
- **Behind the meter and storage.** CAISO's midday cells fall (July 15:00 -12.33 percent to 2025) while 08:00 to 11:00 rise, the batteries charging; the note sizes the charging (1,690 to 2,114 MW). A forecaster adds back rooftop solar; not held.
- **The revisions to retail sales.** Not measured: one vintage is held here. A data request (row 2 below).

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Moderate | MISO's highest hour of 2025, on the default view's ranking and MISO's view, is EIA's estimate in its Adjusted demand; the page says "Nothing is filled" and never says Adjusted demand holds EIA's estimates | MISO reported nothing on 24 July 2025; 120,343 MW (+3.21) against its own highest report 118,106 MW (+1.29); 351 hours of the seven authorities 2019 to 2025 are EIA's (ERCOT 24, CAISO 94, PJM 171, MISO 58, SPP 2, ISO-NE 2) | `wip/audit-demand-1` (words); `wip/audit-demand-2` (the figure) | words, for landing; figure, the owner's |
| 2 | Moderate | "The same growth with the weather taken out" links a view measured against another base (the mean of 2019 to 2021) | 2025: MISO +2.20 against +4.10, NYISO -2.73 against -0.48, PJM +5.37 against +7.16, CAISO +4.45 against +2.86 | `wip/audit-demand-3` | words, for landing |
| 3 | Moderate | "The growth is largest in January at 02:00" names the largest of 288 cells of one month against one month; it moves with the weather | ERCOT's largest cell to 2023, 2024, 2025: July 02:00, October 16:00, January 02:00; January heating degree days 568 in 2025 against 472 in 2019 | `wip/audit-demand-4` | words, for landing |
| 4 | Moderate | "Where industrial and commercial load is growing fastest" ranks billing classes, shows neither the other class nor the total, calls estimates final, and labels totals that hold losses as energy consumed | Texas commercial +13,653,363 MWh (+8.0, sixth) while industrial -7,672,895 and all sectors +9,358,908; industrial below the year before every month from January 2026; losses 15.8 percent of the industrial total, 42.4 of the commercial | `wip/audit-demand-5` | words, for landing |
| 5 | Minor | "Hours left out: 48 blank" counts the workbook's unfilled last day, after the newest hour used, in every area | 24 of ERCOT's 48; 23 to 25 hours in each area | `wip/audit-demand-6` | figure, the owner's |
| 6 | Minor | The year so far's newest month moves with EIA's revisions; the hover did not say so | the Lower 48's October 2026: 460,894.6 MW in the file, 460,066.5 a week later on EIA's hourly route (the replication saw 460,798.6 on 2 November, 461,062.9 on 9 November); the ranking's year so far +10.24 against +10.21 | `wip/audit-demand-7` | words, for landing |
| 7 | Moderate | Every growth rests on one base year; 2018, also whole in EIA's file, gives other signs | 2025 on 2018 against on 2019: CAISO -0.74 against +4.45; MISO -0.63 against +2.20; NYISO -5.92 against -2.73; PJM +2.66 against +5.37; ERCOT +29.54 against +27.22 | `wip/audit-demand-8` | figure, the owner's |

### 1. A peak printed as metered is EIA's estimate

- **Where.** `warehouse/derived/demand_growth.py` `read_demand` takes "Adjusted demand"; `site/app/demand/page.tsx` line 124 (the hover "Which hours are used", ending "Nothing is filled."); `site/lib/decisions.ts` `DEMAND_DECISIONS` key `adjusted`; `docs/methods/demand_growth.md`.
- **Why it is wrong.** EIA's workbook has the authority's own "Demand", an "Imputed demand" and the "Adjusted demand" the page reads. Where an authority files nothing, or a value EIA finds implausible, Adjusted demand carries EIA's estimate, and the screen passes it as a reported hour. The page and the note say nothing is filled and call the series the authority's demand.
- **How much.** `imputed.py` on the workbooks of 3 October 2026, local years 2019 to 2025: hours where Adjusted demand is held and Demand is blank or another value: ERCOT 24 (all in 2025), CAISO 94, PJM 171 (7 replaced, one of them 2,147,409,866 MW), MISO 58, SPP 2, ISO-NE 2, NYISO 0. `peaks_imputed.py`: of the file's 105 peaks, one is such an hour, MISO's 2025 (120,343 MW at 20:00 UTC on 24 July 2025; MISO's Demand is blank from at least 14:00 UTC that day to 02:00 the next). On MISO's own reports with the page's screen the 2025 peak is 118,106 MW on 29 July 2025, +1.29 percent on 2019 against +3.21; MISO stays sixth of seven in the peak column.
- **The tests.** `tests/test_audit_demand_1.py`: MISO's Demand is blank in the hour of the file's 2025 peak (passes where EIA's workbook extract is held); the words (fail on main, pass on the branch). `tests/test_audit_demand_2.py`: the peak on MISO's own reports, 118,106 MW, +1.29 (passes on main where the extract is held).
- **The fix on the branch.** Words only: the hover adds "Nothing is filled here. A grid operator's hours are EIA's Adjusted demand, which already holds EIA's own estimate for an hour the operator reported nothing for or reported implausibly, and such an hour is used as a reported one: MISO's highest hour of 2025 (24 July 2025, a day MISO reported nothing) is EIA's estimate." The decision and its note line say the same with the count; the note gains "EIA's estimates inside Adjusted demand". Drawn and read (`b1_draw_default.txt`, `b1_draw_miso.txt`): the 91 figures unchanged.
- **For the owner.** Reading the authority's own Demand where EIA estimated moves MISO's 2025 peak from 120,343 to 118,106 MW (+3.21 to +1.29 percent) and CAISO's 2025 average growth from +4.45 to +4.58; nothing else by more than 0.1 point. Default: left as it is.

### 2. Not the same growth

- **Where.** `site/app/demand/page.tsx` line 86.
- **Why it is wrong.** The link said "The same growth with the weather taken out". The second view's growth is against the mean of 2019 to 2021 (`demand_weather.json` `train`), not 2019, and 2020 holds the lockdowns, so a reader crossing the tab sees another figure for the same grid and year.
- **How much.** 2025's average demand: MISO +2.20 here, +4.10 there; NYISO -2.73 and -0.48; PJM +5.37 and +7.16; SPP +11.14 and +12.70; CAISO +4.45 and +2.86; ISO-NE -2.54 and -1.28; ERCOT +27.22 and +26.55.
- **The test.** `tests/test_audit_demand_3.py`: the two files' bases and MISO's two figures (passes on main); the words (fail on main).
- **The fix on the branch.** "Growth with the weather taken out is the second view; it is measured against the mean of 2019 to 2021, not against 2019 alone, so its growth is not this view's figure." The note's line on the second view gives the four pairs. Drawn and read (`b3_draw_default.txt`).

### 3. The cell that grew most is a month's weather

- **Where.** `site/app/demand/page.tsx` line 109 (the summary); `lib/demandgrowth.ts` `extremes`.
- **Why it is wrong.** The summary named, as where "the growth is largest", the most extreme of 288 cells, each one month of 2025 against the same month of 2019. Its hover-free sentence reads as a fact about the grid; for a siting team overnight growth reads as new flat load. The heat map's hover says a hot or mild month colors a row; the sentence did not.
- **How much.** ERCOT's largest cell to 2023: July 02:00 (+26.95); to 2024: October 16:00 (+35.13); to 2025: January 02:00 (+42.55). ERCOT's January heating degree days (five cities, weighted): 472 in 2019, 561 in 2024, 568 in 2025, the most of the eight Januaries held; the January 02:00 cell was 35,837 MW in 2019, 47,914 in 2024, 51,087 in 2025. Every area's largest cell moves between those three last years.
- **The test.** `tests/test_audit_demand_4.py`: from the page's file, the largest cell to 2023, 2024 and 2025 (passes on main); the words (fail on main).
- **The fix on the branch.** "Of the cells of month and hour, the one that grew most is January at 02:00 (+42.55 percent), one month of 2025 against the same month of 2019: a cold or hot month can make it, and the cell that grows most moves from year to year." The note gains "The cell that grew most". Drawn and read for ERCOT and PJM (`b4_draw_default.txt`, `b4_draw_pjm.txt`); the figure unchanged.

### 4. A sector is a billing class

- **Where.** `site/app/consumption/view.tsx`: the section "Where industrial and commercial load is growing fastest" and its note (line 155); the Monthly Energy Review's note (line 250). `docs/methods/consumption.md`.
- **Why it is wrong.** EIA's sectors are the classes sellers bill under; customers move between them and sellers do not class a large customer alike. The list ranks a class's sales as load and shows neither the other class nor the state's total. The months are Form EIA-861M's estimates from a sample, revised with the annual survey; the view calls it a survey and no more. "Total energy consumed" in the Monthly Energy Review holds the sector's share of the electrical system's losses.
- **How much.** September 2025 to August 2026 on the twelve months before (`consumption.out`, `sector_months.out`): Texas commercial +13,653,363 MWh (+8.0 percent, sixth of the commercial list), Texas industrial -7,672,895 MWh, all sectors +9,358,908; Texas industrial ran above the same month a year before in every month of 2024 and 2025 but October 2025, and below it in every month from January 2026 (-699 to -2,168 GWh). Whether customers moved between the classes or EIA's sample changed with the year cannot be told from these rows. Arizona is in both lists. The Monthly Energy Review, twelve months to July 2026: industrial losses 5,012 of 31,740 TBtu (15.8 percent); commercial total less end use 7,305 of 17,233 (42.4 percent).
- **The test.** `tests/test_audit_demand_5.py`: Texas commercial up more than 10 TWh while industrial down more than 5 TWh (passes where the table is); the industrial total is end use plus losses; the words (fail on main).
- **The fix on the branch.** The list's note adds "A sector is the class a utility bills a customer under, and customers move between classes, so one sector's growth can be another's loss: read it beside the state's other sectors and all-sector change in the table below. The months are EIA's estimates from its monthly sample of sellers, revised when the annual survey is in." The energy note adds that a sector's total holds its share of the losses. The note gains "What a sector's change is and is not". The title is unchanged (a test of session 239 holds it). Drawn from a fixture of the main copy's rows and read (`b5_draw_consumption.txt`); every number unchanged.

### 5. A day of the blank hours is after the record

- **Where.** `warehouse/derived/demand_growth.py` (`since` runs to the workbook's last row); the page's line "Hours left out for ERCOT: ... 48 blank".
- **How much.** From the page's file: hours not used inside the years written against the count printed: ERCOT 24 of 48 lie after October 2026 (the workbook's last day, EIA's not yet filled); every area 23 to 25. The replication of session 7014 found it and the note says it in that section; the page does not.
- **The test.** `tests/test_audit_demand_6.py` (passes on main).
- **For the owner.** Counting to the newest hour used moves every area's blank count down by about 24 (ERCOT 48 to 24). Default: left as it is.

### 6. The newest month moves

- **Where.** `site/app/demand/page.tsx` line 92 (the hover "The year so far").
- **How much.** The Lower 48's October 2026: 460,894.6 MW in the file (built 6 November), 460,066.5 on EIA's hourly route as held on 13 November; the replication saw 460,798.6 on 2 November and 461,062.9 on 9 November. The ranking's year so far for the Lower 48 is +10.24 in the file and +10.21 on the later hours. The seven authorities' months to September agree with the workbook of 3 October to the digit.
- **The test.** `tests/test_audit_demand_7.py`: the October mean on the later read differs by more than 100 MW (passes where the table is); the words (fail on main).
- **The fix on the branch.** The hover adds "EIA goes on revising its newest hours for some weeks, the Lower 48's total most, so the newest month of the year so far can move at the next build (this copy was built 2026-11-06)." Drawn and read (`b7_draw_default.txt`).

### 7. One base year

- **Where.** `warehouse/derived/demand_growth.py` `BASE = 2019` (it reads hours from 2018 for the screen's median and writes nothing of 2018); `DEMAND_DECISIONS` key `base-2019` ("the last whole year before the pandemic in the file", true).
- **Why it matters.** A growth against one year carries that year's weather and that year's faults: CAISO's 2019 holds EIA's low early months (the register's `eia930_ciso_demand_low_early_2019`). A forecaster measures against a weather-normal base or a trend, never one year. The page offers one base and no second.
- **How much.** `restate.py --base 2018` on the same workbooks (2018 whole in all eight areas: 8,712 to 8,760 hours used): 2025's average on 2018 against on 2019: ERCOT +29.54 and +27.22; SPP +9.62 and +11.14; Lower 48 +6.04 and +7.03; PJM +2.66 and +5.37; CAISO -0.74 and +4.45; MISO -0.63 and +2.20; NYISO -5.92 and -2.73; ISO-NE -6.51 and -2.54. The ranking's order of the seven is unchanged at the top (ERCOT, SPP, PJM) and CAISO and MISO change sign.
- **The test.** `tests/test_audit_demand_8.py`: 2018 is whole for CAISO and MISO in EIA's file (January to June from EIA's six-month file `eia930_all_history`, the rest from the workbook's extract) and their 2025 averages are below it (passes on main where both are held).
- **For the owner.** A base of 2018 and 2019 together, or a stated second base beside 2019, moves every growth figure on the page (CAISO's 2025 to about +1.8 on the mean of the two, by the figures above). Default: left as it is.

## The branches

Each from `origin/main`, pushed; tests run: the branch's own test and every test file that reads the changed file (30 files for branches 1, 3, 4, 7; 5 for branch 5), all passing.

| Branch | Head | Kind | Files | Test | Drawn and read |
|---|---|---|---|---|---|
| `wip/audit-demand-1` | `46961e819` | words, for landing | `site/app/demand/page.tsx`, `site/lib/decisions.ts`, `docs/methods/demand_growth.md` | `tests/test_audit_demand_1.py` | pass |
| `wip/audit-demand-2` | `0e73619e0` | figure, not for landing | test only | `tests/test_audit_demand_2.py` | not drawn (no words) |
| `wip/audit-demand-3` | `bfc8a1794` | words, for landing | `site/app/demand/page.tsx`, `docs/methods/demand_growth.md` | `tests/test_audit_demand_3.py` | pass |
| `wip/audit-demand-4` | `9e525313e` | words, for landing | `site/app/demand/page.tsx`, `docs/methods/demand_growth.md` | `tests/test_audit_demand_4.py` | pass |
| `wip/audit-demand-5` | `1afa22d8c` | words, for landing | `site/app/consumption/view.tsx`, `docs/methods/consumption.md` | `tests/test_audit_demand_5.py` | pass |
| `wip/audit-demand-6` | `154e59e09` | figure, not for landing | test only | `tests/test_audit_demand_6.py` | not drawn (no words) |
| `wip/audit-demand-7` | `9e3583db1` | words, for landing | `site/app/demand/page.tsx` | `tests/test_audit_demand_7.py` | pass |
| `wip/audit-demand-8` | `607923413` | figure, not for landing | test only | `tests/test_audit_demand_8.py` | not drawn (no words) |

Branches 1, 3, 4 and 7 change different lines of `site/app/demand/page.tsx` (124, 86, 109, 92) and 1, 3 and 4 different places of `docs/methods/demand_growth.md`; trial-merged together onto `origin/main` (`ea02c6820`) they merge without a conflict, their tests and the page's pass (58 passed), and the default view draws the same 91 figures.

## Data requests (rows for the data machine)

1. **Where in ERCOT the growth sits.** From EIA-930's ERCO workbook (its eight "Subregion" columns: COAS, EAST, FWES, NRTH, NCEN, SOUT, SCEN, WEST) or `eia930_subba_demand_hourly`: each zone's average demand of 2019 and 2025 and its growth, with the screen and the 95 percent rule of `docs/methods/demand_growth.md`, and the zones' sum against ERCOT's own. To say which part of ERCOT's +27.22 percent is west Texas.
2. **The size of EIA's revisions to retail sales.** From the archive's earlier vintages of `eia_retail_sales_monthly` (`warehouse/archive`): for each state and sector, the twelve-month total of September 2024 to August 2025 as first held and as held now, and the same for each month of 2025, to size how far the consumption view's "Change" moves after it is printed.

## What was checked and found right

- The screen, the 95 and 90 percent rules, local years, months and hours, California's late hours and the emptied hour, the year so far over the same months, growth from the rounded means, peaks' first hour: every value of the whole years restated equal.
- The ranking: largest first, the Lower 48 unnumbered and last of none, a missing measure last.
- The peaks' local hours ("18 August 2025, 17:00"), the hover of "On the year before" (+5.21 for the All grids tab, from the same file).
- The consumption view's twelve months against twelve, the 1 TWh floor, "no data" when a month is missing.
- The range test of session 118 removes no hour in any area here, as the note says.

## Not covered, or left open

- The fourth view (the whole country) and its forecast section were not re-done; their replication met 449,440 of 449,440 on 19 November.
- The weather view's fit was not rebuilt; only its file's figures were read beside the first view's.
- The Ask panel was not run (it calls a model).
- The note's replication section of session 7014 says a neighbour is "the nearest hours held and above zero"; the code drops a blank neighbour and takes no further hour (the later section "The rule in full" says so correctly). Not fixed here.
- The restatement used the workbooks of 3 October 2026; the page's file was built from those of 5 November. The year so far's October is the one place the difference shows.
