# SPP's demand cleared in the day-ahead market, an hour, from September 2025 (SPP Marketplace portal, Market Clearing, DA-MC files, Total Demand)

Energy Research Warehouse (ERW), method note written in session 2180 (chain 097) for a table first written on 6 October 2026 (session 136).

Tables: `spp_dam_cleared_energy`

## Publisher and address

Southwest Power Pool (SPP), the Marketplace portal's public file browser, folder "Market Clearing", the day-ahead file of each operating day (`https://portal.spp.org/pages/market-clearing`, named in the header and not asked):

`https://portal.spp.org/file-browser-api/download/market-clearing?path=/<YYYY>/<MM>/DA-MC-<YYYYMMDD>0100.csv`

One CSV a day, a row an hour for each balancing authority area (BAA) it names, with the column "Total Demand" among others. The connector sends the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)". No reading of portal.spp.org's robots file is recorded in `warehouse/metadata/license_reads.csv`; this note made no request.

Source id `spp:DA-MC:cleared` (in `sources.csv`, license public, first seen 2026-10-06, last seen 2026-10-10). Connector: `warehouse/connectors/spp_dam_cleared.py` (session 136), its only table, on the frame the five day-ahead cleared energy connectors share, `warehouse/connectors/dam_cleared.py`. The same files are read for the reserve quantities by `warehouse/connectors/spp_as_quantities.py` (session 100), and a day whose file either connector kept on the machine is read from `warehouse/raw/` without a request. The method of the page row is `docs/methods/supply_and_trade.md` ("Day-ahead energy cleared"). `warehouse/supabase/live_set.yaml` holds the table out of the live catalogue (`catalogue_hold`, session 136: "nothing reads them from Supabase").

Schedule: `warehouse/refresh_supply.sh` runs the connector (step `spp_dam_cleared`, under `warehouse/health.py run` and a pull budget of 15 minutes, `warehouse/pull_budget.py`), after `ercot`, `caiso`, `nyiso` and `isone`. `warehouse/run_daily.sh` calls that script on Saturdays (UTC) only, or on any day with `SUPPLY=1`, and `.github/workflows/daily-prices.yml` runs `run_daily.sh` on GitHub's runner. `warehouse/metadata/run_status.csv` holds one run: `20261010T150020Z` on GitHub, ok.

A run asks for the days from 14 days before today (Central) to tomorrow, newest first: 16 files by default (`--days`). Two seconds after each request. A day SPP has not posted (HTTP 404) is not written.

## Vintage and revision

Central days 1 September 2025 to 10 October 2026 (`ts_utc` 2025-09-01T05:00:00Z to 2026-10-11T04:00:00Z), in the file on the data machine, restored from the Redivis draft by `scripts/sync.py` (its last header line), with the header of run `20261010T150020Z`: "Rows read from the operator in this run: 720 (this run's ceiling 5,000). Hours written by this run: 720, 2026-09-26T05:00:00Z to 2026-10-11T04:00:00Z", and "720 rows: 144 new, 576 replacing earlier rows ...; 13632 rows are kept from earlier runs". `vintage` is empty. `coverage.csv` gives the same 14,352 rows, the same first and last `ts_utc`, one node, and last run 2026-10-10T15:00:20Z.

`retrieved_at` is the time the file was first downloaded, by whichever connector kept it: 13,632 rows carry 4 October 2026, 11:40:59Z to 11:50:32Z (390 daily files that `spp_as_quantities.py` saved in session 100; hours to 2026-09-26T04:00:00Z), and 720 rows 10 October 2026, 15:00:28Z to 15:01:12Z (15 files the run of 10 October asked of SPP on GitHub's runner). So the earliest `retrieved_at` is older than the table: the first date above is from the commit that added the connector (`f1ae6e5f`, 6 October 2026, 20:45 UTC), from session 136's report (14,208 hours from September 2025, "three daily files" read from SPP, "the other 14,064 hours were read from files the reserve-quantity connector already kept on this machine") and from `sources.csv`.

Each run merges its rows into the held file on (entity, variable, ts_utc) (`ip.write_csv`), so the table grows past the connector's window. A file kept in `warehouse/raw/` is never asked again, so a file SPP revises after it was kept is not read again on the machine that keeps it; the GitHub runner keeps no raw file and asks for its 16 days each run.

## Shape and variables

Series, 14,352 rows, two entities, one variable. `variable` `dam_cleared_energy`; `value` the file's "Total Demand" for the hour and the area; `unit` MW (MW over the hour, so a value is also the hour's MWh); `freq` PT1H; `ts_utc` the file's `GMTIntervalEnd` less one hour, the start of the hour; `geo` "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY" in every row; `market` spp_dam; `node` "Total Demand", the column read; `source` `spp:DA-MC:cleared`; `source_url` the day's file (405 files); `vintage` empty. There are no `x_` columns.

