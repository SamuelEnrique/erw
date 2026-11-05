# Session 560 report: another public source; PHMSA refused, EIA's energy efficiency programs taken

21 October 2026, from 22:31 UTC (PHMSA's probe, run early) and 23:23 UTC, on lab-desktop (the data machine), a session of `queue/done/031-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **PHMSA's pipeline incident data: refused.** `www.phmsa.dot.gov` answers HTTP 403 both to its robots file and to its data page for incidents and accidents. That is an access control, and it was not worked around, so the source ends there (`runs/s560/phmsa.md` on the data machine).
- **Chosen instead: EIA's energy efficiency programs by state** (route `electricity/state-electricity-profiles/energy-efficiency`, Form EIA-861's demand-side management). It is a public EIA source the ERW did not hold, and it bears on demand, which the ERW's large-load work reads.
  - `warehouse/connectors/eia_energy_efficiency.py` writes `eia_energy_efficiency_state_annual`: 19,740 rows, 520 series, 2013 to 2024.
  - Variables: energy savings (MWh), potential peak savings (MW), customer incentives and all other costs (USD, EIA's thousand dollars times 1,000).
  - EIA's two time periods are kept in the entity: "Reporting Year" (2013 to 2019) and "Expected Life Cycle of Programs".
- **Cross-check, internal**: the sectors sum to EIA's all-sector figure in all 987 state-periods, and the states sum to the U.S. in every year. The U.S. reporting-year savings run from 24.7 TWh (2013) to 28.6 TWh (2019).
- **Written under the data lock** (23:25 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0. **Held** from `/data` and Redivis v1. Sector rule (`power`). Tests: `tests/test_session560.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.phmsa.dot.gov | 2 | robots file and the data page, both 403 (counted in session 554's note) |
| api.eia.gov | 4 of 20 | the profiles' routes; the efficiency route and a 2023 page; the trial (1) |

## Files

- New: `warehouse/connectors/eia_energy_efficiency.py`, `tests/test_session560.py`, this report. Changed: the shared metadata, holds and package.
