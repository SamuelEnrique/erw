# Session 682 report: seven green days, the data jobs

22 October 2026, from about 10:16 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **"Scheduled jobs green for 0 days"**: `warehouse/health.py days --from 2026-10-15 --to 2026-10-22` (written to `runs/c043/health_days.json`, not to the site's copy) counts the streak back from 22 October, whose daily run had not yet run at 10:16 UTC ("missing: daily prices"). The site's `/internal/health` reads `site/data/health_days.json`, last written 21 October 16:24 UTC: green for 0 days, counted to 20 October.
- **21 October is the first day of the week with no failed step** (572 rows of `erw_health`, 0 failed); 22 October has none so far (264 rows). 15 to 20 October had 3 to 15 failed steps a day.
- **Nearly every failure of the week is a Redivis limit, not this repository's code:**
  - **The export cap** ("Cannot export more than 100GB within a 30 day period, unless the dataset's owner has configured an export billing project"): the daily run's restore of `state_generation_mix_monthly` (5 days), the Roundup's restore of `weather_obs_hourly` (2), the data machine's `erw_headers` merge (3).
  - **The old account's full storage**: the data machine's store steps (`dm_*_stores`, "redivis exited 1"), 3 a day for 11 tables from 16 to 18 October, and `ercot_all_hub_prices_history` on 20 October.
- **The rest, each once or a few times, none since 20 October:** the data machine's live set step failed on `sources` (5, 15 to 20 October), its commit step's `git pull --rebase` (4, "committed here, not pushed"), the daily run's Supabase load of `datacenter_projects` and `energy_deals` (19 October), EIA-930's incomplete data for five areas (20 October, a source gap), `generation_mix` without its input (20 October, the same day's EIA series), and one package test, `test_large_table_by_partition[nyiso_zone_load_hourly]` (20 October).
- **GitHub's own record** (`actions/runs?status=failure` since 15 October): 6 failed runs, all of `code branch` (the code machine's checks); no data workflow run failed as a run. A data job's step failure is recorded as a row of `erw_health` inside a run that ends green.
- **Nothing was fixed:** the limits are the owner's (the export cap and the storage are both in `For Samuel's ruling` of earlier sessions), and the code faults stopped before this session with no failure to reproduce.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 1 of 30 | the failed runs since 15 October |
| Supabase (`erw_health`, read only) | 16 | eight days of rows, twice (`health.py days`, and the failed rows with their reasons) |

## Decisions made without you

- The streak was computed to a file of this session's, not to `site/data/health_days.json`, which the site reads: that is the daily summary's to write.
- The package test's failure of 20 October (`nyiso_zone_load_hourly` by partition) was not chased: it passed in the daily runs after, and the table is the runner's.

## For Samuel's ruling

- Redivis's export cap stops the daily run's restore and the Roundup's whenever it is reached; the export billing project Redivis names ("unless the dataset's owner has configured an export billing project") is the owner's to set, or the daily run's move to the Stanford dataset (session 660).

## Files

- New: this report. On the data machine only: `runs/c043/health_days.json`, `runs/c043/failures_682.out`, `runs/c043/gh_failed_runs.json`.
