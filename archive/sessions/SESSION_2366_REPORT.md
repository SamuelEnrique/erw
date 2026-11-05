# Session 2366 report: method notes for this chain's tables, and the Stanford draft

24 October 2026, from 09:03 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Sessions 2367 and 2368 ran while the data lock was held by chain 112's draft. Model spend USD 0. Pulls: Redivis's API, 142 requests of 150; Supabase twice, for the uploader.

## Read these first

- **Five method notes,** linked from the Method column: this chain's four tables, and chain 105's `eurostat_electricity_capacity_annual`, written after that chain's notes session.
  - `docs/methods/makstat_macedonia_electricity_monthly.md`
  - `docs/methods/statbank_moldova_electricity_monthly.md`
  - `docs/methods/eurostat_oil_monthly.md`
  - `docs/methods/eurostat_solid_fuels_monthly.md`
  - `docs/methods/eurostat_electricity_capacity_annual.md`

  Two helpers drafted them with no request; I read each, acted on every point or recorded it, and added a paragraph to each saying which. Every row of the five tables equals its raw file.
- **Corrected, with all five tables written again offline** (the same rows), their metadata rows replaced by key:
  - **MakStat's "gross inland consumption" is net imports.** It equals imports less exports in every month, so its 13 negative months are months of net exports, not impossible values. It keeps MakStat's name and the header says what it is.
  - **MakStat's `vintage`** is now empty (it said 2013-04-23).
  - **StatBank:** the header no longer says what "acquired from other sources" holds, since the bureau's table does not say; it is 0 from January 2025. Production is no longer called gross.
  - **Eurostat:** the EU rows are the reporting members' sums, short in some months. Stock change is positive into stock for oil and out of stock for coal.
  - **The capacity table:** commissioning covers only 23 codes and most countries from 2020. Germany's 2021 total is 60,036 MW short of its parts, as published, and so are the EU's.
  - **Reports corrected,** each correction saying so: 2357, 2358, 2363, 2364 and chain 105's 2356.
- **The Stanford draft** (`runs/c110/s2366/stanford.sh`, from the main checkout pulled, with this branch's records, merged with main):
  - **Uploaded, each proved by the draft's count:**
    - Moldova's StatBank table, the solid fuels and the capacity table (run A);
    - the oil table alone (run B).
  - **The caps fell inside the metadata tables.** Run A stopped inside `erw_coverage` and `erw_sources`, run B inside `erw_sources`. Chain 112's session 2380 refreshed the metadata tables between the runs, and the closing reconcile finds all of them matching.
  - **Reconciles:** before, 338 of 388 match; after, 344 match, 44 differ (tables daily runs have grown); none missing.
  - **The release note is extended.** Nothing is released.
  - **Left for the next draft session:** session 2369's `eurostat_crude_imports_monthly`.

## Errors

- **Run A's shell was killed for low memory** while its uploader ran on.
  - The uploader was let finish, and every table was proved.
  - The killed shell would have carried the record, put main's files back and released the lock; I did all three by hand, after checking the process had ended.
  - The record gained no rows for run A, since the uploader writes it only when every table succeeds.
- **The caps of runs A and B** (70 and 60) were too small for the metadata refresh after the tables. The next draft session should leave about 40 requests for it; the release note says so.

## Decisions made without you

- **Notes for chain 105's Eurostat capacity table here,** since chain 105's notes session came before it.
- **MakStat's line kept under its own name,** with its meaning in the header, rather than renamed.

## For Samuel's ruling

- None new.

## Files

- New: the five notes above, this report.
- Changed:
  - the connectors `makstat_macedonia.py`, `statbank_moldova.py`, `eurostat_oil_monthly.py`, `eurostat_solid_fuels_monthly.py` and `eurostat_capacity.py`;
  - reports 2356, 2357, 2358, 2363 and 2364;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`;
  - `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c110/s2366/`, `runs/s2366*`.
