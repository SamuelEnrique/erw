# Session 872 report: ERCOT's resources with their county and zone, from the CDR

23 October 2026, from 03:28 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md`. Model spend USD 0. Pulls: none.

## Read these first

- **ERCOT's resource lists are posted under `/misapp`, which its robots file disallows; none was asked for** (chain 046's rule). The CDR workbook session 851 saved (posted under `/files/docs/`, allowed) holds a "Unit Details" sheet with each unit's ERCOT unit code, county and zone.
- **`ercot_cdr_units` is written: 1,772 units in 184 Texas counties**, each with its unit code (or its interconnection request number while planned), technology, fuel, CDR status (operating 1,442, planned 313, suspended 17; ERCOT's own code kept in `x_cdr_status`), resource attribute, county, zone, in-service date, installed capacity and the seasonal capability ERCOT counts for each season to 2030/2031. Validated, archived, in coverage (sector power, public), in the release package, both holds. No request.
- **What it fills:** "a node's county" for most ERCOT nodes: by station prefix (the part of a name before its first "_"), 65 percent of `node_basis_daily`'s 888 nodes and 78 percent of the 339 storage resources of `ercot_dam_esr_awards` find a CDR unit. "A node's wires utility (TSP)" stays open: the CDR does not name it.
- **The cross-check:** every county is a Texas county of `utility_service_territories` but ERCOT's "Hill & Limestone" (one unit on the line between two).

## Decisions made without you

- The CDR's unit sheet in place of ERCOT's resource lists, which the robots file keeps from the ERW.
- ERCOT's CDR statuses mapped to the data standard's (OPER and RMR to operating, PLAN to planned, MOTH and EXT to suspended), ERCOT's code kept.
- Station-prefix matching is shown as a cross-check only; no node is given a county in any table.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ercot_cdr_units.py`, `tests/test_session872.py` (3 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c047/s872/`, `runs/s872_*`.
