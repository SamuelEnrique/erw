# Session 2025 report: seven days of the data jobs

23 October 2026, from 19:13 UTC, on lab-desktop (the data machine), a session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`, in session 962's form, run while session 2024's upload was being proved (it writes nothing to the warehouse). Model spend USD 0.

## Read these first

- **Failed steps by day** (`erw_health`, read only, `runs/c057/s2025/byday.py`):

  | Day | Steps | Failed |
  |---|---|---|
  | 17 October | 668 | 13 |
  | 18 October | 684 | 15 |
  | 19 October | 763 | 3 |
  | 20 October | 777 | 5 |
  | 21 October | 632 | 0 |
  | 22 October | 731 | 1 |
  | 23 October (to 19:13 UTC) | 593 | 1 |

- **One new failed step, after session 2011's read:** today's GitHub daily run (39965879843, `daily prices`, 16:28 UTC), step `package tests`: `test_coverage_has_one_row_per_table_and_the_documented_columns`, "assert np.False_". **Its cause:** the coverage the run committed (`dd9c3a27`, 16:19 UTC) held one row whose validator status was not a pass, `usgs_mcs_critical_minerals`, "blocked (1 errors)", the stale 692-row row from before chain 055 landed (session 2003 found it, and session 988 wrote the table again). The run's job concluded success: the package tests' failure is recorded, not fatal, and the run's metadata was committed.
- **Already put right on main, nothing to fix here:** main's coverage now holds `usgs_mcs_critical_minerals` at 1,600 rows, "pass" (chains 055 and 056 landed at 17:14 and 18:21 UTC), and no row of main's coverage fails the test's pattern. Tomorrow's run should not repeat it. Chain 059's agent traced the same row independently. The pattern behind it, a branch's validator put back before the coverage build so a new unit's row is written "blocked", is fixed in the write scripts chains 057 to 059 now use (`runs/c058/write_table.sh` and its copies).
- **GitHub's record:** the same 7 failed runs since 17 October as session 2011 found, all `code branch` (the last, chain 051's `task/909-922-data` at 09:01 UTC); no data workflow failed as a run.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.github.com | 2 of 30 | the failed run's jobs and steps; the failed runs since 17 October (this machine's token, reads only) |
| Supabase (`erw_health`, read only) | 8 | seven days of rows, and today's again |

## Decisions made without you

- **Run out of order,** while session 2024 held the lock and waited on Redivis.
- **No code change:** the fault was a stale record on main, gone since the landings, not this repository's code.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c057/s2025/`.
