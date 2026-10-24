# Energy bought in ERCOT's day-ahead market, system-wide, an hour (ERCOT NP4-192-CD, DAM Total Energy Purchased)

Energy Research Warehouse (ERW), method note written in session 2152 (chain 092) for a table first written on 6 October 2026 (session 136).

Tables: `ercot_dam_cleared_energy`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), report NP4-192-CD, "DAM Total Energy Purchased" (report type 12333), on ERCOT's public reports site: one zip a day-ahead run, the file published on a day covering the next delivery day, each holding one CSV with the energy bought at each settlement point by hour (columns DeliveryDate, HourEnding, Settlement_Point, Total_DAM_Energy_Bought, RepeatedHourFlag; Central time). ERCOT lists the last 31 days only.

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12333` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each zip)

Product page `https://www.ercot.com/mp/data-products/data-product-details?id=NP4-192-CD`, named in the header and not asked. Every request goes to the host `www.ercot.com`, under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read by session 850, and again by session 2002 at 15:11:50 UTC on 23 October 2026, read 170 of `warehouse/metadata/license_reads.csv`), with the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)". Source id `ercot:NP4-192-CD`. Connector: `warehouse/connectors/ercot_dam_cleared.py` (session 136), its only table, with the frame it shares with the other day-ahead cleared connectors in `warehouse/connectors/dam_cleared.py`.

It is run once a week, on Saturday (UTC), by `warehouse/refresh_supply.sh`, which `warehouse/run_daily.sh` calls (`SUPPLY=1` forces it on another day), under `warehouse/health.py` and a pull budget of 15 minutes (`warehouse/pull_budget.py`), on GitHub's runner, which restores the table first (`warehouse/redivis/config.yaml`). The last run `run_status.csv` records is its only one for this connector, `20261010T145904Z` (10 October 2026, on GitHub): "192 hours; 184,082 rows read". No run on Saturday 17 October is recorded. The first date is from the rows and the header: the earliest `retrieved_at` is 6 October 2026 20:27:27 UTC, and the header says "the history starts with the first pull (6 October 2026)". Session 136's report gives no date of its own, and records 360 hours (15 days from 23 September) and 349,351 ERCOT rows read in all.

## Vintage and revision

Central delivery days 23 September to 10 October 2026 (23 September 2026 05:00 UTC to 11 October 2026 04:00 UTC), 18 days, in the file on the data machine, last written by run `20261010T145904Z` and restored from the Redivis draft by `scripts/sync.py`, as its header says: "Hours written by this run: 192, 2026-10-03T05:00:00Z to 2026-10-11T04:00:00Z." The rows' `retrieved_at` are 6 October 2026 (240 rows, 23 September to 2 October) and 10 October 2026 (192 rows, 3 to 10 October), from 18 addresses, one a delivery day. `vintage` is empty. `coverage.csv` gives the same 432 rows and dates: it agrees.

A run asks for the newest `--days` files on ERCOT's list (default 8), newest first. Every file is asked of ERCOT unless a raw file an earlier run kept on the machine answers it (`warehouse/raw/ercot_dam_cleared/`; GitHub's runner keeps none). `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc): an hour read again replaces the one held, and the table grows past ERCOT's 31 days. A row's `retrieved_at` is when its file was first downloaded (the raw record's).

## Shape and variables

Series, 432 rows, one entity. `entity` `ercot:system`; `variable` `dam_cleared_energy`; `value` the sum of Total_DAM_Energy_Bought over every settlement point of ERCOT's file for the hour, the connector's one computation, to one decimal; `unit` MWh (ERCOT's file names no unit; its product page calls the figure an amount of energy for the hour, read here as MWh); `freq` PT1H; `ts_utc` the hour's start, from DeliveryDate and HourEnding (Central) less one hour, RepeatedHourFlag Y marking the repeated autumn hour; `market` `ercot_dam`; `geo` US-TX; `node` "Total_DAM_Energy_Bought, summed over settlement points"; `vintage` empty.

| Entity | Variable | Hours | Mean MWh | Lowest | Highest |
|---|---|---|---|---|---|
| `ercot:system` | `dam_cleared_energy` | 432 | 41,209 | 29,939.5 (10 October 2026, 13:00 UTC) | 52,634.7 (28 September 2026, 21:00 UTC) |

Every one of the 18 Central days holds 24 hours; no clock change falls in the window. The mean day is 989,025 MWh.

## Reading ERCOT's reports site

- The list is asked afresh each run; only documents whose name ends `_csv.zip` are read, newest first, at most `--days` of them.
- Before each file, the run checks that 26,000 more rows (what a day's file is taken to hold) would not pass its ceiling (`--ceiling`, default 250,000 rows read from ERCOT); if they would, it stops asking and writes what it has. A file's rows are then counted (a raw file reused is not counted), and a count past the ceiling stops the run with nothing written. The run of 10 October read 184,082 rows for 8 files.
- A zip must hold exactly one CSV, with exactly the columns above, or the run stops and nothing is written.
- An hour any of whose rows is blank or not a number is not summed and not written; the run goes on. The hour ending must read HH:00; an hour the spring clock change skips stops the run. The repeated-hour flag is not checked for values other than Y and N, and the hour ending not for its range (unlike `ercot_as_prices.py`).
- From the frame: no hour at all stops the run; an hour given twice across files stops it; a newest hour more than 5 days old stops it, and nothing is written.
- A request is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.with_retries`; no retry once the pull budget has passed); HTTP 404 is not retried and stops the run. Three seconds after each request asked of ERCOT.
- ERCOT is checked against `warehouse/metadata/paused_sources.csv` before any request (`ip.paused("ercot")`, in the frame; it is not paused); a paused publisher is a skipped status row and no request.
- `--out-dir` writes a trial elsewhere and leaves the registry and the run status alone.

## License

The header: "License: public. ERCOT's terms of use, item 5: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices" (https://www.ercot.com/help/terms, read 6 October 2026)." The docstring also quotes item 6, which forbids use that harms the site's performance. `coverage.csv`: public. `license_tables.csv` names ERCOT as the table's one publisher (from the source registry); `license_verdicts.csv` gives ERCOT "may be public" (read 2 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict public.

## Cross-checks (session 2152)

- The counts above were computed from the rows, read past the 13 header lines; no hour is given twice.
- Hours complete: from 23 September 2026 05:00 to 11 October 2026 04:00 UTC there are 432 hours, and the table holds every one.
- Against ERCOT's actual load (`ercot_zone_load_hourly`, entity `ercot:system`, MW) in the 192 hours both hold (23 September 05:00 to 1 October 04:00 UTC): the energy bought day-ahead averages 43,348 MWh an hour and the load 67,206 MW; the ratio's median is 0.647 (lowest 0.580, highest 0.742) and the correlation 0.950, so the figure is below the load in every hour both hold. The two are different quantities and the connector does not compare them.
- Session 136's report: the five operators' totals are not the same measure (ERCOT's is every purchase at every settlement point), and are not to be added or ranked.
- The connector has no cross-check of its own beyond its reading rules.

## Found while writing this note

- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 23 October 2026, session 2002). Neither its docstring nor its header says so.
- The weekly run is due every Saturday, and none since 10 October 2026 is recorded, so the table ends with delivery day 10 October. A default run asks for the newest 8 files only: the days between 10 October and the first of them stay out unless a run passes a larger `--days` while ERCOT still lists them (31 days).

## What it does not hold

- The energy bought by settlement point or load zone: only the system sum is written.
- Energy sold in the day-ahead market, and the real-time market.
- Delivery days before 23 September 2026 (ERCOT lists 31 days) and after 10 October 2026 (no run since).
