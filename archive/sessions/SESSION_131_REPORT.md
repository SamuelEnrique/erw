# Session 131 report: scheduled jobs and the freeze, and why the daily run ran long

## To finish

**The freeze is on** (`REVIEW_FREEZE`, 5 to 7 October). This session pushed `wip/131-freeze-scheduled` only, deployed nothing, loaded nothing and switched nothing on. The branch is from main (`e33f4e0`) and builds on no other. It changes three workflows, the daily script and the loader, so landing it changes what the next scheduled runs do (the loader fix at once; the hold not at all until its switch is turned). When `python scripts/freeze.py status` exits 0:

```bash
git checkout wip/131-freeze-scheduled && git fetch origin && git merge origin/main
node site/scripts/snapshot-live.mjs take before-131
git push origin wip/131-freeze-scheduled && git push origin wip/131-freeze-scheduled:task/131-freeze-scheduled
python runs/session118/watch_run.py task/131-freeze-scheduled 15
node site/scripts/snapshot-live.mjs take after-131 && node site/scripts/snapshot-live.mjs compare before-131 after-131
git push origin --delete wip/131-freeze-scheduled
```

- **What the comparison should show: nothing but the clock.** Nothing under `site/` changed.
- **Land it before 14:00 UTC if you can**, so that day's run uses the fixed loader. Take one more snapshot before that run and one after it: **the first run with the fix reads every table once and writes far less than usual**, and on the live pages only a "retrieved" time, if a page shows one, may read differently (point 4 below).
- **To switch the hold on, later and separately:** the six approvals in `docs/freeze_hold.md`, then one line, `enabled: true`, in `warehouse/config/freeze_hold.yaml`, by the same route.

## Verdict

**The freeze hold: built, tested, not switched on, as asked. Ready to switch on once you approve six things** (below). One part of it could not be tested here: a held run on GitHub's own runner. The first held day should be watched.

**The long run: cause found and fixed on this branch, with a test on real rows. Ready to land when the freeze ends.** Until it lands, each daily run will write all 336,332 rows of `ercot_as_prices` again and may record it as failed again. **The table is whole each time**; it is the record that is wrong, and the run that is long.

## Read these first

1. **The daily run was rewriting whole tables every day**, on each of the three days I have its records for. The loader's rule is to write only what changed, but it counted a row as changed when only its retrieval time was new, and a connector that rebuilds its table stamps every row with the run's time. On 3 October it wrote 182,950 rows of 542,074; on 5 October, 927,833 of 1,292,645.
2. **5 October's two "failed" tables were whole.** After writing every row of each, the loader's count of them timed out, and it recorded a failure. The same counts answered in 1.6 and 0.5 seconds on 6 October: 336,332 and 345,306 rows, equal to the files.
3. **4 October's failed table was a different fault, already fixed.** ERCOT changed a file from CSV to a workbook; session 113 fixed the connector on 5 October, and that is on main.
4. **The fix changes one thing a reader could see.** In the live set, a row's `retrieved_at` becomes the time of the load that last changed it, not of the last fetch. The CSV, the archive and Redivis are unchanged. I chose this over fixing each connector; it is your call to confirm.
5. **The hold is one switch, and it is off.** With it off, every scheduled job does exactly what it did before; a test compares the three kept-live jobs with main byte for byte, and another reads the switch.

## Part one: the freeze hold

Full design: `docs/freeze_hold.md`.

**The rule.** A scheduled job asks `python scripts/freeze.py hold`. The answer is `hold` only when the site is frozen **and** `warehouse/config/freeze_hold.yaml` says `enabled: true`. Otherwise `run`.

| Under hold | |
|---|---|
| Kept live | the 15-minute prices and the hourly network: their workflows and scripts are not touched |
| Fetched as usual | every pull, the validator, coverage, the archive, the Redivis draft |
| Held: the live set | the daily loader is not run; nor the Roundup's load of the cost ledger |
| Held: commits | the daily run's files, the health summary, the Roundup, the vacuum's sizes go to the branch `held/scheduled`, never to main. These are all four scheduled pushes to main; a test finds them in the workflows' own text |
| Still sent | the digest and the Roundup by email, and the failure alert |

