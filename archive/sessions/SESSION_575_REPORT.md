# Session 575 report: wood pellets' feedstock costs

21 October 2026, from 23:46 UTC (the probe) and 23:57 UTC, on lab-desktop (the data machine), a session of `queue/done/033-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_wood_pellets_monthly` now holds the cost of the pellets' feedstocks**: 2,090 rows (477 new), 13 series, January 2016 to May 2026.
  - The cost by fuel type (sawmill residuals, roundwood and pulpwood, wood products manufacturing residuals, other residuals), in `USD/short_ton`.
  - It comes from a fourth route of session 558's connector (`densified-biomass/feedstocks-and-cost`), keyed by fuel type where the other three are keyed by region. The quantities in tons are not taken.
  - Withheld costs ("W") have no row.
- **Cross-check**: in all 124 months, the dearest feedstock costs less than the pellets' U.S. domestic price. Feedstock costs run from 18.29 to 49.33 a ton.
- **Written under the data lock** (23:57 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. The release row was replaced. Tests: in `tests/test_session574.py`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 3 of 10 | the route and a 2026 page (the probe); the trial (1; the other routes' pages reused) |

## Files

- New: this report. Changed: `warehouse/connectors/eia_wood_pellets.py`, `docs/redivis/release-v1/tables.csv`, `docs/coverage.md`, `warehouse/metadata/{coverage,archive_manifest}.csv`.
