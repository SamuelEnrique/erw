# EIA-930's hourly demand and net generation for the seven ISO balancing authorities, January to June 2018, from EIA's six-month file

Energy Research Warehouse (ERW), method note written in session 2284 (chain 104) for a table first written on 1 October 2026 (session 49, `archive/sessions/SESSION_49_REPORT.md`, "d. EIA-930 six-month file, 2018 January to June", an approved pull; commits `79ac2b10` and `88cb0a83`). Its one use is the 728-day baseline of COVID-19 in `event_window_daily` (`docs/methods/events.md`, "Session 49"; `docs/methods/event_study.md`).

Tables: `eia930_all_history`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor), the six-month balance file `https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2018_Jan_Jun.csv` (Last-Modified Wed, 30 Sep 2026 14:39:43 GMT), listed from `https://www.eia.gov/electricity/gridmonitor/about`. One file, one request. Source id `eia:gridmonitor/sixMonthFiles` (`warehouse/metadata/sources.csv`, first and last seen 2026-10-01). Raw copy under `warehouse/raw/eia930_history/<run>/` (not on this machine).

Connector: `warehouse/connectors/eia930_history.py` (session 49), `--file EIA930_BALANCE_2018_Jan_Jun.csv [--from-raw]`, ceiling 100,000 rows. It keeps the rows of CISO, ERCO, ISNE, MISO, NYIS, PJM and SWPP ("US48 is not a balancing authority in these files") and the columns "UTC Time at End of Hour", "Demand (MW) (Adjusted)" and "Net Generation (MW) (Adjusted)"; `ts_utc` is the end of the hour less one hour; a value that is not a number is not written, and the count of such values goes into the header.

Schedule: **none**. The table was written once from the approved file; no step of `warehouse/run_daily.sh`, `run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh`, `refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names the connector, and the Redivis restore list does not name the table. `run_status.csv` has no row of it. `archive_manifest.csv`: 60,084 rows as of run `20261004T023527Z-local`. Not in the Supabase live set (no pattern of `live_set.yaml` names it). Readers: `warehouse/derived/event_window.py` (`build_covid`), `warehouse/analysis/watch.py`, `warehouse/metadata/build_coverage.py`.

## Vintage and revision

One run, `20261001T035016Z`; the file was downloaded at 2026-10-01T03:48:41Z (`retrieved_at` in every row), and `vintage` is the file's Last-Modified, 2026-09-30T14:39:43Z, in every row: EIA rewrote its 2018 file eight years on, so the values are EIA's as of that date. "This run wrote 60084 rows: 60084 new". The copy here was restored from the Redivis draft by `scripts/sync.py` (header line 11). Nothing asks EIA again; a later revision of the file would reach the table only if someone ran the connector.

## Shape and variables

Series, 60,084 rows, 14 columns (the series columns and `ba`). Two variables: `demand_mw` 30,402 rows and `net_generation_mw` 29,682, unit MW, `freq` PT1H; entity `eia930:<BA>`; `geo` the BA's states; `market` and `node` blank. Seven entities, `ts_utc` from 2018-01-01T05:00:00Z to 2018-07-01T06:00:00Z.

| ba | First hour | Last hour | Hours | Demand mean | Lowest | Highest | Net generation mean | Net generation over demand | Demand, TWh |
|---|---|---|---|---|---|---|---|---|---|
| ciso | 2018-01-01T08 | 2018-07-01T06 | 4,343 | 24,128 | 18,068 | 37,598 | 17,012 | 0.705 | 104.79 |
| erco | 2018-01-01T06 | 2018-07-01T04 | 4,343 | 41,558 | 27,371 | 69,039 | 41,627 | 1.002 | 180.49 |
| isne | 2018-01-01T05 | 2018-07-01T03 | 4,343 | 13,488 | 9,331 | 20,822 | 11,196 | 0.830 | 58.58 |
| miso | 2018-01-01T05 | 2018-07-01T04 | 4,344 | 75,409 | 52,844 | 119,733 | 71,431 | 0.947 | 327.58 |
| nyis | 2018-01-01T05 | 2018-07-01T03 | 4,343 | 17,604 | 12,077 | 28,166 | 14,340 | 0.815 | 76.46 |
| pjm | 2018-01-01T05 | 2018-07-01T03 | 4,343 | 92,249 | 62,804 | 149,170 | 93,293 | 1.011 | 400.64 |
| swpp | 2018-01-01T06 | 2018-07-01T04 | 4,343 | 30,528 | 21,243 | 49,194 | 29,813 | 1.011 | 132.58 |

MW (EIA's MWh in the hour). SWPP's net generation has 3,623 hours and its ratio is over those hours.

- **SWPP's net generation ends at 2018-06-01T04:00:00Z.** Its 720 later hours are empty in EIA's Adjusted column, which is the header's "720 BA-hour values were empty". No other value is missing.
- **SWPP's demand is 30,344 MW for 81 hours running,** from 2018-01-09T21:00:00Z: one value in EIA's Adjusted column for three and a half days. No other series repeats a value for more than two hours.
- No value is zero or negative.

## Placing values in time, and what is filled

`ts_utc` is the start of the hour in UTC. The file runs from local midnight on 1 January to the last hour of 30 June in each BA's own time: CISO's first hour is 08:00Z (Pacific), ERCO's and SWPP's 06:00Z (Central), the others' 05:00Z (Eastern). MISO keeps Eastern Standard Time all year and so has 4,344 hours; the others lose the hour of the spring clock change and have 4,343. Nothing is filled: an empty value has no row.

## License

Header: "License: public (U.S. Energy Information Administration)." The docstring: "The file is public (EIA, U.S. Government data)." `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", "may be public". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2284)

