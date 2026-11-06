# Session 901 report: an ERCOT node's county and zone (a derived table)

23 October 2026, from 06:43 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: none.

## Read these first

- **One derived entities table written, validated, archived, in coverage (sector power, public), in the release package, both holds, with its method note** (`docs/methods/ercot_node_places.md`, linked from coverage's Method column): `ercot_node_places`. It places 569 of `node_basis_daily`'s 873 resource nodes in a county and an ERCOT load zone, from the units ERCOT's Capacity, Demand and Reserves report (`ercot_cdr_units`, session 872) lists at the same station. This closes part of the siting gaps' "A node's zone, hub, wires utility and county" (session 733): the county and the zone.
- **The match:**
  - A node's station code is its settlement point's name up to the first "_"; a unit's is its unit code up to the first "_".
  - A node takes the county and zone only when every unit at its station agrees.
  - Left out and counted, never guessed: 295 nodes whose station no CDR unit carries, and 9 whose station's units give two counties or zones. Hubs and load zones are not resources and are left out.
- **Plausible by class, the only check open:** wind nodes fall mostly in the West (61), Coastal (20) and Panhandle (18) zones, gas nodes in the South (42), North (38) and Houston (30). No other public table gives a node's county to compare.
- **Not given: the wires utility.** The CDR names no EIA plant id, so `eia860_plants_annual`'s transmission owner cannot be joined without a guess.

## Decisions made without you

- `entity_type` `generator` for a resource node (the resource ERCOT settles there).
- The station code as the join, the only key the two tables share.
- A one-table derived write script (`runs/c049/write_derived.sh`). The first write stopped at coverage, as the builder had not registered its source; the source is now registered as other derived builders do it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/derived/ercot_node_places.py`, `docs/methods/ercot_node_places.md`, `tests/test_session901.py` (2 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c049/`, `runs/s901*`.
