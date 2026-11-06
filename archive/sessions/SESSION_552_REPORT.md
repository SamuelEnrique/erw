# Session 552 report: natural gas proved reserves by state

21 October 2026, from 22:07 UTC, on lab-desktop (the data machine), a session of `queue/done/030-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_gas_reserves.py`: dry natural gas proved reserves and their changes by state and area, a year**, from EIA's API v2 (route `natural-gas/enr/dry`), as `eia_gas_reserves_annual`.
  - 19,232 rows: 561 series, 1977 to 2021, in `bcf`.
  - Eleven processes: EIA's "expected future production" (its proved reserves, as `proved_reserves`), adjustments, revision increases and decreases, sales, acquisitions, extensions, extensions and discoveries, new field and new reservoir discoveries, and production.
  - The same areas as session 551.
- **Cross-check** (`runs/s551/crosscheck.py`): the Lower 48 and Alaska equal the U.S. in all 45 years. The states and the federal offshore are a median 0.9994 of the U.S., low in a few early years (down to 0.45).
- **Held** from `/data` and Redivis v1. Sector rule (`gas`). Tested with 551 in `tests/test_session551.py`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 6 of 10 | a 2021 page (the probe); the trial (5) |

## Files

- New: `warehouse/connectors/eia_gas_reserves.py`, this report. Changed: the shared metadata, holds and package.
