# Real-time LMPs, the eight load zones and the Internal Hub, 15-minute means of five-minute prices (ISO-NE)

Energy Research Warehouse (ERW), method note written in session 2110 (chain 069) for a table first written on 25 September 2026 (session 3).

Tables: `isone_rtm_zone_prices`

## Publisher and address

ISO New England (ISO-NE), five-minute real-time LMPs, named by the connector "Real-Time Energy Market Five-Minute LMPs" with the report page `https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-five-min-final`, read through gridstatus 0.36.0 (`ISONE.get_lmp`, market REAL_TIME_5_MIN). For a past day gridstatus reads six files of four hours each:

`https://www.iso-ne.com/static-transform/csv/histRpts/5min-rt-prelim/lmp_5min_<YYYYMMDD>_<00-04|04-08|08-12|12-16|16-20|20-24>.csv`

A run's window never holds today, so gridstatus's request for today's rolling interval is not made. Since a day comes from six files, every row's `source_url` is the report page, and the run log names each file; `vintage` is empty. Source id `isone:rt_lmp_5min`. Connector: `warehouse/connectors/iso_prices.py` (`pull_isone`, the spec RTM), which writes `isone_dam_zone_prices` and `isone_rtm_zone_prices_hourly` in the same run.

It is run every day by `warehouse/run_daily.sh` (`iso_prices.py isone --days "$DAYS"`, `DAYS` 3 by default), which the daily workflow `.github/workflows/daily-prices.yml` runs, under a pull budget of 15 minutes (`warehouse/pull_budget.py`). The first date is session 3's report (run 2026-09-25 UTC): `isone_rtm_zone_prices.csv` "is new", 2,592 rows, 9 nodes by 288 quarter hours of 22 to 24 September; session 2 had not written it. Those rows have all been replaced: the earliest `retrieved_at` in the rows is 26 September 2026 23:33:09 UTC.

## Vintage and revision

Eastern operating days 27 August to 22 October 2026 (27 August 2026 04:00 UTC to 23 October 2026 03:45 UTC), 47 of those 57 days, in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, with the header of the connector's run `20261023T143058Z`: "this run wrote 2 complete days of 3; days not written keep any rows from earlier runs: 2026-10-20 (day incomplete: .H.INTERNAL_HUB: 88 rows, expected 96, missing 8 ...". `coverage.csv` gives the same 40,608 rows and dates (last run 2026-10-23T14:30:58Z). The rows' `retrieved_at` fall on 22 days from 26 September to 23 October 2026; 19,008 rows (22 days) carry 26 September 2026.

A run asks for the three complete Eastern days before today, one day at a time (`run_market_per_day`, session 13). A day whole at every node replaces its rows; a day that is not whole is not written, any rows an earlier run wrote for it are kept, and it is a gap row of `warehouse/metadata/run_status.csv`. Every request goes to ISO-NE (each answer is kept under `warehouse/raw/isone/<run_id>/`). `ip.write_csv` merges on (entity, variable, ts_utc), so the table grows past the window. A day leaves the window after three runs, so a day ISO-NE completes later is not read again. The rebuild from the archive keeps a row's `retrieved_at` from the run that first archived its values, which is why most days carry the date of the run after them.

The ten days missing: 2, 11, 12, 13, 15 and 25 September, 1, 14, 15 and 20 October 2026. `run_status.csv` holds gap rows for eight of them (2 to 25 September from run `20260926T155920Z`, 1 October from `20261004T141143Z`, 20 October from the runs of 21, 22 and 23 October), each short of one to eight quarter hours. For 14 and 15 October it holds no gap row: the daily runs it records go from 14 October (`20261014T142656Z`) to 20 October (`20261020T002541Z`), and none of them held those two days in its window.

## Shape and variables

Series, 40,608 rows: nine entities of 4,512 quarter hours each (47 Eastern days of 96). `entity` `isone:<node>`; `variable` `lmp_rtm_15m_mean`; `value` the mean of the quarter hour's three five-minute LMPs, time-weighted, to four decimals; `unit` USD/MWh; `freq` PT15M; `ts_utc` the quarter hour's start in UTC; `market` `isone_rtm`; `geo` US-CT,US-MA,US-ME,US-NH,US-RI,US-VT; `node` the node's ISO-NE name.

