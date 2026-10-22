# Session 612 report: EIA-930's demand by sub-region, 2025, the first part

22 October 2026, from 01:43 UTC, on lab-desktop (the data machine), a session of `queue/done/037-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **2025's pages through July are saved; nothing is written yet, as the chain file planned.** Session 613 writes the year from both sessions' pages.
  - `warehouse/connectors/eia930_subba.py` has a year mode: `--year 2025` reads the year in twelve monthly windows, each paged on its own, and writes `eia930_subba_demand_hourly_2025`. Its ceiling is 89 requests a run. A run that reaches it writes nothing, and its saved pages answer the next run.
  - The run (01:44 to 01:50 UTC) read January to July whole: from 55,770 records (February) to 61,736 (May) a month. It reached its ceiling in August's pages.
- **The yearly table's sector rule (`power`) and both holds** are in, ready for 613's write. Tests: `tests/test_session612.py`, 4.

## Decisions made without you

- **Monthly windows rather than one window for the year.** Each month's pages are their own requests, so a page saved in this session is the same address the next session asks for. One window of 750,000 records would have been paged by offset over the whole year, where a late change in EIA's data would move every later page.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 89 of 90 | 2025, January to part of August (the trial, run from the main checkout) |

## Files

- New: `tests/test_session612.py`, this report. Changed: `warehouse/connectors/eia930_subba.py`, `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`.
