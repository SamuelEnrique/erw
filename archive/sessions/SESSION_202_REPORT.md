# Session 202 report: why scheduled runs fail, and one alert policy

12 October 2026, from 16:59 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `task/202-reliability`. Model spend USD 0, no model call. Pulls: none (GitHub's API and the project's own Supabase were read; no publisher was asked). No data lock taken. No warehouse table written.

## Read these first

- **A fault of mine: five rows were written to the live table `erw_health` by a test run.** At 17:06 UTC I ran the older tests against my half-finished change; the idle check's new "remember what was said" step used the real database (this machine holds the service key). Rows 2551 to 2555: workflow `alerts`, step `idle alarm`, status `ok`, reasons `quiet|b|2026-10-11T06:30` and four like it. They name machines that do not exist, match no real key, are read by nothing after 30 hours, and are left out of every count this session built. I did not delete them: a session does not delete rows of a live table. A guard is in place since (a test that hands in no stand-in can neither read nor write that memory) and a test holds it. Ruling 1.
- **40 distinct failures in 14 days; 11 were still open in our own code.** Six are fixed here, two are a patch for the connectors (not applied: a session does not touch them), three wait for a ruling. The full table is in the repository: `docs/state/scheduled_failures_2026-10-12.md`.
- **The public day of 20 October is at risk on the count alone.** "Scheduled jobs green for 0 days", counted to 11 October; 12 October is red already. Seven green days by 20 October means every day from 13 to 19 October green, so tomorrow's 14:00 UTC run must be green. It will not be without rulings 3, 5 and 6 (the cost ledger's load, CARB's file asked from the runner, Oregon's docket host).
- **One alert policy is in the code and written in `docs/machines.md`.** A silence and a failure are each said once; successes send nothing; a morning summary at 07:00 Pacific. The first morning summary goes out tomorrow.
- **`/internal/health` did not exist. It is built**, with the line "Scheduled jobs green for N days" and the days behind it.

## What to review

After the landing; open the internal view first at https://erw-flame.vercel.app/internal/open (paste the token, press "Open the internal view").

1. https://erw-flame.vercel.app/internal/health
   - Under the title: "Scheduled jobs green for 0 days." and "Counted to 2026-10-11 (UTC)".
   - "By day": ten rows, 11 October first, each "red: N failed"; the columns give each job's runs that day.
   - "Failed steps": 33 rows, the newest "2026-10-11 23:24, energy roundup, ledger: live set".
   - In a private window (no internal view) the same address answers the "not found" page.
2. The policy: https://github.com/SamuelEnrique/erw/blob/main/docs/machines.md , section "One alert policy (session 202)": one table, a row per kind of event.
3. Every failure of the 14 days: https://github.com/SamuelEnrique/erw/blob/main/docs/state/scheduled_failures_2026-10-12.md
4. The morning summary as it would read today, under "The dry run" below. Its HTML is on the old laptop: `C:\Users\lossa\Documents\erw\runs\session202\summary.html` (open in a browser).
5. Tomorrow at 07:00 Pacific: one email, "ERW morning summary, 13 October 2026: N green, N red". No other email unless something newly fails or a machine goes idle.

## The failures of the last 14 days

Read by an agent of the session, read only: `erw_health` (it begins on 2 October), the daily summaries, `run_status.csv`, the daily run's commits, GitHub's runs and 46 logs. Not read: the data machine's `runs/data_machine_daily.out` (it is on lab-desktop); its commits and health rows were read instead (one scheduled run in the window, 11 October, 12 steps ok).

| Fix is | Distinct failures | Still open on 12 October |
|---|---|---|
| code | 26 | 11 before this session; 5 after it |
| a ruling | 2 | 1 |
| the publisher's side | 12 | 1 (and 4 standing known gaps) |

The eleven that were open in our code:

