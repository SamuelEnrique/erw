# Session 878 report: the Stanford draft, chain 047's tables up

23 October 2026, from 03:45 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md`. Model spend USD 0.

## Read these first

- **11 public tables uploaded to the Stanford draft with the true replace, each proved by the draft's count:** this chain's ten (`eia861_utility_data`, `eia861_demand_response`, `eia861_dynamic_pricing`, `eia861_advanced_meters`, `eia861_net_metering`, `ercot_cdr_units`, `eia860_plants_annual`, `eia_coal_receipts_annual`, `eia861_short_form`, and the tables' header lines in `erw_headers`, 2,946 lines) and `eia861_delivery_only` again (session 865 corrected its rows' source). Nothing released.
- **One gap:** `eia_coal_receipts_annual` was first refused by the main checkout's validator, which does not yet know the unit `Btu/lb` (Decision 52 is on this branch); uploaded alone with the branch's validator, proved (270,547 rows), but its header lines did not reach `erw_headers` before the ceiling. The next Redivis session merges them (`upload.py --target stanford --prove-by-listing --tables eia_coal_receipts_annual` once this branch has landed).
- **The reconcile:** 169 of 214 tables match; the 45 that differ are the tables the daily run has grown since their upload, and `erw_coverage` and `erw_sources`, as before.
- **The remote test was not run:** the uploads took the ceiling; the four tests session 864 fixed stay for a later Redivis session.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com | 98 of 100 | the ten uploads, their proofs and the header merge (73), the receipts' upload and proof (19), the reconcile (6) |
| Supabase | 2 | the data lock's checks |

## Decisions made without you

- The uploads before the remote test, as the chain lists them.

## For Samuel's ruling

- None new (the click, as the release note gives it).

## Files

- New: this report. Changed: `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`. On the data machine only: `runs/c047/s878/`.
