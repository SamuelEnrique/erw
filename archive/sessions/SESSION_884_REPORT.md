# Session 884 report: the petroleum products' exports by destination

23 October 2026, from 04:39 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: EIA, 16 requests of 20 (the API host's robots address, which answers only with a key error, so there is no robots file to read there; the product list; 14 pages).

## Read these first

- **`eia_petroleum_exports_by_destination` now holds all seven products session 860 left out**, from January 2015 to July 2026: distillate fuel oil (EPD0), finished motor gasoline (EPM0F), kerosene-type jet fuel (EPJK), propane (EPLLPA), residual fuel oil (EPPR), ethane (EPLLEA) and petroleum coke (EPPC), beside crude oil and the products' total: 112,478 rows (45,058 before), 1,145 series, 202 destinations. Rewritten in place, since no page reads it (held from the live set); the archive holds the 67,420 new rows; coverage and the release package replaced.
- **How it was asked:** the seven as a query of their own, sorted by product, so that a ceiling reached part way leaves out the product it cut, whole, and names it in the header; crude oil's and the total's pages, saved by session 860, were reused (no request). All seven fitted in 14 pages.
- **The cross-check, against EPP0, EIA's total of petroleum products:** over the destinations, the seven are 77 to 83 percent of the total each year (2025: 2,491 million barrels in all, propane 649, distillate 456, finished gasoline 284, ethane 211, coke 199, jet fuel 79, residual 41). By destination and month, the seven stay within the total in 12,238 of 12,311 destination-months; in 73 (0.6 percent) EIA's products exceed its own total for that destination (for example the United Kingdom, August 2024, by 2.3 million barrels; Australia, September 2025, where the total is 0). The table keeps EIA's figures as EIA gives them.

## Decisions made without you

- The table extended rather than a table of its own: the queue file allowed it where no page reads the table.
- The connector's ceiling raised from 11 to 30 for a fresh run of all nine products, with `--ceiling` to set less (this session ran with 18, two requests already spent).
- The session's test found that the header would have said "the ceiling reached" of a product EIA gives no record; the connector now says "no record from EIA" in that case. The table written does not change (all seven came).

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session884.py` (3 tests), this report. Changed: `warehouse/connectors/eia_petroleum_exports.py`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `docs/redivis/release-v1/tables.csv`, `variables.csv`. On the data machine only: `runs/c048/`, `runs/s884*`.

## Corrected by session 891

The method notes' checks (session 891) found these against the code, the tables and EIA's files:

- The 12,311 destination-months include the U.S. total's own 139 (EIA's area NUS-Z00). The seven exceed EIA's total in 88 destination-months by any amount, in 73 by more than 0.05 percent and half a thousand barrels (the check's tolerance).
- The write (run 20261023T044326Z) read the pages the trial saved, with the connector's default ceiling (its header: 0 requests of 30); the trial ran with 18. That write stamped every row's `retrieved_at` with its own time, the crude oil and total rows included. Session 891 corrected the connector (a page reused from warehouse/raw carries the time it was really fetched), added a test, and wrote the table again.
