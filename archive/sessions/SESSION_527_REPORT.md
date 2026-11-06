# Session 527 report: crude oil production by state

21 October 2026, from 21:00 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/028-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_crude_production_state.py`: crude oil field production by state, PADD and federal offshore area, a month**, from EIA's API v2 (route `petroleum/crd/crpdn`), as `eia_crude_production_state_monthly`.
  - 25,644 rows: 43 series, January 2001 to July 2026.
  - Units: EIA's thousand barrels (`kbbl`, the month's volume) and thousand barrels a day (`kbbl/d`), as two variables.
- **The first trial stopped on a key given twice**, with nothing written. Alaska carries two series under one area code: the state (MCRFPAK) and its North Slope (MANFPAK) within it. The entity is now the area and EIA's series stem, and the header says the North Slope is within Alaska.
- **Cross-checks** (`runs/s527/crosscheck.py` on the data machine). STEO's table in the ERW holds no crude production series, so these are internal, plus one order of magnitude:
  - the U.S. against the five PADDs summed: 307 months, equal every month;
  - each per-day rate times the month's days against the month's volume:
    - every row of 3,000 kbbl a month or more is within 0.5%;
    - small producers' rates are given in whole kbbl/d, so all rows together are 79% within 5%;
  - Texas and New Mexico against the Permian region of `eia_basin_production_monthly`: the Permian is a median 0.770 of the two states' production.
- **Written under the data lock** (21:14 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`oil`). Tests: `tests/test_session527.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 7 of 20 | a 2026 page (the probe); the first trial's one page; the second trial's five more |

## Files

- New: `warehouse/connectors/eia_crude_production_state.py`, `tests/test_session527.py`, this report. Changed: the shared metadata, holds and package.
