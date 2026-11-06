# Session 558 report: densified biomass (wood pellets)

21 October 2026, from 23:08 UTC, on lab-desktop (the data machine), a session of `queue/done/031-night-22-october-sources.md` (run before 557, whose route EIA was answering with 502s). Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_wood_pellets.py`: wood pellet prices, plants and employees, a month**, from three of EIA's `densified-biomass` routes (the Monthly Densified Biomass Fuel Report), as `eia_wood_pellets_monthly`.
  - 1,613 rows: 9 series, January 2016 to May 2026.
  - The domestic price by region (East, South, West and the U.S.) and the export price, in `USD/short_ton`; the number of plants and of full-time employees by region (`count`).
- **Not taken**: EIA's tonnages (sales, exports, production, capacity), since the vocabulary has no tonnage unit. That ruling is already asked (sessions 490 and 519). The decision was one table for the three routes, with the route's short name in the entity.
- **Cross-check, internal**: the regions' plants sum to the U.S. in 123 of 125 months and the employees in 116; the other months have a region EIA withholds. The domestic price runs from 115.76 to 267.68 a ton.
- **Written under the data lock** (23:11 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`power`). Tests: `tests/test_session558.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 7 of 20 | four routes' metadata (the probe); the trial (3) |

## Files

- New: `warehouse/connectors/eia_wood_pellets.py`, `tests/test_session558.py`, this report. Changed: the shared metadata, holds and package.
