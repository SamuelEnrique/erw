# Session 917 report: a siting gap filled, ERCOT's transmission projects by a node's county

23 October 2026, from 08:37 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: none of 10.

## Read these first

- **The gap row:** "ERCOT nodes | Node panel | transmission projects by county" (`docs/reviews/siting-gaps.md`, session 703), whose source the review named as ERCOT's TPIT report. Both halves are now public ERW tables: TPIT itself (`ercot_transmission_projects`, session 852) and a node's county (`ercot_node_places`, session 901). No ruling is needed and no robots-held path is asked.
- **One derived table written, validated, archived, in coverage (sector power, public), in the release package, both holds, with its method note** (`docs/methods/ercot_node_transmission.md`): `ercot_node_transmission`, 569 nodes in 148 counties. For each node, TPIT's project phases that begin or end in its county, counted by sheet (future, planned, completed, cancelled), and over the open (future and planned) phases the distinct projects, new and upgraded circuit miles, highest voltage and earliest projected in-service date.
  - 548 of the 569 nodes are in a county with at least one open phase. The most: Harris 157 open phases, Bexar 79 (649 new circuit miles, up to 765 kV), Brazoria 66, Dallas 52, Cameron 46 (583 miles, 765 kV).
  - 11 of the 148 counties have no TPIT phase (zeros, since TPIT lists every project the owners report).
- **The cross-check:** Harris, Pecos and Bexar counted by hand from `ercot_transmission_projects` equal the table in every status.
- **The siting gaps' file has a state section for this chain,** naming the row filled for the placed nodes; the tab does not yet draw it.

## Decisions made without you

- **A line between two counties counts in both,** and its miles go to both: the table answers how much transmission work touches a node's county, not the network's length. The method note says so.
- **One row a placed node,** with the same ids as `ercot_node_places`, so that the node panel joins it directly; a county table would hold the same counts once.

## For Samuel's ruling

- None new.

## Errors

- **A reader with `comment="#"` cuts rows.** The first hand count read `ercot_transmission_projects` with pandas' `comment="#"`, which ends a row at a '#' inside a value: 66 TPIT phases hold one (switch and line numbers), and 52 lost their counties, so the hand count was one short in Pecos. The builder reads past the header lines only and was right. The same fault had touched session 911's cross-check (3 EHA rows, 163 of EIA-860M's): its report is corrected, and every cross-check of this chain now reads with `runs/c051/readt.py`. The package's readers already never use `comment="#"` (`package/src/erw/api.py`, `backends.py`).

## Files

- New: `warehouse/derived/ercot_node_transmission.py`, `docs/methods/ercot_node_transmission.md`, `tests/test_session917.py` (3 tests), this report.
- Changed: `docs/reviews/siting-gaps.md` (a state section), `archive/sessions/SESSION_911_REPORT.md` (its cross-check), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c051/s917/`, `runs/c051/readt.py`, `runs/c051/write_derived.sh`, `runs/s917*`.

## Addendum by session 922

- Chain 072 (the old laptop, session 1048, landed at about 08:10 UTC while this chain ran) draws the same gap row on the tab, counting TPIT's phases by a placed node's county in `warehouse/derived/siting_page.py`. The two counts were made apart and agree: the table equals the tab's `site/data/siting/nodes.json` in all 137 counties the tab lists by future, planned and completed phases; the 11 others are this table's zero counties. The table is the warehouse's copy of the same figures, for the package and Redivis; the siting gaps' state section says so.
