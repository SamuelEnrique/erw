# Session 2090 report: the gas pipelines between states (EIA's state-to-state capacity)

23 October 2026, from 21:20 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, run before sessions 2088 and 2089 had finished (2088's notes were being drafted, and 2089's licenses round reads this session's publisher). Model spend USD 0. Pulls: 4 requests of 15 (below).

## Read these first

- **One table written, validated, archived, in coverage (sector gas, public), in the release package, both holds:** `eia_state_to_state_capacity`, each interstate pipeline's capacity at each state border it crosses, a year a row, 1990 to 2025 (33 years), from the data sheet of EIA's U.S. State-to-State Capacity workbook (the January 2026 issue, released 3 February 2026): 19,311 rows for 686 crossings, including those to and from Canada and Mexico. Capacity in `bcf/d` (EIA's MMcf a day over 1,000, kept as published beside it), with each crossing's regions, states, counties, pipeline and EIA's notes.
- **Rows kept as EIA lists them:** 12 crossings repeat within a year (a pipeline on two lines between the same counties, each with its own capacity), so a crossing's id carries its place among the repeats; two rows EIA lists twice, field for field, are kept twice, as EIA's own pivot tables sum them.
- **The cross-check against `eia_gas_pipeline_projects`** (the completed interstate projects that cross a state border, by year in service): the capacity the border table adds each year (the rise over the year before, summed over the crossings) moves with the projects' capacity, correlation 0.74 from 2015 to 2025; both are highest in 2017 and 2018 (28,090 and 21,707 MMcf a day added, against 11,465 and 11,161 of projects) and lowest in 2022 and 2023 (897 against 897; 2,283 against 894). The border table adds more in the busy years, likely because a project counted once in the tracker raises the capacity at every border it crosses.

## The pulls

1. `www.eia.gov/robots.txt` (read 244). 2. The natural gas data page (its "Pipelines" links). 3. The January 2026 workbook. 4. The connector's trial: the data page again (asked fresh), the workbook reused.

## Decisions made without you

- **`bcf/d`, not a new unit:** the unit vocabulary has `MMcf` and `bcf/d`, not MMcf a day; the published figure stays in `x_capacity_mmcfd`.
- **The crossing as EIA gives it,** not summed by state pair: EIA's own sheets sum it by state and region, and a reader can.
- **The newest issue taken from the page's links,** so a later run reads the next January's.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_state_to_state.py`, `tests/test_session2090.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (244), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c068/s2090/`, `runs/license_reads/s2090/`, `runs/s2090*`, `warehouse/raw/eia_state_to_state/`.
