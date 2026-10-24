# ERCOT's wind and solar, the forecast a day ahead and the actual output, hourly (ERCOT's hourly averaged actual and forecasted values)

Energy Research Warehouse (ERW), method note written in session 2138 (chain 090) for a table first written on 6 October 2026 (session 133).

Tables: `ercot_wind_solar_forecast`

How the energy mix page reads the forecasts is in `docs/methods/generation_mix_hourly.md` (session 133 and later); this note describes the code and the rows as they stand.

## Publisher and address

Electric Reliability Council of Texas (ERCOT), two hourly reports, each posted once an hour with about two days of actual output behind it and a week of forecast ahead:

- Wind: "Wind Power Production - Hourly Averaged Actual and Forecasted Values", NP4-732-CD, report type 13028 (list `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13028`). ERCOT's file names end `WPPHRLYAVGACTNP4732_csv`.
- Solar: "Solar Power Production - Hourly Averaged Actual and Forecasted Values", report type 13483 (list `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13483`). ERCOT's file names end `PVGRHRLYAVGACTNP4737_csv`, the product NP4-737-CD. The connector, its header and `sources.csv` call it NP4-745-CD (below).

Each posting is a zip at `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`. Source ids `ercot:NP4-732-CD` (wind) and `ercot:NP4-745-CD` (solar). Connector: `warehouse/connectors/ercot_wind_solar_forecast.py` (session 133), one step: it asks, reads and writes in one run (`--out-dir` writes a trial elsewhere).

## Vintage and revision

Actual output for 27 September 2026 05:00Z to 23 October 2026 15:00Z, forecasts for 30 September 2026 06:00Z to 30 October 2026 15:00Z, in the file on the data machine, written by run `20261023T173200Z` (23 October 2026): "This run: wind: 180 postings, 227 hours of actual, 322 of forecast, 154 with both; solar: 180 postings, 227 hours of actual, 322 of forecast, 154 with both." Its merge line: "File holds 2730 rows ... This run wrote 1098 rows: 96 new, 1002 replacing earlier rows ... 1632 rows are kept from earlier runs."

ERCOT's list keeps about a week: on 23 October it held 360 documents of each report, 180 of them CSV postings, published 16 October 00:55 to 23 October 11:55 Central. The data machine runs the connector every day (`dm_ercot_ws_forecast` in `warehouse/run_data_machine_tables.sh`); a day not pulled within the week is lost. The raw folders on the data machine show runs on 6 October and then daily from 13 October; the gap of 6 days 22 hours was inside the week, and no hour is missing (below).

Rows are merged into the file held on (entity, variable, ts_utc). An hour's actual is replaced by each later posting that holds it, for about two days. An hour's forecast is replaced while a newer posting published at least 24 hours before the hour is on the list, that is until the hour is 24 hours away. In the file, 672 rows say `retrieved_at` 6 October 2026, 96 rows each day from 13 to 22 October, and 1,098 rows 23 October. `vintage` is empty.

## Shape and variables

