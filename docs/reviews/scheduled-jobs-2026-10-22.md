# Seven days of scheduled jobs, read and mended (15 to 21 October 2026, UTC)

Energy Research Warehouse (ERW), session 578 of chain 034, written on the night of 21 to 22 October 2026 on samueloldlaptop. Roadmap item "The loop runs itself": main green on every scheduled job for seven days. The session's report: `archive/sessions/SESSION_578_REPORT.md`.

**How it was read.** Every run of every workflow in `.github/workflows/` created from 2026-10-14T23:51:46Z to 2026-10-21T23:51:46Z, through GitHub's REST API (`/actions/runs` in twelve-hour slices, the jobs of each run that did not succeed, each such job's log and check-run annotations), with the token `scripts/alert.py` reads, never printed: 1,680 runs. A run GitHub marks green can hold a failed step, because `warehouse/health.py run` records a step's failure in Supabase's `erw_health` and exits 0; so the steps were read too, from the committed summaries `queue/summary/2026-10-15-health.md` to `2026-10-20-health.md` and, for 21 October, `warehouse/health.py summary --day 2026-10-21` at 23:53 UTC (632 steps; written to `runs/`, not committed). No schedule, trigger or secret was changed; nothing was written to Supabase; no request to a publisher.

## Read these first

- **Eleven runs did not succeed on GitHub** (table 1): four daily runs (three stopped at the job's old limit of 180 minutes, one cancelled by a person), six pushes to `task/` branches stopped by the gate, and one push run superseded by a newer push. **Every cause is mended on main**: none of them is open in the repository's code tonight.
- **Inside the green runs, 52 steps failed** over the seven days (table 2): 3, 13, 13, 15, 3, 5 and 0 a day. Most were one limit, Redivis's 100 GB export cap of 30 days, which stopped the daily run's restore from 15 to 18 October and the Roundup of week 42 (fixed by session 305 on 19 October). Every other cause has a fix on main, or waits for Samuel where the notes already say so (below).
- **21 October is the first day with no failed step** (0 of 632). `site/data/health_days.json` on main counts to 20 October with `green_days` 0; the next count should make it 1. Seven green days in a row cannot come before 27 October.
- **21 October was not whole, though**: pg_cron in Supabase did not start the 15-minute and hourly jobs from 23:30 UTC on 20 October to 05:30 UTC on 21 October ("job startup timeout"; latest prices 78 of 96 slots, chain watch 77, hourly network 18 of 23). The database's slowness, named in `queue/summary/2026-10-21-health.md`; the setting and the streak rule wait for Samuel's ruling there, not decided here.
- **Mended by this session: the suite's fixture lines were read as annotations.** On GitHub's runner a printed line that begins `::warning::` is an annotation; the tests' fixtures made 20 to 29 false ones on every run of the suite ("network_hourly FAILED: RuntimeError: boom", "daily model cap reached: USD 1.32 spent today (2026-10-08 UTC ...)", "x FAILED: RuntimeError: HTTP 500"), listed beside the real ones on each failed run read here. `tests/test_000_quiet_annotations.py` (below) stops that, without a change to any workflow.

## Runs by workflow

| Workflow (file) | Runs | Success | Failure | Cancelled |
|---|---|---|---|---|
| chain watch (`chain-watch.yml`) | 697 (46 schedule, 651 dispatch) | 697 | 0 | 0 |
| latest prices (`latest-prices.yml`) | 695 (45 schedule, 650 dispatch) | 695 | 0 | 0 |
| hourly network (`hourly-network.yml`) | 197 (42 schedule, 155 dispatch) | 197 | 0 | 0 |
| code branch (`code-branch.yml`, push to `task/**`) | 69 | 62 | 6 | 1 |
| daily prices (`daily-prices.yml`) | 18 (7 schedule, 11 dispatch) | 14 | 0 | 4 |
| energy roundup (`roundup.yml`) | 2 | 2 | 0 | 0 |
| weekly vacuum (`weekly-vacuum.yml`) | 2 | 2 | 0 | 0 |
| issues (`issues.yml`), thesis (`thesis.yml`) | 0 (dispatch only) | | | |

A dispatch is pg_cron's start (migrations 015 and 022); a schedule run is GitHub's own fallback, which skips as a duplicate when pg_cron's run came first. The daily run's 14:00 UTC dispatch and its fallback both ran each day; the second found the day done (`gate`) except when the first did not finish.

## 1. Runs that failed or were cancelled on GitHub

First error line: the job's first `##[error]` line, or the first test failure for a failed suite. Sort: **code** (a fault of the repository's code), **source** (a publisher's outage or slowness), **database** (Supabase's slowness), **limit** (Redivis, the spend cap, a job's time limit), **person** (a stop someone made), **gate** (the branch gate refusing a branch, which is its work).

| Run | Created (UTC) | Workflow, ref | Job, step | First error line | Sort | State |
|---|---|---|---|---|---|---|
| 38747505887 | 10-15 14:00 | daily prices, main `0137e1f6` | refresh, step 8 "Pull, validate, rebuild coverage" | The job has exceeded the maximum execution time of 3h0m0s (last output 16:04:50, the validator's list, then 56 minutes without a line) | source, against a limit of the repository's | Mended: session 321 (`a6579c47`, 19 October 20:38 UTC) raised the job to 300 minutes and gave each publisher pull a budget of 15 minutes (`warehouse/pull_budget.py`); the fallback run of 17:55 finished but stopped at the restore (table 2, Redivis) |
| 39207762565 | 10-19 06:03 | daily prices, main `7bd74acf` | refresh, step 9 "Pull, validate, rebuild coverage" | The job has exceeded the maximum execution time of 3h0m0s (last output 08:07:26, `eia930_all_interchange.csv`, then 57 minutes) | source, against a limit | Mended by session 321, as above |
| 39264997370 | 10-19 14:00 | daily prices, main `121ef886` | refresh, step 9 "Pull, validate, rebuild coverage" | The job has exceeded the maximum execution time of 3h0m0s (last output 16:46:29, the validator's list, then 14 minutes) | source, against a limit | Mended by session 321; its cut-off before the commit caused the supabase_load refusal of 19 October (table 2) |
| 39322988664 | 10-19 20:52 | daily prices, main `68b46126` | refresh, step 6 "Merge tests" | The run was canceled by @SamuelEnrique. | person | Nothing to mend; the next run (23:58) succeeded |
| 39237187594 | 10-19 10:24 | code branch, `task/300-home-page` | merge, step 3 "Open the pull request and merge it" | CONFLICT (content): Merge conflict in docs/licenses.md (and tests/test_session205.py) | gate | The next push (10:43, `9e46a147`) merged |
| 39358324576 | 10-20 02:19 | code branch, `task/327-afternoon` | checks, step 6 "Tests (tests/)" | FAIL: test_the_python_rule_gives_what_the_cases_say (test_session157.TagRule) | code (a test that read a file the daily run rewrites) | Mended by `b3722a41` (20 October 02:47 UTC): the test holds every case as the cases say and lets an action tagged after the cases were frozen carry a known tag; the branch's commits are on main |
| 39359967442 | 10-20 02:38 | code branch, `task/317-charts` | checks, step 6 "Tests (tests/)" | FAIL: test_the_python_rule_gives_what_the_cases_say (test_session157.TagRule) | code, as above | Mended by `b3722a41`; the next push (02:48) merged |
| 39400638183 | 10-20 09:26 | code branch, `task/357-price-years` | checks, step 6 "Tests (tests/)" | FAIL: test_the_status_command_keeps_a_recorded_permission (test_session207.LicenseStatus): AssertionError: 40 != 41 (and three more on `nyiso_load_queue`'s license status: test_session248 twice, test_session275) | gate (a branch behind main's license records) | The next push (10:01, `1e1166cc`) merged |
| 39524179379 | 10-21 00:54 | code branch, `task/367-372` `a94c7f1f` | checks, step 6 "Tests (tests/)" | FAIL: test_an_ancillary_service_table_not_on_the_machine_is_skipped (test_session166.TheBoardBuilder): AssertionError: 3 != 4 | code | Mended: session 386 (`b875583a`) took test_session166's fix from the branch; the branch's commits are on main |
| 39525362021 | 10-21 01:06 | code branch, `task/367-372` `b39bada3` | checks, step 7 "Site build and check-routes" | Error: Supabase entities: HTTP 500 {"code":"57014", ... "canceling statement due to statement timeout"} | database | Named, not fixed here: the build's read of Supabase timed out (the reads take turns since session 90; `scripts/db_probe.py` is the chains' guard before a build) |
| 39659885982 | 10-21 19:14 | code branch, `task/489-499-sources` | checks, step 6 "Tests (tests/)" | Canceling since a higher priority waiting request for code-branch-refs/heads/task/489-499-sources exists | gate (a newer push to the branch) | The newer push (19:22, `48616a54`) merged |

The five suite failures (rows 6 to 9) fail no longer: `tests.test_session157`, `test_session166`, `test_session207`, `test_session248` and `test_session275` pass on this branch (77 tests, exit 0).

The three stops at the time limit print their last line minutes before the stop because Python's output to a pipe is written in blocks; the step that did not answer is therefore not named by the log. Session 321 named the hosts from its own reading (CAISO's and SPP's, EIA's API) and gave each pull its budget. Since that landing every daily run has finished: 19 October 23:58 (139 minutes), 20 October 05:14 (136 minutes), 21 October 14:00 (144 minutes), each well inside 300.

## 2. Steps that failed inside green runs (erw_health)

One row a cause; the causes are written in full in the "Root causes" section of each day's summary (sessions 305, 321, 336, 374, 377, 384), which this table follows. `local:SU-4QC3QR3` is the data machine (lab-desktop).

| Cause | Days (failed steps) | Job, step | Error, as recorded | Sort | State |
|---|---|---|---|---|---|
| Redivis's export cap | 10-15 to 10-19 (daily run 10-15 to 10-18, Roundup 10-18 23:01 and 10-19 00:37, dm_zone_redivis 10-16 to 10-18) | daily prices "daily run" (restore); energy roundup "write the Roundup"; data machine dm_zone_redivis | FAIL restore weather_obs_hourly: APIError: [400 invalid_request] Cannot export more than 100GB within a 30 day period | limit (Redivis) | Mended by session 305 (`1ca1684e`, 19 October 06:02 UTC): restores from GitHub's cache, then the archive bucket, Redivis last under 2 GB a day. The Roundup of week 42 was not sent |
| The store steps' read after an upload, refused by the same cap | 10-16 to 10-18 (9 or 10 tables a day) | data machine dm_*_stores | ercot_rtm_node_prices FAILED: redivis exited 1 | limit (Redivis) | Mended by session 305: a read refused for the cap is a skip |
| Redivis's 10 GB of free storage | 10-20 | data machine dm_ercot_hub_append_stores | ercot_all_hub_prices_history FAILED: redivis exited 1 ("would cause your account to exceed its free storage allotment of 10GB") | limit (Redivis) | Recorded as a skip since session 377 (`STORAGE_SKIP`); the storage itself waits for Samuel (a paid tier, or tables out of the draft) |
| The live set's sources check | 10-15 to 10-18, 10-20 | data machine dm_live_set | FAILED tables: ['sources'] | code (rows loaded from branches not on main) | Mended by sessions 305 and 374; passed on 21 October |
| The data machine's pull refused | 10-15 to 10-18 | data machine dm_commit | git pull --rebase exit 128: committed here, not pushed | code | Mended by session 305 (`run_data_machine.sh` stashes such files first) |
| The live load refused older rows | 10-19 | daily prices supabase_load | FAILED tables: ['datacenter_projects', 'energy_deals'] | code, after a limit (the 14:00 run cut off before its commit) | Mended by session 321 (tables restored from the archive; the 300-minute limit) |
| The license check read a cap-refused header | 10-19 | daily prices "daily run" | license check: 34 internal tables, 0 in the public dataset, 4 unknown tables there; FAILED | code | Mended by session 321 (`check_license`); `power_deals` out of the draft waits for a person |
| EIA-930 demand one hour short | 10-20 00:26 | daily prices eia930 | eia930_ciso_demand FAILED ... demand_mw: 71 of 72 hours (1 missing) | code (the window's end) | Mended by session 336 (`demand_window_end`); not yet proven by a run that starts near midnight |
| generation_mix without its input | 10-20 00:50 | daily prices generation_mix | RuntimeError: input table absent: eia_state_generation_monthly | source (eia_series reached its 15-minute budget), with a guard missing in code | Mended by session 327's guard (`d65db7f7`) |
| Package test on a rebuilt header | 10-20 02:17 | daily prices "package tests" | FAILED package/tests/test_erw.py::test_large_table_by_partition[nyiso_zone_load_hourly] | code | Mended by session 336 (`88702c6c`) |
| CARB's LCFS week | every day | dm_carb_lcfs; daily prices carb_lcfs | the newest week CARB holds is 2026-09-14, 29 to 37 days old (limit 28) | source | A skip, "stale at source" (session 271); not a failure |
| Federal Reserve's empty body | 10-15, 10-19, 10-21 | daily prices frb_treasury | RuntimeError: the Board answered an empty body | source | Passed on its retry each day |
| EIA's API read timeout | 10-20 23:07 | hourly network | ReadTimeout: api.eia.gov, read timeout=60 | source | Passed on its retry |

Failed steps a day (`erw_health`): 15 October 3, 16 October 13, 17 October 13, 18 October 15, 19 October 3, 20 October 5, 21 October 0.

## 3. Mended by this session

**The suite's fixture lines on the runner.** `warehouse/health.py`, `warehouse/connectors/ercot_dam_esr.py`, `warehouse/derived/energy_projects.py` and `ercot_peak_premium.py` print GitHub workflow commands (`::warning::`, `::notice::`) unconditionally, which is right for a scheduled step and wrong for a test: the fixtures of many test modules call them, and on the runner each such line became an annotation of the run. The daily run's "merge tests" step and code-branch's "Tests (tests/)" step each added 20 to 29 (the failed daily run of 15 October holds 29 annotations, 25 of them the suite's). A reader of a failed run read a fake "network_hourly FAILED" or "daily model cap reached ... 2026-10-08" beside the real error, and GitHub keeps a limited number of annotations a step and a job. Fix: `tests/test_000_quiet_annotations.py`. `python -m unittest discover -s tests` imports every test module in sorted order before it runs one (`sorted(os.listdir(start_dir))` in `unittest/loader.py`), so this one first; on the runner (`GITHUB_ACTIONS=true`) it prints `::stop-commands::<random token>` and, at the process's exit, `::<token>::`, so the suite's lines are plain text in the log and health.py's own line after a failed suite is read as before. Off the runner it prints nothing. Its five tests: nothing off the runner, the stop and the resume with one random token, a fixture's line between them in a process of its own, nothing printed by the module off the runner, and the module first in discovery's order. No workflow was changed. The proof on the runner is the first `code-branch` run after the landing: its annotations should hold none of the fixture lines above.

## 4. Named, not fixed

- **The database's slowness**: the build's statement timeout of 21 October 02:02 (table 1), and pg_cron's "job startup timeout" of 20 to 21 October (no 15-minute run from 02:30 to 05:30 UTC). Both outside the repository's code; pg_cron's setting waits for Samuel (`queue/summary/2026-10-21-health.md`).
- **Sources**: CARB's LCFS week (37 days old on 21 October), the Federal Reserve's empty answers, EIA's API timeouts, and the slow hosts behind the three stops at the time limit.
- **Limits**: Redivis's 10 GB of free storage (every growing table's Redivis step is a skip until Samuel settles it). The daily model cap (USD 1.50) failed no step; on 19 October it was reached (USD 1.53 in 60 calls, on a day of five daily runs, two of them stopped at the time limit) and five model steps were skipped, the Digest of that day written without the model-written parts (`queue/summary/2026-10-19-health.md`, skips).
- **Coming changes on GitHub's side, not failures yet**: every job warns "Node.js 20 is deprecated" for `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`, `actions/upload-artifact@v4` and `actions/cache/restore@v4` (forced to run on Node.js 24, and running); and "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026". A change of an action's version or of `runs-on` is a workflow change this session did not make; a later session can, with the gate's run as its proof.

## Waiting for Samuel's ruling (from the notes named above; none decided here)

- pg_cron's `cron.use_background_workers`, or a read of the project's resource use for 20 to 21 October (`queue/summary/2026-10-21-health.md`).
- Whether a job far below its expected count of runs ends the green streak (`health.py`, `missing`; same file).
- Redivis's storage: a paid tier, or tables out of the draft (session 377).
- `power_deals` out of the Redivis draft before a release (session 321).
- The data machine's scheduled task run with no console (session 384).
