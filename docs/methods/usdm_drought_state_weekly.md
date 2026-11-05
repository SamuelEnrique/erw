# Percent of each state's area in drought, a week (the U.S. Drought Monitor's state statistics)

Energy Research Warehouse (ERW), method note written in session 2066 (chain 066) for a table first written on 23 October 2026 (session 2058).

Tables: `usdm_drought_state_weekly`

## Publisher and address

The U.S. Drought Monitor, produced by the National Drought Mitigation Center at the University of Nebraska-Lincoln, the U.S. Department of Agriculture and the National Oceanic and Atmospheric Administration; its data services (`https://droughtmonitor.unl.edu/DmData/DataDownload/WebServiceInfo.aspx`), the state statistics by percent of area in the traditional form: `https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=<the 48 contiguous states' FIPS codes, joined by %2C>&startdate=1/1/<first year>&enddate=12/31/<last year>&statisticsType=1`, asked as CSV, the current year's span ending on the day of the run. Source id `usdm:state_statistics`. Connector: `warehouse/connectors/usdm_drought.py` (session 2058). droughtmonitor.unl.edu's robots file (read 218) disallows `/data/`, `/nadmdata/`, `/webfiles/` and `/DmData/DataArchive.aspx`, none asked; usdmdataservices.unl.edu has none (read 219, HTTP 404).

## Vintage and revision

The maps of 30 December 2014 to 20 October 2026, from three answers: 2015 to 2018 retrieved 23 October 2026 20:06:26 UTC, 2019 to 2022 at 20:06:43 and 2023 to 23 October 2026 at 20:06:50, written by run `20261023T201905Z` from the saved answers (`--offline`). The service sends no Last-Modified, so `vintage` is empty in every row.

Spans are four years from the start year (2015 by default): 2015 to 2018, 2019 to 2022 and 2023 to 2026, so three requests. A span that ends before the current year is read from its saved answer once a run has saved it, so a revision the Monitor makes to an earlier span is taken only when the saved copy is gone; the current year's span is asked again on every run that is not `--offline`. Its address carries the day of the run, so `--offline` finds it only on the day it was saved. The table is written whole each time (a snapshot).

## Shape and variables

Series, 177,696 rows: 48 states (the contiguous states; not AK, HI or PR), 617 weeks, 6 variables. `entity` `usdm:<ST>`; `node` the state's abbreviation; `geo` `US-<ST>`; `unit` pct, two decimals as the Monitor gives them; `freq` P1W; `ts_utc` the map date at 00:00:00Z, a Tuesday in all 617 weeks, each 7 days after the last, none missing; `market` empty. `x_valid_start` the map date, and `x_valid_end` six days after it, in every row.

| Variable | The area, percent of the state |
|---|---|
| none | in none of the categories |
| d0 | abnormally dry or worse |
| d1 | moderate drought or worse |
| d2 | severe drought or worse |
| d3 | extreme drought or worse |
| d4 | exceptional drought |

The categories are cumulative (the traditional form): d1 holds d2, d3 and d4, so a category's own area is the difference of two rows, and none plus d0 is the whole state.

## Reading the service

- Each answer must hold the columns MapDate, StateAbbreviation, None, D0 to D4, ValidStart and ValidEnd, and its states must be exactly the 48 asked, none missing and none extra; otherwise the run stops.
- A map date that does not read as YYYYMMDD, or a figure that is not a number, stops the run.
- Every figure must lie between 0 and 100, none plus D0 must be 100 within 0.02, and D0, D1, D2, D3 and D4 must never rise from one to the next; otherwise the run stops.
- A span's start date can return the map of the week before it, whose valid week holds 1 January. A state, variable and map date given by two spans is kept once if the two agree and stops the run if they differ. In this table the 2023 span gave the map of 27 December 2022, which the 2019 span gives too: 288 rows, kept once. The 2015 span gave the map of 30 December 2014, which no other span gives, and it is kept.
- The rows are dicts, not tuples: a column named None would be renamed. Nothing is filled.
- Ceiling: one request a span (three for 2015 to 2026), each tried up to four times, with 2 seconds after each answer.

## License

Not settled. The table's header said "License: public, with the Monitor's credit" when first written; session 2066 corrected it to "not settled" and wrote the table again. It carries the credit ("The U.S. Drought Monitor is jointly produced by the National Drought Mitigation Center at the University of Nebraska-Lincoln, the United States Department of Agriculture, and the National Oceanic and Atmospheric Administration. Map courtesy of NDMC."), but `license_verdicts.csv` gives the Monitor no verdict: session 2061 read its home page and About the Data page (reads 220 and 221), which state no terms, and left its Permission page (`/About/Permission.aspx`) to chain 068's licenses round (session 2089). `license_tables.csv` maps the table to the U.S. Drought Monitor through the source registry; until a verdict, `docs/licenses.md` holds it as not settled.

## Cross-checks (session 2066)

- Session 2058, each western state's yearly mean of d1 against its yearly conventional hydroelectric generation (`eia_state_generation_monthly`), 2015 to 2025: correlation -0.83 for California, -0.35 for Washington, -0.22 for Oregon. Session 2066 computed the same yearly means from the rows: California 99.6 percent in 2022, 5.7 in 2024 and 14.4 in 2017; Washington 64.0 in 2015 and 4.4 in 2016; Oregon 91.6 in 2015 and 3.8 in 2017.
- The counts above were computed from the rows, read past the header lines. The three answers held 10,032, 10,032 and 9,600 state-weeks; less the 48 given twice, 29,616 = 48 states times 617 weeks, and times 6 variables 177,696 rows, the header's count.
- None plus d0 is 100 exactly (to the second decimal) in all 29,616 state-weeks, and d0 to d4 never rise in any.
- The widest week: 32 of the 48 states with more than half their area in moderate drought or worse on 19 May 2026; none on 12 March 2019. On 20 October 2026 Maine had 100 percent at d1, and 13 states some area at d4.

## What it does not hold

- Alaska, Hawaii, Puerto Rico, counties, climate divisions and the nation's total.
- The categorical statistics (each category's own area) and areas in square miles or population: percent of area, cumulative, only.
- Maps before 30 December 2014.
- The service's StatisticFormatID column.
