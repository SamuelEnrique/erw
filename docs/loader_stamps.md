# The loader and the retrieval stamp: why the daily run rewrote whole tables

Session 131. Found from the daily runs' own artifacts of 3, 4 and 5 October 2026 (`runs/supabase_reconcile.csv` in
each), fixed in `warehouse/supabase/load.py` on `wip/131-freeze-scheduled`, tested in `tests/test_session131.py`.

## What happened

| Run | Tables selected | Rows selected | Rows written | Tables written whole | Database before, after (MB) | Recorded as failed |
|---|---|---|---|---|---|---|
| 3 October, 37128094436 | 48 | 542,074 | 182,950 | 17 (101,933 rows) | 399.0, 468.2 | none |
| 4 October, 37207629600 | 49 | 564,285 | 201,822 | 18 (123,177 rows) | 433.3, 514.3 | `ercot_as_prices` (its connector, below) |
| 5 October, 37321169760 | 58 | 1,292,645 | 927,833 | 25 (848,123 rows) | 971.0, 1,127.2 | `ercot_as_prices`, `ercot_hub_prices_daily` (the load) |

The loader's file gives no written count for the two tables it recorded as failed on 5 October; their 681,638 rows are counted as written because every row of both carried that load's `loaded_at` afterwards (session 126). Without them the file's own sum is 246,195 rows written and 23 tables written whole.

Three separate things, two of them one cause.

**4 October: a connector, already fixed.** ERCOT published the 2026 file of its yearly reserve prices (NP4-181-ER) as
an Excel workbook in place of a CSV. `ercot_as_prices.py` stopped ("zip holds [...xlsx], expected one CSV"), so the
whole table was absent on the runner and recorded as failed, and the battery stack skipped. Session 113 taught the
connector both forms on 5 October; that is on main, with ERCOT's own two files as its test.

**Every day: the loader rewrote every table a connector rebuilds whole.** The loader's rule since session 11 is to
write only what changed. It compared every column, and one of them is `retrieved_at`, when the document was fetched.
A connector that rebuilds its table from the source each run stamps every row with that run's time, so every row
"changed", every day: 17 to 25 tables a day, among them `eia_fuel_spot_prices` (27,717 rows), `fred_daily_spot_prices`
(24,306), `storage_buildout_monthly` (21,229), `storage_daily_cycle` (14,057) and `energy_projects` (34,638). Postgres
keeps the old copy of a rewritten row until a vacuum, which is why the database grew 70 to 80 MB during each load.
The data standard asked each derived table to keep an unchanged row's stamp (decision 26); few did, and a source
table rebuilt on a runner with no raw files cannot.

**5 October: two large tables joined the selection.** `ercot_as_prices` (336,332 rows) is built whole on the runner
from ERCOT's nine yearly files, so all its rows carried that run's stamp, and `ercot_hub_prices_daily` (345,306) was
new. The loader wrote all 681,638 rows. It then asked Supabase for each table's count, straight after rewriting every
row of it, and both counts came back HTTP 500 with no body ("JSON could not be generated": the statement timed out,
and a HEAD request carries no message; the check before the write had already timed out with Postgres's own code
57014). The loader recorded both as FAILED and left their hash empty, so the next run would write them again. **Both
tables were whole**: on 6 October the same counts answered 336,332 in 1.6 seconds and 345,306 in 0.5.

**Why the run was long.** Its daily step took 135 minutes against 85 and 80 the two days before. The load began
half an hour later than on 3 October (15:23 against 14:53 UTC: Monday's weekly pulls), and the load, digest and upload
then took about 55 minutes against about 32: 927,833 rows written against about 190,000.

**What would have followed.** `ercot_as_prices` is rebuilt whole every day, so every daily run would have written
its 336,332 rows again, and the count after a rewrite of that size could time out again: a table recorded as failed
every day, and a load some twenty minutes longer than it need be.

## The fix

1. **A row fetched again is not a changed row.** `retrieved_at` is left out of the row comparison (`canon`) and of the
   table's hash (`rows_sha256`). A row is written when its value, unit, source, source document, vintage or any other
   column differs, and not otherwise. A table rebuilt from the same documents is skipped whole. For `ercot_as_prices`
   a day's load becomes that day's 120 rows.
2. **The count is asked three times** (after 10 and 30 seconds) before a table is recorded as failed.

**What changes for a reader.** In Supabase a row's `retrieved_at` becomes the time of the load that last changed the
row, not of the last time its document was fetched. The CSV, the archive and Redivis keep the connector's stamp as
before. A page that shows the newest `retrieved_at` of a table will show the day its data last changed.

**On the first run with the fix** every table's stored hash is of the old kind, so every table is compared row by row
once (read, not written). After that an unchanged table is not read at all.

## Not fixed here

- The check that refuses a table older than the live copy (`older_than_live`) sorts the table by `retrieved_at` and
  timed out on the 336,332 rows; it then says so and lets the load go on. An index on `(table_name, retrieved_at)`
  would make it a lookup. That is a migration, and migrations are a person's to approve.
- The loader reads a table back page by page with an offset. For 340,000 rows that is 340 requests, each skipping
  further. Reading by key would be faster. It matters less now that an unchanged table is not read.
- Other failures of the same runs that are not the loader's: `grid_network` ("'bool' object has no attribute 'get'"),
  `build_status` (`eia930_all_interchange` has two extra columns), the digest's duplicate item, ISO-NE's hourly file,
  the package test of `ercot_dam_esr_awards`. Each is its own fault and none made the run long.
