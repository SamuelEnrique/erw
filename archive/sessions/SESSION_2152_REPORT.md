# Session 2152 report: six held ERCOT tables described

23 October 2026, from 23:51 UTC, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`, run while sessions 2153 to 2155 worked. Model spend USD 0. Pulls: none (Supabase for the lock).

## Read these first

- **Six method notes for ERCOT tables that had none,** chosen among the 86 source tables without one (none named in a note on main or on chains 079 and 090's branches). The Method cells are filled (`runs/c057/method_cells_locked.sh`).

| Note | Rows | Entities, variables | First and last hour (UTC) |
|---|---|---|---|
| `docs/methods/ercot_as_prices.md` | 338,492 | 5, 1 | 1 January 2018 to 24 October 2026 |
| `docs/methods/ercot_as_quantities.md` | 4,800 | 5, 1 | 3 September to 13 October 2026 |
| `docs/methods/ercot_dam_cleared_energy.md` | 432 | 1, 1 | 23 September to 11 October 2026 |
| `docs/methods/ercot_wind_solar_forecast.md` | 2,730 | 1, 4 | 27 September to 30 October 2026 |
| `docs/methods/ercot_wind_solar_output_hourly.md` | 52,608 | 1, 2 | 1 January 2023 to 1 January 2026 |
| `docs/methods/ercot_wind_solar_hsl_hourly.md` | 9,120 | 12, 4 | 28 September to 23 October 2026 |

- **Written by a helper agent in the chain's worktree, checked here:** every count, entity and variable count and range recomputed from the tables (all as written); each note's `Tables:` line; no em or en dash. Five agree with `coverage.csv`. The forecast table holds 96 rows more than its coverage row, from the run of 23 October.
- **Found while writing the notes, recorded in them and left in the code:**
  1. **All six tables come from `/misapp` and `/misdownload` on www.ercot.com,** which ERCOT's robots file disallows (read 170, session 2002). This session counts **thirteen connectors** using those paths, `iso_prices.py`'s ERCOT document list among them. It is **the standing question of chain 046's note** (twelve connectors then), still yours: pause, read ERCOT's MIS terms, or a key for ERCOT's public API.
  2. `ercot_as_prices.py`, `ercot_as_quantities.py` and `ercot_wind_solar_forecast.py` never ask `iso_prices.paused()`, which CLAUDE.md requires (checked: none of the three names it).
  3. The forecast connector calls ERCOT's solar report (type 13483) NP4-745-CD. The note finds ERCOT's file names carry NP4-737. That was **not checked against ERCOT** here, since the list is under `/misapp`.
  4. The forecast docstring's "as it stood a day ahead" holds only for the next day's hours. Its ceiling is checked after the file that passes it. The wind and solar history's "never asked for again" does not hold on the GitHub runner, which keeps no raw files.
  5. `ercot_as_quantities` is on no schedule, though its docstring speaks of growing a day each run. `ercot_dam_cleared_energy` has had no weekly run since 10 October, and a default run will not recover 11 to 16 October.
- **Not fixed here:** the descriptions and the missing pause checks are for a code chain, as session 2060 left CAISO's. The robots question is yours.

## Errors

- None.

## Decisions made without you

- **ERCOT's six,** a group of source tables, chosen among the 86.
- **No code changed** in ERCOT's connectors: they run daily, and their access is a standing question.

## For Samuel's ruling

- **ERCOT's robots file and the thirteen connectors that use `/misapp` and `/misdownload`** (chain 046's question, the count updated).

## Files

- New: the six notes above, this report.
- Changed: `docs/coverage.md` (the Method cells).