Series, 2,730 rows: 1 entity, 4 variables. `entity` ercot:SYSTEM (ERCOT's system-wide columns); `unit` MW; `freq` PT1H; `ts_utc` the hour's start (ERCOT's DELIVERY_DATE and HOUR_ENDING, Central); `geo` US-TX; `market` empty; `node` SYSTEM; `source_url` the report's list, not the posting; values rounded to 4 decimals.

| Variable | ERCOT's column | Rows | First hour | Last hour | Mean MW | Highest MW |
|---|---|---|---|---|---|---|
| `wind_actual_mw` | SYSTEM_WIDE_GEN | 635 | 2026-09-27T05:00Z | 2026-10-23T15:00Z | 11,675.1 | 26,491.9 |
| `wind_forecast_24h_mw` | STWPF_SYSTEM_WIDE | 730 | 2026-09-30T06:00Z | 2026-10-30T15:00Z | 12,862.5 | 32,737.6 |
| `solar_actual_mw` | SYSTEM_WIDE_GEN | 635 | 2026-09-27T05:00Z | 2026-10-23T15:00Z | 9,156.7 | 32,938.1 |
| `solar_forecast_24h_mw` | STPPF_SYSTEM_WIDE | 730 | 2026-09-30T06:00Z | 2026-10-30T15:00Z | 8,950.1 | 33,199.5 |

The forecast is ERCOT's short-term forecast for the hour (STWPF for wind, STPPF for solar) from the newest posting published at least 24 hours before the hour began. 562 hours of each fuel hold both an actual and a forecast (30 September 06:00Z to 23 October 15:00Z); 168 forecast hours of each lie after the last actual. Over the 562 hours the forecast was above the actual by 867.9 MW on average for wind (mean absolute difference 1,571.5 MW, 13.37 percent of the mean actual) and by 330.7 MW for solar (687.1 MW, 7.59 percent). No value is negative.

## Reading the source

- The connector does not ask `iso_prices.paused()` before it reaches ERCOT. ERCOT is not in `paused_sources.csv` today; if it were, this connector would still ask.
- Each report's list is asked afresh: up to four attempts (`iso_prices.with_retries`, the waits growing by 5 seconds), timeout 90 seconds. Every listed document whose FriendlyName contains "csv" is read through `iso_prices.fetch_raw`, which reuses a copy an earlier run of the connector saved on the machine (the run of 23 October saved 52 files: the two lists and 50 postings) and otherwise asks ERCOT, with 0.15 seconds after each request and 1 second between the two reports.
- A posting without DELIVERY_DATE, HOUR_ENDING, SYSTEM_WIDE_GEN and its forecast column stops the run. A value that is not a number is no row. An hour the spring clock change skips is no row; the repeated autumn hour is told apart by DSTFlag.
- Ceiling: 200,000 rows of ERCOT's files read in a run, saved copies included; past it the run stops and nothing is written. The run of 23 October read 77,760. The docstring's ceiling of 2,000,000 rows for session 133's forecast pulls in all is stated in the header, not counted by the code.
- An hour with no posting a day ahead of it has no forecast row. Nothing is filled. Any failure stops the run and no file is written.
- `retrieved_at` is the time each report was finished in the run, the same for all its rows; the row does not say which posting its value came from or when that posting was published.

## License

Public. `license_verdicts.csv` records ERCOT, read 2 (`https://www.ercot.com/help/terms`, 12 October 2026 in `license_reads.csv`): "may be public", for public and for commercial use. The sentence: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." The header: "License: public (ERCOT public market information; cite "ERCOT")." `sources.csv` flags `ercot:NP4-732-CD` and `ercot:NP4-745-CD` public; `license_tables.csv` lists the table under ERCOT.

## Cross-checks (session 2138)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice, and no hour is missing inside any variable's span.
- Against `ercot_wind_solar_hsl_hourly` (ercot:system, read from ERCOT's by-region reports by `ercot_wind_solar_history.py`), in the 608 hours both hold (28 September 05:00Z to 23 October 12:00Z): the actual output agrees within 0.03 MW in every hour, exactly in 278 wind hours and 281 solar hours. One hour of each differs by 0.03 MW, more than the 0.02 MW an hour that `ercot_wind_solar_history.py --check` allows between the two reports: wind on 9 October 01:00Z (5,398.02 here, 5,397.99 there) and solar on 8 October 00:00Z (118.43 and 118.40).
- Against `eia930_all_generation` (eia930:ERCO, net_generation_wind_mw and net_generation_solar_mw), in the 619 hours both hold (27 September 05:00Z to 22 October 23:00Z): the median difference is 0.3 MW for wind and 0.4 MW for solar, so EIA's hours and ERCOT's are the same hours (shifted by one hour the median difference is 666 MW for wind and 181 to 186 MW for solar). Wind differs by more than 100 MW in 24 hours, all on 4 and 5 October (UTC), EIA lower by 3,195 MW on average over 19 hours of 4 October and by 1,494 MW over 5 hours of 5 October; solar in 9 hours, all on 4 October, EIA lower by 981 MW on average. Over the shared hours EIA's sum is 0.9905 of ERCOT's for wind and 0.9985 for solar.

What the docstring and header say and ERCOT's files do not:

- The docstring, the `REPORTS` entry, the header and `sources.csv` name the solar report NP4-745-CD (source id `ercot:NP4-745-CD`, page `https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD`). The report the code reads, type 13483, is NP4-737-CD by ERCOT's own file names (`PVGRHRLYAVGACTNP4737_csv`). `ercot_wind_solar_history.py` gives NP4-745-CD to the solar report by geographical region (type 21809), and its `--check` names the system-wide reports "NP4-732-CD and NP4-737-CD". The source id and page address of the solar rows are therefore those of another ERCOT product.

## What it does not hold

- Hours before 27 September 2026 (actual) and 30 September 2026 (forecast): ERCOT's public list keeps about a week, and the first run was on 6 October 2026.
- Forecasts made at other lead times than 24 hours, ERCOT's other forecast columns (WGRPP, PVGRPP), the COP HSL and the actual HSL, and the load zone columns of the wind postings.
- Which posting each value came from.
