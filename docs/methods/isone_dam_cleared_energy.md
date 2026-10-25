# Demand cleared in the day-ahead market, New England as a whole, an hour (ISO-NE ISO Express, hourlydayaheaddemand)

Energy Research Warehouse (ERW), method note written in session 2110 (chain 069) for a table first written on 6 October 2026 (session 136).

Tables: `isone_dam_cleared_energy`

## Publisher and address

ISO New England (ISO-NE), ISO Express report "Day-Ahead Hourly Cleared Demand", system-wide, at most fifteen days a request:

`https://www.iso-ne.com/transform/csv/hourlydayaheaddemand?start=<YYYYMMDD>&end=<YYYYMMDD>`

The file's lines are "C" (comments), two "H" lines (`"H","Date","Hour Ending","Day-Ahead Cleared Demand"` and the unit line ending "MWh") and "D" (data). The connector's docstring: the address answers HTTP 403 to a plain request and answers a session that has first opened one of ISO Express's report pages (an anonymous cookie, no account), and ISO Express's own page puts a CAPTCHA on its search of past dates. The connector opens the report's page, `https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/dmnd-da-hourly-cleared`, once a run, with the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)", and asks in that session. Source id `isone:hourlydayaheaddemand`. Connector: `warehouse/connectors/isone_dam_cleared.py` (session 136), its only table, with the frame it shares with the other day-ahead cleared connectors in `warehouse/connectors/dam_cleared.py`.

It is run once a week, on Saturday (UTC), by `warehouse/refresh_supply.sh`, which `warehouse/run_daily.sh` calls (`SUPPLY=1` forces it on another day), under `warehouse/health.py` and a pull budget of 15 minutes (`warehouse/pull_budget.py`). The last run `run_status.csv` records is `20261010T150011Z` (10 October 2026, on GitHub): "360 hours; 360 rows read". The first date is from the rows: the earliest `retrieved_at` is 6 October 2026 20:22:40 UTC; session 136's report gives no date of its own, and records 888 hours from September 2026 in three requests and a refresh of 384.

## Vintage and revision

Eastern days 1 September to 10 October 2026 (1 September 2026 04:00 UTC to 11 October 2026 03:00 UTC) in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261020T011604Z-github`, with the header of the connector's run `20261010T150011Z`: "Hours written by this run: 360, 2026-09-26T04:00:00Z to 2026-10-11T03:00:00Z." The rows' `retrieved_at` are 6 October 2026 (576 rows), 9 October (24) and 10 October (360), from five addresses (1 to 15 September, 360 hours; 16 to 30 September, 144; 22 September to 6 October, 72; 25 September to 9 October, 24; 26 September to 10 October, 360). `coverage.csv` gives the same 960 rows and dates.

A run asks every Eastern day from 14 days back (`--days`, default 14) to tomorrow, in requests of fifteen days, oldest first; the run of 10 October asked to 11 October and was answered through 10 October. Nothing is read from a kept file: every run asks ISO-NE again (each answer is kept by the raw store in `warehouse/raw/isone_dam_cleared/`). `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): an hour asked again replaces the held one, and the table grows past the window a run asks for. The rebuild from the archive keeps a row's `retrieved_at` from the run that first archived its values, so an hour re-read with the same value keeps its earlier date.

## Shape and variables

Series, 960 rows, one entity. `entity` `isone:system`; `variable` `dam_cleared_energy`; `value` ISO-NE's Day-Ahead Cleared Demand for the hour, MWh, as printed (every value a whole number); `unit` MWh; `freq` PT1H; `ts_utc` the hour's start, from the Date and Hour Ending (Eastern) less one hour; `market` `isone_dam`; `geo` US-CT,US-MA,US-ME,US-NH,US-RI,US-VT; `node` `Day-Ahead Cleared Demand` (the column read); `vintage` empty.

| Entity | Variable | Hours | Mean MWh | Lowest | Highest |
|---|---|---|---|---|---|
| `isone:system` | `dam_cleared_energy` | 960 | 11,729 | 7,448 (6 October 2026, 15:00 UTC) | 18,508 (10 September 2026, 22:00 UTC) |

Every one of the 40 Eastern days holds 24 hours; no clock change falls in the window.

## Reading ISO Express

- The first "H" line must be H, Date, Hour Ending, Day-Ahead Cleared Demand, and the second "H" line must end in MWh, or the run stops and nothing is written.
- An answer that is not HTTP 200 with a CSV content type is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.with_retries`; no retry once the pull budget has passed), and then the run stops and nothing is written. An HTTP 404 is not treated apart. The cookie page is asked once; its answer is not checked.
- The hour. Hour ending "02X" is the second 01:00 to 02:00 hour of the autumn clock change (standard time); an hour ending that names a clock time the spring day never had stops the run.
- A blank value gives no hour. A value that is not a number stops the run.
- An hour a file gives twice: the later line replaces the earlier without a word (the hours are held by their start). The frame's test for an hour given twice can fire only across requests, and a run's requests do not overlap.
- No hour at all stops the run. A newest hour more than 5 days old stops it, and nothing is written.
- Ceiling: 2,000 rows read from ISO-NE in a run by default (`--ceiling`), every "D" line counted, blank or not. Past it the run stops and writes nothing. A run of 14 days asks for 16 days, 384 lines.
- Three seconds after each request. ISO-NE is checked against `warehouse/metadata/paused_sources.csv` before any request (it is not paused); a paused publisher is a skipped status row and no request.

## License

The header: "License: internal. ISO-NE's legal notice: "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws" (https://www.iso-ne.com/legal-privacy, read 6 October 2026). Not published, in no public dataset and no download." `coverage.csv`: internal. `license_tables.csv` names ISO-NE as the table's one publisher (from the source registry); `license_verdicts.csv` gives ISO-NE "needs written permission" (read 4 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict internal.

## Cross-checks (session 2110)

- The counts above were computed from the rows, read past the 13 header lines; no hour is given twice.
- Hours complete: from 1 September 2026 04:00 to 11 October 2026 03:00 UTC there are 960 hours, and the table holds every one.
- No hour is shared with ISO-NE's real-time demand in `isone_zone_load_hourly`, which ends on 31 August 2026 (Eastern), so the two cannot be set against each other from the rows held.
- Against the Internal Hub's day-ahead price in `isone_dam_zone_prices` over the 960 hours both hold, the correlation is 0.818. The connector does not compare them.
- Session 136's report: the five operators' totals are not the same measure (NYISO's and SPP's include cleared virtual bids; CAISO's and ISO-NE's are cleared demand), and are not to be added or ranked.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Cleared demand by load zone: the report is system-wide. Real-time demand by zone is `isone_zone_load_hourly`.
- The real-time market: day-ahead only.
- Days before 1 September 2026: past years are never walked (the CAPTCHA on ISO Express's own search, the connector's docstring).
- Days after 10 October 2026: no run since 10 October is recorded.
