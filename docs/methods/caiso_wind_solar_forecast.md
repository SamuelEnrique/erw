# Wind and solar, the day-ahead forecast and the actual output, by trading hub, an hour (CAISO OASIS, SLD_REN_FCST)

Energy Research Warehouse (ERW), method note written in session 2060 (chain 066) for a table first written on 6 October 2026 (session 133).

Tables: `caiso_wind_solar_forecast`

## Publisher and address

California Independent System Operator (CAISO), OASIS report SLD_REN_FCST, "Wind and Solar Forecast", through the SingleZip API, asked twice for each span of at most 30 days, once for market run DAM (the day-ahead forecast) and once for ACTUAL (actual generation):

`https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=SLD_REN_FCST&version=1&market_run_id=<DAM|ACTUAL>&startdatetime=<YYYYMMDD>T07:00-0000&enddatetime=<YYYYMMDD>T07:00-0000`

Each span runs from 07:00 UTC of its first day to 07:00 UTC of the day after its last, and the spans meet end to start. Report page `https://oasis.caiso.com/mrioasis/logon.do`. Source id `caiso:SLD_REN_FCST`. Connector: `warehouse/connectors/caiso_wind_solar_forecast.py` (session 133), its only table. The data machine's daily run runs it as the step `dm_caiso_ws_forecast` of `warehouse/run_data_machine_tables.sh`, with `--start` ten days before today (UTC), to yesterday in Pacific time. The first date is from the rows: the earliest `retrieved_at` is 6 October 2026 09:35 UTC; session 133's report gives no date of its own.

## Vintage and revision

1 June 2023 07:00 UTC to 23 October 2026 06:00 UTC (Pacific days 1 June 2023 to 22 October 2026) in the file on the data machine, written by run `20261023T173048Z`. Its header: "Window: this run asked 2026-10-13 to 2026-10-22; CAISO answered no data for 0 of the spans asked" and "This run wrote 2880 rows: 288 new, 2592 replacing earlier rows". `coverage.csv`, built before that run, gives 344,329 rows to 22 October 2026 06:00 UTC; the file holds 344,617. The rows' `retrieved_at`: 6 October 2026 (338,857 rows, session 133's pull from January 2023), 288 on each day from 13 to 22 October, and 2,880 on 23 October.

Without `--start` a run asks from 1 January 2023; OASIS keeps the report for about three years, and the rows begin on 1 June 2023 (session 133's report: "CAISO from June 2023 (OASIS keeps about three years)"). Every span asked is asked of CAISO again (no raw file is reused; each run's requests are saved under `warehouse/raw/caiso_wind_solar_forecast/<run_id>/`). `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): an hour read again replaces the held one, so a revised hour is taken, and an hour no longer asked is kept.

## Shape and variables

Series, 344,617 rows: 3 entities, 12 series. `entity` `caiso:<hub>`, CAISO's trading hubs NP15, SP15 and ZP26; `value` CAISO's MW for the hour, unchanged; `unit` MW; `freq` PT1H; `ts_utc` the interval's start as CAISO gives it in GMT; `geo` US-CA; `node` the hub; `market` and `vintage` empty.

| Variable | Market run | Hours a hub | Mean MW, NP15, SP15, ZP26 |
|---|---|---|---|
| `solar_forecast_dam_mw` | DAM | 29,760 | 756.9, 4,300.3, 834.5 |
| `solar_actual_mw` | ACTUAL | 29,692, 29,692, 29,693 | 621.9, 3,889.6, 725.1 |
| `wind_forecast_dam_mw` | DAM | 29,760; ZP26 23,711 | 431.1, 1,407.6, 20.7 |
| `wind_actual_mw` | ACTUAL | 29,691, 29,692; ZP26 23,646 | 419.9, 1,365.1, 24.0 |

ZP26's wind begins on 8 February 2024 08:00 UTC; every other series on 1 June 2023 07:00 UTC. The actual output is negative in many hours as CAISO gives it (solar at night: NP15 9,902 hours, SP15 12,890, ZP26 11,676; wind 271 to 3,793 hours a hub); the forecasts are never negative. The three hubs' solar output was highest on 25 June 2026 at 19:00 UTC, 19,738.5 MW.

## Reading OASIS

- A request is tried up to four times (12, 24 and 36 seconds apart); an answer that is not HTTP 200 or not a zip is a failure. One that still fails stops the run, and nothing is written.
- An answer that is OASIS's error 1000 ("No data returned for the specified selection") is logged and skipped, and the spans so answered are counted in the header; any other OASIS error stops the run. A span with no row of the three hubs is treated the same way.
- The CSV must hold INTERVALSTARTTIME_GMT, INTERVALENDTIME_GMT, TRADING_HUB, RENEWABLE_TYPE, MW and MARKET_RUN_ID; the hubs' rows must be of the market run asked and of Solar or Wind only; an interval that is not one hour stops the run. Rows of areas outside the three hubs (other balancing areas of CAISO's regional markets) are passed over.
- A value that is not a number is not written; it is not counted.
- An hour that two answers give is written once, from the later.
- Ceiling: 2,000,000 rows for session 133's forecast pulls (CAISO and ERCOT). The count is of the rows kept from the three hubs, added after each answer; past the ceiling the run stops and writes nothing.
- No row at all stops the run. Six seconds between requests. No test of the newest hour's age. The connector does not consult `warehouse/metadata/paused_sources.csv` (CAISO is not on it).

## License

The header: "License: public (CAISO OASIS public data; cite "California ISO, OASIS")." `coverage.csv`: public. `license_tables.csv` names CAISO as the table's one publisher (from the source registry); `license_verdicts.csv` gives CAISO "may be public" (read 3 of `license_reads.csv`, 12 October 2026): its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO", with the note that the same page's API terms forbid use "for any other benchmarking or competitive purposes". `docs/licenses.md`: ERW verdict public.

## Cross-checks (session 2060)

- The counts above were computed from the rows, read past the 11 header lines; no (entity, variable, ts_utc) is given twice.
- Hours complete: from 1 June 2023 07:00 to 23 October 2026 06:00 UTC there are 29,760 hours. The five forecasts that begin then hold every one, and ZP26's wind forecast every hour of its span. The actuals miss 65 to 69 hours each, mostly single hours and the same hours across hubs (8 June 2023 16:00, 11 July 2023 17:00, 13 July 2023 16:00 UTC, and so on).
- Forecast against actual, over the hours both hold: solar's forecast is above its output on average (bias 133.1 MW at NP15, 400.5 at SP15, 107.5 at ZP26; mean absolute error 161.2, 466.4, 136.1); wind's bias is 11.3, 42.4 and -3.3 MW (mean absolute error 92.9, 232.9, 9.3). Over the Pacific year 2025, the three hubs' solar forecast sums to 53.777 TWh against an output of 47.717, and wind to 15.493 against 15.342.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The report's other market runs (the hour-ahead and real-time forecasts): day-ahead forecast and actual only.
- The areas outside CAISO's three trading hubs that the report also lists.
- Hours before June 2023 (ZP26's wind before 8 February 2024), and the actual hours CAISO does not list.
- Curtailment: CAISO's figures are `caiso_curtailment_daily` and `caiso_curtailment_intervals`.
- The header's "Rows read" is the count of rows kept from the three hubs, not of the rows CAISO answered.
