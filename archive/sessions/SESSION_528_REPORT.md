# Session 528 report: natural gas production by state

21 October 2026, from 21:07 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/028-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_gas_production_state.py`: natural gas production by state, a month**, from EIA's API v2 (route `natural-gas/prod/sum`), as `eia_gas_production_state_monthly`.
  - 47,805 rows: 184 series, January 2001 to July 2026, in `MMcf` a month.
  - Five series: gross withdrawals, marketed production, dry production (the U.S. only), vented and flared, and shale gas (within gross withdrawals).
  - **Not taken**: EIA's per-day series, since the vocabulary has no `MMcf/d` and they are the month's volume over its days. Also not taken: the withdrawals from gas, oil and coalbed wells, repressuring, nonhydrocarbons removed and extraction loss.
- **R98 is EIA's "Other States"**, a sum of small states that EIA also gives one by one, not an offshore area as I first wrote. The first cross-check found it: the states, the Gulf of America and R98 together ran 2.6% above the U.S.
  - Without R98, the states and the Gulf equal the U.S.: 307 months, median 1.0000, range 0.9912 to 1.0000.
  - The connector's description was corrected before the write, and the header says to leave R98 out of a sum.
- **Cross-check**: Pennsylvania, West Virginia and Ohio's marketed production (as bcf/d) against the Appalachian region of `eia_basin_production_monthly`: 139 months, median ratio 0.999.
- **Written under the data lock** (21:14 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. Its metadata conflicted with session 525's, next to it, and `runs/union_resolve.py` kept both. **Held** from `/data` and Redivis v1. Sector rule (`gas`). Tests: `tests/test_session528.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 14 of 30 | a 2026 page (the probe); the trial (13 pages) |

## Files

- New: `warehouse/connectors/eia_gas_production_state.py`, `tests/test_session528.py`, this report. Changed: the shared metadata, holds and package.
