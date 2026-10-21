# The live set's two largest tables, sized for a ruling (21 October 2026)

Energy Research Warehouse (ERW), session 456 (`queue/done/018-day-21-october-data.md`), for Samuel. Reads only, behind `scripts/db_probe.py` (open, 0.54 s). Nothing in `warehouse/supabase/live_set.yaml` was changed. With `docs/state/database_2026-10-21.md`: `series` is 2,142 MB (3,606,639 rows, about 623 bytes a row: 373 of heap and 250 of indexes; `series_pkey` 474 MB, `series_entity` 303 MB, `series_ts` 62 MB) against 512 MB of shared buffers.

## Read these first

- **No page reads `node_basis_daily` from Supabase.** The site reads `node_basis_summary` (1,260 rows: `site/lib/nodebasisread.ts`, the battery and cost-of-power pages). Neither the site (`site/lib`, `site/app`), the `erw` package nor Ask (`warehouse/chat/`) names `node_basis_daily`. Yet its 957,969 rows are **27% of `series`**, about 597 MB of the 2,142, loaded whole by session 374 at 20:35 UTC on 20 October. `live_set.yaml` lists it beside `node_basis_summary` ("the node basis on the three economics pages", session 358).
- **`ercot_rtm_price_adders`** (601,810 rows, 17%, about 375 MB) has one reader: the datacenter answers (`site/lib/datacenter/answers.ts`, session 236). They make two reads of one variable, `rtorpa_mean` for `ercot:system`, bounded in time: the hours held since the first of the page's twelve months, and the hours at or above a level since fourteen months before that. From August 2024 that is 11,786 rows. The other seven variables (500,932 rows) are read by nothing.
- Together the two are **43% of `series`, about 970 MB**. Taking them out would bring the table from about 2.1 GB to about 1.2 GB, still over the 512 MB of buffers, and shrink `series_pkey` and `series_entity` by the same share (about 205 and 130 MB). A plain vacuum would mark the space for reuse; a `VACUUM FULL`, a person's command, would return it.

## The choices, with what each keeps

| Choice | Rows kept in Supabase | Rows out | About freed |
|---|---|---|---|
| `node_basis_daily` as it is (whole) | 957,969 | 0 | 0 |
| `node_basis_daily`, the last 365 days (`live_set.yaml`'s `days`) | 909,579 | 48,390 | 30 MB |
| the last 90 days | 216,771 | 741,198 | 460 MB |
| the last 35 days (the `recent` window's length) | 140,874 | 817,095 | 510 MB |
| **out of the live set** (no reader; the table stays in `warehouse/output`, the archive and Redivis once stored) | 0 | 957,969 | **600 MB** |
| `ercot_rtm_price_adders` as it is | 601,810 | 0 | 0 |
| only `rtorpa_mean` (the variable the page reads), whole | 100,878 | 500,932 | 310 MB |
| only the page's rows (`rtorpa_mean`, from August 2024) | 11,786 | 590,024 | 370 MB |
| out of the live set | 0 | 601,810 | 375 MB (the datacenter answers' adder lines would then read nothing: a page change) |

The megabytes are rows times the table's average of 623 bytes a row; a table's own rows may be wider or narrower. The pages' own files (as `/board` reads `site/data/board.json`) would be the other way for either table, a code change.

## The reads, timed now (09:10 UTC, as `postgres`, 1,000 rows each)

| Read | First | Second |
|---|---|---|
| the battery page's `node_basis_summary` for the hub | 0.08 s | 0.03 s |
| the datacenter answers' adder hours from August 2025 | 0.03 s | 0.03 s |
| the cost-of-power page's `cost_of_power_monthly` | 0.05 s | 0.03 s |

The database is quiet now, so these show the shape of the reads, not the night's slowness. Every read uses the `(table_name, entity, ...)` indexes, which are as large as they are because of the two tables above.

## For Samuel's ruling

- `node_basis_daily` out of the live set: about 600 MB, and no reader loses anything. The smallest change with the largest effect.
- `ercot_rtm_price_adders` cut to `rtorpa_mean` (310 MB), or to the page's rows (370 MB).
