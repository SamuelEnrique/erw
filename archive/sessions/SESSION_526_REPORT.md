# Session 526 report: the state electricity profiles' capacity

21 October 2026, from 20:59 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/028-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_state_capacity.py`: each state's net summer capacity by producer type and energy source, a year**, from EIA's API v2 (route `electricity/state-electricity-profiles/capability`), as `eia_state_capacity_annual`.
  - 56,719 rows: 2,671 series, 1990 to 2024, in MW.
  - Producer types: electric utilities, independent producers, and both.
  - Energy sources: all, each fuel, and each fuel's parts (NGCC within NG, for one). The header says a sum must take one level and leave ALL and TOT out.
- **Cross-check, an order of magnitude** (`runs/s526/crosscheck.py` on the data machine): each state's 2024 net summer capacity (both producer types, all sources) against `eia860m_operating_generators`, today's nameplate, summed by state.
  - 51 areas; median ratio 0.895, middle half 0.854 to 0.917.
  - The U.S.: 1,230,416 MW against 1,417,946 MW.
  - Net summer capacity runs below nameplate, and the fleet has grown since 2024.
- **Written under the data lock** (21:14 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`power`). Tests: `tests/test_session526.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 14 of 20 | the route and a 2024 page (the probe); the trial (12 pages) |

## Files

- New: `warehouse/connectors/eia_state_capacity.py`, `tests/test_session526.py`, this report. Changed: the shared metadata, holds and package.
