# Session 2053 report: seven days of the data jobs

23 October 2026, from 19:22 UTC, on lab-desktop (the data machine), the twelfth session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`, in session 962's form, run while session 2050's write waited for the data lock (chain 057's Redivis upload held it from 19:09 UTC). Model spend USD 0.

## Read these first

- **Failed steps by day** (`erw_health`, read only, `runs/c059/s2053/byday.py`, session 2011's):

  | Day | Steps | Failed |
  |---|---|---|
  | 17 October | 668 | 13 |
  | 18 October | 684 | 15 |
  | 19 October | 763 | 3 |
  | 20 October | 777 | 5 |
  | 21 October | 632 | 0 |
  | 22 October | 731 | 1 |
  | 23 October (to 19:22 UTC) | 601 | 1 |

- **One failed step since session 2011 read it:** today's `daily prices` run (39965879843, started 14:00 UTC on main's `7dbd3722`), step `package tests`, at 16:28 UTC: `test_coverage_has_one_row_per_table_and_the_documented_columns`, `assert np.False_`. The run itself succeeded (the step records its failure and the run goes on).
- **Its cause, found:** the assertion that fails with `np.False_` is the one that every table's `validator_status` reads "pass". At `7dbd3722`, main's `coverage.csv` carried `usgs_mcs_critical_minerals` as "blocked (1 errors)": a table with a new unit (`t`, `USD/kg`, Decision 56) whose coverage row had been built with a validator that did not yet know the unit. **Main's coverage holds no blocked row now** (`origin/main` at 19:22 UTC, 385 tables), so the next daily run should pass this test.
- **The same fault in this chain, found and fixed:** `runs/c058/write_table.sh`, which this chain copied, puts main's validator back before `build_coverage.py --only`, and the coverage step validates the table again. This chain's `noaa_climdiv_state_monthly` (unit `in`, Decision 60) was given the row "blocked (1 errors)" in session 2045. `runs/c059/write_table.sh` now keeps the branch's validator in through the coverage step; the row is rebuilt when the data lock is free (session 2054). Chain 058 had found and fixed the same order in its own script at 18:46 UTC, after this chain copied it, and rebuilt its two new-unit tables' rows; chain 057's copy was taken after that fix. Both were told, and both answered so.
- **GitHub's record:** 7 failed runs since 16 October, all of `code branch` (the last, chain 051's `task/909-922-data` at 09:01 UTC today); no data workflow failed as a run. Today's runs to 19:22 UTC: 209; of the first 100 listed, 41 `latest prices`, 40 `chain watch`, 11 `hourly network`, 6 `code branch` and 2 `daily prices`, all succeeded.
- **No fault of the repository's code to fix:** the fault is in the chains' write scripts under `runs/` (the data machine's, not in git), and the repository's validator and coverage builder did what they say. No test is added.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 4 of 30 | the failed runs since 16 October; today's runs; the failed step's run and its jobs (this machine's token for two, the public API for two) |
| Supabase (`erw_health`, read only) | 8 | seven days of rows, and today's failed row in full |

## Decisions made without you

- **The write script fixed in `runs/`, not a test added to the repository:** the repository's code is not at fault.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- On the data machine only: `runs/c059/s2053/`, `runs/c059/write_table.sh` (the validator's order).
