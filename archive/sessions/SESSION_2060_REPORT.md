# Session 2060 report: six held CAISO tables described

23 October 2026, from 20:11 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: none.

## Read these first

- **111 of the source tables in `coverage.csv` had no method note** (by `build_coverage.method_notes()`, chain 058's unlanded notes counted too). This session wrote six, CAISO's:
  - `docs/methods/caiso_area_load_hourly.md` (266,340 rows, 6 areas, 17 September 2021 to 10 October 2026)
  - `docs/methods/caiso_as_prices.md` (229,440 rows, 8 series, 14 July 2023 to 23 October 2026, Pacific days)
  - `docs/methods/caiso_battery_storage.md` (365,472 rows, 3 series, 24 August 2025 to 23 October 2026)
  - `docs/methods/caiso_curtailment_daily.md` (25,120 rows, 8 series, 1 May 2014 to 21 October 2026)
  - `docs/methods/caiso_dam_cleared_energy.md` (9,727 rows, 1 series, 1 September 2025 to 11 October 2026)
  - `docs/methods/caiso_wind_solar_forecast.md` (344,617 rows, 12 series, 1 June 2023 to 23 October 2026)
- **Written by a helper agent in the chain's worktree, checked by this session:** every count and range recomputed from the tables (all as written), each note's `Tables:` line, no em or en dash. Four of the six drafts were committed early, inside session 2058's commit, by an over-broad `git add docs/` while the helper was still writing them; this session's commit holds the finished six.
- **The notes' own checks:** the five areas sum to the system total in every hour (one hour, 31 August 2024 17:00 UTC, missing from all six); 6 to 8 April 2025 missing from all eight ancillary series (session 65's "no data" gap); stand-alone plus hybrid batteries equal the total in only 3,180 of 121,824 intervals (differences to 1,182 MW).
- **Descriptions corrected to the code, text only** (no figure, rule or request changed; 43 test modules, 783 tests, pass):
  - `caiso_dam_cleared.py` said each run asks "the halves of this month and the last": from the 1st of the month 14 days back, so the last month only in a month's first 14 days; and a half month's zip, not a month's.
  - `caiso_as_prices.py`: its default start is 2024-09-01, and the table holds hours from 14 July 2023 (session 273's `--start`).
  - `caiso_outlook.py`: the interval start is CAISO's "Time" column, not "Interval Start".
  - `curtailment.py`: CAISO's curtailment reason (local or system) is in the rows from 1 January 2022, not "2024 on" (its docstring, a comment and the table's header line, which takes the new words at the next run).
  - `caiso_wind_solar_forecast.py`: the ceiling counts the rows kept from the three hubs after each answer.
- **Left as found, for Samuel (below):** `curtailment.py` fills each reason with 0 across a workbook's dates, so in January to March 2022 local plus system fall short of the total (solar by 751,278 MWh on 90 days, wind by 31,580 MWh on 83); and four CAISO connectors (`caiso_as_prices.py`, `caiso_outlook.py`, `caiso_wind_solar_forecast.py`, `curtailment.py`) do not ask `paused_sources.csv` before a request, as CLAUDE.md says every connector should (CAISO is not paused). `caiso_outlook.py`'s header calls stand-alone and hybrid "its two parts", which the rows do not bear out; and its docstring's clock-change rule (276 and 300 intervals) is not seen in the rows, which hold neither clock-change day.
- **Two older notes name two of these tables in their text** (`curtailment.md`, `capacity_and_ancillary.md`) without a `Tables:` line; the new notes stand beside them.
- **The Method cells** of the six are filled (`runs/c057/method_cells_locked.sh`); `caiso_wind_solar_forecast`'s coverage row moved forward to this machine's copy (344,617 rows, today's run).

## Errors

- **The over-broad `git add docs/`** in session 2058 (above).

## Decisions made without you

- **The notes written by a helper agent and checked here,** as in sessions 2004, 2018 and 2023.
- **Descriptions corrected, code left:** the curtailment fill and the missing pause checks change a daily table's figures or a connector's behaviour, which is not a notes session's to do.

## For Samuel's ruling

- **`caiso_curtailment_daily`'s zero-filled reasons** (January to March 2022): leave the reasons empty where CAISO gives none (the table's figures change), or keep. A page may read this table, so a change waits for you.
- **The pause check in four CAISO connectors:** add it (a code chain's change).

## Files

- New: the six notes above (four of them first committed in session 2058's commit), this report.
- Changed: `warehouse/connectors/caiso_dam_cleared.py`, `caiso_as_prices.py`, `caiso_outlook.py`, `curtailment.py`, `caiso_wind_solar_forecast.py` (descriptions), `docs/coverage.md`, `coverage.csv`.
- On the data machine only: `runs/c066/s2060/`.
