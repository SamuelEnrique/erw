# Session 525 report: natural gas in underground storage by state

21 October 2026, from 20:57 UTC, on lab-desktop (the data machine), the third session of `queue/done/028-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_gas_storage_state.py`: natural gas in underground storage by state, a month**, from EIA's API v2 (route `natural-gas/stor/sum`), as `eia_gas_storage_state_monthly`.
  - 55,015 rows: 205 series, January 2001 to July 2026.
  - Five series: working gas, base gas, the total (working and base), injections and withdrawals, in EIA's `MMcf`.
  - Not taken: EIA's change in working gas and net withdrawals, which follow from these. A region (R<code>) has the geo US.
- **Cross-checks** (`runs/s525/crosscheck.py` on the data machine):
  - the Lower 48's working gas (the U.S. less Alaska) at each month's end against `eia_gas_storage_weekly`'s Lower 48 figure for the week ending within 3 days of it: 200 months (2009 to 2026), median ratio 0.999, middle half 0.993 to 1.006;
  - the states summed against the U.S.: 307 months, equal every month.
- **Written under the data lock** (21:13 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`gas`). Tests: `tests/test_session525.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 14 of 30 | the process facet (1); the trial (13 pages) |

## Files

- New: `warehouse/connectors/eia_gas_storage_state.py`, `tests/test_session525.py`, this report. Changed: the shared metadata, holds and package (with 524 and 526 to 528).
