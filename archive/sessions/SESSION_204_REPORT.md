# Session 204 report: the data decisions of 12 October, on lab-desktop

lab-desktop (data role), 12 October 2026 from 09:00 UTC (02:00 Pacific). Unattended, first session of the night's chain. Branch `task/204-data-decisions`. Model spend USD 0, no model call. One approved pull (ERCOT's node prices). No request to a paused publisher; no NYISO, SPP, PJM or MISO request. No site page, test logic, run time or trigger, scanner or release gate touched.

## Read these first

- **Three of the generator page's steps are in the run and switched off: the snapshot, the hub files and the hourly CSV. That part of ruling 3 is not done.** Six tests on `main` hold the CSV to its export of 7 October 2026. A re-export fails them, the snapshot cannot move without the CSV, and rule 8 keeps this session off a test's logic. `GENERATOR=1` turns the three on once those tests are changed. Details under "The generator's group".
- **No branch can pass GitHub's check between 05:00 and 13:00 UTC.** `tests/test_planner.py` (`TheQueueStep.test_with_the_planner_on_the_planned_chain_is_committed_pushed_and_taken`) reads the real clock and fails in those hours: "a session may start from 13:00 to 05:00 UTC". Found at 09:25 UTC on a clean copy of `main` plus this branch; it is the only failure of 3,427 tests. So this branch's push waited for 13:00 UTC. The code machine's landings of tonight meet the same wall.
- **ERCOT's node prices: 213,900 rows before, 424,632 after; 28 September 04:45 UTC to 12 October 08:45 UTC, no gap.** 672 files pulled, 0 failed, 209,664 rows counted against the ceiling of 500,000. The pull came within hours of a gap: ERCOT's list began at the interval after the last one held.
- **The pull is a soft step of the daily run from today (17:00 UTC), with the same ceiling a day.** So are the battery page's two downloads, the hybrid's hours, and the fix for the two storage offers tables. `scheduled.py --list` names all seven new steps.
- **Landed: see "The landing".**

## What to review

- This report: https://github.com/SamuelEnrique/erw/blob/main/archive/sessions/SESSION_204_REPORT.md
- The run, blocks "1b" and "3b", and the note above the switched-off steps: https://github.com/SamuelEnrique/erw/blob/main/warehouse/run_data_machine.sh
- The seven steps (`DATA_MACHINE`) and the refusal anywhere but on a data machine (`where`): https://github.com/SamuelEnrique/erw/blob/main/warehouse/scheduled.py
- The connector, `--daily` and the row ceiling: https://github.com/SamuelEnrique/erw/blob/main/warehouse/connectors/ercot_rt_spp.py
- A table's stores in one script: https://github.com/SamuelEnrique/erw/blob/main/warehouse/table_stores.py
- The tests, 34: https://github.com/SamuelEnrique/erw/blob/main/tests/test_session204.py
- The one line changed in an earlier test: https://github.com/SamuelEnrique/erw/blob/main/tests/test_session120.py (`test_neither_pull_is_on_a_schedule`)
- The section "The data machine's daily run since session 204": https://github.com/SamuelEnrique/erw/blob/main/docs/machines.md
- The battery download with today's header: https://erw-flame.vercel.app/battery/erw_2026_battery_dispatch.csv
- `LAST_ANSWERED`: https://github.com/SamuelEnrique/erw/blob/main/archive/sessions/LAST_ANSWERED and what it leaves on https://erw-flame.vercel.app/internal/waits

## 1. Worktrees and branches

Worktrees on this machine. Removed only where `git status --porcelain` was empty and the branch's tip is on `main`:

