# Session 625 report: natural gas exports and imports by country, a month

22 October 2026, from 03:51 UTC, on lab-desktop (the data machine), a session of `queue/done/039-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_gas_trade_country_monthly`: 30,337 rows, 207 series, January 1973 to July 2026.** U.S. natural gas exports and imports by country, from two routes of EIA's Natural Gas Monthly:
  - exports by country (`natural-gas/move/expc`): 23,713 records;
  - imports by country (`natural-gas/move/impc`): 16,010 records.
  - `volume` (`MMcf`) and `price` (`USD/Mcf`).
  - The mode (pipeline, LNG by vessel, by truck, compressed, re-exports) and the country are in EIA's series id and its name (the node).
- **The whole history fit the ceiling**: 39,723 records, 9 pages.
- **Cross-checks**:
  - **The countries against the U.S. total of the same mode** (volumes): 1,823 of 1,856 mode and month keys within 1 MMcf. The 33 that differ are LNG by vessel (27), re-exports (3) and LNG imports (3).
  - **U.S. LNG exports against `eia_lng_exports_monthly`'s terminals summed by month** (132 months from November 2013): median ratio 0.999, from 0.980 to 1.382, never equal to the MMcf. The two tables come from different EIA routes (by country, and by point of exit); the difference is not looked into.
- **Written under the data lock** (03:54 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (30,337 rows archived). Each table has one row in the metadata files. Release rows added; `licenses.py check` 0 problems (284 tables). **Held** from `/data` and Redivis v1. Sector rule (`gas`). Tests: `tests/test_session625.py`, 4.

## Decisions made without you

- **Variables named by unit** (`volume`, `price`), the mode in the entity and node, as in session 614, rather than twenty process words of the ERW's own.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 13 of 30 | a January 2026 page of each route, each route's count, the trial (9) |

## Files

- New: `warehouse/connectors/eia_gas_trade.py`, `tests/test_session625.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage, sources and the archive manifest.
