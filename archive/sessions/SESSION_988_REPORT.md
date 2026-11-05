# Session 988 report: the Stanford draft, chain 055's tables

23 October 2026, 16:37 to 16:43 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`, run by the second agent once the daily run had released the data lock (the chain's first agent stopped at 14:19 UTC). Model spend USD 0. Pulls: Redivis's API, 88 requests of 150 (and 1 to Supabase for the lock check).

## Read these first

- **A first reconcile (6 requests) found every table of chain 054 in the draft and current;** chain 055's five new public tables were not yet uploaded, and `usgs_mcs_critical_minerals` was stale (692 rows in the draft, 1,600 since session 981).
- **Six tables uploaded to the Stanford draft, each proved by the draft's count:** `eia_ieo_projections` (17,856 rows), `eia_capacity_factors_annual` (374), `eia_capacity_factors_monthly` (1,224), `eia_heat_rates_annual` (44), `egrid_subregions_annual` (540) and `usgs_mcs_critical_minerals` (1,600), in one plain upload (76 Redivis requests, under a cap of 120), which also refreshed `erw_coverage` (379 rows) and `erw_sources` (468) and rebuilt `erw_headers` (3,576 lines).
- **Not uploaded, by the target's own rule (public verdicts only):** `lbnl_hybrid_plants` (held internal, session 979) and `usace_nid_dams` (no verdict: the Corps' terms unread, session 983).
- **The last reconcile (6 requests): 239 of 276 tables match; 37 differ, none is missing from the draft,** every one a table a daily run has grown since its upload.
- **For the uploads, the main checkout ran with the branch's `coverage.csv`, `sources.csv`, license record and `docs/licenses.md`;** main's files were restored after, and the upload record (6 rows) carried to the branch. No new unit or entity type was in these tables, so main's validator served.
- **The release note extended.** Nothing released.

## Decisions made without you

- **One plain upload for all six,** the USGS table with them: main's validator knows `t` and `USD/kg` since chain 054 landed, so no second run was needed.

## For Samuel's ruling

- None new. The release note's "click" list stands: every public table of chains 048 to 055 is in the draft.

## Files

- New: this report.
- Changed: `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c055/s988/`.
