# Session 626 report: underground natural gas storage capacity, a month

22 October 2026, from 03:55 UTC, on lab-desktop (the data machine), a session of `queue/done/039-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_gas_storage_capacity_monthly`: 23,980 rows, 123 series, January 1989 to July 2026.** From EIA's Natural Gas Monthly (route `natural-gas/stor/cap`, Form EIA-191).
  - Total underground storage capacity (`total_capacity`) and working gas capacity (`working_capacity`), both in `MMcf`, and the number of storage fields (`storage_fields`, `count`).
  - The areas are the states, the lower 48, the U.S. and EIA's storage regions. The early years use EIA's three AGA regions (R87 to R89: producing, eastern consuming, western consuming), which the first trial stopped on; they were added to the map.
- **Cross-checks**:
  - **The states against the U.S.**: all 633 process and month keys within 0.1%, 532 within 1 MMcf or 1 field.
  - **Working gas in storage** (`eia_gas_storage_state_monthly`) **against working capacity**, 5,552 state and U.S. months: median 0.61 of capacity. The U.S. is never above it (highest 0.858, October 2012).
  - In 91 state months the working gas is above the state's working capacity, Oregon from June to October 2012 among them (up to 1.17). EIA's capacity is a design figure; the months are kept as EIA gives them and not looked into further.
- **Written under the data lock** (03:59 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (23,980 rows archived). Each table has one row in the metadata files. Release rows added; `licenses.py check` 0 problems (285 tables). **Held** from `/data` and Redivis v1. Sector rule (`gas`). Tests: `tests/test_session626.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 7 of 15 | the count, a January 2026 page, the first trial (1, stopped at R87), the trial (4) |

## Files

- New: `warehouse/connectors/eia_gas_storage_capacity.py`, `tests/test_session626.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage, sources and the archive manifest.
