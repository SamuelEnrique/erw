# Session 1046 report: the tables as they land

23 October 2026, about 07:50 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1046. Model spend USD 0. No request to a publisher; no warehouse data written; no build. Read: `warehouse/metadata/coverage.csv` on main and on the data machine's `origin/task/895-908-data` (chain 049, sessions 895 to 908, its gate "code branch" run 39919055887 in progress at 07:47 UTC, so not yet on main). The two tables below were rebuilt from the archive's bucket into `runs/archive_restore/` (`warehouse/archive/restore.py --from-bucket`), as the chain's rule allows, never into `warehouse/output/`.

## Landed (on chain 049's branch, merging when its gate passes)

| Table | License | Rows | Window | For |
|---|---|---|---|---|
| `eia411_capacity_margins_annual` (session 895, method `docs/methods/eia411.md`) | public | 2,924 | summer 1990 to summer 2027 (actual to 2016, EIA's projections 2017 to 2027 from its last release, November 2016); 16 NERC assessment areas | 1047 |
| `ercot_node_places` (session 901, method `docs/methods/ercot_node_places.md`) | public | 569 | one snapshot, 23 October 2026 06:46 UTC; 569 of node_basis_daily's 873 resource nodes placed by county and load zone | 1048, 1049 |

Two facts that shape 1047 and 1048:

- **EIA-411 is not a current assessment.** Its newest actual year is 2016; 2026 is a projection made in 2016. And its "capacity margin" is of two kinds: from 2015, MISO's, PJM's, SPP's, TRE's and FRCC's projected margins are reserve margins (over demand), the rest capacity margins (over resources) (the method note's cross-check).
- **`ercot_node_places` gives no wires utility**: the CDR names no EIA plant id. Every one of its 569 nodes is a node of the tab's `nodes.json` (873 nodes); 304 are not placed (295 with no CDR unit at their station, 9 whose units disagree).

## Not landed

`ercot_settlement_points`, `hifld_substations`, `hifld_transmission_lines`, `utility_large_load_tariffs`, and a 2026 sub-region table (`eia930_subba_demand_hourly` holds whole years 2019 to 2025 and a live 90 days, 24 July to 21 October 2026). Also held and public, from chain 046: `ercot_cdr_units` (1,772 units) and `ercot_transmission_projects` (2,122 events).

## The landing

Landed with sessions 1043 to 1061 in one push: `wip/1042-allgrids` gated by `scripts/land_check.py` at `a8a91dde` (freeze, main merged, task branches, the clean-copy suite 6,224 tests OK, npm ci, the build: pass; check-values: 12 failures, all the chain's known three: the ten license-held floors, `/digest` before the day's issue, and the 21 October Digest's revised WTI; every All grids value matched). As the rules say, the same commit was built locally on its own and checked by hand: check-routes 0 (225 pages in review, 0 failed), check-cross-checks 0 (92 passed), check-csp 0 (97 pages, 0 violations). Main then gained one queue file only (data chain 052's), merged without a third gate (`3306941d`). Snapshot `c072a-before` as its own command at 08:58 UTC; pushed to `task/1042-1061-allgrids` after the ancestry check; merged by run 39928557187 as `cbf8662e`; production served the node list's county filter (`data-node-county`) at 09:18 UTC (9 minutes of probing); `c072a-after` and `compare`: **0 differences** on the 25 pages (every page is in review: a visitor sees the in-review page), expected.

## Decisions made without you

1. **The tables read from chain 049's branch, not main**, since its gate was running: 1047 and 1048 are wired from the archive's copies, and this chain lands only after chain 049 has merged.

## For Samuel's ruling

- None new.
