# Session 856 report: EIA-930's demand by sub-region, 2019, written

23 October 2026, from 02:03 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **`eia930_subba_demand_hourly_2019` is written: 687,952 rows, 82 sub-regions, 2019-01-01T00 to 2019-12-31T23 UTC**, from session 855's saved pages (89 reused) and 56 new requests. Validated, archived (`20261023T020803Z-local`), in coverage (sector power, public), in the release package, both holds, named by the sub-region note. 55 of the 82 sub-regions are short of 8,760 hours, 30,368 hours in all, more than any later year: EIA's sub-region reporting was filling in during 2019.
- **The cross-check against `ferc714_area_demand_2019`** (57,658 hours in common), sub-regions summed by parent and hour, median ratio: CAISO 0.9976, ERCOT 0.9999, NYISO 0.9997, PJM 1.0052, SPP 0.9977, ISO-NE 0.9835; PNM 1.44 as every year. ERCOT's sub-regions meet FERC's hours on only 5,251 hours of 2019.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 56 of 90 | August to December 2019 (session 855's 89 pages reused) |

## Decisions made without you

- None beyond the chain's.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session856.py`, this report and session 855's. Changed: `docs/methods/eia930_subba_demand.md`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`. On the data machine only: the saved pages, `runs/s855_*`, `runs/s856_*`, `runs/c046/s856_*`.
