# Session 544 report: each state's electricity supply and disposition

21 October 2026, from 21:44 UTC, on lab-desktop (the data machine), the third session of `queue/done/029-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_state_disposition.py`: each state's electricity supply and disposition, a year**, from EIA's API v2 (route `electricity/state-electricity-profiles/source-disposition`), as `eia_state_source_disposition_annual`.
  - 37,738 rows: 52 areas, 1990 to 2024.
  - Each of EIA's 21 columns is a variable (with "-" as "_"):
    - generation by utilities, independent producers and combined heat and power, with EIA's subtotals and total;
    - imports and total supply;
    - sales by full-service and energy-only providers, facility direct, direct use, exports, estimated losses, net interstate trade, unaccounted and total disposition, all in MWh;
    - the net trade index, a ratio.
  - The header names the subtotals and totals to leave out of a sum.
- **Cross-check**: each state's total net generation against `eia_state_generation_monthly` summed by year. 1,224 state-years (2001 to 2024): median ratio 1.0000, all within 1%. The U.S. in 2024 is 4,308.6 TWh, EIA's total that session 524 compared against.
- **Written under the data lock** (21:48 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`power`). Tests: `tests/test_session544.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 2 of 20 | the route (the probe); the trial (one page holds every year) |

## Files

- New: `warehouse/connectors/eia_state_disposition.py`, `tests/test_session544.py`, this report. Changed: the shared metadata, holds and package.
