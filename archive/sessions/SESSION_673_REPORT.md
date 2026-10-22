# Session 673 report: the live set

22 October 2026, from about 10:03 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **The chain's four public tables are in the live set**, loaded whole and proved by the loader: `utility_service_territories` 11,893 rows, `interconnection_durations` 3,098, `interconnection_durations_summary` 1,365, `grid_peak_vs_capacity` 56 (16,412 in all; "match" for each, CSV against Supabase, and for the sources registry, 398 rows). Each carries its row-level license, `public`, from coverage. The database: 2,331.3 MB before, 2,334.0 MB after, against a limit of 7,500.
- **The names the code machine's session 718 reads from `coverage.csv` are fixed:** `utility_service_territories`, `interconnection_durations` (with `interconnection_durations_summary`), `grid_peak_vs_capacity`. `hifld_substations`, `hifld_transmission_lines`, `utility_large_load_tariffs` and `nerc_reserve_margins` are not written (sessions 668 to 670 and 672: no publisher, no key, no terms), so `coverage.csv` holds no row for them.
- **The gates, each run alone and its exit code read:** the validator on the four files (0 each, with the branch's validator, which knows the unit `month`); `build_coverage.py --only` on the four (0); `docs/coverage.md` regenerated for them, with the Method column (session 674) filled for the 81 tables a note names.
- No page reads these tables; every page is in review. A load of a table a live page reads would need rule 8's snapshots; none did.

## Pulls against their ceilings

None: the loader writes to Supabase, it reads no publisher.

## Decisions made without you

- The four tables moved from `catalogue_hold` to `full` in `live_set.yaml`: small, public, and the All grids tab's sources. The Redivis hold of `release_v1.py` stays (the old account's draft is full); the Stanford upload is session 680's.
- The load ran from the main checkout with the branch's `live_set.yaml`, `coverage.csv` and `sources.csv` copied in for the run and main's put back after, since the branch has not landed.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/supabase/live_set.yaml`, `tests/test_session667.py`, `tests/test_session671.py`. New: this report. On the data machine only: `runs/c043/load.out`, `runs/c043/load_dry.out`.
