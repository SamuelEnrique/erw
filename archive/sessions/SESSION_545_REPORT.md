# Session 545 report: net metering by state

21 October 2026, from 21:45 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/029-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_net_metering.py`: each state's net-metered capacity and customers by sector, a year**, from EIA's API v2 (route `electricity/state-electricity-profiles/net-metering`), as `eia_net_metering_state_annual`.
  - 16,226 rows: 1,031 series, 2013 to 2024. Capacity is in MW and customers are a count.
  - EIA gives four technologies a year from 2013 to 2019 and only "All Technologies" from 2020. The technology is kept as a slug in the entity.
- **Cross-check, internal**: the five sectors sum to EIA's all-sector figure in all 624 state-years (within 0.5%), and the states sum to the U.S. every year.
  - No table the ERW holds measures net-metered capacity. So the cross-check against behind-the-meter owners that the chain proposed was not made: those are sales, not capacity.
- **Written under the data lock** (21:48 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0.
  - Its source row conflicted with session 544's as a patch, and `runs/union_resolve.py` kept both.
- **Held** from `/data` and Redivis v1. Sector rule (`power`). Tests: `tests/test_session545.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 4 of 10 | the route and a 2024 page (the probe); the trial (2) |

## Files

- New: `warehouse/connectors/eia_net_metering.py`, `tests/test_session545.py`, this report. Changed: the shared metadata, holds and package.
