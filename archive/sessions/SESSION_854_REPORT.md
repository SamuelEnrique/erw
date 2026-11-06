# Session 854 report: generation with a signed interconnection agreement, derived

23 October 2026, from 01:50 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Two derived tables from `lbnl_interconnection_queue`** (Queued Up, 2026 edition), written, validated, archived, in coverage (sector power, public, tier derived), in the release package, both holds; method `docs/methods/interconnection_agreements.md`, linked from coverage's Method column:
  - `interconnection_agreements_signed`: 2,522 requests still in the queue (active or suspended), with a signed agreement and no operation date;
  - `interconnection_agreements_by_grid`: 438 rows: by grid and for the U.S., the signed MW and requests beside the MW still in the queue and the signed share; by grid and fuel; by grid and year of agreement.
- **Two marks of a signed agreement:** Berkeley Lab gives the study phase "IA Executed" and an agreement date, and neither covers the other (1,101 requests both, 1,188 the phase only, 357 the date only, of 9,181 still in the queue). Either counts; `signed_by` says which. 124 that give an operation date are left out.
- **What it says:** 499 GW of the 2,002 GW still in the queue have a signed agreement (24.9 percent). ERCOT 133 GW (29.6 percent of its queue), CAISO 94 GW (49.3), MISO 67 GW (19.2), PJM 44 GW (31.4), West 74 GW (14.3).
- **The cross-checks:** the grids sum to the U.S. row, each grid's fuels to the grid, and in every grid the signed MW are no more than the MW still in the queue. A comparison with ERCOT's CDR is not like with like: the CDR counts its planned additions at ELCCs, these are nameplate MW (the method note says so).

## Decisions made without you

- A request counts with either mark of an agreement (the phase or the date), rather than the date alone the chain named.
- The queue's state dated 2025-01-01 (`freq` `P1Y`), as the file holds requests to the end of 2025.
- Not loaded into the live set (no ruling names it); held from Redivis until a person uploads it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/derived/interconnection_agreements.py`, `docs/methods/interconnection_agreements.md`, `tests/test_session854.py` (3 tests), this report. Changed: `warehouse/metadata/build_coverage.py` (sector and tier), `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c046/s854/`, `runs/c046/write_derived_pair.sh`, `runs/s854*`.
