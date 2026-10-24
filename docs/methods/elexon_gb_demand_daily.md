# Great Britain's national demand a day (Elexon BMRS, Initial National Demand Outturn per day)

Energy Research Warehouse (ERW), method note written in session 2171 (chain 094) for a table first written on 24 October 2026 (session 2162, `archive/sessions/SESSION_2162_REPORT.md`).

Tables: `elexon_gb_demand_daily`

## Publisher and address

Elexon Limited, Balancing Mechanism Reporting Service (BMRS, `https://bmrs.elexon.co.uk/`), Insights API, endpoint demand/outturn/daily (INDOD), no key: `https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/daily?settlementDateFrom=<from>&settlementDateTo=<to>&format=csv`, one request a window of at most two years (the endpoint's limit is 731 days). Source id `elexon:indod`. Answers saved under `warehouse/raw/elexon_demand/`.

Connector: `warehouse/connectors/elexon_demand.py` (session 2162): `[--end YYYY-MM-DD] [--offline] [--out-dir DIR]`, four windows (2020 to 2021, 2022 to 2023, 2024 to 2025, 2026 to the day before `--end`). **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T002105Z`; the four windows retrieved from 2026-10-24T00:17:29Z to 00:17:31Z. `vintage` is empty; `x_publish_time` holds Elexon's publication time of each day's figure: 23:15 UTC on the day itself in British summer time (1,180 days) and 00:15 UTC the next day in winter (752 days), that is 00:15 on the following day by Britain's clock. A later run merges by (entity, variable, ts_utc).

## Shape and variables

Series, 1,932 rows, one a settlement day: entity `elexon:GB`, variable `indo_daily`, unit MWh, freq P1D, geo GB, node "Great Britain", `x_settlement_date` the day as Elexon gives it. INDO, the API's description: "the total demand volume for the previous day expressed on an initial National Demand outturn (INDO) basis, i.e. excluding station transformer, pumping and interconnector export demand ... summing the half hourly INDO demands (divided by two to convert to MWh)". Embedded generation that the transmission system does not see is not in it.

| Year | Days | TWh |
|---|---|---|
| 2021 (from 27 April) | 178 | 118.1 |
| 2022 | 362 | 231.2 |
| 2023 | 365 | 227.9 |
| 2024 | 366 | 230.6 |
| 2025 | 365 | 228.8 |
| 2026 (to 23 October) | 296 | 179.2 |

Lowest day 395,760 MWh (2025-05-25); highest 909,318 MWh (2025-01-10).

## Placing values in time

`ts_utc` is the settlement day at 00:00:00Z (Decision 11, as EIA-930's daily tables write a day), equal to `x_settlement_date` in every row; the settlement day is Great Britain's own (Europe/London), which begins at 23:00Z the day before in summer time.

## What is and is not filled

A day Elexon gives no figure for has no row; nothing is filled. The endpoint's daily series begins on 27 April 2021 (the window asked from 1 January 2020 answers from then). Prices are not taken.

## License

Header: "License: public. Contains BMRS data (c) Elexon Limited copyright and database right 2026" (the header prints the copyright sign), with the licence's address `https://www.elexon.co.uk/bsc/data/balancing-mechanism-reporting-agent/copyright-licence-bmrs-data/`. The session report records the licence (read 306) as a new verdict, may be public.

## Checks (session 2171)

The figures in this note were computed from the rows of `warehouse/output/elexon_gb_demand_daily.csv`, read past its 10 header lines (scripts in `runs/c094/s2171/`).

- 1,932 rows, `ts_utc` from 2021-04-27T00:00:00Z to 2026-10-23T00:00:00Z, as the header states. No day twice.
- 74 days between the first and the last have no row, as the header says: 57 in May and June 2021 (all of May; June but the 14th and 15th, and the 29th and 30th), 14 other days of 2021, and 3 in 2022 (9 July, 23 September, 30 December).
- Session 2162's cross-check (`runs/c094/s2162/cross.py`), run again: its output is identical to the saved `cross.out`.
  - INDO a year against Ember's UK demand (`owid_ember_electricity_annual`, GBR): 2023 227.9 against 315.8 TWh (0.722), 2024 230.6 against 317.4 (0.727), 2025 228.8 against 321.4 (0.712).
  - The month's mean daily demand over the year's, 2021 to 2025: Great Britain January 1.21, June 0.85, December 1.15; its largest day fell in January (2 years), December (2) and November (1). ERCOT: August 1.24, largest day in February (2 years), December, January and August (1 each). PJM: July 1.18, largest day in June (2), July (2) and December (1).

## Where the description and the data disagree

1. **`geo` GB for Great Britain.** The header and node say Great Britain, and INDO excludes Northern Ireland; ISO 3166-1's GB is the United Kingdom, and `desnz_uk_electricity_quarterly` uses `geo` GB for the whole United Kingdom. The same code names two areas in the warehouse.

## The session report against the table

Every figure of `SESSION_2162_REPORT.md` checked against the table and the rerun cross-check holds (1,932 days, 27 April 2021 to 23 October 2026, 74 days without a figure, "most of May and June 2021 and 17 days to the end of 2022", 227.9 to 230.6 TWh in 2023 to 2025, 0.712 to 0.727 of Ember's, January 1.21 and June 0.85, the largest day in November to January every year 2021 to 2025, ERCOT's August 1.24 and PJM's July 1.18, four request windows), except:

- "ERCOT's largest day fell in a winter month in three of the five years": the rerun cross-check gives February twice, December once, January once and August once, a winter month in four of the five years.

Acted on in session 2171: the docstring now says `geo` GB is ISO 3166's code for the United Kingdom, the nearest the standard has, while the figure covers Great Britain only; session 2162's report is corrected (ERCOT's largest day in a winter month in four of five years, not three).

## What it does not hold

- Half-hourly demand, embedded generation, Northern Ireland, any day before 27 April 2021 and the 74 days above, and prices.
