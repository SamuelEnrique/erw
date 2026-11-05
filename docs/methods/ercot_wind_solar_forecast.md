# ERCOT wind and solar, the forecast a day ahead and the actual output, system-wide, an hour (ERCOT NP4-732-CD and report type 13483)

Energy Research Warehouse (ERW), method note written in session 2152 (chain 092) for a table first written on 6 October 2026 (session 133).

Tables: `ercot_wind_solar_forecast`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), two hourly reports on its public reports site, each posted once an hour, each holding about two days of actual output behind it and a week of forecast ahead; ERCOT's list keeps about a week of postings (each document's ExpiredDate is a week after it was published):

- NP4-732-CD, "Wind Power Production, Hourly Averaged Actual and Forecasted Values" (report type 13028).
- Report type 13483, which the connector names NP4-745-CD. ERCOT's own list for it, saved at 17:32 UTC on 23 October 2026 under `warehouse/raw/ercot_wind_solar_forecast/20261023T173200Z/`, names it "Solar Power Production - Hourly Averaged Actual and Forecasted Values", with the file name `PVGRHRLYAVGACTNP4737_csv`: NP4-737-CD (see "Found while writing this note").

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=<13028 or 13483>` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each posting, a zip of one CSV)

Columns read: DELIVERY_DATE, HOUR_ENDING, DSTFlag, SYSTEM_WIDE_GEN (actual output) and the short-term forecast, STWPF_SYSTEM_WIDE for wind and STPPF_SYSTEM_WIDE for solar. A solar posting also holds COP_HSL_SYSTEM_WIDE, PVGRPP_SYSTEM_WIDE and SYSTEM_WIDE_HSL, which are not read. Every request goes to the host `www.ercot.com`, under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read by session 850, and again by session 2002 at 15:11:50 UTC on 23 October 2026, read 170 of `warehouse/metadata/license_reads.csv`), with the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)". Source ids `ercot:NP4-732-CD` and `ercot:NP4-745-CD` (the second for report type 13483). Connector: `warehouse/connectors/ercot_wind_solar_forecast.py` (session 133), its only table.

It is run every day on the data machine, as the step `dm_ercot_ws_forecast` of `warehouse/run_data_machine_tables.sh` (session 247), which `warehouse/run_data_machine.sh` sources: a soft step under `warehouse/health.py`, then `warehouse/table_stores.py` (validator, coverage, archive, Redivis draft) when the table moved, and the table is in the weekly live-set load. `warehouse/refresh_mix.sh` also calls the connector, but no job calls that script (its own header, and the session 310 note in `run_data_machine_tables.sh`); `warehouse/run_daily.sh` does not. The data machine holds 13 run logs, from 07:47 UTC on 13 October to 17:32 UTC on 23 October 2026, and rows were retrieved on every day from 13 to 23 October and on none from 7 to 12 October. `run_status.csv` holds no row for this connector. The first date is from the rows: the earliest `retrieved_at` is 6 October 2026 09:30:26 UTC, and `sources.csv` first saw both reports on 2026-10-06; session 133's report gives no date of its own, names the freeze of 5 to 7 October, and says ERCOT's forecast view rested then on 146 hours.

## Vintage and revision

Actual output for the hours 27 September 2026 05:00 UTC to 23 October 2026 15:00 UTC, and forecasts for 30 September 2026 06:00 UTC to 30 October 2026 15:00 UTC, in the file on the data machine, last written by run `20261023T173200Z`, whose header reads: "wind: 180 postings, 227 hours of actual, 322 of forecast, 154 with both; solar: 180 postings, 227 hours of actual, 322 of forecast, 154 with both", 77,760 rows of ERCOT's files read. The rows' `retrieved_at` are 6 October 2026 (672 rows), 96 rows on each day from 13 to 22 October, and 1,098 on 23 October. `vintage` is empty.

`coverage.csv` gives 2,634 rows, 2026-09-27T05:00:00Z to 2026-10-29T15:00:00Z, last run 2026-10-22T17:32:57Z. It does not agree with the file, which holds 2,730 rows to 2026-10-30T15:00:00Z: the coverage row was built before the run of 23 October, which added 96 rows.

A run reads every posting on both lists. For each hour, the actual is SYSTEM_WIDE_GEN from the newest posting that holds it, and the forecast is from the newest posting published at least 24 hours before the hour began. `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): a run replaces an hour's actual with a newer posting's, and an hour's forecast with one from a newer posting still a day ahead, and the table keeps hours ERCOT's list has dropped. An hour more than a day after a run holds, until a later run replaces it, a forecast made more than 24 hours ahead: after the run of 23 October, 142 hours of each fuel (24 October 18:00 UTC to 30 October 15:00 UTC). A posting saved by an earlier run on the machine is read from `warehouse/raw/ercot_wind_solar_forecast/`; the lists are always asked again. A row's `retrieved_at` is when the run finished reading the report, and its `source_url` is the report's document list, not the posting.

## Shape and variables

Series, 2,730 rows, one entity. `entity` `ercot:SYSTEM`; `variable` `wind_actual_mw`, `solar_actual_mw` (SYSTEM_WIDE_GEN), `wind_forecast_24h_mw`, `solar_forecast_24h_mw` (STWPF or STPPF); `value` ERCOT's figure, rounded to four decimals; `unit` MW; `freq` PT1H; `ts_utc` the hour's start, from DELIVERY_DATE and HOUR_ENDING (Central) less one hour, DSTFlag Y marking the repeated autumn hour; `market` empty; `geo` US-TX; `node` SYSTEM; `vintage` empty.