The figures in this note were computed from the rows of `warehouse/output/eia930_all_history.csv`, read past its 11 header lines (counted), with `runs/c104/s2284/profile.py` and `check_history.py` (outputs beside them).

- 60,084 rows and the range 2018-01-01T05:00:00Z to 2018-07-01T06:00:00Z, as header line 10 states; 720 empty values, as header line 8 states (60,084 plus 720 is two variables for every hour of the seven BAs). No (entity, variable, ts_utc) twice; no blank value; one unit; one `source_url`, `retrieved_at` and `vintage` in every row, as the code writes them.
- Every BA has every hour from its first to its last for both variables, except SWPP's net generation after 1 June.
- **Against ERCOT's own load** (`ercot_zone_load_hourly`, ERCOT's native load files, entity `ercot:system`): over 4,343 hours ERCO's `demand_mw` differs from ERCOT's load by 130.0 MW on average, against 1,396.6 and 1,374.6 MW with EIA's hour moved an hour either way; the median ratio is 1.0025 (5th percentile 0.9989, 95th 1.0083); 180.485 TWh against 180.009. The hour-start reading holds.

## Where the description and the data disagree

1. **"A BA-day missing any hour is counted in run_status."** The docstring says so; the code writes no such row (its one status line is the run's, `ok` with the count of empty values), and `run_status.csv` holds no row of `eia930_history` at all. SWPP's 30 days without net generation are recorded only in the header's count and the run log.
2. **When the workbooks begin.** The docstring says "the hourly extracts of the BA workbooks begin 2018-06-30"; `docs/methods/events.md` says "EIA's workbooks start 2018-07-01"; `eia930_all_emissions`, read from those workbooks, begins at 2018-07-02T00:00:00Z (`coverage.csv`). Not settled here: the workbooks are not on this machine. This table ends at 2018-07-01T06:00:00Z.

Not acted on: this note changes no file but itself. SWPP's flat 81 hours are EIA's Adjusted values, recorded, not changed.

Recorded, not changed in session 2284: the docstring's run_status rows that the code does not write, and the three dates for EIA's first workbook, are for the connector's next change.

## The session report against the table

`SESSION_49_REPORT.md`: "60,084 of the 100,000 ceiling"; "seven ISO BAs, demand and net generation, the Adjusted columns"; "US48 is not a balancing authority in that file, so seven": all hold. The report's figures for `event_window_daily` (275 or 276 days for the seven BAs) are that table's and are not checked here.

## What it does not hold

- July 2018 on (the hourly tables and EIA's workbooks; `eia930_daily_demand` from 2019); any year before 2018; US48; EIA's as-submitted columns ("Demand (MW)" before adjustment) and its forecast, interchange and fuel columns; SWPP's net generation from 1 June 2018.
