# Italy's public net electricity production by type, load and cross-border trading, an hour from 2020 to 2025 and a quarter hour in 2026 (Energy-Charts.info, Fraunhofer ISE, API public_power)

Energy Research Warehouse (ERW), method note written in session 2289 (chain 104) for a table first written on 24 October 2026 (session 2281 of chain 104, its report `archive/sessions/SESSION_2281_REPORT.md`).

Tables: `energy_charts_italy_power`

## Publisher and address

Energy-Charts.info, run by the Fraunhofer Institute for Solar Energy Systems ISE, its API's public net production for Italy, one request a calendar year of Italian local days:

`https://api.energy-charts.info/public_power?country=it&start=<year>-01-01&end=<year>-12-31` (2020 to 2025), and `...&start=2026-01-01&end=2026-10-22`.

Source id `energy_charts:public_power_it`. The API's description (`https://api.energy-charts.info/openapi.json`, version 2.0, read 471, saved as `runs/license_reads/s2281/05_...bin`) says the endpoint "Returns the public net electricity production in Megawatt (MW) for a given country for each production type", that a day given as a date "is assumed to be at 00:00 on the specified date in the local timezone of the specified country", that "All timestamps returned by the API mark the beginning of the period the value refers to", and that requests are limited to "2 requests per minute with a burst of 4". Each answer is JSON: `unix_seconds`, `production_types` (a name and a list of values, a null where there is none) and `deprecated` (false in all seven). The description names no upstream publisher for Italy's figures.

Terna, Italy's transmission operator, was read first and not taken: its robots file (read 467) disallows `/Portals/` and other site paths; its legal notice (read 469) says "The reproduction of documents published on these websites is authorised exclusively for personal and non-commercial use, provided that the source is cited correctly." Session 2281's probe (`runs/c104/s2281/probe.csv`) made 12 requests: Terna's robots file, home page and legal notice (reads 467 to 469), Energy-Charts' robots file (HTTP 404, read 470) and description (read 471), and the seven years (HTTP 200, 1,147,262 to 4,019,014 bytes, 04:58:12Z to 05:01:39Z, 34 or 35 seconds apart). All twelve are saved in `runs/license_reads/s2281/`; the seven answers were seeded into `warehouse/raw/energy_charts_italy/20261024T045655Z_probe/`, and the trial and the write read them offline.

Connector: `warehouse/connectors/energy_charts_italy.py` (session 2281): `[--first 2020] [--last 2026] [--end 2026-10-22] [--offline] [--out-dir DIR]`, one request a year, 31 seconds between them. Every production type is taken, its name in snake case, except the three the API derives (residual load, the renewable shares of load and of generation). An answer without `unix_seconds` and `production_types`, intervals not evenly spaced (or neither an hour nor a quarter hour), a type whose values do not match the intervals, a value that is not a number or an interval given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `warehouse/supabase/live_set.yaml` lists it under `catalogue_hold`.

## Vintage and revision

