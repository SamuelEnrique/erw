# Session 2292 report: LNG peak-shaving storage by state (EIA), a third source of the session's own choosing

24 October 2026, from 05:28 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: EIA's API, 4 requests of 20 (below).

## Read these first

- **Why this source:**
  - Utilities in the cold states (New England above all) fill LNG tanks in summer and draw them on winter's coldest days. These peak-shaving volumes are what keeps gas flowing when pipelines are full.
  - The ERW held the export terminals and underground storage, not these tanks. No chain plans them, and EIA's verdict is on record.
- **One table written, validated, archived, in coverage (sectors gas and LNG), in the release package, both holds:** `eia_lng_storage_annual`, 1969 to 2024, 3,074 rows, 81 series.
  - Additions to and withdrawals from LNG storage, in MMcf, for the U.S. and the states.
  - Each row carries the time EIA served its page.
- **EIA's "net withdrawals" series is not taken.** In most years it equals additions less withdrawals (for example, 2023 U.S.: 49,805 − 41,033 = 8,772), the reverse of its name. In some years it has the opposite sign: the U.S. in 2003 and 2006, Georgia in 2006. Tennessee's 1998 reads −1,746,367 MMcf. The docstring says a reader takes withdrawals less additions.
- **The cross-check** (`runs/c104/s2292/cross.py`, `cross.out`, `cross2.out`):
  - The states sum to the U.S. exactly, for additions (46 years) and withdrawals (45 years).
  - U.S. withdrawals were 62,431 MMcf in 1980, 51,513 in 2000, 34,286 in 2020 and 45,435 in 2024.

## The pulls

1. EIA's route metadata (annual only, 1969 to 2024), and a monthly sample request that EIA refused (the route has no monthly figures).
2. One annual page of 2023 and 2024.
3. The trial's page, asked twice (once with the net series, once without). The write reused the second (0 requests).

## Errors

- **The first trial took EIA's net series,** whose identity the cross-check found broken. It is now not asked for, and the trial was run again.
- **The first sample asked for monthly figures,** which this route does not have.

## Decisions made without you

- **EIA's LNG storage as the session's own choice,** for the reasons above.
- **EIA's net series left out,** for the reasons above.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_lng_storage.py`, `tests/test_session2292.py`, this report.
- Changed:
  - `warehouse/connectors/eia_gas_plant_processing.py` (a space)
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c104/s2292/`, `runs/s2292_*`, `warehouse/raw/eia_lng_storage/`.