| `entity` | Hours | First and last Central day | Mean MW | Lowest MW | Highest MW |
|---|---|---|---|---|---|
| `spp:SPP` | 9,720 | 1 September 2025 to 10 October 2026 (405 days) | 38,252.3 | 26,722.7 (2025-09-07T09:00:00Z) | 61,332.1 (2026-09-03T22:00:00Z) |
| `spp:SWPW` | 4,632 | 1 April 2026 to 10 October 2026 (193 days) | 3,143.7 | 1,934.3 (2026-05-13T09:00:00Z) | 5,071.9 (2026-07-20T23:00:00Z) |

A file from before 1 April 2026 has no BAA column; its one row an hour is written as `spp:SPP`. From 1 April 2026 the file names two areas, SPP and SWPW, and each is a row; the file does not say what SWPW stands for (`spp_as_quantities.py`'s docstring; `spp_dam_cleared.py`'s calls it "the western area"). Session 136 kept the two apart because, added together, the year-on-year change read +8.5 percent, which was the new area and not demand (its report). `docs/methods/supply_and_trade.md` says Total Demand "is the sum of its three cleared bid columns, the virtual one among them", so the figure is not load.

Both entities hold every hour of their spans: no hour is missing, and each Central day has 24 hours except 2 November 2025 (25) and 8 March 2026 (23) for `spp:SPP`. No (entity, variable, ts_utc) is given twice, and no value is 0 or negative. The counts in this note were computed in session 2180 with pandas from the rows of `warehouse/output/spp_dam_cleared_energy.csv`, read past its 12 header lines.

## Checks the connector makes

- Before any request, `dam_cleared.run` asks `iso_prices.paused("spp")`; a paused publisher gets no request, and the run writes a "skipped" status and nothing else. SPP is not in `warehouse/metadata/paused_sources.csv`. `paused_host()` is not asked (the host is fixed in the code).
- A file must hold the columns `GMTIntervalEnd` and `Total Demand`, or the run stops. Every BAA the file names is written as `spp:<BAA>`.
- A cell that does not read as a number gives no row. Nothing is filled, summed across hours or estimated.
- An (entity, variable, ts_utc) given twice in the run's rows stops the run, and nothing is written.
- The newest hour must be at most 5 days old, or nothing is written.
- No complete-day rule: a file short of hours is written with the hours it has.
- Ceiling: 5,000 rows read from SPP in a run (the rows of each file fetched, not of files read from `warehouse/raw/`); past it the run stops and writes nothing (`--ceiling` changes it). The run of 10 October read 720.
- Each file is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.fetch_raw` and `with_retries`), with no retry once the pull budget has passed; HTTP 404 is not retried and leaves the day out.
- `--out-dir` writes a trial elsewhere.

## License

The header: "License: public, with citation. SPP's terms: "Permission is implicitly granted to copy and distribute ... in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication" (https://www.spp.org/terms-conditions/, read 6 October 2026)." `license_verdicts.csv` gives SPP "may be public" (read 6), and "needs written permission" if the ERW sells anything. `license_tables.csv` names SPP as the table's one publisher (from the source registry), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public. The same verdict's note records that `spp_as_prices` gets no scheduled step until the license is answered (session 308); this table keeps its weekly step.

## Found while writing this note

- `parse()` builds a dictionary keyed by (area, hour): an hour a file gives twice keeps its last value without a word, and the run's check for a key given twice sees only what is left.
- The docstring says "An empty cell is not a quantity and gives no row". The code also drops, without a count, a cell that holds text that is not a number.
- The refresh is weekly, on Saturdays, but `run_status.csv` holds only the run of Saturday 10 October 2026 for this table, and no row of any connector dated 15, 16 or 17 October. The copy on the data machine ends on 10 October 2026 (Central).

## What it does not hold

- The file's other columns: cleared demand bids, fixed demand bids, virtual bids, generation, prices; the reserve products are in `spp_as_quantities`.
- Real-time quantities, and days before 1 September 2025 (session 136 read thirteen months to give a year-ago figure).
- An area the file does not name: before 1 April 2026, SWPW.
