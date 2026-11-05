# Session 559 report: petroleum product stocks

21 October 2026, from 23:13 UTC, on lab-desktop (the data machine), a session of `queue/done/031-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_petroleum_stocks.py`: ending stocks of petroleum products for the U.S., the PADDs and PADD 1's three sub-districts, a month**, from EIA's API v2 (route `petroleum/stoc/ts`), as `eia_petroleum_stocks_monthly`.
  - 18,247 rows: 63 series, January 2001 to July 2026, in `kbbl`.
- **The route is not what its name and the chain file said.** On 21 October it holds total gasoline, distillate fuel oil with its three sulfur grades, propane and propylene, and residual fuel oil. There is no crude oil and no breakdown by type of storage.
  - The connector says so, and its header names the levels to keep apart in a sum.
  - Crude and storage types are left to a route that holds them.
- **Cross-check**: the U.S. stocks at each month's end against `eia_petroleum_stocks_weekly`'s week ending within 3 days of it, 307 months.
  - Distillate (MDISTUS1 against WDISTUS1): median 1.013, middle half 1.002 to 1.028.
  - Gasoline (MGTSTUS1 against WGTSTUS1): median 1.009, middle half 1.003 to 1.017.
  - The monthly survey runs about 1% above the weekly estimate. That it is the fuller count is my reading, not EIA's statement.
- **Written under the data lock** (23:17 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. Its metadata met session 556's next to it, and the union resolver kept both; there are no duplicate rows. **Held** from `/data` and Redivis v1. Sector rule (`oil;products`). Tests: `tests/test_session559.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 5 of 20 | a June 2026 page (the probe); the trial (4) |

## Files

- New: `warehouse/connectors/eia_petroleum_stocks.py`, `tests/test_session559.py`, this report. Changed: the shared metadata, holds and package.
