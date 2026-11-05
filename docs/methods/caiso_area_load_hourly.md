# Hourly actual load by transmission access charge (TAC) area, and the ISO's total (CAISO OASIS, SLD_FCST)

Energy Research Warehouse (ERW), method note written in session 2060 (chain 066) for a table first written on 7 October 2026 (session 138).

Tables: `caiso_area_load_hourly`

## Publisher and address

California Independent System Operator (CAISO), OASIS report SLD_FCST, "CAISO Demand Forecast", its actual run (market run ACTUAL, the hourly integrated load, not a forecast), through the SingleZip API, one request a 30-day window:

`https://oasis.caiso.com/oasisapi/SingleZip?queryname=SLD_FCST&market_run_id=ACTUAL&tac_area_name=CA%20ISO-TAC,PGE-TAC,SCE-TAC,SDGE-TAC,VEA-TAC,MWD-TAC&startdatetime=<YYYYMMDD>T00:00-0000&enddatetime=<YYYYMMDD>T00:00-0000&version=1&resultformat=6`

The answer is a zip of one CSV. The request names the six areas, so the report's other areas (the docstring counts 37 without the parameter, most of them balancing areas of the Western Energy Imbalance Market) are not asked for. Report page `https://oasis.caiso.com/mrioasis/logon.do`. Source id `caiso:SLD_FCST`. Connector: `warehouse/connectors/caiso_area_load.py` (session 138), its only table, with the frame it shares with the other load connectors in `warehouse/connectors/zone_load.py` and the counter in `warehouse/connectors/dam_cleared.py`. It is run once a week, on Saturday (UTC), by `warehouse/refresh_supply.sh`, which `warehouse/run_daily.sh` calls.

## Vintage and revision

17 September 2021 00:00 UTC to 10 October 2026 14:00 UTC in the file on the data machine, last written by run `20261010T150256Z` and restored from the Redivis draft by `scripts/sync.py`, as its header says. The rows' `retrieved_at` are 7 October 2026 (263,514 rows) and 10 October 2026 (2,826). `coverage.csv` gives the same 266,340 rows and dates.

The windows are 30 days counted from 1 January 2019 (UTC), so a window's address never changes; the table begins with the window of 17 September 2021. A run asks, newest first, for the windows that reach from its first day (by default 10 days back; `--from` for a history) to today. A window that ends in the last 35 days is asked of CAISO again each run; an earlier one is read from the raw file a run kept (`warehouse/raw/caiso_area_load/`). `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): an hour asked again replaces the held one, and an hour no longer asked is kept from the earlier run.

## Shape and variables

Series, 266,340 rows: 6 entities of 44,390 hours each. `variable` `load`; `value` CAISO's data item SYS_FCST_ACT_MW, "Total Actual Hourly Integrated Load", MW over the hour, whole numbers; `unit` MW; `freq` PT1H; `ts_utc` the interval's start as CAISO gives it in GMT; `market` `caiso_load`; `geo` US-CA; `node` CAISO's area name; `vintage` empty.

| Entity | Area (`node`) | Mean MW | Highest MW |
|---|---|---|---|
| `caiso:system` | CA ISO-TAC, CAISO's own total | 25,721 | 51,292 (6 September 2022, 23:00 UTC) |
| `caiso:SCE-TAC` | SCE-TAC | 11,991 | 25,851 |
| `caiso:PGE-TAC` | PGE-TAC | 11,250 | 22,371 |
| `caiso:SDGE-TAC` | SDGE-TAC | 2,252 | 5,395 |
| `caiso:MWD-TAC` | MWD-TAC | 159 | 316 |
| `caiso:VEA-TAC` | VEA-TAC | 70 | 475 |

A TAC area is not a trading hub: PGE-TAC lies in NP15 and ZP26, SCE-TAC and SDGE-TAC in SP15, and no join with the price tables is offered. Nothing is summed by the connector; `caiso:system` is CAISO's own figure. Two areas hold negative hours as CAISO gives them: VEA-TAC 33 (as low as -80 MW, July 2022 to February 2025) and MWD-TAC one (-1 MW, 10 February 2022); MWD-TAC is 0 in 986 hours. On 10 October 2026 at 14:00 UTC: the system 24,548 MW, SCE-TAC 11,386, PGE-TAC 10,412, SDGE-TAC 2,525, MWD-TAC 176, VEA-TAC 49.

## Reading OASIS

- A zip with no CSV that holds OASIS's error 1000 ("No data returned") gives no hour; any other answer without a CSV stops the run, and nothing is written.
- The CSV must hold the columns INTERVALSTARTTIME_GMT, INTERVALENDTIME_GMT, MARKET_RUN_ID, TAC_AREA_NAME, XML_DATA_ITEM and MW, or the run stops. Only rows of SYS_FCST_ACT_MW, run ACTUAL and the six areas are kept.
- An interval that is not one hour stops the run.
- A value that is not a number is not written; it is not counted.
- An area's hour given twice in a window is written once when its rows agree, and not at all when they differ; those hours are counted in the header. Two windows that hold the same hour give it once, from the newer window.
- No hour at all stops the run, and nothing is written. A newest hour more than 5 days old stops it too, recorded as a skip ("stale at source", the publisher's lag), not a failure.
- Ceiling: 12,000 lines read from CAISO in a run by default (a raw file reused does not count). Before each window the run checks that another 4,320 lines (30 days, 24 hours, 6 areas) would fit; if not, it stops asking, writes what it has and says so in the header.
- A request is tried up to four times (5, 10 and 15 seconds apart); an HTTP 404 is not retried. Six seconds between requests. CAISO is checked against `warehouse/metadata/paused_sources.csv` before any request (it is not paused).

## License

The header: "License: public, with credit to the California ISO. Its terms: materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO" (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026)." `coverage.csv`: public. `license_tables.csv` names CAISO as the table's one publisher (from the source registry); `license_verdicts.csv` gives CAISO "may be public" (read 3 of `license_reads.csv`, 12 October 2026), with the note that the same page's API terms forbid use "for any other benchmarking or competitive purposes". `docs/licenses.md`: ERW verdict public.

## Cross-checks (session 2060)

- The counts above were computed from the rows, read past the 12 header lines; no (entity, variable, ts_utc) is given twice.
- Hours complete: from the first hour to the last there are 44,391 hours; each of the six entities holds 44,390, and the one hour missing is the same for all six, 31 August 2024 17:00 UTC.
- The five areas sum to `caiso:system` exactly (a difference of 0 MW) in all 44,390 hours. Over the whole table SCE-TAC carries 46.6% of the system's load, PGE-TAC 43.7%, SDGE-TAC 8.8%, MWD-TAC 0.6% and VEA-TAC 0.3%.
- The system's mean load by year: 25,660 MW in 2022, 25,024 in 2023, 25,599 in 2024 (8,783 hours, a leap year less the missing hour), 25,664 in 2025, 27,473 in 2026 to 10 October.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- CAISO's load forecasts (the report's other market runs): the actual run only.
- The balancing areas of the Western Energy Imbalance Market that the report also answers.
- Prices: CAISO's trading hubs are in the ERW's price tables, and a TAC area does not map to a hub one for one.
- Hours before 17 September 2021, and the hour of 31 August 2024 17:00 UTC.
