# Session 873 report: EIA-860's plants, with each plant's wires owner

23 October 2026, from 03:31 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md`. Model spend USD 0.

## Read these first

- **`eia860_plants_annual` is written: 17,349 plants of 2025** (EIA-860's final 2025 release, `xls/eia8602025.zip`; the early release and `/archive/` not read): each plant's place (address, county, coordinates), operator, balancing authority, NERC region, sector, grid voltages, and the transmission or distribution system owner it connects to, with every other column of EIA's plant sheet (37 in all). Validated, archived, in coverage (sector power, public), in the release package, both holds.
- **Why:** EIA-860M's generator tables already carry county and coordinates; what they lack is the plant's wires utility, the gap "a node's wires utility (TSP)" of `siting-gaps.md`. In Texas 1,522 of 1,533 plants name it (Oncor 426, AEP Texas Central 229, CenterPoint 212, TNMP 88, LCRA 71 and others).
- **The cross-check:** 14,699 of the 14,767 plants of `eia860m_operating_generators` are here (99.5 percent), with the same county in every one.
- **A request spent for nothing (mine):** the probe script keeps the first 20 MB of a body, so its copy of the 23.6 MB zip was cut short; the connector's own fetch saved it whole. 4 of 4 requests.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eia.gov | 4 of 4 | the page and the zip by the probe (the zip cut short), then the page and the zip by the trial, which the write reused |

## Decisions made without you

- Every column of EIA's sheet kept under its heading's name, rather than a chosen few.
- The plant table, not the generator file: EIA-860M already holds the generators.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia860_plants.py`, `tests/test_session873.py` (4 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c047/s873/`, `runs/license_reads/s873/`, `runs/s873_*`.
