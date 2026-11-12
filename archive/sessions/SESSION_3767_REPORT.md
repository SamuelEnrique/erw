# Session 3767 report: the derived tables' second pass (parked 193), with 3768

Energy Research Warehouse (ERW). Chain 211, sessions 18 and 19 of 24, data machine (lab-desktop), 12 November 2026. Opus 5.5. Model spend USD 0. Requests: none.

- **`iso_queue_snapshot_summary` in the live set:** it is listed in `warehouse/supabase/live_set.yaml` but held 0 rows live. Its load needs the data lock, which the catch-up run holds; it is done with the Redivis draft in session 3770 once the lock is free (see that report).
- **The weekly gas storage:** `eia_gas_storage_weekly` still ends 16 October (retrieved 24 October). The refresh is the daily run's Saturday step (`refresh_supply.sh`), and the runs of 7 November stopped at the merge tests. So it has not caught up, and `gas_balance_weekly` was not rebuilt. The next Saturday run (14 November) refreshes it.
- **The per-reactor outages** (`eia_nuclear_outages_generator_daily`, ending 21 October): EIA publishes them daily (API route `nuclear-outages/generator-nuclear-outages`, frequency daily), not monthly, so there is no monthly slot to add them to.
  - No step of the daily run or the data machine's run pulls them.
  - A daily pull of the 2015 window is about 60 requests under the connector's ceiling of 98. It needs an incremental window first.
  - Carried to chain 212 with that design.
- **CARB LCFS:** the newest week CARB holds is 14 September 2026, 59 days old on 12 November against the 28-day rule. The limit was not raised and the series was not marked discontinued:
  - The rule correctly says the publisher has not published, and the health table counts it as stale, not as a failure.
  - No CARB statement of discontinuance was read.

## Decisions made without you

- **CARB's 28-day rule kept.** Raising it to 60 would have written a 59-day-old table as fresh and hidden a real lag. The parked file allowed either way; this one keeps the signal.
- **The outage pull not scheduled.** A schedule added without an incremental window would spend about 60 requests a day re-reading pages already held.

## For Samuel's ruling

- None new.
