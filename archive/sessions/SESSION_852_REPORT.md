# Session 852 report: ERCOT's transmission projects

23 October 2026, from 01:43 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **`ercot_transmission_projects` is written: 2,122 project phases** from ERCOT's Transmission Project and Information Tracking report (the public edition, "future projects as of 7/13/2026", updated 17 July 2026): 1,424 future, 358 planned, 262 completed, 78 cancelled, by 50 transmission owners (or owner pairs). An events table: the in-service date (actual where ERCOT gives one, else projected), the owner, the sheet as status, and ERCOT's fields (title, description, from and to, kV, new and upgraded circuit miles, MVA, Mvar, the counties of the start and the end, tier, RPG and RTP numbers). Validated, archived, in coverage (sector power, public), in the release package, both holds. This fills "transmission projects by county" for ERCOT's nodes (`siting-open-2026-10-23.md`, item 12).
- **Left out on purpose:** the "TSP/Company Contact" column and the owners' contact sheet (people's names, addresses and telephone numbers), which the warehouse has no need of; this edition has no costs.
- **ERCOT's marks:** `9999-01-01` stands where a project has no actual date (19 rows): not taken as a date, ERCOT's cell kept in `x_actual_in_service`. Five project phases are given twice with every field the same: kept once and counted (chain 030's rule).
- **The cross-checks:** 1,930 of the 2,122 rows name a county; of the 189 county names, 188 are among the 254 Texas counties of `utility_service_territories`, and the one that is not is ERCOT's spelling "Stonwall" (Stonewall County). All four wires utilities of `texas_delivery_charges` own projects here (as first owner: Oncor 505, CenterPoint 398, AEP Texas Central 248 and North 137, TNMP 62). The future list holds 41 phases at 765 kV with 2,667 new circuit miles.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.ercot.com | 4 of 8 | the probe's planning page and workbook, then the trial's page and workbook into `warehouse/raw/ercot_tpit/`, which the write reused (ERCOT's robots file allows `/gridinfo/` and `/files/docs/`, session 850) |

## Decisions made without you

- An events table (one row a project phase), the event's date the in-service date, rather than a series.
- People's contact details not taken.
- ERCOT's spelling of county names kept as given ("Stonwall"); the cross-check names it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ercot_tpit.py`, `tests/test_session852.py` (4 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c046/s852/`, `runs/s852_*`, `runs/license_reads/s852/`.
