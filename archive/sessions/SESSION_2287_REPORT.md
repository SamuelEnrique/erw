# Session 2287 report: natural gas plant processing (EIA), a second source of the session's own choosing

24 October 2026, from 05:23 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: EIA's API, 4 requests of 20 (below).

## Read these first

- **Why this source:** gas processing plants strip the liquids (ethane, propane and the rest) from the gas the wells produce. Their volumes link the ERW's gas production tables to its natural gas liquids. The ERW did not hold them, no chain plans them, and EIA's verdict is on record.
- **One table written, validated, archived, in coverage (sectors gas and products), in the release package, both holds:** `eia_gas_plant_processing_annual`, 1967 to 2024, with one 2025 row (the U.S. extraction loss, which EIA already gives), 5,829 rows, 276 series.
  - Gas processed and extraction loss in MMcf; liquids extracted in kbbl.
  - For the U.S., the states, EIA's offshore areas, and EIA's pairs of a processing state and an origin state. A pair's geo is its first state.
  - Area codes are accepted by EIA's forms (NUS, S<state>, an R area, or either with -S<state>); any other stops the run.
  - Each row carries the time EIA served its page.
- **The cross-check** (`runs/c104/s2287/cross.py`, `cross.out`):
  - The states' own totals come to 0.925 to 1.000 of the U.S. over 56 years of gas processed (0.980 in 2024). The rest is EIA's offshore areas.
  - Extraction loss: 0.930 to 1.000 (0.979 in 2024).
  - The U.S. processed 18.5 trillion cubic feet in 1970, 14.6 in 1990 and 27.1 in 2024. Liquids extracted rose from 573 million barrels in 1990 to 2,563 in 2024.
  - `eia_gas_balance_annual` carries none of these series, so no comparison with it.

## The pulls

1. EIA's route metadata and one page of 2023 and 2024 (2 requests).
2. The trial's two pages. The write reused them (0 requests).

## Errors

- **The connector's generator dropped the units line** with the template's area block; it was put back before the trial.

## Decisions made without you

- **EIA's gas plant processing as the session's own choice,** for the reasons above.
- **A year, not a month,** to keep the table to its 5,829 rows.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_gas_plant_processing.py`, `tests/test_session2287.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c104/s2287/`, `runs/s2287_*`, `warehouse/raw/eia_gas_plant_processing/`.