**When the freeze ends.** The next scheduled run starts by putting the held files in its working tree (`scripts/held.py restore`), commits them to main with its own, deletes the branch, and its loader writes whatever differs, for however many days. The data waits in the archive and the Redivis draft; the files wait on the branch. Nothing waits only on a runner.

**What I built.**

| File | What |
|---|---|
| `scripts/freeze.py` | a second command, `hold`. `status` is as it was |
| `warehouse/config/freeze_hold.yaml` | the switch, `enabled: false` |
| `scripts/held.py` | `restore`, `commit`, `clear`, `status`: the held files, on a branch no page is built from |
| `.github/workflows/daily-prices.yml`, `roundup.yml`, `weekly-vacuum.yml` | two steps at the start (the answer; the held files), and a guard before each push to main and before the Roundup's load |
| `warehouse/run_daily.sh` | one guard: under hold the loader is skipped and recorded as skipped with its reason. Nothing else in the day changes |
| `docs/freeze_hold.md` | the design and the approvals |

**What you must approve to switch it on.**

1. **The line itself**, `enabled: true`, by the usual route, and with it the test that guards it (`test_it_is_not_switched_on`).
2. **That Vercel will not build `held/scheduled`.** On 5 October every `wip/` and `task/` commit read "Canceled by Ignored Build Step". I cannot read the rule. If it is "only main", nothing to do; if it names those two prefixes, add `held/`.
3. **Email during a freeze.** The digest and the Roundup still go out; their links to that day's page reach the in-review page until the freeze ends. If email should hold too, say so: it is one more guard.
4. **That prices and the network keep moving** for a reviewer. That is what you asked; I name it because it is the one thing on the three open pages that will still change: `/network`'s hourly snapshot.
5. **A long first run after a freeze**, loading every held day at once.
6. **A manual run during a freeze is held too.** To load on purpose mid-freeze, a person runs the loader from a data machine with the snapshot.

