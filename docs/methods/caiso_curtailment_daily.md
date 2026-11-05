# Wind and solar curtailment and output, a day (CAISO's production and curtailments workbooks, then its Daily Renewable Report)

Energy Research Warehouse (ERW), method note written in session 2060 (chain 066) for a table first written on 27 September 2026 (session 18).

Tables: `caiso_curtailment_daily`

## Publisher and address

California Independent System Operator (CAISO), two sources, split at 1 January 2026:

| Days | Source id | CAISO's publication | Address |
|---|---|---|---|
| to 31 December 2025 | `caiso:production_curtailments` | Production and curtailments data, 5-minute, one workbook a period | the library page `https://www.caiso.com/library/production-curtailments-data`; every `/documents/...curtailments-data...xlsx` link on it (12 workbooks in the rows, from `productionandcurtailmentsdata-may1_2014-may31_2017.xlsx` to `production-and-curtailments-data-june-december-2025.xlsx`) |
| from 1 January 2026 | `caiso:daily_renewable_report` | Daily Renewable Report, one HTML page a day | the index `https://www.caiso.com/library/daily-renewable-reports`, its month pages `/library/daily-renewable-reports-<mon>-<yyyy>`, and the day's page `/documents/daily-renewable-report-<mon>-<dd>-<yyyy>.html` |

From a workbook the connector reads the sheet Curtailments (Date, Hour, Interval, Wind Curtailment, Solar Curtailment, and Reason where the sheet has it) and the sheet Production (Date, Solar, Wind). From a report it reads the chart date and the JavaScript arrays `curt_hr_tot_<fuel>_<category>_mwh` (hourly MWh, six categories: economic, self-schedule cut and operator instruction, each local or system) and `tot_gen_<fuel>_iso_telem` (5-minute MW). Connector: `warehouse/connectors/curtailment.py` (session 18, platform tool 22), one of its three tables; the meaning of each figure is in `docs/methods/curtailment.md`. The daily run (`warehouse/run_daily.sh`) runs it without `--history`, so only the reports are read; the workbooks are read with `--history`.

## Vintage and revision

1 May 2014 to 21 October 2026 in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, from the connector's run `20261023T144531Z`. Its header: "This run wrote 100 rows: 8 new, 92 replacing earlier rows". `coverage.csv` gives the same 25,120 rows and dates. The rows' `retrieved_at`: 27 September 2026 (24,830 rows, session 18's history), the rest from the daily runs since.

A daily run reads the reports of the 14 days before today to yesterday (Pacific), and a run with `--history` every workbook and every report from 1 January 2026. `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): a day read again replaces its rows, and the rest is kept. A workbook day on or after 1 January 2026 is not written.

## Shape and variables

Series, 25,120 rows: one entity, `caiso:ISO`, 8 variables, on 4,557 days (every calendar day from 1 May 2014 to 21 October 2026 has a row). `unit` MWh, rounded to 3 decimals; `freq` P1D; `ts_utc` the Pacific operating day at 00:00:00Z; `geo` US-CA; `market`, `node` and `vintage` empty.

| Variable | Days | From | Workbook days | Report days |
|---|---|---|---|---|
| `curtailed_solar_mwh`, `curtailed_wind_mwh` | 4,556 each | 2 May 2014 | 4,262 | 294 |
| `curtailed_solar_local_mwh`, `curtailed_solar_system_mwh`, `curtailed_wind_local_mwh`, `curtailed_wind_system_mwh` | 1,755 each | 1 January 2022 | 1,461 | 294 |
| `solar_generation_mwh`, `wind_generation_mwh` | 4,494 each | 1 May 2014 | 4,262 | 232 |

A workbook's 5-minute MW is 5/60 MWh, summed over the Date column's day; a report's curtailment is the sum of its hourly MWh, and its output the 5-minute telemetry times 5/60. The curtailment is not in the output figures. Curtailment by year, solar and wind in GWh: 1,497.2 and 90.3 in 2020, 3,192.6 and 230.8 in 2024, 3,482.3 and 283.3 in 2025, 4,910.1 and 352.6 in 2026 to 21 October. The largest solar day is 17 May 2026, 98,685 MWh (local 59,942, system 38,743).

## Reading the workbooks and the reports

- Every request is tried up to four times (5, 10 and 15 seconds apart); one that still fails stops the table, and nothing of it is written. A library page with no workbook link stops it too.
- Workbooks: a row whose Date is not a date is passed over; a curtailment cell that is empty or not a number adds nothing. The workbooks overlap (the June to December 2025 file starts on 1 January 2025), so a curtailment interval with the same date, hour, interval, reason and values is counted once, from the first workbook in name order that lists it; the run's log gives the count.
- Every day from the first to the last day with a curtailment row is written, with 0 for a fuel that has no row that day. Where a workbook has a Reason column, every day from its first to its last date gets local and system rows, 0 for a reason with no row.
- A day's output is written from a workbook only with every 5-minute interval of the Pacific day (288, or 276 and 300 at the clock changes) and a number in Solar and Wind in each.
- Reports: a day is taken only from the report whose chart date is that day. Each of the twelve hourly arrays must hold 23, 24 or 25 values, none missing, or no row of the day is written. The output is written only when the telemetry holds every 5-minute interval of the day; otherwise the day's curtailment is written without it and the log says so.
- A month page outside the days asked is not read. 0.3 seconds between the reports and between the month pages.
- No row at all stops the table. No ceiling and no test of the newest day's age. The connector does not consult `warehouse/metadata/paused_sources.csv` (CAISO is not on it).

## License

The header has no license line; `coverage.csv`: public. `license_tables.csv` names CAISO as the table's one publisher (from the source registry); `license_verdicts.csv` gives CAISO "may be public" (read 3 of `license_reads.csv`, 12 October 2026): its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO", with the note that the same page's API terms forbid use "for any other benchmarking or competitive purposes". `docs/licenses.md`: ERW verdict public.

## Cross-checks (session 2060)

- The counts above were computed from the rows, read past the 9 header lines; no (entity, variable, ts_utc) is given twice, every `ts_utc` is a day at 00:00:00Z, and each variable holds every day of its span except the output.
- Local plus system equals the total within 0.002 MWh on 1,665 of 1,755 days for solar and 1,672 for wind. Every other day is in January to March 2022 (90 days for solar, 83 for wind), where local plus system falls short of the total: by 751,278 MWh of solar (2022's total 2,320,258, its parts 1,568,981) and 31,580 MWh of wind.
- Output missing inside its span: 63 days, 9 December 2019 (a workbook day short of intervals, as `docs/methods/curtailment.md` records) and 62 report days of 2026 whose telemetry was not complete (22 of them in July).
- Solar curtailed as a share of solar curtailed plus produced: 5.90% in 2024 and 5.73% in 2025.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The reports' six categories (economic, self-schedule cut, operator instruction): summed here into local and system.
- The 5-minute intervals: those are `caiso_curtailment_intervals`. The monthly sums are `iso_curtailment_monthly`.
- Curtailment by reason before 2022, and output on the 63 days above.
- The header's line and `docs/methods/curtailment.md` say the reason is published from 2024; the rows hold local and system from 1 January 2022, from the 2022 workbook, and in its first three months they do not add up to the total.
