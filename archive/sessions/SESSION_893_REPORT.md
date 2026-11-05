# Session 893 report: seven days of the data jobs, and the one fault since 20 October fixed

23 October 2026, from 05:42 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`, in chain 043's session 682's form. Model spend USD 0.

## Read these first

- **Failed steps by day** (`erw_health`, read only):

  | Day | Steps | Failed |
  |---|---|---|
  | 16 October | 674 | 13 |
  | 17 October | 668 | 13 |
  | 18 October | 684 | 15 |
  | 19 October | 763 | 3 |
  | 20 October | 777 | 5 |
  | 21 October | 632 | 0 |
  | 22 October | 731 | 1 |
  | 23 October (to 05:43 UTC) | 150 | 0 |

  `warehouse/health.py days --from 2026-10-16 --to 2026-10-23` (written to `runs/c048/s893/health_days.json`, not to the site's copy) counts the streak as 0 days, because of 22 October's one failure.
- **16 to 20 October, the causes session 682 named, none since:**
  - Redivis's export cap on the daily run's and the Roundup's restores (`weather_obs_hourly`), and on the data machine's header merge (`dm_zone_redivis`).
  - The old account's full storage on the data machine's store steps (`dm_*_stores`, "redivis exited 1", three a day for ten tables to 18 October, `ercot_all_hub_prices_history` on 20 October).
  - The live set step on `sources` (4).
  - The commit step's `git pull --rebase` (3).
  - The daily run's package test on `nyiso_zone_load_hourly` (2), its Supabase load of `datacenter_projects` and `energy_deals` (1), and one EIA-930 and generation mix failure on 20 October.
- **The one failure since 20 October, a fault of this repository's code, fixed:** on 22 October the daily run's package test failed on `test_price_board_table_units_freq_license_sector[carb_auction_allowance_prices]`, asserting "public" == "internal".
  - Session 324 made the table public (`carbon_auctions.py`, CARB's verdict "may be public"), and the daily run's coverage took the flag on 22 October; `package/tests/test_erw.py` still expected "internal".
  - The expectation is now "public"; the test's 13 price board cases pass when run from the main checkout.
  - A new repository test (`tests/test_session893.py`) reads the package test's expected flags and checks them against `coverage.csv`, so such a drift fails at a landing, not in a daily run. Without the fix, the 23 October daily run would have failed the same way.
- **GitHub's record** (`actions/runs?status=failure` since 16 October, 1 request): 6 failed runs, all of `code branch` (the code machine's checks, 19 to 21 October); no data workflow failed as a run.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 1 of 30 | the failed runs since 16 October |
| Supabase (`erw_health`, read only) | 24 | eight days of rows, three times (the days, the failed steps, the days' counts) |

## Decisions made without you

- The streak written to this session's file, not to `site/data/health_days.json`, which the daily summary writes.
- The Redivis limits of 16 to 20 October not chased: they are the owner's (the export billing project and the old account's storage, already in earlier sessions' rulings), and none has recurred since 20 October.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session893.py`, this report.
- Changed: `package/tests/test_erw.py` (CARB's expected flag).
- On the data machine only: `runs/c048/s893/` (the scripts, the days' file, the failed steps, GitHub's answer).