| # | Step | Days | The error | Root cause | What this session did |
|---|---|---|---|---|---|
| 1 | daily run, board_page | 7 to 12 Oct | `FileNotFoundError ... carb_lcfs_credit_prices.csv` | The board's builder read California's fuel credit table without asking if it was there; on the runner it never is. The builder stopped, so the runner has not rebuilt the price board since 6 October | Fixed: the two rows are skipped when the table is absent and the held rows are kept (`warehouse/derived/board_page.py`, `build_lcfs`) |
| 2 | package tests, 4 tests | 5 to 12 Oct | `assert (False)` on the header's first line | A table rebuilt from the archive carries one note above its own first header line | Fixed: the tests read past the note |
| 3 | package tests | 5 to 12 Oct | `'ercot_dam_cleared_energy' != 'ercot_hub_prices_daily'` | A list of ERCOT's tables kept by hand, two tables behind. Three more lists by hand were hidden behind it in the same test | Fixed: the test holds to coverage; the three others too |
| 4 | package tests | 7 to 12 Oct | `KeyError: 'imf'`, `'cftc'` | A map of publishers kept by hand | Fixed: four publishers added |
| 5 | package tests | 7 to 12 Oct | `assert ['fred_treasury_yields'] == []` | The test said no table has the sector "equities"; coverage gives it to Treasury yields on purpose | Fixed |
| 6 | package tests | 8 to 12 Oct | `validator_status == 'pass'` | One table reads "pass, 1 warnings" | Fixed: a warning is a pass |
| 7 | daily run, redivis_upload | 7, 11, 12 Oct | `refused: 2,283 rows would shrink ... below the 2,285` | `price_board_spreads` is a moving 365-day window; on a day with no new fuel price it loses two rows, and the upload's guard refuses any smaller count | Not changed: ruling 4 |
| 8 | daily run, supabase_load (and the Roundup) | 9 to 12 Oct | `api_cost_ledger: refused, older than the live copy: 2,494 rows here and 3,179 in Supabase` | Each machine keeps its own ledger; the loader replaces the table and refuses fewer rows. Session 176 wrote the repair; it was never run | Not changed: ruling 3 |
| 9 | daily run, isone real-time hourly | 5, 12 Oct; gap days between | `EmptyDataError('No columns to parse from file')` | ISO-NE's final file for a day not yet posted now answers with no table where it answered "not found", so the fallback to the preliminary file is skipped | Patch prepared, not applied: ruling 8 |
| 10 | Saturday supply refresh, ercot_zone_load | 10 Oct | `the operator answered no hour; rows read 0` | ERCOT renamed this year's file `Native_Load_2026-1-.zip`; the pattern takes only `native_load_<year>` | Patch prepared, not applied: ruling 8. Fails again Saturday 17 October |
| 11 | the weekday digest's email | 5 Oct | recorded ok: "2026-10-02: sent" on 5 October | When the day's brief is not written, the email step sends the last issue there is: Friday's went out on Monday | Not changed: ruling 7 |

