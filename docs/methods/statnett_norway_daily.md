# Statnett's daily production and consumption for all of Norway, 1 January 2020 to the day before the run

Energy Research Warehouse (ERW), method note written in session 2353 (chain 105) for a table first written on 24 October 2026 (session 2350, `archive/sessions/SESSION_2350_REPORT.md`, "Norway's production and consumption a day (Statnett), a source of the session's own choosing"; commit `bc35f676`, whose message still says "Session 2300": the chain's sessions 2300 to 2306 were renumbered 2350 to 2356 by commit `0ca0c408` the same morning). Statistics Norway's monthly balance, the table this one is checked against, is `ssb_norway_electricity_monthly` (`docs/methods/ssb_norway_electricity_monthly.md`).

Tables: `statnett_norway_daily`

## Publisher and address

Statnett SF, Norway's transmission system operator, "Data from the power system", the Production and Consumption chart `https://driftsdata.statnett.no/Web/ProductionConsumption?language=en`. The table comes from the REST address behind the chart, one GET, `https://driftsdata.statnett.no/restapi/ProductionConsumption/GetData?From=2020-01-01`, which answers JSON with the keys `StartPointUTC`, `EndPointUTC`, `PeriodTickMs`, `Production`, `Consumption`, `ProductionConsumptionSidebarViewModel` and `MetaData` (null). Source id `statnett:driftsdata_production_consumption`; `sources.csv`: publisher Statnett SF, report "Data from the power system, Production and Consumption", document list `https://www.statnett.no/en/for-stakeholders-in-the-power-industry/data-from-the-power-system/`, license internal, first and last seen 2026-10-24. Statnett's Norwegian page "Last ned grunndata" offers base data from the power system "til Excel", by data type and year; the ERW does not use it.

The answer: 45,130 bytes, sha256 `273153e4...`, HTTP 200, `application/json`, no `Last-Modified`, fetched at 2026-10-24T06:29:35Z by session 2350's probe (`runs/c105/s2300/probe.py`, row 5 of `probe.csv`). It is saved at `warehouse/raw/statnett_norway/20261024T062857Z_probe/probe_05_no_restapi_productionconsumption_getdata_from_2020_01_01.bin`, and the same bytes at `runs/license_reads/s2300/05_...bin`. The connector's two writes, runs `20261024T063238Z` and `20261024T064329Z`, read that file offline ("raw file reused", their run logs in `warehouse/output/logs/`); their own raw folders hold only the data lock's check, and `20261024T063156Z` (the trial) holds an empty manifest.

Connector: `warehouse/connectors/statnett_norway.py` (session 2350), `--offline` and `--out-dir`. It asks `iso_prices.paused` and `iso_prices.paused_host("driftsdata.statnett.no")` before anything else; neither names Statnett. It stops if the step is not 86,400,000 ms, if the two arrays differ in length, or if the slots, once placed, do not end on Norway's day of `EndPointUTC` (below). The day in progress is not written. The file is a snapshot (`iso_prices.write_snapshot`): each run replaces it, nothing merges. Ceiling: one request.

Schedule: none. No line of `warehouse/run_daily.sh`, `run_data_machine.sh`, `run_data_machine_tables.sh` or `run_monthly.sh`, no workflow and no step of `warehouse/scheduled.py` names the connector, so the table holds Norway's days to 23 October 2026 until a person runs it again.

`run_status.csv`: no row (the run wrote `runs/status/statnett_norway.json`, run `20261024T064329Z`, "ok", "4960 rows"; disagreement 3). `archive_manifest.csv`: 4,960 rows, run `20261024T064334Z-local`, data hash `d681f76d...`, which equals the hash of the file on this machine. `redivis_uploads.csv`: no row. Live set: in `catalogue_hold` of `warehouse/supabase/live_set.yaml` (not loaded, not in the live catalogue). Readers: none; `build_coverage.py` gives it the sector `power`, and `tests/test_session2350.py` tests the placement (4 tests).

## Vintage and revision

One retrieval: every row's `retrieved_at` is 2026-10-24T06:29:35Z. The header's "Retrieved: 20261024T064329Z" is the second write, made offline at 06:43 UTC so that the header names session 2350; the first, at 06:32:38Z, held the same rows (header line 10, "the previous file held 4960 rows"; the archive run found 0 rows changed). `vintage` is blank in every row: the answer carries no publication time and no `Last-Modified`. Whether Statnett revises a day after publishing it is not known; one retrieval cannot show it.

The answer's own summary, `ProductionConsumptionSidebarViewModel`, counts the day in progress: production mean 416,808.65 and lowest 82,734 MWh (that partial day), against the table's mean of 416,943 over whole days.

## Shape and variables

Series, 4,960 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 10 header lines. One entity, `statnett:norway`; unit MWh as published; `freq` P1D; `geo` NO; `market`, `node` and `vintage` blank; one `source_url`, the address above. Every value is a whole number, none blank, none zero or negative.

| Variable | Days | Mean | Median | Lowest (day) | Highest (day) |
|---|---|---|---|---|---|
| `consumption` | 2,480 | 370,975 | 360,454 | 255,677 (2020-05-31) | 574,672 (2026-01-07) |
| `production` | 2,480 | 416,943 | 402,236 | 201,513 (2021-08-08) | 650,057 (2026-01-06) |

MWh a day. A year, TWh (days held):

| | 2020 (366) | 2021 (365) | 2022 (365) | 2023 (365) | 2024 (366) | 2025 (357) | 2026 to 23 October (296) |
|---|---|---|---|---|---|---|---|
| Production | 153.33 | 156.46 | 144.11 | 152.26 | 155.31 | 155.72 | 116.83 |
| Consumption | 132.86 | 138.92 | 131.57 | 134.49 | 136.83 | 133.29 | 112.06 |

Production exceeds consumption on 2,024 days and falls below it on 456; production less consumption is 20.48, 17.54, 12.54, 17.77, 18.48 and 22.42 TWh in 2020 to 2025 (2025 without its eight missing days) and 4.77 TWh in 2026 to 23 October.

## Placing values in time, and what is filled

Statnett's answer is two arrays and a clock: `StartPointUTC` 1577833200000 (Norway's midnight of 1 January 2020, 23:00Z), `EndPointUTC` 1792792800000 (Norway's midnight of 24 October 2026, 22:00Z), a step of 24 hours. Each array has 2,495 slots; from the first day to the end day there are 2,489 of Norway's days, six fewer. Fourteen slots are empty, in both arrays together:

- **Six, one each autumn,** slots 299, 671, 1036, 1401, 1766 and 2131, each right after a day the clocks went back: 2020-10-25, 2021-10-31, 2022-10-30, 2023-10-29, 2024-10-27 and 2025-10-26. The values go on after each.
- **Eight,** slots 2154 to 2161: 18 to 25 November 2025.

Skipping the six autumn slots puts the last slot on 2026-10-24, the end day (production 82,734 MWh and consumption 99,172 MWh, a part day: the answer was fetched at 08:29 Norway's time). Counting them as days would put it on 2026-10-30, six days after the end day. The table equals this placement on all 2,480 days before 2026-10-24.

An independent test of the placement is the week. Within each of the seven stretches between the autumn slots, Sunday has the lowest mean consumption of the seven weekdays. Over the 352 whole weeks, Sunday is the week's lowest day in 205; with every day moved one day earlier, in 4; one day later, in 131. A stretch placed a day off would make Saturday or Monday the low day.

`ts_utc` is Norway's day (Europe/Oslo) written at 00:00:00Z, a label (Decision 11), not the instant the day begins (22:00Z or 23:00Z of the day before); every row is at 00:00:00Z. Whether Statnett's figure for a clock-change day covers its 23 or 25 hours is not known. Against the Sundays a week either side, consumption on the spring change days is 0.904 to 1.003 and on the autumn days 0.937 to 1.029, where any Sunday's ratio runs from 0.937 (10th percentile) to 1.065 (90th), median 1.000; a 25-hour day would come out near 1.042 and a 23-hour day near 0.958, so the weather hides the hour.

Nothing is filled. The eight days of November 2025 have no row and are named in header line 3; no row of `run_status.csv` or `known_gaps.csv` names them. The day in progress is never written. The next autumn change, 25 October 2026, falls after the newest day held; a run after it will place the slot that follows it the same way.

## License

Header line 9: "License: internal until the licenses' round reads Statnett's terms. Source: Statnett." `coverage.csv` and `sources.csv`: internal. `license_tables.csv`: Statnett SF, "the source registry". `docs/licenses.md`, the table's row: Statnett SF, "not settled (needs written permission by default)", not read: Statnett SF, flag internal, "not settled", if the ERW sells anything "may be public" (disagreement 4), ERW verdict internal; and in its list, "not read: Statnett SF". No row in `license_verdicts.csv`, `license_reads.csv`, `license_status.csv` or `paused_sources.csv`.

The pages session 2350 read, saved in `runs/license_reads/s2300/`: `https://driftsdata.statnett.no/robots.txt` (HTTP 404, the server's "404 - File or directory not found" page), `https://www.statnett.no/robots.txt` (HTTP 404, a 64,835-byte page), the English page "Data from the power system" and the Norwegian page "Last ned grunndata" (HTTP 200). Their text, once tags and scripts are removed (9,799 and 4,192 characters), holds none of the words terms, license, copyright, vilkår, lisens, opphavsrett, NLOD, Creative Commons, privacy or personvern. The English page is the one that says: "Data may be missing in some places on this page, for example, data from wind power production that came into operation after 2019. This does not affect our operations."

## Checks (session 2353)

The figures in this note were computed by `runs/c105/s2353/check_statnett_norway_daily.py` (output `check_statnett_norway_daily.out` beside it) from the rows of `warehouse/output/statnett_norway_daily.csv` in the main checkout, read past its 10 header lines (counted, never parsed as comments), from the raw answer, and from `ssb_norway_electricity_monthly`. No request was made.

- 4,960 rows, 2020-01-01 to 2026-10-23, as header line 1 states; no (entity, variable, ts_utc) twice; rows in key order; no blank value; `coverage.csv` agrees (4,960 rows, the same range, validator pass, last run 2026-10-24T06:43:29Z).
- **Against the raw answer:** the placement above, done again from the arrays, gives the same 2,480 days and the same two values on each.
- **Against Statistics Norway** (`ssb_norway_electricity_monthly`, entity `ssb:norway`, MWh, months 1993-01 to 2026-09), each month's sum of the table's days, 81 months from 2020-01 to 2026-09:

| Statnett | Statistics Norway | Median, 81 months | Median, the 80 whole months | Mean, 80 whole months | Lowest whole month | Highest |
|---|---|---|---|---|---|---|
| production | `total_electricity_generation` | 0.9936 | 0.9937 | 0.9893 | 0.9613 (2023-07) | 1.0036 (2021-01) |
| consumption | `gross_electricity_consumption` | 0.9918 | 0.9922 | 0.9874 | 0.9508 (2023-07) | 1.0040 (2021-01) |
| consumption | `net_electricity_consumption` | 1.0532 | 1.0532 | 1.0523 | 1.0305 (2022-08) | 1.0737 (2020-01) |

  November 2025, with 22 of its 30 days, is 0.702 of total generation and 0.696 of gross consumption. Statnett's consumption sits between Statistics Norway's net and gross consumption, near gross.
- **The gap is a summer one.** Production against total generation, the median of each calendar month's whole months: January 0.9987, February 1.0019, March 0.9989, April 0.9970, May 0.9791, June 0.9657, July 0.9765, August 0.9876, September 0.9867, October 0.9891, November 0.9971, December 0.9989. Ten whole months fall under 0.97 (2020-06, 2022-07, 2022-10, 2023-05, 2023-06, 2023-07, 2024-05, 2024-07, 2025-06, 2026-06). Consumption falls short in the same months (twelve under 0.97), so the gap is not production's alone. By year the median moves from 0.9969 (2020) and 0.9977 (2021) to 0.9863 to 0.9933 from 2022 on.

## Where the description and the data disagree

1. **"Retrieved: 20261024T064329Z ... by warehouse/connectors/statnett_norway.py".** Header line 4 names the run that wrote the file as the retrieval; that run made no request (its raw folder holds only the lock check). The answer was fetched at 06:29:35Z by session 2350's probe script, as the line's second half and every `retrieved_at` say. Suggested: "Written: 20261024T064329Z (UTC), offline, by warehouse/connectors/statnett_norway.py, from the answer fetched at 2026-10-24T06:29:35Z by session 2350's probe (runs/c105/s2300/probe.py)".
2. **"About 1 percent under", put down to wind.** Header line 3 and the docstring ("production is about 1 percent under Statistics Norway's total generation", after Statnett's sentence on wind power from 2019) and `SESSION_2350_REPORT.md` ("some summer months are down to 96 percent"). The median whole month is 0.6 percent under and the mean 1.1 percent, but the gap is seasonal: 0.3 percent or less at the median of each month from November to March, 3.4 percent at June's median, 3.9 percent in July 2023; consumption falls short in the same months, down to 4.9 percent (July 2023), so missing wind production does not account for it, and October 2022 is also under 97 percent. Suggested: "about 1 percent under on average: 0.3 percent or less from November to March, 2 to 4 percent from May to July; consumption falls short in the same months (session 2353)", with Statnett's sentence quoted as Statnett's, not as the cause.
3. **No record of the run or the gaps.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap". It holds no row of this table: the run wrote only `runs/status/statnett_norway.json`, and the eight days of November 2025 are named only in header line 3 (no row in `run_status.csv` or `known_gaps.csv`). Suggested: record the run with `run_status.py record`, and the eight days as gaps in `run_status.csv` or `known_gaps.csv`.
4. **"May be public" if the ERW sells anything.** `docs/licenses.md`, the table's row, gives "may be public" in the column "If the ERW sells anything" for a publisher whose terms no one has read ("not settled", "not read: Statnett SF"). Suggested: "not settled" there too, until Statnett's terms are read.

Not acted on: this note changes no file but itself. The eight missing days are Statnett's, recorded, not filled.

## The session report against the table

`SESSION_2350_REPORT.md`: "4,960 figures, production and consumption in MWh as published, for Norway's days from 1 January 2020 to 23 October 2026": holds. "They hold one empty slot after each autumn clock-change day, 2020 to 2025": holds, slots 299 to 2131. "The last slot to Norway's day of the end time, the day in progress (82,734 MWh, partial)": holds (production). "Treating them as days would put it six days in the future": holds, 2026-10-30. "Eight days Statnett leaves empty, 18 to 25 November 2025": holds. "Production is 99.4 percent of total generation (the median of 81 months); consumption is 99.2 percent of gross consumption; November 2025 is 70 percent": holds (0.9936, 0.9918, 0.702). "Some summer months are down to 96 percent": production's lowest is 96.1 percent, consumption's 95.1 (disagreement 2). "The clock-change Sundays do not stand out from the Sundays around them": holds, recounted above. "The test is tests/test_session2350.py (4 tests)": holds.

## What it does not hold

- Hours or any period shorter than a day; production by type (hydro, wind, thermal); imports and exports, by neighbour or in all; Norway's price areas NO1 to NO5.
- Days before 1 January 2020, which the request (`From=2020-01-01`) did not ask for; the eight days of 18 to 25 November 2025; the day in progress and every day after 23 October 2026 until the connector is run again (it is in no schedule).
- Whether a clock-change day's figure covers 23, 24 or 25 hours; Statnett's earlier figures for a day it has revised (`vintage` blank, one retrieval).
- The production Statnett's page says may be missing (wind power that came into operation after 2019, and whatever makes the summer gap); Statistics Norway's monthly balance is `ssb_norway_electricity_monthly`.
