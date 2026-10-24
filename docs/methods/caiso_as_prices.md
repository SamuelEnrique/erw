# Day-ahead ancillary service clearing prices, the two system regions, an hour (CAISO OASIS, PRC_AS)

Energy Research Warehouse (ERW), method note written in session 2060 (chain 066) for a table first written on 2 October 2026 (session 65).

Tables: `caiso_as_prices`

## Publisher and address

California Independent System Operator (CAISO), OASIS report PRC_AS, "AS Clearing Prices", day-ahead market (market run DAM), version 12, every service type and region, through the SingleZip API, one request a Pacific operating day (from its midnight to the next, in UTC):

`https://oasis.caiso.com/oasisapi/SingleZip?queryname=PRC_AS&market_run_id=DAM&anc_type=ALL&anc_region=ALL&startdatetime=<YYYYMMDD>T<HH>:00-0000&enddatetime=<YYYYMMDD>T<HH>:00-0000&version=12&resultformat=6`

OASIS answers it at `https://oasis.caiso.com/oasisapi/GroupZip?groupid=DAM_PRC_AS_GRP&startdatetime=<YYYYMMDD>T<HH>:00-0000&resultformat=6&version=12`, the address every row's `source_url` keeps. The connector's docstring: OASIS answers one operating day a request whatever range is asked (checked in session 65). Report page `https://oasis.caiso.com/mrioasis/logon.do`. Source id `caiso:PRC_AS`. Connector: `warehouse/connectors/caiso_as_prices.py` (session 65), its only table; method `docs/methods/capacity_and_ancillary.md`. The daily run (`warehouse/run_daily.sh`) runs it with `--start` six days before today (UTC; `DAYS` plus 3, `DAYS` 3 by default), to today in Pacific time.

## Vintage and revision

Pacific operating days 14 July 2023 to 23 October 2026 (14 July 2023 07:00 UTC to 24 October 2026 06:00 UTC) in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, from the connector's run `20261023T150356Z`. Its header: "Window: Pacific operating days 2026-10-17 to 2026-10-23. ... 0 are left out of this run." `coverage.csv` gives the same 229,440 rows and dates. The rows' `retrieved_at`: 2 October 2026 (145,728 rows, session 65's first pull from 1 September 2024), 14 October 2026 (79,872, session 273's pull of 14 July 2023 to 31 August 2024, the oldest days OASIS still served), and 3,840 rows (20 days of 192 rows) on 16 other days from 3 to 23 October 2026.

Each day's zip is kept in `warehouse/raw/caiso_as_prices/`, and a day already saved (under either address) is read from it and never asked of CAISO again, so a later revision by CAISO of a saved day is not taken; a saved answer that turns out to be an error document is fetched again. `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): a day read again replaces its rows, and the rest of the table is kept.

## Shape and variables

Series, 229,440 rows: 2 regions by 4 services, 8 series of 28,680 hours each (1,195 Pacific days). `unit` USD/MW-hour (US dollars per MW of capacity held for one hour), to five decimals at most; `freq` PT1H; `ts_utc` the trading hour's start (INTERVALSTARTTIME_GMT); `market` `caiso_dam`; `geo` US-CA; `node` the region; `vintage` empty.

| Variable | Service (OASIS type) | `caiso:AS_CAISO_EXP` mean | `caiso:AS_CAISO` mean, hours above 0 |
|---|---|---|---|
| `as_price_dam_ru` | Regulation Up (RU) | 3.157 | 0.004, 134 |
| `as_price_dam_rd` | Regulation Down (RD) | 4.737 | 0.057, 851 |
| `as_price_dam_sr` | Spinning Reserve (SR) | 1.716 | 0.000, 1 |
| `as_price_dam_nr` | Non-Spinning Reserve (NR) | 1.602 | 0, none |

