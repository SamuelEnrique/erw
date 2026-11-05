# Session 694 report: coal production by mine, a public source the ERW did not hold

23 October 2026, from 00:29 UTC, on lab-desktop (the data machine), a session of `queue/done/045-evening-22-october-data-resumed.md`. Model spend USD 0.

## Read these first

- **No OpenEI key** (`OPENEI_API_KEY` is not in this machine's `.env`), so the large-load tariffs wait, and the session took a public source the ERW did not hold, as the chain says.
- **`eia_coal_mine_production_annual` is written: 72,852 rows, 4,665 mines, 5,455 series, 2001 to 2024**: each mine's production (short tons) and average employees a year, with its MSHA number, county, operator, status and coordinates as EIA gives them (route `coal/mine-production`, the Annual Coal Report's mine file). Validated, archived, in coverage (sector coal, public), in the release package, both holds; method `docs/methods/eia_coal_mine_production_annual.md`, linked from coverage's Method column.
- **Why this source:** it is the mine-level layer under `eia_coal_production_annual` (session 685), which its method note named as missing; it places coal supply by county and coordinates beside the plants of `eia923_plant_fuel_annual`. The first choice, EIA's refiner prices of petroleum products (`petroleum/pri/refoth`), **ends at March 2022 on EIA's API** (351,962 records): a series no longer published was set aside after its probe.
- **The cross-check:** the mines' production summed by year equals EIA's U.S. total exactly in every year 2001 to 2024 (512.5 million short tons in 2024). By state and EIA region (655 state-years): median ratio 1.0000, 93.1 percent within 1 percent; the widest are Pennsylvania anthracite (`PAA`) and Arkansas in 2001, where EIA's aggregate places some coal in another region than the mine's own.
- **EIA's coal regions inside a state** (`KYE`, `KYW`, `PAA`, `PAB`, `WVN`, `WVS`) are put in their state's `geo` (`US-KY`, `US-PA`, `US-WV`); `x_state` keeps EIA's code. The trial found them (its first `geo` was `US-PAA`) before the write.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 14 of 20 | `refoth`'s metadata, two facets and its newest records (4); `mine-production`'s metadata and newest records (2); the trial's eight pages (8), which the write reused |

## Decisions made without you

- Mine-level coal production in place of the refiner prices, which EIA's API stops at March 2022.
- A production of 0 that EIA gives is kept (12,589 rows: preparation plants and idle mines); an empty figure has no row.
- The rank and mine type are in the key: a preparation plant can report as surface and as underground in one year.
- Labor hours are not taken, as session 685 decided for the state aggregates.

## For Samuel's ruling

- None new (the OpenEI key stays on the waiting list).

## Files

- New: `warehouse/connectors/eia_coal_mine_production.py`, `docs/methods/eia_coal_mine_production_annual.md`, `tests/test_session694.py` (6 tests), this report. Changed: `warehouse/metadata/build_coverage.py` (the sector rule), `warehouse/redivis/release_v1.py` and `warehouse/supabase/live_set.yaml` (the holds), `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c045/s694/`, `runs/s694_*`.