- `erw-184` (`wip/184-lab-desktop`, tip `949bb241`): removed. On `main` through `13d1ba61`, "Merge task/185-data-machine".
- `erw-185n` (`wip/185-night-report`, `b7a5e816`): removed. On `main` through `a8067cca`, "Merge task/185-night-report".
- `erw-185` (`wip/185-data-machine`, `e694ac64`, on `main` through `13d1ba61`): **left**. One line: `?? warehouse/output/raw/` (what the suite leaves behind).
- `erw-191` (`wip/191-scanner-review`, `8c27f9cb`, through `330933e0`): **left**, the same one line.
- `erw-192` (`wip/192-roundup-repeat`, `86c00eb8`, through `e5af1750`): **left**, the same one line.
- `erw-193` (`wip/193-ba-map`, `75c15bbe`, through `ad0307b1`): **left**, the same one line.
- `erw-200` (`task/200-report`, `5ec7e8a1`, through `8830320e`): **left**, the same one line.

Branches on GitHub, deleted, each with its tip on `main`:

- `wip/180-network-map` (`a3fed2ab`), through `ad0307b1`, "Merge task/193-ba-map".
- `wip/185-data-machine` (`e694ac64`), through `13d1ba61`.
- `wip/185-night-report` (`b7a5e816`), through `a8067cca`.
- `wip/191-scanner-review` (`8c27f9cb`), through `330933e0`.
- `wip/192-roundup-repeat` (`86c00eb8`), through `e5af1750`.
- `wip/193-ba-map` (`75c15bbe`), through `ad0307b1`.
- `wip/200-roadmap-inputs` (`fd4f3a57`), through `3b79fab4`, "Merge task/200-roadmap-inputs".

Left on GitHub, not on `main`: `task/198-battery-data` and `wip/198-battery-data` (4 and 5 commits ahead), `wip/076-land` (1), `wip/130-deals-v3` (1), `wip/131-freeze-scheduled` (2), `wip/171-virginia` (3). Local branches were not deleted: the prompt names worktrees and GitHub.

## 2. ERCOT's node prices

- Before: 213,900 rows, 690 intervals, 2026-09-28T04:45:00Z to 2026-10-05T09:00:00Z, 310 settlement points.
- After: 424,632 rows, 1,361 intervals, 2026-09-28T04:45:00Z to 2026-10-12T08:45:00Z, 312 settlement points. Every 15-minute interval between is held.
- 210,732 rows are new. 209,664 come from the 672 files pulled (312 a file). The rest: two storage points the awards table has gained since 5 October, read from the week's files already saved (1,380 rows), less one file that repeats an interval (312).
- **ERCOT posted one interval twice** (ending 8 October 11:45 Central, two files a second apart, every price the same). The table refused both at the first write. The connector now reads two postings with the same prices as one interval, and leaves an interval out when two postings differ. Nothing chooses between prices.
- Validator exit 0. Archive: 210,732 rows new or changed. Redivis draft: 424,632 rows, nothing released. `sync.py --check`: current.
- **Kept internal:** not in the live set (`catalogue_hold` in `warehouse/supabase/live_set.yaml`, as since session 120; a test now holds it there). No page reads it.
- **The daily step:** `scheduled.py ercot_rtm_node_prices` runs `ercot_rt_spp.py --daily --max-rows 500000`, first thing after the sync. About 96 files and 30,000 rows a day.
- The ceiling counts the rows the table keeps of each file as it is saved, per UTC day, in `warehouse/raw/ercot_rtm_spp/rows_by_run.csv`. The request that could pass the ceiling is not made.

## 3. The battery page's downloads, the generator page's builders

- **`battery_dispatch_export`: in the run, ran once.** The model gives the same 26,304 hours (window 2023-10 to 2026-09). The CSV's two dated header lines now name today's tables. `tests.test_session178`: exit 0.
- **`battery_scenario_steps`: in the run, ran once (13 minutes).** Every month of every cell equals the file on `main`, so the file was left as committed. The live battery page prints this file's build date; it still says 10 October.
- **Both keep a file that did not move** (`--keep-same`, new). Without it the live page's printed date would change every day.
- **`seller_hybrid`: in the run, ran once.** `site/data/seller/hybrid.json` and the 17 yearly price files are of today. `tests.test_session162`: exit 0.
- **The snapshot, the hub files, the hourly CSV: ran once, not committed, switched off in the run.** Next section.
- Each group has its own tests in the run. A group one of whose steps or tests fails is put back as committed and recorded as failed. So `main` does not get a file its own tests refuse.
- "The three downloads describe today's files": the battery's yes (header of today, same hours); the datacenter's is the daily run's own, last written 11 October; **the generator's no**, still the export of 7 October.