One write, run `20261024T050358Z` ("This run wrote 1329375 rows: 1329375 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the seven saved answers. `retrieved_at` is each answer's download time (2020 at 2026-10-24T04:58:12Z, 2021 04:58:47Z, 2022 04:59:21Z, 2023 04:59:55Z, 2024 05:00:30Z, 2025 05:01:04Z, 2026 05:01:39Z), as header line 4 lists them; `vintage` is blank in every row (the answers carry no Last-Modified).

The API marks no value as provisional or final; whether Energy-Charts revises a figure after it is first served, the answers do not say. A later run merges by (entity, variable, ts_utc): a changed value replaces the old one, but an interval the API later gives as null writes no row, so the earlier value would be kept.

## Shape and variables

Series, 1,329,375 rows, one entity `energy_charts:IT`, `node` Italy, `geo` IT, `unit` MW, `market` blank. `freq` is each answer's own interval: PT1H for the 52,608 hours from 2019-12-31T23:00:00Z to 2025-12-31T22:00:00Z, PT15M for the 28,316 quarter hours from 2025-12-31T23:00:00Z to 2026-10-22T21:45:00Z (80,924 intervals in all). Twenty variables, nineteen of the API's types and load:

| Variable | Rows | First ts_utc | Last ts_utc | Mean | Lowest | Highest | Zeros |
|---|---|---|---|---|---|---|---|
| load | 80,924 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 32,264.3 | 15,334 (2020-04-13T02:00Z) | 52,503 (2023-07-19T14:00Z) | 0 |
| fossil_gas | 80,924 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 12,147.6 | 1,002 (2026-06-14T08:45Z) | 31,198 (2024-12-12T16:00Z) | 0 |
| cross_border_electricity_trading | 80,924 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 5,502.5 | -4,779 (2026-01-06T07:00Z) | 11,188.5 (2024-01-29T11:00Z) | 22 |
| solar | 80,922 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 3,488.7 | 0 | 26,085 (2024-07-05T11:00Z) | 34,913 |
| hydro_run_of_river | 80,924 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 3,251.4 | 787 (2022-03-13T03:00Z) | 9,768 (2024-07-05T18:00Z) | 0 |
| wind_onshore | 80,913 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 2,444.7 | 40 (2026-09-08T07:30Z) | 9,107 (2026-02-06T09:45Z) | 0 |
| others | 80,924 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 1,865.3 | 193 (2024-12-20T02:00Z) | 3,914 (2024-07-04T14:00Z) | 0 |
| fossil_hard_coal | 78,575 | 2019-12-31T23:00Z | 2026-10-20T12:00Z | 925.9 | 0 | 4,053 (2023-01-26T06:00Z) | 206 |
| geothermal | 70,185 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 607.2 | 460 (2025-10-06T11:00Z) | 687 (2020-02-06T23:00Z) | 0 |
| biomass | 80,924 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 580.2 | 151 (2023-12-09T20:00Z) | 855 (2025-12-14T00:00Z) | 0 |
| hydro_water_reservoir | 80,900 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 529.9 | 4 (2022-03-26T11:00Z) | 2,131 (2020-06-22T17:00Z) | 0 |
| fossil_coal_derived_gas | 78,182 | 2019-12-31T23:00Z | 2026-09-25T07:30Z | 523.1 | 0 | 1,135 (2020-09-23T19:00Z) | 1 |
| hydro_pumped_storage | 62,671 | 2019-12-31T23:00Z | 2026-10-22T19:00Z | 459.2 | 0 | 4,786 (2022-07-21T17:00Z) | 13,154 |
| battery | 20,354 | 2024-12-31T23:00Z | 2026-10-22T21:15Z | 374.4 | 0 | 1,662 (2026-04-20T18:15Z) | 6,989 |
| fossil_oil | 79,691 | 2019-12-31T23:00Z | 2026-10-22T21:45Z | 130.0 | 0 | 3,358 (2024-11-02T00:00Z) | 328 |
| other_renewables | 4,060 | 2024-12-31T23:00Z | 2025-07-08T23:00Z | 108.6 | 0 | 1,114 (2025-06-28T19:00Z) | 1,608 |
| waste | 64,597 | 2019-12-31T23:00Z | 2026-05-06T14:00Z | 93.1 | 0 | 409 (2024-01-13T21:00Z) | 2,441 |
| wind_offshore | 59,757 | 2022-05-31T22:00Z | 2026-10-22T21:45Z | 5.6 | 0 | 30 (2022-07-17T12:00Z) | 22,261 |
| battery_consumption | 20,353 | 2024-12-31T23:00Z | 2026-10-22T21:15Z | -259.5 | -1,623 (2026-04-27T11:15Z) | 0 | 11,906 |
| hydro_pumped_storage_consumption | 62,671 | 2019-12-31T23:00Z | 2026-10-22T19:00Z | -247.0 | -4,210 (2026-04-05T12:00Z) | 0 | 25,015 |

MW; means rounded to one decimal; where a lowest or highest value recurs, its first interval is given. Every value is written with one decimal; all are whole MW but 37,512 of the trading's.

- **Signs.** The two consumptions are 0 or negative in every row; the trading is positive (a net import) in 78,931 intervals, negative in 1,971 and 0 in 22. Every other type is 0 or positive.
- **The types change from year to year.** The answers hold 19 types (with the three derived) in 2020 and 2021, 20 in 2022 to 2024, 23 in 2025 and 22 in 2026: wind offshore from the 2022 answer, the batteries and "Other renewables" from the 2025 answer, "Other renewables" absent again in 2026.
- **Long gaps and a level change** (counted from the answers' nulls and the rows by month, `runs/c104/s2289/ec_italy.out` and `ec_italy_gaps.out`):
  - geothermal: 769 null hours in 2024 (from November), 6,514 of 8,760 in 2025 (no row at all in February, March, April or August 2025), 3,456 of 28,316 quarter hours in 2026; its UTC year's energy falls from 4.801 TWh in 2024 to 1.328 in 2025;
  - pumped storage and its consumption: 1,765 null hours in 2025, 16,488 of 28,316 quarter hours in 2026; the batteries 1,485 null hours in 2025 and 15,237 (battery) and 15,238 (battery consumption) quarter hours in 2026;
  - waste: 16,255 null quarter hours in 2026 (its last row 2026-05-06T14:00Z), and its level changes between answers: a monthly mean of 33.6 to 39.4 MW in January to March 2023, 286.6 to 362.5 MW from April 2023 to December 2024, 2.4 to 7.6 MW from January 2025 (0.295 TWh in 2020, 2.836 in 2024, 0.044 in 2025);
  - fossil hard coal 2,349 and coal-derived gas 2,742 null quarter hours in 2026; oil 721 null hours in 2024; wind offshore 3,623 null hours in 2022 (before its first row); the reservoirs 24 null hours in 2021; solar 2 null quarter hours in 2026.
- A UTC year's energy (MW times each interval's hours, TWh), 2020 and 2025: load 273.198 and 277.248; fossil gas 109.107 and 101.777; trading 34.054 and 48.958; run-of-river 37.255 and 25.424; solar 20.404 and 33.945; wind onshore 18.588 and 21.194; others 18.161 and 15.068; coal 12.350 and 3.177.

## Placing values in time, and what is filled

`ts_utc` is the interval's start in UTC, from the answer's `unix_seconds`; the API says its timestamps mark the beginning of the period. Each year was asked as Italian local days, so a year's first interval is 23:00Z on 31 December. The hourly and quarter-hourly spans are complete: 52,608 hours (2020 and 2024 of 8,784, the others of 8,760) and 28,316 quarter hours (295 local days of 96, less the 4 of the spring change), evenly spaced in each answer, so the changes of hour leave no gap in UTC. A null has no row; nothing is filled. A value is the API's MW for the interval; whether it is a mean over the interval or a reading at its start, the description does not say.

## License

Header: "License: public, CC BY 4.0 (the API's description). Source: Energy-Charts.info. The values are reshaped from wide to long; none is changed." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 442 (the API's description, read by chain 102's session 2253; session 2281's read of the same page is read 471, and its own verdict row was dropped when chain 102 landed first, commit ef284545), "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license. Proper attribution to Energy-Charts.info as the source is required.", verdict "may be public", if the ERW sells anything "may be public". The table's row: flag public, "agrees", ERW verdict public. Terna's own verdict (read 469) is "needs written permission" in both columns; session 2282's report asks Samuel whether Energy-Charts' CC BY should govern figures that operators publish under narrower terms.

## Checks (session 2289)

The figures in this note were computed from the rows of `warehouse/output/energy_charts_italy_power.csv`, read past its 10 header lines (counted), and from the saved answers, read only (scripts `runs/c104/s2289/ec.py` and `ec_gaps.py`, outputs `ec_italy.out` and `ec_italy_gaps.out` beside them).

- 1,329,375 rows, 20 variables, `ts_utc` from 2019-12-31T23:00:00Z to 2026-10-22T21:45:00Z, the interval counts and spans of header line 3 (PT15M 28,316, PT1H 52,608); one entity; no (entity, variable, ts_utc) twice; no blank value; unit MW, geo IT throughout; `source_url` and `retrieved_at` the year's answer.
- **Against the answers:** the seven answers hold 1,329,375 values that are not null, outside the three derived types, and each type's values in each answer equal the table's rows for those intervals (0 types differ).
- **The trial against the table:** `runs/c104/s2281/trial/energy_charts_italy_power.csv` (run `20261024T050309Z`) has the same rows past its header, byte for byte; the headers differ only in the run's name and log.
- Session 2281's cross-check (`runs/c104/s2281/cross.py`), run again from the main checkout with the written table as argument 1 (output `runs/c104/s2289/italy_cross.out`): identical to the saved `cross.out`, which was run on the trial. Load against Ember's Italian demand (`owid_ember_electricity_annual`), UTC years: 0.884 (2020), 0.881, 0.886, 0.883, 0.876 and 0.890 (2025: 277.248 against 311.60 TWh); production, storage and trading less load over 80,924 intervals: median 169 MW, 5th percentile -2,080, 95th 1,020, a median 0.54 percent of load; solar 20.4 TWh in 2020 to 33.9 in 2025. The sum counts only the types present in each interval, so the gaps above enter it.

## Where the description and the data disagree

1. **Not twenty production types and load, and one type left out of the report's list.** The report counts "Twenty production types and load"; the table holds twenty variables, load among them, so nineteen types and load. Its list omits `other_renewables`, which has 4,060 rows from 2024-12-31T23:00:00Z to 2025-07-08T23:00:00Z (the docstring names it).
2. **A type's series is not continuous across the years.** The header describes "Italy's public net electricity production by type" with "A null has no row; nothing is filled". Both hold, but for several types the rows are far from complete or change level from one answer to the next: geothermal holds 2,246 of 8,760 hours in 2025; pumped storage 6,995 hours of 2025 and 11,828 of 28,316 quarter hours of 2026; waste falls from monthly means near 300 MW (April 2023 to December 2024) to under 8 MW from January 2025 and has no row after 2026-05-06. A year's sum of these types is not Italy's production of them, and nothing in the header says so.
3. **The year requests were not 31 seconds apart.** The report says they were; the probe's times give 35, 34, 34, 35, 34 and 35 seconds (the 31 seconds the connector waits, plus each request's time).
4. **The reads' numbers in the report's file list.** The report's text gives reads 467 to 471, its file list "`warehouse/metadata/license_reads.csv` (436 to 440)" and "`license_verdicts.csv` (Terna, Energy-Charts)". Since the merge of chain 102 (commit ef284545) the reads are 467 to 471 and the Energy-Charts verdict row is chain 102's (read 442, recorded in session 2257); this chain's row was dropped.

Compared besides, with no contradiction found: the header's and docstring's counts, spans, frequencies, entity, unit, variables (against the docstring's list), the derived series left out, the signs, and "nothing is filled" against the rows and the answers.

Not acted on: this note changes no file but itself.

Recorded, not changed in session 2289: the series' gaps and level changes are Energy-Charts' as published. Session 2289's report corrects session 2281's "twenty" types (19 and load), its 31 seconds (34 to 35) and its read numbers.

## The session report against the table

Every figure of `SESSION_2281_REPORT.md` checked against the table, the saved answers and the rerun cross-check holds (2020 to 22 October 2026, 1,329,375 rows, MW from the API's description, hourly to 2025 and quarter-hourly in 2026, residual load and the renewable shares not taken, 0.876 to 0.890 of Ember's demand, 277.248 against 311.60 TWh in 2025, a median 169 MW or 0.54 percent of load, solar 20.4 TWh in 2020 and 33.9 in 2025, 12 requests of 15, no robots file at api.energy-charts.info, 2 requests a minute), except:

- "Twenty production types and load": nineteen and load, and `other_renewables` not in the list (disagreement 1).
- "the year requests were 31 seconds apart": 34 or 35 seconds (disagreement 3).
- Files: "`license_reads.csv` (436 to 440)" and the Energy-Charts verdict row: renumbered and replaced at the merge (disagreement 4).

## What it does not hold

- The API's derived series (residual load, the renewable shares), Italy's bidding zones, prices, installed power and forecasts, which the API offers on other endpoints; Terna's own publications; anything before 2020 or after 22 October 2026; self-consumption and what Energy-Charts does not count as public net production; and the intervals and types the answers give as null.
