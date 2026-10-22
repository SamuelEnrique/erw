# Session 667 report: utility service territories

22 October 2026, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **`utility_service_territories` is written: 11,893 utility and county pairs, 2,909 utilities, 56 states and territories**, EIA-861's 2025 `Service_Territory_2025.xlsx`, from the zip saved on 21 October (no request). Entities shape, a snapshot; validated (pass), archived, in coverage (sector power, public by its ERW verdict), registered in `sources.csv` as `eia:eia861_territory`.
- **The cross-check against `eia861_utility_sales` (2025)** is clean where it should be: of 1,238 utilities with bundled sales, 13 have no territory, all third-party solar owners (Tesla, Sunrun and others). The 303 utilities with sales and no territory are energy-only retailers (233) and power marketers (87); the 1,680 with a territory and no sales row are mostly short-form filers, whose sales EIA imputes (`runs/s667/crosscheck.out`).
- **Both holds:** `live_set.yaml`'s `catalogue_hold` and `release_v1.py`'s held list (in v1 by its license once uploaded). Session 673 decides the live set.
- **Its method note:** `docs/methods/utility_service_territories.md`. Tests: `tests/test_session667.py` (5).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| none | 0 | the zip saved by `eia861_sales.py` on 21 October; `--offline` |

## Decisions made without you

- The table is a snapshot of one year (2025), not a merge of years: EIA's earlier years are under `/archive/`, which its robots file disallows.
- A county is EIA's county name, with no FIPS code: the sheet gives none, and none is added.
- The new tables' metadata reached the branch as one combined coverage build for the chain's four tables (`runs/c043/write_new_tables.sh`), after per-table patches conflicted with each other.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_territories.py`, `docs/methods/utility_service_territories.md`, `tests/test_session667.py`, this report. Changed: `warehouse/metadata/build_coverage.py` (sector rule), `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`.
