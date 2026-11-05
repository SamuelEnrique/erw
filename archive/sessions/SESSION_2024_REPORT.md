# Session 2024 report: the Stanford draft, chains 056 and 057's tables

23 October 2026, 19:09 to 19:24 UTC, on lab-desktop (the data machine), a session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`, under the data lock for the whole session. Model spend USD 0. Pulls: Redivis's API, **150 requests of 150** (6, 92, 40, 6 and 6), and 3 to Supabase for the lock.

## Read these first

- **`erw_coverage` is empty in the Stanford draft. This session's fault, and the first thing to put right:** the second upload (one table, `boem_offshore_platforms`) ran under a request cap of 40 that I set too low. It fell inside `erw_coverage`'s true replace, which had already deleted the table, against the chain's rule that a cap stops between tables, never inside one. The session's last 6 requests re-created the table but could not upload its rows. `erw_sources` (479) and `erw_headers` (3,689) are whole. The draft is unreleased, and nothing scheduled releases it. **Chain 058's session 2038 refreshes the metadata tables in its plain upload**; the next file says so (session 2027). **Samuel: do not click before then**; the release note says the same.
- **A first reconcile (6 requests):** 232 of 276 tables match; 44 differ, each a table a daily run has grown since its upload; none missing. Chain 056's six public tables were not in the draft (its session 2010 did not run).
- **Eleven tables uploaded, each proved by the draft's count:** chain 056's `doe_useer_employment` (3,311), `nrc_new_reactor_applications` (6), `nrc_advanced_reactor_preapplicants` (43), `usbr_hydropower_monthly` (31,702), `noaa_cpc_degree_days_daily` (118,900) and `boem_offshore_platforms` (7,092), and this chain's `eia_mecs_manufacturing` (5,363), `eia_cbecs_commercial_buildings` (5,944), `eia_recs_households` (2,802), `lbnl_tracking_the_sun` (8,762) and `eia_lng_liquefaction_projects` (48). The first plain upload (92 requests) also refreshed `erw_coverage` (391 rows) and `erw_sources` (479) and rebuilt `erw_headers` (3,689 lines).
- **`boem_offshore_platforms` was refused in the first run:** the main checkout's validator was 33 commits behind origin's main and did not know chain 056's entity type `platform`. The second run copied the branch's validator in for the one table (the chain's rule), and main's was put back after.
- **Not uploaded, by the target's rule (public verdicts only):** `eia_ice_electricity_daily` (internal, sessions 2014 and 2019).
- **The last reconcile (6):** 242 of 287 match, 44 differ (the same daily-grown tables), none missing; every table uploaded here matches.
- **For the uploads the main checkout ran with the branch's `coverage.csv`, `sources.csv`, license record and `docs/licenses.md`,** under the lock (chains 058 and 059 run on this machine too); main's files were restored after, the upload record (11 rows) carried to the branch, and the main checkout pulled to origin's main.
- **The release note extended.** Nothing released.

## Errors

- **The cap inside `erw_coverage`'s replace,** above. Where a run's cost is not known, the cap must leave room for the whole run: a single table with the three metadata tables cost more than 40 (session 988's six tables cost 76).
- **The validator behind main,** above: this checkout had not pulled since chain 056 landed.

## Decisions made without you

- **The ceiling kept:** no request past 150 to repair `erw_coverage`; the repair is left to chain 058's session 2038, which uploads in full.
- **Chain 056's tables uploaded here,** for its session 2010.

## For Samuel's ruling

- **Do not release the Stanford draft until `erw_coverage` holds its rows again** (chain 058's session 2038, or any run of `python warehouse/redivis/upload.py --target stanford <a table>` on the data machine).

## Files

- New: this report.
- Changed: `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c057/s2024/`.