### The generator's group

- All three ran and passed their own checks: the model (8,335 rows, snapshot 2.0 MB), the hub files (each main hub equal to the snapshot), the CSV (72,576 hours to 2026-10-11T04:00Z, each of 100 months equal to the snapshot).
- Then the tests. With the new CSV, six fail:
  - `tests/test_session183_replication.py`, class `TheExport`, four tests: the row count (72,384), the last hour (2026-10-03T04:00:00Z), the last local day (2026-10-02), the count of blank hours (72).
  - `tests/test_session199.py`, class `TheFrozenFiles`, two tests: the capture build the CSV's header names (7 October), and the list of dated records, which a daily export lengthens by one a day.
- With the committed CSV and the new snapshot, two others fail: the CSV is checked against the snapshot (October 2026 has more hours).
- So the snapshot, the hub files and the CSV were put back as committed. The new builds are kept on this machine under `runs/s204/new_generator/`.
- **The table `merchant_revenue_monthly` stays as built today** (188 rows changed, validator exit 0, archive, Redivis draft). I first put it back with its snapshot; the archive keeps no return to an earlier value, so the archive and the table then disagreed on 188 rows. Set forward again, the table, the archive and Redivis agree (0 values differ).
- One test fails on this machine alone because of that: `tests.test_session51` `Snapshot.test_snapshot_equals_the_table` (the snapshot of 4 October against today's table). It is skipped where the table is absent, so not on GitHub.

## 4. LAST_ANSWERED

- `last_answered: 200`, `on: 2026-10-12`. One note added above the two lines.

## 5. The two storage offers tables

- **Today they agree** (session 200 rebuilt the monthly tables at 01:47 UTC; `tests.test_session116` `Records.test_the_tables_on_this_machine_add_up`: exit 0).
- **Still open as a cause:** today's sync brings a new day into the daily table and leaves the monthly ones.
- **The fix is two lines, not one, added after the sync:**
  - `soft_step dm_storage_awards_rollup "$PYTHON" warehouse/derived/ercot_storage_dam_awards.py`
  - `soft_step dm_storage_offers_rollup "$PYTHON" warehouse/derived/ercot_storage_dam_offers.py`
  - Why two: one line needs `bash -c`, and under `warehouse/health.py` Windows itself looks for that `bash` and can find another than the one running the script.
  - Both tried into a scratch folder: exit 0 and 0, 252 and 819 rows.

## Pulls against their ceilings

| Pull | Address | Time (UTC) | Size | Ceiling |
|---|---|---|---|---|
| NP6-905-CD, the list | `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12301` | 09:08:40 (first attempt a connection error, second answered) | 700,367 bytes, 690 intervals listed | one list a run |
| NP6-905-CD, each listed file not held | `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<id>`, 672 addresses (in `warehouse/raw/ercot_rtm_spp/zips/manifest.csv`) | 09:08:59 to 09:29:30 | 672 files, 5,684,470 bytes, 0 failed | 500,000 rows this session: 209,664 counted, 41.9 percent |

- No other request to a publisher. GitHub's public API was read for the checks (no token).

## Checks, with exit codes

None piped; outputs under `runs/s204/` on lab-desktop.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 204"` | 0 | 6 of 6, on duty |
| `scripts/freeze.py status` | 0 | no freeze |
| `scripts/duty.py beat`, before the pull | 0 | |
| `ercot_rt_spp.py --pull --max-rows 500000` | 0 | 672 files, 209,664 rows counted |
| `ercot_rt_spp.py --write`, under the lock | 1, then 0 | first: "a settlement point and interval twice across files"; after the fix: 424,632 rows |
| `table_stores.py ercot_rtm_node_prices`, under the lock | 0 | validator 0, coverage 0, archive 0, Redivis 0 |
| `merchant_revenue.py`, under the lock | 0 | 8,335 rows |
| `table_stores.py merchant_revenue_monthly`, under the lock | 0 | three times: today's build, the put-back, today's build again |
| `restore.py merchant_revenue_monthly --from-bucket` and a comparison | 0 | the archive equals the table, 0 values differ |
| `battery_dispatch_export.py` | 0 | 26,304 rows, 36 months |
| `battery_scenario_steps.py` | 0 | 12 cases, the same but for when |
| `generator_hourly_export.py`, `seller_hybrid.py`, `merchant_hubs.py` | 0, 0, 0 | |
| `erw_validate.py` on the two tables written | 0 | pass |
| `scripts/sync.py --check --no-git`, all tables | 0 | "tables in coverage: 198; current: 198" |
| `warehouse/scheduled.py --list` | 0 | 17 steps, the seven new ones named |
| `scheduled.py <step> --check`, each of the seven | 0 | "every input is here" |
| `bash -n warehouse/run_data_machine.sh`; `--check` | 0, 0 | |
| `python -m unittest tests.test_session204` | 0 | 34 tests |
| `tests.test_session120`, `114_part2`, `149`, `185`, `190`, `116` | 0 each | the earlier pins of the schedule and of the run hold |
| `tests.test_session178`, `179`, `162` on the rebuilt files | 0, 0, 0 | |
| The generator's five modules on the new CSV | 1 | 6 failures, listed above |
| The same on the committed CSV and the new snapshot | 1 | 2 failures |
| The same with the group put back | 0 | |
| The whole suite on a clean copy of the branch, 09:45 UTC | 1 | 3,427 tests, 1 failure (the planner's clock), 253 skipped |

- **One command of mine ran in the wrong order, and nothing was lost.** At the first write I started the stores without reading the write's exit code. The write had failed and written nothing, so the stores ran on the table as it was: 0 rows archived, the same table uploaded again. From then on the stores ran only after exit 0.
- **Not run:** the daily run itself (rule 4). The new blocks' two shell functions were run in a scratch harness with stand-in commands. `--daily` was not run against ERCOT: the pull and the write ran as two commands, the pull outside the lock.
- **Not verified:** nobody has run the do-files in Stata.

## The landing

- **The push waited for 13:00 UTC.** `tests/test_planner.py` has one test that reads the real clock and fails from 05:00 to 13:00 UTC. GitHub's check runs the suite, so a branch pushed in those hours is refused. The test was not touched (rule 8). The work was finished by about 09:45 UTC; the push went at about 13:05 UTC.
- At 13:01 UTC: `tests.test_planner` exit 0 (30 tests); `origin/main` still at `9687ca26` (the code machine had landed nothing, so there was nothing to merge); `scripts/freeze.py status` exit 0, no freeze.
- **Before snapshot:** `node site/scripts/snapshot-live.mjs take before204`, exit 0, 25 pages, 0 failed, at 2026-10-12T13:01:41Z. Every one of the 25 addresses is in review in `site/lib/release.ts` on main and is read as the in-review page. Against session 200's last snapshot (`compare after200c before204`): 0 differences.
- **The after snapshot, the comparison and GitHub's check are in session 205's report,** under "The landing of session 204": this file is pushed with the branch, before its own result exists.

## Decisions made without you

- **The generator's three steps are switched off, not changed tests.** Rule 8 against the letter of ruling 3. The reversible side: one word turns them on.
- **Session 205 started while this branch waited for 13:00 UTC.** The work stayed in order; only the push waited on the clock.
- **`task/198-battery-data` was not landed here.** It edits the same two files; my blocks sit where its blocks do not, so the two merge without a conflict. Its quantities step is still not in the run.
- **The new steps are a second list in `scheduled.py`, not entries of `JOBS`.** `JOBS` is pinned by session 114's tests as the runner's schedule. So no earlier test of the schedule changed.
- **One earlier test changed by one condition:** session 120's "neither pull is on a schedule" still forbids `ercot_rt_spp` in the runner's two scripts and in every workflow, and no longer in `scheduled.py`. The ruling it stated is the one you changed tonight.
- **A table's stores are one script** (`warehouse/table_stores.py`), not a third copy of the load zones' block in the run.
- **Each new group is tested in the run and put back when its tests fail.** The run commits straight to `main`; this is what broke `main` on 11 October.
- **`--keep-same` for the two battery files.** Reversible: drop the flag in `scheduled.py`.
- **The steps file was left as committed** although it "ran once": the cells are the same and the live page prints its date. The battery CSV's header was committed: no page prints it.
- **The node price pull ran outside the lock; the write under it** (rule 4: the lock for the write). The run of 17:00 UTC holds the lock throughout, as it does for everything.
- **"500,000 rows" is read as rows added in a UTC day, counted per file saved,** not as the table's size. The table passes 500,000 rows on about 15 October.
- **The node table's license flag in coverage is unchanged** (`public`). "Internal" is read as your parenthesis says: not in the live set.
- **An interval posted twice with different prices is left out of the table,** like the repeated hour of the clock change.
- **Five worktrees were left** for one untracked line each. Rule 7: nothing deleted but what is named, and the rule for a worktree is an empty status.
- **A scratch worktree of mine** (`erw-204`, made and removed in the first minutes) and a clean copy in the session's scratch folder for the suite.
- **The hybrid's 17 yearly price files are rewritten every day** though only the current year's prices move (each carries a build stamp).

## For Samuel's ruling

- The generator's CSV, snapshot and hub files cannot move daily until six tests stop holding the CSV to 7 October (four in `test_session183_replication.py`, two in `test_session199.py`). Have a code session change them, then set `GENERATOR=1` in the run?
- `tests/test_planner.py` fails from 05:00 to 13:00 UTC, so nothing lands in those hours. Have a code session give that test a fixed clock?
- `task/198-battery-data` (the daily ancillary quantities) is still not on `main`. Land it now that `main` is green outside those hours?
- The node price table grows by about 30,000 rows a day, 11 million a year, and its file is rebuilt from every saved zip each day. Keep every settlement point, or a ceiling on the table's size?
- The node price table sits in the public Redivis dataset's draft (its coverage flag is `public`, ERCOT's terms allow it). Move it to the internal dataset?
- Once the generator's steps are on, the daily commit grows by about 20 MB of files (hub files 14 MB, snapshot 2 MB, CSV 4 MB). Daily, or monthly as session 183 recommended?
- The battery tests will refuse the CSV when October 2026 enters the window (about 28 October) if they hold a date. The run then puts the file back and reports it. Have a session look before that day?
- Five worktrees hold only the suite's residue (`warehouse/output/raw/`). Remove them by force?
- `tests.test_session51` fails on this machine until the snapshot is rebuilt (today's table against the snapshot of 4 October). Leave it as the alarm?

## The prompt

"Chain of 12 October (night): sessions 204 and 205, the data machine", pasted on 12 October 2026 at about 02:00 Pacific: ten rules (precheck first; unattended; landing with freeze status and snapshots, pull and merge main, no cutoff; data writes under the lock, nothing re-runs the daily run; pulls as approved, model spend USD 0; a beat before a long step; no em dashes, nothing deleted but what 204 names; no page, test logic, run time or trigger, scanner or release gate; this report; the chain queue after 205) and five pieces of work for 204 (the merged worktrees and branches; the node price pull and its daily step; the battery downloads, the generator's builders and its CSV in the daily run; LAST_ANSWERED at 200; the storage offers tables).
