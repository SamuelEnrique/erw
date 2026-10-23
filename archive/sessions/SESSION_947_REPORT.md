# Session 947 report: the Stanford draft, chain 053's eight tables and one a later chain left out

23 October 2026, 11:35 to 11:41 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`. Model spend USD 0. Pulls: Redivis's API, 102 requests of 150 (and 1 to Supabase for the lock check).

## Read these first

- **A first reconcile (6 requests) found nine public tables never uploaded to the target:** chain 053's eight and `uswtdb_wind_turbines`, which session 888 settled as public (its publisher name had matched no verdict) and no Stanford upload since had included.
- **Nine tables uploaded to the Stanford draft in one plain upload, each proved by the draft's count:** `uswtdb_wind_turbines` (77,839 rows), `eia_world_coal_annual` (317,307), `eia_world_energy_co2_annual` (246,988), `ornl_npd_potential` (597), `lbnl_solar_projects` (1,775), `lbnl_hybrid_ppa_prices` (113), `ornl_eha_hydropower_units` (5,362), `lbnl_wind_capacity_factors` (1,210), `ercot_node_wires_utilities` (569).
- **The plain upload also refreshed the draft's metadata:** `erw_coverage` (361 rows, from 353), `erw_sources` (457, from 451) and `erw_headers` rebuilt in full (3,414 lines).
- **90 Redivis requests for the upload,** one run under a cap of 130, no cap inside a table.
- **The last reconcile (6 requests): 223 of 260 tables match; 37 differ, none is missing from the draft.** The 37 are tables a daily run has grown since their upload (SPP's curtailment, the state generation mix, the storage cycle, the weather tables and the rest).
- **For the upload, the main checkout ran with the branch's `coverage.csv`, `sources.csv` and `docs/licenses.md`;** main's files were restored after, and the upload record (`warehouse/metadata/redivis_uploads_stanford.csv`, nine rows) carried to the branch as a patch.
- **The release note extended** (`docs/reviews/redivis-v1-release-note-2026-10-23.md`, session 947's paragraph). Nothing released.

## Decisions made without you

- **`uswtdb_wind_turbines` uploaded with the chain's tables,** as the next file's "first any table a later chain left out" asks: it is public by session 888's settlement and passed the upload's own license check.

## For Samuel's ruling

- None new. The release note's "click" list stands: every public table of chains 048 to 053 is in the draft.

## Files

- New: this report.
- Changed: `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c053/s947/`.