**One thing I could not make hold: `/network` reads a file the daily run commits** (`site/data/grid_network.json`, and the replay's `daily_*.json`). Under hold those do not reach main, so the page's fallback and its replay stay at the freeze's first day while its hourly snapshot moves. That is consistent with the rule, and worth knowing.

## Part two: why the daily run ran long and recorded whole tables as failed

Full account: `docs/loader_stamps.md`. The evidence is the three runs' own artifacts, which I downloaded through GitHub's API (read only): each holds `runs/supabase_reconcile.csv`, the loader's line for every table.

| Run | Tables | Rows selected | Rows written | Tables written whole | Database before, after (MB) | Recorded failed |
|---|---|---|---|---|---|---|
| 3 October | 48 | 542,074 | 182,950 | 17 (101,933 rows) | 399.0, 468.2 | none |
| 4 October | 49 | 564,285 | 201,822 | 18 (123,177 rows) | 433.3, 514.3 | `ercot_as_prices`, by its connector |
| 5 October | 58 | 1,292,645 | 927,833 | 25 (848,123 rows) | 971.0, 1,127.2 | `ercot_as_prices`, `ercot_hub_prices_daily`, by the loader |

(For 5 October the loader's file has no written count for the two failed tables. Their 681,638 rows are counted as written because session 126 found every row of both carrying that load's time. The file's own sum without them is 246,195.)

**4 October.** ERCOT's 2026 file of yearly reserve prices arrived as an Excel workbook. The connector stopped, the table was not built, the battery stack skipped. Fixed by session 113; on main.

**Every day.** `eia_fuel_spot_prices` (27,717 rows), `fred_daily_spot_prices` (24,306), `storage_buildout_monthly` (21,229), `storage_daily_cycle` (14,057), `energy_projects` (34,638) and a dozen more were written whole each day, because their rows' `retrieved_at` was new and nothing else. The database grew 70 to 80 MB in each load, to be vacuumed back.

**5 October.** Two tables of about 340,000 rows joined the selection. `ercot_as_prices` is built whole on the runner from ERCOT's nine yearly files, so every row was "new". The loader wrote 681,638 rows, asked for each count straight after, and both counts timed out (HTTP 500 with no body; the check just before the write had already failed with Postgres's own timeout code, 57014). It recorded both as failed and left their hashes empty.

**The length.** The daily step took 135 minutes against 85 and 80. The load began half an hour later than on 3 October (Monday's weekly pulls) and then took about 55 minutes with the digest and upload against about 32.

**The fix, in `warehouse/supabase/load.py`.**

1. **A row fetched again is not a changed row.** `retrieved_at` is left out of the comparison and of the table's hash. For `ercot_as_prices` a day's load becomes that day's 120 rows; a table rebuilt from the same documents is skipped without being read.
2. **The count is asked three times**, 10 and 30 seconds apart, before a table is recorded as failed.

**The test** (`tests/test_session131.py`, on 360 real rows of `ercot_as_prices` as the connector wrote them on 5 October, against a stand-in for Supabase that keeps rows in memory): two days loaded, then the whole table rebuilt with a new stamp and a third day: **120 rows written, where the old loader wrote 360**. A revised price is still written (1 row). A republished file with a new vintage is still written (120). Rows that left the selection are still deleted. The hash does not move with the stamp and does move with a value, a row or the license. `retrieved_at` is the only column left out: the test changes each column in turn. A count that fails twice is answered on the third try; one that fails three times still fails the table.

**Not fixed, and why.**

- The check that refuses a table older than the live copy sorts by `retrieved_at` and times out on large tables, then lets the load go on. An index would fix it; that is a migration, yours to approve.
- The loader reads a table back by offset, 1,000 rows a request. Slow for 340,000 rows; it matters less now that an unchanged table is not read.
- Five other failures in the same runs, none of which made them long: `grid_network` ("'bool' object has no attribute 'get'"), `build_status` (two extra columns in `eia930_all_interchange`), the digest's duplicate item, ISO-NE's hourly file, the package test of `ercot_dam_esr_awards`. Your prompt asked for the long run and the failed tables; I name these and left them.

## Checks

- Tests: `tests/test_session131.py`, 20 tests. The hold: the switch, the answer for each pairing of freeze and switch, the last day and the day after, the command's exit code. The held files, on real git repositories made for the test: a held run moves neither main nor the checkout; the next run starts from the held state; a person's change on main during the freeze survives; the run after the freeze brings everything to main and the branch is gone. The workflows: every scheduled push to main and every scheduled load sits behind the hold; the kept-live jobs are main's. The daily script's own lines, run in bash: the load is skipped under hold and nothing else is. The loader: above.
- Full suite: `python -m unittest discover -s tests`, exit 0: Ran 1295 tests in 397.185s, OK (skipped=19).
- No site build: nothing under `site/` changed. The three workflow files parse as YAML; `bash -n warehouse/run_daily.sh` passes.
- `python scripts/freeze.py hold` on this branch today: "run: the freeze hold is not switched on", exit 0. `python scripts/held.py status` against the real origin: "origin has no branch held/scheduled".
- **Not run: the loader itself.** Its dry run refuses on this machine because its tables are older than coverage (the rule of session 65, working). A real load is a write to tables the live pages read, which the freeze forbids. So the fix is proven on the stand-in and not yet on Supabase.

## Decisions made without you

- **The switch is a file in the repository**, not a setting on GitHub, so that switching it on leaves a commit and goes through the checks.
- **Held commits go to a branch**, not to the storage bucket: a person can see them, and nothing new needs a key.
- **A freeze file that cannot be read is held**, as it is frozen for sessions.
- **Email is not held.**
- **The Redivis draft is not held**: no visitor sees it and nothing releases it.
- **The loader ignores the stamp for every table**, not only the two that failed.
- **I downloaded three run artifacts from GitHub** to read the loader's own records. Read only, and not a data pull.
- **A few read-only requests to Supabase** (the count of three tables, and two rows of the catalogue) to learn whether the two tables were whole and whether the count now answers.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| The first list of held files named a file no run had changed | the test on real repositories: on this machine a clone rewrote line ends | the test's clones keep files as committed; on GitHub's runner the case does not arise |
| `count_rows` used `time` before the loader imports it | the first test run | imported at the top |
| GitHub's artifact download refused the token on its redirect | HTTP 401 | the redirect is followed without the token |

## What is left

1. Land this branch when the freeze ends (the commands above), before a 14:00 UTC run if possible.
2. Your six approvals, then the switch.
3. Watch the first held day, if a freeze follows.
4. The index for the older-than-live check, if you want that guard to work on large tables.
5. The five other failures of the daily run, each its own small fault.
