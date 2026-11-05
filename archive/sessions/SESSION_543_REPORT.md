# Session 543 report: refinery inputs and utilization, weekly

21 October 2026, from 21:41 UTC, on lab-desktop (the data machine), the second session of `queue/done/029-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_refinery_weekly.py`: refinery inputs, capacity and utilization for the U.S. and the five PADDs, a week**, from EIA's API v2 (route `petroleum/pnp/wiup`, the Weekly Petroleum Status Report), as `eia_refinery_weekly`.
  - 50,753 rows: 59 series, January 2010 to the week ending 16 October 2026.
  - Variables: net input and refinery net input by product, operable capacity (`kbbl/d`), and utilization (a ratio, EIA's percent divided by 100).
  - Each value is stamped on EIA's week-ending date, as `eia_petroleum_supply_weekly` is.
- **From 2010**: the route runs back to 1982, and 2010 on fitted the ceiling with room for retries.
- **Cross-check**: three series this route shares with `eia_petroleum_supply_weekly` (the U.S. crude input, WCRRIUS2, and PADDs 1 and 3, WCRRIP12 and WCRRIP32) are equal on all 875 weeks that both hold. Utilization runs from 0.366 to 1.125: EIA reports above 100% in some weeks, and those are kept as published.
- **Written under the data lock** (21:48 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`oil;products`). Tests: `tests/test_session543.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 12 of 20 | a September 2026 page (the probe); the trial (11) |

## Files

- New: `warehouse/connectors/eia_refinery_weekly.py`, `tests/test_session543.py`, this report. Changed: the shared metadata, holds and package.
