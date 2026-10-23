# Demand cleared in the day-ahead market, the ISO's total, an hour (CAISO OASIS, ENE_SLRS)

Energy Research Warehouse (ERW), method note written in session 2060 (chain 066) for a table first written on 6 October 2026 (session 136).

Tables: `caiso_dam_cleared_energy`

## Publisher and address

California Independent System Operator (CAISO), OASIS report ENE_SLRS, "Market Schedules", day-ahead market (market run DAM), the ISO's totals (`tac_zone_name=Caiso_Totals`), every schedule, through the SingleZip API, one request a half month:

`https://oasis.caiso.com/oasisapi/SingleZip?queryname=ENE_SLRS&market_run_id=DAM&tac_zone_name=Caiso_Totals&schedule=ALL&startdatetime=<YYYYMMDD>T00:00-0000&enddatetime=<YYYYMMDD>T00:00-0000&version=1&resultformat=6`

The answer is a zip of one CSV with four schedules an hour (load, generation, imports, exports); only the data item ISO_TOT_LOAD_MW is kept. Report page `https://oasis.caiso.com/mrioasis/logon.do`. Source id `caiso:ENE_SLRS`. Connector: `warehouse/connectors/caiso_dam_cleared.py` (session 136), its only table, with the frame it shares with the other day-ahead cleared connectors in `warehouse/connectors/dam_cleared.py`. It is run once a week, on Saturday (UTC), by `warehouse/refresh_supply.sh`, which `warehouse/run_daily.sh` calls. The first date is from the rows: the earliest `retrieved_at` is 6 October 2026 20:24 UTC, and the connector's docstring names a request of 6 October 2026; session 136's report gives no date of its own.

## Vintage and revision

1 September 2025 00:00 UTC to 11 October 2026 06:00 UTC in the file on the data machine, last written by run `20261010T145938Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says. The rows' `retrieved_at` are 6 October 2026 (8,760 rows) and 10 October 2026 (967). `coverage.csv` gives the same 9,727 rows and dates.

A request covers a half month in UTC, the 1st to the 16th or the 16th to the next 1st; OASIS refuses 31 days. A run (by default 14 days back) asks every half from the first day of the month 14 days back to tomorrow, newest first; the last half is cut at the day after tomorrow, since the day-ahead market has run for tomorrow. A half of this month or the last is asked of CAISO again; an earlier half is read from the raw file a run kept (`warehouse/raw/caiso_dam_cleared/`). `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): an hour asked again replaces the held one, and the table grows past the window CAISO keeps.

## Shape and variables

Series, 9,727 rows, one entity. `entity` `caiso:system`; `variable` `dam_cleared_energy`; `value` CAISO's ISO_TOT_LOAD_MW, which the connector describes from CAISO's interface specification as the ISO's total MW cleared as demand in the day-ahead market, MW over the hour, to two decimals; `unit` MW; `freq` PT1H; `ts_utc` the interval's start as CAISO gives it in GMT; `market` `caiso_dam`; `geo` US-CA; `node` `ISO_TOT_LOAD_MW`; `vintage` empty.

| Entity | Variable | Hours | Mean MW | Lowest | Highest |
|---|---|---|---|---|---|
| `caiso:system` | `dam_cleared_energy` | 9,727 | 24,042 | 13,048 (19 April 2026, 19:00 UTC) | 44,254 (10 September 2026, 00:00 UTC) |

The last day, 11 October 2026, holds 7 hours (00:00 to 06:00 UTC), the end of the Pacific day of 10 October; the run read CAISO at 14:59 UTC on 10 October.

## Reading OASIS

- A zip with no CSV that holds OASIS's error 1000 ("No data returned") gives no hour; any other answer without a CSV stops the run, and nothing is written.
- The CSV must hold INTERVALSTARTTIME_GMT, INTERVALENDTIME_GMT, MARKET_RUN_ID, TAC_ZONE_NAME, XML_DATA_ITEM and MW, or the run stops. Only rows of ISO_TOT_LOAD_MW, run DAM and Caiso_Totals are kept.
- An interval that is not one hour stops the run.
- A value that is not a number is not written; it is not counted.
- An hour is written once whatever CAISO answers (the first read, from the newest half); an hour given twice after that stops the run.
- No hour at all stops the run. A newest hour more than 5 days old stops it, and nothing is written.
- Ceiling: 20,000 rows read from CAISO in a run by default, every row of each CSV fetched counted (all four schedules; a raw file reused does not count). Past it the run stops and writes nothing.
- A request is tried up to four times (5, 10 and 15 seconds apart); an HTTP 404 is not retried. Six seconds between requests. CAISO is checked against `warehouse/metadata/paused_sources.csv` before any request (it is not paused).

## License

The header: "License: public, with credit to the California ISO. Its terms: materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO" (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026)." `coverage.csv`: public. `license_tables.csv` names CAISO as the table's one publisher (from the source registry); `license_verdicts.csv` gives CAISO "may be public" (read 3 of `license_reads.csv`, 12 October 2026), with the note that the same page's API terms forbid use "for any other benchmarking or competitive purposes". `docs/licenses.md`: ERW verdict public.

## Cross-checks (session 2060)

- The counts above were computed from the rows, read past the 12 header lines; no hour is given twice.
- Hours complete: from 1 September 2025 00:00 to 11 October 2026 06:00 UTC there are 9,727 hours, and the table holds every one.
- Against the actual load of `caiso_area_load_hourly` (`caiso:system`, CA ISO-TAC), in the 9,711 hours the two share (to 10 October 2026 14:00 UTC): the day-ahead cleared demand averages 24,041 MW and the actual load 27,020. The ratio's median is 0.937; it is lowest at midday Pacific (median 0.721 at 11:00) and near 0.97 in the evening (18:00 to 21:00); the cleared demand is above the actual load in 202 hours. The two are different quantities and the connector does not compare them.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The generation, import and export schedules the same request answers: read and not written.
- The real-time market and the hour-ahead run: day-ahead only.
- Demand by area: the actual load by TAC area is `caiso_area_load_hourly`. The other operators' day-ahead cleared energy is in `ercot_dam_cleared_energy`, `nyiso_dam_cleared_energy`, `isone_dam_cleared_energy` and `spp_dam_cleared_energy`.
- Hours before 1 September 2025.