`caiso:AS_CAISO` is the CAISO system region and `caiso:AS_CAISO_EXP` the expanded system region (the system with the interties), as OASIS names them. The sub-regions (AS_NP26, AS_SP26 and their expanded forms) are not pulled, by session 65's ruling. The prices are carried by the expanded region: it is above 0 in all but 1 hour for RU, SR and NR and all but 9 for RD, while the system region is 0 in 97% to 100% of hours. The highest price is 1,011.72 USD/MW-hour for RU, SR and NR on 17 August 2023, 02:00 UTC (the evening of 16 August, Pacific). The expanded region's yearly means (Pacific years): RU 5.267, RD 5.377, SR 3.856, NR 3.568 in 2023 (from 14 July); RU 2.278, RD 4.940, SR 0.748, NR 0.703 in 2025.

## Reading OASIS

- An answer that is not a zip, or a zip without one CSV that is not OASIS's "No data returned", is a throttle: the day is asked again after 30, 60, 90 and 120 seconds. A request that fails after the shared fetcher's four tries (5, 10 and 15 seconds apart) is asked again after 60, 120, 180 and 240 seconds. After five tries the run stops and nothing is written. An HTTP 404 is not retried and stops the run.
- A day OASIS answers with "No data returned" is a gap: no row, logged, counted in the header and recorded as a gap in the run's status.
- The CSV must hold INTERVALSTARTTIME_GMT, OPR_DT, ANC_TYPE, ANC_REGION, MARKET_RUN_ID, XML_DATA_ITEM and MW; its market run must be DAM only; a service type other than RU, RD, SR, NR and the mileage types RMU and RMD stops the run; every kept data item must end in `_CLR_PRC`; the file must hold no operating day but the one asked. Each failure stops the run.
- Kept: the two system regions and the four capacity services. The mileage prices (RMU, RMD) are left out.
- An empty price is not written. A price that is not a number stops the run. A (region, service, hour) given twice stops it.
- Never filled: a (region, service, Pacific day) is written only with every hour of the day exactly once (24, or 23 and 25 at the clock changes); a day short of it is left out, logged, counted in the header and recorded as a gap.
- Ceiling: 500,000 rows in a run (session 65's ruling). Past it only the expanded system region is kept; if that would still pass it, nothing is written.
- Six seconds after each request CAISO answered. No test of the newest day's age. The connector does not consult `warehouse/metadata/paused_sources.csv` (CAISO is not on it).

## License

The header: "License: public. CAISO terms of use: materials may be used provided the notices are kept intact and the California ISO is credited." `coverage.csv`: public. `license_tables.csv` names CAISO as the table's one publisher (from the source registry); `license_verdicts.csv` gives CAISO "may be public" (read 3 of `license_reads.csv`, 12 October 2026), with the note that the same page's API terms forbid use "for any other benchmarking or competitive purposes". `docs/licenses.md`: ERW verdict public.

## Cross-checks (session 2060)

- The counts above were computed from the rows, read past the 12 header lines; no (entity, variable, ts_utc) is given twice.
- Days complete: every one of the 9,560 (series, Pacific day) groups holds exactly the day's hours (24, or 23 and 25 at the clock changes). Of the 1,198 calendar days from 14 July 2023 to 23 October 2026, three are missing from all eight series: 6, 7 and 8 April 2025, which session 65's report records as "no data returned" at OASIS.
- The expanded region's price is at least the system region's in 114,315 of 114,720 (service, hour) pairs; the 405 others are hours in which the system region holds a price of its own (for example RD on 4 August 2023, 05:00 UTC: 3.81 against 2.25).
- At the highest hours, RU, SR and NR of the expanded region are equal (17 August 2023, 02:00 UTC: 1,011.71778 each).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The sub-regions AS_NP26 and AS_SP26 and their expanded forms.
- The regulation mileage prices (RMU, RMD), per MW of movement, not of capacity.
- The hour-ahead (HASP) and real-time runs: day-ahead only.
- Days before 14 July 2023, and 6 to 8 April 2025.
- The connector's docstring and its default start say "from 2024-09-01"; the table begins on 14 July 2023 because session 273 ran it with `--start 2023-07-14`.
