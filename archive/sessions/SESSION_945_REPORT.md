# Session 945 report: a gap of the siting review (a node's wires utility, by county)

23 October 2026, from 11:25 UTC, on lab-desktop (the data machine), a session of `queue/done/053-day-23-october-data-world-energy-dams-solar-projects.md`. Model spend USD 0. Pulls: none (four tables held).

## Read these first

- **The code machine's latest state read first:** main's `docs/reviews/siting-gaps.md` (chain 073's 1081 section and chain 052's 931 section) and the log to session 1086 (chain 074 taken, then withdrawn; no row changed). Open after them: a node's wires utility, substations and lines, large-load tariffs, a 2026 sub-region table, a node's bus.
- **The row taken: a node's wires utility,** open since chain 072 because the CDR names no EIA plant number. The county `ercot_node_places` gives and EIA-861's service territories close it in part, without a ruling: `ercot_node_wires_utilities` (derived, method `docs/methods/ercot_node_wires_utilities.md`), 569 nodes in 148 counties, each with the utilities EIA-861 lists in its county (median 4), the delivery-only companies among them and those outside Texas RE.
- **What it says:** 517 nodes have a delivery-only company in their county, 287 exactly one, 191 two, 39 three; 52 nodes in 18 counties have none (21 in Bexar: the City of San Antonio and cooperatives own their wires); 128 have a utility outside Texas RE in the county (Entergy Texas, Southwestern Public Service and others).
- **The cross-check:** by load zone the companies are the ones the grid's map gives (all 53 Houston nodes have CenterPoint; 127 of 138 North nodes Oncor; 89 of 138 South nodes AEP Texas Central); Bexar, Pecos and Harris read by hand from the territories equal the table.
- **The other rows:** substations and lines, and a node's bus, need a public map of ERCOT's network the ERW does not hold (and ERCOT's own are behind the robots-held paths); large-load tariffs wait on an OpenEI key; a 2026 sub-region table has no public source found. The state section is added to `docs/reviews/siting-gaps.md`; the table's rows are left as written.

## Decisions made without you

- **County, not site:** a utility serving the county may not serve the node's site, and where two delivery-only companies serve it the table names both. Said in the header, the note and the state section.
- **Transmission-only companies are not given:** they have no customers and so no territory. The table names the utilities a load in the county connects through, not the owner of the line a generator ties into.
- **The method note written in this session,** as session 931's was; session 946 checks it with the chain's others.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/derived/ercot_node_wires_utilities.py`, `docs/methods/ercot_node_wires_utilities.md`, `tests/test_session945.py` (3 tests), this report.
- Changed: `docs/reviews/siting-gaps.md` (a state section), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c053/s945/`, `runs/s945*`.
