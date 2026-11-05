# Session 557 report: natural gas supply and disposition by state

21 October 2026, from 23:05 UTC (its probes; the route answered 502s and the session was taken up again at 23:19), on lab-desktop (the data machine), a session of `queue/done/031-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_gas_balance.py`: each state's natural gas supply and disposition, a year**, from EIA's API v2 (route `natural-gas/sum/snd`, annual, the Natural Gas Annual), as `eia_gas_balance_annual`.
  - 11,274 rows: 460 series, 1997 to 2025, in `MMcf`.
  - Ten processes: total consumption, dry production, supplemental fuels, imports and exports in transit, interstate receipts and deliveries, storage injections and withdrawals, and EIA's balancing item.
- **Annual, not monthly.** The monthly form of the route holds only the U.S. balance (four rows a month) and the states' storage, which `eia_gas_storage_state_monthly` (session 525) already holds. The annual form holds the whole balance by state.
- **EIA's API answered the annual page with a 502 (and once with a page that was not JSON)**. The session went on to 558 and 559 and came back to it, and it answered then.
- **Cross-checks** (`runs/s557/crosscheck.py` on the data machine):
  - each state's total consumption against SEDS' natural gas consumption (NGTCB, at 1.036 TBtu per thousand MMcf): 1,428 state-years, median 1.005, middle half 0.995 to 1.014;
  - the U.S. dry production against session 528's monthly dry production summed by year: equal in all 25 years.
- **Written under the data lock** (23:21 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`gas`). Tests: `tests/test_session557.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 7 of 20 | a June 2026 monthly page; three tries at the 2024 annual page (two failed); the trial (3) |

## Decisions made without you

1. The annual form, since the monthly one repeats what the ERW already holds.

## Files

- New: `warehouse/connectors/eia_gas_balance.py`, `tests/test_session557.py`, this report. Changed: the shared metadata, holds and package.
