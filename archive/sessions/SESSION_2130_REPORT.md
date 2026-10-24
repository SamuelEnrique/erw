# Session 2130 report: the Stanford draft

23 October 2026, from 23:21 UTC, on lab-desktop (the data machine), the eleventh session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`. Model spend USD 0. Pulls: Redivis's API, 94 requests of 150 (a reconcile, 7; the upload, 79 and one Supabase read for the lock; a reconcile, 7).

## Read these first

- **The run** (`runs/c079/s2130/run.sh`, session 2080's, started as a detached process so that the 10-minute limit of a foreground command could not stop it inside a table; under the data lock from 23:21:46 to 23:28:11 UTC; the main checkout, clean, pulled to origin's main `388d41d1` first; the branch's metadata, license record and validator copied in and main's put back after).
- **No table of chain 069 to reconcile first:** chain 069 uploads its own (its session 2116), as chain 068 did before landing.
- **This chain's five public tables uploaded, each proved by the draft's own count:** `usgs_comcat_earthquakes_south_central` (16,000), `epa_tri_energy_releases_annual` (384,483), `eurostat_renewable_capacity_annual` (49,313), `owid_ember_electricity_annual` (12,406), `epa_lmop_landfill_projects` (3,399). The upload record (5 rows) is carried to the branch.
- **The metadata tables refreshed:** `erw_coverage` 418 rows, `erw_sources` 505, `erw_headers` 4,032 lines (90 header lines of 9 tables not on this machine kept).
- **But the branch was cut before chain 068 landed,** so the refreshed `erw_coverage` lacks chain 068's four tables (`irena_capacity_annual`, `irs_soi_energy_credits_annual`, `eia_state_to_state_capacity`, `noaa_cpc_oni_monthly`), which main's coverage holds. Session 2133 refreshes it again after merging main into the branch, with a plain upload of one small table of this chain (about 34 requests, within this session's remaining 56).
- **The reconciles:** before, 312 tables, 262 match, 45 differ, none missing; after, 268 match, 44 differ (tables daily runs have grown since their upload), none missing. Five of this chain's tables were not yet in the upload record before (not asked); they match after.
- The release note is extended. Nothing released.

## Errors

- **The metadata refresh from a branch older than main** (above): the same pattern chain 059's upload left (its `erw_coverage` lacked chain 057's tables); the repair is scheduled in session 2133.

## Decisions made without you

- **The upload run as a detached process** rather than in the foreground: the TRI table (158 MB) could have outlasted the foreground limit, and an upload stopped inside a table empties it.
- **The `erw_coverage` repair left to session 2133,** after the merge with main, rather than a second upload now from a branch that would still lack chain 068's tables.

## For Samuel's ruling

- **The Stanford draft:** do not click before chain 069 has landed and uploaded, and an upload has refreshed `erw_coverage` from main.

## Files

- New: this report.
- Changed: `warehouse/metadata/redivis_uploads_stanford.csv` (5 rows), `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c079/s2130/`.
