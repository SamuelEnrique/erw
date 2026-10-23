# Session 690 report: EIA-861's "empty provenance rows" were a reader's cut at a "#"

23 October 2026, from 00:22 UTC, on lab-desktop (the data machine), a session of `queue/done/045-evening-22-october-data-resumed.md`. Model spend USD 0.

## Read these first

- **The 111 rows were never empty.** `eia861_utility_sales` holds them whole, every field filled: their utilities are named "Vera Irrigation District #15" (`eia861:19784:WA:A:BPAT`, 2015 to 2025, 105 rows) and "Maricopa County M W C Dist #1" (`eia861:40355:AZ:A:AZPS`, 2019 and 2021, 6 rows). A reader that skips the header with pandas' `comment="#"` cuts each of those lines at the "#" and sees the rest of the row empty; session 674's note was written from such a read. Traced against the saved zips: each year's sheet gives exactly the rows the table holds, with the zip as `source_url`. Nothing was fixed in the data because nothing was wrong in it.
- **The paths that publish read it right:** the `erw` package, the Supabase loader, the Redivis uploader, the validator, the coverage builder and the archive all skip the header by its leading "#"; a test now keeps it so.
- **The header's "Years held" line is true:** it said "2025" of a file holding 2015 to 2025. The connector now names every year the file holds once its run's year is merged in; the table was written again under the lock for 2025 from the saved page and zip (0 requests; 34,484 rows replaced by the same values, archive: unchanged). The header now reads "Years held: 2015 to 2025 (this run wrote 2025; ...)".
- **Found, not fixed (the code machine's):** 45 tables hold a "#" inside a row on this machine (`runs/c045/s690/hash_tables.out`), among them `lbnl_interconnection_queue` (1,581 rows), `ferc_eqr_contracts_history` (18,011), `eia923_plant_fuel_annual` (4,354). Three readers still use `comment="#"`: `warehouse/analysis/findings/findings_common.py` lines 115 and 284 (the findings scanner's generic reader; the queue findings read `lbnl_interconnection_queue`), and `warehouse/deals/duplicates.py` line 81 (`energy_deals`, which holds no "#" today). A finding built on a cut row sees its later fields empty. Changing the reader may move a finding's figure, so it is listed, not changed.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| none | 0 of 0 | the saved EIA-861 page and zips |

## Decisions made without you

- The method note's line on the 111 rows is replaced by the reader's caution, rather than the rows being rewritten.
- The table was written again (same rows) so that its header's "Years held" line is true now, not at the next run.
- The metadata patch conflicted with session 689's adjacent line (`eia861m_utility_sales_monthly`); resolved with `runs/s622/resolve_ours_plus.py` and the older duplicate line dropped (`runs/c045/keep_newest_row.py`).

## For Samuel's ruling

- Whether the findings scanner's reader (`findings_common.py` lines 115 and 284) should read rows whole, which may move a queue finding's figures (the code machine's work).

## Files

- New: `tests/test_session690.py` (5 tests), this report. Changed: `warehouse/connectors/eia861_sales.py`, `docs/methods/eia861_utility_sales.md`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `sources.csv`. On the data machine only: `runs/c045/s690/` (the trace, the trial, the list of tables with a "#"), `runs/s690_*`.
