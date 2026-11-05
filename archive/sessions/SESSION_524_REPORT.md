# Session 524 report: EIA-923's back years

21 October 2026, from 20:43 UTC, on lab-desktop (the data machine), the second session of `queue/done/028-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia923_plant_fuel_annual` now runs from 2001 to 2024**: 872,492 rows, 15,500 plants (4,647 in 2001, 13,258 in 2024). Session 510 held 2020 to 2024.
- **The connector's default years are 2001 to 2024**, and its ceiling is 130. The pages of 2020 to 2024, saved by session 510, were reused.
- **Cross-checks** (`runs/s510/crosscheck.py` on the data machine, run on the new table):
  - every plant's ALL row against the sum of its fuels: 180,659 plant-years, all within 1 MWh;
  - the U.S. total each year against `eia_state_generation_monthly`: equal to the tenth of a TWh from 2001 to 2016 (2001: 3,736.6 against 3,736.6). From 2017 the plants run 0.2% to 0.5% above (2017: 4,044.6 against 4,035.4; 2024: 4,325.0 against 4,308.6).
  - Why the later years differ was not established. It may be how EIA's monthly table counts some small or new plants.
- EIA's API answered with two 504s, each asked once more. The trial took 27 minutes.
- **Written under the data lock** (21:13 UTC) from the saved pages (0 requests). The validator, coverage and archive exited 0. The table's release row was replaced.
- Tests: `tests/test_session524.py`, 2.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 71 of 130 | 2001 to 2019 (the trial, two 504s asked again); the write reused them |

## Files

- New: `tests/test_session524.py`, this report. Changed: `warehouse/connectors/eia923_plant_fuel.py`, `docs/redivis/release-v1/`, and the shared metadata (with sessions 525 to 528).