| Entity | Variable | Hours | Mean MW | Lowest | Highest |
|---|---|---|---|---|---|
| `ercot:SYSTEM` | `wind_actual_mw` | 635 | 11,675 | 896.99 (27 September 2026, 18:00 UTC) | 26,491.91 (16 October 2026, 13:00 UTC) |
| `ercot:SYSTEM` | `wind_forecast_24h_mw` | 730 | 12,863 | 1,763.0 (9 October 2026, 14:00 UTC) | 32,737.6 (16 October 2026, 17:00 UTC) |
| `ercot:SYSTEM` | `solar_actual_mw` | 635 | 9,157 | 0.08 (5 hours, first 5 October 2026, 01:00 UTC) | 32,938.08 (17 October 2026, 16:00 UTC) |
| `ercot:SYSTEM` | `solar_forecast_24h_mw` | 730 | 8,950 | 0.0 (336 hours, the nights) | 33,199.5 (17 October 2026, 16:00 UTC) |

In the 562 hours of each fuel that hold both (30 September 06:00 to 23 October 15:00 UTC), the forecast less the actual averages +868 MW for wind (mean absolute 1,571 MW, against a mean actual of 11,753) and +331 MW for solar (mean absolute 687 MW, against 9,057). Computed here; the connector computes no error.

## Reading ERCOT's reports site

- Each list is asked with a timeout of 90 seconds inside `iso_prices.with_retries` (up to four tries, 5, 10 and 15 seconds apart), which retries an error of the connection only: an answer that is not the list's JSON stops the run.
- Every document whose name contains "csv" is read (180 of the 360 each list held on 23 October), through `iso_prices.fetch_raw` (up to four tries; HTTP 404 is not retried and stops the run), 0.15 seconds after each posting asked of ERCOT and one second between the two reports.
- The first file in each zip is read as a CSV (not checked to be the only one, or a CSV); it must hold DELIVERY_DATE, HOUR_ENDING, SYSTEM_WIDE_GEN and the forecast column, or the run stops and nothing is written.
- Ceiling: the rows of every posting read are counted, reused ones included; once the count passes 200,000 the run stops and writes nothing. The check comes after each file is read. The run of 23 October read 77,760.
- A blank or a value that is not a number gives no row. An hour the spring clock change skips is dropped without a word.
- No posting holding any hour stops the run. There is no test of how old the newest hour is.
- No pause check: the connector does not ask `iso_prices.paused()` before its requests (ERCOT is not paused).
- `--out-dir` writes a trial elsewhere and leaves the registry and the run status alone.

## License

The header: "License: public (ERCOT public market information; cite "ERCOT")." `coverage.csv`: public. `license_tables.csv` names ERCOT as the table's one publisher (from the source registry); `license_verdicts.csv` gives ERCOT "may be public" (read 2 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict public.

## Cross-checks (session 2152)

- The counts above were computed from the rows, read past the 13 header lines; no hour is given twice.
- Hours complete: the actuals hold every hour from 27 September 05:00 to 23 October 15:00 UTC (635), and the forecasts every hour from 30 September 06:00 to 30 October 15:00 UTC (730).
- Against the system-wide output of `ercot_wind_solar_hsl_hourly`, read from ERCOT's reports by region (NP4-742-CD, NP4-745-CD), in the 608 hours both hold: the two differ in 330 wind hours and 327 solar hours, by at most 0.03 MW (wind at 01:00 UTC on 9 October, solar at 00:00 UTC on 8 October).
- The connector has no cross-check of its own beyond its reading rules.

## Found while writing this note

- Report type 13483 is not NP4-745-CD. The connector's docstring, its `REPORTS`, the source id `ercot:NP4-745-CD`, the header's Source line and product page, `sources.csv` and the coverage row's `source_report` all name it NP4-745-CD, while ERCOT's list names its files `PVGRHRLYAVGACTNP4737`: it is NP4-737-CD. NP4-745-CD is the solar report by region (report type 21809) that `ercot_wind_solar_history.py` reads. `docs/methods/curtailment.md` made the same correction for `curtailment.py`. The rows are from report type 13483 as they should be; only the name is wrong.
- The docstring calls each forecast "the forecast as it stood a day ahead". For an hour more than a day after the latest run the row holds a forecast made further ahead, up to about a week, and is replaced on a later run (142 hours of each fuel in the file now). If the runs stop, those rows stay with their longer lead.
- The docstring says "The run stops if the rows read would pass 200,000"; the code stops after reading the file that passes it.
- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 23 October 2026, session 2002). Neither its docstring nor its header says so.
- `CLAUDE.md` says every connector that reaches a publisher's servers asks `iso_prices.paused()` first. This one does not.
- `coverage.csv` lags the file by the run of 23 October (above).

## What it does not hold

- Forecasts by region, the other forecast columns (ERCOT's PVGRPP and COP HSL), and the High Sustained Limit; the HSL is in `ercot_wind_solar_hsl_hourly`.
- Hours before 27 September 2026 (actual) and 30 September 2026 (forecast): ERCOT's list keeps about a week, and its history is not openly published.
- Forecasts for hours whose day-ahead posting left ERCOT's list before a run read it.
