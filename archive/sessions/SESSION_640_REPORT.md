# Session 640 report: EIA-930's demand by sub-region, 2021, the first part

22 October 2026, from 06:56 UTC, on lab-desktop (the data machine), a session of `queue/done/041-morning-22-october-sources.md`. Model spend USD 0.

## Read these first

- **2021's pages through July are saved; nothing is written yet, as planned.** Session 641 writes the year from both sessions' pages.
  - `python warehouse/connectors/eia930_subba.py --year 2021` ran from the main checkout (06:56 to 07:11 UTC) and reached its ceiling of 89 requests.
  - January to July were read whole, from 55,104 records (February) to 61,008 a month.
  - EIA answered HTTP 504 once; it was asked once more after 60 seconds and answered.
- **The yearly table's two holds** are in. `tests/test_session612.py` checks them.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 89 of 90 | 2021, January to part of August, with one retry |

## Files

- New: this report. Changed: `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `tests/test_session612.py`.