Also found:
- **The weekday digest was written on 5 of 10 weekdays** (2, 7, 8, 9, 12 October). Not written: 29 and 30 September, 1, 5, 6 October; each cause is fixed (rows 30 and 31 of the table).
- **The health row of a step names one failure where there are several.** "package tests" has read one test's name every day while 2 to 9 failed. Ruling 12.
- **Failures inside the daily run's own step are not rows of `erw_health`** (ISO-NE, CARB's auction file, NYISO's queue, ERCOT's large-load list): they are in the commit's subject and in `run_status.csv` only. Neither the green streak nor the new-failure email sees them. Ruling 5.
- **Tests pinned to the clock.** `tests/test_planner.py` (session 201). `tests/test_session138_demand.py` would have failed from 6 January 2027: fixed (a fixed day). Listed and not changed: `tests/test_session152.py` (reads the real weekday; not shown to fail), `site/scripts/test-ask-tables.mjs` (fails when November begins; not run on GitHub; session 199's ruling 4).

## One alert policy

`scripts/alert.py`, `scripts/duty.py`, `scripts/notify.py`, `.github/workflows/chain-watch.yml`, `.github/workflows/daily-prices.yml`; written in `docs/machines.md`.

| What happens | Before | Now |
|---|---|---|
| A machine on duty runs nothing for 30 minutes | one email at 30 minutes and again every hour | one email, once for that silence |
| A marked chain saves nothing for 30 minutes | the same | one email, once |
| A machine declares idle (queue empty) | one email | unchanged: one email |
| A step of a scheduled job fails | the daily run only: one line a run, every day the same steps failed | any job: one email when a step newly fails; nothing while it keeps failing |
| A step fails and passes at the second try | nothing | nothing |
| A session finishes, a job runs, a landing passes | `notify.py` sent a line when asked | nothing; `notify.py` sends only with `--failed` |
| Every morning | nothing | one summary at 07:00 Pacific |

- "Once" is remembered as a row of `erw_health` (workflow `alerts`), not timed: a check that runs late still sends, a check that runs twice does not repeat. When that memory cannot be read, the old window rule holds (never more than once).
- The new-failure check and the morning summary are two steps of the chain watch (every 15 minutes, started by the database's schedule). No migration, no new secret, no new workflow.
- The morning summary: sent by the first run at or after 07:00 Pacific (14:00 UTC now, 15:00 UTC from 1 November; the script knows the change).

### The dry run (`runs/session202/summary.html`; `scripts/alert.py summary --dry-run`, 17:16 UTC)

```
Subject: ERW morning summary, 12 October 2026: 17 green, 4 red

The runs from 11 October 14:00 to 12 October 17:16 UTC, one line each. A success sends no other email.
Scheduled jobs green for 0 days (counted to 2026-10-11, UTC).

red    daily prices: 10 failed in 3 runs: carb_lcfs (...); board_page (FileNotFoundError ...); policy_monitor_refresh (...); and 2 more
red    energy roundup: 1 failed in 2 runs: ledger: live set (FAILED api_cost_ledger: RuntimeError: refused, older than the live...)
red    machine SU-4QC3QR3: 1 failed in 14 steps: session198_ercot_as_quantities (ModuleNotFoundError: No module named 'pandas')
red    task/198-battery-data: checks failure (run 38172045438), not merged
green  chain watch: 115 runs, no failure
green  hourly network: 31 runs, no failure
green  latest prices: 114 runs, no failure
green  machine lab-desktop: 3 steps, no failure; last: idle at 13:40 UTC
green  machine samueloldlaptop: 2 steps, no failure; last: idle at 03:44 UTC
green  weekly vacuum: 1 run, no failure
green  task/201-tooling: checks passed, merged into main
(and ten more landings, each "checks passed, merged into main")
```

## `/internal/health`

- New page, behind the internal cookie as `/internal/waits` is (no token in an address), not in the menu, not indexed.
- It reads one committed file, `site/data/health_days.json`. `warehouse/health.py summary` adds a day to it with each day's summary, and the daily run commits both. So the page is as new as the last daily run: today's steps are counted tomorrow.
- N: the days in a row, back from the newest day recorded, with no failed step. 0 whenever a job failed that day. A day with no record ends the count; so does a day on which a job that runs every day recorded no run. A second try that passed is not a failure.
- Filled for 2 to 11 October from the table (it holds nothing earlier): 10 days, all red, 33 failed steps.

## Checks, with exit codes

None piped; outputs under `runs/session202/`.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 202"` | 0 | 6 of 6; on duty |
| `tests.test_session202` | 0 | 36 tests |
| The older alert, health and queue tests (12 modules) after their move to the new policy | 0 | 295 tests; ten of them asserted the hourly repeat, the old step or the old wording and were changed |
| `package/tests/test_erw.py`, the six tests of rows 2 to 6, on this machine's tables | 1 | 147 of 148 pass. The one left: `cite[eia930_demand_growth]` (coverage says the table is not derived, its citation says it is; a table the runner does not hold). Before: 11 failed |
| `package/tests/test_erw.py`, whole, on this machine | 1 | 628 pass, 68 fail: 58 are row counts against coverage (this laptop's tables are behind it; not the runner's case), 9 are in tests this session did not change and I did not read one by one, and the one above |
| `warehouse/derived/board_page.py --site-dir <scratch>` | 0 | 794 rows, the two credit rows built (the table is on this machine) |
| `warehouse/health.py days --from 2026-10-02 --to 2026-10-11` | 0 | 10 days written; green for 0 days |
| `scripts/alert.py summary --dry-run --html runs/session202/summary.html` | 0 | the text above |
| `scripts/alert.py failures --dry-run` | 0 | "quiet: no step newly failed in the last 60 minutes" |
| `npm run build` on the merged commit `93e6a39c` (one comment of the new page was reworded after it) | 0 | no "statement timeout" line |
| `site/scripts/check-internal-health.mjs` on that build | 0 | 19 checks: 404 for a visitor and for a token in the address; the line holds the file's number; every day a row; no sideways scroll at 390 px |
| `site/scripts/check-security.mjs`, `site/scripts/check-routes.mjs` on that build | 0, 0 | 50 of 50; 160 pages asked as a visitor, 0 failed. A first run of the three answered from a server left over from the build before (the new one had not taken the port); they were run again on a fresh server |
| Whole suite, clean copy, `93e6a39c` | 1 | 3,481 tests, 1 failure: a comment of the new page named another internal page's address, which a test of session 188 forbids |
| Whole suite, clean copy, `cce4b9e4` (the comment reworded; this report's last edit follows it, and the tests that read reports were run again on it) | 0 | 3,481 tests, 237 skipped |
| `git apply --check --ignore-whitespace` of the connectors patch | 0 | applies; not applied |

- **Not verified, and cannot be here:** the six fixes on the runner. Tomorrow's daily run is the test: its "board_page" and "package tests" steps should be ok.
- **Not verified:** a real send of any email under the new policy (every send in the tests is a stand-in; the dry runs send nothing). The first real ones are tomorrow's summary and the next new failure.
- **Not run:** the connectors patch against ISO-NE or ERCOT (no pull in this session). The new link pattern was tried on three file names only.

## The landing

- Freeze status before the push: exit 0, no freeze. `main` merged into the branch first.
- Before snapshot `s202-before`, its own command, then `git push origin task/202-reliability`.
- Expected: 0 differences on the 25 pages. The branch adds one page (`/internal/health`, not among the 25, 404 for a visitor) and one data file only that page reads.
- **The result (GitHub's check, the merge, Vercel's answer, the after snapshot and the comparison) is written into this report by session 203's branch**, under this heading.

## Decisions made without you

- **The page was built, since it did not exist**, on a committed file and not a live read: the table answers the service key only and the site holds none. A live read needs a migration. Ruling 11.
- **The memory of what was said lives in `erw_health`**, under the workflow name `alerts`: no new table, no migration.
- **The summary and the failure check are steps of the chain watch**, not a new workflow: that job is the one the database starts on time.
- **The daily run's own failure email is removed** (one line a run, every day). The chain watch tells a new failure of any job.
- **The Roundup keeps its own failure email**: its workflow was not to be touched. The chain watch leaves the Roundup's failures to it, so none is told twice.
- **More than five new failures at once are one email** naming them all (a database outage fails thirty steps together).
- **`scripts/notify.py` sends only with `--failed`.** A finished session is a success.
- **The hook's rule is unchanged** (a session waiting for a permission or for input: at most one email per session and kind every 10 minutes). Ruling 10.
- **What counts toward the streak:** every step of a scheduled workflow, and a machine's own daily run (its steps are named `dm_...`). A session's own rows on a machine are shown and do not count. A step the model cap skipped is a skip, not a failure.
- **The upload's shrink guard, the ledger's load and the digest's email step were not changed.** Each guards a store or sends to readers; each is a ruling.
- **The connectors were not touched**, as the chain rules; their two fixes are a patch in the repository, beside the table.
- **The five stray rows were left in place.**
- **`CLAUDE.md` is not edited.** Its rule on gates is unchanged by this session.
- **This file's landing result is added by session 203's branch**, as session 201's was by this one.

## For Samuel's ruling

1. The five stray rows of `erw_health` (ids 2551 to 2555, written by my test run). Remove them, or leave them. They affect nothing.
2. The daily model cap is USD 1.00 and news scoring alone spends about USD 1.07 on a weekday. So every later model step is skipped every day since 10 October, and the digest of 12 October and the Roundup of 11 October were written without the model. Raise the cap (session 176 measured about USD 1.45 on a full day), or say which steps it may drop.
3. The cost ledger has not loaded since 9 October (the page `/internal/costs` stops at 8 October), and it fails the daily run's load step every day. Session 176 wrote the repair (five commands that write the archive, Supabase and the Redivis draft). Give the go-ahead, and say whether the loader should then add ledger rows instead of replacing the table.
4. `price_board_spreads` is refused by the Redivis upload on any day its one-year window loses rows (7, 11, 12 October). Either that table may shrink, or it is judged by its newest date.
5. What counts as "green" for the public day. Two things the count does not see today: (a) CARB's fuel credit file is asked from GitHub's runner every day and refused every day, a known gap that fails a step; record a known gap as skipped on the runner, or stop asking from there. (b) A connector that fails inside the daily run's main step (ISO-NE today, CARB's auction file, NYISO's queue) is not a row of the health table at all. Whether those should turn a day red.
6. Oregon's docket host has not answered GitHub's runner for two days, and one regulator's failure fails the whole policy step. Ask Oregon from the data machine, or let one regulator fail without failing the step.
7. The digest's email: when the day's brief was not written, the step sends the newest issue there is (Friday's on Monday 5 October). Send nothing that day instead?
8. The two connector fixes (ISO-NE's empty final file; ERCOT's renamed load file): `docs/state/scheduled_failures_2026-10-12_connectors.patch`. Apply with `git apply --ignore-whitespace` in a data session that can test them with a pull. ERCOT's fails again on Saturday 17 October.
9. The Roundup's failure email is the one alert outside the policy. When its workflow may be edited, remove its last step.
10. The hook (a session waits for a permission or input): once per session and kind every 10 minutes today. Say if it should be once.
11. The health page shows the days up to yesterday. A live count needs one migration (a function the page may call with the internal token, as `/internal/usage` has). Wanted or not.
12. A failed step's reason names one failure of several. Whether the health row should name them all (it would have shown six failing package tests, not one).
13. `eia930_demand_growth`: coverage says "not derived", its citation says "derived". One of the two is wrong; it is a table the ERW computes.
14. The three allow rules of session 188 (session 201's patch) would have let this session's precheck run without a prompt on a machine that asks. Unchanged.

## The prompt

Chain of 12 October (night), sessions 201 to 203; this session's text: "Session 202: why scheduled runs fail, and one alert policy. Long end 2:30. Branch task/202-reliability": read the last 14 days of every scheduled job, a table of every failure with its root cause; fix every cause that is code, tested on a clean copy; one alert policy in `scripts/alert.py` and the workflows, written in `docs/machines.md`; `/internal/health` gains the line "Scheduled jobs green for N days". "Done means: the suite exit 0; a dry run of the summary email saved to runs/session202/summary.html; landing with snapshots."
