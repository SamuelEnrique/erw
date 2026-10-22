# Session 633 report: EIA-930's demand by sub-region, 2022, the first part

22 October 2026, from 05:22 UTC, on lab-desktop (the data machine), a session of `queue/done/040-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **2022's pages through July are saved; nothing is written yet, as planned.** Session 634 writes the year from both sessions' pages.
  - `python warehouse/connectors/eia930_subba.py --year 2022` ran from the main checkout (05:22 to 05:49 UTC) and reached its ceiling of 89 requests.
  - January to July were read whole, from 54,432 records (February) to 61,008 (July) a month.
  - EIA answered HTTP 502 twice and 504 once; each was asked once more after 60 seconds and answered.
- **The yearly table's two holds** are in. `tests/test_session612.py` checks them.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 89 of 90 | 2022, January to part of August, with three retries |

## Files

- New: this report. Changed: `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `tests/test_session612.py`.
