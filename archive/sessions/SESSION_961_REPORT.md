# Session 961 report: the Stanford draft, chain 054's eleven tables

23 October 2026, 13:01 to 13:09 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: Redivis's API, 142 requests of 150 (and 2 to Supabase for the lock checks).

## Read these first

- **A first reconcile (6 requests) found every table of chain 053 in the draft and current;** the eleven not yet uploaded were this chain's.
- **Eleven tables uploaded to the Stanford draft, each proved by the draft's count:** `onrr_production_monthly` (2,264 rows), `onrr_production_annual` (15,068), `onrr_revenue_monthly` (413,554), `lbnl_wind_costs` (119), `lbnl_wind_turbine_orders` (122), `eia_primary_energy_monthly` (15,156), `blm_ca_renewable_rows` (57), `eia_coal_distribution_quarterly` (1,207), `eia_uranium_production_quarterly` (171), `eia_uranium_facilities` (24) in one plain upload (93 requests, under a cap of 130), which also refreshed `erw_coverage` (372 rows) and `erw_sources` (463) and rebuilt `erw_headers` (3,526 lines); and `usgs_mcs_critical_minerals` (692) in a second run (37 requests).
- **Why a second run:** the uploader validates each table with the main checkout's validator, which does not yet know `t` and `USD/kg` (session 954's Decision 56, on this branch); it blocked the USGS table and uploaded the rest. The second run had the branch's validator copied in for the one run, and main's put back.
- **The last reconcile (6 requests): 234 of 271 tables match; 37 differ, none is missing from the draft,** every one a table a daily run has grown since its upload.
- **For the uploads, the main checkout ran with the branch's `coverage.csv`, `sources.csv` and `docs/licenses.md`;** main's files were restored after, and the upload record (11 rows) carried to the branch as a patch.
- **The release note extended.** Nothing released.

## Decisions made without you

- **The USGS table by `--tables` in its own run,** so the metadata tables were not rebuilt twice within the ceiling.

## Errors

- **The plain upload exited 1 for the one blocked table** (the validator's unit vocabulary on main); the other ten and the metadata were proved before the second run.

## For Samuel's ruling

- None new. The release note's "click" list stands: every public table of chains 048 to 054 is in the draft.

## Files

- New: this report.
- Changed: `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c054/s961/`.
