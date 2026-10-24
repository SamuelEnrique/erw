# New York's load scheduled in the day-ahead market, an hour, from September 2025 (NYISO P-30, Day-Ahead Market Daily Energy Report, Total Load Scheduled)

Energy Research Warehouse (ERW), method note written in session 2180 (chain 097) for a table first written on 6 October 2026 (session 136).

Tables: `nyiso_dam_cleared_energy`

## Publisher and address

New York Independent System Operator (NYISO), public report P-30, "Day-Ahead Market Daily Energy Report" (its list, `http://mis.nyiso.com/public/P-30list.htm`, is named in the header and not asked), one zip a calendar month holding one CSV a day:

`http://mis.nyiso.com/public/csv/damenergy/<YYYYMM>01DAM_energy_rep_csv.zip`

The addresses are plain http, as the code writes them. Each daily CSV has a row an hour, "Date Hour" (Eastern, the hour's start), the column "Total Load Scheduled" among others, and a last line "Total". The connector sends the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)". No reading of mis.nyiso.com's robots file is recorded in `warehouse/metadata/license_reads.csv`; this note made no request.

Source id `nyiso:damenergy` (in `sources.csv`, license public, first seen 2026-10-06, last seen 2026-10-10). Connector: `warehouse/connectors/nyiso_dam_cleared.py` (session 136), its only table, on the frame the five day-ahead cleared energy connectors share, `warehouse/connectors/dam_cleared.py`. The method of the page row is `docs/methods/supply_and_trade.md` ("Day-ahead energy cleared"). `warehouse/supabase/live_set.yaml` holds the table out of the live catalogue (`catalogue_hold`, session 136: "nothing reads them from Supabase").

Schedule: `warehouse/refresh_supply.sh` runs the connector (step `nyiso_dam_cleared`, under `warehouse/health.py run` and a pull budget of 15 minutes, `warehouse/pull_budget.py`). `warehouse/run_daily.sh` calls that script on Saturdays (UTC) only, or on any day with `SUPPLY=1`, and `.github/workflows/daily-prices.yml` runs `run_daily.sh` on GitHub's runner. `warehouse/metadata/run_status.csv` holds one run: `20261010T150004Z` on GitHub, ok.

A run asks for each calendar month from the month of the day 14 days before today (Eastern) to this month, newest first (`--days`, default 14): one or two zips. This month's and last month's are asked again on every run; an older month is read from `warehouse/raw/` once kept. Two seconds after each request. A month NYISO does not hold (HTTP 404) is not written.

## Vintage and revision

Eastern days 1 September 2025 to 11 October 2026 (`ts_utc` 2025-09-01T04:00:00Z to 2026-10-12T03:00:00Z), 406 days, in the file on the data machine, restored from the Redivis draft by `scripts/sync.py` (its last header line), with the header of run `20261010T150004Z`: "Rows read from the operator in this run: 1,025 (this run's ceiling 5,000). Hours written by this run: 984, 2026-09-01T04:00:00Z to 2026-10-12T03:00:00Z" (the 41 rows more are the days' "Total" lines), and "984 rows: 96 new, 888 replacing earlier rows ...; 8760 rows are kept from earlier runs". `vintage` is empty. `coverage.csv` gives the same 9,744 rows, the same first and last `ts_utc`, one node, and last run 2026-10-10T15:00:04Z.

`retrieved_at`: 8,760 rows carry 6 October 2026, 20:22:03Z to 20:22:34Z (12 monthly zips, September 2025 to August 2026, session 136's run), and 984 rows 10 October 2026, 15:00:05Z to 15:00:07Z (the zips of September and October 2026). The first date is from these rows, from the commit that added the connector (`f1ae6e5f`, 6 October 2026, 20:45 UTC), from session 136's report ("9,648 (from September 2025)", "14 monthly files") and from `sources.csv`.

Each run merges its rows into the held file on (entity, variable, ts_utc) (`ip.write_csv`), so the table grows past the connector's window, and an hour NYISO revises in this month's or last month's zip replaces the one held. On the day-ahead side the run of 10 October already held 11 October, the next operating day.

## Shape and variables

Series, 9,744 rows, one entity, one variable. `entity` `nyiso:system`; `variable` `dam_cleared_energy`; `value` the file's "Total Load Scheduled" for the hour; `unit` MW (MW over the hour, so a value is also the hour's MWh); `freq` PT1H; `ts_utc` the "Date Hour" read as America/New_York (the repeated autumn hour placed by its order, `ambiguous="infer"`) and given in UTC; `geo` US-NY; `market` nyiso_dam; `node` "Total Load Scheduled", the column read; `source` `nyiso:damenergy`; `source_url` the month's zip (14 zips); `vintage` empty. There are no `x_` columns.

Every hour of the 406 days is held: each Eastern day has 24 hours except 2 November 2025 (25) and 8 March 2026 (23), and no hour is missing. The mean is 17,711.1 MW, the lowest 12,268.2 (2026-10-11T07:00:00Z) and the highest 31,245.5 (2026-07-03T22:00:00Z). No (entity, variable, ts_utc) is given twice, and no value is 0 or negative.

What the figure counts: the docstring says "the load the day-ahead market scheduled system-wide (bid load, bilateral load and price-capped load together, as NYISO totals them)". `docs/methods/supply_and_trade.md` says "NYISO's Total Load Scheduled and SPP's Total Demand include cleared virtual bids". The table keeps the one column and cannot settle which is right.

The counts in this note were computed in session 2180 with pandas from the rows of `warehouse/output/nyiso_dam_cleared_energy.csv`, read past its 12 header lines.

## Checks the connector makes

- Before any request, `dam_cleared.run` asks `iso_prices.paused("nyiso")`; a paused publisher gets no request, and the run writes a "skipped" status and nothing else. NYISO is not in `warehouse/metadata/paused_sources.csv`. `paused_host()` is not asked (the host is fixed in the code).
- Each daily CSV must hold the columns `Date Hour` and `Total Load Scheduled`, or the run stops. The "Total" line is the day's sum and is not a row. A local hour that does not exist (the spring clock change) stops the run.
- A cell that does not read as a number gives no row. Nothing is filled, summed across hours or estimated.
- An (entity, variable, ts_utc) given twice in the run's rows stops the run, and nothing is written.
- The newest hour must be at most 5 days old, or nothing is written.
- No complete-day rule: a day short of hours is written with the hours it has.
- Ceiling: 5,000 rows read from NYISO in a run (the lines of each zip fetched, "Total" lines included; not of zips read from `warehouse/raw/`); past it the run stops and writes nothing (`--ceiling` changes it). The run of 10 October read 1,025.
- Each zip is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.fetch_raw` and `with_retries`), with no retry once the pull budget has passed; HTTP 404 is not retried and leaves the month out.
- `--out-dir` writes a trial elsewhere.

## License

The header: "License: public, with a caution (sessions 65 and 85). NYISO's legal notice grants no license and forbids republishing "any image or video on this website as a stand-alone file", which names images and video, not data (https://www.nyiso.com/legal-notice, read 6 October 2026). A person can rule otherwise." `coverage.csv`: public. `license_verdicts.csv` gives NYISO "needs written permission" (read 5, 12 October 2026, of `https://www.nyiso.com/legal-notice`; the same if the ERW sells anything). `license_status.csv` holds the table as "license needed" from 2026-10-21, and `docs/licenses.md` gives "ruled: license needed from 2026-10-21" and the ERW verdict unsettled.

## Found while writing this note

- The header and `coverage.csv` say public; `license_verdicts.csv`, `license_status.csv` and `docs/licenses.md` say NYISO's permission is needed (license needed from 21 October 2026, ERW verdict unsettled). The connector keeps its weekly step in `warehouse/refresh_supply.sh`, while NYISO's note in `license_verdicts.csv` records that `nyiso_as_prices` gets no scheduled step until this license is answered (session 308).
- The docstring and `docs/methods/supply_and_trade.md` disagree on what Total Load Scheduled counts: the docstring lists the virtual bids among the columns "read and not written"; the method note says the total includes cleared virtual bids.
- Within a month's zip, `pull()` gathers the days' hours in one dictionary (`hours.update`): an hour given by two daily files keeps the later file's value without a word, and the run's check for a key given twice sees only what is left.
- The docstring is silent on cells that are not numbers; the code drops them without a count.
- The refresh is weekly, on Saturdays, but `run_status.csv` holds only the run of Saturday 10 October 2026 for this table, and no row of any connector dated 15, 16 or 17 October. The copy on the data machine ends on 11 October 2026 (Eastern).

## What it does not hold

- The report's other columns: offers, generation, imports, exports, virtual bids.
- Load by zone (`nyiso_zone_load_hourly`), real-time load, and reserves (NYISO publishes no hourly reserve quantity: `docs/methods/reserve_quantities_nyiso_spp.md`).
- Days before 1 September 2025 (session 136 read thirteen months to give a year-ago figure).