| Node | Quarter hours | Mean USD/MWh | Lowest | Highest | Below 0 |
|---|---|---|---|---|---|
| `.H.INTERNAL_HUB` | 4,512 | 38.78 | -51.30 (5 October 2026, 20:00 UTC) | 132.57 (7 October 2026, 11:15 UTC) | 31 |
| `.Z.CONNECTICUT` | 4,512 | 38.21 | -51.53 (5 October, 20:00) | 131.63 (7 October, 11:15) | 31 |
| `.Z.MAINE` | 4,512 | 35.88 | -72.35 (31 August 2026, 14:00 UTC) | 128.46 (7 October, 11:15) | 59 |
| `.Z.NEMASSBOST` | 4,512 | 39.03 | -51.79 (5 October, 20:00) | 133.48 (7 October, 11:15) | 31 |
| `.Z.NEWHAMPSHIRE` | 4,512 | 38.54 | -51.41 (5 October, 20:00) | 133.14 (7 October, 11:15) | 32 |
| `.Z.RHODEISLAND` | 4,512 | 38.28 | -50.91 (5 October, 20:00) | 131.73 (7 October, 11:15) | 31 |
| `.Z.SEMASS` | 4,512 | 38.95 | -51.60 (5 October, 20:00) | 133.35 (7 October, 11:15) | 31 |
| `.Z.VERMONT` | 4,512 | 39.19 | -52.18 (5 October, 20:00) | 134.84 (7 October, 11:15) | 31 |
| `.Z.WCMASS` | 4,512 | 38.87 | -51.49 (5 October, 20:00) | 133.34 (7 October, 11:15) | 31 |

The Hub's 31 negative quarter hours fall on 5 days; Maine's 59 on 9 days, from 31 August (16) to 10 October 2026.

## Reading ISO-NE

- gridstatus reads each of a day's six files and, when one fails to load, logs it and goes on without it; the day is then short, and the completeness rule below leaves it out. A day whose reading raises (no file at all, for example) is tried four times by the connector, 5, 10 and 15 seconds apart (`iso_prices.with_retries`; no retry once the pull budget has passed), and is then a gap, not a failure of the table.
- Kept: the nine nodes of `ISONE_NODES`; the rest of each file is read and not written.
- Every five-minute row must be five minutes long, or the day is not written. A quarter hour is kept only when its intervals cover all 900 seconds without crossing its end; its value is the time-weighted mean, which with three regular intervals is the plain mean.
- Per-day completeness: a day is written only when every node holds all 96 quarter hours of it exactly once; otherwise the day is a gap row with the reason. No day complete in the window fails the market.
- Where two files give the same (node, interval), one is kept (the latest by `vintage`, which is empty here, so the last read) and a difference over 0.005 USD/MWh is logged.
- No ceiling of rows and no test of age. ISO-NE is checked against `warehouse/metadata/paused_sources.csv` before any request (it is not paused). A pull still unanswered at its 15-minute budget is a skip (exit 75), with its tables as gap rows.

## License

The header carries no license line. `coverage.csv`: public; the source registry: public. `license_tables.csv` names ISO-NE as the table's one publisher (from the source registry); `license_verdicts.csv` gives ISO-NE "needs written permission" (read 4 of `license_reads.csv`, 12 October 2026). `license_status.csv`: "license needed" from 2026-10-21. `docs/licenses.md`: "ruled: license needed from 2026-10-21"; ERW verdict unsettled.

## Cross-checks (session 2110)

- The counts above were computed from the rows, read past the 12 header lines; no (entity, variable, ts_utc) is given twice. Every held day holds 96 quarter hours at every node, and every `ts_utc` falls on :00, :15, :30 or :45.
- Against `isone_dam_zone_prices` at the Hub, over the 1,128 hours whose four quarter hours this table holds: real-time mean 38.78, day-ahead mean 41.33 USD/MWh; real-time above day-ahead in 385 hours; correlation 0.632.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Ten days of the 57 (above), and days before 27 August 2026.
- The five-minute prices themselves: only their 15-minute means. ISO-NE's own hourly real-time prices, final where posted, are `isone_rtm_zone_prices_hourly`.
- ISO-NE's other pricing nodes, and the price components.

## Found while writing this note

- The rows are ISO-NE's preliminary five-minute prices: gridstatus 0.36.0 reads `histRpts/5min-rt-prelim/lmp_5min_<date>_<hours>.csv`. The connector cites them to the final five-minute report's page (`lmps-rt-five-min-final`), as its report name and `source_url` say, and the source registry carries the same page.
- The header line from `FIVE_MIN_NOTE` says "A quarter hour missing any 5-minute price is incomplete and fails the file", and `iso_prices.py`'s docstring says "a market's file is written only if every node has every interval in the window". Since session 13 this market is checked per day: a short day is left out and the rest of the window is written (the same header's next line says so).
