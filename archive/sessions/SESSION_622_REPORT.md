# Session 622 report: one more source: EIA's movements between PADDs by rail and by tanker and barge

22 October 2026, from 03:17 UTC, on lab-desktop (the data machine), a session of `queue/done/038-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_padd_rail_barge_movements_monthly`: 56,182 rows, 586 series, January 2010 to July 2026.** Movements of crude oil and petroleum products between PADDs, from two routes of EIA's Petroleum Supply Monthly:
  - **by rail** (`petroleum/move/rail`, `rail_receipts`): 20,406 records, 10 products;
  - **by tanker and barge** (`petroleum/move/tb`, `tanker_barge_receipts`): 36,108 records, 50 products, with PADD 1's three subdistricts.
  - All in `kbbl`. EIA's area pair `<receiving>-<origin>` stays in the series id, and EIA's series name says both areas.
- **Why this source**: the ERW holds crude oil's pipeline movements between PADDs (`eia_padd_crude_pipeline_flows`), but not the other modes. These two routes complete the picture for crude by rail and for products by water. Both are small, in a unit the vocabulary holds, and need no ruling.
- **Cross-checks**:
  - For tanker and barge, the total of crude oil and products (EP00) equals crude (EPC0) plus products (EPP0) on all 2,101 pair and month keys, to the barrel.
  - Crude by rail between PADDs, a year: 5.7 million barrels in 2010, 289.1 million in 2014 (its peak), 86.5 million in 2024. This is the course of the Bakken crude-by-rail boom and its decline.
- **From 2010, not each route's first month**: both routes' full histories were about 24 pages, beyond the session's 20 requests. Tanker and barge before 2010 is left for a later session.
- **Written under the data lock** (03:24 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (56,182 rows archived).
  - The metadata patch met session 617's row of `eia_petroleum_snd_monthly` in three files: the patch was made against main's older row (475,869 rows), the branch holds 617's (523,835).
  - A union would have kept both rows. Instead, the branch's lines were kept and only the new table's line was added (`runs/s622/resolve_ours_plus.py`, sessions 549 and 601's way). Each table has one line in each file.
  - The release step was then run again from the branch's package: `licenses.py check` 0 problems (283 tables).
  - **Held** from `/data` and Redivis v1. Sector rule `oil;products`. Tests: `tests/test_session622.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 15 of 20 | a January 2026 page of each route, the trial (13) |

## Files

- New: `warehouse/connectors/eia_padd_movements.py`, `tests/test_session622.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage, sources and the archive manifest.
