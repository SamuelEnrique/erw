# Session 530 report: CO2 emissions by state, sector and fuel

21 October 2026, from 21:28 UTC, on lab-desktop (the data machine), the first session of `queue/done/029-night-22-october-sources.md` (its probe and trial run while chain 028's landing waited for its checks). Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_co2_state.py`: energy-related CO2 by state, sector and fuel, a year**, from EIA's API v2 (route `co2-emissions/co2-emissions-aggregates`), as `eia_co2_state_annual`.
  - 66,144 rows: 1,248 series, 1970 to 2022.
  - Sectors: commercial, electric power, industrial, residential, transportation and all. Fuels: coal, natural gas, petroleum and all.
  - In `tCO2` (EIA's million metric tons times 1,000,000). The header says a sum must take one level and leave the totals out.
- **Cross-check, an order of magnitude** (`runs/s530/crosscheck.py` on the data machine): the electric power sector's CO2 by state against EPA GHGRP's power plants (`epa_ghgrp_power_co2`) summed by state, 2010 to 2022.
  - 605 state-years: GHGRP over EIA, median 1.009, middle half 0.976 to 1.039.
  - The U.S. in 2022: 1,532 Mt (EIA) against 1,554 Mt (GHGRP).
- The first probe page came back as something other than JSON (a gateway's answer, I take it) and was asked once more.
- **Written under the data lock** (21:47 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`power;gas;oil;coal;carbon`). Tests: `tests/test_session530.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 18 of 20 | the route and two tries at a 2022 page (the probe); the trial (15) |

## Files

- New: `warehouse/connectors/eia_co2_state.py`, `tests/test_session530.py`, this report. Changed: the shared metadata, holds and package (with 543 to 545).
