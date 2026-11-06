# Session 551 report: crude oil proved reserves by state

21 October 2026, from 22:07 UTC, on lab-desktop (the data machine), a session of `queue/done/030-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_crude_reserves.py`: crude oil proved reserves and their changes by state and area, a year**, from EIA's API v2 (route `petroleum/crd/pres`), as `eia_crude_reserves_annual`.
  - 13,931 rows: 416 series, 1977 to 2021.
  - Eight processes: proved reserves, adjustments, revision increases and decreases, sales, acquisitions, extensions and discoveries, and production.
  - In `kbbl`, EIA's million barrels times 1,000.
  - Areas: states, the U.S., the Lower 48, and EIA's parts of states and offshore areas (Texas's districts, Louisiana's north and south, California's basins, New Mexico's east and west, federal and state offshore). The header says a sum takes one level.
- **Cross-check** (`runs/s551/crosscheck.py` on the data machine):
  - the Lower 48 and Alaska equal the U.S. in all 45 years;
  - the states and the federal offshore summed against the U.S.: median 0.9987. A few early years run lower (down to 0.45), when EIA gives fewer states.
- Made with session 552's connector by `runs/s551/make_connectors.py` (on the data machine) from session 550's.
- **Held** from `/data` and Redivis v1. Sector rule (`oil`). Tests: `tests/test_session551.py`, 5 (with 552's).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 4 of 10 | a 2021 page (the probe); the trial (3) |

## Files

- New: `warehouse/connectors/eia_crude_reserves.py`, `tests/test_session551.py`, this report. Changed: the shared metadata, holds and package.
