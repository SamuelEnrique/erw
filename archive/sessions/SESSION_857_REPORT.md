# Session 857 report: EIA-930's demand by sub-region, its first months: none before 2019

23 October 2026, from 02:10 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **EIA holds no sub-region demand before 2019.** One request for the route `electricity/rto/region-sub-ba-data` from 2015-01-01T00 to 2018-12-31T23 (EIA's hour-ending periods), sorted by period, answered a total of 0 records. The first hour EIA holds is the first of `eia930_subba_demand_hourly_2019` (2019-01-01T00 UTC, session 856), so the series is complete from its start and no `_2018` table exists to write.
- The hours missing in 2019 (30,368, session 856) are EIA's sub-regions starting to report during that year, not a window the ERW did not ask for.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 1 of 60 | the count of 2015 to 2018 |

## Decisions made without you

- No table, and the ceiling's other 59 requests left unused.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c046/s857/requests.log`.
