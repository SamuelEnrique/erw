# Day-ahead LMPs, the eight load zones and the Internal Hub, an hour (ISO-NE, Day-Ahead Energy Market Hourly LMPs)

Energy Research Warehouse (ERW), method note written in session 2110 (chain 069) for a table first written on 25 September 2026 (session 2).

Tables: `isone_dam_zone_prices`

## Publisher and address

ISO New England (ISO-NE), report "Day-Ahead Energy Market Hourly LMPs", one file an Eastern operating day, read through gridstatus 0.36.0 (`ISONE.get_lmp`, market DAY_AHEAD_HOURLY):

`https://www.iso-ne.com/static-transform/csv/histRpts/da-lmp/WW_DALMP_ISO_<YYYYMMDD>.csv`

gridstatus asks for it in a session that has first opened `https://www.iso-ne.com/isoexpress/web/reports/operations/-/tree/gen-fuel-mix` (ISO-NE's cookie). ISO-NE answers the file at `https://www.iso-ne.com/histRpts/da-lmp/WW_DALMP_ISO_<YYYYMMDD>.csv`, the address every row's `source_url` keeps; `vintage` is that file's HTTP Last-Modified. Report page `https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-da-hourly`. Source id `isone:da_lmp_hourly`. Connector: `warehouse/connectors/iso_prices.py` (`pull_isone`, the spec DAM), which writes `isone_rtm_zone_prices` and `isone_rtm_zone_prices_hourly` in the same run.

It is run every day by `warehouse/run_daily.sh` (`iso_prices.py isone --days "$DAYS"`, `DAYS` 3 by default; `isone` is in its list `ISOS`), which the daily workflow `.github/workflows/daily-prices.yml` runs, under a pull budget of 15 minutes (`warehouse/pull_budget.py`). The first date is session 2's report (run 2026-09-25 UTC): `isone_dam_zone_prices.csv`, 6,696 rows, "08-26 to 09-24, plus forward 09-25". The earliest `retrieved_at` in the rows is 25 September 2026 19:37:11 UTC (the 216 rows of 26 August).

## Vintage and revision

Eastern operating days 26 August to 23 October 2026 (26 August 2026 04:00 UTC to 24 October 2026 03:00 UTC) in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, with the header of the connector's run `20261023T143058Z`: "Window: ISO-NE operating days 2026-10-20 to 2026-10-22 ... Forward DAM days also included (published before retrieval): 2026-10-23". `coverage.csv` gives the same 12,744 rows and dates (last run 2026-10-23T14:30:58Z). The 59 days come from 59 files, each last modified on the Eastern day before the day it prices, between 12:12 and 15:01 Eastern (from 25 August 2026 16:42:05 UTC to 22 October 2026 17:27:27 UTC). The rows' `retrieved_at` fall on 24 days from 25 September to 23 October 2026; 5,832 rows (27 days) carry 26 September 2026.

A run asks for the three complete Eastern days before today, and for every later day up to tomorrow as a forward day, written only when ISO-NE has published it whole. Every request goes to ISO-NE (each answer is kept under `warehouse/raw/isone/<run_id>/` with a manifest). Where two files give the same (node, hour), the latest published wins, and a difference over 0.005 USD/MWh is logged. `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): a day read again replaces its rows, and the table grows past the window. A day is read again by later runs (as a forward day, then in up to three windows); the rebuild from the archive keeps a row's `retrieved_at` from the run that first archived its values, which is why most days carry the date they were first read as a forward day.

## Shape and variables

Series, 12,744 rows: nine entities of 1,416 hours each (59 Eastern days of 24 hours; no clock change falls in them). `entity` `isone:<node>`; `variable` `lmp_dam`; `value` the locational marginal price as ISO-NE prints it; `unit` USD/MWh; `freq` PT1H; `ts_utc` the hour's start in UTC (gridstatus's reading of the file's hour ending, Eastern); `market` `isone_dam`; `geo` US-CT,US-MA,US-ME,US-NH,US-RI,US-VT; `node` the node's ISO-NE name.

| Node | Hours | Mean USD/MWh | Lowest | Highest |
|---|---|---|---|---|
| `.H.INTERNAL_HUB` | 1,416 | 41.24 | 4.37 | 88.02 |
| `.Z.CONNECTICUT` | 1,416 | 40.53 | 4.35 | 93.67 |
| `.Z.MAINE` | 1,416 | 38.67 | 4.07 | 84.22 |
| `.Z.NEMASSBOST` | 1,416 | 41.54 | 4.37 | 88.57 |
| `.Z.NEWHAMPSHIRE` | 1,416 | 41.05 | 4.32 | 87.33 |
| `.Z.RHODEISLAND` | 1,416 | 40.71 | 4.34 | 86.83 |
| `.Z.SEMASS` | 1,416 | 41.40 | 4.38 | 88.92 |
| `.Z.VERMONT` | 1,416 | 41.66 | 4.45 | 86.25 |
| `.Z.WCMASS` | 1,416 | 41.30 | 4.38 | 87.82 |

Every node's lowest hour is 6 October 2026, 06:00 UTC, and every node's highest is 18 October 2026, 22:00 UTC. No price is at or below 0.

## Reading ISO-NE

- Each window day's file is fetched by gridstatus (its own three tries, HTTP 200 and a CSV content type required) inside the connector's four tries, 5, 10 and 15 seconds apart (`iso_prices.with_retries`; no retry once the pull budget has passed). A window day that still fails fails the market: nothing is written for DAM, and the run's status says failed. A forward day is tried once; a day not yet published is logged and left out.
- Kept: the nine nodes of `ISONE_NODES`. The rest of the file is read and not written.
- Every row must be an interval of 60 minutes, or the market stops.
- Strict completeness over the whole window (`run_market`): every node must hold every hour of the three days exactly once, or nothing is written for DAM. A forward day is added only when all nine nodes hold all its hours.
- No ceiling of rows and no test of the newest day's age beyond the window. ISO-NE is checked against `warehouse/metadata/paused_sources.csv` before any request (it is not paused); a paused publisher gets a skipped status row and no request. A pull still unanswered at its 15-minute budget is a skip (exit 75), with its tables as gap rows.

## License

The header carries no license line. `coverage.csv`: public; the source registry: public. `license_tables.csv` names ISO-NE as the table's one publisher (from the source registry); `license_verdicts.csv` gives ISO-NE "needs written permission" (read 4 of `license_reads.csv`, 12 October 2026). `license_status.csv`: "license needed" from 2026-10-21, "flagged public; the publisher's sentence read in session 205 asks for it". `docs/licenses.md`: "ruled: license needed from 2026-10-21"; ERW verdict unsettled. The ERW's other ISO-NE tables, under the same sentence, are internal; session 85's report left that difference open.

## Cross-checks (session 2110)

- The counts above were computed from the rows, read past the 11 header lines; no (entity, variable, ts_utc) is given twice.
- Hours complete: every one of the 531 (node, Eastern day) groups holds 24 hours, and no day from 26 August to 23 October 2026 is missing.
- The zones against the Hub, mean over the same hours: Maine 2.58 USD/MWh below, Connecticut 0.71 below, Rhode Island 0.53 below, New Hampshire 0.19 below, WCMASS 0.06 above, SEMASS 0.15 above, NEMASSBOST 0.30 above, Vermont 0.42 above.
- Against the real-time 15-minute means of `isone_rtm_zone_prices` at the Hub, over the 1,128 hours whose four quarter hours that table holds: day-ahead mean 41.33, real-time mean 38.78 USD/MWh; real-time above day-ahead in 385 hours; correlation 0.632.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- ISO-NE's other pricing nodes, and the energy, congestion and loss components gridstatus returns with the price.
- Days before 26 August 2026 (session 2's first 30-day window). ISO-NE's load zones from 2019 are in `isone_zone_prices_history` (internal, `warehouse/connectors/zone_price_history.py`).
- The real-time market: `isone_rtm_zone_prices` (15-minute means of five-minute prices) and `isone_rtm_zone_prices_hourly` (ISO-NE's hourly prices).
