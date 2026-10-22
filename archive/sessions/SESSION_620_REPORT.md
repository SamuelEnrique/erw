# Session 620 report: EIA-930's demand by sub-region, 2024, the first part

22 October 2026, from 02:53 UTC, on lab-desktop (the data machine), a session of `queue/done/038-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **2024's pages through June are saved; nothing is written yet, as planned.** Session 621 writes the year from both sessions' pages.
  - `python warehouse/connectors/eia930_subba.py --year 2024` ran from the main checkout (02:53 to 03:09 UTC), where session 612's year mode now is, and reached its ceiling of 89 requests in July's pages.
  - January to June were read whole, from 57,360 records (February) to 61,748 (May) a month.
- **EIA answered HTTP 502 or 504 three times** (April's page at offset 35,000; May's at 0 and 20,000). Each was asked once more after 60 seconds and answered; each retry counted against the ceiling.
- **The yearly table's two holds** are in (the sector rule `^eia930_subba_demand_hourly_\d{4}$` exists since session 612). `tests/test_session612.py` checks them.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 89 of 90 | 2024, January to part of July, with three retries |

## Files

- New: this report. Changed: `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `tests/test_session612.py`.
